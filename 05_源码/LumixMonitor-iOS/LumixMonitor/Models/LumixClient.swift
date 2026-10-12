// LumixClient.swift
//
// HTTP client for the Panasonic Lumix camera control protocol (`/cam.cgi`).
// Reverse-engineered from com.panasonic.jp.lumixsync (LUMIX Sync) and verified
// against live DC-S5 (MC801) responses. See S5逆向_研究总报告_20261011/research/PROTOCOL_AUDIT.md.
//
// Transport: plain HTTP on port 80. No auth, no session token on DC-S5.
// User-Agent MUST be exactly "LUMIX Sync".
// Per-command timeouts (PROTOCOL_AUDIT §1): default 10s; camcmd/camctrl/getstate/
// get_content_info 3s; playcmd 10s. `err_busy` retried up to 5x with 1s backoff.
//
import Foundation

// MARK: - Command description

struct LumixCommand: Hashable {
    let mode: String
    var type: String? = nil
    var value: String? = nil
    var value2: String? = nil

    /// Query string, e.g. `mode=camctrl&type=focus&value=wide`.
    var query: String {
        var q = "mode=\(mode)"
        if let t = type { q += "&type=\(t)" }
        if let v = value { q += "&value=\(v)" }
        if let v2 = value2 { q += "&value2=\(v2)" }
        return q
    }
}

// MARK: - Camera state (parsed from `getstate`)

struct CameraState: Equatable {
    var ok: Bool
    var battery: String = ""        // e.g. "2/5"
    var batteryPercent: Int = -1
    var camMode: String = ""        // e.g. "play", "shoot", "movie"
    var sdCardStatus: String = ""   // e.g. "write_enable"
    var sd2CardStatus: String = ""
    var currentSD: String = ""      // e.g. "sd2"
    var version: String = ""        // e.g. "VD4.30"
    var play: String = ""           // e.g. "stop"
    var temperature: String = ""
    var lens: String = ""
    var sdFull: Bool = false
    var sd2Full: Bool = false

    var isUsable: Bool {
        ok && (sdCardStatus.contains("write") || sd2CardStatus.contains("write"))
    }

    /// Battery display string, e.g. "5/5" or "78%".
    var batteryDisplay: String {
        if batteryPercent > 0 { return "\(batteryPercent)%" }
        return battery.isEmpty ? "--" : battery
    }

    var sdStatusDisplay: String {
        sdCardStatus.contains("write_enable") ? "可写入" :
        sdCardStatus.isEmpty ? "未检测" : sdCardStatus
    }

    var sd2StatusDisplay: String {
        sd2CardStatus.contains("write_enable") ? "可写入" :
        sd2CardStatus.isEmpty ? "未检测" : sd2CardStatus
    }
}

// MARK: - Progress (getprogress CSV: status,percent)

struct LumixProgress: Equatable {
    var status: String     // exec / finish / error / err_busy
    var percent: Int = -1
    var done: Bool { status == "finish" }
    var failed: Bool { status.hasPrefix("err") || status == "error" }
}

// MARK: - Client

final class LumixClient {

    static let userAgent = "LUMIX Sync"
    /// camsetting partition size (verified: getinfo camsetting -> 65533 bytes).
    static let camsettingSize = 65_533

    let ip: String
    /// Optional command/response logger (research monitor).
    var log: CommandLog?

    private let session: URLSession

    init(ip: String, log: CommandLog? = nil) {
        self.ip = ip
        self.log = log
        let config = URLSessionConfiguration.ephemeral
        config.timeoutIntervalForRequest = 10
        config.timeoutIntervalForResource = 30
        config.requestCachePolicy = .reloadIgnoringLocalCacheData
        config.waitsForConnectivity = false
        self.session = URLSession(configuration: config)
    }

    // MARK: URL building (mirrors p168v5/n.java: mode -> type -> value -> value2, skip nil)

    func url(for cmd: LumixCommand, port: Int = 80) -> URL? {
        var comps = URLComponents()
        comps.scheme = "http"
        comps.host = ip
        comps.port = port
        comps.path = "/cam.cgi"
        var items: [URLQueryItem] = []
        items.append(URLQueryItem(name: "mode", value: cmd.mode))
        if let t = cmd.type { items.append(URLQueryItem(name: "type", value: t)) }
        if let v = cmd.value { items.append(URLQueryItem(name: "value", value: v)) }
        if let v2 = cmd.value2 { items.append(URLQueryItem(name: "value2", value: v2)) }
        comps.queryItems = items
        return comps.url
    }

    // MARK: Low-level request

    struct Response {
        let status: Int
        let data: Data
        let headers: [String: String]
        let elapsed: TimeInterval
        var body: String { String(data: data, encoding: .utf8) ?? String(data: data, encoding: .isoLatin1) ?? "" }

        var contentType: String { headers["content-type"] ?? "" }
        var isBinary: Bool {
            contentType.contains("octet-stream") || data.contains(where: { $0 > 0x7F })
        }
    }

    /// Per-command timeout per PROTOCOL_AUDIT §1.
    private static func timeout(for mode: String) -> TimeInterval {
        switch mode {
        case "camcmd", "camctrl", "getstate", "get_content_info": return 3
        case "playcmd": return 10
        default: return 10
        }
    }

    private func request(_ cmd: LumixCommand,
                         method: String = "GET",
                         port: Int = 80,
                         extraHeaders: [String: String] = [:],
                         logIt: Bool = true) async throws -> Response {
        guard let url = url(for: cmd, port: port) else { throw LumixError.badURL }
        var req = URLRequest(url: url)
        req.httpMethod = method
        req.timeoutInterval = Self.timeout(for: cmd.mode)
        req.setValue(Self.userAgent, forHTTPHeaderField: "User-Agent")
        for (k, v) in extraHeaders { req.setValue(v, forHTTPHeaderField: k) }

        if logIt { log?.append(.request, "GET /cam.cgi?\(cmd.query)") }

        let start = Date()
        let (data, resp) = try await session.data(for: req)
        let elapsed = Date().timeIntervalSince(start)
        let http = resp as? HTTPURLResponse
        let status = http?.statusCode ?? 0
        var headers: [String: String] = [:]
        for (k, v) in http?.allHeaderFields ?? [:] {
            if let k = k as? String { headers[k.lowercased()] = "\(v)" }
        }
        let r = Response(status: status, data: data, headers: headers, elapsed: elapsed)

        if logIt {
            if r.isBinary {
                let hex = data.prefix(16).map { String(format: "%02X", $0) }.joined(separator: " ")
                log?.append(.response, "HTTP \(status) · \(data.count) B (binary) · \(hex)…")
            } else {
                let preview = r.body
                    .replacingOccurrences(of: "\r\n", with: " ")
                    .replacingOccurrences(of: "\n", with: " ")
                    .trimmingCharacters(in: .whitespaces)
                log?.append(.response, "HTTP \(status) · \(data.count) B · \(String(format: "%.0f", elapsed * 1000)) ms · \(preview.prefix(500))")
            }
        }
        return r
    }

    // A single cam.cgi call with err_busy retry (protocol: up to 5 retries, 1s backoff).
    private func call(_ cmd: LumixCommand,
                      retries: Int = 5,
                      backoff: TimeInterval = 1.0,
                      logIt: Bool = true) async throws -> Response {
        var last = try await request(cmd, logIt: logIt)
        for _ in 0..<retries {
            if last.body.contains("err_busy") {
                try await Task.sleep(nanoseconds: UInt64(backoff * 1_000_000_000))
                last = try await request(cmd, logIt: false) // retries are noisy; log only the first
            } else {
                break
            }
        }
        return last
    }

    // MARK: - Camera state

    func getstate(logIt: Bool = true) async throws -> CameraState {
        let r = try await call(LumixCommand(mode: "getstate"), logIt: logIt)
        return Self.parseState(r.body)
    }

    static func parseState(_ xml: String) -> CameraState {
        var s = CameraState(ok: false)
        s.ok = xml.contains("<result>ok</result>") || xml.contains("ok")
        func tag(_ name: String) -> String {
            let open = "<\(name)>"
            let close = "</\(name)>"
            guard let a = xml.range(of: open), let b = xml.range(of: close), a.lowerBound < b.lowerBound else { return "" }
            return String(xml[a.upperBound..<b.lowerBound]).trimmingCharacters(in: .whitespacesAndNewlines)
        }
        s.battery = tag("batt")
        if let p = Int(tag("batt_per")) { s.batteryPercent = p }
        s.camMode = tag("cammode")
        s.sdCardStatus = tag("sdcardstatus")
        s.sd2CardStatus = tag("sd2_cardstatus")
        s.currentSD = tag("current_sd")
        s.version = tag("version")
        s.play = tag("play")
        s.temperature = tag("temperature")
        s.lens = tag("lens")
        s.sdFull = tag("sd_full") == "true"
        s.sd2Full = tag("sd2_full") == "true"
        return s
    }

    // MARK: - Capability / info

    func getinfo(_ type: String) async throws -> String {
        let r = try await call(LumixCommand(mode: "getinfo", type: type))
        return r.body
    }

    func capability() async throws -> String { try await getinfo("capability") }

    /// Read the camera settings partition (65,533 bytes, binary).
    /// Verified oracle: getinfo camsetting returns live partition data.
    func getCamsetting() async throws -> Data {
        let r = try await call(LumixCommand(mode: "getinfo", type: "camsetting"))
        return r.data
    }

    // MARK: - Shutter / control

    /// Remote shutter (standard Lumix remote-release command).
    func shoot() async throws {
        _ = try await call(LumixCommand(mode: "camcmd", type: "shoot"))
    }

    func power(on: Bool) async throws {
        _ = try await call(LumixCommand(mode: "camcmd", type: on ? "poweron" : "poweroff"))
    }

    /// Switch camera mode: "shoot" (still), "movie", "play" (review), etc.
    func setCameraMode(_ mode: String) async throws {
        _ = try await call(LumixCommand(mode: "camcmd", type: mode))
    }

    // MARK: - camctrl (focus / lock / play / probes)

    /// Focus: value in { wide, normal, tele, stop }.
    func focus(_ value: String) async throws {
        _ = try await call(LumixCommand(mode: "camctrl", type: "focus", value: value))
    }

    /// AF/AE lock on/off.
    func afAELock(on: Bool) async throws {
        _ = try await call(LumixCommand(mode: "camctrl", type: "af_ae_lock", value: on ? "on" : "off"))
    }

    /// Review-mode playback: start / pause / stop.
    func play(_ cmd: String) async throws {
        _ = try await call(LumixCommand(mode: "playcmd", type: cmd))
    }

    /// Firmware version gate probe (read-only): returns err_fw_same / err_fw_old / ok.
    func fwVersionGate(_ version: String) async throws -> String {
        let r = try await call(LumixCommand(mode: "camctrl", type: "fw_update_mode", value: version))
        return Self.resultValue(r.body)
    }

    /// Research-session handshake probe. S5 answers 4 fields, no session token.
    func accProbe(deviceName: String) async throws -> String {
        let r = try await call(LumixCommand(mode: "accctrl", type: "req_acc", value: deviceName))
        return r.body
    }

    // MARK: - Settings

    func setSetting(_ key: String, _ value: String) async throws {
        _ = try await call(LumixCommand(mode: "setsetting", type: key, value: value))
    }

    func getSetting(_ key: String) async throws -> String {
        let r = try await call(LumixCommand(mode: "getsetting", type: key))
        // Response is CSV: "ok,<value>"
        let parts = r.body.split(separator: ",").map { $0.trimmingCharacters(in: .whitespaces) }
        return parts.count >= 2 ? parts[1] : r.body
    }

    // MARK: - Content / transfer

    func getContentInfo(_ dirID: String) async throws -> String {
        // dir_id literal goes in `value`, `type` omitted (PROTOCOL_AUDIT §2.4)
        let r = try await call(LumixCommand(mode: "get_content_info", value: dirID))
        return r.body
    }

    func getProgress() async throws -> LumixProgress {
        // No type param (PROTOCOL_AUDIT §2.5). CSV: status,percent
        let r = try await call(LumixCommand(mode: "getprogress"))
        let parts = r.body.split(separator: ",").map { $0.trimmingCharacters(in: .whitespaces) }
        var p = LumixProgress(status: parts.first ?? r.body)
        if parts.count >= 2, let n = Int(parts[1]) { p.percent = n }
        return p
    }

    func transferNotify() async throws {
        _ = try await call(LumixCommand(mode: "notify", type: "transfer"))
    }

    // MARK: - Live view (official UDP startstream)

    /// Start the official UDP live-view stream to the given port.
    /// The phone must already have bound the UDP socket to this port.
    func startStream(port: Int) async throws -> String {
        let r = try await call(LumixCommand(mode: "startstream", value: String(port)))
        return r.body
    }

    /// Stop the live-view stream.
    func stopStream() async throws -> String {
        let r = try await call(LumixCommand(mode: "stopstream"))
        return r.body
    }

    // MARK: - Raw command (research console)

    /// Execute an arbitrary cam.cgi query string, e.g.
    /// `mode=camctrl&type=af_ae_lock&value=on`. Full response text returned.
    func rawCommand(_ query: String) async throws -> String {
        guard let url = URL(string: "http://\(ip)/cam.cgi?\(query)") else { throw LumixError.badURL }
        var req = URLRequest(url: url)
        req.timeoutInterval = 10
        req.setValue(Self.userAgent, forHTTPHeaderField: "User-Agent")
        log?.append(.request, "GET /cam.cgi?\(query)   [raw]")
        let start = Date()
        let (data, resp) = try await session.data(for: req)
        let elapsed = Date().timeIntervalSince(start)
        let status = (resp as? HTTPURLResponse)?.statusCode ?? 0
        let body = String(data: data, encoding: .utf8) ?? String(data: data, encoding: .isoLatin1) ?? ""
        let preview = body.replacingOccurrences(of: "\r\n", with: " ").trimmingCharacters(in: .whitespaces)
        log?.append(.response, "HTTP \(status) · \(data.count) B · \(String(format: "%.0f", elapsed * 1000)) ms · \(preview.prefix(500))")
        return body
    }

    // MARK: - Response classification

    /// Extract the `<result>` value from a cam.cgi XML response body.
    /// Falls back to the first CSV token (e.g. `ok`) for non-XML replies.
    static func resultValue(_ body: String) -> String {
        let open = "<result>", close = "</result>"
        if let a = body.range(of: open), let b = body.range(of: close), a.lowerBound < b.lowerBound {
            return String(body[a.upperBound..<b.lowerBound]).trimmingCharacters(in: .whitespacesAndNewlines)
        }
        let t = body.trimmingCharacters(in: .whitespacesAndNewlines)
        let first = t.split(whereSeparator: { $0 == "\n" || $0 == "," || $0 == " " }).first.map(String.init) ?? t
        return first
    }

    /// True when the camera is in a mode that has no live-view finder
    /// (review / menu / setting / off). In these modes `startstream` is rejected.
    static func isLiveViewBlockingMode(_ camMode: String) -> Bool {
        switch camMode.trimmingCharacters(in: .whitespacesAndNewlines).lowercased() {
        case "play", "menu", "setting", "off":
            return true
        default:
            return false
        }
    }

    // MARK: - Live view (HTTP JPEG polling, fallback only)

    /// Candidate live-view JPEG endpoints, tried in order (S/M/L sizes).
    static let liveViewPaths = ["/liveview_s.jpg", "/liveview_m.jpg", "/liveview_l.jpg", "/img/0.jpg"]

    /// Fetch one live-view JPEG frame from a specific endpoint.
    func liveViewFrame(path: String) async -> Data? {
        guard let url = URL(string: "http://\(ip)\(path)") else { return nil }
        var req = URLRequest(url: url)
        req.setValue(Self.userAgent, forHTTPHeaderField: "User-Agent")
        req.cachePolicy = .reloadIgnoringLocalCacheData
        do {
            let (data, resp) = try await session.data(for: req)
            let http = resp as? HTTPURLResponse
            if http?.statusCode == 200, data.count > 100, data.jpegMagic() {
                return data
            }
        } catch {
            // fall through
        }
        return nil
    }

    /// Try all known endpoints in order (auto mode).
    func liveViewFrame() async -> Data? {
        for path in Self.liveViewPaths {
            if let d = await liveViewFrame(path: path) { return d }
        }
        return nil
    }
}

// MARK: - Errors

enum LumixError: LocalizedError {
    case badURL
    case unreachable
    case server(Int, String)

    var errorDescription: String? {
        switch self {
        case .badURL: return "无效的相机地址"
        case .unreachable: return "无法连接相机"
        case .server(let code, let body): return "相机返回错误 (HTTP \(code)): \(body.prefix(120))"
        }
    }
}

// MARK: - Helpers

extension Data {
    /// JPEG magic bytes (FFD8FF).
    func jpegMagic() -> Bool {
        let b = [UInt8](self.prefix(3))
        return b.count == 3 && b[0] == 0xFF && b[1] == 0xD8 && b[2] == 0xFF
    }

    /// CAMSET checksum (verified): the whole block must sum to 0 mod 256,
    /// i.e. checksum = 256 - (Σ first N-1 bytes) mod 256.
    var camsettingChecksum: UInt8 {
        guard count > 1 else { return 0 }
        var sum: UInt64 = 0
        for i in 0..<(count - 1) { sum += UInt64(self[i]) }
        let last = self[count - 1]
        return UInt8((sum + UInt64(last)) % 256 == 0 ? last : 0)
    }

    /// True when the block sums to 0 mod 256 (valid CAMSET checksum).
    var camsettingChecksumValid: Bool {
        guard count > 1 else { return false }
        var sum: UInt64 = 0
        for b in self { sum += UInt64(b) }
        return sum % 256 == 0
    }
}
