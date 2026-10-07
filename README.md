# 정밀조립존 마이크로 셀 · OCS Cell 설계

총괄5-세부1 기술실증 테스트베드의 **A-3 정밀조립(Micro) Zone** 설계 산출물을 코드로 생성하는 저장소임. 5개 셀 배치·구성품 BOM, 1차년도 OCS 시뮬레이션 Cell 3종, 정밀조립존 OCS Cell(Local Server – Edge Gateway 데이터 계층)을 HTML 페이지로 빌드함.

> 설계 추정본임. 단가는 2026년 국내 시장가 기준 추정·공개가·견적을 섞어 쓰며 등급([공개가·확인]/[공개가·검색]/[견적]/[추정])을 표기함. 금액 단위 천원, VAT 별도.

## 페이지 (공개본, `docs/`)

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
| `privacy.py` | 대외비 단가 분리 스위치(`PUBLIC`, `OUT_DIR`) |
| `build.sh` | 전체 빌드 |

## 빌드

```sh
./build.sh
```

- `docs/*.html` — 공개본. DMWorks 정가 기반 금액은 0원·“비공개”로 표기하고 합계에서 뺌
- 루트 `*.html` — 로컬 전체본. `private_prices.py`(대외비, git 제외)가 있을 때만 생성함

## 대외비 처리

DMWorks 3.0 정가표(이지로보틱스, 대외비)에서 나온 단가는 `private_prices.py`에만 두고 커밋하지 않음. 이 파일이 없으면 모든 빌드가 공개본으로 동작함.
