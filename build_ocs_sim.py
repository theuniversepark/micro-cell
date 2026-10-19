"""OCS 시뮬레이션 Cell 3종(유연제조·적응가공·AI정밀검사) 장비 설치·연결 구성 페이지 → ocs_sim_fms.html · ocs_sim_adaptive.html · ocs_sim_qms.html
근거: 이지로보틱스 10/15 최종 견적서(견26CAMTIC-DMWorks-1015-1~3), 10/16 자체장비심의 발표자료(1-3. 발표자료_이형수),
10/18 유지연 팀장 메일 「자체장비 심의시 질의&제안사항 공유 및 중장위 심의 준비(~10.21/수) 안내」·첨부 「26.10.16_자체장비심의 질의응답_제안사항.hwpx」.
심의위원 공통 지침에 따라 품목은 일반 명칭·사양으로 적고, 견적서 기재 품목명(업체·모델)은 내부 대조 열에만 둠."""
import html

import build_ocs_pz as pz
from privacy import out

E = html.escape
CSS, PZ_EXTRA = pz.CSS, pz.EXTRA


def k(n):
    return f"{n:,.0f}"


# ------------------------------------------------------------------ 일반 명칭·사양 (업체·모델명 없음)
# key: (구성품 일반 명칭, 세부 사양, 설치 노드)
GEN = {
    "BASE": ("3D 공정 시뮬레이션 SW 기본 모듈", "설비 기구학 모델링(관절·좌표계·CAD 형상) + 공장 레이아웃·로봇 라이브러리·모션/Task·충돌검사·케이블 시뮬레이션(단일 공정). 네트워크 라이선스", "OPC"),
    "MON": ("DT 실시간 모니터링 모듈", "설비 실시간 연동으로 가상모델 동작 동기화, Cell/Zone 생산량·진행률·사이클타임 분할 화면, 사용자 권한 관리", "MON"),
    "CADI": ("CAD 입력 변환 모듈 (포맷당)", "외부 CAD 형상을 시뮬레이션 모델로 변환·경량화. 포맷당 1모듈", "OPC"),
    "CADE": ("CAD 출력 변환 모듈 (포맷당)", "시뮬레이션 모델을 외부 표준 포맷으로 출력. 포맷당 1모듈", "OPC"),
    "OLP": ("로봇 오프라인 프로그래밍 모듈 (제어기당)", "가상환경에서 로봇 작업 프로그램 생성·간섭 검증 후 제어기 언어로 변환·다운로드. 제어기 기종당 1모듈", "OPC"),
    "RRS": ("로봇 제어기 연동 사이클타임 정밀 산출 모듈 (제어기당)", "로봇 제조사 제어 알고리즘(RCS) 연동으로 경로·사이클타임 정밀 산출. RCS 모듈은 로봇 제조사 별도 제공", "OPC"),
    "PC": ("3D 스캔 점군 처리 모듈", "점군 데이터 반입·정합·경량화, 실측 점군 위에 가상 작업장 구성", "OPC"),
    "MP": ("다공정·물류 시뮬레이션 모듈", "다공정 라인·컨베이어·AMR 물류·버퍼 모델링, UPH·가동률·병목 분석", "OPC"),
    "PLC": ("PLC 가상 시운전 모듈 (PLC 기종당)", "PLC 프로그램–가상 설비 연동(OPC UA), I/O 매핑, 인터록·시퀀스·이상복구 검증. 상태 읽기 + 핸드셰이크 방식", "OPC"),
    "PID": ("기능 확장 개발 키트 (API)", "API로 전용 기능·UI 개발 — AAS 출력, OCS 연동, 외부 AI 연계", "OPC"),
    "PIU": ("기능 확장 실행 모듈", "개발한 확장 기능 실행 환경", "OPC"),
    "USD": ("OpenUSD 변환 모듈", "Workcell을 계층 구조 그대로 OpenUSD로 변환해 학습 DT 서버에 업로드, 물리 설정 정보 반영", "OPC"),
    "LE": ("OpenUSD 실시간 동기화 모듈", "공정 시뮬레이션–학습 DT 간 위치·동작 실시간 동기화(리뷰 세션용)", "OPC"),
    "ACSB": ("검사결과 기반 리워크 프로그램 자동생성 모듈", "결함 위치 3D 좌표로 로봇 리워크 경로·레시피 자동 생성, AI 판정 결과 연동", "OPC"),
    "ACSO": ("리워크 경로 로봇 프로그램 변환 모듈 (제어기당)", "리워크 경로를 로봇 제어기 형식 프로그램으로 생성. 제어기 기종당 1모듈", "OPC"),
    "PIA": ("스캔 측정결과 분석·시각화 SW", "3D 스캔 데이터 경량화, 설계 대비 편차 컬러맵·단면·차트 시각화로 품질 경향 분석", "OPC"),
    "TES": ("용접부 품질 자동 판정 SW", "스캔 데이터로 저항 점용접 품질 자동 판정, 용접 조건 제시", "OPC"),
    "AIMSS": ("로봇 자동 측정 시뮬레이션 모듈 (제어기당)", "가상 측정 작업장 구성, 측정기 캘리브레이션·측정 경로 시뮬레이션, 측정 로봇 오프라인 프로그래밍", "OPC"),
    "AIMSC": ("측정 시스템 통합 제어 모듈 (제어기당)", "측정기·로봇 통합 제어, 측정 데이터 수집, 실시간 결과 모니터링", "OPC"),
    "AMC": ("SW 유지보수 (연간)", "위 SW 합계의 연 18% × 4년. 버전 업데이트·기술지원", None),
}

# 견적서 공통 HW·로컬 구성 (단가 천원)
SRV_SPEC = ("4U급 GPU 서버 · 서버용 CPU 128코어급 ×2 · DDR5 RDIMM 64GB ×12(768GB) · 데이터 SSD U.2 7.68TB ×4 · OS SSD M.2 NVMe 8TB ×2 · "
            "전문가용 GPU 96GB ×4 · 차세대 방화벽 1식 포함 · 설치")
LOCAL_SUB = [  # (기호, 구성품, 사양, 수량 표기)
    ("DPS", "데이터 처리 서버", "2U 2소켓 랙서버 · RAM 128GB · NVMe SSD 3.84TB (견적서 '등')", "5대"),
    ("NAS", "통합 스토리지", "올플래시 · U.2 4TB SSD ×15 (raw 60TB)", "1식"),
    ("BAK", "백업 스토리지", "견적서에 사양 없음", "1식"),
    ("EGW", "Edge Gateway", "견적서에 사양·수량 없음", "–"),
    ("VNODE", "영상 수집 노드", "견적서에 사양·수량 없음", "–"),
    ("NET", "네트워크 — 코어·TSN·방화벽·PTP·AP·배선", "견적서에 사양·수량 없음", "1식"),
    ("RACK", "서버실 — 랙·캐비닛·UPS·KVM", "견적서에 사양·수량 없음", "1식"),
]

# ------------------------------------------------------------------ 존별 10/15 최종 견적 (천원)
# SW: (번호, key, 상세(일반), 수량, 단가, 견적서 기재 품목)
ZONES = [
    {
        "slug": "fms", "id": "A-1-4", "name": "유연제조(FMS) 통합 OCS 시뮬레이션 Cell", "short": "유연제조",
        "zone": "유연제조존 (A-1)", "no": "견26CAMTIC-DMWorks-1015-1", "title": "캠틱종합기술원 유연제조 ZONE 디지털 트윈 시뮬레이션 시스템 구축 견적서",
        "total": 1991000, "ga": 125088.606, "cmp": 2258000, "lhw": 528000,
        "sw": [
            ("1-1", "BASE", "", 1, 81338.4, "DMWorks Base"),
            ("1-2", "MON", "", 1, 35200, "DM-Monitoring"),
            ("1-3", "CADI", "STL·CATIA·AutoCAD 3종", 3, 5148, "CAD IMPORT - STL, CATIA, AUTOCAD"),
            ("1-4", "CADE", "JT 1종", 1, 5148, "CAD EXPORT - JT"),
            ("1-5", "OLP", "Cell 로봇 제어기 2종", 2, 13728, "DM OLP - HYUNDAI, KAWASAKI"),
            ("1-6", "RRS", "Cell 로봇 제어기 1종", 1, 11440, "DM RRS - HYUNDAI"),
            ("1-7", "PC", "", 1, 21736, "DM POINT CLOUD"),
            ("1-8", "MP", "", 1, 26312, "DM MULTIPLE PROCESS"),
            ("1-9", "PLC", "Cell PLC 2종", 2, 25282.4, "DM PLC SIMULATION - LS, MITSUBISHI"),
            ("1-10", "PID", "", 1, 24024, "DM PLUG-IN For Developer"),
            ("1-11", "PIU", "", 1, 8008, "DM PLUG-IN For User"),
            ("1-12", "USD", "", 1, 15840, "Omniverse USD Converter"),
            ("1-13", "LE", "", 1, 11440, "Omniverse Live Edit"),
            ("1-14", "AMC", "4년", 4, 60111.216, "AMC(Annual Maintenance Charge)"),
        ],
        "scan": ("광대역 3D 공간 스캐너 (HW·운영 SW 포함)", "공장·Cell 공간 스캔, 컬러 점군 취득. 측정거리·정확도·스캔 속도는 견적서에 없음 — 규격서 기재 필요",
                 171600, "광대역 스캐너 - RTC700 (HW 및 운영 SW포함)", "현장 이동형 · 삼각대"),
        "ts": [("5-1", "Cell 구성 설비별 DT 연동 기능 개발", 11000), ("5-2", "DB 연동 시각화 UI 개발", 28050), ("5-3", "기능 확장(플러그인) 개발", 5500)],
        "cells": [
            ("금속 판넬 유연 제조 (용접조립)", "'28 연결", ["용접·핸들링 로봇 제어기", "Cell PLC", "모듈형 지그·픽스처", "비전 위치·자세 인식"]),
            ("정밀 위치 제어 부품 장착 조립", "'28 연결", ["조립 로봇 제어기", "Cell PLC", "다중 캐리지", "비전 위치 인식"]),
            ("AMR/AGV Cell 간 이동 연계", "'27 연결", ["AMR·AGV", "AMR 관제", "도킹·충전 스테이션", "Cell PLC"]),
        ],
        "deck": "1-3. 발표자료_이형수 1~16쪽",
    },
    {
        "slug": "adaptive", "id": "A-2-5", "name": "적응가공(Adaptive) 통합 OCS 시뮬레이션 Cell", "short": "적응가공",
        "zone": "적응가공존 (A-2)", "no": "견26CAMTIC-DMWorks-1015-2", "title": "캠틱종합기술원 적응가공 ZONE 디지털 트윈 시뮬레이션 시스템 구축 견적서",
        "total": 2192000, "ga": 129299.178, "cmp": 2400000, "lhw": 682000,
        "sw": [
            ("1-1", "BASE", "", 1, 81338.4, "DMWorks Base"),
            ("1-2", "MON", "", 1, 35200, "DM-Monitoring"),
            ("1-3", "CADI", "NX·JT·Solid Edge·SolidWorks 4종", 4, 5148, "CAD IMPORT - NX, JT, SOLID EDGE, SOLIDWORKS"),
            ("1-4", "CADE", "AAS·JT·IGES·FBX 4종", 4, 5148, "CAD EXPORT - AAS, JT, IGES, FBX"),
            ("1-5", "OLP", "Cell 로봇 제어기 2종", 2, 13728, "DM OLP - YASKAWA, KUKA"),
            ("1-6", "PC", "", 1, 21736, "DM POINT CLOUD"),
            ("1-7", "MP", "", 1, 26312, "DM MULTIPLE PROCESS"),
            ("1-8", "PLC", "Cell PLC 1종", 1, 25282.4, "DM PLC SIMULATION - SIMENS"),
            ("1-9", "PID", "", 1, 24024, "DM PLUG-IN For Developer"),
            ("1-10", "PIU", "", 1, 8008, "DM PLUG-IN For User"),
            ("1-11", "USD", "", 1, 15840, "Omniverse USD Converter"),
            ("1-12", "LE", "", 1, 11440, "Omniverse Live Edit"),
            ("1-13", "AMC", "4년", 4, 57207.744, "AMC(Annual Maintenance Charge)"),
        ],
        "scan": ("소형 제품 자동 3D 스캐너 (HW·운영 SW 포함)", "가공 소재·제품 자동 스캔, 점군을 가상 작업장·검사모델에 반영. 측정 범위·정확도·자동화 구성은 견적서에 없음 — 규격서 기재 필요",
                 209000, "소형 제품 스캐너(자동) - HyperScan (HW 및 운영 SW포함)", "자동 스캔 스테이션"),
        "ts": [("5-1", "Cell 구성 설비별 DT 연동 기능 개발", 22000), ("5-2", "DB 연동 시각화 UI 개발", 44000), ("5-3", "기능 확장(플러그인) 개발", 11000)],
        "cells": [
            ("고속 가공기·이기종 로봇 협업", "", ["5축 머시닝센터 CNC", "로딩 로봇 제어기", "Cell PLC", "팔레트·AMR"]),
            ("절삭가공 실시간 AI 품질예측", "", ["가공기 CNC", "공구·진동 센서", "Cell PLC", "비전"]),
            ("선삭가공·이기종 로봇 협업", "", ["복합가공기 CNC", "로봇 제어기", "Cell PLC", "AMR"]),
            ("초정밀 측정 및 리워크 연계", "", ["접촉식 측정기", "후처리·표면검사", "로봇 제어기", "Cell PLC"]),
        ],
        "deck": "1-3. 발표자료_이형수 17~30쪽",
    },
    {
        "slug": "qms", "id": "A-4-5", "name": "AI 정밀검사(QMS) 통합 OCS 시뮬레이션 Cell", "short": "AI정밀검사",
        "zone": "AI정밀검사존 (A-4)", "no": "견26CAMTIC-DMWorks-1015-3", "title": "캠틱종합기술원 AI 정밀 검사 ZONE 디지털 트윈 시뮬레이션 시스템 구축 견적서",
        "total": 2610000, "ga": 172301.082, "cmp": 3059000, "lhw": 627000,
        "sw": [
            ("1-1", "BASE", "", 1, 81338.4, "DMWorks Base"),
            ("1-2", "MON", "", 1, 35200, "DM-Monitoring"),
            ("1-3", "CADI", "STEP·OBJ·AAS·Parasolid 4종", 4, 5148, "CAD IMPORT - STEP, OBJ, AAS, PARASOLID"),
            ("1-4", "CADE", "AAS·STEP·Parasolid 3종", 3, 5148, "CAD EXPORT - AAS, STP, PARASOLID"),
            ("1-5", "OLP", "Cell 로봇 제어기 2종", 2, 13728, "DM OLP - FANUC, ABB"),
            ("1-6", "RRS", "Cell 로봇 제어기 1종", 1, 11440, "DM RRS - FANUC"),
            ("1-7", "PC", "", 1, 21736, "DM POINT CLOUD"),
            ("1-8", "MP", "", 1, 26312, "DM MULTIPLE PROCESS"),
            ("1-9", "PLC", "Cell PLC 1종", 1, 25282.4, "DM PLC SIMULATION - ROCKWELL"),
            ("1-10", "PID", "", 1, 24024, "DM PLUG-IN For Developer"),
            ("1-11", "PIU", "", 1, 8008, "DM PLUG-IN For User"),
            ("1-12", "USD", "", 1, 15840, "Omniverse USD Converter"),
            ("1-13", "LE", "", 1, 11440, "Omniverse Live Edit"),
            ("1-14", "ACSB", "", 1, 28600, "ACS BASE"),
            ("1-15", "ACSO", "Cell 로봇 제어기 2종", 2, 18920, "ACS OLP - FANUC, ABB"),
            ("1-16", "PIA", "", 1, 35200, "PIA"),
            ("1-17", "TES", "", 1, 66000, "TESCar"),
            ("1-18", "AIMSS", "Cell 로봇 제어기 2종", 2, 52800, "AIMS - SIMULATOR (FANUC, ABB)"),
            ("1-19", "AIMSC", "Cell 로봇 제어기 2종", 2, 39600, "AIMS - CONTROLLER (FANUC, ABB)"),
            ("1-20", "AMC", "4년", 4, 121779.504, "AMC(Annual Maintenance Charge)"),
        ],
        "scan": None,
        "ts": [("5-1", "Cell 구성 설비별 DT 연동 기능 개발", 22000), ("5-2", "DB 연동 시각화 UI 개발", 44000), ("5-3", "기능 확장(플러그인) 개발", 11000),
               ("5-4", "리워크 자동생성 시스템 연동 개발", 22000)],
        "cells": [
            ("초고성능 로봇형 검사 비전", "", ["검사 로봇 제어기", "표면 비전", "Cell PLC", "AMR"]),
            ("3D 스캔·초음파 용접 검사 로봇", "", ["3D 스캔·레이저 트래커", "초음파 검사", "로봇 제어기", "Cell PLC"]),
            ("4족 보행 검사·안전 모니터링", "", ["4족 보행 검사 로봇", "열화상·비전", "무선 관제", "안전 센서"]),
            ("원키트(One-Kit) 비전 센서 드론", "", ["무인 조사 드론", "비전 센서 키트", "무선 관제", "도킹 스테이션"]),
        ],
        "deck": "1-3. 발표자료_이형수 31~46쪽",
    },
]
TS_LABEL = {"Cell 구성 설비별 DT 연동 기능 개발": "CELL 구성 설비별 디지털 트윈 연동 기능 Customizing", "DB 연동 시각화 UI 개발": "DB 연동 시각화 UI Customizing",
            "기능 확장(플러그인) 개발": "DM PLUG-IN 기능 Customizing", "리워크 자동생성 시스템 연동 개발": "ACS 시스템 Customizing"}
NODE_NAME = {"OPC": "DT·시뮬레이션 운영 PC", "MON": "DT 모니터링 시스템", "DPS": "데이터 처리 서버", "GPU": "DT·AI 연산 서버", "FW": "방화벽 (OT/IT 경계)"}


def hw_rows(z):
    """(번호, 구분, 기호, 구성품, 사양, 수량, 단가, 견적서 기재 품목, 노드, 점검)"""
    r = []
    n = 1
    if z["scan"]:
        nm, sp, up, lab, _ = z["scan"]
        r.append((f"2-{n}", "OCS HW", "SCN", nm, sp, 1, up, lab, "SCN", "spec")); n += 1
    r += [(f"2-{n}", "OCS HW", "GPU", "DT·AI 연산 서버 (방화벽 포함)", SRV_SPEC, 1, 385000, "서버 - ESC8000A-E13P · EPYC 9755×2 · RTX PRO 6000 ×4 · 방화벽 NGF 1300", "GPU", "ok"),
          (f"2-{n + 1}", "OCS HW", "OPC", "DT·시뮬레이션 운영 PC", "견적서에 사양 없음 — CPU·RAM·GPU·모니터 사양 기재 필요", 1, 13200, "디지털 트윈 및 시뮬레이션 운영 PC", "OPC", "spec"),
          (f"2-{n + 2}", "OCS HW", "NB", "시뮬레이션 운영 노트북", "견적서에 사양 없음 — 현장 시운전·스캔 작업용 사양 기재 필요", 1, 7150, "시뮬레이션 운영 노트북", "NB", "spec"),
          (f"2-{n + 3}", "OCS HW", "MON", "DT 모니터링 시스템 (구성품·설치·연동 셋업)", "견적서에 구성품 없음 — 표시장치·제어 PC 등 구성품과 금액 구분 필요", 1, 55000, "모니터링 구성품 구매, 설치 시스템 연동 셋업", "MON", "lump")]
    return r


def zone_rows(z):
    """견적서 항목 순서 그대로 모든 행 (그룹, 번호, 기호, 구성품, 사양, 수량, 단위, 단가, 금액, 견적서 품목, 노드, 점검, sub)"""
    rows = []
    for no, key, det, q, u, lab in z["sw"]:
        nm, sp, node = GEN[key]
        sp2 = f"{det} — {sp}" if det and key != "AMC" else sp
        chk = "maker" if key in ("OLP", "RRS", "PLC", "ACSO", "AIMSS", "AIMSC") else ("amc" if key == "AMC" else "ok")
        rows.append(("항목1. OCS SW", no, key, nm, sp2, q, "년" if key == "AMC" else ("카피" if q == 1 else "모듈"), u, q * u, lab, node, chk, False))
    for no, g, sym, nm, sp, q, u, lab, node, chk in hw_rows(z):
        rows.append(("항목2. OCS HW", no, sym, nm, sp, q, "식" if sym == "MON" else "대", u, q * u, lab, node, chk, False))
    rows.append(("항목3. 로컬 HW", "3-1", "LHW", "로컬 데이터·네트워크 기반 (1식)", "아래 7개 구성품을 1식 금액으로만 제시 — 견적서 '상세 사양 별도 협의 필요'", 1, "식", z["lhw"], z["lhw"],
                 "데이터 처리 서버 - HP3 ProLiant DL380 GEN12 x 5 등 · NAS(Dell PowerStore 1200T) · 백업 스토리지 · Edge Gateway · 영상 수집 노드 · 네트워크 · 서버실", None, "lump", False))
    for i, (sym, nm, sp, qs) in enumerate(LOCAL_SUB):
        rows.append(("항목3. 로컬 HW", f"3-1-{'abcdefg'[i]}", sym, nm, sp, qs, "", None, None, "", sym, "split", True))
    rows.append(("항목4. 로컬 OCS·보안", "4-1", "TSDB", "운영 시계열 DB (클러스터·계층형)", "Cell 상태·이벤트·공정값 시계열 저장·조회, 계층형 클러스터 구성", 1, "식", 49500, 49500,
                 "Operational TSDB - Machbase Cluster Edition (계층)", "DPS", "ok", False))
    rows.append(("항목4. 로컬 OCS·보안", "4-2", "SEC", "통합 인증·접근통제 (IAM/PKI · 서버 접근제어)", "사용자·장비 인증(SSO·PKI 인증서), 서버·DB 접근통제·감사로그", 1, "식", 38500, 38500,
                 "보안 스택(IAM/PKI) - Keyloak+HIWARE", "DPS", "ok", False))
    for no, nm, u in z["ts"]:
        rows.append(("항목5. 기술지원", no, "TS", nm, "공급사 맞춤 개발(Customizing) — 산출물·범위 명시 필요", 1, "식", u, u, TS_LABEL[nm], None, "scope", False))
    return rows


CHK = {"ok": ("적합", "ok"), "spec": ("사양 보완", "chk"), "lump": ("금액 미구분", "adj"), "split": ("금액 미구분", "adj"),
       "maker": ("기종 확인", "chk"), "amc": ("기간 확인", "chk"), "scope": ("범위 명시", "chk")}
CHK_NOTE = {"spec": "규격서에 성능·사양 수치 기재", "lump": "구성품별 금액으로 나눈 견적 필요(총액만이면 불인정)", "split": "구성품별 금액 없음",
            "maker": "Cell 실발주 기종과 일치 확인. 제출 서류엔 제조사명 대신 '제어기 n종'", "amc": "견적서 참고사항 '5년 AMC' vs 계산 ×4",
            "scope": "개발 범위·산출물·투입 M/M 명시"}


# ------------------------------------------------------------------ 연결 토폴로지
def topo_svg(z):
    cells = z["cells"]
    H = 948
    o = [f'<svg class="arch plan" viewBox="0 0 1120 {H}" role="img" aria-label="{E(z["name"])} 장비 설치·연결 구성" style="max-width:1120px">']

    def dev(x, y, w, h, t, s="", cls="dv", fs=12, sym=None, sub_cls="dvs"):
        if sym:
            o.append(f'<a href="#it-{sym}" class="nlink" aria-label="{E(t)} — 구성품 표로 이동"><g data-node="{sym}" id="topo-{sym}">')
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" class="{cls}"/>')
        o.append(f'<text x="{x + w / 2}" y="{y + (h / 2 + 4 if not s else h / 2 - 2)}" class="dvt" font-size="{fs}">{E(t)}</text>')
        if s:
            o.append(f'<text x="{x + w / 2}" y="{y + h / 2 + 13}" class="{sub_cls}">{E(s)}</text>')
        if sym:
            o.append("</g></a>")

    def link(pts, cls, label="", lx=None, ly=None, anchor="start"):
        o.append(f'<polyline points="{" ".join(f"{x},{y}" for x, y in pts)}" class="lk {cls}"/>')
        if label:
            o.append(f'<text x="{lx}" y="{ly}" class="lkt" text-anchor="{anchor}">{E(label)}</text>')

    # 외부
    dev(300, 12, 380, 54, "중앙 Server (AAS 통합서버 · DCC 통합관제 · SDF-OCS)", "타 장비 · 총괄1 — 구매범위 아님", "ext")
    o.append(f'<rect x="8" y="80" width="1104" height="{H - 88}" rx="12" class="zonebd"/>'
             f'<text x="1098" y="97" class="zonebd-t" text-anchor="end">{E(z["zone"])} — 설치: (임시) 창조2관 3층 → (최종) 메타팩토리</text>')
    # 서버실
    o.append('<rect x="20" y="106" width="724" height="386" rx="8" class="room"/><text x="34" y="128" class="room-t">Zone 서버실 — 로컬 데이터·네트워크 기반(항목3·4) · DT·AI 연산(항목2)</text>')
    dev(330, 140, 120, 40, "방화벽", "OT/IT 경계", "dv2", 12, "NET")
    link([(390, 66), (390, 140)], "l10", "↑ AI Ready·AAS 전송 · ↓ 명령·레시피 (TLS)", 460, 162)
    dev(250, 212, 120, 44, "코어 스위치 1", "L3 · 이중화(가정)", "dv2", 12, "NET")
    dev(410, 212, 120, 44, "코어 스위치 2", "", "dv2", 12, "NET")
    link([(370, 180), (310, 212)], "l10a")
    link([(410, 180), (470, 212)], "l10b")
    link([(370, 234), (410, 234)], "l100")
    # Rack A 데이터 처리
    o.append('<rect x="36" y="280" width="392" height="198" rx="5" class="rack"/>')
    o.append('<a href="#it-RACK" class="nlink"><g data-node="RACK" id="topo-RACK"><text x="48" y="298" class="rack-t">Rack A · 로컬 데이터 처리 (랙·UPS·KVM ↗)</text></g></a>')
    for i in range(5):
        dev(48 + i * 75, 308, 69, 46, f"DPS-{i + 1}", "데이터 처리", "dv", 11.5, "DPS")
    o.append('<text x="232" y="372" class="lkt" text-anchor="middle">운영 시계열 DB 클러스터(4-1) · 통합 인증·접근통제(4-2) · SW 라이선스 서버</text>')
    dev(48, 384, 170, 44, "통합 스토리지", "올플래시 60TB raw", "dv", 12, "NAS")
    dev(228, 384, 110, 44, "백업 스토리지", "", "dv3", 11.5, "BAK")
    dev(348, 384, 70, 44, "PTP", "시간동기", "dv3", 11, "NET")
    dev(48, 438, 370, 30, "랙 · UPS · KVM", "", "dv3", 11, "RACK")
    link([(275, 256), (275, 268), (200, 268), (200, 280)], "l25a")
    link([(470, 256), (470, 272), (214, 272), (214, 280)], "l25b")
    o.append('<text x="60" y="275" class="lkt">25GbE (가정)</text>')
    # Rack B DT·AI 연산
    o.append('<rect x="448" y="280" width="284" height="198" rx="5" class="rack"/><text x="460" y="298" class="rack-t">Rack B · DT·AI 연산 (항목2)</text>')
    dev(460, 308, 260, 40, "방화벽 (DT 연산 구간)", "서버와 일괄 공급 · 배치 위치 추정", "dv2", 11.5, "GPU")
    dev(460, 360, 260, 70, "DT·AI 연산 서버", "GPU 96GB ×4 · CPU 128코어급 ×2 · 768GB", "dv", 13, "GPU")
    o.append('<text x="590" y="446" class="lkt" text-anchor="middle">학습 DT(OpenUSD 씬)·합성데이터·정책 추론 검증</text>')
    link([(320, 256), (320, 264), (590, 264), (590, 308)], "l25a")
    link([(500, 256), (500, 260), (604, 260), (604, 308)], "l25b")
    link([(590, 348), (590, 360)], "l25")
    # 운영실
    o.append('<rect x="760" y="106" width="340" height="386" rx="8" class="room"/><text x="774" y="128" class="room-t">Zone 운영실 — DT·시뮬레이션 운영 (항목1·2)</text>')
    dev(776, 142, 160, 58, "DT·시뮬레이션 운영 PC", "공정 시뮬레이션 SW 실행", "dv", 12, "OPC")
    dev(946, 142, 140, 58, "운영 노트북", "현장 시운전·스캔", "dv", 12, "NB")
    dev(776, 212, 310, 58, "DT 모니터링 시스템", "모니터링 모듈 표시 · 구성품·연동 셋업", "dv", 12.5, "MON")
    if z["scan"]:
        nm, _, _, _, where = z["scan"]
        dev(776, 282, 310, 52, nm.split(" (")[0], where + " · 스캔 데이터 → 운영 PC·통합 스토리지", "dv", 12, "SCN")
        link([(1016, 334), (1016, 346)], "l1")
    else:
        dev(776, 282, 310, 52, "측정·검사 장비는 각 Cell 소속", "측정 시스템 통합 제어 모듈(1-19)이 Cell 측정기를 제어", "dvx", 11.5)
    nsw = len([s for s in z["sw"] if GEN[s[1]][2] == "OPC"])
    o.append(f'<a href="#it-OPC" class="nlink"><g data-node="OPC"><rect x="776" y="346" width="310" height="132" rx="4" class="dv3"/>'
             f'<text x="931" y="368" class="dvt" font-size="12">운영 PC 탑재 SW {nsw}종 (항목1)</text>')
    names = [GEN[s[1]][0].split(" (")[0] for s in z["sw"] if GEN[s[1]][2] == "OPC"]
    lines, cur = [], ""
    for nme in names:
        nxt = (cur + " · " if cur else "") + nme
        if len(nxt) > 34:
            lines.append(cur)
            cur = nme
        else:
            cur = nxt
    lines.append(cur)
    for i, ln in enumerate(lines[:8]):
        o.append(f'<text x="931" y="{386 + i * 12.5}" class="dvs" font-size="9.5">{E(ln)}</text>')
    o.append("</g></a>")
    # 운영실 ↔ 코어
    link([(530, 226), (760, 226), (760, 171), (776, 171)], "l10a", "10GbE (가정)", 640, 220)
    link([(530, 244), (768, 244), (768, 241), (776, 241)], "l10b")
    link([(936, 171), (946, 171)], "l1")
    # SW 흐름 주석
    o.append('<text x="640" y="190" class="lkt flow" text-anchor="middle">OpenUSD 변환·업로드 → DT·AI 연산 서버</text>')
    # 케이블 트레이
    ty = 516
    o.append(f'<a href="#it-NET" class="nlink"><g data-node="NET"><rect x="20" y="{ty}" width="1080" height="16" rx="3" class="tray"/>'
             f'<text x="560" y="{ty + 12}" class="tray-t" text-anchor="middle">Zone 케이블 트레이 — 코어 ↔ Cell 캐비닛 이중 광 업링크 · PTP 시간동기 (네트워크·배선, 항목3)</text></g></a>')
    link([(300, 256), (300, ty)], "l25a")
    link([(440, 256), (440, ty)], "l25b")
    # Cells
    n = len(cells)
    cw = (1080 - (n - 1) * 12) / n
    y0 = 560
    for i, (cname, yr, fdev) in enumerate(cells):
        x = 20 + i * (cw + 12)
        o.append(f'<rect x="{x:.0f}" y="{y0}" width="{cw:.0f}" height="330" rx="6" class="cab"/>')
        o.append(f'<text x="{x + 10:.0f}" y="{y0 + 18}" class="cab-t" font-size="11.5">{E(cname)}</text>')
        o.append(f'<text x="{x + 10:.0f}" y="{y0 + 34}" class="lkt">Cell {i + 1}{" · " + yr if yr else ""} · 캐비닛</text>')
        mid = x + cw / 2
        link([(x + cw - 30, ty + 16), (x + cw - 30, y0)], "l25a")
        link([(x + cw - 16, ty + 16), (x + cw - 16, y0)], "l25b")
        bw = (cw - 30) / 2
        dev(round(x + 10), y0 + 46, round(bw), 42, "Edge Gateway", "OPC UA 수집·AAS 매핑", "dv", 11.5, "EGW")
        dev(round(x + 20 + bw), y0 + 46, round(bw), 42, "영상 수집 노드", "영상 버퍼·전처리", "dv", 11.5, "VNODE")
        dev(round(x + 10), y0 + 98, round(bw), 32, "TSN 스위치", "", "dv2", 11, "NET")
        dev(round(x + 20 + bw), y0 + 98, round(bw), 32, "AP", "", "dv2", 11, "NET")
        link([(x + 10 + bw / 2, y0 + 88), (x + 10 + bw / 2, y0 + 98)], "l10")
        link([(x + 20 + bw * 1.5, y0 + 88), (x + 20 + bw * 1.5, y0 + 98)], "l10")
        o.append(f'<text x="{mid:.0f}" y="{y0 + 152}" class="lkt" text-anchor="middle">OPC UA·AAS ↑상태·이벤트 · ↓명령·레시피·프로그램</text>')
        for j, d in enumerate(fdev):
            fx = x + 10 + (j % 2) * (bw + 10)
            fy = y0 + 166 + (j // 2) * 54
            dev(round(fx), fy, round(bw), 44, d, "각 Cell 구매", "fdx", 11)
        link([(x + 10 + bw / 2, y0 + 130), (x + 10 + bw / 2, y0 + 166)], "l1")
        link([(x + 20 + bw * 1.5, y0 + 130), (x + 20 + bw * 1.5, y0 + 166)], "wl")
        o.append(f'<text x="{mid:.0f}" y="{y0 + 292}" class="lkt" text-anchor="middle">PLC 가상 시운전 · 로봇 프로그램 다운로드는</text>')
        o.append(f'<text x="{mid:.0f}" y="{y0 + 308}" class="lkt" text-anchor="middle">Edge Gateway 경유 (직접 병렬 경로 없음)</text>')
    o.append(f'<text x="560" y="{H - 16}" class="lkt" text-anchor="middle">점선 테두리 = 각 Cell 구매 장비(본 장비 구매범위 아님) · 노드를 누르면 구성품 표의 해당 행으로 이동</text>')
    o.append("</svg>")
    return "".join(o)


LEGEND = [("l100", "코어 간 피어링"), ("l25a", "코어 1 측 연결"), ("l25b", "코어 2 측 연결 (이중화 짝)"), ("l10", "10GbE"), ("l1", "1GbE·USB (운영 단말·스캐너)"),
          ("wl", "무선 Wi-Fi (AMR·로봇·드론)"), ("l10a", "운영실 업링크")]


def legend():
    return '<ul class="lg">' + "".join(
        f'<li><svg width="34" height="10" aria-hidden="true"><line x1="0" y1="5" x2="34" y2="5" class="lk {c}"/></svg>{E(t)}</li>' for c, t in LEGEND) + "</ul>"


# ------------------------------------------------------------------ 표
def tag(c):
    t, cls = CHK[c]
    return f'<span class="tag {cls}">{t}</span>'


def item_table(z):
    rows = zone_rows(z)
    gsum = {}
    for r in rows:
        if r[8] is not None:
            gsum[r[0]] = gsum.get(r[0], 0) + r[8]
    sw_by_node = {}
    for r in rows:
        if r[0].startswith("항목1") and r[10]:
            sw_by_node.setdefault(r[10], []).append(r[1])
    for r in rows:
        if r[0].startswith("항목4"):
            sw_by_node.setdefault("DPS", []).append(r[1])
    body, cur, seen = [], None, set()
    for g, no, sym, nm, sp, q, unit, u, amt, lab, node, chk, sub in rows:
        if g != cur:
            cur = g
            body.append(f'<tr class="grp"><th colspan="7" scope="rowgroup">{E(g)}</th><td class="num">{k(gsum[g])}</td><td colspan="3"></td></tr>')
        rid = ""
        anchor = sym if sym in ("SCN", "GPU", "OPC", "NB", "MON", "DPS", "NAS", "BAK", "EGW", "VNODE", "NET", "RACK") else None
        if anchor and anchor not in seen:
            rid = f' id="it-{anchor}"'
            seen.add(anchor)
        nmh = E(nm)
        if anchor and anchor in sw_by_node:
            ids = ",".join(f"r-{x}" for x in sw_by_node[anchor])
            lst = sw_by_node[anchor]
            nmh += f'<span class="where">탑재: {E(", ".join(lst) if len(lst) <= 3 else f"SW {len(lst)}종 ({lst[0]}~{lst[-1]})")} <a href="#r-{sw_by_node[anchor][0]}" class="tolink" data-flash="{ids}">↓</a></span>'
        if anchor:
            nmh += f' <a href="#topo-{anchor}" class="tolink">도면 ↑</a>'
        elif node:
            nmh += f'<span class="where">설치: {E(NODE_NAME.get(node, node))} <a href="#topo-{node}" class="tolink">↑</a></span>'
        cls = ' class="subrow"' if sub else ""
        rowid = rid or f' id="r-{no}"'
        if rid:
            body.append(f'<tr id="r-{no}" hidden></tr>')
        body.append(f'<tr{rowid}{cls}><td class="sym">{E(no)}</td><td class="nm">{nmh}</td><td class="spec">{E(sp)}</td><td class="q"><b>{E(str(q))}</b></td><td class="u">{E(unit)}</td>'
                    f'<td class="num">{k(u) if u is not None else "–"}</td><td class="num">{k(amt) if amt is not None else "미구분"}</td>'
                    f'<td>{tag(chk)}<span class="where">{E(CHK_NOTE.get(chk, ""))}</span></td><td class="note">{E(lab)}</td></tr>')
    pre = sum(r[8] for r in rows if r[8] is not None)
    base = sum(r[8] for r in rows if r[8] is not None and (r[0].startswith("항목1") or r[0].startswith("항목2") or r[0].startswith("항목5")))
    foot = (f'<tr class="tot"><th colspan="7">항목6. 일반관리비·기업이윤 — (항목1 + 항목2 + 항목5) {k(base)}의 10%, 견적서 기재값</th><td class="num">{k(z["ga"])}</td><td colspan="2"></td></tr>'
            f'<tr class="tot"><th colspan="7">합계 (단위절삭 전)</th><td class="num">{k(pre + z["ga"])}</td><td colspan="2"></td></tr>'
            f'<tr class="tot strong"><th colspan="7">견적 합계 (단위절삭 후)</th><td class="num">{k(z["total"])}</td><td colspan="2">{E(z["no"])}</td></tr>')
    return ('<div class="tbl-wrap"><table class="bom wide2"><thead><tr><th>번호</th><th>구성품 (일반 명칭)</th><th>세부 사양</th><th style="text-align:center">수량</th><th>단위</th>'
            '<th class="r">단가</th><th class="r">금액</th><th>지침 점검</th><th>견적서 기재 품목 <span class="chg">(내부 대조용 · 제출 문서에는 쓰지 않음)</span></th></tr></thead>'
            f'<tbody>{"".join(body)}</tbody><tfoot>{foot}</tfoot></table></div>'), pre


def group_sums(z):
    rows = zone_rows(z)
    out_ = {}
    for r in rows:
        if r[8] is not None:
            out_[r[0]] = out_.get(r[0], 0) + r[8]
    return out_


def summary_table(z):
    gs = group_sums(z)
    sw = gs["항목1. OCS SW"]
    amc = [s for s in z["sw"] if s[1] == "AMC"][0]
    rows = [
        ("장비명", f'{z["name"]} — 사업계획서·심의요청서 장비명과 같게 씀. 견적서 건명은 「{z["title"]}」로 달라 수정 요청 필요'),
        ("견적", f'{z["no"]} (2026.10.15) · 합계 {k(z["total"])}천원 · 비교견적 {k(z["cmp"])}천원(발표자료 별첨 3)'),
        ("구성 (견적서 6개 항목)", " · ".join(f"{g.split('. ')[1]} {k(v)}" for g, v in gs.items()) + f' · 일반관리비·이윤 {k(z["ga"])}천원'),
        ("SW 라이선스", f'네트워크 라이선스(Network-Lock), 모듈별 1카피(포맷·제어기·PLC 단위 모듈은 수량만큼). 유지보수 연 18% × 4년 {k(amc[3] * amc[4])}천원이 항목1에 포함'),
        ("설치 장소", "(임시) 전북대학교 창조2관 3층 → (최종) 연구클러스터 메타팩토리. '29년 이전 시 랙 단위 이설·재연결 (10/16 발표자료)"),
        ("연결 Cell", " · ".join(f"{c[0]}{'(' + c[1] + ')' if c[1] else ''}" for c in z["cells"]) + " — 각 Cell 장비의 제어기·PLC를 Edge Gateway에 OPC UA·AAS로 연결. 장비 단위 엣지는 구매 제외"),
    ]
    body = "".join(f'<tr><th scope="row">{E(a)}</th><td>{E(b)}</td></tr>' for a, b in rows)
    return f'<div class="tbl-wrap"><table class="bom sumtbl"><tbody>{body}</tbody></table></div>'


def roles_table(z):
    rows = [("DT·시뮬레이션 운영 PC", "OPC", "공정 시뮬레이션 SW 모듈 실행(라이선스 서버에서 네트워크 라이선스 할당), 3D DT 모델·PLC 가상 시운전·로봇 프로그램 작성, OpenUSD 변환",
             "Zone 운영실"),
            ("DT 모니터링 시스템", "MON", "모니터링 모듈로 Cell 운영 정보(생산량·진행률·사이클타임)와 가상모델 동작을 표시", "Zone 운영실"),
            ("DT·AI 연산 서버", "GPU", "학습 DT(OpenUSD 씬) 호스팅, 다중 시나리오 연산·합성데이터 생성·정책 추론 검증 (모델 학습은 외부 국가 GPU 인프라)", "서버실 Rack B"),
            ("데이터 처리 서버 ×5", "DPS", "운영 시계열 DB 클러스터, 통합 인증·접근통제, SW 라이선스 서버, OCS 연계 서비스 (배치는 추정 — 공급사 협의)", "서버실 Rack A"),
            ("통합·백업 스토리지", "NAS", "DT 모델·프로젝트·스캔 점군·Raw 운영 데이터 단기 보존, 백업", "서버실 Rack A"),
            ("Edge Gateway · 영상 수집 노드", "EGW", "Cell 상태·이벤트 수집, 명령·레시피·프로그램 전달, Actual Trace 생성, 영상 버퍼·전처리", "각 Cell 캐비닛"),
            ("네트워크 (코어·TSN·방화벽·PTP·AP·배선)", "NET", "Zone 백본, OT/IT 경계 보호, 가상·실측 데이터 시간동기, AMR·이동 로봇 무선", "서버실·Cell·통로")]
    if z["scan"]:
        rows.insert(2, (z["scan"][0].split(" (")[0], "SCN", "현장·제품 3D 스캔 → 점군 처리 모듈로 가상 작업장·검사모델 구성", "Zone 운영실 · " + z["scan"][4]))
    body = "".join(f'<tr><th scope="row"><a href="#topo-{s}" class="tolink sw">{E(a)}</a></th><td>{E(b)}</td><td class="note">{E(c)}</td></tr>' for a, s, b, c in rows)
    return f'<div class="tbl-wrap"><table class="bom keytbl"><thead><tr><th>장비</th><th>용도</th><th>설치 위치</th></tr></thead><tbody>{body}</tbody></table></div>'


def guide_table(z):
    rows_ = zone_rows(z)
    n_spec = sum(1 for r in rows_ if r[11] == "spec") + sum(1 for r in rows_ if r[12] and "없음" in r[4])
    lumps = [r for r in rows_ if r[11] == "lump"]
    lump_amt = sum(r[8] for r in lumps)
    G = [
        ("장비명 일치", "과제명·장비명은 사업계획서와 동일", f"페이지 제목·구성도에 「{z['name']}」 사용", f"견적서 건명 「{z['title']}」 → 장비명으로 수정 요청", "chk"),
        ("규격서·사양서", "판단 가능하게 사양·성능을 구체적으로 (전북대 자료 참고)", "구성품마다 일반 명칭 + 세부 사양 열로 정리",
         f"사양이 없는 구성품 {n_spec}건(운영 PC·노트북·모니터링 구성품{', 스캐너 성능 수치' if z['scan'] else ''}·로컬 HW 하위 품목) — 공급사에 사양서 요청", "chk"),
        ("견적서 유효", "6개월 이내 견적서 필수", "2026.10.15 견적 — 6개월 기준 충족", "견적서 자체 유효기간은 30일(~11.14) → 계약 시점 재견적", "ok"),
        ("구성품별 금액", "세부 구성품명·구성품별 금액 구분 (총액만이면 불인정)", f"1식 금액 {len(lumps)}건 {k(lump_amt)}천원을 '금액 미구분'으로 표시",
         "로컬 HW 1식(데이터 처리 서버·스토리지·백업·Edge Gateway·영상 노드·네트워크·서버실)과 모니터링 시스템 1식을 구성품별 금액으로 나눈 견적 요청", "adj"),
        ("복수 견적", "입찰 예정이면 업체별 견적서 2개 이상, 제조사가 다른 비교견적", f"비교견적 1건 확인({k(z['cmp'])}천원)", "'2개 이상' 기준이면 비교견적 1건 추가 확보", "chk"),
        ("A System = a社 + b社", "제조사별 사양 구분, 제조사별 견적서 첨부",
         "견적서 대조 열로 구성품별 제조사 구분 가능(SW 개발사·서버·스토리지·시계열 DB·보안·방화벽" + ("·스캐너" if z["scan"] else "") + ")",
         "SI 턴키 1건 견적 → 제조사별 견적서(또는 공급사 확인서) 첨부 여부 결정", "chk"),
        ("시스템 구성도", "구성도 제시 (성균관대 자료 참고)", "1장 연결 토폴로지 + 2장 장비 용도로 제시", "성균관대 자료 양식과 표기 맞춤", "ok"),
        ("업체·모델 비노출", "특정 업체·모델을 서류·발표에 쓰지 않음", "구성도·구성품명·사양은 일반 명칭만 사용. 견적서 대조 열은 내부용",
         "10/16 발표자료(적정성·운영 인력 쪽)에 SW·서버·스토리지·시계열 DB·보안·스캐너 제품명이 남아 있음 → 일반 명칭으로 교체", "adj"),
    ]
    Q = [
        ("라이선스·카피 수", "플랫폼이 라이선스인지, 몇 카피인지", "네트워크 라이선스, 모듈별 1카피. 포맷·제어기·PLC 단위 모듈만 수량만큼"),
        ("3개 Cell 각각 도입 이유", "OCS 3개에 솔루션을 각각 넣는 이유", f"존별 대상 공정·로봇·PLC 기종·CAD 포맷이 다름 — {z['short']}은 " + {
            "fms": "용접·조립 로봇 OLP·PLC 2종·AMR 물류 중심", "adaptive": "가공기 머신텐딩·강화학습 연계(OpenUSD)·가공 CAD 4종 중심",
            "qms": "측정·리워크(자동 측정·리워크 자동생성·결과 분석) 중심"}[z["slug"]]),
        ("커스터마이징·유지보수", "커스터마이징·기술지원·유지보수 견적 명확히", f"기술지원 {len(z['ts'])}건 {k(sum(t[2] for t in z['ts']))}천원, 유지보수 연 18% × 4년 항목1에 포함 — 범위·산출물 명시 필요"),
        ("이전 비용", "임시공간 → 메타팩토리 이동 시 비용·서버 운용 영향", "'29년 랙 단위 이설 계획. 이설 비용·중단 기간은 견적에 없음 → 운영계획에 추가"),
        ("자립화", "장비 운영 수익·인건비·유지비", "발표자료에 자립화(운영 수익·유지비) 장표 추가 필요"),
        ("공급사 규모", "작은 업체면 AS 질문", "공급사 매출·인력·AS 체계 자료 준비"),
    ]
    if z["slug"] in ("adaptive", "qms"):
        Q.append(("같은 솔루션 사용 이유", "적응가공·정밀검사에 같은 솔루션을 쓰는 이유", "공통 기본 모듈 위에 존별 모듈(가공: OpenUSD·가공 포맷 / 검사: 측정·리워크·분석)을 달리 구성 — 모델·데이터 재사용"))
    st = {"ok": ("충족", "ok"), "chk": ("보완", "chk"), "adj": ("필수 조치", "adj")}
    g = "".join(f'<tr><th scope="row">{E(a)}</th><td>{E(b)}</td><td>{E(c)}</td><td><span class="tag {st[s][1]}">{st[s][0]}</span></td><td>{E(d)}</td></tr>' for a, b, c, d, s in G)
    q = "".join(f'<tr><th scope="row">{E(a)}</th><td>{E(b)}</td><td>{E(c)}</td></tr>' for a, b, c in Q)
    return ('<h3>공통 지침 적용 점검</h3><div class="tbl-wrap"><table class="bom issuetbl"><thead><tr><th>지침</th><th>요구</th><th>이 페이지 반영</th><th>상태</th><th>남은 조치</th></tr></thead>'
            f'<tbody>{g}</tbody></table></div>'
            '<h3>OCS Cell 3종 심의위원 질의 대응</h3><div class="tbl-wrap"><table class="bom keytbl"><thead><tr><th>질의</th><th>내용</th><th>대응</th></tr></thead>'
            f'<tbody>{q}</tbody></table></div>')


# ------------------------------------------------------------------ 로컬 관제 센터 공간 구성 (2D·3D)
# 좌표 mm. 서버실 x 0~3400, 운영실 x 3400~8400, 깊이 y 0~5400. 치수는 가정(실측 후 확정)
ROOM_W, ROOM_D, SPLIT = 8400, 5400, 3400
TRAY_Z = 2300


def space_items(z):
    """(기호, 이름, 설명, kind, x, y, w, d, h, z0, 링크)"""
    it = [
        ("R1", "랙 1 · 네트워크·보안", "방화벽 · 코어 ×2 · PTP · KVM", "rack", 400, 800, 600, 1200, 2000, 0, "NET"),
        ("R2", "랙 2 · 데이터", "데이터 처리 서버 ×5 · 스토리지 · 백업", "rack", 1000, 800, 600, 1200, 2000, 0, "DPS"),
        ("R3", "랙 3 · DT·AI 연산", "GPU 서버 4U · 방화벽(DT 구간)", "gpu", 1600, 800, 600, 1200, 2000, 0, "GPU"),
        ("UPS", "UPS · 배터리", "랙 이중 PDU 급전", "ups", 2400, 800, 800, 900, 1900, 0, "RACK"),
        ("AC", "항온항습기 (견적 외)", "열부하 약 10kW", "ext", 500, 4500, 1000, 600, 1900, 0, None),
        ("VW", "DT 모니터링 시스템", "표시장치(구성 가정)", "screen", 4700, 0, 2800, 120, 1400, 800, "MON"),
        ("D1", "운영 데스크 1", "DT·시뮬레이션 운영 PC", "desk", 4600, 2000, 1300, 800, 750, 0, "OPC"),
        ("D2", "운영 데스크 2", "운영 노트북 · 스캔 처리", "desk", 6200, 2000, 1300, 800, 750, 0, "NB"),
    ]
    if z["slug"] == "fms":
        it.append(("SCN", "공간 스캐너 보관·충전", "현장 이동형 · 삼각대", "scan", 7600, 4400, 600, 500, 900, 0, "SCN"))
    elif z["slug"] == "adaptive":
        it.append(("SCN", "자동 스캔 스테이션", "1.4×1.4m 가정 · 위치 협의", "scan", 6700, 3800, 1400, 1400, 1800, 0, "SCN"))
    return it


def _links_mm(z):
    """(cls, [(x,y)...], label, (lx,ly)) — 2D·3D 공용, 3D는 TRAY_Z 높이"""
    L = [
        ("l25a", [(700, 1400), (2200, 1400)], "", None),
        ("l10a", [(1300, 1400), (3400, 1400), (7500, 1400)], "운영실 10GbE (천장 트레이 → 데스크·표시장치 하강)", (3600, 1300)),
        ("l10a", [(5250, 1400), (5250, 2000)], "", None),
        ("l10a", [(6850, 1400), (6850, 2000)], "", None),
        ("l10a", [(6100, 1400), (6100, 120)], "", None),
        ("l25b", [(900, 1400), (900, 5400)], "Cell 캐비닛 이중 광 업링크", (960, 3400)),
        ("l10", [(500, 1400), (0, 1400)], "건물 광 인입 → 중앙 Server", (60, 650)),
        ("pw", [(2800, 2100), (700, 2100)], "UPS → 랙 전원", (1500, 2280)),
    ]
    if z["slug"] == "fms":
        L.append(("wl", [(7900, 4400), (7300, 2800)], "스캔 데이터 (Wi-Fi·USB)", (7350, 3700)))
    elif z["slug"] == "adaptive":
        L.append(("l1", [(7400, 3800), (7400, 2800)], "스캐너 ↔ 운영 노트북", (7460, 3400)))
    return L


def space_2d(z):
    s, ox, oy = 0.1, 70, 60
    P = lambda x, y: (ox + x * s, oy + y * s)
    W, H = ox * 2 + ROOM_W * s + 40, oy + ROOM_D * s + 150
    o = [f'<svg class="arch plan" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="{E(z["short"])} 로컬 관제 센터 2D 평면" style="max-width:{W:.0f}px">']
    # grid
    for gx in range(0, ROOM_W + 1, 1000):
        x, _ = P(gx, 0)
        o.append(f'<line x1="{x}" y1="{oy}" x2="{x}" y2="{oy + ROOM_D * s}" class="grid"/>')
    for gy in range(0, ROOM_D + 1, 1000):
        _, y = P(0, gy)
        o.append(f'<line x1="{ox}" y1="{y}" x2="{ox + ROOM_W * s}" y2="{y}" class="grid"/>')
    # rooms
    o.append(f'<rect x="{ox}" y="{oy}" width="{SPLIT * s}" height="{ROOM_D * s}" class="rm srv"/>')
    o.append(f'<rect x="{ox + SPLIT * s}" y="{oy}" width="{(ROOM_W - SPLIT) * s}" height="{ROOM_D * s}" class="rm ops"/>')
    o.append(f'<text x="{ox + 12}" y="{oy + 22}" class="rm-t">서버실 3.4 × 5.4 m</text>')
    o.append(f'<text x="{ox + SPLIT * s + 12}" y="{oy + 22}" class="rm-t">운영실 (로컬 관제) 5.0 × 5.4 m</text>')
    # doors
    for (x1, y1, x2, y2) in [(SPLIT, 3800, SPLIT, 4800), (2000, ROOM_D, 3000, ROOM_D), (5200, ROOM_D, 6400, ROOM_D)]:
        a, b = P(x1, y1)
        c, d = P(x2, y2)
        o.append(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" class="door"/>')
    # aisles
    a, b = P(400, 2000)
    o.append(f'<rect x="{a}" y="{b}" width="{2800 * s}" height="{1000 * s}" class="aisle-c"/><text x="{a + 6}" y="{b + 60}" class="aisle-ct">전면 작업공간 1.0m+ (콜드 아일)</text>')
    a, b = P(400, 0)
    o.append(f'<text x="{a + 6}" y="{b + 50}" class="aisle-ct">후면 0.8m (핫 아일)</text>')
    # items
    for sym, nm, sub, kind, x, y, w, d, h, z0, ln in space_items(z):
        a, b = P(x, y)
        tag = f'<a href="#it-{ln}" class="nlink"><g data-node="{ln}">' if ln else "<g>"
        o.append(tag + f'<rect x="{a}" y="{b}" width="{w * s}" height="{d * s}" rx="2" class="sp {kind}"/>')
        if kind in ("rack", "gpu"):
            o.append(f'<text x="{a + w * s / 2}" y="{b + d * s / 2 + 4}" class="sp-t v">{E(sym)}</text>')
        elif kind == "ups":
            o.append(f'<text x="{a + w * s / 2}" y="{b + 30}" class="sp-t v">UPS</text>')
        elif kind == "screen":
            o.append(f'<text x="{a + w * s / 2}" y="{b + 30}" class="sp-t">{E(nm)}</text>')
        else:
            o.append(f'<text x="{a + w * s / 2}" y="{b + d * s / 2 - 2}" class="sp-t">{E(nm)}</text>'
                     f'<text x="{a + w * s / 2}" y="{b + d * s / 2 + 12}" class="sp-s">{E(sub)}</text>')
        o.append("</g></a>" if ln else "</g>")
    # links
    for cls, pts, lab, lp in _links_mm(z):
        d = " ".join(f"{P(x, y)[0]:.1f},{P(x, y)[1]:.1f}" for x, y in pts)
        o.append(f'<polyline points="{d}" class="lk {cls}"/>')
        if lab and lp:
            a, b = P(*lp)
            o.append(f'<text x="{a}" y="{b}" class="lkt">{E(lab)}</text>')
    # rack legend under rack row
    a, b = P(400, 3150)
    o.append(f'<text x="{a}" y="{b}" class="sp-s" style="text-anchor:start">R1 네트워크·보안 · R2 데이터 · R3 DT·AI 연산 (600×1200, 42U)</text>')
    # corridor + cells
    a, b = P(0, ROOM_D)
    o.append(f'<rect x="{a}" y="{b + 6}" width="{ROOM_W * s}" height="34" class="aisle-c"/><text x="{a + 8}" y="{b + 28}" class="aisle-ct">복도 · 케이블 트레이 → 각 Cell 캐비닛</text>')
    cells = " · ".join(c[0] for c in z["cells"])
    o.append(f'<text x="{a + 8}" y="{b + 62}" class="lkt">연결 Cell {len(z["cells"])}개: {E(cells)}</text>')
    # dims
    a, b = P(0, 0)
    o.append(f'<line x1="{a}" y1="{b - 18}" x2="{a + ROOM_W * s}" y2="{b - 18}" class="dim"/><text x="{a + ROOM_W * s / 2}" y="{b - 24}" class="dim-t2">8.4 m (가정)</text>')
    o.append(f'<line x1="{a - 18}" y1="{b}" x2="{a - 18}" y2="{b + ROOM_D * s}" class="dim"/><text x="{a - 24}" y="{b + ROOM_D * s / 2}" class="dim-t2" transform="rotate(-90 {a - 24} {b + ROOM_D * s / 2})">5.4 m</text>')
    o.append("</svg>")
    return "".join(o)


def space_3d(z):
    import math
    C, S, OX, OY = math.cos(math.pi / 6), 0.07, 410, 230

    def P(x, y, h=0):
        return (OX + (x - y) * C * S, OY + (x + y) * 0.5 * S - h * S)

    def poly(pts, cls, extra=""):
        return f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" class="{cls}"{extra}/>'

    o = [f'<svg class="arch plan" viewBox="0 0 960 730" role="img" aria-label="{E(z["short"])} 로컬 관제 센터 3D" style="max-width:960px">']
    # floors
    o.append(poly([P(0, 0), P(SPLIT, 0), P(SPLIT, ROOM_D), P(0, ROOM_D)], "fl srv"))
    o.append(poly([P(SPLIT, 0), P(ROOM_W, 0), P(ROOM_W, ROOM_D), P(SPLIT, ROOM_D)], "fl ops"))
    for gx in range(0, ROOM_W + 1, 1000):
        a, b = P(gx, 0)
        c, d = P(gx, ROOM_D)
        o.append(f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}" class="grid"/>')
    for gy in range(0, ROOM_D + 1, 1000):
        a, b = P(0, gy)
        c, d = P(ROOM_W, gy)
        o.append(f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}" class="grid"/>')
    # back walls (x=0 plane, y=0 plane) + partition low cut
    WH = 2700
    o.append(poly([P(0, 0), P(0, ROOM_D), P(0, ROOM_D, WH), P(0, 0, WH)], "wall"))
    o.append(poly([P(0, 0), P(ROOM_W, 0), P(ROOM_W, 0, WH), P(0, 0, WH)], "wall"))
    o.append(poly([P(SPLIT, 0), P(SPLIT, 3800), P(SPLIT, 3800, WH), P(SPLIT, 0, WH)], "wall part"))
    lab = []

    def box(x, y, w, d, h, z0, kind, link=None):
        x1, y1, z1 = x + w, y + d, z0 + h
        top = [P(x, y, z1), P(x1, y, z1), P(x1, y1, z1), P(x, y1, z1)]
        fr = [P(x1, y, z0), P(x1, y1, z0), P(x1, y1, z1), P(x1, y, z1)]
        fl = [P(x, y1, z0), P(x1, y1, z0), P(x1, y1, z1), P(x, y1, z1)]
        g = (f'<a href="#it-{link}" class="nlink"><g data-node="{link}">' if link else "<g>")
        g += poly(fl, f"bx {kind} fL") + poly(fr, f"bx {kind} fR") + poly(top, f"bx {kind} fT")
        if kind in ("rack", "gpu"):  # 전면 유닛 줄
            for k in range(1, 8):
                zz = z0 + h * k / 8
                a, b = P(x, y1, zz)
                c, dd = P(x1, y1, zz)
                g += f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{dd:.1f}" class="ru"/>'
        g += "</g></a>" if link else "</g>"
        return g

    items = sorted(space_items(z), key=lambda r: (r[4] + r[6] / 2) + (r[5] + r[7] / 2))
    for sym, nm, sub, kind, x, y, w, d, h, z0, ln in items:
        o.append(box(x, y, w, d, h, z0, kind, ln))
        if kind == "desk":  # 모니터
            o.append(box(x + 200, y + 100, w - 400, 60, 420, h, "screen"))
        lab.append((P(x + w / 2, y + d / 2, z0 + h + 250), nm, kind))
    # trays + drops
    for cls, pts, lb, lp in _links_mm(z):
        zz = 2100 if cls == "pw" else (900 if cls in ("wl", "l1") else TRAY_Z)
        d = " ".join(f"{P(x, y, zz)[0]:.1f},{P(x, y, zz)[1]:.1f}" for x, y in pts)
        o.append(f'<polyline points="{d}" class="lk {cls}"/>')
    for x, y, zt in [(5250, 2000, 1170), (6850, 2000, 1170), (6100, 120, 2200), (900, 5400, 0)]:
        a, b = P(x, y, TRAY_Z)
        c, d = P(x, y, zt)
        o.append(f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}" class="lk drop3"/>')
    a, b = P(900, ROOM_D + 600, 0)
    o.append(f'<text x="{a:.0f}" y="{b:.0f}" class="lkt" text-anchor="middle">→ Cell 캐비닛 {len(z["cells"])}개</text>')
    a, b = P(0, 1400, TRAY_Z)
    o.append(f'<text x="{a - 6:.0f}" y="{b - 8:.0f}" class="lkt" text-anchor="end">건물 광 인입 → 중앙 Server</text>')
    for (a, b), nm, kind in lab:
        if kind == "screen":
            continue
        o.append(f'<text x="{a:.0f}" y="{b:.0f}" class="iso-t">{E(nm.split(" · ")[0] if kind in ("rack", "gpu") else nm)}</text>')
    a, b = P(5900, 0, 2350)
    o.append(f'<text x="{a:.0f}" y="{b:.0f}" class="iso-t">DT 모니터링 시스템 (표시장치)</text>')
    a, b = P(1700, 0, WH + 120)
    o.append(f'<text x="{a:.0f}" y="{b:.0f}" class="iso-t" font-size="13">서버실</text>')
    a, b = P(5900, 0, WH + 380)
    o.append(f'<text x="{a:.0f}" y="{b:.0f}" class="iso-t" font-size="13">운영실 (로컬 관제)</text>')
    o.append("</svg>")
    return "".join(o)


RACKS = [
    ("R1 · 네트워크·보안", "NET", [(42, 2, "패치패널 ×2", "net"), (40, 1, "방화벽 (OT/IT 경계)", "net"), (39, 1, "코어 스위치 1", "net"), (38, 1, "코어 스위치 2", "net"),
                                  (37, 1, "관리망 스위치 (가정)", "opt"), (36, 1, "PTP 시간동기", "net"), (20, 1, "KVM 콘솔", "net")]),
    ("R2 · 데이터", "DPS", [(42, 2, "패치패널", "net"), (36, 2, "데이터 처리 서버 1", "srv"), (34, 2, "데이터 처리 서버 2", "srv"), (32, 2, "데이터 처리 서버 3", "srv"),
                           (30, 2, "데이터 처리 서버 4", "srv"), (28, 2, "데이터 처리 서버 5", "srv"), (24, 2, "통합 스토리지 (60TB raw)", "sto"), (20, 2, "백업 스토리지", "sto")]),
    ("R3 · DT·AI 연산", "GPU", [(42, 2, "패치패널", "net"), (40, 1, "방화벽 (DT 연산 구간)", "net"), (16, 4, "DT·AI 연산 서버 (GPU ×4)", "gpu"), (11, 4, "증설 여유 4U", "opt")]),
]


def rack_svg():
    UH, W, gap, top = 11, 240, 40, 34
    o = [f'<svg class="arch plan" viewBox="0 0 {3 * W + 2 * gap + 60} {top + 42 * UH + 30}" role="img" aria-label="랙 실장도" style="max-width:{3 * W + 2 * gap + 60}px">']
    for i, (title, link, units) in enumerate(RACKS):
        x = 40 + i * (W + gap)
        o.append(f'<a href="#it-{link}" class="nlink"><text x="{x + W / 2}" y="{top - 12}" class="dvt" font-size="12.5">{E(title)}</text></a>')
        o.append(f'<rect x="{x}" y="{top}" width="{W}" height="{42 * UH}" class="rk"/>')
        for u in range(0, 43, 6):
            yy = top + (42 - u) * UH
            if i == 0:
                o.append(f'<text x="{x - 6}" y="{yy + 3}" class="u-n">{u if u else ""}</text>')
        for ut, n, nm, kind in units:
            yy = top + (42 - ut) * UH
            o.append(f'<rect x="{x + 6}" y="{yy + 1}" width="{W - 12}" height="{n * UH - 2}" rx="1.5" class="ru-b {kind}"/>'
                     f'<text x="{x + W / 2}" y="{yy + n * UH / 2 + 3.5}" class="ru-t">{E(nm)} · {n}U</text>')
        used = sum(n for _, n, _, k in units if k != "opt")
        o.append(f'<text x="{x + W / 2}" y="{top + 42 * UH + 18}" class="sp-s">사용 {used}U / 42U</text>')
    o.append("</svg>")
    return "".join(o)


POWER = [  # (장비, 수량, kW, 근거)
    ("DT·AI 연산 서버", 1, 3.8, "GPU 600W ×4 + CPU ×2 + 기타, 최대 부하 (추정)"),
    ("데이터 처리 서버", 5, 0.6, "2U 2소켓, 평상 부하 (추정)"),
    ("통합 스토리지", 1, 1.0, "올플래시 2U (추정)"),
    ("백업 스토리지", 1, 0.4, "(추정)"),
    ("네트워크·보안·시간동기", 1, 0.8, "방화벽 ×2 · 코어 ×2 · 관리·PTP·KVM (추정)"),
]


def power_table():
    it_kw = sum(q * kw for _, q, kw, _ in POWER)
    rows = "".join(f'<tr><td class="nm">{E(n)}</td><td class="q">{q}</td><td class="num">{kw:.1f}</td><td class="num">{q * kw:.1f}</td><td class="note">{E(b)}</td></tr>' for n, q, kw, b in POWER)
    ups = it_kw / 0.8
    foot = (f'<tr class="tot strong"><th colspan="3">서버실 IT 부하</th><td class="num">{it_kw:.1f} kW</td><td></td></tr>'
            f'<tr class="tot"><th colspan="3">UPS (부하율 80%)</th><td class="num">{ups:.1f} kW↑</td><td class="note">15kVA급 이상 권장 — 견적서 UPS 용량 미기재</td></tr>'
            f'<tr class="tot"><th colspan="3">냉방 (IT 부하 + 10%)</th><td class="num">{it_kw * 1.1:.1f} kW</td><td class="note">약 {it_kw * 1.1 / 3.517:.1f} RT — 항온항습기는 견적에 없음</td></tr>')
    return ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>장비</th><th style="text-align:center">수량</th><th class="r">대당 kW</th><th class="r">합계 kW</th><th>근거</th></tr></thead>'
            f'<tbody>{rows}</tbody><tfoot>{foot}</tfoot></table></div>')


SPACE_REQ = [
    ("서버실 면적", "3.4 × 5.4 m (약 18㎡) — 42U 랙 3대 + UPS·배터리 + 항온항습기, 전면 1.0m·후면 0.8m 작업공간", "가정 치수. 창조2관 3층 실측 후 확정"),
    ("운영실 면적", "5.0 × 5.4 m (약 27㎡) — 표시장치 벽면, 운영 데스크 2석" + ", 스캔 장비 공간", "기업 실증 참관 인원에 따라 확대"),
    ("전기", "서버실 전용 분전반(3상 380V), 랙별 이중 PDU, UPS 경유 급전", "분전반·배선 공사는 견적에 없음"),
    ("냉방", "IT 부하 약 9kW 상시 → 항온항습기 10kW급, 서버실 전용", "견적에 없음 — 별도 확보 필요"),
    ("통신 인입", "건물 광 인입(중앙 Server·DCC 연계), 복도 상부 트레이로 Cell 캐비닛 이중 광", "건물 측 광 경로 확인"),
    ("이전", "'29년 메타팩토리 이전 시 랙 단위 이설 — 랙 3대·UPS를 그대로 옮기는 구성", "이설 비용·중단 기간 운영계획에 반영"),
]


def space_req_table():
    body = "".join(f'<tr><th scope="row">{E(a)}</th><td>{E(b)}</td><td class="note">{E(c)}</td></tr>' for a, b, c in SPACE_REQ)
    return f'<div class="tbl-wrap"><table class="bom keytbl"><thead><tr><th>항목</th><th>구성</th><th>비고</th></tr></thead><tbody>{body}</tbody></table></div>'


LEGEND_SP = [("l10", "건물 광 인입 (중앙 Server)"), ("l25a", "랙 간 25GbE · 상부 트레이"), ("l10a", "운영실 10GbE (데스크·표시장치)"), ("l25b", "Cell 캐비닛 이중 광 업링크"),
             ("pw", "UPS 전원"), ("l1", "스캐너 연결 (유선)"), ("wl", "스캐너 연결 (무선)")]


def legend_sp():
    return '<ul class="lg">' + "".join(
        f'<li><svg width="34" height="10" aria-hidden="true"><line x1="0" y1="5" x2="34" y2="5" class="lk {c}"/></svg>{E(t)}</li>' for c, t in LEGEND_SP) + "</ul>"


def space_section(z):
    return f'''<section id="space">
  <p class="eyebrow">2. 로컬 관제 센터 공간 구성</p>
  <h2>서버실·운영실 2D 평면과 3D 배치, 연결 경로</h2>
  <p class="note-box">견적서 항목2·3·4 장비를 (임시) 창조2관 3층에 서버실 + 운영실로 설치하는 경우의 배치안. 치수·랙 실장·전력은 가정이며, 견적서에 없는 항온항습기·분전반 공사는 점선·비고로 표시함. 장비를 누르면 구성품 표의 해당 행으로 이동함.</p>
  <h3>2D 평면 (1칸 = 1m)</h3>
  <figure class="fig">{space_2d(z)}{legend_sp()}</figure>
  <h3>3D 배치 (아이소메트릭, 앞쪽 벽 생략)</h3>
  <figure class="fig">{space_3d(z)}{legend_sp()}
  <figcaption>천장 트레이(높이 2.3m)를 따라 랙 → 운영실 데스크·표시장치로 내려가고, 서버실 앞쪽 벽을 지나 복도 트레이로 각 Cell 캐비닛에 연결됨.</figcaption></figure>
  <h3>랙 실장도 (42U)</h3>
  <figure class="fig">{rack_svg()}</figure>
  <h3>공간·전력·냉방 요건</h3>
  {space_req_table()}
  {power_table()}
</section>'''


SPACE_CSS = """<style>
.grid{stroke:var(--rule);stroke-width:.6}
.rm{stroke:var(--ink);stroke-width:2.5} .rm.srv{fill:var(--cellbg)} .rm.ops{fill:var(--paper)}
.rm-t{fill:var(--teal);font-size:12.5px;font-weight:700}
.door{stroke:var(--paper);stroke-width:5} .aisle-c{fill:var(--aisle)} .aisle-ct{fill:var(--teal);font-size:10.5px}
.sp{stroke:var(--ink);stroke-width:1.2} .sp.rack{fill:var(--navy2)} .sp.gpu{fill:var(--teal)} .sp.ups{fill:var(--amber)}
.sp.ext{fill:none;stroke-dasharray:5 3;stroke:var(--muted)} .sp.screen{fill:var(--ink)} .sp.desk{fill:var(--grp)} .sp.scan{fill:var(--cam);fill-opacity:.35}
.sp-t{fill:var(--ink);font-size:11px;font-weight:700;text-anchor:middle} .sp-t.v{fill:#fff}
.sp-s{fill:var(--muted);font-size:10px;text-anchor:middle}
.dim{stroke:var(--muted);stroke-width:1} .dim-t2{fill:var(--muted);font-size:11px;text-anchor:middle;font-family:var(--mono)}
.lk.pw{stroke:var(--amber);stroke-width:2;stroke-dasharray:7 4}
.lk.drop3{stroke:var(--muted);stroke-width:1.2;stroke-dasharray:3 3}
.fl.srv{fill:var(--cellbg);stroke:var(--ink);stroke-width:1.5} .fl.ops{fill:var(--paper);stroke:var(--ink);stroke-width:1.5}
.wall{fill:var(--grp);fill-opacity:.55;stroke:var(--muted);stroke-width:1} .wall.part{fill-opacity:.35}
.bx{stroke:var(--ink);stroke-width:.8;stroke-linejoin:round}
.bx.rack{fill:var(--navy2)} .bx.gpu{fill:var(--teal)} .bx.ups{fill:var(--amber)} .bx.desk{fill:var(--muted)} .bx.screen{fill:var(--ink)}
.bx.scan{fill:var(--cam)} .bx.ext{fill:var(--paper);stroke-dasharray:4 3}
.bx.fT{fill-opacity:.55} .bx.fR{fill-opacity:.8} .bx.fL{fill-opacity:1}
.ru{stroke:#fff;stroke-opacity:.35;stroke-width:.6}
.iso-t{fill:var(--ink);font-size:11px;font-weight:700;text-anchor:middle;paint-order:stroke;stroke:var(--bg);stroke-width:4px}
.rk{fill:var(--cellbg);stroke:var(--ink);stroke-width:2}
.ru-b{stroke:var(--ink);stroke-width:.6} .ru-b.net{fill:var(--grp)} .ru-b.srv{fill:var(--navy2)} .ru-b.sto{fill:var(--eqline);fill-opacity:.6}
.ru-b.gpu{fill:var(--teal)} .ru-b.opt{fill:none;stroke-dasharray:4 3;stroke:var(--muted)}
.ru-t{fill:var(--ink);font-size:9.5px;text-anchor:middle;paint-order:stroke;stroke:var(--paper);stroke-width:3px}
.u-n{fill:var(--muted);font-size:9px;text-anchor:end;font-family:var(--mono)}
</style>"""


REFS = [
    ("Q", "견적서", "이지로보틱스 존별 디지털 트윈 시뮬레이션 시스템 구축 견적서 (10/15 최종)", "2026-10-15", "피지컬AI 3본부 / 04.장비심의 / 장비별 구비서류"),
    ("G1", "이메일", "유지연 팀장 「자체장비 심의시 질의&제안사항 공유 및 중장위 심의 준비(~10.21/수) 안내」 — 공통 제안의견·중장위 제출서류", "2026-10-18", "Outlook"),
    ("G2", "첨부", "26.10.16_자체장비심의 질의응답_제안사항.hwpx — 장비별 질의응답·심의요청서 작성 항목", "2026-10-16", "메일 첨부 · llm-wiki raw"),
    ("P", "발표자료", "1-3. 발표자료_이형수 — 유연제조·적응가공·AI정밀검사 OCS 시뮬레이션 Cell (Cell 구성·설치장소·계층 구성·단계 도입)", "2026-10-16", "피지컬AI 3본부 / 04.장비심의 / 심의순서별 발표자료"),
]


def page(z):
    table, pre = item_table(z)
    gs = group_sums(z)
    kp = "".join(f'<div><b>{k(v / 1000)}</b><span>{E(g.split(". ")[1])} (백만원)</span></div>' for g, v in gs.items())
    refs = "".join(f'<tr><td class="sym">[{a}]</td><td class="u">{E(b)}</td><td>{E(c)}</td><td class="u">{E(d)}</td><td class="note">{E(e)}</td></tr>' for a, b, c, d, e in REFS)
    return f'''<title>{E(z["short"])} OCS 시뮬레이션 Cell</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=IBM+Plex+Mono:wght@400;500&display=swap">
{CSS}{PZ_EXTRA}{EXTRA}{SPACE_CSS}
<header class="mast"><div class="wrap">
  <p class="eyebrow">총괄5-세부1 · {E(z["id"])} · 10/15 최종 견적({E(z["no"])}) 기준 · 10/18 중장위 심의 준비 지침 적용 · 2026.10.19 작성 · 검토본</p>
  <h1>{E(z["name"])}</h1>
</div></header>
<nav class="toc" aria-label="바로가기"><div class="wrap">
  <a href="#sum">요약</a><a href="#topo">연결 토폴로지</a><a href="#space">공간 구성 2D·3D</a><a href="#items">구성품·사양·금액</a><a href="#guide">지침 점검</a><a href="#refs">근거</a>
</div></nav>
<main class="wrap">
<section id="sum" style="margin-top:8px">
  <p class="eyebrow">결론 및 핵심 요약 (Executive Summary)</p>
  <h2>견적 {k(z["total"])}천원 · 견적서 6개 항목을 서버실·운영실·Cell 캐비닛에 배치</h2>
  <div class="kpis">{kp}</div>
  {summary_table(z)}
</section>
<section id="topo">
  <p class="eyebrow">1. 물리 연결 토폴로지</p>
  <h2>장비 설치·연결 구성</h2>
  <figure class="fig">{topo_svg(z)}{legend()}
  <figcaption>견적서 항목2(OCS HW)·항목3(로컬 HW)·항목4(로컬 OCS·보안)를 설치 위치별로 나누고, 항목1(SW)은 탑재 장비에 묶어 그림. <b>장비 노드를 누르면 2장 구성품 표의 해당 행으로 이동함.</b>
  견적서에 수량·사양이 없는 로컬 HW 하위 품목(코어 이중화, 링크 속도, Cell별 Edge Gateway·영상 노드 1대씩)은 「로컬 OCS Zone 구성 - (예시) 정밀조립존」과 같은 구조로 가정해 그렸음 — 공급사 상세 사양 확정 후 갱신. 업체·모델명은 쓰지 않음.</figcaption></figure>
  <h3>주요 장비 용도·설치 위치</h3>
  {roles_table(z)}
</section>
{space_section(z)}
<section id="items">
  <p class="eyebrow">3. 구성품·사양·금액</p>
  <h2>견적서 항목 순서대로 구성품별 사양·금액</h2>
  <p class="note-box">단위 천원. 번호는 견적서 항목 순서(항목1~6)를 따름 — 심의위원 제안대로 규격서·견적서·비교견적서의 구성 항목 순서를 이 순서에 맞추면 됨. 견적서 표지는 'VAT 포함', 참고사항은 '부가세 별도'로 엇갈림.
  <b>지침 점검</b>: 적합 · 사양 보완(성능 수치 없음) · 기종 확인 · 기간 확인 · 범위 명시 · <b>금액 미구분</b>(총액만 제시 — 불인정 위험).</p>
  {table}
</section>
<section id="guide">
  <p class="eyebrow">4. 중장위 심의 준비 지침 점검</p>
  <h2>10/18 공통 지침·10/16 질의 대응 현황</h2>
  {guide_table(z)}
</section>
<section id="refs">
  <p class="eyebrow">근거</p>
  <h2>근거 문서</h2>
  <div class="tbl-wrap"><table class="bom"><thead><tr><th>표기</th><th>구분</th><th>문서·내용</th><th>일자</th><th>위치</th></tr></thead><tbody>{refs}</tbody></table></div>
</section>
</main>
<script>
(function(){{
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function flash(id){{
    var els = id.indexOf('topo-') === 0 ? Array.prototype.slice.call(document.querySelectorAll('[data-node="' + id.slice(5) + '"]')) : [document.getElementById(id)];
    els.forEach(function(n){{ if (n) n.classList.add('flash'); }});
  }}
  document.addEventListener('click', function(e){{
    Array.prototype.forEach.call(document.querySelectorAll('.flash'), function(n){{ n.classList.remove('flash'); }});
    var a = e.target.closest && e.target.closest('a[href^="#it-"], a[href^="#r-"], a[href^="#topo-"]');
    if (!a) return;
    var id = a.getAttribute('href').slice(1), t = document.getElementById(id);
    if (!t) return;
    e.preventDefault();
    t.scrollIntoView({{behavior: reduce ? 'auto' : 'smooth', block: 'center'}});
    var lst = a.getAttribute('data-flash');
    (lst ? lst.split(',') : [id]).forEach(flash);
    try {{ history.replaceState(null, '', '#' + id); }} catch (err) {{}}
  }});
}})();
</script>
'''


EXTRA = """<style>
.fdx{fill:var(--cellbg);stroke:var(--muted);stroke-width:1.2;stroke-dasharray:5 3}
.lkt.flow{fill:var(--teal);font-weight:700}
.tag{display:inline-block;font:600 11px var(--mono);padding:1px 7px;border-radius:3px;white-space:nowrap}
.tag.ok{background:var(--teal);color:#fff} .tag.chk{background:#FFF1E2;color:#9A4A00;border:1px solid #F0C08A} .tag.adj{background:#FDE8E8;color:#A12020;border:1px solid #F2B8B8}
.chg{font:500 11px var(--mono);color:var(--muted)}
tr.subrow td{font-size:12.5px;color:var(--muted)} tr.subrow td.sym{padding-left:18px}
table.wide2{min-width:1500px} table.wide2 td.spec{min-width:300px} table.wide2 td.note{min-width:220px;font-size:12px}
table.sumtbl th{width:150px}
</style>"""


if __name__ == "__main__":
    for z in ZONES:
        open(out(f"ocs_sim_{z['slug']}.html"), "w", encoding="utf-8").write(page(z))
        _, pre = item_table(z)
        print(z["id"], "items", k(pre), "+ga", k(pre + z["ga"]), "quote", k(z["total"]))
