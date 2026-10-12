// ControlView.swift
//
// Remote control panel: shutter, power, camera mode, focus, AF/AE lock,
// review playback. All commands verified against the cam.cgi protocol audit.
//
import SwiftUI

struct ControlView: View {
    @EnvironmentObject var model: AppModel
    @State private var afLockOn: Bool = false

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                resultBanner
                shutterSection
                modeSection
                focusSection
                lockSection
                playSection
                warningNote
            }
            .padding()
        }
        .background(Color.black.ignoresSafeArea())
        .navigationTitle("控制")
    }

    @ViewBuilder
    private var resultBanner: some View {
        if !model.controlResult.isEmpty {
            Text(model.controlResult)
                .font(.footnote.weight(.medium))
                .foregroundStyle(.cyan)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(10)
                .background(Color(.systemGray6))
                .clipShape(RoundedRectangle(cornerRadius: 8))
        }
    }

    // MARK: Shutter

    private var shutterSection: some View {
        VStack(spacing: 10) {
            Text("快门").font(.subheadline.weight(.medium))
            Button {
                Task { await model.shoot() }
            } label: {
                ZStack {
                    Circle().stroke(.white, lineWidth: 3).frame(width: 84, height: 84)
                    Circle().fill(.white).frame(width: 66, height: 66)
                }
            }
            Text("camcmd&type=shoot")
                .font(.caption2)
                .monospaced()
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 8)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    // MARK: Mode

    private var modeSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("相机模式").font(.subheadline.weight(.medium))
                Spacer()
                if let m = model.state?.camMode {
                    Text("当前：\(m)").font(.caption).foregroundStyle(.secondary)
                }
            }
            HStack(spacing: 8) {
                ModeButton(label: "拍照", icon: "camera", value: "shoot") {
                    Task { await model.setCameraMode("shoot") }
                }
                ModeButton(label: "录像", icon: "video", value: "movie") {
                    Task { await model.setCameraMode("movie") }
                }
                ModeButton(label: "回放", icon: "photo.on.rectangle", value: "play") {
                    Task { await model.setCameraMode("play") }
                }
            }
            Text("camcmd&type=shoot|movie|play")
                .font(.caption2)
                .monospaced()
                .foregroundStyle(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    // MARK: Focus

    private var focusSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("对焦").font(.subheadline.weight(.medium))
            HStack(spacing: 8) {
                FocusButton(label: "广角", value: "wide") { Task { await model.focus("wide") } }
                FocusButton(label: "正常", value: "normal") { Task { await model.focus("normal") } }
                FocusButton(label: "长焦", value: "tele") { Task { await model.focus("tele") } }
                FocusButton(label: "停止", value: "stop") { Task { await model.focus("stop") } }
            }
            Text("camctrl&type=focus&value=wide|normal|tele|stop")
                .font(.caption2)
                .monospaced()
                .foregroundStyle(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    // MARK: AF/AE lock

    private var lockSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("AF/AE 锁定").font(.subheadline.weight(.medium))
                Spacer()
                Toggle("", isOn: $afLockOn)
                    .labelsHidden()
                    .onChange(of: afLockOn) { _, on in
                        Task { await model.afAELock(on: on) }
                    }
            }
            Text("camctrl&type=af_ae_lock&value=on|off")
                .font(.caption2)
                .monospaced()
                .foregroundStyle(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    // MARK: Review playback

    private var playSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("回放控制（PLAY 模式）").font(.subheadline.weight(.medium))
            HStack(spacing: 8) {
                PlayButton(label: "开始", icon: "play.fill", value: "start") {
                    Task { await model.play("start") }
                }
                PlayButton(label: "暂停", icon: "pause.fill", value: "pause") {
                    Task { await model.play("pause") }
                }
                PlayButton(label: "停止", icon: "stop.fill", value: "stop") {
                    Task { await model.play("stop") }
                }
            }
            Text("playcmd&type=start|pause|stop")
                .font(.caption2)
                .monospaced()
                .foregroundStyle(.secondary)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }

    private var warningNote: some View {
        Text("提示：部分命令在相机处于播放/菜单模式时会被拒绝（err_reject）。状态栏实时显示当前模式。")
            .font(.caption2)
            .foregroundStyle(.secondary)
    }
}

// MARK: - Button subviews

private struct ModeButton: View {
    let label: String
    let icon: String
    let value: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Image(systemName: icon).font(.title3)
                Text(label).font(.caption)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 8)
        }
        .buttonStyle(.bordered)
    }
}

private struct FocusButton: View {
    let label: String
    let value: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(label)
                .font(.caption.weight(.medium))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 8)
        }
        .buttonStyle(.bordered)
    }
}

private struct PlayButton: View {
    let label: String
    let icon: String
    let value: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 4) {
                Image(systemName: icon).font(.caption2)
                Text(label).font(.caption)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 8)
        }
        .buttonStyle(.bordered)
    }
}
