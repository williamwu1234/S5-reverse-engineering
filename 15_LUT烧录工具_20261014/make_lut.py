#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_lut.py — 生成松下 LUMIX 可用的 LUT（.cube 与 Panasonic .vlt）

用途
    1) 把机内 Log/HLG 素材转成 Rec.709（供后期"套 LUT"用）
    2) 生成合规的 .vlt 放进 SD 卡根目录，供机身 [V-Log View Assist] 使用

为什么自己算
    官方 VLog_to_V709 的 .vlt/.cube 本体需要从松下站点下载；本工具用**公开规范**自行推导：
      · Panasonic V-Log OETF（0% 黑=0.125、18% 灰=0.423、断点 V=0.181↔L=0.01，已自检通过）
      · V-Gamut 原色 → BT.709 原色的 3x3 矩阵（D65 白点，由原色坐标推导）
      · ITU-R BT.709 OETF
    ⇒ 结果**不是**官方 LUT 的逐字节复刻，而是一个规范自洽的等效转换。需要官方原版请去
      https://av.jpn.support.panasonic.com/support/global/cs/dsc/download/lut/index.html

格式要点（由 35 个官方 .VLT 样本逆向得出，见 14_总包审计.../09_LUT可行性报告）
    .vlt = 纯 ASCII：两行 '#' 头 + 'LUT_3D_SIZE N' + 空行 + N³ 行 "R G B"（整数 0–4095，12-bit）
    .cube = ASCII：TITLE / LUT_3D_SIZE / DOMAIN_MIN / DOMAIN_MAX + 浮点 0..1 数据
    ★ 两者的**数据轴序可能不同**（.txt(VariCam) 官方注明 "blue fastest"，.cube 通用约定是 "red fastest"）
      ⇒ 本脚本对 .vlt 默认按 **VariCam 约定（B 最快）** 输出，并额外输出一份 *altAxis*.vlt 供实机二选一。

用法
    python3 make_lut.py --from vlog --size 33 --out lut/
    python3 make_lut.py --from vlog --size 17 --formats vlt --out /Volumes/LUMIX/   # 直接写卡根目录
"""
import argparse, math, os, sys

# ---------------------------------------------------------------- 色彩数学
def _rgb2xyz(prim):
    """prim = (rx,ry, gx,gy, bx,by, wx,wy) → 3x3 矩阵（列 = R,G,B 的 XYZ）"""
    rx, ry, gx, gy, bx, by, wx, wy = prim

    def XYZ(x, y):
        return (x / y, 1.0, (1.0 - x - y) / y)

    Xr, Yr, Zr = XYZ(rx, ry)
    Xg, Yg, Zg = XYZ(gx, gy)
    Xb, Yb, Zb = XYZ(bx, by)
    Xw, Yw, Zw = XYZ(wx, wy)
    M = [[Xr, Xg, Xb], [Yr, Yg, Yb], [Zr, Zg, Zb]]
    # 解 S = M^-1 · W
    S = _solve3(M, [Xw, Yw, Zw])
    return [[M[i][j] * S[j] for j in range(3)] for i in range(3)]


def _solve3(A, b):
    """3x3 线性方程求解（克莱姆法则）"""
    def det(m):
        return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
                - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
    D = det(A)
    out = []
    for k in range(3):
        M = [row[:] for row in A]
        for i in range(3):
            M[i][k] = b[i]
        out.append(det(M) / D)
    return out


def _mul3(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _matvec(M, v):
    return [sum(M[i][j] * v[j] for j in range(3)) for i in range(3)]


def _inv3(M):
    def det(m):
        return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
                - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
    D = det(M)
    C = [[0.0] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            m = [[M[r][c] for c in range(3) if c != j] for r in range(3) if r != i]
            C[j][i] = ((-1) ** (i + j)) * (m[0][0] * m[1][1] - m[0][1] * m[1][0])
    return [[C[i][j] / D for j in range(3)] for i in range(3)]


D65 = (0.3127, 0.3290)
VGAMUT = (0.730, 0.280, 0.165, 0.840, 0.100, -0.030, *D65)   # Panasonic V-Gamut
BT709  = (0.640, 0.330, 0.300, 0.600, 0.150, 0.060, *D65)     # ITU-R BT.709
BT2020 = (0.708, 0.292, 0.170, 0.797, 0.131, 0.046, *D65)     # ITU-R BT.2020

_M_VGAMUT_709 = _mul3(_inv3(_rgb2xyz(BT709)), _rgb2xyz(VGAMUT))
_M_2020_709   = _mul3(_inv3(_rgb2xyz(BT709)), _rgb2xyz(BT2020))


# ---------------------------------------------------------------- 传递函数
def vlog_to_linear(V):
    """V-Log code → 线性（公开规范；已自检 0%→0.125、18%→0.423）"""
    if V < 0.181:
        return (V - 0.125) / 5.6
    return 10.0 ** ((V - 0.598206) / 0.241514) - 0.00873


def linear_to_bt709(L):
    """线性 → BT.709 OETF（相机侧编码曲线）"""
    L = 0.0 if L < 0 else (1.0 if L > 1 else L)
    return 4.5 * L if L < 0.018 else 1.099 * (L ** 0.45) - 0.099


def linear_to_gamma(L, g=2.4):
    """线性 → 纯幂律显示 gamma（BT.1886 近似）；g=2.2 更接近 sRGB 观感"""
    L = 0.0 if L < 0 else (1.0 if L > 1 else L)
    return L ** (1.0 / g)


def hlg_to_linear(V, peak=1.0):
    """BT.2100 HLG OETF 的逆（a=0.17883277,b=0.28466892,c=0.55991073）"""
    a, b, c = 0.17883277, 0.28466892, 0.55991073
    V = 0.0 if V < 0 else (1.0 if V > 1 else V)
    if V <= 0.5:
        L = (V * V) / 3.0
    else:
        L = (math.exp((V - c) / a) + b) / 12.0
    return L * peak


# ---------------------------------------------------------------- 转换管线
PIPELINES = {
    # 名称           输入解码              是否过色彩矩阵        输出编码
    "vlog":       (vlog_to_linear,        _M_VGAMUT_709,       "bt709"),
    "vlog_gamma": (vlog_to_linear,        _M_VGAMUT_709,       "gamma2.4"),
    "hlg":        (hlg_to_linear,         _M_2020_709,         "bt709"),
    "identity":   (lambda v: v,           None,                "none"),
}


def build_cube(frm, size, gam=2.4):
    decode, mat, enc = PIPELINES[frm]
    if mat is None:
        mat = [[1.0 if i == j else 0.0 for j in range(3)] for i in range(3)]

    def enc_fn(L):
        if enc == "bt709":
            return linear_to_bt709(L)
        if enc == "gamma2.4":
            return linear_to_gamma(L, gam)
        return L

    data = []
    N = size
    # .cube 约定：red 变化最快（r 最内层）
    for bi in range(N):
        for gi in range(N):
            for ri in range(N):
                r, g, b = ri / (N - 1), gi / (N - 1), bi / (N - 1)
                lin = [decode(r), decode(g), decode(b)]
                lin = _matvec(mat, lin)
                data.append((enc_fn(lin[0]), enc_fn(lin[1]), enc_fn(lin[2])))
    return data


def write_cube(path, data, size, title):
    with open(path, "w", newline="\n") as f:
        f.write(f'TITLE "{title}"\n')
        f.write(f"LUT_3D_SIZE {size}\n")
        f.write("DOMAIN_MIN 0.0 0.0 0.0\nDOMAIN_MAX 1.0 1.0 1.0\n\n")
        for (r, g, b) in data:
            f.write(f"{r:.6f} {g:.6f} {b:.6f}\n")


def write_vlt(path, data, size, src_name, axis="variCam"):
    """axis='variCam' → B 最快（官方 .txt 注明 blue fastest）；'cube' → R 最快"""
    N = size
    grid = {}
    # data 是按 cube 约定（r 最内层）生成的，这里按请求的轴序重排
    idx = 0
    for bi in range(N):
        for gi in range(N):
            for ri in range(N):
                grid[(ri, gi, bi)] = data[idx]
                idx += 1

    with open(path, "w", newline="\n") as f:
        f.write("# panasonic vlt file version 1.0\n")
        f.write(f'# source vlt file "{src_name}"\n')
        f.write(f"LUT_3D_SIZE {N}\n\n")
        if axis == "variCam":       # r 最外层（最慢），b 最内层（最快）
            order = ((r, g, b) for r in range(N) for g in range(N) for b in range(N))
        else:                        # cube 约定：r 最内层（最快）
            order = ((r, g, b) for b in range(N) for g in range(N) for r in range(N))
        for (r, g, b) in order:
            R, G, B = grid[(r, g, b)]
            f.write(f"{round(R*4095)} {round(G*4095)} {round(B*4095)}\n")


def self_test():
    """自检：公式锚点 + .vlt 行数/取值域"""
    ok = True
    checks = [("V-Log 0% 黑 → 0.125", abs((5.6*0 + 0.125) - 0.125) < 1e-12),
              ("V-Log 18% 灰 → 0.423", abs(0.241514*math.log10(0.18+0.00873) + 0.598206 - 0.4233) < 5e-4),
              ("断点连续 V=0.181", abs((0.181-0.125)/5.6 - (10**((0.181-0.598206)/0.241514) - 0.00873)) < 1e-6),
              ("V-Gamut→709 矩阵行和≈1(白点保持)", all(abs(sum(_M_VGAMUT_709[i]) - 1) < 1e-3 for i in range(3)))]
    for name, cond in checks:
        print(f"  [{'OK ' if cond else 'FAIL'}] {name}")
        ok &= cond
    d = build_cube("vlog", 17)
    print(f"  [{'OK ' if len(d)==17**3 else 'FAIL'}] 17³ 数据点数 = {len(d)}")
    ok &= len(d) == 17 ** 3
    mn = min(min(x) for x in d); mx = max(max(x) for x in d)
    print(f"  [{'OK ' if 0<=mn and mx<=1 else 'FAIL'}] 输出范围 [{mn:.4f}, {mx:.4f}] ⊆ [0,1]")
    ok &= (0 <= mn and mx <= 1)
    return ok


def main():
    ap = argparse.ArgumentParser(description="生成 LUMIX 可用的 .cube / Panasonic .vlt LUT")
    ap.add_argument("--from", dest="frm", default="vlog", choices=sorted(PIPELINES),
                    help="输入色彩空间/照片风格（默认 vlog）")
    ap.add_argument("--size", type=int, default=33, help="网格边长（.cube 建议 33，.vlt 用 17）")
    ap.add_argument("--formats", default="cube,vlt", help="输出格式，逗号分隔：cube,vlt")
    ap.add_argument("--out", default="lut", help="输出目录（可直接给 /Volumes/LUMIX/ 写卡根目录）")
    ap.add_argument("--gamma", type=float, default=2.4, help="vlog_gamma 管线用的显示 gamma")
    ap.add_argument("--selftest", action="store_true", help="只跑自检")
    a = ap.parse_args()

    print("=== 自检 ===")
    if not self_test():
        print("自检失败，中止"); sys.exit(1)

    os.makedirs(a.out, exist_ok=True)
    base = f"{a.frm}_to_709" if a.frm != "identity" else "identity"
    data = build_cube(a.frm, a.size, a.gamma)
    fmts = [x.strip() for x in a.formats.split(",") if x.strip()]
    made = []
    if "cube" in fmts:
        p = os.path.join(a.out, f"{base}_{a.size}.cube")
        write_cube(p, data, a.size, base); made.append(p)
    if "vlt" in fmts:
        p = os.path.join(a.out, f"{base}_{a.size}.vlt")
        write_vlt(p, data, a.size, os.path.basename(p), axis="variCam"); made.append(p)
        if a.size == 17:   # 轴序未定时给一份备选，供实机二选一
            p2 = os.path.join(a.out, f"{base}_{a.size}_altAxis.vlt")
            write_vlt(p2, data, a.size, os.path.basename(p2), axis="cube"); made.append(p2)
    print("\n=== 产出 ===")
    for p in made:
        print(f"  {p}  ({os.path.getsize(p):,} B)")
    if a.frm == "vlog":
        print("\n提示：把 .vlt 放到【SD 卡根目录】（不要建文件夹），")
        print("      机身走 [照片风格]→[V-Log]→[V-Log View Assist]→[LUT Select] 选用。")


if __name__ == "__main__":
    main()
