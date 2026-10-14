# DC-S5 服务态 USB 通道勘察 —— 交接包

**日期**：2026-10-14 · **状态**：已完整刻画，未打通 · **承接人**：见下方「先读这个」

> ### 一句话
> **服务态 USB 个性 `04da:2370` 已被完整刻画，但三个方向全部打不通
> （EP0 厂商 IN 全 STALL、bulk OUT 八种帧格式全被 NAK、两个 IN 端点全程静默）。
> 它很可能属于松下的服务软件，而不是 LUMIX Tether。
> 剩下的工作在 Linux/Windows 上做会容易得多。**

---

## 先读这个

| 顺序 | 文件 | 内容 |
|---|---|---|
| **1** | **[`00_交接总结_全文.md`](00_交接总结_全文.md)** | **总入口**：背景 / 已确认事实 / 已排除路径 / 两个未解异常 / 交接任务 / 安全红线 |
| **2** | [`01_实测记录.md`](01_实测记录.md) | 逐条原始实测输出，可复核每条结论 |
| **3** | [`02_工具/README.md`](02_工具/README.md) | 三个工具的用法、编译、**跨平台替代方案** |
| **4** | [`03_Tether协议线索.md`](03_Tether协议线索.md) | 从 Tether v2.12 反汇编挖出的设备选择器与 PID 逻辑 |

---

## 承接人最该做的四件事

| # | 任务 | 风险 | 在哪做 |
|---|---|---|---|
| **1** | **用 LUMIX Tether 在正常模式 `0x2382` 下抓包**，拿官方协议帧格式 | 🟢 零 | **Windows（USBPcap）/ Linux（usbmon）** |
| 2 | EP0 **零长度厂商 OUT** 探针 —— `0x2370` 唯一未测方向 | 🟡 低 | Linux（pyusb）最方便 |
| 3 | 枚举相机全部 USB 模式，画全 PID 地图 | 🟢 零 | 任意平台 |
| 4 | 复核「历史记录说写入成功、本次实测超时」的矛盾 | 🟢 零 | macOS 可用本包工具 |

**任务 1 是本包的推荐主线**；任务 2 是唯一可能真正打开服务层的一步。

---

## 本包内容

```
13_USB服务通道勘察_交接包_20261014/
├── README.md                  ← 本文件
├── 00_交接总结_全文.md         ← ★ 总入口
├── 01_实测记录.md              ← 原始输出存档
├── 02_工具/
│   ├── README.md              ← 用法 / 编译 / 跨平台
│   ├── s5_usb_desc.c          ← 描述符 dump（纯只读）
│   ├── s5_usb_listen.c        ← 监听 + 可选写入
│   └── s5_usb_ep0.c           ← EP0 厂商 IN 扫描（纯只读）
└── 03_Tether协议线索.md        ← 反汇编发现
```

**编译**（macOS，无第三方依赖）：

```bash
cd 02_工具
clang -O2 -Wall -framework IOKit -framework CoreFoundation -o s5_usb_desc   s5_usb_desc.c
clang -O2 -Wall -framework IOKit -framework CoreFoundation -o s5_usb_listen s5_usb_listen.c
clang -O2 -Wall -framework IOKit -framework CoreFoundation -o s5_usb_ep0    s5_usb_ep0.c
```

---

## ⚠️ 三条必须遵守

1. **本包中 `s5_usb_desc` 与 `s5_usb_ep0` 是纯只读的**；
   `s5_usb_listen` 默认被动只读，仅 `--ptp` / `--tryall` / `--hex` 会写入
2. **服务菜单里除 `DSC→SD`（导出）外一律不碰**
   —— `SD*→DSC`（写回）、`ADJFLAG→ALL F`、`WBADJ→STEPMODE` 都可能**不可逆**
3. **绝不真刷固件**
4. **本包与实测记录中含机身序列号**（字符串索引 3，`XJL########15`）
   —— **对外分发前必须脱敏**

---

## 安全收尾

- 退出服务模式：按住 **`AF ON` + `方向右键`** 关机
- 相机异常：拔电池 10 秒
- USB 被工具 `Seize` 抢走：拔插一次即恢复
