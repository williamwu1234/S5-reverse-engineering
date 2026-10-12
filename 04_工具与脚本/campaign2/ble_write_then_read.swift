// ble_write_then_read.swift — 复现 LUMIX Sync 的 BLE 顺序：先写身份，再读数据
//
// 依据 APK（C5/e.java A() / E5/j.java / H5/s.java）：
//   连接 → (注册通知；本机无 CCCD，跳过) → 读 idx35 取密钥 → 写 DLNA_UUID_APS + FRIENDLY_NAME_APS
//   → 读 idx5 CAMERA_SSID → 读 idx6 CAMERA_WIFI_PASSWORD
//
// 我们的假设：相机对"没先写身份就读"的行为直接断链。
// 由于密钥有默认值（H5/s: key==0 -> 0x9032782C），可能不必先读就能完成身份写入。
//
// 本工具流程：
//   A) 连接 + 枚举
//   B) 写 bb5d2a8c (DLNA_UUID_APS)   = encode(DLNA_UUID, DEFAULT_KEY, 20)
//   C) 写 7b61774f (FRIENDLY_NAME_APS) = encode("MacBLE",  DEFAULT_KEY, 20)
//   D) 读 03e23a31 (idx35 INITIAL_INFORM) → 若成功，取前 4 字节大端为会话密钥
//   E) 用会话密钥读 idx5 (SSID) / idx6 (Wi-Fi 密码) 并解码
//
// 用法: ./ble_write_then_read [秒数]
import Foundation
import CoreBluetooth

let SVC_MAIN = "054AC620-3214-11E6-AC0D-0002A5D5C51B"
let CH_INITIAL = "03E23A31-A54C-40FA-A668-DE9ACDC910BB"
let CH_DLNA_APS = "8D08A420-3213-11E6-8ACA-0002A5D5C51B"   // 非APS路径: 写原始 DLNA_UUID
let CH_NAME_APS = "CD7A71A0-3213-11E6-8F56-0002A5D5C51B"   // 非APS路径: 写原始设备名
let CH_SSID = "E206A5C0-3214-11E6-AFE4-0002A5D5C51B"
let CH_PASS = "C97CF1A5-3C03-4290-8C1B-9E74B9500F54"

let DEFAULT_KEY: UInt32 = UInt32(bitPattern: -1875740628)   // 0x9032782C

func ts() -> String {
    let f = DateFormatter(); f.dateFormat = "HH:mm:ss.SSS"
    return f.string(from: Date())
}
func swap32(_ v: UInt32) -> UInt32 {
    ((v >> 24) & 0xFF) | ((v << 24) & 0xFF000000) |
    ((v << 8) & 0x00FF0000) | ((v >> 8) & 0x0000FF00)
}
/// H5/s.java s.b(String,int) 的等价：定长缓冲 [len][payload][0xFF…]，再做字节置换+XOR
func encode(_ payload: [UInt8], key: UInt32, total: Int = 20) -> [UInt8] {
    let k: UInt32 = (key == 0) ? DEFAULT_KEY : key
    var buf = [UInt8](repeating: 0xFF, count: total)
    buf[0] = UInt8(payload.count & 0xFF)
    for (i, b) in payload.enumerated() where (1 + i) < total { buf[1 + i] = b }
    var out = [UInt8]()
    var i = 0
    while i < total {
        let b = Array(buf[i..<min(i + 4, total)])
        let v = (UInt32(b[3]) << 24) | (UInt32(b[2]) << 16) | (UInt32(b[1]) << 8) | UInt32(b[0])
        let x = v ^ k
        out += [UInt8((x >> 24) & 0xFF), UInt8((x >> 16) & 0xFF), UInt8((x >> 8) & 0xFF), UInt8(x & 0xFF)]
        i += 4
    }
    return out
}
/// H5/s.java s.a(byte[],long) 的等价
func decode(_ data: [UInt8], key: UInt32) -> [UInt8] {
    let k: UInt32 = (key == 0) ? DEFAULT_KEY : key
    var out = [UInt8]()
    var i = 0
    while i + 4 <= data.count {
        let v = (UInt32(data[i + 3]) << 24) | (UInt32(data[i + 2]) << 16) |
                (UInt32(data[i + 1]) << 8) | UInt32(data[i])
        let x = swap32(v) ^ k
        if i == 0 {
            out += [UInt8((x >> 8) & 0xFF), UInt8((x >> 16) & 0xFF), UInt8((x >> 24) & 0xFF)]
        } else {
            out += [UInt8(x & 0xFF), UInt8((x >> 8) & 0xFF), UInt8((x >> 16) & 0xFF), UInt8((x >> 24) & 0xFF)]
        }
        i += 4
    }
    if let z = out.firstIndex(of: 0xFF) { out = Array(out[0..<z]) }
    return out
}
func hex(_ d: Data?) -> String {
    guard let d = d else { return "(nil)" }
    return d.map { String(format: "%02x", $0) }.joined()
}

// 身份：与 APK H5/p.java A() 同构 —— "4D454930010010008001" + seed
let DLNA_UUID: [UInt8] = [0x4D, 0x45, 0x49, 0x30, 0x01, 0x00, 0x10, 0x00, 0x80, 0x01,
                          0x02, 0x00, 0x00, 0x02, 0x5A, 0xD6]
let FRIENDLY: [UInt8] = Array("MacBLE".utf8)

final class Pair: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    var central: CBCentralManager!
    var target: CBPeripheral?
    var chars: [String: CBCharacteristic] = [:]
    var started = false
    var svcTotal = 0, svcDone = 0
    var key: UInt32 = 0
    var disconnected = false
    var ssid: String?, pass: String?
    var passTries = 0

    func log(_ s: String) { print("[\(ts())] \(s)") }

    func centralManagerDidUpdateState(_ c: CBCentralManager) {
        if c.state == .poweredOn {
            log("扫描…"); c.scanForPeripherals(withServices: [CBUUID(string: SVC_MAIN)], options: nil)
        } else { log("central state=\(c.state.rawValue)") }
    }
    func centralManager(_ c: CBCentralManager, didDiscover p: CBPeripheral, advertisementData a: [String: Any], rssi R: NSNumber) {
        log("发现 \(p.name ?? "?") rssi=\(R)，连接")
        target = p; p.delegate = self; c.stopScan(); c.connect(p, options: nil)
    }
    func centralManager(_ c: CBCentralManager, didConnect p: CBPeripheral) {
        log("已连接 → discoverServices"); p.discoverServices(nil)
    }
    func centralManager(_ c: CBCentralManager, didDisconnectPeripheral p: CBPeripheral, error: Error?) {
        disconnected = true
        log(">>> 断链：\(error?.localizedDescription ?? "对端主动断开")")
    }
    func peripheral(_ p: CBPeripheral, didDiscoverServices error: Error?) {
        svcTotal = (p.services ?? []).count
        for s in p.services ?? [] { p.discoverCharacteristics(nil, for: s) }
    }
    func peripheral(_ p: CBPeripheral, didDiscoverCharacteristicsFor s: CBService, error: Error?) {
        svcDone += 1
        for ch in s.characteristics ?? [] { chars[ch.uuid.uuidString.uppercased()] = ch }
        if svcDone == svcTotal && !started {
            started = true
            log("枚举完成：\(chars.count) 个特征")
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) { self.step1_write() }
        }
    }

    // ---- 步骤 1：写身份（DLNA_UUID_APS） ----
    func step1_write() {
        guard let p = target, !disconnected else { return }
        log("步骤1: 写原始 DLNA_UUID（非APS） = \(hex(Data(DLNA_UUID)))")
        if let c = chars[CH_DLNA_APS] { p.writeValue(Data(DLNA_UUID), for: c, type: .withResponse) }
        else { log("  !! 找不到 \(CH_DLNA_APS)") }
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) { self.step2_write() }
    }
    // ---- 步骤 2：写身份（FRIENDLY_NAME_APS） ----
    func step2_write() {
        guard let p = target, !disconnected else { return }
        log("步骤2: 写原始设备名（非APS） = \(hex(Data(FRIENDLY)))")
        if let c = chars[CH_NAME_APS] { p.writeValue(Data(FRIENDLY), for: c, type: .withResponse) }
        else { log("  !! 找不到 \(CH_NAME_APS)") }
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) { self.step3_read_initial() }
    }
    // ---- 步骤 3：读 INITIAL_INFORM ----
    func step3_read_initial() {
        guard let p = target, !disconnected else { return }
        log("步骤3: 读 INITIAL_INFORM (idx35) —— 若这步不再断链，假设成立")
        if let c = chars[CH_INITIAL] { p.readValue(for: c) }
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) { self.step4_read_ssid() }
    }
    // ---- 步骤 4/5：读 SSID / 密码 ----
    func step4_read_ssid() {
        guard let p = target, !disconnected else { return }
        log("步骤4: 读 CAMERA_SSID (idx5)  会话密钥=0x\(String(format: "%08X", key))")
        if let c = chars[CH_SSID] { p.readValue(for: c) }
    }

    func peripheral(_ p: CBPeripheral, didWriteValueFor ch: CBCharacteristic, error: Error?) {
        log("  ← 写回调 \(ch.uuid.uuidString.prefix(8)) err=\(error?.localizedDescription ?? "成功")")
    }
    func peripheral(_ p: CBPeripheral, didUpdateValueFor ch: CBCharacteristic, error: Error?) {
        let u = ch.uuid.uuidString.uppercased()
        if let e = error { log("  ← 读回调 \(u.prefix(8)) ERR \(e.localizedDescription)"); return }
        guard let v = ch.value else { return }
        let b = [UInt8](v)
        log("  ← 读回调 \(u.prefix(8)) raw=\(hex(v))")
        if u == CH_INITIAL {
            if b.count >= 4 {
                key = (UInt32(b[0]) << 24) | (UInt32(b[1]) << 16) | (UInt32(b[2]) << 8) | UInt32(b[3])
                log("     INITIAL_INFORM → 会话密钥 = 0x\(String(format: "%08X", key))")
            }
        } else if u == CH_SSID {
            let nul = CharacterSet(charactersIn: "\0")
            let raw = String(bytes: b, encoding: .utf8)?
                .trimmingCharacters(in: nul.union(.whitespacesAndNewlines))
            let dec = String(bytes: decode(b, key: key), encoding: .utf8)?
                .trimmingCharacters(in: .whitespacesAndNewlines)
            ssid = (raw?.isEmpty == false ? raw : nil) ?? dec
            log("     >>> SSID raw-ascii=\(raw ?? "-")  key-decoded=\(dec ?? "-")")
            // 立刻读密码，不给相机断链的机会
            if let c = chars[CH_PASS], let pp = target {
                log("步骤5: 立即读 CAMERA_WIFI_PASSWORD (idx6)")
                pp.readValue(for: c)
                DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) {
                    if self.pass == nil && self.passTries < 4 && !self.disconnected {
                        self.passTries += 1
                        self.log("  密码为空，重试第 \(self.passTries) 次")
                        pp.readValue(for: c)
                    }
                }
            }
        } else if u == CH_PASS {
            let nul = CharacterSet(charactersIn: "\0")
            let raw = String(bytes: b, encoding: .utf8)?
                .trimmingCharacters(in: nul.union(.whitespacesAndNewlines))
            let dec = String(bytes: decode(b, key: key), encoding: .utf8)?
                .trimmingCharacters(in: .whitespacesAndNewlines)
            pass = (raw?.isEmpty == false ? raw : nil) ?? dec
            log("     >>> WIFI PASSWORD hex=\(hex(v)) raw-ascii=\(raw ?? "-")  key-decoded=\(dec ?? "-")")
            if pass == nil && passTries < 4 {
                passTries += 1
                DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                    self.log("  空值，重试第 \(self.passTries) 次")
                    if let c = self.chars[CH_PASS] { p.readValue(for: c) }
                }
            }
        }
    }
}

let secs = CommandLine.arguments.compactMap { Double($0) }.first ?? 50
let p = Pair(); p.central = CBCentralManager(delegate: p, queue: nil)
RunLoop.main.run(until: Date().addingTimeInterval(secs))
let verdict = "disconnected=\(p.disconnected) key=\(String(format: "%08X", p.key)) ssid=\(p.ssid ?? "-") pass=\(p.pass ?? "-")\n"
try? verdict.write(toFile: "/tmp/ble_wr_result.txt", atomically: true, encoding: .utf8)
print("[\(ts())] 结束 disconnected=\(p.disconnected) ssid=\(p.ssid ?? "-") pass=\(p.pass ?? "-")")
