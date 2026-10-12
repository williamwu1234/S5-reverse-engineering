// CapturePhotoIntent.swift
//
// "拍一张" — open the app and fire the shutter on the connected camera (if
// not connected, it connects to the most recent camera first, then shoots).
//
import AppIntents

struct CapturePhotoIntent: AppIntent {
    static let title: LocalizedStringResource = "拍摄照片"
    static let description = IntentDescription("让 Lumix 相机拍摄一张照片")
    static let openAppWhenRun = true

    init() {}

    func perform() async throws -> some IntentResult {
        await MainActor.run {
            AppIntentRouter.shared.handledIntent = .init(intent: self)
        }
        return .result()
    }
}
