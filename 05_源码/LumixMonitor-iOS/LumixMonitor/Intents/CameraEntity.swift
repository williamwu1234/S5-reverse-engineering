// CameraEntity.swift
//
// The camera as an App Intents entity. Exposed to Siri / Shortcuts / Spotlight
// so users can say "连接我的 DC-S5" or pick a camera from a system picker.
// It only carries the fields the system needs (IP + display name) — it does
// not mirror the full persistence model.
//
import AppIntents

struct CameraEntity: AppEntity {
    let id: String      // the camera IP
    let name: String

    static let typeDisplayRepresentation: TypeDisplayRepresentation = "相机"
    static let defaultQuery = CameraQuery()

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: LocalizedStringResource(stringLiteral: name), subtitle: "IP \(id)")
    }
}

struct CameraQuery: EntityQuery {
    func entities(for identifiers: [CameraEntity.ID]) async throws -> [CameraEntity] {
        CameraStore.readRaw()
            .filter { identifiers.contains($0.ip) }
            .map { CameraEntity(id: $0.ip, name: $0.name) }
    }

    func suggestedEntities() async throws -> [CameraEntity] {
        CameraStore.readRaw().map { CameraEntity(id: $0.ip, name: $0.name) }
    }
}
