// bake.swift — 用 CoreImage 把 3D LUT 烧进照片/视频（macOS 原生，无外部依赖）
//
// 为什么不用 ffmpeg：本机 ffmpeg 是坏 bottle（install_name 里 @@HOMEBREW_CELLAR@@ 未替换），
// 且 /opt/homebrew 非当前用户所有、又在工作区之外（沙箱不可写）。CoreImage 走 GPU，
// 原生支持 10-bit HEVC（本机素材为 5184x3456 10-bit hvc1），无需任何第三方依赖。
//
// 用法:
//   bake probe <file>                                 查看素材规格
//   bake image <lut.cube> <in> <out> [--quality 0.95]  烧录单张图片
//   bake video <lut.cube> <in> <out> [--preset hevc]   烧录视频
//   bake batch <lut.cube> <outdir> <in...>             批量（按扩展名自动分流）
//
// 说明:
//   · 支持 .cube（TITLE/LUT_3D_SIZE/DOMAIN_* + 浮点 0..1）
//   · LUT 按“输入已编码值 → 输出已编码值”解释；色彩空间默认 sRGB（可用 --cs 改）
//     ⇒ 与 V-Log/HLG 这类“对编码值做映射”的 LUT 语义一致
//   · 视频路径：AVVideoComposition(applyingCIFiltersWithHandler:) + AVAssetExportSession
//     会保留源分辨率；10-bit 素材建议用 hevc 预设

import Foundation
import AVFoundation
import CoreImage
import CoreImage.CIFilterBuiltins
import ImageIO
import UniformTypeIdentifiers
import CoreServices

// MARK: - LUT 解析

struct CubeLUT {
    let dimension: Int
    let data: Data          // Float32 RGBA，R 变化最快（.cube 约定）

    /// 解析 Panasonic .vlt（纯 ASCII：两行 # 头 + LUT_3D_SIZE N + N³ 行 "R G B"，整数 0–4095）
    /// axis: "variCam"（官方 .txt 注明 blue fastest，r 最慢）或 "cube"（r 最快）
    static func loadVLT(_ path: String, axis: String) throws -> CubeLUT {
        let text = try String(contentsOfFile: path, encoding: .ascii)
        var dim = 0
        var grid: [(Int, Int, Int)] = []
        for raw in text.split(separator: "\n", omittingEmptySubsequences: false) {
            let line = raw.trimmingCharacters(in: .whitespacesAndNewlines)
            if line.isEmpty || line.hasPrefix("#") { continue }
            if line.uppercased().hasPrefix("LUT_3D_SIZE") {
                let p = line.split(separator: " ")
                dim = Int(p.count > 1 ? String(p[1]) : "0") ?? 0
                continue
            }
            let p = line.split(separator: " ").compactMap { Int($0) }
            if p.count >= 3 { grid.append((p[0], p[1], p[2])) }
        }
        guard dim > 1, grid.count == dim * dim * dim else {
            throw NSError(domain: "bake", code: 5,
                          userInfo: [NSLocalizedDescriptionKey:
                                     ".vlt 解析失败：N=\(dim) 数据点=\(grid.count)（期望 N³）"])
        }
        // 按生成时的轴序还原成 (r,g,b) 索引；再按 .cube 约定（r 最快）重排
        var table = [Float](repeating: 0, count: dim * dim * dim * 4)
        var k = 0
        let N = dim
        func put(_ r: Int, _ g: Int, _ b: Int, _ rgb: (Int, Int, Int)) {
            let idx = ((b * N + g) * N + r) * 4    // .cube 布局：r 最快
            table[idx]     = Float(rgb.0) / 4095.0
            table[idx + 1] = Float(rgb.1) / 4095.0
            table[idx + 2] = Float(rgb.2) / 4095.0
            table[idx + 3] = 1.0
        }
        if axis.lowercased() == "cube" {
            for b in 0..<N { for g in 0..<N { for r in 0..<N {
                put(r, g, b, grid[k]); k += 1 } } }
        } else {  // variCam: r 最慢、b 最快
            for r in 0..<N { for g in 0..<N { for b in 0..<N {
                put(r, g, b, grid[k]); k += 1 } } }
        }
        return CubeLUT(dimension: N, data: table.withUnsafeBufferPointer { Data(buffer: $0) })
    }

    static func loadAuto(_ path: String, vltAxis: String) throws -> CubeLUT {
        if path.lowercased().hasSuffix(".vlt") { return try loadVLT(path, axis: vltAxis) }
        return try load(path)
    }

    static func load(_ path: String) throws -> CubeLUT {
        let text = try String(contentsOfFile: path, encoding: .utf8)
        var dim = 0
        var vals: [Float] = []
        for raw in text.split(separator: "\n", omittingEmptySubsequences: false) {
            let line = raw.trimmingCharacters(in: .whitespacesAndNewlines)
            if line.isEmpty || line.hasPrefix("#") { continue }
            let up = line.uppercased()
            if up.hasPrefix("LUT_3D_SIZE") {
                let p = line.split(separator: " ")
                dim = Int(p.count > 1 ? String(p[1]) : "0") ?? 0
                continue
            }
            if up.hasPrefix("TITLE") || up.hasPrefix("DOMAIN_MIN") || up.hasPrefix("DOMAIN_MAX") { continue }
            if up.hasPrefix("LUT_1D_SIZE") {
                throw NSError(domain: "bake", code: 2,
                              userInfo: [NSLocalizedDescriptionKey: "只支持 3D LUT（LUT_1D_SIZE 不支持）"])
            }
            let p = line.split(separator: " ").compactMap { Float($0) }
            if p.count >= 3 { vals.append(contentsOf: [p[0], p[1], p[2], 1.0]) }
        }
        guard dim > 1 else {
            throw NSError(domain: "bake", code: 3,
                          userInfo: [NSLocalizedDescriptionKey: "LUT_3D_SIZE 读取失败"])
        }
        let expect = dim * dim * dim * 4
        guard vals.count == expect else {
            throw NSError(domain: "bake", code: 4,
                          userInfo: [NSLocalizedDescriptionKey:
                                     "数据点数不符：得到 \(vals.count / 4) 个点，期望 \(dim * dim * dim)（N³）"])
        }
        let data = vals.withUnsafeBufferPointer { Data(buffer: $0) }
        return CubeLUT(dimension: dim, data: data)
    }

    func filter(colorSpace: CGColorSpace?) -> CIFilter {
        let f = CIFilter.colorCubeWithColorSpace()
        f.cubeDimension = Float(dimension)
        f.cubeData = data
        f.colorSpace = colorSpace
        return f
    }
}

func cs(named: String) -> CGColorSpace? {
    switch named.lowercased() {
    case "srgb":    return CGColorSpace(name: CGColorSpace.sRGB)
    case "bt709":   return CGColorSpace(name: CGColorSpace.itur_709)
    case "bt2020":  return CGColorSpace(name: CGColorSpace.itur_2020)
    case "linear":  return CGColorSpace(name: CGColorSpace.linearSRGB)
    case "displayp3": return CGColorSpace(name: CGColorSpace.displayP3)
    default:        return CGColorSpace(name: CGColorSpace.sRGB)
    }
}

// MARK: - 工具

func fmt(_ d: [String: Any]) -> String {
    d.sorted { $0.key < $1.key }.map { "    \($0.key) = \($0.value)" }.joined(separator: "\n")
}

func probe(_ path: String) async {
    let url = URL(fileURLWithPath: path)
    let asset = AVURLAsset(url: url)
    guard let track = try? await asset.loadTracks(withMediaType: .video).first else {
        print("  (无视频轨)"); return
    }
    let sz = (try? await track.load(.naturalSize)) ?? .zero
    let fr = (try? await track.load(.nominalFrameRate)) ?? 0
    let dur = (try? await asset.load(.duration)) ?? .zero
    print("  \(url.lastPathComponent)")
    print("    分辨率   \(Int(sz.width))x\(Int(sz.height))")
    print("    帧率     \(String(format: "%.3f", fr)) fps")
    print("    时长     \(String(format: "%.2f", CMTimeGetSeconds(dur))) s")
    if let fds = try? await track.load(.formatDescriptions) {
        for d in fds {
            let st = CMFormatDescriptionGetMediaSubType(d).bigEndian
            let fourcc = String(bytes: [UInt8((st >> 24) & 0xff), UInt8((st >> 16) & 0xff),
                                        UInt8((st >> 8) & 0xff), UInt8(st & 0xff)], encoding: .ascii) ?? "?"
            print("    编码     \(fourcc)")
            if let ext = CMFormatDescriptionGetExtensions(d) as? [String: Any],
               let bits = ext["BitsPerComponent"] { print("    位深     \(bits)") }
        }
    }
}

func bakeImage(lut: CubeLUT, input: String, output: String,
               quality: Double, csName: String) throws {
    let cictx = CIContext(options: [.useSoftwareRenderer: false])
    guard var img = CIImage(contentsOf: URL(fileURLWithPath: input),
                            options: [.applyOrientationProperty: true]) else {
        throw NSError(domain: "bake", code: 10,
                      userInfo: [NSLocalizedDescriptionKey: "无法读取图片：\(input)"])
    }
    let f = lut.filter(colorSpace: cs(named: csName))
    f.setValue(img, forKey: kCIInputImageKey)
    guard let out = f.outputImage else {
        throw NSError(domain: "bake", code: 11, userInfo: [NSLocalizedDescriptionKey: "LUT 应用失败"])
    }
    img = out
    let ext = (output as NSString).pathExtension.lowercased()
    let type: UTType = (ext == "png") ? .png : (ext == "tif" || ext == "tiff") ? .tiff
                                   : (ext == "heic") ? .heic : .jpeg
    let url = URL(fileURLWithPath: output)
    try? FileManager.default.removeItem(at: url)
    guard let dest = CGImageDestinationCreateWithURL(url as CFURL, type.identifier as CFString, 1, nil) else {
        throw NSError(domain: "bake", code: 12,
                      userInfo: [NSLocalizedDescriptionKey: "无法创建输出：\(output)"])
    }
    guard let cg = cictx.createCGImage(img, from: img.extent, format: .RGBA8,
                                       colorSpace: cs(named: csName)) else {
        throw NSError(domain: "bake", code: 13, userInfo: [NSLocalizedDescriptionKey: "渲染失败"])
    }
    let props: [CFString: Any] = [kCGImageDestinationLossyCompressionQuality: quality]
    CGImageDestinationAddImage(dest, cg, props as CFDictionary)
    guard CGImageDestinationFinalize(dest) else {
        throw NSError(domain: "bake", code: 14, userInfo: [NSLocalizedDescriptionKey: "写入失败"])
    }
}

/// 高码率路径：AVAssetWriter 显式控制码率（AVAssetExportSession 无法设码率，只能吃 Apple 默认阶梯）
/// 用途：源为 all-intra / 高码率（如本机 6K 素材 ~107 Mbps）时，避免默认阶梯把码率砍到 ~1/4
func bakeVideoHQ(lut: CubeLUT, input: String, output: String,
                 csName: String, bitrate: Int, maxSeconds: Double?, codec: String) async throws {
    let asset = AVURLAsset(url: URL(fileURLWithPath: input))
    guard let vtrack = try await asset.loadTracks(withMediaType: .video).first else {
        throw NSError(domain: "bake", code: 30, userInfo: [NSLocalizedDescriptionKey: "无视频轨"])
    }
    let sz = try await vtrack.load(.naturalSize)
    let fps = try await vtrack.load(.nominalFrameRate)
    let nominalFR = fps > 0 ? fps : 30.0
    let csRef = cs(named: csName)
    let lutFilter = lut.filter(colorSpace: csRef)

    let comp = AVVideoComposition(asset: asset, applyingCIFiltersWithHandler: { req in
        let src = req.sourceImage
        let f = lutFilter
        f.setValue(src, forKey: kCIInputImageKey)
        req.finish(with: (f.outputImage ?? src).cropped(to: src.extent), context: nil)
    })

    // 以 10-bit YCbCr 解码（保住源位深），LUT 由 CIContext 渲进半浮点缓冲后交给编码器
    let reader = try AVAssetReader(asset: asset)
    let vout = AVAssetReaderTrackOutput(
        track: vtrack,
        outputSettings: [kCVPixelBufferPixelFormatTypeKey as String:
                            kCVPixelFormatType_420YpCbCr10BiPlanarVideoRange])
    vout.alwaysCopiesSampleData = false
    guard reader.canAdd(vout) else {
        throw NSError(domain: "bake", code: 31, userInfo: [NSLocalizedDescriptionKey: "reader 无法添加输出"])
    }
    reader.add(vout)
    if let cap = maxSeconds, cap > 0 {
        reader.timeRange = CMTimeRange(start: .zero,
                                       duration: CMTime(seconds: cap, preferredTimescale: 600))
    }

    let outURL = URL(fileURLWithPath: output)
    try? FileManager.default.removeItem(at: outURL)
    let isProRes = codec.lowercased().contains("prores")
    // 事前预检：ProRes 422 / H.264 的编码器不接受 >4096 宽的画幅，AVAssetWriter 会抛 NSException
    //（Swift 捕获不到 ObjC 异常）⇒ 必须在这里挡住，否则进程直接崩
    if (isProRes || codec.lowercased() == "h264") && Int(sz.width) > 4096 {
        throw NSError(domain: "bake", code: 37, userInfo: [NSLocalizedDescriptionKey:
            "该编码器（\(codec)）不支持 \(Int(sz.width))x\(Int(sz.height)) 画幅（上限 4096 宽）。" +
            "本机 6K 3:2 素材请用默认 HEVC（10-bit，已可用），" +
            "或先用 -vf scale=4096:-2 降尺寸；需要高码率中间格式请用 DaVinci Resolve 套我们生成的 .cube。"])
    }
    let writer = try AVAssetWriter(outputURL: outURL, fileType: isProRes ? .mov : .mp4)
    var vcodec: AVVideoCodecType = .hevc
    if isProRes { vcodec = .proRes422HQ } else if codec.lowercased() == "h264" { vcodec = .h264 }
    let settings: [String: Any] = [
        AVVideoCodecKey: vcodec,
        AVVideoWidthKey: Int(sz.width),
        AVVideoHeightKey: Int(sz.height),
        AVVideoCompressionPropertiesKey: (isProRes
            ? [AVVideoAllowFrameReorderingKey: true]
            : [AVVideoAverageBitRateKey: bitrate,
               AVVideoMaxKeyFrameIntervalKey: Int(nominalFR * 2),
               AVVideoAllowFrameReorderingKey: true,
               AVVideoProfileLevelKey: kVTProfileLevel_HEVC_Main10_AutoLevel as String]) as [String: Any],
        AVVideoColorPropertiesKey: [
            AVVideoColorPrimariesKey: AVVideoColorPrimaries_ITU_R_709_2,
            AVVideoTransferFunctionKey: AVVideoTransferFunction_ITU_R_709_2,
            AVVideoYCbCrMatrixKey: AVVideoYCbCrMatrix_ITU_R_709_2,
        ] as [String: Any],
    ]
    let win = AVAssetWriterInput(mediaType: .video, outputSettings: settings)
    win.expectsMediaDataInRealTime = false
    let adaptor = AVAssetWriterInputPixelBufferAdaptor(
        assetWriterInput: win,
        sourcePixelBufferAttributes: [
            // ProRes 输入不接受半浮点 RGBA，只能退到 8-bit BGRA；HEVC 用半浮点以保住 10-bit
            kCVPixelBufferPixelFormatTypeKey as String: (codec.lowercased().contains("prores")
                ? kCVPixelFormatType_32BGRA : kCVPixelFormatType_64RGBAHalf),
            kCVPixelBufferWidthKey as String: Int(sz.width),
            kCVPixelBufferHeightKey as String: Int(sz.height),
        ])
    guard writer.canAdd(win) else {
        throw NSError(domain: "bake", code: 32, userInfo: [NSLocalizedDescriptionKey: "writer 无法添加输入"])
    }
    writer.add(win)
    guard writer.startWriting(), reader.startReading() else {
        throw NSError(domain: "bake", code: 33,
                      userInfo: [NSLocalizedDescriptionKey: "启动失败：\(writer.error?.localizedDescription ?? reader.error?.localizedDescription ?? "?")"])
    }
    writer.startSession(atSourceTime: .zero)

    let ciCtx = CIContext(options: [.useSoftwareRenderer: false,
                                    .workingColorSpace: csRef as Any])
    let queue = DispatchQueue(label: "bake.hq")
    try await withCheckedThrowingContinuation { (cont: CheckedContinuation<Void, Error>) in
        var done = false
        win.requestMediaDataWhenReady(on: queue) {
            if done { return }
            while win.isReadyForMoreMediaData {
                guard let sb = vout.copyNextSampleBuffer() else {
                    done = true
                    win.markAsFinished()
                    writer.finishWriting {
                        if writer.status == .completed { cont.resume() }
                        else { cont.resume(throwing: NSError(domain: "bake", code: 34,
                            userInfo: [NSLocalizedDescriptionKey: "写入失败：\(writer.error?.localizedDescription ?? "?")"])) }
                    }
                    return
                }
                if let pb = CMSampleBufferGetImageBuffer(sb) {
                    let t = CMSampleBufferGetPresentationTimeStamp(sb)
                    var outBuf: CVPixelBuffer? = nil
                    var st = kCVReturnError
                    if let pool = adaptor.pixelBufferPool {
                        st = CVPixelBufferPoolCreatePixelBuffer(nil, pool, &outBuf)
                    } else {
                        done = true
                        win.markAsFinished()
                        writer.finishWriting {
                            cont.resume(throwing: NSError(domain: "bake", code: 36,
                                userInfo: [NSLocalizedDescriptionKey:
                                "像素缓冲池创建失败：该编码器/画幅组合不被支持（ProRes 在 6K 3:2 上不可用，请改用默认 HEVC 或用 DaVinci Resolve 套 LUT）"]))
                        }
                        return
                    }
                    var appended = false
                    if st == kCVReturnSuccess, let ob = outBuf {
                        var src = CIImage(cvPixelBuffer: pb)
                        let f = lutFilter
                        f.setValue(src, forKey: kCIInputImageKey)
                        let res = (f.outputImage ?? src).cropped(to: src.extent)
                        ciCtx.render(res, to: ob, bounds: src.extent, colorSpace: csRef)
                        appended = adaptor.append(ob, withPresentationTime: t)
                        src = CIImage.empty()
                    }
                    if !appended {
                        done = true
                        win.markAsFinished()
                        writer.finishWriting {
                            cont.resume(throwing: NSError(domain: "bake", code: 35,
                                userInfo: [NSLocalizedDescriptionKey: "append 失败：\(writer.error?.localizedDescription ?? "?")"]))
                        }
                        return
                    }
                }
                CMSampleBufferInvalidate(sb)
            }
        }
    }
}

func bakeVideo(lut: CubeLUT, input: String, output: String,
               csName: String, presetName: String, maxSeconds: Double?) async throws {
    let asset = AVURLAsset(url: URL(fileURLWithPath: input))
    guard let track = try await asset.loadTracks(withMediaType: .video).first else {
        throw NSError(domain: "bake", code: 20, userInfo: [NSLocalizedDescriptionKey: "无视频轨"])
    }
    let _ = track
    let csRef = cs(named: csName)
    let lutFilter = lut.filter(colorSpace: csRef)

    let comp = AVVideoComposition(asset: asset, applyingCIFiltersWithHandler: { req in
        let src = req.sourceImage
        let f = lutFilter
        f.setValue(src, forKey: kCIInputImageKey)
        let out = f.outputImage ?? src
        req.finish(with: out.cropped(to: src.extent), context: nil)
    })

    var preset = presetName
    if preset == "auto" {
        preset = AVAssetExportPresetHEVCHighestQuality
    }
    guard let session = AVAssetExportSession(asset: asset, presetName: preset) else {
        throw NSError(domain: "bake", code: 21,
                      userInfo: [NSLocalizedDescriptionKey: "预设不可用：\(preset)"])
    }
    session.videoComposition = comp
    session.shouldOptimizeForNetworkUse = false
    let outURL = URL(fileURLWithPath: output)
    try? FileManager.default.removeItem(at: outURL)
    session.outputURL = outURL
    let ext = outURL.pathExtension.lowercased()
    session.outputFileType = (ext == "mov") ? .mov : .mp4
    if let cap = maxSeconds, cap > 0 {
        session.timeRange = CMTimeRange(start: .zero,
                                        duration: CMTime(seconds: cap, preferredTimescale: 600))
    }
    await session.export()
    if session.status != .completed {
        throw NSError(domain: "bake", code: 22,
                      userInfo: [NSLocalizedDescriptionKey:
                                 "导出失败：\(session.error?.localizedDescription ?? "未知")"])
    }
}

// MARK: - 入口

let args = Array(CommandLine.arguments.dropFirst())
guard let cmd = args.first else {
    print("""
    用法:
      bake probe <file>
      bake image <lut> <in> <out> [--quality 0.95] [--cs srgb] [--vlt-axis ...]
      bake video <lut> <in> <out> [--cs srgb] [--preset hevc|auto] [--max-seconds N] [--vlt-axis ...] [--bitrate 120M] [--codec hevc|prores|h264]
      bake batch <lut> <outdir> <in...> [--cs srgb] [--vlt-axis variCam|cube]
    """)
    exit(1)
}

func parseBitrate(_ s: String) -> Int {
    let t = s.trimmingCharacters(in: .whitespaces).lowercased()
    if t.isEmpty || t == "0" { return 0 }
    var mult = 1_000_000
    var num = t
    if t.hasSuffix("mbps") { num = String(t.dropLast(4)) }
    else if t.hasSuffix("mb") { num = String(t.dropLast(2)) }
    else if t.hasSuffix("kbps") { num = String(t.dropLast(4)); mult = 1_000 }
    else if t.hasSuffix("kb") { num = String(t.dropLast(2)); mult = 1_000 }
    else if t.hasSuffix("m") { num = String(t.dropLast(1)) }          // 裸 120M
    else if t.hasSuffix("k") { num = String(t.dropLast(1)); mult = 1_000 }
    else if t.hasSuffix("bps") { num = String(t.dropLast(3)) }
    guard let v = Double(num) else { return 0 }
    return Int(v * Double(mult))
}

func opt(_ name: String, _ def: String) -> String {
    if let i = args.firstIndex(of: "--" + name), i + 1 < args.count { return args[i + 1] }
    return def
}

do {
    switch cmd {
    case "probe":
        guard args.count >= 2 else { print("需要文件路径"); exit(1) }
        let sem = DispatchSemaphore(value: 0)
        Task { await probe(args[1]); sem.signal() }
        sem.wait()

    case "image":
        guard args.count >= 4 else { print("需要 <lut> <in> <out>"); exit(1) }
        let lut = try CubeLUT.loadAuto(args[1], vltAxis: opt("vlt-axis", "variCam"))
        let q = Double(opt("quality", "0.95")) ?? 0.95
        try bakeImage(lut: lut, input: args[2], output: args[3],
                      quality: q, csName: opt("cs", "srgb"))
        print("✅ \(args[3])")

    case "video":
        guard args.count >= 4 else { print("需要 <lut> <in> <out>"); exit(1) }
        let lut = try CubeLUT.loadAuto(args[1], vltAxis: opt("vlt-axis", "variCam"))
        var preset = opt("preset", "auto")
        if preset == "hevc" { preset = AVAssetExportPresetHEVCHighestQuality }
        if preset == "h264" { preset = AVAssetExportPresetHighestQuality }
        let cap = Double(opt("max-seconds", "0")) ?? 0
        let brStr = opt("bitrate", "0")
        let bitrate = parseBitrate(brStr)
        let wantCodec = opt("codec", "hevc").lowercased()
        if bitrate > 0 || wantCodec != "hevc" {
            let sem = DispatchSemaphore(value: 0)
            var err: Error? = nil
            Task {
                do {
                    try await bakeVideoHQ(lut: lut, input: args[2], output: args[3],
                                          csName: opt("cs", "srgb"), bitrate: bitrate, maxSeconds: cap > 0 ? cap : nil,
                                          codec: opt("codec", "hevc"))
                    print("✅ \(args[3])  (高码率路径 \(bitrate/1_000_000) Mbps)")
                } catch { err = error }
                sem.signal()
            }
            sem.wait()
            if let e = err { throw e }
            break
        }
        let sem = DispatchSemaphore(value: 0)
        var err: Error? = nil
        Task {
            do {
                try await bakeVideo(lut: lut, input: args[2], output: args[3],
                                    csName: opt("cs", "srgb"), presetName: preset,
                                    maxSeconds: cap > 0 ? cap : nil)
                print("✅ \(args[3])")
            } catch { err = error }
            sem.signal()
        }
        sem.wait()
        if let e = err { throw e }

    case "batch":
        guard args.count >= 4 else { print("需要 <lut> <outdir> <in...>"); exit(1) }
        let lut = try CubeLUT.loadAuto(args[1], vltAxis: opt("vlt-axis", "variCam"))
        let outdir = args[2]
        try? FileManager.default.createDirectory(atPath: outdir, withIntermediateDirectories: true)
        let imgs: Set<String> = ["jpg", "jpeg", "png", "tif", "tiff", "heic", "heif"]
        let vids: Set<String> = ["mp4", "mov", "m4v"]
        for inPath in args.dropFirst(3) {
            let ext = (inPath as NSString).pathExtension.lowercased()
            let base = (inPath as NSString).lastPathComponent
            let outPath = (outdir as NSString).appendingPathComponent(base)
            do {
                if imgs.contains(ext) {
                    try bakeImage(lut: lut, input: inPath, output: outPath, quality: 0.95,
                                  csName: opt("cs", "srgb"))
                    print("✅ \(base)")
                } else if vids.contains(ext) {
                    let sem = DispatchSemaphore(value: 0)
                    var err: Error? = nil
                    Task {
                        do {
                            try await bakeVideo(lut: lut, input: inPath, output: outPath,
                                                csName: opt("cs", "srgb"),
                                                presetName: AVAssetExportPresetHEVCHighestQuality,
                                                maxSeconds: nil)
                        } catch { err = error }
                        sem.signal()
                    }
                    sem.wait()
                    if let e = err { throw e }
                    print("✅ \(base)")
                } else {
                    print("⏭  跳过（未知类型）：\(base)")
                }
            } catch {
                print("❌ \(base): \(error.localizedDescription)")
            }
        }

    default:
        print("未知命令：\(cmd)"); exit(1)
    }
} catch {
    FileHandle.standardError.write("错误：\(error.localizedDescription)\n".data(using: .utf8)!)
    exit(2)
}
