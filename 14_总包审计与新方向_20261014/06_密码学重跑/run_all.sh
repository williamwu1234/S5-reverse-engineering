#!/usr/bin/env bash
# 一键重跑：S5 固件密码学（修正 +0x200 偏移后）
# 全程只读固件文件，不联网、不连接相机。所有输出写入 ./out/
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p out

echo "== [0] 单一真源判决实验（必须 7/7，否则停止） =="
python3 upd_table.py | tee out/00_self_test.txt

echo
echo "== [1] 记录 SHA 语义（全部 48 分区，两偏移对照） =="
python3 exp1_record_sha.py | tee out/01_exp1_record_sha.txt

echo
echo "== [2] 已知明文 / keystream / 模式判决 =="
python3 exp2_known_plaintext_mode.py | tee out/02_exp2_known_plaintext_mode.txt

echo
echo "== [3] 跨版本密文一致性（V29 vs V24，附 V11/V20/V23） =="
python3 exp3_cross_version.py | tee out/03_exp3_cross_version.txt

echo
echo "== [4] 阳性对照：错误偏移是否漏检正确密钥（约 30 秒） =="
python3 exp4_positive_control.py | tee out/04_exp4_positive_control.txt

echo
echo "全部完成。逐项判读见 结论.md"
