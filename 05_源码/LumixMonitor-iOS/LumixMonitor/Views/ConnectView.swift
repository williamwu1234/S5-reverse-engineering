// ConnectView.swift
import SwiftUI

struct ConnectView: View {
    @EnvironmentObject var model: AppModel
    @ObservedObject private var store = CameraStore.shared
    @StateObject private var discovery = CameraDiscovery()
    @State private var manualIP: String = ""

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    header
                    recentCard
                    permissionCard
                    manualCard
                    discoveredCard
                    protocolNote
                }
                .padding()
            }
            .background(Color.black.ignoresSafeArea())
            .navigationTitle("Lumix Monitor")
            .onAppear {
                discovery.startBrowsing()
                Task { await model.requestPhotoPermission() }
            }
            .onDisappear { discovery.stopBrowsing() }
        }
    }

    private var header: some View {
        VStack(spacing: 6) {
            Image(systemName: "camera.aperture")
                .font(.system(size: 46))
                .foregroundStyle(.cyan)
            Text("LUMIX S5 监视器")
                .font(.title3.weight(.semibold))
            Text("基于 cam.cgi / UDP startstream / DLNA 协议的 DC-S5 (MC801) 研究监视工具。全程本地运行，无云端。")
                .font(.footnote)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 12)
    }

    @ViewBuilder
    private var recentCard: some View {
        let recent = store.knownCameras
        if !recent.isEmpty {
            VStack(alignment: .leading, spacing: 10) {
                Text("最近使用").font(.headline)
                ForEach(recent) { cam in
                    HStack(spacing: 12) {
                        Button {
                            Task { await model.connect(ip: cam.ip, name: cam.name) }
                        } label: {
                            HStack(spacing: 12) {
                                Image(systemName: "camera")
                                    .foregroundStyle(.cyan)
                                VStack(alignment: .leading) {
                                    Text(cam.name).font(.body.weight(.medium))
                                    Text(cam.ip).font(.caption).foregroundStyle(.secondary)
                                }
                                Spacer()
                                Image(systemName: "chevron.right").font(.caption).foregroundStyle(.secondary)
                            }
                            .contentShape(Rectangle())
                            .padding(.vertical, 6)
                        }
                        .buttonStyle(.plain)
                        .foregroundStyle(.primary)

                        Button {
                            store.remove(cam.ip)
                        } label: {
                            Image(systemName: "xmark.circle.fill")
                                .foregroundStyle(.tertiary)
                        }
                        .buttonStyle(.borderless)
                    }
                }
            }
            .padding()
            .background(Color(.systemGray5))
            .clipShape(RoundedRectangle(cornerRadius: 12))
        }
    }

    private var permissionCard: some View {
        Button {
            Task { await model.requestPhotoPermission() }
        } label: {
            Label("授权相册（用于保存回传的照片）", systemImage: "photo.badge.plus")
                .frame(maxWidth: .infinity)
        }
        .buttonStyle(.bordered)
    }

    private var manualCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("手动输入相机 IP").font(.headline)
            HStack {
                TextField("192.168.x.x", text: $manualIP)
                    .keyboardType(.numbersAndPunctuation)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                    .padding(8)
                    .background(Color(.systemGray6))
                    .clipShape(RoundedRectangle(cornerRadius: 8))
                Button("连接") {
                    Task { await model.connect(ip: manualIP) }
                }
                .buttonStyle(.borderedProminent)
                .disabled(manualIP.trimmingCharacters(in: .whitespaces).isEmpty || model.isConnecting)
            }
            if model.isConnecting {
                HStack(spacing: 8) {
                    ProgressView()
                    Text(model.statusMessage).font(.caption).foregroundStyle(.secondary)
                }
            }
            if !model.errorMessage.isEmpty {
                Text(model.errorMessage).font(.caption).foregroundStyle(.red)
            }
        }
        .padding()
        .background(Color(.systemGray5))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private var discoveredCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("自动发现（Bonjour _http._tcp.）").font(.headline)
                Spacer()
                if discovery.isBrowsing { ProgressView() }
            }
            if discovery.found.isEmpty {
                Text("未发现相机。请确认相机已开启 Wi-Fi 并与手机在同一网络（相机热点或同一局域网）。")
                    .font(.caption).foregroundStyle(.secondary)
            } else {
                ForEach(discovery.found) { item in
                    Button {
                        Task { await model.connect(ip: item.host, name: item.name) }
                    } label: {
                        HStack {
                            Image(systemName: "camera")
                            VStack(alignment: .leading) {
                                Text(item.name).font(.body.weight(.medium))
                                Text("\(item.host):\(item.port)").font(.caption).foregroundStyle(.secondary)
                            }
                            Spacer()
                            Image(systemName: "chevron.right").font(.caption).foregroundStyle(.secondary)
                        }
                        .padding(.vertical, 6)
                    }
                    .foregroundStyle(.primary)
                }
            }
        }
        .padding()
        .background(Color(.systemGray5))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private var protocolNote: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("协议要点").font(.subheadline.weight(.medium))
            Text("• cam.cgi: GET /cam.cgi?mode=… · User-Agent 必须为 LUMIX Sync")
            Text("• 实时取景: UDP startstream（端口 49152–65535）")
            Text("• 文件浏览/回传: DLNA 端口 60606（ContentDirectory）")
            Text("• S5 不签发会话令牌，无需 X-SESSION_ID")
        }
        .font(.caption2)
        .foregroundStyle(.secondary)
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }
}
