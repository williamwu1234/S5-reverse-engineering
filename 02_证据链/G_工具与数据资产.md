# G · 工具与数据资产（素材稿）

> **生成方式**：纯离线通读 `03_解包_APK/`（13 md）、`04_工具与脚本/`（13 md + 全部脚本）、`05_源码/`（2 md）、
> `06_数据与证据/`（4 md + 全部二进制）、`07_参考仓库/`（README/说明类）、`08_`、`09_` 的 README。
> **纪律**：命令一律**原样抄录**自文档或脚本自身的 `Usage` / docstring；文档没写的命令一律标注来源。
> 凡本文写"未验证"，指**在本次通读的文档里找不到实测记录**，不代表它不能用。
>
> **路径约定**：`$REPO` = `/Users/<user>/Documents/ChatGPT/S5_逆向_项目总包_20261012`
>
> **状态图例**
> | 标记 | 含义 |
> |---|---|
> | ✅ | 文档中明确记录了**实机实测成功**（真机/真卡/真相机） |
> | ◐ | 有强证据但未完全闭合，或仅离线/离线复现成立 |
> | ⚠️ | 脚本存在、文档有用法，但**未见实测记录**（可跑，未验证） |
> | ❌ | 文档明确记录**已失败/已排除/已撤回** |

---

## 0. 先说三条"别重复劳动"的硬事实

1. **大量工具不在你猜的目录里。** 文档（`TOOLS.md`、`TOOLS_工具箱总览.md`、`00_调用前必查…`）反复写
   `04_工具与脚本/cam_cgi/xxx.py` 和 `04_工具与脚本/exfat/xxx.py` —— **这两个目录在 `04_工具与脚本/` 下都不存在**。
   真实位置是 **`04_工具与脚本/campaign2/`**（全部 cam.cgi 工具 + 全部 exfat 工具都堆在这一个目录里）。
   另有一份 cam_cgi 完整副本在 `11_DC-S5成果包_20261013/02_工具链/cam_cgi/`。详见 §7 矛盾 #1/#2。
2. **exFAT 与 USB PTP 的命令有 `sudo` / 人工前置条件**：exFAT 工具受 macOS **Unix 权限 + TCC 双重保护**，
   自动化进程过不去，**必须由人在终端 `sudo` 执行**（`00_项目总结/05_环境与依赖.md` §9）。
3. **`cam.cgi` 的所有请求必须带 `User-Agent: LUMIX Sync`**，所有脚本里写死的相机 IP 常量是 `192.168.1.131`，
   换网络要改脚本头部的 `IP = "192.168.1.131"`。文档里的 `192.168.x.x` 是脱敏占位。

---

## 1. 工具总清单（重点，尽量最全）

### 1.1 Wi-Fi 无线监看 · 最成熟、已发行（`04_工具与脚本/s5_monitor/`）

| 工具 | 路径 | 用途 | 确切调用命令 | 状态 |
|---|---|---|---|---|
| `s5monitor.py` | `04_工具与脚本/s5_monitor/s5monitor.py` | **无线监看主程序**：MJPEG 取景流转发成 HTTP `multipart/x-mixed-replace`，触摸对焦/AE锁定/拍照/录像/变焦/LUT/相册；复刻官方 12 步逻辑 + SSDP alive | `cd "$REPO/04_工具与脚本/s5_monitor"`<br>`python3 s5monitor.py --host 192.168.54.1 --port 8080 --pacing-mode fixed --pacing-fps 18 --device-name "LUMIX Sync"`<br>浏览器开 `http://127.0.0.1:8080` | ✅ 实机（640×432@18–19.8fps、camctrl 自检 4/7） |
| `run.sh` | `04_工具与脚本/s5_monitor/run.sh` | 一键启动（默认 fixed/18fps，自动查本机 IP、ping 相机） | `./run.sh 192.168.1.131 8080 fixed 18` | ✅ 文档主推 |
| `s5probe.py` | `04_工具与脚本/s5_monitor/s5probe.py` | 设置枚举对照探针：同时测**控制面**（camctrl X/12）+**取景面**（到达fps/丢弃/抖动/最大间隔/>120ms停顿） | `python3 s5probe.py --label "基线（未改任何设置）"`<br>`python3 s5probe.py --report` | ✅ 计划已定，实测数据在 README |
| `s5gate_test.sh` | `04_工具与脚本/s5_monitor/s5gate_test.sh` | 判定「取景流是否独占相机 ⇒ camctrl 全 err_busy」的 A/B 对照 | `./s5gate_test.sh`（默认测 `127.0.0.1:8080`） | ◐ 脚本 `CGI` 写死 `192.168.1.131` |
| `设置枚举测试计划.md` | `04_工具与脚本/s5_monitor/设置枚举测试计划.md` | A/B/C 三组设置枚举计划表（改哪项、判据是什么） | — | ✅ 计划 |
| `www/index.html` | `04_工具与脚本/s5_monitor/www/index.html` | 前端（四段式控制栏、对焦框、LUT 滑杆） | 由 `s5monitor.py` 提供 | ✅ |

### 1.2 `cam.cgi` HTTP 控制 · 日常主力（全部在 `04_工具与脚本/campaign2/`）

| 工具 | 用途 | 确切调用命令 | 状态 |
|---|---|---|---|
| **`persist.py`** | **核心**：分块 `separate` 协议读写 **65,533 B** camsetting 配置块；校验和修复；四种模式 `verify`/`flashwrite`/`flashwrite-file`/`restore` | `python3 persist.py verify`（只读安全）<br>`python3 persist.py flashwrite --confirm`<br>`python3 persist.py flashwrite-file <blob.bin> --confirm`<br>`python3 persist.py restore --confirm`<br>（dispatch 见脚本 `main()`：`verify/flashwrite/flashwrite-file <blob>|restore`，写操作都要 `--confirm`） | ✅ 实机（三字段跨断电持久，n=2） |
| `persist_quality.py` | 写【录制质量】并落 flash：校验名字在 `allmenu` → `setsetting` → 回读确认 → 备份 → 分块写 | `python3 persist_quality.py mov_60p_200mbps_4k_10bit`（dry，1–3 步）<br>`python3 persist_quality.py mov_60p_200mbps_4k_10bit --confirm`（也推 flash） | ✅ 实机 |
| `container_switch.py` | 切换容器 `videoformat`：`status`/`mp4`/`mov`/`mp4ed`/`avchd`/`mp4hevc`，可 `--persist` | `python3 container_switch.py mov`<br>`python3 container_switch.py mp4ed`（RAM，菜单会变灰）<br>`python3 container_switch.py mov --persist`<br>`python3 container_switch.py status` | ✅ 实机 |
| `hidden_features.py` | 隐藏功能开关与审计：`status`/`vlog`/`6kphoto`/`lpcm`/`avchd`/`restore`；**含"DOES NOT WORK"清单** | `python3 hidden_features.py status`<br>`python3 hidden_features.py vlog`<br>`python3 hidden_features.py 6kphoto`<br>`python3 hidden_features.py lpcm`<br>`python3 hidden_features.py avchd`<br>`python3 hidden_features.py restore` | ✅ 实机（且注明"设置会被相机自动持久化到 flash"） |
| `s5_quality.py` | **健壮的**录制格式/质量控制台：`status`/`list`/`set`/`safe`；处理 `err_reject`/`ok 假成功`/`a6k` 改容器 | `python3 s5_quality.py status`<br>`python3 s5_quality.py list [--grep 200mbps] [--all]`<br>`python3 s5_quality.py set mov_60p_200mbps_4k_10bit`<br>`python3 s5_quality.py set mov_60p_200mbps_c4k_10bit --allow-grey`<br>`python3 s5_quality.py safe` | ✅ 实机（只写 RAM，不写 flash） |
| `safe_handshake.py` | **安全握手**：`accctrl req_acc` → `req_acc_can` 清理，避免留下"陈旧待批复槽" | `python3 safe_handshake.py --ip <IP> [--port 80] [--name "LUMIX Sync"] [--polls 6] [--poll-delay 2.5] [--no-cleanup]` | ✅ 文档标注为已跑通路径 |
| `state_check.py` | 状态核对 | `python3 state_check.py --ip <IP> [--port 80] [--timeout 6.0]` | ⚠️ |
| `probe_format_slots.py` | **零风险** RAM 探测 `0x005e` 槽数组索引规则（遍历拍摄模式看哪个槽被点亮） | `python3 probe_format_slots.py`（只打印计划）<br>`python3 probe_format_slots.py --run`（执行，仍不写 flash） | ✅ 零风险路径已跑 |
| `experiment_mov_shadow.py` | 影子槽实验：写偏移 `3062..3074` 全 `0x06`，重算校验和后 flash 写 | `python3 experiment_mov_shadow.py --dry-run`（纯离线）<br>`python3 experiment_mov_shadow.py --confirm`（危险） | ❌ **结论已修订**：全槽写 n=1 重启后回退；相机自身只写槽 0（n=2 保留）。见 §7 矛盾 #8 |
| `api_enum.py` / `api_enum2.py` | `mode`/`getinfo` 子类型枚举 | `python3 api_enum.py` / `python3 api_enum2.py` | ⚠️ |
| `enum_vq2.py` / `enum_videoquality.py` / `enum_video_use.py` | 质量 token / 录制质量档枚举 | `python3 enum_vq2.py`；`python3 enum_videoquality.py [--confirm]`；`python3 enum_video_use.py` | ✅（`TOOLS_工具箱总览` 列为已跑） |
| `menu_map.py` / `menu_recon_live.py` | `allmenu`/`curmenu` 菜单结构映射 | `python3 menu_map.py` / `python3 menu_recon_live.py` | ⚠️ |
| `read_values.py` | 状态读取 | `python3 read_values.py` | ⚠️ |
| `isolate_videoquality.py` | 单变量隔离实验 | `python3 isolate_videoquality.py` | ⚠️ |
| `enable_one.py` | 单个 `setsetting` 域写入 | `python3 enable_one.py <type> <value> [value2]` | ⚠️ |
| `batch_enable.py` | 批量开关某个域 | `python3 batch_enable.py <domain>`（默认 `photo`） | ⚠️ |
| `blindwrite.py` | 盲写探测（带握手） | 脚本头部有 `Usage:`（`python3 blindwrite.py …`） | ⚠️ |
| `gate_probe.py` / `gate_test.py` / `session_gate_test.py` | 访问门控探测与对照 | `python3 gate_probe.py [<IP>]`<br>`python3 gate_test.py`<br>`python3 session_gate_test.py --phase {hevc,ed,all}` | ✅（F 阶段实测记录） |
| `unlock_video.py` / `unlock_video2.py` | 解锁视频档 | `python3 unlock_video.py`<br>`python3 unlock_video2.py [b1\|b2\|all]` | ⚠️ |
| `portscan.py` | 端口扫描 | `python3 portscan.py` | ✅ **结果：只开 80/tcp 与 60606** |
| `http_fingerprint.py` / `http_primitives.py` | HTTP 指纹与协议原语 | `python3 http_fingerprint.py` / `python3 http_primitives.py` | ✅ 指纹结论见 §3 |
| `opengate_recon.py` | 片门全开侦察 | `python3 opengate_recon.py` | ✅（配 `06_数据与证据/camera_settings/OPENGATE_FINDINGS.md`） |
| `crk.py` / `crk2.py` | 崩溃/挂死触发过程脚本 | `python3 crk.py` / `python3 crk2.py` | ❌ 状态机 DoS，非内存破坏 |
| `startsend_test.py` | `startsenddata` 单发测试 | `python3 startsend_test.py [<IP>] [<size>]`（默认 size=90238464） | ✅ 定位分块协议 |
| `find_checksum.py` | 校验和算法反推 | `python3 find_checksum.py` | ✅ |
| `roundtrip_test.py` / `enc_handshake_test.py` | 往返/加密握手一致性 | `python3 roundtrip_test.py`；`python3 enc_handshake_test.py [<IP>]` | ⚠️ / ✅ |
| `read_values.py`·`recon.py`·`control.py`·`common.py`·`campaign.py` | 过程脚本与共享基础设施 | `campaign.py` 见 §1.4 | ◐ |

### 1.3 安全侧（DoS / 溢出 / RCE）— 大部分**已排除**

| 工具 | 用途 | 确切调用命令 | 状态 |
|---|---|---|---|
| `ptp_attack.py` | PTP length-DoS | `python3 ptp_attack.py`（脚本头部 `Usage:`） | ✅ **可复现挂死，拔插 USB 恢复，不砖机** |
| `usb_oob.py` | USB OOB 探测 | `python3 usb_oob.py` | ◐（同族结论：仅 DoS） |
| `crash_cam.py` / `crash_v3.py` / `crash_v3b.py` / `crash_v3c.py` | 崩溃触发实验 | `python3 crash_cam.py` 等 | ✅ 实测 ⇒ **状态机 DoS，非内存破坏** |
| `goahead_overflow.py` | GoAhead 溢出 fuzz | `python3 goahead_overflow.py` | ❌ **全失败** |
| `overflow_fuzz.py` | 溢出 fuzz 变体 | `python3 overflow_fuzz.py`（全变体）<br>`python3 overflow_fuzz.py H1 H3 T1`（指定变体） | ❌ |
| `mutation_test.py` | 变异测试 | `python3 mutation_test.py` | ❌ |
| `oob_read_probe.py` | 越界读探测 | `python3 oob_read_probe.py` | ◐ **未闭合** |
| `rce_ldpreload.py` / `rce_probe.py` / `rce_surface_probe.py` | RCE 路线 | `python3 rce_ldpreload.py`；`python3 rce_probe.py [<only…>]`；`python3 rce_surface_probe.py` | ❌ **全失败**（LD_PRELOAD / CVE-2017-17562） |
| `launch_daemon.py` | 服务/进程面探测 | `python3 launch_daemon.py [<log>]` | ❌ |
| `run_recon_when_up.py` | 等相机上线自动跑 recon | `python3 run_recon_when_up.py` | ⚠️ |

### 1.4 Wi-Fi 预言机 / 固件上传（`04_工具与脚本/campaign2/`）

| 工具 | 用途 | 确切调用命令 | 状态 |
|---|---|---|---|
| `campaign.py` | 第二波探测 A–G（安全，只读/可逆）+ H（崩溃，需 `--confirm`） | `python3 campaign.py --ip 192.168.1.131 --phase A`<br>`python3 campaign.py --ip 192.168.1.131 --phase A,B,C`<br>`python3 campaign.py --ip 192.168.1.131 --phase A-G`<br>`python3 campaign.py --ip 192.168.1.131 --phase H --confirm`<br>`python3 campaign.py --ip 192.168.1.131 --all` | ✅ A–G 已跑 |
| `upload.py` | **核心预言机** Phase I（版本+1，可恢复）/ Phase J（翻数据字节，高危） | `python3 upload.py --ip 192.168.1.131 --phase I --confirm`<br>`python3 upload.py --ip … --phase I --ver-field inner --confirm`<br>`python3 upload.py --ip … --phase J --data-flip 0x5600000 --confirm` | ❌ **Phase I 判读为死路**；J 不自动跑 |
| `wait_and_run.sh` | 等相机上线 → A–G → Phase I 一键 | `bash wait_and_run.sh`<br>`bash wait_and_run.sh --no-i` | ⚠️ |
| `common.py` | 共享网络/日志/健康守卫/`parse_camrply` | 被 import | ✅ 基础设施 |
| `control.py` | 门控 + 定速上传控制 | `--ip` / `--gate-version V3.00` / `--target-ms 150.0` / `--retries 6` / `--no-fast` / `--max-chunks 0` | ⚠️ |
| `finalfix.py` | 收尾修复流程 | `--ip` / `--gate-version` / `--fw` / `--wait-final 2.0` / `--settle 45.0` / `--pace-ms 0.0` | ⚠️ |
| `probe_final_chunk.py` / `probe_partial_final.py` | **最终 chunk 定址**排查（阻塞点 F5） | `python3 probe_final_chunk.py` / `python3 probe_partial_final.py` | ◐ **未打通**（~31s 定址超时/磨损） |
| `upload_diag.py` | 上传诊断 | `python3 upload_diag.py` | ⚠️ |
| `hidden_test.py` / `hidden_test_hlg.py` | 隐藏项测试（含 `hlg=8k`） | `python3 hidden_test.py` / `python3 hidden_test_hlg.py` | ◐ `hlg=8k` 写入 ok、回读仍 off（模式门控） |

### 1.5 exFAT 越界写（**同在 `04_工具与脚本/campaign2/`，不在 `exfat/`**）

| 工具 | 用途 | 确切调用命令 | 状态 |
|---|---|---|---|
| `exfat_patch.py` | exFAT 全功能解析与补丁工具（子命令见下） | `sudo python3 exfat_patch.py <子命令> /dev/diskNsM [参数...]` | ✅ 实机（真卡） |
| `exfat_spray.py` | 目录项堆喷：用**文件名长度**控制 `kmalloc` 档位 | `sudo python3 exfat_spray.py size <长度>`<br>`sudo python3 exfat_spray.py make <挂载点> <数量> <长度>`<br>`sudo python3 exfat_spray.py both <挂载点> <每档数量>`<br>`sudo python3 exfat_spray.py clean <挂载点>` | ✅ |
| `s5_exfat_test.sh` | 编排入口（自动卸载 + 按卷名/FS/容量自动识别设备 + 卡代次守卫 + GO/NO-GO 拦截） | `sudo bash s5_exfat_test.sh <子命令> /dev/diskNsM [参数...]` | ✅ |

**`s5_exfat_test.sh` 实际子命令**（脚本 `case` 分支实测枚举，**比 `TOOLS.md` 列的多**）：
`prep` · `l1` · `l2` · `setfat` · `go1` · `session` · `go1check` · `dumpbitmap` · `go2` · `hijack` ·
`checkalloc` · `mkdeleted` · `trimdir` · `mkentries` · `mkspray` · `verdict` · `info` · `entries` · `bitmap` · `chain` · `restore`

**`exfat_patch.py` 子命令**（`main()` 的 `mode ==` 分支实测枚举）：
`info` · `entries` · `setfat` · `go1` · `go2` · `hijack` · `checkalloc` · `mkdeleted` · `trimdir` ·
`mkentries` · `mkspray` · `verdict` · `go1check` · `dumpbitmap` · `bitmap` · `chain` · `restore`

**堆喷档位换算**（`bufsize = 8 + (num_ext+1) × 32`）：

| 文件名长度 | entries | bufsize | slab |
|---|---|---|---|
| 90 | 8 | 264 | kmalloc-512 |
| 150 | 12 | 392 | kmalloc-512 |
| 210 | 16 | 520 | kmalloc-1024 |
| 240 | 18 | 584 | kmalloc-1024 |
| 255 | 19 | 616 | kmalloc-1024 |

**最短复现入口**（`00_项目总结/04_定因与工具链成果_20261013.md` §六，原样）：

```bash
# 0) 拷贝工具到 /tmp（TCC 保护不到这里）
TOOLS=04_工具与脚本/campaign2
mkdir -p /tmp/s5exfat && cp "$TOOLS"/exfat_patch.py "$TOOLS"/exfat_spray.py "$TOOLS"/s5_exfat_test.sh /tmp/s5exfat/ && chmod +x /tmp/s5exfat/*
# 1) 相机格式化 SDXC（>32GB）→ 拍 1 张 → 【正常关机】→ 拔卡插到 Mac
# 2) 写前体检（必须 K = 0，否则停手）
sudo bash /tmp/s5exfat/s5_exfat_test.sh checkalloc /dev/disk8s1
# 3) 写 360 个 240 字符长名目录项（复现崩溃）
sudo bash /tmp/s5exfat/s5_exfat_test.sh mkentries /dev/disk8s1 360 240 0
# 4) 写后体检（K 必须仍为 0）
sudo bash /tmp/s5exfat/s5_exfat_test.sh checkalloc /dev/disk8s1
# 5) 【正常关机】后拔卡 → 插进相机开机 → 应反复重启
```

### 1.6 USB PTP / USB 服务通道（`04_工具与脚本/ptp/`）

| 工具 | 用途 | 确切调用命令 | 状态 |
|---|---|---|---|
| `s5_ptp_raw.c` / `s5_ptp_raw` | **自建原始 USB PTP 客户端**：IOUSBLib 直连 bulk 端点，绕过 macOS ImageCaptureCore | `clang -framework IOKit -framework CoreFoundation -o s5_ptp_raw s5_ptp_raw.c`<br>`./s5_ptp_raw --list`<br>`./s5_ptp_raw <outdir> [vid] [pid]`（默认 `0x04da 0x2370`） | ✅ **这是 macOS 上唯一跑通的 PTP dump 路径** |
| `s5_ptp_dump.m` / `s5_ptp_dump` | 原生 ImageCaptureCore 客户端；4 种 mode | `clang -framework Foundation -framework ImageCaptureCore -o s5_ptp_dump s5_ptp_dump.m`<br>`./s5_ptp_dump ./ptp_out`<br>`./s5_ptp_dump ./ptp_out S5`<br>`./s5_ptp_dump ./ptp_out S5 fwup`<br>`./s5_ptp_dump ./ptp_out_fuzz S5 fuzz`<br>`./s5_ptp_dump ./ptp_out_lp S5 lenprobe` | ◐ 2026-10-11 dump 成功；**当前 USB 个性 PID 变 0x2370/vendor class 0xFF ⇒ ImageCaptureCore 认不到、3 分钟超时**，改用 `s5_ptp_raw` |
| `s5_ptp_dump.py` | 早期 libusb/pyusb 版 | `./.venv/bin/python s5_ptp_dump.py --list`<br>`./.venv/bin/python s5_ptp_dump.py --dry-run`<br>`./.venv/bin/python s5_ptp_dump.py`<br>`./.venv/bin/python s5_ptp_dump.py --skip-baseline`<br>`./.venv/bin/python s5_ptp_dump.py --tag 0x080000a1` | ❌ **macOS 上 bulk IN 报 `[Errno 84] Overflow`，不可用**；Linux 可用 |
| `s5_usb_desc.c` / `s5_usb_desc` | **零副作用**：只发 chapter-9 `GET_DESCRIPTOR`，不打开接口 | `clang -framework IOKit -framework CoreFoundation -o s5_usb_desc s5_usb_desc.c`<br>`./s5_usb_desc [--list] [vid] [pid] [--strings N] [--no-open]`（默认 `0x04da 0x2370 strings=64`） | ⚠️ 新（2026-10-14），未见实测记录 |
| `s5_usb_listen.c` / `s5_usb_listen` | 被动监听服务通道的**两个 IN 端点**（bulk `0x82` + interrupt `0x83`） | `clang -O2 -framework IOKit -framework CoreFoundation -o s5_usb_listen s5_usb_listen.c`<br>`./s5_usb_listen [seconds] [vid] [pid] [--ptp]`（默认 seconds=20） | ⚠️ 新 |
| `s5_usb_ep0.c` / `s5_usb_ep0` | vendor IN 控制请求扫描（EP0） | `clang -O2 -framework IOKit -framework CoreFoundation -o s5_usb_ep0 s5_usb_ep0.c`<br>`./s5_usb_ep0 [vid] [pid] [--max N] [--types 80,c0,c1,c2]` | ❌ 文档记录 **三收件人 vendor IN 全 STALL** |
| `s5_usb_ep0out.c` / `s5_usb_ep0out` | vendor OUT 控制请求扫描（**唯一没试过的方向**）；**默认 DRY RUN** | `clang -O2 -Wall -framework IOKit -framework CoreFoundation -o s5_usb_ep0out s5_usb_ep0out.c`<br>`./s5_usb_ep0out [vid] [pid] [--go] [--start N] [--max N] [--types 40,41,42] [--delay ms] [--keep-going]` | ⚠️ 新（未实测） |
| `PTP_0x9421_dump_使用说明.md` | PTP dump 完整使用说明 + 安全底线 + 排错表 | — | ✅ |

### 1.7 固件 / UPD / 密码学（离线，`04_工具与脚本/firmware_crypto/`）

> ⚠️ **这批脚本多数有硬编码路径**：`exp_cipher.py`/`keyhunt2.py`/`ks_extract.py`/`parse_all.py`/`xver*.py`/`verify_sha.py`
> 读 `~/Downloads/S5___V29.bin`；`ivsig.py`/`keyhunt.py`/`rawtest.py`/`verify512.py` 读**当前工作目录**的
> `S5___V29.bin` + `s5_parts_v2.json`；部分还 `from Crypto.…` **需要 pycryptodome**。

| 工具 | 用途 | 确切调用命令 | 状态 |
|---|---|---|---|
| `parse_upd.py` / `parse_all.py` | UPD 固件包解析（parts/布局/外层头/分区表 48×92） | `python3 parse_upd.py`（内部 `parse_upd(path)`）<br>`python3 parse_all.py`（读 `~/Downloads/S5___{V11,V20,V23,V24,V29}.bin`） | ✅ 离线跑通 |
| `keyhunt.py` / `keyhunt2.py` | AES 密钥线索搜索 | `python3 keyhunt.py` / `python3 keyhunt2.py` | ❌ **结论：密钥在芯片 OTP，不可离线提取** |
| `exp_cipher.py` / `ks_extract.py` | 密码学实验 / 密钥流提取（`history` 明文 vs `ipu_data` 密文 ⇒ 密钥流熵） | `python3 exp_cipher.py` / `python3 ks_extract.py` | ❌ 密钥流熵 ≈8 ⇒ 真加密流 |
| `verify512.py` / `verify_sha.py` / `ivsig.py` | 签名与校验验证（512B 重复结构、条目 SHA=明文 SHA、IV 是否可由 name/index 派生） | `python3 verify512.py` / `python3 verify_sha.py` / `python3 ivsig.py` | ❌ IV 无确定派生；`ivsig.py` 报"需公钥,无法离线完成" |
| `xver.py` / `xver2.py` / `xver_fixed.py` | 跨版本（V11/V20/V23/V24/V29）门与结构验证 | `python3 xver.py` / `python3 xver2.py` / `python3 xver_fixed.py` | ✅ 离线跑通（版本字段 5 版一致） |
| `rawtest.py` | 原始数据/解压尝试 | `python3 rawtest.py` | ❌ |
| `交付包_tools/analysis/*.py` | 上列的 **Python3（非 2）交付副本**：`verify_sha` `ks_extract` `keyhunt` `keyhunt2` `xver` `parse_upd` `xver_fixed` `parse_all` `xver2` `rawtest` `verify512` `ivsig` `exp_cipher` | 同名同用法 | ◐ 交付副本 |

### 1.8 BLE 蓝牙（`04_工具与脚本/campaign2/` + `ble_win/`，另 `08_/09_` 包内有副本）

| 工具 | 用途 | 确切调用命令 | 状态 |
|---|---|---|---|
| `ble_scan.swift` / `ble_scan` | 扫描 + 连接 + **完整 GATT 枚举** | `swiftc -framework CoreBluetooth -framework Foundation -o ble_scan ble_scan.swift`<br>`./ble_scan 30` | ✅ 实机 |
| `ble_read.swift` / `ble_read` | 逐特征读取诊断；`--idle` 判别"读触发断链 vs 空闲超时" | `./ble_read …`（`--idle`） | ✅ 实机（**任何属性读都会被相机断链**） |
| `ble_pair.swift` / `ble_pair` | 完整配对链路（注册通知 → 读 `INITIAL_INFORM` 取密钥 → 写 `DLNA_UUID`/`FRIENDLY_NAME` → 读 SSID/密码） | `./ble_pair` | ✅ 实机 |
| `ble_diag.swift` / `ble_diag` | 完整诊断：枚举 + 描述符 + 通知 + 读 +（可选）写 | `./ble_diag` | ✅ |
| `ble_write_then_read.swift` / `ble_wr` | **复现正确顺序的凭据读取**（先写身份、再读 SSID/密码） | `./ble_wr` | ✅ |
| `ble_hold.swift` / `ble_hold` | 握手后**保持连接**（相机热点只在 BLE 会话期间在线） | `./ble_hold` | ✅ |
| `ble_lan_pair.swift` / `ble_lan_pair` | 局域网版：BLE 注册身份 + 同一 UUID 走 `accctrl`（含加密路径编码器） | `./ble_lan_pair` | ✅ |
| `ble_wifi_pair.swift` / `ble_wifi_pair` | BLE 侧 Wi-Fi 配对 | `./ble_wifi_pair` | ⚠️ |
| `ble_then_ap.sh` | **正确顺序**：先 BLE 唤醒热点 → 再连热点 → `accctrl` | `( nohup bash ble_then_ap.sh <结果目录> >/dev/null 2>&1 & )`（内含 `CAM_SSID="S5-XXXXXX"`、`IFACE=en0` 需改） | ✅ 实机（否则 join 必然 `-3970`） |
| `hold_then_ap.sh` | **BLE 全程保持** + 连它开的热点 + `accctrl` | `( nohup bash hold_then_ap.sh <结果目录> >/dev/null 2>&1 & )` | ✅ |
| `s5_ap_pair.py` | 连上相机热点后的 `accctrl` 配对 | `python3 s5_ap_pair.py <outfile> [camera_ip]`（默认 `192.168.54.1`） | ✅ |
| `s5_ap_probe.py` / `s5_ap_probe2.py` | 热点侧探测并落 JSON | `python3 s5_ap_probe.py <out.json> [camera_ip]`<br>`python3 s5_ap_probe2.py <out.json> [cam_ip]` | ⚠️ |
| `wifi_ap_pair.sh` / `wifi_ap_probe.sh` / `wifi_ap_probe2.sh` / `wifi_ble_pair.sh` | 热点/BLE 配对编排脚本 | `bash wifi_ap_pair.sh …` 等（参数见脚本头部） | ⚠️ |
| `s5ctl.sh` | 控制小工具 | `bash s5ctl.sh …` | ⚠️ |
| `04_工具与脚本/ble_win/s5_ble.py` | **Windows/bleak** 版：`scan`/`enum`/`read`/`idxtest` | `python s5_ble.py scan [seconds]`<br>`python s5_ble.py enum`<br>`python s5_ble.py read <uuid> [...]`<br>`python s5_ble.py idxtest` | ⚠️ 第三方/协作者提供，需 `bleak` |
| `04_工具与脚本/ble_win/s5_ble_watch.py` | 守望广播 → 连接 → 枚举 → 25s 空闲稳定 → 读 idx35→idx5→idx6 | `python s5_ble_watch.py [minutes]` | ⚠️ |
| `04_工具与脚本/ble_win/s5_ble_handshake.py` | 复刻官方握手**读**路径：先订阅 ~12 个 CCCD 通知再读 | `python s5_ble_handshake.py [--confirm]`（**会写相机**：标准 GATT CCCD 写） | ⚠️ 未验证假设 |
| `04_工具与脚本/ble_win/s5_ble_pair.ps1` | WinRT 显式配对（macOS CoreBluetooth 缺的能力） | PowerShell 直接跑 | ⚠️ |

**BLE 关键 UUID（`s5_ble.py` 头部原样）**：
主服务 `054ac620-3214-11e6-ac0d-0002a5d5c51b`；`idx35` 密钥源（`INITIAL_INFORM`）`03e23a31-a54c-40fa-a668-de9acdc910bb`；
`idx5` `CAMERA_SSID` `e206a5c0-3214-11e6-afe4-0002a5d5c51b`；`idx6` `WIFI_PASS` `c97cf1a5-3c03-4290-8c1b-9e74b9500f54`；
`idx16` `DLNA_UUID`（写）`bb5d2a8c-5d3b-43ad-bfc3-470cad55c1ca`；`idx17` `NAME_APS`（写）`7b61774f-efb4-44c6-a66d-c69e3b384c4a`；**default key `0x9032782C`**。

### 1.9 APK 侧 / 固件预言机的脚本（`03_解包_APK/com.panasonic.jp.lumixsync/`）

| 工具 | 用途 | 确切调用命令 | 状态 |
|---|---|---|---|
| `lumix_handshake.py` | `accctrl` 握手（明文 + `--encrypt` 加密路径） | `python3 lumix_handshake.py`<br>`python3 lumix_handshake.py --ip 192.168.1.131 --test`<br>`python3 lumix_handshake.py --encrypt`<br>`python3 lumix_handshake.py --selftest` | ✅ 实机 |
| `capture_lumix.sh` | **离线**抓 LUMIX Sync ↔ 相机流量（`tcpdump`，需 sudo） | `./capture_lumix.sh [output.pcap]`（`IFACE=en0`） | ✅ 产出 `lumix_sync.pcap` |
| `oracle/upload_test.py` | **固件上传预言机**四阶段（0/1 安全，2/3 危险） | `python3 upload_test.py --ip 192.168.1.131 --bin ../fw_fetch/S5___V29.bin --phase 0`<br>`python3 upload_test.py --ip … --phase 1 --field 0x24`<br>`python3 upload_test.py --ip … --phase 2 --field 0x24 --confirm-risky`<br>`python3 upload_test.py --ip … --phase 3 --field 0x24 --partition zboot --confirm-risky`<br>（另 `--retries N` 默认 5） | ❌ **phase 0 已跑 4 次 ⇒ 无预言机，勿重复浪费 90MB 上传** |
| `oracle/wait_cam_and_run.sh` | 等相机上线自动跑阶段 0（15s 探测，30 分钟上限） | `bash wait_cam_and_run.sh` | ✅ 已跑 |
| `oracle/gate_test.py` | `fw_update_mode` 门禁测试（会话能否解锁 `camctrl&type=fw_update_mode`） | `python3 gate_test.py` | ✅ 实机 |
| `oracle/camset_write_test.py` | **CAMSET 校验和预言机**：A 原版 / B 改数据不改校验和 / C 改数据+修校验和 | `python3 camset_write_test.py` | ✅ 实机（证明校验和可伪造） |
| `oracle/fw_reject_test.py` | **安全**固件校验拒绝探针：用 CAMSET blob 冒充 `type=fw` 流式上传，在 UPD 魔数处被拒 ⇒ 确认固件校验门，**零变砖风险** | `python3 fw_reject_test.py` | ✅ 实机 |
| `oracle/mode_enum.py` | 只读 `cam.cgi` **MODE 枚举**（找 19 个已知 mode 之外的调试面） | `python3 mode_enum.py` | ✅ 实机（无额外 mode） |
| `fw_fetch/boot_analysis.py` | 48 分区表 + 逐分区熵/魔数/字符串统计（含 S5m2 对比） | `cd fw_fetch && python3 boot_analysis.py` | ✅ |
| `fw_fetch/boot_deep.py` | IV 线性拟合 / loader1 头部 / 解密假设深查 | `cd fw_fetch && python3 boot_deep.py` | ✅ |
| `fw_fetch/decrypt_attempt.py` / `decrypt_attempt2.py` | 解密尝试 1（XOR/AES/SHA-384）、2（48B 字段=密钥+IV 假设） | `cd fw_fetch && python3 decrypt_attempt.py` / `decrypt_attempt2.py` | ❌ 负结果 |
| `fw_fetch/cross_model.py` | S5 vs S5m2 对比（64B 块、`unk` 字段） | `cd fw_fetch && python3 cross_model.py` | ◐（**样本是 ZIP 截断，二进制级对比无效**） |
| `fw_fetch/scan_verify.py` | 明文容器公钥/结构扫描器 | `cd fw_fetch && python3 scan_verify.py` | ❌ **容器内无内嵌公钥** |
| `jadx_out/sources/p168v5/*.java` | 官方 app 反编译源码（**相机 HTTP 协议唯一权威来源**） | jadx 产物，直接读 | ✅ |

### 1.10 参考仓库里的可复用工具（`07_参考仓库/s1m2-research/`）

| 工具 | 用途 | 确切调用命令 | 状态 |
|---|---|---|---|
| `s1m2_firmware_project/tools/unpack_upd.py` | UPD 原始容器/头部/组件提取 | `python3 s1m2_firmware_project/tools/unpack_upd.py S1m2_V14.bin -o analysis/unpacked` | ◐ 需自备原厂 BIN |
| `…/verify_components.py` | 组件大小/散列/目录校验 | `python3 s1m2_firmware_project/tools/verify_components.py analysis/unpacked` | ◐ |
| `…/repack_upd.py` | 外层原样重打包与一致性验证 | `python3 s1m2_firmware_project/tools/repack_upd.py analysis/unpacked -o /tmp/S1m2_V14_roundtrip.bin` | ◐ 验收：逐字节一致 |
| `…/ptp_property_parser.py` | 已采集 PTP 属性响应的紧凑 TLV 解析 | `python3 s1m2_firmware_project/tools/ptp_property_parser.py …` | ◐ |
| `…/dump_memory_parser.py` | 合成内存格式样本解析（**无真实 RAM 输入**） | `python3 s1m2_firmware_project/tools/dump_memory_parser.py …` | ❌ 无真实输入 |
| `…/tests/run_all_tests.py` | 五套固件测试 | `python3 s1m2_firmware_project/tests/run_all_tests.py` | ◐ |
| `evidence/verify_public.py` | 校验随库档案 + 三项 PTP 布局测试 + 合成 RAM 标记测试 | `python3 evidence/verify_public.py` | ◐ |
| `evidence/reproduce_offline.py` | 一键离线重放（能力解码 + 保存首张对照；带 `--firmware` 时含 5 套测试） | `python3 evidence/reproduce_offline.py --output ../s1m2-replay`<br>`python3 evidence/reproduce_offline.py --firmware /absolute/path/S1m2_V14.bin --output ../s1m2-replay-with-firmware` | ◐ |
| `analysis/read_s1m2_known_setting.py` | 读保存首张开关字段（配置子标签 `0x030f`） | `python3 analysis/read_s1m2_known_setting.py --json analysis/highres_firstnormal_on_fan_20261008_04/config_1.DAT analysis/highres_firstnormal_off_fan_20261008_05/config_1.DAT` | ◐ |

> ⚠️ **`07_参考仓库/s1m2-research/` 是精简副本**：`docs/REPRODUCE.md` 提到的
> `analysis/inspect_firmware.py`、`probe_encoding.py`、`compare_versions.py`、
> `recover_ptool_crypto.py`、`probe_cbc_without_iv.py`、`audit_*.py` 等 **在本仓库副本里不存在**。

### 1.11 自有 App 源码（`05_源码/`）

| 工具 | 路径 | 用途 | 确切调用命令 | 状态 |
|---|---|---|---|---|
| LumixFast-iOS | `05_源码/LumixFast-iOS/` | iOS 移植版（取景 / 遥控 / 相册浏览 + DLNA 回传） | `xcodegen generate` → `open LumixFast.xcodeproj`<br>`./scripts/build_ipa.sh`（未签名 → `dist/LumixFast.ipa`）<br>`DEVELOPMENT_TEAM=XXXXXXXXXX ./scripts/sign_ipa.sh`（→ `dist/LumixFast-signed.ipa`） | ◐ 有 IPA 产物 |
| LumixMonitor-iOS | `05_源码/LumixMonitor-iOS/` | 功能更全的监看 App（含 Intent/Shortcuts、`ControlView`、`DashboardView`） | `xcodegen generate` → Xcode Run；产物 `build/LumixMonitor.ipa`、`build/LumixMonitor.xcarchive` | ◐ 有 IPA 产物 |
| usb-scsi 源码集 | `05_源码/usb-scsi/` | 从 **S1R II 官方内核**（linux-4.19.124 + Panasonic Milbeaut 移植）按 USB SCSI 主题导出的源码；**关键文件 `drivers/usb/gadget/legacy/pvc_mass_storage.c`（松下私有 USB 大容量存储 gadget）** | 只读参考（见 `05_源码/usb-scsi/README.md`） | ✓ 源码 |

### 1.12 外部工具 / 编译器 / 系统命令（`00_项目总结/05_环境与依赖.md`）

| 项 | 版本 | 用途 | 状态 |
|---|---|---|---|
| `/usr/bin/python3` | **3.9.6** | 全部 Wi-Fi/CGI 脚本；**仅标准库** | ✅ |
| 项目 Python | `/Users/<user>/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3` | 无线监看/传输脚本的**指定解释器**（含 numpy/Pillow） | ✅ |
| `swiftc` | 6.4 | BLE 三工具编译 | ✅ |
| `clang` | 21.0.0 | `s5_ptp_raw.c`、`s5_ptp_dump.m` | ✅ |
| `xcodegen` | `brew install xcodegen` | LumixFast-iOS 工程生成 | ✅ |
| `ipatool` | 2.7.0（`brew install ipatool`） | 试着下 iOS LUMIX Sync IPA | ❌ **FairPlay 加密，反编不出代码；改走 Android APK。**非必要依赖 |
| macOS 框架 | — | `CoreBluetooth` / `CoreWLAN` / `Foundation` / `IOKit`+`IOUSBLib` / `CoreFoundation` | ✅ |
| 系统命令 | — | `curl` `sips` `plutil` `unzip` `dns-sd` `codesign` `networksetup` `ioreg` `system_profiler` `diskutil` `shasum` | ✅ |

**已知不可用组件（别重复踩）**

| 组件 | 状态 | 替代 |
|---|---|---|
| `ffprobe`（Homebrew ffmpeg 9.0.1_1） | ❌ **崩溃**：`Symbol not found: _av_bprint_finalize` | 自写 Python 解析 MOV/MP4 box（`tkhd`/`stsd`/`stts`/`stss`） |
| `pyusb` / libusb | ❌ macOS bulk IN `EOVERFLOW`(84) | IOKit/IOUSBLib（`s5_ptp_raw`） |
| ImageCaptureCore | ❌ 当前个性 PID `0x2370`/vendor class `0xFF` 不被识别 → 3 分钟超时 | `s5_ptp_raw` |
| `airport` 工具 | ❌ macOS 14+ 已移除 | CoreWLAN（读 SSID 需定位权限） |
| 免密 `sudo` | ❌ 不可用 | 抓包/写卡只能人工 `sudo` |
| Wireshark/dumpcap/tshark | ❌ 未安装 | 无 |
| `tcpdump` | ⚠️ 需 sudo（本项目靠 `capture_lumix.sh` 由用户跑） | — |

---

## 2. 数据资产清单

### 2.1 固件二进制（`02_固件二进制/`，整目录 700 MB）

| 路径 | 大小(B) | SHA256 | 用途 |
|---|---|---|---|
| `02_固件二进制/DC-S5/S5___V29.bin` | 90,238,464 | `b2ec4aeec209693b874df8dfdf11fc85b38fa4675b44ec554b7a167f430827e1` | **主目标固件**（UPD，MC801，VD4.30/V2.9），48 分区、加密 |
| `02_固件二进制/DC-S5/S5___V29.sig` | 512 | `76bfa404cc0e056971d19b42e3de188d9c56fde0b429cdf437d73541009a806a` | RSA-4096 签名（= `.bin` 尾 512 B 的独立拷贝） |
| `02_固件二进制/DC-S5/S5___V29.bin.parts.json` | 10,700 | `4fe13caa2c18f7e7389c66551db78bf5cac30bec103f5aa76cac9411a52cc9e3` | 48 分区表解析结果（= `s5_parts_v2.json`） |
| `02_固件二进制/DC-S5/s5_layout.json` | 13,983 | `bc9a1b3fc1b2ab7a3128d0264d58758760bcb48997bb94f5dd5dd43b0939af29` | 固件布局（F3 成果） |
| `02_固件二进制/DC-S5/s5_parts_v2.json` | 10,700 | 同 `.parts.json` | 分区表（供 `firmware_crypto/*.py` 读） |
| `02_固件二进制/DC-S5_版本历史/S5___V11.bin` | 88,178,176 | `1895f7e19c41039851ade42a212cb3c8db307ffc7e6df27cc91317d184652ac3` | 跨版本对照（V1.10） |
| `02_固件二进制/DC-S5_版本历史/S5___V20.bin` | 88,702,464 | `5af7e7f434748727c27f9066948ec442f0906412dcf97b8261eaad83febedcef` | 跨版本对照（V2.03） |
| `02_固件二进制/DC-S5_版本历史/S5___V23.bin` | 90,238,464 | `8b0703d5b7383db5314dce55ea84272a68ad2ed9dbe54b4672434e501cb156fd` | 跨版本对照（V2.30） |
| `02_固件二进制/DC-S5_版本历史/S5___V24.bin` | 90,238,464 | `b23c3eddd3af819c0444afd88f30cf782c72dbc3558d15fe9e5d646e1c69449f` | 跨版本对照（V2.40） |
| `02_固件二进制/DC-S1H/S1H__V28.bin` | 91,012,608 | `a3cc5c88cde50f5980acb67f849a33d74432effc9a8e4d3ab95b56b7e13f0514` | S1H V2.8，**53 分区 / 表起 `0x2DC`**，隐藏格式参考机型 |
| `02_固件二进制/DC-S1/S1___V24.bin` | 90,226,176 | `1c54dd84bddb4ebf041713eb47a1d37b6996162479055153a4699459b21ee0bd` | S1 V2.4 对照 |
| `02_固件二进制/DC-G100/G100_V13.bin` | 105,410,048 | `6c726fe0278a2a4a31a5c4f21f7f05915dfbb435579f5241259f85e3dc91492c` | **G100 明文固件**（18_G100明文与同类项目） |

> **注**：`G100_V13.bin` **不在 `MANIFEST.sha256` 里**（哈希为本次现算）。
> 上述 S5 V29 / S5 版本历史 / S1H / S1 的哈希**与 `MANIFEST.sha256` 逐字节一致**（已核对）。

### 2.2 相机配置与设置 dump（`04_工具与脚本/ptp/`、`06_数据与证据/camera_settings/`）

| 路径 | 大小(B) | SHA256 | 用途 |
|---|---|---|---|
| `04_工具与脚本/ptp/s5_config_0x9421_DC-S5_v2.9.bin` | 65,545 | `e808a6b899173a5a7ee8ef7a790c5ca24ba450d64b80ea3fe731db10123f20ab` | **USB PTP `0x9421` 全量配置 dump**（成品，S5 = 64.0 KiB，831 条 16 位记录） |
| `04_工具与脚本/ptp/ptp_out_wired/config_0x9421.bin` | 65,545 | `d3f30fc79f7fd83c67e67cffc15ed9b6fee7ca4f27cdfb07005f926dba2f26c8` | 有线 PTP 复测 dump |
| `04_工具与脚本/ptp/ptp_out_wired/device_info.bin` | 225 | — | `GetDeviceInfo`（型号/固件/SN） |
| `04_工具与脚本/ptp/ptp_out_wired/{storage_ids,sync_list}.bin` + `*.resp.bin` | 12 / 32 / 12×4 | — | PTP 基线事务载荷 + 12 B 响应头 |
| `04_工具与脚本/ptp/ptp_out_wired/capture_log.json` | 1,558 | `c525be5391cf320a8f9c124c7dccddcf7165e42ca0df6317e566eba44f8ad564` | 每事务 opcode/返回码/字节数日志 |
| `04_工具与脚本/ptp/ptp_out_fwup/fwup_ev_0x4100001{2..7}*.bin` | 12 / 20 ×13 | — | `0x9605` 固件升级状态机**只读**查询事件载荷 |
| `04_工具与脚本/ptp/ptp_out{,2..6}/capture_log.json` | — | — | 早期 PTP 尝试（含失败留档） |
| `04_工具与脚本/ptp/ptp_out_vendor/`、`ptp_raw_out/` | 空目录 | — | 待填 |
| `06_数据与证据/captures/s5_device_info_DC-S5.bin` | 225 | `57971c8da62b73166c7dc05fb65244e027b1fd2516e9591f95f82f5deb5f5b45` | 设备信息 |
| `06_数据与证据/captures/lumix_sync.pcap` | 1,084,323 | `db2ac23cf9efbdef9a106da2e9e2388ba970dac416b44e5ae9e0e83b74df0d93` | **相机↔app 网络抓包（协议逆向依据）** |
| `06_数据与证据/captures/s5_dl.html` | — | — | DLNA 描述页留档 |

### 2.3 camsetting blob / 菜单 XML / 能力声明（**隐藏格式这条线的全部原始证据**）

| 路径 | 大小(B) | SHA256 | 用途 |
|---|---|---|---|
| `06_数据与证据/camera_settings/camsetting.bin` | 65,533 | `84171981fdd871af5f9b3e76a79447531a784aba15adca528d5b341213e8d740` | **核心 blob**（pal+mp4+`0xc1`）：44 B 头 + 8 B 子头 + **831 条 TLV** + 尾 + 1 B 校验和（`sum%256==0`） |
| `06_数据与证据/camera_settings/allmenu.xml` | 307,714 | `2cf69074d41ac134e9a65ca631cf4842cefc5c49d24cc855ac2094fdbd1e857c` | `getinfo&type=allmenu` 菜单树（**740 item / 666 可设置 / 47 cmd_type**；唯一非标准大响应） |
| `06_数据与证据/camera_settings/capability.xml` | 8,150 | `6de123f761d05fcf55426ba61e48339c88de2107a22e1518076180188a823adc` | 能力声明（6 camcmd / 17 camspec / 协议版本 10.0） |
| `06_数据与证据/camera_settings/curmenu.xml` | 47,162 | `79af32bdbddc2c30b552f9f7c474b1ca4cf9f06036364f8cc53a692f204f2533` | 当前菜单（**判"档位是否可用"的权威判据：`enable="yes"` 集合**） |
| `06_数据与证据/camera_settings/surface_map.json` | 25,229 | — | 界面/控制面映射 |
| `03_解包_APK/…/camera_api/lumix_allmenu.xml` | 307,714 | 与 `allmenu.xml` 同 | 同一份菜单树的 APK 侧存档 |
| `03_解包_APK/…/camera_api/lumix_curmenu.xml` | 46,726 | — | `curmenu` 存档 |
| `03_解包_APK/…/camera_api/lumix_capability.xml` | 8,150 | — | `capability` 存档 |
| `03_解包_APK/…/camera_api/lumix_lens.xml` | 113 | — | 镜头 CSV（含镜头序列号 3997 字段） |
| `03_解包_APK/…/camera_api/lumix_state.xml` | 622 | — | 状态存档（`cammode=play`） |
| `03_解包_APK/…/oracle/burst_183125/live_camsetting_full.bin` | 65,533 | `f2d639681bc6431de989965018df0e5104e6772a566ad5729cd48fe03e9c66c0` | 活体 blob（burst/photo 态，288 处与 campaign 态不同） |
| `03_解包_APK/…/oracle/live_camsetting.bin` / `live_camsetting2.bin` | **94** | — | **陷阱：这两份不是 65,533 B blob，是错误响应的 94 字节** |
| `04_工具与脚本/campaign2/out/blob_GOLD_mov_persisted_20261013_020600.bin` | 65,533 | `13b5925487913288043503d76a5ed257e164052540da38f50a4cebd3c107745c` | **黄金 payload（mov 已持久态）** |
| `04_工具与脚本/campaign2/out/diff_blob_mov.bin` | 65,533 | `2202fca00555793aafb95fa1d15486af4d94475968555b3d9834d5f95608610f` | ntsc+**mov**+`0x8b` 态 |
| `04_工具与脚本/campaign2/out/diff_blob_mp4.bin` / `blob_postreboot_*.bin` | 65,533 | — | mp4 态 / 断电重启后态（F==E 逐字节相同） |
| `04_工具与脚本/campaign2/out/backup_pre_*.bin`、`restore_payload_*.bin`、`mov_shadow_*.bin`、`quality_payload_*.bin` | 65,533 ×N | — | 每次写 flash 前的自动备份 + 各实验 payload（回滚底） |
| `04_工具与脚本/campaign2/out/parse_out.txt` | — | — | 831 条记录的逐字段 dump |
| `04_工具与脚本/campaign2/out/parse_s5_records.py` | — | — | **blob 解析脚本（全文内嵌在 `S5_format_slots_analysis.md` 末尾）** |

> ⚠️ `隐藏格式持久化_成果.md` 提到的 `out/GOLDEN_S5_hidden_format_payload.bin` **在本仓库不存在**（已核实缺失）。

### 2.4 exFAT 实验证据（`06_数据与证据/exfat/`）

| 路径 | 大小(B) | SHA256 / 内容 | 用途 |
|---|---|---|---|
| `bm_before.bin` | 61,036 | `a1da5e505bf51ccdb415bbff16dad4bd2334c05035e57142df24b28641efc12b` | 写前分配位图快照 |
| `bm_after.bin` / `bm_now.bin` | 61,036 ×2 | — | 写后/当前位图 |
| `bm_*.bin.meta.json` | 120–123 | `{"boot_ck":643956855,"cluster_count":488288,"allocated":199,…}` | **卡指纹**（BootChecksum / ClusterCount / 已分配簇数） |
| `s5_go1_state.json` | 467 | `{"tail":115,"old":4294967295,"injected":491522,"target_start":39,"chain_len":77,"chain":[39..115],"mode":"L2"}` | **L2 越界注入记录（原值 0xFFFFFFFF → 越界值 491522）** |
| `.exfat_patch_backup.json` | 19 | 原值备份索引 | 还原用 |

### 2.5 隐藏格式证据包（`06_数据与证据/hidden_format_evidence/`）

| 路径 | 大小(B) | SHA256 | 用途 |
|---|---|---|---|
| `recording/P1022640/P1022640.MP4` | 888,140 | `b83395a3902c5a1b4cd73a30913f69436e36bbea53742297d3870b961802bd7d` | 隐藏档实拍样片（+ `metadata.json` / `software_decode.log`(1,841) / `verified_recording.json`） |
| `recording/P1022641/P1022641.MP4` | 223,826,574 | `a579a0ff325ed380ac8f6162421f8a382a19c9597e997fd6cf53aed072f19059` | 长样片（+ `full_decode.log` 65,731 / `verified_recording.json`） |
| `verified_findings.json` | 901 | — | 逐项实测认定（**注意 `snapshot_binary_included=false`、`my_list_saved_reentry_verified=false`**） |
| `candidate_results.md` | 1,664 | — | S1H PAL 16 项候选核对表 |
| `s1h_activation/*.bin`（13 个） | 小 | — | ⚠️ **不是 CAMSET 二进制，是 HTTP 响应 XML**（getter/setter 的 `camrply`） |
| `static_review/20261012_解码入口研究记录.md` | — | — | S1H 布局误判纠正（表尾 `0x15E8`；loader1/2/3 是特殊连续区） |
| `static_review/*.json` | — | — | 误判复现与偏移校正 |
| `native_menu.png` / `reboot_contact.png` | 1,708,299 / 4,988,970 | — | 机身菜单 / 重启接触点截图 |
| `historical_source/*.py.txt` + `README.md` | — | — | 历史脚本审计副本（**不应直接运行**） |

### 2.6 服务模式 / ROM BACKUP 证据

| 路径 | 大小(B) | SHA256 | 用途 |
|---|---|---|---|
| `06_数据与证据/rombackup_20261013/ADJUST.bin` | 131,072 | `40a43c65909d30158a1dd7a0fa6d7fbb9bcd87ef8a5a9fa427fd0db086f345de` | ROM BACKUP 导出（ADJUST） |
| `06_数据与证据/rombackup_20261013/FIX.bin` | 131,072 | `cf49c6336e6d487c11831aee568ad1ba8a5bde799b74deba03b95dd516c592d5` | ROM BACKUP 导出（FIX） |
| `06_数据与证据/rombackup_20261013/UPDATE.bin` | 131,072 | `b3817352f31d344284cd6ba9fc5b3fedd01e57becdf1b008c0fd08e62dae4538` | ROM BACKUP 导出（UPDATE） |
| `…/S5A.TXT` / `S5F.TXT` / `S5U.TXT` | 356,673 / 356,670 / 356,668 | `849bcb30…` / `59314333…` / `6ef6656b…` | 服务模式文本日志 |
| `06_数据与证据/service_mode_evidence/*.jpg`（7 张） | 102,994 – 2,053,216 | — | 服务菜单逐屏留档（含「相机信息 / 序列号与计数」「录制质量」「LENSCOMM」「SDCARD」） |
| `06_数据与证据/ble_evidence/20261013_ble_gatt_枚举.txt`、`…_ble_读取测试.txt` | 2,985 ×2 | — | GATT 枚举 / 读取测试原始记录 |

### 2.7 APK 解包产物（`03_解包_APK/`，整目录 256 MB）

| 路径 | 大小(B) | SHA256 | 用途 |
|---|---|---|---|
| `…/app.apk` | 32,802,428 | `1ae644d67bc5b42d4bd849e7c9ca099485f296ebdef89f269301fb4898edee6e` | 官方 LUMIX Sync APK 原件 |
| `…/classes.dex` / `classes2.dex` | 7,012,908 / 1,859,788 | `aca4d0a5…` / `61bb0c7f…` | dex 字节码 |
| `…/resources.arsc` | 4,237,988 | `c10a375bec4bab1ba06433046c6560cc207c9ecdd76067a398154979baad4f8a` | 资源表 |
| `…/jadx_out/` | **124 MB** | — | jadx 反编译产物（`sources/` 42 MB + `resources/` 82 MB） |
| `…/fw_fetch/fw_sample.bin` | 65,536 | `0bfa3436dd80d93ec9651f187e3c55d7a43f6e4b941fb2d1878924d21e1aef03` | S5m2 固件 ZIP 前 64 KB（**ZIP 截断样本，二进制级对比无效**） |
| `…/fw_fetch/S5___V29.sig` | 512 | 同 `02_固件二进制/DC-S5/S5___V29.sig` | 签名 |
| `…/fw_fetch/probe_results/`（**97 份 XML**） | — | — | 每个被探测命令/type 一份响应存档 |
| `…/fw_fetch/firm_list.xml` / `firm_info_s5m2.xml` / `apli_list.xml` | 1,573 / 5,260 / 443 | — | 固件目录/机型信息/app 目录 XML |
| `…/oracle/oracle_results.md` / `.jsonl` | 220,411 / 399,449 | — | 4 次 phase 0 完整响应与耗时日志 |
| `…/res/`、`assets/`、`lib/` | 58 MB / 2.3 MB / 15 MB | — | APK 资源 / 隐私声明与 license / 4 ABI native `.so`（`libdlnaCore` 等） |

> ⚠️ `03_解包_APK/…/fw_fetch/S5___V29.bin`（90 MB）**在本仓库不存在**（`TREE.md`/`README.md` 却这么写）。

---

## 3. 官方 APK 逆向的结论

> 来源：`03_解包_APK/com.panasonic.jp.lumixsync/README.md`、`PROTOCOL_AUDIT.md`、
> `PANASONIC_FIRMWARE_UPDATE_PROTOCOL.md`、`camera_api/lumix_key_method.md`，
> 以及 `jadx_out/sources/p168v5/*.java`。

### 3.1 传输层

- 基址 `http://<ip>`，命令统一 **GET**：`/cam.cgi?mode=<mode>[&type=][&value=][&value2=]`
  参数顺序**恒为 mode → type → value → value2**，为 null 的字段**整体跳过**（`p168v5/n.java:c()`）。
- **`User-Agent` 固定为 `LUMIX Sync`**（`p094l5/e.java:39`；文件下载类 `d` 继承 `e`）。
- `X-SESSION_ID` 头**仅当会话令牌非空时**附加（`p094l5/b.java:89`）；S5 不签发令牌 ⇒ app 从不发此头。
- 超时：默认 10000 ms；`camcmd`/`camctrl`/`getstate`/`get_content_info` 用 3000 ms；`playcmd` 10000 ms。
- 重试：每命令最多 **5 次**；`err_busy` 退避 **1000 ms**。
- 响应解析：按 `Content-Type` 判定——`text/xml` 走 XML，否则 CSV/纯文本。
- 所有执行调用串行化在一把全局锁上（`p168v5/m.java`）。

### 3.2 命令面（mode 全集，逐行核实自 `p168v5/a.java`）

| mode | type（实参） | value / value2 | 说明 |
|---|---|---|---|
| `camcmd` | 调用方传入（`poweroff`/`recmode`/`playmode`/`pictmode`/…） | — | 电源/模式 |
| `camctrl` | `focus`、`af_ae_lock`、`touch`、`touch_trace`、`pinch`、`asst_disp`、`change_disp_mag`、`frame_ctrl`、`fw_update_mode`、`lens_fw_update_mode`、`hrs`、`interval`、`livecomp`、`program_shift`、`shtrspeed_syncro`、`stop_motion`、`touchae_ctrl`、`touchaf_chg_area`、`touchaf_chg_pos`、`touchcapt_ctrl` | value/value2 | 实时控制 |
| `setsetting` | `device_name`、`photostyle`、`photostyle2`、`peaking`、`colormode`、`current_sd`、`overlay`、`raw_img_send` | value=新值 | 写设置 |
| `getsetting` | `photostyle`、`photostyle2`、`colormode`、… | — | 读设置 |
| `getstate` | `keep_alive` / 空串 | — | 状态轮询 |
| `getinfo` | `curmenu`、`lens`、`allmenu`、`camsetting`、`capability` | — | `camsetting` 走二进制通道（要求 `application/octet-stream`） |
| `get_content_info` | **空**（type 缺省） | `value=dir_id_*` | 目录内容 |
| `getprogress` | **空串** | — | 传输进度（响应 CSV `状态,百分比`） |
| `accctrl` | `req_acc`、`req_acc_g`、`req_acc_e`、`req_acc_can` | value=设备名、value2=网络名 | 会话握手 |
| `notify` | `transfer` | — | 传输通知 |
| `playcmd` | `start`/`stop`/`pause`/`restart`/`setplayscene` | — | 回放控制 |
| `editcmd` | `rating` | value=文件、value2=1–5 | 照片评分 |
| `startstream` / `stopstream` | — | value=UDP 端口（**49152–65535**） | 取景流 |
| `startsenddata` | `camsetting`、`fw`（**仅这两种**） | — | 上传会话 |
| `senddata` / `requestsenddata` / `endsenddata` / `abortsenddata` | — | — | 上传数据/续块/结束/中止 |

**`dir_id` 是字面令牌，放 `value` 不放 `type`**（`⚠️ 关键修正`）：
`dir_id_sd_auto_upload`、`dir_id_mark_list`、`dir_id_sd_mp4_only`、`dir_id_mem_mp4_only`。

### 3.3 会话 / 鉴权（**无令牌结论**）

- 明文 `req_acc` 实测响应为 **4 字段**：`ok_under_research_no_msg,S5-XXXXXX,remote,encrypted\r\n`，
  **无第 5 字段（令牌）**；`err_others_requesting` 表示已有别的客户端在请求会话。
- app 的 `T()` 要求首字段 == `ok` **且 ≥5 字段**才存令牌 ⇒ **app 对 S5 也从不存会话**。
- `req_acc_g` / `req_acc_e`（加密握手）本机返回 **`err_param`**（不支持，属其它机型）。
- **加密握手算法（其它机型路径，已还原）**：`req_acc_g` 拿 32 位十六进制密钥 →
  `H5/s.java` 的 XOR + 字节旋转混淆 uuid/name（key 为 0 时用默认 `-1875740628` = `0x904CB4AC`；
  字符串右补 `(char)255` 到 4 的倍数；每 4 字符大端拼 long 后异或 + 移位）→ `req_acc_e` → 取 index 4 为令牌。
- `H5/t.java` 的 RSA/OAEP（AndroidKeyStore 别名 `LumixSync`）**与 accctrl 无关**（app 自建密钥对）。
- **安全性评估**：明文 HTTP 无 TLS；"加密" = 可逆 XOR 混淆（密钥由相机主动给出）；令牌明文返回
  ⇒ **不构成安全边界**。
- **写命令同样免鉴权**：`camcmd&value=tele-normal` 返回 `ok`，全程无 `X-SESSION_ID`。

### 3.4 固件更新（上传）时序

```
GET /cam.cgi?mode=startsenddata&type=fw&value=<file-size>
   → <result>ok</result> + <method>once|separate</method> + <bufsize>N</bufsize>
separate → iA = bufsize - V()，逐块：
   POST /cam.cgi?mode=senddata   (multipart/form-data)
   GET  /cam.cgi?mode=requestsenddata
最后   GET  /cam.cgi?mode=endsenddata
失败   GET  /cam.cgi?mode=abortsenddata
```

- multipart boundary：`"=====" + UUID.randomUUID().toString() + "====="`（46 字符，进程内固定）。
- 每个 part：`Content-Disposition: form-data; name="filename"; filename="send"` +
  `Content-Type: application/octet-stream` + `Content-Transfer-Encoding: binary` +
  `Content-Length: <chunk-size>`；结束 `--<B>--` **前面没有 CRLF**。
- `V()` 用**硬编码 `Content-Length: 61460`** 估算每块开销 ⇒ 相机 `bufsize` ≈ `61460 + V()`（开销 ≈270 B，46 字符 boundary）。
- 响应 XML 标签：`<result>`（`ok`/`err_busy`/`err_reject`/`error`…）、`<method>`（`once`/`separate`）、`<bufsize>`（int）。
- 进度回调 `p168v5.s`：`a()` 开始 / `b()` 完成 / `c(result)` 错误 / `d(seconds, percent)` 剩余时间。
- 实测：`startsenddata=ok, method=separate, bufsize=61460`；**90,238,464 B ⇒ 1474 个 61192 B 分片 + 4341 B 尾块**。

### 3.5 DLNA 相关

| 项 | 结论 |
|---|---|
| 控制端点（SOAP `Browse`） | `http://<ip>:60606/Server0/CDS_control`（`p154t5/a.java:213`） |
| 数据端点 | `http://<ip>:60606/Lumix/Server0/ddd`（`p168v5/a.java:882`） |
| SOAPAction | `urn:schemas-upnp-org:service:ContentDirectory:1#Browse` |
| UA | `Panasonic MIL DLNA CP UPnP/1.0` |
| 缩略图 | 请求头 `X-CONVERT: MediumSize\|SmallSize` |
| 大小 | 响应头 `X-FILE-SIZE`；空间不足回 `notRemain` 并抛 `LargeData` |
| 端口 | **60606**（实测与 80 一起开放；`portscan` 只开 80/60606） |
| 授权门 | 设备描述/SCPD **免认证**；`Browse`/`50001` **需 accctrl 授权** |
| 模式 | **DLNA 内容树只在回放模式有内容** |
| 角色 | **官方 app 不用 `http://<ip>/DCIM/...` 拉文件**，走 DLNA；`/DCIM` 是相机额外暴露的旁路 |
| SSDP | 官方 native `dlnaCore` 的 `DlnaWrapper.advertisementStart()` 会广播存在；s5monitor 已复刻（`239.255.255.250:1900`，每 20 s 重发 + `/desc.xml`） |

### 3.6 官方 app **不存在**的功能（❌ 别自创协议）

| 项 | 结论 |
|---|---|
| **删除照片** | ❌ **官方无任何删除命令**（无 `delimage`/`delete`/`camcmd delimage`）；`delete` 字符串只在 DLNA 能力解析里出现 |
| **LUT / `.vlt` / `.cube` 上传** | ❌ **全源码无任何 LUT 文件传输**；LUT 匹配只有 UI 资源 `lvf_image_ctrl_lut_1..10`；S5 的 LUT 装载走 **SD 卡机内读取**；`setsetting photostyle/photostyle2` 只是**选择机内已装载的照片风格** |
| `startsenddata` 的 type | ✅ **只有 `camsetting` 与 `fw`**（改用 `type=photo_style` 传 LUT = 无依据的自创协议） |
| `getinfo` 子类型 | ✅ 只有 5 个（`curmenu`/`lens`/`allmenu`/`camsetting`/`capability`） |

### 3.7 活体只读探测（`fw_fetch/probe_results.md`，97 份响应存档）

- `getinfo&type=allmenu` = **307,714 B**（`menuset model="S5" version="2.0" date="20201027"`）——唯一非标准大响应。
- 约 **60 个 `getinfo&type` 候选 + 25 个隐藏 `mode` 候选**（`dump/diag/debug/read/memory/flash/key/otp/getfirm/backup`…）
  全部 `err_param` / `err_reject` / `err_unsuitable_app`。
- **W1 成果：Wi-Fi 无调试后门**（~70 候选 mode 全 `err_param`）。
- `lens` 接口返回镜头参数 CSV（含镜头序列号），属正常信息。

### 3.8 APK 侧汇总的四条最终结论（`README.md` §一）

1. 相机 HTTP 协议**已完全逆向，无需鉴权即可读写控制**。
2. 这台 S5 固件**不签发会话令牌**。
3. **固件容器格式已完全逆向，但分区数据是加密的**（熵 ≈7.8，无明文魔数）。
4. **密钥无法从 app、固件文件或相机 HTTP 接口获取**（在 MC801 芯片内部）。

---

## 4. 参考仓库清单

### 4.1 `07_参考仓库/s1m2-research/`（332 MB）

| 项 | 值 |
|---|---|
| 仓库名 | 松下 LUMIX 系统逆向研究（`lumix-s1m2-research`） |
| 主样本 | **Panasonic LUMIX DC-S1M2 V1.4**（BIN 171,867,648 B，SHA-256 `e91620854dd435131e03178076b486767cf9a3d2cfd62d173c537cb2afe9ea0f`），含旧 GH2 阳性对照与 Leica SL3 封装比较 |
| 用途 | 公开研究相机更新包、引导/加载链、平台源码、USB/PTP 协议、设置格式与维护接口 |
| 我们借鉴了什么 | ① **UPD 解包/校验/重打包工具**（`unpack_upd.py`/`verify_components.py`/`repack_upd.py`）；② **条目 48 B 字段 = 32 B SHA-256(明文) + 16 B 每分区 IV**（S5 上 `lens_hist` 阳性对照成立、7 个 type-2 分区 SHA 全匹配）；③ **`0x220` 64 B 块 = ECDSA P-256 签名**，不是密钥材料；④ 三平台同族映射 **S5=MC801 / S5M2=MC8223 / S1M2=MC8243（Milbeaut M20V）**；⑤ **CAMSET/`.DAT` TLV 记录结构**（tag/len/flag/payload，`0x005e` 格式门 + `0x122/0x123/0x124/0x16e` 逐格式质量记忆）直接用于解析 S5 的 65,533 B blob；⑥ `.DAT` 语义完全在固件内、无主机侧 tag→名称表（⇒ 不能凭 tag 猜含义）；⑦ **穷举排除离线破解**（GH2 自嵌式密钥移植、AV 固定 key、SL3 交叉、13 万+ 探测、CBC-without-IV） |
| 关键结论（我们复用） | **密钥固化在芯片硬件（OTP/eFuse/Crypto Engine/TrustZone），固件文件内无密钥材料** ⇒ 与我们的负结果一致 |
| 精简说明 | 本地是**精简副本**：`docs/REPRODUCE.md` 点名的多个 `analysis/*.py`（`inspect_firmware.py`、`probe_encoding.py`、`compare_versions.py`、`recover_ptool_crypto.py`、`probe_cbc_without_iv.py`、`audit_*.py`）**不在**本副本里 |

**仓库自带的"已验证结论 / 已排除 / 更正"三件套**（强烈建议直接引用，省自己踩）：
`docs/FINDINGS.md`（10 条已验证结论 + 边界）、`docs/DEAD_ENDS.md`（8 条已排除 + 3 条阻塞 + "不值得重复的动作"）、
`docs/CORRECTIONS.md`（8 条历史结论降级）、`docs/REPRODUCE.md`（从零复现步骤与验收）、
`docs/PUBLICATION.md`（脱敏与许可证边界）、`S1M2研究当前状态.md`、`S1M2固件逆向_阶段结果汇总.md`。

**它明确"不值得重复的动作"**：没有新材料时，**不重复同一批密钥猜测、下载入口循环或存根功能堆叠**。

### 4.2 `07_参考仓库/s5_oss_kernel/`（765 MB）

| 项 | 值 |
|---|---|
| 仓库名 | `s5_oss_kernel`（松下 **DC-S5 官方开源内核源码**） |
| 内容 | `linux-3.18.18.tar.gz`（127,569,372 B）+ 解包目录 + `copyright.tar.gz`（948,474 B）+ `copyright/*.htm`（21 个 GPL 声明页：`linux.htm` 6.7 MB、`glibc.htm` 2.2 MB 等） |
| 头文件版权 | `# Copyright (C) 2017-2019 Panasonic Corporation.`，`VERSION=3 PATCHLEVEL=18 SUBLEVEL=18` |
| 用途 | 松下 **Milbeaut** 平台内核源码；查驱动实现、设备树、USB gadget 面 |
| 我们借鉴了什么 | ① **`05_源码/usb-scsi/` 就是从 S1R II 的官方内核树按「USB SCSI」主题导出的源码集**：主机侧 `usb-storage`/UAS（`usb.c`/`transport.c`/`uas.c`）+ SCSI 核心（`scsi_lib.c`/`sd.c`/`sg.c`）；gadget 侧 `f_mass_storage.c` 的 `do_scsi_command` 与 **松下私有 `pvc_mass_storage.c`**（`05_源码/usb-scsi/README.md` 指出：**CDB 的实际解析/执行在松下用户态/固件完成，内核只做 CBW/CSW 搬运**）—— 即"恶意 U 盘打主机"和"恶意主机打相机"两个解析面；② `pvc_sdio.c` / `pvc_mass_storage.h` 等松下私有驱动样本；③ 印证 3.18 内核对 **exFAT** 的支持面（exFAT 越界写那条线） |
| 备注 | ⚠️ **本仓库的 `s5_oss_kernel/` 里没有 README/说明类 md**；只有上游 `linux-3.18.18/README`、`COPYING`、`firmware/README.AddingFirmware` 与 `copyright/*.htm`。真正的说明在 `05_源码/usb-scsi/README.md` |

### 4.3 官方 LUMIX Sync APK（第三方逆向对象，`03_解包_APK/`）

| 项 | 值 |
|---|---|
| 包名 | `com.panasonic.jp.lumixsync`（构建号 `b0834c31`） |
| 用途 | **相机 HTTP 协议 + BLE 协议 + 固件上传协议的唯一权威来源** |
| 我们借鉴了什么 | 全部 cam.cgi 命令面与参数格式、`req_acc` 握手/UUID 格式 `4D454930-0100-1000-8001-<seed>`、BLE 特征 UUID 与注册顺序、`startsenddata` 多部分与分块算法、DLNA 端点与 SOAP 头、`cfg` 目录令牌 |
| 备注 | ios 侧 `LUMIX Sync` IPA 因 FairPlay 加密**放弃**（`ipatool` 2.7.0 试过） |

### 4.4 报告里提到但**仓库内不存在**的两个克隆仓库

`03_解包_APK/…/README.md` 与 `TREE.md` 写有 `research_repos/williamwu1234-lumix-s1m2-research/`
与 `research_repos/siegfried82-lumix-s1m2-research/`（含 `unpack_upd.py`、`probe_cbc_without_iv.py`），
以及 `research_repos/*_notes.md`、`hardware_attack_surface_notes.md`、`verify_logic_notes.md`。
**这些目录/文件在本仓库中均不存在**（`03_解包_APK/…/research_repos/` 缺失）。见 §7 矛盾 #10。

我们**已确证复用过的版本**在 `07_参考仓库/s1m2-research/`（见 §4.1）。

---

## 5. exFAT 越界写这条线的结论

> 来源：`00_项目总结/04_定因与工具链成果_20261013.md`、`09_exFAT越界写成果包_20261013/README.md`、
> `04_工具与脚本/TOOLS.md`、`04_工具与脚本/campaign2/s5_exfat_test.sh`（脚本自述）、
> `06_数据与证据/exfat/s5_go1_state.json`。

### 5.1 成立的（✅）

| # | 结论 | 证据 |
|---|---|---|
| 1 | **内核对簇号不做归属校验**：释放文件簇时**完全跟随卡上被篡改的 FAT 链值** | 位图实机比对：注入的簇（不属于被删文件）**确实被释放** |
| 2 | 漏洞在 **exFAT 驱动的位图分配路径（`vol_amap`/`clr_alloc_bitmap`）**，**FAT32 不走这条路** | `s5_exfat_test.sh` 头注释 |
| 3 | **360 个 240 字符长文件名 ⇒ DC-S5 开机反复重启**（四组对照矩阵） | A 241×240 ✅ / **B 360×240 ❌** / C 2160×12 ✅ / D 360×12 ✅ |
| 4 | **纯目录项即可触发崩溃**，不需要文件数据、不需要任何注入 | `mkentries` 直接写目录项即可复现 |
| 5 | 阈值模型：**58 KB ✅ / 86 KB ❌** ⇒ 很像「定长缓冲 + 长度未校验」= **内存破坏类** | B vs C 排除"数量/体量"，B vs D 排除"分配大小" |

### 5.2 **已撤回**的（❌ 重要，别再引用）

| 结论 | 状态 | 撤回依据 |
|---|---|---|
| 「S5 内核**越界写**已实机确认」 | ❌ **撤回** | 注入**必为 NULL** 的 slab 填充区索引 → **只报错不崩** ⇒ 存在 **NULL 提前返回**；原推理"报卡写失败 ⇒ 内存写已执行"**不成立** |
| 「**堆喷命中越界槽**」 | ❌ **撤回** | A/B 对照：**去掉注入后照样重启** ⇒ 崩溃**不能归因于注入** |
| 「长名崩溃 = 数量 × 长度」 | ⚠️ **修正** | 初版实验里**我们自己的工具把目录链拐进了照片数据区** ⇒ 崩溃另有原因；重做后结论 = **长文件名本身** |

> **方法论铁律（已写入项目）**：
> ① **没有对照组的结论不要写进报告。**
> ② **"相机报写入错误"不能当作"内存写已执行"的判据** —— NULL 提前返回的表现完全一样。
> （**S1R2 报告也用了这个判据，后人不应照抄。**）

### 5.3 这个发现的价值边界（原文照录）

| 层面 | 评价 |
|---|---|
| 作为攻击面 | 🟡 **有限** —— 只是 **拒绝服务**，而"把卡做坏"本身就能让相机没法用，不构成新能力 |
| 作为漏洞线索 | 🟢 **有真价值** —— 与文件名字节总量相关的崩溃，典型成因是**定长缓冲溢出**（内存破坏类），比被 NULL 检查挡住的 exFAT 位图路径**更接近可利用** |
| 作为诊断信息 | 🟢 **立刻可用** —— S5 的**缓冲余量很紧**，任何堆布局相关的尝试都要把这条边界算进去 |
| 进一步利用 | 🔴 **需要调试通道**（UART/JTAG）。目前只有"崩/不崩"一个二值信号，与 exFAT 那条路遇到的是**同一堵墙** |

### 5.4 我们自己工具曾把卡写坏（已修复）+ 由此产生的硬规矩

```
根因：alloc_one_cluster() 只信分配位图；
      而相机位图【延迟写回】——未正常关机就拔卡，位图停在旧状态
后果：分配器拿到【照片正在使用的簇】→ 清零 + 断链 + 目录链拐进数据区
症状：照片"文件在、但无法访问/无法删除"
证据：FAT[39] 被改成 482（照片本该 39→40→…→115）
修复：分配簇改为三重校验 —— 位图位==0 且 不在目录链上 且 FAT[clu]==0
```

**两条硬规矩**：① **拔 SD 卡前必须在相机里正常关机**（让位图落盘）；
② **每次写卡前后都必须跑 `checkalloc`，`K > 0` 立即停手**。

### 5.5 三个"看起来像成功"的陷阱

| 陷阱 | 真相 |
|---|---|
| 相机报"写入错误" ⇒ 以为内存写执行了 | 可能是 **NULL 提前返回** |
| 相机重启 ⇒ 以为攻击命中 | 可能**与我们无关**（A/B 对照才发现） |
| 改了 FAT 后"能开机" ⇒ 以为补丁生效 | 可能**根本没被读到**（卡代次/指纹已变） |

**恢复**：从相机拔卡 → Mac 上 `diskutil eraseVolume ExFAT LUMIX /dev/disk8s1` → 插进相机让它自己格式化。**卡可完全恢复，无硬件损伤。**

### 5.6 exFAT 证据落盘位置

`06_数据与证据/exfat/`：`bm_before.bin` / `bm_after.bin` / `bm_now.bin`（各 61,036 B 位图快照 + `*.meta.json` 卡指纹）
+ `s5_go1_state.json`（L2 注入记录：原值 `0xFFFFFFFF` → 越界值 `491522`，目标链 39..115）
+ `.exfat_patch_backup.json`（原值备份）。
`09_exFAT越界写成果包_20261013/` 目录本身**已并库清空**，只留 README 指向 10 号包版本。

---

## 6. 已证伪 / 已排除的路线

> 强度标记：**✗ = 已证伪（终局）** · **◐ = 有强证据但未完全闭合（不能写成已证伪）**

### 6.1 固件 / 密钥（✗ 终局）

| # | 路线 | 结论 | 证据 |
|---|---|---|---|
| F1 | **AES 密钥离线提取** | ✗ **终局** | 密钥在 MC801 芯片 **OTP/eFuse/Crypto Engine/TrustZone**，**不在固件/转接环/I2C**；社区 13 万+ 探测 + GH2 自嵌式密钥移植 + AV 固定 key + SL3 交叉全排除 |
| F2 | **版本门改号绕过** | ✗ | `comm_proto_ver` 字段方向 + 无比较逻辑；版本字段在签名覆盖内 |
| F1b | 单字节 / 重复密钥 XOR | ✗ | 密钥候选：`"panasonic"`、`0x220` 64 B 块、48 B 字段、loader1 24 B/64 B、SHA/MD5 派生 —— 全不中 |
| F1c | RC4 | ✗ | 同上候选 + 24+64 拼接 + SHA256/SHA1/MD5 派生，`dtb`/`zimage`/`rootfs` 目标 |
| F1d | AES-128/192/256 ECB/CBC/CTR | ✗ | 全部候选密钥 × IV=`0`/前16B/后16B/12B-nonce+4B-counter |
| F1e | 48 B 校验块 = 无密钥哈希 | ✗ | SHA-384/256/1/MD5/CRC32 的 **19 种输入组合**（`name+data`、`entry92+data`、`header+data`、`panasonic`块+data…）全试过 ⇒ 极可能是**带芯片内密钥的 HMAC/CMAC** |
| F1f | IV 可由 name/index/model/序号派生 | ✗ | `ivsig.py` 全候选不中 |
| F1g | 固件内含解密密钥材料 | ✗ | `keyhunt.py`/`keyhunt2.py` 全分区高熵、无已知明文 |
| F3 | **容器内嵌公钥 / Phison 式"同替公钥+签名"** | ✗ | `verify_logic_notes`：明文容器**无内嵌公钥**（公钥只在 BootROM/OTP） |
| F4 | **无回退标志 / 次级验证路径** | ✗ | 验证工件仅 **CRC32 + ECDSA P-256 + RSA-4096** 三件 |
| F5 | **改版本 / 降级** | ✗ | 版本字段（外层 `0x24`、内层 `0x2C4`）被 ECDSA+RSA 签名覆盖 ⇒ 必破坏签名 |

### 6.2 固件上传「解密预言机」（✗ 已实测关闭）

- **`oracle/upload_test.py --phase 0` 已跑 4 次**，最后一次（02:51）在会话门打开后把**原封 V2.9 完整上传**：
  `startsenddata=ok,method=separate,bufsize=61460`，1474 分片全 `ok`，**最后一个分片** `err_busy`→重试→`err_critical`，
  `abortsenddata=error`；**相机仍在 VD4.30，未变砖**。
- 三条硬结论：
  1. **降级保护实证**：正确签名的旧固件被拒（`err_critical`），且发生在**收完全文件之后、写 flash 之前** ⇒ 版本/签名门先于写 flash。
  2. **无预言机**：只给一个粗粒度 `err_critical`（**不是** `err_fw_old`/`err_fw_same` —— 那是 app 端文案）；
     无逐字节/逐分片错误反馈；Wi-Fi HTTP 下 RSA 耗时被网络抖动淹没，**无可用时序差**。
  3. **阶段 1 前提已失效**（原假设"原始旧固件 → `err_fw_same`"，实测是 `err_critical`）⇒ 逐字段找版本位已无判别信号。
- ⇒ **建议停止上传预言机这条线**；phase 2/3 有真实变砖风险且换不到密钥。
- 阶段 0 实测耗时：`1474 chunks / avg 131 ms / 269 s`（另一次 `1475 / 350 ms / 590 s`）—— **别重复浪费**。
- **相对安全的替代**：`oracle/fw_reject_test.py`（用 CAMSET blob 冒充 `type=fw` 流式上传，在 UPD 魔数处被拒，**零变砖风险**）。

### 6.3 网络 RCE（✗ 全失败）

| # | 路线 | 结论 |
|---|---|---|
| W5a | **GoAhead buffer overflow** | ✗ |
| W5b | **LD_PRELOAD（CVE-2017-17562 / EV-43360）** | ✗ |
| W5c | file-op / exec / dynamic-load 泄漏 | ✗（~90 mode + ~110 getinfo 子类型候选全 `err_param`/`err_reject`） |
| W5d | CGI 参数注入 → shell | ✗（timing + MARKER 无回显） |
| W5e | DLNA 路径穿越 | ✗ |
| W7 | 服务器身份 | ✓ **Panasonic 定制 CGI（GoAhead 系）**；实测判据：`OPTIONS *` 返回 `Allow: OPTIONS, GET, HEAD, POST` ⇒ **lighttpd**；**错误页样式不能判别**（GoAhead 也是 XHTML）；`OPTIONS /cam.cgi`→500 与 `HEAD /cam.cgi`→500 都是 **cam.fcgi 后端**行为 |
| W6 | **CVE-2019-5096（multipart UAF）** | ◐ **未测** —— 唯一剩余公开 RCE，**需堆控** |

**⇒ 网络层 RCE 极难/很可能不可行；已证明的唯一可控原语是 `setsetting` 状态写（47 个可写域），可作状态变更/取证，但非代码执行。**

### 6.4 崩溃 / DoS（不是内存破坏）

| 路线 | 结论 |
|---|---|
| **PTP length-DoS** | ✅ **唯一可复现挂死**（12 B 头声明 length=`0x400`，相机校验 `type` 不校验 `length` 且无超时）；**拔插 USB 恢复，不砖机** |
| `senddata` 尾块拒 → 状态机 DoS | ✅ 曾致需**拔电池**的彻底卡死，**非内存破坏** |
| `crash_cam.py` / `crash_v3*.py` | ✅ 实测 ⇒ **状态机 DoS，非内存破坏** |
| `usb_oob.py` / `oob_read_probe.py` | ◐ 越界读**未闭合** |
| USB vendor IN（三收件人） | ❌ 全 STALL |
| USB bulk-OUT 8 种分帧 | ❌ 全 NAK |
| USB 两个 IN 端点 | ❌ 保持静默（⇒ 才需要 `s5_usb_listen` / `s5_usb_ep0out`） |
| vendor OUT 控制请求 | ⚠️ **唯一没试过的方向**（`s5_usb_ep0out`，默认 DRY RUN） |

### 6.5 exFAT / 长文件名

见 §5.2 —— ✗ 越界写、✗ 堆喷命中；✅ 长名 DoS（价值有限，需 UART/JTAG 才能进一步利用）。

### 6.6 环境/工具层面已排除

| 项 | 结论 |
|---|---|
| iOS LUMIX Sync IPA 逆向 | ❌ FairPlay 加密，反编不出代码；改走 Android APK |
| `ffprobe` | ❌ 崩溃（`_av_bprint_finalize`）；改用自写 Python 解析 MOV/MP4 box |
| `pyusb`/libusb（macOS） | ❌ bulk IN `EOVERFLOW`(84) |
| ImageCaptureCore（新 USB 个性） | ❌ PID `0x2370`/vendor class `0xFF` 不被识别，3 分钟超时 |
| `airport` 工具 | ❌ macOS 14+ 移除 |
| 免密 sudo / Wireshark | ❌ 不可用/未安装 |
| `S5m2 固件二进制级对比` | ❌ **样本是 ZIP 截断**（`PK\x03\x04`，内层 `S5m2_V31.bin` 205 MB 未完整下载），对比无效 |
| **「mov 开机回落 mp4」** | ❌ **已作废的原因解释**：真因是 `persist.py` 用**单次 65 KB POST**（相机要求分块 `method=separate`）⇒ mov **从未写进 flash**；改用正确分块后 mov 跨断电持久（n=2） |
| **「12 个影子槽 = 每模式格式默认」** | ❌ S5II 反例：slot1=`06` 但活动容器仍 slot0=`05` ⇒ **"任一槽=mov ⇒ 开机活动槽=mov"不成立** |
| **「改 slot0 就能持久 mov」** | ⚠️ 修订：相机自身行为是**仅写槽 0**；全槽写 n=1 回退、仅写槽 0 n=2 保留 ⇒ **相关性因果未确立，列为待验证假设** |

### 6.7 参考仓库明确"已排除/不值得重复"的（`07_参考仓库/s1m2-research/docs/DEAD_ENDS.md`）

| 路线 | 结论 |
|---|---|
| 旧 GH2/PTool 参数直接用于 S1M2 | ✗ 已试候选未获可信明文 |
| 原样套用 Panasonic A/V 固定密钥独立 8 字节块模型 | ✗ 与全 FF 候选及编码块分布不相容 |
| 把 SL3 当同款固件 / 直接替换加载器 / 用目录散列证明同密钥 | ✗ 实际编码载荷与关键组件不同 |
| 把 `GetPartialObject` 对象偏移当物理 RAM 地址 | ✗ 属媒体/对象读取，无任意物理内存映射证据 |
| 把配置 DAT / 保存首张字段当全输入 RAW | ✗ 得到的是序列化菜单配置，不是像素数据 |
| 从平台内核关闭 `STRICT_DEVMEM` 推断可在相机直接 `dd` | ✗ 无机身 shell/root/执行入口 |
| 把原厂存储查询 `0x9114` 当当前可用通道 | ✗ 本次返回 `0x2005`；标准存储详情 `0x2008` |
| 把存根编译 / 合成 RAM 标记 / 原样重打包当功能完成 | ✗ 没有采集/融合真实像素，也没有新机内可执行代码 |

**当前阻塞（不能写成已证伪）**：同型号调整软件/Adjustment Manual/Factory Data 未取得（TSN 登录门槛已确认）；
ROM BACKUP 的 S1M2 输出范围/大小/介质未知；49 个编码组件缺可信解码方法。

---

## 7. 文档之间的矛盾（**优先级最高的一节，直接决定"要不要动手"**）

### #1 【路径错误·影响最大】`cam_cgi/` 目录不存在，工具实际在 `campaign2/`

| 文档怎么说 | 实际 |
|---|---|
| `00_调用前必查…` §2.3：「现成工具：`04_工具与脚本/cam_cgi/safe_handshake.py`」 | `04_工具与脚本/cam_cgi/` **不存在** |
| `00_调用前必查…` §2.4：`cam_cgi/persist.py`、`cam_cgi/persist_quality.py`、`cam_cgi/container_switch.py`、`cam_cgi/hidden_features.py` | 全部实际在 **`04_工具与脚本/campaign2/`** |
| `TOOLS_工具箱总览.md` §一：`cam_cgi/` 是"主战场"，还列了 `probe_format_slots.py` 等 | 同上；另有一份完整副本在 `11_DC-S5成果包_20261013/02_工具链/cam_cgi/` |

**⇒ 任何人照 `00_调用前必查` 的命令 `cd cam_cgi && python3 persist.py verify` 都会直接失败。** 这很可能就是"没人读得全导致重复劳动"的头号成因。

### #2 【路径错误】`exfat/` 目录不存在

- `04_工具与脚本/TOOLS.md` §一：「**本轮主角是 `exfat/`**」，命令 `sudo python3 exfat_patch.py …`。
- `00_项目总结/04_定因…` §六 已自我更正："工具现位于 `04_工具与脚本/campaign2/`（原包内 `02_工具链/exfat/` 的副本已去重移除）"。
- 实际：`04_工具与脚本/campaign2/exfat_{patch,spray}.py`、`s5_exfat_test.sh`；另在 `11_DC-S5成果包_20261013/02_工具链/exfat/`。

### #3 【工具清单不一致】`TOOLS_工具箱总览.md` 的清单与磁盘对不上

**（a）文档提到了一个不存在的脚本**：§1.4 与 §1.5 都点名 **`probe_quality.py`** ——
`campaign2/` 里**没有**这个文件（实际是 `persist_quality.py`；"probe_quality" 极可能是旧名或笔误）。
§1.5 的 **`probe_*chunk*.py`** 也是通配写法，真实文件名是 `probe_final_chunk.py` / `probe_partial_final.py`。

**（b）`campaign2/` 里存在、但两份 TOOLS 文档都没列的工具（共 30+ 个）**：
`s5_quality.py`、`s5_ap_pair.py`、`s5_ap_probe.py`、`s5_ap_probe2.py`、
`hidden_test.py`、`hidden_test_hlg.py`、`crash_v3b.py`、`crash_v3c.py`、`crk.py`、`crk2.py`、
`batch_enable.py`、`enable_one.py`、`payload.S`、`run_recon_when_up.py`、
`ble_wifi_pair`(.swift)、`ble_then_ap.sh`、`hold_then_ap.sh`、`wifi_ap_pair.sh`、`wifi_ap_probe.sh`、`wifi_ap_probe2.sh`、`wifi_ble_pair.sh`、`s5ctl.sh`、`wait_and_run.sh`、
以及一整套 **exFAT** 工具（`exfat_patch.py` / `exfat_spray.py` / `s5_exfat_test.sh`）。
**其中最重要的是 `s5_quality.py`（2026-10-14 新增的健壮录制格式/质量控制台 + `err_reject` 退避 + 回读校验 + `a6k` 容器副作用自动复原），
两份 TOOLS 文档里一个字都没有。**

### #4 【内容矛盾】`TOOLS.md` 与 `s5_exfat_test.sh` 对子命令的记载不一致

- `TOOLS.md` §1.3 写的子命令：`prep / bitmap / chain / dumpbitmap / info / entries / go1 / go1check / go2 / session / verdict / setfat / restore`。
- 脚本 `case` 实际分支**多了 7 个**：**`checkalloc`**、**`mkentries`**、`hijack`、`mkdeleted`、`trimdir`、`mkspray`、`l1`、`l2`。
- **`checkalloc` 与 `mkentries` 正是 §5 全部关键结论（长名崩溃、写坏卡修复）依赖的命令**，而 `TOOLS.md` 完全没提。

### #5 【字段值矛盾】`mov_60p_200mbps_c4k_10bit` 的 blob 码

| 文档 | 值 |
|---|---|
| `隐藏格式持久化_成果.md`（权威、含更正说明） | **`0x8b`**（并明确写"不是旧文档/旧摘要写的 `0xf4`，那是错的"） |
| `隐藏格式持久化_成果_副本.md`（**同名副本，内容残缺**） | **完全没有 `0x8b`**，只列 `0x9b`/`0xc1`；字段表也比正本少 `0x8b` 与 `0x00`=NTSC 说明 |
| `persist.py` 源码常量 | `VQ_MOV60P_C4K = 0x8b` ✅ 与正本一致 |

**⇒ 应以正本 `隐藏格式持久化_成果.md` + `persist.py` 为准；`_副本.md` 应删除或标注"过期"。**

### #6 【老文档说"不可用"、新文档说"可用"】mp4hevc / HEVC

| 文档 | 说法 |
|---|---|
| `隐藏格式持久化_成果.md` 最终轮 | 「**放弃 HEVC** 容器」 |
| 同文件 10-14 更正框 | 「**`mp4hevc` 并非不可用**：NTSC + mp4 态下有 **2 档启用**（`mp4hevc_24p_72mbps_4k_10bit`、`mp4hevc_30p_72mbps_4k_10bit`）。项目当年"放弃 HEVC"是**主动取舍，不是相机不支持**。**凡写"HEVC 不可用/不支持"处均应加注**」 |
| `hidden_features.py` | `videoformat = mp4hevc` 列为 **WORKS**，但注 `(deprecated, 4:2:0 10-bit)` |

**⇒ 凡见"HEVC 不支持"的表述，都应按 10-14 更正加注。**

### #7 【数字矛盾】mov 态可选档数 17 vs 18；mp4 档数 16 vs 13 vs 8

| 文档 | 数字 |
|---|---|
| `隐藏格式持久化_成果.md` 最终轮 | mov 态 **17 档**；mp4 常规档 ~~16 个~~ → **13 个** |
| 同文件 10-14 追加实测 | **NTSC + mov = 18**（24p 6 + 30p 6 + 60p 6）；**PAL + mov = 12**；NTSC + mp4 = **8**（+mp4hevc 2） |
| `00_项目总结/01_成果总表.md` H2 | mov（NTSC **18** / PAL **12**）/ mp4（~~16~~ **8**，另 mp4hevc **2**） |
| `s5_quality.py` 头部 | 「`curmenu` 声明 126 条 mov 档，`allmenu` 只有 106 条，**机身实际可选仅 17 条**」 |

**⇒ 权威判据 = 实时 `GET /cam.cgi?mode=getinfo&type=curmenu` 中 `<item id="menu_item_id_v_quality_<档名>" enable="yes"/>` 的集合**；
"17"是 NTSC 专属旧数字（差 1 在于是否含当前选中项）。

### #8 【结论修订链·极易误读】mov 影子槽实验

| 文档 | 说法 |
|---|---|
| `S5II_slot_crosscheck_20261013.md` §3 | 「`experiment_mov_shadow.py --confirm`（3062..3074 全 = `0x06`）**依然是唯一正确的下一步**」 |
| 同文件 §4 后记 | 真因是 `persist.py` 单次 POST **从未写进 flash** ⇒ mov 持久化成立 |
| 同文件 §4 末 **10-14 补充** | 「§3 中"全槽写是唯一正确的下一步"**已被后续实验修订**：相机自身行为为**仅写槽 0**；全槽写（`06 ×13`）重启后回退为 `05 ×13` + mp4（**n=1**），而仅写槽 0（`06 05 ×12`）重启后保留（**n=2**）。**该相关性因果未确立，列为待验证假设**；操作上建议**采相机自身行为，即仅写槽 0**」 |
| `experiment_mov_shadow.py` 脚本 docstring | 仍以 H1/H2 假设呈现，**未反映上述修订** |

**⇒ 跑 `experiment_mov_shadow.py` 前必须读 `S5II_slot_crosscheck_20261013.md` §4 末段，否则会重复一个 n=1 已回退的实验。**

### #9 【持久化条件矛盾】`setsetting` 到底写不写 flash

| 文档 | 说法 |
|---|---|
| `隐藏格式持久化_成果.md` 机制表 | `setsetting`：`ntsc_pal` 写 flash ✓、`videoformat`/`videoquality` **只写 RAM** ✗ |
| **`hidden_features.py` 头部 WARNING** | 「settings written here are **AUTO-PERSISTED by the camera to flash**（confirmed 2026-10-13）」 |
| `06_数据与证据/…/S1M2_format_field_notes.md` 更正框 | 「"开机 mov 回落 mp4"实为 `persist.py` 的**上传协议 bug**，并非固件行为」 |
| `00_项目总结/01_成果总表.md` H1 | 三项**均可跨断电保留**（n=2）；**附条件**：`videoquality` 的保留与**开机时 SD 卡槽 1 的挂载状态**相关（槽 1 未挂载时 `0x9b`→`0x9f`） |

**⇒ 结论：字段级"写不写 flash"没有统一答案，且带 SD 卡挂载前提；样本量 n=2，机制假设待重复。引用时必须带条件。**

### #10 【文档引用了不存在的文件】多处"文件索引"与磁盘不符

| 文档说存在 | 实际 |
|---|---|
| `03_解包_APK/…/fw_fetch/S5___V29.bin`（90 MB）、`S5___V29_副本.bin` | **不存在**（固件只在 `02_固件二进制/`） |
| `…/README.md` 索引里的 `research_repos/*_notes.md`、`research_repos/{williamwu1234,siegfried82}-lumix-s1m2-research/`、`hardware_attack_surface_notes.md`、`verify_logic_notes.md` | **整个 `research_repos/` 目录不存在** |
| `04_工具与脚本/campaign2/out/GOLDEN_S5_hidden_format_payload.bin` | **不存在** |
| `07_参考仓库/s1m2-research/docs/REPRODUCE.md` 点名的 `analysis/inspect_firmware.py`、`probe_encoding.py`、`compare_versions.py`、`recover_ptool_crypto.py`、`probe_cbc_without_iv.py`、`audit_*.py` | **本地副本里不存在**（精简副本） |
| `01_研究报告/…/scripts/USB-PTP/s5_ptp_dump`（在 08/09/11 包内） | 09 包里**只剩 11 个文件**（`01_研究报告_全集/…/scripts/{RCE/s5pre_mipsel.o,s5pre_mipsel.so,USB-PTP/s5_ptp_dump}` 3 个 + `02_工具链/ble/{ble_diag,ble_hold,ble_lan_pair,ble_pair,ble_read,ble_scan,ble_wr}` 7 个 + 1 个 README），其余 414 个已去重移除 |

### #11 【方法论矛盾】`oracle/README.md` 的判定表已被实测推翻

- README 原假设：原始旧固件 → `err_fw_same`；`err_reject` → 签名门；`ok` → 版本绕过成立。
- 实测（2026-10-10）：原封 V2.9 → **`err_critical`**（不是 `err_fw_same`）⇒ **判定表 3 行全部失配**，
  「逐字段找版本位」已无判别信号。README 自己也在 §"阶段 0 实测结论"里承认了这点，但**判定表仍留在文中**（只加了"前提已失效"一行）。

### #12 【同名不同内容】两份"隐藏格式持久化_成果"

| 文件 | 行数 | 内容 |
|---|---|---|
| `campaign2/隐藏格式持久化_成果.md` | 196 | 完整：机制表 + 字段偏移 + HEVC 追加 + 最终轮 + 4 处更正框 + 备份/回滚清单 |
| `campaign2/隐藏格式持久化_成果_副本.md` | 73 | 残缺早期版：无 HEVC 节、无最终轮、无 `0x8b`、字段表少项 |

**⇒ 只保留/只引用 196 行那份。**

### #13 【数据结构记载矛盾】camsetting blob 的头部与记录数

| 项 | `S5_camsetting_fieldmap.md`（Hank） | `S5_format_slots_analysis.md`（更正） |
|---|---|---|
| 记录流起点 | `0x2c` | **`0x34`**（`0x2c..0x33` 是 8 B 子头 `cc ff 00 00 00 03 00 00`）；`0x2c` 说法"Hank's map said payload begins at 0x2c"是错的 |
| 记录数 | 830 | **831**（Hank 漏了 tag `0x0001` 机型标识 = 13×u16 `0x0049` = `'I'`） |
| `0x005e` 记录头偏移 | `0x0bee`(3054) | **`0x0bf0`(3056)**（Hank 的"active value = byte 3062"是对的，只有记录偏移差 2） |
| `videoquality` 槽数 | 16 | **13**（`len=0x20=32` = 6 B 头 + 26 B payload = 13×u16；Hank 差 3） |

**⇒ 引用 blob 结构时以 `S5_format_slots_analysis.md` 为准。**

### #14 【任务简报 vs 实际】本块简报的字数/文件数

| 简报说 | 实际 |
|---|---|
| `03_解包_APK/` 13 个 md、6,540 行 | ✅ 13 个 md；行数 6,540（含 `oracle_results.md` 的 **3,063 行**自动日志） |
| `04_工具与脚本/` 13 个 md、2,297 行 | ✅ 13 个 md、2,297 行（**未计入 `campaign2/out/*.md` 的 5 份分析**——它们也是 md，共 887 行，本文已读） |
| `07_参考仓库/` 58 个 md，只读 README/说明类 | ✅ 58 个 md；但 **`s5_oss_kernel/` 里 0 个 md**（只有 `linux-3.18.18/README`、`COPYING`、`copyright/*.htm`）⇒ 该仓库的"说明"实际在 `05_源码/usb-scsi/README.md` |
| `05_源码/` 2 个 md | ✅ `LumixFast-iOS/README.md`(135) + `usb-scsi/README.md`(92) |
| `06_数据与证据/` 4 个 md | ✅ 含 `historical_source/README.md`(3 行) |

---

## 8. 本块最有价值的 5 条

1. **`04_工具与脚本/campaign2/` 是真正的"军火库"，而且文档把它写错了地方。**
   日常主力四个（`persist.py` / `persist_quality.py` / `container_switch.py` / `hidden_features.py`）+
   全部 exFAT 工具（`exfat_patch.py` / `exfat_spray.py` / `s5_exfat_test.sh`）**都在这一个目录**。
   修好文档里 `cam_cgi/` 这一个错误路径，能立刻消掉项目里最大的一类重复劳动。
2. **`04_工具与脚本/campaign2/s5_quality.py` 是 2026-10-14 新增、却几乎没有被任何索引收录的"最健壮设置器"**：
   它把 `err_reject`（不是失败，是状态窗口问题）、`ok ≠ 生效`（唯一可信判据是回读）、
   `a6k` 家族会静默把容器改成 `avchd` 这三条血泪教训**全做进了代码**（退避重试 + 回读校验 + 容器复原 + `--allow-grey` 门）。
   做任何录制格式/质量实验**应该先用它**，而不是自己重写 `setsetting`。
3. **`06_数据与证据/camera_settings/camsetting.bin`（65,533 B）+ `S5_format_slots_analysis.md` 里内嵌的 `parse_s5_records.py`，
   是一套"离线就能干活"的完整工具**：44 B 头 + 8 B 子头 + **831 条 TLV（`field_id u16 / len u16 / flag u16 / payload`）** +
   `ff ff 00 00` 尾 + 1 B 校验和（`sum%256==0`）；关键字段偏移 `3062`(videoformat) / `6986`(videoquality) / `65230`(ntsc_pal)。
   不用碰相机就能做字段差分、槽语义分析、payload 构造（改完必须重算 `byte[65532]`）。
4. **"没有对照组的结论不要写进报告"这条铁律的代价已经被量化付过了**：exFAT 越界写与堆喷命中两条结论被撤回，
   原因都是缺 A/B 对照 + 把"相机报写入错误"当"内存写已执行"。同一个错误判据 **S1R2 报告也用了**——
   这条复盘（`00_项目总结/04_定因与工具链成果_20261013.md` §2.2/4.3）比任何工具都值钱，应该前置到所有交接文档开头。
5. **`07_参考仓库/s1m2-research/docs/DEAD_ENDS.md` + `CORRECTIONS.md` 是"防止重复劳动"的现成范本**：
   它把 8 条已排除路线、3 条"当前阻塞（不能写成已证伪）"、以及"**不值得重复的动作**（没有新材料时不重复同一批密钥猜测、下载入口循环、存根功能堆叠）"
   写成了正式文档，每条都附证据文件与"允许重新打开的条件"。**本项目的 `00_调用前必查…` §三已知陷阱应该按同样的格式补齐"重新打开条件"。**

## 9. 最容易被重复劳动的 3 件事

1. **重新写一个 `cam.cgi` 客户端 / 重新逆一遍协议。**
   官方 app 的命令面已经**逐行核实**（`PROTOCOL_AUDIT.md` 的 mode 全集表 + `p168v5/n.java` 的 URL 构建原文）、
   分块上传协议已完整还原（`PANASONIC_FIRMWARE_UPDATE_PROTOCOL.md`：`once`/`separate`、`bufsize`、`V()` 上的 61460 硬编码、multipart 布局）、
   DLNA 端点/头/端口全部有据（`60606`、`CDS_control`、`Lumix/Server0/ddd`、`X-CONVERT`）。
   **⇒ 先查 §3，再决定写不写代码。** 尤其**删除照片**和 **LUT 上传**这两条：官方 app 里**根本不存在**，
   重写一遍只会得到同一个"无协议依据"的结论。

2. **重跑"固件上传预言机" / 再上传一次 90 MB 固件。**
   `oracle/upload_test.py --phase 0` **已跑 4 次**（最后一次 1474 分片 / 269 s / `err_critical`，相机未变砖），
   结论是**没有预言机**：只有粗粒度 `err_critical`、无逐片反馈、无可用时序差，且**降级保护已实证**（正确签名的旧固件在写 flash 前被拒）。
   想再验证"固件校验门"请用 **`oracle/fw_reject_test.py`**（用 CAMSET blob 冒充 `type=fw`，**零变砖风险**）。
   同理，**离线解密**不要再跑：XOR/RC4/AES 全模式 + 19 种 48 B 校验块输入组合 + IV 派生候选**全已排除**（§6.1）。

3. **重做 exFAT 越界写 / 重新论证"越界写是否成立"。**
   两条结论（越界写实机确认、堆喷命中越界槽）**已正式撤回**，撤回依据是**决定性实验**（注入必为 NULL 的 slab 填充区索引 ⇒ 只报错不崩 ⇒ 存在 NULL 提前返回）与**A/B 对照**（去掉注入照样重启）。
   现状：内核确实不校验簇归属（✅ 成立），但越界索引处有 NULL 提前返回 ⇒ **这条路已被挡住**；
   真正有价值的剩余线索是**长文件名 DoS（360 × 240 字符 ⇒ 反复重启）**，而它进一步利用**需要 UART/JTAG**。
   **⇒ 动手前必读 §5.2 与 `00_项目总结/04_定因与工具链成果_20261013.md` §2.2，并遵守两条硬规矩：正常关机后再拔卡、每次写卡前后跑 `checkalloc`（`K > 0` 立即停手）。**
