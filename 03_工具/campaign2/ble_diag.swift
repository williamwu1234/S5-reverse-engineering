// ble_diag.swift — DC-S5 BLE 完整诊断：枚举 → 描述符 → 通知 → 读 → (可选)写
//
// 目的：搞清"一读即断"到底是什么操作触发的，以及 macOS 能否触发 BLE 绑定。
//
// 用法：
//   ./ble_diag [--write] [秒数]
//     --write   额外尝试一次 1 字节写（默认不写）
//
// 所有结果写 stdout，同时留时间戳，便于和 macOS 蓝牙日志对齐。
import Foundation
import CoreBluetooth

let SVC_MAIN = "054AC620-3214-11E6-AC0D-0002A5D5C51B"
let DO_WRITE = CommandLine.arguments.contains("--write")
let SECS = CommandLine.arguments.compactMap { Double($0) }.first ?? 60

func ts() -> String {
    let f = DateFormatter(); f.dateFormat = "HH:mm:ss.SSS"
    return f.string(from: Date())
}
func hex(_ d: Data?) -> String {
    guard let d = d else { return "(nil)" }
    return d.prefix(24).map { String(format: "%02x", $0) }.joined()
}

final class Diag: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    var central: CBCentralManager!
    var target: CBPeripheral?
    var servicesDone = 0, svcTotal = 0
    var charsDone = 0, charsTotal = 0
    var descDone = 0
    var allChars: [CBCharacteristic] = []
    var services: [CBService] = []
    var phase = "init"
    var disconnected = false

    func log(_ s: String) { print("[\(ts())] \(s)") }

    func centralManagerDidUpdateState(_ c: CBCentralManager) {
        if c.state == .poweredOn {
            log("central poweredOn, 扫描…")
            c.scanForPeripherals(withServices: [CBUUID(string: SVC_MAIN)], options: nil)
        } else { log("central state=\(c.state.rawValue)") }
    }

    func centralManager(_ c: CBCentralManager, didDiscover p: CBPeripheral,
                        advertisementData a: [String: Any], rssi R: NSNumber) {
        log("发现 \(p.name ?? "?") rssi=\(R) —— 连接（不配对）")
        target = p; p.delegate = self
        c.stopScan()
        c.connect(p, options: nil)
    }

    func centralManager(_ c: CBCentralManager, didConnect p: CBPeripheral) {
        log("已连接，开始 discoverServices")
        phase = "discover-services"
        p.discoverServices(nil)
    }

    func centralManager(_ c: CBCentralManager, didFailToConnect p: CBPeripheral, error: Error?) {
        log("连接失败: \(error?.localizedDescription ?? "?")")
    }

    func centralManager(_ c: CBCentralManager, didDisconnectPeripheral p: CBPeripheral, error: Error?) {
        disconnected = true
        log(">>> 断链！phase=\(phase)  error=\(error?.localizedDescription ?? "clean(对端主动断开)")")
        save(); CFRunLoopStop(CFRunLoopGetMain())
    }

    func peripheral(_ p: CBPeripheral, didDiscoverServices error: Error?) {
        if let e = error { log("discoverServices ERR \(e.localizedDescription)"); return }
        services = p.services ?? []
        svcTotal = services.count
        for s in services { p.discoverCharacteristics(nil, for: s) }
        log("服务数 = \(svcTotal)")
    }

    func peripheral(_ p: CBPeripheral, didDiscoverCharacteristicsFor s: CBService, error: Error?) {
        charsDone += 1
        let cs = s.characteristics ?? []
        allChars += cs
        log("  服务 \(s.uuid.uuidString.prefix(8)) → \(cs.count) 个特征")
        for ch in cs {
            let pr = ch.properties
            var f: [String] = []
            if pr.contains(.read) { f.append("R") }
            if pr.contains(.write) { f.append("W") }
            if pr.contains(.writeWithoutResponse) { f.append("w") }
            if pr.contains(.notify) { f.append("N") }
            if pr.contains(.indicate) { f.append("I") }
            log("    \(ch.uuid.uuidString) [\(f.joined())]")
        }
        if charsDone == svcTotal {
            charsTotal = allChars.count
            log("特征总数 = \(charsTotal)；开始逐个 discoverDescriptors")
            phase = "discover-descriptors"
            descNext(0)
        }
    }

    func descNext(_ idx: Int) {
        guard let p = target else { return }
        if idx >= allChars.count {
            log("描述符发现完成（\(descDone) 个特征有描述符）")
            afterDescriptors()
            return
        }
        p.discoverDescriptors(for: allChars[idx])
    }

    func peripheral(_ p: CBPeripheral, didDiscoverDescriptorsFor ch: CBCharacteristic, error: Error?) {
        let ds = ch.descriptors ?? []
        if !ds.isEmpty {
            descDone += 1
            log("    DESC \(ch.uuid.uuidString.prefix(8)): \(ds.map { $0.uuid.uuidString }.joined(separator: ","))")
        }
        descNext(allChars.firstIndex(of: ch).map { $0 + 1 } ?? allChars.count)
    }

    func afterDescriptors() {
        guard let p = target, !disconnected else { return }
        // ---- 步骤 A：通知订阅（等价 App 的 registNotify；写 CCCD） ----
        if let n = allChars.first(where: { $0.properties.contains(.notify) }) {
            phase = "setNotify(\(n.uuid.uuidString.prefix(8)))"
            log("步骤A: setNotifyValue(true) on \(n.uuid.uuidString) （会写 CCCD 描述符）")
            p.setNotifyValue(true, for: n)
        } else {
            log("步骤A: 没有 notify 特征，跳过")
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 6) { self.stepRead() }
    }

    func peripheral(_ p: CBPeripheral, didUpdateNotificationStateFor ch: CBCharacteristic, error: Error?) {
        log("  ← 通知状态回调 \(ch.uuid.uuidString.prefix(8)) isNotifying=\(ch.isNotifying) err=\(error?.localizedDescription ?? "无")")
    }

    func stepRead() {
        guard let p = target, !disconnected else { return }
        if let r = allChars.first(where: { $0.properties.contains(.read) }) {
            phase = "read(\(r.uuid.uuidString.prefix(8)))"
            log("步骤B: readValue on \(r.uuid.uuidString)")
            p.readValue(for: r)
        } else { log("步骤B: 无可读特征") }
        DispatchQueue.main.asyncAfter(deadline: .now() + 8) { self.stepWrite() }
    }

    func peripheral(_ p: CBPeripheral, didUpdateValueFor ch: CBCharacteristic, error: Error?) {
        log("  ← 读回调 \(ch.uuid.uuidString.prefix(8)) value=\(hex(ch.value)) err=\(error?.localizedDescription ?? "无")")
    }

    func stepWrite() {
        guard let p = target, !disconnected else { return }
        guard DO_WRITE else { log("步骤C: 未启用写（加 --write 才做）"); finish(); return }
        if let w = allChars.first(where: { $0.properties.contains(.write) || $0.properties.contains(.writeWithoutResponse) }) {
            phase = "write(\(w.uuid.uuidString.prefix(8)))"
            log("步骤C: writeValue(0x00) on \(w.uuid.uuidString)  ← 可能触发系统配对")
            p.writeValue(Data([0x00]), for: w, type: .withResponse)
        } else { log("步骤C: 无可写特征") }
        DispatchQueue.main.asyncAfter(deadline: .now() + 10) { self.finish() }
    }

    func peripheral(_ p: CBPeripheral, didWriteValueFor ch: CBCharacteristic, error: Error?) {
        log("  ← 写回调 \(ch.uuid.uuidString.prefix(8)) err=\(error?.localizedDescription ?? "成功")")
    }

    func finish() {
        log("诊断结束（未断链）")
        save()
        CFRunLoopStop(CFRunLoopGetMain())
    }

    func save() {
        let s = "phase=\(phase) disconnected=\(disconnected) services=\(svcTotal) chars=\(charsTotal) desc=\(descDone)\n"
        try? s.write(toFile: "/tmp/ble_diag_result.txt", atomically: true, encoding: .utf8)
    }
}

let d = Diag()
d.central = CBCentralManager(delegate: d, queue: nil)
RunLoop.main.run(until: Date().addingTimeInterval(SECS))
print("[\(ts())] 窗口结束 phase=\(d.phase) disconnected=\(d.disconnected)")
