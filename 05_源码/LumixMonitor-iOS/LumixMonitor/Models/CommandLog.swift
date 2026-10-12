// CommandLog.swift
//
// Thread-safe ring buffer of timestamped cam.cgi requests/responses.
// The research monitor view renders snapshots of this log; the client
// appends from any thread.
//
import Foundation

struct LogEntry: Identifiable, Equatable {
    enum Direction: Equatable {
        case request
        case response
    }

    let id: UUID
    let time: Date
    let direction: Direction
    let text: String

    init(direction: Direction, text: String) {
        self.id = UUID()
        self.time = Date()
        self.direction = direction
        self.text = text
    }
}

final class CommandLog {

    private let lock = NSLock()
    private var entries: [LogEntry] = []
    private let limit = 800

    /// Called on the main thread after each append (UI refresh).
    var onAppend: () -> Void = {}

    func append(_ direction: LogEntry.Direction, _ text: String) {
        let e = LogEntry(direction: direction, text: text)
        lock.lock()
        entries.append(e)
        if entries.count > limit {
            entries.removeFirst(entries.count - limit)
        }
        lock.unlock()
        DispatchQueue.main.async { [weak self] in
            self?.onAppend()
        }
    }

    func snapshot() -> [LogEntry] {
        lock.lock()
        defer { lock.unlock() }
        return entries
    }

    func clear() {
        lock.lock()
        entries.removeAll()
        lock.unlock()
        DispatchQueue.main.async { [weak self] in
            self?.onAppend()
        }
    }

    /// Plain-text export (for saving/sharing the session).
    func exportText() -> String {
        let df = DateFormatter()
        df.dateFormat = "yyyy-MM-dd HH:mm:ss.SSS"
        let lines = snapshot().map { e in
            "\(df.string(from: e.time))  \((e.direction == .request ? ">>>" : "<<<").pad(toLength: 3, withPad: " ", startingAt: 0))  \(e.text)"
        }
        return lines.joined(separator: "\n")
    }
}

private extension String {
    func pad(toLength: Int, withPad: Character, startingAt: Int) -> String {
        let paddedSelf = String(repeating: String(withPad), count: max(0, toLength - count)) + self
        let startIndex = paddedSelf.index(paddedSelf.startIndex, offsetBy: startingAt)
        return String(paddedSelf[startIndex...])
    }
}
