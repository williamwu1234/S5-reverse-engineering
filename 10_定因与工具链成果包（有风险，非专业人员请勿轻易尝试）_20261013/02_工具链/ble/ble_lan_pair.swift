// ble_lan_pair.swift — 局域网版：BLE 注册身份 + 同一 UUID 走 Wi-Fi accctrl（含加密路径）
//
// 为什么要有这一版：连相机热点极不稳定（macOS 会因为"无互联网"自动回落家网，
// 且相机 SoftAP 反复 -3970/-3906）。而相机作为 station 挂在家庭路由器上时，
// Mac 完全不用切网 —— 稳定、可反复做。
//
// 依据 APK：
//   · 身份 UUID（BLE 写入）      H5/p.java:272   "4D454930010010008001" + seed
//   · accctrl 明文 value         H5/p.java:1515  "4D454930-0100-1000-8001-" + seed, type=req_acc
//   · accctrl 加密 value         type=req_acc_e，value/value2 经 H5/s.b(str, key) 编码
//   · 密钥 key                    p168v5/a.java U() = req_acc_g 应答第 2 个逗号字段(十六进制)
//   · 路径选择                    com/panasonic/jp/service/c.java:757
//                                aVar==Encrypt ? "req_acc_e" : "req_acc"
//     而 accctrl req_acc（无参）应答末位就是 encrypted / open
//
// 用法: ./ble_lan_pair <相机IP> [seed] [秒数]
import Foundation
import CoreBluetooth

let SVC_MAIN = "054AC620-3214-11E6-AC0D-0002A5D5C51B"
let CH_DLNA  = "8D08A420-3213-11E6-8ACA-0002A5D5C51B"
let CH_NAME  = "CD7A71A0-3213-11E6-8F56-0002A5D5C51B"
let DEFAULT_KEY: UInt32 = UInt32(bitPattern: -1875740628)   // 0x9032782C

func ts() -> String { let f = DateFormatter(); f.dateFormat = "HH:mm:ss.SSS"; return f.string(from: Date()) }
func log(_ s: String) { print("[\(ts())] \(s)") }
func hexs(_ d: [UInt8]) -> String { d.map { String(format: "%02x", $0) }.joined() }

/// H5/s.java s.b(String,int)：字符串按 0xFF 补齐到 4 的倍数，
/// 每 4 字符大端成 32 位再 XOR key，最后输出字节序翻转后的 8 位十六进制串。
func encodeString(_ s: String, key: UInt32) -> String {
    let k: UInt32 = (key == 0) ? DEFAULT_KEY : key
    var chars = Array(s.utf8).map { UInt8($0) }
    while chars.count % 4 != 0 { chars.append(0xFF) }
    var out = ""
    var i = 0
    while i < chars.count {
        let j = (UInt32(chars[i]) << 24) | (UInt32(chars[i + 1]) << 16) |
                (UInt32(chars[i + 2]) << 8) | UInt32(chars[i + 3])
        let x = j ^ k
        let swapped = ((x >> 24) & 0xFF) | ((x << 24) & 0xFF000000) |
                      ((x << 8) & 0x00FF0000) | ((x >> 8) & 0x0000FF00)
        out += String(format: "%08x", swapped)
        i += 4
    }
    return out
}

@discardableResult
func httpGet(_ urlStr: String, timeout: TimeInterval = 8) -> String {
    guard let url = URL(string: urlStr) else { return "(bad url)" }
    var req = URLRequest(url: url)
    req.setValue("LUMIX Sync", forHTTPHeaderField: "User-Agent")
    req.timeoutInterval = timeout
    let sem = DispatchSemaphore(value: 0)
    var out = "(no response)"
    URLSession.shared.dataTask(with: req) { data, _, err in
        if let d = data { out = String(data: d, encoding: .utf8) ?? "(binary)" }
        else if let e = err { out = "(err) \(e.localizedDescription)" }
        sem.signal()
    }.resume()
    _ = sem.wait(timeout: .now() + timeout + 3)
    return out.replacingOccurrences(of: "\n", with: " ").trimmingCharacters(in: .whitespaces)
}

final class Pair: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    var central: CBCentralManager!
    var target: CBPeripheral?
    var chars: [String: CBCharacteristic] = [:]
    var svcTotal = 0, svcDone = 0, started = false
    var bleConnected = false
    var camIP = "192.168.1.131"
    var seed = "020000025AD6"
    var uuidStr = ""
    var seedBytes: [UInt8] = []
    var lanFired = false

    func centralManagerDidUpdateState(_ c: CBCentralManager) {
        if c.state == .poweredOn { log("BLE 扫描…"); c.scanForPeripherals(withServices: [CBUUID(string: SVC_MAIN)], options: nil) }
        else { log("BLE state=\(c.state.rawValue)") }
    }
    func centralManager(_ c: CBCentralManager, didDiscover p: CBPeripheral, advertisementData a: [String: Any], rssi R: NSNumber) {
        log("BLE 发现 \(p.name ?? "?") rssi=\(R)")
        target = p; p.delegate = self; c.stopScan(); c.connect(p, options: nil)
    }
    func centralManager(_ c: CBCentralManager, didConnect p: CBPeripheral) {
        log("BLE 已连接"); bleConnected = true; p.discoverServices(nil)
    }
    func centralManager(_ c: CBCentralManager, didDisconnectPeripheral p: CBPeripheral, error: Error?) {
        bleConnected = false
        log("BLE 断链：\(error?.localizedDescription ?? "对端断开")")
        if !lanFired {   // 身份已写，仍继续走 Wi-Fi 侧
            log("（身份写入已完成，继续走 Wi-Fi 阶段）")
            fireLAN()
        }
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
            log("BLE 枚举完成 \(chars.count) 特征")
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { self.writeIdentity() }
        }
    }
    func writeIdentity() {
        guard let p = target, bleConnected else { log("BLE 未连接，跳过写入"); fireLAN(); return }
        let dlna: [UInt8] = [0x4D,0x45,0x49,0x30,0x01,0x00,0x10,0x00,0x80,0x01] + seedBytes
        log("写身份 DLNA_UUID = \(hexs(dlna))  (accctrl value = \(uuidStr))")
        if let c = chars[CH_DLNA] { p.writeValue(Data(dlna), for: c, type: .withResponse) }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            log("写身份设备名 = MacBLE")
            if let c = self.chars[CH_NAME] { p.writeValue(Data("MacBLE".utf8), for: c, type: .withResponse) }
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { self.fireLAN() }
        }
    }
    func peripheral(_ p: CBPeripheral, didWriteValueFor ch: CBCharacteristic, error: Error?) {
        log("  ← BLE 写回调 \(ch.uuid.uuidString.prefix(8)) err=\(error?.localizedDescription ?? "成功")")
    }

    func fireLAN() {
        guard !lanFired else { return }
        lanFired = true
        let base = "http://\(camIP)/cam.cgi"
        log("=== Wi-Fi 阶段（BLE \(bleConnected ? "保持连接" : "已断")）===")
        let baseline = httpGet("\(base)?mode=accctrl&type=req_acc")
        log("基线 req_acc      → \(baseline)")
        let low = baseline.lowercased()
        let encrypted = low.contains("encrypted")

        var key: UInt32 = 0
        let g = httpGet("\(base)?mode=accctrl&type=req_acc_g")
        log("req_acc_g         → \(g)")
        let parts = g.split(separator: ",")
        if parts.count >= 2 { key = UInt32(parts[1].trimmingCharacters(in: .whitespaces), radix: 16) ?? 0 }
        log("解析密钥 key       = 0x\(String(format: "%08X", key))")

        if encrypted {
            log("链路为 encrypted → 走 req_acc_e（UUID/名字用密钥编码）")
            let ev = encodeString(uuidStr, key: key)
            let ev2 = encodeString("MacBLE", key: key)
            log("  encoded value  = \(ev)")
            log("  encoded value2 = \(ev2)")
            let r = httpGet("\(base)?mode=accctrl&type=req_acc_e&value=\(ev)&value2=\(ev2)", timeout: 15)
            log("req_acc_e         → \(r)")
        } else {
            log("链路为 open → 走明文 req_acc")
            let r = httpGet("\(base)?mode=accctrl&type=req_acc&value=\(uuidStr)&value2=MacBLE", timeout: 15)
            log("req_acc           → \(r)")
        }
        poll(0)
    }

    func poll(_ n: Int) {
        guard n < 25 else { log("轮询结束"); verify(); return }
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            let r = httpGet("http://\(self.camIP)/cam.cgi?mode=accctrl&type=req_acc")
            log("  +\(n*3)s → \(r)")
            if r.lowercased().hasPrefix("ok") && !r.lowercased().contains("err_") { self.verify(); return }
            self.poll(n + 1)
        }
    }

    func verify() {
        let base = "http://\(camIP)/cam.cgi"
        for (name, q) in [("getstate", "mode=getstate"),
                          ("getinfo capability", "mode=getinfo&type=capability"),
                          ("getinfo allmenu", "mode=getinfo&type=allmenu"),
                          ("getinfo lens", "mode=getinfo&type=lens"),
                          ("getsetting videoformat", "mode=getsetting&type=videoformat")] {
            log("   \(name.padding(toLength: 24, withPad: " ", startingAt: 0)) → \(httpGet("\(base)?\(q)", timeout: 10))")
        }
        finish()
    }
    func finish() {
        log("清理 req_acc_can → \(httpGet("http://\(camIP)/cam.cgi?mode=accctrl&type=req_acc_can&value=\(uuidStr)&value2="))")
        CFRunLoopStop(CFRunLoopGetMain())
    }
}

let args = CommandLine.arguments
let ip = args.first(where: { $0.hasPrefix("192.168.") || $0.hasPrefix("10.") }) ?? "192.168.1.131"
let seed = args.first(where: { $0.range(of: "^[0-9a-fA-F]{12}$", options: .regularExpression) != nil })
            ?? "020000025AD6"
let secs = args.compactMap { Double($0) }.first ?? 150

let p = Pair()
p.camIP = ip
p.seed = seed
p.uuidStr = "4D454930-0100-1000-8001-" + seed
p.seedBytes = stride(from: 0, to: 12, by: 2).map { i -> UInt8 in
    let s = seed.index(seed.startIndex, offsetBy: i)
    let e = seed.index(s, offsetBy: 2)
    return UInt8(seed[s..<e], radix: 16) ?? 0
}
log("目标 IP=\(p.camIP)  seed=\(seed)  UUID=\(p.uuidStr)")
log("编码自检 encodeString(\"ABC\",0x9032782C) = \(encodeString("ABC", key: DEFAULT_KEY))")
p.central = CBCentralManager(delegate: p, queue: nil)
RunLoop.main.run(until: Date().addingTimeInterval(secs))
log("窗口结束")
