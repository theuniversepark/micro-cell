#!/bin/sh
# 전체본 빌드: 루트 *.html(로컬 미리보기, git 제외) + docs/*.html(git 포함)
# PUBLIC=1 ./build.sh 로 실행하면 DMWorks 단가를 가린 공개본으로 빌드함
set -e
cd "$(dirname "$0")"
python3 build_page.py && python3 build_ocs.py && python3 build_ocs_pz.py
OUT_DIR=docs python3 build_page.py
OUT_DIR=docs python3 build_ocs.py
OUT_DIR=docs python3 build_ocs_pz.py
python3 web_wrap.py
