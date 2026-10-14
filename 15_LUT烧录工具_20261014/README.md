# LUT 烧录工具 · DC-S5

> **一句话**：初代 S5 **不能在机身里把 LUT 烧进文件**，但本工具用三条路把它做到：
> ① 生成的 `.vlt` 放进 SD 卡根目录 → 机身 `[V-Log View Assist]` 监看套 LUT；
> ② 电脑端把 LUT **烧进照片/视频**（10-bit HEVC，6K 约 0.7× 实时）；
> ③ **监视目录自动烧录**（新素材一落地就出片）＝你要的"实时烧录"。
>
> 全部 **macOS 原生**（CoreImage / AVFoundation），不依赖 ffmpeg（本机 ffmpeg 是坏 bottle，见文末）。

---

## 0. 已经在卡上的东西（现在就能用）

SD 卡根目录 `/Volumes/LUMIX/` 已写好（**根目录，不是文件夹**——这是官方硬要求）：

| 文件 | 说明 |
|---|---|
| `VL709.vlt` | V-Log → Rec.709，17³，**VariCam 轴序**（B 变化最快） |
| `VL709A.vlt` | 同上，**另一种轴序**（R 变化最快）——若第一个套上去色偏，用这个 |
| `VL709.cube` | 同上，33³ `.cube` 版（部分机型/后期软件用） |

**机身操作**：`[照片风格] 选 [V-Log]` → `[V-Log View Assist]` → `[LUT Select]` 选 `VL709` → 需要时开 `[LUT View Assist (Monitor)]` / `[LUT View Assist (HDMI)]`。
屏幕出现 `[LUT]` 标记即为生效。**这是监看/HDMI 辅助，不会写进机内文件。**

> ⚠️ 注意：本机 `photostyle=standard`（实测），V-Log 需在拍摄时主动选中。**没拍 V-Log 的素材不要套这个 LUT**（见 §4）。

---

## 1. 快速开始

```bash
cd 15_LUT烧录工具_20261014

# 单张照片
./bake image lut/vlog_to_709_17.vlt 输入.jpg 输出.jpg

# 单个视频（默认 HEVC 10-bit）
./bake video lut/vlog_to_709_17.vlt 输入.MP4 输出.mp4

# 批量
./bake batch lut/vlog_to_709_17.cube ./输出目录 文件1 文件2 ...

# 【实时】监视目录，新素材自动烧
python3 watch_bake.py --lut lut/vlog_to_709_17.vlt \
    --src /Volumes/LUMIX/DCIM --out ~/Pictures/LUT_baked
```

---

## 2. 三个工具

### 2.1 `make_lut.py` — 生成 LUT

```bash
python3 make_lut.py --from vlog  --size 17 --formats vlt  --out /Volumes/LUMIX/   # 给机身
python3 make_lut.py --from vlog  --size 33 --formats cube --out lut/               # 给后期
python3 make_lut.py --selftest                                                      # 只跑自检
```

**为什么自己算**：官方 `VLog_to_V709` 的 `.vlt` 需要从松下站点下载；本工具用**公开规范**推导：

- Panasonic V-Log OETF：`V = 5.6L + 0.125`（L<0.01）；`V = 0.241514·log₁₀(L + 0.00873) + 0.598206`
- 自检锚点（全部通过）：**0% 黑 = 0.125**、**18% 灰 = 0.4233**、断点 **V=0.181 ↔ L=0.01 两侧连续**
- V-Gamut 原色（`0.730,0.280 / 0.165,0.840 / 0.100,−0.030`，D65）→ BT.709 原色的 3×3 矩阵（由坐标推导，白点保持）
- ITU-R BT.709 OETF

**→ 结果是规范自洽的等效转换，不是官方 LUT 的逐字节复刻。** 要官方原版去
<https://av.jpn.support.panasonic.com/support/global/cs/dsc/download/lut/index.html>

**`.vlt` 格式**（由 35 个官方样本逆向，本工具输出已逐项合规）：
纯 ASCII，两行 `#` 头 + `LUT_3D_SIZE N` + 空行 + N³ 行 `R G B`（**整数 0–4095，12-bit**）。官方样本全为 17³。

### 2.2 `bake.swift` → `bake` — 烧录器

```bash
./bake probe <文件>                       # 看规格（分辨率/帧率/编码/位深）
./bake image <lut> <in> <out>             # 照片（jpg/png/tif/heic）
./bake video <lut> <in> <out> [选项]       # 视频
./bake batch <lut> <outdir> <in...>       # 批量
```

| 选项 | 说明 |
|---|---|
| `--max-seconds N` | 只烧前 N 秒（试跑用） |
| `--bitrate 120M` | 走显式码率路径（HEVC Main10） |
| `--codec hevc\|h264` | 默认 hevc |
| `--cs srgb\|bt709\|bt2020\|linear\|displayp3` | LUT 解释用的色彩空间（默认 sRGB） |
| `--vlt-axis variCam\|cube` | `.vlt` 轴序（默认 variCam；套上去色偏就换 cube） |

**实测性能与规格**（源：`P1000026.MP4` 5184×3456 10-bit HEVC 29.97fps，107 Mbps）：

| 路径 | 位深 | 码率 | 6K 速度 |
|---|---|---|---|
| 默认 | **10-bit** | ~27 Mbps | 3 s 素材约 4 s（**≈0.7× 实时**） |
| `--bitrate 120M` | **10-bit** | ~29 Mbps（硬件编码器上限，见 §5） | 约 0.5× 实时 |

### 2.3 `watch_bake.py` — 实时烧录（你要的那条）

```bash
# A) 卡插在电脑上：卡上一出现新素材就烧
python3 watch_bake.py --lut lut/vlog_to_709_17.vlt --src /Volumes/LUMIX/DCIM --out ~/Pictures/LUT_baked

# B) 用 LUMIX Sync / 访达 把照片拖进中转目录，拖进来即烧
python3 watch_bake.py --lut lut/vlog_to_709_17.vlt --src ~/Downloads/LUMIX --out ~/Pictures/LUT_baked

# C) 只跑一遍（cron / 快捷指令）
python3 watch_bake.py ... --once
```

- **等文件写完**：连续两次采样 `(size, mtime)` 不变、再静默 `--settle` 秒才动手（相机与拷贝都是分块写入）
- **幂等**：状态文件记录 `(size, mtime)`，同一文件不重复烧
- **风格自检**：先判断素材是不是 Log，若不是会**警告**（`--skip-normal` 可直接跳过）
- **绝不写源目录**，产物只进 `--out`

**实测**：投放素材 → 检测 → 风格自检 → 烧录完成，**约 5 秒**（`--interval 1 --settle 1` 时）。

### 2.4 `check_style.py` — 判断素材是不是 Log（防套错 LUT）

```bash
python3 check_style.py testdata/frame.jpg
```

**判据**：**V-Log 的黑位是 0.125（≈32/255），永远不会有真黑**；普通风格黑位贴近 0。
所以「是否存在真黑像素」是最稳的单一判据，在极端低调画面上也不失效。

**双向验证**（本工具已实测）：

| 输入 | 判定 | 黑位 P1 |
|---|---|---|
| 相机直出帧（Standard） | 🟩 **NORMAL**（91.3% 真黑） | 0 |
| 同帧反算成 V-Log | 🟦 **LOG**（8/8） | **31** ← V-Log 黑位理论值 0.125×255 = **31.875** |

→ 这条同时**独立印证了 V-Log 公式与整条 LUT 链的正确性**。

---

## 3. 闭环验证（为什么可以信这套工具）

用相机自己的 6K 素材做了一次**往返测试**：

```
原始帧(Standard) ──反算成 V-Log──► 合成 V-Log 帧 ──我们的 LUT 烧录──► 恢复出原始画面
                        │                                          │
                  风格自检判 LOG(8/8)                      画面与原始一致（见 out/）
```

另外：`.cube` 与 `.vlt` 两条输入路径的烧录结果**平均像素差 = 0.00**，证明 `.vlt` 解析与轴序处理正确。

---

## 4. ★ 最重要的使用前提：LUT 必须匹配拍摄时的照片风格

**把 V-Log 的 LUT 套到非 Log 素材上，画面只会变暗变糟。** 本机实测：

| | 均值 | P50 | P99 |
|---|---|---|---|
| 原始帧（Standard，夜景） | 9.0 | 1.0 | 204 |
| 套 VLog→709 后 | **6.5（更暗）** | 0.0 | 224 |

所以你卡上那段 `P1000026.MP4`（**6K 片门全开 5184×3456 10-bit HEVC**，与相机当前 `6k4k_photo=6k_burst` 一致）**判定为 NORMAL 风格** ⇒ **不需要套 VLog→709**。

**建议工作流**：
1. 想用 LUT → 拍摄时把 `[照片风格]` 设成 **V-Log**（本机 `ph_sty_vlog enable=yes`，可用）；
2. 素材到手先 `python3 check_style.py 素材`；
3. 判为 LOG 才套 `VL709`；判为 NORMAL 就别套（或换成创意 LUT）。

---

## 5. 已知限制（诚实清单）

| # | 限制 | 说明 / 出路 |
|---|---|---|
| 1 | **内置 HEVC 编码器在 6K 下码率上限约 29 Mbps** | 源是 107 Mbps（all-intra 风格），重编必然降码率。**要真正保质请用 DaVinci Resolve** 套我们生成的 `.cube`（或 `--bitrate` 已是能找到的上限） |
| 2 | **ProRes / H.264 不支持 >4096 宽** | 6K 3:2 会直接报错（已做预检，不会崩）。需要 ProRes 中间格式请用 Resolve |
| 3 | 中间缓冲 | HEVC 路径用**半浮点 RGBA**（保住 10-bit）；ProRes 路径只能用 8-bit BGRA |
| 4 | **不能改机身行为** | 初代 S5 无 Real Time LUT（官方对比表否证），本工具只做机身外处理 + 机身监看 LUT |
| 5 | 本机 ffmpeg 不可用 | `/opt/homebrew/Cellar/ffmpeg/9.0.1_1/bin/ffmpeg` 的 install_name 里 `@@HOMEBREW_CELLAR@@` 未替换（坏 bottle），且 `/opt/homebrew` 非当前用户所有 ⇒ **本工具全程不依赖它** |
| 6 | 色彩空间近似 | LUT 按"编码值→编码值"解释，默认 sRGB 容器；BT.709 OETF 与 sRGB 接近但不等同。严格比对请用 Resolve |
| 7 | 卡上写 LUT 后 | macOS 会生成 `._*` 资源分叉——**已清理**。若你再次插拔卡，建议插回相机前确认根目录没有 `._*` 与 `.fseventsd` |

---

## 6. 目录内容

```
15_LUT烧录工具_20261014/
├── make_lut.py            # 生成 .cube / .vlt（含自检）
├── bake.swift             # 烧录器源码（CoreImage/AVFoundation）
├── bake                   # 编译产物
├── watch_bake.py          # 【实时】目录监视 + 自动烧录
├── check_style.py         # Log / 普通风格判定
├── lut/                   # 生成的 LUT
│   ├── vlog_to_709_17.vlt / _altAxis.vlt / _33.vlt
│   └── vlog_to_709_17.cube / _33.cube
├── testdata/              # 测试素材（从 6K 视频抽帧 + 合成 V-Log 帧）
├── out/                   # 烧录产物（含闭环验证图）
└── build/                 # 编译中间件与辅助工具（grab 抽帧、probe 探测）
```

**重新编译**（改了 `bake.swift` 后）：
```bash
swiftc -O -module-cache-path "$PWD/.modcache" bake.swift -o bake
```

---

## 7. 复现命令（全部）

```bash
cd 15_LUT烧录工具_20261014
PY=/Users/wuwilliam/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3

# LUT 自检 + 生成
$PY make_lut.py --selftest
$PY make_lut.py --from vlog --size 17 --formats vlt --out lut
$PY make_lut.py --from vlog --size 33 --formats cube --out lut

# 风格判定（双向验证）
$PY check_style.py testdata/frame.jpg              # → NORMAL
$PY check_style.py testdata/frame_synth_vlog.jpg   # → LOG

# 单文件烧录
./bake probe /Volumes/LUMIX/DCIM/100_PANA/P1000026.MP4
./bake image lut/vlog_to_709_17.vlt testdata/frame_synth_vlog.jpg out/rt.jpg
./bake video lut/vlog_to_709_17.vlt /Volumes/LUMIX/DCIM/100_PANA/P1000026.MP4 out/x.mp4 --max-seconds 2

# 实时监视
$PY watch_bake.py --lut lut/vlog_to_709_17.vlt --src /tmp/watch_src --out /tmp/watch_out --once
```


---

# 8. 「实时烧录」的四条路（含机内可行性裁决）

## 8.1 ★ 机内实时烧录：**不可能**（已定论，别再找了）

| 层次 | 结论 |
|---|---|
| **功能层** | Real Time LUT 是 **S5II / S5IIX / GH7 / S9 / G9M2 / S1M2 / S1R2** 的能力。[官方 S5/S5Ⅱ/S5ⅡX 三机对比表](https://panasonic.jp/dc/feature/S5M2-S5M2X/difference.html)的「照片风格」行：S5 清单里**没有「リアルタイムLUT」**，S5Ⅱ 有 |
| **管线层** | Real Time LUT 是**一个照片风格条目**，背后需要**实时 3D LUT 插值**并与 JPEG/HEIF 与视频编码器串联。S5 的影像处理器里没有这一级；S5 的 `MY PHOTO STYLE 1-10` 只有**参数化**调整（对比度/高光/阴影/饱和度/色相/降噪/锐度），**没有 LUT 槽位** |
| **可达层** | 跨代不可移植（MC801 32-bit A7 ↔ SC2006A 4×A53 64-bit）；固件加密 + 签名；无 RCE。⇒ 不是"开关还没找到"，而是**没有那级硬件管线** |

**唯一"实时且烧录"的合法路径**：若 `[V-Log View Assist]` 里含 **[LUT View Assist (HDMI)]**，则 **HDMI 输出口吐出的就是已套 LUT 的画面**，外接录机（Atomos/Ninja 等）录下来即"烧录版"。
👉 **请在机身菜单里看一眼 `[V-Log View Assist]` 下面有没有 `[LUT View Assist (Monitor)]` / `[LUT View Assist (HDMI)]` 两个开关**——这是唯一还需确认的点。

> ✅ **已实测确认（你刚验证的）**：初代 S5 **能读入自定义 `.vlt`**（`[LUT Select]` 列出了 `VL709`）。
> 这把此前只能给到"高度可能（等级 D）"的结论升级为**实机确证**——本项目第一条。

## 8.2 四条路对比

| 路径 | 实时性 | 能否烧进文件 | 前置条件 |
|---|---|---|---|
| **A. HDMI 外录 + `LUT View Assist (HDMI)`** | ★★★ **真·实时** | ✅ 烧进外录文件 | 外接录机；且 S5 需有该 HDMI 开关 |
| **B. WiFi 取片 + 本地烧（`wifi_lut.py`）** | ★★ 照片数秒～十几秒 | ✅ | 需取片通道可用（**待 probe**） |
| **C. USB 大容量存储 + 卡挂载 + `watch_bake.py`** | ★ 批处理（该模式下通常不能拍摄） | ✅ | 相机菜单 → USB 连接模式 → **大容量存储** |
| **D. 卡插读卡器 + `watch_bake.py`** | ★ 批处理 | ✅ | 卡要取出 |

**蓝牙（BLE）不可行**：项目实测 BLE 只暴露凭据面（SSID/密码），**没有文件传输面**；有效吞吐 ~10–100 KB/s 量级，一张 10 MB JPEG 要数分钟。视频更无可能。

## 8.3 WiFi 路径：`wifi_lut.py`

```bash
# ① 先探路：把 DLNA 的所有 header/body 变体 + get_content_info + 其它读取端点
#    + SSDP 发现 + 本机挂载卷 全部试一遍，找出真正可用的那条
python3 wifi_lut.py probe --cam 192.168.1.131

# ② 列出相机上的内容
python3 wifi_lut.py list  --cam 192.168.1.131

# ③ 实时：轮询新照片 → 下载 → 立刻套 LUT → 落盘
python3 wifi_lut.py watch --cam 192.168.1.131 --lut lut/vlog_to_709_17.vlt --out ~/Pictures/LUT_baked
```

**已知障碍**：60606 的 DLNA **控制面在 station（家网）模式实测 403**（我跑过 10 个 header/body 变体，静态描述 200、所有控制 POST 403），而项目自有 iOS App 的 `connect()` **只调 `getstate`、没有任何 accctrl 握手**，且**库内从无 Browse 成功证据**（审计发现 E-3）。
⇒ `probe` 就是为了**用一次相机在线的时间把这条路一次性判定清楚**：要么找到可用的变体，要么确认 station 模式下无通道（那就改走 SoftAP 或 USB/读卡器）。

**注意**：`watch` 模式下不做任何写相机操作，纯 GET + SOAP 查询。
