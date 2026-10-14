# LUMIX Tether 协议线索（从 v2.12 反汇编挖出）

**素材位置**（不在本包内）：
- `07_参考仓库/s1m2-research/analysis/tether_2_12_ptp_arm64_disassembly.txt`（16 MB，**带符号**）
- `07_参考仓库/s1m2-research/analysis/tether_2_12_app_arm64_disassembly.txt`（12 MB）
- `07_参考仓库/s1m2-research/analysis/tether_client_transport_paths.json`（函数级调用图，120 KB）

Tether 安装包松下仍在官网公开提供（约 74 MB）：
<https://av.jpn.support.panasonic.com/support/software/lumixtether/download/d_lumixtether2.html>

---

## 1. 设备选择器（关键发现）

在 `tether_2_12_ptp_arm64_disassembly.txt` 偏移 `0x33200`–`0x33320`，有一个按
`ConnectDevType` 选 PID 的函数。日志字符串佐证参数名：

```
literal pool for: "Enter %s - ConnectDevType:%d, pDeviceName:%s\015\n"
```

反汇编逻辑（已整理为 C）：

```c
VID = 0x04da;
PID = 0x2382;              /* 默认 */
cmp  w19, #0x2
b.hi → 默认路径

cbz  w19, 0x332dc          /* w19 == 0 */
...
cmp  w19, #0x1
b.ne 0x332d4
/* w19 == 1 */
VID = 0x04da;
PID = 0x2374;
b 0x33320

0x332dc:                   /* w19 == 0 */
VID = 0x04da;
PID = 0x2382;
/* 并写入字符串："/PTPRemote/Server0/ddd" 与 "PTPRemoteView" */
```

**整理成表**：

| `ConnectDevType` | VID | PID | 附带 |
|---|---|---|---|
| **0** | 0x04da | **0x2382** | IOKit 路径 `/PTPRemote/Server0/ddd`、服务名 `PTPRemoteView` |
| **1** | 0x04da | **0x2374** | 不写驱动路径 |
| ≥2 | 默认 | 0x2382 | — |

**结论**
1. **Tether 只认 `0x2382` 与 `0x2374` 两个 PID**
2. **`0x2370` 不在其中** ⇒ 服务态的 USB 个性**不是 Tether 通道**
3. 类型 0 带 `/PTPRemote/Server0/ddd` 驱动路径、类型 1 不带
   ⇒ 类型 1 是**老机型兼容路径**

---

## 2. 关于 `0x2374` —— 已查清，与本机无关

我曾据上表推断"`0x2374` 是 S5 应该切过去的目标模式"。**这个推断是错的，已作废。**

**证据**：gphoto-devel 邮件列表明确记录
**`04da:2374` = 松下 DMC-FZ28（2008 年便携机）**
（[原始邮件](https://sourceforge.net/p/gphoto/mailman/message/22155036/)：
"Panasonic DMC-FZ28: 04da:2374 PTP ok, 04da:2372 storage fails"）。

⇒ **`0x2374` 与 DC-S5 无关，不要去找。**

---

## 3. 对 S5 的实际含义

| PID | 身份 | 谁能驱动 |
|---|---|---|
| **`0x2382`** | S5 **正常 PTP / PC 模式** | ✅ **LUMIX Tether（类型 0）** + 项目已有 `s5_ptp_dump` |
| `0x2370` | S5 服务态 / `!→LUMIX` 态 | ❓ 未知（不是 Tether）——推测是**松下服务软件**通道 |

**⇒ Tether 本来就支持 S5，走的是正常模式 `0x2382`，不是 `0x2370`。**

这正是交接总结 §6 **任务 1** 的基础：**在正常模式下用 Tether 连上并抓包，
即可拿到松下官方厂商协议的完整帧格式。**

---

## 4. 抓包能拿到什么

调用图 JSON 里能看到带符号的函数名，例如：

```
__ZN11lumixtether13DeviceAdapter37adp_LMX_func_api_FirmwareUpdate_startE7QStringS1_b
  = lumixtether::DeviceAdapter::adp_LMX_func_api_FirmwareUpdate_start(QString, QString, bool)
```

`adp_LMX_func_api_*` 是 Tether 的 API 面，涵盖实时取景、设置读写、
**固件更新**等。抓到真实流量即可确定每一帧的
**头部 / 长度 / 类型 / 事务 ID / 负载**结构。

> **诚实提示**：Tether 是**消费级遥控软件**。
> 它的协议**大概率不会直接给出 root 或固件明文**——它是来遥控拍照的。
> 但它是**松下官方协议**、有 16 MB 带符号反汇编做对照，是当前最确定的收获。
> 真正通向服务层的是 `0x2370`，见交接总结 §6 任务 2。

---

## 5. 复核方法（可自行验证本文结论）

```bash
cd 07_参考仓库/s1m2-research/analysis

# 看设备选择器
grep -n -A25 "ConnectDevType" tether_2_12_ptp_arm64_disassembly.txt | head -40

# 确认 Tether 只含这两个 PID（注意：必须搜【立即数】形式）
grep -nE "#0x2382|#0x2374" tether_2_12_ptp_arm64_disassembly.txt

# 排除误报：0x2370 从未作为立即数出现，
# 之前命中的是 adrp 地址页 0x237000（OpenSSL 的 ASN.1/DH 代码），属巧合
grep -nE "#0x2370" tether_2_12_ptp_arm64_disassembly.txt || echo "无立即数命中（已确认）"
```

⚠️ **踩坑提醒**：`grep 0x2370` 会命中 `adrp x3, 411 ; 0x237000` 这类**地址页引用**。
判读 USB PID 必须看 **`mov w?, #0x____` 立即数形式**，否则会得出错误结论
（我第一遍就是这么错的）。
