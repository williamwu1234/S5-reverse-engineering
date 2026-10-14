# Panasonic DC-S5 (LUMIX S5) — Reverse Engineering Summary

A short, technical overview of what we tried, what worked, and what didn't.
Written for people who do camera / embedded firmware work.

---

## Target

| | |
|---|---|
| **Camera** | Panasonic DC-S5 (LUMIX S5) |
| **Firmware** | VD4.30 (research image) |
| **SoC** | Panasonic "MC801" — Milbeaut / internally "PVC" family, ARM Cortex-A7, 32-bit |
| **Kernel** | Panasonic-modified Linux; OSPO publishes `linux-3.18.18` for this model (see caveat below) |
| **Channels used** | Wi-Fi HTTP CGI (`cam.cgi`, requires `User-Agent: LUMIX Sync`), USB PTP, SD card |

Method: black-box, over the wire. No disassembly of the unit, no firmware modification for the
interface work. Evidence in the reports is tagged **✓ closed on hardware · ◐ strong but open · ✗ disproved**.

---

## 1. Firmware encryption — negative result

The firmware image is AES-encrypted. The key is held on-die
(OTP / eFuse / crypto engine / TrustZone) and does not appear in the firmware file, the lens
adapter, or on the lens I²C bus.

- ~130k offline probes across all 40/41 encrypted partitions
- A genuine 256 KB keystream recovered for analysis
- UPD-header "version gate" fields located — changing `comm_proto_ver` does **not** bypass the gate

**Conclusion: offline key recovery is a dead end.** The realistic route to plaintext is a runtime
RAM dump (JTAG), not cryptanalysis.

## 2. Wi-Fi attack surface — negative result

The web server is a Panasonic-customised **GoAhead** CGI (`cam.cgi`).

- ~70 candidate privileged mode strings (`dmesg`, `memdump`, `flash`, `jtag`, `keydump`, …)
  all return a generic `err_param`. No debug backdoor.
- The Wi-Fi surface behaves as a **verification oracle** only — three of them: version gate
  (anti-rollback), firmware signature check, and the CAMSET checksum (forgeable).
- Most published GoAhead CVEs don't apply here. `LD_PRELOAD` injection is a no-go.
- **Only reproducible bug: a PTP length DoS** — the parser validates `type` but not `length`;
  a mismatched length hangs the interface with no timeout. Recovers by unplugging USB. No memory write.

## 3. Hidden video format unlock + persistence — main result

- The camera only ever serves a **RAM copy** of its settings over HTTP.
  `setsetting` writes RAM only (lost on power-off).
- Writing the **65,533-byte settings blob** straight to flash — via the chunked
  `startsenddata` → `senddata` → `endsenddata` protocol (`method=separate`, two chunks) —
  **persists across a battery pull**. Verified after full power loss.
- **`videoformat` is a single exclusive container gate.** Flipping it to MOV exposes 17
  high-bitrate `mov_*` modes (4K / C4K, 100–200 Mbps, 10-bit) that are otherwise hidden.
- Checksum scheme: `byte[65532] = (256 − Σ(byte[0..65531])) mod 256`
- Blob layout: 44-byte header (`"Panasonic"` + `"DC-S5"`) + 8-byte preamble + **831 TLV records**
  (`[field_id u16][len u16][flag u16][payload]`)

**Gotcha worth repeating:** a single 65 KB POST silently never lands. The camera announces the
required chunking in the `startsenddata` reply (`method`/`bufsize`) — read it. We initially
misread the resulting "format falls back on reboot" as firmware re-derivation; it was just an
upload that never happened.

## 4. Sibling-model cross-check (DC-S1RM2)

Another team working on the DC-S1RM2 (Socionext SC2006A) shared two results:

- **CAMSET settings block (9.2 MB)** — same design family, and the same checksum formula
  `(256 − Σ) mod 256`, derived independently. Good mutual confirmation across models.
- **FunctionFS OOB** in the USB gadget layer — low impact (fixed offsets, upper 16 bits always
  zero) → DoS + weak infoleak, not RCE.

## 5. exFAT — including one retraction

- **Confirmed:** the kernel does not validate cluster ownership when freeing, so it follows a
  tampered FAT chain from the card.
- **Retracted:** our earlier claim of a "confirmed OOB kernel memory write."
  Injecting an index that *must* be NULL produced an error but **no crash** — i.e. there is a
  NULL check before the write. The inference "card write failed ⇒ the in-memory write already
  happened" is **unsound**, and the S1RM2 report above used the same inference.
  *Lesson: always run a control group.*
- **Separately confirmed:** ~360 files with **240-character filenames** in `DCIM/100_PANA` put the
  camera into a **boot loop**. Four-way control matrix isolates the cause to the name bytes
  themselves (threshold between 58 KB and 86 KB) — looks like a fixed-size buffer with no length
  check. DoS only, but a more promising lead than the exFAT bitmap path.

## 6. Open-source release caveat

Panasonic's OSPO site publishes kernel source for the DC-S5
(`https://ospo.panasonic.com/oss/source/dsc/DC-FZ1K2/linux-3.18.18.tar.gz`, ~122 MB, public).
That tree contains **no exFAT code whatsoever** — yet the camera clearly mounts exFAT and the
exFAT free path behaves as described above. The published tree also ships a minimal
networking-only defconfig (no USB gadget support), while the shipping device obviously has USB.

**So the published OSS does not match the shipping kernel.** U-Boot is not published at all.
This is currently one of our main open questions.

---

## Where we're stuck

1. **On-chip AES key.** Has anyone recovered keys from a Milbeaut / "PVC" crypto engine *without*
   a JTAG RAM dump? Is JTAG the only realistic route on this family?
2. **JTAG / UART on Milbeaut "PVC" (Cortex-A7).** Any experience with CoreSight on this platform,
   or locating debug pads? We're at the "identify the test points" stage.
3. **OSS vs. shipping kernel.** Has anyone seen Panasonic publish a kernel different from what
   actually ships, or found the real S5 kernel elsewhere?
4. **Firmware update write path.** We can stream all 1,474 full 61,192-byte blocks cleanly, but the
   **final partial block (~41 KB) always fails**: ~31 s of flash addressing → `err_busy`, then
   `err_critical` on retry. Independent of payload, pacing, and device state. Suspect an internal
   erase/write timeout or wear on the large image's last block. Anyone seen this on Milbeaut?

---

## Links

- **Research repo** (reports, tools, evidence):
  https://github.com/williamwu1234/S5-reverse-engineering
- **Wireless monitor v1.0** (practical output of this work — real-time viewfinder, touch AF,
  photo/record, AE lock; pure Python stdlib, no app install):
  https://github.com/williamwu1234/S5-wireless-monitor

> Both repositories are public. They contain real camera data (settings blobs, allocation
> bitmaps, service-mode photos) and some reports include the camera serial number.
