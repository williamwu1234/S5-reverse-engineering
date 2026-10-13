// ble_hold.swift — BLE 握手后【保持连接不放】，让相机维持它自动开启的 Wi-Fi 热点
//
// 用户实测结论（2026-10-13）：
//   "先与相机握手之后它会自动开启 WiFi，而在配对模式下是无法退出的"
//   ⇒ 相机热点只在 BLE 会话期间在线；BLE 一断，热点即关。
//
// 因此正确流程是：
//   BLE 连接 + 握手（写身份 → 读 INITIAL_INFORM/SSID/密码）
//     → 写就绪标记 /tmp/ble_hold_ready（外壳脚本据此去连热点）
//     → 【保持连接】期间周期性读 idx35 作为保活
//     → 外壳脚本完成 accctrl 后再退出
//
// 用法: ./ble_hold [保持秒数] [就绪标记路径]
import Foundation
import CoreBluetooth

let SVC_MAIN = "054AC620-3214-11E6-AC0D-0002A5D5C51B"
let CH_DLNA  = "8D08A420-3213-11E6-8ACA-0002A5D5C51B"
let CH_NAME  = "CD7A71A0-3213-11E6-8F56-0002A5D5C51B"
let CH_INIT  = "03E23A31-A54C-40FA-A668-DE9ACDC910BB"
let CH_SSID  = "E206A5C0-3214-11E6-AFE4-0002A5D5C51B"
let CH_PASS  = "C97CF1A5-3C03-4290-8C1B-9E74B9500F54"
let DEFAULT_KEY: UInt32 = UInt32(bitPattern: -1875740628)

func ts() -> String { let f = DateFormatter(); f.dateFormat = "HH:mm:ss.SSS"; return f.string(from: Date()) }
func log(_ s: String) { print("[\(ts())] \(s)"); fflush(stdout) }
func hexs(_ d: [UInt8]) -> String { d.map { String(format: "%02x", $0) }.joined() }
func decode(_ data: [UInt8], key: UInt32) -> [UInt8] {
    let k: UInt32 = (key == 0) ? DEFAULT_KEY : key
    func sw(_ v: UInt32) -> UInt32 {
        ((v >> 24) & 0xFF) | ((v << 24) & 0xFF000000) | ((v << 8) & 0x00FF0000) | ((v >> 8) & 0x0000FF00)
    }
    var out = [UInt8](); var i = 0
    while i + 4 <= data.count {
        let v = (UInt32(data[i+3]) << 24) | (UInt32(data[i+2]) << 16) | (UInt32(data[i+1]) << 8) | UInt32(data[i])
        let x = sw(v) ^ k
        if i == 0 { out += [UInt8((x >> 8) & 0xFF), UInt8((x >> 16) & 0xFF), UInt8((x >> 24) & 0xFF)] }
        else { out += [UInt8(x & 0xFF), UInt8((x >> 8) & 0xFF), UInt8((x >> 16) & 0xFF), UInt8((x >> 24) & 0xFF)] }
        i += 4
    }
    if let z = out.firstIndex(of: 0xFF) { out = Array(out[0..<z]) }
    return out
}

final class Hold: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    var central: CBCentralManager!
    var target: CBPeripheral?
    var chars: [String: CBCharacteristic] = [:]
    var svcTotal = 0, svcDone = 0, started = false
    var key: UInt32 = 0
    var handshakeDone = false
    var readyPath = "/tmp/ble_hold_ready"
    var deadline = Date().addingTimeInterval(300)
    var keepTimer: Timer?

    func centralManagerDidUpdateState(_ c: CBCentralManager) {
        if c.state == .poweredOn { log("BLE 扫描…"); c.scanForPeripherals(withServices: [CBUUID(string: SVC_MAIN)], options: nil) }
        else { log("BLE state=\(c.state.rawValue)") }
    }
    func centralManager(_ c: CBCentralManager, didDiscover p: CBPeripheral, advertisementData a: [String: Any], rssi R: NSNumber) {
        log("BLE 发现 \(p.name ?? "?") rssi=\(R)")
        target = p; p.delegate = self; c.stopScan(); c.connect(p, options: nil)
    }
    func centralManager(_ c: CBCentralManager, didConnect p: CBPeripheral) {
        log("BLE 已连接（将全程保持）"); p.discoverServices(nil)
    }
    func centralManager(_ c: CBCentralManager, didDisconnectPeripheral p: CBPeripheral, error: Error?) {
        log("!! BLE 断链：\(error?.localizedDescription ?? "对端断开") —— 相机热点应随之关闭")
        try? "disconnected".write(toFile: readyPath + ".lost", atomically: true, encoding: .utf8)
        CFRunLoopStop(CFRunLoopGetMain())
    }
    func peripheral(_ p: CBPeripheral, didDiscoverServices error: Error?) {
        svcTotal = (p.services ?? []).count
        for s in p.services ?? [] { p.discoverCharacteristics(nil, for: s) }
    }
    func peripheral(_ p: CBPeripheral, didDiscoverCharacteristicsFor s: CBService, error: Error?) {
        svcDone += 1
        for ch in s.characteristics ?? [] { chars[ch.uuid.uuidString.uppercased()] = ch }
        if svcDone == svcTotal && !started { started = true; log("枚举完成 \(chars.count) 特征 → 写身份"); handshake() }
    }
    func handshake() {
        guard let p = target else { return }
        let dlna: [UInt8] = [0x4D,0x45,0x49,0x30,0x01,0x00,0x10,0x00,0x80,0x01,0x02,0x00,0x00,0x02,0x5A,0xD6]
        log("写 DLNA_UUID = \(hexs(dlna))")
        if let c = chars[CH_DLNA] { p.writeValue(Data(dlna), for: c, type: .withResponse) }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            log("写设备名 = MacBLE")
            if let c = self.chars[CH_NAME] { p.writeValue(Data("MacBLE".utf8), for: c, type: .withResponse) }
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                if let c = self.chars[CH_INIT] { p.readValue(for: c) }
            }
        }
    }
    func peripheral(_ p: CBPeripheral, didWriteValueFor ch: CBCharacteristic, error: Error?) {
        log("  ← 写回调 \(ch.uuid.uuidString.prefix(8)) err=\(error?.localizedDescription ?? "成功")")
    }
    func peripheral(_ p: CBPeripheral, didUpdateValueFor ch: CBCharacteristic, error: Error?) {
        let u = ch.uuid.uuidString.uppercased()
        if let e = error { log("  ← 读回调 \(u.prefix(8)) ERR \(e.localizedDescription)"); return }
        guard let v = ch.value else { return }
        let b = [UInt8](v)
        if u == CH_INIT {
            if b.count >= 4 { key = (UInt32(b[0]) << 24) | (UInt32(b[1]) << 16) | (UInt32(b[2]) << 8) | UInt32(b[3]) }
            log("  INITIAL_INFORM=\(hexs(b))  会话密钥=0x\(String(format: "%08X", key))")
            if !handshakeDone, let c = chars[CH_SSID] { p.readValue(for: c) }
        } else if u == CH_SSID {
            let s = String(bytes: b, encoding: .utf8)?.trimmingCharacters(in: CharacterSet(charactersIn: "\0").union(.whitespacesAndNewlines))
            log("  >>> SSID = \(s ?? "?")")
            if !handshakeDone, let c = chars[CH_PASS] { p.readValue(for: c) }
        } else if u == CH_PASS {
            let d = decode(b, key: key)
            let s = String(bytes: d, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines)
            log("  >>> PASSWORD = \(s ?? "(空)")")
            // 握手完成 —— 通知外壳脚本可以去连热点了
            handshakeDone = true
            try? "ready".write(toFile: readyPath, atomically: true, encoding: .utf8)
            log("*** 握手完成，已写就绪标记 \(readyPath) —— 外壳脚本现在应去连相机热点 ***")
            // 保活：全局只建一次定时器，且用轻量读（避免刷爆相机）
            if self.keepTimer == nil {
                log("*** 启动保活（每 10s 一次轻量读，只建一次）***")
                DispatchQueue.main.async {
                    self.keepTimer = Timer.scheduledTimer(withTimeInterval: 10, repeats: true) { _ in
                        if let c = self.chars[CH_SSID], let pp = self.target, pp.state == .connected {
                            pp.readValue(for: c)
                        }
                    }
                }
            }
        }
    }
}

let secs = CommandLine.arguments.compactMap { Double($0) }.first ?? 300
let h = Hold()
if CommandLine.arguments.count > 2 { h.readyPath = CommandLine.arguments[2] }
try? FileManager.default.removeItem(atPath: h.readyPath)
h.deadline = Date().addingTimeInterval(secs)
h.central = CBCentralManager(delegate: h, queue: nil)
log("保持窗口 \(Int(secs))s，就绪标记 \(h.readyPath)")
RunLoop.main.run(until: Date().addingTimeInterval(secs))
log("保持窗口结束，主动断开")
if let p = h.target, let c = h.central { c.cancelPeripheralConnection(p) }
RunLoop.main.run(until: Date().addingTimeInterval(2))
