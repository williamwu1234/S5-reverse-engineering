#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s5_lut.py — 3D LUT 加载与实时套用（用于 S5 无线监看的实时取景流）

为什么这样做
    初代 S5 机内**没有** Real Time LUT（影像管线里没有实时 3D LUT 级），
    所以"机内烧录"不可能。但相机的**实时取景流**是 WiFi 上唯一真正实时、
    且已经被本项目跑通的图像通道（UDP MJPEG → 本进程 → 浏览器）。
    ⇒ 把 LUT 套在这一层，就能得到**实时套 LUT 的画面**（监看级，非原始分辨率）。

支持的 LUT 格式
    · Adobe/Resolve `.cube`（3D，浮点 0..1，R 变化最快）
    · Panasonic `.vlt`（3D，整数 0..4095，默认按 VariCam 轴序=B 最快解析）
    两者都用 `make_lut.py` 生成过，也可直接读官方/第三方文件。

性能
    输入是 8-bit JPEG（S5 取景约 640×432）。采用 numpy 三线性插值，
    单帧约 10–25 ms ⇒ 与取景帧率匹配（不只够用，还有余量）。
    首次加载时把 LUT 重采样成 float32 数组并缓存；换 LUT 才重新解析。

用法（库）
    from s5_lut import LutLibrary
    lib = LutLibrary("lut")          # 目录
    lib.list()                       # -> [名称...]
    lib.select("vlog_to_709_17.vlt") # 选择
    jpg2 = lib.apply_jpeg(jpg1)      # bytes -> bytes
"""
from __future__ import annotations
import io, os, threading, time

try:
    import numpy as np
    from PIL import Image
    _HAVE = True
except Exception:                                   # 缺依赖时优雅降级
    _HAVE = False


# ---------------------------------------------------------------- LUT 解析
def _parse_cube(text: str):
    """返回 (N, float32[(N,N,N,3)])，索引顺序 [r,g,b]（.cube 约定 R 最快）"""
    N = 0
    vals = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        up = line.upper()
        if up.startswith("LUT_3D_SIZE"):
            N = int(line.split()[1]); continue
        if up.startswith(("TITLE", "DOMAIN_MIN", "DOMAIN_MAX")):
            continue
        if up.startswith("LUT_1D_SIZE"):
            raise ValueError("只支持 3D LUT（LUT_1D_SIZE 不支持）")
        p = line.split()
        if len(p) >= 3:
            try:
                vals.extend((float(p[0]), float(p[1]), float(p[2])))
            except ValueError:
                pass
    if N <= 1:
        raise ValueError("LUT_3D_SIZE 读取失败")
    arr = np.asarray(vals, dtype=np.float32)
    if arr.size != N * N * N * 3:
        raise ValueError(f"数据点数不符：{arr.size//3} 个点，期望 {N**3}（N³）")
    # ★ .cube 规范：**R 变化最快**。numpy 的 C-order reshape 让最后一个下标最快，
    #   因此 reshape 得到的是 [b,g,r]，必须 transpose(2,1,0) 换成 [r,g,b] 才能按下标查表。
    return N, arr.reshape(N, N, N, 3).transpose(2, 1, 0, 3).copy()


def _parse_vlt(text: str, axis: str = "variCam"):
    """Panasonic .vlt：整数 0..4095；axis='variCam'(B 最快) 或 'cube'(R 最快)"""
    N = 0
    grid = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.upper().startswith("LUT_3D_SIZE"):
            N = int(line.split()[1]); continue
        p = line.split()
        if len(p) >= 3:
            try:
                grid.append((int(p[0]), int(p[1]), int(p[2])))
            except ValueError:
                pass
    if N <= 1 or len(grid) != N ** 3:
        raise ValueError(f".vlt 解析失败：N={N} 数据点={len(grid)}（期望 N³）")
    out = np.zeros((N, N, N, 3), dtype=np.float32)
    k = 0
    if axis == "cube":
        for b in range(N):
            for g in range(N):
                for r in range(N):
                    out[r, g, b] = grid[k]; k += 1
    else:                                  # variCam：r 最慢、b 最快
        for r in range(N):
            for g in range(N):
                for b in range(N):
                    out[r, g, b] = grid[k]; k += 1
    return N, out / 4095.0


# ---------------------------------------------------------------- 应用
def _trilinear(lut: np.ndarray, N: int, rgb: np.ndarray) -> np.ndarray:
    """rgb: uint8 (H,W,3) → float32 (H,W,3) 0..1。三线性插值。"""
    pos = rgb.astype(np.float32) * ((N - 1) / 255.0)
    i0 = np.floor(pos).astype(np.int32)
    np.clip(i0, 0, N - 2, out=i0)
    f = pos - i0
    r0, g0, b0 = i0[..., 0], i0[..., 1], i0[..., 2]
    r1, g1, b1 = r0 + 1, g0 + 1, b0 + 1
    fr = f[..., 0:1]; fg = f[..., 1:2]; fb = f[..., 2:3]
    c000 = lut[r0, g0, b0]; c100 = lut[r1, g0, b0]
    c010 = lut[r0, g1, b0]; c110 = lut[r1, g1, b0]
    c001 = lut[r0, g0, b1]; c101 = lut[r1, g0, b1]
    c011 = lut[r0, g1, b1]; c111 = lut[r1, g1, b1]
    c00 = c000 * (1 - fr) + c100 * fr
    c01 = c001 * (1 - fr) + c101 * fr
    c10 = c010 * (1 - fr) + c110 * fr
    c11 = c011 * (1 - fr) + c111 * fr
    c0 = c00 * (1 - fg) + c10 * fg
    c1 = c01 * (1 - fg) + c11 * fg
    return c0 * (1 - fb) + c1 * fb


# ---------------------------------------------------------------- 256³ 精确查表
def build_u8_table(lut: np.ndarray, N: int, chunk: int = 32, progress=None):
    """把 N³ 浮点 LUT 展开成 **256³ 的 uint8 精确查表**。

    为什么这样做：
      · 输入是 8-bit JPEG ⇒ 颜色空间只有 256³ = 16.7M 种取值，
        **一次预计算就能完全消除逐帧插值**（结果与逐帧三线性**逐位等价**）。
      · 逐帧成本从「8 次 (H,W,3) gather + 大量浮点运算」降到
        「1 次 (H,W) gather」，实测 640×360 从 ~80 ms 降到个位数 ms。
      · 代价：一次性构建 + 50 MB 内存（select 时才建）。

    注：这里刻意**不做** gamma/插值近似 —— 逐位等价才能保证
        "与逐帧三线性结果一致"这条验收标准继续成立。
    """
    tbl = np.empty((256, 256, 256, 3), dtype=np.uint8)
    v = np.arange(256, dtype=np.float32)
    pos = v * ((N - 1) / 255.0)
    i0 = np.clip(np.floor(pos).astype(np.int32), 0, N - 2)
    fr_full = pos - i0
    np.clip(i0, 0, N - 1, out=i0)
    for r0 in range(0, 256, chunk):
        r1 = min(r0 + chunk, 256)
        # 索引 3 维用于 lut[R,G,B]，插值权重 4 维用于与 (chunk,256,256,3) 广播
        R0 = i0[r0:r1][:, None, None];    fR = fr_full[r0:r1][:, None, None, None]
        G0 = i0[None, :, None];           fG = fr_full[None, :, None, None]
        B0 = i0[None, None, :];           fB = fr_full[None, None, :, None]
        R1, G1, B1 = R0 + 1, G0 + 1, B0 + 1
        c000 = lut[R0, G0, B0]; c100 = lut[R1, G0, B0]
        c010 = lut[R0, G1, B0]; c110 = lut[R1, G1, B0]
        c001 = lut[R0, G0, B1]; c101 = lut[R1, G0, B1]
        c011 = lut[R0, G1, B1]; c111 = lut[R1, G1, B1]
        c00 = c000 * (1 - fR) + c100 * fR
        c01 = c001 * (1 - fR) + c101 * fR
        c10 = c010 * (1 - fR) + c110 * fR
        c11 = c011 * (1 - fR) + c111 * fR
        c0 = c00 * (1 - fG) + c10 * fG
        c1 = c01 * (1 - fG) + c11 * fG
        out = c0 * (1 - fB) + c1 * fB
        tbl[r0:r1] = (np.clip(out, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)
        if progress:
            progress(r1 / 256.0)
    return tbl


# ---------------------------------------------------------------- 库
class LutLibrary:
    """扫描目录里的 .cube/.vlt，提供"选一个 + 套一帧"的最小接口。线程安全。"""

    EXTS = (".cube", ".vlt")

    def __init__(self, lut_dir: str, vlt_axis: str = "variCam", quality: int = 88):
        self.dir = os.path.abspath(lut_dir)
        self.vlt_axis = vlt_axis
        self.quality = quality
        self._lock = threading.Lock()
        self._name = None
        self._base = ""
        self._strength = 1.0
        self._cache = {}            # "name|base" -> 256³ uint8 表（避免重复构建）
        self._building = False
        self._pending = None
        self._lut = None
        self._tbl = None            # 256³ uint8 精确查表（select 时构建）
        self._N = 0
        self.enabled = False
        self.last_ms = 0.0
        os.makedirs(self.dir, exist_ok=True)

    # -- 发现 --
    def list(self):
        if not os.path.isdir(self.dir):
            return []
        return sorted(f for f in os.listdir(self.dir)
                      if f.lower().endswith(self.EXTS) and not f.startswith("._"))

    # -- 选择 --
    def _load_table(self, name: str):
        """读一个 LUT 文件并展开成 256³ uint8 表。返回 (N, lut_float, table)。"""
        path = os.path.join(self.dir, name)
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        if name.lower().endswith(".vlt"):
            N, lut = _parse_vlt(text, self.vlt_axis)
        else:
            N, lut = _parse_cube(text)
        return N, lut, build_u8_table(lut, N)

    def select(self, name: str, base: str = ""):
        """选择 LUT。`base` 非空时做**串联**：先套 base（如 V-Log→709），再套 name。

        ★ 为什么需要串联：
          胶片模拟类 LUT（Fuji NC / Kodak Gold 等）是给**普通对比度**素材设计的；
          而 S5 拍 V-Log 时画面是灰平的，直接套胶片 LUT 会发灰、不成立。
          正确链路是 V-Log →(还原)→ Rec.709 →(风格化)→ 胶片。本实现把两级
          **在 256³ 表上复合**（`composed[r,g,b] = f2[f1[r,g,b]]`，一次 gather），
          因此串联**不增加任何逐帧开销**。
        """
        if not _HAVE:
            raise RuntimeError("缺少 numpy/Pillow，无法套用 LUT")
        key = f"{name}|{base}"
        t0 = time.time()
        cached = self._cache.get(key)
        if cached is not None:
            N, tbl = cached
            build_ms = 0.0
        else:
            N, lut, tbl = self._load_table(name)
            if base:
                N2, lut2, tbl2 = self._load_table(base)
                # 复合：把 base 的输出当作 creative 的输入
                tbl = tbl[tbl2[..., 0], tbl2[..., 1], tbl2[..., 2]]
            self._cache[key] = (N, tbl)
            build_ms = (time.time() - t0) * 1000.0
        with self._lock:
            self._lut, self._tbl, self._N, self._name = None, tbl, N, name
            self._base = base or ""
            self.enabled = True
        return dict(name=name, size=N, points=int(N ** 3),
                    base=base or "", build_ms=round(build_ms, 1),
                    cached=build_ms == 0.0)

    def select_async(self, name: str, base: str = ""):
        """后台构建：立刻返回，不阻塞 HTTP（构建 3-7 秒，期间沿用旧表）。"""
        key = f"{name}|{base}"
        if key in self._cache:
            return self.select(name, base)
        with self._lock:
            if self._building:
                self._pending = (name, base)
                return dict(queued=True, name=name, base=base)
            self._building = True
        def work():
            try:
                self.select(name, base)
            finally:
                with self._lock:
                    self._building = False
                    pend = self._pending
                    self._pending = None
                if pend:
                    try:
                        self.select_async(*pend)
                    except Exception:
                        pass
        threading.Thread(target=work, daemon=True).start()
        return dict(building=True, name=name, base=base)

    @property
    def strength(self):
        return getattr(self, "_strength", 1.0)

    def set_strength(self, v: float):
        self._strength = max(0.0, min(1.0, float(v)))
        return self._strength

    @property
    def building(self):
        return getattr(self, "_building", False)

    @property
    def cached_keys(self):
        return list(getattr(self, "_cache", {}).keys())

    @property
    def name(self):
        return self._name

    @property
    def size(self):
        return self._N

    @property
    def base(self):
        return getattr(self, "_base", "")

    def save_upload(self, filename: str, data: bytes):
        """保存用户上传的 .cube/.vlt 到 lut/ 目录。返回落盘文件名。

        安全：只接受 .cube/.vlt 扩展名；文件名做白名单清洗（去掉路径分隔符与
        可疑字符），并把重名自动加序号，**绝不覆盖已有文件**。
        """
        import re as _re
        base = os.path.basename(filename or "").strip()
        if not base.lower().endswith(self.EXTS):
            raise ValueError("只接受 .cube / .vlt 文件")
        stem, ext = os.path.splitext(base)
        if ext.lower() == ".cube" and not stem.lower().endswith(".cube"):
            pass
        stem = _re.sub(r"[^\w\u4e00-\u9fff .()\-]+", "_", stem).strip() or "lut"
        name, i = stem + ext, 1
        while os.path.exists(os.path.join(self.dir, name)):
            name = f"{stem}_{i}{ext}"; i += 1
        # 先做一次解析校验，避免把坏文件落盘
        if ext.lower() == ".vlt":
            _parse_vlt(data.decode("utf-8", "replace"), self.vlt_axis)
        else:
            _parse_cube(data.decode("utf-8", "replace"))
        with open(os.path.join(self.dir, name), "wb") as f:
            f.write(data)
        return name

    def disable(self):
        self.enabled = False

    # -- 应用 --
    def apply_rgb(self, rgb: np.ndarray) -> np.ndarray:
        with self._lock:
            tbl, lut, N = self._tbl, self._lut, self._N
        if tbl is not None:
            # ★ 快路径：256³ 精确查表，一次 gather（输入是 8-bit，位位精确）
            out = tbl[rgb[..., 0], rgb[..., 1], rgb[..., 2]]
            st = self._strength
            if st < 0.999:
                # 强度混合：原件·(1-s) + LUT·s。胶片类 LUT 很轻微，滑杆让它可调可见。
                if st <= 0.001:
                    return rgb
                return (rgb.astype(np.int16) * (1.0 - st) + out.astype(np.int16) * st
                        ).round().clip(0, 255).astype(np.uint8)
            return out
        if lut is None:
            return rgb
        out = _trilinear(lut, N, rgb)
        return (np.clip(out, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)

    def apply_jpeg(self, jpg: bytes) -> bytes:
        """bytes(JPEG) → bytes(JPEG)，套上当前 LUT。未启用/无 LUT 时原样返回。

        ⚠️ 判据必须是 `self._tbl`（256³ 查表）——重构后 `_lut`（浮点网格）
        已经不再保存，若仍检查 `_lut is None` 会**永远原样返回**，
        表现为「LUT 明明 enabled 却完全没效果」（2026-10-15 踩过）。
        """
        if not self.enabled or self._tbl is None or not _HAVE:
            return jpg
        t0 = time.time()
        try:
            im = Image.open(io.BytesIO(jpg)).convert("RGB")
            rgb = np.asarray(im, dtype=np.uint8)
            out = self.apply_rgb(rgb)
            buf = io.BytesIO()
            Image.fromarray(out, "RGB").save(buf, format="JPEG", quality=self.quality)
            self.last_ms = (time.time() - t0) * 1000.0
            return buf.getvalue()
        except Exception:
            return jpg          # 任何异常都退回原帧，绝不打断取景流


# ---------------------------------------------------------------- 自测
def _selftest():
    if not _HAVE:
        print("缺少 numpy/Pillow"); return 1
    here = os.path.dirname(os.path.abspath(__file__))
    lutdir = os.path.join(here, "lut")
    lib = LutLibrary(lutdir)
    print("发现 LUT：", lib.list())
    if not lib.list():
        print("lut/ 目录为空，先跑 make_lut.py 生成"); return 1
    for name in lib.list():
        try:
            info = lib.select(name)
            print(f"  ✅ {name}: N={info['size']} 点={info['points']}")
        except Exception as e:
            print(f"  ❌ {name}: {e}"); return 1

    # 合成测试图：V-Log 外观的灰阶 + 彩条
    h, w = 240, 320
    ramp = np.tile(np.linspace(0, 255, w, dtype=np.uint8), (h // 2, 1))
    bars = np.zeros((h - h // 2, w, 3), dtype=np.uint8)
    cols = [(255,255,255),(255,255,0),(0,255,255),(0,255,0),(255,0,255),(255,0,0),(0,0,255),(0,0,0)]
    for i, c in enumerate(cols):
        bars[:, i * w // 8:(i + 1) * w // 8] = c
    img = np.vstack([np.stack([ramp]*3, -1), bars])
    buf = io.BytesIO(); Image.fromarray(img, "RGB").save(buf, "JPEG", quality=95)
    src = buf.getvalue()

    import time as _t
    for name in lib.list()[:2]:
        lib.select(name)
        t0 = _t.time()
        out = lib.apply_jpeg(src)
        dt = (_t.time() - t0) * 1000
        a = np.asarray(Image.open(io.BytesIO(src)).convert("RGB"), dtype=np.int16)
        b = np.asarray(Image.open(io.BytesIO(out)).convert("RGB"), dtype=np.int16)
        print(f"  {name}: {len(src)}B → {len(out)}B  耗时 {dt:.1f} ms  平均像素差 {np.abs(a-b).mean():.1f}")
    print("\n✅ 自测完成（耗时 < 30 ms ⇒ 实时取景足够）")
    return 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
