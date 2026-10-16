# E · 总包审计 / 无线监看 / LUT 工具链 —— 素材提取

> **本块覆盖**（25 个 .md，共 6,822 行，全部逐文件通读）：
> `14_总包审计与新方向_20261014/`（11 个）、`12_S5无线监看_v1.0_20261014/`（4 个）、
> `15_LUT烧录工具_20261014/`（1 个）、`16_S5无线监看发行包_20261015/`（3 个）、`00_项目总结/`（6 个）。
>
> **提取范围**：① 已确证结论（带证据等级）② **已验证可用操作路径（命令原样抄全）** ③ 已证伪/已排除路线
> ④ 已知陷阱与危险操作 ⑤ 未解决/开放问题 ⑥ 文档之间的矛盾。
>
> **纪律**：纯离线读文件所得，**不臆造**。凡属代码级核查（非文档陈述）的，均标注「★ 本次核查」。
> 行号引用格式：`相对路径:行号`。证据等级沿用项目惯例：**实测 ✓** / **强推断 ◐** / **弱推断 ⚠️** / **未验证 ✗**。

---

## 速查：本块 5 个入口

| 想做什么 | 直接跳到 |
|---|---|
| **跑起无线监看**（拿 `ok` + 实时取景 + 拍照录像） | [§2.1 监看器完整可用功能与确切启动命令](#21-★-监视器完整可用功能与确切启动命令) |
| **照着错误码排查** | [§2.2 错误码语义表](#22-★-错误码语义总表与每种的处理方法) |
| **套 LUT**（监看实时套 / 机身读入 / 后期烧录） | [§2.3 LUT 工具链](#23-★-lut-工具链格式烧录路径17³-vs-33³) |
| **别踩雷**（会砖机/会封会话的操作） | [§4 已知陷阱与危险操作](#4-已知陷阱与危险操作血泪教训逐条) |
| **总包审计说了什么 / 新方向** | [§2.5 总包审计结论](#25-★-总包审计的结论与修复清单) 、[§2.6 新方向清单](#26-★-新方向清单26-个四梯队) |

---

## 1. 已确证的结论（按证据等级）

### 1.1 实测 ✓ —— 可放心引用

| # | 结论 | 关键数字/证据 | 出处 |
|---|---|---|---|
| A1 | **热点的 `accctrl` 授权可在 10 秒内拿到 `ok`** | 干净状态实测 10 秒；取景流 30 fps | `12_S5无线监看_v1.0_20261014/README.md:252` |
| A2 | **"如何拿到完整授权"已有确定配方** | `DEFAULT_DEVICE_ID`（`4D454930-0100-1000-8001-020A0003BD13`）+ `--device-name "LUMIX Sync"` + 机身屏幕按【允许】；实测 `access_raw = "ok,S5-XXXXXX,remote,encrypted"`、`camctrl_ok=true`、已推帧 1,345,385 | `14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:184-189` |
| A3 | **取景流规格 = MJPEG 640×432，单帧约 25 KB，UDP 端口 49152（官方允许 49152–65535）** | 相机平均 ~30 fps 但**突发式** | `附_技术参考.md:18-24`（v1.0 与 v1.5 两份逐字节相同） |
| A4 | **固定 18 fps + 只取最新帧 = 官方做法** | 实测延迟 0 ms、抖动 2 ms、零停顿零跳帧；追相机 30 fps 会导致延迟堆到 **1266 ms** | `附_技术参考.md:35-42` |
| A5 | **心跳必须 10 秒** | 不发心跳相机 **13 秒后停流**；每 2–3 秒一次会让相机持续繁忙⇒卡顿；**10 秒 + 状态走服务端缓存 = 零停顿** | `附_技术参考.md:54-61` |
| A6 | **授权状态在"翻动"，`camctrl` 只在恰为 `ok` 的瞬间成功** | 日志 `ok → ok_under_research_no_msg → ok → …`；对 `err_busy`/`err_reject` 退避重试最多 8 次后触摸对焦 **8/8 = 100%** | `附_技术参考.md:109-116` |
| A7 | **相机强制单流会话** | 上次没 `stopstream` 干净关闭 ⇒ 新 `startstream` 返回 `err_busy`；工具做法 = 先 `stopstream` 清场 + 退避重试 4 次 | `附_技术参考.md:26-27`、`s5monitor.py:305-320` ★ |
| A8 | **`camctrl type=focus` 是【变焦】不是对焦** | 值 `tele-normal/tele-fast/wide-normal/wide-fast/focus-stop`；官方 UI 归属 `LiveViewLumixZoomView` | `附_技术参考.md:83-85` |
| A9 | **触摸对焦必须斜杠分隔且必须带 `value2=on`** | `camctrl?type=touch&value=<x>/<y>&value2=on` | `附_技术参考.md:69` |
| A10 | **全家网/热点路径对比：热点直连完胜** | 同一相机同一参数（`fixed/18fps/队列3`）：热点 **18.1 fps、空窗口 0/79、新画面 40/40=100%、端到端 53 ms、RTT stddev 6.6 ms**；经路由器 **新画面 18/30（重复率 40%）、延迟 400–700 ms、RTT stddev 258 ms（差 39 倍）** | `12_S5无线监看_v1.0_20261014/README.md:468-479` |
| A11 | **`run.sh` 默认 `192.168.54.1` 不是随便写的** | 那是相机 SoftAP 网关，官方设计的低延迟路径 | `12_S5无线监看_v1.0_20261014/README.md:479` |
| A12 | **卡顿根因 = 相机突发式推流，非软件** | 帧间隔中位 56 ms、>200 ms 停顿 0 次，但 30 帧里只有 15 帧新画面；同现 `pacing_underrun=1369`（队列空）与 `frames_dropped_queue_full=1540`（队列满） | `12_S5无线监看_v1.0_20261014/README.md:448-457` |
| A13 | **无线访问机身存储已解决** | **`accctrl=ok` + 相机切【回放模式】⇒ DLNA 立刻列出全部内容，可从 50001 端口下载原始全分辨率照片** | `12_S5无线监看_v1.0_20261014/README.md:276-280` |
| A14 | **DM 门的真身 = accctrl 的 `ok`** | A/B 对照：`ok` ⇒ **HTTP 500 + SOAP Fault `<errorCode>701</errorCode>`**；`ok_under_research_no_msg` ⇒ **HTTP 403** | `10_仓库补丁/定因与交接_20261014.md:281-286` |
| A15 | **能收到 SOAP Fault 本身就是"已放行"的证据** | 403 时相机不处理请求、无响应体 | `10_仓库补丁/定因与交接_20261014.md:288-289` |
| A16 | **`req_acc_can` 清陈旧 pending 实测有效，不必重启相机** | 清理前 `ok_under_research_no_msg` / `getstate=err_reject` → 用**同一 UUID** 发一次 `req_acc_can` 后 **`ok` / `ok`** | `10_仓库补丁/定因与交接_20261014.md:261-266` |
| A17 | **`.cube` 与 `.vlt` 两条路径逐像素最大差 = 1**（仅量化取整）；LUT 烧录两路平均像素差 **0.00** | 实时套用（640×432）单帧 **20–26 ms** | `12_S5无线监看_v1.0_20261014/README.md:130`、`15_LUT烧录工具_20261014/README.md:147` |
| A18 | **17³ 与 33³ 网格在暗部差异可达 126** | V-Log 曲线暗部很陡；机身只吃 17³，实时监看可用 33³ | `12_S5无线监看_v1.0_20261014/README.md:140-141` |
| A19 | **初代 S5 能读入自定义 `.vlt`（实机确证）** | `[LUT Select]` 成功列出我们生成的 `VL709`；这是本项目第一条实机证据，把此前"高度可能（等级 D）"升级为实机确证 | `09_LUT可行性报告_20261014.md:408-419` |
| A20 | **官方对比表直接否证初代 S5 有 Real Time LUT** | S5「照片风格」清单**无「リアルタイムLUT」**，S5Ⅱ/S5ⅡX 有。具备机型：S5M2/S5M2X/S9/GH7/G9M2/S1M2/S1R2；不具备：**S5(初代)/S1/S1R/S1H/GH5/GH6** | `09_LUT可行性报告_20261014.md:321-333` |
| A21 | **LUT 放卡根目录，不是文件夹**（三处官方一手文档互印） | `/AD_LUT/` 说法在官方与实测证据中均不成立（且本项目文档从未使用过该词，无需清理） | `09_LUT可行性报告_20261014.md:264-278` |
| A22 | **`.VLT` 格式规范（35 个官方样本逆向，等级 A）** | `LUT_3D_SIZE` **全部为 17 零例外**；数据行 **4913 = 17³** 零例外；严格 `^\d+ \d+ \d+$`（无小数/无第四列/无逗号）；**整数 0–4095（12-bit）**；LF 与 CRLF 官方都有；≈67–69 KB；**无** `DOMAIN_MIN/MAX`、无 `LUT_3D_INPUT_RANGE`、无 `TITLE` | `09_LUT可行性报告_20261014.md:282-307` |
| A23 | **HDMI 输出口会带上 LUT** | `[V-Log View Assist]` 官方定义原文 "show images with LUT file applied on the monitor/viewfinder **and output them via HDMI**" ⇒ 外接录机录下的就是"烧录了 LUT"的素材 | `09_LUT可行性报告_20261014.md:339-348` |
| A24 | **V-Log 在本机可选**（View Assist 的前置条件已满足） | `menu_item_id_ph_sty_vlog` = **`enable="yes"`**；`ph_sty_vlog_l` = no；当前 `photostyle=standard` | `08_实机与离线验证记录_20261014.md:118`、`09_LUT可行性报告_20261014.md:36-43` |
| A25 | **`func_type` 是机身自报的机型能力指纹**（建议作为全项目"功能可用性第一判据"） | S5 = **`sp_embeded_ph_sty11`**（S1H = `ph_sty9`，App 序列排到 `ph_sty13`）；App 的 LUT UI 门控 = `IsPhotoStyleLutDensitySupport \|\| func_type == "sp_embeded_ph_sty13"` | `09_LUT可行性报告_20261014.md:74-81, 241-254` |
| A26 | **三种独立取证一致：不存在 LUT 文件上传路径** | 相机 HTTP（`startsenddata` 的 type 白名单只有 `camsetting`/`fw`）、官方 APK（`.cube/.vlt/.3dl/AD_LUT/lutfile/LUT_LIBRARY` 全 0 命中）、项目自有 App | `09_LUT可行性报告_20261014.md:214-225` |
| A27 | **磁盘实测规模 = 2.5 GB / 77,509 文件 / git 跟踪 1,390 文件** | 六条主题线并行深读 | `00_审计总报告.md:4`、`00_审计总报告.md:349` |
| A28 | **MANIFEST 集合层面完全自洽** | 清单 77,509 条 = 磁盘 77,509 条，零缺失零多余 | `00_审计总报告.md:342` |
| A29 | **审计缺口的实机裁决：项目数字全部正确** | `allmenu` videoquality 去重 **44（31+13）**、`cmd_value` 出现 **666**、item 总数 **740**、`curmenu enable=yes`（NTSC+mov）**18**、幽灵档**恰好 1 个**、47 个可写域 — **全部复现 ✅** | `08_实机与离线验证记录_20261014.md:31-40` |
| A30 | **`allmenu` 归档与实机逐字节相同** | sha `2cf69074d41a…`（307,714 B，model="S5"），四份归档全同 | `05_相机只读快照_20261014/README.md:72` |
| A31 | **`+0x200` 偏移模型确证** | V29 type=2 明文分区「sha256(data)==记录 SHA」**7/7 命中**（错误偏移仅 2/7）；**V11/V20/V23/V24/V29 五版全部 7/7** | `06_密码学重跑/结论.md:14, 68` |
| A32 | **阳性对照成功 ⇒ 项目那两次"0 命中"是假阴性** | 真密钥确证在候选集合内；错误偏移 **6/6 全部漏检**，正确偏移 **6/6 全部命中真密钥**（无假阳性）；211 子集 wrong=0 / correct=命中 | `06_密码学重跑/结论.md:15, 278-290` |
| A33 | **记录 SHA 语义就是"明文的 SHA-256"** | type=2 直接 7/7；`storage` 记录 SHA == `SHA256(b'')` = `e3b0c442…b855` | `06_密码学重跑/结论.md:90-97` |
| A34 | **全库只有一对已知明文** | `ipu_data`（type=3, 262144 B, IV=`0e43dbd57c2da5fbc9c59ba5a71f9f37`）记录 SHA == `SHA256(262144 个 0x00)` == `8a39d2abd3999ab7…b4a90` | `08_实机与离线验证记录_20261014.md:164-174` |
| A35 | **41 个加密分区逐版本 IV 全变、全唯一** | `IV 逐版本全变 41 / 全同 7（全零 IV 的 type=2）/ 部分变化 0` | `06_密码学重跑/结论.md:242-244` |
| A36 | **同偏移密文相等率 ≈ 随机基线 ⇒ 排除 ECB 与版本稳定 keystream** | 全体 type=3 平均 **0.3881%** vs 随机基线 **0.3906%** | `06_密码学重跑/结论.md:223, 329` |
| A37 | **`0x220-0x260` 的 64B 是逐版本变化的签名样数据** | 5 版互异、高熵、位置固定；`0x200-0x20C` = `b"panasonic"`；非零字节 V29 63/64、V24/V23/V20 64/64、V11 63/64 | `07_签名与密钥恢复/结论.md:45-49` |
| A38 | **CBC + 全零明文 ⇒ 块全同 —— 这条准则是错的** | 块全同是 **ECB + 常量明文**的指纹。自造样本实测：真 CBC+全零 → `len(set(blocks))=256/256`；真 CTR → `256/256`；真 ECB → **1** | `06_密码学重跑/结论.md:150-167` |
| A39 | **`ipu_data` 实测 `len(set(blocks)) = 16384/16384`** | ⇒ **只能排除 ECB，CBC 与 CTR 在本数据上不可区分** | `06_密码学重跑/结论.md:169-176` |
| A40 | **RSA-4096 模数未恢复** | e∈{3,5,7,17,257} × 3,620 候选 × BE/LE 全排除；e=65537 前 24 高先验候选（PKCS#1 v1.5+DigestInfo）× BE/LE 全排除（3,012 s） | `07_签名与密钥恢复/结论.md:248-269` |
| A41 | **ECDSA 公钥未恢复** | 累计 **90,144 组**（602 唯一消息候选 × 3 曲线 × 11 哈希 × 4 编码端序，约 **1,014 GB** 哈希）→ **0 收敛**；工具自检 **6/6 PASS**（T1–T5b） | `07_签名与密钥恢复/结论.md:95-121` |
| A42 | **60606 在 station（家网）模式即暴露且无需认证** | `GET http://192.168.1.131:60606/Lumix/Server0/ddd` → **200 OK, 1624 B**；泄露 `serialNumber=WJ1DA######`、`friendlyName=S5-XXXXXX`、UDN 内嵌 Wi-Fi MAC、`X_FirmVersion=2.90`、`X_PTPPortNo=15740`、`X_AdditionalFunction=CPRemoteView` | `08_实机与离线验证记录_20261014.md:69-88` |
| A43 | **60606 的边界是信息泄露，不是文件访问** | 两个 UPnP 服务所有 SOAP 控制动作（含只读 `GetProtocolInfo`/`GetSystemUpdateID`/`Browse`）**一律 403**；静态描述 200 | `08_实机与离线验证记录_20261014.md:89-90` |
| A44 | **菜单 `enable` 语义 = "可选"，不是"当前值"** | `videoformat_mp4` 与 `_mov` **同时** `enable="yes"`（当前只有 mov）；`ntsc` 与 `pal` 也同时 yes | `08_实机与离线验证记录_20261014.md:96-108` |
| A45 | **LUT 面板依赖 numpy+Pillow，缺失时自动禁用** | 原有监看/对焦/拍照**零第三方依赖**（纯 Python 3 标准库） | `12_S5无线监看_v1.0_20261014/README.md:202-204` |
| A46 | **256³ 精确查表与逐帧三线性逐位等价** | 全色域随机图 + 8 个角点验证最大差 **0**；预计算 4.7 s、内存 50 MB | `12_S5无线监看_v1.0_20261014/README.md:262-271` |

### 1.2 强推断 ◐

| # | 结论 | 推断依据 | 出处 |
|---|---|---|---|
| B1 | **`0x220` 的 64B 是"ECDSA P-256 签名"是三级转述，源头已自我撤回** | 上游 `07_参考仓库/s1m2-research/docs/CORRECTIONS.md:12` 明文：「外层 ECDSA 字段与签名机制已经确认」→**「字段名称是候选；没有签名验证和完整机制证据」**。原始依据仅「长度 = 64 字节」 | `07_签名与密钥恢复/结论.md:173-183` |
| B2 | **`0x220` 是 HMAC 或带密钥 KDF 输出** —— 离线不可判定 | 直接摘要相等性检验（135 消息 × 13 哈希）**0 命中**，但带密钥构造无法离线排除 | `07_签名与密钥恢复/结论.md:143, 164` |
| B3 | **「版本字段的值」几乎必然被某条链保护** | 内层副本 `0x2BC/0x2C4` 在 CRC32 覆盖内且落在 `[0x200, L-512)` 内 ⇒ 只要存在任何覆盖 ⊇`[0x200, L-512)` 的签名（RSA 或 ECDSA），版本字段值就被该签名覆盖 | `07_签名与密钥恢复/结论.md:216-217` |
| B4 | **"固定密钥"目前只是假设，不是由跨版本实测支持的结论** | 48 分区里「明文相同 **且** IV 相同」的只有 7 个，而全是 type=2 明文分区（IV 全零、根本没加密）；type=3 中该对照组 = **0 个** ⇒ 跨版本数据对"密钥是否跨版本相同"**零检验力** | `06_密码学重跑/结论.md:231-238` |
| B5 | **`accctrl` 访问控制是"单客户端会话"式** | 监看进程持 `ok` 时，另起的 `curl` 一律 `err_unsuitable_app` | `10_仓库补丁/定因与交接_20261014.md:202-209` |
| B6 | **DLNA 控制面 403 与推流无关** | 推流中 Browse = 403；**停流后 Browse 仍 = 403** ⇒ "相机资源被长推流占住"假设已排除 | `10_仓库补丁/定因与交接_20261014.md:192-200` |
| B7 | **卡文件名规则**：仅字母数字；FAT32(SD/SDHC) ≤ 8 字符（不含扩展名）；exFAT(SDXC) ≤ 255 字符（含扩展名） | 同页官方原文 | `09_LUT可行性报告_20261014.md:280` |
| B8 | **`.cube` 支持内嵌 base Photo Style，`.vlt` 不支持** | `#LUMIXPHOTOSTYLE <TAG>` **仅 `.cube` 支持**；机身接受 **2–33 点**网格 | `09_LUT可行性报告_20261014.md:316-317` |
| B9 | **S5 的 HDMI 输出规格与外录能力匹配性、以及两套 LUT 机制是否互斥需实测** | S5M2 手册明写"在 `[Photo Style]` 画质调整里套 LUT 时 `[LUT View Assist]` 不可用" | `09_LUT可行性报告_20261014.md:348` |
| B10 | **S5 代 SoC 公开名 = V9AHD（pvc02v），4×Cortex-A7** | `pvc0xV` = 松下对 Milbeaut 硅片的封装平台名（pvc02v=V9AHD、pvc03v=V10、pvc04v=M20V）；SD 控制器为松下自定义 `"panasonic,sdhci"`（sdio@0x7c320000），**非 Milbeaut 标准 F_SDH30** | `10_仓库补丁/口径修正_SD引导与SoC代_20261015.md:13-21` |

### 1.3 弱推断 ⚠️

| # | 结论 | 为何只是弱推断 | 出处 |
|---|---|---|---|
| C1 | **热点密码可由公开 MAC 推算** | 1 个样本：MAC `70:74:14:XX:XX:XX`，热点密码 `a707########`，去掉首字母 `a` = `70741470e2` + `3`，MAC 前 10 位 = `70741470e2` **完全一致**。**建议记为「强相关，待验证」** | `12_S5无线监看_v1.0_20261014/连热点时怎么测.md:46-60` |
| C2 | **`0x220` 是 Schnorr / HMAC-SHA-512 / 两个独立 32B 随机数** | 这些没有公钥恢复性质，无公钥时原理上不可证实/证伪 | `07_签名与密钥恢复/结论.md:164` |
| C3 | **SD.DAT 路线的第一道门（MC801 BootROM 有无 SD 入口）** | 公开证据**无法判定**；唯一直接判定手段 = 拆机引 UART 看 bootlog。新口径：M8M/M10V 已证实；**PVC/MC801 待证实（正反均无直接证据）** | `10_仓库补丁/口径修正_SD引导与SoC代_20261015.md:11, 30-32` |
| C4 | **`Lumix-Fast`(Android) 字符串池含 LUT 面 —— 不能当结论** | 那些字符串**只出现在 dex 字符串池**，无可用 JRE ⇒ 无法方法级归因；且 S5 无 Real Time LUT 功能簇，即使存在该 tag 大概率也不接受 | `09_LUT可行性报告_20261014.md:227-239` |

### 1.4 未验证 ✗

| # | 主张 | 状态 | 出处 |
|---|---|---|---|
| D1 | **项目 iOS App 声称 DLNA Browse 可用** | **库内无任何成功证据**（全部 60606 证据只是设备描述本身 200） | `14_总包审计与新方向_20261014/README.md:111`（E-3） |
| D2 | **「版本字段是否在签名覆盖内」** | **裁决：不可判定**（既不是"成立"也不是"不成立"） | `07_签名与密钥恢复/结论.md:19, 189-195` |
| D3 | **「`err_user_refused` 需 BLE 绑定」** | **0 次验证**，工具从未运行 ⇒ 纯假设 | `00_审计总报告.md:518` |
| D4 | **「WPA2 机型 BLE 会返回真实密码」** | **0 次实测** ⇒ 纯外推 | `00_审计总报告.md:519` |
| D5 | **「UART 死路」** | S1R2 类比，**S5 的 P3 核验从未执行** ⇒ 必须写成"S5 未验证" | `08_实机与离线验证记录_20261014.md:150-152` |
| D6 | **exFAT 越界写 & NULL 提前返回** | **两者均未证实**（撤回逻辑本身也不成立） | `00_审计总报告.md:284` |

---

## 2. 已验证可用的操作路径 ★（命令原样抄全）

### 2.1 ★ 监视器完整可用功能与确切启动命令

#### 2.1.1 能力矩阵（实测可用）

| 功能 | 操作 | 实测指标 | 出处 |
|---|---|---|---|
| **实时监看** | 打开即看 | **640×432 @ 18fps**，延迟约 **0.27 秒**（热点直连实测 **53 ms**） | `使用说明.md:45`、`README.md:473` |
| **触摸对焦** | **点画面** | 绿框落点 = 对焦点；AF 模式正常工作，**实测 8/8 = 100%** | `使用说明.md:46` |
| **连续对焦** | **按住拖动** | 3Hz 限流 | `使用说明.md:47` |
| **焦点驱动（近/远）** | 点或**长按**「焦点近 ▶」「◀ 焦点远」 | 长按连续驱动 | `使用说明.md:48` |
| **拍照** | 点底部 **⚪ 大圆** | `camcmd?value=capture` | `使用说明.md:49` |
| **录像起/停** | 点 **◉** | 带红色计时；`video_recstart`/`video_recstop` | `使用说明.md:50` |
| **AE 锁定** | 点 **AE** | `camctrl?type=af_ae_lock&value=on\|off` | `使用说明.md:51` |
| **回放 / 拍摄切换** | 点 **▶回放** / **◉拍摄** | 回放模式下无取景流（正常） | `使用说明.md:52` |
| **全屏 / 停流省电** | **⛶** / **⏸** | 再点恢复 | `使用说明.md:53-54` |
| **📊 诊断** | 卡顿归因报告 | 显示延迟、队列、相机侧空档、逐条卡顿事件 | `使用说明.md:60` |
| **🧪 控制自检** | 逐条测试 **12 个**控制命令 | 告诉你哪些当前可用 | `使用说明.md:61` |
| **🎨 LUT 面板** | 选文件 → 勾「启用」 → 取景即套上 | 需 numpy+Pillow（缺失自动禁用） | `README.md:120-131` |
| **📁 机身存储访问** | 列举相机内容 → 下载原图 → 自动套 LUT | 见 §2.1.5 | `README.md:143-145` |

#### 2.1.2 启动命令（v1.0 原始工具，最完整）

```bash
 # 三步
1. 确认网络 —— 相机接入 Wi-Fi（或手机热点），电脑与相机在同一网络。验证：ping 192.168.x.x
2. 启动 —— 双击 启动.command（macOS），或命令行 ./run.sh 192.168.x.x
3. 打开浏览器 —— 访问终端打印的 http://<本机IP>:8080
```
> `12_S5无线监看_v1.0_20261014/README.md:17-22`（逐字抄录）

```bash
./run.sh <相机IP> [端口] [节奏模式] [帧率]

./run.sh 192.168.x.x                 # 默认 8080 端口、固定 18fps
./run.sh 192.168.x.x 8090            # 换端口
./run.sh 192.168.x.x 8080 fixed 12   # 降至 12fps 省带宽
./run.sh 192.168.x.x 8080 adaptive   # 自适应模式（不推荐）
```
> `12_S5无线监看_v1.0_20261014/README.md:24-30`、`使用说明.md:101-109`

| 参数 | 默认 | 说明 |
|---|---|---|
| 相机IP | `192.168.54.1` | 相机地址（默认值为相机 SoftAP 网关） |
| 端口 | `8080` | 本机 HTTP 端口 |
| 节奏模式 | `fixed` | `fixed`=固定帧率取最新帧；`adaptive`=跟随相机速率（不推荐） |
| 帧率 | `18` | fixed 模式输出帧率（官方 640p 标准） |

`run.sh` 实际 exec 的命令（★ 原样）：
```bash
exec python3 "$(dirname "$0")/s5monitor.py" --host "$HOST" --port "$PORT" \
     --pacing-mode "$MODE" --pacing-fps "$FPS" --device-name "LUMIX Sync"
```
> `12_S5无线监看_v1.0_20261014/run.sh:47-48` ★

**含 LUT 的启动方式**（挑带 numpy/Pillow 的解释器）：
```bash
./启动_含LUT.command <相机IP> <端口>      # 默认 192.168.1.131 / 8080
exec "$PY" -u s5monitor.py --host "$CAM" --port "$PORT" --device-name "LUMIX Sync"
```
> `12_S5无线监看_v1.0_20261014/启动_含LUT.command:12-13, 51` ★

#### 2.1.3 启动命令（v1.5 发行包，当前推荐）

```bash
 # 1) 安装依赖（只需一次）：双击 首次运行_安装依赖.command
 #    → 在本目录创建独立虚拟环境 .venv 并安装 numpy/Pillow；失败自动换国内镜像
 # 2) 让相机上线：相机菜单 → Wi-Fi → 遥控拍摄与监看（或"发送图像"），相机自建热点
 #    Mac 的 Wi-Fi 连上相机热点（SSID 形如 S5-XXXXXX），相机 IP 就是 192.168.54.1（网关）
 # 3) 启动：双击 启动.command（或 ./启动.command <相机IP>）
 #    等 10–20 秒让授权完成（页面顶栏显示 access=ok），浏览器打开 http://127.0.0.1:8080
```
> `16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/README.md:13-36`（逐字抄录）

`启动.command` 实际 exec（★ 原样）：
```bash
exec "$PY" -u s5monitor.py --host "$CAM" --port 8080 --device-name "LUMIX Sync"
```
> `16_…/S5无线监看_LUT版_v1.5/启动.command:56` ★

安装依赖的实际命令（★ 原样）：
```bash
python3 -m venv .venv
.venv/bin/python3 -m pip install --quiet --disable-pip-version-check numpy pillow
 # 官方源失败时：
.venv/bin/python3 -m pip install --quiet --disable-pip-version-check \
     -i https://pypi.tuna.tsinghua.edu.cn/simple numpy pillow
```
> `16_…/首次运行_安装依赖.command:40, 46-47, 51-52` ★（VERSION 文件内容 = `1.5`）

#### 2.1.4 命令行入口（v1.5 全部工具）

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
> `16_…/S5无线监看_LUT版_v1.5/README.md:111-122`（逐字抄录）

**一键取片全参数**：
```bash
python3 s5_get_photo.py                # 取最新一张并套 LUT
python3 s5_get_photo.py --shoot        # 先拍一张再取
python3 s5_get_photo.py --no-lut       # 只下载
python3 s5_get_photo.py --index 0      # 取第 0 张
```
> `12_S5无线监看_v1.0_20261014/README.md:416-421`

**s5_content.py 子命令**（DLNA 全流程）：
```bash
python3 s5_content.py cleanup --cam 192.168.1.131   # 清理陈旧 pending（解决"需要更新app"）
python3 s5_content.py diagnose --cam 192.168.1.131  # 全因素诊断（含 ok 门判读）
python3 s5_content.py sweep   --cam 192.168.1.131   # 已放行后扫 ObjectID
python3 s5_content.py list    --cam 192.168.1.131   # 列举内容
```
> `10_仓库补丁/定因与交接_20261014.md:325-330`

#### 2.1.5 新增 HTTP 端点（v1.1+）

| 端点 | 说明 |
|---|---|
| `GET /api/luts` | 列出 LUT、当前选择、是否启用、单帧耗时 |
| `GET /api/lut?name=<文件>` | 选择 LUT（`name=off` 关闭） |
| `GET /stream?lut=1` | **套 LUT 的实时取景流**（MJPEG） |
| `GET /api/content_diag` | 机身存储访问诊断全文 |
| `GET /api/gallery?id=<ObjectID>` | 列举相机内容（DLNA Browse） |
| `GET /api/download?res=<url>&name=<f>&bake=1` | 下载并可选套 LUT |

> `12_S5无线监看_v1.0_20261014/README.md:192-199`

#### 2.1.6 协议层确切报文（★ 原样抄全）

**取景流协议**：
```
GET http://<相机IP>/cam.cgi?mode=camcmd&value=recmode        切拍摄模式
GET http://<相机IP>/cam.cgi?mode=startstream&value=<UDP端口>  相机把流发到该 UDP 端口
      ↓
UDP 上收到 MJPEG：每个包内含完整 JPEG（SOI ff d8 … EOI ff d9）
      ↓
GET http://<相机IP>/cam.cgi?mode=stopstream                   停止
```
> `附_技术参考.md:9-16`（v1.0 与 v1.5 两份逐字节相同）

**控制命令逐条对照（逐条对照官方 APK 还原）**：

| 功能 | 命令 | 备注 |
|---|---|---|
| **触摸对焦** | `camctrl?type=touch&value=<x>/<y>&value2=on` | ★ **斜杠分隔**，且**必须带 `value2=on`** |
| 释放 | `camctrl?type=touch&value=0/0&value2=off` | 抬起时发 |
| 移动 AF 点 | `camctrl?type=touchaf_chg_pos&value=<x>/<y>` | |
| AF 区域 | `camctrl?type=touchaf_chg_area&value=up\|down` | |
| AE 锁定 | `camctrl?type=af_ae_lock&value=on\|off` | |
| **焦点驱动** | `camcmd?value=tele-normal` / `wide-normal`（还有 `-fast`） | capability 明确列出，**稳定可用** |
| 停止驱动 | `camcmd?value=focus-stop` | |
| 拍照 | `camcmd?value=capture` | |
| 录像起/停 | `camcmd?value=video_recstart` / `video_recstop` | |
| 模式 | `camcmd?value=recmode` / `playmode` | |
| 读对焦模式 | `getsetting?type=focusmode` | 返回 `<settingvalue focusmode="afs">` |

> `附_技术参考.md:67-79`

**`accctrl` 会话（授权）**：
```
GET cam.cgi?mode=accctrl&type=req_acc&value=<设备ID>&value2=<设备名>
      ↓
返回： <状态>,<相机名>,<模式>,<加密标志>
      例： ok,S5-XXXXXX,remote,encrypted
```
- 设备 ID 格式：**`4D454930-0100-1000-8001-` + seed**（逆向自官方 APK）
- 实际使用的完整 UUID：**`4D454930-0100-1000-8001-020A0003BD13`**
- 相机名 `S5-XXXXXX` 与 **BLE 广播名一致**（交叉验证）

> `附_技术参考.md:122-137`、`12_S5无线监看_v1.0_20261014/README.md:483`

**清理陈旧 pending（★ 同一 UUID，实测有效）**：
```bash
curl -s -A "LUMIX Sync" \
  "http://192.168.1.131/cam.cgi?mode=accctrl&type=req_acc_can&value=<同一UUID>&value2="
```
> `10_仓库补丁/定因与交接_20261014.md:256-259`

**恢复流程（出现 invalid login 时）**：
```
① 相机断电重启（拔电池几秒再上电）—— 这一步不可省
② 确认在线：curl -s -A "LUMIX Sync" "http://<相机>/cam.cgi?mode=getstate"  → <result>ok</result>
③ 启动本工具【一次】，然后不要再碰相机
④ 通常 10–20 秒内 accctrl 变 ok（顶栏显示）
```
> `12_S5无线监看_v1.0_20261014/README.md:245-250`

**DLNA 官方请求（从 APK 取出，`p168v5/a.java:212-213`、`p168v5/m.java:83-87`）**：
```
URL      : http://<ip>:60606/Server0/CDS_control
Headers  : Accept-Charset: UTF-8
           Content-Type: text/xml; charset="utf-8"
           SOAPAction: urn:schemas-upnp-org:service:ContentDirectory:1#Browse
           User-Agent: Panasonic MIL DLNA CP UPnP/1.0
           Host: <ip>:60606
Body     : 单行无空白；子元素**不带 s: 前缀**；含松下私有扩展
           <pana:X_FromCP>LumixLink2.0</pana:X_FromCP>
           xmlns:pana="urn:schemas-panasonic-com:pana"
```
> `12_S5无线监看_v1.0_20261014/README.md:294-304`、`10_仓库补丁/定因与交接_20261014.md:79-89`

**响应形状**（`NumberReturned=16`，每条 item 含三种分辨率）：
```xml
<item id="01000018" parentID="0">
  <dc:title>100-0018</dc:title>
  <upnp:class name="imageItem">object.item.imageItem</upnp:class>
  <res ...DLNA.ORG_PN=JPEG_LRG... size="9346560">http://<ip>:50001/DO01000018.JPG</res>  ← 原图
  <res ...DLNA.ORG_PN=JPEG_MED... size="100000"> http://<ip>:50001/DM....JPG</res>      ← 中图
  <res ...DLNA.ORG_PN=JPEG_TN ... size="5000">   http://<ip>:50001/DT01000018.JPG</res>  ← 缩略图
</item>
```
> `12_S5无线监看_v1.0_20261014/README.md:310-318`
> **⇒ `50001` 端口就是内容数据服务**（此前项目报告 18 说它"家网侧不存在"，实测**存在且未识别**）

**SSDP "alive" 上报**：
> 官方 App 的 `DlnaWrapper.advertisementStart()`（native `dlnaCore`）会向网络广播自己的存在。本工具已复刻：向 `239.255.255.250:1900` 发 **SSDP alive NOTIFY** + **M-SEARCH**（每 20 秒重发），并提供 `/desc.xml` 供 SSDP `LOCATION` 引用。
> `附_技术参考.md:162-164`

**可调参数（`s5monitor.py` 顶部）**：
```python
PACING_MODE = "fixed"     # fixed=官方风格；adaptive=队列反馈控制
PACING_FPS  = 18.0        # 输出帧率
FIXED_KEEP  = 3           # 最多保留 3 帧（≈170ms），抗短空档
KEEPALIVE_SEC = 10.0      # 心跳间隔
```
> `附_技术参考.md:45-50`

#### 2.1.7 相机在线自检（连热点时怎么测"边录边发"）

```bash
cd "/Users/<user>/Documents/ChatGPT/S5_逆向_项目总包_20261012/12_S5无线监看_v1.0_20261014"
/Users/<user>/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3 s5_selfcheck.py
```
> `12_S5无线监看_v1.0_20261014/连热点时怎么测.md:14-17`
> 脚本自动找相机（先试 `192.168.1.131`，再试热点网关 `192.168.54.1`），然后：① 报相机当前模式（rec/play）② ★ 关键：测 rec 模式下 DLNA 内容树有没有内容 ③ 有内容就下载第一张验证

先在【家网】下试（不用动 Wi-Fi）：
```bash
/Users/<user>/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3 \
  s5_selfcheck.py --cam 192.168.1.131
```
> `连热点时怎么测.md:37-40`

**怎么读结果**：
| 输出 | 含义 | 下一步 |
|---|---|---|
| `内容条目数 = 0`，HTTP 200 | 有响应但**没内容** | 「边录边发」没生效，或该模式不支持此网络形态 |
| `HTTP 403` | **授权没到 `ok`**（不是模式问题） | 先跑监看工具拿 `ok`，再重跑本脚本 |
| `内容条目数 > 0` 🎉 | **「边录边发」生效** | 可在拍摄模式下无线取片 ⇒ 能实现"边录边套 LUT" |

> `连热点时怎么测.md:27-31`

**热点切换安全脚本**（本机默认路由走有线 en9，切 Wi-Fi 不断网）：
```bash
./ap_test.command              # 全程自动（测完自动断开热点）
./ap_test.command --keep       # 测完保留热点连接
./ap_test.command --ssid X --pass Y
```
内部关键命令（★ 原样）：
```bash
networksetup -setairportnetwork en0 "$SSID" "$PASS"
route get default | awk '/interface:/{print $2}'      # 安全检查：确认为 en9 而非 en0
networksetup -setairportpower en0 off                 # 断开还原
```
> `12_S5无线监看_v1.0_20261014/ap_test.command:8-13, 39, 51, 60, 117` ★

#### 2.1.8 实测数据速查（可直接引用）

| 项 | 结果 | 出处 |
|---|---|---|
| 授权耗时 | **10 秒**（干净状态） | `README.md:340` |
| 内容条目 | **16**（15 JPEG + 1 MP4） | `README.md:341` |
| 下载原图 | **9,346,560 B** = 6000×4000 MPO | `README.md:342` |
| 下载后套 LUT（全尺寸 6000×4000） | **432 ms** | `README.md:343` |
| 下载后套 LUT（1600px） | **38 ms** | `README.md:344` |
| 取片实测（相机 `[照片风格]=V-Log`） | 列举 11 张；下载 **9,613,312 B / 6.9 s = 11.1 Mbps**；规格 6000×4000 | `README.md:429-433` |
| **风格判定** | 黑位 P1 = **33**（V-Log 理论黑位 `0.125×255 = 31.9` ★几乎一致），真黑占比 0.0% ⇒ 🟦 **确为 V-Log** | `README.md:432` |
| 套 LUT（33³） | **385 ms @ 6000×4000**，平均像素差 29.1 | `README.md:433` |
| 实时套 LUT 单帧（640×432） | **20–26 ms** | `README.md:129` |
| 逐帧三线性（640×360 真实分辨率） | **73–160 ms** ⇒ 远超 55.6 ms 预算 ⇒ 画面看起来完全卡死 | `README.md:259-260` |
| 256³ 查表（640×360） | **6.7 ms**；吞吐 17.4 → 17.8 fps（零损失）；构建 4.7 s；内存 50 MB | `README.md:266-271` |

---

### 2.2 ★ 错误码语义总表与每种的处理方法

#### 2.2.1 HTTP API 层错误码（`附_技术参考.md:96-105`）

| 返回 | 含义 | 处理 |
|---|---|---|
| `ok` | 成功 | — |
| **`err_param`** | **参数格式错** | 检查格式（**不重试**） |
| **`err_reject`** | 格式对，但**相机当前状态不接受** | **重试**（状态会翻动） |
| **`err_busy`** | 相机忙 | **退避重试** |
| `err_critical` | 严重状态错误 | 重启相机（先用 `camcmd&value=recmode` 重试） |
| `err_user_refused` | 相机内部校验拒绝 | 重新走流程 |

**补充语义（10-14 实测定案，`00_项目总结/02_项目时间线.md:265-270`）**：

| 返回 | 语义 | 处置 |
|---|---|---|
| **`ok`** | 请求被接收 | ⚠️ **≠ 生效**，必须回读 `getsetting videoquality` 确认（当天 **≥6 次反例**） |
| **`err_reject`** | 格式对、状态不接受 | **退避重试 8–12 次、间隔 2–3 秒** |
| **`err_param`** | 参数格式被拒 | 不重试，检查档名 |
| **`err_critical`** | 严重状态错误 | 先重试（`camcmd&value=recmode` 实测重试即 `ok`），仍失败才重启 |

#### 2.2.2 `accctrl` 状态取值表（`附_技术参考.md:129-134`）

| 状态取值 | 含义 | 处理 |
|---|---|---|
| **`ok`** | **完整授权**（camctrl / DLNA 控制面可用） | — |
| `ok_under_research_no_msg` | 受限；相机未显示待批消息 | DLNA 控制面返回 **403**；用同一 UUID 发 `req_acc_can` 清理 |
| `ok_under_research` | 受限 | 同上 |
| `err_user_refused` | 相机内部校验拒绝 | 重新走流程 |
| **`err_others_requesting`** | **相机端唯一的"待批复"槽被别的请求占住** | ⛔ **不要清理**（那是别人占着会话，误伤他人请求）；先等 5 秒让相机清掉上一个请求 |
| **`err_unsuitable_app`** | 客户端不是合适的 App（**监听器持有 `ok` 时裸 curl 一律返回这个，是正常的不是故障**） | 走监视器自己的 HTTP API，不要绕过它 |

> 出处：`附_技术参考.md:129-134`、`12_S5无线监看_v1.0_20261014/README.md:166-167, 240`、`10_仓库补丁/定因与交接_20261014.md:116-118, 205-208`、`s5monitor.py:276-278` ★

#### 2.2.3 帧流层错误码

| 返回 | 含义 | 处理 |
|---|---|---|
| `startstream → err_busy` | 相机侧有残留流会话（相机**强制单流会话**） | **相机断电重启**；工具做法 = 先 `stopstream` 清场 + 退避重试 4 次 |

> `附_技术参考.md:26-27, 181`

#### 2.2.4 UPnP / DLNA 层判定

| 现象 | 含义 | 处理 |
|---|---|---|
| **HTTP 403** | **`accctrl` 未达 `ok`**（不是"相机对 DLNA 单独限制"） | 先拿 `ok` 再重试 |
| **HTTP 500 + `<errorCode>701</errorCode> No such object`** | **控制面已放行**（能收到 SOAP Fault 就是证据），只是 ObjectID 不对 | 换 ObjectID / 跑 `sweep` |
| 内容树 `NumberReturned=0` | **相机不在回放模式**（拍摄模式下内容树是空的） | 切回放：`camcmd&value=playmode` |

> `10_仓库补丁/定因与交接_20261014.md:281-289`、`12_S5无线监看_v1.0_20261014/README.md:286-291`

---

### 2.3 ★ LUT 工具链：格式、烧录路径、17³ vs 33³

#### 2.3.1 三条路（含机内可行性裁决）

| 路径 | 实时性 | 能否烧进文件 | 前置条件 | 出处 |
|---|---|---|---|---|
| **A. HDMI 外录 + `LUT View Assist (HDMI)`** | ★★★ **真·实时** | ✅ 烧进外录文件 | 外接录机；且 S5 需有该 HDMI 开关 | `15_LUT烧录工具_20261014/README.md:254` |
| **B. WiFi 取片 + 本地烧（`wifi_lut.py`）** | ★★ 照片数秒～十几秒 | ✅ | 需取片通道可用（**已跑通**，见 §2.1.5） | 同上 `:255` |
| **C. USB 大容量存储 + 卡挂载 + `watch_bake.py`** | ★ 批处理（该模式下通常不能拍摄） | ✅ | 相机菜单 → USB 连接模式 → **大容量存储** | 同上 `:256` |
| **D. 卡插读卡器 + `watch_bake.py`** | ★ 批处理 | ✅ | 卡要取出 | 同上 `:257` |
| **❌ 机内实时烧录** | — | ❌ **不可能** | 三层理由见下 | 同上 `:236-243` |

> **蓝牙（BLE）不可行**：只暴露凭据面（SSID/密码），**没有文件传输面**；有效吞吐 ~10–100 KB/s 量级，一张 10 MB JPEG 要数分钟。视频更无可能。`15_LUT烧录工具_20261014/README.md:259`

**机内实时烧录不可能的三层裁决**：
| 层次 | 结论 |
|---|---|
| **功能层** | Real Time LUT 是 **S5II / S5IIX / GH7 / S9 / G9M2 / S1M2 / S1R2** 的能力。官方三机对比表「照片风格」行：S5 清单里**没有「リアルタイムLUT」**，S5Ⅱ 有 |
| **管线层** | 它是**一个照片风格条目**，背后需要**实时 3D LUT 插值**并与 JPEG/HEIF 与视频编码器串联。S5 影像处理器没有这一级；S5 的 `MY PHOTO STYLE 1-10` 只有**参数化**调整（对比度/高光/阴影/饱和度/色相/降噪/锐度），**没有 LUT 槽位** |
| **可达层** | 跨代不可移植（MC801 32-bit A7 ↔ SC2006A 4×A53 64-bit）；固件加密 + 签名；无 RCE ⇒ 不是"开关还没找到"，而是**没有那级硬件管线** |

> `15_LUT烧录工具_20261014/README.md:236-243`

#### 2.3.2 `.vlt` 格式规范（等级 A，35 个官方文件逆向）

```text
 # panasonic vlt file version 1.0      ← 必需：格式版本头
 # source vlt file "Cyan 1 E-L.vlt"    ← 可选：来源文件名（注释）
LUT_3D_SIZE 17                        ← 必需：网格边长
                                      ← 空行
309 309 309                           ← 数据：4913 行 = 17³，每行 "R G B"
312 308 308
...
4095 4095 4095                        ← 最后一行
```
> `09_LUT可行性报告_20261014.md:286-294`

| 项 | 实测结果（35 个官方样本，共 172,095 行） |
|---|---|
| `LUT_3D_SIZE` | **全部为 17**，零例外 |
| 数据行数 | **4913 = 17³**，零例外 |
| 行格式 | 全部严格匹配 `^\d+ \d+ \d+$`（无小数、无第四列、无逗号） |
| 数值域 | **整数 0–4095（12-bit）**，实测最大值 4095 |
| 行尾 | **LF 与 CRLF 两种官方样本都存在** ⇒ 均可接受 |
| 体积 | ≈ 67–69 KB |
| 缺失字段 | **无** `DOMAIN_MIN/MAX`、`LUT_3D_INPUT_RANGE`、`TITLE`（即固定 12-bit 全域语义） |

> `09_LUT可行性报告_20261014.md:297-307`

**`.VLT` vs `.cube` 对照**：

| | Panasonic `.VLT` | Adobe `.cube` |
|---|---|---|
| 血统 | VariCam 35 / EVA1 → LUMIX | Resolve / Adobe / 全行业 |
| 数值域 | **整数 0–4095（12-bit）** | **浮点 0.0–1.0** |
| 头部 | `# panasonic vlt file version 1.0` + `LUT_3D_SIZE` | `TITLE`/`LUT_3D_SIZE`/`DOMAIN_MIN`/`DOMAIN_MAX` |
| 网格 | 官方样本全为 **17³** | 官方样本 33³；机身接受 **2–33 点** |
| 内嵌 base Photo Style | ❌ 不支持 | ✅ **仅 `.cube` 支持** `#LUMIXPHOTOSTYLE <TAG>` |

> `09_LUT可行性报告_20261014.md:311-317`

**自制 `.vlt`（格式简单到只需一个循环，★ 原样）**：
```python
N = 17
out = ['# panasonic vlt file version 1.0', '# source vlt file "MYLUT.vlt"', f'LUT_3D_SIZE {N}', '']
for b in range(N):
    for g in range(N):
        for r in range(N):
            R, G, B = my_transform(r/(N-1), g/(N-1), b/(N-1))   # 归一化输入 → 归一化输出
            out.append(f'{round(R*4095)} {round(G*4095)} {round(B*4095)}')
open('MYLUT.vlt', 'w', newline='\n').write('\n'.join(out) + '\n')
```
> `09_LUT可行性报告_20261014.md:372-381`
> **通用约定是 R 变化最慢、B 最快**（`.cube` 即如此）。生成 `.vlt` 时先沿用该约定，再用测试图在机身上验证是否套反。
> ⚠️ `ffmpeg` 的 `lut3d` 滤镜支持 `.cube/.3dl/.dat/.m3d`，**不支持 `.vlt`** ⇒ 可用来离线"验证套用效果"，但不能直接产出 `.vlt`。`09_LUT可行性报告_20261014.md:384`

#### 2.3.3 机身装载 LUT 的确切步骤

```
① 相机正常关机 → 取出 SD 卡 → 读卡器接到电脑
② 把 LUT 文件（.vlt）复制到【卡的根目录】——不要建文件夹
      文件名只用字母数字；FAT32 卡 ≤8 字符（不含扩展名）
③ 插回卡 → 开机 → [照片风格/Photo Style] 选 [V-Log]
④ 菜单 → [V-Log View Assist]
      ├─ [LUT Select]        选要套用的 LUT
      ├─ [LUT View Assist (Monitor)]  监视器/取景器套用
      └─ [LUT View Assist (HDMI)]     HDMI 输出套用
⑤ 屏幕出现 [LUT] 标记 = 已生效
```
> `09_LUT可行性报告_20261014.md:352-362`

**已实测确认**：`[LUT Select]` 成功列出了我们生成的 `VL709`。这把此前"高度可能（等级 D）"升级为**实机确证**。`09_LUT可行性报告_20261014.md:410-411`

**建议的分步验证法（把"格式问题"与"支持性问题"分开）**：
1. 先用**官方样本** `VLog_to_V709_forV35_ver101.vlt`（17³，已逐字节验证合规）当"已知 good 样本"——若机身能识别，说明目录名/命名/格式流程正确；
2. 再换成**自制 LUT**；
3. **必须实机验证轴序**：官方 `.VLT` **没有**声明"哪个通道变化最快"。若套用后出现明显色偏，把生成时的 R/B 索引对调即可恢复。
4. 记录：能否识别 33³？能列几个 LUT？

> `09_LUT可行性报告_20261014.md:364-368`

#### 2.3.4 17³ vs 33³ —— 结论

| 项 | 17³ | 33³ |
|---|---|---|
| **机身能否读** | ✅ 官方样本全为 17³；机身接受 | ◐ **仍待实机确认**（`09_LUT可行性报告_20261014.md:368` 明确列为待记录项） |
| **实时监看** | 可用 | ✅ **可用且画质更好** |
| **暗部差异** | — | **两网格暗部差异可达 126**（V-Log 曲线暗部很陡，17³ 不够用） |
| **后期软件** | 可用 | ✅ 官方 `.cube` 样本 33³；机身接受 2–33 点 |

> **原话**：「**17³ 与 33³ 网格在暗部差异可达 126 —— V-Log 曲线暗部很陡，17³ 不够用。机身只吃 17³，但实时监看可以用 33³，画质更好。**」`12_S5无线监看_v1.0_20261014/README.md:140-141`
> **注意**：机器上 v1.5 发行包 `lut/` 里**同时有** `vlog_to_709_33.cube`(970,381 B) 与 `vlog_to_709_33.vlt`(380,320 B)；`15_LUT烧录工具_20261014/lut/` 也生成 33³ 的 `.cube` 与 `.vlt`。但 §2.3.3 的机身步骤与 33³ 机身可读性仍标注为待确认。

#### 2.3.5 LUT 烧录工具确切命令（`15_LUT烧录工具_20261014/`）

**快速开始**：
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
> `15_LUT烧录工具_20261014/README.md:31-46`

**`make_lut.py` — 生成 LUT**：
```bash
python3 make_lut.py --from vlog  --size 17 --formats vlt  --out /Volumes/LUMIX/   # 给机身
python3 make_lut.py --from vlog  --size 33 --formats cube --out lut/               # 给后期
python3 make_lut.py --selftest                                                      # 只跑自检
```
> `15_LUT烧录工具_20261014/README.md:54-58`

**为什么自己算**（官方 `.vlt` 需从松下站点下载；本工具用**公开规范**推导）：
- Panasonic V-Log OETF：`V = 5.6L + 0.125`（L<0.01）；`V = 0.241514·log₁₀(L + 0.00873) + 0.598206`
- 自检锚点（全部通过）：**0% 黑 = 0.125**、**18% 灰 = 0.4233**、断点 **V=0.181 ↔ L=0.01 两侧连续**
- V-Gamut 原色（`0.730,0.280 / 0.165,0.840 / 0.100,−0.030`，D65）→ BT.709 原色的 3×3 矩阵
- ITU-R BT.709 OETF
> **→ 结果是规范自洽的等效转换，不是官方 LUT 的逐字节复刻。** 要官方原版去 <https://av.jpn.support.panasonic.com/support/global/cs/dsc/download/lut/index.html>
> `15_LUT烧录工具_20261014/README.md:60-68`

**`bake` — 烧录器**：
```bash
./bake probe <文件>                       # 看规格（分辨率/帧率/编码/位深）
./bake image <lut> <in> <out>             # 照片（jpg/png/tif/heic）
./bake video <lut> <in> <out> [选项]       # 视频
./bake batch <lut> <outdir> <in...>       # 批量
```
> `15_LUT烧录工具_20261014/README.md:76-80`

| 选项 | 说明 |
|---|---|
| `--max-seconds N` | 只烧前 N 秒（试跑用） |
| `--bitrate 120M` | 走显式码率路径（HEVC Main10） |
| `--codec hevc\|h264` | 默认 hevc |
| `--cs srgb\|bt709\|bt2020\|linear\|displayp3` | LUT 解释用的色彩空间（默认 sRGB） |
| `--vlt-axis variCam\|cube` | `.vlt` 轴序（默认 variCam；套上去色偏就换 cube） |

> `15_LUT烧录工具_20261014/README.md:82-88`

**实测性能**（源：`P1000026.MP4` 5184×3456 10-bit HEVC 29.97fps，107 Mbps）：
| 路径 | 位深 | 码率 | 6K 速度 |
|---|---|---|---|
| 默认 | **10-bit** | ~27 Mbps | 3 s 素材约 4 s（**≈0.7× 实时**） |
| `--bitrate 120M` | **10-bit** | ~29 Mbps（硬件编码器上限） | 约 0.5× 实时 |

> `15_LUT烧录工具_20261014/README.md:92-95`

**`watch_bake.py` — 实时烧录**：
```bash
 # A) 卡插在电脑上：卡上一出现新素材就烧
python3 watch_bake.py --lut lut/vlog_to_709_17.vlt --src /Volumes/LUMIX/DCIM --out ~/Pictures/LUT_baked

 # B) 用 LUMIX Sync / 访达 把照片拖进中转目录，拖进来即烧
python3 watch_bake.py --lut lut/vlog_to_709_17.vlt --src ~/Downloads/LUMIX --out ~/Pictures/LUT_baked

 # C) 只跑一遍（cron / 快捷指令）
python3 watch_bake.py ... --once
```
> `15_LUT烧录工具_20261014/README.md:100-107`
- **等文件写完**：连续两次采样 `(size, mtime)` 不变、再静默 `--settle` 秒才动手
- **幂等**：状态文件记录 `(size, mtime)`，同一文件不重复烧
- **风格自检**：先判断素材是不是 Log，若不是会**警告**（`--skip-normal` 可直接跳过）
- **绝不写源目录**，产物只进 `--out`
- **实测**：投放素材 → 检测 → 风格自检 → 烧录完成，**约 5 秒**（`--interval 1 --settle 1` 时）

**`check_style.py` — 判断素材是不是 Log**：
```bash
python3 check_style.py testdata/frame.jpg
```
> **判据**：**V-Log 的黑位是 0.125（≈32/255），永远不会有真黑**；普通风格黑位贴近 0。「是否存在真黑像素」是最稳的单一判据。
> 双向验证：相机直出帧（Standard）→ 🟩 **NORMAL**（91.3% 真黑）黑位 0；同帧反算成 V-Log → 🟦 **LOG**（8/8）黑位 **31**（理论值 31.875）
> `15_LUT烧录工具_20261014/README.md:119-133`

**闭环验证**：
```
原始帧(Standard) ──反算成 V-Log──► 合成 V-Log 帧 ──我们的 LUT 烧录──► 恢复出原始画面
                        │                                          │
                  风格自检判 LOG(8/8)                      画面与原始一致（见 out/）
```
另：`.cube` 与 `.vlt` 两条输入路径的烧录结果**平均像素差 = 0.00**，证明 `.vlt` 解析与轴序处理正确。
> `15_LUT烧录工具_20261014/README.md:141-147`

**重新编译**：
```bash
swiftc -O -module-cache-path "$PWD/.modcache" bake.swift -o bake
```
> `15_LUT烧录工具_20261014/README.md:202`

**复现命令（全部，★ 原样）**：
```bash
cd 15_LUT烧录工具_20261014
PY=/Users/<user>/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3

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
> `15_LUT烧录工具_20261014/README.md:209-229`

**`wifi_lut.py` — WiFi 路径**：
```bash
 # ① 先探路：把 DLNA 的所有 header/body 变体 + get_content_info + 其它读取端点
 #    + SSDP 发现 + 本机挂载卷 全部试一遍，找出真正可用的那条
python3 wifi_lut.py probe --cam 192.168.1.131

 # ② 列出相机上的内容
python3 wifi_lut.py list  --cam 192.168.1.131

 # ③ 实时：轮询新照片 → 下载 → 立刻套 LUT → 落盘
python3 wifi_lut.py watch --cam 192.168.1.131 --lut lut/vlog_to_709_17.vlt --out ~/Pictures/LUT_baked
```
> **注意**：`watch` 模式下不做任何写相机操作，纯 GET + SOAP 查询。`15_LUT烧录工具_20261014/README.md:263-278`

**卡上已写好的东西**（SD 卡根目录 `/Volumes/LUMIX/`，**根目录不是文件夹——官方硬要求**）：
| 文件 | 说明 |
|---|---|
| `VL709.vlt` | V-Log → Rec.709，17³，**VariCam 轴序**（B 变化最快） |
| `VL709A.vlt` | 同上，**另一种轴序**（R 变化最快）——若第一个套上去色偏，用这个 |
| `VL709.cube` | 同上，33³ `.cube` 版 |

> `15_LUT烧录工具_20261014/README.md:14-20`

**内置 LUT 清单（v1.5 `lut/`，9 个）**：
| 文件 | 用途 |
|---|---|
| `vlog_to_709_17.cube / .vlt` | V-Log → Rec.709（17³，与机内同规格） |
| `vlog_to_709_33.cube / .vlt` | V-Log → Rec.709（33³，暗部更准） |
| `vlog_to_709_17_altAxis.vlt` | 备选轴序 |
| `VOL12 TXD FUJI NC P.cube` | 富士 NC 胶片模拟（示例） |
| `VOL19 TXD GLOD 200T V2.cube` | 柯达 Gold 200T 胶片模拟（示例） |
| `GR4-CineG/CineY Plady.cube` | GR4 电影风格（示例） |

> `16_…/S5无线监看_LUT版_v1.5/README.md:66-75`
> 示例 LUT 来自用户提供的 Lightroom 导出文件，仅供演示；请替换为你自己的。

**LUT 串联与强度（v1.5 新增）**：
- **LUT 串联**：V-Log →(还原 709)→ 胶片模拟；**复合成单表零开销**
- **LUT 强度**：0–100% 滑杆，实时调节
- **A/B 对比**：原始画面 / 套 LUT 一键切换
- **已构建过的组合 1 ms 秒切**

> `16_…/S5无线监看_LUT版_v1.5/README.md:48-51, 58`

---

### 2.4 ★ 一键只读审核（审计断言复算）

```bash
cd "/Users/<user>/Documents/ChatGPT/S5_逆向_项目总包_20261012"
bash 14_总包审计与新方向_20261014/01_一键只读审核.sh 2>&1 | tee /tmp/s5_audit.txt
```
> 约 1–3 分钟。**全程只读、不联网、不连相机。** 按 A–I 九段输出：规模、MANIFEST、副本传播、blob 空操作检测、固件偏移判决、档位实测、敏感信息、撤回残留、压缩包盲区。
> `14_总包审计与新方向_20261014/README.md:32-37`、`00_审计总报告.md:609-613`

**九段判读**（`02_全包查看指令手册.md:200-213`）：
| 段 | 核对什么 | 预期 / 判读要点 |
|---|---|---|
| **A** | 文档规模声明 vs 实测 | 声明 864，实测 1,390；四个成果包仍有 13/13/46/462 个文件 ⇒ **"已并库"是假陈述** |
| **B** | MANIFEST 完整性 | 77,504 OK / **5 FAILED**，且集合零差异 ⇒ 清单生成后 12_ 目录被改过（追溯缺口） |
| **C** | 副本传播 | 仅 `25_`/`26_` 号在 10_/11_ 包内为旧版 |
| **D** | blob 校验和 + 空操作检测 | 校验和应全通过；**空操作对会被标出** ⇒ 这就是 S1 |
| **E** | 固件偏移判决 | `+0x200` 命中 7/7，原值 2/7 ⇒ 脚本偏移 bug 确证（S2） |
| **F** | 档位实测 | 库内快照仅 5 mp4 + 1 mp4hevc ⇒ 18/12/10 不可离线复现 |
| **G** | 敏感信息 | 找 `192.168.*`、`70:74:14`、`XJL####`（**但 29 号用 hex 绕过了它**） |
| **H1/H2** | 撤回结论残留 | H1 会列出 22 号报告与工具代码里的旧判据；H2 会命中 `exfat_patch.py:535` 等**活代码提示** |
| **H3** | 压缩包盲区 | 列出 8 个 zip；**普通 grep 扫不到它们内部** |
| **I** | 未提交改动 / 嵌套仓库 | 应只见 `14_总包审计…`；嵌套仓库只有 `12_` |

**判读速查表（项目证据分级惯例，`02_全包查看指令手册.md:442-447`）**：
| 标记 | 含义 |
|---|---|
| ✓ / ✅ | 实机或协议闭合 |
| ◐ | 有证据但未闭合（**多数旗舰结论实际在这一档**） |
| ✗ / ❌ | 证伪或已撤回 |
| ⚠️ | 项目自己标注的"待验证假设" |

---

### 2.5 ★ 总包审计的结论与修复清单

#### 2.5.1 四条旗舰结论的证据链**在审计中不成立**（S 级）

| # | 问题 | 一句话 | 出处 |
|---|---|---|---|
| **S1** | 10-14"受控复测"是**空操作** | 写入 payload 与写入前备份**逐字节相同**（`175604`/`180310` 两对）⇒ 不能证明"写入可持久化" | `00_审计总报告.md:69-98` |
| **S2** | 固件密码学被 **off-by-0x200** 污染 | 改正后明文分区记录 SHA **7/7 命中**，不改仅 2/7；两个密钥搜索脚本对假设**零检验力** | `00_审计总报告.md:102-145` |
| **S3** | "全槽写→回退"的因果被污染 | 反例取自协议修复前的无效跑；而 `06×13` 全槽写的 GOLD blob **恰恰是已持久的那份** | `00_审计总报告.md:149-179` |
| **S4** | "`camsetting` 是 RAM 副本"是**循环论证** | 其唯一实验依赖一个被项目自己撤销的前提 | `00_审计总报告.md:183-192` |

**最危险的一条**：已撤回的判据"相机报错 ⇒ 内存写已执行"**仍活在工具代码的运行路径**里（`exfat_patch.py:535` 等），并在 09 号包的 **7.3 MB zip** 中成体系对外分发——**普通 grep 永远扫不到**。`00_审计总报告.md:16`

**合规问题**：`29 号报告:138` 用 hex 写出完整机身序列号，等于作废全项目的 `XJL########15` 脱敏。`00_审计总报告.md:17`

#### 2.5.2 审计的十项独立复算（R1–R10）

| # | 复算内容 | 结果 | 与项目文档的关系 |
|---|---|---|---|
| R1 | CAMSET 校验和规则 `byte[65532]=(256−Σ[0..65531]) mod 256` | `camsetting.bin` → 0x4d ✅；`blob_GOLD_mov` → 0xd3 ✅；`sum%256==0` ✅ | **印证** |
| R2 | `0x005e` 记录 `3062..3074` 的结构 | 确为 **13 元素数组** + 1 字节 0x00；基线 A=`05×13`、`diff_blob_mov`=`06 05×12`、GOLD=`06×13` | **新增结构证据** |
| R3 | 10-14 复测的 payload vs 备份 | `175604` 与 `180310` 两对**逐字节相同** | **否定** |
| R4 | 固件分区表记录 SHA 的偏移归属 | `doff+0x200` → 明文分区 **7/7**；`doff` → **2/7** | **否定** |
| R5 | 48 分区 type↔IV 统计 | type=2 共 7、type=3 共 41、全零 IV 7 个、唯一 IV 42 | **印证** |
| R6 | MANIFEST 全量校验 | 77,504 OK / **5 FAILED** / 集合零差异 | **新发现** |
| R7 | S5 OSS 内核 `f_fs.c` 审计 | **无** `current_alt_setting`、无松下改动；全树无 exFAT 驱动、无 PTP gadget | **新增 + 重要限定** |
| R8 | 库内 `curmenu.xml` 档位 | 仅 5 个 mp4 + 1 个 mp4hevc `enable=yes`（PAL+mp4 态） | **无法复现** 18/12/10 |
| R9 | 交错验证：err_fw_same 两种解释 | `finalfix.py:20` 说"FLASH LANDED"，`control.py:83` 说"TRANSPORT CLEAN…does NOT flash" | **直接矛盾** |
| R10 | 序列号 hex 解码 | `584a4c####################` = `XJL########15` | **合规泄露确认** |

> `00_审计总报告.md:50-61`

#### 2.5.3 结论可靠性三级分类（对外引用按此分级）

**✅ 可以放心引用**（实机/协议闭合，审计方已复算）——节选关键项：
- UPD 容器结构：512B 头 + **64B 逐版本互异高熵字段@0x220** + 48×92B 分区表 + **512B 尾块**（⚠️ 该 64B 与 512B 是不是「ECDSA P-256 签名」与「RSA-4096 签名」——**无正面依据**）
- `type=2 ⟺ IV 全零`、`type=3 ⟺ IV 非零`，48/48 吻合；41 个 IV 全唯一
- CAMSET blob = 65533 B，831 条 TLV，止于 65528，尾 `ffff0000`
- 校验和 `byte[65532]=(256−Σ[0..65531]) mod 256`，`sum%256==0`
- `videoformat`（字节 3062，记录 `0x005e`）是**唯一**容器门；mov↔mp4 只改这 1 字节（+校验和）
- 菜单变灰 ⇔ 当前值 ∉ `allmenu`；`allmenu` 含 44 个 videoquality（mov 31 + mp4 13）
- CAMSET 写入必须分块 `method=separate`，单次 POST 不落地
- BLE 需**先写身份再读**，无需配对即可读 SSID/密码特征；本机密码为空
- BLE 身份 ≠ Wi-Fi 授权，`cam.cgi` 有独立 accctrl 门
- 相机 SoftAP 为**无密码开放网络**；开放热点 ≠ 开放控制面
- 服务态 USB `04da:2370` 描述符刻画；EP0 双向穷举全 STALL（有正对照）
- ROM BACKUP 门控 = 卡槽 1 + **FAT32**（非"解除初始设置"）
- ROM BACKUP 导出 EEPROM 三区各 128KB；服务模式进入键 = `回放+AF ON+右键`
- PTP length-DoS：可复现挂死、拔插恢复、不砖机
- 6K PHOTO 原生支持、`6k4k_photo` 可写
- 360 个 240 字符长文件名 → 开机反复重启（B vs D 干净对照）

> `00_审计总报告.md:466-485`

**◐ 需重做或降级**（节选）：

| 结论 | 问题 | 应降为 |
|---|---|---|
| "写入 ntsc+mov+0x9b 后三项跨断电保留" | 写入为**空操作**（S1） | ◐ 待重做 |
| **"AES 密钥提取终局否定"** | 密码学实验被偏移 bug 污染（S2） | ◐ 离线希望渺茫（非"终局"） |
| "全槽写会回退，应仅写槽 0" | 反例取自协议修复前的无效跑（S3） | ◐ 假设，非规程 |
| "`getinfo camsetting` 返回 RAM 副本（已独立验证）" | 循环论证，前提已被项目撤销（S4） | ◐ 未证 |
| "18/12/10 档位" | 权威快照未入库（B5） | ◐ 需归档四态 |
| "越界索引处存在 NULL 检查" | 撤回逻辑本身不成立（A7） | ◐ 两种解释均未证实 |
| "UART 死路" | S1R2 类比，S5 P3 从未执行 | ◐ S5 未验证 |
| "只开 80 端口" | 已被热点模式 50001/60606 部分证伪 | ◐ 模式相关 |

> `00_审计总报告.md:509-521`

**❌ 已失效 / 不应再引用**（节选）：
| 结论 | 状态 |
|---|---|
| "S5 内核越界写已实机确认" | 项目已撤回；**但旧表述仍在 22 号报告、09 zip、工具提示中** |
| "堆喷命中越界槽" | 同上 |
| "改 `comm_proto_ver` 绕过版本门" | 已证伪 |
| "网络层 RCE（GoAhead 溢出/LD_PRELOAD/file-op/exec）" | 已证伪 |
| "频繁 invalid login 是漏洞" | 根因是陈旧 pending 请求，非漏洞 |
| "记录 SHA ≠ 存储字节哈希" | 审计 R4 直接反证 |
| "固件升级写路径可用" | 从未见过一次成功 `endsenddata` |

> `00_审计总报告.md:527-534`

#### 2.5.4 最小修复清单（按投入产出比，★ 即"今天就能做"）

| 优先 | 动作 | 类型 | 成本 |
|---|---|---|---|
| 1 | 修 `+0x200` 并重跑密码学脚本，重出 A17/A20–A23 结论 | 代码 | 1–2 小时 |
| 2 | 删除或重打包 `09_…/exfat越界包（…）.zip`；给 `exfat_patch.py:15,535`、`s5_exfat_test.sh:18,121-124`、`TOOLS.md:33`、22 号报告加撤回框 | 安全 | 30 分钟 |
| 3 | 从 `29 号报告:138` 移除 hex 序列号；日志中 `S5-XXXXXX` 打码 | 合规 | 10 分钟 |
| 4 | `persist.py:450` 检查 `requestsenddata` 返回值；`:344` 检查上传返回值；`:334` 增加 no-op 断言 | 正确性 | 30 分钟 |
| 5 | `s5monitor.py`：默认绑 `127.0.0.1`、控制端点加 token、`/api/setting` 加类型白名单、`req_acc` 限频、删 `:1133-1195` 死代码 | 安全 | 2 小时 |
| 6 | 重新生成 `MANIFEST.sha256`（12_ 目录 5 处已漂移） | 可追溯 | 1 分钟 |
| 7 | 25/26 号报告回灌 10_/11_（或改 README 指引），并同步 `11_/00_成果总结_全文.md` | 一致性 | 20 分钟 |
| 8 | 更正 `README.md:74`（并库假陈述）、`:197`（864→1390）、`REPO_CONTENTS.md:7`；目录地图补 `s5_oss_kernel/` | 文档 | 30 分钟 |
| 9 | 三份英文稿 + 小红书稿回填 10-14 更正，或加横幅 | 对外 | 1 小时 |
| 10 | `TOOLS.md` 修正目录名、补第三方依赖清单、加 `--confirm`/风险矩阵 | 文档 | 1 小时 |

> `00_审计总报告.md:648-659`

#### 2.5.5 两条（共五条）应写入项目方法学铁律的建议

项目已有（`REPO_CONTENTS.md:67-70`）：
> ① 没有对照组的结论不要写进报告；② "相机报写入错误"不能当作"内存写已执行"的判据。

**审计建议补充**：
> **③ 任何"写入类"实验，上传前必须断言 `payload != pre_write_readback`；若相等，立即中止并如实记为"无效试验"。**
> **④ 任何依赖结构化二进制偏移的结论，必须附一个"偏移判决实验"：用已知明文/已知校验验证同一偏移模型在多个样本上命中，并在 `TOOLS.md` 登记单一真源（如 `upd_table.py`）。**
> **⑤ 每个"权威结论文件"必须登记它的"判据侧原始数据"在哪。**

> `00_审计总报告.md:625-642`、`03_新方向与实验设计.md:725-740`

**可直接落地的补丁代码**（★ 原样）：
```python
 # persist.py cmd_restore 中增加
if payload == cur:
    log("!! payload == current readback: NO-OP write, experiment invalid. Aborting.")
    sys.exit(2)
```
> `00_审计总报告.md:634-639`

---

### 2.6 ★ 新方向清单（26 个，四梯队）

#### 第一梯队 —— 零设备、零风险、纯离线（**今天就能做**）

| # | 方向 | 状态 | 为什么值得做 |
|---|---|---|---|
| **1** | 修 `+0x200` 后重跑全部密码学脚本 | ✅ **已完成** | 当前"0 命中"对假设**零检验力**；决定"终局否定"是否成立 |
| **2** | **ECDSA P-256 公钥恢复** | ✅ **已完成**（0 收敛） | 90,144 组、1,014 GB 哈希 → 零收敛；「版本字段是否在签名覆盖内」裁决为**不可判定** |
| **3** | **RSA-4096 模数恢复** | ✅ **已完成**（未恢复） | e∈{3,5,7,17,257}×3,620 全排除；e=65537 前 24 高先验 × BE/LE 全排除 |
| **4** | **已知明文扩面** | ✅ **已关闭** | 41 个加密分区 × 13 种均匀模板 + 4 种结构化模板 → **只命中 `ipu_data` 一个** |
| **5** | 写一个**正确的** AES 验证器（CBC 与 CTR 双模型） | 待做 | 硬约束：**全库只有一对已知明文**；须声明**不缩小 2^128** |
| **6** | **用本机 OSS 内核树做离线代码审计** | ✅ **实质关闭** | 771 MB 源码**已在本机**，却被索引漏列；**但已查明那棵树是 DC-FZ1K2 的，不是 S5 的** |
| **7** | **证据链修复** | 待做（需你点头） | 重生成 MANIFEST、回灌 25/26、删/重打包 09 zip、加撤回框 |

> `00_审计总报告.md:544-552`、`03_新方向与实验设计.md:696-702`

#### 第二梯队 —— 低风险（相机只读或纯抓包）

| # | 方向 | 价值 | 关键命令/要点 |
|---|---|---|---|
| **8** | **官方 Tether 在 `0x2382` 抓包复核固件升级帧**（抓到 `startsenddata` 即止） | 唯一能判定"末块失败是相机对所有人都拒绝，还是我们客户端的问题" | 见下方命令块 |
| **9** | 把服务模式 `SCREEN CAPTURE` / `ERR CODE DISP` 当**第三、第四观测面** | 唯一现成的升级手段（**绝不按 `DISP.`**） | 见 §4 |
| **10** | ROM BACKUP 再用 `DSC→SD` 导一次，与 `27 号:85` 的 sha256 逐字节比对 | 唯一能**客观判定**那次误点 `ADJFLAG→ALL F` 是否真改了标志 | — |
| **11** | 热点专属面 `60606` UPnP 与 `50001` 协议指纹 | **未经 accctrl 门**即达（60606 直返 200） | 见下方命令块 |
| **12** | BLE 写身份解锁后**枚举其余只读特征** | 只验证了 idx35/5/6 | 待枚举：`3D22C6BE`/`E1392720`/`A09FAD60`/`054AC621-23`/`69E4D998`/`20F5FFFC` |
| **13** | 修 `SetAlternateInterface` 返回值检查后重跑 USB `--ptp` | 裁决矛盾，成本极低 | `s5_usb_listen.c:142` |
| **14** | PTP `0x9103` 未文档化操作码只读侦察 | 唯一由 fuzz 发现的新操作码 | `python3 04_工具与脚本/ptp/s5_ptp_dump.py --help` |
| **15** | 补做 S5 U-Boot console 离线核验 | ✅ **已完成：S5 上不可判定** | 7 个 type=2 分区 2,490,368 B 搜 17 个关键词 **0 命中** |

> `00_审计总报告.md:569-580`

**方向 8 的确切步骤**：
```text
环境：Windows 11 + USBPcap + Wireshark（或 Linux + usbmon）
步骤：
  1. 相机正常模式（PID 0x2382），启动官方 Tether 2.12
  2. 在 Tether 里选"固件更新"→ 选固件文件 → 只到"开始更新"前的确认页
  3. 抓包，观察并记录：
       · 是否发送 0x9406 子码 0x00090013（FWUP Request，疑先擦除）
       · 0x9605 Get_Event_Info 返回的 {Status, Address, Size}
       · 0x9606 Send_Data_Info 的 [Size][Address][DataType]
       · 分块大小与顺序（对照自建客户端的 61192 / 41456）
  4. ★ 在"开始写入"之前中止，不要真刷
```
> ⚠️ 风险：若让 Tether 真刷，有砖机风险。**抓到 `startsenddata` 即止。**
> `03_新方向与实验设计.md:367-386`

**方向 11 的确切命令**：
```bash
 # 需要 macOS/Linux 接入相机 SoftAP（macOS 已证实可行，见 18:12-14）
curl -s http://192.168.54.1:60606/Lumix/Server0/ddd | head -40
curl -s http://192.168.54.1:60606/ | head
curl -sI http://192.168.54.1:50001/ | head
 # 提示：这是松下的私有 UPnP 实现，可尝试标准 UPnP 描述/控制面
curl -s http://192.168.54.1:60606/desc.xml | head -40
```
> `03_新方向与实验设计.md:445-452`

#### 第三梯队 —— 中风险（需改变相机状态，须 AC 供电 + 健康守卫）

> **共同前置**：AC 电源、电量充足、健康守卫（`getstate` 出 `ok`；重启后 ≤180 s 必须恢复，否则停止）、每次写前备份 blob。`03_新方向与实验设计.md:538`

| # | 方向 | 设计要点（★ 红线） |
|---|---|---|
| **16** | **E1：重做非空操作的持久化实验** | 自变量写入值 A（≠当前值）+ 对照值 B；**每值 ≥3 次独立断电循环**（总 ≥6）；判据①断电后 `camsetting` 三字段②**实拍文件头**（`tkhd/stsd/stts`）③机身菜单截图；**上传前必须断言 `payload != pre_write_readback`** |
| **17** | **E4：分离 RAM 与 flash 的判定实验** | 比较"改值→**不断电**"与"改值→**立即断电**"两条支路；判定：`X==新值 且 Y==旧值 ⇒ getinfo=RAM 副本`；`X==新值 且 Y==新值 ⇒ setsetting 会落盘`；`X==旧值 ⇒ 连 RAM 都不反映，方法学需重写` |
| **18** | **E2：SD 槽挂载 × 开机降档** | **≥3×3**，顺序**随机化并交替**（ABAB/BAAB）；判据 = 开机后 `videoquality` 码值 + **能否实拍**；必须记录每轮 `remaincapacity`、卡型号/速度等级 |
| **19** | **E3：槽形态 `06×13` vs `06 05×12` 的真正因果** | **≥5×5**，随机顺序；**必须用同一已修好的分块协议**；先跑一次对照确认两种形态都能通过 `senddata @61192 ok`；**并正面处理 GOLD（`06×13` 且已持久）这个反反例** |
| **20** | 长名崩溃的**严格阈值实验** | 方案一（推荐）：**固定文件数 360，变名字长度** 12/48/96/144/192/240；额外对照 = **"0xC1 Name 项个数"对照**；每组 ≥2；防护：正常关机再拔卡、接 AC、触发 boot loop 后拔卡 + 格式化恢复；报告须声明每个量的**单位** |
| **21** | CVE-2019-5096 的"版本 + 存在性"两小步 | 步1 版本指纹（非破坏）🟢低；步2 路径确认 🟡低-中；步3 存在性（崩溃）探测 🟠中（**建议在可牺牲机上做**）；步4 堆控 🔴高。**还必须分析：multipart 解析发生在 accctrl 门之前还是之后？** |
| **22** | 在 WPA2 机型复测 BLE 凭据链 | 决定该漏洞的 CVSS 量级 |

> `03_新方向与实验设计.md:540-658`

**E4 实验的完整判定逻辑**（★ 原样）：
```text
支路 A：setsetting 改 quality → 不走写 flash 流程 → 立刻读 camsetting → 记录 X
支路 B：setsetting 改 quality → 立刻拔电池 → 开机 → 读 camsetting → 记录 Y
判定：
  X == 新值 且 Y == 旧值   ⇒ getinfo = RAM 副本（项目结论成立）
  X == 新值 且 Y == 新值   ⇒ setsetting 会落盘（09 号结论成立）
  X == 旧值                ⇒ 连 RAM 都不反映，方法学需重写
```
> `03_新方向与实验设计.md:578-585`

**E1 的补丁代码**（★ 原样）：
```python
 # persist.py  cmd_restore 中，构造 payload 之后、上传之前
if payload == cur:
    log("!! payload == current readback → NO-OP WRITE, experiment invalid. Aborting.")
    log("   要验证持久化，写入值必须与当前状态不同。")
    sys.exit(2)
```
> `03_新方向与实验设计.md:554-560`

#### 第四梯队 —— 高风险 / 需硬件

| # | 方向 | 说明 |
|---|---|---|
| **23** | 拆机只读取证 → UART bootlog → JTAG dump DDR | **顺序很重要**：①只读取证（丝印/测试点照片，零风险先做）②UART bootlog ③JTAG dump DDR。**限定**：A7 有完整 CoreSight，但 **M0 监督核无 CoreSight**，密钥可能在**独立安全芯片** ⇒ **JTAG 能拿到明文，未必能拿到密钥** |
| **24** | 恢复模式（USB）只读入口调研 | `oracle/README.md:88-100` 指出"恢复模式下的固件写入通常跳过签名检查"——这是目前**唯一未被否定**的验证绕过路径。**只做只读枚举，不写固件** |
| **25** | 恶意 USB 主机面（畸形 CBW/CDB） | `05_源码/usb-scsi/` 是 **S1R2 的内核导出**；**前置**：先确认 S5 是否复用同一 gadget（S5 未验证） |
| **26** | chip-off / Crypto Engine 故障注入 / 侧信道 | 唯一能拿"密钥本身"的路。LAB 级、高成本。**建议在方向 23 之后** |

> `03_新方向与实验设计.md:664-688`

#### 不建议继续投入的方向（附 C）

| 方向 | 原因 |
|---|---|
| 扩大语义字典撞库（密码学） | `29:221` 自己指出 S1R2 已穷尽 282 万角度；且**在方向 1 完成前，任何新穷举都会重复生产无效数据** |
| 继续盲试 PTP mode / getinfo 类型 | ~70 候选全部回通用 `err_param`；`16 号` 的"未找到=不存在"已被自己的 `lens` 反例打脸 |
| 改 `comm_proto_ver` 绕过版本门 | 已证伪（字段方向 + 无比较逻辑） |
| exFAT 越界写提权 | 已撤回；且撤回逻辑本身也不成立（A7）。**若重启，先找到不依赖相机屏幕的判据** |
| 无对照地重复末块上传 | 12 次 × 30 s 的连续擦写有写放大风险，且存在循环论证 |
| 把 09 号包的 zip 继续对外分发 | 内含已撤回结论 + 会写坏卡的旧分配器 |

> `03_新方向与实验设计.md:743-752`

---

## 3. 已证伪 / 已排除的路线

### 3.1 监看器相关（从界面移除或明确不支持）

| 路线 | 返回 | 状态 | 出处 |
|---|---|---|---|
| 峰值对焦显示 | `camctrl?type=asst_disp` → **`err_param`** | ❌ 参数格式未找到，**已从界面移除** | `附_技术参考.md:91`、`使用说明.md:87` |
| 放大辅助 | `camctrl?type=change_disp_mag` → **`err_reject`**（值已按官方规范用 300–2000，仍被拒） | ❌ 未找到准入条件，**已从界面移除** | `附_技术参考.md:92`、`使用说明.md:88` |
| **MF 模式下触摸对焦** | — | ❌ 相机设计如此，请改用「焦点近/远」按钮 | `使用说明.md:81` |
| **提高画质（>640×432）** | `startstream` 接口只有端口参数、**无画质选项** | ❌ **640×432 是相机硬上限**；要全画质监看只能走 HDMI + 采集卡 | `README.md:73`、`使用说明.md:92` |
| **用 BLE 提升画质** | 带宽仅 KB/s 级 | ❌ 仅用于配对/唤醒 | `使用说明.md:95` |
| **`adaptive` 节奏模式** | — | ❌ 不推荐（追相机速率会被抽干） | `README.md:36` |

### 3.2 LUT 相关

| 路线 | 为何不可行 | 出处 |
|---|---|---|
| **机内实时烧录 LUT**（像 S5II 那样） | 功能层/管线层/可达层三重关闭 | `15_LUT烧录工具_20261014/README.md:236-243` |
| **通过 Wi-Fi 上传 LUT** | `startsenddata` 的 `type` 只有 `camsetting` 与 `fw`；三条独立取证一致 | `09_LUT可行性报告_20261014.md:30, 214-225` |
| **菜单注入**（把 LUT 项加进 allmenu） | 菜单树**由固件提供**，不在 65533 B 的 `camsetting` blob 里；对 blob 的所有写入**从未改变 allmenu 任何条目** | `09_LUT可行性报告_20261014.md:98` |
| **固件改写 / 跨代移植** | 三重门同时关闭：① AES 密钥在 MC801 片内 ② 签名硬门 ③ 升级写路径**从未成功过一次 `endsenddata`**（末块 41456 B 定址失败 ~31 s → `err_busy`/`err_critical`）。且 MC801（32 位 A7）与 S5II 的 SC2006A（4×A53）**跨代** | `09_LUT可行性报告_20261014.md:99` |
| **`/AD_LUT/` 目录** | 官方三处一手文档均要求**卡根目录**；该说法不成立 | `09_LUT可行性报告_20261014.md:264-278` |
| **ffmpeg 生成 `.vlt`** | `lut3d` 滤镜**不支持 `.vlt`** | `09_LUT可行性报告_20261014.md:384` |
| **拆机 JTAG 为了 LUT** | 即使 dump 到明文，也只能**知道**有没有，不能**打开**它 | `09_LUT可行性报告_20261014.md:145-147` |

### 3.3 项目级已证伪路线

| 路线 | 状态 | 出处 |
|---|---|---|
| **S5 内核越界写已实机确认** | ❌ 项目已撤回；**但旧表述仍在 22 号报告、09 zip、工具提示中** | `00_审计总报告.md:527` |
| **堆喷命中越界槽** | ❌ 已撤回 | `00_审计总报告.md:528` |
| **改 `comm_proto_ver` 绕过版本门** | ❌ 已证伪（**但见补充：其前提「版本字段被签名覆盖」同样无正面依据**） | `00_审计总报告.md:529` |
| **网络层 RCE**（GoAhead 溢出/LD_PRELOAD/file-op/exec） | ❌ 已证伪 | `00_审计总报告.md:530` |
| **频繁 invalid login 是漏洞** | ❌ 根因是陈旧 pending 请求，非漏洞 | `00_审计总报告.md:531` |
| **记录 SHA ≠ 存储字节哈希** | ❌ 审计 R4 直接反证 | `00_审计总报告.md:532` |
| **固件升级写路径可用** | ❌ 从未见过一次成功 `endsenddata`；`finalfix.py` 的"FLASH LANDED"判据已被 `oracle/README` 否定 | `00_审计总报告.md:534` |
| **S5 5.9K 片门全开** | ❌ 四变量全覆盖（制式×模式×重试×命名族）全部失败；实拍 `P1000004.MOV` = **4096×2160 @59.94fps** = C4K 60p，非 5888×3312 | `00_项目总结/02_项目时间线.md:223-232` |
| **exFAT 越界写** | ❌ 判定不成立，不再投入 | `00_项目总结/04_定因与工具链成果_20261013.md:164` |
| **BLE 读取 Wi-Fi 凭据（未加密链路）** | ❌ 相机对未加密链路**拒绝读并断链**；该安全结论已撤回 | `00_项目总结/03_思路总结_全文.md:171-173` |
| **菜单项注入** | ❌ 已证伪（allmenu 由固件提供，S5 无 My List 机制） | `00_项目总结/03_思路总结_全文.md:126-127` |
| **"flash 存安全值 + RAM 上隐藏档"双轨方案** | ❌ 实测证伪（菜单读的是 RAM 值，不是 flash 值） | `00_项目总结/02_项目时间线.md:259` |
| **USB mass-storage 路线可拍摄** | ⚠️ 该模式下相机通常**不能同时拍摄**，属"拍完接线批量" | `10_仓库补丁/定因与交接_20261014.md:161` |

---

## 4. 已知陷阱与危险操作（血泪教训逐条）

### 4.1 🔴🔴 `req_acc` 频率保护 —— 会封禁相机（必须断电重启）

**机制**：
```
短时间多次 req_acc  ⇒  相机屏幕显示「智能手机应用程序需要更新」
                    ⇒  invalid login
                    ⇒  **必须断电重启相机**（只能这样恢复）
```
> 症状：所有端点开始返回 `err_reject` / `err_unsuitable_app`，`startstream` 被拒（画面完全不动）。
> `12_S5无线监看_v1.0_20261014/README.md:211-221`

**亲历记录**（排查中把 `ensure_access` 改成「每 10 秒重发一次 req_acc」后）：
```
相机屏幕显示：
    「智能手机应用程序需要更新」
        ↓
    invalid login
        ↓
    要求重启相机
```
> **⇒ 相机把"短时间内大量连接请求"判定为异常/过旧的 App，直接封禁。**
> **⇒ 只能靠断电重启恢复。**
> **⇒ 正确做法：`req_acc` 只在启动时发【一次】，之后只轮询 `getstate`。**
> `附_技术参考.md:139-154`

**另更正一个误区**：相机**不会弹出任何授权对话框** —— 全程是相机内部自己校验。`附_技术参考.md:156`
> ⚠️ 但 `启动_含LUT.command` 仍提示「请【盯着相机屏幕】：若弹出「允许连接？」请按【允许】」，`定因与交接_20261014.md:153` 也说"应弹「允许连接？」→ 按【允许】"。**这是矛盾，见 §6.7。**

**审计方的操作教训**：用**自造 UUID** 发起了 `req_acc`，之后又用项目既有 ID 重发，导致 `accctrl` 状态在 `err_others_requesting` → `ok_under_research` → `err_user_refused` 之间反复跳。`10_仓库补丁/定因与交接_20261014.md:120-125`

### 4.2 🔴 三条必须遵守的规则（监视器版）

| # | 规则 | 原因 |
|---|---|---|
| 1 | **`req_acc` 只在启动时发一次**，之后只轮询 `getstate` 心跳保活 | 心跳就是会话保活机制；多发 `req_acc` 会触发频率保护 |
| 2 | **会话拿到 `ok` 后不要重启本服务** | 重启 = 重新请求 = 需重新批准，且累积触发保护 |
| 3 | **清理陈旧 pending 必须用同一 UUID**，且 `err_others_requesting` 时不要清理 | 相机端只有一个"待批复"槽；用错 UUID 或误伤他人请求都会污染状态 |

> `12_S5无线监看_v1.0_20261014/README.md:225-229`

### 4.3 🔴 三条铁律（UUID / 清理时机 / 不用新 UUID）

1. **永远只用监视器自己那一个 UUID**：`4D454930-0100-1000-8001-020A0003BD13`
2. **绝不在启动时发 `req_acc_can`** —— 清理只在【结束】时做
3. **绝不用新 UUID / 匿名请求做调试**

> `12_S5无线监看_v1.0_20261014/README.md:483-485`

**为什么（相机维护"已注册设备表"）**：

| 请求 | 结果 |
|---|---|
| 已注册 UUID | ✅ 直接受理（`ok` / `ok_under_research_no_msg`） |
| **全新 UUID** | ❌ 创建"待批复"请求 ⇒ 之后**所有**请求都看到 `err_others_requesting` |
| **匿名（不带 `value`）** | ❌ 同上，同样污染 |

> 相机端**只有一个"待批复"槽**。一次没被清理的新请求会**卡住整个会话**，而且症状很迷惑（`err_others_requesting` 看起来像"别的设备在连"，其实可能只是自己刚才的调试请求）。
> `12_S5无线监看_v1.0_20261014/README.md:487-496`

**实测佐证（★ 本次核查代码发现，比文档更明确）**：`s5monitor.py:273-279` 注释原文——
> 「★ 启动时【绝不】发 `req_acc_can` —— 项目 `safe_handshake.py` 的实战结论：清理只在【结束】时做。启动时紧跟 `req_acc` 的 can 会让相机把它当成"第二个请求者" ⇒ `err_others_requesting` ⇒ 会话建立不起来。（实测 2026-10-14：加了启动清理后，热点模式下 **90 秒都拿不到 ok**；去掉后单次 `req_acc` 直接拿 `ok`。）」

### 4.4 🔴 绝不用裸 `curl` 直接访问相机

```bash
 # ❌ 危险：不带 value（UUID）的 req_acc 会留下**匿名 pending**，
 #          之后监视器带正式 UUID 请求时会撞上它 ⇒ err_others_requesting
curl "http://<相机>/cam.cgi?mode=accctrl&type=req_acc"
```
> 相机的访问控制是**按客户端身份**的，**同一个时刻只有一个身份能用**：监视器持有 `ok` 时，裸 `curl` 一律返回 `err_unsuitable_app`（**这是正常的，不是故障**）。
> ⇒ **所有操作都走监视器的 HTTP API（8080），不要绕过它直接打相机。**
> `12_S5无线监看_v1.0_20261014/README.md:231-241`

### 4.5 🔴 三条安全规则（清理 pending 时）

1. 清理**必须用同一 UUID**；
2. `err_others_requesting` 时**不要清理** —— 那是别人占着会话，误伤他人请求；
3. **绝不用 `req_acc_can` 去打断一个已 `ok` 的会话**；也绝不快速连发 `req_acc`。

> `10_仓库补丁/定因与交接_20261014.md:268-272`

### 4.6 🔴 性能教训：实时 LUT 必须在**真实分辨率**上测

**踩坑原文**：
> 本项目曾用 **320×240 合成图**测出 20–26 ms，就以为 18 fps 够用；但真实取景流是 **640×360（3 倍像素）**，实测 **73–160 ms/帧**，远超 **55.6 ms** 预算 ⇒ 队列空、反复重播上一帧 ⇒ **画面看起来完全卡死**。

**修复**：把 N³ 浮点 LUT 预计算成 **256³ uint8 精确查表**（输入是 8-bit JPEG ⇒ 颜色空间只有 256³ 种取值，一次预计算即可消除逐帧插值，结果与原逐帧三线性**逐位等价**，已用全色域随机图 + 8 个角点验证，最大差 0）。

| | 逐帧三线性 | 256³ 查表 |
|---|---|---|
| 单帧耗时（640×360） | 73–160 ms | **6.7 ms** |
| 吞吐影响 | 卡死 | **零损失**（17.4 → 17.8 fps） |
| 构建耗时 | — | 4.7 s（一次性，select 时） |
| 内存 | — | 50 MB |

> `12_S5无线监看_v1.0_20261014/README.md:254-271`

### 4.7 🔴 `.cube` 轴序 bug（R 变化最快 vs numpy C-order）

> **踩过的坑（已修）**：`.cube` 规范是 **R 变化最快**，而 numpy 的 C-order reshape 让最后一个下标最快 ⇒ 直接 `reshape(N,N,N,3)` 得到的是 `[b,g,r]`，必须 `transpose(2,1,0)`。
> 该 bug 由"`.cube` 与 `.vlt` 结果必须一致"这条验收标准抓出。
> `12_S5无线监看_v1.0_20261014/README.md:133-135`

### 4.8 🔴 相册与取景互斥（卡顿的真相）

**现象与定因**：用过「列举相机内容」后，实时取景出现明显卡顿（诊断面板显示相机侧空档 700–880 ms）。

**定因（三层）**：
1. **取片的必要条件**：DLNA 内容树**只在回放模式下有内容** ⇒ 列举必须先切 `playmode`
2. **回放模式下没有实时取景** ⇒ 相机只会零星推帧 ⇒ 画面卡顿
3. **原实现切过去就不管了** ⇒ 相机一直停在回放模式 ⇒ 取景持续卡顿

**修复**：`/api/gallery` 与 `/api/download` 办完会在**后台线程自动 `camcmd recmode`** 切回拍摄模式（`?restore=0` 可关闭）。

> `12_S5无线监看_v1.0_20261014/README.md:358-373`
> ⚠️ 回放模式下**没有实时取景**（DLNA 内容与取景流互斥）。看完相册想回到监看，点界面上的「拍摄」按钮即可。`README.md:352-353`

### 4.9 🟡 诊断面板的 `max_camera_gap_ms` 是**累计值** —— 会误导

> **★ 怎么正确判断"是否还在卡"**：诊断面板的 `max_camera_gap_ms` 是**累计值**——它会把「流重启时的一次 10.7 秒空档」和「回放模式期间的零星推帧」永远算在里面，**看起来像是一直没修好**。**应看近期窗口，别信累计最大值**：

```bash
 # 每 250ms 采一次帧计数，连采 20 秒
python3 - <<'EOF'
import urllib.request, json, time
def st():
    with urllib.request.urlopen("http://127.0.0.1:8080/api/state", timeout=5) as r:
        return json.load(r)
prev = st()['frames']; t0 = time.time(); s = []
while time.time() - t0 < 20:
    time.sleep(0.25); f = st()['frames']; s.append(f - prev); prev = f
run = mx = 0
for x in s:
    if x == 0: run += 1; mx = max(mx, run)
    else: run = 0
print(f"{sum(s)/20:.1f} fps   空窗口 {sum(1 for x in s if x==0)}/{len(s)}   最长空档 {mx*0.25:.2f}s")
EOF
```
> **健康标准**：18 fps 左右、250 ms 窗口均匀 4–5 帧、空窗口 0、最长空档 0.00s。
> `12_S5无线监看_v1.0_20261014/README.md:375-400`

### 4.10 🟡 SSDP 公布错误的网卡地址（真 bug，已修）

```python
s.connect(("192.168.1.1", 80))     # ← 写死了家庭路由器
```
> 本机同时有有线（家网 `192.168.1.x`）与无线（相机热点 `192.168.54.x`）时，它会公布 `192.168.1.148` —— **相机在热点网段根本够不到**，表现为：**相机能看到我们的 SSDP 广播，却始终连不上（卡在"选择设备"）**。
> **已改为按【相机地址】探测路由**（热点优先、家网兜底）。实测公布地址由 `192.168.1.148` → `192.168.54.10`（相机可达）。
> `12_S5无线监看_v1.0_20261014/README.md:498-511`

### 4.11 🟡 链路质量是外部因素（软件层无法根治）

> 实测到**路由器** RTT 3.6/5.4/16.0 ms（stddev **2.8 ms**，极稳），到**相机** RTT 7.4/232/743 ms（stddev **254 ms**）⇒ 抖动来自**相机侧无线链路**。
> 相机是 **2.4GHz-only**，若与路由器距离远/隔墙，取景帧率会明显下降——这属于环境因素，软件层无法根治（可用 `--pacing-fps` 调低目标帧率让节奏更稳）。
> 顺带排除：ClashX 代理的 `ExceptionsList` 含 `192.168.0.0/16`，**局域网流量绕过代理**，与本问题无关。
> `12_S5无线监看_v1.0_20261014/README.md:402-409`

### 4.12 🔴 LUT 使用前提：照片风格必须匹配

| 相机照片风格 | 该用的 LUT | 用错的后果 |
|---|---|---|
| **V-Log** | `vlog_to_709_*.cube/.vlt` | — |
| Standard / 其它 | **不要套 V-Log LUT** | 变暗、过饱和 |

> 判据：**V-Log 黑位 ≈ 32/255 且绝无真黑**；普通风格黑位贴近 0。`s5_get_photo.py` 会自动判定并在不匹配时警告。
> `12_S5无线监看_v1.0_20261014/README.md:437-445`

**实测数据（把 V-Log LUT 套到非 Log 素材上）**：
| | 均值 | P50 | P99 |
|---|---|---|---|
| 原始帧（Standard，夜景） | 9.0 | 1.0 | 204 |
| 套 VLog→709 后 | **6.5（更暗）** | 0.0 | 224 |

> `15_LUT烧录工具_20261014/README.md:156-158`

### 4.13 🔴 卡上写 LUT 后的 macOS 副作用

> 卡上写 LUT 后：macOS 会生成 `._*` 资源分叉——**已清理**。若你再次插拔卡，建议插回相机前确认根目录没有 `._*` 与 `.fseventsd`。`15_LUT烧录工具_20261014/README.md:179`

### 4.14 🔴 拔插 SD 卡必须在相机里正常关机后

> ⚠️ **拔插 SD 卡必须在相机里正常关机后**（项目红线 `25:20`）：相机分配位图延迟写回，直接拔卡会让位图停在旧状态。
> `09_LUT可行性报告_20261014.md:125`

**工具曾把卡写坏的完整记录**：
```
根因：alloc_one_cluster() 只信分配位图；
      而相机位图【延迟写回】——未正常关机就拔卡，位图停在旧状态
后果：分配器拿到【照片正在使用的簇】→ 清零 + 断链 + 目录链拐进数据区
症状：照片"文件在、但无法访问/无法删除"
证据：FAT[39] 被改成 482（照片本该 39→40→…→115）
```
**修复**：分配簇改为**三重校验** —— `位图位==0` **且** `不在目录链上` **且** `FAT[clu]==0`。

**由此产生的两条硬规矩**：
1. **拔 SD 卡前必须在相机里正常关机**（让位图落盘）
2. **每次写卡前后都必须跑 `checkalloc`**，`K > 0` 立即停手

> `00_项目总结/04_定因与工具链成果_20261013.md:85-98`

### 4.15 🔴 `a6k` 家族会**静默改容器** —— 禁用

> `a6k` **不止"忽略"**：实测会把 `videoformat` 从 `mov` **静默改成 `avchd`**（`videoquality` 变成 `avchd_50p_28mbps`）——**不报错、只改状态**。
> ⇒ **禁用该家族**。恢复：`setsetting videoquality=mov_60p_200mbps_4k_10bit`（同时把容器带回 mov）。
> `00_项目总结/02_项目时间线.md:110-113`

### 4.16 🔴 服务模式：绝不要按 `DISP.`

> ⛔ 绝对不要按 `DISP.`：`13:247-248` 会解除 `[Strict]`，**地区后缀一次性锁死，不可逆**。
> `03_新方向与实验设计.md:408`
> ⛔ 红线（`27:152`）：绝不碰 `SD→DSC` / `ADJFLAG` / `WBADJ` 等写回方向。`03_新方向与实验设计.md:431`
> 退出前必须先拔掉卡槽 1 的 FAT32 卡（`13:228-230`）。`03_新方向与实验设计.md:406`

### 4.17 🔴 改制式通常要求格式化存储卡

> 补齐另外三态 `curmenu` 需 `setsetting` 改 `ntsc_pal`/`videoformat`（写操作）；**改制式在松下机身上通常要求格式化存储卡**；项目实测 `ntsc_pal` 会持久化到 flash。可逆性中等，须先确认卡内无待保留素材。
> `08_实机与离线验证记录_20261014.md:190`

### 4.18 🔴 `cammode=play` 时视频域写操作全部无效

> `cammode=play` 时所有视频域 `setsetting` 一律 `err_param`，**且已回 `ok` 的调用也不生效**。
> 相机当前正是 `play` 模式 ⇒ **任何视频域写实验前，必须先 `camcmd&value=recmode` 切到拍摄模式**——这是一个额外的状态变更步骤，需纳入实验设计与授权范围。
> `08_实机与离线验证记录_20261014.md:263-265`

### 4.19 🟡 机身停在菜单界面时 `getinfo camsetting` 回 `err_reject`

> 另一条操作坑：**机身停在菜单界面时 `getinfo camsetting` 回 `err_reject`**（其它 getinfo 正常），退出菜单即恢复；`download_blob` 已加提示。
> `00_项目总结/02_项目时间线.md:101-102`
> （另见 `01_成果总表.md:11`、`00_执行摘要_全文.md:106`）

### 4.20 🟡 `ok` ≠ 生效（当天 ≥6 次反例）

> **`ok`**：请求被接收，⚠️ **≠ 生效**，必须回读 `getsetting videoquality` 确认（当天 **≥6 次反例**）。
> `00_项目总结/02_项目时间线.md:267`
> 铁律：`setsetting` 返回 `ok` **不等于**生效。所有格式类结论必须以**实拍文件头**（`tkhd`/`stsd`/`stts`）或**断电后读回**为准。`00_项目总结/03_思路总结_全文.md:58-59`

### 4.21 🟡 空操作陷阱：写入 payload 与写入前备份相同

> 两个备份在**写入前**就已经是 `65230=0x00(ntsc)` / `3062=0x06(mov)` / `6986=0x9b`，槽形态也已是 `06 05×12`。
> ⇒ 报告 §3.2 用**槽形态 `06 05×12`** 作为"写入已落地"的签名，但该形态在写入前的备份中**已经存在**，因此它对"是否写过"**零信息量**。
> `00_审计总报告.md:79-83`

**项目自己已识别的同类坑（5.9K 那次）**：
> 本轮落盘文件 `out/quality_payload_mov_30p_200mbps_5_9k_10bit_20261013_024240.bin` 与同批次 `out/backup_pre_quality_20261013_024240.bin` **逐字节相同**（cmp 验证，均 65,533 B）⇒ 那次"5.9K 写入"是**空操作，从未真正改过码字节**。**后人不要因为 `out/` 里存在这个文件名就以为"5.9K 已经试过了"**。
> `00_项目总结/02_项目时间线.md:118-121`

### 4.22 🟡 `grep "endsenddata -> ok"` 会命中**无相机模拟**行

> `logs/写路径/campaign.md` 里同时有真机运行与 `# BENCH (pure Python, no camera)` 的**无相机模拟**，两者的输出格式一样。**`grep "endsenddata -> ok"` 会命中模拟行**，从而误判"曾经刷写成功"。
> `02_全包查看指令手册.md:183, 190`

```bash
grep -n "BENCH" 01_研究报告/02_研究总报告_20261011/logs/写路径/campaign.md | head
grep -n "endsenddata -> ok" 01_研究报告/02_研究总报告_20261011/logs/写路径/campaign.md | head
```
> 判读：把两者对照，**确认"ok"是否紧跟在 BENCH 之后**。

### 4.23 🟡 压缩包是 grep 的审计盲区

> **审计盲区**：这些内容在 zip 二进制里，`grep --include=*.md` 类的全仓一致性检查**永远扫不到**。
> `00_审计总报告.md:238`

```bash
cd "/Users/<user>/Documents/ChatGPT/S5_逆向_项目总包_20261012"
Z="09_exFAT越界写成果包_20261013/exfat越界包（有风险非专业人员请勿轻易尝试.zip"
unzip -l "$Z" | head -20                          # 看条目结构
unzip -p "$Z" "*/00_成果总结_全文.md" | head -8    # 看是否含已撤回结论
unzip -p "$Z" "*/02_工具链/exfat/exfat_patch.py" | sed -n '741,756p'  # 看是否是旧版分配器
```
> `02_全包查看指令手册.md:229-234`

### 4.24 🟡 MANIFEST 追溯缺口

```bash
shasum -a 256 -c MANIFEST.sha256 | grep FAILED
```
> 输出 5 条，**全部集中在一个目录**：`12_S5无线监看_v1.0_20261014/` 的 `README.md`、`run.sh`、`使用说明.md`、`启动.command`、`附_技术参考.md`。
> 时间线：MANIFEST `19:32:01` → 这 5 个文件 `19:35:12–17`。
> ⇒ **这不是数据损坏，而是追溯缺口**：用 MANIFEST 校验会报错。应重新生成清单。
> `00_审计总报告.md:337-343`

### 4.25 🟡 环境层两个坑

**① 第三方 App 抢占 USB 设备**：
> 夸克网盘（`QuarkCloudDrive`）曾在相机 USB 设备上挂了 `IOUserClient`（`ioreg` 里可见 `IOUserClientCreator`），导致 PTP 完全无响应。
```bash
ioreg -w0 -l -r -n DC-S5 | grep IOUserClientCreator
```
> `00_项目总结/05_环境与依赖.md:126-128`

**② macOS 原始磁盘设备访问的双重保护**（exFAT 实验必需）：

| 层 | 事实 | 后果 |
|---|---|---|
| **Unix 权限** | `brw-r----- root operator` | 普通用户直接 `Permission denied` |
| **TCC** | 原始磁盘访问还需**「完全磁盘访问」** | 即使用 `osascript ... with administrator privileges` 拿到 **uid=0**，仍报 `Operation not permitted` |

> ⇒ **自动化/AI 进程两条路都过不去**，这些命令**必须由人在终端里 `sudo` 执行**。
> 另一个 TCC 陷阱：`osascript` 提权后的 root shell **访问不了 `~/Documents` 等受保护目录**（报 `Operation not permitted (126)`）—— 所以脚本要放到 **`/tmp`** 之类不受保护的位置再执行。
> `00_项目总结/05_环境与依赖.md:135-161`

**③ 免密 sudo / Wireshark 不可用**：
> `tcpdump`（**需要 sudo**，本会话无免密 sudo → 未使用）；Wireshark/dumpcap/tshark ❌ 未安装。
> `00_项目总结/05_环境与依赖.md:67, 83`

### 4.26 🟡 ffmpeg 不可用（坏 bottle）

> 本机 ffmpeg 不可用：`/opt/homebrew/Cellar/ffmpeg/9.0.1_1/bin/ffmpeg` 的 install_name 里 `@@HOMEBREW_CELLAR@@` 未替换（坏 bottle），且 `/opt/homebrew` 非当前用户所有 ⇒ **本工具全程不依赖它**。
> `15_LUT烧录工具_20261014/README.md:177`
> **替代方案**：`ffprobe` ❌ **崩溃**（`Symbol not found: _av_bprint_finalize`）⇒ 自写 Python 解析 MOV/MP4 box（`tkhd`/`stsd`/`stts`/`stss`）。`00_项目总结/05_环境与依赖.md:78`

### 4.27 🟡 服务模式的未决风险事件（ADJFLAG→ALL F）

> `27 号:162-176` 记录了一次**真实的误操作**：菜单被依次点到第 2–7 项（含 `ADJFLAG→ALL F`）。现有"验证"只是"重启后功能正常"的**主观判断**。唯一能**客观判定**的方法是：再导一次 EEPROM 三区，与 `27 号:85-87` 记录的 sha256 逐字节比对。
> `03_新方向与实验设计.md:420-435`

### 4.28 🔴 项目安全红线（总）

- 常接 AC 电源；相机极易砖，恢复靠拔电池。
- **绝不真刷固件**；绝不 `resetDevice`；绝不执行 PTP 配置写回（`0x9422/0x9423`）/ `0x9406` 带副作用子码。
- 每次写后健康守卫（`getstate→ok`；重启后 ≤180s 内必须恢复，否则停止）。
- flash 写入必须 AC 供电。
- 服务模式只读（不动 ROM WRITE / ADJUST / REGION / 初始设置）。
- `4kcrop` 不碰。
- 读 camsetting 前退出机身菜单。

> `00_项目总结/00_执行摘要_全文.md:154-158`、`00_项目总结/03_思路总结_全文.md:212-217`、`02_全包查看指令手册.md:14-18`

### 4.29 🟡 监看器的安全面（审计 A5 —— 交付/分享前须处理）

| 问题 | 位置 | 说明 |
|---|---|---|
| 绑定 `0.0.0.0` | `s5monitor.py:1036,1143`（HTTP）、`:398`（UDP） | 默认对局域网/相机热点全网开放 |
| **无任何认证** | `/api/cmd`、`/api/ctrl`、`/api/mode`、`/api/stream`、`/api/setting`、`/api/info` | 无 token、无会话 |
| 控制端点全是 **GET** | `s5monitor.py:771,782,908,923,937`；`do_POST` 仅转发 | 同网段任意网页可用 `<img src="http://host:8080/api/cmd?value=capture">` 触发拍照/录像/改设置（**CSRF**） |
| **白名单被绕过** | `ALLOWED_CAMCMD`/`ALLOWED_CAMCTRL`（`:83-105`）只守 `camcmd`/`camctrl`；`/api/setting`（`:937-943`）直接调 `setsetting`（`:195-196`） | 与 `README.md:100`/`使用说明.md:154`/`附_技术参考.md:173` 声称的"代码内置白名单，永不发送有副作用的命令"**直接冲突** |
| 前端 XSS 面 | `www/index.html:475,496,516,523,531` 用 `innerHTML` 拼接相机原始回复 | 与无认证叠加提升风险 |

> **未发现命令注入**（全仓无 `shell=True`/`os.system`；仅 `lsof` 以列表参数调用）——这条是干净的。
> `00_审计总报告.md:256-267`
> ⛔ **不要运行** `s5monitor.py`（除非你已改绑 `127.0.0.1` 并加了 token）。`02_全包查看指令手册.md:370`

**⚠️ 但审计的 `req_acc` 指控是错的** —— 见 §6.1（★ 本次代码核查）。

---

## 5. 未解决 / 开放问题

### 5.1 相机行为层

| # | 开放问题 | 现状 | 判定路径 |
|---|---|---|---|
| O1 | **ObjectID 根对象是什么** | `701 No such object` 说明 Panasonic LumixLink 内容树的根对象**不是标准 UPnP 的 `"0"`**；官方 App 的 ObjectID 由调用方传入（`p154t5/a.java:209 l(str, ip, count)`、`DlnaWrapper.h(objectID, ...)`），反编译里未见字面量常量 | `python3 s5_content.py sweep --cam <ip>`，`CANDIDATE_OBJECT_IDS` 已内置 16 个候选（`0/1/2/3/4/10/100/Lumix/LumixLink/DCIM/100_PANA/...`）。判据：**返回条目** 或 **错误码 ≠ 701** 即为命中 |
| O2 | **相机的 DMS 开关是否需要手动启动** | APK 里有 `"DMS Enabled"/"DMS Disabled"/"DMS Enabled When AppStarted"/"DMS Disabled:For Camera"/"DMS StateWatch"` ⇒ DLNA 媒体服务器**可被相机侧开/关**，App 只做状态监视 | 若 `sweep` 扫完仍无命中，应考虑 **DMS 未启动**（内容树为空 ⇒ 任何 ObjectID 都 701）。候选排查：相机菜单里的 Wi-Fi → 发送图像 / DLNA 相关项是否需要手动进入 |
| O3 | **「一边录制一边发送图像」是否生效** | 待测 | 跑 `s5_selfcheck.py`；判据见 §2.1.7 |
| O4 | **33³ `.vlt` 机身能否读入** | 待实机确认 | 记录：能否识别 33³？能列几个 LUT？ |
| O5 | **`.vlt` 轴序（哪个通道变化最快）** | 官方 `.VLT` **不声明轴序** | 看取景画面是否色偏；偏了换成 `VL709A.vlt`（另一种轴序） |
| O6 | **`[V-Log View Assist]` 下有没有 `[LUT View Assist (Monitor)]` / `[LUT View Assist (HDMI)]` 两个开关** | **唯一还需确认的点**；若有 HDMI 开关 ⇒ HDMI 输出即"已套 LUT" ⇒ 外接录机可录到**烧录版** | 直接在菜单里看 |
| O7 | **S5 是否有自己的 OSPO 页** | 本次未能确认（harness 无法访问 `ospo.panasonic.com`） | 人工用浏览器访问 `https://ospo.panasonic.com/oss/dsc/` 索引页，查是否存在 `DC-S5` 条目 |
| O8 | **USB PTP 直写 LUT 是否存在可写 tag** | `Lumix-Fast`(Android) dex 字符串池含 `实时 LUT`/`LUT Base Photo Style`/`LUT不透明度` 等，但**无法做方法级归因**（无可用 JRE，jadx 跑不起来） | 需 JRE + jadx/baksmali，在 `/tmp` 解一次，定位 const-string 使用点及邻近的 `0x0?xxxxxx` tag 常量。**唯一尚未排除的"USB PTP 直写 LUT"候选路径** |
| O9 | **`0x005e` 槽形态 `06×13` vs `06 05×12` 的真正因果** | 反例 n=1 / 正例 n=2，**因果未确立**；且 GOLD（`06×13`）恰恰是已持久的那份 | E3 实验：≥5×5，随机顺序，同一已修好的分块协议 |
| O10 | **`videoquality` 保留与 SD 槽 1 挂载状态的机制** | **仅 1 组对照，待重复实验确认**（T1 槽1 unset ⇒ `0x9f` 降档；T2 槽1 set ⇒ `0x9b` 保留） | E2 实验：≥3×3，顺序随机化并交替 |
| O11 | **「存在比 `allmenu` 更严格的第二层过滤」的位置** | `mov_30p_200mbps_5_9k_10bit` **在 allmenu 里**却仍 `err_reject` ⇒ `∈allmenu` 只是"菜单不变灰"的**必要**条件，不是"设置器接受"的**充分**条件。（`capability.xml` 完全不含 5.9K/6K 字样，该层位置待定） | 未给出路径 |
| O12 | **CBC vs CTR 判定** | 当前静态数据**不可判定** | 需要密钥、或同一 (key, IV) 下**明文被改动过**的第二份密文、或运行时 DDR 明文。**不要再从密文统计量上尝试** |
| O13 | **外层头是否被带密钥签名覆盖** | **不可判定**（离线） | 唯一能终结的路径需要容器外信息：拿到 BootROM/OTP 内的公钥后把 `recover` 换成 `verify`（单次验签 <1 ms），或从 UART bootlog 看有无验签告警 |

### 5.2 固件/硬件层

| # | 开放问题 | 现状 |
|---|---|---|
| O14 | **固件升级末块为何失败** | 能干净流送全部 1474 个完整 61192B 块，但**最终部分块（41456B）始终失败**：触发 ~31s flash 定址 → `err_busy`（慢）→ 重试 `err_critical`（快）。与内容/节奏/状态均无关。**从未用官方 Tether 做过对照** |
| O15 | **三个替代解释未排除** | ① **SD 卡状态**：fwup 实验**从未把 SD 卡当受控变量**（ROM BACKUP 已被证实由 FAT32 门控）② **缺 erase 步骤**：PTP 侧需 `0x9406/0x13`，CGI 侧从未发送 ③ **块对齐**：`chunk=61192` **不是 512 的倍数**（119.5）；总长是 512 倍数但**不是 128 KiB 倍数**（688.46） |
| O16 | **S5 实机是否有 F1/F2 越界** | ❌ **不能回答**（树是裁剪发布且机型绑定未验证） |
| O17 | **S5 是否有自己的 OSPO 内核页 / 能否拿到 S5 的真内核树** | 未确认 |
| O18 | **keyhunt 重跑结果** | 用正确偏移重跑 `keyhunt.py`/`keyhunt2.py` 的搜索 —— **现在它第一次具有检验力**。注意：5240 个文件内候选 key 仍只是极小集合 |
| O19 | **`25 号报告`与`00-执行摘要`自相矛盾** | 项目自认"唯一副作用是 1 次 length-DoS"（`S5_AES…:415`）vs "多次 90MB 流送已致相机多次 brick"（`00-执行摘要:46`）⇒ **设备可能已非正常态，影响所有"设备行为"阴性结论的可信度** |
| O20 | **RSA e=65537 完整穷举** | 只跑了先验排序前 24 名（PKCS#1 v1.5 + DigestInfo）× BE/LE = 48 次 gcd（3,012 s）。高先验全集 84 个、全部 `(msg,hash,padding)` 3,620 个**未跑完**。可用 `--max-cands-65537` / `--budget` / `--pads` 扩跑（完整跑约需 2.5 小时） |

### 5.3 数据/证据层缺口

| # | 缺口 | 说明 |
|---|---|---|
| O21 | **另外三态 `curmenu` 从未入库**（PAL+mov / NTSC+mp4 / PAL+mp4） | 需 `setsetting` 改制式/容器（**属写操作**）——本次未做，留待用户授权 |
| O22 | **18/12/10 档位的判据侧原始数据** | `sd_memory` 读数、`startsenddata` 响应文本、`P1000004.MOV` 实拍**全部不在库内**，导致这些数字**不可离线复现** |
| O23 | **exFAT 归档证据无法复核 22 号报告** | `bm_before` 与 `bm_after` 指纹**互不相同**，不是合法配对；归档中**不存在"allocated 190"的基线** ⇒ 22 号的"指纹一致 ✅"无法从归档复核（A8） |
| O24 | **方向 4 的硬约束** | **全库只有一对已知明文**（`ipu_data`，256 KB 全零）⇒ 任何 AES 验证器**只能依赖这一对**，且必须同时声明"**不缩小 2^128 密钥空间**"。想靠"多找已知明文"提高判定力的路**到此为止** |

---

## 6. 文档之间的矛盾

### 6.1 ★★ 审计指控 `s5monitor.py` 自动重发 `req_acc` —— **本次代码核查证明该指控不成立**

| 出处 | 原文主张 |
|---|---|
| `00_审计总报告.md:264` | 「**自动重发 `req_acc`**：`s5monitor.py:126-138` 在任何 `err_reject` 上自动重发 ⇒ 与 `附_技术参考.md:139-154` 自己的红线"`req_acc` 绝不能高频重发，只在启动时发一次"**冲突**；正是文档描述的"打回受限会话/触发 invalid login/需拔电池"行为」 |
| **★ 本次核查实际代码** | `s5monitor.py:265-310` 的 `ensure_access()` 实际行为：<br>① 先 `req_acc()` **一次**，随后**只轮询 `getstate`**（每 2 秒）<br>② **仅当** `getstate` 已通但权限等级仍非 `ok` 时，才允许**补一次**确认请求，且**节流为 `> 20 秒`**（注释：总量极少）<br>③ `s5monitor.py:273-279` **显式注释**："★ 启动时【绝不】发 `req_acc_can`"，并记录实测：加了启动清理后热点模式下 **90 秒都拿不到 `ok`**，去掉后单次 `req_acc` 直接拿 `ok`<br>④ 超时分支打印警告："⚠️ 切勿反复重试 `req_acc` —— 会被相机判为异常 App 并触发 invalid login！"<br>⑤ `req_acc_can` **只在超时退出前清理**时发（`s5monitor.py:306-309`），且 `err_others_requesting` 时**跳过** |

**⇒ 结论**：审计报告的 A5 中「自动重发 `req_acc` 违反自己的红线」一条**是错误指控**。代码实现与文档红线**一致**（启动一次 + 心跳保活 + 结束清理 + 20 秒节流）。
**⇒ 落地提醒**：若后续文档要转述 A5，应**只保留**「绑 `0.0.0.0` + 无认证 + GET 控制端点（CSRF）+ `/api/setting` 绕过白名单 + 前端 `innerHTML` XSS 面」这几条，**删掉 `req_acc` 那一条**。

### 6.2 ★★ 取景流分辨率的三种写法（640×432 / 640×360 / 320×240）

| 出处 | 写法 |
|---|---|
| `附_技术参考.md:21`（v1.0 与 v1.5 两份相同） | **640 × 432**（3:2，与传感器一致） |
| `使用说明.md:45`、`README.md:45` | **640×432 @ 18fps** |
| `12_S5无线监看_v1.0_20261014/README.md:259`（性能教训） | 「**真实取景流是 640×360（3 倍像素）**」 |
| `12_S5无线监看_v1.0_20261014/README.md:258` | 「本项目曾用 **320×240** 合成图测出 20–26 ms」 |
| `定因与交接_20261014.md:54` | 「单帧 **20–26 ms**（640×432）」 |

**⇒ 矛盾点**：性能章节说真实流是 640×360，协议章节说 640×432。二者不可能同时为真（640×432 = 3:2；640×360 = 16:9）。
**⇒ 实操影响**：做 LUT 性能预算时，**以 640×360 为准更保守**（像素数更小但被明确标注为"真实取景流"）；640×432 出现在协议规格表。**建议实测确认后再写进对外文档。**

### 6.3 ★★ 16_ 发行包内的 `使用说明.md` 与 `附_技术参考.md` 是 **v1.0 的原始拷贝**

**★ 本次核查（逐字节 diff）**：
```
diff 12_S5无线监看_v1.0_20261014/使用说明.md \
     16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/使用说明.md
→ (完全相同)

diff 12_S5无线监看_v1.0_20261014/附_技术参考.md \
     16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/附_技术参考.md
→ (完全相同)
```

**⇒ 后果（发行包里三处硬伤）**：
1. `使用说明.md:1` 标题仍是「**DC-S5 无线监看 v1.0**」，而包 `README.md:1` 已写「**LUT 版 v1.5**」（`VERSION` 文件内容 = `1.5`）
2. `使用说明.md:20,102` 仍教用户跑 `./run.sh 192.168.x.x` —— **v1.5 包里没有 `run.sh`**（只有 `启动.command` / `首次运行_安装依赖.command`）
3. `使用说明.md:136-143` 的「文件说明」画的是 `12_S5无线监看_v1.0_20261014/` 的目录树（列 `run.sh`、`www/index.html`），与 v1.5 实际目录（含 `s5_lut.py`/`s5_content.py`/`s5_transfer.py`/`s5_get_photo.py`/`s5_selfcheck.py`/`lut/`）不符
4. **两文件通篇零 LUT 内容**，与包 `README.md:47-53` 的 LUT 卖点完全脱节

**⇒ 判断**：v1.5 打包时**只更新了 `README.md`**，另两份文档忘了同步。**这是发行包最主要的可用性缺陷。**

### 6.4 ★★ ObjectID 根对象：一处说"卡在最后一环"，另一处说"已跑通"

| 出处 | 主张 |
|---|---|
| `10_仓库补丁/定因与交接_20261014.md:296` | 「`701 No such object` 说明 Panasonic LumixLink 内容树的根对象**不是标准 UPnP 的 `"0"`**」；§7.3 标题即「**尚未解决的最后一环：ObjectID**」 |
| `12_S5无线监看_v1.0_20261014/README.md:192-199, 348-350` | `GET /api/gallery?id=<ObjectID>` 已可用；「浏览器 → 「🎨 LUT」面板 → 「列举相机内容」（会自动切回放模式）」 |
| `08_实机与离线验证记录_20261014.md:303` | 「`CANDIDATE_OBJECT_IDS` 已内置 16 个候选」——**暗示根对象尚未确定** |

**⇒ 矛盾**：`定因与交接` 写于同日较早（把 ObjectID 列为未解），`README` 的「已解决」章节写在更晚（2026-10-14 实测定因），并给出 `NumberReturned=16` 的成功响应。**最可能是时序问题：ObjectID 后来被解掉了**，但 `定因与交接_20261014.md` 未回填更正。
**⇒ 建议**：以 `README.md:276-353` 为准（有 `NumberReturned=16` 的成功数据），把 `定因与交接_20261014.md` §7.3 标注为"已被后续解决"。

### 6.5 ★★ 文档声明的"已并库/已移除"与实测不符

| 出处 | 声明 | 实测 |
|---|---|---|
| `README.md:74`、`REPO_CONTENTS.md:20` | 四包"**已去重并库、各留一份并库说明**" | 四包残留 **534 个文件** |
| 三份包 README | "包内文件**已全部移除**" | `08_`=13、`09_`=13、`10_`=46、`11_`=462 |
| `00_项目总结/04_定因与工具链成果_20261013.md:112-113` | 「该包已**去重并库**——包内 434 个文件里 421 个与权威目录逐字节相同，故包目录不再保存副本，**仅留一份并库说明**」 | 与上同 |

> **⇒ "重复"判断准确，"已移除"是假的。真正的错误是「并库未执行，却宣告已执行」。**
> `00_审计总报告.md:305-317`
> 附带：`README.md:179-186` 的"以下重复内容已删除，仅保留一份"逐项清单里**没有** `P1022641.MP4`（213 MB × 2 = 426 MB），而它恰好是全包最大的重复文件。`00_审计总报告.md:410`

### 6.6 ★★ 仓库规模数字三处不一致且都与实测不符

| 项 | 声明 | 实测 |
|---|---|---|
| 跟踪文件数 | 864（`README.md:197`、`REPO_CONTENTS.md:7`） | **1,390** |
| 体积 | 41.5 MB（`REPO_CONTENTS.md:7`）/ 约 55 MB（`README.md:11`） | **67.2 MB** |
| 唯一内容 | 583 份 | 未复核 |
| 去重前 | 2,188 → 864 | **"2,188"无任何可复核依据**（无历史清单） |

> `00_审计总报告.md:345-352`、`02_全包查看指令手册.md:109`

### 6.7 ★★ 相机是否弹「允许连接？」对话框 —— 三处说法不一致

| 出处 | 说法 |
|---|---|
| `附_技术参考.md:156` | 「**另更正一个误区**：相机**不会弹出任何授权对话框** —— 全程是相机内部自己校验。」 |
| `12_S5无线监看_v1.0_20261014/启动_含LUT.command:47-48` | 「↳ 启动后请【**盯着相机屏幕**】：若弹出「允许连接？」请按【**允许**】」 |
| `10_仓库补丁/定因与交接_20261014.md:153` | 「跑 `python3 s5monitor.py --host 192.168.1.131`，**盯着相机屏幕**：应弹「允许连接？」→ **按【允许】**」|
| `s5monitor.py:281`（★ 代码原文） | 「👉 若相机屏幕出现「允许连接？」请点【允许 / 是】（**多数固件不弹，内部自校验**）」 |

**⇒ 最可能的和解**：**多数固件不弹**（内部自校验），少数会弹。`s5monitor.py` 的措辞最准确（"若…"+"多数固件不弹"）。
**⇒ 落地建议**：统一写成「**大部分情况下相机不弹对话框，内部自校验；若屏幕出现「允许连接？」则按【允许】**」。

### 6.8 ★★ 已撤回判据仍在活代码路径（最危险的一条）

| 位置 | 内容 |
|---|---|
| `04_工具与脚本/campaign2/exfat_patch.py:15` | 模块 docstring："目的：触发内核越界写（相机报"写入错误"**即为已执行**）" |
| `04_工具与脚本/campaign2/exfat_patch.py:535` | **`go2` 的交互提示**："【先内存写、后卡写】⇒ 内核内存位清除【**已经执行**】⇒ 越界写成立" |
| `04_工具与脚本/campaign2/s5_exfat_test.sh:18,121-124` | 同上，写进 shell 现场提示 |
| `04_工具与脚本/TOOLS.md` | 通篇 0 处提及撤回；`:33` 仍把 `go2` 当活能力介绍 |
| `01_研究报告/21_…:69-70`、`22_…:115,132` | **未撤回**的旧断言；22 号仍称"前置条件已实机确认" |
| 副本 | `11_DC-S5成果包…/02_工具链/{exfat,cam_cgi}/`、10 号包内、`DC-S5_成果包_20261013.zip` 内 |

> `exfat_patch.py:535` 是**操作者现场读到并据此做判断**的活代码路径。**分发物仍在扩散"把报错当成功"的操作规程。**
> `00_审计总报告.md:198-215`

```bash
grep -rn "即为已执行\|已经执行" --include="*.py" --include="*.sh" 04_工具与脚本/ | grep -v 审核
```

### 6.9 ★ 同一个 `err_fw_same` 两个脚本给出**相反解释**

| 文件 | 解释 |
|---|---|
| `finalfix.py:20-31`、`:254-257` | 「`err_fw_same`: **(a) FLASH LANDED. The write completed** … The WRITE PATH works end to end.」 |
| `control.py:83-86` | 「`err_fw_same`: **TRANSPORT CLEAN** … the camera refused … **it does NOT flash**」 |

> 而 `oracle/README.md` 已用实测证明该前提**已失效**：正确签名的旧固件上传得到的是 **`err_critical`**（不是 `err_fw_same`），并明确写"**阶段 1 的前提已失效**"、"`err_fw_same` 是 **App 端文案**，不是相机上传响应"。
> ⇒ `finalfix.py` 的判据既与同项目脚本矛盾，也已被实验否定，但**未同步更正**。
> `00_审计总报告.md:217-232`

### 6.10 ★ 10_/11_ 包内的 25/26 号报告是**过期旧版**，而 README 标为"使用前必读"

| 文件 | 权威（`01_研究报告/`） | 副本（10_/11_） | 副本缺失内容 |
|---|---|---|---|
| `25_操作记录与风险手册_20261013.md` | 19,687 B / `eb42e3e7…` | 12,909 B / `fd0a7df1…` | **§11 录制格式操作红线**（`ok≠生效` 的 6 次反例、`err_reject` 退避、`a6k` 静默改容器） |
| `26_本次运行日志_20261013.md` | 33,156 B / `2cef7858…` | 13,650 B / `d9cc7bc6…` | **[第 6 阶段] 无线监看工具** 与 **[第 7 阶段]** 全部（约 382 行） |

> `11_DC-S5成果包_20261013/README.md:5` 把这个缺风险章节的旧版标为"**使用前必读**"。
> 其余 22 份报告在三处**逐字节一致**。
> **注**：mtime 不可作判据——26 号两侧 mtime 同为 10-14 19:29，内容却差 382 行。
> `00_审计总报告.md:324-333`

### 6.11 ★ 版本门证伪链的前提已被上游撤回

| 出处 | 主张 |
|---|---|
| 项目文档 | 「改 `comm_proto_ver` 绕过版本门」**已证伪**（字段方向 + 无比较逻辑） |
| `07_签名与密钥恢复/结论.md:225`、`14_总包审计与新方向_20261014/README.md:112` | 该证伪所依赖的前提「**版本字段在签名覆盖内 ⇒ 改版本号必然破坏签名**」——其源头 `07_参考仓库/s1m2-research/docs/CORRECTIONS.md` **已自我撤回**该断言 ⇒ **整条链降级为候选假设**；「改版本号绕过版本门」的**证伪依据也不再成立**（既不能支持"能绕过"，也不能支持"必然被拒"） |

### 6.12 ★ OSS 内核树的机型绑定错误（同文自相矛盾）

| 出处 | 原话 |
|---|---|
| `S5_RE_Project_Summary_EN.md:92` | 下载 URL = `https://ospo.panasonic.com/oss/source/dsc/**DC-FZ1K2**/linux-3.18.18.tar.gz` |
| `S5_RE_Project_Summary_EN.md:15` | "OSPO publishes `linux-3.18.18` **for this model**"（指 DC-S5）← **同文自相矛盾** |
| `REPO_CONTENTS.md:101` | 如实写作 "`ospo.panasonic.com` → **`DC-FZ1K2`** 页" |

> **⇒ 那棵 771 MB 的 `linux-3.18.18` 是 DC-FZ1K2 的内核源码，不是 DC-S5 的。** 因此 `f_fs.c` 的阴性结论**对 S5 实机不具备排除力**。
> 项目英文稿把该树"缺 exFAT、缺 USB gadget"解释为"松下发布的 OSS 与设备不匹配"——**更可能的解释是：那本来就是另一台机器的源码**。这个"OSS mismatch"论点应从对外材料中撤下。
> `08_实机与离线验证记录_20261014.md:238-253`

### 6.13 ★ 档位数字的内部冲突

| 出处 | 写法 |
|---|---|
| `08 号报告:166` | PAL+mov = **12** |
| `08 号报告:167` | PAL+mov = **11** |
| `08 号报告` §1/§1b | 仍用 17/11 |
| `30:269` | 把 17→18 归因于"是否含当前选中项" |
| `30:293-295` | 自己的差集算术表明那个 +1 就是 curmenu 独有档 `mov_60p_200mbps_c4k_10bit` —— **两种解释互斥** |
| `00_执行摘要_全文.md:76-80` | **同页内**先写"18 档"（更正后）又写"这 17 档"（更正前）——更正框与它要更正的正文**相隔 3 行** |

> `00_审计总报告.md:354-359`、`02_全包查看指令手册.md:123`
> **可复算的部分是对的**：`allmenu.xml` 去重 `cmd_value` = 44（mov 31 + mp4 13）。

### 6.14 ★ 对"版本字段"的三重表述并存

| 出处 | 表述 |
|---|---|
| 项目旧文档 | 「ECDSA 覆盖外层头 `0x0-0x200`」（判定为**强假设，未验签**） |
| `07_签名与密钥恢复/结论.md:223` | **本工作的裁决：该具体假设在本轮穷举范围内未被支持（被排除）** |
| `07_签名与密钥恢复/结论.md:216-217` | 但**可确证**：内层副本 `0x2BC`/`0x2C4` 在 CRC32 覆盖内且落在 `[0x200, L-512)` 内 ⇒ 只要存在任何覆盖 ⊇`[0x200, L-512)` 的签名，版本字段值就被覆盖 |
| `00_审计总报告.md:529` | "改 `comm_proto_ver` 绕过版本门"仍列在 ❌ 已失效 |

**⇒ 三条并存**：旧"强假设" / 新"该假设被穷举排除" / "改版本号绕门已证伪"。三者不能同时成立。

### 6.15 ★ CBC 判决准则：审计自己写错又自己更正

| 出处 | 表述 |
|---|---|
| `03_新方向与实验设计.md` 初版（方向 5） | 「若为 CBC 且明文全零 ⇒ 所有 16 字节密文块必须相同」← **密码学错误** |
| `03_新方向与实验设计.md:271-272` | 已加勘误框并重写 |
| `08_实机与离线验证记录_20261014.md:271-283` | 审计方自认「**我写的 CBC 判决准则是错的**」，并给出教训：「判据类准则在写进实验设计前应先做**阳性/阴性对照自测**」 |
| `06_密码学重跑/结论.md:19, 150-167` | 给出实测：真 CBC+全零 → `256/256` 全不同；真 ECB → `1` |

**⇒ 已在最新文档中修正，但若引用 `03_新方向与实验设计.md` 的旧版本会拿到错误准则。**

### 6.16 ★ `08 号报告` 与 `00_审计总报告.md` 对"只开 80 端口"的判定不同

| 出处 | 主张 |
|---|---|
| `16 号:78-88` | 「端口扫描 1–10000 只有 80，没有 DLNA」 |
| `00_审计总报告.md:398` | **已被 18 号部分证伪**：热点模式 `60606` 直返 200 的 UPnP 设备描述 |
| `08_实机与离线验证记录_20261014.md:92` | 端口对照：**`60606` 开放（200/404）、`50001` 在 station 模式关闭、`80` 返回 403** |

**⇒ 三个口径**："只有 80" / "热点有 60606+50001" / "station 有 60606、50001 关闭、80 返回 403"。
**⇒ 正确表述**：**端口开放情况与网络模式（station / SoftAP）强相关**，不可跨模式引用。

### 6.17 ★ `连热点时怎么测.md` 的内网 IP 与 SSID 未脱敏

| 出处 | 内容 |
|---|---|
| `12_S5无线监看_v1.0_20261014/连热点时怎么测.md:9` | 「本机实测该相机：**SSID `S5-XXXXXX` / 密码 `a707########`**」 |
| `连热点时怎么测.md:49-54` | 讨论 MAC `70:74:14:XX:XX:XX` 与热点密码 `a707########` 的推算关系 |

**⇒ 这是明文 Wi-Fi 密码写在文档里**（与本块其余文档统一使用 `S5-XXXXXX` 打码的做法不一致），而 `00_审计总报告.md` C2/C3 正把"真实 SSID/MAC 通过日志绕过正文脱敏"列为合规问题。
**⇒ 落地提醒**：**本文件属对外分享前必须处理的合规项**（`连热点时怎么测.md` 在 `12_` 目录，且 `12_` 目录内嵌 git 有"脱敏：设备本地名打码"提交）。

### 6.18 ★ 默认相机 IP 三处不一致

| 出处 | 默认值 |
|---|---|
| `run.sh:20`（★ 代码） | `192.168.54.1`（热点网关） |
| `启动.command:11`（★ 代码） | `192.168.1.131`（家网） |
| `启动_含LUT.command:12`（★ 代码） | `192.168.1.131` |
| `16_…/启动.command`（v1.5，★ 代码） | 交互询问，默认 `192.168.54.1` |
| `README.md:34` / `使用说明.md:113`（参数表） | `192.168.54.1` |
| `使用说明.md:18` / `启动.command` 提示 | `192.168.1.131` |
| `ap_test.command:14`（★） | `SSID="S5-XXXXXX"`, `PASS="a707########"` |

**⇒ 矛盾**：文档参数表统一写 `192.168.54.1`（热点），但两个 `.command` 双击入口默认 `192.168.1.131`（家网）。**而 §1.1-A10 明确说热点直连才流畅（延迟 53 ms vs 400–700 ms）。**
**⇒ 落地提示**：**双击启动会默认走慢路径。** 建议统一默认 `192.168.54.1`。

### 6.19 ★ s5_selfcheck.py 的相机搜索顺序与文档描述不符

| 出处 | 说法 |
|---|---|
| `连热点时怎么测.md:19` | 「脚本会自动找相机（**先试 `192.168.1.131`，再试热点网关 `192.168.54.1`**）」 |
| `ap_test.command:65`（★ 代码） | `for c in 192.168.54.1 192.168.0.1 192.168.1.131` ← **热点优先** |
| `16_…/README.md:121` | 「`python3 s5_selfcheck.py` # 自检（**自动找相机**）」 |

**⇒ 矛盾**：文档说家网优先，`ap_test.command` 的实际搜索顺序是热点优先。

### 6.20 ★ 监看器"白名单"声称与实际不符（审计 A5）

| 出处 | 声称 |
|---|---|
| `README.md:100-101` | 「**代码内置白名单，永不发送**：固件升级、格式化、重置、关机、配置上传等任何有副作用或不可逆的命令」 |
| `使用说明.md:154-155` | 同上 |
| `附_技术参考.md:170-173` | 同上 |
| **实际代码** | `ALLOWED_CAMCMD`/`ALLOWED_CAMCTRL`（`:83-105`）只守 `camcmd`/`camctrl`；**`/api/setting`（`:937-943`）直接调 `setsetting`（`:195-196`）绕过白名单** |

> `00_审计总报告.md:263`

---

## 7. 本块最有价值的 5 条

### ★1 「拿到完整授权」的配方已被实测写死 —— 这是所有 Wi-Fi 能力的总开关

`DEFAULT_DEVICE_ID`（`4D454930-0100-1000-8001-020A0003BD13`）+ `--device-name "LUMIX Sync"` + 机身屏幕按【允许】。
实测证据是**一个已连续运行 22 小时 36 分、推帧 1,345,385、`camctrl_ok=true`、`streaming=true`、fps 29.5** 的进程。
**没有这条，监看/对焦/拍照/取景/相册/LUT 全部为零。** 而它的三个禁忌（`req_acc` 只发一次、只用那一个 UUID、启动时绝不发 `req_acc_can`）也都是实测得来——违反任一条都会把相机打到"必须拔电池"的状态。
> `10_仓库补丁/定因与交接_20261014.md:184-189`、`12_S5无线监看_v1.0_20261014/README.md:211-229, 483-496`

### ★2 取片通道的**完整因果**已经闭合：`ok` + 回放模式 + 官方逐字节 SOAP

`accctrl=ok` + 相机切【回放模式】⇒ DLNA 立刻列出全部内容，从 **50001** 端口下载原始全分辨率照片。
关键判据是 **403 vs 701**：`ok_under_research_no_msg` ⇒ 403；`ok` ⇒ 500 + `<errorCode>701</errorCode>`。
**"能收到 SOAP Fault 就是已放行"** 这条判据把一个原本被误判为"相机对 DLNA 单独限制"的死结解开了。
一个反直觉的硬约束：**拍摄模式下内容树是空的**——这是卡了最久的一环。
> `12_S5无线监看_v1.0_20261014/README.md:276-328`、`10_仓库补丁/定因与交接_20261014.md:281-292`

### ★3 错误码语义 + 退避策略是**把"偶尔成功"变成 100% 成功**的唯一杠杆

`err_reject` **不是失败**（格式对、状态不接受），`err_busy` 要退避重试。实测把触摸对焦从"偶尔成功"变成 **8/8 = 100%**；`mov_50p_200mbps_4k_10bit` **第 5 次退避重试才成功**。
而 `ok` **≠ 生效**（当天 **≥6 次反例**）——必须回读或看实拍文件头。这三条组合起来，是整个项目最容易复用的方法论。
> `附_技术参考.md:96-116`、`00_项目总结/02_项目时间线.md:218, 265-270`

### ★4 LUT：机内实时烧录**已终局关闭**，但拿到了两条**真能出片**的路

- 官方三机对比表 + 官方原文一手否证初代 S5 无 Real Time LUT（不是"开关没找到"，是**没有那级硬件管线**）
- `.VLT` 格式由 35 个官方样本逆向到**等级 A**（17³、4913 行、整数 0–4095、卡**根目录**、两行 `#` 头）
- 并且**已实机确证**机身能读入我们自制的 `VL709.vlt`
- **唯一还能出"烧录版"的合法路径 = HDMI 外录**（`[V-Log View Assist]` 的输出口带 LUT）
- **实时监看套 LUT 已跑通且性能达标**：256³ 精确查表 **6.7 ms**，吞吐零损失（17.4 → 17.8 fps）
> `09_LUT可行性报告_20261014.md:321-348, 408-419`、`12_S5无线监看_v1.0_20261014/README.md:254-271`

### ★5 审计把"哪些结论不能信"变成了**可复算的清单**，而且它自己也被核查过一次

四条旗舰结论（S1–S4）的证据链不成立，每条都附了可直接粘贴的复现命令；十项独立复算（R1–R10）中 4 项与项目文档相反。
更关键的是它给出的**三条新方法学铁律**（写入前断言 `payload != readback`、偏移类结论必须附判决实验、权威结论必须登记判据侧原始数据）——这三条能防止同类问题再次发生。
**★ 本次核查补一条**：审计的 A5 中「`s5monitor.py` 自动重发 `req_acc`」是**错误指控**（见 §6.1），说明**审计报告也需要被复核**。
> `00_审计总报告.md:50-61, 625-642`

---

## 8. 最容易被重复劳动的 3 件事

### ⚠️1 重新推导「怎么拿到授权」/ 重新摸索 DLNA —— 已经跑通，全在文档里

**重复劳动的样子**：新起一个会话，从 `curl cam.cgi?mode=getstate` 开始摸索，试不同 UUID、试不同 `device-name`、撞 `err_unsuitable_app`、怀疑"相机对 DLNA 单独限制"、怀疑"是不是要 SoftAP 才行"……

**已经确定的全部答案**：
| 问题 | 答案 | 出处 |
|---|---|---|
| 用哪个 UUID | `4D454930-0100-1000-8001-020A0003BD13` | `README.md:483` |
| 用哪个 device-name | `LUMIX Sync` | `定因与交接:186` |
| 要做什么机身操作 | 屏幕按【允许】（多数固件不弹） | `定因与交接:186` |
| 多久拿到 `ok` | **10 秒** | `README.md:252` |
| 403 是什么 | **就是 accctrl 没到 `ok`**，不是 DLNA 特有限制 | `定因与交接:286` |
| 701 是什么 | **已放行**，只是 ObjectID 不对 | `定因与交接:288` |
| 内容树为什么是空的 | **相机不在回放模式**（不是卡上没照片） | `README.md:328` |
| 下载端口 | **50001** | `README.md:320` |
| 为什么裸 curl 失败 | **按客户端身份放行，同时只有一个身份能用**（这是正常的） | `README.md:239-241` |
| 相机报"需要更新 app" | 用**同一 UUID** 发 `req_acc_can` 清陈旧 pending（**不必重启相机**） | `定因与交接:261-266` |

**⇒ 结论**：这一整条链**没有一处需要重新试**。`s5_content.py cleanup/diagnose/sweep/list` 四个子命令已封装全部动作。

### ⚠️2 重新测「机内能不能烧 LUT」/ 重新找「Wi-Fi 上传 LUT」的口子

**重复劳动的样子**：又去 `getinfo type=lut/ad_lut/vlt/lutinfo/lutlist` 试一遍、又去 `camsetting.bin` 里搜 `LUT`、又去 APK 里找 LUT 上传、又怀疑"是不是固件里有隐藏开关"。

**已经确定的全部答案**（三条独立取证一致）：
- `allmenu`(740 item) / `curmenu` 中 LUT 菜单项 **0 个**（7 处 `lut` 命中全是 "High-Reso**lut**ion" 误报）
- `getinfo type=` 的 LUT 相关类型**全部 `err_param`**；`capability` 的 `camspec 17 项`/`camcmd 6 项`**均无 LUT**
- `camsetting.bin`（65533 B）中 `LUT`/`VLT`/`cube` **0 处**
- `startsenddata` 的 `type` 白名单**只有 `camsetting` 与 `fw`**
- 官方 APK：`.cube`/`.vlt`/`.3dl`/`AD_LUT`/`lutfile`/`LUT_LIBRARY` **全 0 命中**（UTF-8 与 UTF-16LE 都查过）
- 官方三机对比表**直接否证**初代 S5 有 Real Time LUT
- 固件侧 `LUT`(3 条)/`VLT`(2 条) 命中**全是密文噪声**，与无意义对照词 `QKJ`/`ZXQ` **同分布**；**数学边界**：≥5 字节关键词在 90 MB 密文中期望命中 ≈ `8×10⁻⁵` ⇒ **"0 命中"是数学必然，不是"功能不存在"的证据**
- **正确表述**：「固件加密区是否含 LUT 解析/Real Time LUT 代码，**不可判定**」；❌ 不能写「固件里没有 LUT」

**⇒ 结论**：**别再搜了。** 唯一还开放的只有"USB PTP 直写 LUT tag"（`Lumix-Fast` dex 字符串池线索，需 JRE+jadx），且**以 `ph_sty11` 判断 S5 大概率也不接受**。
> `09_LUT可行性报告_20261014.md:19-30, 83-92, 214-225, 227-239, 321-333`

### ⚠️3 重新验证「18/12/10 档位」「持久化」「AES 终局否定」—— 三个都已有定论或已降级

**重复劳动的样子**：
- 又去数一遍 `allmenu`/`curmenu` 的 mov 档位（"到底是 17 还是 18？"）
- 又去做一次"写入→拔电池→读回"来验证持久化（**而不知道这个实验已被判定为空操作**）
- 又去跑一次 keyhunt 说"0 命中 ⇒ 密钥不在固件里"（**而不知道旧脚本对假设零检验力**）

**已经确定的答案**：
| 问题 | 答案 | 出处 |
|---|---|---|
| mov 档数 | **NTSC 18 / PAL 12**；`allmenu` 44（mov 31 + mp4 13）；幽灵档**恰好 1 个** = `mov_60p_200mbps_**c4k**_10bit`（与激活档 `4k` 是**不同 token**） | `08_实机与离线验证记录:31-43` |
| 判据 | `curmenu` 的 `enable=yes` 集合，**随制式与容器双重变化**；`enable` 语义 = "可选"不是"当前值" | `08_实机与离线验证记录:96-108` |
| 持久化 | **S1 空操作**已实机独立确认（三者 sha256 完全相同：`2d8c0a767c8c2306…`）；该结论应降为 **◐ 待重做** | `05_相机只读快照/README.md:49-58` |
| AES 终局否定 | **降级为 ◐ 离线希望渺茫（非"终局"）**；两条核心否定证据（5240 key×3 IV、211 候选）**被推翻**（阳性对照 12/12 假阴性） | `06_密码学重跑/结论.md:305-314` |
| 偏移模型 | **单一真源 = `upd_table.py`**，任何脚本**不得手写 `raw[doff:]`**；判决实验必须 **7/7** 才允许继续跑大规模穷举 | `06_密码学重跑/结论.md:43-46, 421-422` |

**⇒ 结论**：这三件事**都不该重做**——该做的是**按新判据重做**（修偏移、加 no-op 断言、≥3×3 交叉），而不是从零再来一遍。

---

## 附：本块文件清单与行数

| 目录 | 文件 | 行数 |
|---|---|---|
| `14_总包审计与新方向_20261014/` | `00_审计总报告.md` | 686 |
| | `02_全包查看指令手册.md` | 469 |
| | `03_新方向与实验设计.md` | 752 |
| | `05_相机只读快照_20261014/README.md` | 83 |
| | `06_密码学重跑/结论.md` | 426 |
| | `07_签名与密钥恢复/结论.md` | 348 |
| | `08_实机与离线验证记录_20261014.md` | 326 |
| | `09_LUT可行性报告_20261014.md` | 449 |
| | `10_仓库补丁/定因与交接_20261014.md` | 346 |
| | `10_仓库补丁/口径修正_SD引导与SoC代_20261015.md` | 32 |
| | `README.md` | 122 |
| `12_S5无线监看_v1.0_20261014/` | `README.md` | 511 |
| | `使用说明.md` | 155 |
| | `附_技术参考.md` | 186 |
| | `连热点时怎么测.md` | 60 |
| `15_LUT烧录工具_20261014/` | `README.md` | 278 |
| `16_S5无线监看发行包_20261015/…v1.5/` | `README.md` | 148 |
| | `使用说明.md` | 155（= v1.0 拷贝） |
| | `附_技术参考.md` | 186（= v1.0 拷贝） |
| `00_项目总结/` | `00_执行摘要_全文.md` | 158 |
| | `01_成果总表.md` | 81 |
| | `02_项目时间线.md` | 286 |
| | `03_思路总结_全文.md` | 244 |
| | `04_定因与工具链成果_20261013.md` | 173 |
| | `05_环境与依赖.md` | 162 |
| | **合计** | **6,822** |

> **★ 标记说明**：带「★ 本次核查」的条目是**直接读代码/跑 diff 得到的事实**，不是文档陈述的转述。共 4 处：
> ① `s5monitor.py` 的 `req_acc` 实际策略（§6.1，**推翻了审计 A5 的一条指控**）
> ② v1.5 两份文档与 v1.0 逐字节相同（§6.3）
> ③ 各 `.command`/`run.sh` 的实际 exec 命令与默认 IP（§2.1.2、§2.1.3、§6.18）
> ④ `ap_test.command` 的相机搜索顺序（§6.19）
