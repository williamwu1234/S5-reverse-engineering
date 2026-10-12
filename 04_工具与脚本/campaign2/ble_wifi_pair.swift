// ble_wifi_pair.swift — 同时使用 BLE + Wi-Fi，复现 LUMIX Sync 的「注册身份 → 请求授权」链路
//
// 假设（来自 APK 交叉阅读）：
//   · BLE 侧写入的 DLNA_UUID（H5/p.java:272  "4D454930010010008001" + seed）与
//     Wi-Fi 侧 accctrl 的 value（H5/p.java:1515 "4D454930-0100-1000-8001-" + seed）
//     是【同一个 seed】——BLE 注册的身份就是 Wi-Fi 请求授权时用的身份。
//   · 相机热点侧 accctrl 报 open（明文），所以按 com/panasonic/jp/service/c.java 走 req_acc（不编码）。
//
// 流程：
//   1) BLE：连接相机 → 写身份（8D08A420 = 原始 UUID 字节；CD7A71A0 = 设备名）→ **保持连接**
//   2) HTTP：accctrl req_acc 基线 → req_acc&value=<UUID>&value2=<name>
//   3) 轮询授权状态（最长 120s）——若机身弹确认，请在相机上点「允许」
//   4) 授权后立刻复测读端点
//   5) req_acc_can 清理
//
// 用法: ./ble_wifi_pair <相机IP(可选)> [秒数]
import Foundation
import CoreBluetooth

let SVC_MAIN   = "054AC620-3214-11E6-AC0D-0002A5D5C51B"
let CH_DLNA    = "8D08A420-3213-11E6-8ACA-0002A5D5C51B"   // 非APS：写原始 UUID
let CH_NAME    = "CD7A71A0-3213-11E6-8F56-0002A5D5C51B"   // 非APS：写原始设备名

let SEED = "020000025AD6"                                  // 两边必须同一个 seed
let UUID_STR = "4D454930-0100-1000-8001-" + SEED
let SEED_BYTES: [UInt8] = [0x02, 0x00, 0x00, 0x02, 0x5A, 0xD6]
let DLNA_UUID: [UInt8] = [0x4D, 0x45, 0x49, 0x30, 0x01, 0x00, 0x10, 0x00, 0x80, 0x01] + SEED_BYTES
let DEV_NAME = "MacBLE"

func ts() -> String { let f = DateFormatter(); f.dateFormat = "HH:mm:ss.SSS"; return f.string(from: Date()) }
func log(_ s: String) { print("[\(ts())] \(s)") }
func hex(_ d: [UInt8]) -> String { d.map { String(format: "%02x", $0) }.joined() }

// ---------------- HTTP ----------------
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

// ---------------- BLE ----------------
final class Pair: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    var central: CBCentralManager!
    var target: CBPeripheral?
    var chars: [String: CBCharacteristic] = [:]
    var svcTotal = 0, svcDone = 0
    var bleReady = false
    var camIP = "192.168.54.1"
    var started = false
    var bleConnected = false

    func centralManagerDidUpdateState(_ c: CBCentralManager) {
        if c.state == .poweredOn {
            log("BLE 扫描…")
            c.scanForPeripherals(withServices: [CBUUID(string: SVC_MAIN)], options: nil)
        } else { log("BLE state=\(c.state.rawValue)") }
    }
    func centralManager(_ c: CBCentralManager, didDiscover p: CBPeripheral, advertisementData a: [String: Any], rssi R: NSNumber) {
        log("BLE 发现 \(p.name ?? "?") rssi=\(R)")
        target = p; p.delegate = self; c.stopScan(); c.connect(p, options: nil)
    }
    func centralManager(_ c: CBCentralManager, didConnect p: CBPeripheral) {
        log("BLE 已连接 → discoverServices"); bleConnected = true; p.discoverServices(nil)
    }
    func centralManager(_ c: CBCentralManager, didDisconnectPeripheral p: CBPeripheral, error: Error?) {
        bleConnected = false
        log("BLE 断链：\(error?.localizedDescription ?? "对端断开")")
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
            log("BLE 枚举完成 \(chars.count) 特征 → 写身份")
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { self.writeIdentity() }
        }
    }
    func writeIdentity() {
        guard let p = target, bleConnected else { log("BLE 未连接，跳过写入"); afterBLE(); return }
        log("写 DLNA_UUID(原始) = \(hex(DLNA_UUID))  →  对应 accctrl value = \(UUID_STR)")
        if let c = chars[CH_DLNA] { p.writeValue(Data(DLNA_UUID), for: c, type: .withResponse) }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            log("写设备名(原始) = \(hex(Array(DEV_NAME.utf8)))")
            if let c = self.chars[CH_NAME] { p.writeValue(Data(DEV_NAME.utf8), for: c, type: .withResponse) }
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { self.afterBLE() }
        }
    }
    func peripheral(_ p: CBPeripheral, didWriteValueFor ch: CBCharacteristic, error: Error?) {
        log("  ← BLE 写回调 \(ch.uuid.uuidString.prefix(8)) err=\(error?.localizedDescription ?? "成功")")
    }

    // ---------- BLE 身份写完后，走 Wi-Fi accctrl ----------
    func afterBLE() {
        guard !bleReady else { return }
        bleReady = true
        let base = "http://\(camIP)/cam.cgi"
        log("=== 进入 Wi-Fi 阶段（BLE 连接\(bleConnected ? "保持中" : "已断")）===")
        log("基线 req_acc      → \(httpGet("\(base)?mode=accctrl&type=req_acc"))")
        log("req_acc_g         → \(httpGet("\(base)?mode=accctrl&type=req_acc_g"))")
        log("发起 req_acc      → \(httpGet("\(base)?mode=accctrl&type=req_acc&value=\(UUID_STR)&value2=\(DEV_NAME)", timeout: 12))")
        poll(0)
    }

    func poll(_ n: Int) {
        guard n < 40 else { log("轮询结束"); finish(); return }
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            let r = httpGet("http://\(self.camIP)/cam.cgi?mode=accctrl&type=req_acc")
            log("  +\(n * 3)s 状态 → \(r)")
            if r.lowercased().hasPrefix("ok") && !r.lowercased().contains("err_") {
                log(">>> 状态 ok：判定已授权！立刻复测读端点")
                self.verify()
                return
            }
            self.poll(n + 1)
        }
    }

    func verify() {
        let base = "http://\(camIP)/cam.cgi"
        for (name, q) in [("getstate", "mode=getstate"),
                          ("getinfo capability", "mode=getinfo&type=capability"),
                          ("getinfo allmenu", "mode=getinfo&type=allmenu"),
                          ("getinfo curmenu", "mode=getinfo&type=curmenu"),
                          ("getinfo lens", "mode=getinfo&type=lens"),
                          ("getsetting videoformat", "mode=getsetting&type=videoformat")] {
            log("   \(name.padding(toLength: 24, withPad: " ", startingAt: 0)) → \(httpGet("\(base)?\(q)", timeout: 10))")
        }
        finish()
    }

    func finish() {
        log("清理 req_acc_can → \(httpGet("http://\(camIP)/cam.cgi?mode=accctrl&type=req_acc_can&value=\(UUID_STR)&value2="))")
        try? "done\n".write(toFile: "/tmp/ble_wifi_pair_done", atomically: true, encoding: .utf8)
        CFRunLoopStop(CFRunLoopGetMain())
    }
}

let secs = CommandLine.arguments.compactMap { Double($0) }.first ?? 180
let pair = Pair()
// 相机 IP：优先命令行给的
for a in CommandLine.arguments where a.hasPrefix("192.168.") || a.hasPrefix("10.") { pair.camIP = a }
pair.central = CBCentralManager(delegate: pair, queue: nil)
log("目标：BLE 身份 \(UUID_STR) / Wi-Fi \(pair.camIP)")
RunLoop.main.run(until: Date().addingTimeInterval(secs))
log("窗口结束")
