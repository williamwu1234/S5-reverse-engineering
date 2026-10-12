// CameraStore.swift
//
// Persists recently-connected cameras (IP + display name) so the app can offer
// one-tap reconnect from the connect screen, and so App Intents can surface
// them as entities (for Siri / Shortcuts / Spotlight disambiguation).
//
// The UI observes this ObservableObject (reactive recent list). App-Intent
// entity queries may run off the main actor, so they use the static,
// thread-safe raw accessors below (backed by UserDefaults).
//
import Foundation
import Combine

struct KnownCamera: Codable, Identifiable, Equatable, Sendable {
    let ip: String
    var name: String
    var lastUsed: Date
    var id: String { ip }
}

final class CameraStore: ObservableObject {
    static let shared = CameraStore()

    private static let key = "knownCameras.v1"
    private let maxEntries = 8

    @Published private(set) var knownCameras: [KnownCamera] = []

    private init() {
        knownCameras = Self.readRaw()
    }

    // MARK: Thread-safe raw access (used by App-Intent entity queries)

    static func readRaw() -> [KnownCamera] {
        guard let data = UserDefaults.standard.data(forKey: key),
              let list = try? JSONDecoder().decode([KnownCamera].self, from: data) else {
            return []
        }
        return list
    }

    static var lastCamera: KnownCamera? {
        readRaw().first
    }

    private static func writeRaw(_ list: [KnownCamera]) {
        let data = (try? JSONEncoder().encode(list)) ?? Data()
        UserDefaults.standard.set(data, forKey: key)
    }

    // MARK: Mutations (call on the main thread)

    func upsert(ip rawIP: String, name: String? = nil) {
        let ip = rawIP.trimmingCharacters(in: .whitespaces)
        guard !ip.isEmpty else { return }
        var list = Self.readRaw()
        if let idx = list.firstIndex(where: { $0.ip == ip }) {
            list[idx].lastUsed = Date()
            if let name, !name.isEmpty { list[idx].name = name }
        } else {
            let display = (name?.isEmpty == false ? name! : ip)
            list.insert(KnownCamera(ip: ip, name: display, lastUsed: Date()), at: 0)
        }
        list = Array(list.prefix(maxEntries))
        Self.writeRaw(list)
        knownCameras = list
    }

    func remove(_ ip: String) {
        var list = Self.readRaw()
        list.removeAll { $0.ip == ip }
        Self.writeRaw(list)
        knownCameras = list
    }
}
