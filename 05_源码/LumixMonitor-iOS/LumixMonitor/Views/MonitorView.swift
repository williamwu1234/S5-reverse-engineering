// MonitorView.swift
//
// Research monitor: live cam.cgi command log, raw command console,
// CAMSET settings-partition reader/exporter, and protocol cheat sheet.
// This is the researcher's workbench — dense, monospace, no frills.
//
import SwiftUI
import UniformTypeIdentifiers

struct MonitorView: View {
    @EnvironmentObject var model: AppModel

    @State private var filter: LogFilter = .all
    @State private var autoScroll = true
    @State private var exportDocument: DataFileDocument?

    private static let timeFmt: DateFormatter = {
        let f = DateFormatter()
        f.dateFormat = "HH:mm:ss.SSS"
        return f
    }()

    private let presets: [(label: String, query: String)] = [
        ("getstate", "mode=getstate"),
        ("capability", "mode=getinfo&type=capability"),
        ("acc 探测", "mode=accctrl&type=req_acc&value=LumixMonitor"),
        ("fw 门控", "mode=camctrl&type=fw_update_mode&value=V2.90"),
        ("getprogress", "mode=getprogress"),
    ]

    var body: some View {
        ScrollView {
            VStack(spacing: 14) {
                rawConsole
                camsetCard
                logCard
                protocolNotes
            }
            .padding()
        }
        .background(Color.black.ignoresSafeArea())
        .navigationTitle("监视")
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                ShareLink(item: model.commandLog.exportText()) {
                    Image(systemName: "square.and.arrow.up")
                }
                .disabled(model.logEntries.isEmpty)
            }
        }
        .onAppear {
            // Wire the thread-safe CommandLog to the published log entries.
            // onAppend is dispatched by CommandLog on the main thread.
            model.commandLog.onAppend = {
                model.logEntries = model.commandLog.snapshot()
            }
            model.logEntries = model.commandLog.snapshot()
        }
        .fileExporter(
            isPresented: $model.showExport,
            document: exportDocument,
            contentType: .data,
            defaultFilename: model.exportedFileURL?.deletingPathExtension().lastPathComponent ?? "CAMSET01.dat"
        ) { result in
            if case .failure(let error) = result {
                model.errorMessage = "导出失败：\(error.localizedDescription)"
            }
        }
    }

    // MARK: - Raw command console

    private var rawConsole: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("原始命令控制台").font(.subheadline.weight(.medium))

            HStack(spacing: 8) {
                TextField("mode=getstate", text: $model.rawQuery)
                    .font(.system(size: 12, design: .monospaced))
                    .autocorrectionDisabled()
                    .textInputAutocapitalization(.never)
                    .submitLabel(.send)
                    .onSubmit { runRaw() }
                    .padding(8)
                    .background(Color(.systemGray6))
                    .clipShape(RoundedRectangle(cornerRadius: 8))

                Button(action: runRaw) {
                    Group {
                        if model.rawBusy {
                            ProgressView().frame(width: 44)
                        } else {
                            Text("执行").frame(width: 44)
                        }
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(model.rawBusy || model.rawQuery.trimmingCharacters(in: .whitespaces).isEmpty)
            }

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 6) {
                    ForEach(presets, id: \.label) { p in
                        Button(p.label) { model.rawQuery = p.query }
                            .font(.caption2)
                            .foregroundStyle(.cyan)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color(.systemGray5))
                            .clipShape(Capsule())
                    }
                }
            }

            ScrollView {
                Text(model.rawResult.isEmpty
                     ? "（无输出。输入 cam.cgi 查询串或点击预设，例如 mode=getstate）"
                     : model.rawResult)
                    .font(.system(size: 10, design: .monospaced))
                    .foregroundStyle(model.rawResult.isEmpty ? Color.secondary : .primary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .fixedSize(horizontal: false, vertical: true)
                    .padding(8)
            }
            .frame(maxHeight: 140)
            .background(Color.black.opacity(0.85))
            .clipShape(RoundedRectangle(cornerRadius: 8))
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private func runRaw() {
        Task { await model.runRawCommand() }
    }

    // MARK: - CAMSET partition reader

    private var camsetCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("CAMSET 设置分区").font(.subheadline.weight(.medium))
                Spacer()
                Button {
                    Task { await model.readCamsetting() }
                } label: {
                    if model.camsettingBusy {
                        ProgressView().frame(width: 60)
                    } else {
                        Label("读取", systemImage: "arrow.down.circle").frame(width: 60)
                    }
                }
                .buttonStyle(.bordered)
                .disabled(model.camsettingBusy)
            }

            if !model.camsettingError.isEmpty {
                Text(model.camsettingError).font(.caption).foregroundStyle(.red)
            }

            if let data = model.camsettingData {
                HStack(spacing: 0) {
                    InfoMini(label: "大小",
                             value: "\(data.count) B",
                             tint: data.count == LumixClient.camsettingSize ? .green : .orange,
                             note: data.count == LumixClient.camsettingSize ? "符合预期" : "与预期不符")
                    InfoMini(label: "校验和",
                             value: data.camsettingChecksumValid ? "有效 ✓" : "无效 ✗",
                             tint: data.camsettingChecksumValid ? .green : .red,
                             note: "Σ mod 256 = 0")
                }

                VStack(alignment: .leading, spacing: 2) {
                    Text("前 32 字节（hex）").font(.caption2).foregroundStyle(.secondary)
                    ForEach(hexRows(data), id: \.self) { row in
                        Text(row).font(.system(size: 10, design: .monospaced))
                    }
                }
                .padding(8)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(Color.black.opacity(0.85))
                .clipShape(RoundedRectangle(cornerRadius: 8))

                Button {
                    if let d = model.camsettingData {
                        // Set the export document before flipping showExport.
                        exportDocument = DataFileDocument(data: d)
                        model.exportCamsetting()
                    }
                } label: {
                    Label("导出为文件", systemImage: "square.and.arrow.up")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
            } else if !model.camsettingBusy {
                Text("读取相机 65,533 字节的设置分区（二进制）。校验规则：整块字节之和 mod 256 = 0。导出后可与参考镜像逐字节对比。")
                    .font(.caption2)
                    .foregroundStyle(.secondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private func hexRows(_ data: Data, perRow: Int = 16, rows: Int = 2) -> [String] {
        let bytes = Array(data.prefix(perRow * rows))
        return (0..<rows).map { r in
            let slice = bytes[r * perRow..<min((r + 1) * perRow, bytes.count)]
            return slice.map { String(format: "%02X", $0) }.joined(separator: " ")
        }
    }

    // MARK: - Command log

    private var logCard: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 8) {
                Text("命令日志").font(.subheadline.weight(.medium))
                Text("\(model.logEntries.count)")
                    .font(.caption2)
                    .monospacedDigit()
                    .foregroundStyle(.secondary)
                Spacer()
                Button {
                    autoScroll.toggle()
                } label: {
                    Image(systemName: autoScroll ? "arrow.down.to.line" : "arrow.up.to.line")
                        .font(.caption)
                }
                .buttonStyle(.borderless)
                .foregroundStyle(autoScroll ? .cyan : .secondary)
                .accessibilityLabel("自动滚动")

                Picker("筛选", selection: $filter) {
                    ForEach(LogFilter.allCases) { f in
                        Text(f.rawValue).tag(f)
                    }
                }
                .pickerStyle(.menu)
                .frame(width: 84)

                Button {
                    model.commandLog.clear()
                } label: {
                    Image(systemName: "trash").font(.caption)
                }
                .buttonStyle(.borderless)
                .foregroundStyle(.secondary)
                .accessibilityLabel("清空日志")
            }

            logList
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private var visibleEntries: [LogEntry] {
        switch filter {
        case .all: return model.logEntries
        case .req: return model.logEntries.filter { $0.direction == .request }
        case .resp: return model.logEntries.filter { $0.direction == .response }
        }
    }

    private var logList: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 3) {
                    if visibleEntries.isEmpty {
                        Text("（无日志条目。状态轮询不记日志，仅记录显式命令；连接/断开会写入标记行。）")
                            .font(.caption2)
                            .foregroundStyle(.secondary)
                            .frame(maxWidth: .infinity)
                    } else {
                        ForEach(visibleEntries) { e in
                            logRow(e)
                                .id(e.id)
                        }
                    }
                }
            }
            .frame(height: 340)
            .background(Color.black.opacity(0.9))
            .clipShape(RoundedRectangle(cornerRadius: 8))
            .onAppear {
                if autoScroll, let last = visibleEntries.last {
                    proxy.scrollTo(last.id, anchor: .bottom)
                }
            }
            .onChange(of: model.logEntries.count) { _, _ in
                guard autoScroll, let last = visibleEntries.last else { return }
                withAnimation(.easeOut(duration: 0.12)) {
                    proxy.scrollTo(last.id, anchor: .bottom)
                }
            }
        }
    }

    private func logRow(_ e: LogEntry) -> some View {
        HStack(alignment: .top, spacing: 6) {
            Text(Self.timeFmt.string(from: e.time))
                .foregroundStyle(.secondary)
            Text(e.direction == .request ? ">>>" : "<<<")
                .foregroundStyle(e.direction == .request ? .cyan : responseTint(e))
            Text(e.text)
                .foregroundStyle(e.direction == .request ? .primary : responseTint(e))
                .frame(maxWidth: .infinity, alignment: .leading)
                .fixedSize(horizontal: false, vertical: true)
        }
        .font(.system(size: 10, design: .monospaced))
        .lineLimit(8)
    }

    private func responseTint(_ e: LogEntry) -> Color {
        let t = e.text.lowercased()
        if t.contains("err") { return .red }
        if t.contains("ok") { return .green }
        return .secondary
    }

    // MARK: - Protocol cheat sheet

    private var protocolNotes: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("协议速查").font(.caption.weight(.medium))
            Text("• get_content_info：dir_id 放在 value，无 type 参数")
            Text("• getprogress：无 type 参数，返回 status,percent")
            Text("• CAMSET：65,533 B，整块字节和 mod 256 = 0")
            Text("• err_busy：自动重试至多 5 次（1s 间隔）")
            Text("• 所有请求必须携带 User-Agent: LUMIX Sync")
            Text("• S5 不签发会话令牌，无 X-SESSION_ID")
        }
        .font(.caption2)
        .foregroundStyle(.secondary)
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }
}

// MARK: - Support types

private enum LogFilter: String, CaseIterable, Identifiable {
    case all = "全部"
    case req = "请求"
    case resp = "响应"
    var id: String { rawValue }
}

/// Minimal FileDocument wrapper so the CAMSET binary can go through
/// .fileExporter (which requires a FileDocument, not a URL).
private struct DataFileDocument: FileDocument {
    static var readableContentTypes: [UTType] { [.data] }
    static var writableContentTypes: [UTType] { [.data] }

    var data: Data

    init(data: Data) {
        self.data = data
    }

    init(configuration: ReadConfiguration) throws {
        data = configuration.file.regularFileContents ?? Data()
    }

    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper {
        FileWrapper(regularFileWithContents: data)
    }
}

private struct InfoMini: View {
    let label: String
    let value: String
    let tint: Color
    var note: String = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label).font(.caption2).foregroundStyle(.secondary)
            HStack(spacing: 6) {
                Text(value).font(.caption.weight(.semibold)).monospacedDigit().foregroundStyle(tint)
                if !note.isEmpty {
                    Text(note).font(.caption2).foregroundStyle(.tertiary)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}
