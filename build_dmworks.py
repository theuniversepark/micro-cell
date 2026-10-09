"""DMWorks 존별 옵션 구성 페이지 → dmworks_zones.html
근거: 이지로보틱스 10/8 견적서(견26CAMTIC-DMWorks-1008-1~3)·제안서, DMWorks 3.0 정가표(2026.01), 9/30 방문 Q&A, 10/6 의사결정."""
import html
import re

import build_page as bp
from privacy import out

E = html.escape
RATE = 0.52  # 10/8 견적 단가 = 정가(Node-Lock) × 52% (전 옵션 동일)

# ------------------------------------------------------------------ 정가표 옵션 (천원)
# key: (옵션, 코드, 정가 Node-Lock, 기능, 9/30 확인·제약)
OPT = {
    "BASE": ("DMWorks Base", "DMW-001", 142200, "Device Modeler(기구학·CAD 생성·좌표계) + Factory Simulator(설비 배치·로봇 라이브러리·모션/Task·충돌검사·케이블·단일 공정)", "단일 공정만(라인·물류는 MULTIPLE PROCESS). 물리엔진 없음 → 학습은 Omniverse"),
    "CADI": ("CAD IMPORT (포맷당)", "DMW-002", 9000, "외부 CAD 변환·경량화. 포맷당 1옵션", "Base에 1종 포함(정가표). 견적은 4종 별도 계상"),
    "CADE": ("CAD EXPORT (포맷당)", "DMW-003", 9000, "DMWorks 데이터를 외부 포맷으로", "업체 고지: 원하는 결과가 안 나올 수 있음"),
    "OLP": ("DM OLP (컨트롤러당)", "DMW-004", 24000, "로봇 컨트롤러별 오프라인 프로그래밍(스폿·핸들링 24,000)", "협동로봇·휴머노이드 컨트롤러 없음(요청 시 지원)"),
    "RRS": ("DM RRS (컨트롤러당)", "DMW-009", 20000, "로봇사 RCS 연동 정밀 경로·사이클타임", "정가표상 현대 Hi5·FANUC RJ3만. RCS 모듈 미포함"),
    "PC": ("DM POINT CLOUD", "DMW-005", 38000, "3D 스캔 데이터로 가상 작업장 구축", "공장 공간 스캔 개념"),
    "MP": ("DM MULTIPLE PROCESS", "DMW-007", 46000, "다공정 라인·물류(컨베이어·셔틀·버퍼)·UPH·가동률", "AMR 실운영 속도 파라미터 필요"),
    "PLC": ("DM PLC SIMULATION (PLC당)", "DMW-010", 44200, "PLC 프로그램–가상 설비 연동 가상 시운전(OPC UA, I/O 매핑, 시퀀스 검증)", "Read + 핸드셰이크만. 이기종 PLC 동시 시뮬레이션 2종까지 경험"),
    "PID": ("DM PLUG-IN For Developer", "DMW-011", 42000, "API로 전용 기능·UI 개발(AI·PLC·MES 연계)", "개발한 Plug-in 실행에는 For User 필요"),
    "PIU": ("DM PLUG-IN For User", "DMW-012", 14000, "개발된 Plug-in 실행 환경", ""),
}
# 정가표에 없는 신규 제품 (10/8 견적·제안서) — 단가는 견적가
NEW = {
    "MON": ("DM-Monitoring", 32000, "설비 실시간 연동으로 DT 동작 일치, CELL/ZONE 운영 정보(생산량·진행률·CT) 분할 화면, 권한 관리", "OCS Cell 관제(OWS·존 오케스트레이터 UI)와 기능이 겹침 → 역할 구분 필요"),
    "USD": ("Omniverse USD Converter", 14400, "Workcell을 Tree 구조 유지한 USD로 변환·Nucleus 업로드, 물리 설정 정보 반영. 기구 정의 변환은 '협의 후 개발 예정'", "9/30 '지오메트리만' 문제를 푸는 항목. 기구 정의는 아직 개발 전"),
    "LE": ("Omniverse Live Edit", 10400, "DMWorks–Omniverse Live Session으로 위치·동작 실시간 동기화", "9/30 업체 스스로 'DT 운영용 비추천(지연)'"),
    "ACSB": ("ACS BASE", 26000, "검사 결과(결함 위치 3D 좌표)로 로봇 리워크 프로그램·레시피 자동 생성 기본 환경", "리워크 공정이 있는 존에만 의미. AI 알고리즘 연동 가능"),
    "ACSO": ("ACS OLP (컨트롤러당)", 17200, "리워크 경로를 로봇 컨트롤러 형식 OLP로 생성", "OLP와 같은 컨트롤러 2종씩 계상"),
    "AIMSS": ("AIMS Simulator (컨트롤러당)", 48000, "가상 측정 작업장·캘리브레이션·측정 시뮬레이션·로봇 OLP", "레이저트래커·스캐너 로봇 자동 측정(CMM 수준)"),
    "AIMSC": ("AIMS Controller (컨트롤러당)", 36000, "측정 시스템 통합 제어·데이터 수집·실시간 결과 모니터링", ""),
    "PIA": ("PIA (Predictive Inspect & Analysis)", 32000, "3D 스캔 데이터 경량화·컬러맵·섹션·차트 시각화로 품질 예측", "측정 결과 분석 SW(9/30 소개)"),
    "TES": ("TESCar", 60000, "스캔 데이터로 저항 점용접 품질 자동 판정·최적 용접조건 제시", "차체 스폿용접 특화 → 유연제조(용접) 쪽 기능에 가까움"),
}

# ------------------------------------------------------------------ 10/8 견적 (천원)
# (구분, key, 상세, 수량, 단가, 검토 [ok|chk|adj], 검토 의견)
Q = {
    "A-1-4": {"no": "견26CAMTIC-DMWorks-1008-1", "total": 1638000, "items": [
        ("SW", "BASE", "", 1, 73944, "ok", "필수. 모니터링은 DM-Monitoring이 맡아 Base는 1카피"),
        ("SW", "MON", "", 1, 32000, "ok", "DT 모니터링 화면(운영 관제는 OCS Cell)"),
        ("SW", "CADI", "STL·CATIA·PRO/E·AUTOCAD", 4, 4680, "ok", "수요기업(삼진산업)·설비사 원본 포맷 반입"),
        ("SW", "CADE", "STL·VRML·OBJ", 3, 4680, "ok", "범용 메시·시각화 포맷 내보내기"),
        ("SW", "OLP", "HYUNDAI·KAWASAKI", 2, 12480, "ok", "로봇 오프라인 프로그래밍(컨트롤러 2종)"),
        ("SW", "RRS", "HYUNDAI", 1, 10400, "ok", "현대 Hi5 컨트롤러 사이클타임 정밀 산출"),
        ("SW", "PC", "", 1, 19760, "ok", "공장 스캐너 데이터 반영"),
        ("SW", "MP", "", 1, 23920, "ok", "혼류 라인·AMR 물류"),
        ("SW", "PLC", "LS·MITSUBISHI", 2, 22984, "ok", "PLC 가상 시운전 2종(DMWorks 동시 시뮬레이션 2기종 경험 범위)"),
        ("SW", "PID", "", 1, 21840, "ok", "3존 공통 개발 거점으로 유지"),
        ("SW", "PIU", "", 1, 7280, "ok", ""),
        ("SW", "USD", "", 1, 14400, "ok", "Isaac Sim 학습 DT 연계 핵심"),
        ("SW", "LE", "", 1, 10400, "ok", "Omniverse 리뷰 세션 실시간 동기화"),
        ("SW", "ACSB", "", 1, 26000, "ok", "재작업 공정 자동 리워크 프로그램 생성"),
        ("SW", "ACSO", "HYUNDAI·KAWASAKI", 2, 17200, "ok", "컨트롤러 종류는 로봇 메이커와 일치시킴"),
        ("유지보수", "AMC", "연 18% × 4년", 4, 68045.76, "chk", "4년치 선계상. 장비비 계상 가능 여부·'5년 면제' 문구 확인"),
        ("HW", "", "공장 스캐너 RTC700 (HW·운영 SW 포함)", 1, 156000, "ok", "대형 공간 스캔으로 공장·셀 가상 작업장 구축"),
        ("HW", "", "DT·AI 연산 서버 (ASUS ESC8000A-E13P · EPYC 9755×2 · 1.5TB · RTX PRO 6000 ×8)", 1, 520000, "ok", "공정·물류 DT 시뮬레이션·강화학습 연산"),
        ("HW", "", "디지털트윈 운영 PC", 1, 12000, "ok", ""),
        ("HW", "", "운영 노트북", 1, 6500, "ok", ""),
        ("HW", "", "구성품 구매·설치·시스템 연동 셋업", 1, 50000, "ok", ""),
        ("기술지원", "", "CELL 구성 설비별 DT 연동 기능 Customizing", 1, 20000, "ok", ""),
        ("기술지원", "", "DB 연동 시각화 UI Customizing", 1, 45000, "ok", "DB 데이터를 DT 화면에 시각화"),
        ("기술지원", "", "DM PLUG-IN 기능 Customizing", 1, 10000, "ok", "AAS 출력·OpenUSD 물성 전달 범위 명시"),
        ("기술지원", "", "ACS 시스템 Customizing", 1, 20000, "ok", ""),
    ]},
    "A-2-5": {"no": "견26CAMTIC-DMWorks-1008-2", "total": 1620000, "items": [
        ("SW", "BASE", "", 1, 73944, "ok", "필수"),
        ("SW", "MON", "", 1, 32000, "ok", "DT 모니터링 화면(운영 관제는 OCS Cell)"),
        ("SW", "CADI", "NX·JT·SOLID EDGE·SOLIDWORKS", 4, 4680, "ok", "가공기·지그 원본 포맷 반입"),
        ("SW", "CADE", "AAS·JT·IGES·FBX", 4, 4680, "ok", "AAS·중립 포맷 내보내기"),
        ("SW", "OLP", "YASKAWA·KUKA", 2, 12480, "ok", "머신텐딩 로봇 오프라인 프로그래밍"),
        ("SW", "PC", "", 1, 19760, "ok", "제품 스캐너 점군을 가상 작업장에 반영"),
        ("SW", "MP", "", 1, 23920, "ok", "팔레트·AMR 물류"),
        ("SW", "PLC", "SIEMENS", 1, 22984, "ok", "PLC 메이커 확정 시 일치 여부 확인"),
        ("SW", "PID", "", 1, 21840, "ok", "존 전용 Plug-in 개발"),
        ("SW", "PIU", "", 1, 7280, "ok", ""),
        ("SW", "USD", "", 1, 14400, "ok", "강화학습 환경(Isaac Lab) 연계"),
        ("SW", "LE", "", 1, 10400, "ok", "Omniverse 리뷰 세션 실시간 동기화"),
        ("SW", "ACSB", "", 1, 26000, "ok", "가공 후 로봇 리워크(디버링·후처리) 프로그램 생성"),
        ("SW", "ACSO", "YASKAWA·KUKA", 2, 17200, "ok", "컨트롤러 종류는 로봇 메이커와 일치시킴"),
        ("유지보수", "AMC", "연 18% × 4년", 4, 62879.04, "chk", "4년치 선계상. 장비비 계상 가능 여부 확인"),
        ("HW", "", "제품 스캐너 소형(자동) HyperScan (HW·운영 SW 포함)", 1, 190000, "ok", "가공 소재·제품 자동 스캔, 점군을 가상 작업장에 반영"),
        ("HW", "", "DT·AI 연산 서버 (RTX PRO 6000 ×8, 사양 동일)", 1, 520000, "ok", "적응가공 DT·강화학습(Isaac Lab) 연산"),
        ("HW", "", "디지털트윈 운영 PC", 1, 12000, "ok", ""),
        ("HW", "", "운영 노트북", 1, 6500, "ok", ""),
        ("HW", "", "구성품 구매·설치·시스템 연동 셋업", 1, 50000, "ok", ""),
        ("기술지원", "", "CELL 구성 설비별 DT 연동 기능 Customizing", 1, 20000, "ok", ""),
        ("기술지원", "", "DB 연동 시각화 UI Customizing", 1, 45000, "ok", "DB 데이터를 DT 화면에 시각화"),
        ("기술지원", "", "DM PLUG-IN 기능 Customizing", 1, 10000, "ok", ""),
        ("기술지원", "", "ACS 시스템 Customizing", 1, 20000, "ok", ""),
    ]},
    "A-4-5": {"no": "견26CAMTIC-DMWorks-1008-3", "total": 2531000, "items": [
        ("SW", "BASE", "", 1, 73944, "ok", "필수"),
        ("SW", "MON", "", 1, 32000, "ok", "DT 모니터링 화면(품질 관제는 QMS·OCS)"),
        ("SW", "CADI", "STEP·OBJ·AAS·PARASOLID", 4, 4680, "ok", "검사 대상 CAD 포맷 반입"),
        ("SW", "CADE", "AAS·STP·PARASOLID", 3, 4680, "ok", "역설계 결과 내보내기"),
        ("SW", "OLP", "FANUC·ABB", 2, 12480, "ok", "검사·리워크 로봇 오프라인 프로그래밍"),
        ("SW", "RRS", "FANUC", 1, 10400, "ok", "FANUC 컨트롤러 사이클타임 정밀 산출"),
        ("SW", "PC", "", 1, 19760, "ok", "스캔 기반 가상 작업장"),
        ("SW", "MP", "", 1, 23920, "ok", "검사 라인·AMR 물류"),
        ("SW", "PLC", "ROCKWELL", 1, 22984, "ok", "검사 라인 PLC 가상 시운전"),
        ("SW", "PID", "", 1, 21840, "ok", "검사 전용 Plug-in 개발"),
        ("SW", "PIU", "", 1, 7280, "ok", ""),
        ("SW", "USD", "", 1, 14400, "ok", "합성 결함 데이터(Omniverse) 연계"),
        ("SW", "LE", "", 1, 10400, "ok", "Omniverse 리뷰 세션 실시간 동기화"),
        ("SW", "ACSB", "", 1, 26000, "ok", "판정→재검사→리워크 폐루프와 직접 맞음"),
        ("SW", "ACSO", "FANUC·ABB", 2, 17200, "ok", "컨트롤러 종류는 리워크 로봇 메이커와 일치시킴"),
        ("SW", "PIA", "", 1, 32000, "ok", "스캔 결과 분석·시각화"),
        ("SW", "TES", "", 1, 60000, "ok", "용접부 품질 검사·분석"),
        ("SW", "AIMSS", "FANUC·ABB", 2, 48000, "ok", "로봇 자동 측정 경로 생성"),
        ("SW", "AIMSC", "FANUC·ABB", 2, 36000, "ok", "측정 시뮬레이션"),
        ("유지보수", "AMC", "연 18% × 4년", 4, 110708.64, "chk", "4년치 선계상(SW가 커 금액도 큼). 장비비 계상 가능 여부 확인"),
        ("HW", "", "대형 제품 스캐너(자동화) AT960SR + AS1 (HW·운영 SW 포함)", 1, 560000, "ok", "레이저트래커 기반 고정밀 자동 측정(AIMS 연계)"),
        ("HW", "", "DT·AI 연산 서버 (RTX PRO 6000 ×8, 사양 동일)", 1, 520000, "ok", "합성 결함 데이터 생성·검사 AI 학습 연산"),
        ("HW", "", "디지털트윈 운영 PC", 1, 12000, "ok", ""),
        ("HW", "", "운영 노트북", 1, 6500, "ok", ""),
        ("HW", "", "구성품 구매·설치·시스템 연동 셋업", 1, 50000, "ok", ""),
        ("기술지원", "", "CELL 구성 설비별 DT 연동 기능 Customizing", 1, 20000, "ok", ""),
        ("기술지원", "", "DB 연동 시각화 UI Customizing", 1, 45000, "ok", "DB 데이터를 DT 화면에 시각화"),
        ("기술지원", "", "DM PLUG-IN 기능 Customizing", 1, 10000, "ok", ""),
        ("기술지원", "", "ACS 시스템 Customizing", 1, 20000, "ok", ""),
    ]},
}

ZONES = [
    {"id": "A-1-4", "slug": "z14", "name": "유연제조 OCS 시뮬레이션 Cell", "purpose": "공정 최적화 + 가상 시운전",
     "tasks": [("삼진산업 도어·차체 혼류 공정 DT 모델링, 설비 배치·로봇 경로 검증", "Base · CAD IMPORT · POINT CLOUD"),
               ("다공정 라인·AMR 물류·스케줄 최적화", "MULTIPLE PROCESS"),
               ("2차년도 실물 셀 투입 전 PLC 가상 시운전", "PLC SIMULATION (1사)"),
               ("용접·핸들링 로봇 OLP·사이클타임", "OLP · RRS (로봇 확정 후)"),
               ("운영 상태 DT 모니터링", "DM-Monitoring"),
               ("Isaac Sim 학습 DT로 Workcell 전달", "Omniverse USD Converter"),
               ("AAS 출력·OCS 연동 플러그인 개발(3존 공통 거점)", "PLUG-IN Developer")]},
    {"id": "A-2-5", "slug": "z25", "name": "적응가공 OCS 시뮬레이션 Cell", "purpose": "데이터 + 강화학습",
     "tasks": [("가공기·로봇·팔레트·AMR 경로·간섭 검증", "Base · CAD IMPORT"),
               ("공정 배정·팔레트·AMR 물류 최적화", "MULTIPLE PROCESS"),
               ("머신텐딩 셀 제어로직·가공기 인터록 검증", "PLC SIMULATION"),
               ("로딩·언로딩 로봇 OLP", "OLP (로봇 확정 후)"),
               ("강화학습 환경(Isaac Lab)으로 셀 전달·결과 환류", "USD Converter · PLUG-IN User"),
               ("※ CNC 가공 경로·NC 검증은 별도 SW(DMWorks에 CAM 없음)", "—")]},
    {"id": "A-4-5", "slug": "z45", "name": "AI정밀검사 OCS 시뮬레이션 Cell", "purpose": "DT(역설계) + 품질 운영",
     "tasks": [("3D 스캔으로 검사 셀·현장을 가상 작업장으로", "POINT CLOUD"),
               ("로봇 자동 측정 경로·측정 시뮬레이션", "AIMS Simulator · Controller"),
               ("스캔 결과 분석·품질 예측 시각화", "PIA"),
               ("판정→재검사→리워크 폐루프(리워크 로봇 프로그램 자동 생성)", "ACS BASE · ACS OLP"),
               ("검사·로봇·AMR 공정 시뮬레이션", "Base · MULTIPLE PROCESS"),
               ("합성 결함 데이터(Omniverse) 연계", "USD Converter")]},
]

# 정밀조립: 10/8 견적 없음 → 견적 단가로 산정
PZ = [("BASE", 1, "DT 워크스테이션 1대용"), ("MP", 1, "셀 간 AMR 물류·배치"), ("PLC", 1, "셀 상태머신·PLC 시퀀스 검증"),
      ("PIU", 1, "A-1-4에서 개발한 AAS 출력 플러그인 실행"), ("USD", 1, "Isaac Sim 학습 DT(VLA)로 셀 전달")]


def k(n):
    return f"{n:,.0f}"


def name_of(key):
    if key in OPT:
        return OPT[key][0]
    if key in NEW:
        return NEW[key][0]
    return {"AMC": "AMC 유지보수"}.get(key, key)


def parts(zid):
    it = Q[zid]["items"]
    sw = sum(q * u for g, _, _, q, u, *_ in it if g in ("SW", "유지보수"))
    hw = sum(q * u for g, _, _, q, u, *_ in it if g == "HW")
    ts = sum(q * u for g, _, _, q, u, *_ in it if g == "기술지원")
    ga = (sw + hw + ts) * 0.10
    return sw, hw, ts, ga


def pz_total():
    return sum((OPT[k_][2] * RATE if k_ in OPT else NEW[k_][1]) * q for k_, q, _ in PZ)


QTOTAL = sum(Q[z]["total"] for z in Q)

CSS = re.search(r"<style>.*?</style>", bp.page(), re.S).group(0)
EXTRA = """<style>
table.bom th.r{text-align:right}
td.dz,th.dz{text-align:center;white-space:nowrap} table.bom td a{white-space:nowrap}
.tag{display:inline-block;font:600 11px var(--mono);padding:1px 7px;border-radius:3px;white-space:nowrap}
.tag.ok{background:var(--teal);color:#fff} .tag.chk{background:#FFF1E2;color:#9A4A00;border:1px solid #F0C08A} .tag.adj{background:#FDE8E8;color:#A12020;border:1px solid #F2B8B8}
.chg{font:500 11px var(--mono);color:var(--muted)}
.keytbl th[scope=row],.issuetbl th[scope=row]{white-space:nowrap;color:var(--navy2);font-weight:700;background:var(--grp);text-align:left}
.keytbl td,.issuetbl td{font-size:13px;line-height:1.55}
</style>"""
TAG = {"ok": ("적합", "ok"), "chk": ("확인", "chk"), "adj": ("조정", "adj")}


def tag(v):
    t, c = TAG[v]
    return f'<span class="tag {c}">{t}</span>'


WHY_COMMON = [
    ("역할 분리", "AI 학습(강화학습·합성데이터)은 물리엔진이 있는 Omniverse/Isaac Sim이, 실제 설비·로봇·PLC가 그대로 돌아가는지 미리 검증하는 일은 프로세스 시뮬레이션이 맡음. DMWorks는 검증 측 도구임", "9/17 세미나 · 9/30 Q&A"),
    ("한 도구로 검증", "국산(조달 원칙 부합). PLC 가상 시운전·라인/물류 시뮬레이션·로봇 오프라인 프로그래밍·3D 스캔 가상 작업장을 한 도구로 처리", "9/30 Q&A"),
    ("학습 DT 연계", "USD Converter로 검증용 셀 모델을 Isaac Sim 학습 환경에 넘겨 두 환경을 이어 씀", "10/8 제안서"),
    ("쓰지 않는 범위", "AI 학습 자체(물리엔진 없음), PLC 직접 제어(Read·핸드셰이크만), 가공 CAM 경로 검증(별도 SW). 협동로봇 OLP는 기성 목록에 없음(요청 시 지원)", "9/30 Q&A"),
]
WHY = [
    ("A-1-4", "z14", "유연제조", "공정 최적화 + 가상 시운전",
     "2차년도 실물 셀(A-1-3) 투입 전 혼류 라인·로봇·AMR·PLC를 가상으로 먼저 맞춰 설치 후 재작업·시운전 기간을 줄여야 함",
     "① 삼진산업 도어·차체 혼류 공정 DT로 설비 배치·로봇 경로 검증 ② 다공정 라인·AMR 물류·스케줄 최적화(UPH·가동률·AMR 대수) ③ PLC 가상 시운전으로 제어로직·이상 상황 사전 시험 ④ 용접·핸들링 로봇 OLP·사이클타임 ⑤ 3존 공통 플러그인(AAS 출력·OCS 연동) 개발 거점",
     "Base · MULTIPLE PROCESS · PLC SIMULATION · OLP · PLUG-IN Developer · USD Converter"),
    ("A-2-5", "z25", "적응가공", "데이터 + 강화학습",
     "가공기·로봇·팔레트·AMR 머신텐딩 셀은 간섭·인터록 오류가 곧 설비 충돌이라 실물 전에 경로·신호를 검증해야 함. 강화학습용 셀 모델의 출발점도 필요",
     "① 가공기–로봇–팔레트–AMR 경로·간섭 검증 ② 공정 배정·물류 흐름 최적화 ③ 머신텐딩 제어로직·가공기 인터록(핸드셰이크) 검증 ④ 셀 모델을 USD로 넘겨 Isaac Lab 강화학습 환경으로 활용·결과 환류",
     "Base · MULTIPLE PROCESS · PLC SIMULATION · OLP · USD Converter · PLUG-IN User"),
    ("A-4-5", "z45", "AI정밀검사", "DT(역설계) + 품질 운영",
     "실제 부품·현장을 3D 스캔해 가상 작업장·검사모델을 만들고 판정→재검사→리워크 폐루프를 돌려야 함. 측정 경로·리워크 프로그램을 매번 사람이 만들 수 없음",
     "① 3D 스캔으로 검사 셀·수요기업 현장 가상 작업장 구축(역설계) ② 로봇 자동 측정 경로·측정 시뮬레이션(AIMS) ③ 스캔 결과 분석·품질 예측 시각화(PIA) ④ 검사 결과로 리워크 로봇 프로그램 자동 생성(ACS) ⑤ 검사·로봇·AMR 공정 시뮬레이션",
     "POINT CLOUD · AIMS · PIA · ACS · Base · MULTIPLE PROCESS · USD Converter"),
    ("A-3", "z3", "정밀조립", "셀 배치·물류·상태머신 검증 (견적 미포함)",
     "셀 5개·협동로봇 50대·AMR 20대가 한 존에서 움직여 셀 배치·셀 간 물류·상태머신을 실물 전에 검증할 수단이 필요. 1차년도 DT 7건 산출물의 검증 도구",
     "① 셀 레이아웃·로봇 작업영역 간섭 검증 ② 셀 간 AMR 물류·대수 산정, 셀 재배정 흐름 ③ 셀 상태머신(IDLE~SAFE-STOP)·셀 PLC 시퀀스 검증 ④ 셀 모델을 USD로 넘겨 VLA 학습 DT(Isaac Sim)와 연결",
     "Base · MULTIPLE PROCESS · PLC SIMULATION · USD Converter · PLUG-IN User"),
]


def why_tables():
    c = "".join(f'<tr><th scope="row">{E(a)}</th><td>{E(b)}</td><td class="note">{E(r)}</td></tr>' for a, b, r in WHY_COMMON)
    z = "".join(f'<tr><td><a href="#{sl}">{E(zid)}</a></td><th scope="row">{E(nm)}<br><span class="chg">{E(pur)}</span></th>'
                f'<td>{E(need)}</td><td>{E(use)}</td><td class="nm">{E(opt)}</td></tr>' for zid, sl, nm, pur, need, use, opt in WHY)
    return ('<h3>공통 — 왜 DMWorks인가</h3><div class="tbl-wrap"><table class="bom keytbl"><thead><tr><th>항목</th><th>내용</th><th>근거</th></tr></thead>'
            f'<tbody>{c}</tbody></table></div>'
            '<h3>존별 구매 필요성과 활용 목적</h3><div class="tbl-wrap"><table class="bom keytbl"><thead><tr><th>존</th><th>구분·목적</th><th>구매가 필요한 이유</th><th>활용 목적</th><th>핵심 옵션</th></tr></thead>'
            f'<tbody>{z}</tbody></table></div>'
            '<p class="note-box">존마다 목적이 달라 같은 구성을 세 벌 사지 않음(10/6 결정). 유연제조는 가상 시운전·OLP, 적응가공은 강화학습 연계(USD), AI정밀검사는 스캔·측정·리워크, 정밀조립은 배치·물류·상태머신 1좌석이 중심임.</p>')


def key_table():
    amc = sum(q * u for z in Q for g, key, _, q, u, *_ in Q[z]["items"] if key == "AMC")
    gpu = 3 * 520000
    scn = sum(u for z in Q for g, _, d, q, u, *_ in Q[z]["items"] if g == "HW" and "스캐너" in d)
    rows = [
        ("견적 개요", f"이지로보틱스가 10/8 존별 3건을 보냄. 유연제조 {k(Q['A-1-4']['total'])} · 적응가공 {k(Q['A-2-5']['total'])} · AI정밀검사 {k(Q['A-4-5']['total'])} = 합계 {k(QTOTAL)}천원(VAT 별도). SW·HW·기술지원에 일반관리비·이윤 10%를 더한 턴키 견적. 과제기간 4개월, Network-Lock 라이선스", "10/8 견적서"),
        ("단가 수준", "정가표에 있는 DMWorks 옵션은 모두 정가(Node-Lock) × 52% — 48% 할인. 10/6에 들은 60% 할인보다 낮음", "정가표 대조"),
        ("구성 방식", "3개 존 모두 같은 틀(Base 1 · DM-Monitoring · USD Converter · Live Edit · ACS · PLUG-IN Developer · GPU 서버 · 스캐너 · AMC 4년)에 존별 CAD 포맷·로봇·PLC 메이커만 바꿈.", "10/6 의사결정"),
        ("금액이 큰 항목", f"GPU 서버 3대 {k(gpu)} · 스캐너 3대 {k(scn)} · AMC 4년 선계상 {k(amc)}천원 — 세 가지가 전체의 약 {round((gpu + scn + amc) / QTOTAL * 100)}%(일반관리비 제외 기준)", "견적 항목 합산"),
        ("확인 항목", "SW·스캐너·DT·AI 연산 서버는 모두 적합. 남은 확인 대상은 AMC 4년 선계상(장비비 계상 가능 여부)임", "존별 검토"),
        ("정밀조립", f"견적 대상이 아님. 같은 단가로 Base·MULTIPLE PROCESS·PLC·Plug-in User·USD Converter 1좌석을 잡으면 약 {k(pz_total())}천원", "견적 단가 적용"),
    ]
    body = "".join(f'<tr><th scope="row">{E(a)}</th><td>{E(b)}</td><td class="note">{E(c)}</td></tr>' for a, b, c in rows)
    return f'<div class="tbl-wrap"><table class="bom keytbl"><thead><tr><th>항목</th><th>내용</th><th>근거</th></tr></thead><tbody>{body}</tbody></table></div>'


def summary_table():
    rows, t = [], [0, 0, 0, 0, 0]
    for z in ZONES:
        sw, hw, ts, ga = parts(z["id"])
        tot = Q[z["id"]]["total"]
        for i, v in enumerate((sw, hw, ts, ga, tot)):
            t[i] += v
        rows.append(f'<tr><td><a href="#{z["slug"]}">{E(z["id"])}</a></td><td class="nm">{E(z["name"])}</td><td class="note">{E(Q[z["id"]]["no"])}</td>'
                    f'<td class="num">{k(sw)}</td><td class="num">{k(hw)}</td><td class="num">{k(ts)}</td><td class="num">{k(ga)}</td><td class="num"><b>{k(tot)}</b></td></tr>')
    rows.append(f'<tr><td><a href="#z3">A-3</a></td><td class="nm">정밀조립존</td><td class="note">견적 없음 · 견적 단가로 산정</td>'
                f'<td class="num">{k(pz_total())}</td><td class="num">–</td><td class="num">–</td><td class="num">–</td><td class="num">{k(pz_total())}</td></tr>')
    rows.append(f'<tr class="tot strong"><th colspan="3">견적 합계 (3개 존)</th>' + "".join(f'<td class="num">{k(v)}</td>' for v in t) + "</tr>")
    return ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>존</th><th>구분</th><th>견적번호</th><th class="r">SW(유지보수 포함)</th><th class="r">HW</th>'
            '<th class="r">기술지원</th><th class="r">일반관리비·이윤 10%</th><th class="r">견적 합계</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div><p class="note-box">단위 천원, VAT 별도. 견적 합계는 업체 단위절삭(백만 원 미만 버림) 후 금액이라 항목 합과 조금 다름.</p>')


def price_table():
    rows = []
    for key in ["BASE", "CADI", "CADE", "OLP", "RRS", "PC", "MP", "PLC", "PID", "PIU"]:
        n, code, lp, func, note = OPT[key]
        qp = lp * RATE
        use = "".join(f'<td class="dz">{sum(q for g, kk, _, q, *_ in Q[z["id"]]["items"] if kk == key) or "–"}</td>' for z in ZONES)
        rows.append(f'<tr><td class="nm">{E(n)}<br><span class="chg">{E(code)}</span></td><td class="num">{k(lp)}</td><td class="num"><b>{k(qp)}</b></td>'
                    f'<td class="q">52%</td><td>{E(func)}</td><td class="note">{E(note)}</td>{use}</tr>')
    for key, (n, qp, func, note) in NEW.items():
        use = "".join(f'<td class="dz">{sum(q for g, kk, _, q, *_ in Q[z["id"]]["items"] if kk == key) or "–"}</td>' for z in ZONES)
        rows.append(f'<tr><td class="nm">{E(n)}<br><span class="chg">신규 · 정가표 외</span></td><td class="num">–</td><td class="num"><b>{k(qp)}</b></td>'
                    f'<td class="q">–</td><td>{E(func)}</td><td class="note">{E(note)}</td>{use}</tr>')
    head = "".join(f"<th class='dz'>{E(z['id'])}</th>" for z in ZONES)
    return ('<div class="tbl-wrap"><table class="bom wide"><thead><tr><th>옵션·제품</th><th class="r">정가</th><th class="r">견적 단가</th><th style="text-align:center">비율</th>'
            f'<th>기능</th><th>확인·제약</th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def task_table(z):
    body = "".join(f"<tr><td>{E(t)}</td><td class='nm'>{E(o)}</td></tr>" for t, o in z["tasks"])
    return f'<div class="tbl-wrap"><table class="bom"><thead><tr><th>이 존에서 해야 할 일</th><th>필요한 기능·옵션</th></tr></thead><tbody>{body}</tbody></table></div>'


def quote_table(zid):
    rows, cur = [], None
    for g, key, det, q, u, v, why in Q[zid]["items"]:
        if g != cur:
            cur = g
            sub = sum(qq * uu for gg, _, _, qq, uu, *_ in Q[zid]["items"] if gg == g)
            rows.append(f'<tr class="grp"><th colspan="4" scope="rowgroup">{E(g)}</th><td class="num">{k(sub)}</td><td colspan="2"></td></tr>')
        nm = name_of(key) if key else det
        dd = det if key else ""
        rows.append(f'<tr><td class="nm">{E(nm)}</td><td>{E(dd)}</td><td class="q"><b>{q}</b></td><td class="num">{k(u)}</td>'
                    f'<td class="num">{k(q * u)}</td><td>{tag(v)}</td><td>{E(why)}</td></tr>')
    sw, hw, ts, ga = parts(zid)
    foot = (f'<tr class="tot"><th colspan="4">일반관리비·기업이윤 (SW+HW+기술지원의 10%)</th><td class="num">{k(ga)}</td><td colspan="2"></td></tr>'
            f'<tr class="tot strong"><th colspan="4">견적 합계 (단위절삭 후)</th><td class="num">{k(Q[zid]["total"])}</td><td colspan="2">{E(Q[zid]["no"])}</td></tr>')
    return ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>품목</th><th>상세(포맷·컨트롤러·사양)</th><th style="text-align:center">수량</th>'
            '<th class="r">단가</th><th class="r">금액</th><th>검토</th><th>검토 의견</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody><tfoot>{foot}</tfoot></table></div>')


def pz_table():
    rows, tot = [], 0
    for key, q, why in PZ:
        u = OPT[key][2] * RATE if key in OPT else NEW[key][1]
        tot += u * q
        rows.append(f'<tr><td class="nm">{E(name_of(key))}</td><td class="q"><b>{q}</b></td><td class="num">{k(u)}</td><td class="num">{k(u * q)}</td><td>{E(why)}</td></tr>')
    rows.append(f'<tr class="tot strong"><th colspan="3">합계 (SW만, 일반관리비·AMC 제외)</th><td class="num">{k(tot)}</td><td>견적 단가(정가×52%) 적용</td></tr>')
    return ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>옵션</th><th style="text-align:center">수량</th><th class="r">단가</th><th class="r">금액</th><th>쓰는 이유</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


ISSUES = [
    ("견적", "할인율", "정가 대비 48% 할인(×52%). 10/6 회의에서 언급된 60% 할인보다 낮음", "SW 금액 약 30% 차이", "60% 할인 적용 가능 여부 협의"),
    ("견적", "AMC 4년 선계상", "연 18% × 4년(1년 무상 + 4년 = 5년 유지보수로 보임)을 장비 견적에 넣음. 참고사항 '5년 AMC 면제' 문구와 표의 계상 금액이 서로 다름", "3존 합계 약 9.7억, 장비비 계상 불가 시 재편성", "문구 의미 확인, NIPA에 유지보수 선계상 가능 여부 확인"),
    ("로봇·PLC", "메이커 가정", "OLP·ACS·AIMS 컨트롤러(현대·가와사키 / 야스카와·쿠카 / 화낙·ABB)와 PLC(LS·미쓰비시 / 지멘스 / 로크웰)가 존마다 다르게 임의 배정", "실제 발주 기종과 다르면 옵션 교체 필요", "존별 로봇·PLC 메이커 확정 후 옵션 재산정"),
    ("범위", "정밀조립 미포함", "견적 3건에 정밀조립존 DT·시뮬레이션이 없음", "정밀조립 1차년도 DT 수단 공백", "정밀조립 1좌석 추가 견적 또는 3존 라이선스 공동활용 협의"),
]


def issues_table():
    body = "".join(f'<tr><td class="u">{E(a)}</td><th scope="row">{E(b)}</th><td>{E(c)}</td><td>{E(d)}</td><td>{E(e)}</td></tr>' for a, b, c, d, e in ISSUES)
    return ('<div class="tbl-wrap"><table class="bom issuetbl"><thead><tr><th>구분</th><th>쟁점</th><th>현재 상황</th><th>영향</th><th>다음 조치</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


REFS = [
    ("Q1", "견적", "캠틱종합기술원 3D가상 환경 구축 및 DMWorks 구매 견적서 — 유연제조(1008-1)·적응가공(1008-2)·AI정밀검사(1008-3)", "2026-10-08", "OneDrive Workspace / Customers / 이지로보틱스 / 2026-10-08"),
    ("Q2", "제안서", "캠틱종합기술원 시뮬레이션 환경 구축 제안서 — 제품 설명(DM-Monitoring·USD Converter·Live Edit·ACS·AIMS·PIA·TESCar), DT 구축 절차, 교육 3단계", "2026-10-08", "같은 폴더"),
    ("E1", "이메일", "송기정 부원장 전달 '기술 실증 테스트베드 시스템 도입 수정 제안서 및 견적서' — 10/7 미팅 후 재접수, DMWorks 옵션 추가·공급 가능 SW 포함·HW 반영", "2026-10-08", "OneDrive Workspace / Email"),
    ("S1", "정가표", "DMWorks 3.0 Solution List Price — 옵션별 정가, 유지보수 18%", "2026-01", "OneDrive Workspace / Customers / 이지로보틱스"),
    ("M1", "회의록", "이지로보틱스 DMWorks 방문 Q&A — USD·PLC·AAS·OLP 제약, 라이선스·교육", "2026-09-30", "OneDrive Workspace / MoM / 2026-09-30"),
    ("W1", "llm-wiki 결정", "OCS 시뮬레이션 셀 존별 목적·구성 문서화 후 견적 확정 — 60% 할인 제안, 스캐너 공동활용, GPU 서버 4.05억", "2026-10-06", "llm-wiki decisions"),
]


def refs_table():
    body = "".join(f'<tr><td class="sym">[{a}]</td><td class="u">{E(b)}</td><td>{E(c)}</td><td class="u">{E(d)}</td><td class="note">{E(e)}</td></tr>' for a, b, c, d, e in REFS)
    return ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>표기</th><th>구분</th><th>문서·내용</th><th>일자</th><th>위치</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


def page():
    zsecs = "".join(f'''
<section id="{z["slug"]}">
  <p class="eyebrow">{E(z["id"])} · {E(z["purpose"])} · {E(Q[z["id"]]["no"])}</p>
  <h2>{E(z["name"])} · 견적 {k(Q[z["id"]]["total"])}천원</h2>
  <h3>해야 할 일과 필요한 기능</h3>
  {task_table(z)}
  <h3>10/8 견적 구성과 검토 <span class="chg">(단위 천원 · VAT 별도)</span></h3>
  {quote_table(z["id"])}
</section>''' for z in ZONES)
    return f'''<title>DMWorks 존별 옵션 구성</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=IBM+Plex+Mono:wght@400;500&display=swap">
{CSS}{EXTRA}
<header class="mast"><div class="wrap">
  <p class="eyebrow">총괄5-세부1 기술실증 테스트베드 · 이지로보틱스 10/8 견적서(1008-1~3) 기준 · 2026.10.08 갱신 · 검토본</p>
  <h1>DMWorks 존별 옵션 구성</h1>
</div></header>
<nav class="toc" aria-label="바로가기"><div class="wrap">
  <a href="#sum">요약</a><a href="#why">구매 필요성</a><a href="#opt">단가·제품</a>{"".join(f'<a href="#{z["slug"]}">{z["id"]}</a>' for z in ZONES)}<a href="#z3">A-3</a><a href="#issues">확인 필요</a><a href="#refs">근거</a>
</div></nav>
<main class="wrap">
<section id="sum" style="margin-top:8px">
  <p class="eyebrow">결론 및 핵심 요약 (Executive Summary)</p>
  <h2>10/8 견적 3개 존 · 합계 {k(QTOTAL)}천원</h2>
  {key_table()}
  <h3>존별 견적 합계</h3>
  {summary_table()}
</section>
<section id="why">
  <p class="eyebrow">1. 구매 필요성</p>
  <h2>존별 구매 필요성·활용 목적</h2>
  {why_tables()}
</section>
<section id="opt">
  <p class="eyebrow">2. 견적 단가·제품</p>
  <h2>옵션별 정가 대비 견적 단가, 신규 제품 기능</h2>
  <p class="note-box">정가표 옵션은 모두 정가 × 52%. 아래 7종은 정가표에 없는 제품으로 견적가만 있음. 오른쪽 열은 존별 견적 수량. 검토 표시: <b>적합</b> 존 목적에 맞음 · <b>확인</b> 기종·포맷·역할 확정 후 결정 · <b>조정</b> 줄이거나 빼기를 제안.</p>
  {price_table()}
</section>
{zsecs}
<section id="z3">
  <p class="eyebrow">A-3 · 셀 배치·물류·상태머신 검증 · 견적 없음</p>
  <h2>정밀조립존 (OCS 셀 없음 · DT 워크스테이션 1대)</h2>
  <p class="note-box">10/8 견적 대상에 없음. 같은 견적 단가로 1좌석을 산정함. 협동로봇(국산)은 OLP 목록에 없어 제외.</p>
  {pz_table()}
</section>
<section id="issues">
  <p class="eyebrow">확인 필요 사항</p>
  <h2>재견적 전에 정리할 쟁점</h2>
  {issues_table()}
</section>
<section id="refs">
  <p class="eyebrow">근거 문서</p>
  <h2>참조</h2>
  {refs_table()}
</section>
</main>
'''


if __name__ == "__main__":
    open(out("dmworks_zones.html"), "w", encoding="utf-8").write(page())
    for z in Q:
        sw, hw, ts, ga = parts(z)
        print(z, k(sw), k(hw), k(ts), k(ga), k(sw + hw + ts + ga), "quote", k(Q[z]["total"]))
    print("pz", k(pz_total()))
