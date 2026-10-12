// PowerState.swift
//
// Fixed on/off choice exposed to the system for the power intent.
//
import AppIntents

enum PowerState: String, AppEnum {
    case on
    case off

    static var typeDisplayName: LocalizedStringResource { "电源状态" }
    static let typeDisplayRepresentation: TypeDisplayRepresentation = "电源状态"

    static var caseDisplayRepresentations: [Self: DisplayRepresentation] {
        [.on: "开机", .off: "关机"]
    }

    var isOn: Bool { self == .on }
}
