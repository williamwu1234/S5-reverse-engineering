Hi all — I've been reversing a **Panasonic DC-S5** (LUMIX S5, fw VD4.30, Panasonic "MC801" / Milbeaut "PVC", Cortex-A7) black-box over Wi-Fi CGI, USB PTP and SD card. I'd value pointers from anyone who's done camera / embedded firmware work.

**What worked:** the 65,533-byte settings blob can be written straight to flash via its chunked upload protocol, and it survives a battery pull. `videoformat` turned out to be a single container gate — MOV mode exposes 17 hidden high-bitrate modes (4K/C4K, 100–200 Mbps 10-bit). I also built a wireless monitor for it, since LUMIX Flow doesn't support the S5.

**What didn't:** firmware AES — the key is on-die, and ~130k offline probes plus a 256 KB keystream got nowhere. Wi-Fi is a dead end too: ~70 privileged mode strings, all generic `err_param`, no RCE.

**Four questions:**

1. Has anyone recovered an on-die AES key from Milbeaut / "PVC" *without* a JTAG RAM dump? Is JTAG the only realistic route?
2. Any CoreSight / JTAG / UART experience on Milbeaut "PVC" (Cortex-A7), or tips on locating debug pads?
3. Panasonic publishes `linux-3.18.18` for the DC-S5, but that tree has **no exFAT driver** — and the camera definitely mounts exFAT. Seen a vendor ship a kernel that doesn't match their OSS?
4. All 1,474 full firmware blocks stream fine, but the final partial block always fails after ~31 s of flash addressing (`err_busy` → `err_critical`). Familiar?

Write-up: https://github.com/williamwu1234/S5-reverse-engineering
Tool: https://github.com/williamwu1234/S5-wireless-monitor

Happy to share detail — and to be told I'm doing something wrong. Thanks.
