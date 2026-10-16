# A · 核心总包（`16_S5_核心总包_20261015/`）逐文件通读素材

> **本文件性质**：项目档案分析员对 `16_S5_核心总包_20261015/`（142 个 `.md` / 50,733 行）**逐文件通读**后的结构化素材，
> 供上级汇编"项目唯一权威调用文档"。**不改写、不美化原文**；原文有错照实记录并标注疑点。
> **方式**：纯离线读文件，未连接任何设备、未执行任何脚本、未修改包内文件。
> **路径约定**：下文所有指针均为**相对 `16_S5_核心总包_20261015/` 的路径:行号**。
> **证据等级标记**（沿用项目自身口径）：`实测`=已实机/协议闭合 · `强推断`=有强证据未闭合 · `弱推断`=结构性推测 · `未验证`=文档自称待做/开放。

---

## 0. 本包规模与结构（供汇编定位）

| 项 | 实测值 |
|---|---|
| `.md` 文件数 | **142**（`find` 计数） |
| `.md` 总行数 | **50,733 行** |
| 包体积 | **63 MB**（含 `MANIFEST.sha256`、LUT 资产、小体积二进制） |
| 最大两份文件 | `01_研究报告/02_研究总报告_20261011/logs/写路径/campaign.md`（**22,801 行**，占全包 45%）、`01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/oracle_results.md`（**3,063 行**） |
| 其余 140 份均值 | 约 **177 行/份** |

**两处大文件的真实内容（重要，避免汇编时误以为它们是分析文档）**
- `campaign.md`：**逐条原始运行日志**（Phase A 枚举 + Phase I 版本号上传重试 20+ 次）。其中 **130 行是 `[INTERESTING]` 标记**——但那是脚本把"`getstate` 带 `type=` 参数仍回 `ok`"误判为"非通用响应"（`logs/写路径/campaign.md:7` 起）；
  真正的方法学结论在 `01_研究报告/02_研究总报告_20261011/01-目标与环境.md:53` 与 `08-WiFi预言机与密钥提取.md:43`：**`getstate` 忽略附加参数、恒回同一份 XML**，故该标记整体为假阳性。
- `oracle_results.md`：phase 0 上传（1474 块）的逐块日志，`oracle_results.md:3062` 为终局 `err_critical`。可复用的判断在 `oracle/README.md:73-90`（勿重复浪费上传）。

---

## 1. 已确证的结论

### 1.1 固件容器 / UPD / 启动链

| # | 结论 | 等级 | 指针 |
|---|---|---|---|
| F-1 | `S5___V29.bin` = **90,238,464 B**（0x560EE00），魔数 `UPD\0`，SoC 标识 **MC801** | 实测 | `01_研究报告/02_研究总报告_20261011/03-固件格式与启动链.md:3`；SHA-256 `b2ec4aee…0827e1` 见 `02_固件指针/固件SHA256与下载来源.md:19` |
| F-2 | 容器布局：`0x0` 外层头 512B → `0x200` `"panasonic"`+**64B 高熵块** → `0x2A0` 内层头 → `0x2E0` 目录头 12B → `0x2EC` **48 条 × 92B 分区表** → `0x1400` 分区数据 → `0x560EC00` **512B 尾块** | 实测 | `03-固件格式与启动链.md:9-16`；`research/FIRMWARE_FORMAT.md:8-16` |
| F-3 | 分区表条目字段：`name[12]` / `off u32`(+0xC) / `size u32`(+0x10) / `load_addr u32`(+0x14) / `type u32`(+0x18) / **`SHA-256(明文)[32]`**(+0x1C) / **`IV[16]`**(+0x3C) / `pad[16]`(+0x4C) | 实测 | `research/FIRMWARE_FORMAT.md:47-58` |
| F-4 | **`type=2 ⟺ IV 全零`、`type=3 ⟺ IV 非零`，48/48 完全吻合；7 个明文 / 41 个加密；41 个 IV 全唯一** | 实测 | `03-固件格式与启动链.md:81`；审计独立复算 `14_总包审计与新方向_20261014/00_审计总报告.md:471`（R5） |
| F-5 | **分区表物理终点 0x142C 与数据起点 0x1400 重叠 44B**（末项 `hr_c_ddr` 的 SHA 尾 12B + IV 16B + 零填充 16B）——这解释了旧文档"loader1 有 28 字节随机数" | 实测 | `03-固件格式与启动链.md:83`；`research/BOOT_FLOW.md:100`；`02-硬件攻击面/verify_logic_notes.md:90-96` |
| F-6 | `loader1` **不是空的**：实为 **512B 零头 + 3584B 高熵载荷**（熵 7.948）；`zboot` 为 **512B 0xFF 头 + 1536B 加密载荷**（熵 7.865） | 实测 | `research/BOOT_FLOW.md:101-102`（明确更正旧结论） |
| F-7 | 90KB 连续引导块：`loader1`(0x1400,4K,load=0x0) → `loader2`(0x2400,38K,0x1000) → `loader3`(0xBC00,48K,0xA800) → `program`(0x17C00,16M,load=0x80000≠相对偏移) | 实测 | `research/BOOT_FLOW.md:31-40` |
| F-8 | `load` 字段 = **目的 RAM 地址**（非 128KB 对齐 flash 地址） | 实测 | `research/BOOT_FLOW.md:103` |
| F-9 | `0x40` = `zlib.crc32(data[0x200:])`，V29 实测 `0x8E73AAC0` | 实测 | `03-固件格式与启动链.md:33`；审计复算 `00_审计总报告.md:497` |
| F-10 | 内层头 `0x2A0-0x2E0` **逐字节等于**外层头 `0x00-0x40`；`0x3C == L-0x200`（5/5 版本） | 实测 | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:211` |
| F-11 | **记录 SHA = 该分区【明文内容】的 SHA-256**：`type=2` 七个分区正确偏移下 **7/7 命中**，且 **V11/V20/V23/V24/V29 五版全部 7/7** | 实测（审计+重跑独立复算） | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:14,59,68`；`08_实机与离线验证记录_20261014.md:176-182` |
| F-12 | 分区用途：`program`=加密主固件 16MB、`zimage`=加密内核 2.5MB、`rootfs1`=3MB、`rootfs2`=10MB、`dtb`=4KB、`zboot`=2KB、`music`/`osdover`/`osddata`/`koutei_kao`/`eep_*`/`ipu_*`/`rc_*`/`nr_*`/`hm_*`/`hr_*` 均 type=3 加密 | 实测 | `03-固件格式与启动链.md:87-98` |
| F-13 | 代码/数据分区**无 ELF/gzip/squashfs 明文魔数**，熵 7.8–7.999 | 实测 | `03-固件格式与启动链.md:100` |
| F-14 | 全文件 **无 PEM / 无 DER SPKI / 无在曲线上的 EC 点**；`0x30 82` 1370 处**全部在密文区**（>0x2400），明文头内 0 处 | 实测 | `02-硬件攻击面/verify_logic_notes.md:15-43` |

### 1.2 AES / 密钥（★ 本包最重要也最需要改写的一块）

| # | 结论 | 等级 | 指针 |
|---|---|---|---|
| A-1 | **软件/离线侧无法从固件文件内取得 AES 密钥**：容器内**无密钥明文、无公钥包裹的 Key Blob（无 PKCS#7/CMS）**；头部除签名/元数据外全零 | 实测（结构观察） | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:84-86`；`02-硬件面/siegfried82_notes.md:53-54`；`03-离线破解与上传预言机/S1M2固件存储拓扑与离线解码技术边界终局报告_20261008.md:83-85` |
| A-2 | **41 个 type=3 分区的 IV 逐版本全变、全唯一、不可由 name/index/model 派生（0/41）** | 实测 | `02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:80,89-97`；重跑维持 `06_密码学重跑/结论.md:328` |
| A-3 | **同偏移密文跨版本相等率 ≈0.39% = 随机基线 ⇒ 排除 ECB 与"版本稳定 keystream"** | 实测（重跑后**证据更强**：全体 type=3 平均 0.3881% vs 基线 0.3906%） | `06_密码学重跑/结论.md:210-227,329` |
| A-4 | **S5 不是固定 XOR 流**：同明文不同 IV 的两对（`eep_ow_a/b`、`eep_act_a/b`）密文**逐字节相等率 0.29–0.37%、XOR 熵 7.92–8.00** ⇒ Nikon「padding 泄露 keystream」手法**原理上不成立** | 实测 | `S5_AES破解可行性评估_20261011.md:541-546`；重跑加固 `06_密码学重跑/结论.md:178-187,331` |
| A-5 | **全库唯一已知明文对**：`ipu_data`（type=3, 262144 B）的记录 SHA **等于 `SHA256(262144 个 0x00)`** ⇒ 其明文为**纯全零**；41 个加密分区对 13 种均匀模板 + 4 种结构模板扫描**仅此 1 命中** | 实测 | `14_总包审计…/08_实机与离线验证记录_20261014.md:155-174`；`06_密码学重跑/结论.md:107` |
| A-6 | `history`(type=2) 记录 SHA 与 `ipu_data` 相同 ⇒ 一份现成的「明文+密文+IV」对照 | 实测 | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:41-45` |
| A-7 | 审计方独立复算：**旧两次"密钥搜索 0 命中"对假设零检验力**（阳性对照 12/12 假阴性）。原因是 `keyhunt.py`/`keyhunt2.py` 等 **7 个脚本用 `raw[doff:]`，漏了 `+0x200`**，密文与明文同时错位 512B | 实测（自造样本阳性对照 6/6 PASS） | `14_总包审计…/00_审计总报告.md:102-145`（S2）；`06_密码学重跑/结论.md:261-314` |
| A-8 | 修正偏移后 `upd_table.py` 判决实验 **5 版全 7/7 PASS**，搜索逻辑**首次具备检验力** | 实测 | `06_密码学重跑/结论.md:14,68,345` |
| A-9 | **CBC 与 CTR 在本数据上不可区分**（`ipu_data` 正确偏移下 16384/16384 块全唯一 ⇒ **只能排除 ECB**）；"CBC+全零明文⇒块全同"是**密码学错误**（块全同是 ECB+常量明文的指纹） | 实测（含 CBC/CTR/ECB 自造样本对照） | `06_密码学重跑/结论.md:19,148-176,349` |
| A-10 | `0x220` 的 64B 在 5 版中**互不相同、位置固定、四周 64B 全零填充**——这些结构特征确证；**但"它是 ECDSA P-256 签名"不可判定**（源头 `s1m2-research/docs/CORRECTIONS.md` **已自我撤回**该断言） | 实测（结构）/ `未验证`（算法归属） | `07_签名与密钥恢复/结论.md:12-22,169-183` |
| A-11 | ECDSA 公钥恢复：**90,144 组假设**（602 消息候选 × 3 曲线 × 11 哈希 × 4 编码端序，约 1,014 GB 哈希）→ **0 收敛**；工具自检 6/6 PASS（真收敛必被检出） | 实测（离线数学） | `07_签名与密钥恢复/结论.md:112-137` |
| A-12 | RSA-4096 模数恢复：e∈{3,5,7,17,257}×3,620 候选 + e=65537 前 24 高先验候选 **全排除** ⇒「尾块 512B 是 RSA-4096」**无正面依据**（512B=4096bit 只是尺寸巧合） | 实测（离线数学） | `07_签名与密钥恢复/结论.md:241-269,495` |
| A-13 | **"版本字段在签名覆盖内"裁决 = 不可判定**。可数学确证的部分：外层 `0x1C`/`0x24` **不在** CRC32 覆盖内；内层副本 `0x2BC`/`0x2C4` **在** CRC32 覆盖内且落在 `[0x200, L-512)` | 实测（CRC32 部分）/ `未验证`（带密钥签名部分） | `07_签名与密钥恢复/结论.md:19,197-235` |
| A-14 | 版本字段编码：4 字节 **BCD `[sub][major][sub][major]`**，`0x1C`(外层) 与 `0x2BC`(内层) 双写；V29=`90 02 90 02` | 实测 | `01_研究报告/02_研究总报告_20261011/03-固件格式与启动链.md:38-46`；`04_工具与脚本/campaign2/README.md:10-13` |
| A-15 | **`02_固件指针/固件SHA256与下载来源.md`** 是唯一权威固件指针清单（7 个版本体积+SHA-256，可据此从官方重取） | 实测 | `02_固件指针/固件SHA256与下载来源.md:17-25` |

> **★ AES 结论的最终状态（汇编请用这句）**
> 截至 2026-10-14 审计与重跑之后，站得住的是：**「密钥不在固件文件内」这一负向结构观察** + **「官方只发单一 `.bin` ⇒ 主密钥按机型固定」的商业逻辑推演**。
> 这两条支持"离线拿密钥希望渺茫"，**不支持**"已证实（终局）"。项目自己在 `S5_AES破解可行性评估_20261011.md:416` 也写了"**不是对 AES 密钥空间的穷举证明**"，与摘要层"已证实（终局）"自相矛盾。
> ⇒ 建议统一改写为 **◐ 离线希望渺茫（非终局）**。

### 1.3 Wi-Fi `cam.cgi` 协议面

| # | 结论 | 等级 | 指针 |
|---|---|---|---|
| W-1 | 端点形态：`http://<ip>:80/cam.cgi?mode=<m>[&type=<t>][&value=<v>][&value2=<v2>]`；**`User-Agent: LUMIX Sync` 必须** | 实测 | `01_研究报告/01_固件AES绕过…/01-固件格式与启动/PANASONIC_FIRMWARE_UPDATE_PROTOCOL.md:11-33`；`.../PROTOCOL_AUDIT.md:10-17` |
| W-2 | 有效 mode = **7**（`getstate`/`getsetting`/`setsetting`/`getinfo`/`accctrl`/`camcmd`/`camctrl`），~90 候选全拒 | 实测 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/00_执行摘要.md:25` |
| W-3 | 有效 `getinfo` 子类型 = **capability / allmenu / curmenu / camsetting / lens**（5 个；`lens` 是后期才发现，~110 候选其余全拒） | 实测 | `01_研究报告/16_App在线状态信息获取_20261013.md:33`（**注意与 00_执行摘要写"4 个"矛盾**，见 §6-16） |
| W-4 | 可写设置域 = **47 个 `cmd_type`** | 实测（审计复算 47） | `01_研究报告/12_可写设置面审计_20261013.md:12-18`；复核 `14_…/05_相机只读快照_20261014/README.md:38` |
| W-5 | `getstate` **忽略 `type`/`value` 附加参数、恒回同一状态 XML** ⇒ 判定某 mode 是否存在必须看"是否回非 `err_param` 的专属响应" | 实测 | `02_研究总报告_20261011/01-目标与环境.md:53`；`08-WiFi预言机与密钥提取.md:43` |
| W-6 | 服务器 = **Panasonic 定制 CGI（GoAhead 系）**：`Server: Panasonic`（无版本号）、错误页 XHTML 指纹、`OPTIONS`/`PUT`/`DELETE` 回 500、只实现 GET/POST | 实测 | `02_研究总报告_20261011/05-RCE与代码注入.md:9-16` |
| W-7 | **`accctrl&type=req_acc` 是唯一会话门**；响应 `ok_under_research_no_msg,S5-XXXXXX,remote,encrypted` —— 4 字段、**无 token ⇒ 不存在 `X-SESSION_ID`** | 实测 | `01_研究报告/03_…/docs/01_版本门与握手修复.md:79-83`；`PROTOCOL_AUDIT.md:107-110` |
| W-8 | `accctrl` 末位字段 = **链路加密标志**：家网 `encrypted`，相机热点 `open`（同字段两值对照） | 实测 | `01_研究报告/18_相机热点SoftAP侧勘察_20261013.md:59-65` |
| W-9 | 相机 **单控制客户端**，但**读类端点不受限**（`getinfo camsetting` 全量 65,533B 可下） | 实测（家网+已建会话时） | `01_研究报告/16_App在线状态信息获取_20261013.md:5-29` |
| W-10 | `getsetting` 响应格式：值是 **attribute** 不是子节点：`<settingvalue <key>="<value>"/>` | 实测 | `01_研究报告/03_…/docs/01_版本门与握手修复.md:84` |
| W-11 | `camctrl type=focus` 是**变焦**不是对焦（`tele-normal`/`wide-normal`/`focus-stop`） | 实测 | `12_S5无线监看_v1.0_20261014/附_技术参考.md:81-86` |
| W-12 | 触摸对焦正确形态：`camctrl?type=touch&value=<x>/<y>&value2=on`（**斜杠分隔 + 必须带 `value2=on`**） | 实测 | `12_S5无线监看_v1.0_20261014/附_技术参考.md:69-71` |
| W-13 | 取景流：`camcmd&value=recmode` → `startstream&value=<UDP端口 49152–65535>` → UDP 上收 **MJPEG，每包一整帧**；**640×432 是相机硬上限**；相机约 30fps **突发式**；官方做法 **固定 18fps 取最新帧** | 实测 | `12_S5无线监看_v1.0_20261014/附_技术参考.md:9-41` |
| W-14 | **单客户端会话 + 只有一个"待批复槽"**：陈旧 pending 会让 `getstate`/`getinfo`/`get_content_info` 一律 `err_reject` | 实测 | `01_研究报告/03_…/docs/01_版本门与握手修复.md:34-49`；`12_S5无线监看…/README.md:173-178` |

### 1.4 录制格式能力（阶段三，项目最实用的成果）

| # | 结论 | 等级 | 指针 |
|---|---|---|---|
| R-1 | **`videoformat`（blob 偏移 3062，记录 `0x005e`）是唯一容器门**，mov↔mp4 切换**只改这 1 字节 + 校验和** | 实测 | `01_研究报告/07_隐藏格式持久化_追查_20261013.md:70,76`；审计复算 `00_审计总报告.md:474`（R2） |
| R-2 | 容器码：`0x00`=avchd、`0x05`=mp4、`0x06`=mov、**`0x07`=mp4ed**、`0x08`=mp4hevc | 实测 | `01_研究报告/09_S1H参考包分析_mp4ed_20261013.md:42`（`0x07` 由 S1H 参考包编号表补测得到） |
| R-3 | **可选档数随【容器 × 制式】双重变化，权威判据 = 实时 `curmenu` 的 `enable="yes"` 集合**：**NTSC+mov = 18**（24p6+30p6+60p6）、**PAL+mov = 12**（25p6+50p6）、**NTSC+mp4 = mp4 8 + mp4hevc 2 = 10** | 实测（2026-10-14 实机 + 只读快照补齐） | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:261-275`；快照复核 `14_…/05_相机只读快照_20261014/README.md:34-44` |
| R-4 | **`enable="yes"` 语义 = 「该选项在当前模式下可被选择」，不是「当前生效值」**（实测 `videoformat_mp4` 与 `_mov` 同时为 yes） | 实测 | `14_总包审计…/08_实机与离线验证记录_20261014.md:96-108` |
| R-5 | `allmenu` = 菜单树（含 `cmd_value`）：**740 item / 666 个 `cmd_value` / `videoquality` 去重 44 个（mov 31 + mp4 13）**；`curmenu` = App 侧可见性快照（**`cmd_value` 出现 0 次**，只有 `id`+`enable`） | 实测 | `01_研究报告/30_…_20261014.md:246-256`；快照复核 `14_…/05_…/README.md:38-41` |
| R-6 | **「启用但 `allmenu` 未声明」的 mov 档恰好 1 个 = `mov_60p_200mbps_c4k_10bit`（`0x8b`）** —— 这正是让机身菜单变灰的元凶 | 实测 | `01_研究报告/30_…:288-303`；`14_…/05_…/README.md:42` |
| R-7 | **菜单变灰精确条件**：`videoquality` 当前值 **∉ `allmenu`** ⇒ 机身【录制质量】整项变灰；双向对照（`mov_50p_200mbps_c4k_10bit` 命中 0 → 灰；`mov_50p_200mbps_4k_10bit` 命中 4 → 恢复） | 实测 | `01_研究报告/30_…:217-228` |
| R-8 | **菜单读的是 RAM 值不是 flash 值** ⇒「flash 存安全值 + RAM 上隐藏档」的**双轨方案实测证伪** | 实测 | `01_研究报告/30_…:229-237` |
| R-9 | **本机可达上限 = `mov_60p_200mbps_4k_10bit`（NTSC）/ `mov_50p_200mbps_4k_10bit`（PAL）= 200Mbps 4K 10bit 且菜单可用** | 实测 | `01_研究报告/30_…:335-348` |
| R-10 | 质量码表（权威，勿另推算）：`0x8b`=`mov_60p_200mbps_c4k_10bit`、`0x9b`=`mov_60p_200mbps_4k_10bit`、`0x92`=`mov_60p_150mbps_c4k`、`0x94`=`mov_30p_150mbps_c4k_10bit`、`0x96`=`mov_24p_150mbps_c4k_10bit`、`0x97`=`mov_24p_100mbps_c4k`、`0xc1`=`mp4_30p_20mbps` | 实测 | `04_工具与脚本/campaign2/隐藏格式持久化_成果.md:159-164` + `01_研究报告/07_…:117-119`；**`0xf4` 是错误值，禁用** |
| R-11 | `videoquality`（记录 `0x0124`，起点 6980）为 **13 槽 u16 数组**，槽 0 = 选中码、槽 1..12 = `0x00c0` | 实测 | `04_工具与脚本/campaign2/out/S5_format_slots_analysis.md:18-23` |
| R-12 | `0x005e` 记录结构：偏移 3056，`[6B 头 5e 00 14 00 01 00][13B 槽][1B 终止 0x00]`（27 个历史 blob 一致） | 实测 | `01_研究报告/30_…:466` |
| R-13 | `setsetting` **会被相机自动存盘**（纠正早期"仅 RAM"假设）：只切过 RAM 的 `mp4ed` 也被写进 flash `0x5e=0x07` | 实测 | `01_研究报告/09_…_mp4ed_20261013.md:76-84`；`02_项目时间线.md:152-156` |
| R-14 | **`a6k` 家族危险**：`mov_25p_200mbps_a6k_10bit` 等返回 **`ok`** 却**静默把 `videoformat` 从 mov 改成 avchd**（且 `videoquality`→`avchd_50p_28mbps`），**不报错只改状态** | 实测 | `01_研究报告/30_…:105-124`；恢复命令见 `:120-122` |
| R-15 | **`ok` ≠ 生效**：单日记录 **≥6 次**「返回 ok 但未生效/被换档」反例 | 实测 | `01_研究报告/30_…:377-387` |
| R-16 | **`err_reject` 需退避重试**（授权状态在 ok/受限之间翻动）：`mov_50p_200mbps_4k_10bit` **第 5 次才成功**；`camcmd&value=recmode` 先 `err_critical` 重试即 `ok` | 实测 | `01_研究报告/30_…:389-401`；`25_操作记录与风险手册_20261013.md:305-318` |
| R-17 | 错误码语义：`ok`=接收（≠生效）｜`err_reject`=格式对但状态不接受（**重试**）｜`err_param`=参数格式被拒（**不重试**）｜`err_busy`=忙（重试）｜`err_critical`=严重（先重试一次） | 实测 | `01_研究报告/30_…:367-375`；`12_…/附_技术参考.md:96-105` |
| R-18 | **6K PHOTO（片门全开）原生支持**：`6k4k_photo=6k_start_stop` + `pictsize_burstspeed=6k_18m_30p` + `aspectratio=3:2` ⇒ 5184×3456 3:2 / 30fps / MP4，是 S5 上**唯一**的 6K 通道 | 实测（可写域；产出需实拍核对） | `01_研究报告/03_…/docs/03_opengate_6k_photo.md:10-30`；`01_研究报告/11_菜单条目注入可行性_20261013.md:22-28` |
| R-19 | `mp4ed` 容器在 S5 上**真实存在**：自动质量 `mp4ed_60p_100mbps`，实拍 `P1000005.MP4` = **1920×1080@59.94 H.264 High 8bit ~96.6Mbps + PCM 音轨 + 30 帧 GOP**（≠ S1H 的 4K 4:2:2 10bit ALL-I 400Mbps） | 实测（实拍文件头解码） | `01_研究报告/09_…_mp4ed_20261013.md:46-54` |
| R-20 | **V-Log 在本机可选**（`menu_item_id_ph_sty_vlog` = `enable="yes"`；S5 通常需付费 DMW-SFU2）；`L.Classic Neo` 亦可用 | 实测 | `01_研究报告/12_可写设置面审计_20261013.md:26-27`；`14_…/08_…:118` |
| R-21 | 照片风格判定可量化：**V-Log 黑位 ≈ 32–33/255（理论 0.125×255=31.9）且无真黑**；普通风格黑位贴近 0 | 实测 | `12_S5无线监看_v1.0_20261014/README.md:432,444` |

### 1.5 写入 / 持久化（★ 证据链已被审计部分推翻，见 §3 与 §6）

| # | 结论 | 等级 | 指针 |
|---|---|---|---|
| P-1 | **CAMSET 写入必须分块 `method=separate`**：`startsenddata` 回 `bufsize=61460`；chunk = `bufsize − multipart 开销 = 61192`；65533B → **61192 + 4341** 两块，块间 `requestsenddata`，末 `endsenddata` | 实测 | `01_研究报告/07_…:40-50`；`docs/00_执行摘要.md:28`；`PROTOCOL_AUDIT.md:120-122` |
| P-2 | **单次 65KB POST 永不落地**（早期"mov 回落 mp4"的**真因**） | 实测 | `01_研究报告/07_…:45-50`；`02_项目时间线.md:80-91` |
| P-3 | 块长数学自洽：`61192+268=61460`、`61192+4341=65533`、`1474×61192+41456=90238464`、`65545−12=65533` | 实测（审计复算） | `14_…/00_审计总报告.md:391` |
| P-4 | blob 结构：65533B = **44B 头**（`"Panasonic"`+`"DC-S5"`）+ **8B 前导**（0x2C..0x33，含 `ffcc`）+ **831 条 TLV**（0x34 起，`[fid u16][len u16][flag u16][payload len-6]`）+ 尾部 `ff ff 00 00`（0xFFF8）+ 校验字节 0xFFFC | 实测 | `01_研究报告/07_…:63-66`；`04_工具与脚本/campaign2/out/S5_format_slots_analysis.md:8-23` |
| P-5 | **校验和 `byte[65532] = (256 − Σ(byte[0..65531])) mod 256`，即 `sum % 256 == 0`**；可伪造（改数据+修和 → `ok`；改数据不修和 → `err_reject`） | 实测（多 blob 独立复算） | `02_研究总报告_20261011/08-WiFi预言机与密钥提取.md:28-31`；`14_…/00_审计总报告.md:473`（R1） |
| P-6 | **S1R2 的校验算法与 S5 完全相同、两组人独立反推**（`checksum = (256 − Σ) mod 256`） | 实测（双证） | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:18` |
| P-7 | **`getinfo camsetting` 返回 RAM 副本** —— 「写完立刻回读」不能作为持久化判据，**只有断电重启后的读回才反映 flash** | **◐ 循环论证（被审计判定）**：其"独立验证"的前提"setsetting 不写 flash"已被项目自己在 `09_…:78` 撤销 | `01_研究报告/31_录制格式持久化_受控复测_20261014.md:50-51,92-99`；反证 `14_…/00_审计总报告.md:183-192`（S4） |
| P-8 | 写入形态三态：`06 ×13`（全 mov，15 次出现）、`05 ×13`（6 次）、**`06 05 ×12`（仅槽 0，6 次，相机自身行为）** | 实测 | `01_研究报告/31_…:74-90` |
| P-9 | 审计独立复算：**`blob_GOLD_mov_persisted_20261013_020600.bin` 实测 `06×13` 全槽写且为 mov 持久态** | 实测（结构） | `14_…/00_审计总报告.md:151-159`（R2/S3） |
| P-10 | **`setsetting` 与 `startsenddata` 是两条通道**：前者改 RAM（但会被自动存盘），后者分块上传整块 blob 落 flash | 实测 | `01_研究报告/04_隐藏格式_持久化成果.md:13-20` |

### 1.6 USB / PTP

| # | 结论 | 等级 | 指针 |
|---|---|---|---|
| U-1 | **PID 地图**：`0x2382`(9090)=正常 PTP/PC 模式（macOS 可 dump，`class 06/01/01`）；**`0x2370`(9072)=服务/厂商模式**（`class 0xFF/0xA0/0xB0`，macOS 不识别、PTP 超时）；`0x2374`=DMC-FZ28 老机型（**与本机无关**） | 实测 | `13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md:84-92,134-139` |
| U-2 | `0x9421` 全量配置 dump = **65,545 B**（= 65533 + 12B PTP 头），sha256 `e808a6b899173a5a7ee8ef7a790c5ca24ba450d64b80ea3fe731db10123f20ab`；完整性三证：结尾 `ff ff 00 00` 终结符、`payload[0:4]=len-4` 自洽、无越界指针 | 实测 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:198-220`；`02_研究总报告_20261011/07-USB-PTP-SCSI.md:22-29` |
| U-3 | `0x9421` 载荷 = 外层单条 TLV `tag=0x080000a2, len=65537` → **831 条 16 位记录**（idx 稀疏 1..0x4b5，type∈{0,1}，最大单条 6664B），熵 3.08（结构化非加密） | 实测 | 同上 `:205-213` |
| U-4 | **`0x9606` 无"任意地址写"原语**：目标地址**由机身经 `0x9605` 下发**（Tether 把地址存主机全局再原样填入），主机不能自填 | 实测 + 反汇编双重 | `S5_AES…:266-268`；`01_研究报告/28_PTP固件更新协议审计_20261013.md:43-58` |
| U-5 | **PTP length-DoS**：解析器**校验 type 不校验 length**，且**无超时** ⇒ 发 12B 但头声明 `length=0x400` → 数据面挂死，**拔插 USB 恢复、不砖机、无写操作** | 实测 | `02_研究总报告_20261011/06-崩溃与DoS.md:5-13`；时间线 `S5_AES…:484-499` |
| U-6 | 43 个只读 fuzz 的异常：**命令参数数量不校验**（多余参数被忽略）、**TID 不校验**（0/最大/复用均成功）、**`0x1005` ResetDevice 回 `0x2008`（被识别但拒绝）**、**`0x9103` 回 `0x2003` SessionNotOpen ⇒ 已实现但未文档化** | 实测 | `S5_AES…:455-480` |
| U-7 | `0x9406` 8 个子码**全部是带副作用的动作**，无一只读；只读查询通道是 **`0x9605`**（Get_Event_Info） | 实测 + 反汇编 | `S5_AES…:224-239`；`28_PTP固件更新协议审计_20261013.md:82-92`（**新增 `0x00090013` FWUP Request 与 `0x00090014` UPDATE**） |
| U-8 | 服务态 `0x2370` 三个方向**全部打不通**：EP0 厂商 IN **4933 个请求全 STALL**、EP0 厂商 OUT 零长度 768 个全 STALL、bulk OUT **8 种帧格式全 NAK**、bulk IN/interrupt IN 监听 20s+30s **0 字节** | 实测（含 `0x2382` 正对照 `SET_CONFIGURATION(1)`=ACCEPTED） | `13_…/00_交接总结_全文.md:96-118` |
| U-9 | `0x2370` 的**两个配置只差供电**（500mA 总线供电 vs 2mA 自供电），接口与端点**逐字节相同** ⇒「第二配置藏固件更新接口」**已排除** | 实测 | `13_…/00_交接总结_全文.md:53-62` |
| U-10 | `s5_ptp_raw.c` 两个 off-by-one（跳过非 bulk 端点导致 interrupt 端点从未被发现；`for (cfg = 1; ...)` 而 USB 配置索引从 0 起）**已在本包工具中修正** | 实测 | `13_…/00_交接总结_全文.md:76-80` |
| U-11 | 服务态设备**字符串索引 3** = 机身 ID `0000000000000000000XJL########15`，与 ROM BACKUP 的 ADJUST `0x0000` **完全一致** | 实测（交叉印证） | `13_…/00_交接总结_全文.md:49-51`；`01_研究报告/28_…:144` |

### 1.7 服务模式 / ROM BACKUP / 蓝牙 / 硬件事项

| # | 结论 | 等级 | 指针 |
|---|---|---|---|
| S-1 | **进入服务模式**：按住 **`回放(Playback)` + `AF ON` + `方向右键`** 同时开机 | 实测 | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:222`；`27_ROM_BACKUP导出成功与数据解析_20261013.md:25` |
| S-2 | **退出服务模式恢复出厂**：按住 **`AF ON` + `方向右键`** 关机；另一记法为回到 `INITIAL SETTINGS` 界面（`MENU/SET`+`方向右键` 关机） | 实测 | `01_研究报告/13_…:223-224`；`27_…:26` |
| S-3 | **ROM BACKUP 变灰的真因 = SD 卡文件系统类型，不是"未解除初始设置"**：64GB exFAT → **灰**；**32GB FAT32（SDHC）→ 可用** | 实测（两卡对照） | `01_研究报告/13_…:182-191`（明确"这推翻了我此前排在第一位的假设"）；`01_研究报告/27_…:23-24` |
| S-4 | ROM BACKUP **只有卡槽 1 能触发**（槽 2 不行）；**不需要**处理地区后缀 | 实测 | `01_研究报告/27_…:23-27` |
| S-5 | **ROM BACKUP 已成功导出**：卡根生成 `S5A.TXT`/`S5F.TXT`/`S5U.TXT`（各 356,6xx B ASCII 十六进制，解析后各 **131,072 B / 128KB**）= EEPROM 三区 `ADJUST ONLY(21)`/`FIX ONLY(22)`/`UPDATE(10)` | 实测 | `01_研究报告/27_…:11-13,58-62` |
| S-6 | 导出含身份字段：`0x0000`=`XJL########15`、`0x0020`=`MXD1D########`、`0x0040`=`X9214######`、`0x0060`=`WJ1DA######`；**不是固件明文、不含 AES 密钥** | 实测 | `01_研究报告/27_…:93-101,154-158` |
| S-7 | `ADJUST 0x11000/0x12000` 两块高熵区是 **(校正值, 像素索引) 坏点校正表**（第二值逐行递增）—— **不是密钥** | 实测（结构规则） | `01_研究报告/27_…:111-119` |
| S-8 | **`[Strict]` 已锁定 + 机型后缀 `GK`（07）= 中文区 = PAL 机型** ⇒ **项目前期"启用隐藏 NTSC 录制格式"的成果是在 PAL 机型上实现的** | 实测（服务界面实拍） | `01_研究报告/13_…:232-258` |
| S-9 | **⚠️ 禁令：不要按 `DISP.`** —— 手册 p15 Step 5 明确会解除 `[Strict]` ⇒ 地区后缀变成可改（且仅一次机会） | 实测（手册） | `01_研究报告/13_…:247-248` |
| S-10 | 服务模式**不暴露任何 Wi-Fi 接口**：`getinfo allmenu` 普通/工程两态 **逐字节相同（307,714 B，`cmp` 一致）**；`getinfo type=service/rom/factory/…` 全 `err_param` | 实测 | `01_研究报告/13_…:13-18` |
| S-11 | 工程模式**没有新增录制质量档**：`curmenu` 的 `videoquality` 启用仍是 18 项 | 实测 | `01_研究报告/13_…:103-104` |
| S-12 | 服务态 USB 个性切换为 **PID `0x2370`**；回到正常模式须**拔插一次 USB** 才重新枚举为 `0x2382` | 实测 | `01_研究报告/13_…:118-139,260-267` |
| S-13 | **BLE 连接与 GATT 枚举不需要配对**（9 服务 / 约 41–44 特征，视主机栈而定）；**必须先写身份特征再读**（写 `8D08A420` + `CD7A71A0`），裸读会被立即断链 | 实测（macOS + Windows 双主机栈） | `01_研究报告/19_BLE凭据链打通_先写后读_20261013.md:8-17,37-61` |
| S-14 | **按正确顺序可读出 `INITIAL_INFORM`（会话密钥）、`CAMERA_SSID`、`CAMERA_WIFI_PASSWORD`**；本机密码解码后**全 0（空）** | 实测 ×2（不同会话密钥） | `01_研究报告/19_…:65-84` |
| S-15 | BLE 加解密：**字节置换 + 32 位 XOR**，密钥 = `INITIAL_INFORM` 前 4 字节**大端**（默认 `0x9032782C`）；已用 Python 复刻并回环自检通过 | 实测（算法还原 + 离线自检；实机链路未跑通） | `01_研究报告/15_蓝牙BLE协议逆向_20261013.md:84-92` |
| S-16 | **BLE 注册的身份打不开 Wi-Fi 的 `accctrl` 门**（两道门独立）；`req_acc_g`/`req_acc_e` 在本机回 `err_param` | 实测 | `01_研究报告/20_BLE身份与WiFi门独立_20261013.md:11-15,69-73` |
| S-17 | **相机 SoftAP 是明文开放网络**：信标 `capability=0x0401`（Privacy 位=0）、无 RSN/WPA IE；2.4GHz / 20MHz / 802.11n / 信道 6 / Beacon Interval **200 TU** | 实测 | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:13-14,62` |
| S-18 | **WPS IE 泄露完整机型信息**：`DMC-MC801`、`LUMIX`、`Panasonic`、UUID-E、设备名；**厂商 IE OUI `00:0C:E7` = MediaTek** ⇒ Wi-Fi 芯片收敛到 MediaTek 系 | 实测（IE 解析）/ `强推断`（芯片归属） | `01_研究报告/17_…:86-109` |
| S-19 | **Wi-Fi 模块型号从未由拆机确认**（仅 IE OUI 强推断）；**存储类型 eMMC/NAND 未确认**；**MC801 精确 die/核心数未确认** | 未验证 | `01_研究报告/01_固件AES绕过…/02-硬件攻击面/hardware_attack_surface_notes.md:44-55,198-209` |
| S-20 | 硬件路线排序（经 S1R2 交叉校验后）：**P1 拆机只读取证 → P2 服务模式键/ P3 U-Boot console 离线核验 / P7 f_fs 审计（零风险并行）→ P4 JTAG dump RAM（主线）→ P5 UART bootlog → P6 SD.DAT（备胎）→ P8 芯片级** | 未验证（规划） | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:80-91` |
| S-21 | Milbeaut 公开先例：**SD.DAT 恢复模式**（BootROM 跑 SD 卡 `SD.DAT`，CM0 @`0xFFE00400`，配 `boot.par`/`sdram.par`/`data.bin`）、**A7 有完整 CoreSight（3 看门点/5 断点）**、**Stubby 的 `CONFIG_RSA_SIGNATURE` 默认只告警不拦截**（须显式 `CONFIG_RSA_SIGNATURE_ENFORCING` 才拒启） | `弱推断`（同平台公开先例，**S5 本机零验证**） | `02-硬件攻击面/hardware_attack_surface_notes.md:89-115,135-152` |

### 1.8 exFAT / 长文件名（本项目最"干净"的两条定因）

| # | 结论 | 等级 | 指针 |
|---|---|---|---|
| E-1 | **内核对簇号不做归属校验**：释放文件簇时**完全跟随卡上被篡改的 FAT 链值**（注入簇 4=根目录，确实被释放；位图实机比对 + 卡指纹一致） | 实测 | `01_研究报告/22_S5_exFAT越界写前置条件确认_20261013.md:11-20,44-59`；维持 `00_项目总结/04_定因与工具链成果_20261013.md:29` |
| E-2 | **360 个 240 字符长文件名 → DC-S5 开机反复重启**；四组对照排除数量/体量/跨簇数/分配大小，**唯一剩余变量 = 长文件名本身**（阈值落在 **58–86 KB**，疑为定长缓冲未校验） | 实测（四组对照矩阵） | `01_研究报告/24_相机长文件名崩溃_定因_20261013.md:10-51` |
| E-3 | **纯目录项即可触发崩溃**（不需文件数据、不需任何注入） | 实测 | `00_项目总结/04_…:32` |
| E-4 | exFAT 关键实现事实：**Boot Checksum 覆盖整个引导区 11 个扇区**（跳 106/107/112），**不是 512 字节** | 实测（两种实现互验） | `01_研究报告/22_…:74`；`25_操作记录与风险手册_20261013.md:265` |
| E-5 | 越界索引公式 `i = (clu − 2) >> 12`；本卡（ClusterCount=488288、128KB 簇、位图 61036B）⇒ `map_sectors=120`，阈值：`≤491521` 合法 / `491522–524289`（索引 120–127）必崩 / `≥524290` 落相邻堆对象 | 实测（结构） | `01_研究报告/22_…:85-101` |
| E-6 | 32 位机器 ⇒ `vol_amap` 用 **4 字节指针**，`120×4=480` ⇒ **kmalloc-512**（S1R2 64 位为 239×8=1912 → kmalloc-2048） | `强推断`（依机器位宽推算） | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:155-164` |

---

## 2. 已验证可用的操作路径（原样命令 / 报文）

> 全部从原文**逐字照抄**。`192.168.x.x` 为文档占位符；代码内保留研究者本机地址（`README.md:163-164` 已声明）。

### 2.1 只读 / 健康判定（零风险）

```bash
# 健康判定（UA 必须 LUMIX Sync）
curl -s -A "LUMIX Sync" "http://192.168.x.x/cam.cgi?mode=getstate"
# 期望 <result>ok</result>；err_unsuitable_app=连接态被污染；err_reject=瞬时
```
指针：`01_研究报告/02_研究总报告_20261011/01-目标与环境.md:41,46-50`；`01_研究报告/03_…/docs/05_复现流程.md:46-54`

```bash
# 相机在线判定（本地）
arp -a | grep 131        # 有 MAC 70:74:14:XX:XX:XX
```
指针：`README.md:149`

```bash
# 访问控制握手（★ 只发一次，绝不连发）
GET /cam.cgi?mode=accctrl&type=req_acc&value=<UUID 4D454930-0100-1000-8001-…>&value2=<设备名>
# 回：ok_under_research_no_msg,S5-XXXXXX,remote,encrypted
# 清理陈旧 pending（必须用【同一 UUID】）
GET /cam.cgi?mode=accctrl&type=req_acc_can&value=<同一UUID>&value2=
```
指针：`01_研究报告/03_…/docs/01_版本门与握手修复.md:78-81`；`14_…/10_仓库补丁/定因与交接_20261014.md:256-259`

```bash
# 状态/能力/菜单/设置块（全量 65,533 B；★ 读前必须让相机退出机身菜单）
GET /cam.cgi?mode=getinfo&type=capability
GET /cam.cgi?mode=getinfo&type=allmenu
GET /cam.cgi?mode=getinfo&type=curmenu
GET /cam.cgi?mode=getinfo&type=camsetting
GET /cam.cgi?mode=getinfo&type=lens
```
指针：`01_研究报告/07_…:121-123`（菜单开着回 `err_reject` 86 字节）；`01_研究报告/16_…:33-45`

```bash
# 端口扫描（家网侧）
经实测：仅 80/tcp（1–10000 全扫 + 常见高端口）
```
指针：`01_研究报告/16_App在线状态信息获取_20261013.md:78-88`

### 2.2 录制格式 / 隐藏功能（写操作，需 AC 供电）

```bash
# 切拍摄/回放模式（★ 动机身拨盘会断开远程连接）
GET /cam.cgi?mode=camcmd&value=recmode
GET /cam.cgi?mode=camcmd&value=playmode
```
指针：`01_研究报告/30_…:46-49`

```bash
# 6K PHOTO（片门全开）激活配方（需【照片模式】+ rec=off + AC）
curl -H "User-Agent: LUMIX Sync" "http://$S5_IP:80/cam.cgi?mode=setsetting&type=6k4k_photo&value=6k_burst"
curl -H "User-Agent: LUMIX Sync" "http://$S5_IP:80/cam.cgi?mode=setsetting&type=pictsize_burstspeed&value=6k_18m_30p"
curl -H "User-Agent: LUMIX Sync" "http://$S5_IP:80/cam.cgi?mode=setsetting&type=aspectratio&value=3:2"
curl -H "User-Agent: LUMIX Sync" "http://$S5_IP:80/cam.cgi?mode=getsetting&type=6k4k_photo"   # 期望 6k_burst
```
指针：`01_研究报告/03_…/docs/03_opengate_6k_photo.md:44-63`；`06_数据与证据/camera_settings/OPENGATE_FINDINGS.md:27-38`

```bash
# 从 a6k 副作用或 avchd 残留中恢复（写合法 mov 质量档会同时把容器带回 mov）
GET /cam.cgi?mode=setsetting&type=videoquality&value=mov_60p_200mbps_4k_10bit
```
指针：`01_研究报告/30_…:118-124`；`25_操作记录与风险手册_20261013.md:327-333`

```bash
# 容器切换（用完切回，否则菜单变灰）
python3 container_switch.py status        # 只读查看 live + flash
python3 container_switch.py mp4ed         # 进入 MP4(LPCM) 1080p60（菜单会变灰，属预期）
python3 container_switch.py mov --persist # 切回声明档，菜单恢复
```
指针：`01_研究报告/09_…_mp4ed_20261013.md:96-102`

```bash
# 健壮设置器（退避重试 + 回读校验 + a6k 拦截）
python3 s5_quality.py status
python3 s5_quality.py list [--grep 200mbps]
python3 s5_quality.py set mov_60p_200mbps_4k_10bit
python3 s5_quality.py set mov_60p_200mbps_c4k_10bit --allow-grey
python3 s5_quality.py safe
```
指针：`04_工具与脚本/campaign2/s5_quality.py:33-39`

```bash
# 隐藏功能工具
python3 hidden_features.py status | vlog | 6kphoto | lpcm | restore
```
指针：`01_研究报告/12_可写设置面审计_20261013.md:54-59`

### 2.3 持久化（★ 见 §3-01：这套"已被验证"的证据链已被审计推翻，命令本身可用但结论待重做）

```bash
# 工作目录：04_工具与脚本/campaign2　（写盘需 AC 供电，写后拔电池做终验）
python3 persist.py verify                      # 只读安全：健康 + 实时 + blob 三字段
python3 persist.py restore --confirm           # 一键恢复隐藏格式（分块 separate）
python3 persist_quality.py <quality_name> --confirm
python3 experiment_mov_shadow.py --dry-run     # 离线自检，只对本地 blob 演算
python3 experiment_mov_shadow.py --confirm     # 分块写入 3062..3074 = mov
# 前置：相机必须停在普通拍摄画面；写前确认 getstate 的 sd_memory=set
```
指针：`README.md:121-147`；`01_研究报告/07_…:129-138`；`01_研究报告/31_…:194-195`

### 2.4 CAMSET / 固件上传协议（原样报文）

```http
GET  /cam.cgi?mode=camctrl&type=fw_update_mode&value=VX.XX      # 打开"版本门"
GET  /cam.cgi?mode=startsenddata&type=fw&value=<file-size>      # 回 method + bufsize
POST /cam.cgi?mode=senddata                                     # multipart，每块 iA 字节（循环）
GET  /cam.cgi?mode=requestsenddata                              # 非最终块后间插
GET  /cam.cgi?mode=endsenddata                                  # 末块后 → 触发验签+刷写
GET  /cam.cgi?mode=abortsenddata                                # 取消
```
```
Header:  User-Agent: LUMIX Sync（可选 X-SESSION_ID，S5 不签发）
multipart boundary: "=====" + UUID + "====="（46 字符，进程内静态）
part:  --<B>\r\n
       Content-Disposition: form-data; name="filename"; filename="send"\r\n
       Content-Type: application/octet-stream\r\n
       Content-Transfer-Encoding: binary\r\n
       Content-Length: <chunk-size>\r\n
       \r\n
       <chunk bytes>
       --<B>--        ← 末块后无前置 CRLF
块长公式：iA = bufsize − V()，V() 按硬编码 Content-Length: 61460 测出 ⇒ 实测 data/chunk = 61192
```
指针：`01_研究报告/02_研究总报告_20261011/04-固件升级写路径.md:7-26`；`01_研究报告/01_固件AES绕过…/01-固件格式与启动/PANASONIC_FIRMWARE_UPDATE_PROTOCOL.md:95-213`

```bash
# CAMSET 读 / 写（65,533 B）
读：?mode=getinfo&type=camsetting                                   → 65,533 B 实时数据
写：?mode=startsenddata&type=camsetting&value=65533                 → ok, method=separate, bufsize=61460
    → 分块 POST ?mode=senddata → GET ?mode=endsenddata
```
指针：`01_研究报告/02_研究总报告_20261011/08-WiFi预言机与密钥提取.md:24-26`

```bash
# 版本门判别（★ 是 camctrl 命令，不是独立 mode；缺 camctrl 包装会回 err_param）
GET /cam.cgi?mode=camctrl&type=fw_update_mode&value=VX.XX
# V2.90→err_fw_same；V2.00/2.10/2.50/2.80→err_fw_old（降级硬拒）；V3.00/V9.99→ok
```
指针：`01_研究报告/01_固件AES绕过…/03-离线破解与上传预言机/Wi-Fi实机预言机与mode枚举实测-中文.md:29-44`

### 2.5 USB PTP（只读允许集）

```bash
./s5_ptp_dump ./ptp_out S5            # mode=dump：0x9421 全量配置
./s5_ptp_dump ./ptp_out S5 fwup       # mode=fwup：0x9605 升级状态机只读
./s5_ptp_dump ./ptp_out_fuzz S5 fuzz  # mode=fuzz：43 个安全只读探测
# ⚠ mode=lenprobe 是受控 DoS 演示（最后才跑，跑完需拔插 USB）
```
**只读允许集**：`0x1001`/`0x1002`/`0x1003`/`0x1004`/`0x9104`/`0x9421`/`0x9605`
**PTP 容器**（小端）：`[0:4]length u32 | [4:6]type u16(1=cmd/2=data/3=resp) | [6:8]opcode u16 | [8:12]tid u32 | [12:]params/payload`
**S5 端点**：接口 0，`0x01` BULK OUT / `0x82` BULK IN（**必须按描述符动态发现**，S1M2 是 `0x81`）/ `0x83` INT IN
指针：`01_研究报告/02_研究总报告_20261011/07-USB-PTP-SCSI.md:56-61`；`S5_AES…:184-194`

### 2.6 无线监看 / 取片 / LUT

```bash
# 启动监看（默认相机地址 = 热点网关 192.168.54.1，官方低延迟路径）
./run.sh 192.168.x.x [端口] [节奏模式 fixed|adaptive] [帧率 18]
# 取片 + 套 LUT
python3 s5_get_photo.py [--shoot] [--no-lut] [--index N]
# DLNA 内容诊断 / 清理 / 列举
python3 s5_content.py cleanup --cam 192.168.x.x   # 清陈旧 pending（解决"需要更新app"）
python3 s5_content.py diagnose --cam 192.168.x.x
python3 s5_content.py sweep   --cam 192.168.x.x   # 已放行后扫 ObjectID
python3 s5_content.py list    --cam 192.168.x.x
```
指针：`12_S5无线监看_v1.0_20261014/README.md:24-30,416-421`；`14_…/10_仓库补丁/定因与交接_20261014.md:325-346`

**DLNA 官方请求（从 APK 逐字取出，`p168v5/a.java:212-213`、`p168v5/m.java:83-87`）**
```
URL      : http://<ip>:60606/Server0/CDS_control
Headers  : Accept-Charset: UTF-8
           Content-Type: text/xml; charset="utf-8"
           SOAPAction: urn:schemas-upnp-org:service:ContentDirectory:1#Browse
           User-Agent: Panasonic MIL DLNA CP UPnP/1.0
           Host: <ip>:60606
Body     : 单行无空白；子元素【不带 s: 前缀】；含松下私有扩展
           <pana:X_FromCP>LumixLink2.0</pana:X_FromCP>
           xmlns:pana="urn:schemas-panasonic-com:pana"
```
三个必要条件（缺一不可）：**① `accctrl` 达 `ok`；② 相机在【回放模式】（★ 拍摄模式下内容树为空）；③ 官方逐字节 SOAP 格式**
数据端点在 **`50001`** 端口（`http://<ip>:50001/DO<ObjectID>.JPG` 原图 / `DM…` 中图 / `DT…` 缩略图）
指针：`12_S5无线监看_v1.0_20261014/README.md:280-321`

### 2.7 服务模式 / ROM BACKUP

```
① 用 FAT32 的 32GB 卡，插【卡槽 1】，接 AC
② 按住【回放 + AF ON + 方向右】同时开机 → 进入服务模式
③ 进入 ROM BACKUP → 选【DSC→SD】→ 确认（再次执行会提示 overwrite）
④ 等待完成（闪一下）→ 按住【AF ON + 方向右】关机
⑤ 卡插到 Mac → 根目录出现 S5A.TXT / S5F.TXT / S5U.TXT
```
指针：`01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:182-188`
导出 sha256：`S5A` `849bcb30…`｜`S5F` `59314333…`｜`S5U` `6ef6656b…`（`27_…:85-87`）

### 2.8 exFAT 实验（★ 需人工 `sudo`，AI/自动化进程过不去）

```bash
# 0) 工具复制到 /tmp（TCC 保护不到这里）
TOOLS=04_工具与脚本/campaign2
mkdir -p /tmp/s5exfat && cp "$TOOLS"/exfat_patch.py "$TOOLS"/exfat_spray.py "$TOOLS"/s5_exfat_test.sh /tmp/s5exfat/ && chmod +x /tmp/s5exfat/*

# 1) 相机格式化 SDXC（>32GB）→ 拍 1 张 → 【正常关机】→ 拔卡插到 Mac
# 2) 写前体检（必须 K = 0，否则停手）
sudo bash /tmp/s5exfat/s5_exfat_test.sh checkalloc /dev/disk8s1
# 3) 写 360 个 240 字符长名目录项（复现崩溃）
sudo bash /tmp/s5exfat/s5_exfat_test.sh mkentries /dev/disk8s1 360 240 0
# 4) 写后体检（K 必须仍为 0；并检查"目录簇链"的新簇不在照片数据区）
sudo bash /tmp/s5exfat/s5_exfat_test.sh checkalloc /dev/disk8s1
# 5) 【正常关机】后拔卡 → 插进相机开机 → 应反复重启
# 恢复：diskutil eraseVolume ExFAT LUMIX /dev/disk8s1 → 相机自己格式化
```
指针：`00_项目总结/04_定因与工具链成果_20261013.md:132-153`；`01_研究报告/24_…:59-71`

```bash
# 只读诊断子命令（零风险）
sudo bash /tmp/s5exfat/s5_exfat_test.sh prep|info|entries|chain|bitmap|dumpbitmap
# 补丁类（有风险）
prep / info / entries / chain / bitmap / dumpbitmap  → 只读
setfat <簇> <值>  → 精确改一个 FAT 项（带 fsync + 重开设备复核）
go1 / go2 / session / sessionA / hijack → 自动挑目标 + 打补丁 + 回读校验
verdict / go1check → 比对与裁决（含卡代次守卫）
```
指针：`01_研究报告/25_操作记录与风险手册_20261013.md:147-153`；`04_工具与脚本/TOOLS.md:23-35`

### 2.9 离线固件分析（正确偏移，单一真源）

```bash
cd 14_总包审计与新方向_20261014/06_密码学重跑
python3 upd_table.py                    # [闸门] 判决实验，必须 7/7，否则后面的都无效
python3 exp1_record_sha.py              # 记录 SHA 语义（48 分区 × 2 偏移）
python3 exp2_known_plaintext_mode.py    # 已知明文 / keystream / CBC-vs-CTR
python3 exp3_cross_version.py           # V29 vs V24（+V11/V20/V23）
python3 exp4_positive_control.py        # ★ 阳性对照（约 30 秒）
bash run_all.sh                         # 一键全跑（约 35 秒）
```
**单一真源定义**（`upd_table.py:31-41`）：
```python
DATA_BASE = 0x200    # ★ doff 是相对它的偏移，abs_off = doff + 0x200
TABLE_BASE = 0x2EC   # 条目表起点
STRIDE = 92          # 每条 92 字节
COUNT_OFF = 0x2E8    # 条目数字段（运行时读取，不硬编码 48）
data(raw, e) -> raw[e.abs_off : e.abs_off + e.size]          # ★ 唯一取数入口
data_legacy_wrong(raw, e) -> raw[e.doff : e.doff + e.size]   # 仅供"错误偏移对照臂"
self_test(raw) -> 命中数                                     # type=2 的 sha256(data)==记录sha
```
指针：`14_…/06_密码学重跑/结论.md:27-46,379-391`

### 2.10 蓝牙（先写身份再读；可重试）

```bash
cd 04_工具与脚本/campaign2
swiftc -framework CoreBluetooth -framework Foundation -o ble_scan ble_scan.swift
./ble_scan 30        # 扫描 30 秒；命中 LUMIX 服务即自动连接并枚举 GATT
# 正确顺序（本机非 APS 分支，写入是原始字节不经密钥编码）：
# [B] 写 8D08A420 = 原始 DLNA_UUID 字节  值 = 4d454930010010008001020000025ad6
# [C] 写 CD7A71A0 = 原始设备名
# [D] 读 03E23A31 (idx35 INITIAL_INFORM) → 会话密钥
# [E] 读 E206A5C0 (idx5 CAMERA_SSID)
# [F] 读 C97CF1A5 (idx6 CAMERA_WIFI_PASSWORD)
```
指针：`01_研究报告/19_BLE凭据链打通_先写后读_20261013.md:42-49`；`01_研究报告/14_蓝牙BLE勘察_20261013.md:88-92`
**成功率约 50%，需重试**（`19_…:104-117`：4 次尝试 2 成）

---

## 3. 已证伪 / 已排除的路线（★ 最重要，防重复劳动）

### 3.1 固件 / 密钥线

| # | 试了什么 | 怎么试的 | 结论 | 指针 |
|---|---|---|---|---|
| ✗A-1 | 从固件文件内找 AES 密钥（XOR / RC4 / AES-128/192/256 各模式） | 130k+ 探测；候选含 loader1 24B+64B、`0x220` 64B 块、SHA/MD5 派生；阳性对照见 §1.2 A-7 | **容器内无密钥材料**；但**旧两次"0 命中"证据无效**（错位 0x200） | `02_研究总报告_20261011/09-已证伪路线.md:5-12`；修订 `14_…/00_审计总报告.md:102-145` |
| ✗A-2 | 真 AES 密钥恢复测试（5240 key × 3 IV；211 候选） | 用已知明文（`ipu_data` 的明文 SHA == `history`）当 oracle | **❌ 推翻（证据无效）**：错误偏移下 12/12 假阴性 | `14_…/06_密码学重跑/结论.md:326-327` |
| ✗A-3 | 跨版本差分推明文/密钥（V11/V20/V23/V24/V29） | 比对同偏移密文相等率；IV 稳定性 | **封死**：相等率 ≈0.4% = 随机基线；41 个 IV 逐版本全变；SSTIC 旋转规律**不成立** | `S5_AES…:83-114` |
| ✗A-4 | Nikon/WonderLantern「padding 泄露 keystream」手法迁移 | 同明文不同 IV 的两对分区密文 XOR 熵 | **原理上不成立**（XOR 熵 7.999，非固定流）；S5 是真 AES + 随机 IV | `S5_AES…:537-546,573` |
| ✗A-5 | 旧 GH2 PTool「密钥切片自嵌法」移植 | 6 张表 × 12 输入 MD5/RC4 key = 120 组合 | **全失败**（S5 是硬件密钥）；S1M2 上 120 组合亦全败 | `01_研究报告/01_固件AES绕过…/00-总评估报告-中文.md:88`；`03-离线破解…/S1M2固件逆向_阶段结果汇总.md:98` |
| ✗A-6 | 改 `comm_proto_ver` 版本号绕过版本门 | 字段方向分析 + APK 反编译 + 握手实际报文 | **不成立**：`comm_proto_ver=10.0` 是相机→App 单向字段；握手**不携带客户端版本**；App 侧**无版本比较分支**（"请更新 App"是通用连接失败文案） | `01_研究报告/03_…/docs/01_版本门与握手修复.md:8-25` |
| ✗A-7 | 「每台相机/每个固件版本 AES 密钥都不同」这一误区 | 5 版 IV 实测 + 官方单一 `.bin` 事实 | **纠正**：变的是 **IV（随版本）+ 明文（随相机）**，**密钥固定、所有 S5 共用** | `S5_AES…:138-166` |
| ✗A-8 | 「512 字节起为明文/低熵」这一加密弱点 | 对 41 个 type=3 分区检查 512B 起是否重复/低熵 | **全部满熵密文**；旧观察只出现在 type=2 擦除态分区 | `S5_AES…:76` |
| ✗A-9 | PTool 旧表提取的"记录 SHA ≠ 存储字节哈希"结论 | 修正偏移后重跑 | **❌ 推翻**：记录 SHA **就是明文 SHA**（type=2 7/7；type=3 由 `ipu_data` 独立证明） | `14_…/06_密码学重跑/结论.md:94-97` |
| ✗A-10 | `0x220` = ECDSA P-256 签名 → 推出"改版本必破签名" | ECDSA 公钥恢复穷举 90,144 组 | **算法归属不可判定**（源头已自我撤回）；**「版本字段在签名覆盖内」= 不可判定**；「ECDSA 覆盖外层头 0x0-0x200」这一具体假设**在穷举范围内被排除** | `14_…/07_签名与密钥恢复/结论.md:12-22,219-235` |
| ✗A-11 | 「尾块是 RSA-4096」并据此推"首字节 `89 a1` ≠ PKCS#1 v1.5" | RSA 模数恢复（e 全部候选） | **未恢复出 N ⇒ 无正面依据**；且 `89 a1` 推理**在密码学上不成立**（`s=m^d mod N` 近似均匀，与填充无关） | `14_…/07_…:269,273-284` |
| ✗A-12 | 「改版本号"不能绕过版本门"」的证伪依据 | 审计裁决 | **该证伪依据（签名覆盖）也已不成立** ⇒ 既不能支持"能绕过"，也不能支持"必然被拒" | `14_…/00_审计总报告.md:497,529` |

### 3.2 转接环 / 跨机型 / 跨团队线

| # | 试了什么 | 结论 | 指针 |
|---|---|---|---|
| ✗B-1 | 改 VILTROX EF-L 转接环固件摸 S5 的 AES 密钥 | **死路**（三重论证）：转接环是卡口 I2C 上**独立从机 MCU**，走镜头通讯协议（AF/光圈/镜头 ID），**不进 SoC 安全密码域**；`EF-L 2.4.ecp`(59392B)→`efl_firmware.bin`(56500B) **是标定数据镜像、非代码**；环自带密钥是**另一套机密** | `01_研究报告/01_固件AES绕过…/00-总评估报告-中文.md:56-63,135-144` |
| ✗B-2 | 借用 S1RM2 的 `ffs` OOB 漏洞（F1/F2） | **不直接迁移**（SC2006A/A53 vs MC801/A7，不同 SoC 家族） | `02_研究总报告_20261011/09-已证伪路线.md:20-24` |
| ✗B-3 | 「S5 OSS 内核树里没有 `current_alt_setting` ⇒ S5 无该 OOB」 | **❌ 机型绑定错误**：那棵 771MB `linux-3.18.18` 的下载 URL 是 **`DC-FZ1K2`**（另一款机型，OSPO 有独立页）⇒ **对 DC-S5 实机不具备排除力** | `14_…/08_实机与离线验证记录_20261014.md:238-253` |
| ✗B-4 | 拿 S5II（S5M2）的录制规格/token/字段地址移植到 S5 | **无可行性**：换代平台（blob 65,533B/831 记录 vs 2,252,861B/966 记录；tag 体系不同，S5 最大 tag `0x04b5`）；**不要用 S5II 的 blob/tag 直写 S5**（属盲写） | `01_研究报告/10_跨机型移植边界_20261013.md:10-24,59-72` |
| ✗B-5 | 移植 S1H 的 400Mbps ALL-I（`mp4ed_25p_400mbps_4k_10bit`） | **44 个 NTSC 候选 0 个读回正常**；S5 的 mp4ed 实为 MP4+LPCM 1080p60 | `01_研究报告/09_…_mp4ed_20261013.md:39,46-54` |
| ✗B-6 | 把 6K PHOTO「换皮」塞进【录制文件格式】菜单 / 添加自定义菜单条目 | **做不到**：菜单树由固件提供（`allmenu`），**不存在我们能写的 65,533B blob 里**；对 blob 的所有写入**从未改变过 `allmenu` 任何条目** | `01_研究报告/11_菜单条目注入可行性_20261013.md:39-51` |
| ✗B-7 | 靠 S1H 的「添加到列表（My List）」注册隐藏档 | **S5 无该机制**（全量菜单扫描无任何 list 项） | `01_研究报告/09_…:85-86`；`01_研究报告/30_…:311-312` |

### 3.3 网络 / RCE 线

| # | 试了什么 | 结论 | 指针 |
|---|---|---|---|
| ✗C-1 | 编译 C / `LD_PRELOAD` 注入（CVE-2017-17562 思路）：MIPS 小桩 `payload.S` + `s5pre_mipsel.o/.so`(1968B)，标记 `S5_RCE_PROOF` | **阴性**：多种 payload/preload/mode 组合一律回 `err_critical`，**无标记、无代码执行** ⇒ GoAhead 不把 `LD_*` 传入 CGI 环境，或 `cam.cgi` 静态链接 | `02_研究总报告_20261011/05-RCE与代码注入.md:18-23` |
| ✗C-2 | HTTP 头/参数溢出 fuzz（`overflow_fuzz.py`、`goahead_overflow.py`） | **阴性**：无越界崩溃、无可控返回地址 | `02_研究总报告_20261011/05-…:33` |
| ✗C-3 | Wi-Fi 调试后门枚举 ~70 个候选 mode（dmesg/memdump/flash/jtag/uart/keydump/otp/efuse…） | **全部回通用 `err_param`**（HTTP 200），健康探针全程 `ok` ⇒ 研究版**无**隐藏调试后门 | `01_研究报告/01_固件AES绕过…/03-离线破解…/Wi-Fi实机预言机与mode枚举实测-中文.md:77-88` |
| ✗C-4 | `getinfo` 子类型 ~110 个候选（serial/sysinfo/kernel/os/cpu/hw/debug/log/env/uptime/config…） | **全部 err/reject** ⇒ 无敏感系统信息泄漏通道 | `01_研究报告/03_…/docs/04_camcgi_RCE面测绘.md:51-52` |
| ✗C-5 | 整数溢出（size=0xFFFFFFFF / 2^31 / 2^32）、HTTP 请求走私 1–6 | 全 `err_critical`/`err_param`/`400`，**无崩溃** | `02_研究总报告_20261011/06-崩溃与DoS.md:30-31` |
| ✗C-6 | PTP 参数/TID 边界 fuzz（43 只读探测） | 回干净错误码且**保持存活**；仅发现"参数数量不校验/TID 不校验"（**可利用性低**） | `S5_AES…:449-480` |
| ✗C-7 | 「反复 invalid login / 需重启」当漏洞 | **非漏洞**：根因 = **陈旧 pending 请求**污染唯一的"待批复槽"；已修复（同一 uuid + `req_acc_can` 清理） | `01_研究报告/03_…/docs/01_版本门与握手修复.md:29-49` |
| ✗C-8 | 「BLE 读取需要配对/绑定」 | **❌ 推翻**：真因是**协议顺序**（先写身份再读）。注意后续又出现"`err_user_refused` 需 BLE 绑定"的**新假设**（0 次验证） | 推翻 `01_研究报告/19_…:1-4`；新假设 `01_研究报告/20_…:191-205` |
| ✗C-9 | 「BLE 握手会唤醒相机热点」/「扫到开放网络 = 相机热点」 | **两条均证伪**：前者复测 `Could not find network`；后者周边有多个开放网络，**假阳性** | `01_研究报告/20_…:102-120` |
| ✗C-10 | 官方 App 不走 `http://<ip>/DCIM/...` 拉文件 | 官方走 DLNA 60606；`/DCIM` 是旁路 | `01_研究报告/01_固件AES绕过…/01-固件格式与启动/PROTOCOL_AUDIT.md:145-154` |
| ✗C-11 | 官方协议里没有的"删除照片"与"上传 LUT" | **`startsenddata` 的 type 只有 `camsetting` 与 `fw` 两种**；全源码无 LUT 文件传输；官方无任何删除命令 | `PROTOCOL_AUDIT.md:124-139,162-163` |

### 3.4 固件升级写路径（★ 核心阻塞）

| # | 试了什么 | 结论 | 指针 |
|---|---|---|---|
| ✗D-1 | 流送全部 1474 个完整 61192B 块 + 尾块 41456B | **能干净流送全部完整块**（fast 81ms/块、pace 150ms/块均成功），但**最终部分块始终失败**：首个 → `err_busy`（触发 **~31s flash 定址**）→ 重试 `err_critical`（快） | `02_研究总报告_20261011/04-固件升级写路径.md:28-42` |
| ✗D-2 | 判别"是否与内容有关"——CONTROL 组发**未改动的真 V29 镜像** | **同样在末块失败**（1474 块 ok/536.6s → final 12 次重试全 `err_critical`，第 4 次起 ~30.8s/次 → `abortsenddata=error`）⇒ **与内容无关** | `logs/写路径/campaign.md:22726-22727`（原文：`TRANSPORT ISSUE: unmodified data ALSO failed at the final chunk`） |
| ✗D-3 | 判别"是否与节奏有关"——87ms / 158ms/chunk | **都失败**（官方 App 是 ~138ms/chunk）⇒ **与节奏无关** | `04-固件升级写路径.md:45-47` |
| ✗D-4 | 判别"是否与状态有关"——拔电池全新重启 | **依然复现** ⇒ 与状态无关 | 同上 `:47` |
| ✗D-5 | 小样本探针（`total=61192` / `102648`）逼近真实定址 | **不行**：`total ≤ 61460` → `method=once` → 小镜像 `err_reject`；`102648`（1 整+1 部分）**部分尾块 `err_reject`(0.10s 快拒)** ⇒ **只有真 90MB 镜像能走到 flash 定址** | `04-固件升级写路径.md:50-56` |
| ✗D-6 | 「在固件升级过程中改升级字节」（Magic Lantern 式） | **不可行**（三条独立证据）：① 无任意地址写原语（地址由机身下发）② 容器双签名 ③ PTP 侧**无 RAM 读回**操作码（逐条核实 6 条路径 0x9112/0x9703/0x9605-07/0x9706-07/0x9421） | `S5_AES…:335-342` |
| ✗D-7 | PTP 走"可测试状态"再探测地址 | **路线关闭**：要拿到地址必须**先发 `0x9406/0x00090013`（FWUP Request）**，该动作**很可能先擦除目标区域**；若擦除后写不进 → **相机可能再也开不了机**，且**兜底无**（SD.DAT 有砖机史）；收益上限只是"把已签名固件写到错误地址" | `01_研究报告/28_PTP固件更新协议审计_20261013.md:122-134` |
| ✗D-8 | `finalfix.py` 的 "`err_fw_same` = FLASH LANDED" 判据 | **与同项目 `control.py` 直接矛盾**，且 `oracle/README.md` 已实测证明该前提失效（正确签名的旧固件上传得到的是 `err_critical`） | `14_…/00_审计总报告.md:217-232` |
| ✗D-9 | 上传预言机（阶段 1/2/3：翻转字段看响应是否变化） | **阶段 1 前提已失效**：原始旧固件上传实测回 `err_critical`（不是 `err_fw_same`）；**"无逐字节/逐分片反馈、无可用时差"** ⇒ 建议**停止上传预言机这条线** | `01_研究报告/01_固件AES绕过…/03-离线破解…/oracle/README.md:73-90` |

### 3.5 录制格式线（穷尽性负结果）

| # | 试了什么 | 结论 | 指针 |
|---|---|---|---|
| ✗E-1 | **5.9K 片门全开**（`mov_24p/25p/30p_200mbps_5_9k_10bit`、`mov_5_9k_*_420_10l`、`mov_c24p_*_5_9k_10bit`） | **全部失败**。四变量全覆盖（PAL✓/NTSC✓ × 视频模式✓/**6K PHOTO 模式✓** × 每档最多 12 次退避重试 × 3 个命名族）。返回 `err_reject`/`err_param`/`ok 但未生效` | `01_研究报告/30_…:81-96,144-170` |
| ✗E-2 | 5.9K 的**实拍终判** | `P1000004.MOV` = **4096×2160 @59.94fps hvc1 ~195Mbps**（= C4K 60p），**不是 5888×3312**。请求 5.9K **30p** 却出 C4K **60p** ⇒ 未知码被回退到顶档 | `01_研究报告/08_格式对照表_NTSC-MOV_20261013.md:145-147` |
| ✗E-3 | 5.9K 的**菜单层** | `curmenu` 的 5.9K 项**永远 `enable="no"`**（连 `videoquality_filter_pictsize_5_9k` 也是 no）——由固件**按机型硬编码**，与当前值/容器/制式无关 | `01_研究报告/08_…:143,149-150` |
| ✗E-4 | 「写全 13 槽（`06 ×13`）是推荐修法」 | **已修订**：相机自身行为是**仅写槽 0**；但审计发现**反例取自协议修复前的无效跑**（`blob_postreboot_movshadow_*` 对应 01:57 那次单次 POST），而分块全槽写（GOLD `06×13`）**反而持久** ⇒ **因果未确立** | `README.md:65`；`14_…/00_审计总报告.md:149-180`（S3） |
| ✗E-5 | 「flash 存安全值 + RAM 上隐藏档」双轨方案 | **实测证伪**：菜单读的是 **RAM 值** | `01_研究报告/30_…:229-237` |
| ✗E-6 | `hlg=8k` 隐藏档（HLG 照片） | `setsetting hlg=8k` → `ok`，但 play 模式读回**仍 `off`**（模式门控）；`full`/`4k` 在 play 模式同样不持久 ⇒ 整个 hlg 域在 play 模式是"只读回显" | `01_研究报告/03_…/docs/02_隐藏功能.md:16-29` |
| ✗E-7 | **`4kcrop` 相关项** | **禁碰**：`4kcrop=20/40` 被拒；**写 `4kcrop` 导致相机约 80 秒无响应**（自行恢复，副作用是 `videoquality` 掉回默认） | `01_研究报告/12_可写设置面审计_20261013.md:38,66` |
| ✗E-8 | `shtrspeed_angle`（快门角度） | **空转**：写 `180` 能读回 `180`，但 `shtrspeed` 不变、`f_and_ss_angle` 菜单项仍 `enable=no` | `01_研究报告/12_…:37` |
| ✗E-9 | `photostyle=hlg`/`hlg_standard`/`hlg_bw`/`custom5..custom10` | **回 `ok` 但被静默忽略**（读回仍 `standard`）；`vlog_l` → `err_param` | `01_研究报告/12_…:44-46` |
| ✗E-10 | `mov_25p_400mbps_c4k_10bit` | `ok` 但回读为空（相机忙），**未生效** | `01_研究报告/30_…:130` |

### 3.6 exFAT / 内核线（含两条重要撤回）

| # | 试了什么 | 结论 | 指针 |
|---|---|---|---|
| ✗F-1 | **「S5 内核越界写已实机确认」** | **❌ 撤回**：决定性实验（注入索引 120 = 必为 NULL 的 slab 填充区）→ **只报错不崩溃** ⇒ 原判据「相机报写入错误 ⇒ 内存写已执行」**不成立**（NULL 提前返回表现完全一样） | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:12-43` |
| ⚠F-1b | 「越界索引处**存在** NULL 检查」 | **◐ 该撤回逻辑本身也不成立**：`vol_amap = kmalloc_array(...)` **不清零**（非 `kzalloc`），越界槽内容取决于堆复用历史，**该前提从未被测量** ⇒ **"越界写"与"NULL 提前返回"两者均未证实** | `14_…/00_审计总报告.md:277-285`（A7） |
| ✗F-2 | **「堆喷命中越界槽」** | **❌ 撤回**：A/B 对照——**去掉注入后照样重启** ⇒ 崩溃不能归因于注入 | `01_研究报告/23_…:166-174` |
| ✗F-3 | 三轮堆喷（240 长名 / 120 长名 / 120 短名+篡改 `num_ext`） | **全部失败**：相机**只报「写入错误」、从未崩溃** —— 与"槽位是 NULL、提前返回"完全一致 | `01_研究报告/23_…:134-141` |
| ✗F-4 | 「长名崩溃 = 数量 × 长度」 | **⚠️ 初版结论被污染**：当时工具把目录链拐进了照片数据区；重做后结论改为 **长文件名本身** | `01_研究报告/24_…:107-123` |
| ✗F-5 | exFAT 越界写路线整体 | **判定不成立，不再投入** | `00_项目总结/04_…:164` |
| ✗F-6 | 我们自己的 exFAT 工具（旧版 `alloc_one_cluster` 只信位图） | **曾把真实照片的簇分配掉、目录链拐进数据区**（`FAT[39]` 被改成 482）；已修复为**三重校验**（位图位==0 **且** 不在目录链上 **且** `FAT[clu]==0`） | `01_研究报告/24_…:110-123` |
| ✗F-7 | S5 U-Boot console 离线核验 | **S5 上不可判定**（正确偏移搜 7 个 type=2 分区，2,490,368 字节，关键词命中 **0**）；且发现这 7 个"明文分区"其实是 **OTA 容器里的空占位**（4 个全 0x00、2 个全 0xFF、`storage` size=0）；**OSPO 未发布 u-boot 源码** ⇒ 离线路径本就不存在 | `14_…/08_实机与离线验证记录_20261014.md:132-153` |
| ✗F-8 | 已知明文扩面（找更多已知明文推 AES） | **已关闭**：41 个加密分区 × 13 均匀模板 + 4 结构模板 ⇒ **仅 `ipu_data` 1 命中**。**全库只有这一对**，是硬约束 | `14_…/08_…:155-174` |

### 3.7 服务模式 / ROM BACKUP / USB 服务态

| # | 试了什么 | 结论 | 指针 |
|---|---|---|---|
| ✗G-1 | 「ROM BACKUP 灰 = 未解除初始设置 / 未释放 Strict」 | **❌ 推翻**（作者自述"这推翻了我此前排在第一位的假设"）：真因是 **SD 卡文件系统**（exFAT→灰；FAT32→可用）。**不需要触碰任何不可逆步骤** | `01_研究报告/13_…:182-191` |
| ✗G-2 | 靠服务模式拿固件明文 / AES 密钥 | **不行**：ROM BACKUP 只导出 EEPROM 标定/参数区（三期各 128KB），**不是**内核/rootfs 明文，**不含 AES 密钥** | `01_研究报告/27_…:154-158` |
| ✗G-3 | 靠工程模式新增录制质量档 | **没有**：工程模式 `curmenu` 与普通模式一致（18 档） | `01_研究报告/13_…:103-104` |
| ✗G-4 | `0x2370` 服务态 USB 通道（EP0 厂商 IN/OUT、bulk OUT 8 种帧、bulk/interrupt IN 监听） | **三个方向全打不通**；**E0 双向穷举完毕** ⇒ 该任务**已从待办移除，不要再重复**。它很可能是**等松下服务软件**（非公开），不是等 Tether | `13_…/00_交接总结_全文.md:96-118,202-212,163-174` |
| ✗G-5 | 「第二个 USB 配置藏着固件更新接口」 | **已排除**（两配置只差供电，接口/端点逐字节相同） | `13_…/00_交接总结_全文.md:53-62` |
| ✗G-6 | 「`0x2374` 是 S5 的目标模式」 | **更正**：`0x2374` = DMC-FZ28（2008 便携机）；Tether 里类型 1 分支是**老机型兼容路径** | `13_…/00_交接总结_全文.md:90-92` |
| ✗G-7 | `!→LUMIX` 是"等 Tether" | **更正**：进入后对焦灯闪烁（"等待主机"），但**三方向依然全死** ⇒ 更可能等**松下服务软件** | `13_…/00_交接总结_全文.md:163-174` |

### 3.8 LUT / 功能层

| # | 试了什么 | 结论 | 指针 |
|---|---|---|---|
| ✗H-1 | 通过 Wi-Fi 上传 LUT / 让 S5「实时 LUT 烧进文件」 | **不可行**（三处零痕迹）：`allmenu`(740 item) 与 `curmenu` 的 LUT 菜单项 = **0**；`getinfo` 的 LUT 类 型（`lut`/`ad_lut`/`vlt`/`viewassist`/`lutinfo`…）**全部 `err_param`**；`capability` 无 LUT 能力位；`camsetting.bin` 中 LUT/VLT/cube 字样 **0 处** | `14_…/09_LUT可行性报告_20261014.md:19-30` |
| ✗H-2 | 「LUT 放 `/AD_LUT/` 目录」 | **纠正**：放 **SD 卡根目录**（官方硬要求）；本项目文档从未用过 `/AD_LUT/` | `14_…/09_LUT可行性报告_20261014.md:264-278` |
| ✓H-3 | **初代 S5 真正可行的"套 LUT"三路** | ① 机身 **V-Log View Assist**（LUT 放卡根目录 → 菜单读入 → 取景/HDMI 套用，**不写文件**）② 后期套 LUT ③ 监看流上实时套（工具已实现） | `14_…/09_…:105-150`；`15_LUT烧录工具_20261014/README.md:3-26` |
| ✗H-4 | 「`imgsize`/`imagesize` 等 LUT 别名」 | **顺带排除的两条歪路**（详见 `09_LUT可行性报告:94-102`） | `14_…/09_…:94` |

---

## 4. 已知陷阱与危险操作

### 4.1 会让相机变砖 / 挂死 / 需拔电池的操作

| # | 操作 | 后果 | 规避 | 指针 |
|---|---|---|---|---|
| D-1 | **反复大镜像流送（90MB）/ 末块反复重试** | 已**多次让相机 brick / 卡死**（拔电池恢复）；flash / 状态机对大镜像流送非常脆弱 | **绝不真刷**；`S5___V29.bin` 仅作 RECOVERY 用；用 `finalfix.py` 手动驱动末块、**不要用 `Upload.stream()`**（12× 重试风暴 + `abortsenddata` 会驱动状态机进未处理分支 → 卡死） | `02_研究总报告_20261011/06-崩溃与DoS.md:41-43`；`11-安全约束.md:23` |
| D-2 | **senddata 末块被拒 + 重试循环** | 相机内部升级状态机进入**未处理分支** → **需拔电池的彻底卡死**（用户实测复现） | 同上；每次操作后健康守卫 | `02_研究总报告_20261011/06-…:15-22` |
| D-3 | **PTP length 不符的包** | 数据面**永久等待（无超时）** → 接口挂死 | 发送前对 length 做精确计算/断言；`lenprobe` 模式是唯一故意的受控演示 | `S5_AES…:195` |
| D-4 | **短时间多次 `req_acc`** | 相机屏幕显示「**智能手机应用程序需要更新**」→ `invalid login` → **必须断电重启**（只能这样恢复）；所有端点开始回 `err_reject`/`err_unsuitable_app` | `req_acc` **只在启动时发一次**，之后只轮询 `getstate`；清理用**同一 UUID** 发一次 `req_acc_can` | `12_S5无线监看_v1.0_20261014/附_技术参考.md:139-154`；`25_…:366-375`；`14_…/10_仓库补丁/定因与交接:246-275` |
| D-5 | **裸 `curl` 不带 `value`（UUID）发 `req_acc`** | 留下**匿名 pending** ⇒ 之后带正式 UUID 的请求撞上它 ⇒ `err_others_requesting` | 所有操作走监视器 HTTP API，不要绕过它直接打相机 | `12_S5无线监看_v1.0_20261014/README.md:231-241` |
| D-6 | **用 `req_acc_can` 打断已 `ok` 的会话** / `err_others_requesting` 时清理 | 误伤他人请求、污染状态 | 见 D-4 三条规则。**裸 `ok` 才算授权**（`ok_under_research*` **不是**授权） | `25_…:203`；`01_研究报告/20_…:156-157` |
| D-7 | **写 `4kcrop`** | 相机**约 80 秒无响应**（自行恢复，副作用 `videoquality` 掉回默认） | **禁碰** | `01_研究报告/12_…:38,66`；`25_…:24` |
| D-8 | **`a6k` 家族** | 返回 `ok` 却**静默把容器改成 avchd**（本机是 PAL 机型，会跳到 `avchd_50p_28mbps`） | **禁用该家族**；`s5_quality.py` 默认拒绝并自动恢复 | `01_研究报告/30_…:105-124` |
| D-9 | **在机身菜单界面读 `camsetting`** | 一律回 `err_reject`（86 字节），其它 getinfo 正常 | 让相机**退出菜单停在普通拍摄画面**；`download_blob` 已加提示 | `01_研究报告/07_…:121-123` |
| D-10 | **`cammode=play` 时做视频域实验** | `setsetting videoquality=<隐藏档>` 一律 `err_param`，**且已回 `ok` 的调用也不生效**（当天两轮扫描因此作废） | 先 `getstate` 确认 `cammode=rec` | `01_研究报告/30_…:40-42` |
| D-11 | **动机身模式拨盘** | **断开远程连接** | 用 API：`camcmd&value=recmode`/`playmode` | `01_研究报告/30_…:46-52` |
| D-12 | **写 flash 时不接 AC / 断电** | 砖机风险 | 写 flash 必须 AC 供电；恢复唯一手段 = **拔电池** | `25_…:16`；`README.md:171` |
| D-13 | **拔 SD 卡前不在相机里正常关机** | 相机分配位图**延迟写回** ⇒ 位图停在旧状态 ⇒ 任何按位图分配的工具会**踩到正在使用的簇**（真实发生过：照片被毁、目录链拐进数据区） | **拔卡前必须正常关机**；**每次写卡前后各跑 `checkalloc`**，`K>0` 立即停手 | `01_研究报告/24_…:126-128`；`25_…:20-21` |
| D-14 | **服务模式里点 `SDxxx→DSC` / `ADJFLAG→ALL F` / `WBADJ→STEPMODE`** | 写回覆盖机身标定 = **不可逆**；`ADJFLAG→ALL F` 改写机身调整标志 | **只动 `DSC→SD`（导出）**；其余一律不碰 | `01_研究报告/27_…:39-52,191`；`13_…/00_交接总结_全文.md:238-239` |
| D-15 | **按 `DISP.` 键（在 INITIAL SETTINGS 界面）** | **解除 `[Strict]` 模式** ⇒ 地区后缀变成**可改且仅一次机会** | **绝不按 `DISP.`** | `01_研究报告/13_…:247-248`；`14_…/00_审计总报告.md:574` |
| D-16 | **为点亮 ROM BACKUP 去做"解除初始设置/地区后缀"** | 地区后缀**单次写入锁止、不可逆** | **不需要**（真因是 FAT32）；收益与风险不成比例 | `01_研究报告/13_…:114-116` |
| D-17 | **`0x9406` 任意子码（尤其新增的 `0x00090013` FWUP Request）** | **疑似先擦除目标区域**；擦除后写不进 → **相机可能再也开不了机**；**兜底无** | **永不发送 `0x9406` 子码** | `01_研究报告/28_…:122-134` |
| D-18 | **`0x9406` 带副作用子码 / `0x9422`/`0x9423` PTP 配置写回 / `0x940d` 电源 / `resetDevice`** | 不可逆/毁配置 | 项目红线，绝不执行 | `02_研究总报告_20261011/11-安全约束.md:11-17`；`README.md:173` |
| D-19 | **未读的 PTP 命令让 bulk 通道卡住** | 需 USB 重插复位（相机本身不受影响） | 发送前精确计算 length；只读操作码白名单 | `01_研究报告/13_…:167-168` |
| D-20 | **`err_critical` 当致命错误** | 可能只是瞬时状态 | **先重试一次**（实测 `camcmd&value=recmode` 重试即 `ok`）；仍失败才重启 | `01_研究报告/30_…:375` |
| D-21 | **把「相机报写入错误」当「内存写已执行」** | **致命判据错误**（NULL 提前返回表现完全一样）；**S1R2 报告也用了该判据，后人不应照抄** | 已写入项目铁律 | `REPO_CONTENTS.md:67-70`；`01_研究报告/23_…:40-42` |
| D-22 | **`fsync` 与回读 fd** | 块设备写入可能停在页缓存，**拔卡就丢**；同一 fd 回读可能命中缓存 | 必须 `fsync`；回读**关闭后重新打开设备** | `01_研究报告/22_…:75-76`；`25_…:266-267` |
| D-23 | **macOS 会生成 `._` 副档名文件** | 每个文件变两个目录项，**名字还更长** ⇒ 实验变量翻倍 | 造测试文件后必须 `rm -f ._*` | `25_…:273` |
| D-24 | **`bash` 变量紧邻全角字符** | `$VAR（` 被当成变量名一部分，`set -u` 下 `unbound variable` ⇒ **恢复函数从未执行**（实测发生） | 一律写 `${VAR}` | `01_研究报告/18_…:39-43`；`25_…:272` |
| D-25 | **`setsetting` 后不回滚** | 未声明值会让机身菜单变灰（已实际发生一次）；`mp4ed` 残留会让【录制文件格式】多出 "(LPCM)" 条目且两项全灰 | 实验后必须 `restore`；改质量前确认名字在 `allmenu` | `01_研究报告/09_…:76-86`；`01_研究报告/12_…:63-64` |
| D-26 | **写 flash 前不确认槽 1 已挂载** | 槽 1 未挂载时 `videoquality` 可能在**开机阶段**被降档（`0x9b`→`0x9f`） | 写前确认 `getstate` 的 `sd_memory=set` | `25_…:387-396`；`01_研究报告/31_…:123-138` |

### 4.2 环境 / 主机侧陷阱（不会伤相机，但会浪费大量时间）

| # | 陷阱 | 真相 | 指针 |
|---|---|---|---|
| E-1 | macOS 原始磁盘设备访问 | **双重保护**：Unix 权限（`brw-r----- root operator`）+ **TCC**（即使 `osascript` 提权到 uid=0 仍 `Operation not permitted`）⇒ **自动化/AI 进程两条路都过不去，必须人工 `sudo`** | `00_项目总结/05_环境与依赖.md:135-153` |
| E-2 | `osascript` 提权后的 root shell | **访问不了 `~/Documents` 等受保护目录**（`Operation not permitted (126)`）⇒ 脚本要放 **`/tmp`** | 同上 `:155-156` |
| E-3 | macOS 没有 `setsid` | `setsid nohup …` 直接"命令未找到"，**脚本静默不执行** | 用 `( nohup bash script.sh args >/dev/null 2>&1 & )` | `01_研究报告/18_…:38-39` |
| E-4 | macOS 上 pyusb/libusb bulk IN | 报 `EOVERFLOW`（Errno 84）**不可用** | 用 macOS 原生 ImageCaptureCore（`s5_ptp_dump`）或自建 IOUSBLib 客户端 | `02_研究总报告_20261011/07-USB-PTP-SCSI.md:51`；`05_环境与依赖.md:79` |
| E-5 | 云盘类 App 抢占 USB 设备 | 夸克网盘（`QuarkCloudDrive`）曾挂 `IOUserClient` ⇒ PTP 完全无响应 | `ioreg -w0 -l -r -n DC-S5 | grep IOUserClientCreator` 检查并退出占用者 | `05_环境与依赖.md:126-128` |
| E-6 | `ffprobe`（Homebrew ffmpeg 9.0.1_1） | **崩溃**：`Symbol not found: _av_bprint_finalize` | 自写 Python 解析 MOV/MP4 box（`tkhd`/`stsd`/`stts`/`stss`） | `05_环境与依赖.md:78` |
| E-7 | `airport` 工具 | macOS 14+ 已移除；CoreWLAN 读 SSID/BSSID 需**定位权限**，CLI 下返回 nil | 给终端开定位服务 | `05_环境与依赖.md:81,129-130` |
| E-8 | macOS SoftAP 连接不稳定 | `-3970` 12+ 次、`-3906` 3 次、`Could not find network` 4+ 次；三层原因（单客户端 / macOS 无互联网自动回落 / AP 时开时关） | **改用 station 模式（相机连家庭路由器）** | `01_研究报告/20_…:19-36,91-98` |
| E-9 | Windows MT7921 关联相机热点 | **本机侧问题**（驱动不吃这条非标准信标：HT Operation Basic MCS Set 全 0、Extended Capabilities 仅 1 字节、Beacon Interval 200 TU）；**手机曾成功连上 ⇒ 相机接受客户端** | 换主机栈（macOS/Linux/手机） | `01_研究报告/17_…:318-330` |
| E-10 | SSDP 公布错误的网卡地址 | `SSDPAdvertiser._detect_ip()` 硬编码 `192.168.1.1` ⇒ 多网卡时公布家网地址，**相机在热点网段够不到** | 已改为按【相机地址】探测路由 | `12_S5无线监看_v1.0_20261014/README.md:498-511` |
| E-11 | 实时 LUT 性能 | **必须在真实分辨率上测**：320×240 合成图 20–26ms，真实 640×360 实测 **73–160ms/帧** ⇒ 队列空、反复重播上一帧 ⇒ 画面看起来**完全卡死** | 预计算 256³ uint8 精确查表（6.7ms，零损失） | `12_S5无线监看_v1.0_20261014/README.md:254-272` |
| E-12 | `.cube` reshape 轴序 | `.cube` 规范是 **R 变化最快**，numpy C-order `reshape(N,N,N,3)` 得到的是 `[b,g,r]` | 必须 `transpose(2,1,0)`；由"`.cube` 与 `.vlt` 结果必须一致"的验收标准抓出 | `12_S5无线监看_v1.0_20261014/README.md:133-135` |
| E-13 | 心跳的两难 | 不发心跳 → 相机约 **13 秒后停流**；每 2–3 秒 → 相机持续繁忙、流反复卡顿 | **每 10 秒一次**（且状态走服务端缓存）⇒ 稳定零停顿 | `12_S5无线监看_v1.0_20261014/附_技术参考.md:52-62` |
| E-14 | `startstream` 残留会话 | 上次没 `stopstream` 干净关闭，新 `startstream` 回 `err_busy` | 先 `stopstream` 清场 + 退避重试 4 次 | `12_S5无线监看_v1.0_20261014/附_技术参考.md:26-27` |
| E-15 | 诊断面板 `max_camera_gap_ms` | 是**累计值**，会把"流重启时的 10.7 秒空档"永远算在里面 ⇒ **看起来像一直没修好** | 看**近期窗口**（README 给出 250ms×20s 采样脚本） | `12_S5无线监看_v1.0_20261014/README.md:375-400` |
| E-16 | 微信路径读不了 | `/Users/<user>/Library/Containers/com.tencent.xinWeChat/...` 被 **macOS TCC** 挡住（`Operation not permitted`） | 仓库内 `01_研究报告/05_Panasonic_hidden_format_参考/` 是同一包副本 | `01_研究报告/09_…:6-9` |

### 4.3 ⚠️ 工具代码层面的已知缺陷（安全相关，汇编请务必收录）

| # | 缺陷 | 位置 | 后果 | 指针 |
|---|---|---|---|---|
| T-1 | **已撤回的错误判据仍活在工具运行路径里** | `campaign2/exfat_patch.py:15`（模块 docstring"相机报写入错误**即为已执行**"）、`:535`（`go2` 交互提示"内存位清除**已经执行**⇒越界写成立"）、`s5_exfat_test.sh:18,121-124`、`TOOLS.md:33` | 操作者现场读到并据此判断；**分发物仍在扩散"把报错当成功"的操作规程**；**普通 grep 扫不到** | `14_…/00_审计总报告.md:198-215`（A1） |
| T-2 | `persist.py` 忽略关键 ACK | `:450` `requestsenddata` 返回值**完全未检查**；`:406,446` `abortsenddata` 未检查；`:344` `_upload_payload` 返回值被丢弃后无条件 `cmd_verify` 并打印 done | separate 模式下块序错位/截断却报成功；失败时可能残留 send 会话 | `14_…/00_审计总报告.md:246-254`（A4） |
| T-3 | **`s5monitor.py` 对外暴露 + 无认证 + 白名单被绕过** | 绑 `0.0.0.0`（`:442,1348,1456`）；`/api/setting`（`:937-943`）直接调 `setsetting`，**绕过** `ALLOWED_CAMCMD`/`ALLOWED_CAMCTRL` 白名单；控制端点全是 GET（**CSRF**）；`:126-138` 在任何 `err_reject` 上自动重发 `req_acc`（**与文档自己的红线冲突**）；`www/index.html:475,496,516,523,531` 用 `innerHTML` 拼相机原始回复（XSS 面） | 与 `README.md:100`/`使用说明.md:154`/`附_技术参考.md:173` 声称的"**代码内置白名单，永不发送有副作用的命令**"**直接冲突** | `14_…/00_审计总报告.md:256-267`（A5） |
| T-4 | exFAT 工具链缺破坏性防护 | `exfat_patch.py`/`exfat_spray.py` **0 个交互确认**；`go2` 只打印警告就直写 `/dev` 原始块设备；**不校验命令行传入的设备是否为目标卡**；卡代次守卫**只在 `verdict` 里**；无 dry-run；`BACKUP` 单条且每轮被清空 | 传错一张 exFAT 卷会被直接改写 | `14_…/00_审计总报告.md:269-275`（A6） |
| T-5 | `exfat_spray.py:22` 仍按 **8 字节指针**设计喷洒 | 而 `23_…:155-164` 已更正 S5 为 **32 位 → 4 字节 → kmalloc-512** | **工具未同步** | `14_…/00_审计总报告.md:275` |
| T-6 | PID 口径三套混用 | `ptp/s5_ptp_raw.c:35` 与 `13_/02_工具/README.md:26` 默认 `04da:2370`；`ptp/PTP_0x9421_dump_使用说明.md:60` 说 `PID=0x2382`；`s5_ptp_dump.py:27,93` 又说 0x2382 的 bulk IN = 0x82 | **工具可能抓错设备** | `14_…/00_审计总报告.md:385-389`（B8） |
| T-7 | `videoquality` 宽度冲突 | `persist.py:163,331` 按**单字节** `blob[6986]`；`persist_quality.py:72,131` 与 `container_switch.py:88` 按 **2 字节 LE** `blob[6986:6988]` | 若 `blob[6987]` 非 0，两条路径写回含义不同 | `14_…/00_审计总报告.md:388` |
| T-8 | 分块 overhead 硬编码 | `upload.py:353-360`、`finalfix.py:115-121` 把 `Content-Length` 写死 `61460`（而 `persist.py:415` 用 `%d`） | 若相机返回 6 位 `bufsize`，`payload = bufsize - len(sample)` 会错 1 字节 | `14_…/00_审计总报告.md:389` |
| T-9 | **`s5_quality.py` 的 docstring 数字与其他文档不一致** | 该 docstring 写「`curmenu` 声明 **126** 条 mov 档，`allmenu` 只有 **106** 条，机身实际可选仅 **17** 条」 | 与 `allmenu` 去重 **44**、mov `enable=yes` **18** 的权威口径**均不符**，属该文件自有旧数字 | `04_工具与脚本/campaign2/s5_quality.py:30-32` vs `01_研究报告/30_…:256` |
| T-10 | `TOOLS.md` 四类系统性失真 | ① 声明的 `exfat/`/`cam_cgi/`/`ble/`/`usb_ptp/` **四个目录均不存在**（实际是 `campaign2/`、`ble_win/`、`ptp/`）② 称"全部只依赖标准库"但实际用到 `pycryptodome`/`usb1`/`pyusb`/`bleak` ③ `ivsig.py` 称"签名与校验验证"实则**无法离线验签** ④ `s5_exfat_test.sh` 称内建 GO/NO-GO 拦截，实则 `l1/l2` **写前无任何确认** | 所有示例路径不可用 | `14_…/00_审计总报告.md:376-384`（B7） |

### 4.4 合规 / 脱敏风险

| # | 项 | 说明 | 指针 |
|---|---|---|---|
| C-1 | **完整机身序列号被十六进制写出** | `29_…:138` 的 `584a4c####################…` 解码即 `XJL########15` ⇒ **等于作废全项目统一脱敏**；同段还有 `MXD1D########` | `14_…/00_审计总报告.md:416-427`（C1） |
| C-2 | **真实 SSID/MAC 通过日志绕过正文脱敏** | 正文写 `S5-XXXXXX`，日志里是真实值：`campaign2/out/s5_ble_pair/ap_ble_pair.log`、`ble_pair_evidence/ble_cred_read.log`、`ble_lan/run.log` | `14_…/00_审计总报告.md:429-438`（C2） |
| C-3 | 主机侧与家庭网络身份外露 | 研究机 Wi-Fi MAC、Windows 用户名、主机 IP（`17_…:30,177-178`）；家网 SSID、本机 IP（`18_…:110-111`） | `14_…/00_审计总报告.md:440-446`（C3） |
| C-4 | **BLE 解码密钥硬编码在 8 个文件，且工具会打印明文 Wi-Fi 密码** | `0x9032782C` 分布在 `ble_win/s5_ble.py:18`、`s5_ble_handshake.py:116,120,132`、`s5_ble_watch.py:56,63,69`、`campaign2/ble_pair.swift:8,43`、`ble_write_then_read.swift:8,28`、`ble_lan_pair.swift:23,201`、`enc_handshake_test.py:10` | `14_…/00_审计总报告.md:448-451`（C4） |
| C-5 | **第二个机身序列号从未打码** | `60606` 设备描述 `serialNumber=WJ1DA######` + UDN 内嵌 Wi-Fi MAC | `14_…/08_实机与离线验证记录_20261014.md:83-94`；`14_…/05_…/README.md:60-63` |
| C-6 | 服务态 USB 字符串索引 3 | `0000000000000000000XJL########15`（**分发前必须脱敏**） | `13_…/00_交接总结_全文.md:49-51` |
| C-7 | 对外素材数字错误 | 小红书稿"**三个月**"（权威时间线 **6 天**）、"48 个分区里 **42** 个密文"（实为 **41** type=3）、三份英文稿 "**17** hidden modes" | `14_…/00_审计总报告.md:453-460`（C5） |

---

## 5. 未解决 / 开放问题

| # | 开放问题 | 现状 | 指针 |
|---|---|---|---|
| O-1 | **固件升级写路径为何卡在最终-chunk flash 定址？** | `~31s` 定址超时/磨损；**从未见过一次成功 `endsenddata`**；签名/版本 oracle 仍是开放问题 | `README.md:110-111`；`02_研究总报告_20261011/04-…:58-59` |
| O-2 | **末块定址失败是"可恢复的 flash 状态"还是"硬损伤/磨损"？** | 未答 | `02_研究总报告_20261011/10-下一步与开放问题.md:40` |
| O-3 | **相机是否强制 Stubby RSA 验签（ENFORCING）？** | 未答；决定 SD.DAT 路线能否写自编代码 | 同上 `:41` |
| O-4 | **签名 oracle 的真实反应**（已签名 vs 改版本 vs 未签名） | 被 O-1 阻塞 | 同上 `:42` |
| O-5 | **`0x9103`（PTP 未文档化操作码）具体是什么？** | 唯一新的 PTP 攻击面线索（回 `SessionNotOpen` 而非 NAK = 已实现） | 同上 `:43`；`S5_AES…:480` |
| O-6 | **CVE-2019-5096（GoAhead multipart UAF → RCE, CVSS 9.8）** | **唯一剩余公开 RCE，未测**；需堆控（heap control），工程量大，**极可能直接 brick 相机** | `02_研究总报告_20261011/05-…:30,38-39` |
| O-7 | **S5 是否有自己的 OSPO 页**（即松下是否发布了 S5 的内核源码） | 本包未能确认（`ospo.panasonic.com` 解析到非公网地址）；需人工用浏览器查 `https://ospo.panasonic.com/oss/dsc/` 索引页 | `14_…/08_…:252` |
| O-8 | **S5 的 U-Boot console 是否开启** | **S5 上不可判定**（离线 0 命中；OSPO 无 u-boot 源码）；只能拆机接 UART 读 bootlog | `14_…/08_…:150-153` |
| O-9 | **S5 的内核里是否有 S1R2 同款 `f_fs.c` OOB** | 待审计；但不能用 DC-FZ1K2 那棵树下结论（O-7） | `01_研究报告/06_S1R2移交…/00_S5结合点与AES路径总结.md:37-40`；`14_…/08_…:238-253` |
| O-10 | **CBC 还是 CTR？** | **本数据上不可区分**；需密钥、或同 (key, IV) 下第二份明文被改过的密文、或运行时 DDR 明文 | `14_…/06_密码学重跑/结论.md:191-193,363,423` |
| O-11 | **「固定密钥」是否成立** | **未被证实**：48 分区里"明文同 + IV 同"只有 7 个且全是 type=2（无加密）；type=3 中该对照 = **0 个** ⇒ 跨版本数据对"密钥是否跨版本相同"**零检验力** | `14_…/06_密码学重跑/结论.md:229-238,364` |
| O-12 | **`videoquality` 保留与槽 1 挂载状态的机制** | 仅 1 组对照（T1 vs T2），**且两次"写入"为空操作** ⇒ ◐ 待重复（≥3×3 交叉） | `01_研究报告/31_…:169-177`；`14_…/00_审计总报告.md:513` |
| O-13 | **槽形态 `06×13` vs `06 05×12` 的真正因果** | 反例取自协议修复前的无效跑 ⇒ **因果未确立**；需 ≥5×5、同一已修好的分块协议 | `14_…/00_审计总报告.md:589`（方向 19） |
| O-14 | **`getinfo camsetting` 是否真为 RAM 副本** | 现有"独立验证"是循环论证 ⇒ ◐ 未证；需比较"改值→不断电"与"改值→立即断电"两条支路 | `14_…/00_审计总报告.md:183-192,587`（S4/方向 17） |
| O-15 | **另外三态 `curmenu` 快照**（PAL+mov / NTSC+mp4 / PAL+mp4） | 需 `setsetting` 改制式或容器（写操作）；**改制式在松下机身上通常要求格式化存储卡** | `14_…/05_…/README.md:45`；`14_…/08_…:190` |
| O-16 | **长名崩溃的严格阈值** | 只知落在 58–86 KB；建议固定文件数 360、变名字长度 12/48/96/144/192/240 | `01_研究报告/24_…:93-104`；`14_…/00_审计总报告.md:590` |
| O-17 | **蓝牙：`err_user_refused` 是否需 BLE 绑定（bonding）** | 领先假设，**0 次验证**（工具从未运行）；可能只能由 Windows/WinRT 补齐 | `01_研究报告/20_…:191-205`；`14_…/00_审计总报告.md:518` |
| O-18 | **WPA2 机型上 BLE 是否返回真实 Wi-Fi 密码** | **0 次实测**（本机密码为空）⇒ 纯外推 | `01_研究报告/19_…:96-98`；`14_…/00_审计总报告.md:519` |
| O-19 | **热点专属面 `60606` / `50001` 的完整协议** | `50001` 在热点模式下"未识别"（后由监看工具确认是图片下载端口）；`60606` 控制面被门控 | `01_研究报告/18_…:87-95`；`12_S5无线监看_v1.0_20261014/README.md:320-321` |
| O-20 | **DLNA Browse 的 ObjectID 根** | `701 No such object` ⇒ LumixLink 内容树根**不是标准 UPnP 的 `"0"`**；另有 **DMS 开关**线索（是否需手动启动） | `14_…/10_仓库补丁/定因与交接_20261014.md:294-321` |
| O-21 | **`mp4ed` 与普通 MP4 的画质/宽容度实际差异** | 未做 A/B 实拍 | `01_研究报告/09_…:106` |
| O-22 | **S5 的 `0x16e`（S1H 的 MP4ed 质量项）是否被使用** | 改质量动的是 `0x122`；字段家族映射 S5 与 S1H **存在差异，尚未厘清** | `01_研究报告/09_…:107-108` |
| O-23 | **S1R2 团队如何在不触发 `0x00090013` 的前提下进入数据传送态** | 需向 S1R2 索取说明；否则维持"关闭"判定 | `01_研究报告/29_…:187-188` |
| O-24 | **ROM BACKUP 那次误点 `ADJFLAG→ALL F` 是否真改了标志** | 现有验证只是"重启后功能正常"的**主观判断**；唯一客观办法 = 再用 `DSC→SD` 导一次比对 sha256 | `14_…/00_审计总报告.md:575`（方向 10） |
| O-25 | **`!→LUMIX` 通道活性是否随相机 UI 状态变化** | 历史记录（"bulk OUT 写入成功"）与本次实测（全部超时）**矛盾**；建议优先复核 | `13_…/00_交接总结_全文.md:148-160,225-230` |
| O-26 | **`Lumix-Fast`（Android）字符串池中的 LUT 面是否对应可写 property tag** | 待验证（需 JRE + jadx/baksmali）；以 DC-S5 无 Real Time LUT 功能簇（`ph_sty11`）看，即使有该 tag **S5 大概率也不接受** | `14_…/08_…:285-303` |
| O-27 | **官方 Tether 在 `0x2382` 上的固件升级帧** | 未抓包；唯一能判定"末块失败是相机对所有人都拒绝，还是我们客户端的问题" | `14_…/00_审计总报告.md:573`（方向 8） |
| O-28 | **s5monitor 的单客户端会话隔离** | 已验证：必须在同一已授权进程内访问 DLNA，另起 `curl` 会被判 `err_unsuitable_app` | `14_…/10_仓库补丁/定因与交接_20261014.md:202-209` |
| O-29 | **相机存储类型（eMMC / NAND）** | **未拆机确认**；决定 SD.DAT 路线的风险等级（S1R2 是 NAND，GoPro 的 eMMC 路径在 NAND 上从未验证成功） | `01_研究报告/06_S1R2移交…/00_S5结合点…:51` |
| O-30 | **MC801 精确 die/核心数、Wi-Fi 模块型号、UART/JTAG 焊点位置、SD.DAT 触发键组合** | 全部**未验证**（调研笔记明确列为"未证实"） | `02-硬件攻击面/hardware_attack_surface_notes.md:200-209` |

---

## 6. 文档之间的矛盾（★ 汇编最重要的一节）

> 以下每条都是**两份或以上文档说不到一起**的地方，已标明双方与我的判定建议。

| # | 矛盾点 | A 方（含指针） | B 方（含指针） | 判定建议 |
|---|---|---|---|---|
| M-1 | **`0x220` 的 64B 是不是 ECDSA P-256 签名** | 当作**事实**使用：`02-硬件攻击面/verify_logic_notes.md:15-63`（"`0x220` 64 字节 ECDSA P-256……r,s ∈ [1,n−1] 合法标量——**支持** P-256 签名判定"）、`03-固件格式与启动链.md:55`、`01_研究报告/01_固件AES绕过…/00-总评估报告-中文.md:76` | **不可判定**：`14_…/07_签名与密钥恢复/结论.md:12-22`（穷举 90,144 组 0 收敛）；其**源头 `s1m2-research/docs/CORRECTIONS.md` 已自我撤回**该断言（`07_…:169-183`）；`siegfried82_notes.md:52` 自己只写"**推断**" | **以 B 为准**，A 方整体降级为「**候选假设**」 |
| M-2 | **「版本字段在签名覆盖内」** | 断言成立：`03-固件格式与启动链.md:48`（"两处都在签名覆盖域内"）、`verify_logic_notes.md:63-84`（"外层 0x24 被 ECDSA 覆盖（判定为强假设，未验签）"） | **不可判定**：`14_…/07_…:19,189-195`；且"ECDSA 覆盖外层头 0x0-0x200"这一**具体假设在穷举范围内已被排除**（`07_…:219-225`） | **以 B 为准**。「改版本号必然破坏 ECDSA」应改写为「**ECDSA 那一半没有正面证据**」 |
| M-3 | **AES 密钥提取** | 「**已证实（终局）**」：`00_项目总结/00_执行摘要_全文.md:29-32`、`01_成果总表.md:33`、`28_PTP…`引用、三份英文稿 | 「**证据不足、需进一步实验**」：`14_…/06_密码学重跑/结论.md:334`（#13 降级）、`14_…/00_审计总报告.md:510` | **以 B 为准**，统一写 **◐ 离线希望渺茫（非终局）** |
| M-4 | **持久化结论（10-14 受控复测）** | 「写入 ntsc+mov+0x9b 后三项均跨断电保留（n=2）」：`01_研究报告/31_…:151-161`、`README.md:82-85`、`00_执行摘要_全文.md:97-101` | 「**T1/T2 的写入是空操作**」：`14_…/00_审计总报告.md:69-98`（S1）+ 实机三份 sha256 完全相同（`14_…/08_…:47-63`、`14_…/05_…/README.md:47-58`） | **以 B 为准** ⇒ 该项降为 **◐ 待重做**；重做**必须**先断言 `payload != pre_write_readback` |
| M-5 | **`videoformat` 是否断电回落 mp4** | 「回落 mp4、仅 `ntsc_pal` 持久」：`07_…`早期版本、`02_项目时间线.md:41-45`（保留以存史） | 「**未获重现（n=2）**」：`01_研究报告/31_…:105-119`、各处更正框 | **以 B 为准**（且 B 本身仍受 M-4 削弱） |
| M-6 | **`getinfo camsetting` 是否为 RAM 副本** | 「是，且经**独立实验确认**」：`01_研究报告/31_…:50-51,92-99`、`README.md:31-32`、`25_…:354-364`、`30_…:412-413` | 「**循环论证**；其前提『setsetting 不写 flash』已被项目自己撤销」：`14_…/00_审计总报告.md:183-192`（S4）vs `01_研究报告/09_…:76-84`（"setsetting 会被相机自动存盘"） | **以 B 为准** ⇒ 在 E4 实验完成前，**该判据不应出现在任何结论链里** |
| M-7 | **「写全 13 槽」是否为推荐修法** | 「**已修订**：相机自身行为为仅写槽 0，全槽写与回调存在观测相关」：`README.md:65,146`、`30_…:428`、`25_…:398-408` | 「全槽写**重启后全部保持 mov**」（10-13 实测）：`07_…:55-61`；且 **GOLD 文件实测确实 `06×13` 且为 mov 持久态**：`14_…/00_审计总报告.md:151-159` | **两者都受污染**：反例取自协议修复前的无效跑 ⇒ **因果未确立**。汇编应写「**待验证假设**，不作规程」 |
| M-8 | **MOV 档位数：17 / 18 / 12 / 11** | 17：`01_研究报告/04_隐藏格式_持久化成果.md:125`、`01_研究报告/08_格式对照表…:38`（NTSC MOV）、`01_研究报告/07_…` | 18（NTSC）/ 12（PAL）：`01_研究报告/30_…:261-275`、`README.md:90`。**同一份 08 号报告内部亦冲突**（`:166` 写 PAL+mov=**12**、`:167` 又留 **11**）；`30_…:269` 把 17→18 归因于"是否含当前选中项"，但 `30_…:293-295` 自己的差集算术表明那个 +1 就是 curmenu 独有档 `mov_60p_200mbps_c4k_10bit` —— **两种解释互斥** | **以 18/12 为准**（有实机只读快照复现：`14_…/05_…/README.md:42`）；"差 1 的原因"**本身仍是未解的内部矛盾**，宜标注 |
| M-9 | **mp4 档位数：16 / 13 / 8** | 16：`04_隐藏格式_持久化成果.md:126`（"16 个 `mp4_*` 常规档"） | 13（`allmenu` 声明）/ 8（NTSC+mp4 实际启用）：`04_工具与脚本/campaign2/隐藏格式持久化_成果.md:128`（已加更正框） | **以 13/8 为准**；"16" 已由项目自己确认**数字有误** |
| M-10 | **热点 Wi-Fi 密码** | 「**密码为空**」：`01_研究报告/19_…:65-84`（两次独立采集解码全 0）、`17_…:13,62`（capability Privacy 位=0）、`18_…:59-65`（`accctrl` 末位 `open`） | 「**密码 `a707########`**」：`12_S5无线监看_v1.0_20261014/连热点时怎么测.md:9` | **★ 未解决的真矛盾**。M-10 的 B 方还说"MAC 前 10 位 = 70741470e2"，但项目文档中相机 MAC 是 `70:74:14:XX:XX:XX`（**只有 3 字节 OUI 可见**），**与 B 方声称的 5 字节无法对上** ⇒ 疑为**另一台设备**或记录错误。**汇编应并列两说并标注未解决** |
| M-11 | **相机热点是否为"开放网络"** | 开放/无密码：`17_…:62`、`18_…:59-65`、`README.md` 相关段落 | 有密码：`12_…/连热点时怎么测.md:9` | 同 M-10 |
| M-12 | **60606 的暴露范围** | 「**热点专属**」：`01_研究报告/18_…:87-95`（"家网侧只有 80"） | 「**station（家网）模式即暴露且无需认证**」：`14_…/08_实机与离线验证记录_20261014.md:69-92`（`GET http://<cam>:60606/Lumix/Server0/ddd → 200 OK, 1624 B`）、`14_…/05_…/README.md:60-63` | **以 B 为准**（更晚的实机实测）；A 方的"热点专属"应更正 |
| M-13 | **50001 端口是否存在** | 「家网侧不存在」：`01_研究报告/18_…:87-95` | 「**存在且未识别**」→ 后由监看工具确认是**图片/视频下载端口**：`12_S5无线监看_v1.0_20261014/README.md:320-321`；另 `14_…/08_…:92` 实测 station 模式下 `50001` **关闭** | **模式相关**，三方口径需按"station / SoftAP / 是否已在回放模式"分列 |
| M-14 | **DLNA Browse 403 的原因** | 「相机对 DLNA 控制做了**单独限制**」：`14_…/10_仓库补丁/定因与交接_20261014.md:112-113`、`14_…/08_…:323` | 「**就是 accctrl 未达 `ok`**」：同一文件 `:279-292`（A/B 对照：`ok` → **HTTP 500 + SOAP Fault 701**；受限 → **403**）⇒ 作者自述"应更正" | **以 B 为准**（同一文件内的后出更正） |
| M-15 | **音量：`videoquality` 槽数 13 vs 16** | **13 槽**：`04_工具与脚本/campaign2/out/S5_format_slots_analysis.md:18-23`（明确更正"`len=0x20=32` 是整条记录：6B 头 + 26B 载荷 = 13×u16"） | **16 槽**：`S5_camsetting_fieldmap.md:52,58-59`（"32 B = 16×u16"、"slots 1..15 hold 0x00c0"） | **以 13 槽为准**（后者被前者逐字节更正） |
| M-16 | **`getinfo` 有效子类型数量：4 vs 5** | **4 个**（capability/allmenu/curmenu/camsetting）：`01_研究报告/03_…/docs/00_执行摘要.md:26`、`03_…/reference/OPENGATE_FINDINGS.md:47` | **5 个**（多了 **`lens`**）：`01_研究报告/16_App在线状态信息获取_20261013.md:33`；`03_思路总结_全文.md:98` 也写 5 个 | **以 5 个为准**（`lens` 是后期才发现，`16_…:45` 自述"此前审计未枚举到该类型"） |
| M-17 | **只开 80 端口 vs 多端口** | 「端口扫描只有 80/tcp，无 FTP/DLNA/RTSP」：`01_研究报告/16_…:78-88` | 「热点模式多开 `80 / 50001 / 60606`」：`01_研究报告/18_…:92`；station 模式 `60606` 也 200：`14_…/08_…:92` | **以 B 为准**（16 号的结论已被 18 号部分证伪，审计亦如此判定 `00_审计总报告.md:398`） |
| M-18 | **`persist.py` 的 `videoquality` 访问宽度** | 单字节 `blob[6986]`：`persist.py:163,331` | 2 字节 LE `blob[6986:6988]`：`persist_quality.py:72,131`、`container_switch.py:88` | **工具间不一致**（`14_…/00_审计总报告.md:388`）；建议按 §1.4 R-11 的 13 槽 u16 数组统一为 2 字节 LE |
| M-19 | **`s5_quality.py` docstring 的档数** | 「`curmenu` **126** 条 mov、`allmenu` **106** 条、实际可选 **17**」：`campaign2/s5_quality.py:30-32` | 「`allmenu` videoquality 去重 **44**（mov 31 + mp4 13）、mov `enable=yes` **18**」：`01_研究报告/30_…:256`、`14_…/05_…/README.md:38-41` | **以 B 为准**；`s5_quality.py` docstring 是遗留旧数字，**建议更正**（注意：该脚本的**逻辑**是对的，只是注释数字错） |
| M-20 | **S1R2 的平台标识** | `MC8244`：`01_研究报告/06_S1R2移交_20261012/S1R2两项成果_移交S5同事.md:3`、`01_研究报告/29_…:4`（标题"《LUMIX S1R2（MC8244）固件加密体系分析报告》"） | `MC8243` / `SC2006A`：`02-硬件攻击面/siegfried82_notes.md:10-11`、`williamwu1234_notes.md:21-23`、`01_研究报告/06_…/S1R2_已排除路线与风险备忘.md:71` | **未解决**：两份移交件自相矛盾（`MC8244` vs `SC2006A/MC8243`）。汇编应并列并标注"**型号标识未统一**" |
| M-21 | **`s5_exfat_test.sh` 是否有"GO/NO-GO 拦截"** | 「内建 GO/NO-GO 拦截」：`04_工具与脚本/TOOLS.md:65` | 「`l1/l2` **写前无任何确认**；GO/NO-GO 是写完**之后**的机器判读」：`14_…/00_审计总报告.md:384` | **以 B 为准** |
| M-22 | **`TOOLS.md` 描述的目录名是否存在** | `exfat/`、`cam_cgi/`、`ble/`、`usb_ptp/`：`04_工具与脚本/TOOLS.md:9,69`、`TOOLS_工具箱总览.md:8` | 实际目录为 `campaign2/`、`ble_win/`、`ptp/`（`ls 04_工具与脚本/`） | **以 B 为准**（A 方所有示例路径不可用） |
| M-23 | **「S5 内核越界写」的撤回 vs 撤回逻辑本身** | 「越界索引处**存在** NULL 检查、**会提前返回**」（标 ✅ 成立）：`01_研究报告/23_…:17`、`00_项目总结/04_…:30` | 「**该撤回逻辑本身也不成立**：`vol_amap = kmalloc_array` 不清零，越界槽内容取决于堆复用历史，该前提**从未被测量**」⇒ **两者均未证实**：`14_…/00_审计总报告.md:277-285`（A7） | **以 B 为准**；正确表述：**「越界写」与「NULL 提前返回」两者均未证实** |
| M-24 | **`22_` 号报告的越界阈值表 vs `23_` 号实测** | 「索引 **120–127 必崩**（NULL 解引用）」：`01_研究报告/22_…:93-97` | 实测索引 120 **只报错不崩**：`01_研究报告/23_…:28` | **直接冲突，而 22 号未改**（`14_…/00_审计总报告.md:285`） |
| M-25 | **`22_` 号报告的"指纹一致 ✅"可否从归档复核** | 声称一对是 `baseline 0x2668BB77 / allocated 190 / 18:02:00` 与 `after 0x2668BB77 / 112 / 18:02:43`：`01_研究报告/22_…:43-47` | 归档中**不存在 allocated 190 的基线**（三份 meta 指纹互不相同）：`14_…/00_审计总报告.md:287-299`（A8） | **以 B 为准**：22 号核心主张**无法从归档复核** |
| M-26 | **服务模式的 USP/PID 与退出键** | 「退出：按住 `AF ON` + `方向右键`」：`01_研究报告/13_…:223`、`13_…/00_交接总结_全文.md:241` | 「**必须先拔掉卡槽 1（FAT32）那张卡，否则退不出工程模式**」：`01_研究报告/13_…:226-230` | **并列**：后者是"隐藏前提"补录（A 方未提）。**操作时两条都要满足** |
| M-27 | **「四个成果包已去重并库、包内文件已移除」** | 明确声明已移除：`README.md:74`、`REPO_CONTENTS.md:20`、三份包 README | **实测残留 534 个文件**（10_/11_ 的 341 个报告副本**受 git 跟踪**，会随公开仓库发布）：`14_…/00_审计总报告.md:305-322`（B1） | **以 B 为准**（"重复"判断准确，"已移除"是假的） |
| M-28 | **仓库规模数字** | 864 跟踪文件 / 41.5 MB / 583 唯一内容：`README.md:197`、`REPO_CONTENTS.md:7` | 实测 **1,390 文件 / 67.2 MB**：`14_…/00_审计总报告.md:345-352`（B4） | **以 B 为准**；"2,188"无任何可复核依据 |
| M-29 | **`07_参考仓库/` 目录地图** | 只列 `s1m2-research/`（第三方）：`README.md:73`、`REPO_CONTENTS.md:78` | 实际还有 **`s5_oss_kernel/`（771 MB / 4.8 万文件）** | **以 B 为准**；且该树实为 **DC-FZ1K2** 的内核（non-S5），见 M-30 |
| M-30 | **那棵 771 MB OSS 内核树是谁的** | 「OSPO publishes `linux-3.18.18` **for this model**」（指 DC-S5）：`S5_RE_Project_Summary_EN.md:15` | 同一份英文稿 `:92` 的下载 URL = **`DC-FZ1K2`**；`REPO_CONTENTS.md:101` 如实写 `DC-FZ1K2` 页；OSPO 站点上 `DC-FZ1K2` 有**独立页面** ⇒ **同文自相矛盾** | **以"是 DC-FZ1K2"为准**；「OSS mismatch」论点应从对外材料撤下（`14_…/08_…:238-253`） |
| M-31 | **MANIFEST 校验** | 声明为全量清单 | 实测 **77,504 OK / 5 FAILED**（全部集中在 `12_` 目录，清单生成后该 5 文件又被改写）；集合层面零差异 | 需**重新生成清单**（`14_…/00_审计总报告.md:335-343`，B3） |
| M-32 | **`persist.py` 的 no-op 断言** | `:334` 有 `assert`，但**只校验字段等于目标值，不校验与当前状态不同** | 10-14 复测与 5.9K 实验**都踩了同一个坑** | 建议增加铁律③（`14_…/00_审计总报告.md:630-639`） |
| M-33 | **偏移模型：文档 vs 脚本** | **文档写对**：`29_…`勘误 E1、`14_…/06_密码学重跑/结论.md:31-41`（`DATA_BASE = 0x200`） | **7 个脚本写错**（仍用 `raw[doff:]`）：`keyhunt.py:16,38`、`keyhunt2.py:17-19`、`ks_extract.py:13-15`、`exp_cipher.py:27-28,42`、`verify_sha.py:27`、`xver_fixed.py:23`、`verify512.py:10`、`rawtest.py:38`、`xver2.py:44` | **没有任何机制能发现这种分裂** ⇒ 建议登记 `upd_table.py` 为唯一真源 + 铁律④（`14_…/00_审计总报告.md:641-642`） |
| M-34 | **`ipu_data` 明文是否"≈全零、仅 508 字节非零"** | 「≈全零、**仅 508 字节非零**」：`S5_AES…:127` | 「**纯全零**；那 508 字节是错位读出来的产物」：`14_…/06_密码学重跑/结论.md:126-127,324`（并已**逐字节复现**恰好 508） | **以 B 为准** |
| M-35 | **「256KB 真实 keystream」的命名** | 多处称"真实 keystream（熵 7.999）"：`S5_AES…:12,77,562` | 「**术语错误**：只有 CTR/流式下 `ct⊕pt` 才等于 keystream，而模式**未判定**；且手上那份是**平移 512B** 的版本（99.80% 字节值正确、位置错）」：`14_…/06_密码学重跑/结论.md:143-146,325` | **以 B 为准**（数值维持、**命名推翻**） |
| M-36 | **`05_源码/usb-scsi/` 是不是 S5 的** | `01_研究报告/01_固件AES绕过…` 的目录说明把它列为"S5 调研"的一部分 | `05_源码/usb-scsi/README.md:3` 明确写**来自松下 S1R II（linux-4.19.124 arm64）**，而 S5 是 MC801 32 位 | **以 B 为准**：**不是 S5 的**，只作攻击面参考（`14_…/00_审计总报告.md:405`） |
| M-37 | **`s5_exfat_test.sh` 的"内建自动卸载/自动识别"** | 声称内建：`04_工具与脚本/TOOLS.md:64-65` | 实测"不校验命令行传入的设备是否为目标卡"、守卫只在 `verdict`、`BACKUP` 每轮被清空 | **部分失真**（`14_…/00_审计总报告.md:269-275`） |
| M-38 | **`11_/README.md` 内部自相矛盾** | 同一句写"**NTSC** + MOV ✅ 已完成并交付（**PAL `GK` 机型**上实现）" | — | 同句自相矛盾（`14_…/00_审计总报告.md:407`） |
| M-39 | **`30_` 号报告的行号引用失效** | 引用 `campaign2/隐藏格式持久化_成果.md` 的"第 **120-121/131/133-138** 行" | 实际内容在 **125-126/157/159-164** 行 | 引用**已被改写过的旧版本**（`14_…/00_审计总报告.md:408`） |
| M-40 | **`01_研究报告/04_隐藏格式_持久化成果.md` 与 `04_工具与脚本/campaign2/隐藏格式持久化_成果.md`** | 文件名不同 | **内容逐字节相同**（易被当成两份独立证据） | 汇编时只引一份（`14_…/00_审计总报告.md:409`） |
| M-41 | **`P1022641.MP4`（213 MB）重复两份** | `README.md:179-186` 的"以下重复内容已删除，仅保留一份"逐项清单里**没有这一项** | 实测本地工作树**存在两份**（约 426 MB），是全包最大重复文件 | 公平说明：`REPO_CONTENTS.md:79` 的"已排除"是对 **Git 仓库**说的，属实；问题是**本地去重清单不完整**（`14_…/00_审计总报告.md:410`） |

---

## 7. 本块最有价值的 5 条 + 最容易被重复劳动的 3 件事

### ★ 本块最有价值的 5 条

1. **AES 的四条硬性结构事实（且"终局否定"必须降级）**
   IV 逐版本全变且不可派生（`S5_AES…:89-97`）· 同偏移密文相等率 = 随机基线（`06_密码学重跑/结论.md:223`）· 同明文不同 IV 的密文 XOR 熵 7.999（非固定流，`06_密码学重跑/结论.md:186`）· 全库**唯一**已知明文对 = `ipu_data` 全零 262144B（`08_实机与离线验证记录:155-174`）。
   **但同时**：旧两次"密钥搜索 0 命中"因 `off-by-0x200` **对假设零检验力**（阳性对照 12/12 假阴性，`06_密码学重跑/结论.md:305-314`），`0x220` 是 ECDSA **不可判定**（`07_签名与密钥恢复/结论.md:12-22`）。
   ⇒ 结论只能是 **「密钥不在固件文件内」+「官方单一 .bin ⇒ 主密钥按机型固定」**，**不是**"已证实/终局"。

2. **`videoformat` 单一容器门 + `allmenu`/`curmenu` 的正确用法**
   可写档的**权威判据 = 实时 `curmenu` 的 `enable="yes"` 集合**（NTSC+mov **18** / PAL+mov **12** / NTSC+mp4 **8+2**），且 `enable="yes"` 语义是**"可选"不是"当前"**（`14_…/08_…:96-108`）。
   本机天花板 = **200Mbps 4K 10bit**（`mov_60p_200mbps_4k_10bit` / PAL `mov_50p_200mbps_4k_10bit`），菜单可用。
   **严禁用 `grep` 跨 `allmenu`/`curmenu` 做朴素差集**（那正是"curmenu 独有 95 条"伪结论的根因，`01_研究报告/30_…:239-256`）。

3. **CAMSET 分块写入协议 + 校验和公式（本项目唯一真正打通的"写"能力）**
   `startsenddata` 必须回 `method=separate`（单次 65KB POST **永不落地**）→ `61192 + 4341` 两块 + `requestsenddata` + `endsenddata`；
   校验和 `byte[65532] = (256 − Σ(byte[0..65531])) mod 256`，**可伪造**，且与 S1R2 双证同源。
   指针：`01_研究报告/07_…:39-50`；`02_研究总报告_20261011/08-…:28-31`；`06_S1R2移交…/00_S5结合点…:18`

4. **exFAT / 长文件名两条"带干净对照组"的定因（本项目方法学的正面样板）**
   ① 内核**对簇号不做归属校验**（位图实机比对）；② **360 个 240 字符长文件名 → 开机反复重启**（四组对照矩阵排除数量/体量/分配大小，阈值 58–86 KB）。
   指针：`01_研究报告/22_…:11-20`；`01_研究报告/24_…:23-51`

5. **服务模式 / ROM BACKUP 的完整可执行知识（原本"高风险低收益"，因一个发现变成"低风险可执行"）**
   进 `回放+AF ON+右键`；**ROM BACKUP 门控 = 卡槽 1 + FAT32**（**不是**"未解除初始设置"，更**不需要**碰不可逆的地区后缀）；导出 `S5A/S5F/S5U.TXT` = EEPROM 三区各 128KB。
   **红线：只动 `DSC→SD`；绝不按 `DISP.`**（会解 `[Strict]`，地区后缀一次性锁死）。
   指针：`01_研究报告/13_…:182-191,247-248`；`01_研究报告/27_…:11-13,23-27,182-192`

### ★ 最容易被重复劳动的 3 件事

1. **再跑一遍"离线找 AES 密钥"**（含所有变体：换候选、换模式、换派生、换已知明文、跨版本差分、Nikon 手法的移植）
   —— 已穷尽且多数**已被证伪或证据无效**；`2^128` 是硬墙，且**全库只有一对已知明文**（`ipu_data`，全零），"多找已知明文"的路已明确关闭（`14_…/08_…:174`）。
   **要做的是**：用**正确偏移**重跑那 7 个脚本（`06_密码学重跑/结论.md:418-420`），把"0 命中"第一次变成**有限定意义的负向证据**。

2. **再上传一次 90MB 固件去试签名 / 末块**
   —— `oracle/README.md:73-90` 已明确"**停止上传预言机这条线**"（阶段 1 的前提已失效、无逐字节反馈、无可用时差）；`CONTROL` 组已用**未改动的真 V29** 证明**末块失败与内容无关**；每次尝试都可能再触发 ~31s 定址 / 卡死。
   **要做的是**：先做 `14_…/00_审计总报告.md:573`（方向 8）——**抓官方 Tether 的包做对照**，判定"是相机对所有人都拒绝，还是我们客户端的问题"。

3. **再次尝试 5.9K / 6K / 400Mbps / `mov_*_a6k_*`**
   —— 5.9K 已由**两种独立证据同向**判死（实拍文件头 = C4K 60p；API 层四变量穷尽全拒）；6K 视频 `err_param`；400Mbps 未生效；
   **`a6k` 是危险项**（返回 `ok` 却静默把容器改成 avchd）。
   更要紧的是：**`out/` 里那个 `quality_payload_mov_30p_200mbps_5_9k_10bit_*.bin` 文件的"5.9K 写入"是空操作**（与备份逐字节相同），**不要因为看到这个文件名就以为"已经试过了"**（`01_研究报告/30_…:188-211`）。
   **另一个同类陷阱**：`out/` 里的 `blob_GOLD_mov_persisted_*.bin`（`06×13`）**是真实持久态**，而"全槽写会回退"的反例来自**协议修复前的无效跑** —— 不要凭前者推翻后者、也不要凭后者立规程（`14_…/00_审计总报告.md:149-180`）。

---

### 附：三条应在汇编文档中固化的方法学铁律（含本项目已有两条）

> ① **没有对照组的结论不要写进报告**（`REPO_CONTENTS.md:67`）
> ② **「相机报写入错误」不能当作「内存写已执行」的判据** —— NULL 提前返回表现完全一样；**S1R2 报告也用了该判据，后人不应照抄**（`REPO_CONTENTS.md:69-70`）
> ③ **任何"写入类"实验，上传前必须断言 `payload != pre_write_readback`；若相等立即中止并如实记为"无效试验"**（`14_…/00_审计总报告.md:632-639`）
> ④ **任何依赖结构化二进制偏移的结论，必须附一个"偏移判决实验"**（用已知明文/已知校验和验证同一偏移模型在**多个样本**上命中），并在工具清单里登记**单一真源**（`14_…/00_审计总报告.md:641-642`）

（本文件完 · 素材来源均为 `16_S5_核心总包_20261015/` 内文件；未连接设备、未执行脚本、未修改包内任何文件）
