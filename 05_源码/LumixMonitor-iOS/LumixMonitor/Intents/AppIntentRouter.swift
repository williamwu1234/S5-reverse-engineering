// AppIntentRouter.swift
//
// Single handoff point between the system (Siri / Shortcuts / Spotlight) and
// the app scene. Intents are thin: `perform()` just records the intent that
// should be handled and opens the app. The scene (RootView) drains the router
// and translates the intent into real navigation / camera actions using the
// live `AppModel`. All business logic stays in the app, not in the intents.
//
import AppIntents
import Combine

final class AppIntentRouter: ObservableObject {
    struct HandledIntent: Equatable {
        let id = UUID()
        let intent: any AppIntent

        static func == (lhs: Self, rhs: Self) -> Bool {
            lhs.id == rhs.id
        }
    }

    static let shared = AppIntentRouter()

    @Published var handledIntent: HandledIntent?

    private init() {}
}
