/*
 * s5_usb_listen.c — passively listen on the DC-S5 service channel's IN endpoints.
 *
 * Why
 * ---
 * The service-mode personality 04da:2370 is vendor class 0xFF/0xA0/0xB0 and has
 * THREE endpoints:
 *     EP 0x01  OUT  bulk       mps 512
 *     EP 0x82  IN   bulk       mps 512
 *     EP 0x83  IN   interrupt  mps 64  interval 16
 * That is a command/response + asynchronous-event architecture, not a
 * write-only firmware sink. A previous attempt formatted requests as PTP and
 * listened on the BULK IN endpoint only -- it never listened on the interrupt
 * endpoint, which is where an event-driven protocol usually announces itself.
 *
 * This tool sends NOTHING by default. It just reads the two IN endpoints and
 * hexdumps whatever the device volunteers. If the camera emits any event on
 * its own, the dump gives us the protocol's header/length/type layout.
 *
 * Modes
 *   (default)   passive only -- zero writes
 *   --ptp       additionally send ONE PTP OpenSession (0x1002) on bulk OUT,
 *               then keep listening. OpenSession is the most benign PTP
 *               command there is, and the project already sends it.
 *
 * Safety: no SetConfiguration unless opening the interface requires it, no
 * bulk writes (except the single opt-in --ptp probe), no vendor opcodes.
 *
 * Build: clang -O2 -framework IOKit -framework CoreFoundation \
 *            -o s5_usb_listen s5_usb_listen.c
 * Usage: ./s5_usb_listen [seconds] [vid] [pid] [--ptp]
 *        defaults: seconds=20, vid=0x04da, pid=0x2370
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>
#include <time.h>
#include <IOKit/IOKitLib.h>
#include <IOKit/IOCFPlugIn.h>
#include <IOKit/usb/IOUSBLib.h>
#include <IOKit/usb/USBSpec.h>
#include <CoreFoundation/CoreFoundation.h>

#define DEF_VID 0x04DA
#define DEF_PID 0x2370
#define BUFSZ   4096

static IOUSBDeviceInterface    **g_dev  = NULL;
static IOUSBInterfaceInterface **g_intf = NULL;
static UInt8 g_pipe_out = 0, g_pipe_in = 0, g_pipe_int = 0;

static double now_s(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

static void hexdump(const unsigned char *p, size_t n, const char *indent)
{
    for (size_t i = 0; i < n; i += 16) {
        printf("%s%04zx  ", indent, i);
        for (size_t j = 0; j < 16; j++)
            printf(j < n - i ? "%02x " : "   ", p[i + j]);
        printf(" ");
        for (size_t j = 0; j < 16 && i + j < n; j++) {
            unsigned char c = p[i + j];
            putchar(c >= 32 && c < 127 ? c : '.');
        }
        printf("\n");
    }
}

/* Read one IN transfer with a timeout. Returns bytes, or -1 on error/timeout. */
static int read_pipe(UInt8 pipe, void *buf, UInt32 len, UInt32 timeout_ms, IOReturn *err)
{
    IOUSBInterfaceInterface183 **i183 = (IOUSBInterfaceInterface183 **)g_intf;
    UInt32 got = len;
    IOReturn r = (*i183)->ReadPipeTO(i183, pipe, buf, &got, timeout_ms, timeout_ms);
    if (err) *err = r;
    if (r) return -1;
    return (int)got;
}

static int open_device(UInt32 vid, UInt32 pid)
{
    CFMutableDictionaryRef m = IOServiceMatching(kIOUSBDeviceClassName);
    CFNumberRef nv = CFNumberCreate(kCFAllocatorDefault, kCFNumberSInt32Type, &vid);
    CFNumberRef np = CFNumberCreate(kCFAllocatorDefault, kCFNumberSInt32Type, &pid);
    CFDictionarySetValue(m, CFSTR(kUSBVendorID), nv);
    CFDictionarySetValue(m, CFSTR(kUSBProductID), np);
    CFRelease(nv); CFRelease(np);

    io_service_t svc = IOServiceGetMatchingService(kIOMainPortDefault, m);
    if (!svc) { fprintf(stderr, "device %04x:%04x not found\n", vid, pid); return -1; }

    IOCFPlugInInterface **plug = NULL; SInt32 score = 0;
    if (IOCreatePlugInInterfaceForService(svc, kIOUSBDeviceUserClientTypeID,
                                          kIOCFPlugInInterfaceID, &plug, &score) || !plug) {
        fprintf(stderr, "plug-in creation failed\n"); IOObjectRelease(svc); return -1;
    }
    (*plug)->QueryInterface(plug, CFUUIDGetUUIDBytes(kIOUSBDeviceInterfaceID), (LPVOID *)&g_dev);
    (*plug)->Release(plug);
    IOObjectRelease(svc);
    if (!g_dev) { fprintf(stderr, "QueryInterface failed\n"); return -1; }

    IOReturn r = (*g_dev)->USBDeviceOpen(g_dev);
    if (r) r = (*g_dev)->USBDeviceOpenSeize(g_dev);
    if (r) { fprintf(stderr, "USBDeviceOpen(Seize) -> 0x%08x\n", r); return -1; }
    printf("[device opened]\n");
    return 0;
}

static int open_interface(void)
{
    IOUSBFindInterfaceRequest req;
    req.bInterfaceClass    = kIOUSBFindInterfaceDontCare;
    req.bInterfaceSubClass = kIOUSBFindInterfaceDontCare;
    req.bInterfaceProtocol = kIOUSBFindInterfaceDontCare;
    req.bAlternateSetting  = kIOUSBFindInterfaceDontCare;

    io_iterator_t it = 0;
    if ((*g_dev)->CreateInterfaceIterator(g_dev, &req, &it)) return -1;

    io_service_t ifsvc;
    while ((ifsvc = IOIteratorNext(it))) {
        IOCFPlugInInterface **ip = NULL; SInt32 sc = 0;
        if (!IOCreatePlugInInterfaceForService(ifsvc, kIOUSBInterfaceUserClientTypeID,
                                               kIOCFPlugInInterfaceID, &ip, &sc) && ip) {
            IOUSBInterfaceInterface **intf = NULL;
            (*ip)->QueryInterface(ip, CFUUIDGetUUIDBytes(kIOUSBInterfaceInterfaceID), (LPVOID *)&intf);
            (*ip)->Release(ip);
            if (intf) {
                IOReturn r = (*intf)->USBInterfaceOpen(intf);
                if (r) {
                    IOUSBInterfaceInterface190 **i190 = (IOUSBInterfaceInterface190 **)intf;
                    r = (*i190)->USBInterfaceOpenSeize(i190);
                }
                if (!r) {
                    (*intf)->SetAlternateInterface(intf, 0);
                    g_intf = intf;
                    IOObjectRelease(ifsvc);
                    IOObjectRelease(it);
                    return 0;
                }
                fprintf(stderr, "  interface open failed 0x%08x\n", r);
                (*intf)->Release(intf);
            }
        }
        IOObjectRelease(ifsvc);
    }
    IOObjectRelease(it);
    return -1;
}

static void find_pipes(void)
{
    UInt8 n = 0;
    (*g_intf)->GetNumEndpoints(g_intf, &n);
    printf("[interface has %u endpoints]\n", n);
    for (UInt8 i = 1; i <= n; i++) {
        UInt8 dir = 0, num = 0, tt = 0; UInt16 mps = 0; UInt8 iv = 0;
        if ((*g_intf)->GetPipeProperties(g_intf, i, &dir, &num, &tt, &mps, &iv)) continue;
        const char *tn = (tt == kUSBBulk) ? "bulk" :
                         (tt == kUSBInterrupt) ? "interrupt" :
                         (tt == kUSBControl) ? "control" : "isochronous";
        printf("  pipe %u: EP 0x%02x %s %s mps=%u interval=%u\n",
               i, num | (dir == kUSBIn ? 0x80 : 0x00),
               dir == kUSBIn ? "IN " : "OUT", tn, mps, iv);
        if (tt == kUSBBulk && dir == kUSBOut) g_pipe_out = i;
        if (tt == kUSBBulk && dir == kUSBIn)  g_pipe_in  = i;
        if (tt == kUSBInterrupt && dir == kUSBIn) g_pipe_int = i;
    }
    printf("[pipes] bulkOut=%u bulkIn=%u intIn=%u\n\n", g_pipe_out, g_pipe_in, g_pipe_int);
}

/* One minimal PTP OpenSession container: 16-byte cmd block (0x1002), tid=1 */
static int send_bytes(const unsigned char *data, UInt32 len, const char *what)
{
    IOUSBInterfaceInterface183 **i183 = (IOUSBInterfaceInterface183 **)g_intf;
    IOReturn r = (*i183)->WritePipeTO(i183, g_pipe_out, (void *)data, len, 1500, 1500);
    printf("[write] %s: %u bytes -> 0x%08x  %s\n", what, (unsigned)len, r,
           r == 0 ? "** ACCEPTED by the device **"
                  : (r == 0xe0004051 ? "(timeout: device NAKed, did not accept)"
                                     : "(error)"));
    fflush(stdout);
    return r == 0 ? 0 : -1;
}

static int send_ptp_opensession(void)
{
    unsigned char cmd[16];
    memset(cmd, 0, sizeof(cmd));
    UInt32 len = 16;
    cmd[0] = len & 0xFF; cmd[1] = (len >> 8) & 0xFF; cmd[2] = (len >> 16) & 0xFF; cmd[3] = (len >> 24) & 0xFF;
    cmd[4] = 1;                       /* type = command block */
    cmd[8]  = 0x02; cmd[9] = 0x10;    /* opcode 0x1002 OpenSession, little endian */
    cmd[12] = 0x01;                   /* transaction id = 1 */
    return send_bytes(cmd, sizeof(cmd), "PTP OpenSession (0x1002)");
}

/* parse "01 02 03" or "010203" into bytes; returns count or -1 */
static int parse_hex(const char *s, unsigned char *out, int max)
{
    int n = 0;
    while (*s && n < max) {
        while (*s == ' ' || *s == ',' || *s == ':') s++;
        if (!*s) break;
        char b[3] = {0, 0, 0};
        int k = 0;
        while (*s && k < 2 && isxdigit((unsigned char)*s)) b[k++] = *s++;
        if (k == 0) break;
        out[n++] = (unsigned char)strtoul(b, NULL, 16);
    }
    return n;
}

int main(int argc, char **argv)
{
    int seconds = 20, do_ptp = 0, do_tryall = 0;
    UInt32 vid = DEF_VID, pid = DEF_PID;
    int saw_pos = 0;
    const char *hexarg = NULL;
    int force_cfg = -1;

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--ptp")) do_ptp = 1;
        else if (!strcmp(argv[i], "--tryall")) do_tryall = 1;
        else if (!strcmp(argv[i], "--cfg") && i + 1 < argc) force_cfg = (int)strtol(argv[++i], NULL, 0);
        else if (!strcmp(argv[i], "--hex") && i + 1 < argc) hexarg = argv[++i];
        else if (!strncmp(argv[i], "0x", 2) || (argv[i][0] >= '0' && argv[i][0] <= '9')) {
            if (!saw_pos) { seconds = atoi(argv[i]); saw_pos = 1; }
            else if (vid == DEF_VID) vid = (UInt32)strtoul(argv[i], NULL, 0);
            else pid = (UInt32)strtoul(argv[i], NULL, 0);
        }
    }
    if (seconds < 1) seconds = 1;

    printf("===============================================================\n");
    printf(" Passive listener for %04x:%04x  (%d s)\n", vid, pid, seconds);
    printf(" mode: %s\n",
           hexarg ? "--hex payload" : do_tryall ? "--tryall framings" :
           do_ptp  ? "--ptp OpenSession" : "PASSIVE (sends nothing)");
    if (force_cfg >= 0) printf(" SetConfiguration(%d) forced before interface open\n", force_cfg);
    printf(" No vendor opcodes.\n");
    printf("===============================================================\n\n");

    if (open_device(vid, pid)) return 1;

    /* report and optionally change the active configuration */
    {
        UInt8 cur = 0;
        IOReturn gr = (*g_dev)->GetConfiguration(g_dev, &cur);
        printf("[GetConfiguration] -> 0x%08x, current configuration value = %u\n", gr, cur);
    }
    if (force_cfg >= 0) {
        IOReturn sr = (*g_dev)->SetConfiguration(g_dev, (UInt8)force_cfg);
        printf("[SetConfiguration(%d)] -> 0x%08x\n", force_cfg, sr);
        sleep(1);
    }

    if (open_interface()) { fprintf(stderr, "could not open interface\n"); return 1; }
    printf("[interface 0 opened, alt 0]\n");
    find_pipes();

    if (!g_pipe_int && !g_pipe_in) {
        fprintf(stderr, "no IN endpoints found; nothing to listen on\n");
        return 1;
    }

    /* ---- write probes: only when explicitly asked ---- */
    if (hexarg) {
        unsigned char payload[512];
        int n = parse_hex(hexarg, payload, sizeof(payload));
        if (n <= 0) { fprintf(stderr, "--hex parsed to 0 bytes\n"); return 1; }
        if (!g_pipe_out) { fprintf(stderr, "no bulk OUT pipe\n"); return 1; }
        send_bytes(payload, (UInt32)n, "--hex payload");
        printf("\n");
    }
    if (do_ptp) {
        if (!g_pipe_out) { fprintf(stderr, "--ptp needs a bulk OUT pipe\n"); return 1; }
        send_ptp_opensession();
        printf("\n");
    }
    if (do_tryall) {
        if (!g_pipe_out) { fprintf(stderr, "--tryall needs a bulk OUT pipe\n"); return 1; }
        printf("=== trying candidate framings on bulk OUT (first ACCEPT wins) ===\n");
        struct { const char *name; const unsigned char *p; int n; } cand[8];
        int nc = 0;
        unsigned char ptp_open[16], ptp_devinfo[16], ascii_help[8], ascii_crlf[2];
        unsigned char zero1[1], len4[4], ptp_zero[16];

        memset(ptp_open, 0, 16);
        ptp_open[0] = 16; ptp_open[4] = 1; ptp_open[8] = 0x02; ptp_open[9] = 0x10; ptp_open[12] = 1;
        cand[nc].name = "PTP OpenSession 0x1002"; cand[nc].p = ptp_open; cand[nc].n = 16; nc++;

        memset(ptp_devinfo, 0, 16);
        ptp_devinfo[0] = 16; ptp_devinfo[4] = 1; ptp_devinfo[8] = 0x01; ptp_devinfo[9] = 0x10; ptp_devinfo[12] = 1;
        cand[nc].name = "PTP GetDeviceInfo 0x1001"; cand[nc].p = ptp_devinfo; cand[nc].n = 16; nc++;

        memset(ptp_zero, 0, 16);
        ptp_zero[0] = 16; ptp_zero[4] = 1;
        cand[nc].name = "PTP-shaped, opcode 0x0000"; cand[nc].p = ptp_zero; cand[nc].n = 16; nc++;

        memcpy(ascii_help, "help\r\n", 6);
        cand[nc].name = "ASCII \"help\\r\\n\""; cand[nc].p = ascii_help; cand[nc].n = 6; nc++;

        ascii_crlf[0] = '\r'; ascii_crlf[1] = '\n';
        cand[nc].name = "ASCII \"\\r\\n\""; cand[nc].p = ascii_crlf; cand[nc].n = 2; nc++;

        zero1[0] = 0x00;
        cand[nc].name = "single 0x00"; cand[nc].p = zero1; cand[nc].n = 1; nc++;

        memset(len4, 0, 4);
        cand[nc].name = "4-byte LE length 0"; cand[nc].p = len4; cand[nc].n = 4; nc++;

        cand[nc].name = "16 zero bytes"; cand[nc].p = ptp_zero; cand[nc].n = 16; nc++;

        int accepted = 0;
        for (int i = 0; i < nc && !accepted; i++) {
            printf("  [%d/%d] %s\n", i + 1, nc, cand[i].name);
            if (send_bytes(cand[i].p, (UInt32)cand[i].n, cand[i].name) == 0) {
                printf("      ^^ ACCEPTED -- this framing is understood by the device\n");
                accepted = 1;
            }
        }
        if (!accepted) printf("  none accepted; all writes were NAKed\n");
        printf("\n");
    }

    unsigned char buf[BUFSZ];
    double t0 = now_s();
    long total_int = 0, total_bulk = 0;
    int events = 0;

    printf("[listening... if the device says nothing, that is itself a result]\n\n");

    while (now_s() - t0 < seconds) {
        if (g_pipe_int) {
            IOReturn err;
            int n = read_pipe(g_pipe_int, buf, sizeof(buf), 200, &err);
            if (n > 0) {
                printf("--- [%7.3fs] INTERRUPT IN  EP0x83: %d bytes ---\n", now_s() - t0, n);
                hexdump(buf, n, "    ");
                printf("\n");
                total_int += n; events++;
            }
        }
        if (g_pipe_in) {
            IOReturn err;
            int n = read_pipe(g_pipe_in, buf, sizeof(buf), 100, &err);
            if (n > 0) {
                printf("--- [%7.3fs] BULK IN  EP0x82: %d bytes ---\n", now_s() - t0, n);
                hexdump(buf, n, "    ");
                printf("\n");
                total_bulk += n; events++;
            }
        }
    }

    printf("=== summary ===\n");
    printf("  interrupt IN bytes : %ld\n", total_int);
    printf("  bulk IN bytes      : %ld\n", total_bulk);
    printf("  events seen        : %d\n", events);
    if (!events)
        printf("  => the device volunteered nothing. Try --ptp to nudge it.\n");

    if (g_intf) (*g_intf)->USBInterfaceClose(g_intf);
    if (g_dev)  { (*g_dev)->USBDeviceClose(g_dev); (*g_dev)->Release(g_dev); }
    return 0;
}
