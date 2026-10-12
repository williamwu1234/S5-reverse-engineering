// AppShortcuts.swift
//
// Discovers the intents in the system surfaces (Shortcuts app, Siri, Spotlight).
// Phrases are verb-led and bilingual-friendly; the app is Chinese-first, so the
// canonical phrases lead with Chinese and use \(.applicationName) for the brand.
//
import AppIntents

struct LumixShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: ConnectCameraIntent(),
            phrases: [
                "用 \(.applicationName) 连接相机",
                "用 \(.applicationName) 连接我的相机"
            ],
            shortTitle: "连接相机",
            systemImageName: "camera"
        )
        AppShortcut(
            intent: CapturePhotoIntent(),
            phrases: [
                "用 \(.applicationName) 拍一张",
                "用 \(.applicationName) 拍照"
            ],
            shortTitle: "拍摄照片",
            systemImageName: "camera.shutter"
        )
        AppShortcut(
            intent: OpenSectionIntent(section: .live),
            phrases: [
                "打开 \(.applicationName) 取景",
                "用 \(.applicationName) 打开实时取景"
            ],
            shortTitle: "实时取景",
            systemImageName: "video"
        )
        AppShortcut(
            intent: PowerCameraIntent(power: .on),
            phrases: [
                "用 \(.applicationName) 开机",
                "用 \(.applicationName) 打开相机"
            ],
            shortTitle: "相机开机",
            systemImageName: "power"
        )
        AppShortcut(
            intent: PowerCameraIntent(power: .off),
            phrases: [
                "用 \(.applicationName) 关机"
            ],
            shortTitle: "相机关机",
            systemImageName: "power"
        )
    }
}
