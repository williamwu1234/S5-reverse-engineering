// PowerCameraIntent.swift
//
// "开机 / 关机" — open the app and toggle the connected camera's power.
//
import AppIntents

struct PowerCameraIntent: AppIntent {
    static let title: LocalizedStringResource = "相机开关"
    static let description = IntentDescription("打开或关闭已连接的 Lumix 相机")
    static let openAppWhenRun = true

    @Parameter(title: "状态", default: .on)
    var power: PowerState

    init() {}
    init(power: PowerState) { self.power = power }

    func perform() async throws -> some IntentResult {
        await MainActor.run {
            AppIntentRouter.shared.handledIntent = .init(intent: self)
        }
        return .result()
    }
}
