# Lumix Fast (iOS)

基于 **Lumix-Fast** Android App 的 **iOS 移植版**。通过 Wi-Fi 连接松下 Lumix 相机，实现：

- 取景（Live View）
- 远程快门 / 开机 / 关机 / 对焦
- 相机相册浏览与照片回传（保存到系统相册）
- 相机状态实时显示（电池、模式、SD、固件版本）

全程**本地运行，无云端**，中文界面（含英文备选）。

---

## 重要：为什么走 Wi-Fi 而不是 USB

原 Android 版 `Lumix-Fast` 的核心是**基于 Android USB Host 的 USB 大容量存储（mass-storage）传输**（`liblumix_usbfs.so` 只暴露 `clearHalt`/`resetDevice` 的 JNI 壳，真正的传输逻辑在 R8 混淆的 Kotlin 里）。

**iOS 无法与非 MFi 认证的 USB 设备通信**，因此原 App 的「USB 高速文件传输」这一能力**无法原样移植到 iOS**。iOS 上唯一可行、且与官方 **LUMIX Sync** 一致的传输通道是 **Wi-Fi**：

- 控制 / 取景 / 快门 → 相机 HTTP 协议 `/cam.cgi`（`User-Agent` 必须为 `LUMIX Sync`）
- 文件浏览 / 回传 → 相机 **DLNA**（ContentDirectory，端口 `60606`）

这也是官方 LUMIX Sync 的做法。本 App 即据此实现，因此**必须让相机与 iPhone 在同一 Wi-Fi 网络**。

---

## 功能与协议来源

协议细节来自 `~/Downloads/com.panasonic.jp.lumixsync_b0834c31/` 的研究（`README.md`、`PROTOCOL_AUDIT.md`、`lumix_handshake.py`、`camera_api/*.xml`、`fw_fetch/probe_results/`）。

- 控制：`http://<ip>/cam.cgi?mode=…&type=…&value=…`
  - `getstate` 取相机状态（XML）
  - `camcmd`：`shoot` / `poweron` / `poweroff` / `playmode` / `recmode`
  - `camctrl`：`focus`（wide/normal/tele/stop）
  - `setsetting` / `getsetting`（如 `photostyle`）
- 文件：DLNA
  - 控制：`POST http://<ip>:60606/Server0/CDS_control`（SOAP `ContentDirectory#Browse`）
  - 数据：`http://<ip>:60606/Lumix/Server0/ddd`；缩略图用请求头 `X-CONVERT`
- 取景：HTTP JPEG 轮询（依次尝试 `/liveview_s.jpg` → `_m` → `_l` → `/img/0.jpg`）

---

## 目录结构

```
LumixFast-iOS/
  project.yml                 # xcodegen 工程描述
  AppIcon-source.svg          # 应用图标矢量源（1024，青/深色）
  LumixFast.xcodeproj         # 由 xcodegen 生成
  LumixFast/
    App/LumixFastApp.swift
    Model/
      LumixClient.swift       # cam.cgi HTTP 客户端
      LumixDLNA.swift         # DLNA 文件浏览/下载
      CameraDiscovery.swift   # Bonjour 发现 + 手动 IP 探测
      AppModel.swift          # 中央视图模型
    Views/
      ConnectView.swift       # 连接（手动 IP / 自动发现）
      LiveViewScreen.swift    # 取景 + 快门 + 状态
      GalleryView.swift       # 相册浏览 + 回传
      SettingsScreen.swift    # 照片风格 / 连接信息
      RootView.swift
    Resources/
      Info.plist
      Assets.xcassets/        # AppIcon（1024 图标）+ AccentColor
      zh-Hans.lproj/Localizable.strings   # 中文（开发语言）
      en.lproj/Localizable.strings        # 英文
  scripts/
    build_ipa.sh              # 生成未签名 IPA
    sign_ipa.sh               # 用你的团队签名 → 可安装 IPA
  dist/                       # 输出目录（.ipa）
```

---

## 构建

依赖：Xcode 27（iOS 27 SDK）、`xcodegen`（`brew install xcodegen`）。

### 1. 生成 / 打开工程

```bash
cd LumixFast-iOS
xcodegen generate          # 重新生成 LumixFast.xcodeproj
open LumixFast.xcodeproj   # 用 Xcode 打开
```

在 Xcode 的 **Signing & Capabilities** 里选择你的 Team（个人/付费开发者账号均可），即可在模拟器或真机上直接运行。

### 2. 生成 IPA

```bash
# 未签名 IPA（仅为交付/打包产物，不能直接安装）
./scripts/build_ipa.sh            # 输出 dist/LumixFast.ipa

# 用你的开发者团队签名 → 可安装 IPA
DEVELOPMENT_TEAM=XXXXXXXXXX ./scripts/sign_ipa.sh   # 输出 dist/LumixFast-signed.ipa
```

> 签名需要有效的代码签名身份。检查：`security find-identity -v -p codesigning`。
> 先把你的 Apple ID 加入 Xcode（Settings > Accounts），Xcode 会自动生成/下载开发描述文件。

### 3. 安装

三种方式任选：

1. **Xcode 直连**：用数据线连上真机，在 Xcode 里选你的设备并 Run（最简单）。
2. **侧载（无付费账号也可）**：用 AltStore / Sideer / Sideloadly 安装 `LumixFast-signed.ipa`。
3. **TestFlight / App Store**：需要付费开发者账号 + 描述文件，走 App Store Connect 归档分发。

---

## 相机要求

- 相机开启 **Wi-Fi**，且与 iPhone 在**同一网络**。
- iPhone 需在 设置 → 隐私 → 本地网络 中允许本 App 访问；首次连接时授予相册（仅添加）权限。
- 支持机型：以实际固件是否提供 `/cam.cgi` 与 DLNA（端口 60606）为准（研究基于 DC-S5，VD4.30）。

---

## 已知限制

- **取景为 HTTP JPEG 轮询**，而非官方 UDP `startstream` 实时流，帧率/延迟按机型可能需微调；端点顺序已内置回退。
- 快门指令 `camcmd&type=shoot` 为通用写法，个别固件字段可能不同，需按机型校准。
- 「照片风格」列表目前是**占位**（capability XML 的完整解析尚未做），可手动选择/后续扩展。
- 协议中**没有**删除照片、上传 LUT 等命令，本 App 未臆造这些功能。
- 未签名 IPA 不能直接安装，必须先用 `sign_ipa.sh`（或 Xcode）签名。

---

## 后续可优化

- 改用 UDP `startstream` 实现官方实时取景流。
- 解析 `getinfo capability` / `allmenu`，按机型动态生成可用设置项。
- 细化 Bonjour 过滤（按相机型号的 TXT 记录），避免列出非相机服务。
