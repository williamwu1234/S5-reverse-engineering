# 实机触发验证 · 进度总结 + 下一步指南

> 日期：2026-10-16 · 状态：**工具已升级到 v2（红线修复 + 三通道崩溃分类 + 71 新用例）；相机 13:35 起 `err_critical` 后热点消失，待物理重启**
> ★ 最新结论与下一步见 `../13_新疑点与新方向_20261016.md`（dhcpcd MSG_PEEK 坐实 CVE-2016-10229 station 触发前置 / crash 001 重评估 / v2 能力清单）

---

## 一、进度总结（截至现在）

### 大项目主线（两条，本目录只做第①条的前半段）

| # | 主线 | 状态 |
|---|---|---|
| ① | 拿内存/flash（JTAG/漏洞）→ 从 dump 解码出密钥 | ⏳ 时间未知，**我们负责"找漏洞"这一段** |
| ② | 破出密钥 → 改固件 → 重新封装 UPD 刷机 | ⏳ 未开始（G100 也没升级上去，见同事《G100固件分析报告.md》） |

### 本支线（找漏洞）已完成

1. **P1 离线攻击面审计**（`../08_Linux攻击面_P1候选漏洞_20261015.md`）：
   - 内核 3.18.18 **零加固**（无 KASLR/栈保护/RWX/LSM）+ **`/dev/mem` 开放**（无 STRICT_DEVMEM）。
   - 找到 2 个真 bug 但都**无远程触发入口**：候选 #1（MTK P2P 信标 768B 溢出，主机配置触发）、
     候选 #3（CVE-2016-10229 udp UAF，需本地 recv(MSG_PEEK)）。
   - 排除：BlueBorne（已打补丁）、pvc_sdio（干净）、mac80211（不在数据路径）。

2. **P2 QEMU 端到端验证**（`../09_QEMU复现_CVE-2016-10229/`）：
   - 用本机 `arm-none-eabi-gcc` 编出 3.18.18 + 启动 + **root 读 /dev/mem 拿到真实物理内存**（成功）。
   - 证明"root → /dev/mem → 读明文 program"这条链成立。

3. **P0 黑盒 fuzz 工具**（本目录）：
   - `fuzz_dlna.py` — dlna SOAP/XML 变异 fuzzer（6 类策略 + 崩溃检测 + 落盘）。
   - `handshake.py` — 一次性正确握手脚本（本次新增）。
   - `send_bad_udp.py` — CVE-2016-10229 坏校验和 UDP 触发器（备用）。

### 当前卡点（2026-10-16 13:38 更新）

- 04:34 v1 fuzz 已跑出 **1 个崩溃候选**（`crash_cases/001_type_StartingIndex_2147483647.xml`），
  但 v1 判据（单通道 8s 超时）无法区分整机崩溃/dlna 进程崩溃/挂起，且 v1 有匿名 `req_acc` 红线违规
  （详见 `../13_新疑点与新方向_20261016.md` §4）。
- 13:35 相机 `getstate=err_critical`（camcmd 重试无效）→ 按权威文档 §4-0 需**物理重启**；随后热点消失。
- **v2 工具已就绪**：`handshake.py`（幂等，绝不重复 req_acc）、`repro_crash.py`（001 受控复现 + 15 变体）、
  `fuzz_dlna.py`（165 用例，三通道分类，JSONL 日志）、`bad_udp`（CVE-2016-10229 坏校验和 UDP，BPF 版，需 sudo）。
- 正确流程（来自 `s5monitor.py` 血泪教训 + 用户实机纠正）：
  ```
  相机断电重启 → 「等待WiFi连接」→ 电脑 handshake.py（req_acc 唯一一次 + playmode）→ 轮询 getstate
  ```
- "连接失败" = 超时 = 电脑没在超时窗口内完成 req_acc + playmode。

---

## 二、下一步指南（相机重启后，可继续跑）

### 前置（一次）

- 相机重启，重新进入「等待WiFi连接」状态（热点模式）。
- Mac 连上相机热点（`192.168.54.1`，本机拿 `192.168.54.10`）。

### 步骤 1：一次性正确握手

```bash
cd /Users/<user>/Documents/S5逆向成果包_20261015/10_实机触发验证
python3 handshake.py 192.168.54.1
```

- 脚本自动做：req_acc（唯一一次）→ camcmd playmode → 轮询 getstate → 验证 dlna 放行。
- **判据**：getstate 返回 `<result>ok</result>`，且 dlna BrowseMetadata 返回 200。
- **红线**：如果没成功，**先重启相机再重跑**，切勿手动连发 req_acc。

### 步骤 2：跑 fuzz

```bash
cd /Users/<user>/Documents/S5逆向成果包_20261015/10_实机触发验证
python3 -u fuzz_dlna.py 192.168.54.1 --strategy all
```

- 崩溃检测：连接复位/超时/健康检查失败/相机重启；每条崩溃输入存 `crash_cases/`。
- 崩溃 = 内存破坏 = 潜在入口（配合零加固内核）。

### 步骤 3（P1，接在 P0 之后）：camsetting 盲 fuzz

- 复用 `../03_工具/campaign2/overflow_fuzz.py` 的协议模板，但把"定向猜字段"改成"盲变异内部 TLV length 字段"。
- 尚未写，等 P0 跑通后再做。

---

## 三、优先级（逆向专家判断）

| 优先级 | 面 | 理由 |
|---|---|---|
| **P0** | dlna SOAP/XML（60606） | 自写 1MB XML 解析器，解析面最复杂，S5 本体二进制与 G100 可能不同 |
| P1 | camsetting 上传解析器（80） | TLV 内部 length 可控，已有协议模板，只做过定向 fuzz |
| P2 | SSDP（1900） | 便宜但解析简单 |
| P3 | lighttpd/cam.fcgi | 上游/已全阴性，跳过 |

## 四、工具清单（本目录）

| 文件 | 用途 |
|---|---|
| `handshake.py` | 一次性正确握手 v2（幂等预检 + req_acc → playmode → getstate） |
| `fuzz_dlna.py` | 网络解析面 fuzzer v2（10 策略 165 用例：SOAP/XML 7 组 + HTTP 层/50001/SSDP 3 组；三通道崩溃分类；JSONL 日志） |
| `repro_crash.py` | crash 001 受控复现（基线计时 + 原 payload 3 轮 + 15 变体梯度 + 三通道判读） |
| `bad_udp.c` / `bad_udp` | CVE-2016-10229 坏校验和 UDP 触发器（macOS BPF 构造帧，`sudo` 运行） |
| `send_bad_udp.py` | （v1 备用，macOS raw socket 路线已确认走不通，弃用） |
| `crash_cases/` | 崩溃输入落盘（c_=整机 d_=dlna进程 h_=挂起） |
| `fuzz_log_*.jsonl` / `repro_log_*.jsonl` | 全量请求日志（case/字节数/耗时/状态码/分类） |
