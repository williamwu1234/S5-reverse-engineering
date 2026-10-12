// LumixUDPLiveView.swift
//
// Official Lumix UDP `startstream` real-time live view.
//
// Protocol (reverse-engineered from com.panasonic.jp.lumixsync, the decompiled
// LUMIX Sync app):
//   1. The phone binds a UDP socket on a free port in 49152..65535 FIRST.
//   2. The phone calls `cam.cgi?mode=startstream&value=<port>` (UA "LUMIX Sync").
//   3. The camera pushes JPEG live-view frames to that UDP port.
//   4. Teardown calls `cam.cgi?mode=stopstream`.
//
// Every datagram is: 32-byte big-endian header (+ optional metadata) + JPEG chunk.
// Header layout (verified against H5/a.java byte reader + p102m5/b.java):
//   [0..1]   totalLen    u16  total datagram length
//   [2..3]   (unused)    i16
//   [4..7]   frameIndex  i32  <0  -> single-packet frame (whole JPEG in 1 datagram)
//                                   >=0 -> chunk sequence 0,1,2,...
//   [8]      moreFlag    u8   !=0 -> MORE chunks follow; ==0 -> LAST chunk (frame done)
//   [9..14]  reserved    6 x u8
//   [15]     (unused)    u8
//   [16]     type        u8   33(0x21)=liveview, 97(0x61)=audio, 68(0x44)=movie
//   [17]     (unused)    u8
//   [18..21] frameSizeA  i32  per-frame generation id (desync detection)
//   [22..25] frameSize   i32  total bytes of the assembled JPEG frame
//   [26..29] chunkOffset i32  byte offset of this chunk within the frame
//   [30..31] metaLen     u16  metadata block length (payload starts at 32+metaLen)
//
// Reassembly (mirrors p189y5/d.java `o()` exactly):
//   * A chunk is accepted only if its frameIndex equals the expected tracker;
//     otherwise the in-progress frame is reset and the chunk is dropped.
//   * frameIndex == 0 starts a fresh frame (allocate frameSize buffer).
//   * Each chunk's payload is copied into the buffer at chunkOffset.
//   * moreFlag != 0 -> more chunks follow, advance the tracker.
//   * moreFlag == 0 -> last chunk: emit the assembled JPEG, reset.
//   The final JPEG is recovered by locating the SOI (FFD8) and EOI (FFD9) markers,
//   which makes the reassembler tolerant to small framing quirks.
//
import Foundation
import Darwin
import os

// MARK: - Diagnostics

struct UDPLiveViewStats: Equatable {
    var packets: Int = 0
    var frames: Int = 0
    var framesSingle: Int = 0
    var framesMulti: Int = 0
    var dropped: Int = 0
    var desync: Int = 0
    var fps: Double = 0
    var lastFrameAge: TimeInterval = .greatestFiniteMagnitude
    var port: Int32 = 0
    var streaming: Bool = false
    var typeCounts: [Int: Int] = [:]
    var lastHeader: String = ""

    var line: String {
        let age = lastFrameAge.isFinite ? String(format: "%.2fs", lastFrameAge) : "--"
        return "UDP \(port) · 包 \(packets) · 帧 \(frames) (单包\(framesSingle)/多包\(framesMulti)) · 丢 \(dropped) · 失步 \(desync) · \(String(format: "%.1f", fps))fps · 距上帧 \(age)"
    }
}

// MARK: - UDP live view

final class LumixUDPLiveView {

    // Callbacks (invoked on the receive thread; caller hops to main as needed).
    var onFrame: ((Data) -> Void)?
    var onStats: ((UDPLiveViewStats) -> Void)?
    var onLog: ((String) -> Void)?

    private let ip: String
    private let portRange = 49152...65535
    // Reference buffer pool is ~640KB; allow comfortable headroom.
    private let maxFrameSize = 1024 * 1024

    private let log = Logger(subsystem: "com.lumixmonitor.ios", category: "UDPLiveView")

    // Guards all reassembly state + counters (written on the receive thread,
    // read by the stats timer / stop on other threads).
    private let stateLock = NSLock()

    private var fd: Int32 = -1
    private var boundPort: Int32 = 0
    private var recvThread: Thread?
    private var statsTimer: DispatchSourceTimer?
    private var stopCalled = false
    private var stopped = false

    // Reassembly state (receive thread, guarded by stateLock).
    private var buffer: [UInt8] = []
    private var curFrameSize = 0
    private var curFrameSizeA: Int32 = 0
    private var tracker = 0

    // Diagnostics (receive thread, guarded by stateLock).
    private var packets = 0
    private var framesSingle = 0
    private var framesMulti = 0
    private var dropped = 0
    private var desync = 0
    private var typeCounts: [Int: Int] = [:]
    private var fpsWindow: [Date] = []
    private var lastFrameTime = Date.distantPast
    private var streaming = false
    private var lastHeader = ""

    init(ip: String) {
        self.ip = ip
    }

    deinit { stop() }

    // MARK: Port binding

    /// Bind a UDP socket on a free port in 49152..65535 and return that port.
    /// Must be called before `startstream`. Returns -1 on failure.
    func bind() -> Int32 {
        if fd >= 0 { close(fd); fd = -1 }
        let s = socket(AF_INET, SOCK_DGRAM, 0)
        guard s >= 0 else {
            log.error("socket() failed: \(String(cString: strerror(errno)))")
            onLog?("socket() 失败: \(String(cString: strerror(errno)))")
            return -1
        }
        var reuse: Int32 = 1
        setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &reuse, socklen_t(MemoryLayout<Int32>.size))

        let range = portRange
        var chosen: Int32 = -1
        for port in range {
            var addr = sockaddr_in()
            addr.sin_family = sa_family_t(AF_INET)
            addr.sin_port = in_port_t(UInt16(port).bigEndian)
            addr.sin_addr.s_addr = INADDR_ANY
            let ok = withUnsafePointer(to: &addr) { ptr in
                ptr.withMemoryRebound(to: sockaddr.self, capacity: 1) { sa in
                    Darwin.bind(s, sa, socklen_t(MemoryLayout<sockaddr_in>.size))
                }
            }
            if ok == 0 { chosen = Int32(port); break }
        }
        guard chosen >= 0 else {
            close(s)
            log.error("no free UDP port in \(range)")
            onLog?("没有可用 UDP 端口")
            return -1
        }

        // Receive timeout so the loop can observe `stopped` without extra wakeups.
        var tv = timeval(tv_sec: 0, tv_usec: 300_000)
        setsockopt(s, SOL_SOCKET, SO_RCVTIMEO, &tv, socklen_t(MemoryLayout<timeval>.size))
        // Larger receive buffer to absorb bursts.
        var rcvbuf: Int32 = 512 * 1024
        setsockopt(s, SOL_SOCKET, SO_RCVBUF, &rcvbuf, socklen_t(MemoryLayout<Int32>.size))

        fd = s
        boundPort = chosen
        log.info("UDP socket bound on port \(chosen)")
        onLog?("UDP 端口已绑定: \(chosen)")
        return chosen
    }

    // MARK: Stream lifecycle

    func start() {
        guard fd >= 0 else {
            onLog?("尚未绑定 UDP 端口")
            return
        }
        stateLock.lock()
        stopCalled = false
        stopped = false
        streaming = true
        resetReassemblyNoLock()
        stateLock.unlock()

        // Strong self: keeps the object alive until the receive thread fully
        // exits, so there is no use-after-free. The thread leaves on its own
        // once `stopped` is observed (socket closed + SO_RCVTIMEO wakeup).
        let thread = Thread { [self] in
            self.recvLoop()
        }
        thread.stackSize = 512 * 1024
        recvThread = thread
        thread.start()

        // Periodic stats + FPS emission.
        let timer = DispatchSource.makeTimerSource(queue: DispatchQueue.global(qos: .utility))
        timer.schedule(deadline: .now() + 0.5, repeating: 0.5)
        timer.setEventHandler { [weak self] in self?.emitStats() }
        statsTimer = timer
        timer.resume()

        log.info("receive loop started")
        onLog?("开始接收实时取景流")
    }

    func stop() {
        stateLock.lock()
        let wasStopped = stopCalled
        stopCalled = true
        stateLock.unlock()
        if wasStopped { return }

        stopped = true
        stateLock.lock()
        streaming = false
        stateLock.unlock()
        statsTimer?.cancel()
        statsTimer = nil
        if fd >= 0 {
            shutdown(fd, SHUT_RDWR)
            close(fd)
            fd = -1
        }
        // Best-effort: the socket close unblocks recvfrom; the loop exits within
        // one SO_RCVTIMEO (300ms). No blocking join on the caller's thread.
        recvThread?.cancel()
        recvThread = nil
        log.info("receive loop stopped")
        emitStats()
    }

    // MARK: Receive loop

    private func recvLoop() {
        let bufSize = 65536
        var buf = [UInt8](repeating: 0, count: bufSize)
        while true {
            stateLock.lock()
            let isStopped = stopped
            stateLock.unlock()
            if isStopped { break }

            var addr = sockaddr()
            var addrLen = socklen_t(MemoryLayout<sockaddr>.size)
            let n = recvfrom(fd, &buf, bufSize, 0, &addr, &addrLen)
            guard n > 0 else {
                continue // timeout or transient error: loop re-checks `stopped`
            }
            let datagram = Array(buf[0..<n])
            process(datagram)
        }
    }

    // MARK: Header parse + reassembly

    private func be16(_ d: [UInt8], _ o: Int) -> UInt16 {
        UInt16(d[o]) << 8 | UInt16(d[o + 1])
    }
    private func be32(_ d: [UInt8], _ o: Int) -> Int32 {
        Int32(bitPattern: UInt32(d[o]) << 24 | UInt32(d[o + 1]) << 16 | UInt32(d[o + 2]) << 8 | UInt32(d[o + 3]))
    }

    private func process(_ data: [UInt8]) {
        stateLock.lock()
        defer { stateLock.unlock() }

        packets += 1
        guard data.count >= 32 else { dropped += 1; return }

        let frameIndex = be32(data, 4)
        let moreFlag = data[8]
        let type = data[16]
        let frameSizeA = be32(data, 18)
        let frameSize = Int(be32(data, 22))
        let chunkOffset = Int(be32(data, 26))
        let metaLen = Int(be16(data, 30))

        lastHeader = "idx=\(frameIndex) more=\(moreFlag) type=\(type) fsA=\(frameSizeA) fs=\(frameSize) off=\(chunkOffset) meta=\(metaLen) len=\(data.count)"

        // Only live-view frame packets (type 33). Audio(97)/movie(68) are counted
        // for debugging but not reassembled.
        guard type == 33 else {
            typeCounts[Int(type), default: 0] += 1
            return
        }

        let payloadStart = 32 + metaLen
        guard payloadStart <= data.count else { dropped += 1; return }
        let payload = data[payloadStart...]

        // Single-packet frame: the entire JPEG is in this one datagram.
        if frameIndex < 0 {
            framesSingle += 1
            emitJPEG(Array(payload))
            return
        }

        // Multi-packet reassembly (mirror d.java o()).
        if frameIndex != tracker {
            // Desync: reset the in-progress frame and drop this chunk.
            desync += 1
            resetReassemblyNoLock()
            return
        }

        if frameIndex == 0 {
            // First chunk of a new frame.
            guard frameSize > 0, frameSize <= maxFrameSize else {
                dropped += 1
                return
            }
            buffer = [UInt8](repeating: 0, count: frameSize)
            curFrameSize = frameSize
            curFrameSizeA = frameSizeA
            copyChunkNoLock(payload, at: chunkOffset)
            if moreFlag != 0 {
                tracker += 1
                return
            }
            // moreFlag == 0 -> single-chunk frame, complete.
            framesMulti += 1
            emitJPEG(buffer)
            resetReassemblyNoLock()
            return
        }

        // frameIndex > 0: continuation chunk; validate header consistency.
        if frameSizeA != curFrameSizeA || frameSize != curFrameSize {
            desync += 1
            resetReassemblyNoLock()
            return
        }
        copyChunkNoLock(payload, at: chunkOffset)
        if moreFlag != 0 {
            tracker += 1
            return
        }
        // moreFlag == 0 -> last chunk: emit and reset.
        framesMulti += 1
        emitJPEG(buffer)
        resetReassemblyNoLock()
    }

    private func copyChunkNoLock(_ payload: ArraySlice<UInt8>, at offset: Int) {
        guard offset >= 0, offset < curFrameSize else { dropped += 1; return }
        let len = min(payload.count, curFrameSize - offset)
        guard len > 0 else { dropped += 1; return }
        for i in 0..<len {
            buffer[offset + i] = payload[i]
        }
    }

    private func resetReassemblyNoLock() {
        buffer = []
        curFrameSize = 0
        curFrameSizeA = 0
        tracker = 0
    }

    /// Extract the JPEG (SOI..EOI) and deliver it. Called with stateLock held.
    private func emitJPEG(_ buf: [UInt8]) {
        guard buf.count > 2 else { dropped += 1; return }
        var start = -1
        for i in 0...(buf.count - 2) where buf[i] == 0xFF && buf[i + 1] == 0xD8 {
            start = i
            break
        }
        if start < 0 {
            dropped += 1
            return
        }
        var end = buf.count
        for i in (start + 1)..<buf.count where buf[i] == 0xD9 && buf[i - 1] == 0xFF {
            end = i + 1
            break
        }
        let jpeg = Data(buf[start..<end])
        guard jpeg.count > 32 else { dropped += 1; return }

        lastFrameTime = Date()
        fpsWindow.append(lastFrameTime)
        let cutoff = lastFrameTime.addingTimeInterval(-2.0)
        while let f = fpsWindow.first, f < cutoff { fpsWindow.removeFirst() }

        // Non-blocking hop: enqueue to main, never block under the lock.
        let cb = onFrame
        cb?(jpeg)
    }

    // MARK: Diagnostics

    private func emitStats() {
        stateLock.lock()
        let now = Date()
        let fps = fpsWindow.count > 1 ? Double(fpsWindow.count) / 2.0 : 0
        let age = lastFrameTime == .distantPast ? .greatestFiniteMagnitude : now.timeIntervalSince(lastFrameTime)
        let stats = UDPLiveViewStats(
            packets: packets,
            frames: framesSingle + framesMulti,
            framesSingle: framesSingle,
            framesMulti: framesMulti,
            dropped: dropped,
            desync: desync,
            fps: fps,
            lastFrameAge: age,
            port: boundPort,
            streaming: streaming,
            typeCounts: typeCounts,
            lastHeader: lastHeader
        )
        stateLock.unlock()
        let cb = onStats
        cb?(stats)
    }
}
