# B · `01_研究报告/` 结构化素材（供汇编"项目唯一权威调用文档"）

> **分析范围**：`01_研究报告/` 全树 —— **91 个 `.md`、40,321 行**，逐文件通读（两份机器日志按结构 + 关键段精读）。
> **路径约定**：本文所有 `路径:行号` 均为**相对 `01_研究报告/`** 的路径。凡引用 `01_研究报告/` 以外的文件，均写全相对 workspace 根的路径。
> **纪律声明**：全程纯离线读文件，未连接任何设备。所有结论均带原文行号指针；凡属推断，一律标注「推断」。**本文不引入任何原文没有的事实**。
> **阅读优先级**：§3（已证伪）> §7（专题 · exFAT / 密码学）> §2（可用操作路径）> §4（陷阱）> §6（矛盾）。

---

## 0. 覆盖清单与"重复劳动预警"

### 0.1 目录构成（7 个簇）

| 簇 | 目录/文件 | 文件数 | 行数 | 性质 |
|---|---|---|---|---|
| ① AES/离线破解调研 | `01_固件AES绕过_调研_20261010/`（6 子目录） | 21 | 3,363 | 静态分析 + S1M2 参考包 + oracle 日志 |
| ② 研究总报告 | `02_研究总报告_20261011/` | 26 | 30,092 | 其中 `logs/写路径/campaign.md` 独占 22,801 行 |
| ③ 隐藏格式（可分发版） | `03_隐藏格式_可分发版_20261012/` | 10 | 846 | 自包含可分发包（含复现流程） |
| ④ 隐藏格式（持久化/追查线） | `04_`~`12_` 共 9 个顶层文件 | 9 | 1,077 | 持久化成果 + 追查 + 格式对照 + 跨机型边界 |
| ⑤ 服务模式/ROM BACKUP/exFAT | `13_`、`21_`~`27_` | 8 | 1,622 | 服务模式、ROM BACKUP、exFAT 越界写、长名崩溃 |
| ⑥ BLE/WiFi 侧勘察 | `14_`~`20_` | 7 | 1,150 | BLE 协议、SoftAP、凭据链 |
| ⑦ PTP/录制格式/风险手册 | `28_`~`31_`、`25_`、`26_` | 6 | 2,221 | PTP 审计、对称密钥分析、录制能力边界、运行日志 |

### 0.2 ★ 已确认的**逐字节重复文件**（7 对 → 14 个文件，实为 7 份内容）

`01_固件AES绕过_调研_20261010/` 与 `02_研究总报告_20261011/research/` **有 7 对 md5 完全相同的文件**（本次逐对 `md5` 校验）：

| 内容 | 副本 A | 副本 B |
|---|---|---|
| `00-总评估报告-中文.md` | `01_固件AES绕过_调研_20261010/00-总评估报告-中文.md` | `02_研究总报告_20261011/research/00-总评估报告-中文.md` |
| `BOOT_FLOW.md` | `…/01-固件格式与启动/BOOT_FLOW.md` | `…/research/BOOT_FLOW.md` |
| `FIRMWARE_FORMAT.md` | `…/01-固件格式与启动/FIRMWARE_FORMAT.md` | `…/research/FIRMWARE_FORMAT.md` |
| `PANASONIC_FIRMWARE_UPDATE_PROTOCOL.md` | `…/01-固件格式与启动/…` | `…/research/…` |
| `PROTOCOL_AUDIT.md` | `…/01-固件格式与启动/…` | `…/research/…` |
| `hardware_attack_surface_notes.md` | `…/02-硬件攻击面/…` | `…/research/…` |
| `Wi-Fi实机预言机与mode枚举实测-中文.md` | `…/03-离线破解与上传预言机/…` | `…/research/…` |

> **汇编建议**：这 7 对只保留一条，另一条只列"同内容副本"指针。**注意 `research/` 里另有 `03-固件格式与启动链.md`（130 行）不是副本**，它是对 `FIRMWARE_FORMAT.md` 的重写升级版，两者在**版本字段偏移**上互相矛盾（见 §6.1）。

### 0.3 两份"巨日志"的正确读法（否则会浪费大量时间）

| 文件 | 行数 | 怎么读 |
|---|---|---|
| `02_研究总报告_20261011/logs/写路径/campaign.md` | 22,801 | **机器日志**。结构：`Phase A`（枚举，L5–L1458，125 条 `getstate type=` 探测）+ **13 次 Phase I 版本号篡改上传**（每次 1474 分片，各占 3,000–4,000 行）+ `Phase CONTROL`×2（L22662–22729）+ `Phase TESTA`×2（L22730 起）。**只有 ~80 行有信息量**：`Phase` 头、`transform:` 行、`VERDICT` 行、末块失败行。|
| `01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/oracle_results.md` | 3,063 | **机器日志**：5 个 `## phase 0` 块（L2/L12/L22/L47/L80）。前 4 块是握手失败排查（L2–L79），第 5 块（L80–3063）是 1474 分片完整上传 + 末块失败。**净结论在 `oracle/README.md:73-90`**。 |
| `02_研究总报告_20261011/logs/指纹/http_fingerprint.md` | 727 | **机器日志**：A 基线头 / B 方法×路径矩阵（L21–449）/ C HTTP 版本 / D 错误页 / E 路径穿越（L514–725）。**净结论在 `02_研究总报告_20261011/05-RCE与代码注入.md:10-16`**。 |

---

## 1. 已确证的结论（含证据等级）

> 证据等级定义：**实测** = 实机/字节级验证；**强推断** = 有结构性硬证据但未直接验证；**弱推断** = 同平台类推；**未验证** = 仅记录假设。

### 1.1 设备与环境

| # | 结论 | 等级 | 指针 |
|---|---|---|---|
| 1 | 机型 DC-S5，SoC **MC801**，SN `XJL########15`，运行固件 **2.9**，协议版本字段 `VD4.30` | 实测（PTP GetDeviceInfo） | `02_研究总报告_20261011/01-目标与环境.md:9-15` |
| 2 | 本机是**研究版**：`req_acc` 回 `ok_under_research_no_msg,S5-XXXXXX,remote,encrypted`，远程访问免机身确认 | 实测 | `01-目标与环境.md:14`；`01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/Wi-Fi实机预言机与mode枚举实测-中文.md:15` |
| 3 | `getstate` **忽略 `type`/`value` 附加参数**，恒回同一状态 XML（622 B） | 实测 | `01-目标与环境.md:52`；`02_研究总报告_20261011/08-WiFi预言机与密钥提取.md:43` |
| 4 | 本机是 **`GK` 机型（中文区）= PAL 机型**；`[Strict]` 地区后缀已锁死不可改 | 实测（服务模式屏显实拍） | `13_服务模式与ROMBACKUP_20261013.md:236,244-248` |
| 5 | 相机 Wi-Fi 芯片 OUI **`00:0C:E7` = MediaTek**（非 Broadcom/Marvell） | 强推断（IE 解析） | `17_相机热点与蓝牙Windows侧勘察_20261013.md:16,80,108-109` |
| 6 | Wi-Fi 模块型号此前列为"待拆机确认"，现收敛到 MediaTek 系 | 强推断 | 同上 `:107-109` |
| 7 | 相机 SoftAP 是**明文开放网络**（`capability=0x0401`、Privacy=0、无 RSN/WPA IE）；**密码为空**（BLE 读出全 0） | 实测（三通道交叉） | `17_…Windows侧勘察…:13,62-63`；`18_相机热点SoftAP侧勘察_20261013.md:64-65`；`19_BLE凭据链打通_先写后读_20261013.md:16,80-84` |
| 8 | Open-Gate `6K PHOTO` 是本机**原生已声明功能**，不是隐藏功能 | 实测 | `03_隐藏格式_可分发版_20261012/docs/03_opengate_6k_photo.md:3-4,73-75` |

### 1.2 固件容器与启动链（UPD）

| # | 结论 | 等级 | 指针 |
|---|---|---|---|
| 9 | `S5___V29.bin` = 90,238,464 B (0x560EE00)，Panasonic **UPD** 容器（`UPD\0` 魔数） | 实测 | `02_研究总报告_20261011/research/FIRMWARE_FORMAT.md:1-3` |
| 10 | 容器布局：外层头 512B(0x0) + `"panasonic"`+ECDSA(0x200/0x220) + 内层头(0x2A0) + 目录头(0x2E0) + **48 条 × 92B 分区表**(0x2EC) + 数据(0x1400) + **RSA-4096 尾块**(0x560EC00, 512B) | 实测 | `research/FIRMWARE_FORMAT.md:8-16` |
| 11 | **type=2 ⟺ IV 全零（明文）；type=3 ⟺ IV 非零（加密）；48/48 无例外** | 实测 | `research/BOOT_FLOW.md:20`；`research/FIRMWARE_FORMAT.md:54` |
| 12 | 分区表**物理终点 0x142C**，与数据起点 0x1400 **重叠 44B**（末项 `hr_c_ddr` 的 sha 尾 12B + IV 16B + 零填充 16B）—— 这解释了旧文档"loader1 有 28B 随机数" | 实测 | `research/BOOT_FLOW.md:100`；`research/FIRMWARE_FORMAT.md:82` |
| 13 | 条目 `0x1C` 起的 48B = **32B SHA-256(明文) + 16B 每分区独立 IV**，**不是 SHA-384** | 实测（`lens_hist` 阳性对照） | `research/FIRMWARE_FORMAT.md:89`；`01_固件AES绕过_调研_20261010/02-硬件攻击面/williamwu1234_notes.md:69-77` |
| 14 | 90KB 连续引导块：loader1(0x1400,4K) → loader2(0x2400,38K) → loader3(0xBC00,48K) → program(0x17C00,16MB) | 实测 | `research/BOOT_FLOW.md:31-40` |
| 15 | **loader1 不为空**：512B 零头 + 3584B 加密载荷（熵 7.948）。**旧文档"loader1 全 0/为空"不成立** | 实测 | `research/BOOT_FLOW.md:48,101,161` |
| 16 | **zboot 不为空**：512B 0xFF 头 + 1536B 加密载荷（熵 7.865）。**旧文档"zboot 全 0xFF(空)"不成立** | 实测 | `research/BOOT_FLOW.md:52,102,162` |
| 17 | 条目 `0x14` 字段 = **目的地址(RAM)**，非"128KB 对齐 flash 地址" | 实测 | `research/BOOT_FLOW.md:103,163` |
| 18 | 启动链倒推：BootROM → 容器三重验证（CRC32/ECDSA/RSA） → 解析 48 分区表 → 搬 90KB 引导块入 RAM → loader1→2→3→program → Linux 子系统 | 强推断（与 Milbeaut SC2000/GP1 公开链映射） | `research/BOOT_FLOW.md:69-96,139-146` |
| 19 | 容器内**无公钥、无"禁验签"开关、无回退标志** | 实测（E1–E6 扫描） | `01_固件AES绕过_调研_20261010/02-硬件攻击面/verify_logic_notes.md:15-62` |
| 20 | RSA 尾块**非 PKCS#1 v1.5**（首字节 `89 a1`），疑似 PSS/裸 RSA | 实测 | `verify_logic_notes.md:97-99` |
| 21 | `program` 内 0x53D、`postboot3` 内 0xF5D 的 "MZ" 是**随机假阳性**，不是 PE 文件 | 实测 | `research/BOOT_FLOW.md:60` |

### 1.3 密码学（AES / 密钥 / 签名）

| # | 结论 | 等级 | 指针 |
|---|---|---|---|
| 22 | **AES 密钥不在固件文件内**，固化在 MC801 片内（OTP/eFuse/Crypto Engine/TrustZone） | 强推断（软件侧穷尽排除，非密钥空间穷举证明） | `02_研究总报告_20261011/09-已证伪路线.md:5-12`；`02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:416` |
| 23 | 密钥是**按机型的固定发布密钥**、所有 S5 共用；**变的是 IV（逐构建）与明文（逐台设备）** | 强推断（最强论据：官方单一 .bin 对所有 S5 可刷） | `S5_AES破解可行性评估_20261011.md:138-167` |
| 24 | 41 个加密分区 IV **全部唯一、逐版本全变、不可由 name/index/model 派生（0/41）** | 实测（V11/V20/V23/V24/V29 五版） | `S5_AES破解可行性评估_20261011.md:80,89-97` |
| 25 | 同偏移密文跨版本相等率 **≈0.3–0.5%**（=随机期望 0.39%）→ **排除 ECB / 版本稳定 keystream**，跨版本差分封死 | 实测 | `S5_AES破解可行性评估_20261011.md:99-114` |
| 26 | 加密**非 ECB**（`eep_ow_a` vs `eep_ow_b` 同明文不同 IV：相同位置密文块 **0/8192**） | 实测 | `29_S1R2报告启示与S5对称密钥分析_20261014.md:73-75` |
| 27 | 双签名：**ECDSA P-256(0x220, 64B) + RSA-4096(尾块 512B)**；ECDSA 的 r,s 均满足 `1≤r,s<N`（合法标量），`s>N/2`（高 s、非规范化） | 实测 | `S5_AES破解可行性评估_20261011.md:65`；`verify_logic_notes.md:57-59` |
| 28 | 离线穷举规模：**130k+ 探测 0 命中**（XOR/RC4/AES-128/192/256 ECB/CBC/CTR）+ 5,240 文件内派生 key 0 命中 + 211 候选真实 AES 解密测试 0 命中 | 实测 | `09-已证伪路线.md:8`；`S5_AES破解可行性评估_20261011.md:78-80,563` |
| 29 | 唯一已知明文的加密分区 = `ipu_data`（明文经 `history` 可知，≈全零）；已提取 **256KB 真实 keystream，熵 7.999** | 实测 | `S5_AES破解可行性评估_20261011.md:77,561-562` |
| 30 | 48B 校验块**不是**无密钥哈希（SHA-384/256/1/MD5/CRC 19 种输入组合全试）→ 极可能是带片内密钥的 HMAC/CMAC | 实测 | `01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:11` |
| 31 | PTool 旧 GH2 密钥切片法（`key[i]=input[0x200+i*0x200+table[i]]`）移植 S5 **120 组合全失败** | 实测 | `09-已证伪路线.md:11`；`01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_解码突破记录.md:34-41` |
| 32 | WonderLantern（Nikon）padding-leak 法**不能迁移**：同明文不同 IV 的密文异或**熵 7.999**（应为 ≈0）→ 是真正的 AES-CBC/CTR，非固定 XOR 流 | 实测（决定性实验） | `S5_AES破解可行性评估_20261011.md:541-546` |
| 33 | 分区表里的 SHA 是**"逻辑明文的校验值"**，不等于 `.bin` 里该分区实算字节的 SHA | 实测（跨 5 版） | `S5_AES破解可行性评估_20261011.md:116-121` |
| 34 | **【重要更正】** 29 号原稿的 `pairs_s5.json` 首块偏移错位 0x200，35 条记录全部作废；修正版 `pairs_s5_FIXED.*`（32 跨版本 + 3 版内，84 B/条）才可用 | 实测（独立复算确认） | `29_S1R2报告启示与S5对称密钥分析_20261014.md:254-298` |
| 35 | **【重要更正】** `history` 是**完整全零** 262,144 B（16,384/16,384 全零块），无 64B 头；原稿"16,353 全零块 + 64 字节头"两个数字都错 | 实测（与目录摘要逐字节相符） | `29_…:300-308` |
| 36 | **【重要更正】** ROM BACKUP 的 `ADJUST.bin`/`FIX.bin` 与固件 `eep_adj`/`eep_fix` **未闭合**（同名同长但 SHA-256 不同）→ "大段零区应一致"是猜测，**不能用来拒绝候选密钥** | 实测 | `29_…:321-329` |
| 37 | **【降级】** 零块链不能称"无条件精确预言机"，只是**带模型前提的筛选条件**（需先确认标准 CBC / IV 用法 / 摘要覆盖阶段） | 方法论更正 | `29_…:310-319` |

### 1.4 有效载荷写入与设置面

| # | 结论 | 等级 | 指针 |
|---|---|---|---|
| 38 | `camsetting` blob = **65,533 B**；结构 = 44B 头(`"Panasonic"`+`"DC-S5"`) + 8B 前导 + **831 条 TLV 记录**（`[field_id u16][len u16][flag u16][payload]`）+ `ff ff 00 00` + 校验字节@65532 | 实测 | `07_隐藏格式持久化_追查_20261013.md:63-73` |
| 39 | 校验和算法：`byte[65532] = (256 − Σ(byte[0..65531])) mod 256`（全块和 ≡ 0 mod 256）；**可伪造** | 实测（A/B/C 三组对照） | `08-WiFi预言机与密钥提取.md:28-32`；`01_固件AES绕过…/Wi-Fi实机预言机与mode枚举实测-中文.md:64-69` |
| 40 | S1R2 与 S5 **校验算法同源**（两组人独立反推一致）→ 证明 LUMIX 全系设置块校验同出一源 | 实测（双证） | `06_S1R2移交_20261012/S1R2两项成果_移交S5同事.md:33-43`；`06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:18` |
| 41 | **`getinfo camsetting` 返回的是 RAM 副本**，不是 flash 内容 → 写完立刻回读**不能**作为持久化判据，**只有断电重启后的回读**才代表 flash | 实测（独立验证：仅 setsetting 改 RAM → blob 立即变） | `31_录制格式持久化_受控复测_20261014.md:92-99`；`25_操作记录与风险手册_20261013.md:354-364` |
| 42 | **`setsetting` 会被相机自动存盘**（纠正早前"RAM-only"假设）：只在 RAM 切过 `mp4ed`，flash 已被写成 `0x07`，重启后仍残留 | 实测 | `09_S1H参考包分析_mp4ed_20261013.md:66-80` |
| 43 | 关键字段偏移（61533 blob）：`65230`=ntsc_pal（0x00 NTSC/0x01 PAL）、`3062`=videoformat（0x05 mp4/0x06 mov/0x07 mp4ed/0x08 mp4hevc/0x00 avchd）、`6986`=videoquality | 实测 | `04_隐藏格式_持久化成果.md:30-32`；`09_S1H参考包分析_mp4ed_20261013.md:42` |
| 44 | `0x005e` 记录（偏移 3056）结构 = `[6B 头 5e 00 14 00 01 00][13B 槽][1B 终止 0x00]`；**相机自身行为 = 仅写槽 0**（形态 `06 05 ×12`） | 实测（27 个历史 blob 一致） | `30_录制格式能力边界与操作教训_20261014.md:466`；`25_…风险手册…:398-405` |
| 45 | 可写设置域 = **47 个 `cmd_type`**（`setsetting` 状态写是唯一已证明的可控原语） | 实测 | `03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md:69`；`12_可写设置面审计_20261013.md:13-18` |
| 46 | 双击 PTP `0x9421` 全量配置 = **65,545 B**（PTP DATA 容器），format = 外层单条 TLV(`tag=0x080000a2, len=65537`) + **16 位记录表 831 条**（idx 1..0x4b5），结尾 `ff ff 00 00` + 校验 `0xbd` | 实测 | `S5_AES破解可行性评估_20261011.md:203-213`；`02_研究总报告_20261011/scripts/USB-PTP/PTP_0x9421_dump_使用说明.md:144-147` |
| 47 | 65,545 B 是**完整非截断**（三条证据：结尾终结符 / `payload[0:4]=len-4` 自洽 / 无越界指针）；老平台配置就是 ~64 KiB，S1M2 是 9.2 MiB（**平台代差 ~140 倍**，非读取上限） | 实测 | `S5_AES破解可行性评估_20261011.md:215-220` |
| 48 | 配置是**活快照**：间隔 2 小时的两次 dump 差 21 字节（实时菜单值 + 1 字节校验和） | 实测 | `S5_AES破解可行性评估_20261011.md:482` |
| 49 | 0x9421 解开的是"**用户设置面**"（明文、只读、运行时），**不是**固件明文/密钥/标定数据 | 实测（分区映射） | `S5_AES破解可行性评估_20261011.md:311-315` |

### 1.5 服务模式 / ROM BACKUP

| # | 结论 | 等级 | 指针 |
|---|---|---|---|
| 50 | 进入服务模式：**按住【回放(Playback) + AF ON + 方向右键】同时开机** | 实测（用户实拍） | `13_服务模式与ROMBACKUP_20261013.md:222`；`27_ROM_BACKUP导出成功与数据解析_20261013.md:25` |
| 51 | 回 INITIAL SETTINGS：**MENU/SET + 方向右键**同时关机；退出/恢复出厂：该界面再按 **方向右键 + MENU/SET** | 实测 | `13_…:223-224` |
| 52 | **ROM BACKUP 的门控 = SD 卡槽 1 + FAT32**（exFAT 卡使其整项变灰；卡槽 2 无效）；**不需要**"解除初始设置" | 实测 | `13_…:184-197`；`27_…:21-28` |
| 53 | ⚠️ 退出工程模式必须先**拔掉那张 FAT32 卡**，否则按键流不生效 | 实测 | `13_…:228`；`26_本次运行日志_20261013.md:231` |
| 54 | ROM BACKUP 导出成功：`S5A.TXT`(356,673B) / `S5F.TXT`(356,670B) / `S5U.TXT`(356,668B)，解析后各 **128 KB**；纯 ASCII 十六进制转储、**可读可编辑** | 实测 | `27_…:59-79` |
| 55 | 导出的 3 区 = EEPROM `ADJUST ONLY(21)` / `FIX ONLY(22)` / `UPDATE(10)`；内容 = 标定/身份数据（序列号@0x0000、生产码@0x0020/0x0040/0x0060） | 实测 | `27_…:93-101` |
| 56 | 曾疑为密钥的两块高熵区（ADJUST 0x11000/0x12000）**已排除**：第二列 16 位值逐行递增 = **(校正值, 像素索引) 坏点校正表** | 实测 | `27_…:111-119` |
| 57 | ROM BACKUP **不含固件明文、不含 AES 密钥**（实证印证手册判断） | 实测 | `27_…:154-158` |
| 58 | ⚠️ 但格式可编辑 + 相机支持写回 ⇒ 存在一条"**读-改-写 EEPROM**"通道（本项目红线：只做 `DSC→SD` 导出） | 实测 | `27_…:134-152` |
| 59 | `UsbDeviceSignature` 尾部携带序列号，与 ROM BACKUP 的 EEPROM ADJUST 0x0000 **完全一致**（两处独立来源交叉印证） | 实测 | `13_…:269`；`28_PTP固件更新协议审计_20261013.md:144` |

### 1.6 USB / PTP / BLE / 网络面

| # | 结论 | 等级 | 指针 |
|---|---|---|---|
| 60 | USB：VID=**0x04DA**、PID=**0x2382**（正常 PTP 相机模式）/ **0x2370**（服务·厂商模式，macOS 不识别、PTP 超时）；接口 0 = `0x01` BULK OUT / `0x82` BULK IN / `0x83` INT IN | 实测 | `02_研究总报告_20261011/07-USB-PTP-SCSI.md:50`；`13_…:124-128,264-265` |
| 61 | **唯一坐实、可复现的实机漏洞 = PTP length-DoS**：相机校验 type 不校验 length 且无超时 → 发 12B 但头声明 `length=0x400` → PTP 数据面挂死，**拔插 USB 恢复**，无写、不砖机 | 实测（受控全链条） | `02_研究总报告_20261011/06-崩溃与DoS.md:5-13`；`S5_AES破解可行性评估_20261011.md:486-499` |
| 62 | 参数错误（与 length 错误不同）是**安全的**：设备回干净 `0x201d/0x2002` 并保持存活 | 实测 | `scripts/USB-PTP/PTP_0x9421_dump_使用说明.md:134` |
| 63 | 解析器校验缺失（低利用价值）：**参数数量不校验**（0x9421/0x9605/0x1001/0x1004 多余参数被忽略，返回逐字节相同）+ **TID 不校验** | 实测 | `S5_AES破解可行性评估_20261011.md:463-479` |
| 64 | **0x9103 被识别**（回 `0x2003 SessionNotOpen` 而非 NAK）→ 已实现未文档化命令，**唯一新 PTP 攻击面线索** | 实测 | `S5_AES破解可行性评估_20261011.md:473,480` |
| 65 | 0x9606 **无"任意地址写"原语**：地址由相机 `0x9605` 下发（主机 `0x260498`/`0x2604ac` 存储后原样回填），主机不能自填 | 实测 + 反汇编双证 | `S5_AES破解可行性评估_20261011.md:268`；`28_PTP固件更新协议审计_20261013.md:43-58` |
| 66 | PTP 侧**无 RAM 读回**原语（逐条核实 6 条路径 0x9112/0x9703/0x9605-07/0x9706-07/0x9421） | 实测 | `S5_AES破解可行性评估_20261011.md:338` |
| 67 | 11 条 NVD CVE **全部不适用**（均为"恶意相机→主机"方向，与本项目方向相反）；Milbeaut SoC 0 个公开 CVE | 实测（逐条核对） | `S5_AES破解可行性评估_20261011.md:429-447` |
| 68 | BLE：**无需配对即可扫描/连接/枚举 GATT**（9 服务 / 41–44 特征，视主机栈而定） | 实测 | `15_蓝牙BLE协议逆向_20261013.md:100-101`；`17_…:283-285` |
| 69 | BLE：**先写两个身份特征（`8D08A420` + `CD7A71A0`）再读**才能读到数据；不写就读 → 相机立即断链 | 实测（推翻 14/15 号"需绑定"结论） | `19_BLE凭据链打通_先写后读_20261013.md:12-17` |
| 70 | BLE：可读出 INITIAL_INFORM（会话密钥）/ CAMERA_SSID / **CAMERA_WIFI_PASSWORD**；本机密码为空（两次不同会话密钥独立验证）；**无需配对/PIN/机身确认** | 实测 ×2 | `19_…:14-16,65-84` |
| 71 | BLE 握手**不稳定，约 1/2 概率在第 2 步后断链**，需重试 | 实测（4 次统计） | `19_…:104-118` |
| 72 | **BLE 身份注册 ≠ Wi-Fi accctrl 授权**：两道门独立；BLE 注册成功（写回调成功）但 Wi-Fi 侧仍 `err_user_refused`/`err_reject` | 实测 | `20_BLE身份与WiFi门独立_20261013.md:11-15,72-73` |
| 73 | 家网侧 `req_acc_g`（加密握手）回 **`err_param`** → APK 的 `req_acc_e` 加密路径在本机固件上**走不通** | 实测 | `20_…:14,69-70` |
| 74 | 相机**单控制客户端**：App 在线时控制类命令被挡，但**读类端点不受限**（`getinfo camsetting` 仍可全量下） | 实测 | `16_App在线状态信息获取_20261013.md:5-29` |
| 75 | `getinfo lens` 是**此前审计未枚举到**的可用类型，返回镜头型号 `LUMIX S 20-60/F3.5-5.6`、厂商、定点数、开关位 | 实测 | `16_…:37-45` |
| 76 | HTTP 服务指纹：`Server: Panasonic`（无版本号），Content-Type `text/xml`，错误页 XHTML DTD，`OPTIONS/PUT/DELETE` 回 500 | 实测 | `02_研究总报告_20261011/05-RCE与代码注入.md:10-16`；`logs/指纹/http_fingerprint.md:5-19` |
| 77 | 路径穿越无效：`GET /var/ /tmp/ /root/` 全 404；`?mode=getstate&value=../../etc/passwd` 照回正常 622B 状态 | 实测 | `logs/指纹/http_fingerprint.md:514-725` |

### 1.7 录制格式能力边界（穷尽性验证）

| # | 结论 | 等级 | 指针 |
|---|---|---|---|
| 78 | 本机可达上限 = **`mov_60p_200mbps_4k_10bit`（NTSC）/ `mov_50p_200mbps_4k_10bit`（PAL）**，200Mbps 4K 10bit，且机身菜单可用 | 实测 | `30_录制格式能力边界与操作教训_20261014.md:18-20,339-345` |
| 79 | `mov`（0x06）是**唯一容器门控字段**，mp4/mov 互斥 | 实测 | `04_隐藏格式_持久化成果.md:120-129` |
| 80 | **菜单变灰充要条件：`videoquality` 当前值 ∉ 机身菜单定义 `allmenu`** —— 双向对照验证（设入 C4K → 变灰；改回 4K → 恢复） | 实测 | `30_…:215-228`；`07_…:101-113` |
| 81 | **"flash 存安全值 + RAM 上隐藏档"的双轨方案不成立**：菜单读的是 **RAM 当前值** | 实测（证伪） | `30_…:229-237` |
| 82 | **5.9K / 6K / 400Mbps / a6k 全部不可得**（四种变量组合穷尽：PAL/NTSC × 视频模式/6K PHOTO 模式 × 12 次退避重试 × 3 个命名族） | 实测（穷尽性） | `30_…:81-141,150-157` |
| 83 | **6K PHOTO 模式原生能开 6K 片门** ⇒ 传感器硬件具备 6K 读出，视频域 5.9K 被拦是**固件按机型分层**，非硬件限制 | 实测（关键对照） | `30_…:172-179` |
| 84 | `mp4hevc` **并非不可用**：NTSC+mp4 态下有 2 档启用；项目当年"放弃 HEVC"是**主动取舍** | 实测 | `30_…:270-272`；`08_格式对照表_NTSC-MOV_20261013.md:118-120` |
| 85 | 存在**比 `allmenu` 更严格的第二层过滤**：`mov_30p_200mbps_5_9k_10bit` 在 allmenu 内却仍 `err_reject`（12 次重试不通过） | 实测 | `30_…:316-331` |
| 86 | S5 的 `mp4ed` = **MP4 + LPCM 1080p60 高码率档**（实拍 `P1000005.MP4`：1920×1080@59.94fps H.264 High ~96.6Mbps + PCM），**不是** S1H 的 4K 4:2:2 10bit ALL-I/400Mbps | 实测（实拍文件头） | `09_S1H参考包分析_mp4ed_20261013.md:46-54` |
| 87 | S5 **没有 S1H 的"添加到列表（My List）"机制** → 无法把隐藏档注册成常规菜单入口 | 实测（全量菜单扫描） | `09_…:85-86`；`30_…:311-312` |

### 1.8 exFAT 越界写 / 长文件名崩溃

| # | 结论 | 等级 | 指针 |
|---|---|---|---|
| 88 | ✅ 内核对簇号**不做归属校验**，释放路径**完全跟随卡上被篡改的 FAT 链值** | 实测（位图证据：注入 `FAT[111]=4` → 根目录簇 4 被释放） | `22_S5_exFAT越界写前置条件确认_20261013.md:11-20,49-56` |
| 89 | ✅ 内核对越界索引**存在 NULL 检查、会提前返回、不写内存** | 实测（决定性实验：索引 120 → 只报错不崩） | `23_S5_exFAT越界写实机确认_20261013.md:17,20-42` |
| 90 | ❌ **"越界内存写已在 S5 执行"——已撤回** | 撤回 | `23_…:18,30-38` |
| 91 | ✅ **360 个 240 字符长文件名目录项 → 相机开机反复重启**（纯目录项触发，不需真实数据） | 实测（四组矩阵 A/B/C/D） | `24_相机长文件名崩溃_定因_20261013.md:11-34` |
| 92 | 长名崩溃的**机制模型**：疑似定长缓冲 + 长度未校验（累加字节数在 58KB 与 86KB 之间存在一道墙）→ 更像**内存破坏类**而非普通 DoS | 推断（明确标注） | `24_…:38-51,84-86` |
| 93 | 长名崩溃作为攻击面**价值有限**（只是 DoS），作为**漏洞线索有真价值** | 判定 | `24_…:77-86` |

### 1.9 无线监看 / cam.cgi 控制面（26 号运行日志）

| # | 结论 | 等级 | 指针 |
|---|---|---|---|
| 94 | `camctrl type=touch` 坐标必须用 **`/` 分隔且必须带 `value2=on`**（逗号或缺 value2 ⇒ `err_param`） | 实测（APK 源码核对） | `26_本次运行日志_20261013.md:307` |
| 95 | **`camctrl type=focus` 是【变焦】不是对焦**（`tele-normal`/`wide-fast`/`focus-stop`…） | 实测 | `26_…:308` |
| 96 | **相机强制单流会话**：上次未 `stopstream` → 新 `startstream` 回 `err_busy` ⇒ 必须先 stop 再 start + 退避重试 | 实测 | `26_…:309` |
| 97 | **心跳与取景流互斥**：不发心跳约 13 秒后停流；最优 = 10 秒一次 + 状态走服务端缓存（实测 45 秒零停顿） | 实测 | `26_…:310` |
| 98 | 取景流规格：**640×432 MJPEG，18.7–19.8 fps**（UDP 49152）；`startstream` **无画质参数** ⇒ 640×432 是硬上限 | 实测 | `26_…:300,312` |
| 99 | 触摸对焦 100% 稳定（8/8）的决定性改进 = 对 `err_busy` **与** `err_reject` 都做退避重试（最多 8 次，0.5→3s） | 实测 | `26_…:629-639` |
| 100 | 根因揭示：相机对 **`req_acc` 有频率保护** → 高频重发触发「智能手机应用程序需要更新」→ `invalid login` → 必须重启相机；**这解释了本项目此前记录的"An invalid login occurred"** | 实测 | `26_…:540-557,590-592` |

---

## 2. 已验证可用的操作路径（原样命令 / 报文）

> 全部**原样抄录**。除特别标注"⚠️有副作用"外，均为只读或可逆。

### 2.1 通用前提（所有 cam.cgi 操作）

```
端点：http://<相机IP>:80/cam.cgi?mode=<m>&type=<t>&value=<v>&value2=<v2>
必带：User-Agent: LUMIX Sync          ← 否则多数命令被拒
参数顺序：mode → type → value → value2；为 null 的字段整体跳过（不拼空参）
健康探针：GET /cam.cgi?mode=getstate  → 必须 <result>ok</result>
```
指针：`02_研究总报告_20261011/research/PROTOCOL_AUDIT.md:10-34`；`03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md:16-18`

### 2.2 版本门（防回滚）

```http
GET /cam.cgi?mode=camctrl&type=fw_update_mode&value=VX.XX
User-Agent: LUMIX Sync
```
| value | 结果 |
|---|---|
| V2.90 | `err_fw_same` |
| V2.00 / V2.10 / V2.50 / V2.80 | `err_fw_old`（降级硬拒） |
| **V3.00 / V9.99** | **`ok`（放行到签名校验）** |

指针：`01_固件AES绕过…/Wi-Fi实机预言机与mode枚举实测-中文.md:27-44`；`02_研究总报告_20261011/08-WiFi预言机与密钥提取.md:8-19`
> ⚠️ 踩坑：`?mode=fw_update_mode&value=…`（缺 `camctrl` 包装）回 `err_param`。

### 2.3 固件上传协议（★ 核心，但末块从未成功）

```http
GET  /cam.cgi?mode=camctrl&type=fw_update_mode&value=V3.00     # 开门（回 ok = GATE OPEN）
GET  /cam.cgi?mode=startsenddata&type=fw&value=<file-size>     # 回 method=separate, bufsize=61460
POST /cam.cgi?mode=senddata                                     # multipart，每块 61192 B
GET  /cam.cgi?mode=requestsenddata                              # 每个非最终块后
GET  /cam.cgi?mode=endsenddata                                  # 最终块后 → 触发验签+刷写
GET  /cam.cgi?mode=abortsenddata                                # 取消
```
**multipart 报文原文**（`Content-Type: multipart/form-data; boundary=<B>`，`Connection: Keep-Alive`，`User-Agent: LUMIX Sync`）：
```
--<B>\r\n
Content-Disposition: form-data; name="filename"; filename="send"\r\n
Content-Type: application/octet-stream\r\n
Content-Transfer-Encoding: binary\r\n
Content-Length: <chunk-size>\r\n
\r\n
<chunk bytes>
--<B>--
```
- 边界 `B` = `"=====" + UUID.randomUUID() + "====="`（**46 字符**，进程内静态）
- **分块数学**：`1474 × 61192 + 1 × 41456 = 90,238,464`（`iA = bufsize − V() = 61460 − 268 = 61192`）
- **`method=once` ⟺ 总长 ≤ 61460**（单发、无 `endsenddata`）；**`method=separate` ⟺ 总长 > 61460**
- 重试语义：每命令 5 次；`err_busy` → 退避 1000 ms 重试

指针：`02_研究总报告_20261011/04-固件升级写路径.md:7-26`；`02_研究总报告_20261011/research/PANASONIC_FIRMWARE_UPDATE_PROTOCOL.md:95-190`；`PROTOCOL_AUDIT.md:114-131`

### 2.4 ★ CAMSET 设置块读写（**已实机持久化成功**的路径）

```http
# 读（65,533 B 实时数据；必须先退出机身菜单，否则 err_reject）
GET /cam.cgi?mode=getinfo&type=camsetting

# 写（method=separate）+ 分块
GET  /cam.cgi?mode=startsenddata&type=camsetting&value=65533   # → ok, method=separate, bufsize=61460
POST /cam.cgi?mode=senddata        # 块1: 61192 B, 块2: 4341 B
GET  /cam.cgi?mode=endsenddata     # → ok（全程 ~2s）
```
**改字段后必须重算校验和**：`byte[65532] = (256 − Σ(byte[0..65531])) mod 256`

复现（工作目录 `04_工具与脚本/campaign2`，AC 供电，写后拔电池终验）：
```bash
python3 persist.py verify                        # 只读：健康 + 实时 + blob 三字段
python3 persist.py restore --confirm             # 一键恢复隐藏格式（危险）
python3 persist.py flashwrite-file <blob> --confirm
python3 persist_quality.py <quality_name>            # 改质量（RAM），先校验 allmenu 是否声明
python3 persist_quality.py <quality_name> --confirm  # 并把质量固化到 flash
python3 container_switch.py mov --persist        # 0x5e=0x06（声明档），菜单恢复
python3 container_switch.py mp4ed / mov / status
```
指针：`08-WiFi预言机与密钥提取.md:23-34`；`07_隐藏格式持久化_追查_20261013.md:40-51,128-138`；`04_隐藏格式_持久化成果.md:55-62`；`09_S1H参考包分析_mp4ed_20261013.md:88-102`

**黄金字段值（实测）**：`65230=0x00`(ntsc) / `3062=0x06`(mov) / `6986=0x9b`(mov_60p_200mbps_4k_10bit) —— 这是**菜单不变灰**的安全组合。
指针：`31_录制格式持久化_受控复测_20261014.md:43`

### 2.5 录制格式 / 设置面（单向写 + 回读）

```http
GET /cam.cgi?mode=setsetting&type=<cmd_type>&value=<value>
GET /cam.cgi?mode=getsetting&type=<cmd_type>
GET /cam.cgi?mode=getinfo&type=allmenu     # 307,714 B，机身菜单定义（权威声明集）
GET /cam.cgi?mode=getinfo&type=curmenu     #  47,162 B，App 可见性快照（enable=yes/no 权威）
GET /cam.cgi?mode=getinfo&type=capability
GET /cam.cgi?mode=getinfo&type=lens
GET /cam.cgi?mode=camcmd&value=recmode     # 切拍摄模式（不动机身拨盘！）
GET /cam.cgi?mode=camcmd&value=playmode    # 切回放模式
```
指针：`30_…:44-52,253-259`；`16_App在线状态信息获取_20261013.md:31-45`

**6K PHOTO 激活配方（可逆）**：
```bash
curl -H "User-Agent: LUMIX Sync" "http://$S5_IP:80/cam.cgi?mode=setsetting&type=6k4k_photo&value=6k_burst"
curl -H "User-Agent: LUMIX Sync" "http://$S5_IP:80/cam.cgi?mode=setsetting&type=pictsize_burstspeed&value=6k_18m_30p"
curl -H "User-Agent: LUMIX Sync" "http://$S5_IP:80/cam.cgi?mode=setsetting&type=aspectratio&value=3:2"
# 读回核对
curl -H "User-Agent: LUMIX Sync" "http://$S5_IP:80/cam.cgi?mode=getsetting&type=6k4k_photo"
```
指针：`03_隐藏格式_可分发版_20261012/docs/03_opengate_6k_photo.md:44-63`；`03_…/reference/OPENGATE_FINDINGS.md:26-38`

**a6k 改坏容器后的恢复（实测 1 次即成功）**：
```http
GET /cam.cgi?mode=setsetting&type=videoquality&value=mov_60p_200mbps_4k_10bit
```
（写合法 mov 质量档会**同时把 `videoformat` 带回 mov**）指针：`30_…:118-124`

### 2.6 握手 / 会话（**必须按此做，否则会 invalid login**）

```bash
python3 state_check.py --ip $S5_IP                        # 只读健康探测（单次，绝不重试）
python3 safe_handshake.py --ip $S5_IP --verify            # 安全握手（v2，含陈旧 pending 清理）
python3 safe_handshake.py --ip 192.168.x.x --polls 6 --poll-delay 2.5
```
原样报文：
```http
GET /cam.cgi?mode=accctrl&type=req_acc&value=<UUID 4D454930-0100-1000-8001-<12hex>>&value2=<设备名>
# S5 回 4 字段： ok,S5-XXXXXX,remote,encrypted   ← 无第 5 字段 → 不存在 X-SESSION_ID
GET /cam.cgi?mode=accctrl&type=req_acc_can&value=<同一个 UUID>     # 终止路径清理陈旧 pending
```
**规则**：整个握手**只用同一个 uuid**；每个终止路径都用**同一 uuid** 发一次 `req_acc_can`；**绝不**用 `req_acc_can` 打断已 `ok` 的会话；**绝不**快速连发 `req_acc`；**只有裸 `ok`** 才算授权（`ok_under_research*` **不是**授权）。
指针：`03_隐藏格式_可分发版_20261012/docs/01_版本门与握手修复.md:41-83`；`20_…:157`

### 2.7 PTP 只读通道（0x9421 / 0x9605）

```bash
# macOS 首选（原生 ImageCaptureCore；libusb 在 macOS 上 bulk IN 会 EOVERFLOW Errno 84）
cd /Users/<user>/Documents/ChatGPT/S5逆向
./s5_ptp_dump ./ptp_out S5              # 0x9421 全量配置 dump（65,545 B）
./s5_ptp_dump ./ptp_out S5 fwup         # 0x9605 升级状态机只读
./s5_ptp_dump ./ptp_out_fuzz S5 fuzz    # 43 个安全只读探测
./s5_ptp_dump ./ptp_out_lp S5 lenprobe  # ⚠ 受控 length-DoS（最后跑，跑完拔插 USB）

# Linux（pyusb）
./.venv/bin/python s5_ptp_dump.py --list
./.venv/bin/python s5_ptp_dump.py --dry-run           # 打印 0x9421 命令字节，离线可跑
./.venv/bin/python s5_ptp_dump.py --tag 0x080000a1
```
**0x9421 命令字节**（原样）：`10 00 00 00 | 01 00 | 21 94 | <tid> | a2 00 00 08`
**PTP 容器格式**：`[0:4] length u32（含 12B 头）[4:6] type u16（1=命令/2=数据/3=响应）[6:8] opcode u16（响应时为返回码）[8:12] tid u32 [12:] params/payload`
**端点必须按接口描述符动态发现**（S5=0x82，S1M2=0x81，硬编码必挂）
指针：`scripts/USB-PTP/PTP_0x9421_dump_使用说明.md:38-105`；`S5_AES破解可行性评估_20261011.md:176,184-196`

### 2.8 BLE 凭据读取（★ 无认证，两步顺序不可颠倒）

```bash
cd 04_工具与脚本/campaign2
swiftc -framework CoreBluetooth -framework Foundation -o ble_wr ble_write_then_read.swift
./ble_wr      # 连接 → 写身份 → 读凭据（可重试）
```
**顺序（原样）**：
```
[A] 连接 + 枚举（9 服务 / 41 特征）
[B] 写 8D08A420-3213-11E6-8ACA-0002A5D5C51B = 原始 DLNA_UUID 字节
      值 = 4d454930010010008001020000025ad6
[C] 写 CD7A71A0-3213-11E6-8F56-0002A5D5C51B = 原始设备名（如 "MacBLE"）
[D] 读 03E23A31-A54C-40FA-A668-DE9ACDC910BB  (idx35 INITIAL_INFORM) → 会话密钥
[E] 读 E206A5C0-3214-11E6-AFE4-0002A5D5C51B  (idx5  CAMERA_SSID)
[F] 读 C97CF1A5-3C03-4290-8C1B-9E74B9500F54  (idx6  CAMERA_WIFI_PASSWORD)
```
**解码算法**（`H5/s.a()`）：`swap32(LE32(raw)) ^ key`，key = INITIAL_INFORM 前 4 字节大端；全 0 时默认 `0x9032782C`。
指针：`19_BLE凭据链打通_先写后读_20261013.md:39-84`；`15_蓝牙BLE协议逆向_20261013.md:20-92`

**写/读/通知路由全表**（原样 UUID）：`15_…:20-68`（写 13 条 type / 读 13 条 idx / 通知 12 条 idx + CCCD `0x2902=0100`；注册顺序 `10,8,30,13,14,29,25,31,32,40,43,53`）

### 2.9 exFAT 卡实验工具链

```bash
# 前提：相机格式化的 exFAT SDXC 卡；写前体检必须 K=0
sudo bash /tmp/s5exfat/s5_exfat_test.sh checkalloc /dev/disk8s1
sudo bash /tmp/s5exfat/s5_exfat_test.sh mkentries /dev/disk8s1 360 240 0
sudo bash /tmp/s5exfat/s5_exfat_test.sh mkspray  /dev/disk8s1 <数量> <num_ext> [起始序号]
sudo bash /tmp/s5exfat/s5_exfat_test.sh mkdeleted /dev/disk8s1 <数量>
sudo bash /tmp/s5exfat/s5_exfat_test.sh trimdir  /dev/disk8s1 <保留槽位数>
sudo bash /tmp/s5exfat/s5_exfat_test.sh setfat  /dev/disk8s1 <簇号> 0xFFFFFFFF
# 越界注入（第 2 级，有风险）
sudo bash /tmp/s5exfat/s5_exfat_test.sh go2 /dev/diskNsM
sudo bash /tmp/s5exfat/s5_exfat_test.sh verdict /dev/diskNsM
```
指针：`24_相机长文件名崩溃_定因_20261013.md:59-72`；`25_操作记录与风险手册_20261013.md:88-105`；`23_…:208-215`

### 2.10 ROM BACKUP 导出（只做 `DSC→SD`）

```bash
# ① FAT32 的 32GB 卡，插【卡槽 1】，接 AC
# ② 按住【回放 + AF ON + 方向右】同时开机 → 服务模式
# ③ ROM BACKUP → 选【DSC→SD】→ 确认（再次执行提示 overwrite）
# ④ 按住【AF ON + 方向右】关机 —— 且必须先拔掉那张 FAT32 卡
# ⑤ 卡插 Mac → 根目录出现 S5A.TXT / S5F.TXT / S5U.TXT
python3 -c "..."   # 每行 H### + 16 个 16 位字（逗号分隔十六进制）→ 解析后各 128 KB
```
sha256 基线：`S5A.TXT 849bcb30…` / `S5F.TXT 59314333…` / `S5U.TXT 6ef6656b…`
指针：`27_ROM_BACKUP导出成功与数据解析_20261013.md:180-195,81-87`

---

## 3. ★ 已证伪 / 已排除的路线（最重要）

### 3.1 权威清单原文：`02_研究总报告_20261011/09-已证伪路线.md`（47 行，逐条抄录）

| # | 路线 | 关闭原因（原文要点） | 指针 |
|---|---|---|---|
| 9.1 | **离线 AES / 密钥破解** —— 死 | XOR/RC4/AES-128/192/256（ECB/CBC/CTR），候选含 loader1 24B+64B、0x220 64B 块、SHA/MD5 派生；**130k+ 探测 0 命中**；真实 256KB keystream 熵 7.999（真随机密文）；48B 校验块不是无密钥哈希 → 极可能是带片内密钥的 HMAC/CMAC；PTool 旧 GH2 自嵌密钥法移植 120 组合全失败。⇒ 密钥固化在芯片硬件（OTP/eFuse/Crypto Engine/TrustZone），**固件文件内无密钥材料** | `09-已证伪路线.md:5-12` |
| 9.2 | **转接环 EF-L 路线** —— 死 | `EF-L 2.4.ecp`(59392B) → `efl_firmware.bin`(56500B)，**是标定数据镜像，非代码**。转接环是卡口 I2C 上的**独立从机 MCU**，与 MC801 走镜头通讯协议，**不进入 SoC 安全密码域**；环自带密钥是另一套机密，读走它 ≠ 拿到 S5 固件 AES 密钥 | `09-已证伪路线.md:14-18`；详证 `01_固件AES绕过…/04-转接环EF-L/EF-L-转接环固件-分析报告-中文.md:117-124` |
| 9.3 | **S1RM2 OOB 漏洞 —— 不迁移** | S1RM2 落 **SC2006A(A53)** 平台，S5 是 **MC801(A7)** 不同 SoC 家族 | `09-已证伪路线.md:20-24` |
| 9.4 | **WonderLantern padding-leak —— 不迁移** | 该手法针对另一平台特定解析实现，不适用 S5 MC801 的 GoAhead/PTP 解析器（本机已做等价 fuzz，无泄露） | `09-已证伪路线.md:26-28`；定量反证 `S5_AES破解可行性评估_20261011.md:541-546` |
| 9.5 | **编译 C / `LD_PRELOAD` RCE** —— 死 | GoAhead 不透传 `LD_*` 到 CGI 环境，或 `cam.cgi` 静态链接 | `09-已证伪路线.md:30-32`；`05-RCE与代码注入.md:18-23` |
| 9.6 | **Wi-Fi 调试后门 / 隐藏 mode** —— 死 | ~70 个候选调试/转储/闪读/密钥 mode 只读枚举**全回通用 `err_param`** | `09-已证伪路线.md:34-36`；`08-WiFi预言机与密钥提取.md:36-43` |
| 9.7 | 死路一览表（6 行） | — | `09-已证伪路线.md:40-47` |

### 3.2 补充排除清单：`06_S1R2移交_20261012/S1R2_已排除路线与风险备忘.md`（S1R2 实测，逐条抄录 + S5 适用性）

| # | S1R2 结论 | 依据 | 对 S5 的适用性（项目判定） | 指针 |
|---|---|---|---|---|
| 1 | ❌ 软件远程入口（USB PTP / Flow / WiFi / BT / HTTP）全部 fuzz 过：只有 DoS，**无 RCE**；富输入解析器（Flow XML、配置导入）都被"格式门控"挡死，格式已丢失 | S1R2 实测 | — | `S1R2_已排除路线与风险备忘.md:28-30` |
| 2 | ❌ **UART 串口是死路** —— 三证据叠加：U-Boot `CONFIG_BOOTDELAY=-2`（无控制台无延迟）+ 内核 `console=null loglevel=0` + `ENV_IS_NOWHERE` | S1R2 OSS 源码实测 | **⚠️ 不可直接套用**：S5 的 U-Boot 配置未读。**先做离线核验**（在 48 分区表 type=2 明文分区里找 env/BOOTDELAY/console 痕迹） | `S1R2_已排除路线与风险备忘.md:31-36`；`00_S5结合点与AES路径总结.md:50` |
| 3 | ⚠️ **SD.DAT / ROM-flashing 高风险别碰** —— 无只读/RAM-boot 模式，跑代码必须写 flash；写错 `pardata.par` = 不可逆毁出厂标定；S1R2 是 NAND（GoPro 的 eMMC 路径从未在 NAND 上验证成功） | S1R2 实测 | **⚠️ 保守处理**：S5 存储类型需拆机确认；若同为 NAND → 降级为 JTAG 之后的备胎 | `S1R2_已排除路线与风险备忘.md:38-43`；`00_S5结合点与AES路径总结.md:51` |
| 4 | ⚠️ `legacyboot`（U-Boot 从 SD 引导自核）命令存在但默认 bootcmd 不用，且需 U-Boot 控制台（被 console=null 堵死） | S1R2 | 同 UART 结论，取决于离线核验结果 | `S1R2_…:45-47` |
| 5 | ⚠️ 服务模式组合键：松下传统 GX85 = `[回放]+[AF/AE LOCK]+[右键]` 开机；ZS30 = `录像+MENU/SET` 开机 → SERVICE MODE；S1R2 组合键无公开资料 | 公开资料 | **✅ 本项目已命中 S5 组合键**（见 §1.5 第 50 条）→ 该项对 S5 **已不再是"未做"** | `S1R2_…:49-52`；`13_…:222` |
| 6 | ⚠️ 配置文件导入（`0x9422`）/ Flow XML：都是"格式门控"，且格式不在 App 里、在加密固件里 → 进不了解析器 | S1R2 | — | `S1R2_…:53-55` |

### 3.3 逐条：试了什么 / 怎么试的 / 结论 / 证据

| 路线 | 试了什么 · 怎么试的 | 结论 | 证据指针 |
|---|---|---|---|
| **改版本号绕过版本门** | 三条独立论证：① `comm_proto_ver=10.0` 只出现在 `getinfo capability`（相机→App 单向）② `accctrl req_acc` 握手**不携带任何客户端版本字段**③ 反编译 LUMIX Sync：`protoVer` 只是普通 getter，**无版本比较/拒绝分支**；"请更新 App"是通用连接失败文案 `msg_error_connect_app_need_update` | ✗ **彻底关闭**：没有可改的字段，也没有比对逻辑可绕 | `03_隐藏格式_可分发版_20261012/docs/01_版本门与握手修复.md:8-25` |
| **文件内改版本字段绕过签名** | 静态判定版本字段位置 + 覆盖关系（CRC32 覆盖 `data[0x200:]`；RSA 覆盖 `data[0x200:0x560EC00]`；ECDSA @0x220） | ✗ 改内层版本字段**必然破坏 ECDSA 与 RSA-4096**（无密钥无法重签） | `verify_logic_notes.md:63-84` |
| **上传"解密/校验预言机"（逐字节翻转试探）** | 阶段 0 跑 4 次，把**原封不动的 V2.9** 完整上传（1474 分片全 ok，末块 `err_busy`→`err_critical`，`abortsenddata=error`） | ✗ **无预言机**：相机对旧版本固件只给粗粒度 `err_critical`，不是 `err_fw_old/err_fw_same`；**无逐字节/逐分片反馈**，Wi-Fi 下 RSA 耗时被网络抖动淹没 → 阶段 1 的前提已失效；**建议停止上传预言机这条线** | `03-离线破解与上传预言机/oracle/README.md:73-90` |
| **固件升级写路径（重写 rootfs）** | 13 次 90MB 版本号篡改上传（每次 1474 分片，各 3,000–4,000 行日志）+ 2 次 CONTROL（未改动真 V29）+ 2 次 TESTA（末块单次 + 静置） | ✗ **从未触达一次成功的 `endsenddata`**。判别结论：**与内容无关**（CONTROL 发未改动真 V29 也失败）、**与节奏无关**（81ms / 150ms 都快于官方 138ms 仍失败）、**与状态无关**（拔电池全新重启后复现）。小样本探针（61192 B `once`、102648 B `separate`）**全被 `err_reject` 快拒**，无法用小样本逼近真实定址 | `02_研究总报告_20261011/04-固件升级写路径.md:28-59`；`logs/写路径/campaign.md:22621,22652,22726,22761` |
| **0x9606 地址覆盖（免擦除进入数据传送态）** | 离线反汇编 Tether 2.12 arm64 + 实机只读 0x9605 探测 | ✗ **本路线判定关闭**：要到"可测试状态"必须先发 `0x9406/0x00090013`（FWUP Request，**很可能先擦除目标区**）→ 高砖机风险且无兜底；收益上限只是"把已签名固件写到错误地址"。**与项目红线一致（永不发送 0x9406 子码）** | `28_PTP固件更新协议审计_20261013.md:8-16,122-134` |
| **exFAT 越界写提权** | ① 第 1 级：只改 4 字节 FAT（链尾指向卡内合法簇）→ 删照片 → 位图比对 ② 第 2 级：注入 `524290`（索引 128）③ 决定性实验：注入 `491522`（索引 120，必为 NULL） | ✗ **撤回"越界内存写已执行"**。决定性实验：索引 120 → 相机报「写入错误 请检查卡」但**未崩溃** ⇒ 存在 `if (vol_amap[i] == NULL) return -EIO;` ⇒ **内存写根本没发生**。原推理（"报卡写失败 ⇒ 内存写必然已执行"）**有漏洞** | `23_S5_exFAT越界写实机确认_20261013.md:17,20-42` |
| **堆喷命中越界槽** | 三轮：240 长名 / 120 长名 / 120 短名 + 篡改 `num_ext`；A/B 对照（B = 喷洒+越界注入，A = 喷洒+无注入） | ✗ **撤回**：A 组（去掉注入）**照样反复重启** ⇒ 崩溃不能归因于越界注入 | `23_…:166-174`；`25_操作记录与风险手册_20261013.md:219` |
| **5.9K 片门全开解锁** | 四种变量组合穷尽：PAL/NTSC × 视频模式/6K PHOTO 模式 × 每档 12 次退避重试 × 3 个命名族（`mov_*_5_9k_10bit` / `mov_5_9k_*_420_10l` / `mov_c24p_*_5_9k_10bit`） | ✗ **已证伪**：① 菜单层面无法解锁（`enable` 由固件按机型硬编码为 no）② 设备层面是假的（请求 5.9K 30p 实拍出 **4096×2160@59.94fps hvc1 ~195Mbps = C4K 60p**，不是 5888×3312） | `08_格式对照表_NTSC-MOV_20261013.md:124-158`；`30_…:81-97,150-157` |
| **"flash 安全 + RAM 隐藏"双轨方案** | flash 存 `0x9b`（allmenu 安全值），RAM 设为 `mov_50p_200mbps_c4k_10bit` | ✗ **实测证伪**：菜单立刻变灰 ⇒ **菜单读的是 RAM 当前值，不是 flash 值** | `30_…:229-237` |
| **把 6K PHOTO 换皮成录制格式菜单项** | 论证 + 实测 | ✗ 做不到：① 菜单不是设置是固件（`allmenu` 不存放在可写的 camsetting 里；对 blob 的所有写入都没改变过 allmenu 任何条目）② 换皮 = 改固件（AES + 签名 + 无 RCE + 写路径卡住）③ 就算能加也没东西可指向（6K/200M/30p 未作为 `videoquality` token 暴露，所有 `*_6k_*` 探测回 `err_param`） | `11_菜单条目注入可行性_20261013.md:39-64` |
| **HLG 照片 8K** | `setsetting hlg=8k` → 回 `ok`，但 play 模式读回仍 `off`（连已声明的 `full`/`4k` 在 play 模式也不持久） | ⚠️ **模式门控**：需在**照片（静态）拍摄模式**下才能真正写入并成像 —— **未闭合**（脚本已就绪但未在照片模式实拍确认） | `03_隐藏格式_可分发版_20261012/docs/02_隐藏功能.md:10-33` |
| **快门角度域** | `setsetting shtrspeed_angle=180` → 写 `180` 能读回 `180`，但 `shtrspeed` 不变、`f_and_ss_angle` 菜单项仍 `enable=no` | ⚠️ **空转，不生效** | `12_可写设置面审计_20261013.md:37` |
| **自定义照片风格 5–10 / V-Log L / HLG 隐藏档** | 逐项试写 + 读回 | ❌ `custom5..custom10` / `hlg` / `hlg_standard` / `hlg_bw` 回 `ok` 但读回仍是 `standard`；`vlog_l` 回 `err_param`；`hlg=8k/full/4k` 读回仍 `off` | `12_…:42-47` |
| **S5II 录制规格移植到 S5** | 对比 blob 布局 + 尝试 `S5II` 专属 tag/token | ✗ **移植没有可行性**：S5 tag 最大 `0x04b5`，S5IIX 有 `0x0534/0x0536–0x0540`（USB-SSD/ProRes/推流/HDMI RAW）；blob 布局、tag 编号、地址、编码管线**四层都不同**；且**已知地址在没有代码执行之前等于零** | `10_跨机型移植边界_20261013.md:14-24,48-64` |
| **S1H 的 400Mbps ALL-I 4K 移植到 S5** | 44 个 NTSC `mp4ed_*` 候选逐个 setsetting + 读回 | ✗ **0 个读回正常**（`err_critical`）；S5 的 mp4ed 顶多到 MP4+LPCM 1080p60 | `09_S1H参考包分析_mp4ed_20261013.md:39-40,54-64` |
| **`4kcrop` 相关** | `setsetting 4kcrop=20/40` | ❌ 被拒；**写 `4kcrop` 导致相机约 80 秒无响应**（自行恢复，副作用是 `videoquality` 掉回默认）→ **禁碰** | `12_…:38` |
| **UVC 零长度控制请求（S1R2 已证）** | S1R2：网络摄像头模式 VS probe `SET_CUR(wLength=0)` → 守护进程挂死，**跨断电不恢复**，须出厂重置 | ⚠️ 对 S5 只是**归档项**（低优先，属 DoS） | `S1R2_已排除路线与风险备忘.md:21`；`00_S5结合点与AES路径总结.md:54` |
| **BLE「握手能唤醒相机热点」** | 观察到握手期间开放网络出现在 t+25s | ✗ **证伪**：正确顺序复测时 `networksetup -setairportnetwork` 连续返回 `Could not find network` ⇒ 之前扫到的是**别人的**开放网络 | `20_…:104-110` |
| **「扫到开放网络 = 相机热点」** | 周边存在多个开放网络（信道 1/5/6/10） | ✗ **不可靠**，会假阳性。可靠判据只有两个：`setairportnetwork` 不报 `Could not find network`，或连上后拿到 `192.168.54.x` | `20_…:112-120` |
| **Windows MT7921 关联相机热点** | 穷举：配置文件连接(open/none)、关 MAC 随机化、指定 BSSID、`discovery_unsecure`、`temporary_profile`、复位射频、重启 wlansvc、强 PHY（ax/n/a-b-g）、强频段 | ✗ **是主机侧问题**（MT7921 驱动不吃这条非标准信标：`HT Operation` Basic MCS Set 全 0、`Extended Capabilities` 只 1 字节、Beacon Interval 200 TU）⇒ **应换主机栈（macOS/Linux）**，不要再在 Windows 上折腾 | `17_…:318-330`；`18_…:11-14` |
| **GoAhead buffer overflow（request-line/header/query）** | 溢出 fuzz（`overflow_fuzz.py`、`goahead_overflow.py`） | ✗ 失败（定制 CGI 不触发） | `03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md:60` |
| **LD_PRELOAD / EV-43360 / CVE-2017-17562** | `rce_ldpreload.py` + `payload.S`（MIPS 小桩，标记 `S5_RCE_PROOF`）多组合 | ✗ 相机一律回 `err_critical`，**无标记、无代码执行** | `05-RCE与代码注入.md:18-23` |
| **mode / getinfo 子类型的 file-op / exec / dynamic-load** | ~90 个 mode + ~110 个 getinfo 子类型枚举 | ✗ 全部 `err/reject`；无文件操作、无命令执行、无动态加载、无系统信息泄漏 | `04_camcgi_RCE面测绘.md:36-52`；`reference/OPENGATE_FINDINGS.md:46-50` |
| **整数溢出 / HTTP smuggling** | `crash_v3.py`（size=0xFFFFFFFF/2^31/2^32；smuggling 1–6） | ✗ 全 `err_critical`/`err_param`/`400`，无崩溃 | `06-崩溃与DoS.md:30-31` |
| **PTP 参数/TID 边界 fuzz（43 探测）** | `s5_ptp_dump.py fuzz` | ✗ 回干净错误码（0x2002/0x201d/0x2005/NAK）且**保持存活**；无 RCE | `06-崩溃与DoS.md:33` |
| **KA 崩溃循环** | `crash_cam.py`/`crash_v3b.py` 反复 startsenddata→senddata | ⚠️ 相机掉线但**快速恢复（0s）**，非可控崩溃 | `06-崩溃与DoS.md:32` |
| **S1R2 `f_fs.c` OOB 迁移到 S5** | S1R2 已实机（写 0x4141 生效、读 250 点）但可利用性=低（256 固定偏移 × 写 4B 且高 16 位恒 0；无堆喷 ⇒ 代码执行死路） | ⚠️ **不直接迁移**（不同 SoC 家族）；对 S5 只是"待审计"（拿到 MC801 内核 OSS 后对照 `current_alt_setting[16]`） | `S1R2两项成果_移交S5同事.md:110-204`；`00_S5结合点与AES路径总结.md:29-40` |
| **公开渠道获取原厂调整工具** | 全球公开网络 + 专业技术库系统排查（TSN、panasonic-europe-service、Elektrotanya、ManualsLib、remont-aud、Software Informer、GitHub、libgphoto2、GMaster） | ✗ **公开网络不存在可直接获取的松下原厂调整工具二进制**；所谓 `DIAS.exe` 条目是爬虫生成的空壳。⇒ 终止盲目的网络检索循环 | `S1M2_ROM_BACKUP与原厂维修协议逆向推导报告_20261009.md:22-28` |
| **上位机负责解密** | LUMIX Tether 2.8 / 2.12（macOS，含 arm64 反汇编）+ LUMIX Lab 3.1.0 APK 全量反编译 | ✗ **被证伪**：上位机完全不解密，只经 PTP 把 .bin 分块推给机身（0x9606 + 0x9607，块 `0x7d000`=512,000 B）；Tether 里的 AES/Camellia/ARIA/CMS/ECDH 符号**全部来自静态链接的 OpenSSL** | `S1M2_ROM_BACKUP…:104`；`williamwu1234_notes.md:90-93` |
| **从开源 GPL 源码找解密算法** | 松下官方开源 U-Boot 2019.07 + Linux 4.19.124 全量排查 | ✗ **彻底证伪**：源码中**完全不存在任何固件升级容器解析、签名核验或解密函数**；内核配置明确 `# CONFIG_CRYPTO_HW is not set` | `S1M2固件存储拓扑与离线解码技术边界终局报告_20261008.md:13-15,112` |
| **ROM BACKUP 当解密入口** | 维修手册交叉 + S5 实机导出 + 细粒度熵扫描 | ✗ 只导出 EEPROM 标定/参数分区（384 KB），**不含固件明文、不含 AES 密钥** | `27_…:154-158`；`S1M2_ROM_BACKUP…:53` |
| **S1R2 「0x9606 地址参数疑似不校验」列为第 3 优先路线** | 本项目已审计并关闭 | ⚠️ **分歧已在 29 号处理**：建议请 S1R2 说明如何在不触发 `0x00090013` 的前提下进入数据传送态；否则**维持关闭判定** | `29_S1R2报告启示与S5对称密钥分析_20261014.md:173-190,344-349` |

---

## 4. 已知陷阱与危险操作

### 4.1 绝对红线（NEVER）—— 三份文档一致

| # | 红线 | 出处 |
|---|---|---|
| 1 | **绝不真刷固件**（`S5___V29.bin` 仅 RECOVERY-ONLY） | `02_研究总报告_20261011/11-安全约束.md:13` |
| 2 | **绝不 `resetDevice`**（PTP 0x1005） | `11-安全约束.md:14` |
| 3 | **绝不执行 PTP 配置写回 `0x9422`/`0x9423`** | `11-安全约束.md:15` |
| 4 | **绝不执行 `0x9406` 的 8 个带副作用子码** + **`0x940d`（电源）** | `11-安全约束.md:16`；`S5_AES破解可行性评估_20261011.md:228-239` |
| 5 | **绝不发送 length 不符的 PTP 包**（除非是最后、已授权的 length-DoS 演示，跑完拔插 USB） | `11-安全约束.md:17` |
| 6 | **绝不连发 `req_acc`**；**绝不**用 `req_acc_can` 打断已 `ok` 的会话 | `03_隐藏格式_可分发版_20261012/docs/06_安全约束与风险.md:12` |
| 7 | **绝不在 `getstate` 非 `ok` 时继续任何写操作** | `06_安全约束与风险.md:13` |
| 8 | **绝不把相机留在"非基线"状态就断开**（每次写后必须回滚并验证） | `06_安全约束与风险.md:14` |
| 9 | **服务模式只读**，不点任何会写标定的项（地区后缀**一次性写入锁止**） | `25_操作记录与风险手册_20261013.md:23` |
| 10 | **ROM BACKUP 菜单里只动 `DSC→SD`**，其余项一律不碰 | `27_…:191` |
| 11 | **不要按 `DISP.` 键**（会解除 Strict 模式 ⇒ 地区后缀变成可改且仅一次机会） | `13_…:247-248` |
| 12 | **`4kcrop` 禁碰** | `25_…:24`；`12_可写设置面审计_20261013.md:38` |
| 13 | **⛔ 禁用 `a6k` 家族**（返回 `ok` 却静默把 `videoformat` 改成 `avchd`） | `25_…:320-333`；`30_…:105-124` |

### 4.2 砖机 / 卡死 / 数据损失（含恢复方法）

| 现象 | 触发 | 恢复 | 指针 |
|---|---|---|---|
| 需要**拔电池**才恢复的彻底卡死 | `senddata` 末块被拒 → 客户端**重试循环** → 相机升级状态机进入未处理分支 | 拔电池 | `06-崩溃与DoS.md:15-22`；`11-安全约束.md:23`（**别用 `Upload.stream()`**，用 `finalfix.py` 手动驱动末块） |
| 反复 brick / 卡死 | 多次 90MB 流送测试 | 拔电池 | `06-崩溃与DoS.md:43` |
| PTP 数据面挂死（相机本身不死） | length 不符的 PTP 包 | **拔插 USB** | `06-崩溃与DoS.md:11` |
| 相机反复重启（boot loop） | `DCIM/100_PANA` 里 **≥300 个 240 字符长文件名**目录项 | 拔卡 → `diskutil eraseVolume ExFAT LUMIX /dev/disk8s1` → 相机自己格式化 | `24_…:8-11,70-71`；`25_…:131-141` |
| 相机报「写入错误 请检查卡」+ 卡不一致（macOS 读文件 `Invalid argument`） | exFAT 越界注入（如 `FAT[112]=524290`） | 相机里重新格式化 | `23_…:88-92` |
| 照片"文件在、但无法访问/无法删除" | ⚠️ **项目自己的工具把卡写坏**：`alloc_one_cluster()` 只信分配位图，而相机位图**延迟写回**（未正常关机就拔卡 → 位图停在旧状态）⇒ 分配器拿到照片正在使用的簇 | 已修复：分配时**三重校验**（位图位==0 **且** 不在目录链上 **且** `FAT[clu]==0`） | `24_…:109-129` |
| 机身【录制质量】/【录制文件格式】整项变灰 | `videoquality` 当前值 ∉ `allmenu`（如 `mov_60p_200mbps_c4k_10bit` 的 `0x8b`、`mp4ed` 的 `0x07`） | 用 allmenu 已声明档覆盖（如 `mov_60p_200mbps_4k_10bit`） | `07_…:101-115`；`09_…:66-94` |
| 对焦灯常闪 | 在 ROM BACKUP 菜单里点了 `ADJFLAG→ALL F` | 重启恢复（**该事件已实际发生**） | `26_…:221-223,288` |
| `invalid login` / 弹「智能手机应用程序需要更新」/ 要求重启 | **高频重发 `req_acc`** | **只能断电重启** | `26_…:540-557`；`25_…:366-375` |
| 相机 ~80 秒无响应 | 写 `4kcrop` | 自行恢复（副作用：`videoquality` 掉回默认） | `12_…:38` |
| 相机 13 秒后断开 | BLE 保活定时器在每次读到密码时都新建 → 读循环轰炸 | 定时器**全局只建一次** | `20_…:152-157` |
| 发送未读的 PTP 命令会让 bulk 通道卡住 | — | USB 重插复位（相机本身不受影响，同段 Wi-Fi `getstate` 仍 ok） | `13_…:167-168` |

### 4.3 方法论陷阱（会污染结论的）

| # | 陷阱 | 真相 | 指针 |
|---|---|---|---|
| 1 | **`getstate` 忽略 type** | "带 type 的 getstate 回非 generic 响应" **不代表**该 mode 存在；有效判据 = "该 mode 回非 `err_param` 的专属响应" | `01-目标与环境.md:52`；`08-WiFi预言机与密钥提取.md:43` |
| 2 | **`ok` ≠ 生效** | 至少 6 次反例（`mov_*_5_9k_*`、`mov_24p_200mbps_6k_10bit` 等回 `ok` 却未生效）。**必须回读 `getsetting` 确认，最终用实拍文件头终判** | `25_…:290-303`；`30_…:377-387` |
| 3 | **`err_reject` 不是失败** | = 参数格式对但相机**当前状态不接受**；授权状态在 `ok` 与受限之间翻动 ⇒ **必须退避重试 8–12 次、间隔 2–3 秒**。单次调用会把成功误判为失败（实测 `mov_50p_200mbps_4k_10bit` 第 5 次才 ok） | `25_…:305-318`；`30_…:389-401` |
| 4 | **写完立刻回读 ≠ 持久** | `getinfo camsetting` 返回 **RAM 副本**；只有**断电重启后**的回读才代表 flash | `31_…:92-99` |
| 5 | **"相机报写入错误" ≠ "内存写已执行"** | 可能存在 NULL 提前返回；两种情形在相机屏幕上**完全一样** | `25_…:162-167` |
| 6 | **严禁用 `grep` 跨 `allmenu`/`curmenu` 做朴素差集** | 两文件性质不同（allmenu 是菜单树、666 处 `cmd_value`；curmenu 只有 `id`+`enable`、0 处 `cmd_value`）。朴素差集会得出「curmenu 独有 95 条」这类**伪结论**（已作废） | `30_…:239-254,453-454` |
| 7 | **不要把"设置持久"等同于"功能可用"** | 31 号报告明确：适用边界仅证明设置项可写并跨断电保留，**不构成该录制格式功能可用的证据** | `31_…:163-165,177` |
| 8 | **在断言"固件不持久某字段"之前，先独立验证写入确实落地** | 本项目的"mov 不持久"曾是 `persist.py` **上传协议 bug**（单次 65KB POST 从未落地）造成的误判 | `07_…:150-155,39-53` |
| 9 | **不要在 `cammode=play` 下做视频域实验** | play 模式下 `setsetting videoquality=<隐藏档>` 一律 `err_param`，且**已回 `ok` 的调用也不生效**（本项目两轮扫描因此整轮作废） | `30_…:40-42`；`25_…:345-352` |
| 10 | **读 `camsetting` 前必须退出机身菜单** | 相机停在菜单界面时 `getinfo camsetting` 一律回 `err_reject`（86 字节）；回到普通拍摄画面立刻恢复 | `07_…:121-123`；`25_…:19` |
| 11 | **模式切换走 API，不动机身拨盘** | 动机身拨盘会**断开远程连接** | `30_…:44-52`；`25_…:335-343` |
| 12 | **别用 macOS 造超长文件名做实验** | 相机不认（不 stat），且 macOS 会生成 `._` 副档名 ⇒ 每个文件变两个目录项、**名字还更长**，实验变量翻倍。造完测试文件必须 `rm -f ._*` | `25_…:273,276` |
| 13 | **块设备写入必须 `fsync` 落盘 + 用新 fd 回读** | 写入会停在页缓存，**拔卡就丢**（这是早期"补丁没生效"的真凶）；同一 fd 回读可能命中缓存 | `25_…:266-267`；`22_…:75-76` |
| 14 | **卡拔插后设备节点会变** | `disk8s1` → 可能变成 `disk9s1`；脚本需按"卷名 LUMIX + ExFAT + ≥60GB"自动重新识别 | `25_…:268`；`22_…:77` |
| 15 | **卡代次守卫** | 用 `BootChecksum + ClusterCount` 当卡指纹；基线/新位图指纹不一致就**拒绝裁决**（否则会把"重新格式化过的新照片"误算成释放簇） | `25_…:269` |
| 16 | **Boot Checksum 覆盖整个引导区 11 个扇区**（跳 106/107/112），**不是 512 字节** | 照 S1R2 报告字面只算 512B 会算错 → 相机判"卡不可用" | `22_…:74`；`25_…:265` |
| 17 | **exFAT 文件名在 entry 偏移 2** | File Name 目录项(0xC1) 前 2 字节是类型+标志 | `22_…:79`；`25_…:270` |
| 18 | **"自身链"要排除注入值** | 链集合若在打完补丁后才记录，会把注入值也算进去，**掩盖结论** | `22_…:80`；`25_…:271` |
| 19 | **bash 变量紧邻全角字符会被吞** | `$VAR（` 被当成变量名一部分，`set -u` 下直接 `unbound variable` —— 一律写 `${VAR}`（本项目因此导致**恢复函数从未执行**，需人工切回家庭网络） | `22_…:81`；`18_…:40-43` |
| 20 | **macOS 没有 `setsid`** | `setsid nohup …` 会静默不执行。正确写法：`( nohup bash script.sh args >/dev/null 2>&1 & )` | `18_…:38-39` |
| 21 | **macOS 原始磁盘设备双重保护** | Unix 权限（`root:operator`）+ TCC。**所有读写原始设备的命令必须由人在终端 `sudo` 执行**；`osascript` 提权到 uid=0 **仍报 Operation not permitted**；提权后的 root shell **访问不了 `~/Documents`** ⇒ 脚本要放 `/tmp` | `25_…:31-36` |
| 22 | **别用 S5II 的 blob / tag 值直写 S5 的 camsetting** | 布局不同，属盲写，**既无收益又增加变砖风险** | `10_跨机型移植边界_20261013.md:71-72` |
| 23 | **不要为点亮 ROM BACKUP 去贸然做"解除初始设置/Strict/地区后缀"** | 那是**不可逆的持久改动**（地区后缀单次写入锁止），且 ROM BACKUP 本身只给标定分区 | `13_…:114-116` |
| 24 | **导出文件含机身序列号** | 对外分发需脱敏 | `27_…:206`；`13_…:205` |
| 25 | **Windows 侧蓝牙射频默认 Off 时 bleak 直接报错** | 且**只有 Windows PowerShell 5.1 能 `Add-Type -AssemblyName System.Runtime.WindowsRuntime`**（pwsh 7 不行） | `17_…:166-170` |
| 26 | **`WLAN_INTERFACE_INFO` 必须 `CharSet=Unicode`；`WLAN_INTERFACE_INFO_LIST` 条目从偏移 8 开始（不是 4）** | 否则 `WlanScan`/`WlanGetNetworkBssList` 全返 1168（ERROR_NOT_FOUND） | `17_…:213-218` |
| 27 | **夸克网盘 `QuarkCloudDrive` 会抢占相机 USB 设备的 IOUserClient** | 表现为 dump 超时；需结束该进程（但本案结束后 dump 仍超时，因为真正原因是 PID 个性） | `13_…:131-132` |

### 4.4 写操作纪律（可分发版标准动作）

`03_隐藏格式_可分发版_20261012/docs/06_安全约束与风险.md:18-26`：健康前置 / 写后 sleep ~1.2s 再读回 / **必回滚**（记基线→写→读回→回滚→验证，四步缺一不可）/ 每批写后跑一次 `getstate` / 一次只动一个域 / 请求间留间隔（pace ~0.35s）。

---

## 5. 未解决 / 开放问题

### 5.1 `02_研究总报告_20261011/10-下一步与开放问题.md` 原文 4 条（逐条抄录）

| # | 开放问题 | 原文要点 | 指针 |
|---|---|---|---|
| 1 | **末块定址失败到底是"可恢复的 flash 状态"还是"硬损伤/磨损"？** | 决定 §10.1 是否还能在软件侧打通 | `10-下一步与开放问题.md:40` |
| 2 | **相机是否强制 Stubby RSA 验签（ENFORCING）？** | 决定 §10.3 路线 B 是否可写自编代码 | `10-下一步与开放问题.md:41` |
| 3 | **签名 oracle 的真实反应**（已签名 vs 改版本 vs 未签名） | 被 §10.1 阻塞，拿到一次 `endsenddata` 即可回答 | `10-下一步与开放问题.md:42` |
| 4 | **0x9103（PTP 未文档化操作码）具体是什么？** | 唯一新的 PTP 攻击面线索，值得只读深挖 | `10-下一步与开放问题.md:43` |

### 5.2 全部未闭合项汇总（跨全部 91 文件）

| # | 未解决项 | 现状 | 指针 |
|---|---|---|---|
| 1 | **CVE-2019-5096（multipart UAF → RCE，CVSS 9.8）** | **未测**（唯一剩余公开 RCE）；本机 CGI 正是 multipart，具备前置条件；需**堆控**，工程量大、极可能直接 brick | `05-RCE与代码注入.md:30,38` |
| 2 | **S5 是否同款 `f_fs.c` OOB** | 需拿到 MC801 内核 OSS 审计 `current_alt_setting[16]`（松下系内统一移植，命中概率不低） | `00_S5结合点与AES路径总结.md:37-40` |
| 3 | **S5 U-Boot 控制台是否可用（决定 UART 生死）** | 未做：在 48 分区表 type=2 明文分区里找 U-Boot env / `BOOTDELAY` / `console=` / `loglevel` 痕迹 | `00_S5结合点与AES路径总结.md:82` |
| 4 | **S5 存储类型（eMMC / NAND）** | 需拆机确认；决定 SD.DAT 路线的风险等级 | `00_S5结合点与AES路径总结.md:51,85` |
| 5 | **拆机只读取证（SoC 丝印 / JTAG 焊点 / Wi-Fi 模块型号 / 主板照片）** | 未做（列为 P1，全部硬件路径的先决条件） | `00_S5结合点与AES路径总结.md:80` |
| 6 | **长名崩溃的精确阈值** | 已收敛到 58–86 KB，可再做 1–2 次二分（`mkentries 300 240` = 72 KB）；是否对齐 64 KB 等整数未知 | `24_…:53,95-99` |
| 7 | **长名崩溃的机制** | 需调试通道（UART/JTAG）才能确认是"定长缓冲溢出"还是别的；目前只有"崩/不崩"一个二值信号 | `24_…:102-104` |
| 8 | **长名崩溃的隔离实验 T1–T3** | 未做（仅 10 个长名 / 240 个短名 / 240 个长名真 JPEG） | `23_…:184-189` |
| 9 | **exFAT 堆喷的下一步** | 需先修掉"文件本身导致崩溃"这个污染变量；换触发时机（删直前）；缩小规模（8–32）；内容改真 JPEG | `23_…:190-197` |
| 10 | **HLG 照片 8K 的实际成像** | 需在**照片（静态）拍摄模式**下重跑 `hidden_test_hlg.py` + 实拍核对 | `03_隐藏格式_可分发版_20261012/docs/02_隐藏功能.md:31-32` |
| 11 | **mp4hevc 隐藏档在 rec 模式下的实际成像** | 需 rec 模式开门 + 设档 + 实拍（脚本已就绪） | `02_隐藏功能.md:63-71` |
| 12 | **开篇 `mp4ed` 与普通 MP4 的实际画质差异** | 未做 A/B 实拍 | `09_S1H参考包分析_mp4ed_20261013.md:106` |
| 13 | **S5 的 `0x16e`（S1H 的 MP4ed 质量项）是否被使用** | S5 上改质量动的是 `0x122`，字段家族映射与 S1H 存在差异，尚未完全厘清 | `09_…:107-108` |
| 14 | **`videoquality` 保留与 SD 卡槽 1 挂载状态的机制** | 机制假设"相机依可用介质的写入能力限制录制画质"，仅 1 组对照（n=1），需重复 T1 条件确认；降档依据（容量？速度等级？挂载状态？）无直接证据 | `31_…:130-138,171-176` |
| 15 | **"仅写槽 0" vs "写全 13 槽"的因果** | 观测相关（反例 n=1 / 正例 n=2），**因果未确立**，列为待验证假设 | `31_…:109-116,174` |
| 16 | **历史"回退"观测是否可全部由分块修复前的单次 POST 缺陷解释** | 尚未逐例复核 | `31_…:175` |
| 17 | **录制可用性（31 号报告标注的"当前最大缺口"）** | 仅验证"设置可保留"，**未验证 200 Mbps 10-bit 的实际录制、码率与文件头** | `31_…:177` |
| 18 | **放大辅助 `change_disp_mag` 的门** | 参数已修正为官方规范（300–2000），错误码从 `err_busy` 变为 `err_reject`（= 参数格式已对），门未找到；待验证"相机菜单放大辅助开关" | `26_…:611-616,643` |
| 19 | **峰值 `asst_disp` 的参数格式** | 多种组合全 `err_param`，未确定 | `26_…:617,644` |
| 20 | **`req_acc_g` / `req_acc_e` 加密握手路径** | 本机固件上 `req_acc_g` 回 `err_param` ⇒ APK 的加密路径**走不通**（原因未知：固件未实现？未启用？） | `20_…:14,69-70` |
| 21 | **相机认为"已配对"的条件** | BLE 侧握手成功（身份写入 + 读凭据）≠ 相机认为已配对（屏幕持续显示"等待配对"）；领先假设 = 需要 **BLE 层已绑定(bonding)**，而 macOS CoreBluetooth 不触发配对、相机以"直接断链"而非回 `Insufficient Authentication` 回应 | `20_…:122-128,191-205` |
| 22 | **Windows/WinRT 绑定路径能否补齐最后一块拼图** | 未做（WinRT 有独立的 `DeviceInformation.Pairing`） | `20_…:205-206`；`17_…:196-201` |
| 23 | **SoftAP 模式的 `50001` / `60606` 服务识别** | `60606` 已知 = Panasonic 私有 UPnP 设备描述（`/Lumix/Server0/ddd`）；`50001` 是二进制协议且拒绝 HTTP，**未识别**；第二轮勘察因热点消失而无效 | `20_…:159-171`；`18_…:98-108` |
| 24 | **SoftAP 第二轮：`req_acc` 不确认时相机是否放行** | 未做（需相机热点重新开启；跑时留意相机屏幕，先不要点允许） | `18_…:126-134` |
| 25 | **`mode=getsetting&type=flash` 回 `ok`** | campaign.md 枚举中标为 `[INTERESTING]`，但**全部文档中无任何解释或跟进** —— 这是目前唯一未被解释的"非通用响应"残留项 | `02_研究总报告_20261011/logs/写路径/campaign.md:591` |
| 26 | **Chrome/网页侧 CSRF** | 未做：`cam.cgi` 为纯 GET，需从相机热点侧验证"外部页面能否盲发写命令" | `17_…:246` |
| 27 | **S5 与 MC801 的精确 die/核心数** | 未证实（推测 SC2000/M10v 一代 32-bit） | `02_研究总报告_20261011/research/hardware_attack_surface_notes.md:44-46` |
| 28 | **S5 是否有同形 `ffs` OOB** | 任务 6，未做 | `01_固件AES绕过…/00-总评估报告-中文.md:239-241` |
| 29 | **转接环支线（不依赖相机）** | 未做：抓 VILTROX 升级工具流量（性价比最高）/ 找 MCU 代码镜像 / 拆环探 SWD | `EF-L-转接环固件-分析报告-中文.md:260-264` |
| 30 | **微信原件与仓库副本逐字节一致性** | 未验证（TCC 阻挡） | `09_S1H参考包分析_mp4ed_20261013.md:109` |

---

## 6. 文档之间的矛盾（必须显式指出）

### ★ 6.1 版本字段偏移：`0x1C` 还是 `0x24`？`0x1C` 是版本号还是机型 ID？（**最严重、已影响实际操作**）

| 说法 A | 说法 B | 说法 C |
|---|---|---|
| `02_研究总报告_20261011/03-固件格式与启动链.md:38-48`：版本字段 = **BCD 4 字节 `[sub][major][sub][major]`**，**同时出现在外层 0x1C 与内层 0x2BC**；V29 实测 `90 02 90 02` = **V2.90**；改外层 0x1C 不改 CRC（在覆盖外）；**结论：版本号可以写大** | `01_固件AES绕过…/02-硬件攻击面/verify_logic_notes.md:63-84`（E7）：版本字段 = **0x24（外层）/ 0x2C4（内层）**，值 `0x07101450` = **BCD 时间戳 MMDDHHMM**（07/10 14:50），**不是明文版本号 "2.9"**；E10（`:100-106`）明确 **0x1C = 机型 id**（S5=`0x02900290`，S5m2=`0x15031503`，随机型变化） | `02_研究总报告_20261011/research/FIRMWARE_FORMAT.md:27-29`：**0x1C = 机型/板号**（两个 u16：0x0290,0x0290）；**0x24 = 时间戳/版本** |

**问题的严重性**：`campaign.md` 里**13 次版本号篡改上传全部改的是 0x1C–0x1F**，日志原文：
```
[upload] transform: version field -> V3.00 (BCD sub=0x00 major=0x03) @ 0x1C,0x1D,0x1E,0x1F;
         CRC32 unchanged 0x8E73AAC0 (0x1C is outside [0x200..end])
```
指针：`logs/写路径/campaign.md:1484,4450,7434,7472,7521,10510,13500,16488,19498,19556,22545,22598`（V3.00）+ `:22621,22652`（V2.90）

⇒ **若说法 B/C 正确（0x1C 是机型 ID），则这 13 次"版本号篡改"实际上篡改的是机型标识**，"改版本号"这个实验变量**从未被真正施加过**。§10.4 的开放问题 3（"签名 oracle 的真实反应"）因此在**实验设计层面就存在疑问**，而不只是被末块失败阻塞。
> **待上级裁定**：这是本项目一个**未被任何人指出的自相矛盾**。建议在权威文档中明确一个偏移，并复核 campaign 的实验有效性。

### 6.2 exFAT 越界写：`22_` 与 `23_` 结论直接冲突（22 未标注被推翻）

| 文件 | 说法 | 指针 |
|---|---|---|
| `22_S5_exFAT越界写前置条件确认_20261013.md` | 标题即"**前置条件确认**"；结论第 4 条：「⇒ 把注入值换成 **≥ 491522** 即触发越界索引 `vol_amap[≥120]`」（**由 2/3 推得**）；§4 明确给出第 2 级做法与判据 | `22_…:11-20,20,106-118` |
| `23_S5_exFAT越界写实机确认_20261013.md` | **决定性实验推翻**：索引 120（必为 NULL）→ 只报错不崩 ⇒ **存在 NULL 检查、内存写根本没发生**；③ 撤回 | `23_…:17,28,30-42` |
| `25_操作记录与风险手册_20261013.md` | 列为**已撤回结论**："S5 内核越界写已实机确认" ❌ 撤回 | `25_…:217` |
| `26_本次运行日志_20261013.md` | 本阶段产出第 4 条：❌ **撤回**"S5 越界写已实机确认"；未决项表："exFAT 越界写 → 判定为**不成立**（NULL 检查阻塞），不再投入" | `26_…:171,186` |

⇒ **`22_` 全文没有"本文结论已被 23 号推翻"的标注**（23 号自己在头部加了修订声明，22 号没有）。任何人只读 22 号会得到**相反的结论**。**强烈建议在权威文档中把 22 号标记为"已被 23 号 §0.5 推翻"**。

### 6.3 `vol_amap` 的 slab 档位：kmalloc-1024 还是 kmalloc-512？

| 说法 | 指针 |
|---|---|
| `22_…:96`：「❌ **必崩**：**kmalloc-1024** 的 slab 填充为 0」 | `22_S5_exFAT越界写前置条件确认_20261013.md:96` |
| `23_…:83-84`：「`vol_amap` 由 `kmalloc(120 × 8 = 960 B)` 得到 → **kmalloc-1024**」 | `23_…:83` |
| `23_…:155-164`（**推算更正**）：指针大小取决于机器位宽 —— **S1R2（64 位）** 239×8=1912 → kmalloc-2048；**S5（MC801，32 位）** **120×4=480 → kmalloc-512** | `23_…:158-163` |

⇒ 同一文件内部（23 号 §2 写 kmalloc-1024、§8.1 推算为 kmalloc-512）与跨文件（22 号 vs 23 号）都存在不一致。23 号自己指出"两种情况下 slab 内槽位数都是 128、索引边界都是 120–127，**从越界行为无法区分**"——这正是喷洒必须两个档位都铺的原因。**S5 到底是 32 位还是 64 位在内核层面未实测确认**（受制于固件加密，"不知道该机内核版本"，见 `21_…:33`）。

### 6.4 隐藏格式持久化：结论被**两次**翻转，且 `n` 的计数口径本身也不一致

| 时点 | 结论 | 指针 |
|---|---|---|
| 10-12 | `setsetting` 只写 RAM；**直接 flash 写入 → 三项全部持久** | `04_隐藏格式_持久化成果.md:12-20` |
| 10-13 早先 | 判为"格式字段不可持久"，H1 降至 ◐ | `07_…:150` |
| 10-13 定案 | 该现象由 `persist.py` **上传协议 bug** 造成（写入从未落地）；改用分块后 mov 保留 | `07_…:150-155` |
| **10-13（晚·续）** | 又称"持久化只对 `ntsc_pal` 成立、`videoformat` 断电后回落 mp4" | `07_…:11-12`；`31_…:13-16` |
| **10-14 受控复测** | 上述**未获重现（n=2）**：三项均保留；`videoquality` 与开机时 SD 槽 1 挂载状态相关 | `31_…:6-7,63-64,155-157` |

**附加矛盾（`n` 的计数口径）**：
- `04_…:24` 写「**样本量 n=2**，机制假设待重复实验确认」（指"videoquality 降档"这一观察）
- `31_…:153` 写「合并口径：两项试验共 **n=2**；其中三项全保留仅见于 **T2（n=1）**」
- `31_…:138` 写「该对照仅 **1 组**（T1 vs T2）」
- `25_…:395` 写「该对照仅 **1 组（n=1 组）**」

⇒ 同一件事在四处被记为 n=2 / n=1 / 1 组。**上游汇编时必须统一 n 的定义与口径**。

### 6.5 `mov` / `mp4` 档数：同一事实有 5 组以上不同数字

| 数字 | 出处 | 说明 |
|---|---|---|
| NTSC MOV **17** 档可见 / PAL 11 档 | `08_格式对照表_NTSC-MOV_20261013.md:14,22,38-45` | 早期实测（allmenu 19 − 2） |
| NTSC MOV **19** 档声明（allmenu）/ PAL 12 | `08_…:14,22` | allmenu 定义数 |
| NTSC MOV **18** 档启用 / PAL 12 | `08_…:49-50,110,166`；`30_…:263,447` | 10-14 重测（差 1 系是否含当前选中项） |
| allmenu 可执行 `videoquality` = **44**（mov **31** + mp4 **13**） | `30_…:256` | 正确口径 |
| mp4 常规档 **16** 个 → **13** 个 | `04_…:126`（错）→ `04_…:128`（更正为 13） | **「16」已确认是错误数字** |
| NTSC + mp4 实际启用 = mp4 **8** + mp4hevc **2** = 10 | `30_…:265,273`；`08_…:39,118-120` | 实测 enable |

**权威判据（项目自己的规定）**：`GET /cam.cgi?mode=getinfo&type=curmenu` 中 `enable="yes"` 的集合 —— **档数随【制式】与【容器】双重变化，单看一个数字没有意义**。
指针：`30_…:443-455`；`08_…:50`

### 6.6 `zboot` 的熵与性质：6.7（近空）还是 7.865（真加密）？

| 说法 | 指针 |
|---|---|
| `BOOT_FLOW.md:52,102,162` + `FIRMWARE_FORMAT.md:72`：zboot = 512B 0xFF 头 + **1536B 加密载荷（熵 7.865）**，是真实的 zImage 引导 stub | `research/BOOT_FLOW.md:52,102` |
| `siegfried82_notes.md:101-102`：S5 的 `zboot`（2KB，flags=3）载荷**几乎全 0xFF、熵仅 6.7、unique=255** —— "**不像 AES 密文**，更像带少量结构的近空区（或 flags 标注与 S1M2 语义略有出入）" | `01_固件AES绕过…/02-硬件攻击面/siegfried82_notes.md:101-102` |

⇒ 两处对同一分区的熵与定性描述**直接冲突**。BOOT_FLOW 的 7.865 是"512B 头之后的 1536B 载荷"的熵，siegfried82 的 6.7 可能是"整个 2KB 分区"的熵 —— **口径可能不同**，但两份文档都没有说明口径，readers 会得到相反印象。

### 6.7 端口面：station 模式下 60606 是否开放？

| 说法 | 指针 |
|---|---|
| `16_App在线状态信息获取_20261013.md:80-86`：对 `192.168.x.x` 扫 1–10000 + 常见高端口 → **开放端口：仅 80/tcp**；**没有 FTP、没有 DLNA、没有 RTSP** | `16_…:82-84` |
| `18_相机热点SoftAP侧勘察_20261013.md:88-94`：家网侧只有 **80**；热点侧 **80 / 50001 / 60606** | `18_…:90-92` |
| **`oracle_results.md` 实测（2026-10-10，station 侧）**：`port scan: OPEN [80, 60606]`（测试端口集含 60606） | `01_固件AES绕过…/03-离线破解与上传预言机/oracle/oracle_results.md:16`（亦见 `:4`、`:27` 等块的同类行） |

⇒ 10-10 实测在 station 侧 **60606 是开的**，但 16 号（10-13）说仅 80。`17_…:244` 也自认"若有 DLNA 则 60606 也应复测，见 16 号报告与 oracle 记录的不一致"—— **项目已知此矛盾但未解决**。可能解释：60606 是**按需启动**（DLNA 服务随连接状态起停），但**无文档证实**（此为本文推断）。

### 6.8 BLE 读取：需要绑定 vs 不需要绑定（两次反转，`15_` 的撤回本身被撤回）

| 文件 | 结论 | 指针 |
|---|---|---|
| `14_…:43-53` | 一读即被断链；「**相机对未加密链路拒绝属性读并断链**……**读取需要绑定**」；初版"需要 App 握手"**已被推翻** | `14_…:43-54` |
| `15_…:94-113` | 撤回"无认证泄露 Wi-Fi 凭据"：「**不能宣称"近场任意设备可无认证读取相机 Wi-Fi 凭据"**。该结论**未获实机支持，予以撤回**」 | `15_…:110-113` |
| **`19_…:1-17,88-98`** | **推翻 14/15**：「**"一读即断"的真因是协议顺序，不是链路加密**」；「**已实机确认：任何在 BLE 范围内的设备，无需配对、无需 PIN、无需机身确认，只要按正确顺序（先写身份、再读），即可读出相机的 Wi-Fi SSID 与密码**」 | `19_…:12,90-98` |
| `20_…:191-205` | 但 Wi-Fi accctrl 门仍打不开；领先假设 = **相机要求 BLE 层已绑定(bonded)** 才肯放行（这适用于 **Wi-Fi 控制面**，不适用于 BLE 凭据读取） | `20_…:191-205` |

⇒ **14/15 号的安全结论是错的，而 19 号的更正只写在 19 号里**。只读 14/15 的人会得到与事实相反的安全判断。**上游必须把三段合并成一条时间线**。

### 6.9 BLE 特征数：41 vs 44

| 说法 | 指针 |
|---|---|
| macOS CoreBluetooth 报 **41** 特征 | `15_…:100,119,130` |
| Windows WinRT 报 **44** 特征 | `17_…:283-285` |
| `14_…:33` 写"约 **44** 个特征"（macOS 侧文档却写 44） | `14_…:33` |

**项目自己给出的解决**：`17_…:283-285`「这解决了文档内部"41 vs 44 特征"的不一致：macOS CoreBluetooth 报 41，Windows 报 44；两者差在 GAP/GATT 通用服务与部分分支特征是否暴露，**以"约 41–44，视主机栈而定"为准**」。
⇒ 但 `14_…:33` 在同一份 macOS 文档里写 44、与 `15_…:100` 的 41 自相矛盾，`17_` 的结论未回填到 14/15。

### 6.10 平台型号归属：`10_…:11` 把 S5II 与 S1M2 混为一谈

| 说法 | 指针 |
|---|---|
| `10_跨机型移植边界_20261013.md:10-11`：「**S5II / S1M2 一代 = SC2006A / MC8243（4×Cortex-A53，64-bit）**」 | `10_…:10-11` |
| `research/FIRMWARE_FORMAT.md:91`：三平台对照：**S5=MC801、S5M2=MC8223、S1M2=MC8243** | `research/FIRMWARE_FORMAT.md:91` |
| `siegfried82_notes.md:10-11`：「**MC8243 既不是我们 S5 的 MC801，也不是我们对照样本 S5M2 的 MC8223** —— 三者是三个不同平台」 | `siegfried82_notes.md:10-11` |
| `williamwu1234_notes.md:21-23`：「**芯片 = MC8243，不是 MC8223**。`MC8223` 是 DC-S5M2 的芯片」 | `williamwu1234_notes.md:21-23` |

⇒ `10_…:11` 把 **S5II(MC8223)** 与 **S1M2(MC8243)** 归为同一型号，与三处文档冲突。虽不影响 `10_` 的主结论（"换代平台不可移植"仍成立），但**型号-芯片对照表在上游必须统一**。

### 6.11 ROM BACKUP 变灰原因：文档内部自我更正，但旧假设仍在文件前部

| 说法 | 指针 |
|---|---|
| 「最可能：Initial Settings 未解除 / Strict 模式未释放」（列为第 1 位）；「用户反馈：点 ROM BACKUP 无任何提示文字（灰态）。这与**第 1 条最吻合**」 | `13_…:51-62` |
| 「**不是**"未解除初始设置"！」「门控是 SD 卡的文件系统类型」；「**这推翻了我此前排在第一位的假设**」 | `13_…:182-191` |
| 同一文件 §7.4 又说「最可能是**尚未执行"解除初始设置"**」 | `13_…:106-112` |

⇒ `13_` 内部 §4/§7.4（旧假设）与 §9.2（更正）并存，且 §7.4 在文件位置上**晚于** §4 但**早于** §9.2。**读者按顺序读会先接受错误假设**。

### 6.12 死路一览表引用的是"参考报告 §4/§5/§6/§9"，但行号指向不明

`09-已证伪路线.md:40-47` 的死路表用「参考报告 §6/§9」「参考报告 §4」「§05, `logs/RCE/`」「§08.2, `logs/指纹/`」这类**相对章节号**。这些章节号对应 `参考报告/S5_AES破解可行性评估_20261011.md`（§4 = `:138`、§5 = `:170`、§6 = `:330`、§9 = `:422`、§10 = `:521`）与 `05-RCE与代码注入.md` / `08-WiFi预言机与密钥提取.md`。**没有一处给出可直接跳转的文件名 + 行号**，是"读不全"的典型成因之一。

### 6.13 `0x9421` 配置大小的两个数字常被混用

| 数字 | 含义 | 指针 |
|---|---|---|
| **65,545 B** | PTP `0x9421` **DATA 容器**总字节（含 8B tag+len）→ `config_0x9421.bin` | `S5_AES破解可行性评估_20261011.md:203` |
| **65,533 B** | `camsetting` **blob** 本身（= `startsenddata&type=camsetting&value=65533` 的 value，= `payload[0:4]=0xfffd`） | `08-WiFi预言机与密钥提取.md:24-26`；`07_…:40-41` |
| 两者混用 | `07_…:24` 写"读写相机**设置分区**（65,533 字节，`type=camsetting`）"；`06_S1R2移交/00:18` 写"S5 `camsetting`（65,533B，getinfo/senddata）" | — |

⇒ **差 12 字节**（PTP 容器头）。文档中常以同一句话混指两者，**字段偏移（如 65230/3062/6986）只在 65,533 口径下成立**，用 65,545 口径会错位 12 字节。

---

## 7. 特别关注专题汇总

### 7.1 固件格式与启动链（一页速查）

```
S5___V29.bin = 90,238,464 B (0x560EE00)   SoC = MC801
┌ 0x000000  0x200   外层 UPD 头（UPD\0 魔数；0x0C 芯片型号；0x38 data_start=0x200；0x3C len=0x560EC00；0x40 CRC32=0x8E73AAC0）
├ 0x000200  0xA0    "panasonic" + 64B ECDSA P-256 (r+s) @0x220
├ 0x0002A0  0x40    内层 UPD 头（字段与外层一致）
├ 0x0002E0  0x0C    目录头：0x1400 / 0x560D800 / 0x30(=48B 校验块尺寸)
├ 0x0002EC  0x1140  分区表：48 条 × 92B（物理至 0x142C，与数据起点 0x1400 重叠 44B）
├ 0x001400  0x560D800 分区数据（41 加密 / 7 明文）
└ 0x560EC00 0x200   RSA-4096 签名（= S5___V29.sig）
   92B 条目：name[12] | off u32 | size u32 | load_addr u32 | type u32 | SHA256(明文)[32] | IV[16] | pad[16]
   type=2 ⟺ IV 全零（明文）   type=3 ⟺ IV 非零（加密）   48/48
   启动：BootROM → 三重验证 → 48 分区表 → 搬 90KB 引导块入 RAM → loader1(0x0) → loader2(0x1000) → loader3(0xA800) → program(0x80000) → Linux(zboot→dtb→zimage→rootfs1/2)
```
指针：`research/FIRMWARE_FORMAT.md:8-58`；`research/BOOT_FLOW.md:31-96`

### 7.2 密码学结论表

| 密钥/密钥源 | 算法 | 用途 | 状态 | 证据 |
|---|---|---|---|---|
| MC801 片内主密钥（OTP/eFuse/Crypto Engine/TrustZone） | AES（CBC/CTR 类，按分区独立 IV） | 41 个 type=3 分区解密 | **未解出**（软件侧终止；非密钥空间穷举证明） | `09-已证伪路线.md:5-12`；`S5_AES破解可行性评估_20261011.md:416` |
| ECDSA P-256 公钥（BootROM/OTP） | ECDSA P-256（r+s 64B @0x220） | 容器验签 | **公钥不在文件内**；r,s 合法标量已实测 | `verify_logic_notes.md:15-43,57-59` |
| RSA-4096 公钥（BootROM/OTP） | RSA-4096 裸签名/PSS（尾块 512B，非 PKCS#1 v1.5） | 容器验签 | **公钥不在文件内** | `verify_logic_notes.md:97-99` |
| 分区表 `SHA-256(明文)` @+0x1C | SHA-256 | 明文完整性校验（相机可在解密后比对） | 已确证字段含义（`lens_hist` 阳性对照） | `research/FIRMWARE_FORMAT.md:89` |
| 48B 校验块（旧称谓） | 未知，**非** SHA-384/256/1/MD5/CRC 的任何无密钥组合 | — | 极可能是带片内密钥的 HMAC/CMAC | `oracle/README.md:11` |
| GH2 旧机型密钥切片 | AES-128-CBC，`key[i]=input[0x200+i*0x200+table[i]]`，`iv=input[0x80:0x90]`，实测 key=`90b43b5ce34c6e667fb28376b5fa5c27` | GH2 固件解密 | **仅 GH2 有效**；S5 移植 120 组合全失败 | `S1M2_解码突破记录.md:34-41` |
| BLE 会话密钥 | 「字节置换 + 32 位 XOR」（4 字节一块，`swap32(LE32(raw)) ^ key`） | BLE 凭据编解码 | **已完整还原 + Python 回环自检通过**；默认 key `0x9032782C` | `15_…:83-92` |
| CAMSET 校验和 | `(256 − Σ) mod 256` | 设置块篡改检测 | **已反推并验证，可伪造** | `08-WiFi预言机与密钥提取.md:28-32` |

### 7.3 exFAT 越界写这条线是什么？结论是什么？

**这条线是什么**：来自 S1R2 团队的一条**纯软件提权链** —— 用一张只改 4 字节 FAT 的 SD 卡，让相机内核在自己的内存里执行一次越界索引 → 位清除写 → 提权(root) → 从 RAM/mtd 取解密后的内核与 rootfs（**不需要 AES 密钥**）。若在 S5 成立，则项目原 **P4（拆机 JTAG dump RAM）可降级为备选**。
指针：`21_S1R2_exFAT越界写对S5的意义_20261013.md:8-24`；`22_…:126-132`

**S5 上的结论（三步，逐级收紧）**：

| 步骤 | 结论 | 等级 | 指针 |
|---|---|---|---|
| ① 前置条件 | ✅ **成立**：内核释放文件簇时**完全跟随卡上被篡改的 FAT 链值**，**不做"该簇是否属于本文件"的校验**。实机证据：`FAT[111]=4` → 删照片后**根目录簇 4 被释放**（不属于被删文件自身链） | 实测 | `22_…:11-20,49-56` |
| ② 越界索引处有 NULL 检查 | ✅ **成立**：注入 `491522`（索引 120，必为 NULL）→ 相机报「写入错误 请检查卡」**但未崩溃** ⇒ 存在 `if (vol_amap[i] == NULL) return -EIO;` | 实测（决定性） | `23_…:17,20-42` |
| ③ "越界内存写已在 S5 执行" | ❌ **撤回**：原论证（"报卡写失败 ⇒ 内存写必然已执行"）**有漏洞**——若有 NULL 提前返回，"写入错误"同样会发生且**根本没碰内存**；两种情形在相机屏幕上**不可区分** | 撤回 | `23_…:18,30-42` |
| ④ 堆喷命中越界槽 | ❌ **撤回**：A/B 对照（A 组去掉注入）**照样反复重启** ⇒ 崩溃不能归因于越界注入 | 撤回 | `23_…:166-174` |
| ⑤ 现状 | **不成立（NULL 检查阻塞），不再投入** | 判定 | `26_…:186` |

**距 root 差什么**：差"**目标地址**"—— 现在只能写到"相邻堆对象里某个指针的 `b_data`"上，**不可选**。下一步方向：① 堆喷控制相邻槽（`num_ext ≈ 15–30` 使 `get_entry_set_in_dir` 落 kmalloc-1024/512）；② 扫描可用槽位画堆布局；③ 建立任意写 → 提权。指针：`23_…:126-131`

**方法论警告（项目自己提出，且适用于 S1R2）**：S1R2 报告也把"相机报写入错误"当作"内存位清除已执行"的判据。**若其代码同样含 NULL 检查，该判据在任何机器上都不可靠**。指针：`23_…:40-42`

**附带发现（独立于 exFAT 位图漏洞）**：长文件名崩溃（见 §1.8 第 91–93 条）—— 项目自己评价它"作为漏洞线索**有真价值**（长名累加 → 定长缓冲溢出，属内存破坏类，比被 NULL 检查挡住的 exFAT 位图路径**更接近可利用**）"。指针：`24_…:82-86`

### 7.4 PTP / USB / SCSI 通道

**操作码全表（已识别）**：

| opcode | 含义 | 副作用 | 状态 | 指针 |
|---|---|---|---|---|
| 0x1001 | GetDeviceInfo | 只读 | 已用（225 B：DC-S5 / 2.9 / SN） | `07-USB-PTP-SCSI.md:9` |
| 0x1002 / 0x1003 / 0x1004 | OpenSession / CloseSession / GetStorageIDs | 会话 | 已用 | 同上 `:10-12` |
| 0x1005 | ResetDevice（标准） | 副作用 | **被识别但拒绝（0x2008 NoMemory）**；红线 | `S5_AES破解可行性评估_20261011.md:470` |
| 0x9001 / 0x9002 / 0x9101 | — | — | 被识别但缺参数（0x2005 InvalidRequest） | `:471` |
| 0x9102 | — | — | 被识别，参数无效（0x201d） | `:472` |
| **0x9103** | **未文档化** | — | ★★ 被识别（0x2003 SessionNotOpen），**唯一新攻击面线索** | `:473` |
| 0x9104 | GetSyncList | 只读 | 已用（32 B） | `07-…:13` |
| 0x9402 / 0x9408 / 0x940a / 0x940e / 0x940f / 0x9414 | 属性派发 / 视频滤镜 / 省电 / 回放 / 变焦 | 只读（部分） | Tether 反汇编识别 | `S1M2_ROM_BACKUP…:100-108` |
| 0x9406 | Setup_Ctrl（**8 个子码全为动作**） | **写/毁数据** | **红线，绝不发送** | `S5_AES破解可行性评估_20261011.md:228-239` |
| 0x940d | Power_Ctrl（子码 0x0a000011 = PowerOff） | 电源 | **红线** | `:106` |
| **0x9421** | 全量配置 dump | 只读 | ✅ **已 dump 成功（65,545 B）** | `07-…:14` |
| 0x9422 / 0x9423 | 配置写回（tag 0x080000a2 / 0x080000a1） | **写** | **红线，未执行** | `07-…:15`；`S1M2_ROM_BACKUP…:114-115` |
| 0x9603 | ChgEvntType（切事件管道到 FWUP 模式） | 状态 | 识别 | `S1M2_ROM_BACKUP…:121` |
| 0x9605 | Get_Event_Info（升级状态机） | 只读 | ✅ 已查询（idle 全零） | `07-…:16`；`28_…:60-78` |
| 0x9606 | Send_Data_Info（`[Size][Addr][DataType]`，32位12B / 64位16B） | 潜在写 | **实测无任意地址写原语**（地址由机身下发） | `07-…:17`；`28_…:29-58` |
| 0x9607 | Send_Data（500 KiB = `0x7d000` 分块） | 写 | 识别 | `28_…:26` |
| 0x9703 / 0x9706 / 0x9707 / 0x9112 | — | — | 无 RAM 读回 | `S5_AES破解可行性评估_20261011.md:338` |

**0x9406 的 8 个子码（本次补全，旧表缺 2 个）**：
`0x00090011` MenuSave / `0x00090012` SD_Format / **`0x00090013` FWUP Request（本次新增）** / **`0x00090014` FWUP UPDATE（本次新增）** / `0x00090015` SensorCleaning / `0x00090016` PixelRefresh / `0x00090017` FirmUpAbort / `0x00090018` ResetSetting
指针：`28_PTP固件更新协议审计_20261013.md:83-95`

**完整升级状态机**：
```
IDLE → 0x9406/0x09000013 FWUP_PREP [PREPARE] ← 状态变更（不做；疑似先擦除）
     → 0x9605 evt 0x41000013 Ready → 拿 addr + size + status [READY]
     → 0x9606 Send_Data_Info(total_size, target_addr, data_type) [DATA_INFO]
     → 0x9607 Send_Data × N，每块 0x7d000（500 KiB）[DATA_TRANSFER]
     → 0x9406/0x09000014 FWUP_DONE [UPDATE/COMMIT]
     → 0x9605 evt 0x41000015 CmpInfo → 完成 status [CMP] → IDLE
     任一时刻可 0x9406/0x09000017 FWupAbort 中止
```
指针：`S5_AES破解可行性评估_20261011.md:272-283`；`28_…:99-118`

**SCSI / 内核源码面**：松下的 `pvc_mass_storage`（`drivers/usb/gadget/legacy/pvc_mass_storage.c`，2470 行）**只做 CBW/CSW 搬运，CDB 的实际解析/执行由松下用户态/固件完成**（`ms_ioctl`(2334) 用 `PVCUSB_GET_DATA` 把 CBW（含 16 字节 CDB）交给用户态）。⇒ "恶意 USB 主机 → 相机本体"的解析面在**用户态**，不在内核。
指针：`01_固件AES绕过…/06-USB-SCSI源码/usb-scsi-src-export/README.md:83-91`

### 7.5 各代平台差异（MC801 / MC301 / S1M2 / S5M2 / S1R2 / S1H）

> ⚠️ **"MC301" 在 `01_研究报告/` 全部 91 个文件中 0 次出现**（本次全文检索确认）。项目文档中的平台代号只有 MC801 / MC8223 / MC8243 / MC8244 / MC7231 / MC8241。**上游若需要 MC301，需从其他块获取。**

| 机型 | 芯片 | 核心 | 内核 | 分区数 | 设置块 | 结局 | 指针 |
|---|---|---|---|---|---|---|---|
| **DC-S5**（本项目） | **MC801** | 32-bit（A7 级，推测 SC2000/M10v） | 未知（固件加密，离线看不到） | **48** | **65,533 B / 831 记录** | 软件侧封死 | `research/FIRMWARE_FORMAT.md:91`；`10_…:19-21` |
| DC-S5M2 | **MC8223** | — | — | — | **2,252,861 / 2,253,165 B / 966–978 记录** | 未研究 | `research/FIRMWARE_FORMAT.md:91`；`10_…:18` |
| DC-S1M2 | **MC8243**（Milbeaut 第 9 代 / M20V） | 4×Cortex-A53（64-bit） | — | 62 | 9,197,325（SD 形态）/ 9,197,337（PTP 形态） | 49 个加密组件**无明文** | `siegfried82_notes.md:10-14`；`S1M2固件存储拓扑…:53` |
| DC-S1RM2 (S1R II) | **MC8244 / SC2006A** | 4×Cortex-A53 | **4.19.124 + 松下移植** | — | CAMSET01.DAT 9,197,325 B | 有实机漏洞（f_fs OOB + UVC DoS），**无 RCE** | `06_S1R2移交…/S1R2两项成果…:3`；`S1RM2-ffs-OOB…:28-29` |
| DC-S1H | 未标注（MC801 一代） | — | — | 53 | 66,933 B / 848 记录，记录起点 0x34 | `mp4ed_25p_400mbps_4k_10bit` **实拍成功**（4K25 422 10bit ALL-I + LPCM） | `05_Panasonic_hidden_format_参考/研究报告.md:16,72-89`；`evidence/static_review/…:9` |
| DC-S9 | SC2006A（OSS 确认） | — | — | — | — | 与 S1RM2 同 OSS 源 | `S1RM2-ffs-OOB…:32` |
| Leica SL3 | **MC7231** | — | — | — | — | 与 S1M2 同一 UPD 封装家族（共享部分明文，无算法/密钥） | `williamwu1234_notes.md:100-102` |

**跨平台可移植性边界（三层）**：
- ✅ **同代同族**（S1 / S1H / S5，MC801 一代）：值得挖 —— 我们已借此拿到 **MOV 全家族** 与 **`mp4ed`**
- ⚠️ **同代不同定位**：token 可能"读回正常"却录不出东西（S1H：16 候选里仅 2 个出真媒体）
- ❌ **换代平台**（S5II / S1M2 / S1RM2，SC2006A 一代）：token、tag、地址、编码管线**四层都不同**，**移植没有可行性**

指针：`10_跨机型移植边界_20261013.md:59-64`

### 7.6 "已排除"安全路线总清单（一页）

**A. 密码学/密钥类（全部死）**
1. 离线 AES 穷举（130k+ 探测 / XOR / RC4 / AES 全模式）— `09-已证伪路线.md:5-12`
2. 文件内派生密钥穷举（5,240 候选 × 3 IV）— `S5_AES破解可行性评估_20261011.md:79`
3. PTool GH2 自嵌密钥切片移植（120 组合）— `09-已证伪路线.md:11`
4. IV 派生/预测（0/41）— `S5_AES破解可行性评估_20261011.md:80`
5. 跨版本差分（同偏移密文相等率 ≈0.39% = 随机）— `S5_AES破解可行性评估_20261011.md:99-114`
6. WonderLantern padding-leak（熵 7.999 ≠ 0）— `09-已证伪路线.md:26-28`
7. 真实 AES 密钥恢复测试（211 候选，0 命中）— `S5_AES破解可行性评估_20261011.md:563`

**B. 物理/协议提取类（全部死）**
8. 转接环 EF-L（独立从机 MCU，不进 SoC 密码域）— `09-已证伪路线.md:14-18`
9. S1RM2 ffs OOB（不同 SoC 家族，不迁移）— `09-已证伪路线.md:20-24`
10. Wi-Fi 调试后门（~70 mode 全 `err_param`）— `09-已证伪路线.md:34-36`
11. PTP 全操作码只读面（无 RAM 读回、无任意地址写、配置明文 ≠ 固件明文）— `S5_AES破解可行性评估_20261011.md:379`
12. ROM BACKUP（只给标定/参数分区）— `27_…:154-158`
13. 上位机解密（Tether 不解密，符号来自 OpenSSL）— `S1M2_ROM_BACKUP…:104`
14. 官方开源 U-Boot/Linux 源码找解密（`# CONFIG_CRYPTO_HW is not set`）— `S1M2固件存储拓扑…:13-15,112`
15. 公开渠道获取原厂调整工具（不存在可用二进制）— `S1M2_ROM_BACKUP…:22-28`

**C. 代码执行类（全部阴性）**
16. `LD_PRELOAD` / CVE-2017-17562 — `09-已证伪路线.md:30-32`
17. GoAhead buffer overflow / 溢出 fuzz — `04_camcgi_RCE面测绘.md:60`
18. mode / getinfo 子类型 file-op / exec / dynamic-load — `04_camcgi_RCE面测绘.md:36-52`
19. 整数溢出 / HTTP smuggling — `06-崩溃与DoS.md:30-31`
20. PTP 参数/TID fuzz — `06-崩溃与DoS.md:33`
21. **唯一剩余**：CVE-2019-5096（multipart UAF → RCE）**未测** — `05-RCE与代码注入.md:30`

**D. 上传/写路径类**
22. 上传"解密/校验预言机"（粗粒度 `err_critical`，无逐字节反馈）— `oracle/README.md:73-90`
23. 改版本号绕过版本门（无可改字段、无比对逻辑）— `03_隐藏格式…/docs/01:8-25`
24. 改版本字段绕签名（必破 ECDSA + RSA-4096）— `verify_logic_notes.md:63-84`
25. 0x9606 地址覆盖（需先发 `0x00090013`，高砖机风险）— `28_…:122-134`
26. 固件升级写路径**未排除，但卡死**（从未触达一次成功 `endsenddata`）— `04-固件升级写路径.md:28-59`

**E. 功能解锁类（部分解锁 / 全部失败）**
27. ✗ 5.9K 片门全开（穷尽性证伪）— `30_…:81-97,150-157`
28. ✗ 6K 视频 / 400Mbps / a6k — `30_…:98-132`
29. ✗ 快门角度域（空转）— `12_…:37`
30. ✗ 菜单条目注入 / 换皮 — `11_…:39-64`
31. ✗ S5II 规格移植 / S1H 400Mbps 移植 — `10_…:48-64`；`09_…:39-40`
32. ✗ `4kcrop`（禁碰，会致相机 ~80s 无响应）— `12_…:38`
33. ✅ **已解锁**：MOV 全家族（17/18 档）、`mp4ed`（MP4+LPCM 1080p60）、V-Log、L.Classic Neo、AVCHD、6K PHOTO（原生）、mp4hevc（2 档，主动放弃）— `12_…:26-31`；`04_…:70-76`；`09_…:46-54`

---

## 本块最有价值的 5 条

1. **"不需要 AES 密钥"是全局导航句，且已被三条独立证据链封闭**：`S5_AES破解可行性评估_20261011.md:364-366` + `00-总评估报告-中文.md:189-196` + `09-已证伪路线.md:5-12`。密钥在 MC801 片内、文件内无密钥材料、130k+ 探测 0 命中、跨版本差分被随机 IV 封死 —— **软件侧已终局**。真正的目标应是"开机后 DDR 里的运行时明文"，路线 = UART/JTAG dump RAM（P4）> SD.DAT（降为备胎）。**这一条能省掉后来者几个月的重复穷举。**

2. **固件升级写路径是软件侧唯一"能改整个 rootfs"的原语，卡点是唯一且可描述的**：`04-固件升级写路径.md:44-59` 给全了判别三维（内容/节奏/状态均无关）+ 两个小样本探针结论（小映像在"合法性"关就被 `err_reject`，无法逼近真实定址）。原始证据在 `logs/写路径/campaign.md:22726,22761`（CONTROL 未改动真 V29 也失败 → "TRANSPORT ISSUE"）。**这是全项目最接近"改内容"的一步，且差最后一步。**

3. **exFAT 越界写这条线的完整"兴起—撤回"链条**：从 `21_`（S1R2 意义，"把物理线变成纯软件线"）→ `22_`（前置条件成立）→ `23_` §0.5（决定性实验：NULL 检查 ⇒ **内存写根本没发生**）→ `26_`（判定不成立，不再投入）。**这是项目里方法论价值最高的一段**：它示范了"没有对照组的结论不要写进报告"（`25_…:222-223`），并连带产出一个**独立的新漏洞线索**（长文件名导致 boot loop，疑似定长缓冲溢出，见 `24_…:82-86`）。

4. **可复现的操作路径已经工程化完毕，且带踩坑清单**：CAMSET 分块写 + 校验和伪造（`07_…:40-51`）、BLE「先写身份再读凭据」四步（`19_…:39-51`）、ROM BACKUP「卡槽1 + FAT32 + 三键开机」（`13_…:222,184-197`）、PTP 0x9421（`scripts/USB-PTP/PTP_0x9421_dump_使用说明.md:38-105`）、exFAT 工具链（`25_…:88-105`）。加上 `25_操作记录与风险手册` 的 10 条通用铁律 + 12 条踩坑清单 + `04.3` 的 27 条方法论陷阱 —— **"只读这一份就知道这块的全部要点"已经可以实现**。

5. **"相机的错误码语义"被完整反推，这是所有后续操作的判读基础**：`ok` ≠ 生效（6 次反例）；`err_reject` = 参数对但状态不接受 ⇒ **必须退避重试 8–12 次**；`err_param` = 格式被拒；`err_busy` = 退避；`err_critical` = 先重试一次；`err_unsuitable_app` = 会话被污染；`err_others_requesting` = 另一客户端持有会话；`err_user_refused` = 内部拒绝。指针：`30_…:367-401`；`25_…:286-318`；`03_隐藏格式…/docs/01:79-84`。**理解这套语义后，触摸对焦从"间歇可用"变成 8/8 = 100%**（`26_…:629-639`）。

---

## 最容易被重复劳动的 3 件事

1. **重新上传 90MB 固件去"试"版本门/签名** —— 已经跑过 **13 次 Phase I（版本号篡改）+ 2 次 CONTROL + 2 次 TESTA + 4 次 oracle phase 0**，每次 1474 分片、3–16 分钟，**没有一次触达成功的 `endsenddata`**（`campaign.md` 覆盖 L1464–L22801，约 21,000 行日志）。更关键的是：**`oracle/README.md:73-90` 已明确判定"上传路径不是解密预言机"并建议停止这条线**；`04-固件升级写路径.md:44-59` 已把"内容/节奏/状态无关"三条排除做实。⇒ **任何人再想跑一次 90MB 上传，必须先读这两处，并回答"这次与那 19 次有什么不同"。**

2. **重新枚举 cam.cgi 的隐藏 mode / getinfo 子类型** —— 至少被做过 **3 次**：`probe_results.md`（97 个 xml 存盘）、`Wi-Fi实机预言机与mode枚举实测-中文.md`（~70 mode）、`campaign.md` Phase A（**125 条 `getstate type=` 探测**，L5–L1458）、`04_camcgi_RCE面测绘.md`（~90 mode + ~110 子类型）。全部结论一致：**全 `err_param`，无后门**。⇒ 并且 `campaign.md` Phase A 的 125 行 `[INTERESTING]` 是**典型的假阳性**（`getstate` 忽略 type，恒回 `ok`），`08-WiFi预言机与密钥提取.md:43` 已明确警告。**唯一值得跟进的残留**是 `campaign.md:591` 的 `mode=getsetting type=flash -> ok`（全项目无解释）。

3. **重新做"录制格式能解锁到什么"的扫描** —— 至少被做过 **4 轮**：`12_可写设置面审计`（47 域全表 + 读写判定）、`08_格式对照表`（逐项计数）、`30_录制格式能力边界`（穷尽性四变量组合）、`09_S1H参考包分析`（44 个 mp4ed 候选）。结论已固定：**上限 = `mov_60p_200mbps_4k_10bit`（NTSC）/ `mov_50p_200mbps_4k_10bit`（PAL）；5.9K/6K/400Mbps/a6k 恒不可得；权威判据 = 实时 `curmenu` 的 `enable=yes`**。⇒ **特别注意一个陷阱**：`30_…:188-211` 发现前人那次"5.9K 尝试"的落盘 payload 与写入前备份**逐字节相同 = 空操作**，因此 `0xf4`/`0xf1` 这些码值是错的 —— **不要相信 `out/` 目录里那个文件名**。
