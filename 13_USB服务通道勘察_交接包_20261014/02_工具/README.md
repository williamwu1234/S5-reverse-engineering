# 工具说明与编译

三个 C 源码，**全部针对 macOS 的 IOUSBLib**。如果你在 Linux/Windows 上，见文末
「跨平台替代」。

---

## 编译（macOS）

```bash
clang -O2 -Wall -framework IOKit -framework CoreFoundation -o s5_usb_desc   s5_usb_desc.c
clang -O2 -Wall -framework IOKit -framework CoreFoundation -o s5_usb_listen s5_usb_listen.c
clang -O2 -Wall -framework IOKit -framework CoreFoundation -o s5_usb_ep0    s5_usb_ep0.c
```

无需任何第三方依赖（只用系统框架）。

---

## `s5_usb_desc` —— 描述符 dump（**纯只读**）

```bash
./s5_usb_desc [--list] [vid] [pid] [--strings N] [--no-open]
```

- 默认 `04da:2370`，`--strings 64`
- **不调 `SetConfiguration`、不开接口、不碰任何管道**，只做标准第 9 章 `GET_DESCRIPTOR`
- 输出：设备描述符、**每一个**配置（含原始 hex 与解析出的接口/端点）、语言 ID、
  1..N 号字符串描述符、IOKit 注册表属性（含 CFData 十六进制）

**当前实现要点**：配置索引按 **0 起**（`for i = 0; i < ncfg`）。
⚠️ 旧的 `s5_ptp_raw.c` 写的是 `for (cfg = 1; ...)`，**会漏掉配置 0**，同一 bug 请勿再犯。

---

## `s5_usb_listen` —— 监听 + 可选写入

```bash
./s5_usb_listen [秒数] [vid] [pid] [--ptp] [--tryall] [--hex <hex串>] [--cfg N]
```

| 模式 | 是否写入 | 说明 |
|---|---|---|
| **（默认）** | ❌ | 被动监听 interrupt IN 与 bulk IN |
| `--ptp` | ✅ 1 次 | 发一条 PTP OpenSession (0x1002) |
| `--tryall` | ✅ ≤8 次 | 依次试 8 种候选帧格式，报告哪一种被设备接受 |
| `--hex "01 02 03"` | ✅ 1 次 | 发自定义载荷 |
| `--cfg N` | — | 打开接口前强制 `SetConfiguration(N)` |

**写入结果判读**：
- `0x00000000` → **被接受**（`** ACCEPTED by the device **`）
- `0xe0004051` → `kIOUSBTransactionTimeout`，**设备 NAK，不接收**

---

## `s5_usb_ep0` —— EP0 厂商请求扫描（**纯只读**）

```bash
./s5_usb_ep0 [vid] [pid] [--max N] [--types 80,c0,c1,c2]
```

- 默认扫 `0xC0`/`0xC1`/`0xC2` × `bRequest 0x00..0x40`
- `--max 255` 扫全范围

**安全保证**：`ep0_in()` 开头硬性断言 `bmRequestType & 0x80`，
非 IN 请求直接拒绝执行 ⇒ **这个工具物理上无法向设备写入任何数据**。

> **它不实现厂商 OUT 请求**（`bmRequestType = 0x40`）。那是唯一未测方向，
> 需要**另写工具**，见交接总结 §6 任务 2。

---

## 跨平台替代（**推荐 Linux/Windows**）

macOS 做 USB 抓包很不方便（要手动 `ifconfig XHC20 up`，Apple Silicon 上接口名还不固定，
本机也未装 Wireshark）。**剩下的工作换平台会容易得多。**

### Linux

```bash
# 描述符
lsusb -v -d 04da:2370            # 含全部字符串描述符

# 原始控制传输（读）
python3 -c "
import usb.core
d = usb.core.find(idVendor=0x04da, idProduct=0x2370)
try:
    print(d.ctrl_transfer(0xc0, 0x01, 0, 0, 64, timeout=500).tobytes().hex())
except Exception as e:
    print('STALL/err:', e)
"

# 抓包（Tether 流量）
sudo modprobe usbmon
sudo tcpdump -i usbmon1 -w usb.pcap
```

### Windows

- **USBPcap + Wireshark** —— 抓 Tether 流量最省事的一套
- 描述符：USB Device Tree Viewer (UsbTreeView)

### 通用

- 抓包文件可直接用 Wireshark 打开，它自带 USB/PTP 解析器

---

## ⚠️ 安全边界

| 工具 | 能否写入设备 |
|---|---|
| `s5_usb_desc` | ❌ 完全不能 |
| `s5_usb_ep0` | ❌ 完全不能（代码内断言） |
| `s5_usb_listen` | 默认不能；仅 `--ptp`/`--tryall`/`--hex` 会写 |

- 三个工具都**不发送任何厂商 opcode**（除了 `--ptp` 那条标准 PTP OpenSession）
- 若系统驱动占着设备，工具会 `USBDeviceOpenSeize` 抢过来
  —— **只影响当前会话，拔插 USB 即恢复**
- **绝不真刷固件**（见交接总结 §7）
