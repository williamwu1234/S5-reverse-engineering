#!/usr/bin/env bash
# ============================================================================
#  DC-S5 逆向总包 · 一键只读审核脚本
#  生成：2026-10-15   作者：总包审计
#
#  设计原则：
#    * 100% 只读 —— 不修改、不移动、不删除任何文件
#    * 不联网 —— 绝不向相机（192.168.x.x / 192.168.54.1）或任何设备发请求
#    * 不执行被测脚本 —— 只 grep/read 代码，不运行 persist.py / exfat_patch.py
#    * 全部结论现场可复算，输出可直接贴进报告
#
#  用法：
#    cd "/Users/wuwilliam/Documents/ChatGPT/S5_逆向_项目总包_20261012"
#    bash 14_总包审计与新方向_20261015/01_一键只读审核.sh 2>&1 | tee /tmp/s5_audit.txt
#
#  预计耗时：约 1–3 分钟（MANIFEST 全量校验读取约 2.5 GB）
# ============================================================================
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1

hr(){ printf '\n%s\n' "======================================================================"; }
sec(){ hr; printf '## %s\n' "$1"; hr; }

echo "S5 总包只读审核 @ $(date '+%Y-%m-%d %H:%M:%S')"
echo "工作目录: $ROOT"

# ---------------------------------------------------------------------------
sec "A. 仓库规模：文档声明 vs 实测"
echo "文档声明（REPO_CONTENTS.md:7）: 864 个文件 / 41.5 MB / 583 份唯一内容"
echo "文档声明（README.md:74）      : 四个成果包『包内文件已移除，各留一份并库说明』"
echo -n "实测 git 跟踪文件数          : "; git ls-files 2>/dev/null | wc -l | tr -d ' '
echo -n "实测工作树文件数(排除 .git)  : "; find . -type f -not -path "*/.git/*" | wc -l | tr -d ' '
echo    "实测各成果包残留文件数       :"
for d in 08_总结与工具箱_20261013 09_exFAT越界写成果包_20261013 \
         10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013 \
         11_DC-S5成果包_20261013; do
  [ -d "$d" ] && printf '   %5s  %s\n' "$(find "$d" -type f 2>/dev/null | wc -l | tr -d ' ')" "$d"
done

# ---------------------------------------------------------------------------
sec "B. MANIFEST.sha256 完整性"
if [ -f MANIFEST.sha256 ]; then
  echo "清单条数: $(wc -l < MANIFEST.sha256 | tr -d ' ')"
  echo "校验中（读取约 2.5 GB，请稍候）..."
  shasum -a 256 -c MANIFEST.sha256 > /tmp/_s5_mani.txt 2>&1
  echo "  OK     : $(grep -c ': OK$' /tmp/_s5_mani.txt)"
  echo "  FAILED : $(grep -c 'FAILED' /tmp/_s5_mani.txt)"
  echo "  --- 内容已变更（清单生成后又被改写）的文件 ---"
  grep 'FAILED' /tmp/_s5_mani.txt | sed 's/^/    /' || true
  echo "  --- 清单集合 vs 磁盘集合差异（应为空）---"
  sed 's/^[0-9a-f]\{64\}  //' MANIFEST.sha256 | LC_ALL=C sort > /tmp/_s5_mp.txt
  find . -type f -not -path "*/.git/*" -not -name MANIFEST.sha256 -not -name .DS_Store \
    -not -path "./14_总包审计与新方向_20261014/*" | LC_ALL=C sort > /tmp/_s5_dp.txt
  echo "    （已排除本审计目录 14_总包审计与新方向_20261014/）"
  echo "    磁盘有、清单无: $(comm -23 /tmp/_s5_dp.txt /tmp/_s5_mp.txt | wc -l | tr -d ' ')"
  echo "    清单有、磁盘无: $(comm -13 /tmp/_s5_dp.txt /tmp/_s5_mp.txt | wc -l | tr -d ' ')"
else
  echo "!! 未找到 MANIFEST.sha256"
fi

# ---------------------------------------------------------------------------
sec "C. 副本传播：01_研究报告/ 与两个成果包副本逐字节比对"
python3 - <<'PY'
import os,hashlib
A="01_研究报告"
copies=["10_定因与工具链成果包（有风险，非专业人员请勿轻易尝试）_20261013/01_研究报告_全集",
        "11_DC-S5成果包_20261013/01_研究报告_全集"]
def h(p):
    return hashlib.sha256(open(p,'rb').read()).hexdigest()
tops=[f for f in sorted(os.listdir(A)) if f.endswith(".md")]
diff=[]
for f in tops:
    pa=os.path.join(A,f)
    for c in copies:
        pc=os.path.join(c,f)
        if os.path.exists(pc):
            if h(pa)!=h(pc):
                diff.append((f,c))
if not diff:
    print("  ✅ 同名报告全部逐字节一致")
else:
    print("  ❌ 不一致清单（副本为旧版）:")
    for f,c in diff:
        pa=os.path.join(A,f); pc=os.path.join(c,f)
        print("    %-46s 权威 %7d B  副本 %7d B   副本=%s" %
              (f, os.path.getsize(pa), os.path.getsize(pc), c.split('/')[0][:6]))
PY

# ---------------------------------------------------------------------------
sec "D. 65533 字节 camsetting blob 全集：校验和 + 空操作(no-op)写入检测"
python3 - <<'PY'
import os,hashlib,glob,re
SIZE=65533
found=[]
for root,dirs,files in os.walk("."):
    if "/.git" in root: continue
    for f in files:
        if f.endswith(".bin"):
            p=os.path.join(root,f)
            try:
                if os.path.getsize(p)==SIZE: found.append(p)
            except OSError: pass
print(f"  共找到 {len(found)} 个 {SIZE} 字节 blob")
bad=[]
for p in found:
    b=open(p,'rb').read()
    if (sum(b)%256)!=0 or b[SIZE-1]!=((256-sum(b[:SIZE-1]))%256): bad.append(p)
print(f"  校验和不合格: {len(bad)} 个" + ("" if not bad else "\n    "+"\n    ".join(bad)))
print("\n  --- no-op 检测：『写入前备份』与『待写入 payload』是否逐字节相同 ---")
def h(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()
pairs=[]
for p in sorted(glob.glob("04_工具与脚本/campaign2/out/backup_pre_*.bin")):
    ts=re.search(r'(2026\d+_\d+)',p)
    if not ts: continue
    for pat in ("restore_payload_%s.bin","quality_payload_%s.bin","*payload*%s.bin"):
        for c in glob.glob("04_工具与脚本/campaign2/out/"+pat%ts.group(1)):
            pairs.append((p,c))
seen=set()
flagged=0
for bkp,pay in pairs:
    k=(bkp,pay)
    if k in seen: continue
    seen.add(k)
    same = h(bkp)==h(pay)
    if same:
        flagged+=1
        print(f"    ⚠️ 空操作(0 字节差异): {os.path.basename(bkp)}  ==  {os.path.basename(pay)}")
if not flagged: print("    未发现空操作对")
else: print(f"    ⇒ 共 {flagged} 对为『空操作』：写入未改动任何字节，不能作为『写入已落地』的证据")
PY

# ---------------------------------------------------------------------------
sec "E. 固件分区表：记录 SHA 与内容 SHA 的偏移归属（+0x200 判决实验）"
python3 - <<'PY'
import struct,hashlib,os
p="02_固件二进制/DC-S5/S5___V29.bin"
if not os.path.exists(p):
    print("  !! 未找到固件（仓库版不含 .bin，需完整本地总包）"); raise SystemExit
raw=open(p,'rb').read(); base=0x2EC
rows=[]
for i in range(48):
    off=base+i*92
    if off+92>len(raw): break
    name=raw[off:off+12].rstrip(b'\0').decode('ascii','replace')
    doff,dsize,daddr,dtype=struct.unpack_from("<IIII",raw,off+0x0C)
    sha=raw[off+0x1C:off+0x3C].hex()
    def ok(s): return s+dsize<=len(raw) and hashlib.sha256(raw[s:s+dsize]).hexdigest()==sha
    rows.append((name,dtype,ok(0x200+doff),ok(doff)))
t2=[r for r in rows if r[1]==2]; t3=[r for r in rows if r[1]==3]
print(f"  分区总数 {len(rows)}   type=2(明文) {len(t2)}   type=3(加密) {len(t3)}")
print("  记录 SHA 命中率：  doff+0x200 -> %d/%d 明文分区命中" % (sum(r[2] for r in t2), len(t2)))
print("                     doff 原值  -> %d/%d 明文分区命中" % (sum(r[3] for r in t2), len(t2)))
print("  => 若 +0x200 全中而原值不全中，则『记录 SHA != 内容哈希』是脚本偏移 bug 的产物")
ZERO = b"\x00"*16
ivs=[raw[base+i*92+0x3C:base+i*92+0x4C] for i in range(len(rows))]
print("  IV: 全零 %d/%d，唯一值 %d" % (len([v for v in ivs if v == ZERO]), len(ivs), len(set(ivs))))
PY

# ---------------------------------------------------------------------------
sec "F. 菜单快照：视频质量档位实测（验证 18/12/10 的表述）"
python3 - <<'PY'
import re,glob,hashlib,os
seen=set()
for p in sorted(glob.glob("**/curmenu.xml",recursive=True)):
    if "/.git" in p: continue
    d=hashlib.sha256(open(p,'rb').read()).hexdigest()
    if d in seen: continue
    seen.add(d)
    s=open(p,encoding='utf-8',errors='replace').read()
    items=re.findall(r'<item\s+id="(menu_item_id_v_quality_[^"]+)"([^>]*)/?>', s)
    yes=[i for i,a in items if 'enable="yes"' in a]
    mv=[i for i in yes if '_mov_' in i]; mp=[i for i in yes if '_mp4_' in i and 'hevc' not in i]; hv=[i for i in yes if 'hevc' in i]
    print(f"\n  {p}\n    sha256={d[:12]}   v_quality 项={len(items)}  enable=yes={len(yes)}  (mp4={len(mp)} mov={len(mv)} hevc={len(hv)})")
    for i in yes: print("      -",i)
print("\n  注：文档主张 NTSC+mov=18 / PAL+mov=12 / NTSC+mp4=8+2；")
print("      若库内快照均非该四态，则这些数字无法离线复现。")
PY

# ---------------------------------------------------------------------------
sec "G. 敏感信息：内网 IP / MAC / 序列号 在文本层的外露"
echo "--- 内网相机 IP（代码/文档）---"
grep -rInE "192\.168\.[0-9]+\.[0-9]+" --include="*.md" --include="*.py" --include="*.sh" . 2>/dev/null \
  | grep -v '^./MANIFEST' | awk -F: '{print $1}' | sort | uniq -c | sort -rn | head -10
echo "--- MAC / 序列号占位 ---"
grep -rInE "70:74:14|XJL[0-9#]|S5-[0-9A-Fa-f]{6}" --include="*.md" . 2>/dev/null \
  | grep -v '^./MANIFEST' | awk -F: '{print $1}' | sort -u | head -15
echo "--- 真序列号模式 XJL[0-9]{10} 是否残留（应为空）---"
grep -rInE "XJL[0-9]{8,}" --include="*.md" --include="*.txt" --include="*.json" . 2>/dev/null | grep -v '^./MANIFEST' | head -10

# ---------------------------------------------------------------------------
sec "H. 结论残留：已被撤回的表述是否仍在文本/工具/压缩包中"
echo "--- H1 文本层（.md/.txt）---"
grep -rInE "越界写.{0,6}(已实机确认|确认了)|堆喷命中、?越界槽|内存写已执行|越界写成立" \
   --include="*.md" --include="*.txt" . 2>/dev/null | grep -v '^./MANIFEST' | head -20
echo "--- H2 工具代码层（运行时提示会误导操作者）---"
grep -rInE "写入错误.{0,10}(即为已执行|已执行)|内存写.{0,6}已执行|越界写成立" \
   --include="*.py" --include="*.sh" . 2>/dev/null | head -20
echo "--- H3 压缩包层（grep 扫不到的盲区）---"
find . -name "*.zip" -not -path "*/.git/*" 2>/dev/null | while read -r z; do
  n=$(unzip -l "$z" 2>/dev/null | tail -1 | awk '{print $2}')
  echo "    $(du -h "$z" | cut -f1)  $n 条目  $z"
done

# ---------------------------------------------------------------------------
sec "I. 未提交改动 / 嵌套仓库"
echo "--- git status ---"; git status --short 2>/dev/null | head -20
echo "--- 嵌套 .git 仓库（会各自带走一份历史）---"
find . -name .git -maxdepth 4 -not -path "./.git" 2>/dev/null

# ---------------------------------------------------------------------------
sec "汇总提示"
cat <<'EOF'
  对照本次审计报告结论，重点看：
   * A 段：文档规模声明与实际不符（成果包并未真正并库）
   * B 段：FAILED 文件 = 清单生成后被改写的文件（追溯性缺口）
   * C 段：25/26 号报告的旧副本会对外传播过期结论
   * D 段：no-op 写入 ⇒ 持久化旗舰结论证据不成立
   * E 段：+0x200 命中率 ⇒ 判定密码学实验是否被偏移 bug 污染
   * F 段：18/12/10 档位数字能否离线复现
   * H3 段：zip 内的已撤回结论是自动化检查的盲区
EOF
echo
echo "审核完成 @ $(date '+%Y-%m-%d %H:%M:%S')"
