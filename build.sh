#!/bin/sh
# 로컬 전체본(대외비 단가 포함, private_prices.py 필요) → 루트 *.html (git 제외)
# 공개본(DMWorks 단가 비공개) → docs/*.html (git 포함)
set -e
cd "$(dirname "$0")"
if [ -f private_prices.py ]; then
  python3 build_page.py && python3 build_ocs.py && python3 build_ocs_pz.py
fi
PUBLIC=1 OUT_DIR=docs python3 build_page.py
PUBLIC=1 OUT_DIR=docs python3 build_ocs.py
PUBLIC=1 OUT_DIR=docs python3 build_ocs_pz.py
