// AppModel.swift
//
// Central view model: connection (+ auto-reconnect), camera state polling,
// UDP/HTTP live view, remote control, settings, gallery (DLNA),
// research monitor (command log, raw console, CAMSET partition reader),
// and saving to the Photos library.
//
import SwiftUI
import Photos
import os

@MainActor
final class AppModel: ObservableObject {

    // MARK: Tabs

    enum Tab: Int, CaseIterable {
        case dashboard, live, control, gallery, monitor
    }
    @Published var activeTab: Tab = .dashboard

    // MARK: Connection

    @Published var ip: String = ""
    @Published var isConnected: Bool = false
    @Published var isConnecting: Bool = false
    @Published var isReconnecting: Bool = false
    @Published var statusMessage: String = ""
    @Published var errorMessage: String = ""
    @Published var lastLatency: TimeInterval = -1
    @Published var lastStateUpdate: Date?

    // MARK: Camera state

    @Published var state: CameraState?

    // MARK: Live view

    enum LiveViewMode: String, CaseIterable, Identifiable {
        case udp, httpS, httpM, httpL
        var id: String { rawValue }
        var label: String {
            switch self {
            case .udp: return "UDP 官方"
            case .httpS: return "HTTP·S"
            case .httpM: return "HTTP·M"
            case .httpL: return "HTTP·L"
            }
        }
    }

    @Published var liveMode: LiveViewMode = .udp
    @Published var liveFrame: UIImage?
    @Published var liveViewActive: Bool = false
    @Published var liveViewBlocked: String = ""
    @Published var debugInfo: String = ""
    @Published var udpStats: UDPLiveViewStats?

    // MARK: Control (transient result line)

    @Published var controlResult: String = ""

    // MARK: Settings

    @Published var settings: [String: String] = [:]
    @Published var capabilityRaw: String = ""
    @Published var settingsBusy: Bool = false

    // MARK: Gallery (DLNA)

    @Published var files: [LumixFileItem] = []
    @Published var browsingPath: [LumixFileItem] = []
    @Published var galleryBusy: Bool = false
    @Published var downloading: Bool = false
    @Published var thumbnailCache: [String: UIImage] = [:]

    // MARK: Research monitor

    let commandLog = CommandLog()
    @Published var logEntries: [LogEntry] = []
    @Published var rawQuery: String = ""
    @Published var rawBusy: Bool = false
    @Published var rawResult: String = ""

    @Published var camsettingBusy: Bool = false
    @Published var camsettingData: Data?
    @Published var camsettingError: String = ""
    @Published var exportedFileURL: URL?
    @Published var showExport: Bool = false
    @Published var showSettings: Bool = false

    /// Live-view quality preset label shown in UI (kept in sync with liveMode).
    @Published var showLiveDebug: Bool = true

    // MARK: Private

    private var client: LumixClient?
    private var dlna: LumixDLNA?
    private var stateTask: Task<Void, Never>?
    private var pollFailures = 0

    // UDP live-view
    private var udp: LumixUDPLiveView?
    private var httpPollTask: Task<Void, Never>?
    private var watchdogTask: Task<Void, Never>?
    private var streamGen = 0
    private var lastFrameAt = Date.distantPast
    private var lastRestartAt = Date.distantPast
    private var restartCount = 0
    private var establishAttempts = 0

    private let log = Logger(subsystem: "com.lumixmonitor.ios", category: "AppModel")

    // MARK: - Connection

    func connect(ip: String, name: String? = nil) async {
        self.ip = ip.trimmingCharacters(in: .whitespaces)
        guard !self.ip.isEmpty else { return }
        isConnecting = true
        isReconnecting = false
        errorMessage = ""
        statusMessage = "正在连接 \(ip) …"
        let c = LumixClient(ip: self.ip, log: commandLog)
        do {
            let start = Date()
            let s = try await c.getstate()
            let latency = Date().timeIntervalSince(start)
            self.client = c
            self.dlna = LumixDLNA(ip: self.ip)
            self.state = s
            self.lastLatency = latency
            self.lastStateUpdate = Date()
            self.pollFailures = 0
            self.isConnected = true
            self.statusMessage = "已连接：\(s.version) · 电池 \(s.batteryDisplay) · \(s.camMode)"
            commandLog.append(.request, "── 已连接 \(self.ip) (UA: LUMIX Sync) ──")
            // Remember this camera for one-tap reconnect and as an App-Intent entity.
            CameraStore.shared.upsert(ip: self.ip, name: name)
            startStatePolling()
        } catch {
            self.isConnected = false
            self.errorMessage = "连接失败：\(error.localizedDescription)"
            self.statusMessage = ""
        }
        isConnecting = false
    }

    func disconnect() {
        stopLiveView()
        stateTask?.cancel()
        stateTask = nil
        client = nil
        dlna = nil
        pollFailures = 0
        isReconnecting = false
        isConnected = false
        state = nil
        files = []
        browsingPath = []
        thumbnailCache = [:]
        settings = [:]
        capabilityRaw = ""
        statusMessage = ""
        commandLog.append(.request, "── 已断开连接 ──")
    }

    // MARK: State polling (+ auto-reconnect)

    private func startStatePolling() {
        stateTask?.cancel()
        stateTask = Task { [weak self] in
            while !Task.isCancelled {
                guard let self else { return }
                guard let c = self.client, self.isConnected else {
                    try? await Task.sleep(nanoseconds: 2_000_000_000)
                    continue
                }
                do {
                    let start = Date()
                    let s = try await c.getstate(logIt: false) // keep the log clean
                    self.state = s
                    self.lastLatency = Date().timeIntervalSince(start)
                    self.lastStateUpdate = Date()
                    self.pollFailures = 0
                    if self.isReconnecting {
                        self.isReconnecting = false
                        self.statusMessage = "连接已恢复"
                        self.log.info("connection restored")
                    }
                } catch {
                    self.pollFailures += 1
                    // Camera drops on Wi-Fi are common (verified in research);
                    // after 3 consecutive failures we flag the link and try to
                    // re-establish a fresh client automatically.
                    if self.pollFailures == 3 {
                        self.isReconnecting = true
                        self.log.warning("connection lost, auto-reconnect started")
                    }
                    if self.pollFailures >= 3 && self.pollFailures % 2 == 1 {
                        await self.connect(ip: self.ip)
                    }
                }
                try? await Task.sleep(nanoseconds: 2_000_000_000)
            }
        }
    }

    // MARK: Live view

    func startLiveView() {
        guard client != nil else { return }
        teardownStream()
        liveViewActive = true
        liveFrame = nil
        restartCount = 0
        establishAttempts = 0
        liveViewBlocked = ""
        if liveMode == .udp {
            debugInfo = "正在启动 UDP 取景…"
            startWatchdog()
            Task { await establishStream() }
        } else {
            startHTTPPolling()
        }
    }

    func stopLiveView() {
        teardownStream()
    }

    func switchLiveMode(_ mode: LiveViewMode) {
        guard mode != liveMode else { return }
        let wasActive = liveViewActive
        liveMode = mode
        if wasActive {
            teardownStream()
            startLiveView()
        }
    }

    /// Tear down the current stream and ask the camera to stop pushing.
    private func teardownStream() {
        streamGen += 1
        liveViewActive = false
        liveViewBlocked = ""
        watchdogTask?.cancel()
        watchdogTask = nil
        httpPollTask?.cancel()
        httpPollTask = nil
        udp?.stop()
        udp = nil
        if let c = client {
            Task { _ = try? await c.stopStream() }
        }
    }

    // MARK: UDP stream

    private func establishStream(restart: Bool = false) async {
        guard let c = client else { return }
        let gen = streamGen
        udp?.stop()

        let v = LumixUDPLiveView(ip: ip)
        v.onFrame = { [weak self] data in
            DispatchQueue.main.async {
                guard let self, self.streamGen == gen else { return }
                if let img = UIImage(data: data) {
                    self.liveFrame = img
                    self.lastFrameAt = Date()
                    self.restartCount = 0
                }
            }
        }
        v.onStats = { [weak self] stats in
            DispatchQueue.main.async {
                guard let self, self.streamGen == gen else { return }
                self.udpStats = stats
            }
        }
        v.onLog = { [weak self] msg in
            DispatchQueue.main.async {
                guard let self, self.streamGen == gen else { return }
                self.debugInfo = msg
            }
        }

        let port = v.bind()
        guard port > 0 else {
            debugInfo = "UDP 绑定失败"
            log.error("UDP bind failed")
            return
        }

        if restart {
            _ = try? await c.stopStream()
            try? await Task.sleep(nanoseconds: 400_000_000)
        }

        do {
            var body = try await c.startStream(port: Int(port))
            if body.contains("err_busy") {
                log.warning("startstream err_busy; force-stopping and retrying")
                _ = try? await c.stopStream()
                try? await Task.sleep(nanoseconds: 500_000_000)
                body = try await c.startStream(port: Int(port))
            }
            guard streamGen == gen else { return }
            if body.contains("ok") {
                udp = v
                v.start()
                lastRestartAt = Date()
                restartCount += 1
                establishAttempts = 0
                liveViewBlocked = ""
                debugInfo = "已连接 UDP 取景流 · 端口 \(port)"
                log.info("UDP live view connected on port \(port)")
            } else {
                let result = LumixClient.resultValue(body)
                if let s = try? await c.getstate(), streamGen == gen {
                    self.state = s
                    self.liveViewBlocked = Self.rejectMessage(result: result, camMode: s.camMode)
                } else {
                    self.liveViewBlocked = Self.rejectMessage(result: result, camMode: self.state?.camMode)
                }
                self.debugInfo = "startstream 被拒绝（\(result)）"
                log.error("startstream failed: \(body.prefix(200))")
            }
        } catch {
            guard streamGen == gen else { return }
            debugInfo = "startstream 异常: \(error.localizedDescription)"
            log.error("startstream threw: \(error.localizedDescription)")
        }
    }

    /// Watchdog: if no frame arrives for a while, restart (bounded); if not
    /// connected, re-check the camera mode and self-heal.
    private func startWatchdog() {
        watchdogTask?.cancel()
        watchdogTask = Task { [weak self] in
            while !Task.isCancelled {
                try? await Task.sleep(nanoseconds: 3_000_000_000)
                guard let self else { return }
                guard self.liveViewActive, self.liveMode == .udp else { continue }
                let now = Date()

                if self.udp != nil {
                    if now.timeIntervalSince(self.lastFrameAt) > 8,
                       now.timeIntervalSince(self.lastRestartAt) > 10,
                       self.restartCount < 8 {
                        self.debugInfo = "取景流静默…重连中"
                        await self.establishStream(restart: true)
                    }
                } else if self.establishAttempts < 60 {
                    if let s = try? await self.client?.getstate() {
                        self.state = s
                        if LumixClient.isLiveViewBlockingMode(s.camMode) {
                            self.liveViewBlocked = Self.rejectMessage(result: "err_reject", camMode: s.camMode)
                            self.debugInfo = "等待相机切换到拍摄/录像模式…"
                        } else {
                            self.establishAttempts += 1
                            await self.establishStream(restart: false)
                        }
                    }
                }
            }
        }
    }

    // MARK: HTTP polling fallback

    private var httpPath: String {
        switch liveMode {
        case .httpS: return "/liveview_s.jpg"
        case .httpM: return "/liveview_m.jpg"
        case .httpL: return "/liveview_l.jpg"
        default: return "/liveview_s.jpg"
        }
    }

    private var httpInterval: Double {
        switch liveMode {
        case .httpS: return 0.4
        case .httpM: return 0.6
        case .httpL: return 0.9
        default: return 0.4
        }
    }

    private func startHTTPPolling() {
        httpPollTask?.cancel()
        debugInfo = "HTTP 轮询取景（\(liveMode.label)）"
        httpPollTask = Task { [weak self] in
            let interval = self?.httpInterval ?? 0.5
            while !Task.isCancelled {
                guard let self, let c = self.client, self.liveViewActive else { return }
                if let data = await c.liveViewFrame(path: self.httpPath),
                   let img = UIImage(data: data) {
                    self.liveFrame = img
                    self.lastFrameAt = Date()
                }
                try? await Task.sleep(nanoseconds: UInt64(interval * 1_000_000_000))
            }
        }
    }

    static func rejectMessage(result: String, camMode: String?) -> String {
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
        if result.lowercased() == "err_reject" {
            return "相机拒绝启动实时取景（当前：\(modeText)）。请在相机上按 REC 键切换到拍照或录像模式，应用会自动重连。"
        }
        switch result.lowercased() {
        case "ok": return "成功"
        case "err_busy": return "相机正忙，稍后自动重试…"
        case "err_critical": return "相机出现严重错误，请检查相机后重试。"
        case "err_param": return "指令参数错误。"
        case "err_system_error": return "相机系统错误。"
        case "err_temperature": return "相机温度异常，请等待温度恢复后再试。"
        case "err_wifi_connecting": return "相机 Wi-Fi 正在连接中，请稍候。"
        case "err_noremain": return "相机剩余电量不足。"
        case "err_no_media": return "相机未检测到存储卡。"
        default: return "相机返回：\(result)（当前：\(modeText)）"
        }
    }

    // MARK: Shutter / control

    func shoot() async {
        guard let c = client else { return }
        do {
            statusMessage = "拍摄中…"
            try await c.shoot()
            statusMessage = "已发送快门指令"
            controlResult = "快门 ✓"
        } catch {
            errorMessage = "快门失败：\(error.localizedDescription)"
            controlResult = "快门 ✗ \(error.localizedDescription)"
        }
    }

    func power(on: Bool) async {
        guard let c = client else { return }
        do {
            try await c.power(on: on)
            controlResult = on ? "开机指令 ✓" : "关机指令 ✓"
        } catch {
            controlResult = "电源指令 ✗"
        }
    }

    func setCameraMode(_ mode: String) async {
        guard let c = client else { return }
        do {
            try await c.setCameraMode(mode)
            controlResult = "已切换模式：\(mode)"
        } catch {
            controlResult = "模式切换 ✗（相机可能拒绝当前操作）"
        }
    }

    func focus(_ value: String) async {
        guard let c = client else { return }
        do {
            try await c.focus(value)
            controlResult = "对焦：\(value) ✓"
        } catch {
            controlResult = "对焦 ✗"
        }
    }

    func afAELock(on: Bool) async {
        guard let c = client else { return }
        do {
            try await c.afAELock(on: on)
            controlResult = on ? "AF/AE 锁定 ✓" : "AF/AE 解锁 ✓"
        } catch {
            controlResult = "AF/AE 锁定 ✗"
        }
    }

    func play(_ cmd: String) async {
        guard let c = client else { return }
        do {
            try await c.play(cmd)
            controlResult = "回放 \(cmd) ✓"
        } catch {
            controlResult = "回放 \(cmd) ✗"
        }
    }

    // MARK: Settings

    static let settingKeys = ["photostyle", "colormode", "peaking", "current_sd", "device_name", "raw_img_send"]

    func refreshSettings() async {
        guard let c = client else { return }
        settingsBusy = true
        for key in Self.settingKeys {
            if let v = try? await c.getSetting(key) {
                settings[key] = v
            }
        }
        if let cap = try? await c.capability() {
            capabilityRaw = cap
        }
        settingsBusy = false
    }

    func setSetting(_ key: String, _ value: String) async {
        guard let c = client else { return }
        do {
            try await c.setSetting(key, value)
            settings[key] = value
            controlResult = "\(key) = \(value) ✓"
            statusMessage = "\(key) = \(value)"
        } catch {
            controlResult = "\(key) 写入 ✗"
        }
    }

    // MARK: Gallery (DLNA)

    func loadGallery() async {
        guard let d = dlna else { return }
        galleryBusy = true
        files = []
        browsingPath = []
        do {
            let root = try await d.browse(objectID: "0")
            files = root
            await loadThumbnails(for: root)
        } catch {
            errorMessage = "浏览失败：\(error.localizedDescription)"
        }
        galleryBusy = false
    }

    func openContainer(_ item: LumixFileItem) async {
        guard let d = dlna else { return }
        do {
            let children = try await d.browse(objectID: item.id)
            browsingPath.append(item)
            files = children
            await loadThumbnails(for: children)
        } catch {
            errorMessage = "进入目录失败：\(error.localizedDescription)"
        }
    }

    func goUp() {
        guard let last = browsingPath.popLast() else {
            Task { await loadGallery() }
            return
        }
        files = []
        Task {
            guard let d = dlna else { return }
            if let kids = try? await d.browse(objectID: last.parentID) {
                self.files = kids
                await self.loadThumbnails(for: kids)
            }
        }
    }

    private func loadThumbnails(for items: [LumixFileItem]) async {
        guard let d = dlna else { return }
        let media = items.filter { $0.isMedia && $0.res != nil }
        for item in media {
            guard let res = item.res, thumbnailCache[item.id] == nil else { continue }
            if let (data, _) = try? await d.download(resURL: res, convert: .small),
               let img = UIImage(data: data) {
                thumbnailCache[item.id] = img
            }
        }
    }

    func download(_ item: LumixFileItem) async {
        guard let d = dlna, let res = item.res else { return }
        downloading = true
        do {
            let (data, _) = try await d.download(resURL: res)
            let saved = await saveToPhotos(data, name: item.title)
            statusMessage = saved ? "已保存：\(item.title)" : "保存失败（请检查相册权限）"
        } catch {
            errorMessage = "下载失败：\(error.localizedDescription)"
        }
        downloading = false
    }

    // MARK: Research monitor

    func runRawCommand() async {
        let q = rawQuery.trimmingCharacters(in: .whitespaces)
        guard !q.isEmpty, let c = client else { return }
        rawBusy = true
        rawResult = ""
        do {
            rawResult = try await c.rawCommand(q)
        } catch {
            rawResult = "请求失败：\(error.localizedDescription)"
        }
        rawBusy = false
    }

    func readCamsetting() async {
        guard let c = client else { return }
        camsettingBusy = true
        camsettingError = ""
        do {
            camsettingData = try await c.getCamsetting()
        } catch {
            camsettingError = "读取失败：\(error.localizedDescription)"
        }
        camsettingBusy = false
    }

    /// Write the CAMSET data to a temporary file for the share/export sheet.
    func exportCamsetting() {
        guard let data = camsettingData else { return }
        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent("CAMSET01_\(ip.replacingOccurrences(of: ".", with: "_")).dat")
        try? data.write(to: url)
        exportedFileURL = url
        showExport = true
    }

    // MARK: Photos

    func requestPhotoPermission() async -> Bool {
        switch PHPhotoLibrary.authorizationStatus(for: .addOnly) {
        case .notDetermined:
            return await PHPhotoLibrary.requestAuthorization(for: .addOnly) == .authorized
        case .authorized, .limited:
            return true
        default:
            return false
        }
    }

    private func saveToPhotos(_ data: Data, name: String) async -> Bool {
        guard UIImage(data: data) != nil else { return false }
        return await withCheckedContinuation { cont in
            PHPhotoLibrary.shared().performChanges {
                let req = PHAssetCreationRequest.forAsset()
                req.addResource(with: .photo, data: data, options: nil)
            } completionHandler: { success, _ in
                cont.resume(returning: success)
            }
        }
    }
}
