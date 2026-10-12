 // LiveViewScreen.swift
 //
 // Viewfinder (live view JPEG), remote shutter, and live camera state.
 //
 import SwiftUI

 struct LiveViewScreen: View {
     @EnvironmentObject var model: AppModel

     var body: some View {
         VStack(spacing: 0) {
             stateBar
             liveView
             controls
         }
         .background(Color.black.ignoresSafeArea())
        .onAppear {
            model.startLiveView()
            Task { await model.loadSettings() }
        }
         .onDisappear { model.stopLiveView() }
     }

     // MARK: State bar

     private var stateBar: some View {
         HStack(spacing: 12) {
             if let s = model.state {
                 Label("电池 \(s.battery)", systemImage: "battery.75")
                 Label(s.camMode.uppercased(), systemImage: "camera")
                 Label("SD \(s.currentSD)", systemImage: "sdcard")
                 Spacer()
                 Label(s.version, systemImage: "info.circle")
             } else {
                 Text(model.statusMessage).font(.caption).foregroundStyle(.secondary)
                 Spacer()
             }
         }
         .font(.caption)
         .padding(.horizontal, 14)
         .padding(.vertical, 8)
         .background(Color(.systemGray6))
     }

     // MARK: Live view

     private var liveView: some View {
         ZStack {
             if let img = model.liveFrame {
                 Image(uiImage: img)
                     .resizable()
                     .aspectRatio(contentMode: .fit)
             } else {
                if model.liveViewBlocked.isEmpty == false {
                    VStack(spacing: 12) {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .font(.system(size: 38))
                            .foregroundStyle(.yellow)
                        Text("实时取景被相机拒绝")
                            .font(.subheadline.weight(.semibold))
                            .foregroundStyle(.yellow)
                        Text(model.liveViewBlocked)
                            .font(.footnote)
                            .foregroundStyle(.white.opacity(0.92))
                            .multilineTextAlignment(.center)
                            .fixedSize(horizontal: false, vertical: true)
                            .padding(.horizontal, 24)
                    }
                } else {
                    VStack(spacing: 10) {
                        Image(systemName: "video.slash")
                            .font(.system(size: 40))
                            .foregroundStyle(.secondary)
                        Text("等待取景画面…").font(.footnote).foregroundStyle(.secondary)
                    }
                 }
             }
             if model.statusMessage.isEmpty == false {
                 VStack {
                     Spacer()
                     Text(model.statusMessage)
                         .font(.caption)
                         .padding(.horizontal, 12).padding(.vertical, 6)
                         .background(.ultraThinMaterial)
                         .clipShape(Capsule())
                         .padding(.bottom, 12)
                 }
             }
            // Debug overlay: live UDP diagnostics for on-device troubleshooting.
            VStack {
                debugPanel
                Spacer()
            }
            .padding(10)
         }
         .frame(maxWidth: .infinity, maxHeight: .infinity)
     }

    @ViewBuilder
    private var debugPanel: some View {
        if model.liveViewActive || model.debugInfo.isEmpty == false || model.udpStats != nil {
            VStack(alignment: .leading, spacing: 3) {
                if model.debugInfo.isEmpty == false {
                    Text(model.debugInfo)
                }
                if let s = model.udpStats {
                    Text(s.line)
                    if s.typeCounts.isEmpty == false {
                        Text("类型 " + s.typeCounts
                            .sorted { $0.key < $1.key }
                            .map { "\($0.key):\($0.value)" }
                            .joined(separator: " "))
                    }
                    if s.lastHeader.isEmpty == false {
                        Text(s.lastHeader)
                    }
                }
            }
            .font(.system(size: 10, design: .monospaced))
            .foregroundStyle(.white)
            .padding(.horizontal, 8).padding(.vertical, 6)
            .background(Color.black.opacity(0.55))
            .clipShape(RoundedRectangle(cornerRadius: 6))
        }
    }

     // MARK: Controls

     private var controls: some View {
         HStack {
             // Focus
             Menu {
                 Button("对焦·广角") { Task { await focus("wide") } }
                 Button("对焦·正常") { Task { await focus("normal") } }
                 Button("对焦·长焦") { Task { await focus("tele") } }
                 Button("停止对焦") { Task { await focus("stop") } }
             } label: {
                 Image(systemName: "scope").font(.title2)
             }

             Spacer()

             // Shutter
             Button {
                 Task { await model.shoot() }
             } label: {
                 ZStack {
                     Circle().stroke(.white, lineWidth: 3).frame(width: 72, height: 72)
                     Circle().fill(.white).frame(width: 58, height: 58)
                 }
             }

             Spacer()

             // Power
             Menu {
                 Button("关机") { Task { await model.power(on: false) } }
                 Button("开机") { Task { await model.power(on: true) } }
             } label: {
                 Image(systemName: "power").font(.title2)
             }
         }
         .padding(.horizontal, 30)
         .padding(.vertical, 18)
         .foregroundStyle(.white)
         .background(Color(.systemGray6))
     }

     private func focus(_ value: String) async {
         guard let c = currentClient() else { return }
         try? await c.focus(value)
     }

     private func currentClient() -> LumixClient? {
         // Re-create a lightweight client for ad-hoc calls (stateless).
         model.isConnected ? LumixClient(ip: model.ip) : nil
     }
 }
