# 로컬 OCS 구성 (micro-cell)

총괄5-세부1 기술실증 테스트베드의 **A-3 정밀조립(Micro) Zone** 설계 산출물을 코드로 생성하는 저장소임. 로컬 OCS Zone 구성 - (예시) 정밀조립존(Local Server – Edge Gateway 데이터 계층)과 DMWorks 존별 옵션 구성을 HTML·PDF·Word로 빌드함. 셀 구성 계획(`build_page.py`)은 루트 로컬 미리보기로만 만들고 웹에는 올리지 않음.

> 설계 추정본임. 단가는 2026년 국내 시장가 기준 추정·공개가·견적을 섞어 쓰며 등급([공개가·확인]/[공개가·검색]/[견적]/[추정])을 표기함. 금액 단위 천원, VAT 별도.

## 페이지 (`docs/`)

웹에서 보기: **https://theuniversepark.github.io/micro-cell/** (GitHub Pages, 로그인 불필요) · 각 페이지 상단의 PDF 저장·Word 저장 버튼으로 내려받기


| 파일 | 내용 |
|---|---|
| `docs/ocs_precision.html` | 로컬 OCS Zone 구성 - (예시) 정밀조립존 — AAS 기반 수집–저장 공통 아키텍처, 물리 연결 토폴로지, 설치 배치, 데이터량·저장 용량 산정, 존/셀 HW·SW 목록 |
| `docs/dmworks_zones.html` | DMWorks 존별 옵션 구성 — 이지로보틱스 10/15 최종 견적 3건(1015-1~3, 정가×57.2%) 기준 존별 구매 필요성·해야 할 일·옵션, 품목별 검토(적합·확인), 10/8 대비 변경, 정밀조립 1좌석 추정, 계약 전 쟁점 |
| `docs/ocs_sim_fms.html` · `ocs_sim_adaptive.html` · `ocs_sim_qms.html` | 유연제조·적응가공·AI정밀검사 통합 OCS 시뮬레이션 Cell — 10/15 최종 견적 항목 기반 장비 설치·연결 토폴로지, 구성품별 사양·금액(일반 명칭), 10/18 중장위 심의 지침 점검 |

**견적서 파일 선택**: DMWorks 페이지 상단 '견적서 파일 선택'(또는 끌어다 놓기)으로 이지로보틱스 견적서 엑셀(존별 시트, 항목1~6)을 고르면 브라우저 안에서 읽어 존별 견적 표·요약·단가표·정밀조립 산정을 다시 그리고, 기준 견적(10/15)과 달라진 품목(변경·추가·삭제)을 표시함. 고른 견적은 그 브라우저의 localStorage에 남아 OCS 시뮬레이션 Cell 3종 페이지(요약·KPI·구성품 표·지침 점검 수치·토폴로지 스캐너·운영 PC 탑재 SW)에도 자동 반영됨(OCS 페이지 상단에서 직접 골라도 됨 — 페이지마다 저장소가 따로인 claude.ai 아티팩트에서는 이 방식). 파일은 서버로 전송되지 않음. 서술형 설명·공간 배치도·PDF·Word 저장본은 기준 견적 그대로이며, '기준 견적으로 되돌리기'로 원상 복구.

## 구조

| 파일 | 역할 |
|---|---|
| `cells_data.py` | 존 블록·5개 셀 구성품·레이아웃, 표준 로봇·카메라 기준 적용(`_apply_standard`) |
| `build_page.py` | 셀 구성 계획 페이지 생성, 공통 CSS·BOM 표 헬퍼 |
| `ocs_pz_products.py` / `build_ocs_pz.py` | 로컬 OCS Zone 구성 - (예시) 정밀조립존 제품·출처·수량 근거·Use Case, 페이지·도면·데이터량 산정 |
| `private_prices.py` | 정밀조립존 DMWorks 1좌석 단가(10/8 견적 단가 기준) |
| `privacy.py` | 단가 마스킹 스위치(`PUBLIC=1`이면 DMWorks 정가·견적 단가와 이를 포함한 소계·일반관리비·합계를 '비공개' 표기, 정밀조립존 DMWorks는 0원), 출력 폴더(`OUT_DIR`) |
| `web_wrap.py` | `docs/`를 독립 웹 페이지로 감쌈(doctype·이동 바) + `index.html` 생성 |
| `build_dmworks.py` | DMWorks 존별 옵션 구성 페이지 생성 |
| `build_ocs_sim.py` | OCS 시뮬레이션 Cell 3종 페이지 생성 |
| `quote_live.py` / `quote_live.js` | 견적서 파일 선택 — 기준 견적 JSON·패널을 페이지에 넣고, 브라우저에서 엑셀을 읽어(SheetJS) 기준 견적과 대조해 표를 다시 그림(Python 표와 같은 HTML) |
| `export_docs.py` | `docs/*.pdf`(Chrome 인쇄, A3 가로)·`docs/*.docx`(python-docx, 도면 PNG 삽입) 생성 — 웹의 PDF·Word 저장 버튼용 |
| `build.sh` | 전체 빌드 |

## 빌드

```sh
./build.sh            # docs/*.html·pdf·docx 전체본 생성 (DMWorks 단가 포함 — 2026-10-08 사용자 결정으로 공개)
PUBLIC=1 ./build.sh   # DMWorks 단가와 이를 포함한 소계·합계를 '비공개'로 가린 버전 (OCS 시뮬레이션 Cell 견적서 원본 절 제외)
NO_DOCS=1 ./build.sh  # HTML만 생성 (PDF·Word는 갱신 안 함)
```

PDF·Word 생성(`export_docs.py`)이 실패하면 빌드가 실패로 끝남. 새 파일은 임시 경로에서 만들어 검증한 뒤 교체하므로 실패 시 이전 파일이 새 결과로 보고되지 않음.
