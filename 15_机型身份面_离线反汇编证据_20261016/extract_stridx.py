#!/usr/bin/env python3
"""
extract_stridx.py —— ARM/Thumb ELF 字符串 xref 提取器（机型身份面离线审计工具）。

用途：从 objdump 反汇编输出里，把所有 `ldr rN, [pc, #imm]  @ POOL` 形式引用的
字面池条目解析出来，读回池里的 4 字节指针，还原成 C 字符串，输出 "code_addr -> string" 表。
用于快速回答："这个字符串（如 pana:X_FromCP / X_Panasonic_Cam_Sync）在哪里被用了"。

前提（本项目的 G100 rootfs 二进制满足）：vaddr = 文件偏移 + 0x10000，可用
`arm-none-eabi-readelf -S <elf>` 核对（.rodata 的 Addr 与 Off 之差就是这个常量）。

用法：
  arm-none-eabi-objdump -d <elf> > /tmp/x.asm
  python3 extract_stridx.py <elf> /tmp/x.asm out.txt [--delta 0x10000] [--minlen 3]

输出：out.txt 每行 "0x<code_addr>  <reg>  pool=0x<pool>  '<string>'"；同时打印统计。
"""
import re
import struct
import sys


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    elf, asm, out = sys.argv[1], sys.argv[2], sys.argv[3]
    delta = 0x10000
    minlen = 3
    a = sys.argv[4:]
    i = 0
    while i < len(a):
        if a[i] == "--delta":
            delta = int(a[i + 1], 0); i += 2
        elif a[i] == "--minlen":
            minlen = int(a[i + 1], 0); i += 2
        else:
            i += 1

    data = open(elf, "rb").read()

    def cstr(vaddr, maxn=160):
        o = vaddr - delta
        if not (0 <= o < len(data)):
            return None
        e = data.find(b"\0", o)
        if e < 0 or e - o > maxn:
            return None
        s = data[o:e]
        try:
            s = s.decode("ascii")
        except Exception:
            return None
        return s if len(s) >= minlen else None

    ldr = re.compile(
        r"^\s+([0-9a-f]+):\s+[0-9a-f]{8}\s+ldr\s+(r\d+),\s+\[pc, #\d+\]\s+@\s+([0-9a-f]+)")
    rows = []
    for line in open(asm):
        m = ldr.match(line)
        if not m:
            continue
        code = int(m.group(1), 16)
        reg = m.group(2)
        pool = int(m.group(3), 16)
        o = pool - delta
        if not (0 <= o + 4 <= len(data)):
            continue
        ptr = struct.unpack("<I", data[o:o + 4])[0]
        s = cstr(ptr)
        if s:
            rows.append((code, reg, pool, s))

    with open(out, "w") as f:
        f.write("# %s 字符串 xref（ldr rN,[pc,#imm] -> 字面池 -> C 字符串）共 %d 条\n"
                % (elf.split("/")[-1], len(rows)))
        for code, reg, pool, s in rows:
            f.write("0x%06x  %-4s pool=0x%06x  %r\n" % (code, reg, pool, s))
    print("[+] %d 条 -> %s" % (len(rows), out))


if __name__ == "__main__":
    main()
