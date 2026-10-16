/*
 * s5_usb_desc.c — dump EVERY USB descriptor of a device.
 *
 * Why this exists
 * ---------------
 * The DC-S5 in service mode enumerates as VID 0x04DA / PID 0x2370,
 * interface class 0xFF / 0xA0 / 0xB0, 3 endpoints, bNumConfigurations = 2.
 * We know almost nothing beyond that -- the third endpoint's type, the
 * second configuration, and every string descriptor are still unknown.
 *
 * Those are the highest-information, zero-risk things left to collect:
 * string descriptors frequently name the mode outright ("SERVICE",
 * "UPDATE", "MASS STORAGE", "DIAG", ...), and the second configuration
 * often reveals a second personality (e.g. a firmware-update interface).
 *
 * Safety
 * ------
 * READ-ONLY AND PASSIVE BY CONSTRUCTION:
 *   - never calls SetConfiguration
 *   - never opens an interface, never touches a bulk or interrupt pipe
 *   - issues only standard chapter-9 GET_DESCRIPTOR control transfers
 * It cannot change device state, start an update, or trigger a flash.
 * A STALL from an unimplemented string index is normal and is ignored.
 *
 * Build:  clang -framework IOKit -framework CoreFoundation \
 *              -o s5_usb_desc s5_usb_desc.c
 * Usage:  ./s5_usb_desc [--list] [vid] [pid] [--strings N] [--no-open]
 *         defaults: vid=0x04da pid=0x2370 strings=64
 *         --list     enumerate all USB devices and exit
 *         --no-open  registry properties only (never opens the device)
 *         --strings N  how many string indices to probe (default 64, max 255)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <IOKit/IOKitLib.h>
#include <IOKit/IOCFPlugIn.h>
#include <IOKit/usb/IOUSBLib.h>
#include <IOKit/usb/USBSpec.h>
#include <CoreFoundation/CoreFoundation.h>

#define DEF_VID 0x04DA
#define DEF_PID 0x2370

static IOUSBDeviceInterface **g_dev = NULL;

/* ---------------------------------------------------------------- utils */

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

/* UTF-16LE -> UTF-8, best effort (ASCII fast path, latin-1 fallback). */
static void print_utf16le(const unsigned char *p, size_t nbytes)
{
    for (size_t i = 0; i + 1 < nbytes; i += 2) {
        unsigned int cp = p[i] | (p[i + 1] << 8);
        if (!cp) break;
        if (cp < 0x80) {
            putchar((int)cp);
        } else if (cp < 0x800) {
            putchar(0xC0 | (cp >> 6));
            putchar(0x80 | (cp & 0x3F));
        } else {
            putchar(0xE0 | (cp >> 12));
            putchar(0x80 | ((cp >> 6) & 0x3F));
            putchar(0x80 | (cp & 0x3F));
        }
    }
}

/* ------------------------------------------------------- control transfer */

static IOReturn get_descriptor(UInt8 type, UInt8 index, UInt16 langid,
                               void *buf, UInt16 len, UInt32 *done)
{
    IOUSBDevRequest req;
    memset(&req, 0, sizeof(req));
    req.bmRequestType = 0x80;                 /* device-to-host, standard, device */
    req.bRequest      = kUSBRqGetDescriptor;  /* 0x06 */
    req.wValue        = (UInt16)((type << 8) | index);
    req.wIndex        = langid;
    req.wLength       = len;
    req.pData         = buf;
    req.wLenDone      = 0;

    IOReturn r = (*g_dev)->DeviceRequest(g_dev, &req);
    if (done) *done = req.wLenDone;
    return r;
}

/* ------------------------------------------------------- registry fallback */

static void dump_registry(io_service_t svc)
{
    CFMutableDictionaryRef props = NULL;
    if (IORegistryEntryCreateCFProperties(svc, &props, kCFAllocatorDefault, 0) || !props) {
        printf("  (registry properties unavailable)\n");
        return;
    }
    const char *keys[] = {
        "USB Product Name", "USB Vendor Name", "USB Serial Number",
        "idVendor", "idProduct", "bcdDevice", "bDeviceClass",
        "bDeviceSubClass", "bDeviceProtocol", "locationID",
        "sessionID", "IOUserClientClass", "UsbDeviceSignature",
        NULL
    };
    for (int i = 0; keys[i]; i++) {
        CFStringRef k = CFStringCreateWithCString(kCFAllocatorDefault, keys[i],
                                                  kCFStringEncodingUTF8);
        CFTypeRef v = CFDictionaryGetValue(props, k);
        if (v) {
            char tmp[512] = {0};
            if (CFGetTypeID(v) == CFStringGetTypeID()) {
                CFStringGetCString(v, tmp, sizeof(tmp), kCFStringEncodingUTF8);
                printf("  %-20s : %s\n", keys[i], tmp);
            } else if (CFGetTypeID(v) == CFNumberGetTypeID()) {
                long long n = 0;
                CFNumberGetValue(v, kCFNumberSInt64Type, &n);
                printf("  %-20s : %lld (0x%llx)\n", keys[i], n, n);
            } else if (CFGetTypeID(v) == CFDataGetTypeID()) {
                CFIndex n = CFDataGetLength(v);
                const UInt8 *p = CFDataGetBytePtr(v);
                printf("  %-20s : CFData, %ld bytes\n", keys[i], (long)n);
                if (p && n > 0 && n <= 4096) hexdump(p, (size_t)n, "      ");
                else if (p && n > 4096) {
                    printf("      (first 256 bytes)\n");
                    hexdump(p, 256, "      ");
                }
            } else {
                printf("  %-20s : (CFTypeID %lu)\n", keys[i], (unsigned long)CFGetTypeID(v));
            }
        }
        CFRelease(k);
    }
    CFRelease(props);
}

/* ------------------------------------------------------- descriptor dumps */

static void dump_device_descriptor(void)
{
    unsigned char d[18]; UInt32 got = 0;
    IOReturn r = get_descriptor(kIOUSBDescriptorTypeDevice, 0, 0, d, sizeof(d), &got);
    printf("\n=== Device descriptor ===  (GET_DESCRIPTOR, %u bytes, status 0x%08x)\n", got, r);
    if (r || got < 18) { printf("  failed\n"); return; }
    hexdump(d, 18, "  ");
    printf("  bLength            = %u\n", d[0]);
    printf("  bDescriptorType    = %u\n", d[1]);
    printf("  bcdUSB             = 0x%04x\n", d[2] | (d[3] << 8));
    printf("  bDeviceClass       = 0x%02x\n", d[4]);
    printf("  bDeviceSubClass    = 0x%02x\n", d[5]);
    printf("  bDeviceProtocol    = 0x%02x\n", d[6]);
    printf("  bMaxPacketSize0    = %u\n", d[7]);
    printf("  idVendor           = 0x%04x\n", d[8]  | (d[9]  << 8));
    printf("  idProduct          = 0x%04x\n", d[10] | (d[11] << 8));
    printf("  bcdDevice          = 0x%04x\n", d[12] | (d[13] << 8));
    printf("  iManufacturer      = %u\n", d[14]);
    printf("  iProduct           = %u\n", d[15]);
    printf("  iSerialNumber      = %u\n", d[16]);
    printf("  bNumConfigurations = %u   <-- read ALL of them\n", d[17]);
}

static void parse_config_blob(const unsigned char *b, size_t total)
{
    size_t off = 0;
    int cur_altsetting = -1, cur_intf = -1;

    while (off + 2 <= total) {
        unsigned len = b[off];
        unsigned type = b[off + 1];
        if (len < 2 || off + len > total) {
            printf("    [malformed descriptor at %zu: len=%u type=%u]\n", off, len, type);
            break;
        }
        switch (type) {
        case kIOUSBDescriptorTypeConfiguration:
            printf("    -- Configuration\n");
            printf("       bLength=%u bDescriptorType=%u wTotalLength=%u\n",
                   b[off], type, b[off+2] | (b[off+3] << 8));
            printf("       bNumInterfaces=%u bConfigurationValue=%u iConfiguration=%u\n",
                   b[off+4], b[off+5], b[off+6]);
            printf("       bmAttributes=0x%02x bMaxPower=%u (=%u mA)\n",
                   b[off+7], b[off+8], b[off+8] * 2);
            break;
        case kIOUSBDescriptorTypeInterface:
            cur_intf = b[off + 2];
            cur_altsetting = b[off + 3];
            printf("    -- Interface %u alt %u\n", cur_intf, cur_altsetting);
            printf("       bInterfaceClass=0x%02x bInterfaceSubClass=0x%02x bInterfaceProtocol=0x%02x\n",
                   b[off+5], b[off+6], b[off+7]);
            printf("       bNumEndpoints=%u iInterface=%u\n", b[off+4], b[off+8]);
            break;
        case kIOUSBDescriptorTypeEndpoint: {
            unsigned addr = b[off + 2], attr = b[off + 3];
            unsigned mps = b[off + 4] | (b[off + 5] << 8);
            unsigned iv = b[off + 6];
            static const char *tn[] = {"control","isochronous","bulk","interrupt"};
            printf("    -- Endpoint 0x%02x  %s  %s  maxPacket=%u  interval=%u\n",
                   addr,
                   (addr & 0x80) ? "IN " : "OUT",
                   tn[(attr & 3) < 4 ? (attr & 3) : 0],
                   mps, iv);
            if ((attr & 3) == 3) printf("       ^^ INTERRUPT endpoint: this channel can push events\n");
            break;
        }
        default:
            printf("    -- Descriptor type %u, len %u (class/vendor specific)\n", type, len);
            break;
        }
        off += len;
    }
}

static void dump_configuration(UInt8 index)
{
    unsigned char head[9]; UInt32 got = 0;
    IOReturn r = get_descriptor(kIOUSBDescriptorTypeConfiguration, index, 0, head, sizeof(head), &got);
    printf("\n=== Configuration %u ===  (status 0x%08x, %u bytes)\n", index, r, got);
    if (r || got < 9) { printf("  failed / absent\n"); return; }

    unsigned total = head[2] | (head[3] << 8);
    if (total < 9 || total > 4096) { printf("  implausible wTotalLength=%u\n", total); return; }

    unsigned char *buf = malloc(total);
    if (!buf) return;
    memset(buf, 0, total);
    r = get_descriptor(kIOUSBDescriptorTypeConfiguration, index, 0, buf, (UInt16)total, &got);
    printf("  raw %u bytes:\n", got);
    hexdump(buf, got, "    ");
    printf("  parsed:\n");
    parse_config_blob(buf, got);
    free(buf);
}

static void dump_langids(UInt16 *langids, int *count)
{
    unsigned char b[256]; UInt32 got = 0;
    IOReturn r = get_descriptor(kIOUSBDescriptorTypeString, 0, 0, b, sizeof(b), &got);
    printf("\n=== String descriptor 0 (LANGID list) ===  (status 0x%08x, %u bytes)\n", r, got);
    *count = 0;
    if (r || got < 4) { printf("  unavailable; falling back to 0x0409\n"); langids[(*count)++] = 0x0409; return; }
    hexdump(b, got, "  ");
    for (UInt32 i = 2; i + 1 < got; i += 2) {
        UInt16 id = b[i] | (b[i + 1] << 8);
        printf("  LANGID 0x%04x\n", id);
        if (*count < 32) langids[(*count)++] = id;
    }
    if (!*count) langids[(*count)++] = 0x0409;
}

static void dump_strings(int maxidx)
{
    UInt16 langids[32]; int nlang = 0;
    dump_langids(langids, &nlang);

    for (int li = 0; li < nlang; li++) {
        printf("\n=== Strings for LANGID 0x%04x (indices 1..%d) ===\n", langids[li], maxidx);
        int found = 0;
        for (int i = 1; i <= maxidx; i++) {
            unsigned char b[512]; UInt32 got = 0;
            IOReturn r = get_descriptor(kIOUSBDescriptorTypeString, (UInt8)i, langids[li], b, sizeof(b), &got);
            if (r || got < 2 || b[1] != kIOUSBDescriptorTypeString) continue;
            printf("  [%3d] ", i);
            print_utf16le(b + 2, got - 2);
            printf("   (raw %u bytes)\n", got);
            found++;
        }
        if (!found) printf("  (none)\n");
    }
}

/* ------------------------------------------------------------------ main */

static io_service_t find_device(UInt32 vid, UInt32 pid)
{
    CFMutableDictionaryRef m = IOServiceMatching(kIOUSBDeviceClassName);
    if (!m) return 0;
    CFNumberRef nv = CFNumberCreate(kCFAllocatorDefault, kCFNumberSInt32Type, &vid);
    CFNumberRef np = CFNumberCreate(kCFAllocatorDefault, kCFNumberSInt32Type, &pid);
    CFDictionarySetValue(m, CFSTR(kUSBVendorID), nv);
    CFDictionarySetValue(m, CFSTR(kUSBProductID), np);
    CFRelease(nv); CFRelease(np);
    return IOServiceGetMatchingService(kIOMainPortDefault, m);
}

static void list_devices(void)
{
    CFMutableDictionaryRef m = IOServiceMatching(kIOUSBDeviceClassName);
    io_iterator_t it = 0;
    if (IOServiceGetMatchingServices(kIOMainPortDefault, m, &it)) return;
    io_service_t svc; int n = 0;
    printf("VID     PID     name\n");
    while ((svc = IOIteratorNext(it))) {
        CFMutableDictionaryRef p = NULL;
        if (!IORegistryEntryCreateCFProperties(svc, &p, kCFAllocatorDefault, 0) && p) {
            CFTypeRef vv = CFDictionaryGetValue(p, CFSTR("idVendor"));
            CFTypeRef pp = CFDictionaryGetValue(p, CFSTR("idProduct"));
            CFTypeRef nn = CFDictionaryGetValue(p, CFSTR("USB Product Name"));
            int vid = 0, pid = 0; char nm[128] = "?";
            if (vv) CFNumberGetValue(vv, kCFNumberIntType, &vid);
            if (pp) CFNumberGetValue(pp, kCFNumberIntType, &pid);
            if (nn) CFStringGetCString(nn, nm, sizeof(nm), kCFStringEncodingUTF8);
            printf("0x%04x  0x%04x  %s%s\n", vid, pid, nm,
                   vid == 0x04DA ? "   <-- Panasonic" : "");
            n++;
            CFRelease(p);
        }
        IOObjectRelease(svc);
    }
    IOObjectRelease(it);
    printf("(%d device%s)\n", n, n == 1 ? "" : "s");
}

int main(int argc, char **argv)
{
    UInt32 vid = DEF_VID, pid = DEF_PID;
    int maxidx = 64, no_open = 0, npos = 0;

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--list")) { list_devices(); return 0; }
        else if (!strcmp(argv[i], "--no-open")) no_open = 1;
        else if (!strcmp(argv[i], "--strings") && i + 1 < argc) maxidx = atoi(argv[++i]);
        else if (!strncmp(argv[i], "0x", 2) || isdigit((unsigned char)argv[i][0])) {
            UInt32 v = (UInt32)strtoul(argv[i], NULL, 0);
            if (npos++ == 0) vid = v; else pid = v;
        }
    }
    if (maxidx < 1) maxidx = 1;
    if (maxidx > 255) maxidx = 255;

    io_service_t svc = find_device(vid, pid);
    if (!svc) {
        printf("device %04x:%04x not found.\n\n", vid, pid);
        list_devices();
        return 1;
    }

    printf("================================================================\n");
    printf(" USB descriptor dump for %04x:%04x\n", vid, pid);
    printf(" PASSIVE: no SetConfiguration, no interface open, no pipe I/O.\n");
    printf(" Only standard GET_DESCRIPTOR control transfers.\n");
    printf("================================================================\n");

    printf("\n=== IOKit registry (no device open required) ===\n");
    dump_registry(svc);

    if (no_open) {
        printf("\n(--no-open: stopping here; descriptor dump needs the device open)\n");
        IOObjectRelease(svc);
        return 0;
    }

    IOCFPlugInInterface **plug = NULL; SInt32 score = 0;
    kern_return_t kr = IOCreatePlugInInterfaceForService(svc, kIOUSBDeviceUserClientTypeID,
                                                         kIOCFPlugInInterfaceID, &plug, &score);
    if (kr != KERN_SUCCESS || !plug) { printf("\nplug-in creation failed\n"); IOObjectRelease(svc); return 1; }
    HRESULT hr = (*plug)->QueryInterface(plug, CFUUIDGetUUIDBytes(kIOUSBDeviceInterfaceID),
                                          (LPVOID *)&g_dev);
    (*plug)->Release(plug);
    if (hr || !g_dev) { printf("\nQueryInterface failed\n"); IOObjectRelease(svc); return 1; }

    IOReturn r = (*g_dev)->USBDeviceOpen(g_dev);
    if (r) {
        printf("\nUSBDeviceOpen -> 0x%08x, trying seize...\n", r);
        r = (*g_dev)->USBDeviceOpenSeize(g_dev);
        if (r) {
            printf("USBDeviceOpenSeize -> 0x%08x\n", r);
            printf("Device is busy. Quit anything holding it (browsers, cloud\n");
            printf("sync, ImageCapture, 'QuarkCloudDrive' has done this before)\n");
            printf("and re-run. Registry properties above are still valid.\n");
            IOObjectRelease(svc);
            return 1;
        }
    }
    printf("\n(device opened; descriptors below are read-only)\n");

    dump_device_descriptor();

    UInt8 ncfg = 0;
    (*g_dev)->GetNumberOfConfigurations(g_dev, &ncfg);
    printf("\n[GetNumberOfConfigurations = %u]\n", ncfg);
    printf("[note: the GET_DESCRIPTOR configuration index is 0-BASED]\n");
    for (UInt8 i = 0; i < ncfg; i++) dump_configuration(i);

    dump_strings(maxidx);

    printf("\n=== done ===\n");
    (*g_dev)->USBDeviceClose(g_dev);
    (*g_dev)->Release(g_dev);
    IOObjectRelease(svc);
    return 0;
}
