# Panasonic 隐藏录制格式研究交付包

版本：1.0 · 2026-10-12 · 状态：S1H 实机结果归档，S5 迁移实验工具。

**先读结论：S1H 已录出并显示 MP4（LPCM）隐藏档位；S5 尚未由本研究实机复现。** 此包让 S5 持有人使用同一核对流程测试本机支持项，不保证 S5 能显示 S1H 的 4K25／422／10bit／ALL-I／400Mbps 档位。没有改版固件，也没有破解签名、代码执行或固件解密成果。

## 文件目录

- `研究报告.md`：研究对象、原理、结果、证据等级、失败案例与迁移边界。
- `复现操作手册.md`：S1H 已验证流程、S5 单项实验、菜单验证及退出恢复。
- `programs/lumix_hidden_format.py`：Python 标准库程序；默认操作 inspect 只读；activate 单项设置写；restore 恢复可见设置。
- `programs/verify_recording.py`：独立媒体文件检查；需自行准备 FFmpeg、FFprobe。
- `programs/test_lumix_hidden_format.py`：不连接相机的协议模拟及异常恢复测试。
- `evidence/`：本研究的原始菜单响应、关键设置响应、截图、媒体文件与核对结果。
- `SHA256SUMS.json`：分发文件完整性清单。`programs/check_package.py` 可离线核对。

Python 3.9 或更高版本。相机与电脑须能在同一局域网通信；USB Tether 不能代替此处的 HTTP 接口。所有命令中的 IP 都要换成**收件人自己的相机地址**。不要连接作者或其他人的设备。

## 快速开始

先在机身选择普通 MP4，保持录像停止；连接相机 Wi-Fi，在本文件夹打开终端：

```sh
python3 programs/lumix_hidden_format.py inspect --ip 192.168.2.107 --model S1H
```

S5 用户将 `--model S1H` 换成 `--model S5`。查看新生成的 `captures/时间/inspection.json`，其中 `enabled_not_declared` 仅表示“当前菜单标为可用但完整菜单未声明 setter 的候选”，并不表示已能录像。

S1H 单项复现（仅当上面的只读检查显示目标已启用）：

```sh
python3 programs/lumix_hidden_format.py activate --ip 192.168.2.107 --model S1H --token mp4ed_25p_400mbps_4k_10bit --write --accept-secondary-change
```

S5 的写入实验需另加 `--experimental-s5`，且必须使用 **S5 本机 inspection.json 标为 enabled 的 token**。不提供盲试或批量写入命令。

成功读回后程序保持该档位，不开录、不自动关机；到机身“录制文件格式”和“录制质量”检查显示。要验证文件，使用机身录像键拍 2–10 秒、再按一次停止，从卡上复制文件检查。工程模式不是本包自动开启的功能；现有证据未验证不同工程状态是否影响接口开放。

## 恢复的实际边界

`restore_journal.json` 保存原先读到的格式与质量。如下命令恢复这两个**可见设置**：

```sh
python3 programs/lumix_hidden_format.py restore --ip 192.168.2.107 --model S1H --journal captures/某次时间/restore_journal.json --write
```

相机会分别记忆多个格式的上次质量，选中隐藏格式可能改变这些“后台记忆项”。通用程序没有经过 S5 配置结构验证，**不能保证恢复所有后台项**。它保存原始二进制快照并核对恢复前后散列；`snapshot_matches_original=false` 必须视作“完整恢复未成立”，不能写成“全部恢复成功”。本研究曾在 S1H 用已确认的各格式原值完成逐字节恢复；其原值不是收件人的原值，不能直接套用。

因此写入需要 `--accept-secondary-change` 显式接受此限制。通信中断、响应异常、恢复失败时停下，先用机身菜单回到已知正常规格；不重复发送、不升级、不回灌快照。

运行生成的 `captures/` 含本机 IP、设置和原始 camsetting，可能含个人配置。**公开分享时不要直接附整个 captures，更不要公开原始配置快照。** 本交付包未包含研究机的原始 CAMSET 快照、固件映像、账号或 Wi-Fi 凭据。

本包新整理的通用程序通过离线模拟测试；S1H 的硬件结果来自归档内历史实验程序与实机证据，未把本次重新封装程序冒充新的硬件验证。S5 模拟测试只验证程序逻辑。
