 // AppModel.swift
 //
 // Central view model: connection, live view, camera state, shutter,
 // settings, gallery (DLNA) and saving to the Photos library.
 //
 import SwiftUI
 import Photos
 import Combine
import os

 @MainActor
 final class AppModel: ObservableObject {

     // Connection
     @Published var ip: String = ""
     @Published var isConnected: Bool = false
     @Published var isConnecting: Bool = false
     @Published var statusMessage: String = ""
     @Published var errorMessage: String = ""

     // Live view
     @Published var liveFrame: UIImage?
     @Published var liveViewActive: Bool = false

     // Camera state
     @Published var state: CameraState?

     // Gallery
     @Published var files: [LumixFileItem] = []
     @Published var browsingPath: [LumixFileItem] = []
     @Published var downloading: Bool = false
     @Published var downloadProgress: Double = 0

     // Settings
     @Published var photoStyles: [String] = []

     private var client: LumixClient?
     private var dlna: LumixDLNA?
     private var stateTask: Task<Void, Never>?

    // UDP live-view
    private var udp: LumixUDPLiveView?
    private var watchdogTask: Task<Void, Never>?
    private var streamGen = 0
    private var lastFrameAt = Date.distantPast
    private var lastRestartAt = Date.distantPast
    private var restartCount = 0
    private var establishAttempts = 0

    // Live-view diagnostics (shown in the UI for debugging)
    @Published var debugInfo: String = ""
    @Published private(set) var udpStats: UDPLiveViewStats?
    /// Persistent, user-facing reason the live view is not showing (e.g. the
    /// camera is in PLAY/menu mode and rejected `startstream`).
    @Published var liveViewBlocked: String = ""

     // MARK: Connection

     func connect(ip: String) async {
         self.ip = ip.trimmingCharacters(in: .whitespaces)
         guard !self.ip.isEmpty else { return }
         isConnecting = true
         errorMessage = ""
         statusMessage = "正在连接 \(ip) …"
         let c = LumixClient(ip: self.ip)
         do {
             let s = try await c.getstate()
             self.client = c
             self.dlna = LumixDLNA(ip: self.ip)
             self.state = s
             self.isConnected = true
             self.statusMessage = "已连接：\(s.version) · 电池 \(s.battery) · \(s.camMode)"
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
         client = nil
         dlna = nil
         isConnected = false
         state = nil
         files = []
         browsingPath = []
         statusMessage = ""
     }

     // MARK: State polling

     private func startStatePolling() {
         stateTask?.cancel()
         stateTask = Task { [weak self] in
             while !Task.isCancelled, let c = self?.client, self?.isConnected == true {
                 if let s = try? await c.getstate() {
                     self?.state = s
                 }
                 try? await Task.sleep(nanoseconds: 2_000_000_000)
             }
         }
     }

    // MARK: Live view (official UDP startstream)

    private let log = Logger(subsystem: "com.lumixfast.ios", category: "AppModel")

    func startLiveView() {
        guard client != nil else { return }
        teardownStream()
        liveViewActive = true
        liveFrame = nil
        restartCount = 0
        establishAttempts = 0
        liveViewBlocked = ""
        debugInfo = "正在启动 UDP 取景…"
        startWatchdog()
        Task { await establishStream() }
    }

    func stopLiveView() {
        teardownStream()
    }

    /// Tear down the current UDP stream and ask the camera to stop pushing.
    private func teardownStream() {
        streamGen += 1
        liveViewActive = false
        liveViewBlocked = ""
        watchdogTask?.cancel()
        watchdogTask = nil
        udp?.stop()
        udp = nil
        if let c = client {
            Task { _ = try? await c.stopStream() }
        }
    }

    /// Bind a UDP port, tell the camera to push its live-view stream there, and
    /// start receiving. `restart` first stops any existing stream on the camera.
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
                // Refresh the camera mode so the guidance is accurate (e.g. PLAY mode).
                if let s = try? await c.getstate(), streamGen == gen {
                    self.state = s
                    self.liveViewBlocked = LumixClient.friendlyMessage(result: result, camMode: s.camMode)
                } else {
                    self.liveViewBlocked = LumixClient.friendlyMessage(result: result, camMode: self.state?.camMode)
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

    /// Watchdog: if no frame arrives for a while, restart the stream (bounded).
    private func startWatchdog() {
        watchdogTask?.cancel()
        watchdogTask = Task { [weak self] in
            while !Task.isCancelled {
                try? await Task.sleep(nanoseconds: 3_000_000_000)
                guard let self else { return }
                let now = Date()
                guard self.liveViewActive else { continue }

                if self.udp != nil {
                    // Connected but went silent → restart (bounded).
                    if now.timeIntervalSince(self.lastFrameAt) > 8,
                       now.timeIntervalSince(self.lastRestartAt) > 10,
                       self.restartCount < 8 {
                        self.debugInfo = "取景流静默…重连中"
                        await self.establishStream(restart: true)
                    }
                } else if self.establishAttempts < 60 {
                    // Not yet connected (e.g. `startstream` was rejected because the
                    // camera is in PLAY/menu mode). Re-check the camera mode; once it
                    // can show a finder, retry the stream so it self-heals.
                    if let s = try? await self.client?.getstate() {
                        self.state = s
                        if LumixClient.isLiveViewBlockingMode(s.camMode) {
                            // Still in a mode with no finder — keep guiding the user
                            // and wait for them to switch to still/movie mode.
                            self.liveViewBlocked = LumixClient.friendlyMessage(result: "err_reject", camMode: s.camMode)
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

     // MARK: Shutter / control

     func shoot() async {
         guard let c = client else { return }
         do {
             statusMessage = "拍摄中…"
             try await c.shoot()
             statusMessage = "已发送快门指令"
         } catch {
             errorMessage = "快门失败：\(error.localizedDescription)"
         }
     }

     func power(on: Bool) async {
         guard let c = client else { return }
         try? await c.power(on: on)
     }

     func setCameraMode(_ mode: String) async {
         guard let c = client else { return }
         try? await c.setCameraMode(mode)
     }

     // MARK: Settings

     func loadSettings() async {
         guard let c = client else { return }
         if let cap = try? await c.capability() {
             // Capability XML enumerates available settings; keep raw for display.
             photoStyles = Self.parsePhotoStyles(cap)
         }
     }

     func setPhotoStyle(_ style: String) async {
         guard let c = client else { return }
         try? await c.setSetting("photostyle", style)
     }

     static func parsePhotoStyles(_ capabilityXML: String) -> [String] {
        // The capability document enumerates supported settings. We surface the
        // standard Lumix photo-style identifiers; users can also type a custom value.
        return ["STANDARD", "VIVID", "NEUTRAL", "SCENE", "VIVID2", "MONO"]
     }

     // MARK: Gallery (DLNA)

     func loadGallery() async {
         guard let d = dlna else { return }
         files = []
         browsingPath = []
         do {
            let root = try await d.browse(objectID: "0")
            files = root
         } catch {
             errorMessage = "浏览失败：\(error.localizedDescription)"
         }
     }

     func openContainer(_ item: LumixFileItem) async {
         guard let d = dlna else { return }
         do {
             let children = try await d.browse(objectID: item.id)
             browsingPath.append(item)
             files = children
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
                 files = kids
             }
         }
     }

     func download(_ item: LumixFileItem) async {
         guard let d = dlna, let res = item.res else { return }
         downloading = true
         downloadProgress = 0
         do {
             let (data, _) = try await d.download(resURL: res)
            let saved = await saveToPhotos(data, name: item.title)
             statusMessage = saved ? "已保存：\(item.title)" : "保存失败（请检查相册权限）"
         } catch {
             errorMessage = "下载失败：\(error.localizedDescription)"
         }
         downloading = false
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
