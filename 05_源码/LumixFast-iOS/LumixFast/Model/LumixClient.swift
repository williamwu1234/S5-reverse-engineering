 // LumixClient.swift
 //
 // HTTP client for the Panasonic Lumix camera control protocol (`/cam.cgi`).
 // Reverse-engineered from com.panasonic.jp.lumixsync (LUMIX Sync) and verified
 // against live DC-S5 responses (see research in com.panasonic.jp.lumixsync_b0834c31).
 //
 // Transport: plain HTTP on port 80. No auth, no session token on DC-S5.
 // User-Agent MUST be exactly "LUMIX Sync".
 //
 import Foundation

 // MARK: - Command description

 struct LumixCommand: Hashable {
     let mode: String
     var type: String? = nil
     var value: String? = nil
     var value2: String? = nil
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
 }

 // MARK: - Client

 final class LumixClient: NSObject {

    static let userAgent = "LUMIX Sync"

    let ip: String
    private let session: URLSession
    private let xmlParser: XMLParserDelegateCapture

    init(ip: String) {
        self.ip = ip
        let config = URLSessionConfiguration.ephemeral
        config.timeoutIntervalForRequest = 10
        config.timeoutIntervalForResource = 30
        config.requestCachePolicy = .reloadIgnoringLocalCacheData
        config.waitsForConnectivity = false
        self.session = URLSession(configuration: config)
        self.xmlParser = XMLParserDelegateCapture()
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
        var body: String { String(data: data, encoding: .utf8) ?? String(data: data, encoding: .isoLatin1) ?? "" }
    }

    private func request(_ cmd: LumixCommand,
                         method: String = "GET",
                         port: Int = 80,
                         extraHeaders: [String: String] = [:]) async throws -> Response {
        guard let url = url(for: cmd, port: port) else { throw LumixError.badURL }
        var req = URLRequest(url: url)
        req.httpMethod = method
        req.setValue(Self.userAgent, forHTTPHeaderField: "User-Agent")
        for (k, v) in extraHeaders { req.setValue(v, forHTTPHeaderField: k) }
        let (data, resp) = try await session.data(for: req)
        let http = resp as? HTTPURLResponse
        let status = http?.statusCode ?? 0
        var headers: [String: String] = [:]
        for (k, v) in http?.allHeaderFields ?? [:] {
            if let k = k as? String { headers[k.lowercased()] = "\(v)" }
        }
        return Response(status: status, data: data, headers: headers)
    }

    // A single cam.cgi call with err_busy retry (protocol: up to 5 retries, 1s backoff).
    private func call(_ cmd: LumixCommand,
                      retries: Int = 5,
                      backoff: TimeInterval = 1.0) async throws -> Response {
        var last = try await request(cmd)
        for _ in 0..<retries {
            if last.body.contains("err_busy") {
                try await Task.sleep(nanoseconds: UInt64(backoff * 1_000_000_000))
                last = try await request(cmd)
            } else {
                break
            }
        }
        return last
    }

    // MARK: - Camera state

    func getstate() async throws -> CameraState {
        let r = try await call(LumixCommand(mode: "getstate"))
        return Self.parseState(r.body)
    }

    /// Keep-alive / liveness probe.
    func keepAlive() async throws -> Bool {
        let r = try await call(LumixCommand(mode: "getstate", type: "keep_alive"))
        return r.body.contains("ok")
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

    // MARK: - Focus

    /// Focus: value in { tele, wide, normal, fast, stop }.
    func focus(_ value: String) async throws {
        _ = try await call(LumixCommand(mode: "camctrl", type: "focus", value: value))
    }

    // MARK: - Content / transfer notifications

    func getContentInfo(_ dirID: String) async throws -> String {
        // dir_id literal goes in `value`, `type` omitted (per PROTOCOL_AUDIT §2.4)
        let r = try await call(LumixCommand(mode: "get_content_info", value: dirID))
        return r.body
    }

    func transferNotify() async throws {
        _ = try await call(LumixCommand(mode: "notify", type: "transfer"))
    }

    // MARK: - Live view (official UDP startstream)

    /// Start the official UDP live-view stream to the given port.
    /// The phone must already have bound the UDP socket to this port.
    /// Response body is `ok` on success; `err_busy` on contention (auto-retried by `call`).
    func startStream(port: Int) async throws -> String {
        let r = try await call(LumixCommand(mode: "startstream", value: String(port)))
        return r.body
    }

    /// Stop the live-view stream.
    func stopStream() async throws -> String {
        let r = try await call(LumixCommand(mode: "stopstream"))
        return r.body
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

    /// Human-readable, actionable Chinese message for a camera command result.
    /// `camMode` (e.g. "play", "shoot", "movie") sharpens the `err_reject` guidance.
    static func friendlyMessage(result: String, camMode: String?) -> String {
        switch result.lowercased() {
        case "ok":
            return "成功"
        case "err_reject":
            let m = (camMode ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
            let modeText: String
            switch m.lowercased() {
            case "play": modeText = "回放(PLAY)模式"
            case "menu": modeText = "菜单模式"
            case "setting": modeText = "设置模式"
            case "off": modeText = "已关机"
            case "": modeText = "无法确认的当前模式"
            default: modeText = "\(m) 模式"
            }
            return "相机拒绝启动实时取景（当前：\(modeText)）。请在相机上按 REC 键切换到拍照或录像模式，应用会自动重连。"
        case "err_busy":
            return "相机正忙，稍后自动重试…"
        case "err_critical":
            return "相机出现严重错误，请检查相机后重试。"
        case "err_param":
            return "指令参数错误。"
        case "err_system_error":
            return "相机系统错误。"
        case "err_temperature":
            return "相机温度异常，请等待温度恢复后再试。"
        case "err_wifi_connecting":
            return "相机 Wi-Fi 正在连接中，请稍候。"
        case "err_noremain":
            return "相机剩余电量不足。"
        case "err_sdcard_write_protected":
            return "SD 卡处于写保护状态。"
        case "err_no_media":
            return "相机未检测到存储卡。"
        case "err_sdcard_access":
            return "SD 卡访问错误。"
        default:
            return "相机返回错误：\(result)"
        }
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

    /// Candidate live-view JPEG endpoints, tried in order.
    static let liveViewPaths = ["/liveview_s.jpg", "/liveview_m.jpg", "/liveview_l.jpg", "/img/0.jpg"]

    /// Fetch one live-view JPEG frame. Returns nil if no endpoint yields a JPEG.
    func liveViewFrame() async -> Data? {
        for path in Self.liveViewPaths {
            guard let url = URL(string: "http://\(ip)\(path)") else { continue }
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
                continue
            }
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
 }

 // Minimal XML element capture used only for lightweight parsing.
 final class XMLParserDelegateCapture: NSObject, XMLParserDelegate {
     var lastElement = ""
     var lastText = ""
     func parser(_ parser: XMLParser, didStartElement name: String, namespaceURI: String?, qualifiedName: String?, attributes: [String: String]) {
         lastElement = name
     }
     func parser(_ parser: XMLParser, foundCharacters string: String) {
         lastText += string
     }
 }
