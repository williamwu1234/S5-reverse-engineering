# H · 全项目命令 / 结论编号 / 已排除 / 危险 四表索引

> **本文件是机械提取产物**：对 `/Users/<user>/Documents/ChatGPT/S5_逆向_项目总包_20261012` 下
> 全部 `.md` 做穷尽 grep + 代码块扫描后汇总，**不对内容做判断、不改写原文**。
> 供「项目唯一权威调用文档」作索引层素材使用。

## 0. 提取口径与去重规则（务必先读）

| 项 | 说明 |
| --- | --- |
| 提取范围 | 项目根下全部 `.md`（460 个文件 / 159,999 行） |
| 排除范围 | `07_参考仓库/`（第三方仓库普通文档，只看 README 类）、`20_总包调用文档_素材/`（本目录）、`.git/` |
| 命令来源 | ① ` ```bash `/` ```sh `/` ```powershell `/` ```http `/ 无语言标注代码块内的命令行；② 正文行内反引号跨度。**原样抄录，未改写** |
| 结论编号来源 | 表格行首单元格 / 列表项 / 标题中的**编号定义行**（非引用行） |
| 已排除 / 危险来源 | 含关键词的表格行、列表项、标题、短正文行 |
| **去重规则** | 项目内存在大量**逐字节相同**的副本：460 个 `.md` 只有 **196 份唯一内容**，**264 份是冗余副本**。本索引统一引用**规范路径**（优先非聚合包、层级更浅者）；完整副本映射见 §5 |
| 出处标注 | 每条给 1–3 个规范 `路径:行号`；「出现次数」列 = 该字符串在**全部副本中**的原始出现处数 |
| 离线声明 | 全程只读本地文件，**未连接任何设备、未发送任何报文** |

### 0.1 编号体系的坑（机械事实，勿踩）

- **`E1–E28` 有两套并存编号，极易混淆**：
  - *全局累计编号*：`dlna_HTTP_SOAP审计.md` = E1–E15 → `dlna_SOAP动作与XML解析审计.md` = E16–E24 → `dlna_剩余盲区审计.md` = **E25–E28**；合计「28 项已排除」（`19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:18`、`:658`）。
  - *文件内局部编号*（**不属于**上一套，同号不同义）：`dlna_SSDP_GENA审计.md` = E1–E12（含 E10b/E10c/E10d）；`dlna_SSDP入站取值审计.md` = E1–E13 + U1。
- `R1–R10`（审计复核项）与 `R1–R6`（已撤回/已更正的说法）是**两套不同的 R**。
- `P1–P7`（待证项/开放问题）与 `P1–P8`（硬件·侵入式路线行动项）是**两套不同的 P**。
- `F1–F5`（S5 成果总表）与 `F3–F8`（S1RM2 `f_fs` 缺陷清单）是**两套不同的 F**。
- `C1–C24`（容器/格式事实结论）与 `C-1`（DLNA 唯一候选）是**两套不同的 C**。
- `H1–H7`（含 `H1b`/`H1c`）为本项目隐藏格式成果编号；`N-S5-1–4` 为 G100 分析新增结论。
- `结论 1–12` 是**外部同事报告**（S5M2 报告）的编号，被本项目大量引用转述，**非本项目自建**，其定义不在本包内。

---

## 表 1 · 全项目可执行命令索引

共 **590** 条去重命令，原始出现 **1601** 处。按工具族分组，组内按命令字典序。

### A. 相机 HTTP / cam.cgi 接口（curl 与 HTTP 报文） —— 39 条

| # | 命令（原样） | 出处（规范路径:行号） | 出现次数 |
| --- | --- | --- | --- |
| 1 | `CALLBACK: <http://192.168.1.50/>     ← 使目标头字段值长度 ≥ 81 字符（具体填充位置待定，见下）` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:178 | 1 |
| 2 | `Content-Length: 0` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:181 | 1 |
| 3 | `DELETE /x              → 404 Not Found` | 19_路径1_Linux侧攻击面_20261015/更正_Web服务器身份与作废的RCE线索_20261015.md:22 | 1 |
| 4 | `GET  /cam.cgi?mode=…   → 200 OK（620 B XML）` | 19_路径1_Linux侧攻击面_20261015/更正_Web服务器身份与作废的RCE线索_20261015.md:26 | 1 |
| 5 | `HEAD /                 → 403（与 GET / 一致，正常）` | 19_路径1_Linux侧攻击面_20261015/更正_Web服务器身份与作废的RCE线索_20261015.md:24 | 1 |
| 6 | `HEAD /cam.cgi?mode=…   → 500 Internal Server Error` | 19_路径1_Linux侧攻击面_20261015/更正_Web服务器身份与作废的RCE线索_20261015.md:25 | 1 |
| 7 | `HOST: 192.168.1.131:60606` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:177 | 1 |
| 8 | `NT: upnp:event` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:179 | 1 |
| 9 | `OPTIONS *              → 200 OK   Allow: OPTIONS, GET, HEAD, POST   ★ 决定性` | 19_路径1_Linux侧攻击面_20261015/更正_Web服务器身份与作废的RCE线索_20261015.md:19 | 1 |
| 10 | `OPTIONS /cam.cgi       → 500 Internal Server Error` | 19_路径1_Linux侧攻击面_20261015/更正_Web服务器身份与作废的RCE线索_20261015.md:20 | 1 |
| 11 | `PUT /x                 → 404 Not Found` | 19_路径1_Linux侧攻击面_20261015/更正_Web服务器身份与作废的RCE线索_20261015.md:21 | 1 |
| 12 | `SUBSCRIBE /upnp/event/ContentDirectory HTTP/1.1` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:176 | 1 |
| 13 | `TIMEOUT: Second-1800` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:180 | 1 |
| 14 | `TRACE /                → 403 Forbidden` | 19_路径1_Linux侧攻击面_20261015/更正_Web服务器身份与作废的RCE线索_20261015.md:23 | 1 |
| 15 | `curl "http://<相机>/cam.cgi?mode=accctrl&type=req_acc"` | 12_S5无线监看_v1.0_20261014/README.md:236 | 2 |
| 16 | `curl "http://<相机IP>/cam.cgi?mode=getsetting&type=focusmode"` | 04_工具与脚本/s5_monitor/README.md:636 | 3 |
| 17 | `curl -A "LUMIX Sync" "http://<IP>/cam.cgi?mode=getstate"` | 00_调用前必查_已跑通路径总索引.md:45 | 1 |
| 18 | `curl -A "LUMIX Sync" http://<相机IP>/cam.cgi?mode=getstate` | 16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/README.md:91 | 1 |
| 19 | `curl -H "User-Agent: LUMIX Sync" "http://$S5_IP:80/cam.cgi?mode=getsetting&type=6k4k_photo"    # 期望 6k_burst` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/03_opengate_6k_photo.md:55 | 3 |
| 20 | `curl -H "User-Agent: LUMIX Sync" "http://$S5_IP:80/cam.cgi?mode=getsetting&type=pictsize_burstspeed"` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/03_opengate_6k_photo.md:56 | 3 |
| 21 | `curl -H "User-Agent: LUMIX Sync" "http://$S5_IP:80/cam.cgi?mode=setsetting&type=6k4k_photo&value=6k_burst"` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/03_opengate_6k_photo.md:48<br>01_研究报告/03_隐藏格式_可分发版_20261012/docs/03_opengate_6k_photo.md:61 | 6 |
| 22 | `curl -H "User-Agent: LUMIX Sync" "http://$S5_IP:80/cam.cgi?mode=setsetting&type=aspectratio&value=3:2"` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/03_opengate_6k_photo.md:52<br>01_研究报告/03_隐藏格式_可分发版_20261012/docs/03_opengate_6k_photo.md:62 | 6 |
| 23 | `curl -H "User-Agent: LUMIX Sync" "http://$S5_IP:80/cam.cgi?mode=setsetting&type=pictsize_burstspeed&value=6k_18m_30p"` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/03_opengate_6k_photo.md:49 | 3 |
| 24 | `curl -s "http://127.0.0.1:8080/api/gallery?id=0"` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:231<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:231 | 2 |
| 25 | `curl -s -A "LUMIX Sync" \<br>"http://192.168.1.131/cam.cgi?mode=accctrl&type=req_acc_can&value=<同一UUID>&value2="` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:257 | 1 |
| 26 | `curl -s -A "LUMIX Sync" \<br>"http://192.168.x.x/cam.cgi?mode=accctrl&type=req_acc_can&value=<同一UUID>&value2="` | 16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:257 | 1 |
| 27 | `curl -s -A "LUMIX Sync" "http://192.168.x.x/cam.cgi?mode=getstate" \| grep -E "cammode\|sd_memory\|current_sd"` | 16_S5_核心总包_20261015/README.md:125<br>README.md:126 | 2 |
| 28 | `curl -s -m 5 "http://192.168.1.131:60606/Lumix/Server0/ddd" \| head -c 600` | 14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:221 | 1 |
| 29 | `curl -s -m 5 "http://192.168.x.x:60606/Lumix/Server0/ddd" \| head -c 600` | 16_S5_核心总包_20261015/14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:221 | 1 |
| 30 | `curl -s http://127.0.0.1:8080/api/state \| grep -o '"access_raw":"[^"]*"'` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:227<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:227 | 2 |
| 31 | `curl -s http://192.168.1.131/cam.cgi?mode=<M>` | 03_解包_APK/com.panasonic.jp.lumixsync/fw_fetch/probe_results.md:36 | 1 |
| 32 | `curl -s http://192.168.1.131/cam.cgi?mode=getinfo&type=<T>` | 03_解包_APK/com.panasonic.jp.lumixsync/fw_fetch/probe_results.md:13 | 1 |
| 33 | `curl -s http://192.168.54.1:60606/ \| head` | 14_总包审计与新方向_20261014/03_新方向与实验设计.md:448 | 2 |
| 34 | `curl -s http://192.168.54.1:60606/Lumix/Server0/ddd \| head -40` | 14_总包审计与新方向_20261014/03_新方向与实验设计.md:447 | 2 |
| 35 | `curl -s http://192.168.54.1:60606/desc.xml \| head -40` | 14_总包审计与新方向_20261014/03_新方向与实验设计.md:451 | 2 |
| 36 | `curl -s http://192.168.x.x/cam.cgi?mode=<M>` | 01_研究报告/01_固件AES绕过_调研_20261010/01-固件格式与启动/probe_results.md:36 | 3 |
| 37 | `curl -s http://192.168.x.x/cam.cgi?mode=getinfo&type=<T>` | 01_研究报告/01_固件AES绕过_调研_20261010/01-固件格式与启动/probe_results.md:13 | 3 |
| 38 | `curl -sI http://192.168.54.1:50001/ \| head` | 14_总包审计与新方向_20261014/03_新方向与实验设计.md:449 | 2 |
| 39 | `curl -sI http://<cam>/` | 19_路径1_Linux侧攻击面_20261015/阶段A_Linux攻击面测绘_20261015.md:134 | 1 |

### B. Python 工具链调用（相机侧：设置/持久化/质量/容器/传输） —— 262 条

| # | 命令（原样） | 出处（规范路径:行号） | 出现次数 |
| --- | --- | --- | --- |
| 40 | `$P analysis/ida_S5M2_AES/recover.py S5m2_V37.bin                # 结果：music 3.4 MB` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:430 | 1 |
| 41 | `$P analysis/ida_S5M2_AES/s1_recon.py      # 8 镜像逐节状态 + 跨镜像 K32` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:422 | 1 |
| 42 | `$P analysis/ida_S5M2_AES/s2_keystream.py  # 已知明文→密钥流；复用测试` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:423 | 1 |
| 43 | `$P analysis/ida_S5M2_AES/s3_scheme.py     # nonce 唯一性、弱 PRNG、nonce=密钥` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:424 | 1 |
| 44 | `$P analysis/ida_S5M2_AES/s4_relate.py     # 同镜像内密钥流关系` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:425 | 1 |
| 45 | `$P analysis/ida_S5M2_AES/s5_stat.py       # 重复块 / 明文泄漏 / 统计检验（需 cryptography）` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:426 | 1 |
| 46 | `$P analysis/ida_S5M2_AES/s6_keybattery.py # 119 候选密钥 × 11 约定（0 命中）` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:427 | 1 |
| 47 | `$P analysis/ida_S5M2_AES/s7_aescode.py    # 定位 G100 里的 AES 模块与其调用者` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:428 | 1 |
| 48 | `$P analysis/ida_S5M2_AES/s8_misc.py       # nonce 来源、跨机型同址比较、导出明文` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:429 | 1 |
| 49 | `$PY check_style.py testdata/frame.jpg              # → NORMAL` | 15_LUT烧录工具_20261014/README.md:219<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:219 | 2 |
| 50 | `$PY check_style.py testdata/frame_synth_vlog.jpg   # → LOG` | 15_LUT烧录工具_20261014/README.md:220<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:220 | 2 |
| 51 | `$PY make_lut.py --from vlog --size 17 --formats vlt --out lut` | 15_LUT烧录工具_20261014/README.md:215<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:215 | 2 |
| 52 | `$PY make_lut.py --from vlog --size 33 --formats cube --out lut` | 15_LUT烧录工具_20261014/README.md:216<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:216 | 2 |
| 53 | `$PY make_lut.py --selftest` | 15_LUT烧录工具_20261014/README.md:214<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:214 | 2 |
| 54 | `$PY watch_bake.py --lut lut/vlog_to_709_17.vlt --src /tmp/watch_src --out /tmp/watch_out --once` | 15_LUT烧录工具_20261014/README.md:228<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:228 | 2 |
| 55 | `./.venv/bin/python s5_ptp_dump.py` | 04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:48 | 7 |
| 56 | `./.venv/bin/python s5_ptp_dump.py --dry-run` | 04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:45 | 7 |
| 57 | `./.venv/bin/python s5_ptp_dump.py --list` | 04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:42 | 7 |
| 58 | `./.venv/bin/python s5_ptp_dump.py --skip-baseline` | 04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:51 | 7 |
| 59 | `./.venv/bin/python s5_ptp_dump.py --tag 0x080000a1` | 04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:54 | 7 |
| 60 | `./.venv/bin/python tools/analysis/keyhunt.py   # 需 S5___V29.bin 在根目录` | 01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:64 | 3 |
| 61 | `/Users/<user>/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3 \<br>-u s5monitor.py --host 192.168.1.131 --port 8080 --device-name "LUMIX Sync" \\ \<br>--pacing-mode fixed --pacing-fps 18` | 00_调用前必查_已跑通路径总索引.md:25 | 1 |
| 62 | `/Users/<user>/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3 \<br>s5_selfcheck.py --cam 192.168.1.131` | 12_S5无线监看_v1.0_20261014/连热点时怎么测.md:38 | 1 |
| 63 | `/Users/<user>/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3 \<br>s5_selfcheck.py --cam 192.168.x.x` | 16_S5_核心总包_20261015/12_S5无线监看_v1.0_20261014/连热点时怎么测.md:38 | 1 |
| 64 | `/Users/<user>/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3 s5_selfcheck.py` | 12_S5无线监看_v1.0_20261014/连热点时怎么测.md:16<br>16_S5_核心总包_20261015/12_S5无线监看_v1.0_20261014/连热点时怎么测.md:16 | 2 |
| 65 | `<LOCAL_HOME>/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 analysis/probe_cbc_without_iv.py` | 01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_解码突破记录.md:148<br>01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件逆向_阶段结果汇总.md:312 | 6 |
| 66 | `<LOCAL_HOME>/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 analysis/probe_metadata_keys.py` | 01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件逆向_阶段结果汇总.md:310 | 3 |
| 67 | `<LOCAL_HOME>/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 analysis/recover_ptool_crypto.py` | 01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_解码突破记录.md:147<br>01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件逆向_阶段结果汇总.md:311 | 6 |
| 68 | `P="env -u PYTHONHOME -u PYTHONPATH .venv-re/Scripts/python.exe"` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:421 | 1 |
| 69 | `PY=/Users/<user>/.dsh/dsh-runtimes/dsh-primary-runtime/dependencies/python/bin/python3` | 15_LUT烧录工具_20261014/README.md:211<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:211 | 2 |
| 70 | `cam_cgi/container_switch.py mov --persist` | 00_调用前必查_已跑通路径总索引.md:57 | 1 |
| 71 | `cam_cgi/hidden_features.py status/vlog/restore` | 00_调用前必查_已跑通路径总索引.md:58 | 1 |
| 72 | `cam_cgi/persist.py verify/restore/flashwrite <tag>` | 00_调用前必查_已跑通路径总索引.md:55 | 1 |
| 73 | `cam_cgi/persist_quality.py <quality_name>` | 00_调用前必查_已跑通路径总索引.md:56 | 1 |
| 74 | `enum_videoquality.py --confirm` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/06_安全约束与风险.md:49 | 3 |
| 75 | `env -u PYTHONHOME -u PYTHONPATH .venv-re/Scripts/python.exe analysis/ida_S5M2_AES/<script>.py` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:399 | 1 |
| 76 | `env -u PYTHONHOME PYTHONPATH="C:\\Program Files\\IDA Professional 9.1\\idalib\\python" \<br>.venv-re/Scripts/python.exe -u analysis/ida_S5M2_AES/ida_slice.py 0x04EEF000 0x1600 aes` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:401 | 1 |
| 77 | `experiment_mov_shadow.py --confirm` | 01_研究报告/07_隐藏格式持久化_追查_20261013.md:56<br>04_工具与脚本/campaign2/out/S5II_slot_crosscheck_20261013.md:65 | 6 |
| 78 | `firmware_crypto/*.py` | 00_调用前必查_已跑通路径总索引.md:61 | 1 |
| 79 | `fw_fetch/decrypt_attempt*.py` | 03_解包_APK/com.panasonic.jp.lumixsync/TREE.md:90 | 1 |
| 80 | `persist.py restore` | 00_项目总结/02_项目时间线.md:99<br>01_研究报告/07_隐藏格式持久化_追查_20261013.md:125<br>14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:191<br>（另 1 处） | 8 |
| 81 | `persist.py verify` | 00_项目总结/02_项目时间线.md:78<br>00_项目总结/02_项目时间线.md:89 | 4 |
| 82 | `probe_format_slots.py --run` | 00_项目总结/02_项目时间线.md:61 | 2 |
| 83 | `python analysis/ida_S5M2_AES/recover.py S5m2_V37.bin` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:296 | 1 |
| 84 | `python ptp_client.py --op 0x9102,0x10001    # 发送单个操作码` | 01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:249 | 3 |
| 85 | `python ptp_client.py --test                 # 开会话 + GetDeviceInfo` | 01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:248 | 3 |
| 86 | `python ptp_fuzz_deep.py --vectors=345       # fuzz 数据长度 / 参数个数 / 边界值` | 01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:250 | 3 |
| 87 | `python recover.py GX9__V15.bin` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:312 | 1 |
| 88 | `python s5_ble.py enum         # 连接(不配对) + 完整 GATT 枚举 + 25 s 空载稳定性测试` | 01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:190 | 4 |
| 89 | `python s5_ble.py read <uuid>  # 读指定特征` | 01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:192 | 4 |
| 90 | `python s5_ble.py scan 25      # 扫描，高亮 Panasonic/LUMIX 广播` | 01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:189 | 4 |
| 91 | `python s5_ble.py session      # 空闲测试 → 读 idx35(INITIAL_INFORM) → idx5(SSID) → idx6(密码)` | 01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:191 | 4 |
| 92 | `python updtool.py diff  S5m2_V37.bin -r test.bin` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:328 | 1 |
| 93 | `python updtool.py setver S5m2_V37.bin 3.7.5 -o test.bin` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:327 | 1 |
| 94 | `python3` | 14_总包审计与新方向_20261014/00_审计总报告.md:621<br>14_总包审计与新方向_20261014/06_密码学重跑/结论.md:393<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md:621<br>（另 1 处） | 4 |
| 95 | `python3 - <<'EOF'` | 12_S5无线监看_v1.0_20261014/README.md:384 | 2 |
| 96 | `python3 - <<'PY'` | 14_总包审计与新方向_20261014/00_审计总报告.md:114<br>14_总包审计与新方向_20261014/00_审计总报告.md:173<br>14_总包审计与新方向_20261014/00_审计总报告.md:362<br>（另 15 处） | 25 |
| 97 | `python3 -c "` | 13_USB服务通道勘察_交接包_20261014/02_工具/README.md:85<br>14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:199<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:199 | 4 |
| 98 | `python3 -c "print(0x60ed)"                     # → 24813` | 19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:453 | 1 |
| 99 | `python3 -c "print(bytes.fromhex('584a4c####################').decode())"` | 14_总包审计与新方向_20261014/00_审计总报告.md:426<br>14_总包审计与新方向_20261014/02_全包查看指令手册.md:219<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md:426 | 4 |
| 100 | `python3 01-固件格式与启动/boot_analysis.py` | 01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:259 | 6 |
| 101 | `python3 01-固件格式与启动/boot_deep.py` | 01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:260 | 6 |
| 102 | `python3 01-固件格式与启动/decrypt_attempt.py` | 01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:262 | 6 |
| 103 | `python3 01-固件格式与启动/decrypt_attempt2.py` | 01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:263 | 6 |
| 104 | `python3 01-固件格式与启动/scan_verify.py` | 01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:261 | 6 |
| 105 | `python3 02_工具与脚本/cam_cgi/persist.py verify demo` | 00_项目总结/05_环境与依赖.md:107 | 2 |
| 106 | `python3 04_工具与脚本/ptp/s5_ptp_dump.py --help    # 先看用法` | 14_总包审计与新方向_20261014/03_新方向与实验设计.md:498 | 2 |
| 107 | `python3 analysis/compare_versions.py` | 01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_解码突破记录.md:146<br>01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件逆向_阶段结果汇总.md:309 | 6 |
| 108 | `python3 analysis/extract_gh2_control.py` | 01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_解码突破记录.md:145<br>01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件逆向_阶段结果汇总.md:308 | 6 |
| 109 | `python3 analysis/inspect_firmware.py` | 01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件逆向_阶段结果汇总.md:305 | 3 |
| 110 | `python3 analysis/inspect_oss_sources.py` | 01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件逆向_阶段结果汇总.md:307 | 3 |
| 111 | `python3 analysis/probe_encoding.py` | 01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件逆向_阶段结果汇总.md:306 | 3 |
| 112 | `python3 boot_analysis.py    # 48 条目表、load 排序、逐分区熵/魔数/字符串、S5m2 对比（注：样本为 ZIP，对比无效）` | 01_研究报告/02_研究总报告_20261011/research/BOOT_FLOW.md:171 | 7 |
| 113 | `python3 boot_deep.py        # IV 线性拟合（否）、loader1 head28=表尾（是）、AES key=field32 解密测试（否）、sha32 候选源（否）` | 01_研究报告/02_研究总报告_20261011/research/BOOT_FLOW.md:172 | 7 |
| 114 | `python3 campaign.py --ip 192.168.x.x --phase A-G --out-dir out` | 04_工具与脚本/campaign2/README.md:59 | 2 |
| 115 | `python3 camset_write_test.py` | 01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:269 | 6 |
| 116 | `python3 check_style.py testdata/frame.jpg` | 15_LUT烧录工具_20261014/README.md:120<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:120 | 2 |
| 117 | `python3 container_switch.py mov       # 切回声明档，菜单恢复` | 01_研究报告/09_S1H参考包分析_mp4ed_20261013.md:100 | 4 |
| 118 | `python3 container_switch.py mov --persist     # 0x5e=0x06（声明档），菜单恢复` | 01_研究报告/09_S1H参考包分析_mp4ed_20261013.md:91 | 4 |
| 119 | `python3 container_switch.py mp4ed     # 进入 MP4(LPCM) 1080p60（菜单会变灰，属预期）` | 01_研究报告/09_S1H参考包分析_mp4ed_20261013.md:99 | 4 |
| 120 | `python3 container_switch.py status    # 只读查看 live + flash` | 01_研究报告/09_S1H参考包分析_mp4ed_20261013.md:101 | 4 |
| 121 | `python3 ecdsa_recover.py --root <项目根> --profile all --deep --exhaustive \<br>--json out_full.json` | 14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:314<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:314 | 2 |
| 122 | `python3 ecdsa_recover.py --root <项目根> --profile core --json out_core.json` | 14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:311<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:311 | 2 |
| 123 | `python3 ecdsa_recover.py --root <项目根> --profile none --exhaustive --mode recover` | 14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:318<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:318 | 2 |
| 124 | `python3 ecdsa_recover.py /path/S5___V29.bin /path/S5___V24.bin /path/S5___V23.bin \<br>/path/S5___V20.bin /path/S5___V11.bin` | 14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:332<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:332 | 2 |
| 125 | `python3 enum_videoquality.py --confirm` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md:134 | 3 |
| 126 | `python3 exp1_record_sha.py              # 记录 SHA 语义（48 分区 × 2 偏移）` | 14_总包审计与新方向_20261014/06_密码学重跑/结论.md:387<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/06_密码学重跑/结论.md:387 | 2 |
| 127 | `python3 exp2_known_plaintext_mode.py    # 已知明文 / keystream / CBC-vs-CTR` | 14_总包审计与新方向_20261014/06_密码学重跑/结论.md:388<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/06_密码学重跑/结论.md:388 | 2 |
| 128 | `python3 exp3_cross_version.py           # V29 vs V24（+V11/V20/V23）跨版本一致性` | 14_总包审计与新方向_20261014/06_密码学重跑/结论.md:389<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/06_密码学重跑/结论.md:389 | 2 |
| 129 | `python3 exp4_positive_control.py        # ★ 阳性对照（约 30 秒）` | 14_总包审计与新方向_20261014/06_密码学重跑/结论.md:390<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/06_密码学重跑/结论.md:390 | 2 |
| 130 | `python3 experiment_mov_shadow.py --confirm       # 分块写入 3062..3074 = mov` | 01_研究报告/07_隐藏格式持久化_追查_20261013.md:133 | 4 |
| 131 | `python3 experiment_mov_shadow.py --dry-run       # 离线自检` | 01_研究报告/07_隐藏格式持久化_追查_20261013.md:132 | 4 |
| 132 | `python3 experiment_mov_shadow.py --dry-run     # 离线自检：只对本地 blob 演算，不碰相机` | 16_S5_核心总包_20261015/README.md:140<br>README.md:141 | 2 |
| 133 | `python3 g100_blscan3.py      # 调用者全表` | 18_G100明文与同类项目_20261015/G100反编译_深挖报告.md:336 | 2 |
| 134 | `python3 g100_dtb.py          # dtb 要点` | 18_G100明文与同类项目_20261015/G100反编译_深挖报告.md:335 | 2 |
| 135 | `python3 g100_parse.py        # 节表 + 映射验证` | 18_G100明文与同类项目_20261015/G100反编译_深挖报告.md:333 | 2 |
| 136 | `python3 g100_strings.py      # 关键词零命中 + panasonic 48 处定位` | 18_G100明文与同类项目_20261015/G100反编译_深挖报告.md:334 | 2 |
| 137 | `python3 hidden_features.py 6kphoto    # 配置 6K PHOTO（片门全开）` | 01_研究报告/12_可写设置面审计_20261013.md:57 | 4 |
| 138 | `python3 hidden_features.py lpcm       # 切 MP4+LPCM（菜单会灰）` | 01_研究报告/12_可写设置面审计_20261013.md:58 | 4 |
| 139 | `python3 hidden_features.py restore    # 恢复 standard / mov / mov_60p_150mbps_c4k` | 01_研究报告/12_可写设置面审计_20261013.md:59 | 4 |
| 140 | `python3 hidden_features.py status     # 只读：关键隐藏项当前值` | 01_研究报告/12_可写设置面审计_20261013.md:55 | 4 |
| 141 | `python3 hidden_features.py vlog       # 开 V-Log` | 01_研究报告/12_可写设置面审计_20261013.md:56 | 4 |
| 142 | `python3 hidden_test_hlg.py` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md:104 | 3 |
| 143 | `python3 hidden_test_hlg.py       # 需相机在【照片】模式` | 01_研究报告/03_隐藏格式_可分发版_20261012/README.md:77 | 3 |
| 144 | `python3 hidden_test_mp4hevc.py` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md:122 | 3 |
| 145 | `python3 hidden_test_mp4hevc.py   # 需相机在【视频/录像】模式` | 01_研究报告/03_隐藏格式_可分发版_20261012/README.md:78 | 3 |
| 146 | `python3 http_fingerprint.py` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md:82 | 3 |
| 147 | `python3 http_fingerprint.py     # 服务器指纹（只读）` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md:81 | 3 |
| 148 | `python3 make_lut.py --from vlog  --size 17 --formats vlt  --out /Volumes/LUMIX/   # 给机身` | 15_LUT烧录工具_20261014/README.md:55<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:55 | 2 |
| 149 | `python3 make_lut.py --from vlog  --size 33 --formats cube --out lut/               # 给后期` | 15_LUT烧录工具_20261014/README.md:56<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:56 | 2 |
| 150 | `python3 make_lut.py --selftest                                                      # 只跑自检` | 15_LUT烧录工具_20261014/README.md:57<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:57 | 2 |
| 151 | `python3 mode_enum.py` | 01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:271 | 6 |
| 152 | `python3 opengate_recon.py` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md:75 | 3 |
| 153 | `python3 opengate_recon.py    # 6K PHOTO / 隐藏 setter` | 01_研究报告/03_隐藏格式_可分发版_20261012/README.md:71 | 3 |
| 154 | `python3 persist.py restore --confirm` | 01_研究报告/04_隐藏格式_持久化成果.md:61<br>04_工具与脚本/campaign2/隐藏格式持久化_成果_副本.md:58 | 8 |
| 155 | `python3 persist.py restore --confirm           # 一键恢复隐藏格式（需 AC 供电）` | 16_S5_核心总包_20261015/README.md:129<br>README.md:130 | 2 |
| 156 | `python3 persist.py verify` | 01_研究报告/04_隐藏格式_持久化成果.md:58<br>04_工具与脚本/campaign2/隐藏格式持久化_成果_副本.md:55<br>16_S5_核心总包_20261015/README.md:132<br>（另 1 处） | 10 |
| 157 | `python3 persist.py verify                        # 只读：健康 + 实时 + blob 三字段` | 01_研究报告/07_隐藏格式持久化_追查_20261013.md:131 | 4 |
| 158 | `python3 persist.py verify                        # 拔电池重启后再跑，判定是否持久` | 01_研究报告/07_隐藏格式持久化_追查_20261013.md:136 | 4 |
| 159 | `python3 persist.py verify                      # 只读，随时可跑` | 01_研究报告/04_隐藏格式_持久化成果.md:98 | 6 |
| 160 | `python3 persist.py verify                     # 只读安全：健康 + 实时 + blob 三字段` | 16_S5_核心总包_20261015/README.md:126<br>README.md:127 | 2 |
| 161 | `python3 persist_quality.py <quality_name>            # 改质量（RAM），先校验 allmenu 是否声明` | 01_研究报告/07_隐藏格式持久化_追查_20261013.md:134 | 4 |
| 162 | `python3 persist_quality.py <quality_name> --confirm  # 并把质量固化到 flash` | 01_研究报告/07_隐藏格式持久化_追查_20261013.md:135 | 4 |
| 163 | `python3 programs/lumix_hidden_format.py activate --ip 192.168.2.107 --model S1H --token mp4ed_25p_400mbps_4k_10bit --write --accept-secondary-change` | 01_研究报告/05_Panasonic_hidden_format_参考/README.md:32<br>01_研究报告/05_Panasonic_hidden_format_参考/复现操作手册.md:39 | 4 |
| 164 | `python3 programs/lumix_hidden_format.py activate --ip 192.168.2.107 --model S5 --token 本机已启用的token --write --experimental-s5 --accept-secondary-change` | 01_研究报告/05_Panasonic_hidden_format_参考/复现操作手册.md:45 | 2 |
| 165 | `python3 programs/lumix_hidden_format.py inspect --ip 192.168.2.107 --model S1H` | 01_研究报告/05_Panasonic_hidden_format_参考/README.md:24<br>01_研究报告/05_Panasonic_hidden_format_参考/复现操作手册.md:17 | 4 |
| 166 | `python3 programs/lumix_hidden_format.py inspect --ip 192.168.2.107 --model S5` | 01_研究报告/05_Panasonic_hidden_format_参考/复现操作手册.md:23 | 2 |
| 167 | `python3 programs/lumix_hidden_format.py restore --ip 192.168.2.107 --model S1H --journal captures/某次时间/restore_journal.json --write` | 01_研究报告/05_Panasonic_hidden_format_参考/README.md:44 | 2 |
| 168 | `python3 programs/lumix_hidden_format.py restore --ip 192.168.2.107 --model S5 --journal captures/本次目录/restore_journal.json --write` | 01_研究报告/05_Panasonic_hidden_format_参考/复现操作手册.md:94 | 2 |
| 169 | `python3 programs/verify_recording.py /完整路径/测试文件.MP4 --output media_check_01` | 01_研究报告/05_Panasonic_hidden_format_参考/复现操作手册.md:72 | 2 |
| 170 | `python3 rce_surface_probe.py` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md:89 | 3 |
| 171 | `python3 rce_surface_probe.py    # mode / getinfo 子类型 RCE 面枚举（只读）` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md:82 | 3 |
| 172 | `python3 rce_surface_probe.py # RCE 面枚举` | 01_研究报告/03_隐藏格式_可分发版_20261012/README.md:72 | 3 |
| 173 | `python3 recon.py` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md:68 | 3 |
| 174 | `python3 recon.py                # 设置面（47 可写域）+ camcmd 词表（只读）` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md:83 | 3 |
| 175 | `python3 recon.py             # 设置面 + camcmd 词表` | 01_研究报告/03_隐藏格式_可分发版_20261012/README.md:70 | 3 |
| 176 | `python3 rsa_modulus.py  /path/S5___V29.bin /path/S5___V24.bin /path/S5___V23.bin \<br>/path/S5___V20.bin /path/S5___V11.bin --e 3,17` | 14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:334<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:334 | 2 |
| 177 | `python3 rsa_modulus.py --root <项目根> --profile all --e 3,5,7,17,257 \<br>--budget 0 --json rsa_small_e.json` | 14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:321<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:321 | 2 |
| 178 | `python3 rsa_modulus.py --root <项目根> --profile all --e 65537 \<br>--max-cands-65537 24 --pads p15_di --budget 0 --json rsa_65537.json` | 14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:325<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:325 | 2 |
| 179 | `python3 s5_content.py cleanup --cam 192.168.1.131` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:336 | 1 |
| 180 | `python3 s5_content.py cleanup --cam 192.168.1.131   # 清理陈旧 pending（解决"需要更新app"）` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:326 | 1 |
| 181 | `python3 s5_content.py cleanup --cam 192.168.x.x` | 16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:336 | 1 |
| 182 | `python3 s5_content.py cleanup --cam 192.168.x.x   # 清理陈旧 pending（解决"需要更新app"）` | 16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:326 | 1 |
| 183 | `python3 s5_content.py diagnose --cam 192.168.1.131` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:339 | 1 |
| 184 | `python3 s5_content.py diagnose --cam 192.168.1.131  # 全因素诊断（含 ok 门判读）` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:327 | 1 |
| 185 | `python3 s5_content.py diagnose --cam 192.168.x.x` | 16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:339 | 1 |
| 186 | `python3 s5_content.py diagnose --cam 192.168.x.x  # 全因素诊断（含 ok 门判读）` | 16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:327 | 1 |
| 187 | `python3 s5_content.py list    --cam 192.168.1.131   # 列举内容` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:329 | 1 |
| 188 | `python3 s5_content.py list    --cam 192.168.x.x   # 列举内容` | 16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:329 | 1 |
| 189 | `python3 s5_content.py list --cam 192.168.1.131` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:345 | 1 |
| 190 | `python3 s5_content.py list --cam 192.168.x.x` | 16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:345 | 1 |
| 191 | `python3 s5_content.py probe --cam 192.168.54.1       # DLNA 三层判定` | 16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/README.md:120 | 1 |
| 192 | `python3 s5_content.py sweep   --cam 192.168.1.131   # 已放行后扫 ObjectID` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:328 | 1 |
| 193 | `python3 s5_content.py sweep   --cam 192.168.x.x   # 已放行后扫 ObjectID` | 16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:328 | 1 |
| 194 | `python3 s5_content.py sweep --cam 192.168.1.131` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:303<br>14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:342 | 2 |
| 195 | `python3 s5_content.py sweep --cam 192.168.x.x` | 16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:303<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:342 | 2 |
| 196 | `python3 s5_get_photo.py                              # 一键取片（老入口，保留）` | 16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/README.md:119 | 1 |
| 197 | `python3 s5_get_photo.py                # 取最新一张并套 LUT` | 12_S5无线监看_v1.0_20261014/README.md:417 | 2 |
| 198 | `python3 s5_get_photo.py --index 0      # 取第 0 张` | 12_S5无线监看_v1.0_20261014/README.md:420 | 2 |
| 199 | `python3 s5_get_photo.py --no-lut       # 只下载` | 12_S5无线监看_v1.0_20261014/README.md:419 | 2 |
| 200 | `python3 s5_get_photo.py --shoot        # 先拍一张再取` | 12_S5无线监看_v1.0_20261014/README.md:418 | 2 |
| 201 | `python3 s5_quality.py set <质量名>              # 带重试与回读校验` | 16_S5_核心总包_20261015/README.md:136<br>README.md:137 | 2 |
| 202 | `python3 s5_quality.py status                   # 当前状态 + 菜单安全性判定` | 16_S5_核心总包_20261015/README.md:135<br>README.md:136 | 2 |
| 203 | `python3 s5_selfcheck.py                              # 自检（自动找相机）` | 16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/README.md:121 | 1 |
| 204 | `python3 s5_transfer.py get   --cam <IP> --newest --lut "xxx.cube" --base vlog_to_709_33.cube` | 00_调用前必查_已跑通路径总索引.md:36 | 1 |
| 205 | `python3 s5_transfer.py get  --cam 192.168.54.1 --all-videos   # 拉全部视频（带进度）` | 16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/README.md:114 | 1 |
| 206 | `python3 s5_transfer.py get  --cam 192.168.54.1 --newest \<br>--lut "VOL19 TXD GLOD 200T V2.cube" --base vlog_to_709_33.cube  # 最新照片+套LUT` | 16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/README.md:115 | 1 |
| 207 | `python3 s5_transfer.py list  --cam <IP>            # 列举（照片/视频）` | 00_调用前必查_已跑通路径总索引.md:35 | 1 |
| 208 | `python3 s5_transfer.py list --cam 192.168.54.1      # 列举照片/视频` | 16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/README.md:113 | 1 |
| 209 | `python3 s5_transfer.py watch --cam 192.168.54.1 \<br>--lut "VOL12 TXD FUJI NC P.cube" --base vlog_to_709_33.cube     # 新照片一出现就下载+套LUT` | 16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/README.md:117 | 1 |
| 210 | `python3 s5_transfer.py watch --cam <IP> --lut "xxx.cube"   # 新照片自动下载+套LUT` | 00_调用前必查_已跑通路径总索引.md:37 | 1 |
| 211 | `python3 s5monitor.py                      # 默认 192.168.54.1` | 04_工具与脚本/s5_monitor/README.md:70 | 3 |
| 212 | `python3 s5monitor.py --host 192.168.1.131 --device-name "LUMIX Sync"` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:223 | 1 |
| 213 | `python3 s5monitor.py --host 192.168.54.1            # 监看（默认）` | 16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/README.md:112 | 1 |
| 214 | `python3 s5monitor.py --host 192.168.x.x # 家庭网` | 04_工具与脚本/s5_monitor/README.md:71 | 3 |
| 215 | `python3 s5monitor.py --host 192.168.x.x --device-name "LUMIX Sync"` | 16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:223 | 1 |
| 216 | `python3 s5monitor.py --host 192.168.x.x --pacing-mode fixed --pacing-fps 18` | 04_工具与脚本/s5_monitor/README.md:420 | 3 |
| 217 | `python3 s5monitor.py --keepalive 0    # 约 13 秒后停流` | 04_工具与脚本/s5_monitor/README.md:220 | 3 |
| 218 | `python3 s5monitor.py --keepalive 10   # 默认，稳定` | 04_工具与脚本/s5_monitor/README.md:221 | 3 |
| 219 | `python3 s5monitor.py --no-stream          # 只起控制台，不自动取景` | 04_工具与脚本/s5_monitor/README.md:72 | 3 |
| 220 | `python3 s5probe.py --label "基线（未改任何设置）"` | 04_工具与脚本/s5_monitor/设置枚举测试计划.md:28 | 3 |
| 221 | `python3 s5probe.py --report` | 04_工具与脚本/s5_monitor/设置枚举测试计划.md:84 | 3 |
| 222 | `python3 safe_handshake.py --ip $S5_IP --verify` | 01_研究报告/03_隐藏格式_可分发版_20261012/README.md:64<br>01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md:58 | 6 |
| 223 | `python3 safe_handshake.py --ip 192.168.x.x` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/01_版本门与握手修复.md:65 | 3 |
| 224 | `python3 safe_handshake.py --ip 192.168.x.x --polls 6 --poll-delay 2.5` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/01_版本门与握手修复.md:66 | 3 |
| 225 | `python3 safe_handshake.py --ip 192.168.x.x --verify   # 成功后只读回读确认` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/01_版本门与握手修复.md:67 | 3 |
| 226 | `python3 selftest_synthetic.py` | 14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:308<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:308 | 2 |
| 227 | `python3 state_check.py --ip $S5_IP` | 01_研究报告/03_隐藏格式_可分发版_20261012/README.md:57<br>01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md:43 | 6 |
| 228 | `python3 tools/dis.py 0x04a8d0 0x04a910      # 0x04a720 → 0x05b084` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:385 | 1 |
| 229 | `python3 tools/dis.py 0x0e969c 0x0e9794         # writeSize/addSize/bufferSize` | 19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:446 | 1 |
| 230 | `python3 tools/dis.py 0x0e9794 0x0e99f0         # 转义追加（逐字符记账）` | 19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:447 | 1 |
| 231 | `python3 tools/dis.py 0x0e9ab0 0x0e9dbc         # 第二份实例` | 19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:448 | 1 |
| 232 | `python3 tools/dis.py 0x4b734 0x4ba30           # 词法切分器（含边界检查）` | 19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:439 | 1 |
| 233 | `python3 tools/dis.py 0x54078 0x541d0           # UTF-16 转码（恰好填满）` | 19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:449 | 1 |
| 234 | `python3 tools/dis.py 0x54c40 0x54e00           # 展开器（memset 6400）` | 19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:440 | 1 |
| 235 | `python3 tools/dis.py 0x55778 0x55860           # 词法展开器` | 19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:441 | 1 |
| 236 | `python3 tools/dis.py 0x928b4 0x92ae4` | 19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:489 | 1 |
| 237 | `python3 tools/dis.py 0x92ae4 0x92c30` | 19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:488 | 1 |
| 238 | `python3 tools/dis.py 0x938c0 0x939e8` | 19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:493 | 1 |
| 239 | `python3 tools/dis.py 0x95e4c 0x95f40` | 19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:492 | 1 |
| 240 | `python3 tools/dis.py 0xaf958 0xafd54        # 厘清 (ctx, ?, n, out...) 的参数语义` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:193 | 1 |
| 241 | `python3 tools/dis.py 0xafa3c 0xafd30` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:528 | 1 |
| 242 | `python3 tools/dis.py 0xba574 0xba6f8           # ★ E23：%ld 进 4B 缓冲` | 19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:442 | 1 |
| 243 | `python3 tools/dis.py 0xd6560 0xd66e8        # Range 零拷贝` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:375 | 1 |
| 244 | `python3 tools/dis.py 0xd69b8 0xd6aa8` | 19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:499 | 1 |
| 245 | `python3 tools/dis.py 0xdb8e4 0xdb9c0        # 入口闸门 strlen<260` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:376 | 1 |
| 246 | `python3 tools/dis.py 0xdbd00 0xdbd40        # ★ Branch A: strcpy(node+0x114, src)` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:377 | 1 |
| 247 | `python3 tools/dis.py 0xdbd54 0xdbde0        # Branch B: 恰好填满` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:378 | 1 |
| 248 | `python3 tools/dis.py 0xe7f40 0xe7f90        # CreateObject 的 Elements → 0x04a720` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:384 | 1 |
| 249 | `python3 tools/dis.py 0xefef0 0xeffa0        # 看 fp-1328 起这块局部区被写入了什么` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:194 | 1 |
| 250 | `python3 tools/dis.py 0xf1a20 0xf1a60        # ★ 证据 A: strncpy(&buf[0x114], src, 80)` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:379 | 1 |
| 251 | `python3 tools/dis.py 0xf1d00 0xf1d40        # strcpy 源 = fp-0x530（260B 缓冲 +148）` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:381 | 1 |
| 252 | `python3 tools/dis.py 0xf1fa0 0xf1fd0        # ★ 证据 B: strncpy(dst, &buf[0x114], 80)` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:380 | 1 |
| 253 | `python3 tools/dis.py 0xf4bbc 0xf4d00        # 闸门 strlen≤127 + memset 128 + strcpy` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:369 | 1 |
| 254 | `python3 tools/dis.py 0xf4d00 0xf4f90        # 4 段 strtoul 的范围检查` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:370 | 1 |
| 255 | `python3 tools/sites.py 0xd66e8 0xd7b2c` | 19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:496 | 1 |
| 256 | `python3 tools/sites.py 0xe7d30 0xe95a0` | 19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:53 | 1 |
| 257 | `python3 tools/sites.py 0xe7d30 0xe95a0         # → total sites: 0` | 19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:438 | 1 |
| 258 | `python3 tools/strsrc.py 0x5b3e8 0x5b680     # UPP_AV_XML_Dec_Xml 的 u16XMLType 串` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:386 | 1 |
| 259 | `python3 tools/strsrc.py 0xd20f0 0xd26bc        # 设备描述生成器全部源串` | 19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:434 | 1 |
| 260 | `python3 tools/strsrc.py 0xd26bc 0xd2f7c        # SCPD 生成器全部源串` | 19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:433 | 1 |
| 261 | `python3 tools/strsrc.py 0xe6274 0xe6cc0        # SOAP 动作分派器` | 19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:435 | 1 |
| 262 | `python3 tools/table.py 0x100c8c 0x100d34 4` | 19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:482 | 1 |
| 263 | `python3 tools/table.py 0x11e020 0x11e300 4     # ★ 锁死 arg0 取值域的静态表` | 19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:443 | 1 |
| 264 | `python3 tools/table.py 0x12068c 0x120790 4` | 19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:485 | 1 |
| 265 | `python3 tools/table.py 0xd2d04 0xd2d70 4` | 19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:452 | 1 |
| 266 | `python3 tools/table.py 0xf4f90 0xf4f94 4    # 常量 0x1869F = 99999` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:371 | 1 |
| 267 | `python3 tools/xr.py 0x100c8c 0x1047cc 0x100b8c` | 19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:502 | 1 |
| 268 | `python3 upd_table.py                    # [闸门] 判决实验，必须 7/7，否则后面的都无效` | 14_总包审计与新方向_20261014/06_密码学重跑/结论.md:386<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/06_密码学重跑/结论.md:386 | 2 |
| 269 | `python3 upd_table.py "/path/to/S5___V29.bin"` | 14_总包审计与新方向_20261014/06_密码学重跑/结论.md:397<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/06_密码学重跑/结论.md:397 | 2 |
| 270 | `python3 upload.py --ip 192.168.x.x --phase I --confirm --out-dir out` | 04_工具与脚本/campaign2/README.md:61 | 2 |
| 271 | `python3 upload.py --ip 192.168.x.x --phase I --ver-field inner --confirm --out-dir out` | 04_工具与脚本/campaign2/README.md:63 | 2 |
| 272 | `python3 upload.py --ip 192.168.x.x --phase J --data-flip 0x5600000 --confirm --out-dir out` | 04_工具与脚本/campaign2/README.md:65 | 2 |
| 273 | `python3 upload_test.py --ip 192.168.1.131 --bin ../fw_fetch/S5___V29.bin --phase 0` | 03_解包_APK/com.panasonic.jp.lumixsync/oracle/README.md:53 | 1 |
| 274 | `python3 upload_test.py --ip 192.168.1.131 --bin ../fw_fetch/S5___V29.bin --phase 1 --field 0x24` | 03_解包_APK/com.panasonic.jp.lumixsync/oracle/README.md:59 | 1 |
| 275 | `python3 upload_test.py --ip 192.168.1.131 --bin ../fw_fetch/S5___V29.bin --phase 2 --field 0x24 --confirm-risky` | 03_解包_APK/com.panasonic.jp.lumixsync/oracle/README.md:63 | 1 |
| 276 | `python3 upload_test.py --ip 192.168.1.131 --bin ../fw_fetch/S5___V29.bin --phase 3 --field 0x24 --partition zboot --confirm-risky` | 03_解包_APK/com.panasonic.jp.lumixsync/oracle/README.md:67 | 1 |
| 277 | `python3 upload_test.py --ip 192.168.x.x --bin ../../01-固件格式与启动/S5___V29.bin --phase 0` | 01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:267 | 6 |
| 278 | `python3 upload_test.py --ip 192.168.x.x --bin ../fw_fetch/S5___V29.bin --phase 0` | 01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:53 | 3 |
| 279 | `python3 upload_test.py --ip 192.168.x.x --bin ../fw_fetch/S5___V29.bin --phase 1 --field 0x24` | 01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:59 | 3 |
| 280 | `python3 upload_test.py --ip 192.168.x.x --bin ../fw_fetch/S5___V29.bin --phase 2 --field 0x24 --confirm-risky` | 01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:63 | 3 |
| 281 | `python3 upload_test.py --ip 192.168.x.x --bin ../fw_fetch/S5___V29.bin --phase 3 --field 0x24 --partition zboot --confirm-risky` | 01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:67 | 3 |
| 282 | `python3 watch_bake.py --lut lut/vlog_to_709_17.vlt \<br>--src /Volumes/LUMIX/DCIM --out ~/Pictures/LUT_baked` | 15_LUT烧录工具_20261014/README.md:44<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:44 | 2 |
| 283 | `python3 watch_bake.py --lut lut/vlog_to_709_17.vlt --src /Volumes/LUMIX/DCIM --out ~/Pictures/LUT_baked` | 15_LUT烧录工具_20261014/README.md:101<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:101 | 2 |
| 284 | `python3 watch_bake.py --lut lut/vlog_to_709_17.vlt --src ~/Downloads/LUMIX --out ~/Pictures/LUT_baked` | 15_LUT烧录工具_20261014/README.md:104<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:104 | 2 |
| 285 | `python3 watch_bake.py ... --once` | 15_LUT烧录工具_20261014/README.md:107<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:107 | 2 |
| 286 | `python3 wifi_lut.py list  --cam 192.168.1.131` | 15_LUT烧录工具_20261014/README.md:269 | 1 |
| 287 | `python3 wifi_lut.py list  --cam 192.168.x.x` | 16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:269 | 1 |
| 288 | `python3 wifi_lut.py probe --cam 192.168.1.131` | 15_LUT烧录工具_20261014/README.md:266 | 1 |
| 289 | `python3 wifi_lut.py probe --cam 192.168.x.x` | 16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:266 | 1 |
| 290 | `python3 wifi_lut.py watch --cam 192.168.1.131 --lut lut/vlog_to_709_17.vlt --out ~/Pictures/LUT_baked` | 15_LUT烧录工具_20261014/README.md:272 | 1 |
| 291 | `python3 wifi_lut.py watch --cam 192.168.x.x --lut lut/vlog_to_709_17.vlt --out ~/Pictures/LUT_baked` | 16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:272 | 1 |
| 292 | `recover.py -r <ref...>` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:353 | 1 |
| 293 | `recover.py <enc.bin> [-r ref...] [-o dir] [--list]` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:388 | 1 |
| 294 | `recover.py GX9__V15.bin -o <dir>` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:322 | 1 |
| 295 | `s5probe.py --label "<改了什么>"` | 04_工具与脚本/s5_monitor/设置枚举测试计划.md:39 | 3 |
| 296 | `safe_handshake.py --verify` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md:161<br>01_研究报告/03_隐藏格式_可分发版_20261012/docs/06_安全约束与风险.md:35 | 6 |
| 297 | `tools/analysis/*.py` | 01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:27 | 3 |
| 298 | `updtool.py decrypt --key` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:129 | 1 |
| 299 | `updtool.py decrypt --key <hex>` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:354 | 1 |
| 300 | `updtool.py list S5m2_V37.bin` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:33 | 1 |
| 301 | `xver_fixed.py / keyhunt2.py / ks_extract.py / exp_cipher.py / parse_upd.py / verify_sha.py` | 01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:621 | 3 |

### C. USB / PTP 工具（s5_ptp_dump、s5_usb_*、ImageCaptureCore、iOS 构建签名） —— 43 条

| # | 命令（原样） | 出处（规范路径:行号） | 出现次数 |
| --- | --- | --- | --- |
| 302 | `./.venv/bin/python tools/s5_ptp_dump.py            # 完整流程` | 01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:61 | 3 |
| 303 | `./.venv/bin/python tools/s5_ptp_dump.py --dry-run  # 打印 0x9421 命令字节（离线可跑）` | 01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:60 | 3 |
| 304 | `./.venv/bin/python tools/s5_ptp_dump.py --list     # 枚举` | 01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:59 | 3 |
| 305 | `./ble_scan 30` | 04_工具与脚本/TOOLS.md:98<br>04_工具与脚本/TOOLS_工具箱总览.md:70 | 4 |
| 306 | `./ble_scan 30        # 扫描 30 秒；命中 LUMIX 服务即自动连接并枚举 GATT` | 01_研究报告/14_蓝牙BLE勘察_20261013.md:91 | 4 |
| 307 | `./s5_ptp_dump ./ptp_out                 # 匹配任意相机，mode=dump（默认）` | 04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:95 | 7 |
| 308 | `./s5_ptp_dump ./ptp_out S5              # 只匹配名称含 "S5" 的相机，mode=dump（默认）` | 04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:96 | 7 |
| 309 | `./s5_ptp_dump ./ptp_out S5            # mode=dump：0x9421 全量配置` | 01_研究报告/02_研究总报告_20261011/07-USB-PTP-SCSI.md:58 | 3 |
| 310 | `./s5_ptp_dump ./ptp_out S5 fwup         # ★ mode=fwup：0x9605 固件升级状态机只读查询` | 04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:97 | 7 |
| 311 | `./s5_ptp_dump ./ptp_out S5 fwup       # mode=fwup：0x9605 升级状态机只读` | 01_研究报告/02_研究总报告_20261011/07-USB-PTP-SCSI.md:59 | 3 |
| 312 | `./s5_ptp_dump ./ptp_out_fuzz S5 fuzz    # ★ mode=fuzz：CVE 类只读探测（43 个安全探测，详见下文）` | 04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:98 | 7 |
| 313 | `./s5_ptp_dump ./ptp_out_fuzz S5 fuzz  # mode=fuzz：43 个安全只读探测` | 01_研究报告/02_研究总报告_20261011/07-USB-PTP-SCSI.md:60 | 3 |
| 314 | `./s5_ptp_dump ./ptp_out_lp S5 lenprobe  # ⚠ mode=lenprobe：受控 length-DoS 演示（最后运行）` | 04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:99 | 7 |
| 315 | `./s5_ptp_raw --list` | 04_工具与脚本/TOOLS_工具箱总览.md:89 | 2 |
| 316 | `./s5_ptp_raw ./ptp_raw_out` | 04_工具与脚本/TOOLS_工具箱总览.md:90 | 2 |
| 317 | `./s5_usb_desc --list` | 13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md:220 | 2 |
| 318 | `./s5_usb_desc [--list] [vid] [pid] [--strings N] [--no-open]` | 13_USB服务通道勘察_交接包_20261014/02_工具/README.md:23 | 2 |
| 319 | `./s5_usb_ep0 [vid] [pid] [--max N] [--types 80,c0,c1,c2]` | 13_USB服务通道勘察_交接包_20261014/02_工具/README.md:59 | 2 |
| 320 | `./s5_usb_listen [秒数] [vid] [pid] [--ptp] [--tryall] [--hex <hex串>] [--cfg N]` | 13_USB服务通道勘察_交接包_20261014/02_工具/README.md:39 | 2 |
| 321 | `./scripts/build_ipa.sh            # 输出 dist/LumixFast.ipa` | 05_源码/LumixFast-iOS/README.md:94 | 2 |
| 322 | `./tools/s5_ptp_dump ./ptp_out S5          # 0x9421 全量配置 dump` | 01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:53 | 3 |
| 323 | `./tools/s5_ptp_dump ./ptp_out S5 fwup     # 0x9605 升级状态机只读查询` | 01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:54 | 3 |
| 324 | `./tools/s5_ptp_dump ./ptp_out_fuzz S5 fuzz    # CVE 类只读探测（43 个安全探测，§9.3）` | 01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:55 | 3 |
| 325 | `./tools/s5_ptp_dump ./ptp_out_lp S5 lenprobe  # ⚠ 受控 length-DoS 演示（最后运行，需拔插恢复）` | 01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:56 | 3 |
| 326 | `./启动.command <相机IP>` | 16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/README.md:33 | 1 |
| 327 | `DEVELOPMENT_TEAM=XXXXXXXXXX ./scripts/sign_ipa.sh   # 输出 dist/LumixFast-signed.ipa` | 05_源码/LumixFast-iOS/README.md:97 | 2 |
| 328 | `Get-PnpDeviceProperty -InstanceId "USB\\VID_04DA&PID_2382\\..." -KeyName 'DEVPKEY_Device_Service'` | 01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:58 | 3 |
| 329 | `clang` | 00_项目总结/05_环境与依赖.md:26<br>00_项目总结/05_环境与依赖.md:28 | 4 |
| 330 | `clang -O2 -Wall -framework IOKit -framework CoreFoundation -o s5_usb_desc   s5_usb_desc.c` | 13_USB服务通道勘察_交接包_20261014/02_工具/README.md:11<br>13_USB服务通道勘察_交接包_20261014/README.md:56 | 4 |
| 331 | `clang -O2 -Wall -framework IOKit -framework CoreFoundation -o s5_usb_ep0    s5_usb_ep0.c` | 13_USB服务通道勘察_交接包_20261014/02_工具/README.md:13<br>13_USB服务通道勘察_交接包_20261014/README.md:58 | 4 |
| 332 | `clang -O2 -Wall -framework IOKit -framework CoreFoundation -o s5_usb_listen s5_usb_listen.c` | 13_USB服务通道勘察_交接包_20261014/02_工具/README.md:12<br>13_USB服务通道勘察_交接包_20261014/README.md:57 | 4 |
| 333 | `clang -framework Foundation -framework ImageCaptureCore -o s5_ptp_dump s5_ptp_dump.m` | 04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:88 | 7 |
| 334 | `clang -framework IOKit -framework CoreFoundation -o s5_ptp_raw s5_ptp_raw.c` | 00_项目总结/05_环境与依赖.md:116<br>04_工具与脚本/TOOLS_工具箱总览.md:88 | 4 |
| 335 | `d = usb.core.find(idVendor=0x04da, idProduct=0x2370)` | 13_USB服务通道勘察_交接包_20261014/02_工具/README.md:87 | 2 |
| 336 | `fastboot` | 18_G100明文与同类项目_20261015/ILCE7M4RE_借鉴分析.md:104<br>18_G100明文与同类项目_20261015/ILCE7M4RE_借鉴分析.md:140 | 4 |
| 337 | `lsusb` | 13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md:183 | 2 |
| 338 | `lsusb -v -d 04da:2370            # 含全部字符串描述符` | 13_USB服务通道勘察_交接包_20261014/02_工具/README.md:82 | 2 |
| 339 | `s5_ptp_dump` | 00_项目总结/00_执行摘要_全文.md:34<br>00_项目总结/01_成果总表.md:35<br>00_项目总结/05_环境与依赖.md:80<br>（另 13 处） | 53 |
| 340 | `s5_ptp_dump.py fuzz` | 01_研究报告/02_研究总报告_20261011/06-崩溃与DoS.md:33 | 3 |
| 341 | `swiftc` | 00_项目总结/05_环境与依赖.md:25<br>00_项目总结/05_环境与依赖.md:28 | 4 |
| 342 | `swiftc -O -module-cache-path "$PWD/.modcache" bake.swift -o bake` | 15_LUT烧录工具_20261014/README.md:202<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:202 | 2 |
| 343 | `swiftc -framework CoreBluetooth -framework Foundation -o ble_scan ble_scan.swift` | 00_项目总结/05_环境与依赖.md:114<br>01_研究报告/14_蓝牙BLE勘察_20261013.md:90<br>04_工具与脚本/TOOLS.md:97<br>（另 1 处） | 10 |
| 344 | `xcodegen generate          # 重新生成 LumixFast.xcodeproj` | 05_源码/LumixFast-iOS/README.md:84 | 2 |

### D. 交叉编译 / 固件构建（arm-none-eabi、make、cmake、stubby） —— 7 条

| # | 命令（原样） | 出处（规范路径:行号） | 出现次数 |
| --- | --- | --- | --- |
| 345 | `arm-none-eabi-gcc 16.2.0` | 18_SDDAT验证/T4_构建校准.md:10 | 2 |
| 346 | `arm-none-eabi-objdump -d -j .text` | 19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:5<br>19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:5 | 2 |
| 347 | `arm-none-eabi-objdump -d -j .text dlna > /tmp/dlna_audit/dlna_text.asm` | 19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:7 | 1 |
| 348 | `arm-none-eabi-objdump -d -j .text dlna > dlna_text.asm` | 19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:479 | 1 |
| 349 | `make <挂载点> <数量> <长度>` | 04_工具与脚本/TOOLS.md:42 | 2 |
| 350 | `make CONFIG=configs/config-sc2000-sddat.h CROSS=arm-none-eabi- CONCURRENT_MAKE=4` | 18_SDDAT验证/T4_构建校准.md:19 | 2 |
| 351 | `make_package.sh --with-firmware` | 01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:619 | 3 |

### E. 固件/镜像解析与二进制处理（unsquashfs、dd、xxd、binwalk、objdump、磁盘打包） —— 27 条

| # | 命令（原样） | 出处（规范路径:行号） | 出现次数 |
| --- | --- | --- | --- |
| 352 | `diskutil eraseVolume ExFAT LUMIX /dev/disk8s1` | 00_项目总结/04_定因与工具链成果_20261013.md:152<br>01_研究报告/24_相机长文件名崩溃_定因_20261013.md:70 | 6 |
| 353 | `diskutil eraseVolume ExFAT LUMIX /dev/diskN sM` | 01_研究报告/25_操作记录与风险手册_20261013.md:74<br>11_DC-S5成果包_20261013/01_研究报告_全集/25_操作记录与风险手册_20261013.md:74 | 4 |
| 354 | `diskutil info` | 01_研究报告/25_操作记录与风险手册_20261013.md:83<br>01_研究报告/26_本次运行日志_20261013.md:13<br>11_DC-S5成果包_20261013/01_研究报告_全集/25_操作记录与风险手册_20261013.md:83<br>（另 1 处） | 8 |
| 355 | `diskutil info /dev/diskNsM \| grep -E "Volume Name\|Disk Size\|File System Personality"` | 01_研究报告/25_操作记录与风险手册_20261013.md:55<br>11_DC-S5成果包_20261013/01_研究报告_全集/25_操作记录与风险手册_20261013.md:55 | 4 |
| 356 | `diskutil unmountDisk force /dev/diskN` | 01_研究报告/25_操作记录与风险手册_20261013.md:73<br>11_DC-S5成果包_20261013/01_研究报告_全集/25_操作记录与风险手册_20261013.md:73 | 4 |
| 357 | `nmap -sn` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md:32 | 3 |
| 358 | `objdump -d -j .text` | 19_路径1_Linux侧攻击面_20261015/dlna_audit/BRIEFING.md:20 | 1 |
| 359 | `shasum -a 256` | 16_S5_核心总包_20261015/00_本包说明_收录与排除.md:67<br>REPO_CONTENTS.md:110 | 3 |
| 360 | `shasum -a 256 "$S/getinfo_camsetting.bin" \<br>04_工具与脚本/campaign2/out/restore_payload_20261014_180310.bin \\ \<br>04_工具与脚本/campaign2/out/backup_pre_restore_20261014_180310.bin` | 14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:204<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:204 | 2 |
| 361 | `shasum -a 256 -c MANIFEST.sha256` | 16_S5_核心总包_20261015/00_本包说明_收录与排除.md:25 | 1 |
| 362 | `shasum -a 256 -c MANIFEST.sha256          # 校验全部（含未入库文件，缺失项会报 FAILED）` | REPO_CONTENTS.md:113 | 2 |
| 363 | `shasum -a 256 -c MANIFEST.sha256 \| grep FAILED` | 14_总包审计与新方向_20261014/00_审计总报告.md:338<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md:338 | 2 |
| 364 | `shasum -a 256 <文件>` | 16_S5_核心总包_20261015/02_固件指针/固件SHA256与下载来源.md:13 | 1 |
| 365 | `shasum -a 256 backup_pre_restore_20261014_175604.bin restore_payload_20261014_175604.bin` | 14_总包审计与新方向_20261014/00_审计总报告.md:92<br>14_总包审计与新方向_20261014/02_全包查看指令手册.md:168<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md:92 | 4 |
| 366 | `shasum -a 256 backup_pre_restore_20261014_180310.bin restore_payload_20261014_180310.bin` | 14_总包审计与新方向_20261014/00_审计总报告.md:93<br>14_总包审计与新方向_20261014/02_全包查看指令手册.md:169<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md:93 | 4 |
| 367 | `strings -n 5` | 14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:87<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:87 | 2 |
| 368 | `strings -n 8 02_固件二进制/DC-S5/S5___V29.bin \| grep -E "Linux version\|3\\.18\\.18\|V9AHD\|V10 SoC" \| head` | 14_总包审计与新方向_20261014/03_新方向与实验设计.md:326 | 2 |
| 369 | `unzip` | 00_项目总结/05_环境与依赖.md:64 | 2 |
| 370 | `unzip -l "$Z" \| head -20                          # 看条目结构` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:231 | 2 |
| 371 | `unzip -l/-p` | 14_总包审计与新方向_20261014/00_审计总报告.md:668<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md:668 | 2 |
| 372 | `unzip -p "$Z" "*/00_成果总结_全文.md" \| head -8    # 看是否含已撤回结论` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:232 | 2 |
| 373 | `unzip -p "$Z" "*/02_工具链/exfat/exfat_patch.py" \| sed -n '741,756p'  # 看是否是旧版分配器` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:233 | 2 |
| 374 | `unzip -p "09_exFAT越界写成果包_20261013/exfat越界包（有风险非专业人员请勿轻易尝试.zip" "*/00_成果总结_全文.md" \| head -8` | 14_总包审计与新方向_20261014/00_审计总报告.md:242<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md:242 | 2 |
| 375 | `unzip -p "09_exFAT越界写成果包_20261013/exfat越界包（有风险非专业人员请勿轻易尝试.zip" "*/02_工具链/exfat/exfat_patch.py" \| sed -n '741,756p'` | 14_总包审计与新方向_20261014/00_审计总报告.md:243<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md:243 | 2 |
| 376 | `zip -r ../08_总结与工具箱.zip .` | 08_总结与工具箱_20261013/README.md:29 | 1 |
| 377 | `zip -r ../09_exFAT越界写成果包.zip .` | 09_exFAT越界写成果包_20261013/README.md:35 | 1 |
| 378 | `zip -r ../10_定因与工具链成果包.zip .` | 10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/README.md:44 | 1 |

### F. 反汇编审计工具（19_路径1 tools/*、psm_audit/*、grep/awk 定位） —— 45 条

| # | 命令（原样） | 出处（规范路径:行号） | 出现次数 |
| --- | --- | --- | --- |
| 379 | `calls.py <start> <end>` | 19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:566 | 1 |
| 380 | `dump.py <addr> <n>` | 19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:564 | 1 |
| 381 | `graph.py callers\\\|callees <addr>` | 19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:565 | 1 |
| 382 | `grep '^\\./01_研究报告/' MANIFEST.sha256 \| shasum -a 256 -c   # 只校验已入库的某目录` | REPO_CONTENTS.md:114 | 2 |
| 383 | `grep -E "^VERSION\|^PATCHLEVEL\|^SUBLEVEL" 07_参考仓库/s5_oss_kernel/linux-3.18.18/Makefile` | 14_总包审计与新方向_20261014/03_新方向与实验设计.md:323 | 2 |
| 384 | `grep -L "\\-\\-confirm" 04_工具与脚本/campaign2/*.py \| head -20` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:356 | 2 |
| 385 | `grep -ln "doff" 04_工具与脚本/firmware_crypto/*.py     # 列出所有涉及 doff 的脚本` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:304 | 2 |
| 386 | `grep -n "0\\.0\\.0\\.0\\\|ALLOWED_CAMCMD\\\|ALLOWED_CAMCTRL\\\|def setsetting\\\|/api/setting\\\|def _get_recover" \<br>12_S5无线监看_v1.0_20261014/s5monitor.py` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:364 | 2 |
| 387 | `grep -n "584a4c32" 01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:218 | 2 |
| 388 | `grep -n "584a4c32\\\|MXD1D########" 01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md` | 14_总包审计与新方向_20261014/00_审计总报告.md:425<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md:425 | 2 |
| 389 | `grep -n "BENCH" 01_研究报告/02_研究总报告_20261011/logs/写路径/campaign.md \| head` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:186 | 2 |
| 390 | `grep -n "doff\\\|DATA_BASE\\\|0x200" 04_工具与脚本/firmware_crypto/parse_upd.py \| head` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:303 | 2 |
| 391 | `grep -n "endsenddata -> ok" 01_研究报告/02_研究总报告_20261011/logs/写路径/campaign.md \| head` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:187 | 2 |
| 392 | `grep -n "raw\\[.*off" 04_工具与脚本/firmware_crypto/verify_sha.py 04_工具与脚本/firmware_crypto/ks_extract.py` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:305 | 2 |
| 393 | `grep -n "勘误\\\|E1\\\|E2\\\|E3\\\|E4\\\|E5\\\|E6" 01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md \| head -30` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:282 | 2 |
| 394 | `grep -n -A25 "ConnectDevType" tether_2_12_ptp_arm64_disassembly.txt \| head -40` | 13_USB服务通道勘察_交接包_20261014/03_Tether协议线索.md:114 | 2 |
| 395 | `grep -nE "#0x2370" tether_2_12_ptp_arm64_disassembly.txt \|\| echo "无立即数命中（已确认）"` | 13_USB服务通道勘察_交接包_20261014/03_Tether协议线索.md:121 | 2 |
| 396 | `grep -nE "#0x2382\|#0x2374" tether_2_12_ptp_arm64_disassembly.txt` | 13_USB服务通道勘察_交接包_20261014/03_Tether协议线索.md:117 | 2 |
| 397 | `grep -nE "add\\s+r[0-9]+, r[0-9]+, #(712\|713)\\b" dlna_text.asm` | 19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:164 | 1 |
| 398 | `grep -nE "bl\\s+f4bbc <" dlna_text.asm       # 调用者 0xdf994/0xdfbd4/0xdfc9c ∈ 0xdf734` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:372 | 1 |
| 399 | `grep -nE "sub\\s+r[0-9]+, r[0-9]+, #(4\|12)\\b" dlna_text.asm \| awk -F: '$1>226000 && $1<230000'` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:526 | 1 |
| 400 | `grep -nE "sub\\s+r\\d+, fp, #(1328\|1332\|1336)" dlna_text.asm   # 全部引用点` | 19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:195 | 1 |
| 401 | `grep -o '<item id="menu_item_id_ph_sty_vlog"[^>]*>' "$S/getinfo_curmenu.xml"` | 14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:196<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:196 | 2 |
| 402 | `grep -o 'img="[^"]*lut[^"]*"' "$S/getinfo_allmenu.xml" \| wc -l                          # 期望 0` | 14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:193<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:193 | 2 |
| 403 | `grep -oiE '<item[^>]*lut[^>]*>' "$S/getinfo_allmenu.xml" \| grep -vi resolut \| wc -l    # 期望 0` | 14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:192<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:192 | 2 |
| 404 | `grep -rIl "Read LUT File\\\|V-Log View Assist" . \| head \|\| echo "  (无 → 属机身功能，非 App 功能)"` | 14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:206<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:206 | 2 |
| 405 | `grep -rIli "exfat" . \| head ; echo "(空 = 无 exFAT 驱动)"` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:386 | 2 |
| 406 | `grep -rIo "S5-XXXXXX" --include="*.log" --include="*.txt" . \| head` | 14_总包审计与新方向_20261014/00_审计总报告.md:437<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md:437 | 2 |
| 407 | `grep -rl "S5-XXXXXX" 04_工具与脚本/campaign2/out/ \| head` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:327 | 2 |
| 408 | `grep -rn "current_alt_setting" drivers/usb/gadget/ ; echo "(空 = 不存在)"` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:390 | 2 |
| 409 | `grep -rn "err_fw_same" 04_工具与脚本/campaign2/finalfix.py 04_工具与脚本/campaign2/control.py` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:357 | 2 |
| 410 | `grep -rn "sp_embeded_ph_sty13" --include="*.java" . \| head` | 14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:205<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:205 | 2 |
| 411 | `grep -rn "即为已执行\\\|已经执行" --include="*.py" --include="*.sh" 04_工具与脚本/ \| grep -v 审核` | 14_总包审计与新方向_20261014/00_审计总报告.md:214<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md:214 | 2 |
| 412 | `sed -n '1,60p'   01_研究报告/31_录制格式持久化_受控复测_20261014.md   # 结论摘要 + 方法` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:159 | 2 |
| 413 | `sed -n '1,80p'   README.md          # 头部：一句话结论 + 持久化结论更正史` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:93 | 2 |
| 414 | `sed -n '150,198p' README.md         # 脱敏说明 + 安全红线 + 去重说明` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:95 | 2 |
| 415 | `sed -n '180,195p' 01_研究报告/31_录制格式持久化_受控复测_20261014.md  # 证据与可复现性表` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:161 | 2 |
| 416 | `sed -n '20,31p;254,257p' 04_工具与脚本/campaign2/finalfix.py` | 14_总包审计与新方向_20261014/00_审计总报告.md:229<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md:229 | 2 |
| 417 | `sed -n '2891,2915p;3005,3015p' drivers/usb/gadget/function/f_fs.c` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:391 | 2 |
| 418 | `sed -n '55,100p' 01_研究报告/31_录制格式持久化_受控复测_20261014.md   # 结果表 + 判据` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:160 | 2 |
| 419 | `sed -n '78,92p' "01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md"` | 14_总包审计与新方向_20261014/00_审计总报告.md:231<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md:231 | 2 |
| 420 | `sed -n '80,150p' README.md          # 核心结论速览（已证/已证伪/仍开放）` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:94 | 2 |
| 421 | `sed -n '83,86p'          04_工具与脚本/campaign2/control.py` | 14_总包审计与新方向_20261014/00_审计总报告.md:230<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md:230 | 2 |
| 422 | `tools/sites.py 0xd66e8 0xd7b2c` | 19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:424<br>19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:440 | 2 |
| 423 | `tools/xr.py 0x1047cc` | 19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:214 | 1 |

### G. 无线 / BLE / SoftAP / 监看（s5_ble、s5ctl、wifi_ap_*、s5monitor、网络工具） —— 21 条

| # | 命令（原样） | 出处（规范路径:行号） | 出现次数 |
| --- | --- | --- | --- |
| 424 | `( nohup bash wifi_ap_probe.sh "$PWD/out/s5_ap" 45 >/dev/null 2>&1 & )` | 01_研究报告/18_相机热点SoftAP侧勘察_20261013.md:33<br>16_S5_核心总包_20261015/01_研究报告/18_相机热点SoftAP侧勘察_20261013.md:33 | 4 |
| 425 | `( nohup bash wifi_ap_probe2.sh "$PWD/out/s5_ap2" 45 >/dev/null 2>&1 & )` | 01_研究报告/18_相机热点SoftAP侧勘察_20261013.md:131<br>16_S5_核心总包_20261015/01_研究报告/18_相机热点SoftAP侧勘察_20261013.md:131 | 4 |
| 426 | `./run.sh 192.168.x.x` | 04_工具与脚本/s5_monitor/README.md:417<br>04_工具与脚本/s5_monitor/设置枚举测试计划.md:16<br>12_S5无线监看_v1.0_20261014/README.md:21<br>（另 1 处） | 11 |
| 427 | `./run.sh 192.168.x.x                    # 默认：8080 端口、固定 18fps` | 12_S5无线监看_v1.0_20261014/使用说明.md:105 | 3 |
| 428 | `./run.sh 192.168.x.x                 # 默认 8080 端口、固定 18fps` | 12_S5无线监看_v1.0_20261014/README.md:27 | 2 |
| 429 | `./run.sh 192.168.x.x 8080 adaptive` | 04_工具与脚本/s5_monitor/README.md:426 | 3 |
| 430 | `./run.sh 192.168.x.x 8080 adaptive      # 自适应模式（不推荐）` | 12_S5无线监看_v1.0_20261014/使用说明.md:108 | 3 |
| 431 | `./run.sh 192.168.x.x 8080 fixed 12` | 04_工具与脚本/s5_monitor/README.md:423 | 3 |
| 432 | `./run.sh 192.168.x.x 8080 fixed 12      # 降到 12fps 省带宽` | 12_S5无线监看_v1.0_20261014/使用说明.md:107 | 3 |
| 433 | `./run.sh 192.168.x.x 8080 fixed 12   # 降至 12fps 省带宽` | 12_S5无线监看_v1.0_20261014/README.md:29 | 2 |
| 434 | `./run.sh 192.168.x.x 8090               # 换端口（默认端口被占用时）` | 12_S5无线监看_v1.0_20261014/使用说明.md:106 | 3 |
| 435 | `./run.sh 192.168.x.x 8090            # 换端口` | 12_S5无线监看_v1.0_20261014/README.md:28 | 2 |
| 436 | `./run.sh <IP> 8090` | 12_S5无线监看_v1.0_20261014/使用说明.md:124 | 3 |
| 437 | `./run.sh <相机IP> [端口] [节奏模式] [帧率]` | 12_S5无线监看_v1.0_20261014/README.md:25<br>12_S5无线监看_v1.0_20261014/使用说明.md:102 | 5 |
| 438 | `kill` | 01_研究报告/04_隐藏格式_持久化成果.md:170<br>04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:16 | 13 |
| 439 | `kill 1404` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:215<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:215 | 2 |
| 440 | `nc -z` | 19_路径1_Linux侧攻击面_20261015/阶段A_Linux攻击面测绘_20261015.md:135 | 1 |
| 441 | `pkill -9 -f s5monitor.py` | 12_S5无线监看_v1.0_20261014/使用说明.md:124<br>12_S5无线监看_v1.0_20261014/附_技术参考.md:186 | 6 |
| 442 | `s5_ble.py scan` | 01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:247 | 4 |
| 443 | `tcpdump` | 00_项目总结/05_环境与依赖.md:67 | 2 |
| 444 | `tcpdump -i usbmon1` | 13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md:195 | 2 |

### H. LUT 烘焙与照片传输（bake、make_lut、check_style、s5_lut） —— 10 条

| # | 命令（原样） | 出处（规范路径:行号） | 出现次数 |
| --- | --- | --- | --- |
| 445 | `./bake batch <lut> <outdir> <in...>       # 批量` | 15_LUT烧录工具_20261014/README.md:79<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:79 | 2 |
| 446 | `./bake batch lut/vlog_to_709_17.cube ./输出目录 文件1 文件2 ...` | 15_LUT烧录工具_20261014/README.md:41<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:41 | 2 |
| 447 | `./bake image <lut> <in> <out>             # 照片（jpg/png/tif/heic）` | 15_LUT烧录工具_20261014/README.md:77<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:77 | 2 |
| 448 | `./bake image lut/vlog_to_709_17.vlt testdata/frame_synth_vlog.jpg out/rt.jpg` | 15_LUT烧录工具_20261014/README.md:224<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:224 | 2 |
| 449 | `./bake image lut/vlog_to_709_17.vlt 输入.jpg 输出.jpg` | 15_LUT烧录工具_20261014/README.md:35<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:35 | 2 |
| 450 | `./bake probe /Volumes/LUMIX/DCIM/100_PANA/P1000026.MP4` | 15_LUT烧录工具_20261014/README.md:223<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:223 | 2 |
| 451 | `./bake probe <文件>                       # 看规格（分辨率/帧率/编码/位深）` | 15_LUT烧录工具_20261014/README.md:76<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:76 | 2 |
| 452 | `./bake video <lut> <in> <out> [选项]       # 视频` | 15_LUT烧录工具_20261014/README.md:78<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:78 | 2 |
| 453 | `./bake video lut/vlog_to_709_17.vlt /Volumes/LUMIX/DCIM/100_PANA/P1000026.MP4 out/x.mp4 --max-seconds 2` | 15_LUT烧录工具_20261014/README.md:225<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:225 | 2 |
| 454 | `./bake video lut/vlog_to_709_17.vlt 输入.MP4 输出.mp4` | 15_LUT烧录工具_20261014/README.md:38<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:38 | 2 |

### I. 仓库 / 环境 / 文件管理（git、pip、pacman、变量导出、目录与文本操作） —— 135 条

| # | 命令（原样） | 出处（规范路径:行号） | 出现次数 |
| --- | --- | --- | --- |
| 455 | `$env:CAMLIBS = "C:\\msys64\\msys64\\ucrt64\\lib\\libgphoto2\\2.5.34"` | 01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:75 | 3 |
| 456 | `$env:IOLIBS  = "C:\\msys64\\msys64\\ucrt64\\lib\\libgphoto2_port\\0.12.2"` | 01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:74 | 3 |
| 457 | `$env:PATH    = "C:\\msys64\\msys64\\ucrt64\\bin;$env:PATH"` | 01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:73 | 3 |
| 458 | `S="14_总包审计与新方向_20261014/05_相机只读快照_20261014"` | 14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:201<br>14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:189<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:201<br>（另 1 处） | 4 |
| 459 | `TOOLS=04_工具与脚本/campaign2` | 00_项目总结/04_定因与工具链成果_20261013.md:135 | 2 |
| 460 | `Z="09_exFAT越界写成果包_20261013/exfat越界包（有风险非专业人员请勿轻易尝试.zip"` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:229 | 2 |
| 461 | `bash 14_总包审计与新方向_20261014/01_一键只读审核.sh 2>&1 \| tee /tmp/s5_audit.txt` | 14_总包审计与新方向_20261014/00_审计总报告.md:611<br>14_总包审计与新方向_20261014/02_全包查看指令手册.md:197<br>14_总包审计与新方向_20261014/README.md:34<br>（另 2 处） | 6 |
| 462 | `bash 14_总包审计与新方向_20261014/01_一键只读审核.sh > /tmp/audit_$(date +%Y%m%d_%H%M).txt 2>&1` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:429 | 2 |
| 463 | `bash run_all.sh` | 14_总包审计与新方向_20261014/06_密码学重跑/结论.md:383<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/06_密码学重跑/结论.md:383 | 2 |
| 464 | `bash wait_and_run.sh          # 等相机(15s×30min) → A-G → Phase I` | 04_工具与脚本/campaign2/README.md:50 | 2 |
| 465 | `bash wait_and_run.sh --no-i` | 04_工具与脚本/campaign2/README.md:52 | 2 |
| 466 | `bash wait_cam_and_run.sh` | 01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:55<br>03_解包_APK/com.panasonic.jp.lumixsync/oracle/README.md:55 | 4 |
| 467 | `brew install tree bat` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:33 | 2 |
| 468 | `cat 00_项目总结/00_执行摘要_全文.md` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:116 | 2 |
| 469 | `cat 00_项目总结/01_成果总表.md` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:117 | 2 |
| 470 | `cat 00_项目总结/02_项目时间线.md        # 最重要：所有改判的时序` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:118 | 2 |
| 471 | `cat 00_项目总结/04_定因与工具链成果_20261013.md` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:128 | 2 |
| 472 | `cat 01_研究报告/13_服务模式与ROMBACKUP_20261013.md          # 进入键、FAT32 门控、[Strict] 禁令` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:333 | 2 |
| 473 | `cat 01_研究报告/19_BLE凭据链打通_先写后读_20261013.md` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:319 | 2 |
| 474 | `cat 01_研究报告/20_BLE身份与WiFi门独立_20261013.md` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:320 | 2 |
| 475 | `cat 01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md  # EEPROM 导出、误操作事件` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:334 | 2 |
| 476 | `cat 04_工具与脚本/TOOLS.md` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:348 | 2 |
| 477 | `cat 04_工具与脚本/TOOLS_工具箱总览.md` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:349 | 2 |
| 478 | `cat 04_工具与脚本/campaign2/out/S5II_slot_crosscheck_20261013.md   # 注意 §1 登记的未定冲突` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:251 | 2 |
| 479 | `cat 04_工具与脚本/campaign2/out/S5_camsetting_fieldmap.md` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:247 | 2 |
| 480 | `cat 04_工具与脚本/campaign2/out/S5_format_slots_analysis.md` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:250 | 2 |
| 481 | `cat 09_对外分享/小红书帖_S5逆向进度_20261014.md` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:405 | 2 |
| 482 | `cat REPO_CONTENTS.md` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:96 | 2 |
| 483 | `cat S5_RE_Discord_Post_EN.md` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:407 | 2 |
| 484 | `cat S5_RE_Discord_Post_EN_2000.md` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:408 | 2 |
| 485 | `cat S5_RE_Project_Summary_EN.md` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:406 | 2 |
| 486 | `cat arch/arm/mach-pvc/Kconfig                        # V9AHD / V10 SoC` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:381 | 2 |
| 487 | `cd "/Users/<user>/Documents/ChatGPT/S5_逆向_项目总包_20261012"` | 14_总包审计与新方向_20261014/00_审计总报告.md:241<br>14_总包审计与新方向_20261014/00_审计总报告.md:610<br>14_总包审计与新方向_20261014/02_全包查看指令手册.md:228<br>（另 12 处） | 20 |
| 488 | `cd "/Users/<user>/Documents/ChatGPT/S5_逆向_项目总包_20261012/04_工具与脚本/campaign2/out"` | 14_总包审计与新方向_20261014/00_审计总报告.md:91<br>14_总包审计与新方向_20261014/00_审计总报告.md:172<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md:91<br>（另 1 处） | 4 |
| 489 | `cd "/Users/<user>/Documents/ChatGPT/S5_逆向_项目总包_20261012/04_工具与脚本/firmware_crypto"` | 14_总包审计与新方向_20261014/03_新方向与实验设计.md:47 | 2 |
| 490 | `cd "/Users/<user>/Documents/ChatGPT/S5_逆向_项目总包_20261012/04_工具与脚本/s5_monitor"` | 04_工具与脚本/s5_monitor/设置枚举测试计划.md:15 | 3 |
| 491 | `cd "/Users/<user>/Documents/ChatGPT/S5_逆向_项目总包_20261012/12_S5无线监看_v1.0_20261014"` | 12_S5无线监看_v1.0_20261014/连热点时怎么测.md:15<br>16_S5_核心总包_20261015/12_S5无线监看_v1.0_20261014/连热点时怎么测.md:15 | 2 |
| 492 | `cd "/Users/<user>/Documents/ChatGPT/S5_逆向_项目总包_20261012/14_总包审计与新方向_20261014/06_密码学重跑"` | 14_总包审计与新方向_20261014/06_密码学重跑/结论.md:380<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/06_密码学重跑/结论.md:380 | 2 |
| 493 | `cd /Users/<user>/Documents/ChatGPT/S5逆向` | 01_研究报告/02_研究总报告_20261011/07-USB-PTP-SCSI.md:57<br>04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:39<br>04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:94 | 17 |
| 494 | `cd /Users/<user>/Documents/ChatGPT/S5逆向/campaign2` | 04_工具与脚本/campaign2/README.md:49 | 2 |
| 495 | `cd /Users/<user>/Downloads/com.panasonic.jp.lumixsync_b0834c31/oracle` | 01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:50<br>03_解包_APK/com.panasonic.jp.lumixsync/oracle/README.md:50 | 4 |
| 496 | `cd 02_工具` | 13_USB服务通道勘察_交接包_20261014/README.md:55 | 2 |
| 497 | `cd 03-离线破解与上传预言机/oracle` | 01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:266 | 6 |
| 498 | `cd 03_解包_APK/com.panasonic.jp.lumixsync` | 14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:204<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:204 | 2 |
| 499 | `cd 04_工具与脚本/campaign2` | 01_研究报告/14_蓝牙BLE勘察_20261013.md:89<br>01_研究报告/18_相机热点SoftAP侧勘察_20261013.md:32<br>01_研究报告/18_相机热点SoftAP侧勘察_20261013.md:130<br>（另 2 处） | 12 |
| 500 | `cd 04_工具与脚本/campaign2/out` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:167 | 2 |
| 501 | `cd 04_工具与脚本/s5_monitor` | 04_工具与脚本/s5_monitor/README.md:69 | 3 |
| 502 | `cd 07_参考仓库/s1m2-research/analysis` | 13_USB服务通道勘察_交接包_20261014/03_Tether协议线索.md:111 | 2 |
| 503 | `cd 07_参考仓库/s5_oss_kernel/linux-3.18.18` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:378 | 2 |
| 504 | `cd 12_S5无线监看_v1.0_20261014` | 00_调用前必查_已跑通路径总索引.md:24<br>14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:25<br>14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:222<br>（另 2 处） | 5 |
| 505 | `cd 14_总包审计与新方向_20261014/07_签名与密钥恢复` | 14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:303<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:303 | 2 |
| 506 | `cd 15_LUT烧录工具_20261014` | 15_LUT烧录工具_20261014/README.md:32<br>15_LUT烧录工具_20261014/README.md:210<br>16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md:32<br>（另 1 处） | 4 |
| 507 | `cd 18_G100明文与同类项目_20261015` | 18_G100明文与同类项目_20261015/G100反编译_深挖报告.md:332 | 2 |
| 508 | `cd 19_路径1_Linux侧攻击面_20261015/dlna_audit` | 19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:476<br>19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:430<br>19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:366 | 3 |
| 509 | `cd <LOCAL_WORKSPACE>` | 01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件逆向_阶段结果汇总.md:304 | 3 |
| 510 | `cd D:\\20261015松下G100逆向` | 18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:420 | 1 |
| 511 | `cd LumixFast-iOS` | 05_源码/LumixFast-iOS/README.md:83 | 2 |
| 512 | `cd fw_fetch` | 01_研究报告/02_研究总报告_20261011/research/BOOT_FLOW.md:170 | 7 |
| 513 | `cd scripts` | 01_研究报告/03_隐藏格式_可分发版_20261012/README.md:55<br>01_研究报告/03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md:79<br>01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md:42 | 9 |
| 514 | `cp -a "$REPO/00_项目总结" .` | 08_总结与工具箱_20261013/README.md:25<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/README.md:40 | 2 |
| 515 | `cp -a "$REPO/01_研究报告" .` | 08_总结与工具箱_20261013/README.md:26<br>09_exFAT越界写成果包_20261013/README.md:32<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/README.md:41 | 3 |
| 516 | `cp -a "$REPO/04_工具与脚本" .` | 08_总结与工具箱_20261013/README.md:27<br>09_exFAT越界写成果包_20261013/README.md:33<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/README.md:42 | 3 |
| 517 | `cp -a "$REPO/06_数据与证据" .` | 08_总结与工具箱_20261013/README.md:28<br>09_exFAT越界写成果包_20261013/README.md:34<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/README.md:43 | 3 |
| 518 | `du -sh */ 2>/dev/null \| sort -hr` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:45 | 2 |
| 519 | `du -sh 07_参考仓库/*/` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:376 | 2 |
| 520 | `echo "--- $part"` | 14_总包审计与新方向_20261014/03_新方向与实验设计.md:512 | 2 |
| 521 | `echo "--- 子目录 ---"; ls -d 01_研究报告/*/` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:142 | 2 |
| 522 | `echo "--- 顶层报告数 ---"; ls 01_研究报告/*.md \| wc -l` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:141 | 2 |
| 523 | `export PYTHONPATH=/tmp/s5sig_lib` | 14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:305<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:305 | 2 |
| 524 | `export S5_IP=192.168.x.x` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md:80 | 3 |
| 525 | `export S5_IP=192.168.x.x        # 改成你相机的实际 IP` | 01_研究报告/03_隐藏格式_可分发版_20261012/README.md:56 | 3 |
| 526 | `export S5_IP=192.168.x.x      # 相机实际 IP` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md:21 | 3 |
| 527 | `export S5_PORT=80              # 默认 80，一般不改` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md:22 | 3 |
| 528 | `ffmpeg` | 14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:384<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:384 | 2 |
| 529 | `ffprobe` | 00_项目总结/05_环境与依赖.md:78 | 2 |
| 530 | `ffprobe -v error -select_streams v:0 -show_frames -show_entries frame=pict_type,key_frame -of json /完整路径/测试文件.MP4` | 01_研究报告/05_Panasonic_hidden_format_参考/复现操作手册.md:78 | 2 |
| 531 | `find . -name .git -maxdepth 4 -not -path "./.git"   # 嵌套仓库` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:77 | 2 |
| 532 | `find . -type f -not -path "./.git/*" \| sed 's/.*\\.//' \| tr 'A-Z' 'a-z' \| sort \| uniq -c \| sort -rn \| head -25` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:57 | 2 |
| 533 | `find . -type f -size +20M -not -path "./.git/*" -exec ls -lh {} \\; 2>/dev/null \| awk '{print $5, $9}' \| sort -hr` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:66 | 2 |
| 534 | `find drivers/usb/gadget -iname "*ptp*" -o -iname "*mtp*" \| head ; echo "(空 = 无 PTP gadget)"` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:387 | 2 |
| 535 | `git am` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:7<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:7 | 2 |
| 536 | `git am 14_总包审计与新方向_20261014/10_仓库补丁/0001-v1.1-LUT.patch` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:34<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:34 | 2 |
| 537 | `git bundle verify` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:8<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:8 | 2 |
| 538 | `git clone --depth 1` | 01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/siegfried82_notes.md:3 | 3 |
| 539 | `git fetch 14_总包审计与新方向_20261014/10_仓库补丁/S5-wireless-monitor_v1.1.bundle main:from-bundle` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:36<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:36 | 2 |
| 540 | `git log --oneline --graph -20` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:75 | 2 |
| 541 | `git ls-files` | 14_总包审计与新方向_20261014/00_审计总报告.md:410<br>14_总包审计与新方向_20261014/02_全包查看指令手册.md:70<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md:410 | 4 |
| 542 | `git ls-files 11_DC-S5成果包_20261013/01_研究报告_全集 \| wc -l    # 318` | 14_总包审计与新方向_20261014/00_审计总报告.md:321<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md:321 | 2 |
| 543 | `git push https://<你的token>@github.com/williamwu1234/S5-wireless-monitor.git main` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:31<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:31 | 2 |
| 544 | `git push origin main` | 14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:28<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:28 | 2 |
| 545 | `git rev-parse HEAD && git log -1 --format='%ci %s'` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:431 | 2 |
| 546 | `git status --short` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:76 | 2 |
| 547 | `head -5 Makefile                                    # 版权与版本（3.18.18）` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:379 | 2 |
| 548 | `jadx` | 14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:300<br>14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:236<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:300<br>（另 1 处） | 4 |
| 549 | `ls -1 01_研究报告/` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:140 | 2 |
| 550 | `ls -l /dev/disk*s*                       # 看容量与时间戳` | 01_研究报告/25_操作记录与风险手册_20261013.md:54<br>11_DC-S5成果包_20261013/01_研究报告_全集/25_操作记录与风险手册_20261013.md:54 | 4 |
| 551 | `ls -la` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:44 | 2 |
| 552 | `ls -la 00_项目总结/` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:115 | 2 |
| 553 | `ls -la 01_研究报告/02_研究总报告_20261011/logs/` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:179 | 2 |
| 554 | `ls -la 06_数据与证据/firmware_crypto_s5/` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:312 | 2 |
| 555 | `ls -la 06_数据与证据/rombackup_20261013/     # ADJUST/FIX/UPDATE.bin 各 128KB + S5A/S5F/S5U.TXT` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:336 | 2 |
| 556 | `ls -la 06_数据与证据/service_mode_evidence/  # 服务菜单实拍` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:337 | 2 |
| 557 | `ls 04_工具与脚本/ble_win/` | 14_总包审计与新方向_20261014/03_新方向与实验设计.md:466 | 2 |
| 558 | `ls 07_参考仓库/` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:375 | 2 |
| 559 | `ls arch/arm/configs/ \| grep -i "pvc\\\|dsc"            # pvc02v_dsc_release_defconfig` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:382 | 2 |
| 560 | `ls arch/arm/mach-pvc/                               # 松下相机平台` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:380 | 2 |
| 561 | `ls drivers/mmc/host/pvc_sdio.c drivers/usb/core/usb-panasonic.c 2>/dev/null` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:383 | 2 |
| 562 | `mkdir -p /tmp/pkg08 && cd /tmp/pkg08` | 08_总结与工具箱_20261013/README.md:24 | 1 |
| 563 | `mkdir -p /tmp/pkg09 && cd /tmp/pkg09` | 09_exFAT越界写成果包_20261013/README.md:31 | 1 |
| 564 | `mkdir -p /tmp/pkg10 && cd /tmp/pkg10` | 10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/README.md:39 | 1 |
| 565 | `mkdir -p /tmp/s5exfat && cp "$TOOLS"/exfat_patch.py "$TOOLS"/exfat_spray.py "$TOOLS"/s5_exfat_test.sh /tmp/s5exfat/ && chmod +x /tmp/s5exfat/*` | 00_项目总结/04_定因与工具链成果_20261013.md:136 | 2 |
| 566 | `mkdir -p ~/s5_crypto_backup && cp *.py ~/s5_crypto_backup/` | 14_总包审计与新方向_20261014/03_新方向与实验设计.md:50 | 2 |
| 567 | `open LumixFast.xcodeproj   # 用 Xcode 打开` | 05_源码/LumixFast-iOS/README.md:85 | 2 |
| 568 | `pacman -S  --noconfirm mingw-w64-ucrt-x86_64-gphoto2` | 01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:67 | 3 |
| 569 | `pacman -Sy --noconfirm` | 01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:66 | 3 |
| 570 | `pip install` | 01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md:14<br>12_S5无线监看_v1.0_20261014/README.md:8 | 5 |
| 571 | `pip install libusb1` | 01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:244 | 3 |
| 572 | `pip3 install --target /tmp/s5sig_lib ecdsa gmpy2      # 可选；缺 ecdsa 时自动回退纯 Python` | 14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:304<br>16_S5_核心总包_20261015/14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:304 | 2 |
| 573 | `pip3 install ecdsa    # 轻量，纯 Python` | 14_总包审计与新方向_20261014/03_新方向与实验设计.md:136 | 2 |
| 574 | `sudo bash /tmp/s5exfat/s5_exfat_test.sh checkalloc /dev/disk8s1` | 00_项目总结/04_定因与工具链成果_20261013.md:141<br>00_项目总结/04_定因与工具链成果_20261013.md:147<br>01_研究报告/24_相机长文件名崩溃_定因_20261013.md:62<br>（另 3 处） | 16 |
| 575 | `sudo bash /tmp/s5exfat/s5_exfat_test.sh go2 /dev/diskNsM      # 自动挑照片、注入越界值 524290` | 01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:212 | 4 |
| 576 | `sudo bash /tmp/s5exfat/s5_exfat_test.sh mkdeleted /dev/disk8s1 <数量>` | 01_研究报告/25_操作记录与风险手册_20261013.md:101<br>11_DC-S5成果包_20261013/01_研究报告_全集/25_操作记录与风险手册_20261013.md:101 | 4 |
| 577 | `sudo bash /tmp/s5exfat/s5_exfat_test.sh mkentries /dev/disk8s1 360 240 0` | 00_项目总结/04_定因与工具链成果_20261013.md:144<br>01_研究报告/24_相机长文件名崩溃_定因_20261013.md:64 | 6 |
| 578 | `sudo bash /tmp/s5exfat/s5_exfat_test.sh mkentries /dev/disk8s1 <数量> <名字长度> [起始序号]` | 01_研究报告/25_操作记录与风险手册_20261013.md:95<br>11_DC-S5成果包_20261013/01_研究报告_全集/25_操作记录与风险手册_20261013.md:95 | 4 |
| 579 | `sudo bash /tmp/s5exfat/s5_exfat_test.sh mkspray  /dev/disk8s1 <数量> <num_ext> [起始序号]` | 01_研究报告/25_操作记录与风险手册_20261013.md:98<br>11_DC-S5成果包_20261013/01_研究报告_全集/25_操作记录与风险手册_20261013.md:98 | 4 |
| 580 | `sudo bash /tmp/s5exfat/s5_exfat_test.sh setfat /dev/disk8s1 <簇号> 0xFFFFFFFF` | 01_研究报告/25_操作记录与风险手册_20261013.md:172<br>11_DC-S5成果包_20261013/01_研究报告_全集/25_操作记录与风险手册_20261013.md:172 | 4 |
| 581 | `sudo bash /tmp/s5exfat/s5_exfat_test.sh trimdir  /dev/disk8s1 <保留槽位数>` | 01_研究报告/25_操作记录与风险手册_20261013.md:104<br>11_DC-S5成果包_20261013/01_研究报告_全集/25_操作记录与风险手册_20261013.md:104 | 4 |
| 582 | `sudo bash /tmp/s5exfat/s5_exfat_test.sh verdict /dev/diskNsM  # ③ 回到 Mac 核对现场` | 01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:214 | 4 |
| 583 | `sudo bash s5_exfat_test.sh <子命令> /dev/diskNsM [参数...]` | 04_工具与脚本/TOOLS.md:59 | 2 |
| 584 | `sudo dseditgroup -o edit -a $(whoami) -t user operator` | 00_项目总结/05_环境与依赖.md:151<br>01_研究报告/25_操作记录与风险手册_20261013.md:43<br>11_DC-S5成果包_20261013/01_研究报告_全集/25_操作记录与风险手册_20261013.md:43 | 6 |
| 585 | `sudo modprobe usbmon` | 13_USB服务通道勘察_交接包_20261014/02_工具/README.md:95 | 2 |
| 586 | `sudo python3 exfat_patch.py <子命令> /dev/diskNsM [参数...]` | 04_工具与脚本/TOOLS.md:20 | 2 |
| 587 | `sudo tcpdump -i XHC20 -w usb.pcap` | 13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md:196 | 2 |
| 588 | `sudo tcpdump -i usbmon1 -w usb.pcap` | 13_USB服务通道勘察_交接包_20261014/02_工具/README.md:96 | 2 |
| 589 | `tail -50 01_研究报告/26_本次运行日志_20261013.md     # 运行日志` | 14_总包审计与新方向_20261014/02_全包查看指令手册.md:180 | 2 |

### Z. 其他 / 未归类 —— 1 条

| # | 命令（原样） | 出处（规范路径:行号） | 出现次数 |
| --- | --- | --- | --- |
| 590 | `./s5ctl.sh start\|stop\|status` | 01_研究报告/20_BLE身份与WiFi门独立_20261013.md:98 | 4 |

---

## 表 2 · 全项目结论编号索引

共 **146** 个编号（跨 18 套体系）。

### C 容器/格式事实结论（C1–C24） —— 24 条

定义出处：`17_SD引导路线_20261015/00_交接包_上下文工具与结论.md`

| 编号 | 一句话结论 / 内容（原样摘录） | 出处 |
| --- | --- | --- |
| **C1** | UPD 容器：`0x200` "panasonic" 标签；`0x2EC` 起 48×92B 分区表；`CRC32(bin[0x200:])==头0x40`（**0x40 字段小端序**；CRC 可伪造，仅完整性） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:89` |
| **C2** | 容器尾 512B 与发布包独立 `.sig` **逐字节相同** | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:90` |
| **C3** | `0x220` 64B 块：S5 五版本互异、与内容绑定——**机制未定**（禁止定性为签名算法） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:91` |
| **C4** | 90,144 组 ECDSA 公钥恢复穷举**零收敛**；RSA 模数恢复（e∈{3,5,7,17,257,65537}）**全部排除** | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:92` |
| **C5** | PVC = Milbeaut 家族（官方佐证：`pvc04v-MC8259.dtsi` 的 compatible 链 `socionext,milbeaut-sc2006a`） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:93` |
| **C6** | S5 代公开名 = **V9AHD（pvc02v）**：4×Cortex-A7；SD 控制器为松下自定义 `"panasonic,sdhci"`@`0x7c320000`（**非** Milbeaut 标准 F_SDH30） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:94` |
| **C7** | BootROM 带 SD 入口的**已证实世代**：M8M（mb86s27，SW3.3 strap 门控）与 M10V（SC2000a，CM0 向量 0x3FFE0400，hypoxic 实测） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:95` |
| **C8** | M20V（SC2006A）起安全模型收紧：BootROM 从 OTP 读公钥、强制验签 bootstrap；取消片内 CM0（改外置 STM32） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:96` |
| **C9** | stubby 参考板 SD loader **不验签**（`config-sc2000-sddat.h` 的 RSA 开关被注释）；但其 SDHCI/UART/DDR 参数全部绑定 SC2000 参考板 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:97` |
| **C10** | stubby 公开支持面 = {mb8ac0300, mb86s7x/mb86s27, SC2000/MLB01, SC2000a/GP1}，**无 PVC/MC801 条目** | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:98` |
| **C11** | 监视器线：accctrl 单槽、按注册 UUID 放行；热点直连零重播（经路由器 40% 重播）；LUT 256³ 查表逐位精确且 1 ms 秒切；DLNA 内容树仅回放模式有 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:99` |
| **C12** | stubby 仓库的 GPL 源码**只覆盖 Stubby（A7 Linux 引导器）**；SD loader（SD.DAT，CM0 Thumb）是**闭源预编译**，源码树 grep 零命中。构建已复现（arm-none-eabi-gcc 16.2.0 + 3 处可移植性补丁） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:100` |
| **C13** | `0x34`：**=0 ⟺ 全明文**（G100 V13 对照臂，37/37 节 sha 命中含 29 个 type=3）、**=3 ⟺ 有加密**（7 容器）——n=8 闭环；**type=3 只是可加密标记，0x34 才是加密使能**；条目"aux16"=16B IV 字段（IV 全零 ⟺ 未加密） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:101` |
| **C14** | **G100 V1.3 全明文容器到手**（`02_固件二进制/DC-G100/G100_V13.bin`，SHA256=6c726fe0…）：0x34=0、37 条目全 IV 零、**type=3 也明文** ⇒ "type=3=可加密标记，0x34=加密使能"实锤（n=8 对照臂补全） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:102` |
| **C15** | G100 loader1 = **ARM 异常向量表**（MPIDR/WFI 次核自旋、复制 0x1A8B 代码到 SRAM 0x60009D00 二段引导）⇒ V9AHD 首段跑 **Cortex-A7**；**全容器 105MB 字节级扫描**：SD.DAT/boot.par/sdram.par/HBOOT/MISCTOP/MDR/bootmode/CM0/0x3FFE0400 **全部零命中**；dtb 无 CM0/misctop 节点 ⇒ **无 SD 引导的固件侧证据**（BootROM 本身不在镜像内，硬件侧仍无法判定） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:103` |
| **C16** | G100 dtb 为明文 FDT：`panasonic,pvc02v-brb`、4×Cortex-A7、4×`panasonic,sdhci`（仅 7c320000=WiFi 使能）、**4×PL011 UART**（7f050000/7f051000/7f052000/7f053000）、`console=ttyAMA,115200`、`root=/dev/mtdblock0`（NAND） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:104` |
| **C17** | G100 zboot = 2KB **Thumb stub→zImage**，入口与 stubby 构建产物（A7 ARM）**不同** ⇒ P4 朝"非同源"倾斜 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:105` |
| **C18** | **平台内置 ECDSA-P256 验签**（P-256 常数 p/n/Gx/Gy 小端序 @容器 0x6F27FC 起，逐字节比对 FIPS；代码区 rt 0x04F6E-0x04F7E 有 4 个 xref；旁有 `"PICTURE_QUALITY"+"ecdsa-p256"+"panasonic"+"jp"` 签名数据块）⇒ 用于**画质参数数据验签**；**program 全段无有效公钥点**（曲线方程验证零命中）⇒ 公钥在 OTP/掩模 ROM 或哈希形式——**解释了 C4 穷举零收敛** | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:106` |
| **C19** | AES：loader1/2/3/zboot **零 AES 常量**（S-box/Rcon 全段扫描）⇒ 节解密在**硬件引擎**；program 内完整 AES（S-box@+0x7CA190）有 **112 个 Thumb 调用者**（加密服务包装 rt 0x04D203A0 起），但**更新路径（upd/wr）零调用**（修正 S5M2 报告结论 9 的支撑证据："仅 ARM 模式无调用者"） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:107` |
| **C20** | G100 更新头校验（字节级）：0x2C/0x34∈{0,2,3}、0x30=0、0x08≥0x200；**0x34 不参与密钥选择**；CRC=标准 zlib CRC32（佐证 C1）；hexrays 包**只覆盖 5 个切片**（约 2MB Thumb 区未覆盖）——"1698 文件 ≠ 全 program" | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:108` |
| **C21** | **K32 预言机（SHA-256 明文预言机）在 S5 的产出**：5 节 0x3BD000B（4.47% 加密字节）= music/koutei_kao/eep_act_a/b/ipu_data；**S5 boot 链（loader1/2/3、zboot、dtb、program）在 G100 无 K32 孪生**（GX9 能搬 loader1/zboot，S5 不能）⇒ 预言机给不了 S5 任何代码明文 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:109` |
| **C22** | G100 program 内 AES 模块**有真实调用者**（Thumb 87 + ARM 15 调用点，≥5 区域：自检×12、CTR+HMAC 工具链×20 等）；更新路径/NAND 写 API 区间仍为 0 调用——同事报告结论 9 的普查**漏了 Thumb 侧**，应窄化为"更新路径不调用 AES" | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:110` |
| **C23** | AES 前端经**固定地址槽运行时间接分发**：0x0584961E/0x0584966C/0x058499C0（槽内容容器内不可解析 ⇒ 解密后端为运行时接线或片上）；0x04EF7xxx 为 HMAC-SHA256 类原语（固定密钥 dword_515E6BC） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:111` |
| **C24** | G100 与 S5 的 boot/OS 节 **load addr 逐节相同**（loader1@0x0、program@0x80000、zboot 同族）⇒ 同代同内存布局；G100 地址图可作 S5 运行时探针的**候选地图**（非精确） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:112` |

### R 复核项（R1–R10，含印证/否定判定） —— 10 条

定义出处：`14_总包审计与新方向_20261014/00_审计总报告.md`

| 编号 | 一句话结论 / 内容（原样摘录） | 出处 |
| --- | --- | --- |
| **R1** | CAMSET 校验和规则 `byte[65532]=(256−Σ[0..65531]) mod 256` \| `camsetting.bin` → 0x4d ✅；`blob_GOLD_mov` → 0xd3 ✅；`sum%256==0` ✅ \| **印证**（项目结论正确） | `14_总包审计与新方向_20261014/00_审计总报告.md:52` |
| **R2** | `0x005e` 记录 `3062..3074` 的结构 \| 确为 **13 元素数组** + 1 字节 0x00；基线 A=`05×13`、`diff_blob_mov`=`06 05×12`、GOLD=`06×13` \| **新增结构证据**（详见 §2 S3） | `14_总包审计与新方向_20261014/00_审计总报告.md:53` |
| **R3** | 10-14 复测的 payload vs 备份 \| `175604` 与 `180310` 两对**逐字节相同** \| **否定**报告 31 §3.2（详见 §2 S1） | `14_总包审计与新方向_20261014/00_审计总报告.md:54` |
| **R4** | 固件分区表记录 SHA 的偏移归属 \| `doff+0x200` → 明文分区 **7/7** 命中；`doff` → **2/7** \| **否定**"记录 SHA ≠ 内容哈希"（详见 §2 S2） | `14_总包审计与新方向_20261014/00_审计总报告.md:55` |
| **R5** | 48 分区 type↔IV 统计 \| type=2 共 7、type=3 共 41、全零 IV 7 个、唯一 IV 42 \| **印证** | `14_总包审计与新方向_20261014/00_审计总报告.md:56` |
| **R6** | MANIFEST 全量校验 \| 77,504 OK / **5 FAILED** / 集合零差异 \| **新发现**（详见 §3 B3） | `14_总包审计与新方向_20261014/00_审计总报告.md:57` |
| **R7** | S5 OSS 内核 `f_fs.c` 审计 \| **无** `current_alt_setting`、无松下改动；全树无 exFAT 驱动、无 PTP gadget \| **新增结论 + 重要限定**（详见 §5 方向 6） | `14_总包审计与新方向_20261014/00_审计总报告.md:58` |
| **R8** | 库内 `curmenu.xml` 档位 \| 仅 5 个 mp4 + 1 个 mp4hevc `enable=yes`（PAL+mp4 态） \| **无法复现** 18/12/10（详见 §3 B5） | `14_总包审计与新方向_20261014/00_审计总报告.md:59` |
| **R9** | 交错验证：err_fw_same 两种解释 \| `finalfix.py:20` 说"FLASH LANDED"，`control.py:83` 说"TRANSPORT CLEAN…does NOT flash" \| **直接矛盾**（详见 §2 A2） | `14_总包审计与新方向_20261014/00_审计总报告.md:60` |
| **R10** | 序列号 hex 解码 \| `584a4c####################` = `XJL########15` \| **合规泄露确认**（详见 §2 C1） | `14_总包审计与新方向_20261014/00_审计总报告.md:61` |

### R 已撤回/已更正的说法（R1–R6） —— 6 条

定义出处：`17_SD引导路线_20261015/00_交接包_上下文工具与结论.md`

| 编号 | 一句话结论 / 内容（原样摘录） | 出处 |
| --- | --- | --- |
| **R1** | "`0x220` = ECDSA P-256 签名" \| 上游自我撤回 + C4 穷举零收敛。正确表述见 C3 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:117` |
| **R2** | "`0x2C/0x34` = 引导段数=3" \| 用户文档 §2.4 提出"保护族"候选（待多版本验证，属 4.3 待证项） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:118` |
| **R3** | "SC2006A = 第 9 代" \| 官方证据：SC2006A 公开对应 **M20V**（4×A53） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:119` |
| **R4** | "SD.DAT 恢复模式 = Milbeaut **全系通用**" \| 仅 M8M/M10V 已证实；PVC/MC801 待证实（无法判定） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:120` |
| **R5** | "相机屏幕弹出允许对话框" \| 实测不弹（内部自校验）——仅涉监视器线，此处备查 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:121` |
| **R6** | "loader1/zboot 有 512B 明文头，载荷从 +0x200 起" \| T3 字节级推翻：旧偏移模型产物。实为表尾/邻区填充；全部代码分区**从字节 0 起密文**（熵 7.9+）。S5 容器**零明文代码区**。补充：同代 G100 容器 100% 明文（唯一例外镜像），其代码可见性红利见 C21–C23 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:122` |

### P 待证项 / 开放问题（P1–P7） —— 7 条

定义出处：`17_SD引导路线_20261015/00_交接包_上下文工具与结论.md`

| 编号 | 一句话结论 / 内容（原样摘录） | 出处 |
| --- | --- | --- |
| **P1** | **MC801 BootROM 是否带 SD 引导入口** \| 软件侧全明文对照负证据（C15）；BootROM 本身不可见，硬件侧仍无法判定。唯一直接判据 = 拆机 UART bootlog | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:128` |
| **P2** | `0x34` 的**机制**（加密使能声明 vs 保护族 vs 其它） \| 相关性 n=8 闭环（C13）；机制仍未证实——G100 校验代码只做 ∈{0,2,3} 范围检查，待 runtime/IDA | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:129` |
| **P3** | MC801 是否含片内 CM0、MDR/MISCTOP 地址与位域 \| 同代全明文镜像零 CM0 痕迹（C15）⇒ 软件侧基本否定；片上实况待硬件 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:130` |
| **P4** | S5 的 zboot 是否 Stubby 同源 \| G100 zboot=2KB Thumb stub→zImage，与 Stubby（A7 ARM）不同（C17）⇒ 朝『非同源』倾斜 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:131` |
| **P5** | 量产 BootROM 删除/熔断 SD 入口的先例 \| 两可；**pvc02v 安全模型=数据签名制**（ECDSA 画质数据，公钥在 OTP/ROM）；索尼先例=量产保留串行引导族 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:132` |
| **P6** | **AES 密钥派生模型（Sony 同构假说）** \| 索尼 A7 IV：密钥=BootROM scramble pad+固件内 ≤64 项小整数索引表派生（ILCE-7M4-RE 方法链）。若 S5 同构 ⇒ 可搜形态=明文头/代码里的**小整数索引表**；G100 全明文镜像可直接搜 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:133` |
| **P7** | V9AHD 代 BootROM 是否有 **UART/USB 串行引导族**（不止 SD） \| 索尼先例：量产未熔断、默认开启、仅解锁码保护。UART 路线升级为与 SD 并列的主线 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:134` |

### P 硬件/侵入式路线行动计划（P1–P8） —— 8 条

定义出处：`01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md`

| 编号 | 一句话结论 / 内容（原样摘录） | 出处 |
| --- | --- | --- |
| **P1** | **拆机只读取证**：SoC 丝印（定 die/代际）、JTAG/SWD 与 UART 测试点、Wi-Fi 模块型号、**存储类型 eMMC/NAND**、主板正反面高清图 \| 拆机（接 AC、备拔电池恢复） \| 零（只读） \| 全部硬件路径的先决条件；信息量最大 \| 未做 | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:80` |
| **P2** | **服务模式组合键盲试**：多键同时按下开机（GX85/ZS30 式），试 S5 的 SERVICE MODE \| 无 \| 零 \| 若命中 → 维护菜单/读入口（或至少排除） \| 未做 | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:81` |
| **P3** | **S5 U-Boot 控制台离线核验**：在 48 分区表 type=2 明文分区中找 U-Boot env / BOOTDELAY / console= / loglevel 痕迹 \| 离线（`s5_layout.json` + `S5___V29.bin.parts.json` 已在包内） \| 零 \| 判定 UART 生死（S1R2 先例：console=null → 死路）；顺带看 Stubby 是否 ENFORCING \| 未做（**本次新增**） | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:82` |
| **P4** | **JTAG / CoreSight dump RAM**：OpenOCD（A7，3 看门点/5 断点）halt → dump loader/program/zimage/rootfs 运行态 \| P1 确认焊点 + 时序 \| 低（只读 halt，不写 flash） \| **★ 解密后运行时明文 = 目标达成** \| 未做（主线） | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:83` |
| **P5** | **UART bootlog**（仅当 P3 判活）：115200 8N1 抓 Stubby 告警/验签/分区表/cmdline \| P3 \| 零 \| 启动链实证 + 验签时机 \| 未做 | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:84` |
| **P6** | **SD.DAT / ROM-flashing**：BootROM 跑 SD 卡自编 `DATA.BIN`，绕 loader2/3 与验签链，可写可 dump \| P1（确认存储类型）+ 全量备份 + 验证过的 `pardata.par` \| **高**（S1R2 NAND 教训：写错标定数据 = 不可逆砖） \| 彻底绕过验签链的写入口（JTAG 受阻时的备胎） \| 未做（降级为备胎） | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:85` |
| **P7** | **S5 内核 f_fs OOB 离线审计**：MC801 内核 OSS 对照 `f_fs.c` 的 `current_alt_setting` 修改（S1R2 报告 §2 代码位置） \| 拿到 MC801 内核 OSS \| 零 \| 若命中 = USB 主机→内核 未授权写原语（CVE 归档/DoS/辅助泄露），单独不解密 \| 未做 | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:86` |
| **P8** | **芯片级**：chip-off / 故障注入 / 侧信道（Crypto Engine） \| 芯片级设备与资金 \| 高 / 高成本 \| 直接提取密钥本身 \| 最后手段 | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:87` |

### H 隐藏格式成果（H1–H7，含 H1b/H1c） —— 9 条

定义出处：`00_项目总结/01_成果总表.md`

| 编号 | 一句话结论 / 内容（原样摘录） | 出处 |
| --- | --- | --- |
| **H1** | 隐藏格式持久化 \| ✓ \| 直写 flash 的 65533 字节 blob 后，`ntsc_pal`、`videoformat`、`videoquality` **三项均可跨断电保留**（2026-10-14 受控复测，**n=2**，见 31 号报告）。**附条件**：`videoquality` 的保留与**开机时 SD 卡槽 1 的挂载状态**相关（槽 1 未挂载时由 `0x9b` 降为 `0x9f`）；该机制仅 1 组对照，**待重复实验确认**。结论修订史：① 10-13 判「mov 回落」系 `persist.py` 上传协议缺陷（单次 POST 从未落地），修复为分块 `separate` 后判持久化成立；② 10-13 晚改判「仅 `ntsc_pal` 持久」，该改判**未被 10-14 受控复测重现**。判据方法：`getinfo camsetting` 返回 **RAM 副本**，写完立刻回读不能作为持… | `00_项目总结/01_成果总表.md:9` |
| **H1b** | CAMSET 写入协议 \| ✓ \| `startsenddata` 返回 `method=separate/bufsize=61460`；须按 61192+4341 分块 `senddata`+`requestsenddata`+`endsenddata`。错校验和 → `err_reject` | `00_项目总结/01_成果总表.md:10` |
| **H1c** | 机身菜单质量约束 \| ✓ \| 持久化的质量码必须存在于机身 `allmenu`，否则机身【录制质量】变灰。`0x8b`(mov_…_**c4k**_10bit) 不在 allmenu → 不可用；`0x9b`/`0x92` 等已声明档可用。另：机身停在菜单时 `getinfo camsetting` 回 `err_reject`（见 07 附录） | `00_项目总结/01_成果总表.md:11` |
| **H2** | 容器门互斥机制 \| ✓ \| `videoformat` 单字段门控，mov(NTSC **18** 档 / PAL **12** 档) / mp4(~~16~~ **8** 档，另 mp4hevc **2** 档) 互斥。<br>**（10-14 更正）** 档数须以实时 `curmenu` 的 `enable=yes` 为准，随**制式**与**容器**变化；旧值 17/16 不准。`mp4hevc` 有 2 档启用，当年「放弃 HEVC」是**主动取舍**、非相机不支持 | `00_项目总结/01_成果总表.md:12` |
| **H3** | 6K PHOTO 片门全开 \| ✓ \| `6k4k_photo` 可写，原生支持 | `00_项目总结/01_成果总表.md:13` |
| **H4** | 47 个可写设置域 \| ✓ \| `setsetting` 状态写，已证明的唯一可控原语 | `00_项目总结/01_成果总表.md:14` |
| **H5** | CAMSET 校验和可伪造 \| ✓ \| `byte[65532]=(256−Σ) mod 256` | `00_项目总结/01_成果总表.md:15` |
| **H6** | hlg=8k 隐藏档 \| ◐ \| 写入 ok，play 模式读回仍 off（模式门控） | `00_项目总结/01_成果总表.md:16` |
| **H7** | mp4hevc 容器 \| ✓→弃用 \| `3062=0x08` 可落地，画质固件派生；按需求最终弃用 | `00_项目总结/01_成果总表.md:17` |

### F 固件/AES 侧成果（F1–F5） —— 5 条

定义出处：`00_项目总结/01_成果总表.md`

| 编号 | 一句话结论 / 内容（原样摘录） | 出处 |
| --- | --- | --- |
| **F1** | AES 密钥不可离线提取 \| ✗(终局) \| 密钥在 MC801 芯片 OTP/eFuse，不在固件/转接环/I2C | `00_项目总结/01_成果总表.md:33` |
| **F2** | 版本门不可改号绕过 \| ✗ \| `comm_proto_ver` 字段方向 + 无比较逻辑 | `00_项目总结/01_成果总表.md:34` |
| **F3** | UPD 格式 / 启动链已解析 \| ✓ \| `s5_layout.json`、parts、`s5_ptp_dump` | `00_项目总结/01_成果总表.md:35` |
| **F4** | 固件升级 = 改内容原语 \| ✓(协议) \| 一旦 endsenddata 成功 = 重写 rootfs | `00_项目总结/01_成果总表.md:36` |
| **F5** | 最终-chunk flash 定址失败 \| ◐(阻塞) \| ~31s 定址超时/磨损，未打通 | `00_项目总结/01_成果总表.md:37` |

### F S1RM2 f_fs OOB 缺陷清单（F3–F8，文件内编号） —— 6 条

定义出处：`01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/S1RM2-ffs-OOB-漏洞报告-中文.md`

| 编号 | 一句话结论 / 内容（原样摘录） | 出处 |
| --- | --- | --- |
| **F3** | 高 \| `FUNCTIONFS_PHYSICAL_ADDR` / `PHYADDR_REMAP` 直接 `phys_to_virt()`/`ioremap_wc()`，无地址/长度校验，且绕过 `copy_from_user` \| 本地（需用户态守护进程配合） | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/S1RM2-ffs-OOB-漏洞报告-中文.md:170` |
| **F4** | 高 \| `ioremap_wc()` 返回值不检查 + `data_len` 无上限 → 可能野 DMA \| 本地 | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/S1RM2-ffs-OOB-漏洞报告-中文.md:171` |
| **F5** | 高 \| AIO 路径对非堆地址 `kfree`（`phys_to_virt` 结果 / ioremap 地址） \| 本地（需 AIO） | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/S1RM2-ffs-OOB-漏洞报告-中文.md:172` |
| **F6** | 中 \| 无锁遍历 DWC3 `started_list`（`#include "../../dwc3/gadget.h"` 分层违规） \| USB 主机（需时序） | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/S1RM2-ffs-OOB-漏洞报告-中文.md:173` |
| **F7** | 中 \| 持自旋锁 + 关中断时 `copy_from_user` \| 本地 | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/S1RM2-ffs-OOB-漏洞报告-中文.md:174` |
| **F8** | 中 \| 未知 alt → 端点全关且不再开（功能级 DoS） \| USB 主机（一行请求） | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/S1RM2-ffs-OOB-漏洞报告-中文.md:175` |

### E HTTP/SOAP 审计条目（E1–E15，文件内编号） —— 15 条

定义出处：`19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md`

| 编号 | 一句话结论 / 内容（原样摘录） | 出处 |
| --- | --- | --- |
| **E1** | `0x092ae4` → `0x0928b4` 请求 URI 解码 \| 栈/结构体溢出 \| 输入 ≤255，解码**不放大**，输出+NUL ≤256 = 字段 `base0+0x19C` 精确大小 ⇒ **恰好填满** | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:432` |
| **E2** | `0x0d6b58` Host 头 \| 结构体溢出 \| 限长 ≤31，字段 `base0+0x29C` 至 0x2BC = **32 B** ⇒ **恰好填满** | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:433` |
| **E3** | `0x0d7204` Content-Type 头 \| 结构体溢出 \| 限长 ≤127，字段 0x18→0x98 = **128 B** ⇒ **恰好填满** | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:434` |
| **E4** | `0x0d717c` contentFeatures 头 \| 结构体溢出 \| 限长 ≤199，字段 0x98→0x160 = **200 B** ⇒ **恰好填满** | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:435` |
| **E5** | `0x0d6fe8` Content-Length 头 \| 整型溢出 / 分配型溢出 \| `0x95e4c` 有 ≤0x0000FFFFFFFFFFFF 范围检查、不接受负号；值只作剩余计数，不参与任何分配或拷贝长度（`0x0938c0`） | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:436` |
| **E6** | `0x0938c0` 体长度消费 \| 越读/越拷 \| `n = min(Content-Length, strlen(可用))`，`ldrd/subs/sbc` 64 位递减，游标推进量恒 ≤ 实际字节数 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:437` |
| **E7** | `0x0931f4` 头分派器 \| 越界写 \| 只做指针切分与 `*p = 0`，写点都在已接收报文体内部；21 项表循环边界 `cmp r3,#20 / ble` 正确 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:438` |
| **E8** | `0x0efb20` CALLBACK URL 解析 \| 无界 strncpy \| `n = colon − p` 被 `cmp r3,#15 / ble` 门住；目标区 500 B | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:439` |
| **E9** | 21 个头处理函数中的 17 个 \| 任意 \| `tools/sites.py 0xd66e8 0xd7b2c` 全量扫描：**只有 5 个危险调用点**（Accept×2、Host、contentFeatures、Content-Type） | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:440` |
| **E10** | `0x0b9934` 6×strcpy \| 栈溢出 \| 源为静态名字表，最长 30 字符 < `memset(.,0,129)` 的 129 B | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:441` |
| **E11** | `0x0db780` + SSDP 广播缓存 `0x0da64c` \| 结构体溢出 \| `dst[maxlen-1]=0` + 截断检测；IP 16 / Server 64 / Location 261 与字段边界 `0x00/0x10/0x50/0x155` 精确吻合 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:442` |
| **E12** | `0x0f3f8c` / `0x0f3a6c` 的 5 个 memcpy \| 栈溢出 \| 全部 `mov r2,#12` 常量长度，源/目标均为 12 字节结构体槽 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:443` |
| **E13** | `0x0f3f8c` 请求行 HTTP 版本解析（`0xf40d8`） \| 越界读/写 \| 局部 20 B 缓冲 `memset(.,0,20)` 后仅拷 19 B ⇒ `buf[19]` 恒为 0，循环必然终止；写下标 ≤19 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:444` |
| **E14** | `0x0d69b8` Accept 头（**候选 1 的可利用性排除**） \| 结构体溢出 \| 越界 ≤3 字节，但 `base0+0x2c8` 之后 560 字节（至 `base1`）**全二进制无任何引用**（`#712/#713` 仅 3 处、全在本 handler 内；`#10240/#11520`+第二 add 模式在 `base+0x2c0..0x4f8` 无命中）⇒ 无破坏目标 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:445` |
| **E15** | `0x0d26bc` / `0x0d20f0` XML 生成器（**候选 2 的可利用性未定**） \| 全局缓冲溢出 \| 缓冲 `0x219030` 大小 **24813 B**；拼接内容为静态片段表 + 配置串；**无长度检查但余量极大**，缺一条"配置串可超长"的路径 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:446` |

### E SOAP 动作/XML 审计条目（E16–E24，文件内编号） —— 9 条

定义出处：`19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md`

| 编号 | 一句话结论 / 内容（原样摘录） | 出处 |
| --- | --- | --- |
| **E16** | `0xe969c` `upp_av_xml_strcat` \| 追加型溢出 / off-by-one \| 条件 `W + A < B`（无符号严格小于）⇒ 最大被触碰下标 `W+A ≤ B−1`，NUL 恰好落在 `B−1`。**记账有效且保守 1 字节** | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:396` |
| **E17** | `0xe9794` 转义追加（放大 4–6 倍） \| 放大绕过记账 \| **逐字符**重算 `strlen(dst)` 并重判 `W + A < B`；`&lt;`/`&gt;`/`&quot;`/`&amp;`/`&apos;` 五种单元长度 4/4/6/5/6 均正确计入 | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:397` |
| **E18** | `0xe9ab0` 第二份转义实例 \| 同上 \| 与 E17 逐指令同构（`0xe9c14`–`0xe9c54`） | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:398` |
| **E19** | `0x4b734` XML 词法切分器 \| u16 数组越界写 \| 循环顶部 `if (count >= out_bytes/2 − 1) break`；退出时写 `out[count]`，下标 ≤ `out_bytes/2 − 1`。内部 8 项栈数组另有 `counter < 8` 独立保护 | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:399` |
| **E20** | `0x55778` 词法展开器 \| 越界写 \| `memset(out, 0, maxlen*2)`；循环 `if (maxlen−1 ≤ i) return −124` ⇒ `i ≤ maxlen−2`。调用方传 3072，目标为 6144 B 局部缓冲（`0x54c40` 帧 6184 B）⇒ 恰好容纳 | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:400` |
| **E21** | `0x54078` UTF-16→Latin-1 转码 \| 越界写 \| `i` 仅在 `maxlen > i+1` 时自增 ⇒ `i ≤ maxlen−1`，`dst[i]=0` 落在 ≤ `maxlen−1`。调用侧缓冲 1024 B、`maxlen=1024` ⇒ **恰好填满** | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:401` |
| **E22** | `0xb49e4` / `0xba6f8`（32 KB 动作代码） \| 全部 289 个 memcpy \| **全部为常量长度 2–24 B**，源为 rodata 静态串（`"GetSearchCapabilities"`=22、`"GetProtocolInfo"`=16…），目标为 713 B 步长表项且先 memset。**输入不来自网络** | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:402` |
| **E23** | `0xba574` `sprintf("%ld")` 进 4 B 缓冲（**本轮最险**） \| 栈溢出 → 野指针写 \| `tmp` = `fp−20`，仅 4 B（`memset(.,0,4)`）；`fp−16` 是**随后被读回使用**的指针 ⇒ 若 `%ld` ≥5 字符即污染 base → `strncpy(base+0x29C, tmp, 3)` 野指针写。**但 `arg0` 被静态表 `0x11e020` 锁死为 {−401,−402,−404,−501,−701…−707} ⇒ `%ld` 恒 3 位数字+NUL = 4 B，恰好填满** | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:403` |
| **E24** | `0xb9934` `sprintf("%d")` + `strncpy(…,12)` \| 栈溢出 \| `memset(tmp,0,12)`；32 位 `%d` 最长 `-2147483648` = 11 字符 + NUL = 12 ⇒ **恰好填满** | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:404` |

### E SSDP/GENA 审计条目（E1–E12，文件内编号） —— 15 条

定义出处：`19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md`

| 编号 | 一句话结论 / 内容（原样摘录） | 出处 |
| --- | --- | --- |
| **E1** | `0xa0e20` \| `nce_upnp_mem_header_strncpy(dst,node,size)` \| 内部 `size-1` clamp + 逐节点 `strncpy` + 剩余量递减 \| `0xa0ea0`–`0xa0ebc`、`0xa0f30`–`0xa0f60` **[实测]** | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:351` |
| **E2** | `0xa11b4` \| 链长度统计（带上限） \| 只读遍历，`cmp` 命中上限即返回；不写内存 \| `0xa1238`–`0xa125c` **[实测]** | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:352` |
| **E3** | `0xa0074` \| 链总长统计 \| 只读累加，返回 `total - node->len` \| 全函数无 store **[实测]** | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:353` |
| **E4** | `0xa3bdc` \| HTTP 头行切分（栈 4096 B） \| 入口检查 `len <= 4096`；`memset(buf,0,4096)`；`memcpy` 长度受同一检查约束 \| `0xa3c58`–`0xa3c68`、`0xa3c94`–`0xa3ca0` **[实测]** | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:354` |
| **E5** | `0x9a740` \| M-SEARCH `ST:`/`MAN:`/`MX:` 解析 \| `strncpy(...,16)`；`MX` 经 `cmp #120` 截断 \| `0x9a838`、`0x9e84c` **[实测]** | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:355` |
| **E6** | `0x9e1ac` \| SSDP 头部字段分派 \| 各字段固定长度（4/80/16 B）并配 `cmp #3 / #79 / #15` 检查 \| `0x9e6a0`、`0x9e6dc`、`0x9e768` **[实测]** | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:356` |
| **E7** | `0x9a83c`/`0x9a97c` \| `strncpy` 到 `fp-36` \| 常数 16 \| **[实测]** | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:357` |
| **E8** | 客户端 SSDP 应答解析 `0x992d8`/`0x99ad8`/`0x99f6c` \| 报文解析 \| 该三函数**不含任何 `strcpy`/`strcat`/`memcpy`**；只有 `memset`/`strlen`/`strcasecmp`/`strncasecmp` \| 逐 `bl` 目标扫描 **[实测]** | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:358` |
| **E9** | GENA `CALLBACK`/`SID`/`NT` 提取 \| 客户端字段进栈 \| `0xa0e20` 上限 260 / 132，均落在对应区段内 \| §4.2 **[实测]** | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:359` |
| **E10** | `0xa1440` \| 自研 `sprintf`（链式缓冲） \| 按需增长缓冲，`%s` 前先 `strlen` 再追加（`0xa1534`–`0xa1558`） \| **[实测]** | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:360` |
| **E10b** | `0xa15d8`–`0xa15f8` \| 上一函数内部的 `sprintf(dst=fp-64)` \| 唯一 `%d` 分支，格式串取自池 `0xa1868` = **`"%d"`**（另有 `0xa1870` = `"%x"`）；32 位整数最长 11 字符 < 64 \| **[实测]**（核对池值） | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:361` |
| **E10c** | `0xe969c` \| `nce_upnp_util_strlcat(dst, src, cap)` \| 入口先 `strlen(dst)+strlen(src) >= cap` 即返回错误码 \| `0xe96fc`–`0xe971c` **[实测]** | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:362` |
| **E10d** | `0xa0f60` / `0xa0f00` \| 链字段 `strncpy` \| 长度先被 clamp 到 `size-1`，循环内按剩余量递减 \| **[实测]** | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:363` |
| **E11** | `0xef900` 的 `strncpy` 家族（19 处） \| GENA 响应构造 \| 全部为常数长度（16/32/132） \| **[实测]** | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:364` |
| **E12** | `0xb0218`、`0xb03e8` \| `strcpy` + `ioctl(SIOCGIFHWADDR)` \| 源为内核返回的接口名（`NETUTIL_GetEtherDevName`），非报文可控 \| **[强推断]** | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:365` |

### E SSDP 入站取值审计条目（E1–E13 + U1，文件内编号） —— 13 条

定义出处：`19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md`

| 编号 | 一句话结论 / 内容（原样摘录） | 出处 |
| --- | --- | --- |
| **E1** | `0x9e1ac` 是否有非栈 store \| **0 处** \| §3.1 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:250` |
| **E2** | `0x9a740` 是否有非栈 store \| **0 处** \| §3.1 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:251` |
| **E3** | 入站子树（105 函数）是否有非栈 store \| **0 处** \| §3.1 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:252` |
| **E4** | 入站子树内 56 处库函数写入的目的地 \| 46 栈 + 6 链缓冲 + 1 静态槽池 + 3 未判定 \| §3.2 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:253` |
| **E5** | `0x9a740` 内 `strncpy` 长度 \| **均为立即数 16**（两处） \| §2.1 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:254` |
| **E6** | `0xab50c`（发包器）内是否有字符串拷贝 \| **0 处**（全量 grep） \| §2.3 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:255` |
| **E7** | `0x9e1ac` 内字段提取的长度参数 \| 立即数 `19` / `4` / `80` / `16`（`0x9e374`/`0x9e69c`/`0x9e720`/`0x9e7a8`）+ `0xa0e20` 内部 clamp \| §2.2 / 第一份报告 §五 E1 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:256` |
| **E8** | `MX:` 是否被截断 \| **是**，`cmp #120`（`0x9e84c`–`0x9e858`） \| §2.2 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:257` |
| **E9** | `USER-AGENT` / 未知头是否有落点 \| **无**（`0x9a740` 内无该字符串引用；解析器跳过未知头） \| §2.2 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:258` |
| **E10** | 报文缓冲是否驻留 \| **否**，每分支收尾 `bl db54c`（释放），8 处 \| §4.1 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:259` |
| **E11** | 回调槽池索引是否有界 \| **是**，`cmp r3,#255; bls`（`0x9eae0`） \| §4.2 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:260` |
| **E12** | 回调槽写入是否越槽 \| **否**，`+0x18+212 = 236 ≤ 244` \| §4.2 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:261` |
| **E13** | 源槽能否被入站报文写入 \| **否** \| §4.1 + §4.2 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:262` |

### E- 自我纠错条目（E-1–E-4） —— 4 条

定义出处：`14_总包审计与新方向_20261014/README.md`

| 编号 | 一句话结论 / 内容（原样摘录） | 出处 |
| --- | --- | --- |
| **E-1** | 我在 `03_新方向与实验设计.md` 方向 5 写的「CBC 且明文全零 ⇒ 所有密文块必须相同」**是错的**。块全同是 **ECB + 常量明文**的指纹；CBC + 全零是迭代链，块基本全不同（自造样本实测 CBC→256/256 全不同、ECB→1）。故 `ipu_data` 的 `16384/16384` **只能排除 ECB**，CBC/CTR 不可区分 \| **已修正**该文件 | `14_总包审计与新方向_20261014/README.md:109` |
| **E-2** | 「60606 控制面 403」不是请求格式问题：我按项目自有 App 的原样（`User-Agent: Panasonic MIL DLNA CP UPnP/1.0` + SOAPAction 不加引号 + `<s:` 前缀信封）复现，并跑 10 个变体，**控制面一律 403、静态描述一律 200** ⇒ 是**会话门**，不是格式 \| 结论**维持并加固** | `14_总包审计与新方向_20261014/README.md:110` |
| **E-3** | 项目 iOS App 声称 DLNA Browse 可用，但**库内无任何成功证据**（全部 60606 证据只是设备描述本身 200）。我的实测也 403 \| **列为未验证主张** | `14_总包审计与新方向_20261014/README.md:111` |
| **E-4** | **项目把 `0x220` 的 64B 当「ECDSA P-256 签名」使用，其源头已自我撤回**：`07_参考仓库/s1m2-research/docs/CORRECTIONS.md` 明文把「外层 ECDSA 字段与签名机制**已经确认**」更正为「字段名称**是候选**；**没有签名验证和完整机制证据**」。而项目据此推出「版本字段在签名覆盖内 ⇒ 改版本号必然破坏签名」 \| **整条链降级为候选假设**；「改版本号绕过版本门」的**证伪依据也不再成立**（既不能支持"能绕过"，也不能支持"必然被拒"）。已回填 `00_审计总报告.md` §3 补充与 `03_新方向与实验设计.md` 方向 2/3 | `14_总包审计与新方向_20261014/README.md:112` |

### N-S5 新增结论（N-S5-1–N-S5-4） —— 4 条

定义出处：`18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md`

| 编号 | 一句话结论 / 内容（原样摘录） | 出处 |
| --- | --- | --- |
| **N-S5-1** | **K32 预言机在 S5 的产出 = 5 节 0x3BD000 B（4.47%）：music/koutei_kao/eep_act_a/b/ipu_data；boot 链与 program 无孪生（逐节 K32 互异）**；S5 五版本 boot 链 K32 恒同、program 逐版变 \| 实测确认 | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:227` |
| **N-S5-2** | **G100 program 内 AES 模块有真实调用者（≥5 区域、Thumb 87+ARM 15 调用点；更新路径/NAND 写 API 区间仍为 0）**——同事报告结论 9 的调用者普查漏了 Thumb 侧，需窄化为"更新路径不调用" \| 实测确认（抽查 3 处反汇编连贯） | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:228` |
| **N-S5-3** | AES 前端经固定槽 0x0584961E/0x0584966C/0x058499C0 运行时间接分发，槽内容容器内不可解析 ⇒ 解密后端为运行时接线或片上；0x04EF7xxx 为 HMAC-SHA256 类原语（固定密钥 dword_515E6BC），与 AES/CTR 同区 \| 实测确认（槽存在）+ 强推断（后端位置） | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:229` |
| **N-S5-4** | G100 与 S5 boot/OS 节**load addr 逐节相同**（loader1@0x0、program@0x80000、zboot@0x3B00000/0x3220000 同族）⇒ 同代同内存布局，G100 的地址图可作为 S5 运行时探针的候选地图（非精确） \| 实测确认 | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:230` |

### T exFAT 长文件名崩溃实验分组（T1–T3） —— 3 条

定义出处：`01_研究报告/23_S5_exFAT越界写实机确认_20261013.md`

| 编号 | 一句话结论 / 内容（原样摘录） | 出处 |
| --- | --- | --- |
| **T1** | 仅 10 个长文件名文件 \| 不崩 ⇒ 与数量/资源压力有关；崩 ⇒ 与文件名长度有关 | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:186` |
| **T2** | 240 个**短名**文件（无效内容） \| 不崩 ⇒ 内容无关；崩 ⇒ 与数量有关 | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:187` |
| **T3** | 240 个长名**真 JPEG**（相机照片副本） \| 崩 ⇒ 与内容无关 | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:188` |

### T 实测运行分组（T1–T3） —— 3 条

定义出处：`11_DC-S5成果包_20261013/01_研究报告_全集/26_本次运行日志_20261013.md`

| 编号 | 一句话结论 / 内容（原样摘录） | 出处 |
| --- | --- | --- |
| **T1** | ~20 \| 240 字符 \| ✅ | `11_DC-S5成果包_20261013/01_研究报告_全集/26_本次运行日志_20261013.md:101` |
| **T2** | 241 \| 12 字符 \| ✅ | `11_DC-S5成果包_20261013/01_研究报告_全集/26_本次运行日志_20261013.md:102` |
| **T3** | 241 \| 240 字符 \| ✅ | `11_DC-S5成果包_20261013/01_研究报告_全集/26_本次运行日志_20261013.md:103` |

### E 累计排除项（E25–E28，续 HTTP/SOAP 的 E1–E24，全局唯一编号） —— 4 条

定义出处：`19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md`

| 编号 | 一句话结论 / 内容（原样摘录） | 出处 |
| --- | --- | --- |
| **E28** | + 1 个候选） | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:4` |
| **E25** | 已排除（恰好填满 + 四重范围检查）。 附带更正：池常量 `0x1869F` 被我的分类器误标为 CODE（它落在 .text 地址区间），实际是数值上限 99999。 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:76` |
| **E26** | `0x0d6560`（Range 值解析）：零拷贝 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:203` |
| **E27** | `0x0db8e4` Branch B（`strcpy@0x0dbdd8`）：恰好填满 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:223` |

### C-1 候选（19_路径1 剩余盲区审计） —— 1 条（1 个编号 / 16 处定义或提及行）

定义出处：`19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md`

| 编号 | 该编号的全部提及行（原样摘录） | 出处 |
| --- | --- | --- |
| **C-1** | 新增候选 \| 1 项（C-1，见 §二） \| | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:19` |
| **C-1** | 二、② 的 Branch A —— 本轮唯一候选 C-1（置信度：中） | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:80` |
| **C-1** | C-1 【候选｜中置信度】订阅者节点 `+0x114` 字段的 `strcpy` 可能溢出 31 字节并污染链表 `next` 指针 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:82` |
| **C-1** | dlna \| 本轮完成 HTTP/SOAP/XML/SSDP 解析层的逐点审计 \| 28 项已排除，1 项中置信度候选（C-1） \| | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:350` |
| **C-1** | 全部结论来自离线反汇编；未连接相机、未发送任何报文、未做模糊测试。C-1 未做任何活体验证，也不建议在确认前做。 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:393` |
| **C-1** | C-1 是"中置信度候选"，不是"确认漏洞"：目标字段 80 B 由两处 `strncpy(...,80)` 与 `+0x16C` 上界夹出（强推断）；源 ≤111 由"指针落在 260 B 缓冲 +148 处"推出（强推断）；但"解析器能否真在该位置留下 >80 字符的串"未验证。在完成 §二末的复核前，不应把它计入"已确认漏洞"。 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:395` |
| **C-1** | 附：C-1 源界定专项（2026-10-15 追加） | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:401` |
| **C-1** | 结论先行：C-1 未能确认为漏洞，也未能干净排除 —— 判定为"未定，倾向排除"。 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:403` |
| **C-1** | 附-3 C-1 最终判定 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:500` |
| **C-1** | 判定：C-1 未定（倾向排除）——不作为漏洞主张 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:510` |
| **C-1** | 最终判定：C-1（2026-10-15 定论轮） | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:547` |
| **C-1** | 结论：C-1 不构成可控写原语，从漏洞清单中移除。 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:551` |
| **C-1** | ★ 前置 SUBSCRIBE 本身是否需要认证？ \| 不需要 ⇒ 整条链免认证 \| 这两件事是同一个函数：`0xefb20` 既是 SUBSCRIBE 的处理器（豁免门之前），又是 `0xdb8e4` 的唯一调用者（`0xf1d38`）。因此"C-1 需要先有一次成功 SUBSCRIBE"这个前置条件本身也在免认证状态下即可达成，无需 accctrl 握手 \| | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:631` |
| **C-1** | ⇒ C-1 的门槛性质 \| 免认证（若它成立的话）\| — \| | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:632` |
| **C-1** | C-1 \| 从"中置信度候选"→【排除】，并从漏洞清单移除 \| | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:656` |
| **C-1** | 「已排除」总数 \| 28 项（E1–E28）+ C-1 = 29 项 \| | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:658` |

---

## 表 3 · 全项目「已排除 / 已证伪 / 失败」清单

共 **1073** 条。**这是防重复劳动的主索引**：凡在此表出现过的路线，除有新证据外不要再试。

关键词口径：`已排除` `证伪` `阴性` `不可行` `死路` `全部失败` `无 RCE` `排除` `零命中` `零收敛` `不成立` `未复现` `不可逆砖` `✗` `❌` `失败`。

| # | 试了什么 / 对象（原样） | 结论（原样） | 出处 |
| --- | --- | --- | --- |
| 1 | 证据强度标记 | ✓=已实机/协议闭合 · ◐=有强证据但未完全闭合 · ✗=已证伪 | `00_项目总结/00_执行摘要_全文.md:5` |
| 2 | 固件 AES 密钥提取与网络 RCE 均为阴性；物理/调试侧（拆机 UART/JTAG 读运行时明文）是绕开 AES 最现实的高价值路径。 | 固件 AES 密钥提取与网络 RCE 均为阴性； | `00_项目总结/00_执行摘要_全文.md:23` |
| 3 | 结论（✗ 终局否定） |  | `00_项目总结/00_执行摘要_全文.md:29` |
| 4 | 离线 130k+ 探测、40/41 加密分区、真实 256KB keystream，均无法恢复密钥。 |  | `00_项目总结/00_执行摘要_全文.md:31` |
| 5 | 能干净流送全部 1474 个完整 61192B 块，但最终部分块（41456B）始终失败 | 触发 ~31s flash 定址 → `err_busy`（慢）→ 重试 `err_critical`（快）。 | `00_项目总结/00_执行摘要_全文.md:48` |
| 6 | 与内容无关（发的是未改动的真 V29 镜像）、与节奏无关（87ms 与 158ms/chunk 都失败）、与状态无关（拔电池重启后仍复现）。 |  | `00_项目总结/00_执行摘要_全文.md:49` |
| 7 | 只有真 90MB 镜像能走到 flash 定址；小镜像在"固件合法性"关就被拒。真实 90MB 的 ~31s 定址失败，最可能是内部 flash 对大镜像末块的擦/写超时或磨损。 | 真实 90MB 的 ~31s 定址失败，最可能是内部 flash 对大镜像末块的擦/写超时或磨损。 | `00_项目总结/00_执行摘要_全文.md:50` |
| 8 | RCE / 代码注入（✗ 全阴性，仅 1 条未测） |  | `00_项目总结/00_执行摘要_全文.md:52` |
| 9 | 编译 C / `LD_PRELOAD` 注入（CVE-2017-17562 思路） | 阴性（GoAhead 不把 `LD_*` 传入 CGI 环境，或 cam.cgi 静态链接）。 | `00_项目总结/00_执行摘要_全文.md:53` |
| 10 | HTTP 头/参数溢出 fuzz | 阴性。 | `00_项目总结/00_执行摘要_全文.md:56` |
| 11 | `senddata` 可能长期不响应（在等 `endsenddata`） | `KA.send()` 的 recv() 卡死。不是失败：数据由 sendall 即已送达。 | `00_项目总结/00_执行摘要_全文.md:127` |
| 12 | S1R2 已排除路线对 S5 的修正 |  | `00_项目总结/00_执行摘要_全文.md:141` |
| 13 | UART | S1R2 实测 `BOOTDELAY=-2` + `console=null` 为死路 → S5 不能直接套用， | `00_项目总结/00_执行摘要_全文.md:142` |
| 14 | SD.DAT | S1R2（NAND）实测无只读模式、写错 `pardata.par` = 不可逆砖 → S5 上降级为 | `00_项目总结/00_执行摘要_全文.md:144` |
| 15 | 证据强度 | ✓=已实机/协议闭合 · ◐=有强证据未完全闭合 · ✗=已证伪 | `00_项目总结/01_成果总表.md:3` |
| 16 | F1 | AES 密钥不可离线提取 \| ✗(终局) \| 密钥在 MC801 芯片 OTP/eFuse，不在固件/转接环/I2C | `00_项目总结/01_成果总表.md:33` |
| 17 | F2 | 版本门不可改号绕过 \| ✗ \| `comm_proto_ver` 字段方向 + 无比较逻辑 | `00_项目总结/01_成果总表.md:34` |
| 18 | F5 | 最终-chunk flash 定址失败 \| ◐(阻塞) \| ~31s 定址超时/磨损，未打通 | `00_项目总结/01_成果总表.md:37` |
| 19 | W5 | 网络 RCE（各路线） \| ✗ \| GoAhead 溢出/LD_PRELOAD/file-op/exec 全失败 | `00_项目总结/01_成果总表.md:47` |
| 20 | C6 | S1R2 排除路线 → S5 修正 \| ✓ \| UART 需先核验 S5 console 配置（S1R2 console=null 死路不可直接套用）；SD.DAT 降级为 JTAG 后备胎（NAND 教训） | `00_项目总结/01_成果总表.md:79` |
| 21 | RCE 各路线（GoAhead 溢出、LD_PRELOAD、file-op/exec）全阴性；HTTP 头/参数 fuzz 阴性。 | RCE 各路线（GoAhead 溢出、LD_PRELOAD、file-op/exec）全阴性； HTTP 头/参数 fuzz 阴性。 | `00_项目总结/02_项目时间线.md:13` |
| 22 | 固件升级写路径 | 流送全部完整块成功，最终部分块 flash 定址失败（~31s）。 | `00_项目总结/02_项目时间线.md:14` |
| 23 | （中途曾被判"证伪"，10-13 查明系上传协议 bug，最终确认成立，见下。） | （中途曾被判"证伪"，10-13 查明系上传协议 bug，最终确认成立，见下。 | `00_项目总结/02_项目时间线.md:26` |
| 24 | （CAMSET 9.2MB 读写 + FunctionFS OOB F1/F2 移交原件、已排除路线风险备忘、`00_S5结合点与AES路径总结.md`）。 |  | `00_项目总结/02_项目时间线.md:37` |
| 25 | 交叉校验修正 AES 路径 | UART 需先离线核验 S5 U-Boot console 配置（S1R2 console=null 死路）、 | `00_项目总结/02_项目时间线.md:38` |
| 26 | 2026-10-13 · 一度判为"持久化证伪" + 容器回落追查（一天内即被更正） |  | `00_项目总结/02_项目时间线.md:41` |
| 27 | 断电终验当时结果 | `ntsc_pal` 与 `videoquality` 持久 ✓，但 `videoformat` 从 mov 回落 mp4 ✗。 | `00_项目总结/02_项目时间线.md:42` |
| 28 | 当时结论 | 「flash 直写三项全部持久」对格式字段不成立；mov 容器尚未真正持久。 | `00_项目总结/02_项目时间线.md:43` |
| 29 | 清理仍在传播已证伪结论的文档 | `README.md`、`00_执行摘要_全文.md` 的"开机即锁定 mov / | `00_项目总结/02_项目时间线.md:54` |
| 30 | slot1 稳定=mov，证明 slot0 之外是真实记忆槽；据此排除"直接提升任一 mov 槽"的 H1 形式， | 据此排除"直接提升任一 mov 槽"的 H1 形式， | `00_项目总结/02_项目时间线.md:59` |
| 31 | 执行影子槽实验时，写盘前的 blob 下载失败（原 20s 超时 < 相机 90–200s 的 68KB 响应）， |  | `00_项目总结/02_项目时间线.md:79` |
| 32 | 结论更正 | 早先"mov 被固件重新派生为 mp4"不成立，H2「固件白名单」无证据支持，撤下； | `00_项目总结/02_项目时间线.md:90` |
| 33 | （10-14 更正 4） 本行「`0xf4` 跨断电保留」不成立 | 该次写入是空操作（见上「更正 3」）， | `00_项目总结/02_项目时间线.md:123` |
| 34 | 并记录两类失败 | `setter=ok` 但 `getter=err_critical`、静默映射到别的格式。 | `00_项目总结/02_项目时间线.md:142` |
| 35 | 但显式写任意 `mp4ed_*` 质量 token 全部失败（44 个 NTSC 候选 0 个读回正常）。 |  | `00_项目总结/02_项目时间线.md:144` |
| 36 | 条目可见与菜单变灰是同一失配的两面，无法同时满足；且 S5 没有 S1H 的"添加到列表（My List）" |  | `00_项目总结/02_项目时间线.md:159` |
| 37 | （全量菜单扫描无任何 list 项），故无法把隐藏档"注册"成常规入口。 |  | `00_项目总结/02_项目时间线.md:160` |
| 38 | curmenu 独有 `_c4k_10bit` | `mov_50p/60p_200mbps_c4k_10bit` \| `ok` \| ✅ \| ❌ 变灰 | `00_项目总结/02_项目时间线.md:212` |
| 39 | 5.9K | `mov_24p/25p/30p_200mbps_5_9k_10bit`、`mov_5_9k_*_420_10l`、`mov_c24p_*_5_9k_10bit` \| `err_reject` / `err_param` / `ok`但未生效 \| ❌ \| — | `00_项目总结/02_项目时间线.md:213` |
| 40 | 6K | `mov_24p_200mbps_6k_10bit`、`mov_c24p_200mbps_6k_10bit` \| `ok`但未生效 / `err_param` \| ❌ \| — | `00_项目总结/02_项目时间线.md:214` |
| 41 | 400Mbps | `mov_25p_400mbps_c4k_10bit` \| `ok` \| ❌ 回读为空，未生效 \| — | `00_项目总结/02_项目时间线.md:216` |
| 42 | ★ `mov_50p_200mbps_4k_10bit` 实测第 5 次退避重试才成功（`err_reject` 不是失败）。 |  | `00_项目总结/02_项目时间线.md:218` |
| 43 | 全部失败。 与 10-13 的实拍文件头终判（`P1000004.MOV` = C4K 60p，非 5888×3312）两条独立证据同向。 | 全部失败。 | `00_项目总结/02_项目时间线.md:232` |
| 44 | 菜单读的是 RAM 值，不是 flash 值 | "flash 存安全值 + RAM 上隐藏档"的双轨方案不成立（实测证伪）。 | `00_项目总结/02_项目时间线.md:259` |
| 45 | 与 10-13（晚·续3）的 `mp4ed` 现象是同一机制的两个表现面 | 条目可见与菜单变灰无法同时满足； | `00_项目总结/02_项目时间线.md:260` |
| 46 | 且 S5 无 S1H 的"添加到列表（My List）"，无法把隐藏档注册成常规入口。 |  | `00_项目总结/02_项目时间线.md:261` |
| 47 | `err_critical` | 严重状态错误 \| 先重试（`camcmd&value=recmode` 实测重试即 `ok`），仍失败才重启 | `00_项目总结/02_项目时间线.md:270` |
| 48 | 同时把做不到的部分用实验排除，而不是靠推测。 |  | `00_项目总结/03_思路总结_全文.md:11` |
| 49 | ✗ | 已实验证伪 \| AES 密钥离线提取；网络 RCE 各路线 | `00_项目总结/03_思路总结_全文.md:56` |
| 50 | 签名校验 | 改固件内容 → 校验失败（用于确认 UPD 结构） | `00_项目总结/03_思路总结_全文.md:66` |
| 51 | AES 密钥在 MC801 芯片 OTP/eFuse，不在固件/转接环/I2C → 不可离线提取 | ✗（终局） | `00_项目总结/03_思路总结_全文.md:81` |
| 52 | 版本门不可靠改号绕过 | ✗ | `00_项目总结/03_思路总结_全文.md:82` |
| 53 | 最终-chunk flash 定址失败（~31s 超时/磨损）→ 升级路径阻塞 | ◐ | `00_项目总结/03_思路总结_全文.md:85` |
| 54 | 排除的路线（同样有价值） |  | `00_项目总结/03_思路总结_全文.md:122` |
| 55 | 网络 RCE 各路线全失败（GoAhead 溢出 / LD_PRELOAD / file-op / exec） |  | `00_项目总结/03_思路总结_全文.md:125` |
| 56 | 菜单项无法注入 | `allmenu` 由固件提供，普通/工程模式完全一致， | `00_项目总结/03_思路总结_全文.md:126` |
| 57 | S5 无 My List 机制 | "给 6K PHOTO 换个皮塞进录制格式菜单"不可行 | `00_项目总结/03_思路总结_全文.md:127` |
| 58 | 另注意：云盘类 App（夸克网盘）会抢占 USB 设备的 IOUserClient，PTP 调试前需先排除。 |  | `00_项目总结/03_思路总结_全文.md:147` |
| 59 | 任意属性读 | ❌ 相机立即断链（普通模式与配对模式相同） | `00_项目总结/03_思路总结_全文.md:160` |
| 60 | CAMSET 块 65,533 B vs 2,252,861 B（966 条记录） | 跨代移植不可行； | `00_项目总结/03_思路总结_全文.md:208` |
| 61 | 菜单项注入 | ✗ 已证伪 \| 不再投入 | `00_项目总结/03_思路总结_全文.md:231` |
| 62 | "S5 内核越界写已实机确认" | ❌ 撤回 \| 注入必为 NULL 的 slab 填充区索引 → 只报错不崩 ⇒ 存在 NULL 提前返回；原推理"报卡写失败 ⇒ 内存写已执行"不成立 | `00_项目总结/04_定因与工具链成果_20261013.md:38` |
| 63 | "堆喷命中越界槽" | ❌ 撤回 \| A/B 对照：去掉注入后照样重启 ⇒ 崩溃不能归因于注入 | `00_项目总结/04_定因与工具链成果_20261013.md:39` |
| 64 | B | 360 \| 240 字符 \| 576 B \| 6480 \| 202 KB \| ❌ 反复重启 | `00_项目总结/04_定因与工具链成果_20261013.md:52` |
| 65 | B vs C（条目数、体量、跨簇数全同） | 排除"数量/体量" | `00_项目总结/04_定因与工具链成果_20261013.md:56` |
| 66 | B vs D（分配大小全同） | 排除"分配大小" | `00_项目总结/04_定因与工具链成果_20261013.md:57` |
| 67 | B: 360 × 240 = 86 KB → ❌ D: 360 × 12 = 4 KB → ✅ |  | `00_项目总结/04_定因与工具链成果_20261013.md:64` |
| 68 | 症状：照片"文件在、但无法访问/无法删除" |  | `00_项目总结/04_定因与工具链成果_20261013.md:89` |
| 69 | 4 | exFAT 越界写 \| 判定不成立，不再投入 | `00_项目总结/04_定因与工具链成果_20261013.md:164` |
| 70 | `ffprobe`（Homebrew ffmpeg 9.0.1_1） | ❌ 崩溃：`Symbol not found: _av_bprint_finalize` \| 自写 Python 解析 MOV/MP4 box（`tkhd`/`stsd`/`stts`/`stss`） | `00_项目总结/05_环境与依赖.md:78` |
| 71 | `pyusb` / libusb 路径 | ❌ macOS 上 bulk IN 报 `EOVERFLOW`（errno 84） \| 改用 IOKit/IOUSBLib（`s5_ptp_raw`）或 ImageCaptureCore | `00_项目总结/05_环境与依赖.md:79` |
| 72 | ImageCaptureCore（`s5_ptp_dump`） | ❌ 当前 USB 个性（PID `0x2370`，vendor class `0xFF`）不被 macOS 相机栈识别 → 3 分钟超时 \| 自建 `s5_ptp_raw`（绕过主机相机库） | `00_项目总结/05_环境与依赖.md:80` |
| 73 | `airport` 工具 | ❌ macOS 14+ 已移除 \| CoreWLAN（但读 SSID/BSSID 需定位权限，CLI 下返回 nil） | `00_项目总结/05_环境与依赖.md:81` |
| 74 | 免密 `sudo` | ❌ 不可用 \| 抓包等需要 root 的操作只能由用户手动执行 | `00_项目总结/05_环境与依赖.md:82` |
| 75 | Wireshark / dumpcap / tshark | ❌ 未安装 \| 无（Wi-Fi 交换式网络下抓手机↔相机流量本身也不可行） | `00_项目总结/05_环境与依赖.md:83` |
| 76 | 需要给终端开「定位服务」权限，否则无法从 Wi-Fi 侧识别相机热点。 |  | `00_项目总结/05_环境与依赖.md:130` |
| 77 | 目的：把「能否通过修改转接环固件来绕过 S5 固件 AES 加密」这条路线的完整评估、证伪过程与真正可行的路线整理成一份可分发的研究指引。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:3` |
| 78 | │ └── probe_results.md ← 离线破解（XOR/RC4/AES 全模式）阴性汇总 |  | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:23` |
| 79 | 修改转接环固件到不了 S5 固件的 AES 密钥。 对「解锁 `S5___V29.bin`」这个具体目标，转接环是死路 |  | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:56` |
| 80 | 离线穷举失败（130k+ 探测） \| XOR / RC4 / AES-128/192/256 ECB/CBC/CTR，候选密钥含 loader1 24B+64B、0x220 64B 块及 SHA/MD5 派生 | 全未命中（`01/probe_results.md`、`03/…阶段结果汇总` §6/§9） \| | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:85` |
| 81 | 上传"预言机"不能提取密钥（但确有 3 个可利用的验证型预言机，见 §2.3） \| 相机对固件/设置是"验证器" | 版本门、签名校验、CAMSET 校验和；对密钥/明文提取仍是死路——无逐字节反馈、无可利用时差（`03/oracle/oracle_results.md` + `03/oracle/burst_183125/`，2026-10-10 实机实测） \| | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:87` |
| 82 | PTool 旧 GH2 方法不适用 S5 \| 旧机型密钥切片硬编码在明文里；S5 是硬件密钥，移植 120 组合全失败（`03/…阶段结果汇总` §7） \| | S5 是硬件密钥，移植 120 组合全失败（`03/…阶段结果汇总` §7） \| | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:88` |
| 83 | 软件离线解密不可行，密钥提取必须走硬件。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:90` |
| 84 | 2 | 固件签名校验 \| `startsenddata(type=fw)` → 分块 `senddata` → `endsenddata` \| 按 分区 SHA-256 + IV + ECDSA P-256(0x220,64B) + RSA-4096 尾块(0x560EC00) 校验；无效→`err_critical`/`err_reject` \| 容器内无公钥、无禁验开关，无法伪造已签名固件 | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:99` |
| 85 | 结论：Wi-Fi 侧是验证型 oracle（可判定固件新旧 / 签名有效性 / 设置校验和），不是密钥或明文的提取通道。BootROM 在 Wi-Fi 存在之前已运行、且属独立 SDIO 信任域，软件 / Wi-Fi 无法触达；密钥/明文提取仍只能走 §5 的物理/调试路径。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:105` |
| 86 | 3. 为什么转接环路线够不到 S5 的 AES 密钥（证伪） |  | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:109` |
| 87 | ✗ 转接环对以上三者 0 数据通路 ✗ |  | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:120` |
| 88 | 因此「修改转接环固件」在物理上无法触达 S5 固件的 AES 密钥。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:133` |
| 89 | 3.2 转接环固件本身的性质（为何无法"塞"攻击载荷） |  | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:135` |
| 90 | 压缩/加密 \| zlib/deflate/lzma 全失败；最大 64B 滑窗熵仅 5.84；直方图强偏斜 \| 未压缩、未加密（真实数据） \| | 压缩/加密 \| zlib/deflate/lzma 全失败； | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:139` |
| 91 | → 拿到的 `.ecp` 是数据分区，不含 I2C 处理器 / 启动代码 / 中断服务，无法静态定位越界写 bug，也无法在其上叠加攻击逻辑（缺代码镜像）。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:144` |
| 92 | 探针卡口总线行为（I2C 时序、镜头握手、认证失败回包）。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:170` |
| 93 | 「密钥在硬件」是已被软件侧穷尽排除后的结论（130k+ 探测 + 上传 oracle 死路 + 容器无 Key Blob），不是对 AES 密钥空间的穷举证明。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:248` |
| 94 | 硬件路线（§5）全部基于同平台公开先例的推论，S5 本机零验证；任何"可行/不可行"的最终判定需要任务 1~4 的实机结果。 | 任何"可行/不可行"的最终判定需要任务 1~4 的实机结果。 | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:249` |
| 95 | 转接环路线对 S5 AES 密钥的证伪（§3）基于总线拓扑 + SoC 安全域隔离 + 固件镜像性质三重论证；若未来发现 S5 的镜头总线上存在未文档化的调试/内存窗口，需重新评估（当前无证据支持）。 | 转接环路线对 S5 AES 密钥的证伪（§3）基于总线拓扑 + SoC 安全域隔离 + 固件镜像性质三重论证； | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:250` |
| 96 | 软件路线 | 已穷尽（离线 130k+ 探测 + 上传 oracle 死路）→ 不可行。 | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:281` |
| 97 | 转接环路线 | 到不了 MC801 的 AES 密钥（总线不通、密钥不在环上、SoC 家族不匹配）→ 对本目标是死路；但它自己是独立攻击面（可读走环自己的机密）。 | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md:283` |
| 98 | S1M2 已经穷举式排除（不建议重复） |  | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/siegfried82_notes.md:63` |
| 99 | Key Slot / ARM TrustZone），离线纯数学无法突破（2^128 空间）。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/siegfried82_notes.md:68` |
| 100 | `analysis/probe_metadata_keys.py` | 头部字面值/型号串作 AES key 的有限测试 \| 结论已排除，勿重复 | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/siegfried82_notes.md:84` |
| 101 | `analysis/recover_ptool_crypto.py` | PTool 静态表提取 + GH2 阳性对照 + 有限移植探测 \| 仅 GH2；S1M2 已排除 | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/siegfried82_notes.md:85` |
| 102 | 全部未命中。与仓库对 S1M2 的阴性结论一致 | MC801 的密钥也不在固件字面值或这类简单派生里。 | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/siegfried82_notes.md:98` |
| 103 | 无任何可直接解密 MC801 的密钥/算法/脚本。仓库对更新一代 MC8243 的穷举式失败 + 我们的有限探测，都指向 | 仓库对更新一代 MC8243 的穷举式失败 + 我们的有限探测，都指向 | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/siegfried82_notes.md:107` |
| 104 | 路线 A | 找机内运行时明文（RAM dump / 诊断协议）。ROM BACKUP 已被排除（只含校准参数）；需找 PTP 厂商扩展 | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/siegfried82_notes.md:110` |
| 105 | 与完整分区表无法对比，仅能对比头部/安全头区域 | 该区域恰好落在样本内）。 | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/verify_logic_notes.md:7` |
| 106 | Phison 式「公钥在镜像内、可同时替换公钥+签名」攻击不可行 | RSA-4096 与 ECDSA | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/verify_logic_notes.md:17` |
| 107 | ECDSA @0x220 覆盖范围无公钥无法实测，但按结构最可能是外层头（0x0-0x200）， |  | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/verify_logic_notes.md:78` |
| 108 | CRC（可重算，无秘密）但必然破坏 ECDSA 与 RSA-4096（无密钥无法重签）。故 |  | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/verify_logic_notes.md:81` |
| 109 | 仅从明文容器无法判定。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/verify_logic_notes.md:84` |
| 110 | 未做/限制 | 无公钥 → 无法实测 ECDSA/RSA 的覆盖范围与验签结果；完整 S5m2_V31.bin | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/verify_logic_notes.md:119` |
| 111 | 不在本地 | 无法对比 S5m2 尾部 RSA 签名块与完整分区表；不涉及解密、不碰相机。 | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/verify_logic_notes.md:120` |
| 112 | 2010 年代老机型，S1M2 上已证伪，对 MC801 大概率也不适用）。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/williamwu1234_notes.md:13` |
| 113 | `docs/FINDINGS.md` / `docs/CORRECTIONS.md` / `docs/DEAD_ENDS.md`（已验证结论 / 更正 / 死路）。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/williamwu1234_notes.md:27` |
| 114 | 仓库不包含任何固件二进制或 ptool3.exe（`.gitignore` 排除了 `S1m2_V*.bin`、`S1m2_V*.zip`、 |  | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/williamwu1234_notes.md:28` |
| 115 | 仓库里的解密脚本（依赖这些二进制）无法在本机直接跑。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/williamwu1234_notes.md:30` |
| 116 | 解密尝试 | 只做了有界假设排除，没有成功。包括：旧 GH2/PTool 密钥派生（6 张表 × RC4/AES-CBC/混合）、 | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/williamwu1234_notes.md:41` |
| 117 | 更新函数里没有任何组件解码调用；「电脑端解密」假说被证伪。 | 「电脑端解密」假说被证伪。 | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/williamwu1234_notes.md:93` |
| 118 | 离线解密不可行论证（2^128 穷举、无 key blob） | 终局报告 §四 \| 对我们 MC801 同样适用 | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/williamwu1234_notes.md:112` |
| 119 | `analysis/sources/ptool_static/ptool3.exe`、`S1m2_V14.bin`、`GH2__V11.bin` 均未提交，无法运行。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/williamwu1234_notes.md:116` |
| 120 | key blob、上位机不解密、离线穷举不可行；这一结论大概率同样适用于 MC801（MC801 同样有每分区 IV | key blob、上位机不解密、离线穷举不可行； | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/williamwu1234_notes.md:124` |
| 121 | 泄露未加密 loader | 与仓库对 S1M2 给出的路线 A/B 相同，纯离线数学破解被论证为不可行。 | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/williamwu1234_notes.md:128` |
| 122 | 【路径 A | 原板通电通信正常】 【路径 B：原板损坏无法开机】 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_ROM_BACKUP与原厂维修协议逆向推导报告_20261009.md:68` |
| 123 | 外部 PTP 接口和配置注入无法绕过机内拍照流水线的硬编码互斥（电子快门绑定）； |  | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_ROM_BACKUP与原厂维修协议逆向推导报告_20261009.md:139` |
| 124 | 核心瓶颈依然回到 专有固件 49 个编码组件的离线静态解码，或者通过合法途径取得内部开发加载器。当前证据链已完整排除了“外部调整工具可直接解锁机内功能”的假说。 | 当前证据链已完整排除了“外部调整工具可直接解锁机内功能”的假说。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_ROM_BACKUP与原厂维修协议逆向推导报告_20261009.md:140` |
| 125 | ptp.h 中有 Panasonic 的属性读取、设置、拍摄、取景、事件和对象传输操作码，以及 ISO、快门、光圈等属性定义。config.c 有 Panasonic 手动对焦、取景、Bulb 等实现。所读 library.c 对 S1M2 的精确文本检索未命中；这只能说明该文件未列此名字，不能排除通用 PTP 支持。 | 这只能说明该文件未列此名字，不能排除通用 PTP 支持。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_公开入口核查与下一步.md:36` |
| 126 | 网页工具可读取资料；本地 curl 尝试 GitHub API 时 DNS 失败，未保存上游源码快照。这是终端联网限制，尚未阻断网页调查。 | 本地 curl 尝试 GitHub API 时 DNS 失败，未保存上游源码快照。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_公开入口核查与下一步.md:50` |
| 127 | `read_mem` 仍调用 `valid_phys_addr_range`，失败返回 `-EFAULT`。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_公开入口核查与下一步.md:67` |
| 128 | 因此可排除这个公开实现对上述全 FF 假设的直接适用。不能排除额外链式模式、逐块不同密钥、压缩/预处理或其他构造；也不能因此确认 S1M2 采用 AES。 | 因此可排除这个公开实现对上述全 FF 假设的直接适用。 不能排除额外链式模式、逐块不同密钥、压缩/预处理或其他构造； | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_公开入口核查与下一步.md:103` |
| 129 | 两包的 `loader1`、`program`、`hr_c_prog`、`hr_d_prog` 目录散列不同，目录数量与组成也不同。所以“相同封装家族、存在共享组件线索”已有直接证据，“整套固件相同或可互刷”则不成立。Leica 官方下载页明确该包仅兼容 SL3。 | 所以“相同封装家族、存在共享组件线索”已有直接证据，“整套固件相同或可互刷”则不成立。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_公开入口核查与下一步.md:143` |
| 130 | 这些候选包含头部/目录每个字节起点的 16/24/32 字节、XOR FF 变体及字段 MD5/SHA-256。不是密钥空间穷举，没有据阴性结果确认 AES/AEAD/OTP/eFuse，也不排除压缩、派生 key、逐块 key 或其他算法。全 FF 候选明文本身仍待解码证明。 | 不是密钥空间穷举，没有据阴性结果确认 AES/AEAD/OTP/eFuse，也不排除压缩、派生 key、逐块 key 或其他算法。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_公开入口核查与下一步.md:167` |
| 131 | 此前扫描只覆盖 PE 展开表中的函数。实际追踪 `0x2c97` 的直接调用发现 `0xc280` 是未出现在该表中的叶函数，不能用之前的阴性结果概括整个 DLL。已扩展 `audit_lumix_sdk_binary.py`，对代码段做补充线性扫描，并保存命令分类表、30 个直接调用位置与关键路径反汇编。结果统一保存在 `analysis/lumix_sdk_command_classes.json`，脚本仅解析字节，不执行 DLL。 | 实际追踪 `0x2c97` 的直接调用发现 `0xc280` 是未出现在该表中的叶函数，不能用之前的阴性结果概括整个 DLL。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_公开入口核查与下一步.md:215` |
| 132 | 文件读取辅助函数 0x41cbc 起，使用 open/stat、按文件大小分配缓冲并 read，返回数据指针和大小。在这个读取函数内没有观察到组件解码操作；不能据此排除其他未查路径。 | 不能据此排除其他未查路径。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_公开入口核查与下一步.md:251` |
| 133 | `audit_tether_aw_update_path.py` 按库散列固定七个 arm64 函数并提取静态路径，结果为 `tether_aw_update_path.json`。其中 `Send_FWUP_Data` 用 0x7d000（512000 字节，不是 512 KiB）计算分块数，0x4228c 将原始文件缓冲基址加上累计偏移作为发送指针，0x42298 调用 Send_Data；该函数于 0x428dc memcpy 到传输缓冲，0x42830 使用 0x9607。0x9606 发送前置数据说明。在… | 通用传输保护和未查调用者不能据此一并排除。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_公开入口核查与下一步.md:262` |
| 134 | 2026-10-07。本轮继续离线逆向，完成旧款解码流程还原、阳性验证、S1M2 跨版本对照与更严格的密钥假设排除。S1M2 的 49 个编码组件仍未解码；完整程序逆向未完成。 | 本轮继续离线逆向，完成旧款解码流程还原、阳性验证、S1M2 跨版本对照与更严格的密钥假设排除。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_解码突破记录.md:3` |
| 135 | 旧 PTool 中 6 组 AES 抽取偏移表，以及 12 个输入 MD5/内部 RC4 key，均进行了有限移植探测。共 120 个已记录组合，没有匹配 S1M2 第 8、10 项的已知填充候选散列。阳性对照证明我们还原的 GH2 方法有效；阴性结果只说明这些移植组合没有成功。 | 阴性结果只说明这些移植组合没有成功。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_解码突破记录.md:101` |
| 136 | 结论严格限于 | 这些候选不是所测试的固定-key CBC、原始全 FF 明文假设下的 key。 没有确认 S1M2 使用 AES，也没有排除密钥派生、封装密钥、其他模式、不同算法、压缩或私有变换。这不是对 AES 密钥空间的穷举。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_解码突破记录.md:114` |
| 137 | S1M2 解码 | 尚未成功；已记录跨版本关系与有限阴性结果 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_解码突破记录.md:125` |
| 138 | 不能据此断言“只能实机提取”或“永远无法离线突破”；也不能把更多无依据的 key 枚举当成已经开展了程序逆向。尚未得到 S1M2 明文时，给出快门、HDR 或授权检查的补丁地址会是编造。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_解码突破记录.md:131` |
| 139 | 因此这些链接无法点击 | 这是对方原始文档的写法，并非本仓库缺失内容。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件存储拓扑与离线解码技术边界终局报告_20261008.md:5` |
| 140 | 四、 为什么离线环境下无法凭空“破出来”？（客观技术边界论证） |  | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件存储拓扑与离线解码技术边界终局报告_20261008.md:94` |
| 141 | 证据薄弱/不成立的假设 |  | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件存储拓扑与离线解码技术边界终局报告_20261008.md:111` |
| 142 | “从开源 GPL 源码或上位机软件中寻找解密算法”的设想已被彻底证伪（全量代码审查无任何关联）。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件存储拓扑与离线解码技术边界终局报告_20261008.md:112` |
| 143 | “纯离线对 `.bin` 文件进行数学暴力解密”在现代商用加密标准下不可行。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件存储拓扑与离线解码技术边界终局报告_20261008.md:113` |
| 144 | 相关文件不在本仓库内，因此这些链接无法点击 | 这是对方原始文档的写法， | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件逆向_阶段结果汇总.md:5` |
| 145 | 简单 XOR | 49 项分别整段 XOR FF、XOR 80，再比目录散列 \| 均未匹配；仅排除这两种直接变换 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件逆向_阶段结果汇总.md:96` |
| 146 | 调查覆盖说明 | U-Boot 包已解包并静态检查；Linux 包有 66156 个目录成员，本次选择提取了 124 个相关普通源码文件，关键词扫描的单文件上限为 4 MB。未完整反编译全部内核，也没有把开源包视为相机专有应用源码。精确型号/更新标识的零命中结论限于已记录的扫描范围。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件逆向_阶段结果汇总.md:233` |
| 147 | 静态穷举已排除 | XOR / RC4* / AES-ECB/CBC/CTR（全部候选密钥含 loader1 24B+64B、0x220 64B 块及派生）、SHA-384 标签。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:9` |
| 148 | [3] 是否先于 [4] 且不可绕过 | 若先于，则任何改动都被 `err_reject` 挡掉，预言机死路（除非有免签名的恢复模式）。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:25` |
| 149 | [4] 失败时返回的错误是否与 [3] 不同 | 若不同，可逐字节翻转密文试探，反推明文/密钥流。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:26` |
| 150 | 3 | 版本 +1 + 改 1 字节（默认改 zboot 分区 48B 校验块首字节；或 `--data-flip` 指定数据位） \| 高：若相机接受，写入的是被破坏的固件，可能无法启动 \| 若 [2] 已 `err_reject` 则本阶段无意义。若 [2] 是 `ok`：本阶段区分「签名只覆盖头部」与「覆盖全文件」 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:35` |
| 151 | 耗时本身也是信息 | RSA-4096 验签要数百毫秒，可区分「验签失败」与「数据校验失败」）。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:71` |
| 152 | `err_reject`（快，<1s） | 上传时验签，签名先于数据检查 \| 预言机死路 → 转「恢复模式是否免签名」验证 + 社区调研 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:107` |
| 153 | `ok` + 相机没回来 | 启动时验签失败 → 变砖 \| 走恢复模式；若恢复模式接受无签名固件 → 预言机从恢复模式入口打开 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:110` |
| 154 | 已排除算法清单（本地实测，供后续参考） |  | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:113` |
| 155 | 未压缩（zlib/deflate/lzma 在多个偏移均失败，无魔数）； |  | `01_研究报告/01_固件AES绕过_调研_20261010/04-转接环EF-L/EF-L-转接环固件-分析报告-中文.md:15` |
| 156 | 诚实的边界 | 因为拿到的镜像是"数据分区"，无法静态定位 I2C 处理器里的具体越界写 / 命令注入 bug。确认 A 路径需要：拿到 MCU 的代码镜像（可能是另一个 `.ecp` 或厂商烧录工具的 flash 转储）做反汇编审计，或用可控相机对实机做 I2C fuzz。 | `01_研究报告/01_固件AES绕过_调研_20261010/04-转接环EF-L/EF-L-转接环固件-分析报告-中文.md:25` |
| 157 | 是否压缩 | zlib / raw-deflate / lzma 在 `0x0000 / 0x0060 / 0x03E8 / 0x0600 / 0x0B20` 等多偏移均解压失败；无压缩魔数（`78 9C`、`FD 37`、`5D 00` 等） \| 否 | `01_研究报告/01_固件AES绕过_调研_20261010/04-转接环EF-L/EF-L-转接环固件-分析报告-中文.md:119` |
| 158 | (4) 是未证实假设 | 因为拿到的 `.ecp` 是数据分区，I2C 处理器的代码不在其中，无法静态定位具体 bug。要坐实必须： | `01_研究报告/01_固件AES绕过_调研_20261010/04-转接环EF-L/EF-L-转接环固件-分析报告-中文.md:178` |
| 159 | 严重性：高（若未鉴权）/ 中（若有弱校验可绕过）。依赖拿到升级工具或抓包，纯静态无法定论。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/04-转接环EF-L/EF-L-转接环固件-分析报告-中文.md:190` |
| 160 | 拿到的 `.ecp` 是数据分区，不含 I2C 处理器 / 启动代码 / 中断服务，因此无法静态定位具体内存破坏 bug；路径 A 的 (4) 目前是"高可行假设"而非"已证实"。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/04-转接环EF-L/EF-L-转接环固件-分析报告-中文.md:255` |
| 161 | `gphoto2 --set-config /main/actions/opcode=` 对私有操作码静默失败 | 必须改用原生客户端； | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:274` |
| 162 | 10. 升级尝试 | 为什么这条 DoS 无法升级为 RCE | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:280` |
| 163 | 传输结果 | 成功 \| ❌ 被 STALL 拒绝 | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:316` |
| 164 | 因此：该 DoS 无法升级为内存破坏或 RCE。 相机的 PTP 实现在命令路径与数据路径均使用有界缓冲区，超限即拒收（副作用是阻塞）。 |  | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:320` |
| 165 | 10.4 仍未排除（供后续研究者） |  | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:322` |
| 166 | 超限输入被端点 STALL 拒绝（有界缓冲区），无法升级为 RCE； |  | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:334` |
| 167 | 答案框架 | 能改内容的最强原语 = 固件升级写路径（刷写 = 重写整个文件系统）。它目前被"最终-chunk flash 定址失败"卡住，尚未打通。RCE 与密钥提取均为阴性。 | `01_研究报告/02_研究总报告_20261011/00-执行摘要.md:4` |
| 168 | 1 | AES 密钥提取不可行：密钥固化在 MC801 芯片内（OTP/eFuse/Crypto Engine/TrustZone），不在固件文件/转接环/镜头 I2C 总线里；离线 130k+ 探测、40/41 加密分区、真实 256KB keystream 均无法恢复密钥 \| 已证实（终局） | `01_研究报告/02_研究总报告_20261011/00-执行摘要.md:12` |
| 169 | 固件升级写路径能干净流送全部 1474 个完整 61192B 数据块，但最终部分块（41456B）始终失败 |  | `01_研究报告/02_研究总报告_20261011/00-执行摘要.md:20` |
| 170 | 与节奏无关（快送 87ms/chunk、慢送 158ms/chunk 都失败；官方 App 是 ~138ms/chunk）。 | 与节奏无关（快送 87ms/chunk、慢送 158ms/chunk 都失败； | `01_研究报告/02_研究总报告_20261011/00-执行摘要.md:24` |
| 171 | ⇒ 结论：只有真 90MB 镜像能走到真正的 flash 定址阶段；小镜像在"固件合法性"这关就被拒，无法用小样本逼近真实定址。真实 90MB 的 ~31s 定址失败，当前最可能是内部 flash 对大镜像末块的擦/写超时或磨损（我们已对同一块 flash 做了大量 90MB 流送测试）。尚未看到过一次成功的 `endsenddata`，因此签名/版本 oracle 仍是开放问题。 | 真实 90MB 的 ~31s 定址失败，当前最可能是内部 flash 对大镜像末块的擦/写超时或磨损（我们已对同一块 flash 做了大量 90MB 流送测试）。 | `01_研究报告/02_研究总报告_20261011/00-执行摘要.md:31` |
| 172 | C. RCE / 代码注入（全部阴性，仅剩一条未测） |  | `01_研究报告/02_研究总报告_20261011/00-执行摘要.md:33` |
| 173 | 编译 C / `LD_PRELOAD` 注入（CVE-2017-17562 思路） | 阴性 \| GoAhead 不把 `LD_*` 传入 CGI 环境，或 `cam.cgi` 为静态链接 | `01_研究报告/02_研究总报告_20261011/00-执行摘要.md:37` |
| 174 | HTTP 头/参数溢出 fuzz | 阴性 \| 无越界崩溃、无可控返回地址 | `01_研究报告/02_研究总报告_20261011/00-执行摘要.md:40` |
| 175 | 1 | 固件升级写路径（刷写=重写 rootfs） \| ✅ 最强 \| 卡住（最终-chunk 定址失败），未打通 | `01_研究报告/02_研究总报告_20261011/00-执行摘要.md:52` |
| 176 | A 固件升级写路径 | Wi-Fi CGI `startsenddata / senddata / endsenddata` \| 重写整个 rootfs（= 改内容最强原语） \| 卡住（最终-chunk 定址失败，未打通一次成功 `endsenddata`） \| §04 | `01_研究报告/02_研究总报告_20261011/02-攻击面总览.md:9` |
| 177 | 软件侧唯一能"写整个 rootfs"的是固件升级写路径（§04） | 它是"改内容"的主通道，但当前被"最终-chunk flash 定址失败"卡住，差最后一步。 | `01_研究报告/02_研究总报告_20261011/02-攻击面总览.md:17` |
| 178 | RCE 目前全部阴性（§05） | 编译 C / `LD_PRELOAD` 无效，已公开 GoAhead CVE 多数不适用，仅 CVE-2019-5096（multipart UAF→RCE）未测。 | `01_研究报告/02_研究总报告_20261011/02-攻击面总览.md:20` |
| 179 | 结论：版本号可以写大（`camctrl type=fw_update_mode value=V3.00` 就放行版本门，见 §08.1），但真正的关卡在签名（ECDSA P-256 + RSA-4096）。改版本号不能绕过签名 → "改版本号绕过版本门"这条线不成立，版本门只是防回滚，不是安全边界。 | 改版本号不能绕过签名 → "改版本号绕过版本门"这条线不成立，版本门只是防回滚，不是安全边界。 | `01_研究报告/02_研究总报告_20261011/03-固件格式与启动链.md:48` |
| 180 | 含义：容器内无公钥、无"禁验签"开关、无回退标志 → 纯软件无法让相机接受自编 / 篡改固件。唯一"签名 oracle"是相机 `endsenddata` 时的真实验签（当前尚未触达，见 §04）。 |  | `01_研究报告/02_研究总报告_20261011/03-固件格式与启动链.md:58` |
| 181 | 关键含义 | 验证链最前两级（BootROM→loader1 明文头→加密载荷）不在可改写用户区明文里；明文容器内无公钥、无回退标志，纯软件无法绕过验签。 | `01_研究报告/02_研究总报告_20261011/03-固件格式与启动链.md:121` |
| 182 | 04 · 固件升级写路径（核心 | 改内容原语 + 最终-chunk 失败深潜） | `01_研究报告/02_研究总报告_20261011/04-固件升级写路径.md:1` |
| 183 | 这是软件侧唯一真正"能改内容"的通道 | 一旦 `endsenddata` 成功 = 相机用我们流送的 90MB 映像重写整个 flash = rootfs（守护进程、socket、配置路径）一次性到手，完全不用拆机/焊接。本章记录协议、判别探针，以及当前卡住的最终-chunk flash 定址失败深潜。 | `01_研究报告/02_研究总报告_20261011/04-固件升级写路径.md:3` |
| 184 | 4.3 ★ 最终-chunk 失败深潜 |  | `01_研究报告/02_研究总报告_20261011/04-固件升级写路径.md:28` |
| 185 | 真 90MB 映像能干净流送全部 1474 个完整 61192B 数据块（~81–108ms/块），但最终部分块（41456B）始终失败 |  | `01_研究报告/02_研究总报告_20261011/04-固件升级写路径.md:31` |
| 186 | CONTROL（未改真 V29，fast keep-alive） | 81ms/块 \| 1474 块 ok（536s）→ final 12 次重试全 `err_critical`（第 4 次起 ~30.8s/次）→ `abortsenddata=error`；未改数据也在末块失败 → 判"传输问题，与内容无关" \| `control_run1.log` / `campaign.md` | `01_研究报告/02_研究总报告_20261011/04-固件升级写路径.md:40` |
| 187 | TESTA-2（final 1/4 次 → err_busy 30.12s → 重试全 err_critical） | pace 150ms（比官方 App 138ms 还慢） \| 1474 块 232.7s → final 4 次全失败 → `abortsenddata=error` \| `campaign.md` | `01_研究报告/02_研究总报告_20261011/04-固件升级写路径.md:42` |
| 188 | 与内容无关 | CONTROL 发的是未改动的真 V29 镜像（字节一致），仍失败 → 排除"我们改坏了镜像"。 | `01_研究报告/02_研究总报告_20261011/04-固件升级写路径.md:45` |
| 189 | 与节奏无关 | fast(81ms)、pace(150ms，比官方 138ms 更慢) 都失败 → 排除"送太快 flash 没跟上"。 | `01_研究报告/02_研究总报告_20261011/04-固件升级写路径.md:46` |
| 190 | 与状态无关 | 拔电池全新重启后依然复现 → 排除"残留状态"。 | `01_研究报告/02_研究总报告_20261011/04-固件升级写路径.md:47` |
| 191 | ⇒ 只有真 90MB 映像能走到真正的 flash 定址阶段；小 / 假映像在"固件合法性"这关就被拒，无法用小样本逼近真实定址行为。 |  | `01_研究报告/02_研究总报告_20261011/04-固件升级写路径.md:56` |
| 192 | 真实 90MB 的 ~31s 定址失败，内容 / 节奏 / 状态无关 | 最可能是内部 flash 对大映像末块的擦/写超时或磨损（本会话已对同一块 flash 做了大量 90MB 流送测试，可能已触发磨损 / 写放大）。尚未看到过一次成功的 `endsenddata`，因此签名 / 版本 oracle 仍是开放问题——我们还没能拿到"相机对已签名 vs 未签名 / 已改版本固件的真实验签反应"。 | `01_研究报告/02_研究总报告_20261011/04-固件升级写路径.md:59` |
| 193 | 卡点单一 | 就差"打通一次成功 `endsenddata`"。若末块定址失败是可恢复的 flash 状态问题（而非硬损伤），换一块干净 SD / 换机、或在全新 flash 状态下一次性流送（不反复重试末块、不静置、让相机自己 drain），有机会拿到第一次真实验签反应——那将直接回答"改版本 / 改内容能否过签名"。 | `01_研究报告/02_研究总报告_20261011/04-固件升级写路径.md:65` |
| 194 | 末块静置更久（60–120s 再 `endsenddata`），排除擦写未 drain。 |  | `01_研究报告/02_研究总报告_20261011/04-固件升级写路径.md:70` |
| 195 | 换 SD 卡 / 换机 | 排除"这块 flash 已被反复 90MB 流送写坏"的可能。 | `01_研究报告/02_研究总报告_20261011/04-固件升级写路径.md:72` |
| 196 | 目标：通过 Wi-Fi HTTP 服务拿到 shell / 执行代码。结论：目前全部阴性，仅剩 CVE-2019-5096（multipart UAF→RCE）未测，且需堆控，工程量大。 | 结论：目前全部阴性，仅剩 CVE-2019-5096（multipart UAF→RCE）未测，且需堆控，工程量大。 | `01_研究报告/02_研究总报告_20261011/05-RCE与代码注入.md:3` |
| 197 | 5.2 编译 C / `LD_PRELOAD` 注入（CVE-2017-17562 思路） | 阴性 | `01_研究报告/02_研究总报告_20261011/05-RCE与代码注入.md:18` |
| 198 | HTTP 头 / 参数溢出 fuzz（`scripts/RCE/overflow_fuzz.py`、`goahead_overflow.py`） | 阴性 —— 无越界崩溃、无可控返回地址。 | `01_研究报告/02_研究总报告_20261011/05-RCE与代码注入.md:33` |
| 199 | 6.3 其它已尝试（全部无有效崩溃 / 无 RCE） |  | `01_研究报告/02_研究总报告_20261011/06-崩溃与DoS.md:24` |
| 200 | 意义：升级状态机可通过 PTP 只读观察，但无法用它触发 / 中止升级（那是 0x9406 带副作用子码，红线）。 |  | `01_研究报告/02_研究总报告_20261011/07-USB-PTP-SCSI.md:35` |
| 201 | `startsenddata(type=fw)` | 分块 `senddata`（`method=separate, bufsize=61460`）→ `requestsenddata` → `endsenddata`。相机在 `endsenddata` 时校验：每分区 SHA-256 + IV（type=2 全零/明文，type=3 非零/加密）+ 外层 ECDSA P-256（0x220）+ 尾块 RSA-4096（0x560EC00）。无效固件 → `err_critical`/`err_reject`。容器内无公钥、无"禁验签"开关 → 无法伪造已签名固件。 | `01_研究报告/02_研究总报告_20261011/08-WiFi预言机与密钥提取.md:21` |
| 202 | 时序 | BootROM 在 Wi-Fi 固件加载之前已运行；Wi-Fi 是网络栈之上的应用层，物理上无法回退到 bootrom 阶段 | `01_研究报告/02_研究总报告_20261011/08-WiFi预言机与密钥提取.md:49` |
| 203 | 结论：密钥固化在 MC801 芯片内（OTP/eFuse/Crypto Engine/TrustZone），不在固件文件 / 转接环 / 镜头 I2C 总线里。软件离线 + Wi-Fi 提取不可行；要拿明文/绕验签只能走物理/调试侧（§10）。 | 软件离线 + Wi-Fi 提取不可行； | `01_研究报告/02_研究总报告_20261011/08-WiFi预言机与密钥提取.md:54` |
| 204 | 别在 Wi-Fi 上继续找密钥或 bootrom 后门 | 它只有"验证器 + 设置写口"，都是死路；把精力放到 UART/JTAG（只读拿运行时明文）或 SD.DAT（绕验签写自编代码）。 | `01_研究报告/02_研究总报告_20261011/08-WiFi预言机与密钥提取.md:64` |
| 205 | 09 · 已证伪路线（死路清单，别再走） |  | `01_研究报告/02_研究总报告_20261011/09-已证伪路线.md:1` |
| 206 | PTool 旧 GH2"自嵌式密钥切片"法 | S5 是硬件密钥，移植 120 组合全失败。 | `01_研究报告/02_研究总报告_20261011/09-已证伪路线.md:11` |
| 207 | 结论：密钥固化在芯片硬件（OTP/eFuse/Crypto Engine/TrustZone），固件文件内无密钥材料 → 软件离线解密不可行，必须硬件提取。 |  | `01_研究报告/02_研究总报告_20261011/09-已证伪路线.md:12` |
| 208 | 结论：转接环是卡口 I2C 上的独立从机 MCU，与 MC801 之间走镜头通讯协议（AF/光圈/镜头 ID），不进入 SoC 安全密码域；转接环自带密钥（镜头认证/设备唯一 ID）是另一套机密，读走它 ≠ 拿到 S5 固件 AES 密钥 → 死路。 | 转接环自带密钥（镜头认证/设备唯一 ID）是另一套机密，读走它 ≠ 拿到 S5 固件 AES 密钥 → 死路。 | `01_研究报告/02_研究总报告_20261011/09-已证伪路线.md:18` |
| 209 | 9.7 死路一览 |  | `01_研究报告/02_研究总报告_20261011/09-已证伪路线.md:38` |
| 210 | 现状：始终卡在最终-chunk flash 定址失败（~31s → `err_busy`/`err_critical`），内容/节奏/状态无关（§04）。 |  | `01_研究报告/02_研究总报告_20261011/10-下一步与开放问题.md:8` |
| 211 | 换 SD 卡 / 换机，排除"当前 flash 已被反复 90MB 流送写坏"。 |  | `01_研究报告/02_研究总报告_20261011/10-下一步与开放问题.md:13` |
| 212 | 末块定址失败到底是"可恢复的 flash 状态"还是"硬损伤/磨损"？ | 决定 §10.1 是否还能在软件侧打通。 | `01_研究报告/02_研究总报告_20261011/10-下一步与开放问题.md:40` |
| 213 | 离线/静态破解线（能否解出固件 AES 密钥） | 结论：不可行，密钥固化在芯片内。 | `01_研究报告/02_研究总报告_20261011/README.md:10` |
| 214 | ├── 04-固件升级写路径.md ← ★ "改内容"原语 + 最终-chunk 失败深潜（核心） |  | `01_研究报告/02_研究总报告_20261011/README.md:30` |
| 215 | ├── 05-RCE与代码注入.md ← 编译C/LD_PRELOAD 已证伪；GoAhead CVE；CVE-2019-5096 | ├── 05-RCE与代码注入.md ← 编译C/LD_PRELOAD 已证伪； | `01_研究报告/02_研究总报告_20261011/README.md:31` |
| 216 | ├── 06-崩溃与DoS.md ← 崩溃/挂死路径、PTP length-DoS |  | `01_研究报告/02_研究总报告_20261011/README.md:32` |
| 217 | ├── 09-已证伪路线.md ← 死路清单（别再走） |  | `01_研究报告/02_研究总报告_20261011/README.md:35` |
| 218 | 软件/Wi-Fi 侧 | 解不开 AES 密钥（芯片内固化），也摸不到调试后门；能拿到的最强"改内容"原语是固件升级写路径，但目前被"最终-chunk flash 定址失败（~31s → err_busy/err_critical）"卡住，尚未打通到一次成功的 `endsenddata`。已确认的实机漏洞只有一条：PTP length 不校验导致的本地 DoS（挂死，拔插 USB 恢复）。RCE（编译 C 注入 / 已公开 GoAhead CVE）目前全部阴性，仅剩 CVE-2019-5096（multipart UAF）未测、需堆控。 | `01_研究报告/02_研究总报告_20261011/README.md:49` |
| 219 | 其余加密分区从字节 0 即高熵，无法区分「无头区」还是「头区也被加密」。 |  | `01_研究报告/02_研究总报告_20261011/research/BOOT_FLOW.md:59` |
| 220 | loader1 本体不为空 | 0x142C 起为 468B 零（到 +0x200 边界），0x1600-0x2400 为 3584B 高熵载荷（熵 7.948，仅 17 个零字节）。→ 旧文档「loader1 全 0/为空」不成立，它是真实的加密 BL1 映像。 | `01_研究报告/02_研究总报告_20261011/research/BOOT_FLOW.md:101` |
| 221 | zboot 也非空 | 512B 0xFF 头 + 1536B 高熵载荷（熵 7.865）。→ 旧文档「zboot 全 0xFF（空）」不成立，它是真实的 zImage 引导 stub（只是头部处于擦除态）。 | `01_研究报告/02_研究总报告_20261011/research/BOOT_FLOW.md:102` |
| 222 | 关键含义（与 `verify_logic_notes.md` 一致） | 验证链最前两级（BootROM→loader1 明文头→加密载荷）不在可改写的用户区明文里；明文容器内无公钥、无回退标志，纯软件无法绕过验签。 | `01_研究报告/02_研究总报告_20261011/research/BOOT_FLOW.md:148` |
| 223 | 离线破解路线已被社区穷举排除（含 GH2 自嵌式密钥法移植、AV 固定 key、SL3 交叉、13 万+ 探测）；结论是密钥固化在芯片硬件（OTP/eFuse/Crypto Engine/TrustZone），固件文件内无密钥材料。软件离线解密不可行，需硬件提取。 | 离线破解路线已被社区穷举排除（含 GH2 自嵌式密钥法移植、AV 固定 key、SL3 交叉、13 万+ 探测）； 软件离线解密不可行，需硬件提取。 | `01_研究报告/02_研究总报告_20261011/research/FIRMWARE_FORMAT.md:92` |
| 224 | 无效固件 | `err_critical` / `err_reject`。容器内无公钥、无"禁验签"开关 → 无法伪造已签名固件。 | `01_研究报告/02_研究总报告_20261011/research/Wi-Fi实机预言机与mode枚举实测-中文.md:55` |
| 225 | 时序：BootROM 在 Wi-Fi 固件加载之前已运行（BootROM → CM0 supervisor → bootstrap → … → 网络栈）。Wi-Fi 侧的 cgi 是"网络栈之上的应用层"，物理上无法回退到 bootrom 阶段。 |  | `01_研究报告/02_研究总报告_20261011/research/Wi-Fi实机预言机与mode枚举实测-中文.md:105` |
| 226 | 验签：唯一"bootrom 相邻"的软件面是固件更新路径，但被 RSA-4096 + ECDSA + 分区 SHA-256 三重签名门控，无公钥、无禁验开关（§1.2）→ 无法让相机接受一个自编固件。 |  | `01_研究报告/02_研究总报告_20261011/research/Wi-Fi实机预言机与mode枚举实测-中文.md:107` |
| 227 | 别在 Wi-Fi 上继续找密钥或 bootrom 后门 | 它只有一个"验证器"和一个"设置写口"，都是死路；把精力放到 UART/JTAG（只读拿运行时明文）或 SD.DAT（绕验签写自编代码）。 | `01_研究报告/02_研究总报告_20261011/research/Wi-Fi实机预言机与mode枚举实测-中文.md:114` |
| 228 | 与 `verify_logic_notes.md` 结论一致（验签逻辑在加密 loader/BootROM 内，明文容器无法直接改）。 |  | `01_研究报告/02_研究总报告_20261011/research/hardware_attack_surface_notes.md:87` |
| 229 | 对 S5（MC801），静态/离线破解 AES 不可行。 密钥固化在 MC801 芯片内部安全域（OTP/eFuse/Crypto Engine/TrustZone），不在固件文件内；40/41 个加密分区无已知明文，唯一例外 `ipu_data` 的明文可经同内容分区 `history`（type=2 明文、≈全零）得知 | 已提取 256 KB 真实 keystream（熵 7.999），但单段 keystream + 128 位随机密钥 + 逐构建随机 IV 仍不足以恢复密钥（§3.3、§10.4）；IV 逐构建随机；ECDSA P-256 + RSA-4096 双重签名封锁一切改动。唯一可行方向是硬件/调试侧（UART/JTAG 读运行时明文，或 SD.DAT 恢复模式绕过验签）——不需要密钥，只需要开机后 DDR 里的明文。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:12` |
| 230 | PTP 漏洞 / CVE 枚举 + 实机探测（§9） | 11 个 NVD CVE 逐条核对（全部是主机侧解析器类，无一适用于 S5 主机→相机方向）+ 43 个安全 fuzz 探测 + 1 次受控 length-DoS → 无 RCE/无明文泄露，坐实唯一漏洞为本地 DoS（length 挂死，拔插恢复）；另发现设备真实实现的未文档化命令 0x9103。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:19` |
| 231 | DoS 隐患已工程化排除，并已受控实机全链条坐实（2026-10-11，见 §9.5） | 相机 PTP 解析器校验 type 不校验 length，length 不符 → 接口挂死、无超时；macOS 主机侧（ImageCaptureCore）同样不校验 length（原样发出，仅内部约 60 s 超时返回空响应）。所有工具发送前对 length 做精确计算/断言；`lenprobe` 模式是唯一故意触发该行为的受控演示（拔插 USB 恢复、无写操作、不砖机）。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:40` |
| 232 | 3. 静态验证矩阵（全部阴性） |  | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:70` |
| 233 | 2 | S5 是否有已知明文的加密分区 \| 扫全部 type=3 分区，找长段恒定/低熵（=恒定明文）；并比对各分区明文 SHA@+0x1C 是否与某 type=2 明文分区相同 \| 40 个无已知明文；唯一例外 `ipu_data` —— 其明文 SHA（`8a39d2…`）与 type=2 明文分区 `history`（≈全零）相同 → 明文已知 → 已提取 256 KB 真实 keystream（`ks_extract.py`，熵 7.999）。但该明文≈全零（仅 508 字节非零），信息量低；且单段 keyst… | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:77` |
| 234 | 3 | PTool 旧款"密钥藏在文件里"方案 \| GH2 表 `key[i]=file[0x200+i*0x200+table[i]]`（table=[77,350,…,84]），base 取 0/0x200/…/0x1400 \| 全失败。2015 年的 PTool 密钥嵌入方案不适用于 2020 的 S5（硬件密钥） | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:78` |
| 235 | 拿到 5 个同型号（均 MC801、48 分区、data_start=0x1400）S5 固件后，专门验证"跨版本差分"这条此前唯一未排除的静态路线。 |  | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:85` |
| 236 | 若是 ECB | 未改动的明文应产生相同密文块 → 会看到远高于 0.4% 的相等率。实际没有 → 排除 ECB / 版本稳定 keystream。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:111` |
| 237 | 跨版本差分这条路被 5 个版本的实测数据彻底封死 | 拿不到"未改动代码 → 相同密文"的捷径，也推不出 keystream 旋转/偏移规律（SSTIC 2016 那类跨版本旋转规律在此不成立）。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:114` |
| 238 | IV 逐构建随机 | 41 个全唯一、不可派生、跨版本全变 → 无 nonce 重用、无 IV 预测、跨版本无法做"同明文同 IV"对齐 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:128` |
| 239 | 真实 AES 密钥恢复测试（本轮，§10.4） | 用唯一已知明文（`ipu_data`，≈全零、经 `history` 可知）提取 256 KB 真实 keystream（熵 7.999），对 211 个文件内派生候选密钥逐一跑 AES-128 CBC/CTR/ECB（table-IV 与 zero-IV）→ 0 命中 → 密钥非文件内派生、且是 128 位随机密钥（单段 keystream 无法反推）。这比"猜 key"强：这次是拿真实明文当校验去解密，仍然失败。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:157` |
| 240 | 静态证据无法 100% 排除芯片内存在逐设备二级密钥/认证层，但它只影响"这台相机是否接受该固件"（验签），不影响"能否解密" | 解密主密钥固定，由"官方单一固件通用"这一事实硬确认。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:166` |
| 241 | `tools/s5_ptp_dump.m` / `tools/s5_ptp_dump` | macOS 原生 ImageCaptureCore 后备（已编译，arm64）。macOS 首选：系统相机栈常占用 PTP 设备导致 libusb 抢接口失败 / 读取 EOVERFLOW，此路径自动处理占用，已用它完成全部实机 dump（见 5.7）。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:177` |
| 242 | 数据面（0x9606/0x9607）的目标地址、长度、数据由主机按固件下发的目标写，但地址是机身给的 | 主机无法把数据写到"非目标地址"。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:286` |
| 243 | 没有"任意地址写"原语 | `0x9606` 的目标内存地址是机身返回的（ready 事件 `0x41000013` 把地址存到主机 `0x260498`/`0x2604ac`，再原样填入 0x9606；§5.5 实机+反汇编双重坐实），不是主机可填 → 主机无法把数据写到任意地址。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:336` |
| 244 | 但这是 JTAG/SD 入口的下游收益；单独靠 PTP 无法落地。 |  | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:355` |
| 245 | "在固件升级过程中动升级字节" | 不可行（无地址写 + 双签名 + 无 RAM 读回）。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:358` |
| 246 | PTP 漏洞 / CVE 枚举 + 实机 fuzz（§9） | 11 个 NVD CVE 逐条核对（全是主机侧解析器类，无一适用于 S5 主机→相机方向）+ 43 个安全探测 + 受控 length-DoS 实验 → 无 RCE、无提权、无密钥/明文泄露；坐实的只有本地 DoS（length 挂死、拔插恢复）与参数数量/TID 校验缺失（无利用价值）。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:380` |
| 247 | ⇒ 静态/离线/跨版本 均无法从密文或版本差中恢复密钥或明文 |  | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:391` |
| 248 | 无 RCE/无明文泄露；仅坐实本地 DoS（length 挂死、拔插恢复） | 无 RCE/无明文泄露； | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:399` |
| 249 | 最终判定 | S5（MC801）静态破解不可行；唯一可行方向是硬件/调试侧 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:402` |
| 250 | "密钥在硬件"是软件侧穷尽排除后的结论（参考库多机型 + 汇总 130k 探测 + 本轮 6 项静态验证 + 5 版跨版本实测 + PTP 全操作码实机验证），不是对 AES 密钥空间的穷举证明。 |  | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:416` |
| 251 | 工具：`./s5_ptp_dump ./ptp_out_fuzz S5 fuzz`（原生 ImageCaptureCore；每包 length 精确；排除全部写/动作操作码）。产物：`ptp_out_fuzz1/`（每探测 `.bin` + `.resp.bin` + `capture_log.json`）。 | 排除全部写/动作操作码）。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:451` |
| 252 | TID 不校验 | TID=0/最大/复用均成功。但设备侧无 TID 状态缓存 → 无法伪造"对其它事务的响应"。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:479` |
| 253 | 按类型推进 OOB（40335：`*offset+=16`） | ✗ 未观察到（数据解析段无越界行为） \| 无证据 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:507` |
| 254 | 整数溢出（libmtp 9831/9832） | ✗ 未观察到（配置块 65,545 B，无大尺寸面；length 字段仅触发"等待"） \| 无证据 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:508` |
| 255 | 事务/TID 状态混淆 | ✗ TID 不校验，但设备侧无 TID 状态缓存可混淆 \| 无证据 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:509` |
| 256 | 字符串缺 null 终止（40334） | ✗ 未观察到 \| 无证据 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:510` |
| 257 | 无 RCE / 提权 / 密钥或明文泄露 | 11 个 PTP 相关 CVE 在 S5 上（主机→相机方向）无一适用；实机 fuzz（43 个安全探测 + 1 个受控 DoS）只发现 本地 DoS（length 挂死） 与 2 处解析器校验缺失（参数数量 / TID），均无利用价值。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:514` |
| 258 | 结论（`exp_cipher.py`） | 若是 Nikon 式固定 XOR 流，两个同明文分区的密文异或应≈全零（因为 keystream 与明文无关、只与位置有关）。实测熵 7.999 → 是真正的 AES-CBC/CTR，keystream 由 `(密钥, IV)` 决定、与明文无关且逐 IV 变化。Nikon 的 padding 泄露法、以及一切基于"固定 keystream"的攻击，在 S5 上从原理上不成立。 这是"能不能借魔灯"这个最根本问题的定量回答。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:546` |
| 259 | 无法直接判"密钥同/异" | 因为加密分区的 IV 逐版随机、不存在"同明文 + 同 IV"的分区对，所以无法用"同明文同 IV → 比密文"直接判定密钥是否跨版本相同。这是随机 IV 设计带来的正面效果——它把跨版本差分这条静态路线彻底封死。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:554` |
| 260 | Nikon 能"解 key"是因为 K8 由文件内 seed 派生。S5 没有这种 seed（头部除签名外几乎全零，无 SHA-1 IV 字面量）。为定量排除"密钥由文件内小 secret 派生"这条最后的可能，用唯一已知明文做一次真实 AES 解密校验（不是猜 key，是拿真实明文当 oracle） |  | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:559` |
| 261 | 结论：S5 的密钥不是文件内派生的小 secret（区别于 Nikon 的 K8）；结合"单段 keystream + 逐构建随机 IV"，即使有已知明文也无法反推 128 位随机密钥。静态/离线侧到此穷尽。 |  | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:565` |
| 262 | 重打包 + 重签名（被双重签名封死，除非走升级流程） | Nikon 用恢复的 K8 重签名即可刷入。S5 是 ECDSA P-256 + RSA-4096 非对称双签名，私钥不可恢复 → 无法离线重签。唯一绕过点是固件升级流程（0x9606/0x9607）——但 §5 已坐实 0x9606 无"任意地址写"原语、机内 Bootloader 仍做外层解包校验，故此路当前不通（留待深挖升级状态机，见 §5.5/§6）。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:570` |
| 263 | 历史背景 | SSTIC 2016（Milbeaut 相机固件跨版本 keystream 旋转规律）——本轮 5 版实测证明该规律在 S5 上不成立（§3.2）。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:631` |
| 264 | 对 S5（MC801），静态/离线破解 AES 不可行。 密钥固化在 MC801 芯片内部安全域（OTP/eFuse/Crypto Engine/TrustZone），不在固件文件内；41 个加密分区没有任何一个已知明文；IV 逐构建随机（5 版实测）；ECDSA P-256 + RSA-4096 双重签名封锁一切改动。松下私有 PTP 全操作码实机只读验证后，软件/协议侧同样封死。唯一可行方向是硬件/调试侧（UART/JTAG 读运行时明文，或 SD.DAT 恢复模式绕过验签） | 不需要密钥，只需要开机后 DDR 里的明文。 | `01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:8` |
| 265 | 6 项新静态验证 + 5 版跨版本实测（全部阴性） | 无已知明文、无文件内密钥、IV 逐构建随机不可派生、同偏移密文跨版本 ≈ 随机（≈0.39%），跨版本差分路线封死。 | `01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:12` |
| 266 | 固件升级状态机全貌（0x9605 只读探测 + Tether 反汇编对照） | 坐实 0x9606 无"任意地址写"原语（目标地址由机身下发）；魔灯式"升级过程动手脚"判定为不可行（无地址写 + 双签名 + 无 RAM 读回）。 | `01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:15` |
| 267 | PTP 漏洞 / CVE 枚举 + 实机探测（§9） | 11 个 NVD CVE 逐条核对（全部是主机侧解析器类，无一适用于 S5 主机→相机方向）+ 43 个安全 fuzz 探测 + 1 次受控 length-DoS 全链条验证 → 无 RCE/无明文泄露，坐实唯一漏洞为本地 DoS（length 挂死、无超时、拔插恢复）；发现 0x9421/0x9605 不校验参数数量、TID 不校验、0x9103 等未文档化命令被设备识别。 | `01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:17` |
| 268 | DoS 隐患已工程化排除，并已受控实机全链条坐实（§9.5） | 相机 PTP 解析器校验 type 不校验 length，length 不符 → 接口挂死、无超时；macOS 主机侧同样不校验 length。所有工具发送前对 length 精确计算/断言；`fuzz`/`lenprobe` 模式中只有 `lenprobe` 故意触发该行为（受控演示，拔插 USB 恢复）。 | `01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:47` |
| 269 | │ ├── 01_版本门与握手修复.md ← 版本门"改版本绕过"证伪 + 卡死根因与修复（本次关键成果） |  | `01_研究报告/03_隐藏格式_可分发版_20261012/README.md:19` |
| 270 | │ ├── 04_camcgi_RCE面测绘.md ← cam.cgi 攻击面测绘 + RCE 不可行结论 |  | `01_研究报告/03_隐藏格式_可分发版_20261012/README.md:22` |
| 271 | 版本门"改版本号绕过"不成立（已证伪）。`comm_proto_ver=10.0` 只是相机 | App 单向字段； | `01_研究报告/03_隐藏格式_可分发版_20261012/README.md:85` |
| 272 | 握手 `req_acc` 不携带客户端版本；反编译确认 App 无版本比较逻辑。"请更新 App"是通用连接失败文案， | "请更新 App"是通用连接失败文案， | `01_研究报告/03_隐藏格式_可分发版_20261012/README.md:86` |
| 273 | cam.cgi 网络 RCE 极难/很可能不可行 | mode 面仅 7 个，无 file-op / exec / dynamic-load / | `01_研究报告/03_隐藏格式_可分发版_20261012/README.md:102` |
| 274 | 系统信息泄漏；GoAhead overflow 与 LD_PRELOAD（CVE-2017-17562）均失败。 | GoAhead overflow 与 LD_PRELOAD（CVE-2017-17562）均失败。 | `01_研究报告/03_隐藏格式_可分发版_20261012/README.md:103` |
| 275 | 一页纸结论。每条带"证据强度" | ✓=已实机验证，◐=有强证据但未完全闭合，✗=已证伪。 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/00_执行摘要.md:5` |
| 276 | 1 | "改版本号绕过版本门"不成立 \| ✓ 反编译 + 协议审计 \| 01 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/00_执行摘要.md:13` |
| 277 | 6 | cam.cgi 网络 RCE 极难/很可能不可行；可控原语=`setsetting` 状态写 \| ✓ 表面测绘 + 多路尝试失败 \| 04 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/00_执行摘要.md:18` |
| 278 | 已证伪 / 不可行路线（不要再走） |  | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/00_执行摘要.md:32` |
| 279 | ✗ 改 `comm_proto_ver` 版本号绕过版本门（字段方向 + 无比较逻辑）。 |  | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/00_执行摘要.md:34` |
| 280 | ✗ 网络层 RCE | GoAhead buffer overflow、LD_PRELOAD（EV-43360 / CVE-2017-17562）、 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/00_执行摘要.md:35` |
| 281 | 各 mode/getinfo 子类型的 file-op / exec / dynamic-load 探测，全部失败。 |  | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/00_执行摘要.md:36` |
| 282 | ✗ 固件 AES 密钥提取（见 2026-10-11 独立评估报告）。 |  | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/00_执行摘要.md:37` |
| 283 | 版本门证伪 + 握手卡死根因与修复 |  | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/01_版本门与握手修复.md:1` |
| 284 | 本文是本研究最核心的成果 | 一条看似可走的"改版本号绕过版本门"路线被证伪； | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/01_版本门与握手修复.md:3` |
| 285 | A. "改版本号绕过版本门" | 不成立（已证伪） | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/01_版本门与握手修复.md:8` |
| 286 | 结论：不成立。 三个独立证据互相印证： | 结论：不成立。 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/01_版本门与握手修复.md:12` |
| 287 | 没有版本比较 / 拒绝分支。"请更新此应用程序"对应的是通用连接失败文案 | "请更新此应用程序"对应的是通用连接失败文案 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/01_版本门与握手修复.md:22` |
| 288 | 在每一个终止路径（成功、失败、用户取消、超时）都用同一个 uuid 发一次 `req_acc_can`， |  | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/01_版本门与握手修复.md:46` |
| 289 | 结论：S5 的 Wi-Fi cam.cgi 网络层 RCE 极难、很可能不可行。 |  | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md:3` |
| 290 | D. RCE 尝试与失败记录（不要再走） |  | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md:56` |
| 291 | GoAhead buffer overflow（request-line / header / query） | ✗ 失败（定制 CGI 不触发） | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md:60` |
| 292 | LD_PRELOAD / EV-43360 / CVE-2017-17562（GoAhead） | ✗ 失败（固件非受影响的 GoAhead 版本 / 路径不可达） | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md:61` |
| 293 | 各 mode / getinfo 子类型 file-op / exec / dynamic-load 探测 | ✗ 全部 err/reject | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md:62` |
| 294 | 固件 AES 密钥提取（2026-10-11 独立评估） | ✗ 不可行 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md:63` |
| 295 | 因此：网络层拿 shell（RCE）基本不可行；能拿到的是"设置面的写权限"。 | 因此：网络层拿 shell（RCE）基本不可行； | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md:72` |
| 296 | 电源 | 强烈建议相机接交流电源（卡死后若没电就无法恢复） | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md:16` |
| 297 | 子类型外全部 err/reject（即无 RCE 面）。只读。 | 子类型外全部 err/reject（即无 RCE 面）。 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md:93` |
| 298 | ✗ 绝不刷写固件、不碰 `fw_update_mode` 相关写、不做 `resetDevice`。 |  | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/06_安全约束与风险.md:10` |
| 299 | ✗ 绝不发 PTP 配置写 / `0x9406` 副作用子码 / 长度不匹配的 PTP 包（USB 侧）。 |  | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/06_安全约束与风险.md:11` |
| 300 | ✗ 绝不连发 `req_acc`；绝不在已 `ok` 的会话上发 `req_acc_can` 去打断它。 | ✗ 绝不连发 `req_acc`； | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/06_安全约束与风险.md:12` |
| 301 | ✗ 绝不在 `getstate` 非 `ok`（相机异常）时继续任何写操作。 |  | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/06_安全约束与风险.md:13` |
| 302 | ✗ 绝不把相机留在"非基线"状态就断开 | 每次写后必须回滚并验证。 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/06_安全约束与风险.md:14` |
| 303 | `setsetting`（CGI 命令） | 写入 flash ✓ \| 只写 RAM ✗ \| 只写 RAM ✗ \| 部分 | `01_研究报告/04_隐藏格式_持久化成果.md:15` |
| 304 | `recv()` 卡死（进程 S 态 / CPU 0%）。`timeout=120` 反而卡了 6 分钟。这不是失败 |  | `01_研究报告/04_隐藏格式_持久化成果.md:168` |
| 305 | 数据由 `sendall` 发出即已送达相机；`send()` 的响应超时/卡死不代表失败。 | `send()` 的响应超时/卡死不代表失败。 | `01_研究报告/04_隐藏格式_持久化成果.md:169` |
| 306 | `研究报告.md` | 研究对象、原理、结果、证据等级、失败案例与迁移边界。 | `01_研究报告/05_Panasonic_hidden_format_参考/README.md:9` |
| 307 | 因此写入需要 `--accept-secondary-change` 显式接受此限制。通信中断、响应异常、恢复失败时停下，先用机身菜单回到已知正常规格；不重复发送、不升级、不回灌快照。 | 通信中断、响应异常、恢复失败时停下，先用机身菜单回到已知正常规格； | `01_研究报告/05_Panasonic_hidden_format_参考/README.md:49` |
| 308 | 程序成功状态 `selected_not_recording_verified` 只代表选中成功。失败后会尝试恢复可见原值；若 `rollback_error` 不为空，停止测试并查看机身状态。未支持或超时不进行自动重试。 | 失败后会尝试恢复可见原值； | `01_研究报告/05_Panasonic_hidden_format_参考/复现操作手册.md:52` |
| 309 | 4.3 其他候选与失败案例 |  | `01_研究报告/05_Panasonic_hidden_format_参考/研究报告.md:110` |
| 310 | S1H 的新程序只允许两个已获得媒体的目标；两个已知异常 token 在所有机型上暂时阻止测试。这是基于历史失败证据的保守限制，不宣称异常在 S5 必然复现。 | 这是基于历史失败证据的保守限制，不宣称异常在 S5 必然复现。 | `01_研究报告/05_Panasonic_hidden_format_参考/研究报告.md:161` |
| 311 | `S1R2两项成果_移交S5同事.md`、`S1R2_已排除路线与风险备忘.md` |  | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:5` |
| 312 | 证据标记 | ✓=已实机闭合 · ◐=有强证据未闭合 · ✗=已证伪/死路 | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:7` |
| 313 | 可利用性 | 低：256 个固定偏移（1KB 步长）× 写 4B 且高 16 位恒 0 → 部分指针覆盖不可行、读 1B 重建不出指针、无堆喷 → 代码执行死路，仅 DoS + 弱信息泄露 \| ✓ 静态分析闭合（S1R2 侧） | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:34` |
| 314 | 二、S1R2 侧「已排除路线」对 S5 的交叉校验 |  | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:44` |
| 315 | S1R2 风险备忘（SC2006A 实测 / OSS 源码确认）中的排除结论，不能直接搬到 S5（MC801），逐条标注适用性 |  | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:46` |
| 316 | ❌ UART 是死路 | U-Boot `BOOTDELAY=-2` + 内核 `console=null loglevel=0` + `ENV_IS_NOWHERE`（接了也是黑的） \| ⚠️ 不可直接套用：S5 的 U-Boot 配置未读（rootfs 加密，离线看不到 env）。先做离线核验（见 §三 P3）：在 48 分区表的 type=2 明文分区里找 env / BOOTDELAY / console 痕迹；若同样关闭 → S5 UART 判死路；若开启 → UART 复活为只读 bootlog 通道 | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:50` |
| 317 | 3.1 已排除（✗ 不要再走） |  | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:66` |
| 318 | Wi-Fi / 网络取密钥或 RCE | ~70 mode 枚举全 err_param；仅 3 个验证型预言机（版本门/签名/CAMSET 校验和）；GoAhead 溢出、LD_PRELOAD、file-op/exec 全失败 | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:72` |
| 319 | 旧机型 PTool 密钥切片移植（GH2 法） | 120 组合全失败，S5 是硬件密钥 | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:74` |
| 320 | P2 | 服务模式组合键盲试：多键同时按下开机（GX85/ZS30 式），试 S5 的 SERVICE MODE \| 无 \| 零 \| 若命中 → 维护菜单/读入口（或至少排除） \| 未做 | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:81` |
| 321 | P3 | S5 U-Boot 控制台离线核验：在 48 分区表 type=2 明文分区中找 U-Boot env / BOOTDELAY / console= / loglevel 痕迹 \| 离线（`s5_layout.json` + `S5___V29.bin.parts.json` 已在包内） \| 零 \| 判定 UART 生死（S1R2 先例：console=null → 死路）；顺带看 Stubby 是否 ENFORCING \| 未做（本次新增） | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:82` |
| 322 | P6 | SD.DAT / ROM-flashing：BootROM 跑 SD 卡自编 `DATA.BIN`，绕 loader2/3 与验签链，可写可 dump \| P1（确认存储类型）+ 全量备份 + 验证过的 `pardata.par` \| 高（S1R2 NAND 教训：写错标定数据 = 不可逆砖） \| 彻底绕过验签链的写入口（JTAG 受阻时的备胎） \| 未做（降级为备胎） | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:85` |
| 323 | UART 从"默认首选"改为"先核验 console 配置再决定"（S1R2 已实测 console=null 死路，S5 待 P3 核验）； |  | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:97` |
| 324 | 本目录 `S1R2_已排除路线与风险备忘.md` | S1R2 已排除路线/风险备忘（下载文件夹同名文件归档） | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:108` |
| 325 | Panasonic LUMIX DC-S1R2 相机 — 已排除路线与风险备忘（给同事） |  | `01_研究报告/06_S1R2移交_20261012/S1R2_已排除路线与风险备忘.md:1` |
| 326 | 三、已排除 / 判定为死路或高风险的路线（重点） |  | `01_研究报告/06_S1R2移交_20261012/S1R2_已排除路线与风险备忘.md:26` |
| 327 | ❌ 1. 软件远程入口（USB PTP / Flow / WiFi / BT / HTTP） |  | `01_研究报告/06_S1R2移交_20261012/S1R2_已排除路线与风险备忘.md:28` |
| 328 | 全部 fuzz 过 | 只有 DoS，无 RCE。富输入的解析器（Flow XML、配置导入）都被"格式门控"挡死，格式已丢失。 | `01_研究报告/06_S1R2移交_20261012/S1R2_已排除路线与风险备忘.md:29` |
| 329 | ❌ 2. UART 串口（拆机读串口） |  | `01_研究报告/06_S1R2移交_20261012/S1R2_已排除路线与风险备忘.md:31` |
| 330 | 死路——三个证据叠加： |  | `01_研究报告/06_S1R2移交_20261012/S1R2_已排除路线与风险备忘.md:32` |
| 331 | 四、仍未排除、相对可行的路 |  | `01_研究报告/06_S1R2移交_20261012/S1R2_已排除路线与风险备忘.md:58` |
| 332 | ③ f->set_alt(f, w_index, ...); ← 却传【未截断的原始 w_index】✗ | ← 却传【未截断的原始 w_index】✗ | `01_研究报告/06_S1R2移交_20261012/S1R2两项成果_移交S5同事.md:132` |
| 333 | ★ 判定 | 低（代码执行方向 = 死路），只能 DoS + 极弱信息泄露 | `01_研究报告/06_S1R2移交_20261012/S1R2两项成果_移交S5同事.md:176` |
| 334 | · 写 4 字节高 16 位恒 0 | 部分指针覆盖不可行（覆盖后指针落到 4GB 窗口头 64KB，未映射） | `01_研究报告/06_S1R2移交_20261012/S1R2两项成果_移交S5同事.md:182` |
| 335 | · USB 主机无法在相机侧做堆喷 | 无法精确命中 | `01_研究报告/06_S1R2移交_20261012/S1R2两项成果_移交S5同事.md:184` |
| 336 | 推论修正 | 上一轮"flash 写进三项、开机被固件重新派生为 mp4"的推断不成立（写入从未发生）。 | `01_研究报告/07_隐藏格式持久化_追查_20261013.md:52` |
| 337 | 并不成立（S5II 有 mov 槽仍活动 mp4）。 |  | `01_研究报告/07_隐藏格式持久化_追查_20261013.md:81` |
| 338 | 排除项：blob 内没有独立的「默认容器 / 白名单 / 注册格式表」字段（全量 831 字段扫描）， |  | `01_研究报告/07_隐藏格式持久化_追查_20261013.md:85` |
| 339 | `download_blob` | camsetting 68KB 响应实测需 90–200s，原 20s 超时必然失败，已提到 240s。 | `01_研究报告/07_隐藏格式持久化_追查_20261013.md:92` |
| 340 | `mov_30p_200mbps_6k_10bit` | ❌ `err_param` | `01_研究报告/08_格式对照表_NTSC-MOV_20261013.md:137` |
| 341 | `getsetting videoquality` 名字回报 | ❌ 错报为 `mov_60p_200mbps_c4k_10bit`（S5 的"码→名"表没有 ~~`0xf1/0xf4`~~） | `01_研究报告/08_格式对照表_NTSC-MOV_20261013.md:138` |
| 342 | 重启后 `curmenu` 的 5.9K 项 | ❌ 仍全部 `enable="no"`（连 `videoquality_filter_pictsize_5_9k` 也是 no） | `01_研究报告/08_格式对照表_NTSC-MOV_20261013.md:143` |
| 343 | 机身菜单可用性 | ❌ 当前值名字不在 `allmenu` → 【录制质量】变灰 | `01_研究报告/08_格式对照表_NTSC-MOV_20261013.md:144` |
| 344 | 实拍文件真实规格 | ❌ 4096×2160 @59.94fps, hvc1, ~195Mbps, PCM（= C4K 60p），不是 5888×3312 | `01_研究报告/08_格式对照表_NTSC-MOV_20261013.md:145` |
| 345 | 结论（写作"已证伪"） |  | `01_研究报告/08_格式对照表_NTSC-MOV_20261013.md:149` |
| 346 | 菜单层面无法解锁 | 5.9K 的 `enable` 由固件按机型硬编码为 no，与当前值/容器/制式无关； | `01_研究报告/08_格式对照表_NTSC-MOV_20261013.md:150` |
| 347 | （TCC）挡住（`Operation not permitted`，非 DSH 沙箱），当前进程无法读取。 |  | `01_研究报告/09_S1H参考包分析_mp4ed_20261013.md:7` |
| 348 | 16 个候选中 14 个"读回准确"但只有 2 个录出真媒体；并记录两类失败 |  | `01_研究报告/09_S1H参考包分析_mp4ed_20261013.md:21` |
| 349 | 失败模式目录 | 我们 5.9K 遇到的"setter ok 但无效"在 S1H 报告中早有记录，可直接对照定性。 | `01_研究报告/09_S1H参考包分析_mp4ed_20261013.md:31` |
| 350 | 显式写任意 `mp4ed_*` 质量 token | ❌ 掉回 `mp4_60p_28mbps` 或 `err_critical`；44 个 NTSC 候选 0 个读回正常 | `01_研究报告/09_S1H参考包分析_mp4ed_20261013.md:39` |
| 351 | 但它不能把 S1H 的 400Mbps ALL-I 4K 移植到 S5 | S5 的 mp4ed 质量 token 全部读回失败。 | `01_研究报告/09_S1H参考包分析_mp4ed_20261013.md:60` |
| 352 | `err_critical` / 静默映射两类失败给出的判据，与我们 5.9K 的结论互相印证。 |  | `01_研究报告/09_S1H参考包分析_mp4ed_20261013.md:62` |
| 353 | 且【录制文件格式】与【录制质量】双双变灰、无法修改。诊断结果 |  | `01_研究报告/09_S1H参考包分析_mp4ed_20261013.md:69` |
| 354 | 两者无法同时成立 | 让条目显示的条件，正是让菜单变灰的条件。 | `01_研究报告/09_S1H参考包分析_mp4ed_20261013.md:84` |
| 355 | 网络侧无 RCE（GoAhead/LD_PRELOAD/exec 全阴性；仅剩未测 CVE-2019-5096）； | 网络侧无 RCE（GoAhead/LD_PRELOAD/exec 全阴性； | `01_研究报告/10_跨机型移植边界_20261013.md:52` |
| 356 | ❌ 换代平台（S5II / S1M2 / S1RM2，SC2006A 一代） | token、tag、地址、编码管线四层都不同， | `01_研究报告/10_跨机型移植边界_20261013.md:63` |
| 357 | 视频质量侧对 6K 的探测（全部失败） |  | `01_研究报告/11_菜单条目注入可行性_20261013.md:30` |
| 358 | 而本项目已证 | 固件 AES 加密 + 签名校验，网络侧无 RCE，固件升级写路径卡在最终部分块 flash 定址。 | `01_研究报告/11_菜单条目注入可行性_20261013.md:47` |
| 359 | ❌ 把 6K 变成视频菜单里的常规档位 | 只有拿到固件改写或代码执行才可能， | `01_研究报告/11_菜单条目注入可行性_20261013.md:59` |
| 360 | 6K PHOTO 本身就是那条 6K 通道，用它即可，但无法把它"换皮"塞进录制格式菜单。 |  | `01_研究报告/11_菜单条目注入可行性_20261013.md:64` |
| 361 | ❌ 回 `ok` 但被静默忽略（读回仍是原值） |  | `01_研究报告/12_可写设置面审计_20261013.md:40` |
| 362 | ⇒ 服务菜单是纯机身 UI 层，不通过 Wi-Fi 接口暴露，远程无法枚举或操作。 |  | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:18` |
| 363 | 已排除的因素 |  | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:130` |
| 364 | 收 PTP 响应（bulk IN） | ❌ 永远超时 `0xE0004051`（kIOUSBTransactionTimeout）；无中断端点 | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:157` |
| 365 | 64 GB SDXC（相机格式化为 exFAT） | exFAT \| 灰 ❌ | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:186` |
| 366 | 这也解释了当初"NTSC MOV 格式无法更改录制质量"为何是个问题 | PAL 机型本不该有那些 NTSC 档位。 | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:258` |
| 367 | `0x2370` (9072) | 服务 / 厂商模式 \| ❌ \| ❌ 超时 | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:265` |
| 368 | 发出任意 `readValue` | ❌ 相机立即主动断链（"device has disconnected from us"） | `01_研究报告/15_蓝牙BLE协议逆向_20261013.md:102` |
| 369 | 相机进入蓝牙配对模式后再试 | ❌ 行为完全相同（仍一读即断） | `01_研究报告/15_蓝牙BLE协议逆向_20261013.md:103` |
| 370 | macOS 侧是否发起绑定 | ❌ 日志中没有任何配对/绑定尝试 | `01_研究报告/15_蓝牙BLE协议逆向_20261013.md:104` |
| 371 | 并触发配对），而是直接被对端关链路 | 无法自动建立绑定。 | `01_研究报告/15_蓝牙BLE协议逆向_20261013.md:108` |
| 372 | 未绑定链路上读取任意特征 | ❌ 一读即被断链（正常模式与配对模式相同） | `01_研究报告/15_蓝牙BLE协议逆向_20261013.md:121` |
| 373 | 系统弹配对、或用 iOS/Android 端 App 先建立绑定），否则读路径无法打开。 |  | `01_研究报告/15_蓝牙BLE协议逆向_20261013.md:126` |
| 374 | 5 | 本机对相机热点的关联请求全部失败（Windows：`特定的网络不可用`，RSSI 255），但热点持续可见、强度 87–88% \| ✓ 实测 | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:17` |
| 375 | 6 | 失败最可能的原因：相机 SoftAP 只允许单客户端，而手机正连着相机热点（用户确认） \| ◐ 待验证 | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:18` |
| 376 | 2.4 关联失败 | 现象与已排除项 | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:111` |
| 377 | `netsh wlan connect` 返回"成功接受"，但 约 2 s 后事件 `8002` 报失败 |  | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:113` |
| 378 | 已穷举并全部失败的手段 |  | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:121` |
| 379 | 配置文件连接（open/none），manual / auto | ❌ | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:125` |
| 380 | 关掉 MAC 随机化（`MacRandomization=false`） | ❌ | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:126` |
| 381 | 指定 BSSID 连接 | ❌ | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:127` |
| 382 | `wlan_connection_mode_discovery_unsecure(3)`（无配置直连开放网） | ❌ | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:128` |
| 383 | `wlan_connection_mode_temporary_profile(1)` | ❌（rc=1206） | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:129` |
| 384 | 关闭/启用 WLAN 网卡（复位射频） | ❌ | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:130` |
| 385 | 重启 `wlansvc` + 重新加配置文件 | ❌ | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:131` |
| 386 | 强制 PHY：802.11ax → 802.11n → 802.11a/b/g | ❌ | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:132` |
| 387 | 强制频段：Dual Band → 2.4 GHz Only | ❌ | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:133` |
| 388 | 首次扫描直接失败 | `BleakBluetoothNotAvailableError: Bluetooth radio is not powered on`。 | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:163` |
| 389 | 相机 `192.168.x.x` | ❌ 当前不可达，相机只在 AP 模式 | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:229` |
| 390 | B. 应用层协议前置（尚未被本项目排除） | APK 握手第 3 步是 | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:308` |
| 391 | 9.4 Wi-Fi 关联失败的原因修正（重要） |  | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:318` |
| 392 | 用户随后确认并断开了手机与相机热点的连接，但本机仍然关联失败。于是 |  | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:320` |
| 393 | 「单客户端占用」解释被削弱/排除（手机已断开仍失败）； |  | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:322` |
| 394 | ⇒ 失败原因是主机侧（MediaTek MT7921 驱动对这条非标准信标不买账）， |  | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:324` |
| 395 | `Beacon Interval = 200 TU`。驱动可以在扫描里列出它、却在选 BSS 时把它排除 | 正好对应 | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:326` |
| 396 | Windows（MT7921）无法关联该热点；本报告用 macOS 完成了接入与只读取证。 |  | `01_研究报告/18_相机热点SoftAP侧勘察_20261013.md:4` |
| 397 | 3 | ⇒ Windows 关联失败确认是主机侧问题（MT7921 驱动不吃这条非标准信标），与相机无关 \| ✓ 实测 | `01_研究报告/18_相机热点SoftAP侧勘察_20261013.md:14` |
| 398 | 2 | ❌ 第 2 步后断链 | `01_研究报告/19_BLE凭据链打通_先写后读_20261013.md:112` |
| 399 | 4 | ❌ 第 2 步后断链 | `01_研究报告/19_BLE凭据链打通_先写后读_20261013.md:114` |
| 400 | "BLE 读取需要绑定"（14/15 号） | ❌ 推翻，是协议顺序问题 | `01_研究报告/19_BLE凭据链打通_先写后读_20261013.md:125` |
| 401 | 4.5 两个被证伪的假设（记录以免重复踩） |  | `01_研究报告/20_BLE身份与WiFi门独立_20261013.md:102` |
| 402 | 4.5.1「BLE 握手会唤醒相机热点」 | ❌ 证伪 | `01_研究报告/20_BLE身份与WiFi门独立_20261013.md:104` |
| 403 | 4.5.2「扫到开放网络 = 相机热点」 | ❌ 不可靠 | `01_研究报告/20_BLE身份与WiFi门独立_20261013.md:112` |
| 404 | 推测注册的完成还需要 Wi-Fi 侧 accctrl 那一步，而该步要求 AP 在线（AP 未起 | 无法完成）。 | `01_研究报告/20_BLE身份与WiFi门独立_20261013.md:127` |
| 405 | 用户实测要点 | "先与相机握手之后它会自动开启 WiFi，而在配对模式下是无法退出的"。 | `01_研究报告/20_BLE身份与WiFi门独立_20261013.md:131` |
| 406 | [4] getstate/getinfo×4/getsetting/startsenddata | 全部 err_critical ❌ 门仍未开 | `01_研究报告/20_BLE身份与WiFi门独立_20261013.md:142` |
| 407 | 相机随后报"连接失败"并自动退出配对模式。 |  | `01_研究报告/20_BLE身份与WiFi门独立_20261013.md:150` |
| 408 | 1 | 保活定时器在每次读到密码时都新建一个 → 变成读循环轰炸 \| 相机 13 秒后断开，屏幕上显示"连接失败"（很可能是被刷崩的） \| 定时器全局只建一次；级联读只在首次握手时发生 | `01_研究报告/20_BLE身份与WiFi门独立_20261013.md:156` |
| 409 | P1–P3 | 拆机取证 / 服务模式组合键 / U-Boot console \| 需拆机或不可行 | `01_研究报告/21_S1R2_exFAT越界写对S5的意义_20261013.md:14` |
| 410 | 固件升级最终-chunk 定址失败（我们卡住的地方） | 有 root 可直接写 mtd，绕开 UPD 分块/校验流程 | `01_研究报告/21_S1R2_exFAT越界写对S5的意义_20261013.md:32` |
| 411 | 离线无法判定 |  | `01_研究报告/21_S1R2_exFAT越界写对S5的意义_20261013.md:41` |
| 412 | 因为 `clr_alloc_bitmap()` 是先内存写、后卡写，卡写失败才报错 |  | `01_研究报告/21_S1R2_exFAT越界写对S5的意义_20261013.md:69` |
| 413 | 能直接用在 S5 上吗？ | 不能直接套：SoC 代际不同、偏移全要重推；且固件加密导致我们离线无法确认 S5 是否有同款缺陷 | `01_研究报告/21_S1R2_exFAT越界写对S5的意义_20261013.md:95` |
| 414 | （附带效果 | 根目录所在簇被标记为空闲 → 文件系统不一致 → macOS 无法挂载、 | `01_研究报告/22_S5_exFAT越界写前置条件确认_20261013.md:58` |
| 415 | 7 | "自身链"要排除注入值 \| 链集合若在打完补丁后才记录，会把注入值也算进去，从而掩盖结论 | `01_研究报告/22_S5_exFAT越界写前置条件确认_20261013.md:80` |
| 416 | 491522 – 524289 | 120–127 \| ❌ 必崩：kmalloc-1024 的 slab 填充为 0 → NULL 解引用 | `01_研究报告/22_S5_exFAT越界写前置条件确认_20261013.md:96` |
| 417 | → 随后 sector_write 失败 → 相机报"写入错误 请检查卡" |  | `01_研究报告/22_S5_exFAT越界写前置条件确认_20261013.md:112` |
| 418 | 请以 §0 的修订结论为准，原 §4 的推理已被证伪，保留在文中仅作记录。 |  | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:5` |
| 419 | ③ "越界内存写已在 S5 执行" | ❌ 撤回 | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:18` |
| 420 | "`clr_alloc_bitmap` 先内存写、后卡写；相机报卡写失败 | 内存写必然已执行。" | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:32` |
| 421 | 既可能是"有效指针 + 卡写失败"，也可能是"NULL + 提前返回"，无法据此认定内存写已执行。 |  | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:38` |
| 422 | 1. 原判定依据（已证伪，保留作记录） |  | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:46` |
| 423 | exfat_bitmap_clear((u8 *)p_fs->vol_amap[i]->b_data, b); /* ① 纯内存写，无返回值、不会失败 */ | /* ① 纯内存写，无返回值、不会失败 */ | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:55` |
| 424 | return sector_write(sb, sector, p_fs->vol_amap[i], 0); /* ② 卡写，会失败 */ | /* ② 卡写，会失败 */ | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:56` |
| 425 | 相机报的是 ② 失败（"写入错误"） | ① 必然已经执行完毕。 | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:60` |
| 426 | 卡：macOS 仍能列目录，但读文件报 `Invalid argument` —— 文件系统已被这次失败的写操作弄成不一致状态。 |  | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:91` |
| 427 | 491522 – 524289 | 120–127 \| ❌ kmalloc-1024 slab 填充为 0 → NULL 解引用 → 必崩 | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:105` |
| 428 | 8. 堆喷实验 | 全部失败，并发现一个新的崩溃点 | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:134` |
| 429 | 都无法证明其意义 | 因为即便命中相邻槽，NULL 检查也可能让内存写根本不发生。 | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:138` |
| 430 | 两种情况下"slab 内槽位数"都是 128，索引边界都是 120–127，从越界行为无法区分； |  | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:163` |
| 431 | 先修掉污染的变量 | 用 T1–T3 把"文件本身导致崩溃"这个干扰排除， | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:192` |
| 432 | 已排除的变量 | 证据 | `01_研究报告/24_相机长文件名崩溃_定因_20261013.md:13` |
| 433 | ❌ 文件数量 | 2160 个短名文件 → 正常 | `01_研究报告/24_相机长文件名崩溃_定因_20261013.md:15` |
| 434 | ❌ 目录内容体量 | 202 KB 的短名条目 → 正常 | `01_研究报告/24_相机长文件名崩溃_定因_20261013.md:16` |
| 435 | ❌ 目录跨簇数 | 139 KB 跨 2 簇正常、202 KB 也跨 2 簇却崩 | `01_研究报告/24_相机长文件名崩溃_定因_20261013.md:17` |
| 436 | ❌ entry set 分配大小（576 B） | 360 个短名+篡改 `num_ext`（同样 576 B 分配）→ 正常 | `01_研究报告/24_相机长文件名崩溃_定因_20261013.md:18` |
| 437 | B vs C | 条目数、目录体量、跨簇数完全相同，只有名字长度与 entry set 大小不同 ⇒ 排除"数量/体量" | `01_研究报告/24_相机长文件名崩溃_定因_20261013.md:32` |
| 438 | B vs D | 分配大小完全相同（都是 576 B），只有名字长度不同 ⇒ 排除"分配大小"，锁定"长文件名" | `01_研究报告/24_相机长文件名崩溃_定因_20261013.md:33` |
| 439 | B: 360 × 240 字符 = 86 KB → ❌ 崩溃 |  | `01_研究报告/24_相机长文件名崩溃_定因_20261013.md:43` |
| 440 | 回滚：无法恢复数据。 |  | `01_研究报告/25_操作记录与风险手册_20261013.md:84` |
| 441 | 删除照片 | 只有在"注入 FAT 链尾"的实验中才需要；此时删除会失败（这是判据，不是故障） | `01_研究报告/25_操作记录与风险手册_20261013.md:128` |
| 442 | NULL 槽会提前返回、根本不碰内存，而相机屏幕上的表现与"内存写成功但卡写失败"完全一样。 |  | `01_研究报告/25_操作记录与风险手册_20261013.md:166` |
| 443 | "S5 内核越界写已实机确认" | ❌ 撤回 \| 决定性实验：注入索引 120（必为 NULL）→ 只报错不崩 ⇒ 存在 NULL 提前返回 | `01_研究报告/25_操作记录与风险手册_20261013.md:217` |
| 444 | "堆喷命中越界槽" | ❌ 撤回 \| A/B 对照：去掉注入后照样重启 | `01_研究报告/25_操作记录与风险手册_20261013.md:219` |
| 445 | 7 | "自身链"要排除注入值 \| 链集合若在打补丁后才记录，会掩盖结论 | `01_研究报告/25_操作记录与风险手册_20261013.md:271` |
| 446 | 11.2 `err_reject` 要退避重试（不是失败） |  | `01_研究报告/25_操作记录与风险手册_20261013.md:305` |
| 447 | 建议：最多 8–12 次，间隔 2–3 秒。单次调用会把成功误判为失败。 | 单次调用会把成功误判为失败。 | `01_研究报告/25_操作记录与风险手册_20261013.md:318` |
| 448 | 11.11 尝试隐藏档失败后应设回 allmenu 内档位 |  | `01_研究报告/25_操作记录与风险手册_20261013.md:410` |
| 449 | 当时的推理（错误） | `clr_alloc_bitmap()` 先内存写、后卡写 ⇒ 报卡写失败 ⇒ 内存写必已执行 | `01_研究报告/26_本次运行日志_20261013.md:64` |
| 450 | 2026-10-13 18 | 1x — 堆喷尝试（三轮，全部失败） | `01_研究报告/26_本次运行日志_20261013.md:67` |
| 451 | 目的：区分"空指针提前返回"与"有效指针 + 卡写失败" |  | `01_研究报告/26_本次运行日志_20261013.md:81` |
| 452 | 影响：❌ 撤回"S5 越界写已实机确认" |  | `01_研究报告/26_本次运行日志_20261013.md:85` |
| 453 | 症状：照片"文件在、但无法访问/无法删除" |  | `01_研究报告/26_本次运行日志_20261013.md:109` |
| 454 | 实际: 39 → 482 → 483 → 0xFFFFFFFF ❌ 只有 3 簇 |  | `01_研究报告/26_本次运行日志_20261013.md:114` |
| 455 | 目录簇链 | [38, 39] ❌ 目录被"扩展"到了照片的数据簇上 | `01_研究报告/26_本次运行日志_20261013.md:115` |
| 456 | B | 360 \| 240 \| 576 B \| 6480 \| 202 KB \| ❌ 崩 | `01_研究报告/26_本次运行日志_20261013.md:137` |
| 457 | B vs C | 排除"条目数/目录体量" | `01_研究报告/26_本次运行日志_20261013.md:141` |
| 458 | B vs D | 排除"entry-set 分配大小" | `01_研究报告/26_本次运行日志_20261013.md:142` |
| 459 | B: 360 × 240 = 86 KB → ❌ |  | `01_研究报告/26_本次运行日志_20261013.md:156` |
| 460 | 4 | ❌ 撤回："S5 越界写已实机确认" | `01_研究报告/26_本次运行日志_20261013.md:171` |
| 461 | 5 | ❌ 撤回："堆喷命中越界槽" | `01_研究报告/26_本次运行日志_20261013.md:172` |
| 462 | exFAT 越界写 | 判定为不成立（NULL 检查阻塞），不再投入 | `01_研究报告/26_本次运行日志_20261013.md:186` |
| 463 | 64GB 卡（exFAT） | ROM BACKUP 整体灰 ❌ | `01_研究报告/26_本次运行日志_20261013.md:198` |
| 464 | 结论：ROM BACKUP 打通；导出内容为标定/参数数据（无密钥、无固件，已用细粒度熵扫描排除） | 导出内容为标定/参数数据（无密钥、无固件，已用细粒度熵扫描排除） | `01_研究报告/26_本次运行日志_20261013.md:217` |
| 465 | 6 | ❌ `0x9606` 地址覆盖路线关闭（前置动作有高砖机风险，收益上限低） | `01_研究报告/26_本次运行日志_20261013.md:287` |
| 466 | 排除：`getstate` 实测只占 0.07s，不是心跳的锅 |  | `01_研究报告/26_本次运行日志_20261013.md:328` |
| 467 | 1 | 固定 20fps 播放 \| 队列储备 0 ⇒ 相机空档时画面定住 ❌ | `01_研究报告/26_本次运行日志_20261013.md:372` |
| 468 | 3 | 固定 ×0.85 \| 储备 12 帧，但队列满不停丢帧 ⇒ 跳帧 ❌ | `01_研究报告/26_本次运行日志_20261013.md:374` |
| 469 | 5 | 误差项误含"已发布帧" \| 播放冲到 48.5fps、垫帧 426 次 ❌ | `01_研究报告/26_本次运行日志_20261013.md:376` |
| 470 | 7.2 ❌ camctrl（触摸对焦/峰值/AE锁定）仍未打通 | 如实记录 | `01_研究报告/26_本次运行日志_20261013.md:395` |
| 471 | `ok` | ✅ 全部可用 \| ❌ 全部 `err_busy` | `01_研究报告/26_本次运行日志_20261013.md:401` |
| 472 | `ok_under_research_no_msg` | ✅ 全部可用 \| ❌ 全部 `err_reject` | `01_研究报告/26_本次运行日志_20261013.md:402` |
| 473 | 已排除的原因（逐条实验） |  | `01_研究报告/26_本次运行日志_20261013.md:404` |
| 474 | ❌ 命令格式错 | 已从官方 APK 逐条对齐，且 实测成功过一次（`touch 320/216 + value2=on → ok`） | `01_研究报告/26_本次运行日志_20261013.md:405` |
| 475 | ❌ 取景流抢占 | 停流后仍是 `err_busy` | `01_研究报告/26_本次运行日志_20261013.md:406` |
| 476 | ❌ App 名不被认可 | 改用 `LUMIX Sync` 注册无效 | `01_研究报告/26_本次运行日志_20261013.md:407` |
| 477 | ❌ 权限等级 | 获得裸 `ok` 后仍是 `err_busy` | `01_研究报告/26_本次运行日志_20261013.md:408` |
| 478 | ❌ 会话 ID 头 | 项目已知 S5 不签发令牌 | `01_研究报告/26_本次运行日志_20261013.md:409` |
| 479 | 触摸对焦 / 峰值 / AE锁定（camctrl） | ❌ 未打通，门控未定位；已排除 5 类原因，下一步需相机侧屏幕状态枚举 | `01_研究报告/26_本次运行日志_20261013.md:444` |
| 480 | 连续快发（≥5Hz） | ❌ `err_busy` | `01_研究报告/26_本次运行日志_20261013.md:517` |
| 481 | `camctrl change_disp_mag 300/500/1000/2000` | ❌ err_reject \| ★ 不再是 err_busy ⇒ 参数格式已对（官方值=倍率×100，300–2000），是状态拒绝 | `01_研究报告/26_本次运行日志_20261013.md:611` |
| 482 | `camctrl asst_disp`（多种参数组合） | ❌ `err_param` \| 参数格式仍未确定 | `01_研究报告/26_本次运行日志_20261013.md:612` |
| 483 | `touch`（触摸对焦） | ✅ 100% 成功 \| ❌ `err_reject`（符合相机设计：MF 下无触摸 AF） | `01_研究报告/26_本次运行日志_20261013.md:646` |
| 484 | `af_ae_lock` | ✅ 可用 \| ❌ `err_reject` | `01_研究报告/26_本次运行日志_20261013.md:647` |
| 485 | `change_disp_mag` | ❌ `err_reject` \| ❌ `err_reject` | `01_研究报告/26_本次运行日志_20261013.md:648` |
| 486 | 放大辅助 | ❌ `err_reject` \| 参数已修正为官方规范（300–2000），门未找到；待验证「相机菜单放大辅助开关」 | `01_研究报告/26_本次运行日志_20261013.md:659` |
| 487 | 峰值（`asst_disp`） | ❌ `err_param` \| 参数格式未确定 | `01_研究报告/26_本次运行日志_20261013.md:660` |
| 488 | `camctrl` 会随授权状态翻动而间歇失败 | 必须重试，单发必然时好时坏 | `01_研究报告/26_本次运行日志_20261013.md:670` |
| 489 | 4.3 曾疑为密钥的两块高熵区 | 已排除 | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:111` |
| 490 | 写坏引导相关字段 | 可能无法开机（需服务通道） | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:150` |
| 491 | ❌ 固件明文（内核 / rootfs） | ROM BACKUP 只覆盖 EEPROM 标定区 | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:156` |
| 492 | ❌ AES 密钥（在 MC801 片内 OTP） |  | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:157` |
| 493 | ❌ 对"固件解密"主线没有直接帮助 |  | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:158` |
| 494 | ⇒ 用官方 Tether 无法测试任意地址（硬编码常量）；但自定义客户端在协议上可以改写回送值。 |  | `01_研究报告/28_PTP固件更新协议审计_20261013.md:57` |
| 495 | `0x00090013` | FWUP Request（升级请求） \| 升级线程内联，无独立包装 \| ❌ 本次新增 | `01_研究报告/28_PTP固件更新协议审计_20261013.md:87` |
| 496 | `0x00090014` | FWUP UPDATE（开始烧写） \| 升级线程内联 \| ❌ 本次新增 | `01_研究报告/28_PTP固件更新协议审计_20261013.md:88` |
| 497 | 兜底 | ❌ 无 —— 项目自己判定 SD.DAT 恢复模式"有砖机史、不可逆" | `01_研究报告/28_PTP固件更新协议审计_20261013.md:129` |
| 498 | 2^128 | 仍不可行 | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:120` |
| 499 | ⇒ 密钥仍是真随机、固化在 MC8244/MC801 片内 ⇒ 纯离线数学破解不可行。 |  | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:210` |
| 500 | 1 | RAM dump（服务模式 / PTP vendor 扩展 / Wi-Fi 诊断口） \| ❌ \| 引导后固件已由硬件解密进 DDR ⇒ 内存里是明文 | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:217` |
| 501 | 3 | 向 S1R2 团队索取 `0x9606` 免擦除进入法 \| ❌ \| 见 §6，有分歧需澄清 | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:219` |
| 502 | 4 | 用 §3/§4 的极速判据重跑一遍大规模撞库（如 2^48） \| ❌ \| 期望值低（但成本也低，AES-NI 几小时） | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:220` |
| 503 | 5 | 继续扩大语义字典撞库 \| ❌ \| 不建议（S1R2 已穷尽 282 万角度） | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:221` |
| 504 | raw[doff | doff+size] # ❌ doff 是相对【外层数据基址 0x200】的偏移 | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:258` |
| 505 | 我的切片 raw[0x1E01400] 首块 = cb078899… ❌ 非零（但明文应全零！） |  | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:268` |
| 506 | `pairs_s5.json` / `pairs_s5.bin` | ❌ 作废（已改名 `*.WRONG_offby0x200`） | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:296` |
| 507 | 6 | "两份独立分析互相印证" \| 不成立 —— 后一份沿用前一份假设，不是独立证据 ⇒ 已改措辞 | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:340` |
| 508 | ❌ 未确认标准 CBC、IV 具体用途、摘要处理阶段、密钥存放位置 |  | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:363` |
| 509 | ❌ 未恢复任何程序明文，未打破 AES |  | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:364` |
| 510 | ❌ 未证明密钥"真随机/在 OTP"（只是有限候选未命中） |  | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:365` |
| 511 | ❌ ROM BACKUP 与固件同名分区的关系未闭合 |  | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:366` |
| 512 | 2.7 其它失败样例 |  | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:134` |
| 513 | 四种变量组合全部失败 |  | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:150` |
| 514 | 在这个模式下重测 5.9K，结果依旧是全部失败（`err_reject` / `err_param`）。 |  | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:170` |
| 515 | 4.2 菜单读的是 RAM 值 | 双轨方案不成立 | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:229` |
| 516 | 实测证伪。 当时 flash 里存的确实是 `0x9b`（allmenu 安全），但 RAM 一旦设为 | 实测证伪。 | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:233` |
| 517 | "flash 安全 + RAM 隐藏"的双轨方案不成立。 |  | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:237` |
| 518 | 本条与 §4.1 是同一机制的两个表现面 | 条目可见与菜单变灰是同一失配的两面，无法同时满足。 | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:310` |
| 519 | 因此无法把隐藏档"注册"成常规菜单入口。 |  | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:312` |
| 520 | `err_critical` | 严重状态错误 \| 先重试一次（实测 `recmode` 重试即 `ok`），仍失败则重启相机 | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:375` |
| 521 | ⇒ 单次调用会把成功误判为失败。 |  | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:401` |
| 522 | `00_项目总结/02_项目时间线.md` §当前状态 | 「三项全部跨断电持久 ✓」→ 后被改为「持久化只对 `ntsc_pal` 成立；`videoformat` 回落 mp4」 \| 该二次更正亦不成立（见下条）。受控复测（n=2）中三项均保留 | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:423` |
| 523 | ⇒ 可判定写入已落地，观测到的保留/降档并非"写入失败"所致。 |  | `01_研究报告/31_录制格式持久化_受控复测_20261014.md:85` |
| 524 | 读取时机 | 若在未断电时读回 RAM 副本，无法区分"未持久"与"已持久但被后续改写"。 | `01_研究报告/31_录制格式持久化_受控复测_20261014.md:121` |
| 525 | 结论分级 | ✅ = 源码逐行核实；⚠️ = 部分核实或与 README 表述不同；❌ = 官方 app 中不存在。 | `03_解包_APK/com.panasonic.jp.lumixsync/PROTOCOL_AUDIT.md:4` |
| 526 | 时序：`startsenddata` →（`senddata` × N 块）→ `requestsenddata`（续块确认）→ `endsenddata`；失败 `abortsenddata`。 | 失败 `abortsenddata`。 | `03_解包_APK/com.panasonic.jp.lumixsync/PROTOCOL_AUDIT.md:118` |
| 527 | 3.2 LUT / 照片风格上传（❌ 官方无此协议） |  | `03_解包_APK/com.panasonic.jp.lumixsync/PROTOCOL_AUDIT.md:135` |
| 528 | 删除照片 | ❌ 官方无任何删除命令（无 `delimage`/`delete`/`camcmd delimage`）；`delete` 字符串只出现在 DLNA 能力解析（云自动上传相关），不删除相机文件。S5Monitor 的删除功能无协议依据。 | `03_解包_APK/com.panasonic.jp.lumixsync/PROTOCOL_AUDIT.md:162` |
| 529 | LUT 上传 | ❌ 无协议依据（§3.2）。 | `03_解包_APK/com.panasonic.jp.lumixsync/PROTOCOL_AUDIT.md:163` |
| 530 | 密钥无法从 app、固件文件或相机 HTTP 接口获取。 解密尝试排除了全部标准算法（XOR、AES-128/256 ECB/CBC/CTR、SHA-384 标签）；相机命令面与活体探测均无任何「读内存/固件/密钥」的口子。密钥在 MC801 芯片内部，HTTP 接口不暴露。 | 解密尝试排除了全部标准算法（XOR、AES-128/256 ECB/CBC/CTR、SHA-384 标签）； | `03_解包_APK/com.panasonic.jp.lumixsync/README.md:18` |
| 531 | 已排除（在 dtb/rootfs1 上实测） | 单字节 XOR；重复密钥 XOR（密钥候选：`"panasonic"`、0x220 64 字节块、48 字节字段、loader1 前 28 字节）；AES-128/256 的 ECB、CBC、CTR（全部候选密钥与 IV，含「48 字节 = 32 字节密钥 + 16 字节 IV」与「64 字节 = 密钥+IV」两组）；SHA-384 作为校验标签。 | `03_解包_APK/com.panasonic.jp.lumixsync/README.md:86` |
| 532 | 佐证发现 | 0x220 的 64 字节块在 S5 与 S5M2 间不同（后经社区仓库确证为 ECDSA P-256 签名，非密钥材料）；分区 `unk` 字段 = 目的 RAM 加载地址（loader2@0x1000、dtb@0x3B00800 等反例证伪「128KB 对齐 flash 地址」说）；条目 48 字节字段 = SHA-256(明文) + 每分区 IV。 | `03_解包_APK/com.panasonic.jp.lumixsync/README.md:87` |
| 533 | 社区调研（已完成） | 两个 lumix-s1m2-research 仓库（`research_repos/`）已调研并互验。结论与我们的负结果一致：S1M2=MC8243、S5M2=MC8223、S5=MC801 三平台同族 UPD 但算法/密钥隔离；社区已穷举排除全部离线破解（含 GH2 自嵌式密钥移植、13 万+ 探测），密钥固化在芯片硬件（OTP/eFuse/Crypto Engine/TrustZone），固件文件内无密钥材料。唯一可复用的是 UPD 解包/探测脚本（`unpack_upd.py` 等），无密钥。详见 `rese… | `03_解包_APK/com.panasonic.jp.lumixsync/README.md:132` |
| 534 | 验证逻辑绕过（已完成，负结果，见 `research_repos/verify_logic_notes.md`） | 明文容器内无内嵌公钥（公钥只在 BootROM/OTP，Phison 式「同替公钥+签名」不可行）、无回退标志/次级验证路径（验证工件仅 CRC32+ECDSA P-256+RSA-4096 三件）、版本字段(外层 0x24 / 内层 0x2C4)被 ECDSA+RSA 签名覆盖——改版本/降级必破坏签名。纯软件无绕过路径。附带纠正：`loader1` 的「28 字节随机数」实为分区表与数据区 44B 重叠的一部分（末项 hr_c_ddr 的 12B SHA-256 尾 + 16B IV，另 16B 零填充）；lo… | `03_解包_APK/com.panasonic.jp.lumixsync/README.md:134` |
| 535 | 待验证（相机当下已休眠/离线，无法实测） |  | `03_解包_APK/com.panasonic.jp.lumixsync/camera_api/lumix_key_method.md:111` |
| 536 | `ppubs.uspto.gov` | 可达、能拿匿名会话令牌，但搜索/计数 API 直接调用返回 `400 Invalid request content`（匿名 guest token + 缺 caseId，无法用纯 curl 复现浏览器搜索，需真实浏览器登录）。 | `03_解包_APK/com.panasonic.jp.lumixsync/patent_fcc_research.md:11` |
| 537 | Bing 走通但只回品牌首页，无法用于检索专利/FCC。 |  | `03_解包_APK/com.panasonic.jp.lumixsync/patent_fcc_research.md:13` |
| 538 | 会话的 caseId/完整 payload，无法用 curl 离线复现。要自动化需先登录 myUSPTO 并在浏览器 |  | `03_解包_APK/com.panasonic.jp.lumixsync/patent_fcc_research.md:62` |
| 539 | 1.4 安全侧（DoS / 溢出 / RCE 路线，均已排除或仅剩 DoS） |  | `04_工具与脚本/TOOLS_工具箱总览.md:43` |
| 540 | `goahead_overflow.py` / `overflow_fuzz.py` / `mutation_test.py` | GoAhead 溢出 fuzz \| ✗ | `04_工具与脚本/TOOLS_工具箱总览.md:49` |
| 541 | `rce_ldpreload.py` / `rce_probe.py` / `rce_surface_probe.py` | RCE 路线 \| ✗ 全失败 | `04_工具与脚本/TOOLS_工具箱总览.md:51` |
| 542 | `launch_daemon.py` | 服务/进程面探测 \| ✗ | `04_工具与脚本/TOOLS_工具箱总览.md:52` |
| 543 | ECDSA 公钥 | 离线拿不到（参考仓库与本地 `ivsig.py` 均无，明确写「需公钥,无法离线完成」）。 | `04_工具与脚本/campaign2/README.md:17` |
| 544 | → 无法离线判断 `0x220` 的签名是否覆盖 `0x1C`。唯一判定办法 = 相机上 Phase I 实测。 |  | `04_工具与脚本/campaign2/README.md:18` |
| 545 | `lumix_hidden_format.py` | 把写质量后「格式自动变为目标家族」当作二次变更（`--accept-secondary-change`），并要求读回质量与格式都精确匹配才算选择成功（`expected = 'mp4ed' if token.startswith('mp4ed_') else 'mp4'`）。其 `restore_visible` 只恢复 getter 读到的可见原值，并明示「无法恢复未知后台记忆槽位」——与「逐格式独立质量记忆 + 独立格式记录」一致。 | `04_工具与脚本/campaign2/out/S1H_format_persistence.md:65` |
| 546 | 符号：`LMX_func_api_RecInfo_4K6K_Get/Set_RecFormat_Param`（行 19117/19167），底层 tag 0x020001c0（`LmxExt_Get_4K6K_Info`，struct `tag_LMX_STRUCT_4K6K_INFO`）。此 `RecFormat` 是 4K/6K 照片连拍/后对焦的录制格式，与视频容器 mp4/mov 无关，不要混淆。相关 `Get4k6kcuttingInfo` tag 0x12800110 在采集清单中返回 0x2002（失… | 相关 `Get4k6kcuttingInfo` tag 0x12800110 在采集清单中返回 0x2002（失败）。 | `04_工具与脚本/campaign2/out/S1M2_format_field_notes.md:63` |
| 547 | 0x9414 | 0x12800110 \| `Get4k6kcuttingInfo` \| 失败 0x2002 | `04_工具与脚本/campaign2/out/S1M2_format_field_notes.md:74` |
| 548 | 可排除：PTP 侧 `Mov_Config_Quality_mode / Rec_mode`、`Mov_Filter_Compression_method` 都不是“容器”字段；`RecInfo_4K6K_RecFormat` 是照片模式。 | 可排除：PTP 侧 `Mov_Config_Quality_mode / Rec_mode`、`Mov_Filter_Compression_method` 都不是“容器”字段； | `04_工具与脚本/campaign2/out/S1M2_format_field_notes.md:90` |
| 549 | "任一槽 = mov | 开机活动槽 = mov"不成立：S5II 有 slot1=`06` 却仍以 slot0=`05` 为活动容器。 | `04_工具与脚本/campaign2/out/S5II_slot_crosscheck_20261013.md:54` |
| 550 | 所以单纯的"影子槽派生"（把某个槽直接提升为活动值）被这组数据排除。 |  | `04_工具与脚本/campaign2/out/S5II_slot_crosscheck_20261013.md:55` |
| 551 | 剩下的与 S5 失败自洽的读法是按上下文/模式索引 | 活动容器 = 当前上下文对应的那个槽。 | `04_工具与脚本/campaign2/out/S5II_slot_crosscheck_20261013.md:59` |
| 552 | 这能在不写 flash 的前提下直接证实/证伪"上下文索引"读法。建议在实验前先做这一步。 | 这能在不写 flash 的前提下直接证实/证伪"上下文索引"读法。 | `04_工具与脚本/campaign2/out/S5II_slot_crosscheck_20261013.md:73` |
| 553 | (d) 手动指定 tag 参数（默认 0x080000a2；失败可试 0x080000a1） | 失败可试 0x080000a1） | `04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:53` |
| 554 | `mode=fuzz` | CVE 类只读探测（2026-10-11 实机验证，结果见主报告 §9.3–9.4）。43 个探测覆盖：基线只读 / 参数数量与取值（0/1/2/3 参、非法 tag/事件 ID）/ TID 边界（0、0xFFFFFFFF、复用）/ 未知邻接操作码发现。全部 exact-length、排除全部写/动作操作码；参数错误类输入设备回干净错误码（0x2002/0x201d/0x2005/0x0000 NAK）且保持存活。每探测产出 `fuzz_0x<op>_p<参>_t<TID>.bin`（数据载荷，若有）+ `.res… | `04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:104` |
| 555 | Python 报 `claim_interface 失败 (code=AccessDenied)` | macOS 系统相机栈占用了 PTP 设备 \| 关掉所有相机相关 App → 拔插 USB → 立刻重跑；仍不行就改用原生 `./s5_ptp_dump`（推荐，macOS 上应直接用原生） | `04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:120` |
| 556 | `0x9421` 返回 `0x2002 GeneralError` | tag 参数/会话不对 \| 脚本会自动尝试 `0x080000a1`、`0x00000000`；都失败则看下面"会话"条 | `04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:122` |
| 557 | 本项目已实机确认 | 升级请求类命令有高砖机风险，因此永久排除。 | `04_工具与脚本/s5_monitor/README.md:138` |
| 558 | 触摸对焦 | ✅ 有 \| ❌ 无 | `04_工具与脚本/s5_monitor/README.md:161` |
| 559 | 远程控制（拍照/录像/参数） | ✅ 有 \| ❌ 无 | `04_工具与脚本/s5_monitor/README.md:162` |
| 560 | 不发心跳 | 相机约 13 秒后停流 ❌ | `04_工具与脚本/s5_monitor/README.md:211` |
| 561 | 每 2–3 秒一次（心跳 + 浏览器轮询同时打） | 相机持续繁忙 ⇒ 取景流反复卡顿 ❌ | `04_工具与脚本/s5_monitor/README.md:212` |
| 562 | 如果播放帧率 ≥ 相机到达速率 | 队列被抽干 ⇒ 相机空档时只能垫帧 ⇒ 画面定住 = 卡顿 ❌ | `04_工具与脚本/s5_monitor/README.md:364` |
| 563 | 1.00（固定 20） | 20.0 \| 0 \| ❌ 每 0.5–0.75s 定住一次 | `04_工具与脚本/s5_monitor/README.md:372` |
| 564 | ❌ 全部回到 err_busy | 即使间隔 5 秒单发也不行 | `04_工具与脚本/s5_monitor/README.md:560` |
| 565 | 没有任何 UI 事件注入接口。无法"帮你在相机菜单里点某个按钮"。 |  | `04_工具与脚本/s5_monitor/README.md:573` |
| 566 | `touch`（触摸对焦） | ✅ 窗口期可用 \| ❌ `err_reject`（符合逻辑：MF 下触摸 AF 无效） | `04_工具与脚本/s5_monitor/README.md:626` |
| 567 | `af_ae_lock` | ✅ 窗口期可用 \| ❌ `err_reject` | `04_工具与脚本/s5_monitor/README.md:627` |
| 568 | `change_disp_mag`（放大辅助） | ❌ `err_reject` \| ❌ `err_reject`（MF 也拒绝） | `04_工具与脚本/s5_monitor/README.md:628` |
| 569 | ⇒ `change_disp_mag` 的门不在对焦模式（已排除 MF）； |  | `04_工具与脚本/s5_monitor/README.md:630` |
| 570 | iOS 无法与非 MFi 认证的 USB 设备通信，因此原 App 的「USB 高速文件传输」这一能力无法原样移植到 iOS。iOS 上唯一可行、且与官方 LUMIX Sync 一致的传输通道是 Wi-Fi |  | `05_源码/LumixFast-iOS/README.md:18` |
| 571 | 之前 GoAhead buffer overflow、LD_PRELOAD(EV-43360/CVE-2017-17562)均已失败,本表面为 Panasonic 定制 CGI(err_critical 行为 + XHTML 错误页指纹)。 |  | `06_数据与证据/camera_settings/OPENGATE_FINDINGS.md:49` |
| 572 | 结论:网络层 RCE 极难/很可能不可行;已证明的可控原语是 setsetting 状态写(47 个可写域),可作状态变更/取证,但非代码执行。 | 结论:网络层 RCE 极难/很可能不可行; | `06_数据与证据/camera_settings/OPENGATE_FINDINGS.md:50` |
| 573 | 「S5 内核越界写已实机确认」 | 撤回（越界索引处存在 NULL 提前返回，原判据不成立） | `09_exFAT越界写成果包_20261013/README.md:20` |
| 574 | 「S5 内核越界写已实机确认」 | ❌ 撤回 | `10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/README.md:26` |
| 575 | 「堆喷命中越界槽」 | ❌ 撤回 | `10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/README.md:27` |
| 576 | exFAT 越界写路线 | ❌ 判定不成立，不再投入 | `10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/README.md:29` |
| 577 | 这一天的工作分三条线 | 解锁隐藏录制格式（已完成）、exFAT 漏洞（证伪）、 | `11_DC-S5成果包_20261013/00_成果总结_全文.md:12` |
| 578 | "S5 内核越界写已实机确认" | ❌ 撤回 \| 注入必为 NULL 的 slab 填充区索引（120）→ 只报错不崩 ⇒ 存在 `if (vol_amap[i]==NULL) return -EIO` ⇒ 原推理"报卡写失败 ⇒ 内存写已执行"不成立 | `11_DC-S5成果包_20261013/00_成果总结_全文.md:64` |
| 579 | 4 | 触发变量 = 长文件名本身（排除数量/体量/entry-set 分配大小） \| ✅ | `11_DC-S5成果包_20261013/00_成果总结_全文.md:84` |
| 580 | B | 360 \| 240 \| 576 B \| 6480 \| 202 KB \| ❌ 反复重启 | `11_DC-S5成果包_20261013/00_成果总结_全文.md:92` |
| 581 | 4. 已关闭 / 判定不成立的路线 |  | `11_DC-S5成果包_20261013/00_成果总结_全文.md:107` |
| 582 | `0x9606` 地址覆盖（任意地址写） | ❌ 关闭 —— 要看到地址必须先发 `0x9406/0x00090013`（升级请求）⇒ 疑似先擦除 ⇒ 高砖机风险；且数据仍必须过签名校验 ⇒ 拿不到执行自编代码的能力。与项目红线一致（"永不发送 `0x9406` 子码"） | `11_DC-S5成果包_20261013/00_成果总结_全文.md:111` |
| 583 | exFAT 越界写 | ❌ 不成立（NULL 检查阻塞） | `11_DC-S5成果包_20261013/00_成果总结_全文.md:112` |
| 584 | 转接环 / 离线破解固件 | ❌ 已证伪（密钥在 MC801 OTP） | `11_DC-S5成果包_20261013/00_成果总结_全文.md:113` |
| 585 | Wi-Fi 调试后门 | ❌ 已证伪 | `11_DC-S5成果包_20261013/00_成果总结_全文.md:114` |
| 586 | ❌ 转接环 / 离线破解 / Wi-Fi 后门 / exFAT 越界 / 0x9606 覆盖 |  | `11_DC-S5成果包_20261013/00_成果总结_全文.md:122` |
| 587 | EEPROM 内含密钥/固件？ | ❌ 没有（细粒度熵扫描实证） | `11_DC-S5成果包_20261013/README.md:41` |
| 588 | `0x9606` 地址覆盖路线 | ❌ 关闭（前置动作有高砖机风险，收益上限低） | `11_DC-S5成果包_20261013/README.md:43` |
| 589 | exFAT 越界写 | ❌ 已撤回（NULL 检查阻塞） | `11_DC-S5成果包_20261013/README.md:44` |
| 590 | 蓝牙（BLE） | 仅用于配对/唤醒，带宽 KB/s 级，无法提升画质 | `12_S5无线监看_v1.0_20261014/README.md:75` |
| 591 | 关于蓝牙（已排除） |  | `12_S5无线监看_v1.0_20261014/README.md:185` |
| 592 | ❌ 危险 | 不带 value（UUID）的 req_acc 会留下匿名 pending， | `12_S5无线监看_v1.0_20261014/README.md:234` |
| 593 | 这属于环境因素，软件层无法根治（可用 `--pacing-fps` 调低目标帧率让节奏更稳）。 |  | `12_S5无线监看_v1.0_20261014/README.md:407` |
| 594 | 顺带排除 | ClashX 代理的 `ExceptionsList` 含 `192.168.0.0/16`，局域网流量绕过代理，与本问题无关。 | `12_S5无线监看_v1.0_20261014/README.md:409` |
| 595 | ⇒ 这是相机侧行为（低照度降帧 / 无线链路），软件层无法根治。 |  | `12_S5无线监看_v1.0_20261014/README.md:456` |
| 596 | 新画面占比 | 40/40 = 100%（重复率 0%） ✅ \| 18/30（重复率 40%）❌ | `12_S5无线监看_v1.0_20261014/README.md:472` |
| 597 | 端到端延迟 | 53 ms ✅ \| 400–700 ms ❌ | `12_S5无线监看_v1.0_20261014/README.md:473` |
| 598 | 全新 UUID | ❌ 创建"待批复"请求 ⇒ 之后所有请求都看到 `err_others_requesting` | `12_S5无线监看_v1.0_20261014/README.md:492` |
| 599 | 匿名（不带 `value`） | ❌ 同上，同样污染 | `12_S5无线监看_v1.0_20261014/README.md:493` |
| 600 | MF（手动） | ❌ 触摸对焦失效（相机设计如此），请改用 「焦点近/远」 按钮 | `12_S5无线监看_v1.0_20261014/使用说明.md:81` |
| 601 | 蓝牙（BLE）只用于配对/唤醒，带宽仅 KB/s 级，无法提升画质。 |  | `12_S5无线监看_v1.0_20261014/使用说明.md:95` |
| 602 | 每 2–3 秒一次 | 相机持续繁忙 ⇒ 流反复卡顿 ❌ | `12_S5无线监看_v1.0_20261014/附_技术参考.md:57` |
| 603 | 没有工厂 shell、没有 autorun。 | fpSup 的机制无法静态验证，最可能待的地方是加密段。 | `13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md:18` |
| 604 | ⇒ "第二个配置藏着固件更新接口"这一猜测已排除。 |  | `13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md:62` |
| 605 | 4. 已排除的路径（含证据，不要再走） |  | `13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md:96` |
| 606 | EP0 厂商 OUT 请求（零长度，无数据阶段） | 3 个接收者（`0x40`/`41`/`42`）× `bRequest` `0x00–0xFF`，768 个请求 \| 全部 STALL，0 命中。`wLength=0`/`pData=NULL` 硬编码，无法携带载荷 | `13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md:101` |
| 607 | `SetConfiguration` | 强制切配置 1、配置 2 \| 配置 1 设置成功但写入仍超时；配置 2 设置失败 `0xe00002ed`。`GetConfiguration` 始终返回 `0xe00002ed`、值 0 ⇒ 配置切换不是关键 | `13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md:105` |
| 608 | ~~任务 2 | EP0 零长度厂商 OUT 探针~~ —— 已完成，阴性（2026-10-14） | `13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md:202` |
| 609 | ⇒ EP0 双向穷举完毕，`0x2370` 无法从主机侧用 EP0 打开。 |  | `13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md:211` |
| 610 | （`s5_usb_ep0` 代码里断言了方向位，无法写入） |  | `13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md:236` |
| 611 | [SetConfiguration(2)] -> 0xe00002ed ← 设置失败 |  | `13_USB服务通道勘察_交接包_20261014/01_实测记录.md:183` |
| 612 | `GetConfiguration` 始终失败（`0xe00002ed`）并返回值 0 | 读不到当前配置 | `13_USB服务通道勘察_交接包_20261014/01_实测记录.md:188` |
| 613 | 配置 1 能设置成功，但写入仍超时 | 配置切换不是关键，该假设排除 | `13_USB服务通道勘察_交接包_20261014/01_实测记录.md:189` |
| 614 | 配置 2 无法设置 |  | `13_USB服务通道勘察_交接包_20261014/01_实测记录.md:190` |
| 615 | （默认） | ❌ \| 被动监听 interrupt IN 与 bulk IN | `13_USB服务通道勘察_交接包_20261014/02_工具/README.md:44` |
| 616 | 非 IN 请求直接拒绝执行 | 这个工具物理上无法向设备写入任何数据。 | `13_USB服务通道勘察_交接包_20261014/02_工具/README.md:66` |
| 617 | `s5_usb_desc` | ❌ 完全不能 | `13_USB服务通道勘察_交接包_20261014/02_工具/README.md:114` |
| 618 | `s5_usb_ep0` | ❌ 完全不能（代码内断言） | `13_USB服务通道勘察_交接包_20261014/02_工具/README.md:115` |
| 619 | 排除误报 | 0x2370 从未作为立即数出现， | `13_USB服务通道勘察_交接包_20261014/03_Tether协议线索.md:119` |
| 620 | 1 | [`00_交接总结_全文.md`](00_交接总结_全文.md) \| 总入口：背景 / 已确认事实 / 已排除路径 / 两个未解异常 / 交接任务 / 安全红线 | `13_USB服务通道勘察_交接包_20261014/README.md:17` |
| 621 | 最要紧的问题 | 全库有 4 条旗舰级结论的证据链在审计中不成立（见 §2 S1–S4），其中 2 条是"实验本身没改变任何字节"与"工具偏移 bug 使实验对假设零检验力"——不是推理强弱之争，而是证据有效性问题。 | `14_总包审计与新方向_20261014/00_审计总报告.md:15` |
| 622 | R8 | 库内 `curmenu.xml` 档位 \| 仅 5 个 mp4 + 1 个 mp4hevc `enable=yes`（PAL+mp4 态） \| 无法复现 18/12/10（详见 §3 B5） | `14_总包审计与新方向_20261014/00_审计总报告.md:59` |
| 623 | S1 ★★★ 10-14"受控复测"的写入是空操作，持久化旗舰结论证据不成立 |  | `14_总包审计与新方向_20261014/00_审计总报告.md:69` |
| 624 | 由此：`31 §5 "三项均跨断电保留"` 只能读作"一个原本就存在的状态在重启后仍是它自己"，无法支撑"blob 写入可持久化"。 |  | `14_总包审计与新方向_20261014/00_审计总报告.md:84` |
| 625 | `raw[doff : +size]`（脚本现状） | 2 / 7 ❌ | `14_总包审计与新方向_20261014/00_审计总报告.md:111` |
| 626 | 5240 key × 3 IV = 0 命中 | `S5_AES破解可行性评估_20261011.md:79` \| ❌ 需重跑 | `14_总包审计与新方向_20261014/00_审计总报告.md:137` |
| 627 | 211 候选真实 AES 恢复 = 0 命中 | 同上 :559-565 \| ❌ 需重跑 | `14_总包审计与新方向_20261014/00_审计总报告.md:138` |
| 628 | "记录 SHA ≠ 存储字节哈希" | 同上 :116-121 \| ❌ 已被 R4 直接反证 | `14_总包审计与新方向_20261014/00_审计总报告.md:140` |
| 629 | ⇒ 反例取自已知无效的对照组；"写入形态"与"协议版本"完全混淆，无法分离因果。 |  | `14_总包审计与新方向_20261014/00_审计总报告.md:167` |
| 630 | ⇒ 31 §3.3 的实验无法分离 RAM 与 flash（"camsetting 随当前值即时变化"对"同时写两者"与"只写 flash"都成立）。其"不写 flash"这个前提已被同一项目撤销。 |  | `14_总包审计与新方向_20261014/00_审计总报告.md:189` |
| 631 | 项目最著名的撤回是"相机报写入错误 | 内存写已执行"不成立（NULL 提前返回表现一样）。但： | `14_总包审计与新方向_20261014/00_审计总报告.md:200` |
| 632 | `persist.py:450` | `requestsenddata` 的返回值完全未检查 → separate 模式下若该步失败，代码静默继续发下一块 → 块序错位/截断 | `14_总包审计与新方向_20261014/00_审计总报告.md:250` |
| 633 | `persist.py:406,446` | `abortsenddata` 返回值未检查 → 失败时相机可能残留 send 会话（项目文档明确"残留会话需断电重启"） | `14_总包审计与新方向_20261014/00_审计总报告.md:251` |
| 634 | A7 ★★ 撤回逻辑本身也不成立 | NULL 检查从未被证实 | `14_总包审计与新方向_20261014/00_审计总报告.md:277` |
| 635 | ⇒ 该"决定性实验"在两个方向上都不成立：既不能证明 NULL 检查存在（"有效指针 + 卡写失败"同样只报错不崩），也不能维持原结论。 |  | `14_总包审计与新方向_20261014/00_审计总报告.md:283` |
| 636 | A8 ★★ exFAT 归档证据无法复核 22 号报告的核心主张 |  | `14_总包审计与新方向_20261014/00_审计总报告.md:287` |
| 637 | ⇒ 22 号的"指纹一致 ✅"无法从归档复核。 |  | `14_总包审计与新方向_20261014/00_审计总报告.md:299` |
| 638 | B5 ★★ "NTSC+mov=18 / PAL+mov=12 / NTSC+mp4=8+2"无法离线复现 |  | `14_总包审计与新方向_20261014/00_审计总报告.md:354` |
| 639 | 能力 | `ivsig.py` = "签名与校验验证" \| 只做 `1<=r,s<n` 与 low-s 检查；`Crypto.PublicKey.ECC` 导入未使用，无法离线验签 | `14_总包审计与新方向_20261014/00_审计总报告.md:382` |
| 640 | "端口扫描 1–10000 只有 80，没有 DLNA" | `16 号:78-88` \| 已被 18 号部分证伪：热点模式 `60606` 直返 200 的 UPnP 设备描述 | `14_总包审计与新方向_20261014/00_审计总报告.md:398` |
| 641 | "`0x2370` 无法用任何 EP0/bulk 手段打开" | `13 包 11_结论:36-39` \| EP0 空间巨大，实测只是两个切面；bulk 只试 8 种自造帧 ⇒ 构造性否证，非穷尽 | `14_总包审计与新方向_20261014/00_审计总报告.md:400` |
| 642 | "UART 死路" | `06_S1R2:33-35` \| 全部依据是 S1R2 实测；S5 的 P3 核验从未执行 | `14_总包审计与新方向_20261014/00_审计总报告.md:401` |
| 643 | `P1022641.MP4`（213 MB）在本地工作树中存在两份（`06_数据与证据/hidden_format_evidence/recording/P1022641/` 与 `01_研究报告/05_Panasonic_hidden_format_参考/evidence/recording/P1022641/`，共约 426 MB）。公平地说 | `REPO_CONTENTS.md:79` 的"已排除"是对 Git 仓库说的，属实（`.gitignore` 忽略 `*.MP4`，`git ls-files` 只跟踪同目录的 `.metadata.json`/`.log`）。问题在本地去重清单不完整——`README.md:179-186` 的"以下重复内容已删除，仅保留一份"逐项清单里没有这一项，而它恰好是全包最大的重复文件。 | `14_总包审计与新方向_20261014/00_审计总报告.md:410` |
| 644 | ECDSA 公钥恢复实测 | 90,144 组假设（602 个唯一消息候选 × 3 曲线 [P-256/secp256k1/brainpoolP256r1] × 11 种哈希 × 4 种编码端序），约 1,014 GB 哈希 → 0 收敛，公钥未恢复。消息族含：任务指定 8 范围、签名区清零/整段移除、头部 `0x1C/0x24/0x3C/0x40` 全部 16 个子集清零、复合拼接、分区表内嵌 SHA-256、尾部锚定区间、全部结构边界两两组成的连续区间穷尽扫描。工具自检 6/6 PASS（真收敛必被检出；不同私钥阴性对照 0 误报；RSA … | `14_总包审计与新方向_20261014/00_审计总报告.md:493` |
| 645 | RSA-4096 模数恢复 | e ∈ {3,5,7,17,257} × 3,620 候选 × BE/LE 全排除；e=65537 前 24 名高先验候选（PKCS#1 v1.5 + DigestInfo）× BE/LE 全排除（3,012 s）⇒ 未恢复出模数 N；「尾块 512B 是 RSA-4096」无正面依据（512B=4096bit 只是尺寸巧合） | `14_总包审计与新方向_20261014/00_审计总报告.md:495` |
| 646 | 两处推理更正 | ①「尾块首字节 `89 a1` 不是 `00 01`，故排除 PKCS#1 v1.5」不成立——`s = m^d mod N` 在 `[0,N)` 近似均匀，`00 01` 前缀描述的是编码后的消息 m，不是 `s`；②「`r,s ∈ [1,n-1]` 支持 P-256 判定」几乎无信息量——随机 256-bit 整数落在该区间的概率是 `1−2^−32` | `14_总包审计与新方向_20261014/00_审计总报告.md:496` |
| 647 | 「版本字段在签名覆盖内」 | 裁决：不可判定。可数学确证（与签名方案无关，5/5 实测）：`stored CRC32 == zlib.crc32(data[0x200:])`、内层头 `0x2A0-0x2E0` 逐字节等于外层头 `0x00-0x40`、`0x3C == L-0x200`。因此外层 `0x1C`/`0x24` 不在 CRC32 覆盖内；内层副本 `0x2BC`/`0x2C4` 在覆盖内且落在 `[0x200, L-512)` ⇒ 只要存在任何覆盖 ⊇`[0x200, L-512)` 的签名，版本字段的值就被该签名覆盖。可确证的只… | `14_总包审计与新方向_20261014/00_审计总报告.md:497` |
| 648 | "越界索引处存在 NULL 检查" | 撤回逻辑本身不成立（A7） \| ◐ 两种解释均未证实 | `14_总包审计与新方向_20261014/00_审计总报告.md:515` |
| 649 | "UART 死路" | S1R2 类比，S5 P3 从未执行 \| ◐ S5 未验证 | `14_总包审计与新方向_20261014/00_审计总报告.md:520` |
| 650 | "只开 80 端口" | 已被热点模式 50001/60606 部分证伪 \| ◐ 模式相关 | `14_总包审计与新方向_20261014/00_审计总报告.md:521` |
| 651 | ❌ 已失效 / 不应再引用 |  | `14_总包审计与新方向_20261014/00_审计总报告.md:523` |
| 652 | "改 `comm_proto_ver` 绕过版本门" | 已证伪（但见下方补充：其前提「版本字段被签名覆盖」同样无正面依据） | `14_总包审计与新方向_20261014/00_审计总报告.md:529` |
| 653 | "网络层 RCE（GoAhead 溢出/LD_PRELOAD/file-op/exec）" | 已证伪 | `14_总包审计与新方向_20261014/00_审计总报告.md:530` |
| 654 | ❌ 不含相机专有部分 | 全树无 exFAT 驱动、无 PTP/MTP gadget（`f_*` 里没有 `f_ptp`）、`# CONFIG_CRYPTO_HW is not set`。⇒ 这是裁剪后的平台树，不是整机固件内核。 | `14_总包审计与新方向_20261014/00_审计总报告.md:559` |
| 655 | ⇒ 因此 `f_fs.c` 无 `current_alt_setting` 这一阴性结论，效力仅限于"该 FZ1K2 树"，对 DC-S5 实机不具备排除力。本项目此前把它当成 S5 的内核来引用（如英文稿的 "OSS mismatch" 论点），属于机型绑定错误。 | ⇒ 因此 `f_fs.c` 无 `current_alt_setting` 这一阴性结论，效力仅限于"该 FZ1K2 树"，对 DC-S5 实机不具备排除力。 | `14_总包审计与新方向_20261014/00_审计总报告.md:564` |
| 656 | 8 | 官方 Tether 在 `0x2382` 抓包复核固件升级帧（抓到 `startsenddata` 即止） \| 唯一能判定"末块失败是相机对所有人都拒绝，还是我们客户端的问题"；这是把"签名 oracle / 块定址"从推测变结论的关键对照 | `14_总包审计与新方向_20261014/00_审计总报告.md:573` |
| 657 | 所有"样本量"批评都基于项目自己记录在案的次数；若实际执行次数多于记录，该批评不成立。 | 若实际执行次数多于记录，该批评不成立。 | `14_总包审计与新方向_20261014/00_审计总报告.md:677` |
| 658 | 它在 `README.md` / `REPO_CONTENTS.md` 里的更正状态是什么？（✅ / ◐ / ❌） |  | `14_总包审计与新方向_20261014/02_全包查看指令手册.md:27` |
| 659 | 判读：`P1022641.MP4` 在本地工作树出现两次（约 426 MB）。注意区分两个口径：`REPO_CONTENTS.md:79` 说的"已排除"是指 Git 仓库（属实，`.gitignore` 忽略 `*.MP4`，`git ls-files` 只跟踪同目录的元数据）；而 `README.md:179-186` 那份"本地去重清单"里没有列这一项 ⇒ 本地去重不完整，全包最大的重复文件被漏掉。 | 注意区分两个口径：`REPO_CONTENTS.md:79` 说的"已排除"是指 Git 仓库（属实，`.gitignore` 忽略 `*.MP4`，`git ls-files` 只跟踪同目录的元数据）； | `14_总包审计与新方向_20261014/02_全包查看指令手册.md:70` |
| 660 | sed -n '80,150p' README.md # 核心结论速览（已证/已证伪/仍开放） |  | `14_总包审计与新方向_20261014/02_全包查看指令手册.md:94` |
| 661 | 99-109 | 已证伪 / 不可行（✗ 不要再走） \| 含 exFAT 越界写的撤回 | `14_总包审计与新方向_20261014/02_全包查看指令手册.md:105` |
| 662 | 判读：报告把这两对分别称为"写入前备份（T1/T2）"与"写入 payload（T1/T2）"，但它们逐字节相同 ⇒ 写入没有改动任何字节 ⇒ §3.2「写入确已落地的验证」不成立。 |  | `14_总包审计与新方向_20261014/02_全包查看指令手册.md:173` |
| 663 | ❌ 但它是裁剪发布 | 无 exFAT 驱动、无 PTP gadget、`CONFIG_CRYPTO_HW` 未设 ⇒ 不是整机固件内核。 | `14_总包审计与新方向_20261014/02_全包查看指令手册.md:396` |
| 664 | ✗ / ❌ | 证伪或已撤回 | `14_总包审计与新方向_20261014/02_全包查看指令手册.md:446` |
| 665 | "不再可行 / 死路" | 去核是"实测证伪"还是"未做/别机型类比"（UART 死路、只开 80 端口） | `14_总包审计与新方向_20261014/02_全包查看指令手册.md:457` |
| 666 | 原则：每个方向都给出「为什么可行 / 需要什么 / 风险 / 成功判据 / 失败也得到什么」。第一梯队零设备零风险，建议今天就做。 | 原则：每个方向都给出「为什么可行 / 需要什么 / 风险 / 成功判据 / 失败也得到什么」。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:4` |
| 667 | 失败也有收获 | 若不到 7/7，说明连 `DATA_BASE` 模型也不完整（需要重新做偏移判决），这本身就是重要发现——在确认模型前不要做任何大规模穷举，否则只会重复生产无效数据。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:106` |
| 668 | ✅ 已完成（2026-10-14）。累计 90,144 组假设（602 唯一消息候选 × 3 曲线 × 11 哈希 × 4 编码端序，约 1,014 GB 哈希） | 零收敛，公钥未恢复；工具自检 6/6 PASS 故该否定有意义。「版本字段是否在签名覆盖内」裁决为【不可判定】。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:121` |
| 669 | 失败也有收获 | 若 5 版无法收敛到同一公钥，说明签名并非 P-256、或签名布局/端序与假设不同 ⇒ 直接修正 `FIRMWARE_FORMAT.md` 的字段定义。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:187` |
| 670 | ✅ 已完成（2026-10-14） | e ∈ {3,5,7,17,257} × 3,620 候选全部排除；e=65537 前 24 名高先验候选（PKCS#1 v1.5 + DigestInfo）也全部排除。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:195` |
| 671 | `verify_logic_notes.md | 97-99` 已排除 PKCS#1 v1.5 ⇒ 疑为 PSS 或裸 RSA，正好适用。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:201` |
| 672 | 失败也有收获 | 确认"仅 `ipu_data` 一个已知明文"，则可把此前"40/41 无已知明文"从估计升级为穷举了本组模板后的确认。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:253` |
| 673 | 唯一能判的判决 | 块全同 ⇒ ECB；块全不同 ⇒ 只能排除 ECB，CBC 与 CTR 不可区分 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:275` |
| 674 | n == len(...) | 排除 ECB；CBC 与 CTR 在本数据上不可区分（需密钥 / 同 (key,IV) 下明文被改动的第二份密文 / 运行时 DDR 才能定） | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:281` |
| 675 | `ipu_data` 实测 `n = 16384 / 16384` | 只能排除 ECB，不能判定 CBC 还是 CTR。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:283` |
| 676 | `eep_ow_a ≡ eep_ow_b` 与 `eep_act_a ≡ eep_act_b` 的记录 SHA 相同 | 在"记录 SHA = 明文 SHA"的前提下，这是两对天然的同明文、不同 IV 样本，无需密钥即可用来检验任何 keystream/padding 假设（实测逐字节相等率 0.3716% / 0.2930%，XOR 熵 ≈ 8 ⇒ 排除 ECB 与固定 XOR 流）。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:286` |
| 677 | S5 实机是否有 F1/F2 越界？ | ❌ 不能 \| 树是裁剪发布（缺 exFAT/PTP/加密引擎），且机型绑定未验证 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:312` |
| 678 | exFAT 驱动是否做簇号归属校验？ | ❌ 不能 \| 树里根本没有 exFAT 驱动 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:313` |
| 679 | 附带产出 | `f_fs.c` 的离线审计结论（无 `current_alt_setting`）应登记为阴性结果 + 限定条件，并去修正 `09-已证伪路线.md:20-24` 把"S5 迁移性 ◐ 待审计"误写成"已证伪"的问题。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:334` |
| 680 | 7.8 | 从 `29 号` 一并检查：项目自认"唯一副作用是 1 次 length-DoS"与"多次 90MB 流送已致相机多次 brick"矛盾 \| `S5_AES…:415` vs `00-执行摘要:46` \| 设备可能已非正常态，影响所有"设备行为"阴性结论的可信度 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:349` |
| 681 | 项目对固件升级末块的判定是"flash 定址失败"，但可观测证据只有 HTTP 层 `err_busy` | `err_critical` + ~31 s 处理时延，没有任何 flash 专用错误码。而项目从未用官方 Tether 做过对照——因此无法区分： | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:358` |
| 682 | Tether 是官方客户端。若 Tether 也失败 | 支持 A；若成功 ⇒ 说明 B，且能直接对照官方分块参数。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:363` |
| 683 | 主要需要排除的三个替代解释（本次审计新提出） |  | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:381` |
| 684 | 项目目前所有实验的判据都是二值信号（"崩/不崩"、"报错/不报错"）。这正是 S1（空操作无法检出）、A7（NULL 检查无法证实）这类问题的根源。 |  | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:393` |
| 685 | `ERR CODE DISP` | 显示历史错误码 —— 可把"失败"细分成不同错误类别 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:396` |
| 686 | exFAT | 用错误码区分"NULL 提前返回"与"卡写失败"——这正是 A7 无法区分的那两种情形。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:414` |
| 687 | `18 号 | 89-94` 实测：热点模式下 `http://192.168.54.1:60606/Lumix/Server0/ddd` 直返 200 的 XML 设备描述——即不需要走 accctrl 门。而 `16 号:78-88` 的"只开 80 端口"结论已被此部分证伪（那个扫描是在 station 模式下做的）。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:442` |
| 688 | `13 号报告 | 156` 记"bulk OUT 写入成功（设备 ACK）"，而本次实测全 `0xe0004051` 超时（`01_实测记录:194-204`）。工具 `s5_usb_listen.c:142` 调用了 `SetAlternateInterface(0)`，但返回值被忽略 ⇒ "接口未真正切到 alt 0 也会造成写超时"这一替代解释未被排除。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:481` |
| 689 | 检查 SetAlternateInterface 的返回码，失败则中止并报错。 |  | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:485` |
| 690 | 现状：项目把"UART 死路"列为已排除，但依据完全是 S1R2 实测（`BOOTDELAY=-2` / `console=null`）；S5 的这项核验（P3）在 `00_S5结合点:82` 明确标"未做"。 | 现状：项目把"UART 死路"列为已排除，但依据完全是 S1R2 实测（`BOOTDELAY=-2` / `console=null`）； | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:506` |
| 691 | 价值：把"S1R2 类比"变成"S5 上不可判定"这一明确结论，避免后人误以为已经排除。 |  | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:532` |
| 692 | 失败也得到什么 | 若在非空操作下 mov 依然回退，则项目原来的"回落 mp4"结论被正确复现，S1 的批评得到闭合。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:563` |
| 693 | 1 | 6. OSS 内核树审计 + 绑定验证 \| 无 \| 🟢 零 \| f_fs 阴性结论 + 边界声明 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:701` |
| 694 | 2 | 8. Tether 抓包对照 \| Win/Linux + USBPcap \| 🟡 低（抓到即止） \| 判定末块失败归因 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:703` |
| 695 | 改 `comm_proto_ver` 绕过版本门 | 已证伪（字段方向 + 无比较逻辑） | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:749` |
| 696 | exFAT 越界写提权 | 已撤回；且撤回逻辑本身也不成立（A7）。若重启，先找到不依赖相机屏幕的判据 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:750` |
| 697 | 无对照地重复末块上传 | 12 次 × 30 s 的连续擦写有写放大风险，且存在循环论证（"重试后失败被当作必然失败"） | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:751` |
| 698 | 且 31 号 §3.2 的另一项子主张（"T2 重启后读回与写入 payload 逐字节仅差 13 个字节"）也不成立 | payload 与它自己的备份零字节差异。 | `14_总包审计与新方向_20261014/05_相机只读快照_20261014/README.md:58` |
| 699 | `curmenu.xml` | `79af32bdbddc…`（47,162 B，3 份全同） \| `719c26aa6740…`（43,233 B） \| ❌ 不同态：归档是 PAL+mp4（仅 5 个 mp4 + 1 个 mp4hevc `enable=yes`）；本次实机是 NTSC+mov（18 档） | `14_总包审计与新方向_20261014/05_相机只读快照_20261014/README.md:73` |
| 700 | 阳性对照 | 成功。自造「已知密钥 + 已知明文」样本，真密钥确证在候选集合内，用同一套搜索逻辑：错误偏移 0 命中（6/6 配置全部假阴性），正确偏移 每个配置都精确命中真密钥（1 个不同密钥，无假阳性） ⇒ 项目那两次「0 命中」对假设零检验力 | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:15` |
| 701 | 被推翻 ❌ | ①「记录 SHA 是逻辑校验和、≠存储字节哈希」；②「5240 key × 3 IV = 0 命中 ⇒ 密钥非文件内派生」；③「211 候选 = 0 命中 ⇒ 同上」 | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:16` |
| 702 | 维持 ✅ | ⑦ 41 个 IV 逐版本全变 / 全唯一；⑧ 同偏移密文相等率 ≈0.4% ⇒ 排除 ECB 与版本稳定 keystream；⑨ 跨版本差分被封死、SSTIC 旋转规律不成立；⑩ Nikon「padding 泄露 keystream」手法在 S5 不成立 | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:18` |
| 703 | 没有推翻任何一条正向的结构性观测（IV 全变、密文无关、排除 ECB）； |  | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:22` |
| 704 | 结论：❌ 推翻。 记录 SHA 就是该分区【明文内容】的 SHA-256。 | 结论：❌ 推翻。 | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:94` |
| 705 | ⇒ 只能排除「ECB + 常量明文」，不能区分 CBC 与 CTR。 |  | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:176` |
| 706 | `eep_ow_a` / `eep_ow_b` | ✅ \| ❌ \| 0.3716% \| ❌ \| 7.9987 | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:182` |
| 707 | `eep_act_a` / `eep_act_b` | ✅ \| ❌ \| 0.2930% \| ❌ \| 7.9184 | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:183` |
| 708 | ECB | 相等率应 100%（实测 ≈0.37% ⇒ 排除） | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:185` |
| 709 | 固定 XOR 流（Nikon 式） | XOR 应恒为 0（实测 XOR 熵 ≈8 ⇒ 排除） | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:186` |
| 710 | 「排除 ECB / 版本稳定 keystream」的结论 ✅ 维持，且现在有了更硬的前提 | 这 39 个"明文相同"是由 | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:226` |
| 711 | 「同密钥不同 IV」和「不同密钥」都相容，无法区分。 |  | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:236` |
| 712 | 5. 实验 4 ★ | 阳性对照 —— 证明"0 命中"是假阴性 | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:261` |
| 713 | 问题：真实固件里我们不知道密钥，所以无法从"0 命中"本身判断搜索逻辑有没有检验力。 |  | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:263` |
| 714 | Oracle-SHA | 6/6 全部漏检（假阴性） \| 6/6 全部命中真密钥（各 1 个不同密钥，无假阳性） | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:282` |
| 715 | Oracle-PREFIX | 6/6 全部漏检（假阴性） \| 6/6 全部命中真密钥 | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:283` |
| 716 | ❌ 推翻这两条推论。 |  | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:312` |
| 717 | 1 | 记录 SHA 是逻辑校验和、≠ 存储字节哈希 \| `S5_AES…:116-121` \| ❌ 推翻 \| 正确偏移 7/7；`storage` 记录 SHA == `SHA256(b'')` | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:322` |
| 718 | 3 | `ipu_data` 明文 ≈全零、仅 508 字节非零 \| `S5_AES…:127` \| ❌ 推翻（细节） \| 正确偏移下非零字节 0；错误偏移下恰好复现 508 | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:324` |
| 719 | 5 | 5240 key × 3 IV = 0 命中 ⇒ 密钥非文件内派生 \| `S5_AES…:79` \| ❌ 推翻（证据无效） \| exp4：阳性对照 12/12 假阴性 | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:326` |
| 720 | 6 | 211 候选真实 AES 恢复 = 0 命中 ⇒ 同上 \| `S5_AES…:157,559-565` \| ❌ 推翻（证据无效） \| exp4：211 子集 wrong=0 / correct=命中真密钥 | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:327` |
| 721 | 8 | 同偏移密文相等率 ≈0.4% ⇒ 排除 ECB / 版本稳定 keystream \| `S5_AES…:111-112` \| ✅ 维持（且证据更强） \| exp3-4.2：全体平均 0.3881% vs 随机基线 0.3906%；exp2-3.4 已证同明文对照 | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:329` |
| 722 | 9 | 5 版实测封死跨版本差分；SSTIC 旋转规律不成立 \| `S5_AES…:114` \| ✅ 维持 \| exp3-4.1/4.2：39 个明文未变的分区密文仍与随机不可区分 | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:330` |
| 723 | 10 | Nikon「padding 泄露 keystream」手法在 S5 不成立 \| `S5_AES…:546` \| ✅ 维持（且前提已证） \| exp2-3.4：同明文不同 IV 的密文 XOR 熵 7.9987（非固定 XOR 流） | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:331` |
| 724 | 12 | 密钥不在固件文件内 ⇒ 只能在芯片安全域 \| `S5_AES…:156` \| ◐ 需进一步实验 \| 原证据（两次搜索）已判无效；既未证伪也未证实 | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:333` |
| 725 | 13 | AES 密钥提取不可行（已证实·终局） \| `00-执行摘要:12` \| ◐ 需进一步实验（降级） \| 两条核心否定证据被推翻 ⇒ 不支持"已证实""终局" | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:334` |
| 726 | 统计：❌ 推翻 4 条（#1、#3、#5、#6）｜◐ 降级/需进一步实验 4 条（#4、#11、#12、#13）｜✅ 维持 5 条（#2、#7、#8、#9、#10）｜⚠️ 范围外 1 条（#14）。 |  | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:337` |
| 727 | N2 | `eep_ow_a`≡`eep_ow_b`、`eep_act_a`≡`eep_act_b` 的记录 SHA 相同 ⇒ 已证同明文对照对 \| 无需密钥即可做"同明文不同 IV"实验（排除 ECB / 固定 XOR 流） | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:346` |
| 728 | `exp4_positive_control.py` | 实验 4 ★：阳性对照（假阴性证明）+ 块全同准则纠错 | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:408` |
| 729 | 它是不是 ECDSA P-256 签名？ | 不可判定（无法证实也无法证伪） \| 假设（见 §4 证据溯源） | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:15` |
| 730 | 5 个版本能否恢复出同一个 ECDSA 公钥？ | 否 —— 累计 90,144 组（曲线×哈希×编码×消息）假设下零收敛 \| 数学上确证（穷举失败，见 §3） | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:16` |
| 731 | 签名覆盖范围是什么？ | 不可判定（离线）；但已排除大量具体假设 \| 排除清单见 §3.5 | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:18` |
| 732 | `0x1C` / `0x24` 版本字段是否在签名覆盖范围内？ | 不可判定。既不是「成立」也不是「不成立」 \| 见 §5 | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:19` |
| 733 | 项目文档「ECDSA 覆盖外层头 `0x0-0x200`」这一具体假设 | 在本次穷举范围内未被支持（被排除） \| 见 §3.5 / §5.3 | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:20` |
| 734 | `verify_logic_notes.md` 自认的「强假设」，在完成本轮全部离线数学之后，仍然是不可判定的 | 但它从「未经验证的强假设」升级为「已被大规模穷举排除掉一大批具体形态的、不可判定的开放问题」，并且暴露出其证据来源本身已被上游撤回（§4）。 | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:22` |
| 735 | 「r,s 是合法标量 | 支持 P-256 判定」不成立。 随机 256-bit 整数落在 `[1, n-1]` 的概率是 `1 - 2^-32`（因为 `2^256 - n ≈ 2^224`）。所以「5/5 合法」的观测在任何 256-bit 随机数据上都会出现，不构成 P-256 的证据。`verify_logic_notes.md` 自己已加了「不证明验签内容」的限定，但该限定比它看上去更弱。 | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:65` |
| 736 | 不收敛 | 该假设被排除（这是本工作的用法）。 | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:85` |
| 737 | T3 | 阴性对照：3 个固件用不同私钥签同一范围 \| PASS（0 收敛，无误报） | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:93` |
| 738 | 3. 公钥恢复穷举 | 结果与已排除假设清单 | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:104` |
| 739 | 结果：0 命中。 该族假设被排除。（注意：若是 HMAC 或带密钥的 KDF 输出，离线不可判定。） | 该族假设被排除。 | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:143` |
| 740 | 3.5 已排除假设清单（明确列举） |  | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:145` |
| 741 | 以下假设全部被跨 5 版收敛判据排除（判据误报率 ≈ `2^-256`，且工具有 §2 的检出能力自检） |  | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:147` |
| 742 | 曲线：P-256 / secp256k1 / brainpoolP256r1 —— 3 条全部排除 |  | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:149` |
| 743 | 编码端序 | 4 种全部排除 | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:150` |
| 744 | 哈希：11 种摘要构造全部排除 —— `sha256`、`sha256d`、`sha384`(截断 32B / 全长)、`sha512`(截断 32B / 全长)、`sha1`、`sha224`、`sha3-256`、`blake2s`、`blake2b-256` |  | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:151` |
| 745 | 消息：602 个不同候选（按名称去重；各家族条目合计 605）全部排除，其中包括： | 各家族条目合计 605）全部排除，其中包括： | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:152` |
| 746 | 「64 字节是明文摘要（含 SHA-512 全长）」 | 排除 | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:158` |
| 747 | 3.6 仍未排除、且原理上离线不可判定的可能 |  | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:160` |
| 748 | 非 ECDSA 原语 | Schnorr（BIP-340 也是 64B = `R.x ‖ s`）、HMAC-SHA-512、两个独立 32 字节随机数/密钥材料等。这些没有公钥恢复性质，因此在没有公钥的前提下无法用离线数学证实或证伪。 | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:164` |
| 749 | 本项目 `verify_logic_notes.md` E5/问题2 | 「`0x220` 64 字节 ECDSA P-256…… r,s ∈ [1,n−1] 合法标量——支持「P-256 签名」判定」 \| 该「支持」不成立（§1.2 更正 1） | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:178` |
| 750 | 不是「成立」，也不是「不成立」。理由 |  | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:191` |
| 751 | 覆盖范围取决于签名方案与实现，而这些无法从明文容器中读出（验签逻辑在加密的 loader2/loader3/BootROM 内）； |  | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:193` |
| 752 | `verify_logic_notes.md` 写 | 「ECDSA 覆盖范围无公钥无法实测，但按结构最可能是外层头（0x0-0x200），即外层 0x24 被 ECDSA 覆盖（判定为强假设，未验签）」。 | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:221` |
| 753 | 说明：`e = 65537` 时 `s^e` 有 2.68 亿位，单次 gcd 约 90 秒（GMP）。脚本默认只跑高先验子集并受 `--max-cands-65537` / `--budget` 限制；`--max-cands-65537 0` 之外的完整穷举在时间上不可行，这一覆盖缺口已在 §7 局限中声明。 | `--max-cands-65537 0` 之外的完整穷举在时间上不可行，这一覆盖缺口已在 §7 局限中声明。 | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:271` |
| 754 | 该推理在密码学上不成立。 PKCS#1 v1.5 里「以 `00 01` 开头」描述的是编码后的消息 m，而我们观察到的是签名值 `s = m^d mod N`。`s` 在 `[0, N)` 上近似均匀分布，其首字节是 `0x89` 的概率约 1/256 量级 | 这与填充方式完全无关。换言之： | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:279` |
| 755 | 「首字节 `89 a1`」不能排除 PKCS#1 v1.5； |  | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:281` |
| 756 | 「511/512 非零」同样不能排除 PKCS#1 v1.5（`s` 本来就几乎不可能是 0）。 |  | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:282` |
| 757 | 无公钥 | 无正面确认。 公钥恢复是「猜测 + 交叉验证」，只能排除假设，不能在没有正确摘要猜测时发现真值。本工作给出的是否定性证据，不是证明签名不存在。 | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:290` |
| 758 | 「不是 ECDSA」无法证明。 Schnorr、HMAC-SHA-512、两个独立随机 32 字节值等在无公钥/无密钥时原理上不可区分。 |  | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:293` |
| 759 | 0) 先证明工具有检出能力（合成固件，含阴性对照） |  | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:307` |
| 760 | 撤回 E9 的 PKCS#1 v1.5 排除论证（§6.2），并撤回「r,s 合法 | 支持 P-256」的推论（§1.2）。 | `14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md:343` |
| 761 | 31 号 §3.2 的另一项子主张也被证伪 | 它称"T2 重启后读回与写入 payload 逐字节仅差 13 个字节"，而 payload 与它自己的备份零字节差异 ⇒ 该 13 字节差是相机自身相对于写入前状态的运行期变化，与"写入"无关。 | `14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:59` |
| 762 | ④-1 方向 15（S5 U-Boot console 离线核验） | 结论：S5 上不可判定，但已排除"离线找得到" | `14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:132` |
| 763 | `UART console 死路` 在 S5 上无法从离线证据判定；项目此前仅凭 S1R2 类比（`06_S1R2 | 33-35`），而 `00_S5结合点:82` 自己也把该核验标为"未做"。 | `14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:151` |
| 764 | 引用时必须写成 "S5 未验证"，不能写成"已排除"。要判定只能靠拆机接 UART 读 bootlog。 | 引用时必须写成 "S5 未验证"，不能写成"已排除"。 | `14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:152` |
| 765 | 因此审计首轮做的 `f_fs.c` 阴性结论（全树无 `current_alt_setting`）效力仅限于"该 FZ1K2 树"，对 S5 实机不具备排除力。已在 [`00_审计总报告.md`](14_总包审计与新方向_20261014/00_审计总报告.md) 方向 6 专栏回填更正。 | 因此审计首轮做的 `f_fs.c` 阴性结论（全树无 `current_alt_setting`）效力仅限于"该 FZ1K2 树"，对 S5 实机不具备排除力。 | `14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:250` |
| 766 | S5 是否有自己的 OSPO 页 | 本次未能确认（harness 无法访问 `ospo.panasonic.com`，其解析到非公网地址）。建议人工用浏览器访问 `https://ospo.panasonic.com/oss/dsc/` 索引页，查是否存在 `DC-S5` 条目——这是唯一能判定"松下是否为 S5 发布了内核源码"的一步。 | `14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:252` |
| 767 | 而 `ipu_data` 正确偏移下实测 `16384/16384` | 只能排除 ECB；CBC 与 CTR 在本数据上不可区分。 | `14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:280` |
| 768 | 教训：判据类准则在写进实验设计前应先做阳性/阴性对照自测——这正是本次 `exp4_positive_control.py` 起的作用。 |  | `14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:283` |
| 769 | 那些 `实时 LUT` / `LUT Base Photo Style` 字符串只出现在 Android `classes.dex` 字符串池，本次无法做方法级归因（无可用 JRE，`jadx` 跑不起来；dex `class_data_item` 增量解析未对齐） | 不能断定"存在可写的 LUT property tag"，只能作为待验证线索。 | `14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:300` |
| 770 | ❌ 不能写「固件里没有 LUT」。 |  | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:92` |
| 771 | 2.6 顺带排除的两条"歪路" |  | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:94` |
| 772 | 路径 | 为何不可行 | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:96` |
| 773 | 固件改写 / 跨代移植 | 三重门同时关闭：① AES 密钥在 MC801 片内（离线不可恢复）；② 签名硬门；③ 升级写路径从未成功过一次 `endsenddata`（末块 41456 B 定址失败 ~31 s → `err_busy`/`err_critical`）。且 MC801（32 位 A7）与 S5II 的 SC2006A（4×A53）跨代，移植不可行 | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:99` |
| 774 | ⚠️ 项目记载 64 GB 及以上 exFAT 卡在机身某些功能上会受限（ROM BACKUP 即因文件系统变灰，`13 | 182-191`）。若 LUT 读入失败，先换 FAT32 卡试。 | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:126` |
| 775 | ❌ 路径 D | 让 S5 像 S5II 那样"实时 LUT 烧进文件" —— 不可行 | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:142` |
| 776 | 1) 菜单零 LUT（含排除 Resolution 假阳性） |  | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:191` |
| 777 | 那些 LUT 字符串只出现在 dex 字符串池；本次无法做方法级归因（无可用 JRE，`jadx` 跑不起来） | 不能断定"存在可写的 LUT property tag"。 | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:236` |
| 778 | 若要坐实 | 需 JRE + jadx/baksmali，在 `/tmp` 解一次，定位 `LUT Base Photo Style` / `实时 LUT` / `LUT不透明度` 的 const-string 使用点及邻近的 `0x0?xxxxxx` tag 常量。这是唯一尚未排除的"USB PTP 直写 LUT"候选路径。 | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:239` |
| 779 | ⚠️ 诚实标注 | DC-S5 完整版说明书的 PDF 是松下私有加密（VCIS，非标准 RC4/AES），三次密钥派生尝试均失败 ⇒ S5 手册只能给到页码级；段落原文用措辞完全一致的 S5M2 官方手册代替（同一功能名 `[V-Log View Assist]`）。因此「初代 S5 能否加载自定义 `.VLT`」属高度可能但未逐字确证。 | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:262` |
| 780 | ⇒ `/AD_LUT/` 这一说法在官方与实测证据中均不成立。 |  | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:277` |
| 781 | 内嵌 base Photo Style | ❌ 不支持 \| ✅ 仅 `.cube` 支持 `#LUMIXPHOTOSTYLE <TAG>` | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:317` |
| 782 | 初代 S5 能否读自定义 `.vlt` | 高度可能（等级 D）——手册页只能给到页码级（S5 手册 PDF 是松下私有 VCIS 加密，三次密钥派生均失败） \| ✅ 实机确证：`[LUT Select]` 列出 `VL709` | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:417` |
| 783 | 新口径：M8M/M10V 已证实；PVC/MC801 待证实（正反均无直接证据，无法判定）。 |  | `14_总包审计与新方向_20261014/10_仓库补丁/口径修正_SD引导与SoC代_20261015.md:11` |
| 784 | SD.DAT 路线的第一道门（MC801 BootROM 有无 SD 入口）公开证据无法判定； |  | `14_总包审计与新方向_20261014/10_仓库补丁/口径修正_SD引导与SoC代_20261015.md:30` |
| 785 | 可达层 | 跨代不可移植；固件加密 + 签名；无 RCE ⇒ 不是"开关没找到"，是没有那级硬件管线 | `14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:67` |
| 786 | 4. 蓝牙（BLE） | 已排除，不是钥匙 | `14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:129` |
| 787 | 6.2 关键实验 | DLNA 403 与推流无关（假设已排除） | `14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:191` |
| 788 | ⇒ "相机资源被长推流占住导致 DLNA 被拒"这个假设不成立，可以划掉。 |  | `14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:200` |
| 789 | 四条旗舰结论的证据链在审计中不成立 |  | `14_总包审计与新方向_20261014/README.md:8` |
| 790 | [`03_新方向与实验设计.md`](14_总包审计与新方向_20261014/03_新方向与实验设计.md) | 26 个方向分四梯队，每个给出「为什么可行 / 需要什么 / 风险 / 成功判据 / 失败也得到什么」；含 E1–E4 可定因的对照实验设计 \| 想动手推进时用它 | `14_总包审计与新方向_20261014/README.md:27` |
| 791 | 所有"样本量"批评均基于项目自己记录在案的次数；若实际执行次数多于记录，该批评不成立。 | 若实际执行次数多于记录，该批评不成立。 | `14_总包审计与新方向_20261014/README.md:51` |
| 792 | 6 | 方向 15（U-Boot 离线核验）关闭：7 个 type=2 分区（2,490,368 B）搜 17 个关键词 0 命中；且发现这些"明文分区"其实是 OTA 容器的空占位（4 个全 `0x00`、2 个全 `0xFF`）⇒ 「UART 死路」在 S5 上不可判定，必须写成"S5 未验证" \| 确定性关闭 | `14_总包审计与新方向_20261014/README.md:79` |
| 793 | 7 | 方向 6（OSS 内核树）实质关闭 —— 重大更正：项目英文稿给出的下载 URL 是 `ospo.panasonic.com/oss/source/dsc/DC-FZ1K2/…`，而 DC-FZ1K2 是另一款独立机型（有它自己的 OSPO 页面）。同文却写 "OSPO publishes … for this model"（DC-S5）⇒ 同文自相矛盾。那棵树不是 DC-S5 的，首轮 `f_fs.c` 阴性结论对 S5 实机不具备排除力 \| 更正（已回填） | `14_总包审计与新方向_20261014/README.md:80` |
| 794 | E-1 | 我在 `03_新方向与实验设计.md` 方向 5 写的「CBC 且明文全零 ⇒ 所有密文块必须相同」是错的。块全同是 ECB + 常量明文的指纹；CBC + 全零是迭代链，块基本全不同（自造样本实测 CBC→256/256 全不同、ECB→1）。故 `ipu_data` 的 `16384/16384` 只能排除 ECB，CBC/CTR 不可区分 \| 已修正该文件 | `14_总包审计与新方向_20261014/README.md:109` |
| 795 | E-4 | 项目把 `0x220` 的 64B 当「ECDSA P-256 签名」使用，其源头已自我撤回：`07_参考仓库/s1m2-research/docs/CORRECTIONS.md` 明文把「外层 ECDSA 字段与签名机制已经确认」更正为「字段名称是候选；没有签名验证和完整机制证据」。而项目据此推出「版本字段在签名覆盖内 ⇒ 改版本号必然破坏签名」 \| 整条链降级为候选假设；「改版本号绕过版本门」的证伪依据也不再成立（既不能支持"能绕过"，也不能支持"必然被拒"）。已回填 `00_审计总报告.md` §3 补充与… | `14_总包审计与新方向_20261014/README.md:112` |
| 796 | 可达层 | 跨代不可移植（MC801 32-bit A7 ↔ SC2006A 4×A53 64-bit）；固件加密 + 签名；无 RCE。⇒ 不是"开关还没找到"，而是没有那级硬件管线 | `15_LUT烧录工具_20261014/README.md:242` |
| 797 | 蓝牙（BLE）不可行 | 项目实测 BLE 只暴露凭据面（SSID/密码），没有文件传输面；有效吞吐 ~10–100 KB/s 量级，一张 10 MB JPEG 要数分钟。视频更无可能。 | `15_LUT烧录工具_20261014/README.md:259` |
| 798 | 16_S5_核心总包_20261015 · 收录与排除说明 |  | `16_S5_核心总包_20261015/00_本包说明_收录与排除.md:1` |
| 799 | 排除所有厂商固件、反编译 APK、第三方参考仓库、实拍录像等大体积二进制， |  | `16_S5_核心总包_20261015/00_本包说明_收录与排除.md:5` |
| 800 | 排除项均在下方清单中留有体积 + SHA-256 + 源工作树路径，可随时恢复。 |  | `16_S5_核心总包_20261015/00_本包说明_收录与排除.md:6` |
| 801 | 本包排除清单（体积 + SHA-256 + 恢复路径） |  | `16_S5_核心总包_20261015/00_本包说明_收录与排除.md:47` |
| 802 | 排除项 | 体积 \| SHA-256（前 16 位） \| 源工作树路径 | `16_S5_核心总包_20261015/00_本包说明_收录与排除.md:49` |
| 803 | 全部排除项保留在源工作树 `/Users/<user>/Documents/ChatGPT/S5_逆向_项目总包_20261012/`， |  | `16_S5_核心总包_20261015/00_本包说明_收录与排除.md:66` |
| 804 | 含 `recording/`（MP4 已另行排除，见包根 `00_本包说明`）、`s1h_activation/`、`static_review/`、 |  | `16_S5_核心总包_20261015/01_研究报告/05_Panasonic_hidden_format_参考/evidence_去重指针.md:4` |
| 805 | 同类被排除内容（源工作树路径） |  | `16_S5_核心总包_20261015/02_固件指针/固件SHA256与下载来源.md:36` |
| 806 | 🔐 路线一 | 扒固件 → 死路 | `16_S5_核心总包_20261015/09_对外分享/小红书帖_S5逆向进度_20261014.md:30` |
| 807 | 之前一直以为"持久化失败"，其实是被悄悄降了。 |  | `16_S5_核心总包_20261015/09_对外分享/小红书帖_S5逆向进度_20261014.md:53` |
| 808 | ❌ 诚实的部分 | 拿不到的 | `16_S5_核心总包_20261015/09_对外分享/小红书帖_S5逆向进度_20261014.md:56` |
| 809 | · 试隐藏档失败后，相机可能停在一个"会让菜单变灰"的档位 |  | `16_S5_核心总包_20261015/09_对外分享/小红书帖_S5逆向进度_20261014.md:65` |
| 810 | 第 2 篇 | 扒固件为什么是死路（AES 那堵墙） | `16_S5_核心总包_20261015/09_对外分享/小红书帖_S5逆向进度_20261014.md:123` |
| 811 | 不属于本项目，已排除。 |  | `16_S5_核心总包_20261015/README.md:8` |
| 812 | 收录范围、排除原因与补齐方式见 [`REPO_CONTENTS.md`](REPO_CONTENTS.md)。 |  | `16_S5_核心总包_20261015/README.md:12` |
| 813 | 直写 flash 的 65533 字节设置 blob 可跨断电保留。固件 AES 密钥提取与网络 RCE 均为阴性。 | 固件 AES 密钥提取与网络 RCE 均为阴性。 | `16_S5_核心总包_20261015/README.md:19` |
| 814 | 离线 130k+ 探测、40/41 加密分区、真实 256KB keystream 均无法恢复密钥。密钥提取终局否定。 |  | `16_S5_核心总包_20261015/README.md:40` |
| 815 | → 结论：~70 个候选 mode 全部回通用 `err_param`，无调试后门；网络 RCE 各路线全阴性 | 网络 RCE 各路线全阴性 | `16_S5_核心总包_20261015/README.md:42` |
| 816 | 固件升级写路径（刷写=重写 rootfs）能流送全部 1474 个完整块，但最终部分块 flash 定址失败，未打通。 |  | `16_S5_核心总包_20261015/README.md:44` |
| 817 | `02_固件二进制/` | 去重后的固件：`DC-S5/`(V29)、`DC-S5_版本历史/`(V11/V20/V23/V24)、`DC-S1/`(V24)、`DC-S1H/`(V28) \| ✗ 版权·体积 | `16_S5_核心总包_20261015/README.md:68` |
| 818 | `03_解包_APK/` | 手机 App 解包（jadx 反编译 + apk + res + lib + dex） \| ✗ 版权·体积 | `16_S5_核心总包_20261015/README.md:69` |
| 819 | `07_参考仓库/` | `s1m2-research/`（S1M2 研究仓库，第三方） \| ✗ 非本项目 | `16_S5_核心总包_20261015/README.md:73` |
| 820 | 收录范围、去重与排除原因详见 [`REPO_CONTENTS.md`](REPO_CONTENTS.md)。 |  | `16_S5_核心总包_20261015/README.md:76` |
| 821 | 已证伪 / 不可行（✗ 不要再走） |  | `16_S5_核心总包_20261015/README.md:99` |
| 822 | 网络层 RCE | GoAhead 溢出、`LD_PRELOAD`、各 mode/getinfo 的 file-op/exec/dynamic-load，全部失败 | `16_S5_核心总包_20261015/README.md:102` |
| 823 | 原判据「相机报写入错误 | 内存写已执行」不成立（NULL 提前返回表现完全一样）。 | `16_S5_核心总包_20261015/README.md:105` |
| 824 | 服务模式组合键盲试（零风险）+ S5 U-Boot console 离线核验（判定 UART 生死，S1R2 实测 console=null 为死路） |  | `16_S5_核心总包_20261015/README.md:115` |
| 825 | SD.DAT 降级为 JTAG 之后的备胎（S1R2 教训 | 无只读模式、NAND 未验证、写错 pardata = 不可逆砖） | `16_S5_核心总包_20261015/README.md:117` |
| 826 | `senddata` 可能长期不响应（在等 `endsenddata`） | 不是失败，用新短超时连接补 `endsenddata` 收尾。 | `16_S5_核心总包_20261015/README.md:175` |
| 827 | 无关项目 `dsh-our-free-model`（LLM 免费模型插件） | 整体排除 | `16_S5_核心总包_20261015/README.md:186` |
| 828 | interface work. Evidence in the reports is tagged ✓ closed on hardware · ◐ strong but open · ✗ disproved. |  | `16_S5_核心总包_20261015/S5_RE_Project_Summary_EN.md:19` |
| 829 | 不装也能用监看/对焦/拍照，只是 LUT 面板禁用）。失败会自动换国内镜像。 | 失败会自动换国内镜像。 | `16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/README.md:17` |
| 830 | 可行部分做到可复现，不可行部分给出有证据的否决。这是"固件明文"目标的 | 可行部分做到可复现，不可行部分给出有证据的否决。 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:11` |
| 831 | 路径）。松下没有等价物；S5 固件 96% 加密 + 容器带内容绑定块，魔灯模式不成立。 | S5 固件 96% 加密 + 容器带内容绑定块，魔灯模式不成立。 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:30` |
| 832 | 独立研究线程完成基线查证 | 判定"无法判定"，报告归档于本目录； | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:40` |
| 833 | `ecdsa_recover.py` | `14_总包审计与新方向_20261014/07_签名与密钥恢复/ecdsa_recover.py` \| 90,144 组 ECDSA 恢复穷举（已跑完，零收敛） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:62` |
| 834 | `rsa_modulus.py` | 同上目录 \| RSA 模数恢复（已跑完，全排除） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:63` |
| 835 | C4 | 90,144 组 ECDSA 公钥恢复穷举零收敛；RSA 模数恢复（e∈{3,5,7,17,257,65537}）全部排除 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:92` |
| 836 | C12 | stubby 仓库的 GPL 源码只覆盖 Stubby（A7 Linux 引导器）；SD loader（SD.DAT，CM0 Thumb）是闭源预编译，源码树 grep 零命中。构建已复现（arm-none-eabi-gcc 16.2.0 + 3 处可移植性补丁） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:100` |
| 837 | C15 | G100 loader1 = ARM 异常向量表（MPIDR/WFI 次核自旋、复制 0x1A8B 代码到 SRAM 0x60009D00 二段引导）⇒ V9AHD 首段跑 Cortex-A7；全容器 105MB 字节级扫描：SD.DAT/boot.par/sdram.par/HBOOT/MISCTOP/MDR/bootmode/CM0/0x3FFE0400 全部零命中；dtb 无 CM0/misctop 节点 ⇒ 无 SD 引导的固件侧证据（BootROM 本身不在镜像内，硬件侧仍无法判定） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:103` |
| 838 | C18 | 平台内置 ECDSA-P256 验签（P-256 常数 p/n/Gx/Gy 小端序 @容器 0x6F27FC 起，逐字节比对 FIPS；代码区 rt 0x04F6E-0x04F7E 有 4 个 xref；旁有 `"PICTURE_QUALITY"+"ecdsa-p256"+"panasonic"+"jp"` 签名数据块）⇒ 用于画质参数数据验签；program 全段无有效公钥点（曲线方程验证零命中）⇒ 公钥在 OTP/掩模 ROM 或哈希形式——解释了 C4 穷举零收敛 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:106` |
| 839 | R1 | "`0x220` = ECDSA P-256 签名" \| 上游自我撤回 + C4 穷举零收敛。正确表述见 C3 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:117` |
| 840 | R4 | "SD.DAT 恢复模式 = Milbeaut 全系通用" \| 仅 M8M/M10V 已证实；PVC/MC801 待证实（无法判定） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:120` |
| 841 | P1 | MC801 BootROM 是否带 SD 引导入口 \| 软件侧全明文对照负证据（C15）；BootROM 本身不可见，硬件侧仍无法判定。唯一直接判据 = 拆机 UART bootlog | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:128` |
| 842 | `PVC_SD入口查证_基线报告_20261015.md` | 研究线程基线查证（9 条发现 + 缺口清单 + 可证伪落点） | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md:149` |
| 843 | 最终判定 | 无法判定（公开证据不足） | `17_SD引导路线_20261015/PVC_SD入口查证_基线报告_20261015.md:7` |
| 844 | PVC02V/V9AHD/MC801（DC-S5/S1/S1R/S1H 代）BootROM 带 SD 入口 | ❓ 无法判定 \| 正反都无直接证据 | `17_SD引导路线_20261015/PVC_SD入口查证_基线报告_20261015.md:19` |
| 845 | S5 固件弱阴性 | S5___V29.bin 全部 printable strings（15.2 万行）扫 SD.DAT/SDRAM.PAR/boot.par/ | `17_SD引导路线_20261015/PVC_SD入口查证_基线报告_20261015.md:45` |
| 846 | 低成本可证伪落点（需要硬件，供后续决策） |  | `17_SD引导路线_20261015/PVC_SD入口查证_基线报告_20261015.md:59` |
| 847 | 且本项目 90,144 组假设的 ECDSA 公钥恢复穷举零收敛。正确表述是 | 且本项目 90,144 组假设的 ECDSA 公钥恢复穷举零收敛。 | `17_SD引导路线_20261015/离线验证大任务书_给同事.md:27` |
| 848 | 90,144 组 ECDSA 恢复穷举、RSA 模数恢复全排除 | 见 | `17_SD引导路线_20261015/离线验证大任务书_给同事.md:29` |
| 849 | 判定"无法判定"（公开证据不足，只证明到 M8M/M10V 两代）。本任务的职责是 |  | `17_SD引导路线_20261015/离线验证大任务书_给同事.md:64` |
| 850 | 目的：把基线的"无法判定"收敛为更强的判定，或找出基线漏掉的正面/反面证据。 |  | `17_SD引导路线_20261015/离线验证大任务书_给同事.md:68` |
| 851 | ② 新证据（若有）；③ 结尾三选一 | 支持 / 反对 / 无法判定； | `17_SD引导路线_20261015/离线验证大任务书_给同事.md:87` |
| 852 | zboot 分区加密 | 无法直接比对二进制；改为比对结构（尺寸、相邻分区关系、 | `17_SD引导路线_20261015/离线验证大任务书_给同事.md:124` |
| 853 | 1 | G100 全容器 无任何 SD 引导痕迹：SD.DAT/boot.par/sdram.par/pardata/HBOOT/SDRAM/MISCTOP/MDR/bootmode/boot source/bootrom/CM0/0x3FFE0400 全部零命中 \| 实测确认（105 MB 字节级扫描） \| P1、P3 | `18_G100明文与同类项目_20261015/G100反编译_深挖报告.md:13` |
| 854 | 零命中（包内） | SD.DAT、boot.par、sdram.par、pardata、HBOOT、SDRAM、MISCTOP、MDR、bootmode、CM0、Cortex、supervisor、panasonic、crc32、RSA、cert、public。`3FFE` 仅 2 处且是地址巧合（`0x4C3FFE0`、`0x6A73FE5`，非 CM0 向量）。 | `18_G100明文与同类项目_20261015/G100反编译_深挖报告.md:35` |
| 855 | B5 | 无 BootROM 打印字符串（"boot from"/"boot source" 零命中） \| §1.2 \| P1 的"拆机 UART bootlog"判据在 G100 镜像里找不到对应实现——G100 的 BootROM 即使存在 SD 入口也不会打印这些串（BootROM 本身不在镜像内，注意此边界） | `18_G100明文与同类项目_20261015/G100反编译_深挖报告.md:158` |
| 856 | B6 | 0x3FFE0400（M10V 式 CM0 向量）零命中；0x3FFE0000 命中是浮点数据 \| §1.2 \| P3：无 CM0 固件/向量痕迹 | `18_G100明文与同类项目_20261015/G100反编译_深挖报告.md:159` |
| 857 | RSA e=65537（0x10001 dword） | 3645 处（program 内） \| 纯噪声（数据值常见），无法据此判定 RSA 存在 | `18_G100明文与同类项目_20261015/G100反编译_深挖报告.md:240` |
| 858 | P1（MC801 BootROM 有无 SD 入口） | G100 同代对照为全面阴性：无 SD 引导字符串/代码、Linux 侧从 NAND 启动、SD 控制器仅 WiFi SDIO 使能。注意边界：BootROM 本身不在镜像内，"镜像里没有"不能否定"BootROM 里有"——但 G100 提供了"同代平台没有 SD 引导的运行时痕迹"这一负证据，拆机 bootlog 判据的价值不变 | `18_G100明文与同类项目_20261015/G100反编译_深挖报告.md:310` |
| 859 | P3（MC801 有无片内 CM0/MDR/MISCTOP） | G100 全镜像无 CM0 向量（0x3FFE0400 零命中）、无 MDR/MISCTOP 字符串、dtb 只有 4×A7 GIC → 同代平台无 CM0 痕迹（弱旁证；CM0 固件若存在也不在 UPD 容器内） | `18_G100明文与同类项目_20261015/G100反编译_深挖报告.md:311` |
| 860 | python3 g100_strings.py # 关键词零命中 + panasonic 48 处定位 |  | `18_G100明文与同类项目_20261015/G100反编译_深挖报告.md:334` |
| 861 | 探测方法（先于协议实现） | `tools/uart_boot_probe/uart_boot_probe.ino` 复位后打 233µs 周期方波"垃圾"，相机无法开机并闪 13 次灯 = 错误码 0x100D（parity error）——用错误灯号当 oracle 证明"已经触达串口引导代码"。作者原话："If your camera 'dies', don't panic, just pull the battery"。 | `18_G100明文与同类项目_20261015/ILCE7M4RE_借鉴分析.md:92` |
| 862 | 9 | "加密但无验签"的存储设计先例 \| 中（作为先例与假说） \| 索尼 eMMC 分区 AES-XTS 无签名校验。我方 0x220 块机制未定（C3）、ECDSA/RSA 已排除（C4）、CRC32 弱校验已确证（C1）——不能据此断言松下同样无验签，但"仅加密即自认完整"是厂商普遍错误，可将其设为假说并设计"拿到密钥后改密文能否过全部校验"的离线验证（属后续阶段）。 | `18_G100明文与同类项目_20261015/ILCE7M4RE_借鉴分析.md:141` |
| 863 | `key(64B) = BootROM[0xb800 | 0xbc00][index_table[0..63]]`，其中索引表在 BootROM/引导器明文里。密钥熵完全来自硅片掩模 ROM，与容器无关——这与我们"容器内无密钥 + 90,144 组 ECDSA 穷举零收敛 + RSA 全排除"的观测完全一致。 | `18_G100明文与同类项目_20261015/ILCE7M4RE_借鉴分析.md:153` |
| 864 | 索尼先例给 P5 增加一个"保留且未熔断"的现代样本（A7 IV 是 2021 年机型，且串口引导至今可用）。P1"无法判定"的现状不应被默认解读为不存在 | 证据天平进一步倾向"值得实测"。 | `18_G100明文与同类项目_20261015/ILCE7M4RE_借鉴分析.md:162` |
| 865 | 6 | 密钥无法从容器内推到：容器内所有材料（blob A/B、机型串、版本、K32、F16、元数据区任意窗口）配合 11 种计数器约定 × AES-128/192/256 全部失败 \| CONFIRMED（否定式，见 §4） | `18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:19` |
| 866 | 一句话：S5M2 的节加密是一个实现正确的、每节随机 IV 的密钥流加密（与 AES-CTR 类模型完全一致，平台内也确实带 AES 实现）；离线无法解密，因为主密钥不在容器内、也不在可见代码中；唯一能做的是用 `K32` 预言机把"别的机型里碰巧明文存放的同一节"搬过来（已拿到 `music`）。 |  | `18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:27` |
| 867 | 明文有 15680 个重复块，而密文一个重复都没有 | 不存在"与位置无关的分组置换"（ECB / 固定 IV 的分组加密被排除）。这是本报告中最硬的一条结构性结论。 | `18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:92` |
| 868 | 32 位 LCG 递推（1024 字） | 不成立 | `18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:100` |
| 869 | xorshift32 递推 | 不成立 | `18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:101` |
| 870 | 同镜像内不同节的密钥流互不相关（`s4_relate.txt`） | S5 有 5 段已知密钥流、GX9 有 5 段、G7 有 3 段、S1m2/S1Rm2 各 2 段，两两 XOR 后熵 7.99、字节直方图 256 种取值——完全是随机的样子，既不是"常数掩码"（说明 `KS = E_K(ctr) XOR nonce` 这种偷懒写法不成立），也不存在"某节密钥流是另一节的窗口/移位/异或平移"（加法计数器与异或计数器两种猜测都否，见 `s8_misc.txt` (b)）： | `18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:108` |
| 871 | 2.5 残留的可能性（无法排除项） |  | `18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:123` |
| 872 | 分组算法是不是 AES | 无法从密文证明。密钥流与真随机不可区分 ⇒ 任何"看起来像 AES"的统计结论都是不可靠的；只有拿到实现或密钥才能确证。平台内含 AES（§3）只能说明"技术上可用"，不能证明容器用了它 | `18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:127` |
| 873 | 是否是 XTS 之类"无 nonce"模式 | 不成立：XTS 不需要每节随机 nonce 字段，本容器有且随机 | `18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:128` |
| 874 | → 二者都使"只有 .bin 文件"的离线解密不可行 |  | `18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:275` |
| 875 | 即：版本号伪造在容器层面可行且完整（与 G100 项目的 `make_version_uniform.py` 同思路），但 `program` 内部的版本副本 / EEPROM 版本记录位于密文节内，无法同步修改——这会是"外壳说 3.7.5、内部说 3.7.4"的不一致镜像。若机上只比头部（`UPD容器格式说明.md` §11.3 第 3 项），则能通过；否则会露馅。 |  | `18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:335` |
| 876 | 6.1 已被本次实验排除的路线（不要再花时间） |  | `18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:341` |
| 877 | blob A/B 是"被融合密钥包起来的每机型密钥" | 一种能解释"每机型唯一、与内容无关、无法派生密钥"的假设；无直接证据。 | `18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:439` |
| 878 | 解密在软件还是硬件 | 两种都自洽：软件解密需要密文代码里的密钥，硬件解密需要 ROM/融合位；现有数据无法区分。 | `18_G100明文与同类项目_20261015/S5M2_AES_分析报告.md:440` |
| 879 | 判定档位 | ✅ S5 成立（本机实测）｜🟡 部分成立/需修正｜🔵 报告已覆盖 S5、本机复核｜❌ 不适用 | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:23` |
| 880 | 2 | 保长、每节独立 IV 的流式加密、与真随机不可区分 \| ✅ 成立 \| S5 V29 全部 48 节 size%16==0；密文熵 7.9993–8.0000；music 密钥流 χ²(255df)=235.8、自相关 0.390–0.394%（基线 0.3906%）（§2-C/F）。"流式/CTR"这一点：我们结论库此前在 S5 上无法区分 CBC 与 CTR（06_重跑 §3.4）；现在有了 3.4MB 真数据密钥流 + G100 代码里被真实使用的 CTR 骨架（fn_4EF054C，本评估 §2-H），C… | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:29` |
| 881 | 6 | 密钥无法从容器内推（11 约定 × AES-128/192/256 全失败） \| ✅ 成立（本机独立电池，阳性对照通过） \| 用 S5 V29 自己的容器材料（0x220 64B 块、MC801 串、48×K32/IV、0x200–0x2EC 全窗口）共 536 个候选密钥 × 11 种文档化计数器约定 + CBC 假说，对 4 段已确证密钥流共 32,160 次测试 0 命中；阳性对照（已知密钥+iv128_be）被检出 ⇒ 电池有检验力（§2-I）。与报告 §4 互补（候选集合不同、独立实现），并补上 06… | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:33` |
| 882 | 32位LCG递推(1024字) | 不成立（527 个商样本 → 527 个互异 a） | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:106` |
| 883 | 阳性对照（自造样本，已知密钥+iv128_be） | True ← 电池有检验力，不是假阴性机器 | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:117` |
| 884 | loader1 | e009d688fb15 \| 6240a8c8f8ec \| ❌ | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:201` |
| 885 | loader2 | 4a925f2e0193 \| 50110b501642 \| ❌ | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:202` |
| 886 | loader3 | 67d44d7c2bb2 \| 21522b7c1a04 \| ❌ | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:203` |
| 887 | zboot | 014dad699b15 \| 8752e78f6877 \| ❌ | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:204` |
| 888 | dtb | f1a4d16edaad \| 2219fa600628 \| ❌ | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:205` |
| 889 | program | fc496d62a91f \| 27b26e32a545 \| ❌ | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:206` |
| 890 | zimage/rootfs1/2/postboot1 | 各不同 \| 各不同 \| ❌ | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:207` |
| 891 | 拿不到：任何 boot/OS 代码明文。想靠 K32 走 S5M2→S5 的"搬代码"路不成立。 | 想靠 K32 走 S5M2→S5 的"搬代码"路不成立。 | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:214` |
| 892 | "S5 首解在片上"是强推断 | 前提是 S5 loader1 与 G100 loader1 同角色且 S5 loader1 不含紧凑 S 盒版 AES——后者无法从密文排除（K32 不同，S5 loader1 是另一构建）。 | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md:268` |
| 893 | 平台验签 = ECDSA-P256（P-256 常数小端序 @0x6F27FC 逐字节对 FIPS；`"PICTURE_QUALITY"+"ecdsa-p256"+"panasonic"+"jp"` 签名块；4 个代码引用） | 用于画质参数数据。公钥不在固件（program 全段曲线方程验证零命中）⇒ 解释了我们 C4 穷举零收敛的旧谜题。 | `18_G100明文与同类项目_20261015/三材料总评估_20261015.md:21` |
| 894 | G100 全容器零 SD 引导痕迹 | SD.DAT/boot.par/sdram.par/HBOOT/MISCTOP/MDR/CM0/0x3FFE0400 全零命中；loader1 = A7 ARM 向量表（MPIDR/WFI 次核自旋）⇒ V9AHD 代无 CM0 痕迹、无 SD 引导的软件侧证据。stubby 的 CM0 SD.DAT 不适用本代。 | `18_G100明文与同类项目_20261015/三材料总评估_20261015.md:26` |
| 895 | 零结果也是结果（排除"0x220=HMAC 固定密钥产物"）。 |  | `18_G100明文与同类项目_20261015/同事任务清单_20261015.md:19` |
| 896 | 公钥在 OTP/掩模 ROM（或哈希形式）。解释了 C4 穷举零收敛的旧谜题。 | 解释了 C4 穷举零收敛的旧谜题。 | `18_G100明文与同类项目_20261015/最新结论速览_20261015.md:13` |
| 897 | 全零命中；loader1 = A7 ARM 向量表（MPIDR/WFI 次核自旋）。stubby 的 CM0 SD.DAT 不适用本代。 | 全零命中； | `18_G100明文与同类项目_20261015/最新结论速览_20261015.md:23` |
| 898 | 1 | 容器内推密钥 \| 119 候选密钥 × 11 计数器约定 × 14 段已知密钥流 全失败（C6 结论） | `18_G100明文与同类项目_20261015/破解AES的路径清单_20261015.md:31` |
| 899 | 6 | 伪造签名 \| ECDSA 公钥不在固件（10MB program 零有效曲线点）；且无私钥无法签 | `18_G100明文与同类项目_20261015/破解AES的路径清单_20261015.md:36` |
| 900 | 我们缺的一环 | 计数器约定未知（11 种约定全失败）⇒ 输入块的具体形式不确定，会抬高 CPA 难度（但对模板攻击不致命）。 | `18_G100明文与同类项目_20261015/破解AES的路径清单_20261015.md:85` |
| 901 | 离线观测无法区分 (a) 和 (b)（两种情况都要求密钥才能判定）。 |  | `18_G100明文与同类项目_20261015/群问题解答_密钥流与AES_20261015.md:46` |
| 902 | 注：索尼先例证明 (a) 在业界确实存在，所以不能排除——但目前是"不可判定"，不是"已证实"。 |  | `18_G100明文与同类项目_20261015/群问题解答_密钥流与AES_20261015.md:48` |
| 903 | 119 个候选密钥 × 11 种计数器约定 × 14 段已知密钥流，全部失败。 |  | `18_G100明文与同类项目_20261015/群问题解答_密钥流与AES_20261015.md:89` |
| 904 | G100 的 loader 链（loader1/2/3/zboot，与 S5 同角色、同加载地址）连 AES 表都没有（S 盒/Rcon 全段零命中）。 |  | `18_G100明文与同类项目_20261015/群问题解答_密钥流与AES_20261015.md:113` |
| 905 | T1 PVC SD 入口 | ❓ 无法判定 \| 复核部分=实测确认 \| `T1_PVC_SD入口判定.md`（基线 3 来源独立复核 + GP2 旁证） | `18_SDDAT验证/00_总览.md:6` |
| 906 | ⚠️ 发现的细节（结论库细化，非失败） |  | `18_SDDAT验证/T0_环境校准.md:21` |
| 907 | 非反射 CRC（poly 0x04C11DB7, MSB-first）不吻合 | 排除。 | `18_SDDAT验证/T0_环境校准.md:25` |
| 908 | 判定：基线 9 条发现中 3 个关键来源已独立复核，全部与原文一致；判定维持"无法判定"。 |  | `18_SDDAT验证/T1_PVC_SD入口判定.md:3` |
| 909 | 证据等级 | 无法判定（公开证据不足）；复核部分=实测确认（原文核对）。 | `18_SDDAT验证/T1_PVC_SD入口判定.md:4` |
| 910 | 复核结论 | 基线报告引用无误，无夸大、无断章。判定"无法判定"维持。 | `18_SDDAT验证/T1_PVC_SD入口判定.md:17` |
| 911 | 连带影响 | 无法在容器内做任何二进制级结构比对（向量表、代码模式全部被加密掩盖）。 | `18_SDDAT验证/T3_启动链结构比对.md:21` |
| 912 | 判定："S5 与 GP1 同构"在容器级没有反例，但全部是弱证据；二进制级比对因加密不可行。 | 二进制级比对因加密不可行。 | `18_SDDAT验证/T3_启动链结构比对.md:33` |
| 913 | 源码树 grep | `HBOOT`/`PARDATA`/`DATA.BIN`/CM0 代码 零命中。 | `18_SDDAT验证/T4_构建校准.md:32` |
| 914 | "用 GPL 源码编译一个 S5 可用的 SD.DAT"不成立 | 源码不包含 SD loader。 | `18_SDDAT验证/T4_构建校准.md:42` |
| 915 | 两条路都以"MC801 是否带 CM0 + BootROM 是否有 SD 入口"为前提（T1 | 无法判定）。 | `18_SDDAT验证/T4_构建校准.md:46` |
| 916 | 不构成"死路"，但一切前置工作都必须先做硬件侧（拆机 UART），软件侧已无可做之事。 |  | `18_SDDAT验证/T5_综合裁决.md:4` |
| 917 | T1 PVC SD 入口 | ❓ 无法判定 \| 基线 3 大来源独立复核无误；GP2"verifies and calls bootstrap"旁证 | `18_SDDAT验证/T5_综合裁决.md:12` |
| 918 | [1] MC801 BootROM 有无 SD 入口 ............. 无法判定（公开证据为零） |  | `18_SDDAT验证/T5_综合裁决.md:20` |
| 919 | 公开资料路线 | 已走到头（T1 无法判定是公开信息的极限）。 | `18_SDDAT验证/T5_综合裁决.md:34` |
| 920 | 若不拆：本路线封存，结论库按"无法判定"归档。 |  | `18_SDDAT验证/T5_综合裁决.md:43` |
| 921 | 明确的"已排除"项 | 13 项（含 4 项"恰好填满"型精确边界，见 §5） | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:19` |
| 922 | 为何降到"不可利用（记账错误）" | 算术部分是实测，无歧义。但补齐了最后一块证据后，可利用性被排除： | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:161` |
| 923 | 四、逐点证据与"已排除"清单 |  | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:221` |
| 924 | 4.1 收包/重组 | 头总长上限 5120 字节（已排除溢出） | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:223` |
| 925 | 4.2 请求目标（URI）解析 + URL 百分号解码（已排除 | 恰好填满，与 cam.fcgi 73 字节同型） | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:241` |
| 926 | 92bec..92c00 | 失败分支 memset(dst, 0, 256) ; ★ 反向证明字段 = 256 B | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:255` |
| 927 | 目标字段 | `base0+0x19C`，由失败分支 `memset(.,0,256)` 反推 = 256 B | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:280` |
| 928 | 额外加固（实测） | `%00` 被改写成 `0x01`，随后被 `isgraph` 校验拒绝 ⇒ 无法用 NUL 截断绕过路径检查；控制字符同样被拒。 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:283` |
| 929 | 证据等级 | 实测。判定：已排除（精确边界）。 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:284` |
| 930 | 4.3 `Content-Length` 的信任范围（已排除 | 不用于分配、不用于拷贝） | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:286` |
| 931 | 95ea8 | cmp r3, #0 ; beq 95eb0 → return 0 ; 没有数字位 → 失败 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:294` |
| 932 | `Content-Length` 不是内存破坏向量。已排除。 | 已排除。 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:326` |
| 933 | 6 | `Host` \| `0x0d6b58` \| `base0+0x29c` \| `len > 31 → return -2` \| 32（下一活跃字段 0x2c8 之前，且 realTimeInfo/PlaySpeed 在 0x2aec/0x2aed… 见注） \| 已排除：恰好填满（31+1 = 32） | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:337` |
| 934 | 10 | `Content-Length` \| `0x0d6fe8` \| `base+0x10`（8 B） \| 魔数校验 + `0x95e4c` 范围检查 \| 8 \| 已排除（§4.3） | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:341` |
| 935 | 12 | `Content-Type` \| `0x0d7204` \| `base+0x18` \| `len > 127 → return -2` \| 128（0x98−0x18） \| 已排除：恰好填满（127+1 = 128） | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:343` |
| 936 | 17 | `contentFeatures.dlna.org` \| `0x0d717c` \| `base+0x98` \| `len > 199 → return -2` \| 200（0x160−0x98） \| 已排除：恰好填满（199+1 = 200） | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:348` |
| 937 | `0x0f3f8c` d_soap | `memcpy @0x0f44c0 / 0x0f474c / 0x0f499c / 0x0f4a24` \| 全部 常量 12 字节，源 = 内存块描述符 `[fp-40]`，目标 = 12 字节栈槽 \| 已排除（4 处 `mov r2,#12` 实测） | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:369` |
| 938 | `0x0f3a6c` d_http | `memcpy @0x0f3ef8` \| 同上，常量 12 \| 已排除 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:370` |
| 939 | `0x0efb20` d_gena | `memcpy @0xf010c`；`strncpy ×13`；`strcpy @0xf1d78/0xf1dac/0xf1dd0` \| 见 §4.5.1 / §4.5.2 \| 已排除 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:373` |
| 940 | 4.5.1 `CALLBACK | ` 头 URL 解析（`0x0efb20` 内，已排除） | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:375` |
| 941 | 这是一处"看起来无界、实际有界"的经典陷阱 | `strncpy(dst, src, end−start)` 的 `n` 形式极像无界拷贝（我一开始也把它列为高危），但唯一到达它的分支被 `cmp r3,#15 / ble` 门住 ⇒ n ≤ 15。目标 `fp-0x3bc` 所在缓冲区间为 `[fp-0x3bc, fp-0x1c8)`（下界由同函数 260 字节读缓冲 `fp-456` 界定）= 500 字节。已排除。 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:394` |
| 942 | 4.5.2 订阅者表插入（`0x0db8e4`，已排除） |  | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:396` |
| 943 | 数值论证 | 表项步长 0x280 = 640 B，字符串字段起于 +0x17C ⇒ 可用空间 = 0x280 − 0x17C = 0x104 = 260 字节（含 NUL ⇒ 最多 259 字符）。唯一的调用者 `0xf1d38`（同属 `nce_upnp_d_gena.c`）传入的是函数内部局部缓冲（`fp-456` 等），其内容源自 `CALLBACK:` 头但已在 `0x0f0a20 / 0x0f0cd4` 处被截到 ≤ 260 读入 + ≤16 写入。本轮未找到能把 ≥259 字符送进该 strcpy 的路径；且该写入… | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:411` |
| 944 | 4.6 其它逐点核对（已排除） |  | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:415` |
| 945 | 位置 | 形式 \| 为什么排除 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:417` |
| 946 | `0xdb780`（`nce_upnp_d_data_setstr(dst, src, maxlen)`） | `dst[maxlen-1]=0; strncpy(dst,src,maxlen); if (dst[maxlen-1]) → 报错返回 7` \| 这是全二进制里最稳健的拷贝原语：强制 NUL + 截断检测 + 拒绝提交。SSDP 广播缓存（`0x0da64c`）的 IP(16)/Server(64)/Location(261) 三个字段全走它，且限长值与字段大小精确相等（`0x50+261 = 0x155`，下一字段 `0x15c`）。已排除。 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:422` |
| 947 | 五、"已排除"清单汇总（这同样是成果） |  | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:428` |
| 948 | E14 | `0x0d69b8` Accept 头（候选 1 的可利用性排除） \| 结构体溢出 \| 越界 ≤3 字节，但 `base0+0x2c8` 之后 560 字节（至 `base1`）全二进制无任何引用（`#712/#713` 仅 3 处、全在本 handler 内；`#10240/#11520`+第二 add 模式在 `base+0x2c0..0x4f8` 无命中）⇒ 无破坏目标 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:445` |
| 949 | `Accept`（候选 1）的越界 3 字节已通过"560 字节区间零引用"排除可利用性（见 §3.1 与 E14）。不建议在活体上验证此事（会造成相机 dlna 进程异常）；如需第三方复核，只需重跑 §8 里 `grep -nE "add\\s+r[0-9]+, r[0-9]+, #(712\|713)\\b" dlna_text.asm` 与偏移穷举脚本。 | `Accept`（候选 1）的越界 3 字节已通过"560 字节区间零引用"排除可利用性（见 §3.1 与 E14）。 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:512` |
| 950 | 新增「已排除」 | 9 项（E16–E24），其中 4 项为"恰好填满"型 | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:18` |
| 951 | A5 `0xba574` | 本轮最险的一处，已排除（恰好填满） | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:121` |
| 952 | ⇒ 已排除（精确边界）。 这也是本二进制第 5 处"恰好填满"。 | ⇒ 已排除（精确边界）。 | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:175` |
| 953 | 32 位 `%d` 最长 `-2147483648` = 11 字符 + NUL = 12，与 `tmp` 的 12 字节精确吻合。已排除。 | 已排除。 | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:189` |
| 954 | 源为静态名字表 `0x11dec0`（`{1,"start"},{2,"done"},{3,"err_SDfull"},…`，最长 `"err_Tempa_4kPreBrst_to_4kBrst"` = 30 字符），目标为 `memset(.,0,129)` 的 129 字节槽。已排除。 | 已排除。 | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:192` |
| 955 | 证据等级 | 实测。⇒ B1/B2/B3 全部落在「已排除」。 | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:249` |
| 956 | ⇒ 已排除（精确边界）。 附带：该函数还主动拒绝 `<` `>` `&` 与非 Latin-1，等于在 XML 解析前就把标记注入面掐掉了。 | ⇒ 已排除（精确边界）。 | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:295` |
| 957 | 四、新增「已排除」清单（接上一份报告的 E1–E15） |  | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:392` |
| 958 | 加上上一份报告的 E1–E15，累计已排除 24 项。 |  | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:406` |
| 959 | E23（`0xba574`）的排除依赖于"静态表 `0x11e020` 是 `arg0` 的唯一取值来源" | 我通过"匹配循环 + `id==0` 终止哨兵 + 表完整枚举（11 项）"三条证据确认，但仍属强推断而非实测：若存在运行时改写该表的代码路径（本轮未搜索），结论需重估。这是本轮唯一一个"排除了但仍值得别人复核一遍"的点。 | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:462` |
| 960 | 5 | `nce_upnp_util_strlcat` 有界 API 用无界 `strcpy` 实现 @ `0xe9774`/`0xe9a9c` \| — \| ❌ 本路径不可达 \| — \| 弱推断（加固项） | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:20` |
| 961 | 五、已排除清单（审过并确认安全） |  | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:347` |
| 962 | adb14 | bl ae090 @ 取另一资源（失败返回 -1 → 错误路径） | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:197` |
| 963 | 五、已检查 / 已排除清单（逐条） |  | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:246` |
| 964 | 第一份报告候选 1「14 处 `strcpy` 可越界覆盖返回地址」= 强推断 | ⬇️ 降级：源槽容量 64/80/128 B 均 < 176 B 余量；且入站报文无法影响源槽 ⇒ 在当前构型下不可越界（实测级证据支撑） | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:271` |
| 965 | 第二份报告「CP 解析面」= 不可达 + O6/O7 排除 | 不变 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:272` |
| 966 | 新的净收获 | ① SSDP 入站侧写入维度封闭，是一条干净的攻击面（排除了内存破坏）；② 定位到 `0xadabc` 回调槽注册器与 `0x9db18 → 注册 0x9d3ec` 的机制，解释了多处"无调用点"现象；③ 明确 3 处 [未判定] 及其核对方法 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:273` |
| 967 | 明确写"已排除"的点（像 cam.fcgi 那个 73 字节恰好填满的例子） |  | `19_路径1_Linux侧攻击面_20261015/dlna_audit/BRIEFING.md:131` |
| 968 | ① `0x0f4bbc` | 已排除（恰好填满 + 四重范围检查）。它是 AVTransport 的 `RelTime`/`AbsTime` 时间规格解析器，网络可达（认证门后）；`strcpy@0xf4c44` 前有 `strlen ≤ 127` 闸门，目标 128 B 局部缓冲 ⇒ 精确吻合 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:14` |
| 969 | ② `0x0d6560`（Range） | 已排除（零拷贝）：只有 `strncmp` + `parse_int64` + 两个 8 字节 `strd` 写 + 起止顺序校验 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:15` |
| 970 | ② `0x0db8e4` | Branch B 已排除（恰好填满）：入口 `strlen < 260` 闸门 + 260 B 字段。 Branch A → 本轮唯一候选（置信度中）：`strcpy@0xdbd1c` 目标字段 80 B、`strcpy` 无长度检查 ⇒ 只要源串 > 80 字节即覆写节点 `next` 指针；源的长度上界本轮未确定 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:16` |
| 971 | 累计已排除 | 28 项（E1–E28） | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:18` |
| 972 | 一、① `0x0f4bbc`（984 B） | 已排除 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:23` |
| 973 | ⇒ E25 已排除（恰好填满 + 四重范围检查）。 附带更正：池常量 `0x1869F` 被我的分类器误标为 CODE（它落在 .text 地址区间），实际是数值上限 99999。 | ⇒ E25 已排除（恰好填满 + 四重范围检查）。 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:76` |
| 974 | `memcpy(node, src_mirror, 364)` 只覆盖到 `+0x16C` 之前，无法恢复被污染的状态字段与 `next` 指针。 |  | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:171` |
| 975 | 在厘清"源"之前，不要上活体验证（该路径直接操作链表，失败模式是 dlna 进程崩溃）。 |  | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:197` |
| 976 | 三、② 的 Branch B 与 `0x0d6560` | 已排除 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:201` |
| 977 | ⇒ 只有 `strncmp` + 自定义整数解析 + 两个 8 字节 `strd` 写（`base+0`、`base+8`）+ 起止顺序校验，没有任何 `strcpy/memcpy`。 已排除。 | 已排除。 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:221` |
| 978 | ⇒ E27 已排除（第 7 处"恰好填满"）。 |  | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:244` |
| 979 | 五、累计「已排除」清单（E1–E28） |  | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:328` |
| 980 | dlna | 本轮完成 HTTP/SOAP/XML/SSDP 解析层的逐点审计 \| 28 项已排除，1 项中置信度候选（C-1） | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:350` |
| 981 | 结论先行 | C-1 未能确认为漏洞，也未能干净排除 —— 判定为"未定，倾向排除"。 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:403` |
| 982 | 判定：C-1 未定（倾向排除）——不作为漏洞主张 |  | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:510` |
| 983 | 倾向排除的理由（是"模式论证"，不是证据） |  | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:512` |
| 984 | 不能干净排除的理由 | 我没有找到强制 ≤79 的那条 `strncpy`/长度检查指令。若存在一条未被发现的路径把 >79 字符写进 `fp-1328`，则同时溢出两处： | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:516` |
| 985 | 判定结果 | 【排除】 —— 且附带发现一处健壮性缺陷（未初始化栈读取） | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:549` |
| 986 | ④ 追加检验：搜全二进制 `0xFFFFFAD4`/`0xFFFFFAD0`（`fp-1328±len` 型 NUL 终止常量） | 零命中 ⇒ `fp-1328` 不是被当作缓冲区使用 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:601` |
| 987 | ⇒ 这是"崩溃/健壮性缺陷"类，不是"攻击者可控写原语"类。 攻击者无法决定那 4 字节的内容（它来自本函数帧内未被任何指令写过的位置，通常是上一次调用留下的残值）。 |  | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:611` |
| 988 | 决-4 为什么"排除"而不是"升级" |  | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:613` |
| 989 | 三条独立理由都指向同一结论 | 【排除】。 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:622` |
| 990 | 残余不确定性（诚实标注） | 手段 ② 依赖"`sub rX, fp, #N` 后 8 条内完成 `add/sub` 链"这一模式；无法排除存在一条寄存器间接存储（例如基址先被 `mov` 到另一寄存器、再经 `add` 偏移后 `str`）把 `fp-1328` 写掉。若如此，则 `fp-1328` 是一个普通的有界字段（按同族字段推断为 64 或 80 字节），结论仍是排除。两种可能都落在"排除"。 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:624` |
| 991 | ⇒ 价值评估：C-1 的可达性条件是好的（免认证、门之前、只需一次免认证 SUBSCRIBE），但缺陷本身不成立。这条链上的真实缺陷是未初始化栈读取，属崩溃类，不构成可利用的写原语。 | ⇒ 价值评估：C-1 的可达性条件是好的（免认证、门之前、只需一次免认证 SUBSCRIBE），但缺陷本身不成立。 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:635` |
| 992 | C-1 | 从"中置信度候选"→【排除】，并从漏洞清单移除 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:656` |
| 993 | 「已排除」总数 | 28 项（E1–E28）+ C-1 = 29 项 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:658` |
| 994 | ⚠️ 因此 | 以下风险必须重新评估（我第一版的"已排除"是错的） | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:78` |
| 995 | [弱推断] 精确版本号（2.0.x 还是 2.1.0） | 二进制里没有 `expat_2.x.x` 之类的版本字符串，`XML_ErrorString` 指针表是运行时构造的（`.rodata` 内搜不到指向 0xff500 区间的指针数组），所以我无法静态给出确定版本号。 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:89` |
| 996 | 4. 有"发现即解析"（无需相机主动搜索）的路径吗？ | 静态分析无法确认：`0xda654`、`0xd4c34`、`0xd5830`、`0xef404` 均无静态调用点、也无函数指针字面量 ⇒ 由运行时回调注册表驱动，注册代码不在本文件中 \| [实测]（"无调用点"是实测；"运行时注册"是推断） | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:102` |
| 997 | 一句话（已修订） | 控制点路径的攻击面确实存在（我方伪装 MediaServer → 相机主动拉取我方 XML），而且我现在确认它不是送到一个自研的、写入受控的 schema 校验器，而是送到静态链接的 Expat 2.0/2.1 世代完整解析器。因此第一版「解析器写入受控」的结论只对 Expat 之上的封装层成立，对 XML 解析整体不成立。当前最关键的两个未知量是：① 该 Expat 是否含 CVE-2016-0718 补丁；② 谁在运行时把网络缓冲区喂给它（§2 的注册表问题）。 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:106` |
| 998 | ef42c | ble ef43c @ 状态码 <=199 → 失败路径 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:146` |
| 999 | 调用它的上下文函数 `[fp,#-24]` 即解析器状态；它按 `d5608` 的一串期望标签顺序推进 | [实测] 这是按固定 schema 顺序匹配的解析器，不是通用 DOM 构造器 —— 这点对安全性有利：未知标签只会导致匹配失败返回，不会进任意节点。 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:241` |
| 1000 | 1.3 远端字段的长度上限检查（我方 XML 无法越界写） |  | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:273` |
| 1001 | 汇总被排除的 8 类怀疑点 |  | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:386` |
| 1002 | 1 | 元素名 / 文本拷进固定栈缓冲 \| 已排除 \| 所有远端字段都经 `0xdb780`（`strncpy` + `dst[n-1]=0` + 校验），上限 64/80/128 B | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:390` |
| 1003 | 2 | 无限深度递归爆栈 \| 大概率排除 \| 深度用显式栈 + `ctx+0x6a` 计数器，有 `cmp/bne` 分支（`0xd5188`）；`ctx+0x2e0` 固定区 → 但无显式上限比较，见 §4 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:391` |
| 1004 | 3 | 未知标签导致任意节点写 \| 已排除 \| `0xd5608` 是顺序 schema 匹配，不匹配即返回错误，不构造通用树 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:392` |
| 1005 | 4 | 实体展开（Billion Laughs / XXE） \| ❌ 前一版结论错误，已作废 —— 见 §〇·零 \| 二进制内确实存在 Expat 的 `ENTITY`/`ENTITIES`/`NDATA`/`SYSTEM`/`PUBLIC`/`NOTATION`/`DOCTYPE` 关键字，以及 `recursive entity reference`、`error in processing external entity reference` 等错误串（0xff580–0xff7f8）。该行原判为「已排除」是本报… | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:393` |
| 1006 | 5 | 注释 / CDATA 处理越界 \| 已排除 \| `"!--"` 仅在 `0xd5d48` 做定长匹配，之后走 `0xd5608` 的有界推进 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:394` |
| 1007 | 6 | HTTP 应答头长度 \| 已排除 \| `0xef404` 状态码区 `cmp #199/#300`；`memcpy(...,12)` 为常量长度（`0xef49c`） | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:395` |
| 1008 | 7 | 服务/设备数量导致数组越界 \| 已排除 \| 4 / 8 / 32 三个显式上限（`0xda770`、`0xdaad8`、`0xdaddc`） | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:396` |
| 1009 | 8 | 名称空间前缀解析（`xmlns:`） \| 已排除 \| 仅定长字符串比较（`0xd5ac8`），无动态分配 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:397` |
| 1010 | 纯静态无法回答"我方广播 NOTIFY 后相机是否立刻来抓 XML"（问题 4） | 需要活体观察或动态跟踪； | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:419` |
| 1011 | O2 | XML 深度是否有显式上限 \| `ctx+0x6a` 是 u16 计数器，未搜到与 65535 或小常数的比较；若上游限制报文总长（链节点 4096 B），实际深度受输入长度约束 —— 但每层至少 1 字节，4096 B 最多约 4096 层，递归爆栈风险不能排除 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:472` |
| 1012 | 我没有把它写成"实测漏洞"，因为按现有证据它不成立；也没有把它写成"已排除"，因为闭合它需要 §2 的注册表信息。这是本次优先级 1 抢占时间后的诚实状态。 | 我没有把它写成"实测漏洞"，因为按现有证据它不成立； 也没有把它写成"已排除"，因为闭合它需要 §2 的注册表信息。 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:502` |
| 1013 | 若第 2 步确认存在拼接且目标 ≤176 B 余量 | 候选 1 升级为实测；否则降级为已排除。 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:508` |
| 1014 | 780b8 | mov r3, #0 @ realloc 失败 → 返回 0 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:593` |
| 1015 | 78194 | mov r3, #0 @ malloc 失败 → 返回 0 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:614` |
| 1016 | ⇒ [实测] 本次 memcpy 的长度上界由 3 条指令前刚分配的块大小所界定（分配点的 `len` 与 memcpy 的长度同源），且分配失败有显式检查。 |  | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:624` |
| 1017 | ⚠️ 不确定性（必须声明） | 我无法静态确定精确版本号——二进制内没有 `expat_x.y.z` 版本字符串，`XML_ErrorString` 的指针表是运行时构造的（在 `.rodata` 内搜不到指向 0xff500–0xff840 区间的指针数组，故无法用表格长度反推版本）。因此本判定是"脆弱签名不存在"的否定式证明，而非"版本 ≥2.2.0"的肯定式证明。若该构建是基于被选择性回移的源码树，理论上仍可能有未回移的其它 Expat CVE——但那需要逐 CVE 的签名匹配，不在本次范围 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:633` |
| 1018 | （`XML_SetBillionLaughsAttackProtection*` 是 2.4.0 引入，我未在二进制中找到对应的可辨识结构，故无法据此上推版本。） |  | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:645` |
| 1019 | 结论：在本二进制内不成立（惰性） —— 证据等级：强推断 |  | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:651` |
| 1020 | 2 | 应用调用 `XML_SetParamEntityParsing(parser, XML_PARAM_ENTITY_PARSING_ALWAYS)` \| ❓ 无法静态确认 \| `XML_ParserCreate`（`0x6e65c`）无任何调用点，也没有函数指针字面量 ⇒ 我无法观察到创建之后的 setter 序列 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:660` |
| 1021 | 3 | 应用调用 `XML_SetExternalEntityRefHandler` 并提供真正做 I/O 的回调 \| ❌ 本二进制内不存在这样的回调 \| 见下 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:661` |
| 1022 | XXE（任意文件读 / SSRF）在本二进制内不成立 | 强推断 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:679` |
| 1023 | Billion Laughs（DoS） | 不能排除，但同样受条件 2 制约。`'recursive entity reference'` 说明有递归检测，但 Expat 2.1.x 没有放大上限（2.4.0 才引入 `XML_SetBillionLaughsAttackProtection*`）。若宿主启用了参数实体解析，内部实体膨胀仍可造成 CPU/内存耗尽 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:681` |
| 1024 | ⚠️ 声明 | 条件 2（`XML_SetParamEntityParsing`）未确认。若宿主在运行时设置为 ALWAYS，则"内部实体膨胀 DoS"成立；"外部实体读文件"仍因缺 I/O 回调而不成立 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:682` |
| 1025 | ② 广播什么 NOTIFY 能让相机来抓我们的 LOCATION？ | 无法静态给出 \| 判定被"注册表"切断：`nce_upnp_c_data.c` 的注册 API `0xd7da0`（内含 `Not Specify cb_alive` / `cb_byebye` / `cb_msearch` / `cb_httpget` / `cb_soap` / `cb_notify` / `cb_sub` 的入参校验）无调用点 ⇒ 宿主在别处注册。"发现即解析"是否存在，静态无法回答 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:731` |
| 1026 | B. 相机 → 我们：相机作为控制点主动抓我们的描述 XML → Expat 解析 | ❓ 静态无法确认（接收/注册侧不在可达集内） \| 不可判定 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:741` |
| 1027 | C. XXE / CVE-2016-0718 经链路 B 利用 | ❌ 即便 B 成立也不成立（O6：无脆弱签名；O7：无 I/O 回调） \| 强推断 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:742` |
| 1028 | 次之（不可判定，需动态） | 控制点 XML 解析（链路 B）。即使可达，O6/O7 已把它的两个最高价值武器（RCE / XXE）排除，剩余价值主要是 DoS（Billion Laughs，取决于参数实体是否启用）。 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:749` |
| 1029 | XXE 在本二进制内不成立 | 强推断 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:772` |
| 1030 | 5 | 已排除：`system()` 全部 19 处参数为常量或内部数值；`PsmCmd_CreateMultipartHeader` 有显式溢出检查；`PsmCmd_Setsetting_DeviceName` 用 `strncpy` 截断。 \| 见 §5「已排除清单」。 | `19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:19` |
| 1031 | 而 `PsmCgi_GetValue2` / `GetValue2String` 都没有调用者。结论 | `value2=` 参数在本版 psm 中是一条死路径，不构成攻击面（这也解释了为什么 `type=mot_conv&value2=...` 之类的组合没有效果）。 | `19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:104` |
| 1032 | 推论（强推断） | 过滤功能未启用、或该 IP 未在允许列表时，`PsmLem_IsEnableIp` 返回 0 → `30cbc beq 30db8` 被采用 → 再经 `0x299b0`（若返回非 0）即可继续进入完整命令分派。也就是说 `exclusion` 与"0x299b0 返回非 0 的场景"不需要先前授权；其余命令的最终判定落在 `0x299b0`，需要在活体上确认它等价于什么（弱推断，无法离线定论）。 | `19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:256` |
| 1033 | 置信度 | 已排除（反汇编直读） | `19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:433` |
| 1034 | → HTTP 参数无法进入 `sprintf` 的 `%s`。132 B 缓冲充裕。排除。 | 排除。 | `19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:458` |
| 1035 | `PsmCmd_CreateMultipartHeader` | `0x20570` \| `strcpy` @ `0x20650` \| 栈 `sp+152`，256 B \| 拷贝前有显式长度检查，失败时打 `"(Multipart-Header name) Buffer Overflow"`（`0x208f0`）并 `return 2` | `19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:480` |
| 1036 | 5. 已排除清单（明确结论） |  | `19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:500` |
| 1037 | A. 命令注入 | 全部排除 | `19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:502` |
| 1038 | B. 参数解析路径 | 排除 | `19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:509` |
| 1039 | `value2` 死路径（§1.4）。 |  | `19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:512` |
| 1040 | C. `mode`/`type` 转换 | 排除 | `19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:514` |
| 1041 | D. 长度检查到位的拷贝 | 排除 | `19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:520` |
| 1042 | E. 不可达 | 排除（但建议在拿到调用者后重审） | `19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:525` |
| 1043 | 判定为"链接保留但静态不可达，或经未恢复的间接调用进入"。置信度 | 中（间接调用无法用纯静态手段完全排除）。 | `19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:527` |
| 1044 | "无 `bl` 调用者" ⇒ 不可达 | 强推断（间接调用不能排除） | `19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:555` |
| 1045 | ⇒ "相机作为 UPnP 控制点"假说在标准 SSDP 发现下不成立（链 B 关闭）。 |  | `19_路径1_Linux侧攻击面_20261015/实验记录_与教训_20261015.md:13` |
| 1046 | HTTP 引擎 | GoAhead（精简版，只实现 GET/POST） \| ❌ lighttpd 1.4.45 | `19_路径1_Linux侧攻击面_20261015/更正_Web服务器身份与作废的RCE线索_20261015.md:12` |
| 1047 | 剩余 RCE 线索 | CVE-2019-5096（GoAhead multipart UAF，CVSS 9.8）未测 \| ❌ 不适用（相机不跑 GoAhead） | `19_路径1_Linux侧攻击面_20261015/更正_Web服务器身份与作废的RCE线索_20261015.md:14` |
| 1048 | ⇒ 该路径已由本轮审计排除（见阶段A汇总 §3.1）。 |  | `19_路径1_Linux侧攻击面_20261015/更正_Web服务器身份与作废的RCE线索_20261015.md:60` |
| 1049 | 网络侧 RCE 结论 | 从"仅剩一条未测线索" → "线索前提错误，全部阴性" | `19_路径1_Linux侧攻击面_20261015/更正_Web服务器身份与作废的RCE线索_20261015.md:71` |
| 1050 | SOAP 控制 / 50001 内容 | ❌ 403 / RST（需 accctrl 授权） | `19_路径1_Linux侧攻击面_20261015/阶段A2_审计汇总_20261015.md:33` |
| 1051 | 可达路径全部边界正确（已排除） | 488 字节协议精确；QUERY_STRING URL 解码输出 ≤ out+376 < 488；CONTENT_TYPE boundary 的 73 字节缓冲有 ≤70/≤71 检查 | `19_路径1_Linux侧攻击面_20261015/阶段A2_审计汇总_20261015.md:41` |
| 1052 | ⇒ 候选 1「14 处 strcpy 可越界覆盖返回地址」：强推断 → 降级为「当前构型下不可越界」（双保险：源槽容量不足 + 入站报文无法影响源槽）。 |  | `19_路径1_Linux侧攻击面_20261015/阶段A2_审计汇总_20261015.md:116` |
| 1053 | ⇒ 免认证可达的内存破坏：在已审范围内「未发现」。 不等于"不存在"——只等于"已查的全是阴性"。 | 不等于"不存在"——只等于"已查的全是阴性"。 | `19_路径1_Linux侧攻击面_20261015/阶段A2_审计汇总_20261015.md:124` |
| 1054 | ❌ 其余全关 | 21/22/23/25/53/81/110/111/139/143/443/445/554/631/993/995/1080/1900(tcp)/ | `19_路径1_Linux侧攻击面_20261015/阶段A2_活体指纹_20261015.md:26` |
| 1055 | SOAP 控制 `/Server0/CDS_control` | ❌ 403（门关着） \| 需要我们的设备被相机授权（accctrl=ok） | `19_路径1_Linux侧攻击面_20261015/阶段A2_活体指纹_20261015.md:72` |
| 1056 | 50001 内容 `DO*/DM*/DT*.JPG` | ❌ 连接被 RST / 空响应 \| 同上，需要授权 | `19_路径1_Linux侧攻击面_20261015/阶段A2_活体指纹_20261015.md:73` |
| 1057 | 不能排除更坏情况（内存破坏导致 dlna 状态异常、DLNA 功能不可用直到重启）。 |  | `19_路径1_Linux侧攻击面_20261015/阶段A2_活体指纹_20261015.md:109` |
| 1058 | S5 的 rootfs 加密，无法离线比对；DLNA = G100 同款二进制这一点由字符串模板逐字吻合支撑（强推断）。 |  | `19_路径1_Linux侧攻击面_20261015/阶段A2_活体指纹_20261015.md:121` |
| 1059 | 栈保护 | ❌ 无 `__stack_chk_fail`（无 canary） | `19_路径1_Linux侧攻击面_20261015/阶段A_Linux攻击面测绘_20261015.md:43` |
| 1060 | 我现在无法再推进的部分需要活体指纹（预计 5 分钟，全部只读） |  | `19_路径1_Linux侧攻击面_20261015/阶段A_Linux攻击面测绘_20261015.md:130` |
| 1061 | 不排除它是工厂产线专用（量产固件裁剪）。 |  | `19_路径1_Linux侧攻击面_20261015/阶段A_Linux攻击面测绘_20261015.md:148` |
| 1062 | S5 的 rootfs 加密，无法离线比对；活体指纹是唯一确认手段。 |  | `19_路径1_Linux侧攻击面_20261015/阶段A_Linux攻击面测绘_20261015.md:150` |
| 1063 | `16_S5_核心总包_20261015/` | 唯一权威核心逻辑总包（2026-10-15）：00/01/04/05/06/09/12–15 各目录去重整合版 + 固件指针清单 + 包级 MANIFEST；不含固件/APK/参考仓库/录像等大二进制，收录与排除明细见包内 `00_本包说明_收录与排除.md` \| 交付包 | `README.md:75` |
| 1064 | 「S5 内核越界写已实机确认」 | ❌ 已撤回 | `REPO_CONTENTS.md:59` |
| 1065 | 「堆喷命中越界槽」 | ❌ 已撤回 | `REPO_CONTENTS.md:60` |
| 1066 | exFAT 越界写路线 | ❌ 判定不成立，不再投入 | `REPO_CONTENTS.md:61` |
| 1067 | 隐藏格式持久化：「`videoformat` 断电后回落 mp4、仅 `ntsc_pal` 持久」 | ❌ 10-14 受控复测未重现（n=2） | `REPO_CONTENTS.md:63` |
| 1068 | 已排除内容 | 体积 \| 原因 | `REPO_CONTENTS.md:74` |
| 1069 | `P1022641.MP4`（2 份） | ~426 MB \| 实拍录像。单文件 213 MB，超过 GitHub 100 MB 硬限制，必须排除 | `REPO_CONTENTS.md:79` |
| 1070 | 完整排除规则见 [`.gitignore`](.gitignore)。 |  | `REPO_CONTENTS.md:87` |
| 1071 | 被排除的只有厂商固件（80–87 MB 的 `S5___V*.bin` 等）。 |  | `REPO_CONTENTS.md:93` |
| 1072 | 收录规则 | 排除所有 `.git/` 目录（含独立子仓库的）、`.DS_Store` 与清单自身。 | `REPO_CONTENTS.md:109` |
| 1073 | 纯协议层与持久化的复现步骤不依赖被排除的大文件。 |  | `REPO_CONTENTS.md:127` |

---

## 表 4 · 全项目「危险 / 警告」清单

共 **410** 条。

关键词口径：`⚠️` `危险` `变砖` `不可逆` `挂死` `断电重启` `拔插` `血泪` `🔴` `警告` `严禁` `禁止`。

> 拆分说明：「后果 / 规避」列仅在原文含明确分隔符（`：` `→` `⇒` `——`）或含关键词从句时**机械拆分**，否则该列为空、内容全在左侧列。

| # | 危险操作 / 症状（原样） | 后果 / 规避（原样） | 出处 |
| --- | --- | --- | --- |
| 1 | ⚠️ 列举会把相机切到回放模式（此时无取景），用完自动切回。 |  | `00_调用前必查_已跑通路径总索引.md:39` |
| 2 | ⚠️ DLNA 内容树只在回放模式有内容。 |  | `00_调用前必查_已跑通路径总索引.md:40` |
| 3 | 三🔴 已知陷阱（踩过的坑，按严重度） |  | `00_调用前必查_已跑通路径总索引.md:66` |
| 4 | 1 | `req_acc` 高频重发 ⇒ 相机屏幕显示「智能手机应用程序需要更新」⇒ `invalid login` ⇒ 只能断电重启 \| `req_acc` 只在启动时发一次 | `00_调用前必查_已跑通路径总索引.md:70` |
| 5 | 5 | `startstream → err_busy` \| 相机有残留流会话 ⇒ 断电重启 | `00_调用前必查_已跑通路径总索引.md:74` |
| 6 | 在受控复测中未被重现（n=2）。写入 `ntsc + mov + 0x9b` 后断电重启，`ntsc_pal`、`videoformat`、 | 写入 `ntsc + mov + 0x9b` 后断电重启，`ntsc_pal`、`videoformat`、 | `00_项目总结/00_执行摘要_全文.md:17` |
| 7 | 「写完立刻回读」不能代表 flash 内容，只有断电重启后的读回才反映 flash。 |  | `00_项目总结/00_执行摘要_全文.md:22` |
| 8 | 唯一实机漏洞 = PTP length-DoS | PTP 解析器校验 type 不校验 length，length 不符 → 接口挂死、无超时；拔插 USB 恢复，无写操作、不砖机。 | `00_项目总结/00_执行摘要_全文.md:44` |
| 9 | ⚠️ 更正 | 这 17 档不是 open-gate 片门全开。真正的 5.9K（`mov_*_200mbps_5_9k_10bit`） | `00_项目总结/00_执行摘要_全文.md:80` |
| 10 | SD.DAT | S1R2（NAND）实测无只读模式、写错 `pardata.par` = 不可逆砖 → S5 上降级为 | `00_项目总结/00_执行摘要_全文.md:144` |
| 11 | H1 | 隐藏格式持久化 \| ✓ \| 直写 flash 的 65533 字节 blob 后，`ntsc_pal`、`videoformat`、`videoquality` 三项均可跨断电保留（2026-10-14 受控复测，n=2，见 31 号报告）。附条件：`videoquality` 的保留与开机时 SD 卡槽 1 的挂载状态相关（槽 1 未挂载时由 `0x9b` 降为 `0x9f`）；该机制仅 1 组对照，待重复实验确认。结论修订史：① 10-13 判「mov 回落」系 `persist.py` 上传协议缺陷（单次… | `00_项目总结/01_成果总表.md:9` |
| 12 | W3 | PTP length-DoS \| ✓ \| 唯一可复现挂死，拔插恢复，不砖机 | `00_项目总结/01_成果总表.md:45` |
| 13 | 2 | PTP 配置写回(0x9422/0x9423) \| ⚠️ 只改设置分区 \| 只读探测，未执行写（安全红线） | `00_项目总结/01_成果总表.md:64` |
| 14 | 3 | CAMSET 校验和伪造 \| ⚠️ 数据级 \| 已反推可伪造，仍是设置数据 | `00_项目总结/01_成果总表.md:65` |
| 15 | （S1M2 维修手册流程），而非"服务模式没进对"。红线 | 不要为点亮它去做不可逆的初始设置/地区后缀操作； | `00_项目总结/02_项目时间线.md:176` |
| 16 | a6k 🔴 | `mov_25p_200mbps_a6k_10bit` 等 \| `ok` \| 🔴 静默把 `videoformat` 改成 `avchd` \| — | `00_项目总结/02_项目时间线.md:215` |
| 17 | ⚠️ 初稿曾用 `grep mov_*` 从两份文件做朴素差集，得出「curmenu 独有 95 条」。那是伪结论 |  | `00_项目总结/02_项目时间线.md:240` |
| 18 | `ok` | 请求被接收 \| ⚠️ ≠ 生效，必须回读 `getsetting videoquality` 确认（当天 ≥6 次反例） | `00_项目总结/02_项目时间线.md:267` |
| 19 | 只有断电重启后的回读才代表 flash。 |  | `00_项目总结/03_思路总结_全文.md:120` |
| 20 | 仅存的 DoS 原语 | PTP length-DoS、senddata 尾块拒绝（均需拔插/拔电池恢复，不砖机）。 | `00_项目总结/03_思路总结_全文.md:130` |
| 21 | PTP 解析无 length 校验 → 可复现挂死（拔插恢复） | ✓ | `00_项目总结/03_思路总结_全文.md:140` |
| 22 | ⚠️ 结论更正 | 曾据此推断"近场任意设备可无认证读取 Wi-Fi 凭据"， | `00_项目总结/03_思路总结_全文.md:171` |
| 23 | 红线内不执行（地区后缀单次写入锁止，不可逆） |  | `00_项目总结/03_思路总结_全文.md:186` |
| 24 | ⚠️ 本包含有对相机写入的操作工具。非专业人员请勿轻易尝试 | 相关风险见 | `00_项目总结/04_定因与工具链成果_20261013.md:3` |
| 25 | "长名崩溃 = 数量 × 长度" | ⚠️ 修正 \| 初版实验里我们自己的工具把目录链拐进了照片数据区 ⇒ 崩溃另有原因。重做后结论为：长文件名本身 | `00_项目总结/04_定因与工具链成果_20261013.md:40` |
| 26 | 进一步利用 | 🔴 需要调试通道（UART/JTAG）。目前只有"崩/不崩"一个二值信号，与 exFAT 那条路遇到的是同一堵墙 | `00_项目总结/04_定因与工具链成果_20261013.md:77` |
| 27 | 1 | ROM BACKUP（服务模式） \| 目标：直接导出工厂/标定分区到 SD 卡。风险已列在手册 §5，其中"解除初始设置"可能不可逆 | `00_项目总结/04_定因与工具链成果_20261013.md:161` |
| 28 | 最后一个分片回 `err_busy` | 重试→`err_critical`，`abortsenddata=error`；相机仍在 VD4.30，未变砖。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:77` |
| 29 | 有真实变砖风险且换不到密钥。建议停止上传预言机这条线，转向恢复模式（见下）或硬件提取。 | 有真实变砖风险且换不到密钥。 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:90` |
| 30 | 相机变砖后的恢复（阶段 2/3 前必读） |  | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:92` |
| 31 | `ok` + 相机没回来 | 启动时验签失败 → 变砖 \| 走恢复模式；若恢复模式接受无签名固件 → 预言机从恢复模式入口打开 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md:110` |
| 32 | 发现：PTP 容器解析器校验了 `type` 字段，但没有校验 `length` 字段。当容器声明的 `length` 与实际发送字节数不符时，相机会按 length 永久等待剩余数据（无超时），导致 PTP 接口不可用，必须拔插 USB 才能恢复。 | 当容器声明的 `length` 与实际发送字节数不符时，相机会按 length 永久等待剩余数据（无超时），导致 PTP 接口不可用，必须拔插 USB 才能恢复。 | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:16` |
| 33 | 每个用例后都做存活校验是必须的 | 相机会阻塞，且只能靠物理拔插恢复。 | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:92` |
| 34 | `len = 4`（短于头部） | `4, 0x0001, op, tid` \| ⚠️ 超时 —— 相机阻塞 | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:175` |
| 35 | `len = 0` | `0, 0x0001, op, tid` \| ⚠️ 超时 —— 相机阻塞 | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:176` |
| 36 | `len = 4096`（大于实发） | `4096, 0x0001, op, tid` \| ⚠️ 超时 —— 相机阻塞 | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:177` |
| 37 | `len = 0xFFFFFFFF` | `0xFFFFFFFF, 0x0001, op, tid` \| ⚠️ 超时 —— 相机阻塞 | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:178` |
| 38 | 恢复必须物理拔插 USB 线（或重启相机）； |  | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:209` |
| 39 | 下一次 `GetDeviceInfo`（0x1001）将超时。相机保持无响应，直到拔插 USB。 | 相机保持无响应，直到拔插 USB。 | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:226` |
| 40 | 缺少必需的数据阶段（或畸形的 `length`）会让相机阻塞，唯一恢复方式是拔插 USB； |  | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:275` |
| 41 | 256 | 1036 B \| ⚠️ USB 写超时 → 挂起 | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:293` |
| 42 | 512 KB | 524300 B \| ⚠️ `USBErrorPipe`（端点 STALL） → 挂起 | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:306` |
| 43 | 相机状态 | 崩溃 / 重启 / 内存破坏 \| 阻塞（需拔插恢复） | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md:317` |
| 44 | 5 | 当前唯一实机漏洞 = PTP length-DoS：相机 PTP 解析器校验 type 不校验 length，length 不符 → 接口挂死、无超时；拔插 USB 恢复，无写操作、不砖机 \| 已证实（受控实测） | `01_研究报告/02_研究总报告_20261011/00-执行摘要.md:16` |
| 45 | PTP length-DoS（唯一"可复现挂死"） | length 不符 → 挂死，拔插恢复。 | `01_研究报告/02_研究总报告_20261011/00-执行摘要.md:44` |
| 46 | 2 | PTP 配置写回（0x9422/0x9423） \| ⚠️ 只改设置分区（数据，非代码） \| 只读探测了状态机；未执行写（安全红线） | `01_研究报告/02_研究总报告_20261011/00-执行摘要.md:53` |
| 47 | 3 | CAMSET 校验和可伪造（写设置分区） \| ⚠️ 数据级 \| 校验和已反推、可伪造；仍是设置数据非代码 | `01_研究报告/02_研究总报告_20261011/00-执行摘要.md:54` |
| 48 | 已确认的实机漏洞只有一条 | PTP length 不校验导致的本地 DoS（§06），挂死、拔插 USB 恢复、无写 / 不砖机。 | `01_研究报告/02_研究总报告_20261011/02-攻击面总览.md:19` |
| 49 | 3 | PTP 配置写回（0x9422 / 0x9423） \| ⚠️ 只改设置分区（数据，非代码） \| 软件 / USB \| 只读探测了状态机；未执行写（安全红线） | `01_研究报告/02_研究总报告_20261011/02-攻击面总览.md:28` |
| 50 | 4 | CAMSET 校验和可伪造（写设置分区） \| ⚠️ 数据级 \| 软件 / Wi-Fi \| 校验和已反推、可伪造；仍是设置数据非代码 | `01_研究报告/02_研究总报告_20261011/02-攻击面总览.md:29` |
| 51 | 用户问题 | 除了崩溃，有没有更有价值的东西。本章先把"崩溃 / 挂死"这一类已打通的结果讲清楚（它们本身不是 RCE，但暴露了状态机/解析器的缺陷），并给出唯一"可复现挂死"的实机漏洞。 | `01_研究报告/02_研究总报告_20261011/06-崩溃与DoS.md:3` |
| 52 | 6.1 ★ 唯一"可复现挂死"实机漏洞 | PTP length-DoS | `01_研究报告/02_研究总报告_20261011/06-崩溃与DoS.md:5` |
| 53 | 触发：发送 12 字节但头声明 `length=0x400` 的包 → PTP 数据面挂死。 |  | `01_研究报告/02_研究总报告_20261011/06-崩溃与DoS.md:10` |
| 54 | 恢复：拔插 USB 即恢复（相机本身不死机，只是该 PTP 会话的 DMA 卡住）。 |  | `01_研究报告/02_研究总报告_20261011/06-崩溃与DoS.md:11` |
| 55 | 价值：证明了"解析器长度未校验"这一真实缺陷，但它是挂死而非内存破坏，不能直接拿到 shell / 改内容。 |  | `01_研究报告/02_研究总报告_20261011/06-崩溃与DoS.md:13` |
| 56 | 已打通的"挂死/卡死"有两条 | PTP length-DoS（拔插 USB 恢复）、senddata 末块重试状态机卡死（拔电池恢复）。 | `01_研究报告/02_研究总报告_20261011/06-崩溃与DoS.md:37` |
| 57 | ⚠ mode=lenprobe 是受控 DoS 演示（最后才跑，跑完需拔插 USB） |  | `01_研究报告/02_研究总报告_20261011/07-USB-PTP-SCSI.md:61` |
| 58 | 相机极易砖（本会话已多次 brick / 卡死），恢复只能靠拔电池。以下规则是"不造成不可逆损坏"的底线，任何实验必须满足。 | 以下规则是"不造成不可逆损坏"的底线，任何实验必须满足。 | `01_研究报告/02_研究总报告_20261011/11-安全约束.md:3` |
| 59 | 绝不发送 length 不符的 PTP 包，除非是最后的、已授权的 length-DoS 演示（跑完需拔插 USB 恢复）。 |  | `01_研究报告/02_研究总报告_20261011/11-安全约束.md:17` |
| 60 | ├── 06-崩溃与DoS.md ← 崩溃/挂死路径、PTP length-DoS |  | `01_研究报告/02_研究总报告_20261011/README.md:32` |
| 61 | 软件/Wi-Fi 侧 | 解不开 AES 密钥（芯片内固化），也摸不到调试后门；能拿到的最强"改内容"原语是固件升级写路径，但目前被"最终-chunk flash 定址失败（~31s → err_busy/err_critical）"卡住，尚未打通到一次成功的 `endsenddata`。已确认的实机漏洞只有一条：PTP length 不校验导致的本地 DoS（挂死，拔插 USB 恢复）。RCE（编译 C 注入 / 已公开 GoAhead CVE）目前全部阴性，仅剩 CVE-2019-5096（multipart UAF）未测、需堆控。 | `01_研究报告/02_研究总报告_20261011/README.md:49` |
| 62 | 候选隐藏/调试 mode（~70 个，纯 GET，零副作用，不含 reboot/reset/format/erase/write 等危险项） |  | `01_研究报告/02_研究总报告_20261011/research/Wi-Fi实机预言机与mode枚举实测-中文.md:81` |
| 63 | 六项附加成果（全部只读；唯一例外是 1 次受控 DoS 演示 | 拔插 USB 即恢复、无任何写操作，见 §9.5）： | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:14` |
| 64 | PTP 漏洞 / CVE 枚举 + 实机探测（§9） | 11 个 NVD CVE 逐条核对（全部是主机侧解析器类，无一适用于 S5 主机→相机方向）+ 43 个安全 fuzz 探测 + 1 次受控 length-DoS → 无 RCE/无明文泄露，坐实唯一漏洞为本地 DoS（length 挂死，拔插恢复）；另发现设备真实实现的未文档化命令 0x9103。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:19` |
| 65 | DoS 隐患已工程化排除，并已受控实机全链条坐实（2026-10-11，见 §9.5） | 相机 PTP 解析器校验 type 不校验 length，length 不符 → 接口挂死、无超时；macOS 主机侧（ImageCaptureCore）同样不校验 length（原样发出，仅内部约 60 s 超时返回空响应）。所有工具发送前对 length 做精确计算/断言；`lenprobe` 模式是唯一故意触发该行为的受控演示（拔插 USB 恢复、无写操作、不砖机）。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:40` |
| 66 | ⚠️ 老/新平台布局差异 | 参考库 `pana_unpack.py`/`cross_model_ks.py` 用的是新平台布局（表@0x2DC、name@+0x10、off@+0x24），对老平台会把 load_addr 当成 offset，导致 keystream 偏移错位。老平台正确偏移为上表（name@+0、off@+0xC）。本报告已用正确偏移复核（规范分区表见 `s5_parts_v2.json`）。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:57` |
| 67 | ★ 头号隐患（已工程化规避） | 相机 PTP 解析器校验 type 不校验 length。length 与实发不符 → 相机永久等待（无超时）→ PTP 接口挂死，需拔插 USB 恢复（本地 DoS，不可升级为 RCE）。两脚本发送前均对 length 做断言/精确计算。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:195` |
| 68 | PTP 漏洞 / CVE 枚举 + 实机 fuzz（§9） | 11 个 NVD CVE 逐条核对（全是主机侧解析器类，无一适用于 S5 主机→相机方向）+ 43 个安全探测 + 受控 length-DoS 实验 → 无 RCE、无提权、无密钥/明文泄露；坐实的只有本地 DoS（length 挂死、拔插恢复）与参数数量/TID 校验缺失（无利用价值）。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:380` |
| 69 | 无 RCE/无明文泄露；仅坐实本地 DoS（length 挂死、拔插恢复） | 仅坐实本地 DoS（length 挂死、拔插恢复） | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:399` |
| 70 | 本报告为静态逆向 + 纯只读实机研究，不宣称已破解，不含可刷写补丁。唯一带副作用的操作是 1 次受控 length-DoS 演示（§9.5） | 使 PTP 接口挂死，拔插 USB 即恢复，未写存储/固件、未重置、未砖机。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:415` |
| 71 | 恢复 | 拔插 USB（相机无恙：未写存储、未影响固件、无重置） | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:494` |
| 72 | 无 length 校验（40333） | ✓ 复现：length 不符 → 挂死、无超时 \| 坐实（本地 DoS） | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:505` |
| 73 | 无 RCE / 提权 / 密钥或明文泄露 | 11 个 PTP 相关 CVE 在 S5 上（主机→相机方向）无一适用；实机 fuzz（43 个安全探测 + 1 个受控 DoS）只发现 本地 DoS（length 挂死） 与 2 处解析器校验缺失（参数数量 / TID），均无利用价值。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:514` |
| 74 | "length-DoS" 成为全链条坐实、可复现的发现 | 可让相机 PTP 接口暂时不可用（拔插恢复）。对 AES 目标无安全价值。 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md:515` |
| 75 | 日期：2026-10-11 性质：静态逆向研究 + 纯只读实机探测（唯一例外：1 次受控 length-DoS 演示，拔插 USB 即恢复、无任何写操作，见主报告 §9.5）。无可刷写补丁。 | 日期：2026-10-11 性质：静态逆向研究 + 纯只读实机探测（唯一例外：1 次受控 length-DoS 演示，拔插 USB 即恢复、无任何写操作，见主报告 §9.5）。 | `01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:3` |
| 76 | PTP 漏洞 / CVE 枚举 + 实机探测（§9） | 11 个 NVD CVE 逐条核对（全部是主机侧解析器类，无一适用于 S5 主机→相机方向）+ 43 个安全 fuzz 探测 + 1 次受控 length-DoS 全链条验证 → 无 RCE/无明文泄露，坐实唯一漏洞为本地 DoS（length 挂死、无超时、拔插恢复）；发现 0x9421/0x9605 不校验参数数量、TID 不校验、0x9103 等未文档化命令被设备识别。 | `01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:17` |
| 77 | DoS 隐患已工程化排除，并已受控实机全链条坐实（§9.5） | 相机 PTP 解析器校验 type 不校验 length，length 不符 → 接口挂死、无超时；macOS 主机侧同样不校验 length。所有工具发送前对 length 精确计算/断言；`fuzz`/`lenprobe` 模式中只有 `lenprobe` 故意触发该行为（受控演示，拔插 USB 恢复）。 | `01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:47` |
| 78 | ./tools/s5_ptp_dump ./ptp_out_lp S5 lenprobe # ⚠ 受控 length-DoS 演示（最后运行，需拔插恢复） |  | `01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md:56` |
| 79 | 🔴 高风险 | `enum_videoquality.py --confirm` \| 批量写；仅在明确授权 + 接电源 + 基线核对后 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/06_安全约束与风险.md:49` |
| 80 | 该状态已写入 flash，跨断电重启持久，无需重启后重新设置。 |  | `01_研究报告/04_隐藏格式_持久化成果.md:7` |
| 81 | `flashwrite`（危险，需 `--confirm`） | 下载当前 blob → 仅设 ntsc → 重算校验和 → 上传。 | `01_研究报告/04_隐藏格式_持久化成果.md:49` |
| 82 | 一键恢复隐藏格式（危险，先确认相机健康，AC 供电） |  | `01_研究报告/04_隐藏格式_持久化成果.md:60` |
| 83 | ⚠️ 注意 | `allmenu` 含 `cmd_value`（可执行项），`curmenu` 一个都没有（其 `mov_*`/`mp4_*` 多出自 `title_id`/`img`/`id` 标签标识符）。切勿用 `grep` 跨这两个文件做朴素差集——那会得出「curmenu 独有 95 条」这类伪结论。 | `01_研究报告/04_隐藏格式_持久化成果.md:129` |
| 84 | ❌ UART 是死路 | U-Boot `BOOTDELAY=-2` + 内核 `console=null loglevel=0` + `ENV_IS_NOWHERE`（接了也是黑的） \| ⚠️ 不可直接套用：S5 的 U-Boot 配置未读（rootfs 加密，离线看不到 env）。先做离线核验（见 §三 P3）：在 48 分区表的 type=2 明文分区里找 env / BOOTDELAY / console 痕迹；若同样关闭 → S5 UART 判死路；若开启 → UART 复活为只读 bootlog 通道 | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:50` |
| 85 | ⚠️ SD.DAT / ROM-flashing 高风险别碰 | 无只读/RAM-boot 模式，跑代码必须写 flash；写错 `pardata.par` = 不可逆毁出厂标定；S1R2 是 NAND，GoPro 的 eMMC 路径从未在 NAND 上验证成功 \| ⚠️ 保守处理：S5 存储类型（eMMC/NAND）需拆机确认（P1）。若同为 NAND → 风险同级，SD.DAT 降级为 JTAG 之后的备胎，不做第一动作 | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:51` |
| 86 | ⚠️ legacyboot（U-Boot 从 SD 引导自核） | 命令存在但默认 bootcmd 不用，且需 U-Boot 控制台（被 console=null 堵死） \| 同 UART 结论，取决于 P3 核验结果 | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:52` |
| 87 | ⚠️ 服务模式组合键 | 松下有传统：GX85 = 回放+AF/AE LOCK+右键 开机；ZS30 = 录像+MENU/SET 开机 → SERVICE MODE；S1R2 组合键无公开资料 \| ✅ 零风险直接试 S5：多键组合开机盲试（参考上述两例 + 快门/电源/拨盘变体），命中即可能进维护菜单 | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:53` |
| 88 | ✓ UVC 零长度控制请求 → 持久 DoS | 网络摄像头模式 VS probe `SET_CUR(wLength=0)` → 守护进程挂死，跨断电不恢复，须出厂重置 \| S5 漏洞档案补充项：UVC probe 零长度测试（低优先，属 DoS 归档） | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:54` |
| 89 | P6 | SD.DAT / ROM-flashing：BootROM 跑 SD 卡自编 `DATA.BIN`，绕 loader2/3 与验签链，可写可 dump \| P1（确认存储类型）+ 全量备份 + 验证过的 `pardata.par` \| 高（S1R2 NAND 教训：写错标定数据 = 不可逆砖） \| 彻底绕过验签链的写入口（JTAG 受阻时的备胎） \| 未做（降级为备胎） | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md:85` |
| 90 | UVC 零长度控制请求 → 持久 DoS | 网络摄像头模式下，向 VS probe 发 `SET_CUR(wLength=0)` → 守护进程整体挂死，跨断电不恢复，须出厂重置 \| ✅ 三段式对照复现 | `01_研究报告/06_S1R2移交_20261012/S1R2_已排除路线与风险备忘.md:21` |
| 91 | ⚠️ 3. SD.DAT / ROM-flashing 恢复模式（Milbeaut 的"EDL 模式"） |  | `01_研究报告/06_S1R2移交_20261012/S1R2_已排除路线与风险备忘.md:38` |
| 92 | 写错 `pardata.par` = 不可逆毁掉出厂标定数据（变砖且救不回）。 |  | `01_研究报告/06_S1R2移交_20261012/S1R2_已排除路线与风险备忘.md:41` |
| 93 | ⚠️ 4. `legacyboot`（U-Boot 从 SD 卡引导自定义内核） |  | `01_研究报告/06_S1R2移交_20261012/S1R2_已排除路线与风险备忘.md:45` |
| 94 | ⚠️ 5. 服务模式组合键（松下传统） |  | `01_研究报告/06_S1R2移交_20261012/S1R2_已排除路线与风险备忘.md:49` |
| 95 | ⚠️ 6. 配置文件导入（`0x9422`）/ Flow XML |  | `01_研究报告/06_S1R2移交_20261012/S1R2_已排除路线与风险备忘.md:53` |
| 96 | ④ 验证 | 菜单里确实变了，且断电重启后仍在（持久）✓ | `01_研究报告/06_S1R2移交_20261012/S1R2两项成果_移交S5同事.md:69` |
| 97 | · 都【持久化】了（断电重启后仍在）✓ |  | `01_研究报告/06_S1R2移交_20261012/S1R2两项成果_移交S5同事.md:77` |
| 98 | ⚠️ 注意 | S1R2 的 CAMSET 是 9.2MB，S5 的 camsetting 是 65,533 字节， | `01_研究报告/06_S1R2移交_20261012/S1R2两项成果_移交S5同事.md:91` |
| 99 | F1 越界写（危险，写内核 RAM） |  | `01_研究报告/06_S1R2移交_20261012/S1R2两项成果_移交S5同事.md:156` |
| 100 | 相机全程未崩（写的是 RAM，最坏 = 死机重启，不会变砖） |  | `01_研究报告/06_S1R2移交_20261012/S1R2两项成果_移交S5同事.md:163` |
| 101 | 内核 OOB = 改内核（DoS / 潜在内存破坏，危险） |  | `01_研究报告/06_S1R2移交_20261012/S1R2两项成果_移交S5同事.md:213` |
| 102 | 该表述在受控复测中未被重现（n=2） | 写入 `ntsc + mov + 0x9b` 后断电重启，`ntsc_pal`、`videoformat`、`videoquality` 三项均保留。 | `01_研究报告/07_隐藏格式持久化_追查_20261013.md:12` |
| 103 | 因此「写完立刻回读」不能作为持久化判据，只有断电重启后的读回才反映 flash 内容。该方法学结论不受本次更正影响。 | 因此「写完立刻回读」不能作为持久化判据，只有断电重启后的读回才反映 flash 内容。 | `01_研究报告/07_隐藏格式持久化_追查_20261013.md:17` |
| 104 | 最终实测状态（断电重启后读回） |  | `01_研究报告/07_隐藏格式持久化_追查_20261013.md:29` |
| 105 | `mov_30p_200mbps_a6k_10bit`（变形 6K） | ⚠️ ~~返回 `ok` 但码不变 → 静默忽略~~ → 实为静默把容器改成 `avchd` | `01_研究报告/08_格式对照表_NTSC-MOV_20261013.md:133` |
| 106 | （10-14 更正·🔴 危险） `a6k` 不止「忽略」 | 实测 `mov_25p_200mbps_a6k_10bit` / `mov_25p_150mbps_a6k_10bit` / `mov_25p_100mbps_a6k` 都返回 `ok`，却静默把 `videoformat` 从 `mov` 改成 `avchd`（`videoquality` 变成 `avchd_50p_28mbps`）——不报错，只改状态。 | `01_研究报告/08_格式对照表_NTSC-MOV_20261013.md:135` |
| 107 | ⚠️ 同代但不同定位 | token 可能"读回正常"却录不出东西（S1H 报告：16 候选里仅 2 个出真媒体）。 | `01_研究报告/10_跨机型移植边界_20261013.md:62` |
| 108 | 既无收益又增加变砖风险。 |  | `01_研究报告/10_跨机型移植边界_20261013.md:72` |
| 109 | ⚠️ 存储有效但不生效 / 有风险 |  | `01_研究报告/12_可写设置面审计_20261013.md:33` |
| 110 | 别碰 `4kcrop`；另外发现大量快速写入也可能让相机短暂挂死，恢复靠拔电池或等待。 | 另外发现大量快速写入也可能让相机短暂挂死，恢复靠拔电池或等待。 | `01_研究报告/12_可写设置面审计_20261013.md:66` |
| 111 | 以下为同族机型的通用清单，S5 逐项名称以用户实拍为准；标 ⚠️ 的是危险项。 | 标 ⚠️ 的是危险项。 | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:22` |
| 112 | ROM WRITE / FACTORY DATA WRITE | 把备份数据写回覆盖 \| ⚠️ 写错=不可逆 | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:27` |
| 113 | VERSION / VERSION UP | 版本显示 / 升级 \| ⚠️ 升级有风险 | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:29` |
| 114 | ADJUST / CALIBRATION | 法兰距、AF、BIS 防抖、快门等校准 \| ⚠️ 破坏性 | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:30` |
| 115 | INITIAL SETTINGS / CANCELLATION | 解除初始设置（许多项的前置门） \| ⚠️ 改持久状态 | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:31` |
| 116 | REGION / MODEL SUFFIX | 地区后缀选择 \| ⚠️ 单次写入锁止，选错可能永久锁死 | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:32` |
| 117 | FLAG SET（all flags → 'F'） | 清/改标志位 \| ⚠️ 破坏性 | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:33` |
| 118 | 红线：不要为了点亮 ROM BACKUP 去贸然做"解除初始设置/Strict/地区后缀"——那是不可逆的持久改动 |  | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:114` |
| 119 | `system_profiler SPCameraDataType` 能看到 DC-S5。改 USB 连接方式后必须拔插一次 USB 才会重新枚举。 | 改 USB 连接方式后必须拔插一次 USB 才会重新枚举。 | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:139` |
| 120 | 不需要触碰任何不可逆步骤（地区后缀单次写入锁止）即可使用 ROM BACKUP。 |  | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:195` |
| 121 | ⚠️ 菜单可能同时有"导出"和"写回"两项 | 只能选导出/备份；选到 ROM WRITE / 恢复 = 覆盖机身标定，不可逆 | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:203` |
| 122 | ⚠️ 导出中途断电/拔卡 | 可能损坏卡（可格式化恢复）或导出不完整 | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:204` |
| 123 | ⚠️ 导出内容含机身序列号 | 对外分发需脱敏 | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:205` |
| 124 | 10.2 ⚠️ 退出工程模式的隐藏前提（本次实测） |  | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:226` |
| 125 | ### ⚠️ 禁令 | 不要按 `DISP.` 键 | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:247` |
| 126 | ⇒ 从服务模式出来后，必须拔插 USB 才会重新枚举为 `0x2382`。 |  | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md:267` |
| 127 | 5. ⚠️ 安全结论（已根据实机结果更正） |  | `01_研究报告/15_蓝牙BLE协议逆向_20261013.md:94` |
| 128 | ⚠️ 两次扫描 IE 不一致 | 一次带 TIM + 短 WPS IE + WMM，另一次无 TIM + 长 WPS IE。 | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:82` |
| 129 | ⚠️ 该步会向相机写入（标准 CCCD 订阅，官方 App 每次连接都做，可逆，不碰设置/flash）， |  | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md:313` |
| 130 | 4. ⚠️ 安全结论（二次更正） |  | `01_研究报告/19_BLE凭据链打通_先写后读_20261013.md:88` |
| 131 | 但越界写是内核内存破坏，S5 的槽位分布完全未知 | 选错槽位 = 崩溃/变砖。 | `01_研究报告/21_S1R2_exFAT越界写对S5的意义_20261013.md:56` |
| 132 | 风险不可逆 | 第 2 级测试是内核内存破坏，可能变砖。建议先做第 1 级， | `01_研究报告/21_S1R2_exFAT越界写对S5的意义_20261013.md:87` |
| 133 | 4 | 卡拔插后设备节点会变 \| `disk8s1` → 可能变成 `disk9s1`，脚本需按"卷名 LUMIX + ExFAT + ≥60GB"自动重新识别 | `01_研究报告/22_S5_exFAT越界写前置条件确认_20261013.md:77` |
| 134 | ⚠️ 本文结论已修订。 原标题为"实机确认"，但后续一个决定性实验 | ⚠️ 本文结论已修订。 | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:3` |
| 135 | ⚠️ 顺带的一个方法论警告 | S1R2 报告同样把"相机报写入错误"当作 | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:40` |
| 136 | ⚠️ 本节原写于"越界写已确认"的错误前提之下。地基（§0.5）既已推翻， | ⚠️ 本节原写于"越界写已确认"的错误前提之下。 | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:136` |
| 137 | ⚠️ 一个必须记录的推算更正 | `vol_amap = kmalloc_array(map_sectors, sizeof(struct buffer_head *))` | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:155` |
| 138 | 必须 fsync 落盘、回读要用新 fd、卡拔插后设备节点会变）。 |  | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md:218` |
| 139 | ⚠️ 继续深挖需要调试通道（UART/JTAG）。目前只有"崩/不崩"一个二值信号， | ⚠️ 继续深挖需要调试通道（UART/JTAG）。 | `01_研究报告/24_相机长文件名崩溃_定因_20261013.md:102` |
| 140 | 2 | 永不刷真实固件 \| 变砖不可恢复 | `01_研究报告/25_操作记录与风险手册_20261013.md:17` |
| 141 | 3 | 永不 `resetDevice`、永不写 PTP 配置回写（`0x9422`/`0x9423`/`0x9406` 子码） \| 不可逆 | `01_研究报告/25_操作记录与风险手册_20261013.md:18` |
| 142 | 8 | 服务模式只读，不点任何会写标定的项 \| 部分项（地区后缀）一次性写入、不可逆 | `01_研究报告/25_操作记录与风险手册_20261013.md:23` |
| 143 | 设备节点 | 卡拔插后会变（`disk8s1` → 可能变 `disk9s1`） \| 脚本需按"卷名 + 文件系统 + 容量"自动重新识别 | `01_研究报告/25_操作记录与风险手册_20261013.md:37` |
| 144 | ⚠️ 若分配器踩到正在使用的簇 | 照片/文件被毁、目录链被打乱（本项目真实发生过一次，见 `24_` §6.1） | `01_研究报告/25_操作记录与风险手册_20261013.md:115` |
| 145 | ⚠️ 相机可能进入反复重启（预期内的实验结果，不是故障） |  | `01_研究报告/25_操作记录与风险手册_20261013.md:116` |
| 146 | `Cancel Initial Settings`（解除初始设置） | 🔴 高 \| 可能触发地区后缀一次性写入，不可逆 | `01_研究报告/25_操作记录与风险手册_20261013.md:184` |
| 147 | 修改任何标定值 | 🔴 极高 \| 影响出厂标定，可能永久损坏 | `01_研究报告/25_操作记录与风险手册_20261013.md:185` |
| 148 | `4kcrop` 相关 | 🔴 禁碰 \| 已知高风险 | `01_研究报告/25_操作记录与风险手册_20261013.md:186` |
| 149 | 标出哪些步骤不可逆，逐一确认后才动手 |  | `01_研究报告/25_操作记录与风险手册_20261013.md:191` |
| 150 | "240 个长名文件导致崩溃（数量×长度）" | ⚠️ 初版结论被污染 \| 当时工具把目录链拐进了照片数据区；重做后结论改为"长文件名本身"（见 `24_`） | `01_研究报告/25_操作记录与风险手册_20261013.md:218` |
| 151 | 风险：（可能造成什么不可逆后果） |  | `01_研究报告/25_操作记录与风险手册_20261013.md:253` |
| 152 | 4 | 卡拔插后设备节点会变 \| 按卷名+文件系统+容量自动重新识别 | `01_研究报告/25_操作记录与风险手册_20261013.md:268` |
| 153 | `mov_25p_200mbps_a6k_10bit` | `ok` \| 容器被改成 AVCHD（危险） | `01_研究报告/25_操作记录与风险手册_20261013.md:298` |
| 154 | `mov_25p_150mbps_a6k_10bit` | `ok` \| 改成 AVCHD（危险） | `01_研究报告/25_操作记录与风险手册_20261013.md:299` |
| 155 | `mov_25p_100mbps_a6k` | `ok` \| 改成 AVCHD（危险） | `01_研究报告/25_操作记录与风险手册_20261013.md:300` |
| 156 | 只有「断电重启之后」的回读才代表 flash 内容 |  | `01_研究报告/25_操作记录与风险手册_20261013.md:359` |
| 157 | 三项在断电重启后均保留，唯 `videoquality` 与开机时 SD 卡槽 1 的挂载状态相关。详见 31 号报告。 | 三项在断电重启后均保留，唯 `videoquality` 与开机时 SD 卡槽 1 的挂载状态相关。 | `01_研究报告/25_操作记录与风险手册_20261013.md:364` |
| 158 | 注意事项 | ⚠️ macOS 给每个文件都生成了 `._文件名` 副档名 ⇒ 目录项翻倍、名字更长，变量被放大两倍 | `01_研究报告/26_本次运行日志_20261013.md:95` |
| 159 | 2026-10-13 19 | 2x — ⚠️ 发现工具把卡写坏了 | `01_研究报告/26_本次运行日志_20261013.md:107` |
| 160 | 6 | ⚠️ 修正："长名崩溃"初版结论被工具 bug 污染，已重做 | `01_研究报告/26_本次运行日志_20261013.md:173` |
| 161 | 注意事项 | ⚠️ 菜单里"灰"不等于禁用，点灰项会尝试执行 | `01_研究报告/26_本次运行日志_20261013.md:214` |
| 162 | 2026-10-13 20 | 0x — ⚠️ 误操作与恢复 | `01_研究报告/26_本次运行日志_20261013.md:219` |
| 163 | 风险：🔴 `ADJFLAG→ALL F` 会改写机身调整标志 |  | `01_研究报告/26_本次运行日志_20261013.md:223` |
| 164 | 退出服务模式 + 拔插后 `idProduct = 9090 (0x2382)` | 正常 | `01_研究报告/26_本次运行日志_20261013.md:244` |
| 165 | 判定：⚠️ 本路线关闭（与项目红线"永不发送 0x9406 子码"一致） |  | `01_研究报告/26_本次运行日志_20261013.md:274` |
| 166 | 2 | 固定 16fps（×0.92） \| 储备仍 0，垫帧 54 次 ⚠️ | `01_研究报告/26_本次运行日志_20261013.md:373` |
| 167 | ④ 严禁反复重试 req_acc | 会触发 invalid login，必须重启相机 | `01_研究报告/26_本次运行日志_20261013.md:557` |
| 168 | 相机断电重启 | 进入"等待App连接" → 启动本工具（只发一次 req_acc） | `01_研究报告/26_本次运行日志_20261013.md:573` |
| 169 | 相机刚断电重启 + 首次授权 ok | camctrl 可用（touch / af_ae_lock 实测 ok） | `01_研究报告/26_本次运行日志_20261013.md:623` |
| 170 | 🚫 三条铁律（血泪教训，后人必读） |  | `01_研究报告/26_本次运行日志_20261013.md:666` |
| 171 | `req_acc` 绝不能高频重发 | 会触发相机「智能手机应用程序需要更新」+ `invalid login`，只能断电重启恢复 | `01_研究报告/26_本次运行日志_20261013.md:668` |
| 172 | 5 | ⚠️ 格式可编辑 + 相机支持写回 ⇒ 存在一条"读-改-写"EEPROM 的通道，潜力大但极高风险 | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:15` |
| 173 | `SDALL→DSC(ID CHECK)` | SD → 相机（全量，带 ID 校验）= 写回 \| 🔴 不可逆 | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:39` |
| 174 | `SDALL→DSC(FORCE)` | SD → 相机（强制） \| 🔴 不可逆 | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:40` |
| 175 | `SDUSER→DSC(FORCE)` | SD(用户数据) → 相机（强制） \| 🔴 不可逆 | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:41` |
| 176 | `ADJFLAG→ALL F` | 把所有调整标志置为 `F` \| 🔴 危险（相机可能视为未标定） | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:43` |
| 177 | `WBADJ→STEPMODE` | 进入白平衡调整步进模式 \| 🔴 校准类 | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:48` |
| 178 | ⚠️ 菜单里的"灰"不等于禁用 | 实测点击灰项会尝试执行并报 `读取错误请检查此卡` | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:51` |
| 179 | 一条"读-改-写"通道 | ⚠️ 见 5.2 | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:132` |
| 180 | 5.2 ⚠️ 新暴露的能力 | EEPROM 读-改-写 | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:134` |
| 181 | 触发地区后缀写锁 | 一次性锁定、不可逆 | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:149` |
| 182 | 6. ⚠️ 本次操作中需要记录的风险事件 |  | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:162` |
| 183 | `ADJFLAG→ALL F` | 改写机身调整标志 \| ⚠️ 需确认相机功能是否正常 | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:170` |
| 184 | 后续严禁再在 ROM BACKUP 菜单里试点其它项 |  | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:176` |
| 185 | ⚠️ 只选 `DSC | SD`；其余项（`SD*→DSC`、`ADJFLAG→ALL F`、`WBADJ→STEPMODE`）一律不碰 | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:191` |
| 186 | ⚠️ 导出中途不要拔卡/断电 |  | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:192` |
| 187 | ⚠️ 导出文件含机身序列号，对外分发需脱敏 |  | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md:193` |
| 188 | 它大概做什么 | 这类流程通常先擦除目标区域 ⚠️ | `01_研究报告/28_PTP固件更新协议审计_20261013.md:127` |
| 189 | 若擦除后不写（或写不进） | 相机可能再也开不了机 ⚠️⚠️⚠️ | `01_研究报告/28_PTP固件更新协议审计_20261013.md:128` |
| 190 | 兜底 | ❌ 无 —— 项目自己判定 SD.DAT 恢复模式"有砖机史、不可逆" | `01_研究报告/28_PTP固件更新协议审计_20261013.md:129` |
| 191 | 判定：这是典型的"擦除即变砖"风险，而收益只是"看一眼地址"。 |  | `01_研究报告/28_PTP固件更新协议审计_20261013.md:133` |
| 192 | ⇒ 它把"验证"加速了，但没有把"搜索空间"变小。 ⚠️ | ⚠️ | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:123` |
| 193 | ⚠️ 注意 | ROM BACKUP 拿到的是本机的当前值，固件里是出厂镜像。 | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:149` |
| 194 | 6. ⚠️ 一处与 S1R2 报告的分歧 | `0x9606` 地址参数 | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:173` |
| 195 | ⚠️ 项目红线不变 | 永不发送 `0x9406` 子码（8 个子码全为带副作用动作）。 | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:190` |
| 196 | ⚠️ 勘误与纠正（2026-10-14，依据同事《固件配对核验与纠正》） |  | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md:249` |
| 197 | 2.5 a6k | 返回 `ok` 但静默把容器改成 AVCHD（危险副作用） | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:105` |
| 198 | `mov_25p_200mbps_a6k_10bit` | `ok` \| 危险：`videoformat` 从 `mov` 变成 `avchd`，`videoquality` 变成 `avchd_50p_28mbps` | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:109` |
| 199 | `mov_25p_150mbps_a6k_10bit` | `ok` \| 危险：同上 | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:110` |
| 200 | `mov_25p_100mbps_a6k` | `ok` \| 危险：同上 | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:111` |
| 201 | `mov_25p_200mbps_a6k_10bit` | `ok` \| 危险：改成 AVCHD | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:385` |
| 202 | `mov_25p_150mbps_a6k_10bit` | `ok` \| 危险：改成 AVCHD | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:386` |
| 203 | `mov_25p_100mbps_a6k` | `ok` \| 危险：改成 AVCHD | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:387` |
| 204 | 只有断电重启后的回读才代表 flash 内容。 |  | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:413` |
| 205 | （2026-10-14 受控复测）持久化结论 | 「持久化只对 `ntsc_pal` 成立、`videoformat` 断电后回落 mp4」 \| 未获重现（n=2）：写入 `ntsc + mov + 0x9b` 后断电重启，`ntsc_pal`、`videoformat`、`videoquality` 三项均保留。`videoquality` 的保留与开机时 SD 卡槽 1 的挂载状态相关（槽 1 未挂载时 `0x9b`→`0x9f`）。样本量 n=2，机制假设待重复实验确认。详见 `01_研究报告/31_录制格式持久化_受控复测_20261014.md` | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:424` |
| 206 | ⇒ 严禁用 `grep` 跨两文件做朴素差集（那正是「curmenu 独有 95 条」伪结论的根因）。 |  | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md:454` |
| 207 | 方法：受控变量实验（flash 写入 → 断电重启 → 读回） |  | `01_研究报告/31_录制格式持久化_受控复测_20261014.md:5` |
| 208 | 结论摘要 | 在两项受控试验中，`videoformat` 的 `mov` 取值均在断电重启后保留， | `01_研究报告/31_录制格式持久化_受控复测_20261014.md:6` |
| 209 | flash 写入 `videoformat=mov` 后，断电重启会回落为 `mp4`；仅 `ntsc_pal` 真正跨断电持久。 | flash 写入 `videoformat=mov` 后，断电重启会回落为 `mp4`； | `01_研究报告/31_录制格式持久化_受控复测_20261014.md:15` |
| 210 | 该性质经独立实验确认（见 §3.3）。因此只有断电重启后的读回才反映 flash 内容。 | 因此只有断电重启后的读回才反映 flash 内容。 | `01_研究报告/31_录制格式持久化_受控复测_20261014.md:51` |
| 211 | 结论分级 | ✅ = 源码逐行核实；⚠️ = 部分核实或与 README 表述不同；❌ = 官方 app 中不存在。 | `03_解包_APK/com.panasonic.jp.lumixsync/PROTOCOL_AUDIT.md:4` |
| 212 | 2.4 `get_content_info` 的 dir_id 位置（⚠️ 关键修正） |  | `03_解包_APK/com.panasonic.jp.lumixsync/PROTOCOL_AUDIT.md:85` |
| 213 | 2.5 `getprogress`（⚠️ 修正） |  | `03_解包_APK/com.panasonic.jp.lumixsync/PROTOCOL_AUDIT.md:96` |
| 214 | 3.1 `startsenddata` 的 type 白名单（⚠️ 关键） |  | `03_解包_APK/com.panasonic.jp.lumixsync/PROTOCOL_AUDIT.md:124` |
| 215 | 4. 下载 / 文件访问（⚠️ 与 README 表述需修正） |  | `03_解包_APK/com.panasonic.jp.lumixsync/PROTOCOL_AUDIT.md:143` |
| 216 | 文件下载 | ⚠️ 官方走 DLNA 60606；`http://ip/DCIM` 为旁路（§4）。 | `03_解包_APK/com.panasonic.jp.lumixsync/PROTOCOL_AUDIT.md:164` |
| 217 | `get_content_info` | ⚠️ dir_id 在 `value`，不在 `type`（§2.4）。 | `03_解包_APK/com.panasonic.jp.lumixsync/PROTOCOL_AUDIT.md:165` |
| 218 | `getprogress` | ⚠️ 无 type 参数（§2.5）。 | `03_解包_APK/com.panasonic.jp.lumixsync/PROTOCOL_AUDIT.md:166` |
| 219 | 固件上传「解密预言机」攻击（已尝试，负结果） | `oracle/` 里已实现完整四阶段框架（`upload_test.py`），阶段 0（原封 V29 完整上传）已跑通——相机收完全文件后回 `err_critical`，未变砖。结论：上传路径只给一个粗粒度 `err_critical`，无逐字节/逐分片错误反馈、无可用时序差，不是解密预言机；降级保护（旧版本拒刷）得到实证。阶段 2/3（版本+1 上传）有真实变砖风险且换不到密钥，不建议再跑。详见 `oracle/README.md`。 | `03_解包_APK/com.panasonic.jp.lumixsync/README.md:131` |
| 220 | │ ├── README.md # 四阶段方案 + 判定表 + 变砖恢复步骤 |  | `03_解包_APK/com.panasonic.jp.lumixsync/TREE.md:67` |
| 221 | 内建：自动卸载（原始访问前必须）、按卷名+文件系统+容量自动识别设备（卡拔插后节点会变）、 |  | `04_工具与脚本/TOOLS.md:64` |
| 222 | `ptp_attack.py` / `usb_oob.py` | PTP length-DoS 与 USB OOB \| ✓ 可复现挂死（拔插恢复） | `04_工具与脚本/TOOLS_工具箱总览.md:47` |
| 223 | J | 翻一个数据字节：区分「签名覆盖全文件」vs「只覆盖头」 \| 高（可能变砖） | `04_工具与脚本/campaign2/README.md:42` |
| 224 | 高危：翻数据字节（需明确许可后才跑，可能变砖） |  | `04_工具与脚本/campaign2/README.md:64` |
| 225 | Phase J 不自动跑 | 高变砖风险，Phase I 结果明确后需显式放行。 | `04_工具与脚本/campaign2/README.md:75` |
| 226 | 最坏情况（`ok`） | 相机写入改过头部的 V29 并重启，不是变砖（分区代码未变）； | `04_工具与脚本/campaign2/README.md:86` |
| 227 | 未获重现（n=2） | 直写 flash 后断电重启，`ntsc_pal`、`videoformat`、`videoquality` 三项均保留。 | `04_工具与脚本/campaign2/out/S1H_format_persistence.md:58` |
| 228 | ⚠️ 2026-10-13 更正 | 本文写作时以"DC-S5 的 `videoformat` 开机从 mov 回落 mp4"为前提； | `04_工具与脚本/campaign2/out/S1M2_format_field_notes.md:3` |
| 229 | 以分块 `method=separate` 协议直写 flash 后，`videoformat=mov` 在断电重启后保留。 |  | `04_工具与脚本/campaign2/out/S1M2_format_field_notes.md:10` |
| 230 | 安全声明 | `dump`/`fwup`/`fuzz` 模式只发送已验证的只读操作（`0x1001`/`0x1002`/`0x1004`/`0x9104`/`0x9421`/`0x9605`/`0x1003`），且每包 length 精确。绝不发送 `0x9406` 子码（8 个全为带副作用动作：保存/格式化/升级准备/完成/除尘/坏点刷新/升级中止/全量重置）、`0x9422`/`0x9423`（配置写回）、`0x940d`（电源）等任何有副作用的操作。`lenprobe` 模式是受控 DoS 演示（故意发送 length 不… | `04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:7` |
| 231 | `mode=lenprobe` | 受控 length-DoS 演示（主报告 §9.5）。发送 12 字节但头声明 length=0x400 → 相机校验 type 不校验 length 且无超时 → PTP 数据面挂死，拔插 USB 恢复（无写操作、不砖机）。macOS 主机侧（ImageCaptureCore）同样不校验 length，约 60 s 内部超时后返回空响应。只在安全 fuzz 跑完后作为最后一步运行；运行后相机需拔插 USB 才能继续 PTP 通讯。 | `04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:105` |
| 232 | Python 报 `claim_interface 失败 (code=AccessDenied)` | macOS 系统相机栈占用了 PTP 设备 \| 关掉所有相机相关 App → 拔插 USB → 立刻重跑；仍不行就改用原生 `./s5_ptp_dump`（推荐，macOS 上应直接用原生） | `04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:120` |
| 233 | 相机 PTP 接口"挂死"、重连无反应 | length 不匹配会触发（已实机坐实：相机校验 type 不校验 length、无超时；本工具常规模式已杜绝，`lenprobe` 是故意触发） \| 拔插 USB 即可恢复，本机无损（只是接口复位；会话控制面可重建但数据面需重连） | `04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:126` |
| 234 | length 精确 | 松下相机的 PTP 容器解析器只校验 `type` 不校验 `length`。若某次 length 与实发字节数不符，相机会永久等待（无超时）→ PTP 接口挂死，需拔插 USB 恢复（本地 DoS，不能升级为 RCE，不写坏存储）。此行为已于 2026-10-11 受控实机全链条验证（含 macOS 主机侧同样不校验 length，见主报告 §9.5）。两个脚本都在发送前对 length 做断言/精确计算，杜绝此情况。 | `04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:133` |
| 235 | 若相机状态异常，第一时间拔 USB 重插，不要反复对挂死的接口发数据。 |  | `04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md:135` |
| 236 | ⚠️ SoftAP 只在 BLE 会话保持期间或相机主动开启「遥控拍摄」时才在线。 |  | `04_工具与脚本/s5_monitor/README.md:61` |
| 237 | ⚠️ 两条关键协议行为（都是踩坑踩出来的） |  | `04_工具与脚本/s5_monitor/README.md:196` |
| 238 | 变焦（长焦/广角） | `camctrl?type=focus&value=tele-normal` `…tele-fast / wide-normal / wide-fast / focus-stop` \| ⚠️ `focus` 是变焦，不是对焦！ 这是最容易搞错的一条 | `04_工具与脚本/s5_monitor/README.md:255` |
| 239 | 拖动对焦 | `camctrl?type=touch_trace&value=…` \| ⚠️ 本机实测仍 `err_param`，格式待定 | `04_工具与脚本/s5_monitor/README.md:260` |
| 240 | 0.92 | 16.1 \| 0 \| ⚠️ 仍垫帧 54 次 | `04_工具与脚本/s5_monitor/README.md:373` |
| 241 | ⚠️ 最重要的一条使用纪律 | 不要重启服务 | `04_工具与脚本/s5_monitor/README.md:444` |
| 242 | ① 相机【断电重启】（清掉 invalid login 状态） | 这一步不可省 | `04_工具与脚本/s5_monitor/README.md:505` |
| 243 | 相机提示 invalid login 后，只能靠断电重启恢复 |  | `04_工具与脚本/s5_monitor/README.md:536` |
| 244 | 相机【刚断电重启】+ 首次授权成功（accctrl 首字段 = ok） |  | `04_工具与脚本/s5_monitor/README.md:554` |
| 245 | 需要触摸对焦时 | 先断电重启相机 → 启动本工具 → 立刻使用（窗口期内） | `04_工具与脚本/s5_monitor/README.md:566` |
| 246 | ⚠️ 第 0 步（必须先做） | 重启相机 | `04_工具与脚本/s5_monitor/设置枚举测试计划.md:7` |
| 247 | 当前相机已经被反复测试打到 `startstream | err_busy`（会话/资源卡死），必须先断电重启： | `04_工具与脚本/s5_monitor/设置枚举测试计划.md:9` |
| 248 | 基线（未改任何设置） 0/12 26.2 0 0 0 0 ⚠️ 控制面 0/12 |  | `04_工具与脚本/s5_monitor/设置枚举测试计划.md:91` |
| 249 | ⚠️ 本包含会写相机存储卡的工具。使用前请读 | ⚠️ 本包含会写相机存储卡的工具。 | `11_DC-S5成果包_20261013/00_成果总结_全文.md:5` |
| 250 | 成果 | 把 NTSC + MOV + `mov_60p_150mbps_c4k` 持久化写入相机（`0x5e=0x06`、vq `0x92`），断电重启后仍生效 | `11_DC-S5成果包_20261013/00_成果总结_全文.md:24` |
| 251 | 7 | 退出/复位组合键：`MENU/SET + 方向右` 关机 → 进入 INITIAL SETTINGS → 再按一次完成重置。⚠️ 必须先拔掉 ROM BACKUP 卡（槽1/FAT32）否则不生效 \| 实机 | `11_DC-S5成果包_20261013/00_成果总结_全文.md:39` |
| 252 | ⚠️ 禁令 | 在 `INITIAL SETTINGS` 界面不要按 `DISP.` —— 会解除 `[Strict]`， | `11_DC-S5成果包_20261013/00_成果总结_全文.md:42` |
| 253 | 使地区后缀变成可改（仅一次机会、不可逆）。 |  | `11_DC-S5成果包_20261013/00_成果总结_全文.md:43` |
| 254 | "长名崩溃 = 数量 × 长度" | ⚠️ 修正 \| 初版实验里我们自己的工具把目录链拐进了照片数据区；重做后结论为 "长文件名本身" | `11_DC-S5成果包_20261013/00_成果总结_全文.md:66` |
| 255 | SD.DAT 恢复模式 | ⚠️ 降级为后备胎（项目判定"有砖机史、不可逆"） | `11_DC-S5成果包_20261013/00_成果总结_全文.md:115` |
| 256 | 6. ⚠️ 风险事件记录（本轮） |  | `11_DC-S5成果包_20261013/00_成果总结_全文.md:132` |
| 257 | 卡片可完全恢复（重新格式化）；相机未做任何不可逆修改 | 相机未做任何不可逆修改 | `11_DC-S5成果包_20261013/00_成果总结_全文.md:167` |
| 258 | ⚠️ 本包含会写相机存储卡的工具。使用前必读 | ⚠️ 本包含会写相机存储卡的工具。 | `11_DC-S5成果包_20261013/README.md:5` |
| 259 | ⚠️ 退出前提 | 必须先拔掉 ROM BACKUP 卡（槽1/FAT32） | `11_DC-S5成果包_20261013/README.md:65` |
| 260 | ⚠️ 绝对禁令 | 不要按 `DISP.`（会解除 `[Strict]`，解锁地区后缀一次性写入） | `11_DC-S5成果包_20261013/README.md:66` |
| 261 | 卡片可完全恢复（重新格式化）；相机未做任何不可逆修改 | 相机未做任何不可逆修改 | `11_DC-S5成果包_20261013/README.md:73` |
| 262 | 相机提示 `invalid login` 时，只能给相机断电重启（拔电池 10 秒） |  | `12_S5无线监看_v1.0_20261014/README.md:64` |
| 263 | 任何有副作用或不可逆的命令。 |  | `12_S5无线监看_v1.0_20261014/README.md:101` |
| 264 | ⇒ 必须断电重启相机（只能这样恢复） |  | `12_S5无线监看_v1.0_20261014/README.md:218` |
| 265 | ❌ 危险 | 不带 value（UUID）的 req_acc 会留下匿名 pending， | `12_S5无线监看_v1.0_20261014/README.md:234` |
| 266 | ① 相机断电重启（拔电池几秒再上电） | 这一步不可省 | `12_S5无线监看_v1.0_20261014/README.md:246` |
| 267 | ⚠️ 回放模式下没有实时取景（DLNA 内容与取景流互斥）。 |  | `12_S5无线监看_v1.0_20261014/README.md:352` |
| 268 | ⚠️ 相册与取景互斥（卡顿的真相） |  | `12_S5无线监看_v1.0_20261014/README.md:358` |
| 269 | `s5_get_photo.py` 会自动判定并在不匹配时警告。 |  | `12_S5无线监看_v1.0_20261014/README.md:445` |
| 270 | ⚠️ 重要注意事项 |  | `12_S5无线监看_v1.0_20261014/使用说明.md:65` |
| 271 | 相机变得不响应 | 停手等 30 秒；仍不行 ⇒ 相机断电重启 | `12_S5无线监看_v1.0_20261014/使用说明.md:128` |
| 272 | 服务启动报 `err_busy` | 相机侧有残留会话 ⇒ 相机断电重启 | `12_S5无线监看_v1.0_20261014/使用说明.md:129` |
| 273 | 固件升级、格式化、重置、关机、配置上传等任何有副作用/不可逆的命令。 |  | `12_S5无线监看_v1.0_20261014/使用说明.md:155` |
| 274 | ⚠️ 为什么不能让我（远程协助）来测 | Mac 一连上相机热点 `S5-XXXXXX`， | `12_S5无线监看_v1.0_20261014/连热点时怎么测.md:3` |
| 275 | ⚠️ 相机强制单流会话 | 上次没 `stopstream` 干净关闭，新的 `startstream` 会返回 | `12_S5无线监看_v1.0_20261014/附_技术参考.md:26` |
| 276 | ⚠️ 最容易搞错的一条 |  | `12_S5无线监看_v1.0_20261014/附_技术参考.md:81` |
| 277 | 🔴 血泪教训 | `req_acc` 绝不能高频重发 | `12_S5无线监看_v1.0_20261014/附_技术参考.md:139` |
| 278 | ⇒ 只能靠断电重启恢复。 |  | `12_S5无线监看_v1.0_20261014/附_技术参考.md:153` |
| 279 | `startstream → err_busy` | 相机侧有残留流会话 \| 相机断电重启 | `12_S5无线监看_v1.0_20261014/附_技术参考.md:181` |
| 280 | 相机提示 `invalid login` | `req_acc` 被高频重发 \| 相机断电重启 | `12_S5无线监看_v1.0_20261014/附_技术参考.md:182` |
| 281 | ⚠️ 对外分发本包前必须脱敏这一串。 |  | `13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md:51` |
| 282 | ⚠️ 更正记录 | 我曾据 Tether 反汇编推断"`0x2374` 是 S5 的目标模式"，这是错的， | `13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md:90` |
| 283 | 4.2 ⚠️ 一个必须写在前面的大坑 |  | `13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md:118` |
| 284 | —— `SD*→DSC`（写回）、`ADJFLAG→ALL F`、`WBADJ→STEPMODE` 都可能造成不可逆后果 |  | `13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md:239` |
| 285 | [ 3] 0000000000000000000XJL########15 (raw 66 bytes) ← ⚠️ 机身 ID，对外分发需脱敏 |  | `13_USB服务通道勘察_交接包_20261014/01_实测记录.md:79` |
| 286 | ⚠️ 与历史记录的矛盾（需承接人复核） |  | `13_USB服务通道勘察_交接包_20261014/01_实测记录.md:194` |
| 287 | ⚠️ 旧的 `s5_ptp_raw.c` 写的是 `for (cfg = 1; ...)`，会漏掉配置 0，同一 bug 请勿再犯。 | ⚠️ 旧的 `s5_ptp_raw.c` 写的是 `for (cfg = 1; | `13_USB服务通道勘察_交接包_20261014/02_工具/README.md:32` |
| 288 | —— 只影响当前会话，拔插 USB 即恢复 |  | `13_USB服务通道勘察_交接包_20261014/02_工具/README.md:120` |
| 289 | ⚠️ 踩坑提醒 | `grep 0x2370` 会命中 `adrp x3, 411 ; 0x237000` 这类地址页引用。 | `13_USB服务通道勘察_交接包_20261014/03_Tether协议线索.md:124` |
| 290 | ⚠️ 三条必须遵守 |  | `13_USB服务通道勘察_交接包_20261014/README.md:63` |
| 291 | —— `SD*→DSC`（写回）、`ADJFLAG→ALL F`、`WBADJ→STEPMODE` 都可能不可逆 |  | `13_USB服务通道勘察_交接包_20261014/README.md:68` |
| 292 | USB 被工具 `Seize` 抢走 | 拔插一次即恢复 | `13_USB服务通道勘察_交接包_20261014/README.md:79` |
| 293 | 最危险的问题 | 已被项目自己撤回的错误判据（"相机报写入错误 ⇒ 内存写已执行"）仍活在工具代码的运行路径里，并在 09 号包的 7.3 MB 压缩包中成体系对外分发；普通 grep 永远扫不到。 | `14_总包审计与新方向_20261014/00_审计总报告.md:16` |
| 294 | 现象：报告 31 声称"写入 `ntsc + mov + 0x9b` 后断电重启三项均保留（T1/T2）"，并把 §3.2 称为"写入确已落地的验证"。但该报告 §7 自己列出的证据文件显示，写入 payload 与写入前备份为同一份文件。 | 现象：报告 31 声称"写入 `ntsc + mov + 0x9b` 后断电重启三项均保留（T1/T2）"，并把 §3.2 称为"写入确已落地的验证"。 | `14_总包审计与新方向_20261014/00_审计总报告.md:71` |
| 295 | "256KB 真实 keystream" | 同上 :12,77 \| ⚠️ `ks=ct⊕pt`，pt 全零 ⇒ ks 就是密文；仅 CTR 下才是 keystream | `14_总包审计与新方向_20261014/00_审计总报告.md:139` |
| 296 | "130k+ 探测" | `00-总评估:85` \| ⚠️ 实为 S1M2（MC8243）的 132,360 次试验，且原文自己声明"不是对密钥空间的穷举" | `14_总包审计与新方向_20261014/00_审计总报告.md:141` |
| 297 | `persist.py:406,446` | `abortsenddata` 返回值未检查 → 失败时相机可能残留 send 会话（项目文档明确"残留会话需断电重启"） | `14_总包审计与新方向_20261014/00_审计总报告.md:251` |
| 298 | `exfat_patch.py` / `exfat_spray.py` 0 个交互确认（grep `input(`/`--confirm` 无命中）；`go2` 只打印警告就直写 `/dev` 原始块设备（` | 82` `open(path,"r+b")`）。 | `14_总包审计与新方向_20261014/00_审计总报告.md:271` |
| 299 | 不校验命令行传入的设备是否为目标卡（`detect_lumix_exfat` 只用于拔插后重识别，`s5_exfat_test.sh | 156-160`）⇒ 传错一张 exFAT 卷会被直接改写。 | `14_总包审计与新方向_20261014/00_审计总报告.md:272` |
| 300 | UPD 容器结构：512B 头 + 64B 逐版本互异高熵字段@0x220 + 48×92B 分区表 + 512B 尾块 | `FIRMWARE_FORMAT.md`；审计复算表步长/偏移一致。⚠️ 该 64B 与 512B 是不是「ECDSA P-256 签名」与「RSA-4096 签名」——无正面依据（见 §3 下方补充） | `14_总包审计与新方向_20261014/00_审计总报告.md:470` |
| 301 | PTP length-DoS：可复现挂死、拔插恢复、不砖机 | `S5_AES…:484-499`（单次受控，n=1） | `14_总包审计与新方向_20261014/00_审计总报告.md:483` |
| 302 | ⚠️ 补充（2026-10-14 由 `07_签名与密钥恢复` 线程裁决） | 签名类结论的前提已被上游自我撤回 | `14_总包审计与新方向_20261014/00_审计总报告.md:487` |
| 303 | ⚠️⚠️ 重大更正（2026-10-14 复核） | 这棵树是另一台相机的。项目自己的英文稿 `S5_RE_Project_Summary_EN.md:92` 给出的下载 URL 是 | `14_总包审计与新方向_20261014/00_审计总报告.md:561` |
| 304 | 未逐行通读约 70 个 campaign2 脚本（精读约 25 个核心文件 + grep 危险模式扫描），故"未提及"不等于"已确认安全"。 |  | `14_总包审计与新方向_20261014/00_审计总报告.md:674` |
| 305 | 危险操作清单（看哪些脚本会写设备且没有 --confirm） |  | `14_总包审计与新方向_20261014/02_全包查看指令手册.md:355` |
| 306 | ⚠️ 限定 | 树中无任何 `DC-S5`/`LUMIX` 字样，机型绑定关系从未被验证 ⇒ 不能据此断定实机没有 F1/F2。 | `14_总包审计与新方向_20261014/02_全包查看指令手册.md:398` |
| 307 | ⚠️ | 项目自己标注的"待验证假设" | `14_总包审计与新方向_20261014/02_全包查看指令手册.md:447` |
| 308 | ⚠️ 勘误（2026-10-14，由 `06_密码学重跑` 线程指出并实测证实） | 本节早先版本写作「CBC 且明文全零 ⇒ 所有密文块必须相同」，这是错的——"块全同"是 ECB + 常量明文的指纹；CBC + 全零明文是迭代链 `C_i = E_K(C_{i-1})`，块基本全不同。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:271` |
| 309 | 机型绑定 | ⚠️ 树中无任何 `DC-S5`/`LUMIX` 字样；项目从 "DC-FZ1K2 页"取得却称其为"DC-S5 的内核源码"——从未验证 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:306` |
| 310 | ⚠️ 风险 | 若让 Tether 真刷，有砖机风险。抓到 `startsenddata` 即止。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:386` |
| 311 | ⛔ 绝对不要按 DISP. | 13:247-248 会解除 [Strict]，地区后缀一次性锁死，不可逆。 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:408` |
| 312 | 步 4：堆控 | 仅当步 3 阳性才做 \| 🔴 高 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:648` |
| 313 | 顺序很重要（避免不可逆动作先行） |  | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:666` |
| 314 | 4 | 23. 拆机 + UART/JTAG \| 硬件工具 \| 🔴 不可逆拆机 \| 运行时明文 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:718` |
| 315 | 4 | 26. chip-off / 侧信道 \| LAB \| 🔴 高成本 \| 密钥本身 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md:721` |
| 316 | ⚠️ 需注意 token 之别 | 幽灵档是 `c4k` 变体（0x8b 家族），而当前激活档是 `4k` 变体（`0x9b`，已在 allmenu 声明）。二者是不同 token，讨论"菜单变灰"时必须区分。 | `14_总包审计与新方向_20261014/05_相机只读快照_20261014/README.md:44` |
| 317 | 14 | 130k+ 离线探测 0 命中 \| `00-总评估:85` \| ⚠️ 未重跑（不在本次范围） \| 审计已定性为 S1M2（MC8243）的 132,360 次试验，项目自己也声明"不是对密钥空间的穷举" | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:335` |
| 318 | 统计：❌ 推翻 4 条（#1、#3、#5、#6）｜◐ 降级/需进一步实验 4 条（#4、#11、#12、#13）｜✅ 维持 5 条（#2、#7、#8、#9、#10）｜⚠️ 范围外 1 条（#14）。 |  | `14_总包审计与新方向_20261014/06_密码学重跑/结论.md:337` |
| 319 | ⚠️ 一个新细节（有实际后果） | 幽灵档是 `c4k` 变体，而当前激活档是 `4k` 变体（`0x9b`，已在 allmenu 声明）。二者是不同 token。 | `14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md:42` |
| 320 | ⚠️ 可信度声明 | 本环境的 `web_fetch` 被 DNS 过滤全面阻断（所有域名解析到非公网地址），因此上述页面正文未被直接读取，结论来自多个独立手册站的索引标题交叉一致。 | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:62` |
| 321 | ⚠️ 拔插 SD 卡必须在相机里正常关机后（项目红线 `25 | 20`）：相机分配位图延迟写回，直接拔卡会让位图停在旧状态。 | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:125` |
| 322 | ⚠️ 项目记载 64 GB 及以上 exFAT 卡在机身某些功能上会受限（ROM BACKUP 即因文件系统变灰，`13 | 182-191`）。若 LUT 读入失败，先换 FAT32 卡试。 | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:126` |
| 323 | ⚠️ 诚实标注 | DC-S5 完整版说明书的 PDF 是松下私有加密（VCIS，非标准 RC4/AES），三次密钥派生尝试均失败 ⇒ S5 手册只能给到页码级；段落原文用措辞完全一致的 S5M2 官方手册代替（同一功能名 `[V-Log View Assist]`）。因此「初代 S5 能否加载自定义 `.VLT`」属高度可能但未逐字确证。 | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:262` |
| 324 | ⚠️ 需自行验证的约束 | S5 的 HDMI 输出规格（分辨率/帧率/位深）与外录能力的匹配；以及 S5M2 手册明确写了"在 `[Photo Style]` 画质调整里套 LUT 时，`[LUT View Assist]` 不可用"——两套机制互斥，S5 需实测。 | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:348` |
| 325 | ⚠️ 注意 | `ffmpeg` 的 `lut3d` 滤镜支持 `.cube/.3dl/.dat/.m3d`，不支持 `.vlt` ⇒ 可用来离线"验证套用效果"，但不能直接产出 `.vlt`。 | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:384` |
| 326 | 存储卡 | ⚠️ 当前未挂在 Mac 上（`/Volumes/` 只有 `Macintosh HD` / `Recovery`）⇒ 需从相机取卡用读卡器 | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:392` |
| 327 | 卡文件系统 | ⚠️ 未知。FAT32 卡文件名 ≤8 字符；exFAT 卡 ≤255 字符。若用长名而卡是 FAT32，机身可能读不到 | `14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md:393` |
| 328 | ⚠️ 本轮的操作教训（务必记住） | 我用自造 UUID 发起了 `req_acc`， | `14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:120` |
| 329 | 项目 `25_操作记录与风险手册` 早已警告 | 切勿反复重试 `req_acc`，会被判为异常 App。 | `14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:123` |
| 330 | ⇒ invalid login ⇒ 需要断电重启。这是相机的自我保护，不是漏洞。 | ⇒ invalid login ⇒ 需要断电重启。 | `14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md:275` |
| 331 | 最危险的一条 | 已撤回的判据"相机报错 ⇒ 内存写已执行"仍活在工具代码的运行路径里（`exfat_patch.py:535` 等），并在 09 号包的 7.3 MB zip 中成体系对外分发——普通 grep 永远扫不到。 | `14_总包审计与新方向_20261014/README.md:17` |
| 332 | 未逐行通读约 70 个 `campaign2` 脚本（精读约 25 个核心文件 + grep 危险模式扫描） | 未提及不等于已确认安全。 | `14_总包审计与新方向_20261014/README.md:50` |
| 333 | 方向 7（证据链修复） | 🟢 对相机零风险 \| 但会改/删既有文件（重构 MANIFEST、删 09 zip、回灌 25/26 副本）；删 zip 与覆盖 MANIFEST 不可逆，建议二次确认 | `14_总包审计与新方向_20261014/README.md:120` |
| 334 | ⚠️ 注意 | 本机 `photostyle=standard`（实测），V-Log 需在拍摄时主动选中。没拍 V-Log 的素材不要套这个 LUT（见 §4）。 | `15_LUT烧录工具_20261014/README.md:25` |
| 335 | 风格自检 | 先判断素材是不是 Log，若不是会警告（`--skip-normal` 可直接跳过） | `15_LUT烧录工具_20261014/README.md:112` |
| 336 | ⚠️ 踩过的坑（血泪） |  | `16_S5_核心总包_20261015/09_对外分享/小红书帖_S5逆向进度_20261014.md:61` |
| 337 | 以及一个健壮设置器（退避重试 + 回读校验 + 危险档拦截）。 |  | `16_S5_核心总包_20261015/09_对外分享/小红书帖_S5逆向进度_20261014.md:69` |
| 338 | - 2026-10-14 受控复测（n=2） | 上述改判未被重现。写入 `ntsc + mov + 0x9b` 后断电重启， | `16_S5_核心总包_20261015/README.md:27` |
| 339 | 「写完立刻回读」不能作为持久化判据，只有断电重启后的读回才反映 flash 内容。 |  | `16_S5_核心总包_20261015/README.md:32` |
| 340 | （唯一未测公开 CVE-2019-5096）；唯一实机漏洞 = PTP length-DoS（可复现挂死、拔插恢复、不砖机）。 | 唯一实机漏洞 = PTP length-DoS（可复现挂死、拔插恢复、不砖机）。 | `16_S5_核心总包_20261015/README.md:43` |
| 341 | 写入 `ntsc + mov + 0x9b` 后断电重启三项均保留（n=2）；`videoquality` 与开机时 SD 卡槽 1 的 | 写入 `ntsc + mov + 0x9b` 后断电重启三项均保留（n=2）； | `16_S5_核心总包_20261015/README.md:50` |
| 342 | 隐藏格式持久化 | 直写 flash 的 65533 字节 blob 后断电重启，`ntsc_pal`、`videoformat`、 | `16_S5_核心总包_20261015/README.md:82` |
| 343 | PTP length-DoS | 唯一可复现挂死 | `16_S5_核心总包_20261015/README.md:93` |
| 344 | SD.DAT 降级为 JTAG 之后的备胎（S1R2 教训 | 无只读模式、NAND 未验证、写错 pardata = 不可逆砖） | `16_S5_核心总包_20261015/README.md:117` |
| 345 | 3) 健壮设置器（退避重试 + 回读校验 + 危险档拦截），仅写 RAM |  | `16_S5_核心总包_20261015/README.md:134` |
| 346 | ⇒ 只能断电重启相机。本程序启动时只发一次，切勿反复重启程序。 | ⇒ 只能断电重启相机。 | `16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/README.md:83` |
| 347 | 恢复流程（出现 invalid login 时） | 断电重启相机 → 确认 | `16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/README.md:90` |
| 348 | ⚠️ 已撤回 | `0x220` 的 64B 不得再称为"ECDSA P-256 签名"。 | `17_SD引导路线_20261015/离线验证大任务书_给同事.md:25` |
| 349 | 风险 | 不可逆拆机；只读操作本身低风险 | `18_G100明文与同类项目_20261015/破解AES的路径清单_20261015.md:70` |
| 350 | 三、不可移植清单（严禁套用） |  | `18_G100明文与同类项目_20261015/索尼方法论_单独提取.md:49` |
| 351 | ⚠️ 竞需纠偏 | 这不等于"不同节用了不同密钥" | `18_G100明文与同类项目_20261015/群问题解答_密钥流与AES_20261015.md:37` |
| 352 | ⚠️ 两处需要精确化 |  | `18_G100明文与同类项目_20261015/群问题解答_密钥流与AES_20261015.md:76` |
| 353 | T3 结构比对 | ⚠️ 推翻"512B 明文头" \| 实测确认 \| `T3_启动链结构比对.md`（新撤回 R6） | `18_SDDAT验证/00_总览.md:8` |
| 354 | T4 构建校准 | ⚠️ Stubby 可构建 / SD loader 无源码 \| 实测确认 \| `T4_构建校准.md`（3 处补丁 + 产物 18,648B） | `18_SDDAT验证/00_总览.md:9` |
| 355 | ⚠️ 发现的细节（结论库细化，非失败） |  | `18_SDDAT验证/T0_环境校准.md:21` |
| 356 | 判定：⚠️ 任务目标部分不可达——SD loader（SD.DAT）在本仓库中无源码； |  | `18_SDDAT验证/T4_构建校准.md:3` |
| 357 | T3 结构比对 | ⚠️ 推翻一条 \| "512B 明文头"是旧偏移产物（R6）；容器零明文代码区 | `18_SDDAT验证/T5_综合裁决.md:14` |
| 358 | T4 构建校准 | ⚠️ 部分不可达 \| Stubby 可构建；SD loader 无源码，只能逆向或从零写 | `18_SDDAT验证/T5_综合裁决.md:15` |
| 359 | （`dlna_text.asm`、`funcs.tsv`（1398 个函数）、`danger_map.txt`（每个危险 libc 调用点 | 所属函数）、`dlna_vma_strings.txt`、`tools/`） | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:7` |
| 360 | 函数 | 危险调用点 \| 源 \| 结论 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:367` |
| 361 | 21 个头处理函数中的 17 个 | — \| 见 §4.4，"只写标志/只比较/只写 1 字节"，没有任何危险调用（`tools/sites.py 0xd66e8 0xd7b2c` 全量扫描只报出 5 个调用点） | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:424` |
| 362 | E9 | 21 个头处理函数中的 17 个 \| 任意 \| `tools/sites.py 0xd66e8 0xd7b2c` 全量扫描：只有 5 个危险调用点（Accept×2、Host、contentFeatures、Content-Type） | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:440` |
| 363 | 全部 21 个头处理函数里的危险调用点（应只报 5 处） |  | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md:495` |
| 364 | A2 逐动作解析器 | 危险调用为零 | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:48` |
| 365 | 危险调用统计 | memcpy 289 · memset 14 · strcpy 6 · strncpy 3 · sprintf 2 | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:100` |
| 366 | B4 XML 解析器主体（`0x82348`–`0x90d0c`） | 危险调用类在构造上不存在 | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:251` |
| 367 | 危险调用（strcpy/strcat/memcpy/sprintf/strncpy/malloc/realloc） | 0 条 | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:257` |
| 368 | `0x9e1a4` / `0x9ebfc`（SSDP 入站）内部逻辑 | 上一份报告只确认了它们没有危险调用，未逐行审计 `MX:`/`ST:`/`MAN:` 的取值路径。 | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:420` |
| 369 | 任务 A | 动作解析器无危险调用 | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md:437` |
| 370 | `0x9d640` | 0x9d3f4（512 B） \| `fp-268` \| 268 B \| `ctx+0x188+148·i` \| ⚠️ 源>267 B 才越界 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:146` |
| 371 | `0x9d888` | 0x9d3f4（512 B） \| `fp-408` \| 408 B \| `ctx+0x628+148·i` \| ⚠️ 需源>407 B | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:148` |
| 372 | `0x9d8b4` | 0x9d3f4（512 B） \| `fp-488` \| 488 B \| `ctx+0x668+148·i` \| ⚠️ 需源>487 B | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:149` |
| 373 | `0x9dd70` | 0x9db20（504 B） \| `fp-268` \| 268 B \| `ctx+0x188+148·i` \| ⚠️ | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:150` |
| 374 | `0x9dfb8` | 0x9db20（504 B） \| `fp-404` \| 404 B \| `ctx+0x628+148·i` \| ⚠️ | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:152` |
| 375 | `0x9dfe4` | 0x9db20（504 B） \| `fp-484` \| 484 B \| `ctx+0x668+148·i` \| ⚠️ | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:153` |
| 376 | `0x9ee44` | 0x9ec04（600 B） \| `fp-196` \| 196 B \| `ctx+0x188+148·i` \| ⚠️ | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:154` |
| 377 | `0x9ee6c` | 0x9ec04（600 B） \| `fp-288` \| 288 B \| `ctx+0x188+148·i` \| ⚠️ | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:155` |
| 378 | `0x9f084` | 0x9ec04（600 B） \| `fp-420` \| 420 B \| `ctx+0x628+148·i` \| ⚠️ | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:156` |
| 379 | `0x9f0b0` | 0x9ec04（600 B） \| `fp-500` \| 500 B \| `ctx+0x668+148·i` \| ⚠️ | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:157` |
| 380 | `0x9f2c4` | 0x9ec04（600 B） \| `fp-196` \| 196 B \| `ctx+0x188+148·i` \| ⚠️ | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:158` |
| 381 | `0x9f348`/`0x9f52c` | 0x9ec04（600 B） \| `fp-580` \| 580 B \| — \| ⚠️ | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md:159` |
| 382 | ⚠️ 范围界定的一处诚实说明 | `0x9a740` 与 `0x9e1ac` 的 `sub sp, sp, #N` 之后紧跟 `str r0/r1/r2/r3, [fp, #-…]` 的无 `push {fp, lr}` 形态（`0x9a740: sub sp,sp,#72`、`0x9e1ac: sub sp,sp,#504`），与本次二进制内多处函数（如 `0x9d3ec`、`0xefb28`、`0xda308`）一致。这意味着它们的实参由调用方帧传递（例：`0x9a740` 用到 `fp-2460`，远超其 72 B 帧）。因此下文对"缓冲大小… | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:39` |
| 383 | `0x0afd00` `memcpy(dst=[fp+24], …, 12)` | 12 B 立即数 \| 目的地是调用方传入的指针（`[fp+24]`）。长度是常量 12，故只有"目的地 < 12 B"才危险；该目的地由调用方提供，不在本子树内定义 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:169` |
| 384 | U1 | 3 处调用方帧目的地的容量（`0xafd00` / `0x0aff68` / `0x0adbb0` 的源） \| [未判定]：长度均为立即数（12 / 常量 / 212），故仅当"调用方提供的目标/源 < 该常量"才危险；这些目标不在本子树内定义。建议：在 `0xaf958` / `0xafd54` / `0xadabc` 的 9 个调用点上逐个核对实参缓冲 \| — | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md:263` |
| 385 | `danger_map.txt` | 每个危险 libc 调用点 → 所属函数 + 该函数的字符串/文件归属 | `19_路径1_Linux侧攻击面_20261015/dlna_audit/BRIEFING.md:24` |
| 386 | `0x9e1a4` / `0x9ebfc`（SSDP 入站）内部取值路径逐行审计（已知无危险 libc 调用）。 |  | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md:356` |
| 387 | 〇·零、⚠️ 本报告最重要发现（取代前一版结论） | 二进制内静态链接了完整版 Expat | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:11` |
| 388 | ⚠️ 因此 | 以下风险必须重新评估（我第一版的"已排除"是错的） | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:78` |
| 389 | 5. 找到候选 bug 了吗？ | ⚠️ 结论已改变。 封装层写入收敛（§1.3 成立），但发现二进制静态链接 Expat 2.0/2.1 世代并直接解析网络输入 ⇒ CVE-2016-0718（≤2.1.0 堆溢出 / RCE）的适用性必须逐条核对，这是本次审计的最高优先级待办。此外 Billion Laughs（DoS）与 XXE（文件读 / SSRF）的代码路径均存在 \| Expat 存在 [实测]；CVE 适用性 [弱推断] | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:103` |
| 390 | ⚠️ 修正 | 下面 A/B/C/D 四段是Expat 之上的一层薄封装（`upp_av_xml_*` 的 schema 遍历逻辑），不是自研解析器。真正的解析器是静态链接的 Expat（见 §〇·零）。这些封装在写入侧确实有界（下文证据有效），但它们没有过滤 DTD / 实体 / 外部实体，所以不能用它们的有界性推断 XML 解析整体安全。 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:176` |
| 391 | ⚠️ 不确定性（必须声明） | 我无法静态确定精确版本号——二进制内没有 `expat_x.y.z` 版本字符串，`XML_ErrorString` 的指针表是运行时构造的（在 `.rodata` 内搜不到指向 0xff500–0xff840 区间的指针数组，故无法用表格长度反推版本）。因此本判定是"脆弱签名不存在"的否定式证明，而非"版本 ≥2.2.0"的肯定式证明。若该构建是基于被选择性回移的源码树，理论上仍可能有未回移的其它 Expat CVE——但那需要逐 CVE 的签名匹配，不在本次范围 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:633` |
| 392 | ⚠️ 声明 | 条件 2（`XML_SetParamEntityParsing`）未确认。若宿主在运行时设置为 ALWAYS，则"内部实体膨胀 DoS"成立；"外部实体读文件"仍因缺 I/O 回调而不成立 | `19_路径1_Linux侧攻击面_20261015/dlna_控制点解析面_源字段追踪.md:682` |
| 393 | `PsmEvt_RemoteLiveViewReceiveAudio` | `0x39fa8` \| `strcpy` @ `0x3a04c` + `system` @ `0x3a068` / `0x3a0ac` \| 栈 `sp+1512`，帧 2536 B \| 危险但不可达：该函数在整份 `.text` 中无 `bl` 调用者，且 `system()` 的实参由相机应答里的 HTTP 头 `Content-Disposition`/`Content-Type` 拼接（`sprintf("%s > %s")`）；判定为"消息分发器驱动的内部路径"，非 HTTP 直控 | `19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:491` |
| 394 | `triage.py` | 按栈帧大小 × 危险 sink 数量的函数排序 | `19_路径1_Linux侧攻击面_20261015/psm_命令参数审计.md:571` |
| 395 | ⚠️ 教训 E1-1 | `req_acc_can` 是【取消】不是【状态查询】 | `19_路径1_Linux侧攻击面_20261015/实验记录_与教训_20261015.md:16` |
| 396 | 恢复：需要相机端重新授权（app 连接）或断电重启。 |  | `19_路径1_Linux侧攻击面_20261015/实验记录_与教训_20261015.md:26` |
| 397 | ⚠️ 死代码函数 `0x111a4` | `sprintf(sp, "http://%s:%s/", SERVER_NAME, SERVER_PORT)` 入 132 字节栈帧、零检查 —— 调用图为空，不可达 | `19_路径1_Linux侧攻击面_20261015/阶段A2_审计汇总_20261015.md:42` |
| 398 | `PsmEvt_ElcTestFunction`（工厂测试） | 消息含 `>` 即 `system(消息)` \| 消息数据 \| 🔴 不可达（见下） | `19_路径1_Linux侧攻击面_20261015/阶段A2_审计汇总_20261015.md:63` |
| 399 | 五、⚠️ 需要你授权的边界验证 |  | `19_路径1_Linux侧攻击面_20261015/阶段A2_活体指纹_20261015.md:101` |
| 400 | 疑似后门 | ⚠️ `PsmEvt_ElcTestFunction`（消息含 `>` 即执行） | `19_路径1_Linux侧攻击面_20261015/阶段A_Linux攻击面测绘_20261015.md:17` |
| 401 | 导入的危险函数 | `strcpy`×1、`sprintf`×2、`strncpy`×1、`memcpy`×10；无 system/popen | `19_路径1_Linux侧攻击面_20261015/阶段A_Linux攻击面测绘_20261015.md:44` |
| 402 | 死代码里的漏洞 | ⚠️ 函数 `0x111a4`：`sprintf(sp, "http://%s:%s/", SERVER_NAME, SERVER_PORT)` 入 132 字节栈帧、零长度检查 —— 但调用图为空（不可达），是编译遗留 | `19_路径1_Linux侧攻击面_20261015/阶段A_Linux攻击面测绘_20261015.md:50` |
| 403 | `PsmEvt_MngExeCmdChkResult` | popen×1 \| `popen(参数命令, "r")` + `fgets` 读输出 \| ⚠️ 执行命令并回读结果 | `19_路径1_Linux侧攻击面_20261015/阶段A_Linux攻击面测绘_20261015.md:74` |
| 404 | `PsmEvt_MngIpSettingEnable` | system×3 \| `ifconfig %s %s netmask %s` / `route add default gw %s` / `/usr/pvc/bin/ipdiagDup %s %s` \| ⚠️ IP/掩码/网关字符串拼接 | `19_路径1_Linux侧攻击面_20261015/阶段A_Linux攻击面测绘_20261015.md:75` |
| 405 | `PsmEvt_MngIpSettingDisable` | system×2 \| `ifconfig %s %s` \| ⚠️ 同上 | `19_路径1_Linux侧攻击面_20261015/阶段A_Linux攻击面测绘_20261015.md:76` |
| 406 | `PsmEvt_ElcTestFunction` 的执行线程 | system×2 \| `/tmp/%s` 与 `%s > %s` \| 🔴 见 4.3 | `19_路径1_Linux侧攻击面_20261015/阶段A_Linux攻击面测绘_20261015.md:81` |
| 407 | 4.3 🔴 疑似工厂测试后门 | `PsmEvt_ElcTestFunction` | `19_路径1_Linux侧攻击面_20261015/阶段A_Linux攻击面测绘_20261015.md:83` |
| 408 | strcpy(cmd, msg+24) ← ⚠️ 无界 strcpy |  | `19_路径1_Linux侧攻击面_20261015/阶段A_Linux攻击面测绘_20261015.md:97` |
| 409 | 「写全 13 槽（`06 ×13`）」为推荐修法 | ⚠️ 已修订：相机自身行为为仅写槽 0；全槽写与重启回退存在观测相关（反例 n=1 / 正例 n=2），因果未确立 | `REPO_CONTENTS.md:65` |
| 410 | ⚠️ `04_工具与脚本/campaign2/` 与 `06_数据与证据/` 中含有会写相机存储卡的 |  | `REPO_CONTENTS.md:129` |

---

## 5. 附：逐字节重复文件镜像映射（去重依据）

全项目 460 个 `.md` 中只有 **196 份唯一内容**；**130 组**存在重复，冗余副本 **264 份**。

其中 `16_S5_核心总包_20261015/` 共 145 个 `.md`，**仅 21 个是该包独有的唯一内容**，其余 **124 个**是其他目录的逐字节副本。

下表：**规范路径**（本索引引用者） → 同内容副本。副本中行号与本索引一致，可直接互查。

| # | 规范路径（本索引引用） | 同内容副本 |
| --- | --- | --- |
| 1 | `00_项目总结/00_执行摘要_全文.md` | 16_S5_核心总包_20261015/00_项目总结/00_执行摘要_全文.md |
| 2 | `00_项目总结/01_成果总表.md` | 16_S5_核心总包_20261015/00_项目总结/01_成果总表.md |
| 3 | `00_项目总结/02_项目时间线.md` | 16_S5_核心总包_20261015/00_项目总结/02_项目时间线.md |
| 4 | `00_项目总结/03_思路总结_全文.md` | 16_S5_核心总包_20261015/00_项目总结/03_思路总结_全文.md |
| 5 | `00_项目总结/04_定因与工具链成果_20261013.md` | 16_S5_核心总包_20261015/00_项目总结/04_定因与工具链成果_20261013.md |
| 6 | `00_项目总结/05_环境与依赖.md` | 16_S5_核心总包_20261015/00_项目总结/05_环境与依赖.md |
| 7 | `01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md` | 01_研究报告/02_研究总报告_20261011/research/00-总评估报告-中文.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/research/00-总评估报告-中文.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/00-总评估报告-中文.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/research/00-总评估报告-中文.md |
| 8 | `01_研究报告/01_固件AES绕过_调研_20261010/01-固件格式与启动/probe_results.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/01-固件格式与启动/probe_results.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/01-固件格式与启动/probe_results.md |
| 9 | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/siegfried82_notes.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/02-硬件攻击面/siegfried82_notes.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/siegfried82_notes.md |
| 10 | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/verify_logic_notes.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/02-硬件攻击面/verify_logic_notes.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/verify_logic_notes.md |
| 11 | `01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/williamwu1234_notes.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/02-硬件攻击面/williamwu1234_notes.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/williamwu1234_notes.md |
| 12 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_ROM_BACKUP与原厂维修协议逆向推导报告_20261009.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_ROM_BACKUP与原厂维修协议逆向推导报告_20261009.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_ROM_BACKUP与原厂维修协议逆向推导报告_20261009.md |
| 13 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_公开入口核查与下一步.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_公开入口核查与下一步.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_公开入口核查与下一步.md |
| 14 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_解码突破记录.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_解码突破记录.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2_解码突破记录.md |
| 15 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件存储拓扑与离线解码技术边界终局报告_20261008.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件存储拓扑与离线解码技术边界终局报告_20261008.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件存储拓扑与离线解码技术边界终局报告_20261008.md |
| 16 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件逆向_阶段结果汇总.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件逆向_阶段结果汇总.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/S1M2固件逆向_阶段结果汇总.md |
| 17 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/README.md |
| 18 | `01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/oracle_results.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/oracle_results.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/oracle/oracle_results.md |
| 19 | `01_研究报告/01_固件AES绕过_调研_20261010/04-转接环EF-L/EF-L-转接环固件-分析报告-中文.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/04-转接环EF-L/EF-L-转接环固件-分析报告-中文.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/04-转接环EF-L/EF-L-转接环固件-分析报告-中文.md |
| 20 | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/S1RM2-ffs-OOB-漏洞报告-中文.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/S1RM2-ffs-OOB-漏洞报告-中文.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/S1RM2-ffs-OOB-漏洞报告-中文.md |
| 21 | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/s1rm2_usb_ptp_research_report_zh.md |
| 22 | `01_研究报告/02_研究总报告_20261011/00-执行摘要.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/00-执行摘要.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/00-执行摘要.md |
| 23 | `01_研究报告/02_研究总报告_20261011/01-目标与环境.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/01-目标与环境.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/01-目标与环境.md |
| 24 | `01_研究报告/02_研究总报告_20261011/02-攻击面总览.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/02-攻击面总览.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/02-攻击面总览.md |
| 25 | `01_研究报告/02_研究总报告_20261011/03-固件格式与启动链.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/03-固件格式与启动链.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/03-固件格式与启动链.md |
| 26 | `01_研究报告/02_研究总报告_20261011/04-固件升级写路径.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/04-固件升级写路径.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/04-固件升级写路径.md |
| 27 | `01_研究报告/02_研究总报告_20261011/05-RCE与代码注入.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/05-RCE与代码注入.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/05-RCE与代码注入.md |
| 28 | `01_研究报告/02_研究总报告_20261011/06-崩溃与DoS.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/06-崩溃与DoS.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/06-崩溃与DoS.md |
| 29 | `01_研究报告/02_研究总报告_20261011/07-USB-PTP-SCSI.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/07-USB-PTP-SCSI.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/07-USB-PTP-SCSI.md |
| 30 | `01_研究报告/02_研究总报告_20261011/08-WiFi预言机与密钥提取.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/08-WiFi预言机与密钥提取.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/08-WiFi预言机与密钥提取.md |
| 31 | `01_研究报告/02_研究总报告_20261011/09-已证伪路线.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/09-已证伪路线.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/09-已证伪路线.md |
| 32 | `01_研究报告/02_研究总报告_20261011/10-下一步与开放问题.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/10-下一步与开放问题.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/10-下一步与开放问题.md |
| 33 | `01_研究报告/02_研究总报告_20261011/11-安全约束.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/11-安全约束.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/11-安全约束.md |
| 34 | `01_研究报告/02_研究总报告_20261011/README.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/README.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/README.md |
| 35 | `01_研究报告/02_研究总报告_20261011/logs/写路径/campaign.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/logs/写路径/campaign.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/logs/写路径/campaign.md |
| 36 | `01_研究报告/02_研究总报告_20261011/logs/指纹/http_fingerprint.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/logs/指纹/http_fingerprint.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/logs/指纹/http_fingerprint.md |
| 37 | `01_研究报告/02_研究总报告_20261011/research/BOOT_FLOW.md` | 01_研究报告/01_固件AES绕过_调研_20261010/01-固件格式与启动/BOOT_FLOW.md<br>03_解包_APK/com.panasonic.jp.lumixsync/fw_fetch/BOOT_FLOW.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/research/BOOT_FLOW.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/01-固件格式与启动/BOOT_FLOW.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/research/BOOT_FLOW.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/01-固件格式与启动/BOOT_FLOW.md |
| 38 | `01_研究报告/02_研究总报告_20261011/research/FIRMWARE_FORMAT.md` | 01_研究报告/01_固件AES绕过_调研_20261010/01-固件格式与启动/FIRMWARE_FORMAT.md<br>03_解包_APK/com.panasonic.jp.lumixsync/fw_fetch/FIRMWARE_FORMAT.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/research/FIRMWARE_FORMAT.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/01-固件格式与启动/FIRMWARE_FORMAT.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/research/FIRMWARE_FORMAT.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/01-固件格式与启动/FIRMWARE_FORMAT.md |
| 39 | `01_研究报告/02_研究总报告_20261011/research/Wi-Fi实机预言机与mode枚举实测-中文.md` | 01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/Wi-Fi实机预言机与mode枚举实测-中文.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/research/Wi-Fi实机预言机与mode枚举实测-中文.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/Wi-Fi实机预言机与mode枚举实测-中文.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/research/Wi-Fi实机预言机与mode枚举实测-中文.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/03-离线破解与上传预言机/Wi-Fi实机预言机与mode枚举实测-中文.md |
| 40 | `01_研究报告/02_研究总报告_20261011/research/hardware_attack_surface_notes.md` | 01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/hardware_attack_surface_notes.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/research/hardware_attack_surface_notes.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/02-硬件攻击面/hardware_attack_surface_notes.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/research/hardware_attack_surface_notes.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/02-硬件攻击面/hardware_attack_surface_notes.md |
| 41 | `01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/参考报告/S5_AES破解可行性评估_20261011.md |
| 42 | `01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/参考报告/根目录README.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/参考报告/根目录README.md |
| 43 | `01_研究报告/03_隐藏格式_可分发版_20261012/README.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/03_隐藏格式_可分发版_20261012/README.md<br>16_S5_核心总包_20261015/01_研究报告/03_隐藏格式_可分发版_20261012/README.md |
| 44 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/00_执行摘要.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/03_隐藏格式_可分发版_20261012/docs/00_执行摘要.md<br>16_S5_核心总包_20261015/01_研究报告/03_隐藏格式_可分发版_20261012/docs/00_执行摘要.md |
| 45 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/01_版本门与握手修复.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/03_隐藏格式_可分发版_20261012/docs/01_版本门与握手修复.md<br>16_S5_核心总包_20261015/01_研究报告/03_隐藏格式_可分发版_20261012/docs/01_版本门与握手修复.md |
| 46 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/02_隐藏功能.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/03_隐藏格式_可分发版_20261012/docs/02_隐藏功能.md<br>16_S5_核心总包_20261015/01_研究报告/03_隐藏格式_可分发版_20261012/docs/02_隐藏功能.md |
| 47 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/03_opengate_6k_photo.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/03_隐藏格式_可分发版_20261012/docs/03_opengate_6k_photo.md<br>16_S5_核心总包_20261015/01_研究报告/03_隐藏格式_可分发版_20261012/docs/03_opengate_6k_photo.md |
| 48 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md<br>16_S5_核心总包_20261015/01_研究报告/03_隐藏格式_可分发版_20261012/docs/04_camcgi_RCE面测绘.md |
| 49 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md<br>16_S5_核心总包_20261015/01_研究报告/03_隐藏格式_可分发版_20261012/docs/05_复现流程.md |
| 50 | `01_研究报告/03_隐藏格式_可分发版_20261012/docs/06_安全约束与风险.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/03_隐藏格式_可分发版_20261012/docs/06_安全约束与风险.md<br>16_S5_核心总包_20261015/01_研究报告/03_隐藏格式_可分发版_20261012/docs/06_安全约束与风险.md |
| 51 | `01_研究报告/04_隐藏格式_持久化成果.md` | 04_工具与脚本/campaign2/隐藏格式持久化_成果.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/04_隐藏格式_持久化成果.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/04_隐藏格式_持久化成果.md<br>16_S5_核心总包_20261015/01_研究报告/04_隐藏格式_持久化成果.md<br>16_S5_核心总包_20261015/04_工具与脚本/campaign2/隐藏格式持久化_成果.md |
| 52 | `01_研究报告/05_Panasonic_hidden_format_参考/README.md` | 16_S5_核心总包_20261015/01_研究报告/05_Panasonic_hidden_format_参考/README.md |
| 53 | `01_研究报告/05_Panasonic_hidden_format_参考/复现操作手册.md` | 16_S5_核心总包_20261015/01_研究报告/05_Panasonic_hidden_format_参考/复现操作手册.md |
| 54 | `01_研究报告/05_Panasonic_hidden_format_参考/研究报告.md` | 16_S5_核心总包_20261015/01_研究报告/05_Panasonic_hidden_format_参考/研究报告.md |
| 55 | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md<br>16_S5_核心总包_20261015/01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md |
| 56 | `01_研究报告/06_S1R2移交_20261012/S1R2_已排除路线与风险备忘.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/06_S1R2移交_20261012/S1R2_已排除路线与风险备忘.md<br>16_S5_核心总包_20261015/01_研究报告/06_S1R2移交_20261012/S1R2_已排除路线与风险备忘.md |
| 57 | `01_研究报告/06_S1R2移交_20261012/S1R2两项成果_移交S5同事.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/06_S1R2移交_20261012/S1R2两项成果_移交S5同事.md<br>16_S5_核心总包_20261015/01_研究报告/06_S1R2移交_20261012/S1R2两项成果_移交S5同事.md |
| 58 | `01_研究报告/07_隐藏格式持久化_追查_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/07_隐藏格式持久化_追查_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/07_隐藏格式持久化_追查_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/07_隐藏格式持久化_追查_20261013.md |
| 59 | `01_研究报告/08_格式对照表_NTSC-MOV_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/08_格式对照表_NTSC-MOV_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/08_格式对照表_NTSC-MOV_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/08_格式对照表_NTSC-MOV_20261013.md |
| 60 | `01_研究报告/09_S1H参考包分析_mp4ed_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/09_S1H参考包分析_mp4ed_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/09_S1H参考包分析_mp4ed_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/09_S1H参考包分析_mp4ed_20261013.md |
| 61 | `01_研究报告/10_跨机型移植边界_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/10_跨机型移植边界_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/10_跨机型移植边界_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/10_跨机型移植边界_20261013.md |
| 62 | `01_研究报告/11_菜单条目注入可行性_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/11_菜单条目注入可行性_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/11_菜单条目注入可行性_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/11_菜单条目注入可行性_20261013.md |
| 63 | `01_研究报告/12_可写设置面审计_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/12_可写设置面审计_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/12_可写设置面审计_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/12_可写设置面审计_20261013.md |
| 64 | `01_研究报告/13_服务模式与ROMBACKUP_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/13_服务模式与ROMBACKUP_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/13_服务模式与ROMBACKUP_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/13_服务模式与ROMBACKUP_20261013.md |
| 65 | `01_研究报告/14_蓝牙BLE勘察_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/14_蓝牙BLE勘察_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/14_蓝牙BLE勘察_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/14_蓝牙BLE勘察_20261013.md |
| 66 | `01_研究报告/15_蓝牙BLE协议逆向_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/15_蓝牙BLE协议逆向_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/15_蓝牙BLE协议逆向_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/15_蓝牙BLE协议逆向_20261013.md |
| 67 | `01_研究报告/16_App在线状态信息获取_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/16_App在线状态信息获取_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/16_App在线状态信息获取_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/16_App在线状态信息获取_20261013.md |
| 68 | `01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/17_相机热点与蓝牙Windows侧勘察_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/17_相机热点与蓝牙Windows侧勘察_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/17_相机热点与蓝牙Windows侧勘察_20261013.md |
| 69 | `01_研究报告/18_相机热点SoftAP侧勘察_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/18_相机热点SoftAP侧勘察_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/18_相机热点SoftAP侧勘察_20261013.md |
| 70 | `01_研究报告/19_BLE凭据链打通_先写后读_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/19_BLE凭据链打通_先写后读_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/19_BLE凭据链打通_先写后读_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/19_BLE凭据链打通_先写后读_20261013.md |
| 71 | `01_研究报告/20_BLE身份与WiFi门独立_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/20_BLE身份与WiFi门独立_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/20_BLE身份与WiFi门独立_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/20_BLE身份与WiFi门独立_20261013.md |
| 72 | `01_研究报告/21_S1R2_exFAT越界写对S5的意义_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/21_S1R2_exFAT越界写对S5的意义_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/21_S1R2_exFAT越界写对S5的意义_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/21_S1R2_exFAT越界写对S5的意义_20261013.md |
| 73 | `01_研究报告/22_S5_exFAT越界写前置条件确认_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/22_S5_exFAT越界写前置条件确认_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/22_S5_exFAT越界写前置条件确认_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/22_S5_exFAT越界写前置条件确认_20261013.md |
| 74 | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/23_S5_exFAT越界写实机确认_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/23_S5_exFAT越界写实机确认_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/23_S5_exFAT越界写实机确认_20261013.md |
| 75 | `01_研究报告/24_相机长文件名崩溃_定因_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/24_相机长文件名崩溃_定因_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/24_相机长文件名崩溃_定因_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/24_相机长文件名崩溃_定因_20261013.md |
| 76 | `01_研究报告/25_操作记录与风险手册_20261013.md` | 16_S5_核心总包_20261015/01_研究报告/25_操作记录与风险手册_20261013.md |
| 77 | `01_研究报告/26_本次运行日志_20261013.md` | 16_S5_核心总包_20261015/01_研究报告/26_本次运行日志_20261013.md |
| 78 | `01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/27_ROM_BACKUP导出成功与数据解析_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/27_ROM_BACKUP导出成功与数据解析_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/27_ROM_BACKUP导出成功与数据解析_20261013.md |
| 79 | `01_研究报告/28_PTP固件更新协议审计_20261013.md` | 11_DC-S5成果包_20261013/01_研究报告_全集/28_PTP固件更新协议审计_20261013.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/28_PTP固件更新协议审计_20261013.md<br>16_S5_核心总包_20261015/01_研究报告/28_PTP固件更新协议审计_20261013.md |
| 80 | `01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md` | 16_S5_核心总包_20261015/01_研究报告/29_S1R2报告启示与S5对称密钥分析_20261014.md |
| 81 | `01_研究报告/30_录制格式能力边界与操作教训_20261014.md` | 16_S5_核心总包_20261015/01_研究报告/30_录制格式能力边界与操作教训_20261014.md |
| 82 | `01_研究报告/31_录制格式持久化_受控复测_20261014.md` | 16_S5_核心总包_20261015/01_研究报告/31_录制格式持久化_受控复测_20261014.md |
| 83 | `03_解包_APK/com.panasonic.jp.lumixsync/PANASONIC_FIRMWARE_UPDATE_PROTOCOL.md` | 01_研究报告/02_研究总报告_20261011/research/PANASONIC_FIRMWARE_UPDATE_PROTOCOL.md<br>01_研究报告/01_固件AES绕过_调研_20261010/01-固件格式与启动/PANASONIC_FIRMWARE_UPDATE_PROTOCOL.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/research/PANASONIC_FIRMWARE_UPDATE_PROTOCOL.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/01-固件格式与启动/PANASONIC_FIRMWARE_UPDATE_PROTOCOL.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/research/PANASONIC_FIRMWARE_UPDATE_PROTOCOL.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/01-固件格式与启动/PANASONIC_FIRMWARE_UPDATE_PROTOCOL.md |
| 84 | `03_解包_APK/com.panasonic.jp.lumixsync/PROTOCOL_AUDIT.md` | 01_研究报告/02_研究总报告_20261011/research/PROTOCOL_AUDIT.md<br>01_研究报告/01_固件AES绕过_调研_20261010/01-固件格式与启动/PROTOCOL_AUDIT.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/research/PROTOCOL_AUDIT.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/01-固件格式与启动/PROTOCOL_AUDIT.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/research/PROTOCOL_AUDIT.md<br>16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/01-固件格式与启动/PROTOCOL_AUDIT.md |
| 85 | `04_工具与脚本/TOOLS.md` | 16_S5_核心总包_20261015/04_工具与脚本/TOOLS.md |
| 86 | `04_工具与脚本/TOOLS_工具箱总览.md` | 16_S5_核心总包_20261015/04_工具与脚本/TOOLS_工具箱总览.md |
| 87 | `04_工具与脚本/campaign2/README.md` | 16_S5_核心总包_20261015/04_工具与脚本/campaign2/README.md |
| 88 | `04_工具与脚本/campaign2/out/S1H_format_persistence.md` | 16_S5_核心总包_20261015/04_工具与脚本/campaign2/out/S1H_format_persistence.md |
| 89 | `04_工具与脚本/campaign2/out/S1M2_format_field_notes.md` | 16_S5_核心总包_20261015/04_工具与脚本/campaign2/out/S1M2_format_field_notes.md |
| 90 | `04_工具与脚本/campaign2/out/S5II_slot_crosscheck_20261013.md` | 16_S5_核心总包_20261015/04_工具与脚本/campaign2/out/S5II_slot_crosscheck_20261013.md |
| 91 | `04_工具与脚本/campaign2/out/S5_camsetting_fieldmap.md` | 16_S5_核心总包_20261015/04_工具与脚本/campaign2/out/S5_camsetting_fieldmap.md |
| 92 | `04_工具与脚本/campaign2/out/S5_format_slots_analysis.md` | 16_S5_核心总包_20261015/04_工具与脚本/campaign2/out/S5_format_slots_analysis.md |
| 93 | `04_工具与脚本/campaign2/隐藏格式持久化_成果_副本.md` | 16_S5_核心总包_20261015/04_工具与脚本/campaign2/隐藏格式持久化_成果_副本.md |
| 94 | `04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md` | 11_DC-S5成果包_20261013/02_工具链/ptp/PTP_0x9421_dump_使用说明.md<br>10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/02_工具链/usb_ptp/PTP_0x9421_dump_使用说明.md<br>01_研究报告/02_研究总报告_20261011/scripts/USB-PTP/PTP_0x9421_dump_使用说明.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/02_研究总报告_20261011/scripts/USB-PTP/PTP_0x9421_dump_使用说明.md<br>16_S5_核心总包_20261015/04_工具与脚本/ptp/PTP_0x9421_dump_使用说明.md<br>16_S5_核心总包_20261015/01_研究报告/02_研究总报告_20261011/scripts/USB-PTP/PTP_0x9421_dump_使用说明.md |
| 95 | `04_工具与脚本/s5_monitor/README.md` | 11_DC-S5成果包_20261013/02_工具链/s5_monitor/README.md<br>16_S5_核心总包_20261015/04_工具与脚本/s5_monitor/README.md |
| 96 | `04_工具与脚本/s5_monitor/设置枚举测试计划.md` | 11_DC-S5成果包_20261013/02_工具链/s5_monitor/设置枚举测试计划.md<br>16_S5_核心总包_20261015/04_工具与脚本/s5_monitor/设置枚举测试计划.md |
| 97 | `05_源码/LumixFast-iOS/README.md` | 16_S5_核心总包_20261015/05_源码/LumixFast-iOS/README.md |
| 98 | `05_源码/usb-scsi/README.md` | 01_研究报告/01_固件AES绕过_调研_20261010/06-USB-SCSI源码/usb-scsi-src-export/README.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/01_固件AES绕过_调研_20261010/06-USB-SCSI源码/usb-scsi-src-export/README.md<br>16_S5_核心总包_20261015/05_源码/usb-scsi/README.md |
| 99 | `06_数据与证据/camera_settings/OPENGATE_FINDINGS.md` | 01_研究报告/03_隐藏格式_可分发版_20261012/reference/OPENGATE_FINDINGS.md<br>11_DC-S5成果包_20261013/01_研究报告_全集/03_隐藏格式_可分发版_20261012/reference/OPENGATE_FINDINGS.md<br>16_S5_核心总包_20261015/06_数据与证据/camera_settings/OPENGATE_FINDINGS.md<br>16_S5_核心总包_20261015/01_研究报告/03_隐藏格式_可分发版_20261012/reference/OPENGATE_FINDINGS.md |
| 100 | `06_数据与证据/hidden_format_evidence/candidate_results.md` | 01_研究报告/05_Panasonic_hidden_format_参考/evidence/candidate_results.md<br>16_S5_核心总包_20261015/06_数据与证据/hidden_format_evidence/candidate_results.md |
| 101 | `06_数据与证据/hidden_format_evidence/historical_source/README.md` | 01_研究报告/05_Panasonic_hidden_format_参考/evidence/historical_source/README.md<br>16_S5_核心总包_20261015/06_数据与证据/hidden_format_evidence/historical_source/README.md |
| 102 | `06_数据与证据/hidden_format_evidence/static_review/20261012_解码入口研究记录.md` | 01_研究报告/05_Panasonic_hidden_format_参考/evidence/static_review/20261012_解码入口研究记录.md<br>16_S5_核心总包_20261015/06_数据与证据/hidden_format_evidence/static_review/20261012_解码入口研究记录.md |
| 103 | `11_DC-S5成果包_20261013/01_研究报告_全集/25_操作记录与风险手册_20261013.md` | 10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/25_操作记录与风险手册_20261013.md |
| 104 | `11_DC-S5成果包_20261013/01_研究报告_全集/26_本次运行日志_20261013.md` | 10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集/26_本次运行日志_20261013.md |
| 105 | `12_S5无线监看_v1.0_20261014/README.md` | 16_S5_核心总包_20261015/12_S5无线监看_v1.0_20261014/README.md |
| 106 | `12_S5无线监看_v1.0_20261014/使用说明.md` | 16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/使用说明.md<br>16_S5_核心总包_20261015/12_S5无线监看_v1.0_20261014/使用说明.md |
| 107 | `12_S5无线监看_v1.0_20261014/附_技术参考.md` | 16_S5无线监看发行包_20261015/S5无线监看_LUT版_v1.5/附_技术参考.md<br>16_S5_核心总包_20261015/12_S5无线监看_v1.0_20261014/附_技术参考.md |
| 108 | `13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md` | 16_S5_核心总包_20261015/13_USB服务通道勘察_交接包_20261014/00_交接总结_全文.md |
| 109 | `13_USB服务通道勘察_交接包_20261014/01_实测记录.md` | 16_S5_核心总包_20261015/13_USB服务通道勘察_交接包_20261014/01_实测记录.md |
| 110 | `13_USB服务通道勘察_交接包_20261014/02_工具/README.md` | 16_S5_核心总包_20261015/13_USB服务通道勘察_交接包_20261014/02_工具/README.md |
| 111 | `13_USB服务通道勘察_交接包_20261014/03_Tether协议线索.md` | 16_S5_核心总包_20261015/13_USB服务通道勘察_交接包_20261014/03_Tether协议线索.md |
| 112 | `13_USB服务通道勘察_交接包_20261014/README.md` | 16_S5_核心总包_20261015/13_USB服务通道勘察_交接包_20261014/README.md |
| 113 | `14_总包审计与新方向_20261014/02_全包查看指令手册.md` | 16_S5_核心总包_20261015/14_总包审计与新方向_20261014/02_全包查看指令手册.md |
| 114 | `14_总包审计与新方向_20261014/03_新方向与实验设计.md` | 16_S5_核心总包_20261015/14_总包审计与新方向_20261014/03_新方向与实验设计.md |
| 115 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md` | 18_G100明文与同类项目_20261015/回传同事包/00_交接包_上下文工具与结论.md |
| 116 | `18_G100明文与同类项目_20261015/G100反编译_深挖报告.md` | 18_G100明文与同类项目_20261015/回传同事包/G100反编译_深挖报告.md |
| 117 | `18_G100明文与同类项目_20261015/ILCE7M4RE_借鉴分析.md` | 18_G100明文与同类项目_20261015/回传同事包/ILCE7M4RE_借鉴分析.md |
| 118 | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md` | 18_G100明文与同类项目_20261015/回传同事包/S5M2报告_对S5适用性评估.md |
| 119 | `18_G100明文与同类项目_20261015/三材料总评估_20261015.md` | 18_G100明文与同类项目_20261015/回传同事包/三材料总评估_20261015.md |
| 120 | `18_G100明文与同类项目_20261015/同事任务清单_20261015.md` | 18_G100明文与同类项目_20261015/回传同事包/同事任务清单_20261015.md |
| 121 | `18_G100明文与同类项目_20261015/最新结论速览_20261015.md` | 18_G100明文与同类项目_20261015/回传同事包/最新结论速览_20261015.md |
| 122 | `18_G100明文与同类项目_20261015/索尼方法论_单独提取.md` | 18_G100明文与同类项目_20261015/回传同事包/索尼方法论_单独提取.md |
| 123 | `18_SDDAT验证/00_总览.md` | 17_SD引导路线_20261015/同事验证结果/00_总览.md |
| 124 | `18_SDDAT验证/T0_环境校准.md` | 17_SD引导路线_20261015/同事验证结果/T0_环境校准.md |
| 125 | `18_SDDAT验证/T1_PVC_SD入口判定.md` | 17_SD引导路线_20261015/同事验证结果/T1_PVC_SD入口判定.md |
| 126 | `18_SDDAT验证/T2_跨型号结构验证.md` | 17_SD引导路线_20261015/同事验证结果/T2_跨型号结构验证.md |
| 127 | `18_SDDAT验证/T3_启动链结构比对.md` | 17_SD引导路线_20261015/同事验证结果/T3_启动链结构比对.md |
| 128 | `18_SDDAT验证/T4_构建校准.md` | 17_SD引导路线_20261015/同事验证结果/T4_构建校准.md |
| 129 | `18_SDDAT验证/T5_综合裁决.md` | 17_SD引导路线_20261015/同事验证结果/T5_综合裁决.md |
| 130 | `REPO_CONTENTS.md` | 16_S5_核心总包_20261015/REPO_CONTENTS.md |

### 5.1 仅存在于 `16_S5_核心总包_20261015/` 的文件（该包独有，包外无副本）

- `16_S5_核心总包_20261015/00_本包说明_收录与排除.md`
- `16_S5_核心总包_20261015/01_研究报告/01_固件AES绕过_调研_20261010/06-USB-SCSI源码_去重指针.md`
- `16_S5_核心总包_20261015/01_研究报告/05_Panasonic_hidden_format_参考/evidence_去重指针.md`
- `16_S5_核心总包_20261015/01_研究报告/18_相机热点SoftAP侧勘察_20261013.md`
- `16_S5_核心总包_20261015/02_固件指针/固件SHA256与下载来源.md`
- `16_S5_核心总包_20261015/09_对外分享/小红书帖_S5逆向进度_20261014.md`
- `16_S5_核心总包_20261015/12_S5无线监看_v1.0_20261014/连热点时怎么测.md`
- `16_S5_核心总包_20261015/14_总包审计与新方向_20261014/00_审计总报告.md`
- `16_S5_核心总包_20261015/14_总包审计与新方向_20261014/05_相机只读快照_20261014/README.md`
- `16_S5_核心总包_20261015/14_总包审计与新方向_20261014/06_密码学重跑/结论.md`
- `16_S5_核心总包_20261015/14_总包审计与新方向_20261014/07_签名与密钥恢复/结论.md`
- `16_S5_核心总包_20261015/14_总包审计与新方向_20261014/08_实机与离线验证记录_20261014.md`
- `16_S5_核心总包_20261015/14_总包审计与新方向_20261014/09_LUT可行性报告_20261014.md`
- `16_S5_核心总包_20261015/14_总包审计与新方向_20261014/10_仓库补丁/定因与交接_20261014.md`
- `16_S5_核心总包_20261015/14_总包审计与新方向_20261014/README.md`
- `16_S5_核心总包_20261015/15_LUT烧录工具_20261014/README.md`
- `16_S5_核心总包_20261015/README.md`
- `16_S5_核心总包_20261015/S5_RE_Discord_Post_EN.md`
- `16_S5_核心总包_20261015/S5_RE_Discord_Post_EN_2000.md`
- `16_S5_核心总包_20261015/S5_RE_Project_Summary_EN.md`

---

## 6. 末尾统计

| 指标 | 数值 |
| --- | --- |
| **命令总数（去重条目）** | **590** |
| 命令原始出现处数 | 1601 |
| **结论编号总数（去重后编号个数）** | **146** |
| 结论编号体系套数 | 18 |
| 结论编号定义/提及行数 | 161 |
| **已排除项总数** | **1073** |
| **危险项总数** | **410** |
| 扫描 md 文件数 | 460（唯一内容 196，冗余副本 264） |
| 扫描总行数 | 159,999 |

### 6.1 命令按工具族分布

| 工具族 | 条数 |
| --- | --- |
| A. 相机 HTTP / cam.cgi 接口（curl 与 HTTP 报文） | 39 |
| B. Python 工具链调用（相机侧：设置/持久化/质量/容器/传输） | 262 |
| C. USB / PTP 工具（s5_ptp_dump、s5_usb_*、ImageCaptureCore、iOS 构建签名） | 43 |
| D. 交叉编译 / 固件构建（arm-none-eabi、make、cmake、stubby） | 7 |
| E. 固件/镜像解析与二进制处理（unsquashfs、dd、xxd、binwalk、objdump、磁盘打包） | 27 |
| F. 反汇编审计工具（19_路径1 tools/*、psm_audit/*、grep/awk 定位） | 45 |
| G. 无线 / BLE / SoftAP / 监看（s5_ble、s5ctl、wifi_ap_*、s5monitor、网络工具） | 21 |
| H. LUT 烘焙与照片传输（bake、make_lut、check_style、s5_lut） | 10 |
| I. 仓库 / 环境 / 文件管理（git、pip、pacman、变量导出、目录与文本操作） | 135 |
| Z. 其他 / 未归类 | 1 |

### 6.2 结论编号按体系分布

| 体系 | 编号个数 | 定义/提及行数 | 定义文件 |
| --- | --- | --- | --- |
| C 容器/格式事实结论（C1–C24） | 24 | 24 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md` |
| R 复核项（R1–R10，含印证/否定判定） | 10 | 10 | `14_总包审计与新方向_20261014/00_审计总报告.md` |
| R 已撤回/已更正的说法（R1–R6） | 6 | 6 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md` |
| P 待证项 / 开放问题（P1–P7） | 7 | 7 | `17_SD引导路线_20261015/00_交接包_上下文工具与结论.md` |
| P 硬件/侵入式路线行动计划（P1–P8） | 8 | 8 | `01_研究报告/06_S1R2移交_20261012/00_S5结合点与AES路径总结.md` |
| H 隐藏格式成果（H1–H7，含 H1b/H1c） | 9 | 9 | `00_项目总结/01_成果总表.md` |
| F 固件/AES 侧成果（F1–F5） | 5 | 5 | `00_项目总结/01_成果总表.md` |
| F S1RM2 f_fs OOB 缺陷清单（F3–F8，文件内编号） | 6 | 6 | `01_研究报告/01_固件AES绕过_调研_20261010/05-S1RM2-OOB漏洞/S1RM2-ffs-OOB-漏洞报告-中文.md` |
| E HTTP/SOAP 审计条目（E1–E15，文件内编号） | 15 | 15 | `19_路径1_Linux侧攻击面_20261015/dlna_HTTP_SOAP审计.md` |
| E SOAP 动作/XML 审计条目（E16–E24，文件内编号） | 9 | 9 | `19_路径1_Linux侧攻击面_20261015/dlna_SOAP动作与XML解析审计.md` |
| E SSDP/GENA 审计条目（E1–E12，文件内编号） | 15 | 15 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP_GENA审计.md` |
| E SSDP 入站取值审计条目（E1–E13 + U1，文件内编号） | 13 | 13 | `19_路径1_Linux侧攻击面_20261015/dlna_SSDP入站取值审计.md` |
| E- 自我纠错条目（E-1–E-4） | 4 | 4 | `14_总包审计与新方向_20261014/README.md` |
| N-S5 新增结论（N-S5-1–N-S5-4） | 4 | 4 | `18_G100明文与同类项目_20261015/S5M2报告_对S5适用性评估.md` |
| T exFAT 长文件名崩溃实验分组（T1–T3） | 3 | 3 | `01_研究报告/23_S5_exFAT越界写实机确认_20261013.md` |
| T 实测运行分组（T1–T3） | 3 | 3 | `11_DC-S5成果包_20261013/01_研究报告_全集/26_本次运行日志_20261013.md` |
| E 累计排除项（E25–E28，续 HTTP/SOAP 的 E1–E24，全局唯一编号） | 4 | 4 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md` |
| C-1 候选（19_路径1 剩余盲区审计） | 1 | 16 | `19_路径1_Linux侧攻击面_20261015/dlna_剩余盲区审计.md` |
