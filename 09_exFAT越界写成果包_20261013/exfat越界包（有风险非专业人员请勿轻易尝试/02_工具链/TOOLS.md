# 工具链清单

**本轮主角是 `exfat/`**，其余是前几轮沉淀下来的 Wi-Fi / 蓝牙 / USB 工具。

全部 Python 脚本**只依赖 Python 3 标准库**（`struct`/`json`/`os`/`time`），无第三方包。

---

## 一、`exfat/` —— exFAT 越界写（本轮核心）

| 文件 | 作用 |
|---|---|
| **`exfat_patch.py`** | exFAT 全功能解析与补丁工具（见下方子命令） |
| **`exfat_spray.py`** | 目录项堆喷：用**文件名长度**控制 `kmalloc` 档位 |
| **`s5_exfat_test.sh`** | 编排入口，封装成一条命令 |

### 1.1 `exfat_patch.py` 子命令

```bash
sudo python3 exfat_patch.py <子命令> /dev/diskNsM [参数...]
```

| 子命令 | 说明 |
|---|---|
| `info` | 解析 BPB（ClusterCount / 簇大小 / FAT 偏移 / RootCluster）+ **Boot Checksum 自检** |
| `bitmap` | 读分配位图目录项(0x81) → 算 **map_sectors** 与**越界阈值** |
| `entries <路径>` | 列目录；文件名按 exFAT 规范从 entry **偏移 2** 解析 |
| `chain <簇>` | 打印某文件的完整 FAT 链 |
| `dumpbitmap <文件>` | 位图落盘 **+ 写卡指纹**（BootChecksum / ClusterCount / 已分配簇数） |
| `setfat <簇> <值>` | **精确改单个 FAT 项**（带 fsync + 重开设备复核）——用于还原 |
| `go1` | 第 1 级：自动挑 JPG → 找链尾 → 挑**合法**注入点 → 存位图 → 打补丁 → 回读 → GO/NO-GO |
| `go1check` | 第 1 级后比对与裁决 |
| `go2 [簇] [越界值]` | **第 2 级**：注入**越界值**（默认 `524290` = 索引 128）→ 触发内核越界索引 |
| `verdict` | 一站式诊断：结构 + 目录 + 位图 + 与基线比对 + **含卡代次守卫** → 直接给结论 |
| `session` | go1 + 等回车 + go1check 一体化（防漏步骤） |

### 1.2 `exfat_spray.py` 子命令

| 子命令 | 说明 |
|---|---|
| `size <长度>` | 打印该文件名长度对应的 `bufsize` 与 `kmalloc` 档位（含速查表） |
| `make <挂载点> <数量> <长度>` | 创建单档位喷洒文件 |
| `both <挂载点> <每档数量>` | **双档位一起铺**（150→kmalloc-512 / 240→kmalloc-1024） |
| `clean <挂载点>` | 清理喷洒文件 |

**档位换算**（`bufsize = 8 + (num_ext+1) × 32`）：

| 文件名长度 | entries | bufsize | slab |
|---|---|---|---|
| 90 | 8 | 264 | kmalloc-512 |
| 150 | 12 | 392 | kmalloc-512 |
| 210 | 16 | 520 | kmalloc-1024 |
| 240 | 18 | 584 | kmalloc-1024 |
| 255 | 19 | 616 | kmalloc-1024 |

### 1.3 `s5_exfat_test.sh` 子命令

```bash
sudo bash s5_exfat_test.sh <子命令> /dev/diskNsM [参数...]
# prep / bitmap / chain / dumpbitmap / info / entries /
# go1 / go1check / go2 / session / verdict / setfat / restore
```

内建：**自动卸载**（原始访问前必须）、**按卷名+文件系统+容量自动识别设备**（卡拔插后节点会变）、
**卡代次守卫**、**GO/NO-GO 拦截**。

---

## 二、`cam_cgi/` —— Wi-Fi `cam.cgi` 工具集（前几轮）

主力四个：

| 脚本 | 用途 |
|---|---|
| `persist.py` | **核心**：分块 `separate` 协议读写 65,533 B 配置块；verify / restore / flashwrite |
| `persist_quality.py` | 写【录制质量】：校验在 `allmenu` → `setsetting` → 回读 → 备份 → 分块写 flash |
| `container_switch.py` | 切换容器（`videoformat`）：mov / mp4 / mp4ed / avchd / mp4hevc |
| `hidden_features.py` | 隐藏功能开关尝试：vlog / 6kphoto / lpcm / avchd |

其余为枚举、探测、安全测试与共享基础设施（详见文件内注释）。

---

## 三、`ble/` —— 蓝牙（Swift + CoreBluetooth）

| 文件 | 用途 |
|---|---|
| `ble_scan` / `.swift` | 扫描 + 连接 + 完整 GATT 枚举（只读） |
| `ble_read` / `.swift` | 逐特征读取诊断；`--idle` 判别"读触发断链 vs 空闲超时" |
| `ble_diag` / `.swift` | 完整诊断：枚举 + 描述符 + 通知 + 读 +（可选）写 |
| **`ble_write_then_read` / `.swift`** | **复现正确顺序的凭据读取**（先写身份、再读 SSID/密码） |
| `ble_hold` / `.swift` | 握手后**保持连接**（相机热点只在 BLE 会话期间在线） |
| `ble_lan_pair` / `.swift` | 局域网版：BLE 注册身份 + 同一 UUID 走 `accctrl`（含加密路径编码器） |
| `ble_wr` | `ble_write_then_read` 的编译产物 |

```bash
swiftc -framework CoreBluetooth -framework Foundation -o ble_scan ble_scan.swift
./ble_scan 30
```

---

## 四、`ble_win/` —— Windows 侧蓝牙（第三方/协作者提供）

`s5_ble.py` / `s5_ble_watch.py` / `s5_ble_handshake.py` / `s5_ble_pair.ps1`
（WinRT 有显式配对 API `DeviceInformation.Pairing`，是 macOS CoreBluetooth 缺的能力）

---

## 五、`usb_ptp/` —— USB PTP

| 文件 | 用途 |
|---|---|
| `s5_ptp_raw.c` | **自建原始 USB PTP 客户端**：IOUSBLib 直连 bulk 端点，绕过 macOS 相机库 |
| `s5_ptp_dump.m` | 原生 ImageCaptureCore 客户端 |
| `s5_ptp_dump.py` | 早期 libusb 版本（macOS bulk IN 会 EOVERFLOW，已不推荐） |
| `PTP_0x9421_dump_使用说明.md` | 使用说明 |

---

## 六、共享约定（所有工具）

- 相机 Wi-Fi 固定 `192.168.1.131`，`cam.cgi` 必须带 **`User-Agent: LUMIX Sync`**
- 读 `camsetting` 前**退出机身菜单**，否则 `err_reject`
- 写 flash 前**必须 AC 供电**
- **macOS 原始磁盘设备受 Unix 权限 + TCC 双重保护**：需要 root **且**进程有"完全磁盘访问"
  → 自动化进程通常两者都过不去，`exfat` 相关命令**必须由人在终端用 sudo 执行**
