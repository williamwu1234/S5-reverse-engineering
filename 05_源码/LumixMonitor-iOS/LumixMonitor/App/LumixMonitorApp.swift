// LumixMonitorApp.swift
import SwiftUI

@main
struct LumixMonitorApp: App {
    @StateObject private var model = AppModel()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(model)
                .preferredColorScheme(.dark)
                .tint(.cyan)
        }
    }
}
