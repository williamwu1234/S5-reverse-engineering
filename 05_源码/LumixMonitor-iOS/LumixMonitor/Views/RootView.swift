// RootView.swift
//
// Top-level navigation. Not connected → connect screen.
// Connected → 5 tabs: 仪表盘 / 取景 / 控制 / 相册 / 监视.
// Settings is reachable from the dashboard toolbar (gear icon).
// Also drains the App Intent router: Siri / Shortcuts / Spotlight intents are
// translated here into navigation + camera actions on the live AppModel.
//
import SwiftUI
import AppIntents

struct RootView: View {
    @EnvironmentObject var model: AppModel
    @ObservedObject private var router = AppIntentRouter.shared

    var body: some View {
        Group {
            if model.isConnected {
                connectedTabs
            } else {
                ConnectView()
            }
        }
        .onReceive(router.$handledIntent) { handled in
            guard let handled else { return }
            router.handledIntent = nil
            processIntent(handled.intent)
        }
        .onAppear {
            // Cold launch: an intent may have been enqueued before this view
            // subscribed to the router.
            if let handled = router.handledIntent {
                router.handledIntent = nil
                processIntent(handled.intent)
            }
        }
    }

    private var connectedTabs: some View {
        TabView(selection: $model.activeTab) {
            NavigationStack {
                DashboardView()
                    .toolbar {
                        ToolbarItem(placement: .navigationBarTrailing) {
                            Button {
                                model.showSettings = true
                            } label: {
                                Image(systemName: "gearshape")
                            }
                        }
                    }
                    .sheet(isPresented: $model.showSettings) {
                        SettingsView()
                    }
            }
            .tabItem { Label("仪表盘", systemImage: "gauge.with.dots.needle.50percent") }
            .tag(AppModel.Tab.dashboard)

            NavigationStack { LiveViewScreen() }
                .tabItem { Label("取景", systemImage: "video") }
                .tag(AppModel.Tab.live)

            NavigationStack { ControlView() }
                .tabItem { Label("控制", systemImage: "slider.horizontal.3") }
                .tag(AppModel.Tab.control)

            NavigationStack { GalleryView() }
                .tabItem { Label("相册", systemImage: "photo.on.rectangle.angled") }
                .tag(AppModel.Tab.gallery)

            NavigationStack { MonitorView() }
                .tabItem { Label("监视", systemImage: "terminal") }
                .tag(AppModel.Tab.monitor)
        }
    }

    // MARK: - App Intent handling

    @MainActor
    private func processIntent(_ intent: any AppIntent) {
        switch intent {
        case let connect as ConnectCameraIntent:
            if let cam = connect.camera {
                Task { await model.connect(ip: cam.id, name: cam.name) }
            } else if let last = CameraStore.lastCamera {
                Task { await model.connect(ip: last.ip, name: last.name) }
            }
        case let section as OpenSectionIntent:
            model.activeTab = section.section.tab
        case let capture as CapturePhotoIntent:
            Task { await handleCapture() }
        case let power as PowerCameraIntent:
            if model.isConnected {
                Task { await model.power(on: power.power.isOn) }
            }
        default:
            break
        }
    }

    @MainActor
    private func handleCapture() async {
        if model.isConnected {
            await model.shoot()
        } else if let last = CameraStore.lastCamera {
            await model.connect(ip: last.ip, name: last.name)
            try? await Task.sleep(nanoseconds: 1_500_000_000)
            await model.shoot()
        } else {
            model.errorMessage = "未连接相机，无法拍照"
        }
    }
}
