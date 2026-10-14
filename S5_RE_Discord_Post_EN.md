# Discord post draft (English)

> Copy-paste ready. Two versions below: a **full post** and a **short one** for channels with
> message-length limits. Replace the two `[link]` placeholders (or keep the literal URLs).

---

## Full version

Hi everyone — I've spent the last few weeks reversing a **Panasonic DC-S5 (LUMIX S5)** and I've
probably hit the limit of what I can work out on my own. I'd really value some pointers from
people who've done camera or embedded firmware work before.

**Quick context:** DC-S5, firmware VD4.30, SoC is Panasonic's "MC801" (Milbeaut, internally
"PVC" — Cortex-A7, 32-bit). I've been working black-box over the Wi-Fi CGI interface, USB PTP and
the SD card. No disassembly, no firmware modification.

**What went well:** the settings block. The camera only ever serves a RAM copy over HTTP, but the
65,533-byte settings blob can be written straight to flash over its chunked upload protocol —
and that survives a battery pull. `videoformat` turned out to be a single container gate, so
flipping it to MOV exposes 17 high-bitrate modes (4K/C4K, 100–200 Mbps, 10-bit) that are
otherwise hidden. I also built a wireless monitor for it, since LUMIX Flow doesn't support the S5.

**What didn't:** firmware AES. The key is on-die, and ~130k offline probes plus a recovered
256 KB keystream got us nowhere. Wi-Fi is a dead end too — ~70 privileged mode strings, all
generic `err_param`, no RCE.

**Four things I'd love advice on:**

1. **On-chip keys on Milbeaut / "PVC".** Has anyone recovered an AES key from this family
   *without* a JTAG RAM dump? I'm trying to work out whether JTAG is genuinely the only route.
2. **CoreSight / debug access on Milbeaut "PVC" (Cortex-A7).** Any experience with JTAG or UART
   on these SoCs, or with locating the debug pads?
3. **An OSS release that doesn't match the device.** Panasonic publishes `linux-3.18.18` for the
   DC-S5, but that tree contains **no exFAT code at all** — and the camera definitely mounts
   exFAT. Has anyone seen a vendor publish a kernel that doesn't match what ships?
4. **Firmware update stalling.** I can stream all 1,474 full blocks cleanly, but the final partial
   block always fails after ~31 s of flash addressing (`err_busy`, then `err_critical` on retry).
   Independent of payload, pacing and device state. Does that ring any bells?

Everything is written up — reports, tools, raw evidence — here:
https://github.com/williamwu1234/S5-reverse-engineering

The monitor tool (the one practical thing that came out of all this) is here:
https://github.com/williamwu1234/S5-wireless-monitor

Happy to go into detail on any of it — and equally happy to be told I'm going about something the
wrong way. Thanks for reading.

---

## Short version

Hi all — I've been reversing a **Panasonic DC-S5** (LUMIX S5, firmware VD4.30, Panasonic "MC801"
/ Milbeaut "PVC", Cortex-A7) black-box over Wi-Fi CGI, USB PTP and SD card. A few questions for
anyone who's done camera/embedded work:

1. **Milbeaut/"PVC" crypto** — any way to get an on-die AES key short of a JTAG RAM dump?
   (~130k offline probes and a 256 KB keystream got us nowhere.)
2. **Debug access** on Milbeaut "PVC" (Cortex-A7) — CoreSight/JTAG/UART experience, or tips on
   locating debug pads?
3. **OSS mismatch** — Panasonic publishes `linux-3.18.18` for the DC-S5, but that tree has **no
   exFAT driver**, and the camera definitely mounts exFAT. Seen this before?
4. **Firmware update stall** — all 1,474 full blocks stream fine, but the final partial block
   always fails after ~31 s of flash addressing (`err_busy` → `err_critical`).

Write-up: https://github.com/williamwu1234/S5-reverse-engineering
Tool: https://github.com/williamwu1234/S5-wireless-monitor

Thanks — happy to share detail on anything.

---

## Notes before posting

- **Both links are public.** The repos contain real camera data (settings blobs, allocation
  bitmaps, service-mode photos) and some reports include the **camera serial number**. Our own
  release notes say "desensitise before sharing externally" — decide whether that's acceptable
  before you post, or scrub the serial numbers first.
- **Trim freely.** Question 4 (firmware update stall) is the most niche; 1 and 2 are the ones
  most likely to get a useful answer from a hardware-savvy crowd.
- **If the channel prefers no links**, drop the URLs and offer to DM the summary — the long-form
  summary is in `S5_RE_Project_Summary_EN.md`.
- Tone check: it states what you've done, asks specific answerable questions, and explicitly
  invites correction. That reads as a peer asking for input rather than asking to be rescued.
