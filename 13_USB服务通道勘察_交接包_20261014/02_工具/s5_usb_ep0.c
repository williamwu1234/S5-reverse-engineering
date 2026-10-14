/*
 * s5_usb_ep0.c — probe the DC-S5 service channel's EP0 vendor requests (READ-ONLY).
 *
 * Situation
 * ---------
 * In service mode the camera is 04da:2370, vendor class 0xFF/0xA0/0xB0, with
 * bulk OUT (0x01), bulk IN (0x82) and interrupt IN (0x83). It answers nothing:
 *   - passive listen on both IN endpoints : 0 bytes
 *   - one PTP OpenSession on bulk OUT    : write itself times out (0xe0004051)
 * So the data pipes are dormant. A dormant vendor channel usually means the
 * device is waiting for an EP0 command to open a session first.
 *
 * This tool sweeps EP0 control requests. It implements IN requests ONLY:
 * every bmRequestType it can emit has bit 7 set (device-to-host). There is no
 * code path in this file that writes a payload to the device, so it cannot
 * change device state, start an update, or write any register.
 *
 * An unsupported bRequest simply STALLs, which is normal USB behaviour.
 * A supported one returns data -- that is the whole point.
 *
 * Build: clang -O2 -framework IOKit -framework CoreFoundation \
 *            -o s5_usb_ep0 s5_usb_ep0.c
 * Usage: ./s5_usb_ep0 [vid] [pid] [--max N] [--types 80,c0,c1,c2]
 *        defaults: vid=0x04da pid=0x2370 max=0x40 types=c0,c1,c2
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <IOKit/IOKitLib.h>
#include <IOKit/IOCFPlugIn.h>
#include <IOKit/usb/IOUSBLib.h>
#include <IOKit/usb/USBSpec.h>
#include <CoreFoundation/CoreFoundation.h>

#define DEF_VID 0x04DA
#define DEF_PID 0x2370
#define BUFSZ   256

static IOUSBDeviceInterface **g_dev = NULL;
static int g_hits = 0;

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

/*
 * One EP0 IN request. bmRequestType MUST have bit7 set; we assert that.
 * Returns the IOReturn; on success *got holds the byte count.
 */
static IOReturn ep0_in(UInt8 bmRequestType, UInt8 bRequest, UInt16 wValue, UInt16 wIndex,
                       void *buf, UInt16 wLength, UInt32 *got)
{
    if (!(bmRequestType & 0x80)) {
        fprintf(stderr, "REFUSING non-IN request type 0x%02x\n", bmRequestType);
        return kIOReturnBadArgument;
    }
    IOUSBDevRequestTO req;
    memset(&req, 0, sizeof(req));
    req.bmRequestType   = bmRequestType;
    req.bRequest        = bRequest;
    req.wValue          = wValue;
    req.wIndex          = wIndex;
    req.wLength         = wLength;
    req.pData           = buf;
    req.wLenDone        = 0;
    req.noDataTimeout   = 200;
    req.completionTimeout = 500;

    IOReturn r = (*g_dev)->DeviceRequestTO(g_dev, &req);
    if (got) *got = req.wLenDone;
    return r;
}

static const char *rt_name(UInt8 t)
{
    static char b[64];
    const char *dir = (t & 0x80) ? "IN " : "OUT";
    const char *ty  = ((t >> 5) & 3) == 0 ? "std" : ((t >> 5) & 3) == 1 ? "class" :
                      ((t >> 5) & 3) == 2 ? "vendor" : "rsvd";
    const char *rcv = (t & 0x1F) == 0 ? "dev" : (t & 0x1F) == 1 ? "if" :
                      (t & 0x1F) == 2 ? "ep" : "oth";
    snprintf(b, sizeof(b), "%s %s %s", dir, ty, rcv);
    return b;
}

static void sanity_check(void)
{
    unsigned char d[18]; UInt32 got = 0;
    IOReturn r = ep0_in(0x80, 0x06, 0x0100, 0, d, 18, &got);  /* GET_DESCRIPTOR device */
    printf("[sanity] standard GET_DESCRIPTOR device -> 0x%08x, %u bytes %s\n",
           r, got, (r == 0 && got == 18) ? "(EP0 works)" : "(PROBLEM)");
}

static void sweep(UInt8 type, int maxreq)
{
    printf("\n=== sweep: bmRequestType 0x%02x (%s), bRequest 0x00..0x%02x, wValue=0 wIndex=0 wLength=64 ===\n",
           type, rt_name(type), maxreq);
    printf("    (only non-STALL / non-error results are printed)\n");
    unsigned char buf[BUFSZ];
    int any = 0;
    for (int b = 0; b <= maxreq; b++) {
        memset(buf, 0xAA, sizeof(buf));
        UInt32 got = 0;
        IOReturn r = ep0_in(type, (UInt8)b, 0, 0, buf, 64, &got);
        if (r == 0) {
            printf("  [HIT] bRequest 0x%02x -> OK, %u bytes\n", b, got);
            if (got) hexdump(buf, got, "        ");
            any = 1; g_hits++;
        } else if (r != kIOUSBPipeStalled && r != kIOReturnNotResponding &&
                   r != 0xe0004051 && r != kIOReturnTimeout) {
            printf("  [??]  bRequest 0x%02x -> 0x%08x, %u bytes\n", b, r, got);
            if (got) hexdump(buf, got, "        ");
            any = 1;
        }
    }
    if (!any) printf("  (all bRequest values STALLed or timed out — no vendor IN requests at this level)\n");
}

int main(int argc, char **argv)
{
    UInt32 vid = DEF_VID, pid = DEF_PID;
    int maxreq = 0x40;
    char types[64] = "c0,c1,c2";

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--max") && i + 1 < argc) maxreq = (int)strtol(argv[++i], NULL, 0);
        else if (!strcmp(argv[i], "--types") && i + 1 < argc) snprintf(types, sizeof(types), "%s", argv[++i]);
        else if (!strncmp(argv[i], "0x", 2)) {
            if (vid == DEF_VID) vid = (UInt32)strtoul(argv[i], NULL, 16);
            else pid = (UInt32)strtoul(argv[i], NULL, 16);
        }
    }
    if (maxreq > 0xFF) maxreq = 0xFF;

    printf("===============================================================\n");
    printf(" EP0 vendor-request probe for %04x:%04x\n", vid, pid);
    printf(" READ-ONLY: only requests with direction=IN are emitted.\n");
    printf(" No payload is ever written to the device by this tool.\n");
    printf("===============================================================\n\n");

    CFMutableDictionaryRef m = IOServiceMatching(kIOUSBDeviceClassName);
    CFNumberRef nv = CFNumberCreate(kCFAllocatorDefault, kCFNumberSInt32Type, &vid);
    CFNumberRef np = CFNumberCreate(kCFAllocatorDefault, kCFNumberSInt32Type, &pid);
    CFDictionarySetValue(m, CFSTR(kUSBVendorID), nv);
    CFDictionarySetValue(m, CFSTR(kUSBProductID), np);
    CFRelease(nv); CFRelease(np);
    io_service_t svc = IOServiceGetMatchingService(kIOMainPortDefault, m);
    if (!svc) { fprintf(stderr, "device %04x:%04x not found\n", vid, pid); return 1; }

    IOCFPlugInInterface **plug = NULL; SInt32 score = 0;
    if (IOCreatePlugInInterfaceForService(svc, kIOUSBDeviceUserClientTypeID,
                                          kIOCFPlugInInterfaceID, &plug, &score) || !plug) {
        fprintf(stderr, "plug-in creation failed\n"); return 1;
    }
    (*plug)->QueryInterface(plug, CFUUIDGetUUIDBytes(kIOUSBDeviceInterfaceID), (LPVOID *)&g_dev);
    (*plug)->Release(plug);
    IOObjectRelease(svc);
    if (!g_dev) { fprintf(stderr, "QueryInterface failed\n"); return 1; }

    IOReturn r = (*g_dev)->USBDeviceOpen(g_dev);
    if (r) r = (*g_dev)->USBDeviceOpenSeize(g_dev);
    if (r) { fprintf(stderr, "USBDeviceOpen(Seize) -> 0x%08x\n", r); return 1; }
    printf("[device opened]\n\n");

    sanity_check();

    /* parse --types "c0,c1,c2" */
    char *save = NULL;
    for (char *tok = strtok_r(types, ",", &save); tok; tok = strtok_r(NULL, ",", &save)) {
        UInt8 t = (UInt8)strtoul(tok, NULL, 16);
        if (!(t & 0x80)) { printf("skipping non-IN type 0x%02x\n", t); continue; }
        sweep(t, maxreq);
    }

    printf("\n=== summary ===\n  hits: %d\n", g_hits);
    if (!g_hits) {
        printf("  EP0 answers no vendor IN request. The channel is either not\n");
        printf("  session-openable this way, or it needs a write to wake up --\n");
        printf("  which this tool deliberately cannot do.\n");
    }

    (*g_dev)->USBDeviceClose(g_dev);
    (*g_dev)->Release(g_dev);
    return 0;
}
