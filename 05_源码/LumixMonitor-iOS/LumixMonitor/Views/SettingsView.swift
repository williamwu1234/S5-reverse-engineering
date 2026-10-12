// SettingsView.swift
//
// Camera settings via getsetting/setsetting, capability viewer,
// connection info, and disconnect.
//
import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var model: AppModel
    @Environment(\.dismiss) private var dismiss

    private let photoStyleOptions = ["STANDARD", "VIVID", "NEUTRAL", "SCENE", "VIVID2", "MONO"]

    var body: some View {
        NavigationStack {
            Form {
                captureSection
                sdSection
                deviceSection
                capabilitySection
                connectionSection
                disconnectSection
            }
            .navigationTitle("设置")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("关闭") { dismiss() }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        Task { await model.refreshSettings() }
                    } label: {
                        Image(systemName: model.settingsBusy ? "arrow.triangle.2.circlepath" : "arrow.clockwise")
                    }
                    .disabled(model.settingsBusy)
                }
            }
            .onAppear {
                if model.settings.isEmpty {
                    Task { await model.refreshSettings() }
                }
            }
        }
    }

    // MARK: Sections

    private var captureSection: some View {
        Section {
            Picker("照片风格", selection: styleBinding) {
                ForEach(photoStyleOptions, id: \.self) { s in
                    Text(s).tag(s)
                }
            }
            .pickerStyle(.menu)

            LabeledContent("色彩模式", value: model.settings["colormode"] ?? "--")
            LabeledContent("峰值对焦", value: model.settings["peaking"] ?? "--")
            LabeledContent("RAW 传输", value: model.settings["raw_img_send"] ?? "--")
        } header: {
            Text("拍摄设置")
        } footer: {
            Text("通过 cam.cgi getsetting / setsetting 读写机内设置。")
        }
    }

    private var sdSection: some View {
        Section {
            Picker("当前存储卡", selection: sdBinding) {
                Text("SD1").tag("sd1")
                Text("SD2").tag("sd2")
            }
            .pickerStyle(.menu)
            LabeledContent("SD1 状态", value: model.state?.sdStatusDisplay ?? "--")
            LabeledContent("SD2 状态", value: model.state?.sd2StatusDisplay ?? "--")
        } header: {
            Text("存储")
        }
    }

    private var deviceSection: some View {
        Section {
            LabeledContent("设备名", value: model.settings["device_name"] ?? "--")
        } header: {
            Text("设备")
        }
    }

    private var capabilitySection: some View {
        Section {
            DisclosureGroup("能力文档（getinfo capability）") {
                ScrollView {
                    Text(model.capabilityRaw.isEmpty ? "未加载" : model.capabilityRaw)
                        .font(.system(size: 10, design: .monospaced))
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.vertical, 4)
                }
                .frame(maxHeight: 260)
            }
        } header: {
            Text("研究")
        } footer: {
            Text("相机上报的可用设置清单（原始 XML）。")
        }
    }

    private var connectionSection: some View {
        Section {
            LabeledContent("相机地址", value: model.ip)
            LabeledContent("固件", value: model.state?.version ?? "--")
            LabeledContent("模式", value: model.state?.camMode ?? "--")
            LabeledContent("延迟", value: model.lastLatency >= 0 ? String(format: "%.0f ms", model.lastLatency * 1000) : "--")
        } header: {
            Text("连接信息")
        }
    }

    private var disconnectSection: some View {
        Section {
            Button("断开连接", role: .destructive) {
                model.disconnect()
                dismiss()
            }
        }
    }

    // MARK: Bindings (read current, write on change)

    private var styleBinding: Binding<String> {
        Binding(
            get: { model.settings["photostyle"] ?? "STANDARD" },
            set: { newValue in
                Task { await model.setSetting("photostyle", newValue) }
            }
        )
    }

    private var sdBinding: Binding<String> {
        Binding(
            get: { model.settings["current_sd"] ?? "sd1" },
            set: { newValue in
                Task { await model.setSetting("current_sd", newValue) }
            }
        )
    }
}
