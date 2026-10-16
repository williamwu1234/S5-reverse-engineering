# 机型身份面 · 离线反汇编证据（2026-10-16）

> 对象：`S5_逆向_项目总包_20261012/19_路径1_Linux侧攻击面_20261015/fs2/`（**G100 明文 rootfs**）
> 工具：`arm-none-eabi-objdump -d`（+ 自写字符串 xref 提取器，输出见同目录 `*_stridx.txt`）
> 边界：**G100 ≠ S5 本体**（权威文档 §1-8 #8）。本目录所有结论是"S5 活体 fuzz 的实验设计依据"，不是 S5 的结论。
> 段基址约定：`vaddr = 文件偏移 + 0x10000`（psm / dlna 均成立）

---

## 1. 结论速览

| # | 结论 | 二进制/地址 | 证据文件 |
|---|---|---|---|
| A1 | **SOAP 体里的 `<pana:X_FromCP>` 是被显式 `strcmp` 匹配并取值存储的客户端身份字段**（不是自由文本，不是只记日志） | dlna `0xe7834` `strcmp(name,"pana:X_FromCP")` | `disasm/dlna_fromcp_parse_e7794.txt`, `dlna_fromcp_store_e7848.txt` |
| A2 | X_FromCP 的**取值是定长受控拷贝**：先 `0x53c54(val,30)` 再 `0x4b734(val, 会话+0x340c, 64)` ⇒ 身份字段**有界**，不是溢出点；它是**语义门** | dlna `0xe7860-0xe7920` | `disasm/dlna_fromcp_store_e7848.txt` |
| A3 | dlna 存在**身份注册函数**，对身份串做 **9 字节前缀比对 `"LumixLink"`**，命中/未命中走两套分支：命中把 `[r4+1256]` 能力字复制给会话（`[r6+1256]`）并置 `fp=1`，未命中置 `fp=2` | dlna `0x13c8c`（函数体）、`0x13ef8`/`0x13f38`（两次 `strncmp(x,"LumixLink",9)`） | `disasm/dlna_identity_register_13c8c.txt`, `dlna_lumixlink_gate_13ef0.txt` |
| A4 | 同一分支内**无条件写 `[r6+0xcc] = 0x80000000`**（INT32_MIN）——与 Browse 的 `StartingIndex` 语义域相关，是 crash 001 重评估的**代码侧线索** | dlna `0x13f40-0x13f54` | `dlna_lumixlink_gate_13ef0.txt` |
| A5 | dlna 解析 **6 个 Panasonic 私有 HTTP 头**：`X_Panasonic_Cam_VRec / PictBrst / Sync / PRec / Req / Transfer`（两处独立簇：构造 0x0ba544 区、消费 0x0d20d8 区）+ `X_DeviceName` 头表（0x60acc） | dlna 上述地址 | `dlna_hdr_table_60acc.txt`, `dlna_camxml_hdr_build_*.txt`, `dlna_stridx.txt` |
| B1 | psm 有**专用 accctrl XML body 生成器**：`PsmXml_getAccctrlReqAccBody` / `PsmXml_getAccctrlResultBody` ⇒ 授权面在 psm 内是一等公民 | psm `0x04ef88`/`0x04f0b8` | `psm_stridx.txt` |
| B2 | **机型能力面 = `cam.cgi?mode=getinfo&type=capability`**（整串匹配分派，第二个对照串 `cam.cgi?mode=camcmd&value=recmode`） | psm `0x3f630` / `0x3f660`，匹配器 `0x3f4c4` | `disasm/psm_capability_3f620.txt` |
| B3 | **机型 ID → 菜单文件跳转表（24 项）**：`model_id` 取自 `NETUTIL_GetConfigModelNumber()`（u16，带缓存），`idx = model_id − 0x137`，`ldrls pc,[pc,r0,lsl#2]` | psm `0x19010-0x19024`，表 `0x19028` | `disasm/psm_menuxml_table_18fbc.txt` |
| B4 | 跳转表实际落点（idx → 机型 → 菜单文件）：311→DC2801、313→MC282、319→DC9801、320→DC1802、322→DC25、325→MC381、326→DC2910、327→DC2901、334→MC301；其余 15 个 idx 落默认路径 `0x18fb4`。另有 WEARABLE / SEMIPRO 两条独立分支 | psm 字符串池 `0x19088..0x19158` | 同上 |
| B5 | `NET_EVT_SERVICE_MENU_SET_MODEL_INFO` / `GET_MODEL_INFO_LIST` / `SET_BACKUP_FILE_NAME` / `SET_LAST_WATERPROOF_TEST_DATE` / `EXE_CAMERA_ADJUST` / `RESTORE_ADJUSTMENT` 全是 **IPC 事件名**（由 `0x2b600` 一带的"事件号→名字"映射函数返回），**不是网络 mode**；网络面**没有** model-info 写入入口（G100 侧） | psm `0x2aba0`-`0x2b700` 区 | `psm_stridx.txt` |

---

## 2. 对 fuzz 的直接价值（每条对应一个可执行用例族）

1. **A1/A3 ⇒ 身份前缀 fuzz**：`X_FromCP` 取值 `LumixLink` / `LumixLink1.0` / `LumixLink2.0` / `LumixLink2.0`+垃圾 / `lumixlink2.0`（小写）/ 超长 / 前 9 字节命中但尾部炸开的串 —— 观察 dlna 响应差异（能力集、可用服务），验证"S5 是否也按 9 字节前缀开能力门"。
2. **A5 ⇒ 私有头 fuzz**：把 6 个 `X_Panasonic_Cam_*` 头当作**未文档化攻击面**做 fuzz（缺失/重复/超长/畸形值/大小写变形），这是权威文档 dlna 审计里**未覆盖**的一组头名。
3. **B2 ⇒ 分派一致性 fuzz**：`cam.cgi?mode=getinfo&type=capability` 是**整串比较**——测参数换序（`type=...&mode=...`）、大小写、多余参数、`%2b`/`+` 空格编码、末尾 `&` ——若整串匹配但后续解析器按子串取值，就可能出现"分派到 A、解析成 B"的不一致。
4. **B3/B4 ⇒ 机型 ID 影响面**：菜单由 `NETUTIL_GetConfigModelNumber()` 决定文件 —— 与"S5 换机型解锁菜单/功能"这条线**同源**。S5 侧的可执行动作 = **只读**取 `mode=getinfo&type=capability` + `getstate`/`getmenuinfo`，验证机型相关返回值；**不做任何 model-info 写入尝试**（写入入口在网络面不存在，且属红线外动作）。

---

## 3. 未决 / 边界（不要当成结论）

- A3 里身份串（`struct+13`）**是否等于** X_FromCP 的取值：静态未能闭合（SOAP 解析器写的是会话结构 `+0x340c`，身份注册函数读的是自己的入参结构 `+13`；两者结构不同）。**用 fuzz 判**：同一会话内发 `X_FromCP=LumixLink2.0` vs `X_FromCP=XXXX` 对比响应差异。
- A4 的 `0x80000000` 是否与本项目 crash 001（`StartingIndex=2147483647`）同源：**未证**，仅路线提示。
- G100 侧 psm/dlna 里**没有** `func_type` 字符串（`grep -rl func_type fs2` 为空）⇒ S5 的机型能力指纹字段**不可**从 G100 静态取得，只能活体读。
- B4 只覆盖 311..334 区间；S5（MC801 级）机型 ID 不在该区间时落默认路径 —— 需要 S5 侧活体核对。

---

## 4. 复现命令

```bash
FS2=/Users/<user>/Documents/ChatGPT/S5_逆向_项目总包_20261012/19_路径1_Linux侧攻击面_20261015/fs2
arm-none-eabi-objdump -d $FS2/usr/pvc/bin/dlna > /tmp/dlna.asm
arm-none-eabi-objdump -d $FS2/usr/pvc/bin/psm  > /tmp/psm.asm
# 字符串 xref（ldr rN,[pc,#imm] → 字面池 → C 串）
python3 - <<'EOF'
import re,struct
data=open('/dev/stdin','rb')  # 见同目录提取脚本 extract_stridx.py
EOF
# 直接复用本目录已提取产物：
grep -nE "FromCP|Panasonic_Cam|LumixLink" dlna_stridx.txt
grep -nE "menuxml|Capability|accctrl|ModelInfo" psm_stridx.txt
```
（提取器脚本：`extract_stridx.py`，用法 `python3 extract_stridx.py <ELF> <objdump输出> <out.txt>`）
