# 相机只读快照 · 2026-10-14

**相机**：Panasonic DC-S5（MC801），`192.168.1.131`，MAC `70:74:14:XX:XX:XX`，固件 **VD4.30**
**方式**：**全部只读**（`getinfo` / `getsetting` / `GET`）。未执行任何 `setsetting`、未写入相机或存储卡、未做 fuzz/DoS。
**并发控制**：单线程串行，每次请求间隔 0.6–0.8 s（项目记载并发请求会触发 `invalid login` / 需重启）。

## 抓取时的相机状态
| 项 | 值 |
|---|---|
| cammode | `play` |
| 电池 | `4/5` |
| 槽1 | `sd_memory=set`（已挂载），`current_sd=sd1` |
| 槽2 | `sd2_memory=unset` |
| 温度 | `low` |
| ntsc_pal | `ntsc` |
| videoformat | **`mov`** |
| videoquality | **`mov_60p_200mbps_4k_10bit`**（= blob `6986=0x9b`） |

## 文件
| 文件 | 内容 |
|---|---|
| `getstate.xml` | 相机状态 |
| `getinfo_capability.xml` | 能力表（`comm_proto_ver=10.0`，`modelname=S5`） |
| `getinfo_curmenu.xml` | **当前菜单（NTSC+mov 态，18 档）** |
| `getinfo_allmenu.xml` | 全部菜单（740 item / 666 cmd_value / 44 档） |
| `getinfo_camsetting.bin` | **65533 字节设置 blob**（`sum%256=0`，`ck=0xd2`） |
| `getsetting_raw/*.xml` | 47 个可写域的当前值原始响应 |
| `live_getsetting.txt` | 同上，纯文本汇总 |
| `60606_devicedesc_station.xml` | UPnP 设备描述（**未认证可达**） |
| `cds_scpd.xml` | ContentDirectory 服务描述 |

## 本次快照解掉的两个审计缺口

### ① 缺口 B5：`NTSC+mov=18` 等数字"不可离线复现" → **已补齐并全部复现 ✅**

| 指标 | 项目文档 | 本次实测 |
|---|---|---|
| allmenu videoquality 去重 | 44（mov 31 + mp4 13） | **44（31+13）** ✅ |
| allmenu `cmd_value` 出现次数 | 666 | **666** ✅ |
| allmenu item 总数 | 740 | **740** ✅ |
| curmenu `enable=yes`（NTSC+mov） | 18 | **18** ✅ |
| 「启用但 allmenu 未声明」 | 1 个 | **`mov_60p_200mbps_c4k_10bit`** ✅ |

> ⚠️ **需注意 token 之别**：幽灵档是 **`c4k`** 变体（0x8b 家族），而当前激活档是 **`4k`** 变体（`0x9b`，**已在 allmenu 声明**）。二者是不同 token，讨论"菜单变灰"时必须区分。
> 仍然只能靠**写操作**（`setsetting` 改制式/容器）才能取到另外三态（PAL+mov / NTSC+mp4 / PAL+mp4）——本次未做。

### ② 缺口 S1：10-14「受控复测」空操作 → **实机独立确认 ✅**

相机**当前**的 live blob 与 T2 的"写入 payload"、"写入前备份"**三者 sha256 完全相同**：

```
2d8c0a767c8c230642b311c0951752ea23c7b4670c8ee6ab963a8527fe3c9ffe  getinfo_camsetting.bin          ← 实机当前
2d8c0a767c8c230642b311c0951752ea23c7b4670c8ee6ab963a8527fe3c9ffe  restore_payload_20261014_180310.bin
2d8c0a767c8c230642b311c0951752ea23c7b4670c8ee6ab963a8527fe3c9ffe  backup_pre_restore_20261014_180310.bin
```

⇒ T2 的"写入"没有改动任何字节；"三项跨断电保留"实为**"相机仍停在它本来就处于的状态"**。
且 31 号 §3.2 的另一项子主张（"T2 重启后读回与写入 payload 逐字节仅差 13 个字节"）也不成立——payload 与它自己的备份**零字节差异**。

## 本次新发现：60606 在 station 模式即暴露（项目认为"热点专属"）
`http://192.168.1.131:60606/Lumix/Server0/ddd` → **200，无需认证**，泄露：
`serialNumber=WJ1DA004124`、`friendlyName=S5-XXXXXX`、`UDN` 内嵌 Wi-Fi MAC、`X_FirmVersion=2.90`、`X_PTPPortNo=15740`、`X_AdditionalFunction=CPRemoteView`。
所有 SOAP 控制动作（`CDS_control` / `CMS_control`，含只读的 `GetProtocolInfo` / `GetSystemUpdateID`）**一律 403** ⇒ 边界是**信息泄露，不是文件访问**。


---

## 附：与库内归档的逐字节对账（2026-10-14 增补）

| 文件 | 归档副本 | 今日实机 | 判定 |
|---|---|---|---|
| `allmenu.xml` | `2cf69074d41a…`（`06_数据与证据/camera_settings/`、`01_研究报告/03_…/reference/`、`11_…/01_研究报告_全集/03_…/reference/` **四份全同**） | **`2cf69074d41a…`（307,714 B, model="S5"）** | ✅ **逐字节一致** ⇒ 菜单树稳定，归档 allmenu 证据有效 |
| `curmenu.xml` | `79af32bdbddc…`（47,162 B，3 份全同） | **`719c26aa6740…`（43,233 B）** | ❌ **不同态**：归档是 **PAL+mp4**（仅 5 个 mp4 + 1 个 mp4hevc `enable=yes`）；本次实机是 **NTSC+mov（18 档）** |

⇒ **审计缺口 B5 至此彻底闭合**：
- `allmenu` 侧**从来不是问题**——归档与实机逐字节相同；
- `curmenu` 侧此前**只归档了 PAL+mp4 一个态**，而 `README.md:90` 的 `NTSC+mov=18` 所需的那个态**从未入库**。**本次已补齐该关键态**（`getinfo_curmenu.xml`）。
- 仍缺三态（PAL+mov / NTSC+mp4 / PAL+mp4）：需 `setsetting` 改制式或容器，**属写操作，未做**。

### 附带发现：S1H 的 allmenu 同样零 LUT 条目
`06_数据与证据/hidden_format_evidence/s1h_activation/allmenu.xml`（`37d35296bd76…`，model=`S1H`，690 个 item id，photo style `func_type=sp_embeded_ph_sty9`）中 **LUT 相关 id = 0**。
S1H 是明确的视频机、具备 V-Log View Assist ⇒ **「LUT 查看助手」是机身功能，不进入 CGI 菜单树**。
⇒ 因此 **"allmenu 里没有 LUT" 不能推出 "机身没有该功能"**，这一条必须写进 LUT 报告以免误导。
