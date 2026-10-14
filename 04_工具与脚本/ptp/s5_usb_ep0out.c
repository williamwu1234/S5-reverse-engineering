/*
 * s5_usb_ep0out.c — zero-length VENDOR OUT probe on EP0.
 *
 * ============================ READ THIS FIRST ============================
 * This tool TRANSMITS. It is the only tool in this set that writes to the
 * device. Everything else we built (s5_usb_desc, s5_usb_ep0) is strictly
 * read-only.
 *
 * What it sends:  bmRequestType = 0x40 / 0x41 / 0x42   (OUT, vendor, dev/if/ep)
 *                 bRequest      = 0x01 .. N
 *                 wValue = 0, wIndex = 0
 *                 wLength = 0          <-- HARD-CODED, cannot be changed
 *                 pData   = NULL       <-- HARD-CODED, cannot be changed
 *
 * ZERO-LENGTH BY CONSTRUCTION. No payload can ever be transmitted; the only
 * thing that reaches the device is the 8-byte setup packet. A zero-length
 * control request can still *trigger* a state change on the device if the
 * opcode happens to mean something (reset, start-update, ...), so this is
 * not risk-free -- it is the smallest possible poke, not a no-op.
 *
 * Safety rails:
 *   - DRY RUN BY DEFAULT. You must pass --go to actually transmit.
 *   - Stops at the first bRequest that is not STALLed (--keep-going to continue).
 *   - Delay between requests (--delay ms, default 100).
 *   - Bounded range (--start / --max).
 *
 * Why this is the one direction left: every other path on the 04da:2370
 * service personality is exhausted -- vendor IN on all three recipients
 * STALLs, eight bulk-OUT framings were NAKed, and both IN endpoints stay
 * silent. Vendor OUT has never been tried.
 *
 * Build: clang -O2 -Wall -framework IOKit -framework CoreFoundation \
 *            -o s5_usb_ep0out s5_usb_ep0out.c
 * Usage: ./s5_usb_ep0out [vid] [pid] [--go] [--start N] [--max N]
 *                        [--types 40,41,42] [--delay ms] [--keep-going]
 *        defaults: vid=0x04da pid=0x2370 start=1 max=0x40 delay=100
 * ========================================================================
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>
#include <IOKit/IOKitLib.h>
#include <IOKit/IOCFPlugIn.h>
#include <IOKit/usb/IOUSBLib.h>
#include <IOKit/usb/USBSpec.h>
#include <CoreFoundation/CoreFoundation.h>

#define DEF_VID 0x04DA
#define DEF_PID 0x2370

static IOUSBDeviceInterface **g_dev = NULL;

static const char *rt_name(UInt8 t)
{
    static char b[64];
    const char *dir = (t & 0x80) ? "IN " : "OUT";
    unsigned ty = (t >> 5) & 3, rc = t & 0x1F;
    const char *tys = ty == 0 ? "std" : ty == 1 ? "class" : ty == 2 ? "vendor" : "rsvd";
    const char *rcs = rc == 0 ? "dev" : rc == 1 ? "if" : rc == 2 ? "ep" : "oth";
    snprintf(b, sizeof(b), "%s %s %s", dir, tys, rcs);
    return b;
}

/*
 * One EP0 OUT request. wLength is forced to 0 and pData to NULL here --
 * there is no code path in this file that can attach a payload.
 */
static IOReturn ep0_out_zero(UInt8 bmRequestType, UInt8 bRequest,
                             UInt16 wValue, UInt16 wIndex, UInt32 *done)
{
    if (bmRequestType & 0x80) {
        fprintf(stderr, "REFUSING IN request type 0x%02x (this tool is OUT-only)\n", bmRequestType);
        return kIOReturnBadArgument;
    }
    IOUSBDevRequestTO req;
    memset(&req, 0, sizeof(req));
    req.bmRequestType     = bmRequestType;
    req.bRequest          = bRequest;
    req.wValue            = wValue;
    req.wIndex            = wIndex;
    req.wLength           = 0;        /* HARD-CODED: zero-length */
    req.pData             = NULL;     /* HARD-CODED: no data phase */
    req.wLenDone          = 0;
    req.noDataTimeout     = 200;
    req.completionTimeout = 500;

    IOReturn r = (*g_dev)->DeviceRequestTO(g_dev, &req);
    if (done) *done = req.wLenDone;
    return r;
}

/* Is this result 'nothing happened'? macOS reports a device STALL as
 * kIOReturnNotResponding (0xe00002ed) on this code path, NOT as kIOUSBPipeStalled.
 * Treating it as a hit produced a false positive once -- see the note in the
 * handover package. Keep this list in sync with s5_usb_ep0.c. */
static int is_noop(IOReturn r)
{
    return r == kIOUSBPipeStalled || r == kIOReturnNotResponding ||
           r == 0xe0004051 || r == kIOReturnTimeout;
}

static const char *describe(IOReturn r)
{
    if (r == kIOReturnSuccess)          return "ACCEPTED  <-- device understood this opcode";
    if (r == kIOUSBPipeStalled)         return "STALL (kIOUSBPipeStalled)";
    if (r == kIOReturnNotResponding)    return "STALL (kIOReturnNotResponding 0xe00002ed)";
    if (r == 0xe0004051)                return "timeout (0xe0004051)";
    if (r == kIOReturnTimeout)          return "timeout";
    return "other";
}

int main(int argc, char **argv)
{
    UInt32 vid = DEF_VID, pid = DEF_PID;
    int start = 0x01, maxreq = 0x40, delay_ms = 100;
    int do_go = 0, keep_going = 0, npos = 0;
    UInt16 wval = 0, widx = 0;
    char types[64] = "40,41,42";

    for (int i = 1; i < argc; i++) {
        if      (!strcmp(argv[i], "--go"))          do_go = 1;
        else if (!strcmp(argv[i], "--keep-going"))  keep_going = 1;
        else if (!strcmp(argv[i], "--max")   && i + 1 < argc) maxreq = (int)strtol(argv[++i], NULL, 0);
        else if (!strcmp(argv[i], "--start") && i + 1 < argc) start  = (int)strtol(argv[++i], NULL, 0);
        else if (!strcmp(argv[i], "--delay") && i + 1 < argc) delay_ms = (int)strtol(argv[++i], NULL, 0);
        else if (!strcmp(argv[i], "--wvalue") && i + 1 < argc) wval = (UInt16)strtol(argv[++i], NULL, 0);
        else if (!strcmp(argv[i], "--windex") && i + 1 < argc) widx = (UInt16)strtol(argv[++i], NULL, 0);
        else if (!strcmp(argv[i], "--types") && i + 1 < argc) snprintf(types, sizeof(types), "%s", argv[++i]);
        else if (!strncmp(argv[i], "0x", 2) || isdigit((unsigned char)argv[i][0])) {
            UInt32 v = (UInt32)strtoul(argv[i], NULL, 0);
            if (npos++ == 0) vid = v; else pid = v;
        }
    }
    if (maxreq > 0xFF) maxreq = 0xFF;
    if (start < 0) start = 0;
    if (start > maxreq) { fprintf(stderr, "start > max\n"); return 1; }

    int count = 0;
    for (const char *p = types; *p; p++) if (*p != ',' && *p != ' ') count++;

    printf("===============================================================\n");
    printf(" EP0 ZERO-LENGTH VENDOR OUT probe  ->  %04x:%04x\n", vid, pid);
    printf("---------------------------------------------------------------\n");
    printf(" THIS TOOL TRANSMITS. It is the only writing tool in this set.\n");
    printf(" wLength is hard-coded to 0 and pData to NULL: no payload can\n");
    printf(" ever be sent. Only the 8-byte setup packet reaches the device.\n");
    printf(" A zero-length request can still TRIGGER something if the opcode\n");
    printf(" means something. Smallest possible poke, not a no-op.\n");
    printf("---------------------------------------------------------------\n");
    printf(" types : %s   (%d recipients)\n", types, count);
    printf(" range : bRequest 0x%02x .. 0x%02x\n", start, maxreq);
    printf(" delay : %d ms between requests\n", delay_ms);
    printf(" stop  : %s\n", keep_going ? "no, keep going after a hit" : "YES, stop at first non-STALL");
    printf(" mode  : %s\n", do_go ? "*** LIVE -- WILL TRANSMIT ***" : "DRY RUN (add --go to transmit)");
    printf("===============================================================\n\n");

    if (!do_go) {
        printf("Dry run. These are the setup packets that WOULD be sent:\n\n");
        for (const char *tok = strtok(strdup(types), ","); tok; tok = strtok(NULL, ",")) {
            UInt8 t = (UInt8)strtoul(tok, NULL, 16);
            for (int b = start; b <= maxreq; b++)
                printf("  bmRequestType=0x%02x (%s)  bRequest=0x%02x  wValue=0x%04x  wIndex=0x%04x  wLength=0\n",
                       t, rt_name(t), b, wval, widx);
        }
        printf("\nNothing was sent. Re-run with --go to actually transmit.\n");
        return 0;
    }

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
    printf("[device opened]\n");

    /* sanity: a standard IN request must still work */
    {
        IOUSBDevRequestTO s; memset(&s, 0, sizeof(s));
        unsigned char d[18]; UInt32 got = 0;
        s.bmRequestType = 0x80; s.bRequest = 0x06; s.wValue = 0x0100; s.wLength = 18;
        s.pData = d; s.noDataTimeout = 200; s.completionTimeout = 500;
        IOReturn sr = (*g_dev)->DeviceRequestTO(g_dev, &s);
        got = s.wLenDone;
        printf("[sanity] GET_DESCRIPTOR -> 0x%08x, %u bytes %s\n\n",
               sr, got, (sr == 0 && got == 18) ? "(EP0 works)" : "(PROBLEM)");
    }

    int hits = 0;
    for (const char *tok = strtok(strdup(types), ","); tok; tok = strtok(NULL, ",")) {
        UInt8 t = (UInt8)strtoul(tok, NULL, 16);
        if (t & 0x80) { printf("skipping IN type 0x%02x\n", t); continue; }
        printf("=== sweep bmRequestType 0x%02x (%s)  bRequest 0x%02x..0x%02x ===\n",
               t, rt_name(t), start, maxreq);
        for (int b = start; b <= maxreq; b++) {
            UInt32 done = 0;
            IOReturn rr = ep0_out_zero(t, (UInt8)b, wval, widx, &done);
            if (!is_noop(rr)) {
                printf("  [%s] bRequest 0x%02x -> 0x%08x  (%s)\n",
                       rr == kIOReturnSuccess ? "HIT " : "??  ", b, rr, describe(rr));
                hits++;
                if (!keep_going) {
                    printf("\n  >>> STOPPING: first non-STALL result at opcode 0x%02x.\n", b);
                    printf("  >>> Do NOT re-run blindly; this opcode did something.\n");
                    goto done;
                }
            }
            if (delay_ms > 0) usleep((useconds_t)delay_ms * 1000);
        }
        printf("  (all STALLed)\n");
    }
done:
    printf("\n=== summary ===\n  non-STALL results: %d\n", hits);
    if (!hits)
        printf("  Every zero-length vendor OUT was STALLed.\n"
               "  => EP0 cannot open this channel either. Combined with the\n"
               "     IN sweep, EP0 is fully ruled out.\n");

    (*g_dev)->USBDeviceClose(g_dev);
    (*g_dev)->Release(g_dev);
    return 0;
}
