# 정밀조립존 마이크로 셀 · OCS Cell 설계

총괄5-세부1 기술실증 테스트베드의 **A-3 정밀조립(Micro) Zone** 설계 산출물을 코드로 생성하는 저장소임. 5개 셀 배치·구성품 BOM, 1차년도 OCS 시뮬레이션 Cell 3종, 정밀조립존 OCS Cell(Local Server – Edge Gateway 데이터 계층)을 HTML 페이지로 빌드함.

> 설계 추정본임. 단가는 2026년 국내 시장가 기준 추정·공개가·견적을 섞어 쓰며 등급([공개가·확인]/[공개가·검색]/[견적]/[추정])을 표기함. 금액 단위 천원, VAT 별도.

## 페이지 (`docs/`)

| 파일 | 내용 |
|---|---|
| `docs/precision_zone.html` | 정밀조립존 셀 구성 계획 — 존 2D 배치도, A-3-1~A-3-5 셀별 HW·SW BOM(셀당 협동로봇 10·AMR 4·AMMR 1, 로봇별 카메라 3대) |
| `docs/ocs_cells.html` | 1차년도 통합 OCS 시뮬레이션 Cell 3종(A-1-4·A-2-5·A-4-5) — 존별 목적·계층 구성·장비 목록 |
| `docs/ocs_precision.html` | 정밀조립존 OCS Cell — AAS 기반 수집–저장 공통 아키텍처, 물리 연결 토폴로지, 설치 배치, 데이터량·저장 용량 산정, 존/셀 HW·SW 목록 |

## 구조

| 파일 | 역할 |
|---|---|
| `cells_data.py` | 존 블록·5개 셀 구성품·레이아웃, 표준 로봇·카메라 기준 적용(`_apply_standard`) |
| `build_page.py` | 셀 구성 계획 페이지 생성, 공통 CSS·BOM 표 헬퍼 |
| `ocs_data.py` / `build_ocs.py` | OCS 셀 3종 데이터·페이지 |
| `ocs_pz_products.py` / `build_ocs_pz.py` | 정밀조립존 OCS Cell 제품·출처·수량 근거·Use Case, 페이지·도면·데이터량 산정 |
| `private_prices.py` | DMWorks 3.0 정가(이지로보틱스, 2026.01) 기반 단가 |
| `privacy.py` | 단가 마스킹 스위치(`PUBLIC=1`이면 DMWorks 금액 0·비공개 표기), 출력 폴더(`OUT_DIR`) |
| `build.sh` | 전체 빌드 |

## 빌드

```sh
./build.sh            # docs/*.html 전체본 생성 (DMWorks 단가 포함)
PUBLIC=1 ./build.sh   # DMWorks 단가를 0원·비공개로 가린 버전
```
