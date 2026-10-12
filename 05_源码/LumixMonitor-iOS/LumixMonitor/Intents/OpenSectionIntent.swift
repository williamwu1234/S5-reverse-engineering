// OpenSectionIntent.swift
//
// "打开某页面" — open the app directly on one of its five tabs.
//
import AppIntents

struct OpenSectionIntent: AppIntent {
    static let title: LocalizedStringResource = "打开页面"
    static let description = IntentDescription("打开 Lumix Monitor 的指定页面")
    static let openAppWhenRun = true

    @Parameter(title: "页面", default: .dashboard)
    var section: SectionIntentValue

    init() {}
    init(section: SectionIntentValue) { self.section = section }

    func perform() async throws -> some IntentResult {
        await MainActor.run {
            AppIntentRouter.shared.handledIntent = .init(intent: self)
        }
        return .result()
    }
}
