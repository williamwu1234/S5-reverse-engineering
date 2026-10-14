# S5 Monitor —— DC-S5 无线监看 + 触摸对焦

**复刻 LUMIX 官方取景逻辑的第三方监看方案。**
让 **S5** 也能拥有 LUMIX Flow / LUMIX Sync 那种「**手机当监视器 + 点屏对焦**」的体验。

> 官方 LUMIX Flow **不支持 S5**（只面向 S9 / GH7 / S5II / S5IIX / G9II 等新机型）。
> 但 S5 硬件**自带取景推流能力**（`cam.cgi mode=startstream`），本工具把它接出来。

---

## 它是什么

```
相机 Wi-Fi (SoftAP 或家庭网)
      │  cam.cgi  mode=startstream&value=49152
      ▼
   相机把【MJPEG 取景流】发到 UDP 49152
      │
      ▼
   s5monitor.py  ──►  HTTP multipart/x-mixed-replace
      │
      ▼
   手机 / 平板 / 电脑浏览器打开  http://<本机IP>:8080
   （浏览器原生支持 MJPEG，**不需要装任何 App**）
```

---

## 复刻了官方的哪些逻辑

| 步骤 | 官方做法 | 本工具 |
|---|---|---|
| ① 配对 | `accctrl type=req_acc` + 设备身份 | ✅ 同（身份格式逆向自 `H5/p.java`：`4D454930-0100-1000-8001-<seed>`） |
| ② 授权判定 | `getstate` 返回 `ok` 才算授权 | ✅ 同（`ok_under_research` **不算**） |
| ③ 进拍摄模式 | `camcmd value=recmode` | ✅ 同 |
| ④ 取景流 | `startstream value=<UDP端口 49152–65535>` | ✅ 同 |
| ⑤ **心跳保活** | 周期性 `getstate` | ✅ 同（8 秒一次；**不发心跳相机会停流**） |
| ⑥ 触摸对焦 | `camctrl type=touch value=x,y` | ✅ 同（坐标按取景流实际分辨率换算） |
| ⑦ 连续拖动对焦 | `camctrl type=touch_trace` | ✅ 同（约 10Hz 限流） |
| ⑧ 放大辅助 | `camctrl type=change_disp_mag` | ✅ 同 |
| ⑨ 峰值/辅助显示 | `camctrl type=asst_disp` | ✅ 同 |
| ⑩ AE 锁定 | `camctrl type=af_ae_lock` | ✅ 同 |
| ⑪ 拍照 / 录像 | `camcmd value=capture / video_recstart / video_recstop` | ✅ 同 |
| ⑫ 收尾 | `stopstream` | ✅ 同 |

**并且复刻了官方的 UI 布局**：顶部状态栏（连接/模式/fps/电量）、画面区域、
**底部四段式控制栏**（回放 / 拍摄 · 录像 ● · 快门 · AE锁定 / 信息）、点屏绿色对焦框、录像计时、全屏。

---

## 快速开始

### 1. 让电脑连上相机

**方式 A（推荐，最简单）**：相机开 Wi-Fi 热点（SoftAP）
```
相机菜单 → Wi-Fi → 新连接 → 用手机/电脑连接（或「遥控拍摄」）
电脑 Wi-Fi 连到 SSID 形如  S5-XXXXXX  的网络
网关就是  192.168.54.1
```
> ⚠️ SoftAP 只在 **BLE 会话保持期间**或相机主动开启「遥控拍摄」时才在线。
> 若用手机 App 配对过，需保持相机处于等待连接状态。

**方式 B**：相机和电脑接同一个路由器，用相机在局域网里的 IP（本项目实测 `192.168.x.x`）

### 2. 启动

```bash
cd 04_工具与脚本/s5_monitor
python3 s5monitor.py                      # 默认 192.168.54.1
python3 s5monitor.py --host 192.168.x.x # 家庭网
python3 s5monitor.py --no-stream          # 只起控制台，不自动取景
```

启动后终端会依次打印官方的四步：
```
① 配对（accctrl req_acc）…
② 切拍摄模式（camcmd recmode）…
③ 请求取景流（startstream）…
 打开浏览器：  http://<本机IP>:8080
```

### 3. 打开监视器

手机/电脑浏览器访问 **`http://<电脑IP>:8080`**（终端会提示；也可用 `ipconfig getifaddr en0` 查）。

> iPhone 上建议「添加到主屏幕」，就和一个 App 一样（全屏、无地址栏）。

---

## 界面操作

| 操作 | 效果 |
|---|---|
| **点画面** | 触摸对焦（绿框落点 = 对焦点；出画框显示红框） |
| **按住拖动** | 连续移动对焦点（`touch_trace`） |
| **双指捏合** | 变焦（本地视觉 + `frame_ctrl`） |
| 底部 **快门** | 拍照（`camcmd capture`） |
| 中间 **◉** | 录像起/停（带计时） |
| **回放 / 拍摄** | 模式切换 |
| **AE 锁定** | `af_ae_lock` |
| 工具条 **放大辅助 / 峰值** | `change_disp_mag` / `asst_disp` |
| **＋ / － 变焦** | 步进变焦 |
| **停流** | 省电（相机停止推送） |

---

## 参数

| 参数 | 默认 | 说明 |
|---|---|---|
| `--host` | `192.168.54.1` | 相机 IP |
| `--port` | `8080` | 本机 HTTP 端口 |
| `--udp` | `49152` | 取景流 UDP 端口（官方允许 49152–65535） |
| `--device-id` | `4D454930-0100-1000-8001-020A0003BD13` | 配对身份（官方格式；固定值可用） |
| `--device-name` | `S5Monitor` | 设备名（会显示在相机屏幕上） |
| `--no-stream` | — | 不自动取景 |

---

## ⚠️ 安全边界

**只发送已验证的常规控制命令**：
```
accctrl(req_acc) / getstate / getinfo / getsetting / setsetting(白名单) /
camcmd(recmode/capture/video_recstart/video_recstop/pictmode/playmode) /
camctrl(touch/touch_trace/pinch/change_disp_mag/asst_disp/af_ae_lock/frame_ctrl/...) /
startstream / stopstream / playcmd
```

**代码里带白名单，绝不发送**：
```
startsenddata / senddata / endsenddata（上传通道）
camcmd=poweroff（关机）
任何 0x9406 子码 / 格式化 / 重置 / 固件升级
```

> 本项目已实机确认：**升级请求类命令有高砖机风险**，因此永久排除。

---

## 排错

| 现象 | 原因与处理 |
|---|---|
| 页面显示但**画面全黑、fps 为 0** | 取景流没起来。确认：① 电脑确实连到了相机网络 ② 相机没有在回放/菜单里 ③ 先按「停流」再按「开始」 |
| 终端提示**未授权** | 相机机身上通常会弹「允许连接？」→ 在相机上点允许；或先在相机 [Wi-Fi] 设置里允许本设备 |
| **一点画面相机就断流** | 心跳没发出去（电脑和相机不在同一网段）。用 `ping 192.168.54.1` 验证 |
| 对焦点**偏了** | 首帧加载后脚本会自动用取景流实际分辨率校正；若仍偏，可在控制台看 `live.naturalWidth/Height` 是否合理 |
| 相机**卡顿/发热** | 按「停流」省电；长时间监看建议接 AC |
| 浏览器提示**不安全** | 纯局域网 HTTP，正常；本工具不上传任何数据 |

---

## 与「HDMI 采集卡」方案对比

| | 本方案 | HDMI 采集卡 |
|---|---|---|
| 延迟 | 中（Wi-Fi + MJPEG） | **极低** |
| 画质 | 取景流分辨率 | **最高** |
| **触摸对焦** | ✅ **有** | ❌ 无 |
| 远程控制（拍照/录像/参数） | ✅ 有 | ❌ 无 |
| 便携 | ✅ 只要有 Wi-Fi | 需要线+采集卡 |
| 占用相机资源 | 有（推流） | 无 |

**两者互补**：**要画质用 HDMI，要控制用本工具。**

---

## 技术参考

本工具的逻辑与协议还原，来自本项目的既有成果：

- `01_研究报告/02_研究总报告_20261011/research/PROTOCOL_AUDIT.md` —— `cam.cgi` 全模式表（`camctrl` 的子类型、`startstream` 的 UDP 端口范围）
- `01_研究报告/15_蓝牙BLE协议逆向_20261013.md` —— 配对身份格式 `4D454930-0100-1000-8001-<seed>`
- `01_研究报告/20_BLE身份与WiFi门独立_20261013.md` —— 授权门控（裸 `ok` 才算）
- 外部参考：`pylumix`（Python 控制松下相机）与 `libgphoto2 lumix` 驱动


---

## 📊 实机实测数据（2026-10-13，DC-S5 固件 VD4.30）

用本工具在**真实相机**上跑出来的硬数据：

| 项 | 实测值 |
|---|---|
| 取景流协议 | **MJPEG**（每包一帧，SOI `ffd8` … EOI `ffd9`） |
| **取景流分辨率** | **640 × 432**（3:2，与传感器一致） |
| 帧率 | **18.7 – 19.8 fps** |
| 单帧大小 | 约 **25 KB** |
| 取景流 UDP 端口 | 49152（官方允许 49152–65535）✅ |
| 授权 | `getstate` **直接返回 `ok`**（无需再配对） |
| 服务端 CPU 占用 | 极低（纯转发） |

### ⚠️ 两条关键协议行为（都是踩坑踩出来的）

#### 1️⃣ 相机强制【单流会话】

```
若上一次会话没被 stopstream 干净关闭，新的 startstream 会返回：
    <camrply><result>err_busy</result></camrply>
```
**⇒ 本工具的做法**：发 `startstream` 前先 `stopstream` 清场；仍 busy 就**退避重试 4 次**。
**⇒ 教训**：**不要用 `kill -9` 强杀本工具**，否则相机侧会话残留（用 `Ctrl-C` 正常退出，会自动停流）。

#### 2️⃣ ★ **心跳与取景流互斥**（本项目最重要的实测发现）

| 心跳间隔 | 结果 |
|---|---|
| **不发心跳** | 相机约 **13 秒后停流** ❌ |
| **每 2–3 秒一次**（心跳 + 浏览器轮询同时打） | 相机**持续繁忙** ⇒ 取景流**反复卡顿** ❌ |
| **每 10 秒一次**（且 `/api/state` 走缓存） | **18.7 fps 稳定，零停顿** ✅ |

**根因**：`getstate` 在相机侧耗时 **1–3 秒**，期间**取景流被挤停**。
**对策**：① 服务端缓存状态，浏览器轮询不再打相机；② 心跳固定 10 秒。

```bash
# 想自己验证：
python3 s5monitor.py --keepalive 0    # 约 13 秒后停流
python3 s5monitor.py --keepalive 10   # 默认，稳定
```

#### 3️⃣ 回放模式没有取景流

相机在**回放模式下不推送实时取景**（实时取景仅拍摄模式有效）。
**⇒ 本工具的做法**：切回放前**先 `stopstream`**（释放相机资源），前端显示遮罩说明；
点「返回拍摄模式」时再 `recmode` + 重新 `startstream`。

---

## 🔧 版本记录

| 日期 | 变更 |
|---|---|
| 2026-10-13 | 首版：完整官方逻辑链路 + 官方风格 UI + 实机验证通过 |
| 2026-10-13 | 修复：心跳独立线程、状态服务端缓存、`err_busy` 退避重试、回放模式遮罩、`--keepalive` 参数 |


---

## ✅ 实机验证通过的命令格式（**逐条对照官方 APK 源码还原**）

以下是**唯一正确的参数格式**（我们从 `03_解包_APK` 的 `p168v5/a.java` 与 `liveview/i.java` 逐条核对，
并在真机上验证通过）。**格式错一个字符就会 `err_param`**。

| 功能 | 命令 | 说明 |
|---|---|---|
| **触摸对焦** | `camctrl?type=touch&value=<x>/<y>&value2=on` | ★ **坐标用斜杠 `/` 分隔**，且**必须带 `value2=on`** |
| **释放对焦** | `camctrl?type=touch&value=0/0&value2=off` | 抬起手指时发 |
| 移动 AF 点 | `camctrl?type=touchaf_chg_pos&value=<x>/<y>` | |
| AF 区域大小 | `camctrl?type=touchaf_chg_area&value=up\|down` | |
| 触摸 AE | `camctrl?type=touchae_ctrl&value=on\|off` | |
| 触摸快门 | `camctrl?type=touchcapt_ctrl&value=enable\|disable\|off` | |
| **变焦（长焦/广角）** | `camctrl?type=focus&value=tele-normal`<br>`…tele-fast / wide-normal / wide-fast / focus-stop` | ⚠️ **`focus` 是变焦，不是对焦！** 这是最容易搞错的一条 |
| 变焦（camcmd） | `camcmd?value=tele-normal` / `wide-normal` | capability 的 `camcmdlist` 里列出的 |
| 放大辅助 | `camctrl?type=change_disp_mag&value=<档位>` | 倍率范围见 capability：300–2000 |
| 峰值/辅助显示 | `camctrl?type=asst_disp&value=on\|off` | |
| AE 锁定 | `camctrl?type=af_ae_lock&value=on\|off` | |
| 拖动对焦 | `camctrl?type=touch_trace&value=…` | ⚠️ 本机实测仍 `err_param`，格式待定 |

### 错误码语义（实测）

| 返回 | 含义 | 处理 |
|---|---|---|
| `ok` | 成功 | — |
| **`err_param`** | **参数格式错**（如坐标用逗号而非斜杠、缺 `value2`） | 检查格式 |
| **`err_reject`** | 格式对，但**相机当前状态不接受**（如 MF 模式、触摸设置 OFF） | 改相机设置 |
| **`err_busy`** | 相机忙（**推流时连打 camctrl 很容易触发**） | **退避 0.6/1.2/1.8 秒重试**（官方同款做法，已实现） |
| `err_critical` | 严重状态错误 | 重启相机 |

### ★ 实测踩坑记录

1. **坐标分隔符是 `/` 不是 `,`** —— 用逗号一定 `err_param`
2. **`touch` 必须带 `value2=on`** —— 只给坐标也 `err_param`
3. **`focus` ≠ 对焦**，它是**变焦**（tele/wide + normal/fast）
4. **`camctrl` 通道会"忙"**：`camcmd`/`getstate` 一直 `ok`，但 `camctrl` 可能全线 `err_busy`
   → 需让相机处于**实时取景激活**状态（在相机屏幕上点一下/唤醒），并**加重试**
5. **取景流没有画质参数**：`startstream(value=<端口>)` 就是全部 —— **640×432 是硬上限**，
   要清晰画质只能走 **HDMI**


---

## 🎬 卡顿根治：节奏缓冲器（Frame Pacer）

### 问题：相机的取景流是「突发式」的

实测逐 250ms 采样相机侧收帧数：

```
基准: 0, 8, 6, 0, 0, 2, 16, 8, 0, 0, 0, 16, 8, 3, 0, 0, 13, 8, 6, 0
        ↑空档           ↑250ms 内 16 帧（约 64fps 的突发）
```

**⇒ 相机不是匀速推流，而是「一阵爆发 + 一段空档」** —— 这就是画面卡顿的真正来源
（实测 `getstate` 只占 0.07s，**不是**它的锅）。

### 解法：服务端加一级「节奏器」

```
相机 UDP（突发）──► 帧队列(24 帧 ≈1.2s) ──► 节奏器(20fps 匀速) ──► HTTP MJPEG ──► 浏览器
                                              │
                                              └─ 队列空时【重播上一帧】，保证浏览器 MJPEG 不断流
```

- **匀出**：按固定 20fps 从队列取帧发布
- **垫底**：队列空档时重播最后一帧（浏览器端表现为"画面定住一瞬"，但**不会卡住/重连**）
- **零额外延迟开销**：队列是共享的最新帧，不做累积等待

### 辅助优化

| 优化 | 作用 |
|---|---|
| **`TCP_NODELAY`** | 关掉 Nagle 算法，避免每帧最多 40ms 的发送延迟 |
| **单次 `write()`** | 头部+JPEG 一次写出，减少 syscall 与 TCP 分片 |
| **UDP 接收缓冲 8MB** | 抗突发丢帧 |
| **状态服务端缓存** | 浏览器轮询不再打相机 |

### 修复前后对比（实测）

| 指标 | 修复前 | **修复后** |
|---|---|---|
| 停顿(>150ms) | 每 0.5–0.75 秒一次 | **0 次 / 25 秒** |
| 帧间隔抖动 | 大（突发 0–64fps） | **标准差 2 ms** |
| 帧率 | 16.7–19.8 不稳 | **稳定 20.0** |
| 帧间隔 | 0–750 ms | 中位 50ms，范围 46–60ms |

### 可调参数（`s5monitor.py` 顶部）

```python
PACING_FPS = 20.0            # 目标匀速帧率（降低可省带宽）
PACING_BUF = 24              # 缓冲帧数（加大更抗空档，代价是延迟略增）
REPUBLISH_ON_UNDERRUN = True # 空档重播上一帧（关掉=宁可停顿也不重发）
```


---

## 📊 卡顿诊断报告功能（`/api/diag` + 界面「📊 诊断」按钮）

界面工具条有 **📊 诊断** 按钮，随时可拉出**当前卡顿归因报告**：

| 字段 | 含义 | 健康值 |
|---|---|---|
| `camera_arrival_fps` | **相机真实到达速率** | ~23 fps |
| `pacing_fps_adaptive` | 自适应播放帧率（= 到达速率 × 0.85） | ~19–20 fps |
| `queue_reserve` / `queue_len` | **队列储备**（>0 才说明能吸收空档） | **≥10 帧** |
| `max_camera_gap_ms` | **相机侧最大空档** | 相机固有，几百 ms |
| `pacing_underrun` | 节奏器垫帧次数 | 越少越好 |
| `http_slow_writes` | **下发侧慢写次数** | **0** |
| `camera_gap_histogram` | 相机空档直方图 | — |
| `recent_stalls[]` | **最近每个卡顿的时间/归因/时长** | — |

**判读方法**：
- `http_slow_writes = 0` 且 `max_camera_gap_ms` 很大 ⇒ **卡顿源在相机侧**（本机就是这种情况）
- `http_slow_writes > 0` ⇒ 卡在**电脑↔浏览器**那段链路（Wi-Fi/浏览器解码）

## 🎯 自适应节奏：为什么必须"播得比相机慢"

这是本次**最关键的调参洞察**：

```
如果播放帧率 ≥ 相机到达速率  ⇒  队列被抽干  ⇒  相机空档时只能垫帧  ⇒  画面定住 = 卡顿 ❌
如果播放帧率 = 到达速率×0.85 ⇒  队列积累储备 ⇒  空档被缓冲区吸收    ⇒  画面匀速流畅 ✅
```

**实测调参过程**：

| `PACING_SAFETY` | 播放帧率 | 队列储备 | 结果 |
|---|---|---|---|
| 1.00（固定 20） | 20.0 | **0** | ❌ 每 0.5–0.75s 定住一次 |
| 0.92 | 16.1 | **0** | ⚠️ 仍垫帧 54 次 |
| **0.85** | **19.4** | **12 帧** | ✅ **最大间隔 88ms，>120ms 停顿 0 次** |

### 最终实测验收（30 秒）

```
帧率 19.3 fps
帧间隔: 最小 32  中位 51  95% 76  最大 88 ms
抖动(标准差) = 10 ms
>120ms 停顿: 0 次   >200ms 停顿: 0 次   >500ms 停顿: 0 次
（同期相机侧最大空档 2685ms —— 全部被缓冲区吸收）
```


---

## 🏆 最终方案：**官方标准 = 固定 18fps @ 640p**（用户实测建议，已验证最优）

### 结论

**不要去"追"相机的高突发帧率**。相机虽然平均能到 30fps，但它是**突发式**的
（250ms 内可能爆 16 帧、然后空 500ms+）。追它只会导致：
- 队列被抽干 ⇒ 空档时垫帧 ⇒ **画面定住**
- 或队列积压 ⇒ **延迟越堆越高**（实测堆到 1266ms）

**官方 App 的做法才是对的：固定 18fps，只取最新帧。**

### 两种模式实测对比

| 指标 | 自适应模式（追 30fps） | **官方模式（固定 18fps）** |
|---|---|---|
| 输出帧率 | 31.5 fps | **18.1 fps** |
| **估算延迟** | 264 ms（曾达 **1266 ms**） | **0 ms** ✅ |
| 帧间隔抖动 | 5 ms | **2 ms** ✅ |
| 最大帧间隔 | 59 ms | **64 ms** |
| >80ms 停顿 | — | **0 次** ✅ |
| >120ms 停顿 | 0 次 | **0 次** ✅ |
| 队列深度 | 8 帧 | **2 帧** ✅ |
| 相机侧最大空档 | 535 ms | **153 ms**（18fps 下相机流更规矩） |

### 用法

```bash
# 默认即官方模式
./run.sh 192.168.x.x

# 显式指定
python3 s5monitor.py --host 192.168.x.x --pacing-mode fixed --pacing-fps 18

# 换帧率（例如省带宽用 12fps）
./run.sh 192.168.x.x 8080 fixed 12

# 回到自适应模式（不推荐）
./run.sh 192.168.x.x 8080 adaptive
```

### 参数

| 参数 | 默认 | 说明 |
|---|---|---|
| `--pacing-mode` | **`fixed`** | `fixed`=官方风格固定帧率取最新帧；`adaptive`=队列反馈控制 |
| `--pacing-fps` | **`18`** | fixed 模式输出帧率（官方 640p 标准） |
| `FIXED_KEEP`（源码常量） | `3` | fixed 模式最多保留 3 帧（≈170ms），抗短空档而不积延迟 |

> **为什么"主动抽帧"不是卡顿**：固定 18fps 而相机送 30fps ⇒ 必然要丢掉一些帧。
> 但我们**总是显示最新的那一帧**，所以画面是**均匀的 18fps**，人眼看起来完全平滑
> —— 这正是官方 App 的行为。诊断里的「主动抽帧」计数就是它。


---

## ⚠️ 最重要的一条使用纪律：**不要重启服务**

实测规律（本项目的关键发现）：

```
每调用一次 accctrl&type=req_acc
   ⇒ 相机上产生一条【待批准】消息
   ⇒ 会话从 ok 退回 ok_under_research_no_msg（受限）
   ⇒ camctrl（触摸对焦等）从"可用"变成 err_busy / err_reject
```

**⇒ 所以**：
1. **服务启动后只发一次 `req_acc`** —— 已在代码里强制
2. **会话通了之后，不要重启服务**（重启 = 重新请求 = 需重新在相机上批准）
3. 如果浏览器顶部出现**黄色横幅**（受限授权）⇒ **在相机屏幕上点「允许」**

## 📋 camctrl 的频率敏感特性（实测量化）

| 发送方式 | 结果 |
|---|---|
| **单条、间隔 ≥1.5 秒** | ✅ 多数成功（`touch` / `touch 0/0 off` 已验证） |
| 连续快发（≥5Hz） | ❌ `err_busy` |
| 12 条连测（自检） | 前几条 ok，后续 `err_busy` |

**⇒ 工具里的对策**：拖动对焦限流 **3Hz**；`camctrl` 自带 err_busy 退避重试（0.6/1.2/1.8 秒）。

## 🆕 SSDP "alive" 上报（复刻官方机制）

官方 App 的 `DlnaWrapper.advertisementStart()`（native `dlnaCore`）会向网络广播自己的存在。
本工具已复刻：向 `239.255.255.250:1900` 发 **SSDP alive NOTIFY** + **M-SEARCH**，每 20 秒重发，
并新增 `/desc.xml` 供 SSDP `LOCATION` 引用。

启动日志会显示：
```
[ssdp] 已启动 alive 上报：uuid=4D454930-0100-1000-8001-020A0003BD13  location=http://<本机IP>:8080/desc.xml
```


---

## ★★★ 决定性发现：`req_acc` 有【频率保护】—— 这是 camctrl 的最后一关

### 血泪教训

排查过程中我把 `ensure_access` 改成了「**每 10 秒重发一次 `req_acc`**」以反复弹批准框，结果：

```
相机屏幕显示：
    「智能手机应用程序需要更新」
        ↓
    invalid login
        ↓
    要求重启相机
```

**⇒ 相机把"短时间内大量连接请求"判定为异常/过旧的 App，直接封禁。**
（这正是本项目早期记录过的「An invalid login occurred（需重启相机）」的成因。）

### ✅ 正确握手流程（已验证 camctrl 全通）

```
① 相机【断电重启】（清掉 invalid login 状态）——这一步不可省
② 相机进入"等待 App 连接"状态
③ 启动本工具（内部只发【一次】req_acc）
④ 相机【不会弹任何授权对话框】—— 全程是相机内部自己校验（实测更正）
⑤ 得到 accctrl 首字段 = ok  ⇒ camctrl 可用
```

**实机验证结果（2026-10-14）**：
```
[accctrl] 状态 = ok
[accctrl] ✅ 已获得完整授权（ok）
        ✅ camctrl af_ae_lock on    ok
        ✅ camctrl af_ae_lock off   ok
        ✅ camctrl touch 320/216    ok     ← 触摸对焦！
        ✅ camctrl touch 0/0 off    ok
        ⇒ camctrl 自检 4/7
```

### `accctrl` 首字段完整取值表（实测）

| 取值 | 含义 | 处理 |
|---|---|---|
| **`ok`** | **完整授权** | ✅ camctrl 可用 |
| `ok_under_research_no_msg` | 受限；相机未显示待批消息 | 等 / 在相机上批准 |
| `ok_under_research` | 受限（相机内部校验中） | 稍后重试 |
| **`err_user_refused`** | 相机【内部校验】拒绝（无对话框） | 重新走一次流程 |
| （超高频请求） | 「App 需要更新」+ invalid login | **必须重启相机** |

### ⛔ 三条铁律

1. **`req_acc` 绝不能高频重发**（会触发 invalid login，必须重启相机）
2. **相机提示 invalid login 后，只能靠断电重启恢复**
3. **会话拿到 `ok` 后不要重启服务**（重启 = 重新请求 = 需重新批准）

### 相机不支持的命令（实测）

| 命令 | 结果 |
|---|---|
| `camctrl asst_disp`（峰值对焦显示） | 相机不返回有效结果（本机不支持） |
| `camctrl change_disp_mag` | `err_reject` |


---

## ⏳ camctrl 的「可用窗口」（重要实测结论）

camctrl **不是一直可用**的。实测规律：

```
相机【刚断电重启】+ 首次授权成功（accctrl 首字段 = ok）
        ↓
   ✅ camctrl 可用（touch / af_ae_lock 实测 ok）
        ↓
   使用一段时间后（或命令发得太密）
        ↓
   ❌ 全部回到 err_busy —— 即使间隔 5 秒单发也不行
        ↓
   ⇒ 只能【再重启相机】才能重新获得窗口
```

**使用建议**：
1. **需要触摸对焦时**：先断电重启相机 → 启动本工具 → 立刻使用（窗口期内）
2. 工具会在**启动时自动自检 camctrl**，终端会告诉你这次窗口是否拿到了
3. **不要连续猛点** —— 前端已限流 3Hz；自检已放慢到 3 秒/条

## 🧭 「模拟相机上的点击」—— 做不到

相机的 LCD 由它自己的系统驱动，`cam.cgi` 只暴露**语义命令**（`camctrl` / `camcmd`），
**没有任何 UI 事件注入接口**。无法"帮你在相机菜单里点某个按钮"。

## 🧭 「蓝牙能否提高画质」—— 不能

蓝牙（BLE）在 Lumix 体系里**只负责配对 / 唤醒 / 传 Wi-Fi 凭据**，带宽仅 KB/s 级。

| 链路 | 用途 | 带宽 |
|---|---|---|
| **BLE** | 配对、唤醒、传 Wi-Fi 凭据 | ~KB/s |
| **Wi-Fi** | 取景流（**仅 640×432**） | ~500 KB/s |
| **HDMI** | **全分辨率画面** | **Gb/s 级** |

**⇒ 画质瓶颈是「相机只肯给 640×432 的取景流」**，与走哪条链路无关
（`startstream` 只有端口参数、无画质选项，已从官方 APK 确认）。
**⇒ 要全画质监看只有一条路：HDMI 输出 + 采集卡**（全分辨率、零延迟，代价是没有触摸对焦）。

## 🔧 change_disp_mag 参数修正（官方规范）

```java
// 官方 APK：值 = 倍率 × 100
q.o("change_disp_mag", BigDecimal × 100 ...)
// capability：<disp_mag min="300" max="2000">
```
**⇒ `value` 必须落在 300–2000**（3.00x–20.00x）。此前本工具传的是 `1`，**严重越界** ⇒ 必被拒。
现已修正，界面「放大辅助」改为 **3x / 5x / 10x / 20x 多档循环**。


---

## 🔁 camctrl 真正的机制：**授权状态在"翻动"**

实测日志（精简）：

```
状态 = ok                        → af_ae_lock on   err_reject   ← 发出去的瞬间不是 ok
状态 = ok_under_research_no_msg
状态 = ok                        → af_ae_lock off  err_reject
状态 = ok_under_research_no_msg
状态 = ok                        → touch           err_reject
```

**⇒ 相机的授权状态在 `ok` 与 `ok_under_research_no_msg` 之间不断跳动，
`camctrl` 只有在「恰好是 `ok`」的那一瞬间才会成功。**

### 对策（已实装）

`camctrl` / `camcmd` 现在对 **`err_busy` 和 `err_reject` 都做退避重试**（最多 8 次，退避 0.5→3 秒），
**一直撞到 `ok` 窗口为止** ⇒ 触摸对焦/AE锁定的成功率大幅提升。

### MF 模式下的新发现

| 命令 | AF 模式 | **MF 模式** |
|---|---|---|
| `touch`（触摸对焦） | ✅ 窗口期可用 | ❌ `err_reject`（**符合逻辑：MF 下触摸 AF 无效**） |
| `af_ae_lock` | ✅ 窗口期可用 | ❌ `err_reject` |
| `change_disp_mag`（放大辅助） | ❌ `err_reject` | ❌ `err_reject`（**MF 也拒绝**） |

**⇒ `change_disp_mag` 的门不在对焦模式**（已排除 MF）；
下一个待验证的假设：相机菜单里的**「放大辅助 / MF 辅助」开关是 OFF**。

### 新增实用 API

```bash
curl "http://<相机IP>/cam.cgi?mode=getsetting&type=focusmode"
# → <settingvalue focusmode="mf"></settingvalue>
```
**⇒ 可以直接读出当前对焦模式**（已接入工具顶栏显示：「MF 手动」/「AFS 自动」…）。
