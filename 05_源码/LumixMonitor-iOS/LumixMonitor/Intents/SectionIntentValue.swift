// SectionIntentValue.swift
//
// Maps the app's five tabs to an AppEnum the system can present as a picker.
// Kept deliberately small: only the fixed set of destinations.
//
import AppIntents

enum SectionIntentValue: String, AppEnum {
    case dashboard
    case live
    case control
    case gallery
    case monitor

    static var typeDisplayName: LocalizedStringResource { "页面" }
    static let typeDisplayRepresentation: TypeDisplayRepresentation = "页面"

    static var caseDisplayRepresentations: [Self: DisplayRepresentation] {
        [
            .dashboard: "仪表盘",
            .live: "取景",
            .control: "控制",
            .gallery: "相册",
            .monitor: "监视",
        ]
    }

    var tab: AppModel.Tab {
        switch self {
        case .dashboard: return .dashboard
        case .live: return .live
        case .control: return .control
        case .gallery: return .gallery
        case .monitor: return .monitor
        }
    }
}
