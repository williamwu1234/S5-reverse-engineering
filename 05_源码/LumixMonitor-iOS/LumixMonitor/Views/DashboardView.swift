// DashboardView.swift
//
// Rich camera state grid: battery, mode, SD slots, temperature, firmware,
// play state, lens — plus connection health (latency, last update) and
// quick actions.
//
import SwiftUI

struct DashboardView: View {
    @EnvironmentObject var model: AppModel

    var body: some View {
        ScrollView {
            VStack(spacing: 14) {
                healthBar
                if let s = model.state {
                    stateGrid(s)
                } else {
                    ContentUnavailableView("等待状态数据", systemImage: "wifi.exclamationmark")
                }
                quickActions
                connectionInfo
            }
            .padding()
        }
        .background(Color.black.ignoresSafeArea())
        .navigationTitle("仪表盘")
        .onAppear {
            if model.settings.isEmpty {
                Task { await model.refreshSettings() }
            }
        }
    }

    // MARK: Connection health

    private var healthBar: some View {
        HStack(spacing: 10) {
            Circle()
                .fill(model.isReconnecting ? Color.orange : (model.lastStateUpdate != nil ? .green : .gray))
                .frame(width: 9, height: 9)
            if model.isReconnecting {
                Text("连接丢失，正在自动重连…")
                    .font(.footnote.weight(.medium))
                    .foregroundStyle(.orange)
            } else if model.lastStateUpdate != nil {
                Text("已连接 · \(model.ip)")
                    .font(.footnote.weight(.medium))
                if model.lastLatency >= 0 {
                    Text("\(model.lastLatency * 1000, specifier: "%.0f") ms")
                        .font(.caption2)
                        .monospacedDigit()
                        .foregroundStyle(.secondary)
                }
            }
            Spacer()
            if let s = model.lastStateUpdate {
                Text(s, style: .time)
                    .font(.caption2)
                    .monospacedDigit()
                    .foregroundStyle(.secondary)
            }
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }

    // MARK: State grid

    private func stateGrid(_ s: CameraState) -> some View {
        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 10) {
            StateTile(icon: "battery.75", title: "电池",
                      value: s.batteryDisplay,
                      tint: batteryTint(s))
            StateTile(icon: "camera", title: "模式",
                      value: s.camMode.uppercased(),
                      tint: modeTint(s.camMode))
            StateTile(icon: "cpu", title: "固件",
                      value: s.version, tint: .cyan)
            StateTile(icon: "thermometer.medium", title: "温度",
                      value: s.temperature.isEmpty ? "--" : s.temperature,
                      tint: s.temperature == "low" ? .green : (s.temperature == "high" ? .red : .gray))
            StateTile(icon: "sdcard", title: "SD1",
                      value: s.sdStatusDisplay + (s.sdFull ? " · 已满" : ""),
                      tint: s.sdFull ? .red : .green)
            StateTile(icon: "sdcard", title: "SD2",
                      value: s.sd2StatusDisplay + (s.sd2Full ? " · 已满" : ""),
                      tint: s.sd2Full ? .red : .green)
            StateTile(icon: "arrow.left.arrow.right", title: "当前卡",
                      value: s.currentSD.isEmpty ? "--" : s.currentSD,
                      tint: .cyan)
            StateTile(icon: "play.rectangle", title: "回放",
                      value: s.play.isEmpty ? "--" : s.play,
                      tint: s.play == "stop" ? .green : .orange)
        }
    }

    private func batteryTint(_ s: CameraState) -> Color {
        if s.batteryPercent > 0 {
            switch s.batteryPercent {
            case ..<20: return .red
            case ..<50: return .orange
            default: return .green
            }
        }
        // N-level representation like "5/5"
        if let slash = s.battery.firstIndex(of: "/"), s.battery[slash] != "0" {
            return .green
        }
        return .orange
    }

    private func modeTint(_ mode: String) -> Color {
        switch mode.lowercased() {
        case "shoot": return .green
        case "movie": return .red
        case "play": return .orange
        case "off": return .gray
        default: return .cyan
        }
    }

    // MARK: Quick actions

    private var quickActions: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("快捷操作").font(.subheadline.weight(.medium))
            HStack(spacing: 10) {
                QuickAction(icon: "camera.shutter", label: "快门") {
                    Task { await model.shoot() }
                }
                QuickAction(icon: model.liveViewActive ? "video.slash" : "video",
                            label: model.liveViewActive ? "停止取景" : "启动取景") {
                    if model.liveViewActive {
                        model.stopLiveView()
                    } else {
                        model.activeTab = .live
                        model.startLiveView()
                    }
                }
                QuickAction(icon: "photo.on.rectangle.angled", label: "相册") {
                    model.activeTab = .gallery
                    Task { await model.loadGallery() }
                }
                QuickAction(icon: "terminal", label: "监视") {
                    model.activeTab = .monitor
                }
            }
        }
    }

    // MARK: Connection info

    private var connectionInfo: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("连接信息").font(.subheadline.weight(.medium))
            InfoRow(label: "地址", value: model.ip)
            InfoRow(label: "固件", value: model.state?.version ?? "--")
            InfoRow(label: "模式", value: model.state?.camMode ?? "--")
            InfoRow(label: "延迟", value: model.lastLatency >= 0 ? String(format: "%.0f ms", model.lastLatency * 1000) : "--")
            if !model.settings.isEmpty {
                InfoRow(label: "照片风格", value: model.settings["photostyle"] ?? "--")
                InfoRow(label: "色彩模式", value: model.settings["colormode"] ?? "--")
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }
}

// MARK: - Subviews

private struct StateTile: View {
    let icon: String
    let title: String
    let value: String
    let tint: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 6) {
                Image(systemName: icon)
                    .font(.caption)
                    .foregroundStyle(tint)
                Text(title)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Text(value)
                .font(.subheadline.weight(.semibold))
                .lineLimit(1)
                .minimumScaleFactor(0.7)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }
}

private struct QuickAction: View {
    let icon: String
    let label: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 6) {
                Image(systemName: icon)
                    .font(.title3)
                    .frame(width: 44, height: 30)
                Text(label)
                    .font(.caption2)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 10)
        }
        .buttonStyle(.bordered)
    }
}

private struct InfoRow: View {
    let label: String
    let value: String

    var body: some View {
        HStack {
            Text(label)
                .font(.footnote)
                .foregroundStyle(.secondary)
            Spacer()
            Text(value)
                .font(.footnote.weight(.medium))
                .monospacedDigit()
        }
    }
}
