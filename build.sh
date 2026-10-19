#!/bin/sh
# 전체본 빌드: 루트 *.html(로컬 미리보기, git 제외) + docs/*.html(git 포함)
# PUBLIC=1 ./build.sh 로 실행하면 DMWorks 단가와 이를 포함한 소계·합계를 가린 공개본으로 빌드함
set -e
cd "$(dirname "$0")"
python3 build_page.py && python3 build_ocs_pz.py && python3 build_dmworks.py && python3 build_ocs_sim.py
OUT_DIR=docs python3 build_ocs_pz.py
OUT_DIR=docs python3 build_dmworks.py
OUT_DIR=docs python3 build_ocs_sim.py
python3 web_wrap.py
# PDF·Word 생성 실패는 빌드 실패로 끝냄. HTML만 만들려면 NO_DOCS=1 (이때 docs/*.pdf·docx는 갱신되지 않음)
if [ "${NO_DOCS:-}" = "1" ]; then
  echo "NO_DOCS=1 — PDF·Word 생성 안 함 (docs/*.pdf·docx는 이전 파일 그대로)"
else
  uv run --quiet --with python-docx --with beautifulsoup4 python export_docs.py
fi
