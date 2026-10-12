// ConnectCameraIntent.swift
//
// "连接相机" — open the app and connect to a camera (a named one, or the most
// recently used). The actual connection happens in AppModel; this intent only
// records the request and opens the app.
//
import AppIntents

struct ConnectCameraIntent: AppIntent {
    static let title: LocalizedStringResource = "连接相机"
    static let description = IntentDescription("连接到一台 Lumix 相机并开始监视")
    static let openAppWhenRun = true

    @Parameter(title: "相机")
    var camera: CameraEntity?

    init() {}
    init(camera: CameraEntity?) { self.camera = camera }

    func perform() async throws -> some IntentResult {
        await MainActor.run {
            AppIntentRouter.shared.handledIntent = .init(intent: self)
        }
        return .result()
    }
}
