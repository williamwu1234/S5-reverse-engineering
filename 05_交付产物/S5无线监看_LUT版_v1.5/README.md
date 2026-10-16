# DC-S5 无线监看 · LUT 版 v1.5

给 **Panasonic DC-S5**（初代，固件 VD4.30）用的电脑/手机无线监视器。
官方 LUMIX Flow 不支持 S5，本工具把它的核心能力补了回来，并额外实现了
**实时 LUT 套用**与**无线取片**。

> 运行环境：macOS（Python 3）+ 任意浏览器（电脑/手机/平板均可，无需装 App）

---

## 三步开始

### 1. 安装依赖（只需一次）

**双击 `首次运行_安装依赖.command`**
它会在本目录创建独立虚拟环境 `.venv` 并安装 numpy/Pillow（LUT 功能需要；
不装也能用监看/对焦/拍照，只是 LUT 面板禁用）。失败会自动换国内镜像。

### 2. 让相机上线

**推荐：热点模式**（直连，最流畅，实测零重播、延迟 30–53 ms）

1. 相机菜单 → Wi-Fi → 遥控拍摄与监看（或"发送图像"），相机自建热点
2. Mac 的 Wi-Fi 连上相机热点（SSID 形如 `S5-XXXXXX`）
3. 相机 IP 就是 **192.168.54.1**（网关）

**备选：家网模式**（同一路由器）
相机与电脑连同一 Wi-Fi，用相机在家网里的 IP（延迟与卡顿会明显增加，
实测重复率 40% vs 热点 0%）。

### 3. 启动

**双击 `启动.command`**（或 `./启动.command <相机IP>`）

等 10–20 秒让授权完成（页面顶栏显示 `access=ok`），然后浏览器打开
**http://127.0.0.1:8080**。同一网络下的手机也能用 `http://<本机IP>:8080`。

---

## 功能

| 功能 | 说明 |
|---|---|
| 实时取景 | 官方节奏：固定 18 fps / 640p，取最新帧 |
| 触摸对焦 / AE 锁定 | camctrl 类（见下方"已知限制"） |
| 拍照 / 录像 / 变焦 | camcmd 类，实测稳定 |
| **实时 LUT** | `.cube` / `.vlt`，256³ 精确查表，单帧约 7 ms |
| **LUT 串联** | V-Log →(还原 709)→ 胶片模拟；复合成单表零开销 |
| **LUT 强度** | 0–100% 滑杆，实时调节 |
| **LUT 导入** | 界面选文件 / 直接拖拽 `.cube` `.vlt` 到面板 |
| **A/B 对比** | 原始画面 / 套 LUT 一键切换 |
| **无线取片** | 列举相机内容 → 下载原图 → 自动套 LUT（回放模式下） |
| 一条命令取片 | `python3 s5_get_photo.py`（详见使用说明） |

### LUT 面板怎么用（核心）

1. 点工具栏 **「🎨 LUT」**
2. **LUT 文件** 选一个（内置 9 个），**已构建过的组合 1 ms 秒切**
3. **前置还原**：拍 **V-Log** 时选 `V-Log → Rec.709（33³，推荐）`；
   拍普通风格（Standard 等）时**不选**
4. 顶部 **原始画面 / 套 LUT** 做 A/B
5. **强度** 滑杆调节浓淡（胶片 LUT 本身很轻，滑杆能把它拉出来）

### 内置 LUT（`lut/` 目录）

| 文件 | 用途 |
|---|---|
| `vlog_to_709_17.cube / .vlt` | V-Log → Rec.709（17³，与机内同规格） |
| `vlog_to_709_33.cube / .vlt` | V-Log → Rec.709（33³，暗部更准） |
| `vlog_to_709_17_altAxis.vlt` | 备选轴序 |
| `VOL12 TXD FUJI NC P.cube` | 富士 NC 胶片模拟（示例） |
| `VOL19 TXD GLOD 200T V2.cube` | 柯达 Gold 200T 胶片模拟（示例） |
| `GR4-CineG/CineY Plady.cube` | GR4 电影风格（示例） |

> 示例 LUT 来自用户提供的 Lightroom 导出文件，仅供演示；请替换为你自己的。

---

## ⛔ 操作铁律（踩过坑，务必读）

1. **`req_acc` 绝不能高频重发** —— 相机有频率保护：
   短时间多次请求 ⇒ 屏幕显示「智能手机应用程序需要更新」⇒ `invalid login`
   ⇒ **只能断电重启相机**。本程序启动时只发一次，**切勿反复重启程序**。
2. **会话拿到 `ok` 后不要重启服务**。
3. **不要用裸 `curl` 直接访问相机**（不带 UUID 的请求会留"匿名 pending"
   污染相机的唯一待批复槽，导致后续 `err_others_requesting`）。
4. **相机按客户端身份放行**：监视器持有 `ok` 时，其它来源的请求返回
   `err_unsuitable_app` 是**正常现象**，不是故障。

**恢复流程（出现 invalid login 时）**：断电重启相机 → 确认
`curl -A "LUMIX Sync" http://<相机IP>/cam.cgi?mode=getstate` 返回 `ok` →
启动本程序一次 → 等待 10–20 秒。

---

## 已知限制（诚实清单）

| 项 | 说明 |
|---|---|
| `camctrl`（触摸对焦/AE锁） | 只在授权状态恰为 `ok` 的瞬间受理；热点遥控模式下实测常被 `err_busy` 挡。`camcmd`（拍照/录像/变焦/模式）正常 |
| **连续对焦** | 用**机身 AF 拨杆切到 AF-C**，相机自己持续对焦（远程改不了，拨杆优先） |
| 相册与取景互斥 | 列举内容会把相机切到回放模式（此时无取景），用完自动切回 |
| DLNA 内容树 | 只在**回放模式**下有内容（实测定因） |
| 画面"卡顿感" | 相机突发式推流所致；**热点直连**下零重播，经路由器会明显变差 |
| 机内烧录 LUT | 不可能 —— 初代 S5 无 Real Time LUT（官方三机对比表否证），本工具在机身外完成 |

---

## 命令行

```bash
python3 s5monitor.py --host 192.168.54.1            # 监看（默认）
python3 s5_transfer.py list --cam 192.168.54.1      # 列举照片/视频
python3 s5_transfer.py get  --cam 192.168.54.1 --all-videos   # 拉全部视频（带进度）
python3 s5_transfer.py get  --cam 192.168.54.1 --newest \
       --lut "VOL19 TXD GLOD 200T V2.cube" --base vlog_to_709_33.cube  # 最新照片+套LUT
python3 s5_transfer.py watch --cam 192.168.54.1 \
       --lut "VOL12 TXD FUJI NC P.cube" --base vlog_to_709_33.cube     # 新照片一出现就下载+套LUT
python3 s5_get_photo.py                              # 一键取片（老入口，保留）
python3 s5_content.py probe --cam 192.168.54.1       # DLNA 三层判定
python3 s5_selfcheck.py                              # 自检（自动找相机）
```

---

## 目录

```
S5无线监看_LUT版_v1.5/
├── 启动.command               # 双击启动
├── 首次运行_安装依赖.command   # 双击一次，装 numpy/Pillow
├── s5monitor.py               # 主程序（监看/对焦/实时 LUT/相册）
├── s5_lut.py                  # LUT 引擎（.cube/.vlt、256³ 查表、串联、强度）
├── s5_content.py              # 机身存储访问（DLNA Browse/下载/诊断）
├── s5_get_photo.py            # 一键取片 + 套 LUT
├── s5_transfer.py             # 传输管理器（列举/批量/视频/监视）
├── s5_selfcheck.py            # 自检脚本
├── www/index.html             # 网页界面
├── lut/                       # 内置 LUT（9 个）
├── 使用说明.md / 附_技术参考.md
└── README.md
```

---

*技术要点归档：官方 DLNA 请求格式（含 `pana:X_FromCP=LumixLink2.0`）、
accctrl 单槽机制、SSDP 按相机路由探测本机 IP、256³ 精确查表（与逐帧三线性逐位等价）等，
详见仓库 `12_S5无线监看_v1.0_20261014` 的提交历史与 `14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md`。*
