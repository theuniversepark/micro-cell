"""DMWorks 존별 옵션 구성 페이지 → dmworks_zones.html
근거: 이지로보틱스 10/15 최종 견적서(견26CAMTIC-DMWorks-1015-1~3), 10/8 견적서(1008-1~3)·제안서, DMWorks 3.0 정가표(2026.01), 9/30 방문 Q&A, 10/6 의사결정."""
import html
import re

import build_ocs_sim as S
import build_page as bp
import quote_live as ql
from privacy import PUBLIC, PUBLIC_NOTE, money as km, out, pick

E = html.escape
RATE = 0.572  # 10/15 최종 견적 단가 = 정가(Node-Lock) × 57.2% (= 10/8 견적 52% × 1.1, 전 옵션 동일)

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
# 정가표에 없는 신규 제품 (10/8 제안서) — 단가는 10/15 최종 견적가
NEW = {
    "MON": ("DM-Monitoring", 35200, "설비 실시간 연동으로 DT 동작 일치, CELL/ZONE 운영 정보(생산량·진행률·CT) 분할 화면, 권한 관리", "OCS Cell 관제(OWS·존 오케스트레이터 UI)와 기능이 겹침 → 역할 구분 필요"),
    "USD": ("Omniverse USD Converter", 15840, "Workcell을 Tree 구조 유지한 USD로 변환·Nucleus 업로드, 물리 설정 정보 반영. 기구 정의 변환은 '협의 후 개발 예정'", "9/30 '지오메트리만' 문제를 푸는 항목. 기구 정의는 아직 개발 전"),
    "LE": ("Omniverse Live Edit", 11440, "DMWorks–Omniverse Live Session으로 위치·동작 실시간 동기화", "9/30 업체 스스로 'DT 운영용 비추천(지연)'"),
    "ACSB": ("ACS BASE", 28600, "검사 결과(결함 위치 3D 좌표)로 로봇 리워크 프로그램·레시피 자동 생성 기본 환경", "리워크 공정이 있는 존에만 의미. AI 알고리즘 연동 가능"),
    "ACSO": ("ACS OLP (컨트롤러당)", 18920, "리워크 경로를 로봇 컨트롤러 형식 OLP로 생성", "OLP와 같은 컨트롤러 2종 계상"),
    "AIMSS": ("AIMS Simulator (컨트롤러당)", 52800, "가상 측정 작업장·캘리브레이션·측정 시뮬레이션·로봇 OLP", "레이저트래커·스캐너 로봇 자동 측정(CMM 수준)"),
    "AIMSC": ("AIMS Controller (컨트롤러당)", 39600, "측정 시스템 통합 제어·데이터 수집·실시간 결과 모니터링", ""),
    "PIA": ("PIA (Predictive Inspect & Analysis)", 35200, "3D 스캔 데이터 경량화·컬러맵·섹션·차트 시각화로 품질 예측", "측정 결과 분석 SW(9/30 소개)"),
    "TES": ("TESCar", 66000, "스캔 데이터로 저항 점용접 품질 자동 판정·최적 용접조건 제시", "차체 스폿용접 특화 → 유연제조(용접) 쪽 기능에 가까움"),
}

# ------------------------------------------------------------------ 10/15 최종 견적 (천원)
# (구분, key, 상세, 수량, 단가, 검토 [ok|chk|adj], 검토 의견)
# 일반관리비·이윤은 (OCS SW + OCS HW + 기술지원)의 10% — 로컬 HW·로컬 OCS·보안은 제외. ga는 견적서 기재값
AMC_NOTE = "견적 SW 합계의 18% × 4년(10/12 결정). 견적서 참고사항은 '5년 AMC 포함'이라 표기와 계산이 다름"
SRV = "DT·AI 연산 서버 (ASUS ESC8000A-E13P · EPYC 9755×2 · 768GB · RTX PRO 6000 96GB ×4 · 방화벽 BLUEMAX NGF 1300)"
LHW = "데이터 처리 서버(HPE DL380 Gen12 ×5)·NAS(Dell PowerStore 1200T)·백업 스토리지·Edge Gateway·영상 수집 노드·네트워크(코어·TSN·방화벽·PTP·AP·배선)·서버실(랙·UPS·KVM)"
LHW_NOTE = "견적서 '상세 사양 별도 협의'. 존마다 금액이 달라(5.28·6.82·6.27억) 총액 맞춤용 조정분으로 보임(추정) — 품목별 사양·수량 확인"
LOCAL = [
    ("로컬 OCS·보안", "", "로컬 제어 부스 HW — Operational TSDB (Machbase Cluster Edition, 계층)", 1, 49500, "ok", "로컬 OCS 운영 데이터 저장"),
    ("로컬 OCS·보안", "", "보안 스택(IAM/PKI) — Keycloak + HIWARE", 1, 38500, "ok", "로컬 OCS 접근·인증 관리"),
]
OCS_HW = [
    ("OCS HW", "", SRV, 1, 385000, "ok", "10/12 결정 GPU 8→4장 반영, 방화벽 포함"),
    ("OCS HW", "", "디지털트윈·시뮬레이션 운영 PC", 1, 13200, "ok", ""),
    ("OCS HW", "", "시뮬레이션 운영 노트북", 1, 7150, "ok", ""),
    ("OCS HW", "", "DT 모니터링 시스템 — 구성품 구매·설치·시스템 연동 셋업", 1, 55000, "ok", ""),
]
Q = {
    "A-1-4": {"no": "견26CAMTIC-DMWorks-1015-1", "total": 1991000, "ga": 125088.606, "items": [
        ("SW", "BASE", "", 1, 81338.4, "ok", "필수. 모니터링은 DM-Monitoring이 맡아 Base는 1카피"),
        ("SW", "MON", "", 1, 35200, "ok", "DT 모니터링 화면(운영 관제는 OCS Cell)"),
        ("SW", "CADI", "STL·CATIA·AUTOCAD", 3, 5148, "ok", "10/15 최종에서 4→3종(PRO/E 삭제)"),
        ("SW", "CADE", "JT", 1, 5148, "ok", "10/15 최종에서 3→1종(STL·VRML·OBJ → JT)"),
        ("SW", "OLP", "HYUNDAI·KAWASAKI", 2, 13728, "ok", "로봇 오프라인 프로그래밍(컨트롤러 2종)"),
        ("SW", "RRS", "HYUNDAI", 1, 11440, "ok", "현대 Hi5 컨트롤러 사이클타임 정밀 산출"),
        ("SW", "PC", "", 1, 21736, "ok", "공장 스캐너 데이터 반영"),
        ("SW", "MP", "", 1, 26312, "ok", "혼류 라인·AMR 물류"),
        ("SW", "PLC", "LS·MITSUBISHI", 2, 25282.4, "ok", "PLC 가상 시운전 2종(DMWorks 동시 시뮬레이션 2기종 경험 범위)"),
        ("SW", "PID", "", 1, 24024, "ok", "존 전용 Plug-in 개발"),
        ("SW", "PIU", "", 1, 8008, "ok", ""),
        ("SW", "USD", "", 1, 15840, "ok", "Isaac Sim 학습 DT 연계 핵심"),
        ("SW", "LE", "", 1, 11440, "ok", "Omniverse 리뷰 세션 실시간 동기화"),
        ("유지보수", "AMC", "연 18% × 4년", 4, 60111.216, "chk", AMC_NOTE),
        ("OCS HW", "", "광대역 공장 스캐너 RTC700 (HW·운영 SW 포함)", 1, 171600, "ok", "대형 공간 스캔으로 공장·셀 가상 작업장 구축"),
        *OCS_HW,
        ("로컬 HW", "", LHW, 1, 528000, "chk", LHW_NOTE),
        *LOCAL,
        ("기술지원", "", "CELL 구성 설비별 DT 연동 기능 Customizing", 1, 11000, "ok", "다른 두 존(22,000)의 절반으로 감액"),
        ("기술지원", "", "DB 연동 시각화 UI Customizing", 1, 28050, "ok", "다른 두 존(44,000)보다 감액. DB 데이터를 DT 화면에 시각화"),
        ("기술지원", "", "DM PLUG-IN 기능 Customizing", 1, 5500, "ok", "AAS 출력·OpenUSD 물성 전달 범위 명시. 다른 두 존(11,000)의 절반"),
    ]},
    "A-2-5": {"no": "견26CAMTIC-DMWorks-1015-2", "total": 2192000, "ga": 129299.178, "items": [
        ("SW", "BASE", "", 1, 81338.4, "ok", "필수"),
        ("SW", "MON", "", 1, 35200, "ok", "DT 모니터링 화면(운영 관제는 OCS Cell)"),
        ("SW", "CADI", "NX·JT·SOLID EDGE·SOLIDWORKS", 4, 5148, "ok", "가공기·지그 원본 포맷 반입"),
        ("SW", "CADE", "AAS·JT·IGES·FBX", 4, 5148, "ok", "AAS·중립 포맷 내보내기"),
        ("SW", "OLP", "YASKAWA·KUKA", 2, 13728, "ok", "머신텐딩 로봇 오프라인 프로그래밍"),
        ("SW", "PC", "", 1, 21736, "ok", "제품 스캐너 점군을 가상 작업장에 반영"),
        ("SW", "MP", "", 1, 26312, "ok", "팔레트·AMR 물류"),
        ("SW", "PLC", "SIEMENS", 1, 25282.4, "ok", "PLC 메이커 확정 시 일치 여부 확인"),
        ("SW", "PID", "", 1, 24024, "ok", "존 전용 Plug-in 개발"),
        ("SW", "PIU", "", 1, 8008, "ok", ""),
        ("SW", "USD", "", 1, 15840, "ok", "강화학습 환경(Isaac Lab) 연계"),
        ("SW", "LE", "", 1, 11440, "ok", "Omniverse 리뷰 세션 실시간 동기화"),
        ("유지보수", "AMC", "연 18% × 4년", 4, 57207.744, "chk", AMC_NOTE),
        ("OCS HW", "", "소형 제품 스캐너(자동) HyperScan (HW·운영 SW 포함)", 1, 209000, "ok", "가공 소재·제품 자동 스캔, 점군을 가상 작업장에 반영"),
        *OCS_HW,
        ("로컬 HW", "", LHW, 1, 682000, "chk", LHW_NOTE),
        *LOCAL,
        ("기술지원", "", "CELL 구성 설비별 DT 연동 기능 Customizing", 1, 22000, "ok", ""),
        ("기술지원", "", "DB 연동 시각화 UI Customizing", 1, 44000, "ok", "DB 데이터를 DT 화면에 시각화"),
        ("기술지원", "", "DM PLUG-IN 기능 Customizing", 1, 11000, "ok", ""),
    ]},
    "A-4-5": {"no": "견26CAMTIC-DMWorks-1015-3", "total": 2610000, "ga": 172301.082, "items": [
        ("SW", "BASE", "", 1, 81338.4, "ok", "필수"),
        ("SW", "MON", "", 1, 35200, "ok", "DT 모니터링 화면(품질 관제는 QMS·OCS)"),
        ("SW", "CADI", "STEP·OBJ·AAS·PARASOLID", 4, 5148, "ok", "검사 대상 CAD 포맷 반입"),
        ("SW", "CADE", "AAS·STP·PARASOLID", 3, 5148, "ok", "역설계 결과 내보내기"),
        ("SW", "OLP", "FANUC·ABB", 2, 13728, "ok", "검사·리워크 로봇 오프라인 프로그래밍"),
        ("SW", "RRS", "FANUC", 1, 11440, "ok", "FANUC 컨트롤러 사이클타임 정밀 산출"),
        ("SW", "PC", "", 1, 21736, "ok", "스캔 기반 가상 작업장"),
        ("SW", "MP", "", 1, 26312, "ok", "검사 라인·AMR 물류"),
        ("SW", "PLC", "ROCKWELL", 1, 25282.4, "ok", "검사 라인 PLC 가상 시운전"),
        ("SW", "PID", "", 1, 24024, "ok", "검사 전용 Plug-in 개발"),
        ("SW", "PIU", "", 1, 8008, "ok", ""),
        ("SW", "USD", "", 1, 15840, "ok", "합성 결함 데이터(Omniverse) 연계"),
        ("SW", "LE", "", 1, 11440, "ok", "Omniverse 리뷰 세션 실시간 동기화"),
        ("SW", "ACSB", "", 1, 28600, "ok", "판정→재검사→리워크 폐루프와 직접 맞음(10/12 결정: ACS는 정밀검사존만)"),
        ("SW", "ACSO", "FANUC·ABB", 2, 18920, "chk", "구매계획(안)은 FANUC·KUKA — 리워크 로봇 메이커로 한쪽에 맞춤"),
        ("SW", "PIA", "", 1, 35200, "ok", "스캔 결과 분석·시각화"),
        ("SW", "TES", "", 1, 66000, "chk", "차체 스폿용접 특화. 감액이 필요하면 1순위 — 유지하려면 대상 부품의 용접부 검사 근거 필요"),
        ("SW", "AIMSS", "FANUC·ABB", 2, 52800, "chk", "레이저트래커 측정용 — 10/15 최종에서 스캐너는 빠졌는데 AIMS는 남음. 측정 HW 없이 쓸 근거 명시 필요"),
        ("SW", "AIMSC", "FANUC·ABB", 2, 39600, "chk", "측정 시스템 제어용 — 제어할 스캐너가 빠져 AIMS Simulator와 같이 판단"),
        ("유지보수", "AMC", "연 18% × 4년", 4, 121779.504, "chk", AMC_NOTE + ". AIMS·TESCar 조정 시 함께 감소"),
        *OCS_HW,
        ("로컬 HW", "", LHW, 1, 627000, "chk", LHW_NOTE),
        *LOCAL,
        ("기술지원", "", "CELL 구성 설비별 DT 연동 기능 Customizing", 1, 22000, "ok", ""),
        ("기술지원", "", "DB 연동 시각화 UI Customizing", 1, 44000, "ok", "DB 데이터를 DT 화면에 시각화"),
        ("기술지원", "", "DM PLUG-IN 기능 Customizing", 1, 11000, "ok", ""),
        ("기술지원", "", "ACS 시스템 Customizing", 1, 22000, "ok", "ACS 리워크 연동"),
    ]},
}
# 10/8 견적(1008-1~3) 대비 변경 — 공통: 단가 전반 ×1.1, 연산 서버 8GPU 520,000 → 4GPU+방화벽 385,000, 로컬 HW·로컬 OCS·보안 추가
CHANGES = {
    "A-1-4": "16.38억 → 19.91억. CAD IMPORT 4→3종·EXPORT 3→1종, ACS(Base·OLP·Customizing) 삭제, 기술지원 감액(75,000 → 44,550), 로컬 HW 528,000·로컬 OCS·보안 88,000 추가",
    "A-2-5": "16.20억 → 21.92억. ACS(Base·OLP·Customizing) 삭제, DB 연동 UI 45,000 → 44,000(×1.1 전), 로컬 HW 682,000·로컬 OCS·보안 88,000 추가",
    "A-4-5": "25.31억 → 26.10억. 대형 제품 스캐너 AT960SR+AS1(560,000) 삭제, ACS·AIMS·PIA·TESCar 유지, 로컬 HW 627,000·로컬 OCS·보안 88,000 추가",
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

# 정밀조립: 견적 없음 → 10/15 최종 견적 단가로 산정
PZ = [("BASE", 1, "DT 워크스테이션 1대용"), ("MP", 1, "셀 간 AMR 물류·배치"), ("PLC", 1, "셀 상태머신·PLC 시퀀스 검증"),
      ("PIU", 1, "A-1-4에서 개발한 AAS 출력 플러그인 실행"), ("USD", 1, "Isaac Sim 학습 DT(VLA)로 셀 전달")]


def k(n):
    return f"{n:,.0f}"


def won(n):
    """DMWorks 금액이 들어간 총액 표기 — 공개본은 '비공개'"""
    return km(n) if PUBLIC else f"{k(n)}천원"


def name_of(key):
    if key in OPT:
        return OPT[key][0]
    if key in NEW:
        return NEW[key][0]
    return {"AMC": "AMC 유지보수"}.get(key, key)


def parts(zid):
    it = Q[zid]["items"]
    sw = sum(q * u for g, _, _, q, u, *_ in it if g in ("SW", "유지보수"))
    hw = sum(q * u for g, _, _, q, u, *_ in it if g == "OCS HW")
    loc = sum(q * u for g, _, _, q, u, *_ in it if g in ("로컬 HW", "로컬 OCS·보안"))
    ts = sum(q * u for g, _, _, q, u, *_ in it if g == "기술지원")
    return sw, hw, loc, ts, Q[zid]["ga"]


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
    ("외산 SW와 구분", "10/12 결정으로 외산 SW 1년 구독이 함께 들어감(유연제조 카티아·델미아, 적응가공 Siemens X-cloud). 외산은 수요기업 포맷·비교 검증용, DMWorks는 셀 단위 PLC 핸드셰이크·AAS 출력·USD 연계를 맡는 국산 기본 도구로 구분 — 심의 중복성 질문 대비", "10/12 결정"),
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
    srv = sum(q * u for z in Q for g, _, d, q, u, *_ in Q[z]["items"] if d == SRV)
    scn = sum(q * u for z in Q for g, _, d, q, u, *_ in Q[z]["items"] if g == "OCS HW" and "스캐너" in d)
    loc = sum(parts(z)[2] for z in Q)
    rows = [
        ("견적 개요", pick(f"이지로보틱스 10/15 최종 견적 3건(1015-1~3). 유연제조 {k(Q['A-1-4']['total'])} · 적응가공 {k(Q['A-2-5']['total'])} · AI정밀검사 {k(Q['A-4-5']['total'])} = 합계 {k(QTOTAL)}천원. ",
                           "이지로보틱스 10/15 최종 견적 3건(1015-1~3) — 유연제조·적응가공·AI정밀검사, 견적 합계는 공개본에서 비공개. ") + "10/14 수정 구매계획서(스토리지 서버 포함) 기준 재견적으로, 10/12 비용 조정 결정이 반영됨. 과제기간 4개월, Network-Lock 라이선스", "10/15 최종 견적서"),
        ("견적 구조", "① OCS SW(DMWorks + AMC) ② OCS HW(스캐너·연산 서버·운영 PC·모니터링) ③ 로컬 HW(데이터 서버·스토리지·네트워크·서버실) ④ 로컬 OCS·보안(TSDB·IAM/PKI) ⑤ 기술지원 ⑥ 일반관리비·이윤 = (①+②+⑤)의 10%. ③·④는 10/8 견적에 없던 항목", "10/15 최종 견적서"),
        ("단가 수준", "정가표 옵션은 모두 정가(Node-Lock) × 57.2% = 10/8 견적 단가(× 52%) × 1.1. 표지 'VAT 포함'이면 할인율은 그대로 48%, 참고사항 '부가세 별도'면 42.8%로 낮아짐. 10/6에 들은 60% 할인은 미반영", "정가표 대조"),
        ("10/12 결정 반영", "유연제조·적응가공 ACS 삭제(정밀검사만 유지), 정밀검사 대형 스캐너 삭제, 연산 서버 GPU 8→4장 + 방화벽(385,000), AMC 18% × 4년 계상, 유연제조 CAD IMPORT 4→3종·EXPORT 3→1종", "10/12 결정 · 10/15 견적"),
        ("금액이 큰 항목", pick(f"로컬 HW 3존 {k(loc)} · 연산 서버 3대 {k(srv)} · AMC 4년 {k(amc)} · 스캐너 2대 {k(scn)}천원 — 네 가지가 전체의 약 {round((loc + srv + amc + scn) / QTOTAL * 100)}%",
                                f"로컬 HW 3존 {k(loc)} · 연산 서버 3대 {k(srv)} · 스캐너 2대 {k(scn)}천원 · AMC 4년(DMWorks SW 기준이라 비공개)"), "견적 항목 합산"),
        ("확인 항목", "AMC '5년' 표기와 ×4 계산 불일치, 표지 VAT 포함 vs 참고사항 부가세 별도. 로컬 HW 상세 사양(견적서 '별도 협의'). 정밀검사 AIMS(측정 HW 없음)·TESCar·ACS OLP 메이커. 나머지 SW·HW는 적합", "존별 검토"),
        ("정밀조립", "견적 대상이 아님. 같은 단가로 Base·MULTIPLE PROCESS·PLC·Plug-in User·USD Converter 1좌석을 잡으면 " + pick(f"약 {k(pz_total())}천원", "금액은 비공개"), "견적 단가 적용"),
    ]
    ids = {"견적 개요": ' id="ql-k-ov"', "금액이 큰 항목": ' id="ql-k-big"'}  # quote_live.js가 업로드 견적 기준으로 고침
    body = "".join(f'<tr><th scope="row">{E(a)}</th><td{ids.get(a, "")}>{E(b)}</td><td class="note">{E(c)}</td></tr>' for a, b, c in rows)
    return f'<div class="tbl-wrap"><table class="bom keytbl"><thead><tr><th>항목</th><th>내용</th><th>근거</th></tr></thead><tbody>{body}</tbody></table></div>'


SUM_FMT = (km, k, k, k, km)  # OCS SW(DMWorks·AMC) · OCS HW · 로컬 · 기술지원 · 일반관리비(SW 포함 기준) — 공개본은 DMWorks 포함 금액만 가림


def summary_table():
    rows, t = [], [0] * 6
    for z in ZONES:
        vals = (*parts(z["id"]), Q[z["id"]]["total"])
        for i, v in enumerate(vals):
            t[i] += v
        rows.append(f'<tr><td><a href="#{z["slug"]}">{E(z["id"])}</a></td><td class="nm">{E(z["name"])}</td><td class="note">{E(Q[z["id"]]["no"])}</td>'
                    + "".join(f'<td class="num">{f(v)}</td>' for f, v in zip(SUM_FMT, vals[:-1])) + f'<td class="num"><b>{km(vals[-1])}</b></td></tr>')
    rows.append(f'<tr><td><a href="#z3">A-3</a></td><td class="nm">정밀조립존</td><td class="note">견적 없음 · 견적 단가로 산정</td>'
                f'<td class="num">{km(pz_total())}</td>' + '<td class="num">–</td>' * 4 + f'<td class="num">{km(pz_total())}</td></tr>')
    rows.append(f'<tr class="tot strong"><th colspan="3">견적 합계 (3개 존)</th>' + "".join(f'<td class="num">{f(v)}</td>' for f, v in zip(SUM_FMT + (km,), t)) + "</tr>")
    return ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>존</th><th>구분</th><th>견적번호</th><th class="r">OCS SW(AMC 포함)</th><th class="r">OCS HW</th>'
            '<th class="r">로컬 HW·OCS·보안</th><th class="r">기술지원</th><th class="r">일반관리비·이윤</th><th class="r">견적 합계</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div><p class="note-box">단위 천원. 견적서 표지는 \'VAT 포함\', 참고사항은 \'부가세 별도\'로 엇갈림. 일반관리비·이윤은 (OCS SW + OCS HW + 기술지원)의 10%로 로컬 HW·로컬 OCS·보안에는 붙지 않음. 견적 합계는 업체 단위절삭(백만 원 미만 버림) 후 금액.</p>')


def price_table():
    rows = []
    for key in ["BASE", "CADI", "CADE", "OLP", "RRS", "PC", "MP", "PLC", "PID", "PIU"]:
        n, code, lp, func, note = OPT[key]
        func = re.sub(r"\s*\d{1,3}(?:,\d{3})+", "", func) if PUBLIC else func  # 기능 설명 속 정가
        qp = lp * RATE
        use = "".join(f'<td class="dz" data-qlq="{key}|{z["id"]}">{sum(q for g, kk, _, q, *_ in Q[z["id"]]["items"] if kk == key) or "–"}</td>' for z in ZONES)
        rows.append(f'<tr><td class="nm">{E(n)}<br><span class="chg">{E(code)}</span></td><td class="num">{km(lp)}</td><td class="num" data-qlu="{key}"><b>{km(qp)}</b></td>'
                    f'<td class="q" data-qlr="{key}">57.2%</td><td>{E(func)}</td><td class="note">{E(note)}</td>{use}</tr>')
    for key, (n, qp, func, note) in NEW.items():
        use = "".join(f'<td class="dz" data-qlq="{key}|{z["id"]}">{sum(q for g, kk, _, q, *_ in Q[z["id"]]["items"] if kk == key) or "–"}</td>' for z in ZONES)
        rows.append(f'<tr><td class="nm">{E(n)}<br><span class="chg">신규 · 정가표 외</span></td><td class="num">–</td><td class="num" data-qlu="{key}"><b>{km(qp)}</b></td>'
                    f'<td class="q">–</td><td>{E(func)}</td><td class="note">{E(note)}</td>{use}</tr>')
    head = "".join(f"<th class='dz'>{E(z['id'])}</th>" for z in ZONES)
    return ('<div class="tbl-wrap"><table class="bom wide"><thead><tr><th>옵션·제품</th><th class="r">정가</th><th class="r">견적 단가</th><th style="text-align:center">비율</th>'
            f'<th>기능</th><th>확인·제약</th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def task_table(z):
    body = "".join(f"<tr><td>{E(t)}</td><td class='nm'>{E(o)}</td></tr>" for t, o in z["tasks"])
    return f'<div class="tbl-wrap"><table class="bom"><thead><tr><th>이 존에서 해야 할 일</th><th>필요한 기능·옵션</th></tr></thead><tbody>{body}</tbody></table></div>'


def fm(g):
    """견적 구분별 금액 표기 — DMWorks SW·AMC는 공개본에서 가림"""
    return km if g in ("SW", "유지보수") else k


def quote_table(zid):
    rows, cur = [], None
    for g, key, det, q, u, v, why in Q[zid]["items"]:
        if g != cur:
            cur = g
            sub = sum(qq * uu for gg, _, _, qq, uu, *_ in Q[zid]["items"] if gg == g)
            rows.append(f'<tr class="grp"><th colspan="4" scope="rowgroup">{E(g)}</th><td class="num">{fm(g)(sub)}</td><td colspan="2"></td></tr>')
        nm = name_of(key) if key else det
        dd = det if key else ""
        rows.append(f'<tr><td class="nm">{E(nm)}</td><td>{E(dd)}</td><td class="q"><b>{q}</b></td><td class="num">{fm(g)(u)}</td>'
                    f'<td class="num">{fm(g)(q * u)}</td><td>{tag(v)}</td><td>{E(why)}</td></tr>')
    foot = (f'<tr class="tot"><th colspan="4">일반관리비·기업이윤 ((OCS SW + OCS HW + 기술지원)의 10%, 견적서 기재값)</th><td class="num">{km(Q[zid]["ga"])}</td><td colspan="2"></td></tr>'
            f'<tr class="tot strong"><th colspan="4">견적 합계 (단위절삭 후)</th><td class="num">{km(Q[zid]["total"])}</td><td colspan="2">{E(Q[zid]["no"])}</td></tr>')
    return ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>품목</th><th>상세(포맷·컨트롤러·사양)</th><th style="text-align:center">수량</th>'
            '<th class="r">단가</th><th class="r">금액</th><th>검토</th><th>검토 의견</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody><tfoot>{foot}</tfoot></table></div>')


def pz_table():
    rows, tot = [], 0
    for key, q, why in PZ:
        u = OPT[key][2] * RATE if key in OPT else NEW[key][1]
        tot += u * q
        rows.append(f'<tr><td class="nm">{E(name_of(key))}</td><td class="q"><b>{q}</b></td><td class="num">{km(u)}</td><td class="num">{km(u * q)}</td><td>{E(why)}</td></tr>')
    rows.append(f'<tr class="tot strong"><th colspan="3">합계 (SW만, 일반관리비·AMC 제외)</th><td class="num">{km(tot)}</td><td>10/15 최종 견적 단가(정가×57.2%) 적용</td></tr>')
    return ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>옵션</th><th style="text-align:center">수량</th><th class="r">단가</th><th class="r">금액</th><th>쓰는 이유</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


ISSUES = [
    ("견적", "VAT·할인율", "10/15 최종 견적서 표지는 'VAT 포함', 참고사항은 '부가세 별도'. 단가는 10/8 × 1.1(정가 × 57.2%). VAT 포함이면 할인율 48% 유지, 별도면 42.8%로 낮아짐. 10/6 회의의 60% 할인 미반영", "VAT 기준에 따라 총액 10% 차이", "업체에 VAT 기준 서면 확인, 60% 할인 적용 가능 여부 협의"),
    ("견적", "AMC 기간", "계상은 10/12 결정대로 18% × 4년. 참고사항은 여전히 '5년 AMC 포함'", "유지보수 기간 해석이 갈림", "업체에 AMC 기간 서면 확인"),
    ("견적", "로컬 HW 사양", "로컬 HW가 존마다 5.28·6.82·6.27억으로 다르고 품목 구성은 같음. 견적서에 '상세 사양 별도 협의'. 10/15 재견적 때 늘어난 금액을 데이터 서버 금액으로 맞춰 총액을 유지했다고 전달됨", "품목별 근거 없이 심의 대응이 어려움", "존별 데이터 서버·스토리지·네트워크 사양·수량 내역 요청"),
    ("예산", "구매계획서 대비", "10/14 수정 구매계획서 존별 합계 21.20·23.41·26.10억(외산 SW 1년 구독 포함). 최종 견적은 19.91·21.92·26.10억 — 적응가공은 X-cloud 1.497억을 빼면 21.91억으로 거의 같음", "외산 SW는 별도 견적으로 더해짐(추정)", "외산 SW 구독 견적 포함 존별 총액이 예산 안인지 재확인"),
    ("구성", "정밀검사 AIMS·TESCar", "대형 스캐너는 빠졌는데 AIMS Simulator·Controller(합 184,800)와 TESCar(66,000)가 남음", "측정 HW 없는 측정 SW, 차체 용접 특화 SW에 심의 질문 예상", "유지 근거 명시 또는 감액"),
    ("로봇·PLC", "메이커 정합", "R2 구매계획서 셀별 항목에 같은 메이커로 반영됨(현대·가와사키 / 야스카와·쿠카 / 화낙·ABB, PLC LS·미쓰비시 / 지멘스 / 로크웰). 정밀검사 ACS OLP는 견적 FANUC·ABB, 구매계획(안) FANUC·KUKA로 불일치", "실제 발주 기종과 다르면 옵션 교체 필요", "실발주 로봇·PLC와 일치 확인, 정밀검사 ACS OLP 한쪽으로 통일"),
    ("범위", "정밀조립 미포함", "견적 3건에 정밀조립존 DT·시뮬레이션이 없음. DMWorks 라이선스 4카피를 우편 수령 예정(교육장·개인 PC 시험용)", "정밀조립 1차년도 DT 수단 공백", "수령 라이선스로 정밀조립 1좌석 대체 가능 여부 확인, 안 되면 1좌석 추가 견적"),
]


# 공개본: 견적 총액·DMWorks 단가가 들어간 문장 대체 (쟁점 → 현재 상황)
ISSUES_PUBLIC = {
    "구매계획서 대비": "10/14 수정 구매계획서 존별 합계(외산 SW 1년 구독 포함)와 최종 견적 합계를 대조 — 적응가공은 X-cloud 1.497억을 빼면 거의 같음(금액은 공개본에서 비공개)",
    "정밀검사 AIMS·TESCar": "대형 스캐너는 빠졌는데 AIMS Simulator·Controller와 TESCar가 남음(단가는 공개본에서 비공개)",
}
REFS_PUBLIC = {
    "Q0": "이지로보틱스 존별 디지털 트윈 시뮬레이션 시스템 구축 견적서 — 유연제조(1015-1)·적응가공(1015-2)·AI정밀검사(1015-3)",
    "P1": "OCS 시뮬레이션 셀 구매계획서 R2(부원장 검토)·10/14 수정본(스토리지 서버 포함) — 존별 합계, AMC 18%×4년",
}


def issues_table():
    rows = [(a, b, ISSUES_PUBLIC.get(b, c) if PUBLIC else c, d, e) for a, b, c, d, e in ISSUES]
    body = "".join(f'<tr><td class="u">{E(a)}</td><th scope="row">{E(b)}</th><td>{E(c)}</td><td>{E(d)}</td><td>{E(e)}</td></tr>' for a, b, c, d, e in rows)
    return ('<div class="tbl-wrap"><table class="bom issuetbl"><thead><tr><th>구분</th><th>쟁점</th><th>현재 상황</th><th>영향</th><th>다음 조치</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


REFS = [
    ("Q0", "최종 견적", "이지로보틱스 존별 디지털 트윈 시뮬레이션 시스템 구축 견적서 — 유연제조(1015-1, 19.91억)·적응가공(1015-2, 21.92억)·AI정밀검사(1015-3, 26.10억)", "2026-10-15", "피지컬AI 3본부 / 04.장비심의 / 장비별 구비서류 / [A-1-4]·[A-2-5]·[A-4-5]"),
    ("Q1", "견적", "캠틱종합기술원 3D가상 환경 구축 및 DMWorks 구매 견적서 — 유연제조(1008-1)·적응가공(1008-2)·AI정밀검사(1008-3)", "2026-10-08", "OneDrive Workspace / Customers / 이지로보틱스 / 2026-10-08"),
    ("Q2", "제안서", "캠틱종합기술원 시뮬레이션 환경 구축 제안서 — 제품 설명(DM-Monitoring·USD Converter·Live Edit·ACS·AIMS·PIA·TESCar), DT 구축 절차, 교육 3단계", "2026-10-08", "같은 폴더"),
    ("E1", "이메일", "송기정 부원장 전달 '기술 실증 테스트베드 시스템 도입 수정 제안서 및 견적서' — 10/7 미팅 후 재접수, DMWorks 옵션 추가·공급 가능 SW 포함·HW 반영", "2026-10-08", "OneDrive Workspace / Email"),
    ("S1", "정가표", "DMWorks 3.0 Solution List Price — 옵션별 정가, 유지보수 18%", "2026-01", "OneDrive Workspace / Customers / 이지로보틱스"),
    ("M1", "회의록", "이지로보틱스 DMWorks 방문 Q&A — USD·PLC·AAS·OLP 제약, 라이선스·교육", "2026-09-30", "OneDrive Workspace / MoM / 2026-09-30"),
    ("W2", "llm-wiki 결정", "OCS 시뮬레이션 셀 비용 조정 — 외산 SW 1년 구독·ACS 검사존만·Field 엣지 최대 삭제·검사존 스캐너 제외·AMC 반영·GPU 4장", "2026-10-12", "llm-wiki decisions"),
    ("P1", "구매계획서", "OCS 시뮬레이션 셀 구매계획서 R2(부원장 검토)·10/14 수정본(스토리지 서버 포함) — 존별 21.20·23.41·26.10억, AMC 18%×4년", "2026-10-14", "llm-wiki sources"),
    ("Q3", "비교견적", "엠아이테크 적응가공 비교견적(24.00억) 외 존별 비교견적", "2026-10-15", "같은 폴더"),
    ("E2", "이메일", "허태한 상무 셀별 재견적 송부 → 이형수 본부장 3본부 전달 — 유연제조 CAD IMPORT/EXPORT 삭제, 서버 수량 조절·방화벽 추가, 데이터 서버 금액 조정으로 총액 유지", "2026-10-15", "OneDrive Workspace / Email"),
    ("W1", "llm-wiki 결정", "OCS 시뮬레이션 셀 존별 목적·구성 문서화 후 견적 확정 — 60% 할인 제안, 스캐너 공동활용, GPU 서버 4.05억", "2026-10-06", "llm-wiki decisions"),
]


def refs_table():
    rows = [(a, b, REFS_PUBLIC.get(a, c) if PUBLIC else c, d, e) for a, b, c, d, e in REFS]
    body = "".join(f'<tr><td class="sym">[{a}]</td><td class="u">{E(b)}</td><td>{E(c)}</td><td class="u">{E(d)}</td><td class="note">{E(e)}</td></tr>' for a, b, c, d, e in rows)
    return ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>표기</th><th>구분</th><th>문서·내용</th><th>일자</th><th>위치</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


def ql_base():
    """quote_live.js용 기준 견적 — 존별 품목 행(견적서 기재 품목·분류는 OCS Cell 페이지 데이터와 같은 순서로 맞춤) + 이 페이지 표기·검토 의견"""
    zs = []
    for z in ZONES:
        oz = next(o for o in S.ZONES if o["id"] == z["id"])
        orows = [r for r in S.zone_rows(oz) if not r[12]]
        items = Q[z["id"]]["items"]
        assert len(orows) == len(items), z["id"]
        rows = []
        for r, (g, key, det, q, u, v, why) in zip(orows, items):
            assert r[5] == q and abs(r[7] - u) < 1e-6, (z["id"], r[1], det)
            rows.append({"g": int(r[0][2]), "cat": S.quote_cat(oz, r[0], r[2], r[1]), "label": r[9], "q": q, "u": u,
                         "dm": {"grp": g, "nm": name_of(key) if key else det, "dd": det if key else "", "v": v, "why": why}})
        zs.append({"id": z["id"], "slug": z["slug"], "name": z["name"], "short": oz["short"], "purpose": z["purpose"], "no": Q[z["id"]]["no"], "date": "2026.10.15",
                   "total": Q[z["id"]]["total"], "ga": Q[z["id"]]["ga"], "rows": rows})
    return {"zones": zs, "names": {**{k_: v[0] for k_, v in OPT.items()}, **{k_: v[0] for k_, v in NEW.items()}, "AMC": name_of("AMC")},
            "list": {k_: v[2] for k_, v in OPT.items()}, "pz": [{"key": k_, "q": q, "why": why, "nm": name_of(k_), "u": OPT[k_][2] * RATE if k_ in OPT else NEW[k_][1]} for k_, q, why in PZ]}


def page():
    zsecs = "".join(f'''
<section id="{z["slug"]}">
  <p class="eyebrow" id="ql-zeb-{z["slug"]}">{E(z["id"])} · {E(z["purpose"])} · {E(Q[z["id"]]["no"])}</p>
  <h2 id="ql-zh2-{z["slug"]}">{E(z["name"])} · 견적 {won(Q[z["id"]]["total"])}</h2>
  <h3>해야 할 일과 필요한 기능</h3>
  {task_table(z)}
  <h3 id="ql-zh3-{z["slug"]}">10/15 최종 견적 구성과 검토 <span class="chg">(단위 천원)</span></h3>
  <p class="note-box" id="ql-zchg-{z["slug"]}">10/8 견적 대비: {E(pick(CHANGES[z["id"]], CHANGES[z["id"]].split(". ", 1)[1]))}. 공통으로 단가 ×1.1, 연산 서버 8GPU → 4GPU + 방화벽.</p>
  <div id="ql-qt-{z["slug"]}">{quote_table(z["id"])}</div>
</section>''' for z in ZONES)
    return f'''<title>DMWorks 존별 옵션 구성</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=IBM+Plex+Mono:wght@400;500&display=swap">
{CSS}{EXTRA}
<header class="mast"><div class="wrap">
  <p class="eyebrow">총괄5-세부1 기술실증 테스트베드 · <span id="ql-eb">이지로보틱스 10/15 최종 견적서(1015-1~3) 기준</span> · 10/12 비용 조정 반영 · 2026.10.19 갱신 · 검토본</p>
  <h1>DMWorks 존별 옵션 구성</h1>
</div></header>
<nav class="toc" aria-label="바로가기"><div class="wrap">
  <a href="#sum">요약</a><a href="#why">구매 필요성</a><a href="#opt">단가·제품</a>{"".join(f'<a href="#{z["slug"]}">{z["id"]}</a>' for z in ZONES)}<a href="#z3">A-3</a><a href="#issues">확인 필요</a><a href="#refs">근거</a>
</div></nav>
<main class="wrap">
{ql.dmw_panel([(f"ocs_sim_{z['slug']}.html", z["short"]) for z in S.ZONES])}
<section id="sum" style="margin-top:8px">
  <p class="eyebrow">결론 및 핵심 요약 (Executive Summary)</p>
  <h2 id="ql-sumh2">10/15 최종 견적 3개 존 · 합계 {won(QTOTAL)}</h2>
  {f'<p class="note-box">{E(PUBLIC_NOTE)}</p>' if PUBLIC else ""}{key_table()}
  <h3>존별 견적 합계</h3>
  <div id="ql-sumtbl">{summary_table()}</div>
</section>
<section id="why">
  <p class="eyebrow">1. 구매 필요성</p>
  <h2>존별 구매 필요성·활용 목적</h2>
  {why_tables()}
</section>
<section id="opt">
  <p class="eyebrow">2. 견적 단가·제품</p>
  <h2>옵션별 정가 대비 견적 단가, 신규 제품 기능</h2>
  <p class="note-box">정가표 옵션은 모두 정가 × 57.2%(10/8 견적 52% × 1.1). 아래 9종은 정가표에 없는 제품으로 견적가만 있음. 오른쪽 열은 존별 10/15 최종 견적 수량. 검토 표시: <b>적합</b> 존 목적에 맞음 · <b>확인</b> 계상 조건 확인 후 결정.</p>
  {price_table()}
</section>
{zsecs}
<section id="z3">
  <p class="eyebrow">A-3 · 셀 배치·물류·상태머신 검증 · 견적 없음</p>
  <h2>정밀조립존 (OCS 셀 없음 · DT 워크스테이션 1대)</h2>
  <p class="note-box">10/15 최종 견적 대상에 없음. 같은 견적 단가로 1좌석을 산정함. 협동로봇(국산)은 OLP 목록에 없어 제외.</p>
  <div id="ql-pz">{pz_table()}</div>
</section>
<section id="issues">
  <p class="eyebrow">확인 필요 사항</p>
  <h2>계약 전에 정리할 쟁점</h2>
  {issues_table()}
</section>
<section id="refs">
  <p class="eyebrow">근거 문서</p>
  <h2>참조</h2>
  {refs_table()}
</section>
</main>
{ql.assets("dmw", ql_base())}
'''


if __name__ == "__main__":
    open(out("dmworks_zones.html"), "w", encoding="utf-8").write(page())
    for z in Q:
        sw, hw, loc, ts, ga = parts(z)
        print(z, k(sw), k(hw), k(loc), k(ts), k(ga), k(sw + hw + loc + ts + ga), "quote", k(Q[z]["total"]), "ga10%", k((sw + hw + ts) * 0.10))
    print("pz", k(pz_total()))
