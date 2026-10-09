# Local OCS 설계 기획 (micro-cell)

총괄5-세부1 기술실증 테스트베드의 **A-3 정밀조립(Micro) Zone** 설계 산출물을 코드로 생성하는 저장소임. 로컬 OCS Zone 구성 - (예시) 정밀조립존(Local Server – Edge Gateway 데이터 계층)과 DMWorks 존별 옵션 구성을 HTML·PDF·Word로 빌드함. 셀 구성 계획(`build_page.py`)은 루트 로컬 미리보기로만 만들고 웹에는 올리지 않음.

> 설계 추정본임. 단가는 2026년 국내 시장가 기준 추정·공개가·견적을 섞어 쓰며 등급([공개가·확인]/[공개가·검색]/[견적]/[추정])을 표기함. 금액 단위 천원, VAT 별도.

## 페이지 (`docs/`)

웹에서 보기: **https://theuniversepark.github.io/micro-cell/** (GitHub Pages, 로그인 불필요) · 각 페이지 상단의 PDF 저장·Word 저장 버튼으로 내려받기


| 파일 | 내용 |
|---|---|
| `docs/ocs_precision.html` | 로컬 OCS Zone 구성 - (예시) 정밀조립존 — AAS 기반 수집–저장 공통 아키텍처, 물리 연결 토폴로지, 설치 배치, 데이터량·저장 용량 산정, 존/셀 HW·SW 목록 |
| `docs/dmworks_zones.html` | DMWorks 존별 옵션 구성 — 이지로보틱스 10/8 견적 3건(정가×52%) 기준 존별 구매 필요성·해야 할 일·옵션, 품목별 검토(적합·확인·조정), 정밀조립 1좌석 추정, 재견적 쟁점 |

## 구조

| 파일 | 역할 |
|---|---|
| `cells_data.py` | 존 블록·5개 셀 구성품·레이아웃, 표준 로봇·카메라 기준 적용(`_apply_standard`) |
| `build_page.py` | 셀 구성 계획 페이지 생성, 공통 CSS·BOM 표 헬퍼 |
| `ocs_pz_products.py` / `build_ocs_pz.py` | 로컬 OCS Zone 구성 - (예시) 정밀조립존 제품·출처·수량 근거·Use Case, 페이지·도면·데이터량 산정 |
| `private_prices.py` | 정밀조립존 DMWorks 1좌석 단가(10/8 견적 단가 기준) |
| `privacy.py` | 단가 마스킹 스위치(`PUBLIC=1`이면 DMWorks 금액 0·비공개 표기), 출력 폴더(`OUT_DIR`) |
| `web_wrap.py` | `docs/`를 독립 웹 페이지로 감쌈(doctype·이동 바) + `index.html` 생성 |
| `build_dmworks.py` | DMWorks 존별 옵션 구성 페이지 생성 |
| `export_docs.py` | `docs/*.pdf`(Chrome 인쇄, A3 가로)·`docs/*.docx`(python-docx, 도면 PNG 삽입) 생성 — 웹의 PDF·Word 저장 버튼용 |
| `build.sh` | 전체 빌드 |

## 빌드

```sh
./build.sh            # docs/*.html 전체본 생성 (DMWorks 단가 포함)
PUBLIC=1 ./build.sh   # DMWorks 단가를 0원·비공개로 가린 버전
```
