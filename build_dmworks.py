"""DMWorks 존별 옵션 구성 페이지 → dmworks_zones.html
근거: 이지로보틱스 10/23 견적서(견26CAMTIC-DMWorks-1023-1~3, 엑셀)·10/15 최종 견적서(1015-1~3), 10/8 견적서(1008-1~3)·제안서, DMWorks 3.0 정가표(2026.01), 9/30 방문 Q&A, 10/6 의사결정."""
import html
import re

import build_ocs_sim as S
import build_page as bp
import quote_live as ql
from privacy import PUBLIC, PUBLIC_NOTE, money as km, out, pick

E = html.escape
RATE = 0.572  # 10/15·10/23 견적 단가 = 정가(Node-Lock) × 57.2% (= 10/8 견적 52% × 1.1, 전 옵션 동일)

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
# 정가표에 없는 제품 (10/8 제안서·10/23 견적) — 단가는 견적가
NEW = {
    "DMON": ("DM-Monitoring", 35200, "설비 실시간 연동으로 DT 동작 일치, CELL/ZONE 운영 정보(생산량·진행률·CT) 분할 화면, 권한 관리", "OCS Cell 관제(OWS·존 오케스트레이터 UI)와 기능이 겹침 → 역할 구분 필요"),
    "USD": ("Omniverse USD Converter", 15840, "Workcell을 Tree 구조 유지한 USD로 변환·Nucleus 업로드, 물리 설정 정보 반영. 기구 정의 변환은 '협의 후 개발 예정'", "9/30 '지오메트리만' 문제를 푸는 항목. 기구 정의는 아직 개발 전"),
    "LE": ("Omniverse Live Edit", 11440, "DMWorks–Omniverse Live Session으로 위치·동작 실시간 동기화", "9/30 업체 스스로 'DT 운영용 비추천(지연)'"),
    "ACSB": ("ACS BASE", 28600, "검사 결과(결함 위치 3D 좌표)로 로봇 리워크 프로그램·레시피 자동 생성 기본 환경", "리워크 공정이 있는 존에만 의미. AI 알고리즘 연동 가능"),
    "ACSO": ("ACS OLP (컨트롤러당)", 18920, "리워크 경로를 로봇 컨트롤러 형식 OLP로 생성", "OLP와 같은 컨트롤러 2종 계상"),
    "AIMSS": ("AIMS Simulator (컨트롤러당)", 52800, "가상 측정 작업장·캘리브레이션·측정 시뮬레이션·로봇 OLP", "레이저트래커·스캐너 로봇 자동 측정(CMM 수준)"),
    "AIMSC": ("AIMS Controller (컨트롤러당)", 39600, "측정 시스템 통합 제어·데이터 수집·실시간 결과 모니터링", ""),
    "PIA": ("PIA (Predictive Inspect & Analysis)", 35200, "3D 스캔 데이터 경량화·컬러맵·섹션·차트 시각화로 품질 예측", "측정 결과 분석 SW(9/30 소개)"),
    "TES": ("TESCar", 66000, "스캔 데이터로 저항 점용접 품질 자동 판정·최적 용접조건 제시", "차체 스폿용접 특화 → 유연제조(용접) 쪽 기능에 가까움"),
    "DEL": ("CATIA DELMIA 1년 구독", 121700, "외산 디지털 제조·공정 시뮬레이션 SW 1년 구독 — 수요기업 CATIA 데이터·공정계획 연계", "10/12 결정 외산 SW. 구독이라 과제 후 갱신비 별도, 장비비 계상 확인"),
    "XCL": ("Siemens X-cloud 1년 구독", 149700, "외산 클라우드 설계·제조 SW 1년 구독 — 포함 모듈(NX·Process Simulate 등)은 견적서에 없음", "10/12 결정 외산 SW. 포함 모듈·갱신비 확인"),
    "LWC": ("3D 형상 경량화·표준 변환 SW", 30000, "디지털 트윈용 3D 형상 데이터 경량화·표준 포맷 변환", "10/23 신규, 제품명 미기재. CAD IMPORT/EXPORT·USD Converter와 역할 구분 필요"),
}

# ------------------------------------------------------------------ 10/23 견적 (천원)
# 품목 행(항목·수량·단가·견적서 품목)은 OCS 시뮬레이션 Cell 데이터(build_ocs_sim.ZONES)에서 가져오고, 여기서는 검토 [ok|chk|adj]·의견만 붙임
Q15 = {"A-1-4": 1991000, "A-2-5": 2192000, "A-4-5": 2610000}  # 10/15 최종 견적 합계
REV = {
    "BASE": ("ok", "필수 기본 모듈"),
    "DMON": ("ok", "DT 모니터링 화면(운영 관제는 OCS Cell)"),
    "CADI": ("ok", "존 CAD 원본 포맷 반입"),
    "CADE": ("ok", "AAS·중립 포맷 내보내기"),
    "OLP": ("ok", "로봇 오프라인 프로그래밍(컨트롤러 2종)"),
    "RRS": ("ok", "컨트롤러 사이클타임 정밀 산출"),
    "PC": ("ok", "스캔 점군·파노라마로 가상 작업장 구축(10/23 품목명에 Panorama 추가, 단가 같음)"),
    "MP": ("ok", "다공정 라인·AMR 물류"),
    "PLC": ("ok", "PLC 가상 시운전 — 10/23 견적에서 항목2로 분리"),
    "PID": ("ok", "존 전용 Plug-in 개발"),
    "PIU": ("ok", ""),
    "USD": ("ok", "Isaac Sim·Isaac Lab 학습 DT 연계 핵심"),
    "LE": ("ok", "Omniverse 리뷰 세션 실시간 동기화"),
    "DEL": ("chk", "10/12 결정 외산 SW 1년 구독 — 10/15엔 별도, 10/23에 견적 안으로 들어옴. 구독이라 장비비 계상 가능 여부·과제 후 갱신비 확인"),
    "XCL": ("chk", "10/12 결정 외산 SW 1년 구독 — 10/15엔 별도, 10/23에 견적 안으로 들어옴. 포함 모듈·장비비 계상 가능 여부·갱신비 확인"),
    "LWC": ("chk", "10/23 신규. 제품명·기능 미기재 — CAD IMPORT/EXPORT·USD Converter와 겹치는지 확인"),
    "AMC": ("ok", "최초 1년 무상 + 18% × 4년 = 참고사항 '5년 AMC'와 맞음(10/15 쟁점 해소). 외산 구독은 제외"),
    "GPU": ("ok", "10/12 결정 GPU 4장 + 방화벽, 10/15와 같음"),
    "OPC": ("ok", "10/23 견적에 사양 기재(CPU·GPU·RAM·SSD)"),
    "NB": ("ok", "10/23 견적에 사양 기재"),
    "MON": ("chk", "구성품(비디오월 4면·영상 제어기·운영 콘솔·연동 셋업)은 3존 같은데 금액이 75,000·126,000·159,500으로 다름(10/15은 55,000)"),
    "LSV": ("chk", "하위 5종(서버 노드·GPU 서버·스토리지·백업 NAS·TSDB) 나열만, 사양·수량·금액 없음. 존별로 금액만 다름(222,592·389,535·340,000)"),
    "EGW": ("chk", "3존 같은 금액. Edge Gateway 서버·영상 노드·캐비닛 수량 1 — Cell 수만큼 필요한지 확인"),
    "NET": ("chk", "8개 구성품 나열(10/22 사양서 세분안과 같음), 3존 같은 금액 — 사양·수량·금액 없음"),
    "RACK": ("chk", "서버랙·UPS·항온항습기·KVM — 항온항습기가 새로 포함됨, 용량 미기재"),
    "SEC": ("ok", "로컬 OCS 접근·인증 관리"),
    "SCN": ("ok", "10/23 견적에 성능 수치 기재 — 규격서에 옮겨 적으면 됨"),
    "TS": ("chk", "10/15 맞춤 개발(DT 연동·DB 시각화 UI·플러그인)이 '교육 및 기술지원 — 과제기간 내 무상'으로 바뀜. 맞춤 개발 포함 여부 서면 확인"),
    "ACSB": ("ok", "판정→재검사→리워크 폐루프와 직접 맞음(10/12 결정: ACS는 정밀검사존만)"),
    "ACSO": ("chk", "구매계획(안)은 FANUC·KUKA — 리워크 로봇 메이커로 한쪽에 맞춤"),
    "PIA": ("ok", "스캔 결과 분석·시각화"),
    "TES": ("chk", "차체 스폿용접 특화. 10/23에 항목4(최적화·제조데이터 플랫폼)로 옮김. 감액이 필요하면 1순위 — 유지하려면 대상 부품의 용접부 검사 근거 필요"),
    "AIMSS": ("chk", "레이저트래커 측정용 — 측정 HW(대형 스캐너)는 10/15에 빠졌는데 AIMS는 남음. 측정 HW 없이 쓸 근거 명시 필요"),
    "AIMSC": ("chk", "측정 시스템 제어용 — 제어할 측정 HW가 없어 AIMS Simulator와 같이 판단"),
}
REV_Z = {
    "A-1-4": {"CADI": ("chk", "10/12 결정(PRO/E 빼고 3종)과 달리 4종으로 원복"), "CADE": ("chk", "10/12 결정(JT 1종)과 달리 JT·VRML·OBJ 3종으로 원복"),
              "OLP": ("ok", "용접·핸들링 로봇 오프라인 프로그래밍(컨트롤러 2종)"), "RRS": ("ok", "현대 Hi5 컨트롤러 사이클타임 정밀 산출"),
              "PLC": ("ok", "PLC 가상 시운전 2종(DMWorks 동시 시뮬레이션 2기종 경험 범위) — 10/23에 항목2로 분리"), "MP": ("ok", "혼류 라인·AMR 물류"),
              "SCN": ("ok", "대형 공간 스캔으로 공장·셀 가상 작업장 구축 — 10/23 견적에 성능 수치 기재")},
    "A-2-5": {"OLP": ("ok", "머신텐딩 로봇 오프라인 프로그래밍"), "MP": ("ok", "팔레트·AMR 물류"),
              "PLC": ("ok", "PLC 메이커 확정 시 일치 여부 확인 — 10/23에 항목2로 분리"),
              "AMC": ("chk", "형상 변환 SW를 AMC 계상 기준에서 뺌(다른 두 존은 포함, 실효 16.4%) — 3존 기준 통일 확인"),
              "SCN": ("ok", "가공 소재·제품 자동 스캔 — 10/23 견적에 성능 수치 기재. 자동 스캔 스테이션 구성은 없음")},
    "A-4-5": {"OLP": ("ok", "검사·리워크 로봇 오프라인 프로그래밍"), "RRS": ("ok", "FANUC 컨트롤러 사이클타임 정밀 산출"), "MP": ("ok", "검사 라인·AMR 물류"),
              "PLC": ("ok", "검사 라인 PLC 가상 시운전"), "DMON": ("ok", "DT 모니터링 화면(품질 관제는 QMS·OCS) — 10/23에 항목3으로 옮김"),
              "OPC": ("ok", "10/23에 항목2(공정·로봇 시뮬레이션 SW)로 옮김, 사양 기재"), "NB": ("ok", "10/23에 항목2로 옮김, 사양 기재"),
              "MON": ("chk", "3존 중 가장 큼(159,500, 10/15은 55,000). 모니터링 워크스테이션은 운영 PC 공용으로 적혀 있어 금액 근거 확인"),
              "TS": ("chk", "10/15 맞춤 개발(DT 연동·DB 시각화 UI·플러그인·ACS 연동 99,000)이 '과제기간 내 무상'으로 바뀜. 맞춤 개발 포함 여부 서면 확인"),
              "AMC": ("ok", "최초 1년 무상 + 18% × 4년. ACS·AIMS·PIA·TESCar·형상 변환 SW 포함 — AIMS·TESCar 조정 시 함께 감소")},
}
HWK = ("GPU", "OPC", "NB", "MON", "SCN")  # OCS HW
LOCK = ("LSV", "EGW", "NET", "RACK", "SEC")  # 로컬 HW·보안


def _items(oz):
    """(항목, key, 상세, 수량, 단가, 검토, 의견, sym) — key는 단가표 제품(OPT·NEW·AMC)일 때만, 아니면 상세에 견적서 품목명"""
    out_ = []
    for gt, no, sym, det, q, u, lab in S.qlines(oz):
        v, why = REV_Z[oz["id"]].get(sym) or REV.get(sym, ("ok", ""))
        if sym in OPT or sym in NEW or sym == "AMC":
            out_.append((gt, sym, f"{S.amc_text(oz)} (최초 1년 무상)" if sym == "AMC" else det, q, u, v, why, sym))
        else:
            out_.append((gt, "", lab, q, u, v, why, sym))
    return out_


Q = {oz["id"]: {"no": oz["no"], "total": oz["total"], "ga": oz["ga"], "items": _items(oz)} for oz in S.ZONES}
# 10/15 최종 견적(1015-1~3) 대비 변경 — 앞 문장(합계)은 공개본에서 뺌
CHANGES = {
    "A-1-4": "19.91억 → 21.00억. 카티아·델미아 1년 구독 121,700·형상 경량화·변환 SW 30,000 추가, CAD IMPORT 3→4종·EXPORT 1→3종 원복, 모니터링 시스템 55,000 → 75,000, 기술지원(맞춤 개발 44,550) → 무상, 로컬 HW(TSDB 포함) 577,500 → 546,025",
    "A-2-5": "21.92억 → 23.20억. Siemens X-cloud 1년 구독 149,700·형상 경량화·변환 SW 30,000 추가, 모니터링 시스템 55,000 → 126,000, 기술지원(맞춤 개발 77,000) → 무상, 로컬 HW(TSDB 포함) 731,500 → 712,968",
    "A-4-5": "26.10억 → 26.00억. 형상 경량화·변환 SW 30,000 추가, 모니터링 시스템 55,000 → 159,500, 기술지원(맞춤 개발 99,000) → 무상, 로컬 HW(TSDB 포함) 676,500 → 663,433, 항목 재배치(운영 PC·노트북 → 항목2, DM-Monitoring → 항목3, TESCar → 항목4)",
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

# 정밀조립: 견적 없음 → 10/23 견적 단가로 산정
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
    """품목 성격별 합계 — SW(DMWorks·외산·AMC) · OCS HW · 로컬 HW·보안 · 기술지원 · 일반관리비"""
    it = Q[zid]["items"]
    f = lambda c: sum(q * u for _, _, _, q, u, _, _, s in it if c(s))
    return f(lambda s: s in S.GEN), f(lambda s: s in HWK), f(lambda s: s in LOCK), f(lambda s: s == "TS"), Q[zid]["ga"]


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
    ("외산 SW와 구분", "10/12 결정에 따라 10/23 견적에 외산 SW 1년 구독이 들어옴(유연제조 카티아·델미아, 적응가공 Siemens X-cloud). 외산은 수요기업 포맷·비교 검증용, DMWorks는 셀 단위 PLC 핸드셰이크·AAS 출력·USD 연계를 맡는 국산 기본 도구로 구분 — 심의 중복성 질문 대비", "10/12 결정 · 10/23 견적"),
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
    amt = lambda c: sum(q * u for z in Q for _, _, _, q, u, _, _, s in Q[z]["items"] if c(s))
    amc, srv, scn, sub = amt(lambda s: s == "AMC"), amt(lambda s: s == "GPU"), amt(lambda s: s == "SCN"), amt(lambda s: s in S.SUBSCR)
    loc = sum(parts(z)[2] for z in Q)
    q15 = sum(Q15.values())
    rows = [
        ("견적 개요", pick(f"이지로보틱스 10/23 견적 3건(1023-1~3, 엑셀). 유연제조 {k(Q['A-1-4']['total'])} · 적응가공 {k(Q['A-2-5']['total'])} · AI정밀검사 {k(Q['A-4-5']['total'])} = 합계 {k(QTOTAL)}천원 "
                           f"(10/15 최종 {k(q15)}천원 대비 {QTOTAL - q15:+,.0f}천원). 존별 합계가 연구개발계획서 1차년도 계획액(21.00·23.20·26.00억)과 같음. ",
                           "이지로보틱스 10/23 견적 3건(1023-1~3, 엑셀) — 유연제조·적응가공·AI정밀검사, 견적 합계는 공개본에서 비공개. ")
                      + "10/12 결정의 외산 SW 1년 구독(유연제조 카티아·델미아, 적응가공 Siemens X-cloud)이 이번에 견적 안으로 들어옴. 과제기간 4개월, Network-Lock 라이선스, VAT 포함", "10/23 견적서"),
        ("견적 구조", "항목1~4 이름·구성이 존마다 다름 — 유연제조·적응가공: ① 공정 시뮬레이션 SW(외산 구독 포함) ② PLC 가상 시운전 SW ③ 연산 서버·운영 PC·모니터링 ④ 로컬 서버·Edge Gateway·네트워크·기반시설·보안·스캐너 / "
                      "AI정밀검사: ① 측정·분석 SW ② 공정·로봇 시뮬레이션 SW·운영 PC ③ DM-Monitoring·모니터링·연산 서버 ④ TESCar·로컬. 공통 ⑤ 교육·기술지원(무상) ⑥ AMC ⑦ 일반관리비·이윤 = (①+②+③)의 10%(유연제조·적응가공은 산식에서 1천원 차감)", "10/23 견적서"),
        ("단가 수준", "정가표 옵션은 10/15와 같은 정가(Node-Lock) × 57.2% = 10/8 견적 단가(× 52%) × 1.1. 10/23 견적은 표지·참고사항 모두 'VAT 포함'이라 공급가 기준 할인율 48%(10/15 쟁점 해소). 10/6에 들은 60% 할인은 미반영", "정가표 대조"),
        ("10/15 대비 변경", "외산 구독 2건(271,400)·형상 경량화·변환 SW 3건(90,000) 추가, 모니터링 시스템 55,000 → 75,000·126,000·159,500, 유연제조 CAD 옵션 4·3종으로 원복(10/12 결정과 다름), 기술지원 맞춤 개발 220,550 → 무상, "
                             "로컬 HW 1식을 Local Server·Edge Gateway·네트워크·기반시설로 분리(TSDB는 Local Server에 포함, 항온항습기 추가)", "10/15 · 10/23 대조"),
        ("금액이 큰 항목", pick(f"로컬 HW 3존 {k(loc)} · 연산 서버 3대 {k(srv)} · AMC 4년 {k(amc)} · 외산 구독 {k(sub)} · 스캐너 2대 {k(scn)}천원 — 다섯 가지가 전체의 약 {round((loc + srv + amc + sub + scn) / QTOTAL * 100)}%",
                                f"로컬 HW 3존 {k(loc)} · 연산 서버 3대 {k(srv)} · 외산 구독 {k(sub)} · 스캐너 2대 {k(scn)}천원 · AMC 4년(DMWorks SW 기준이라 비공개)"), "견적 항목 합산"),
        ("확인 항목", "외산 구독의 장비비 계상·갱신비, 형상 변환 SW 제품·AMC 기준, 모니터링 시스템 존별 금액, 1식 품목(Local Server·Edge Gateway·네트워크·기반시설) 사양·금액, 기술지원 무상 범위, 유연제조 CAD 원복. "
                      "정밀검사 AIMS(측정 HW 없음)·TESCar·ACS OLP 메이커는 10/15부터 남은 항목", "존별 검토"),
        ("정밀조립", "견적 대상이 아님. 같은 단가로 Base·MULTIPLE PROCESS·PLC·Plug-in User·USD Converter 1좌석을 잡으면 " + pick(f"약 {k(pz_total())}천원", "금액은 비공개"), "견적 단가 적용"),
    ]
    ids = {"견적 개요": ' id="ql-k-ov"', "금액이 큰 항목": ' id="ql-k-big"'}  # quote_live.js가 업로드 견적 기준으로 고침
    body = "".join(f'<tr><th scope="row">{E(a)}</th><td{ids.get(a, "")}>{E(b)}</td><td class="note">{E(c)}</td></tr>' for a, b, c in rows)
    return f'<div class="tbl-wrap"><table class="bom keytbl"><thead><tr><th>항목</th><th>내용</th><th>근거</th></tr></thead><tbody>{body}</tbody></table></div>'


SUM_FMT = (km, k, k, k, km)  # SW(DMWorks·외산·AMC) · OCS HW · 로컬 · 기술지원 · 일반관리비(SW 포함 기준) — 공개본은 DMWorks 포함 금액만 가림


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
    return ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>존</th><th>구분</th><th>견적번호</th><th class="r">SW(DMWorks·외산·AMC)</th><th class="r">OCS HW(서버·PC·모니터링·스캐너)</th>'
            '<th class="r">로컬 HW·보안</th><th class="r">기술지원</th><th class="r">일반관리비·이윤</th><th class="r">견적 합계</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div><p class="note-box">단위 천원, VAT 포함(10/23 견적은 표지·참고사항 모두 \'부가세 포함\'). 열은 품목 성격별로 다시 묶은 것으로 견적서 항목 번호와 다름. 일반관리비·이윤은 견적서 (항목1+2+3)의 10%. 견적 합계는 업체 단위절삭(10/23은 천만 원 미만 버림 — 8,878·1,056·2,594천원) 후 금액.</p>')


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
    """견적서 항목별 금액 표기 — SW 품목이 든 항목(DMWorks·AMC 등)은 공개본에서 가림"""
    return km if g in S.SWG else k


def quote_table(zid):
    rows, cur = [], None
    for g, key, det, q, u, v, why, _ in Q[zid]["items"]:
        if g != cur:
            cur = g
            sub = sum(qq * uu for gg, _, _, qq, uu, *_ in Q[zid]["items"] if gg == g)
            rows.append(f'<tr class="grp"><th colspan="4" scope="rowgroup">{E(g)}</th><td class="num">{fm(g)(sub)}</td><td colspan="2"></td></tr>')
        nm = name_of(key) if key else det
        dd = det if key else ""
        rows.append(f'<tr><td class="nm">{E(nm)}</td><td>{E(dd)}</td><td class="q"><b>{q}</b></td><td class="num">{fm(g)(u)}</td>'
                    f'<td class="num">{fm(g)(q * u)}</td><td>{tag(v)}</td><td>{E(why)}</td></tr>')
    foot = (f'<tr class="tot"><th colspan="4">항목7. 일반관리비·기업이윤 ((항목1 + 항목2 + 항목3)의 10%, 견적서 기재값)</th><td class="num">{km(Q[zid]["ga"])}</td><td colspan="2"></td></tr>'
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
    rows.append(f'<tr class="tot strong"><th colspan="3">합계 (SW만, 일반관리비·AMC 제외)</th><td class="num">{km(tot)}</td><td>10/23 견적 단가(정가×57.2%, 10/15와 같음) 적용</td></tr>')
    return ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>옵션</th><th style="text-align:center">수량</th><th class="r">단가</th><th class="r">금액</th><th>쓰는 이유</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')


ISSUES = [
    ("견적", "외산 SW 1년 구독", "유연제조 카티아·델미아 121,700, 적응가공 Siemens X-cloud 149,700 — 10/12 결정대로 10/23 견적 안에 들어옴(10/15엔 별도). 1년 구독이라 자산이 아니고 AMC 계상에서도 빠짐",
     "장비비로 못 잡으면 구성 변경, 과제 후 매년 갱신비", "연구시설장비 계상 가능 여부 확인(안 되면 다른 비목), 포함 모듈·갱신 단가 견적 요청"),
    ("견적", "형상 경량화·변환 SW", "3존 각 30,000 신규. 제품명·기능 범위 없음. AMC 계상 기준에 유연제조·정밀검사는 넣고 적응가공은 뺌", "CAD IMPORT/EXPORT·USD Converter와 겹치면 심의 질문",
     "제품명·기능·DMWorks 모듈과 차이 확인, AMC 기준 3존 통일"),
    ("견적", "모니터링 시스템 금액", "구성품(55인치 비디오월 4면·영상 제어기·27인치 4K 콘솔·연동 셋업)은 3존 같은데 75,000·126,000·159,500(10/15은 3존 55,000). 정밀검사는 워크스테이션을 운영 PC 공용으로 적음",
     "총액 맞춤용 조정분으로 보임(추정) — 근거 없이 심의 대응 어려움", "존별 구성품·수량·금액 내역 요청"),
    ("견적", "1식 품목 사양·금액", "Local Server 222,592·389,535·340,000(하위 5종 같음), Edge Gateway 81,796·네트워크 198,864·기반시설 42,774는 3존 같은 금액. 하위 구성품은 나열됐지만 사양·수량·금액 없음. Edge Gateway·캐비닛 수량 1 vs Cell 3~4개",
     "총액만 제시하면 심의 불인정 위험", "구성품별 사양·수량·금액 견적 요청, Edge Gateway Cell별 수량 확인"),
    ("범위", "기술지원 무상", "10/15의 맞춤 개발(DT 연동·DB 시각화 UI·플러그인, 정밀검사 ACS 연동) 44,550·77,000·99,000이 '교육 및 기술지원 — 과제 기간 내 무상'으로 바뀜",
     "맞춤 개발이 빠진 것인지 무상 포함인지 불분명", "맞춤 개발 범위·산출물 포함 여부 서면 확인"),
    ("구성", "유연제조 CAD 옵션", "10/12 결정(IMPORT 3종·EXPORT 1종)과 달리 IMPORT 4종(PRO/E 포함)·EXPORT 3종(JT·VRML·OBJ)으로 원복 — +15,444(AMC·일반관리비 포함 약 28,000)",
     "결정 사항과 견적 불일치", "필요 포맷 재확인 후 확정"),
    ("예산", "계획 대비", "10/23 존별 합계 21.00·23.20·26.00억 = 연구개발계획서 1차년도 계획액과 같음. 10/14 수정 구매계획서(21.20·23.41·26.10억, 외산 구독 포함)보다 0.10~0.21억 적음",
     "예산 안", "외산 구독을 장비비에서 빼야 하면 존별 구성 재조정"),
    ("구성", "정밀검사 AIMS·TESCar", "대형 스캐너는 10/15에 빠졌는데 AIMS Simulator·Controller(합 184,800)와 TESCar(66,000)가 남음. TESCar는 10/23에 항목4로 옮김",
     "측정 HW 없는 측정 SW, 차체 용접 특화 SW에 심의 질문 예상", "유지 근거 명시 또는 감액"),
    ("로봇·PLC", "메이커 정합", "R2 구매계획서 셀별 항목에 같은 메이커로 반영됨(현대·가와사키 / 야스카와·쿠카 / 화낙·ABB, PLC LS·미쓰비시 / 지멘스 / 로크웰). 정밀검사 ACS OLP는 견적 FANUC·ABB, 구매계획(안) FANUC·KUKA로 불일치",
     "실제 발주 기종과 다르면 옵션 교체 필요", "실발주 로봇·PLC와 일치 확인, 정밀검사 ACS OLP 한쪽으로 통일"),
    ("범위", "정밀조립 미포함", "10/23 견적 3건에도 정밀조립존 DT·시뮬레이션이 없음. DMWorks 라이선스 4카피를 우편 수령 예정(교육장·개인 PC 시험용)", "정밀조립 1차년도 DT 수단 공백",
     "수령 라이선스로 정밀조립 1좌석 대체 가능 여부 확인, 안 되면 1좌석 추가 견적"),
    ("견적", "VAT·AMC 표기 (해소)", "10/23 견적은 표지·참고사항 모두 '부가세 포함'. AMC는 '최초 1년 무상 + 18% × 4년'으로 참고사항 '5년 AMC 포함'과 맞음", "—", "10/15 쟁점 해소 — 남은 조치 없음"),
]


# 공개본: 견적 총액·DMWorks 단가가 들어간 문장 대체 (쟁점 → 현재 상황)
ISSUES_PUBLIC = {
    "유연제조 CAD 옵션": "10/12 결정(IMPORT 3종·EXPORT 1종)과 달리 IMPORT 4종(PRO/E 포함)·EXPORT 3종(JT·VRML·OBJ)으로 원복(금액은 공개본에서 비공개)",
    "계획 대비": "10/23 존별 합계가 연구개발계획서 1차년도 계획액과 같고 10/14 수정 구매계획서보다 조금 적음(금액은 공개본에서 비공개)",
    "정밀검사 AIMS·TESCar": "대형 스캐너는 10/15에 빠졌는데 AIMS Simulator·Controller와 TESCar가 남음. TESCar는 10/23에 항목4로 옮김(단가는 공개본에서 비공개)",
}
REFS_PUBLIC = {
    "Q0": "이지로보틱스 존별 디지털 트윈 시뮬레이션 시스템 구축 견적서 — 유연제조(1023-1)·적응가공(1023-2)·AI정밀검사(1023-3), 엑셀",
    "Q4": "같은 견적서 10/15 최종본 — 유연제조(1015-1)·적응가공(1015-2)·AI정밀검사(1015-3)",
    "P1": "OCS 시뮬레이션 셀 구매계획서 R2(부원장 검토)·10/14 수정본(스토리지 서버 포함) — 존별 합계, AMC 18%×4년",
}


def issues_table():
    rows = [(a, b, ISSUES_PUBLIC.get(b, c) if PUBLIC else c, d, e) for a, b, c, d, e in ISSUES]
    body = "".join(f'<tr><td class="u">{E(a)}</td><th scope="row">{E(b)}</th><td>{E(c)}</td><td>{E(d)}</td><td>{E(e)}</td></tr>' for a, b, c, d, e in rows)
    return ('<div class="tbl-wrap"><table class="bom issuetbl"><thead><tr><th>구분</th><th>쟁점</th><th>현재 상황</th><th>영향</th><th>다음 조치</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


REFS = [
    ("Q0", "견적 (기준)", "이지로보틱스 존별 디지털 트윈 시뮬레이션 시스템 구축 견적서 — 유연제조(1023-1, 21.00억)·적응가공(1023-2, 23.20억)·AI정밀검사(1023-3, 26.00억), 엑셀(시트 3장)", "2026-10-23", "OneDrive Workspace / Customers / 이지로보틱스 / 2026-10-23"),
    ("Q4", "최종 견적", "같은 견적서 10/15 최종본 — 유연제조(1015-1, 19.91억)·적응가공(1015-2, 21.92억)·AI정밀검사(1015-3, 26.10억)", "2026-10-15", "피지컬AI 3본부 / 04.장비심의 / 장비별 구비서류 / [A-1-4]·[A-2-5]·[A-4-5]"),
    ("S2", "사양서", "OCS 시뮬레이션 셀 3개 주요 사양서 — 이지로보틱스 수정본(10/22), 10/23 견적과 같은 폴더로 받음", "2026-10-22", "OneDrive Workspace / Customers / 이지로보틱스 / 2026-10-23"),
    ("Q1", "견적", "캠틱종합기술원 3D가상 환경 구축 및 DMWorks 구매 견적서 — 유연제조(1008-1)·적응가공(1008-2)·AI정밀검사(1008-3)", "2026-10-08", "OneDrive Workspace / Customers / 이지로보틱스 / 2026-10-08"),
    ("Q2", "제안서", "캠틱종합기술원 시뮬레이션 환경 구축 제안서 — 제품 설명(DM-Monitoring·USD Converter·Live Edit·ACS·AIMS·PIA·TESCar), DT 구축 절차, 교육 3단계", "2026-10-08", "같은 폴더"),
    ("E1", "이메일", "송기정 부원장 전달 '기술 실증 테스트베드 시스템 도입 수정 제안서 및 견적서' — 10/7 미팅 후 재접수, DMWorks 옵션 추가·공급 가능 SW 포함·HW 반영", "2026-10-08", "OneDrive Workspace / Email"),
    ("S1", "정가표", "DMWorks 3.0 Solution List Price — 옵션별 정가, 유지보수 18%", "2026-01", "OneDrive Workspace / Customers / 이지로보틱스"),
    ("M1", "회의록", "이지로보틱스 DMWorks 방문 Q&A — USD·PLC·AAS·OLP 제약, 라이선스·교육", "2026-09-30", "OneDrive Workspace / MoM / 2026-09-30"),
    ("W2", "llm-wiki 결정", "OCS 시뮬레이션 셀 비용 조정 — 외산 SW 1년 구독·ACS 검사존만·Field 엣지 최대 삭제·검사존 스캐너 제외·AMC 반영·GPU 4장", "2026-10-12", "llm-wiki decisions"),
    ("P1", "구매계획서", "OCS 시뮬레이션 셀 구매계획서 R2(부원장 검토)·10/14 수정본(스토리지 서버 포함) — 존별 21.20·23.41·26.10억, AMC 18%×4년", "2026-10-14", "llm-wiki sources"),
    ("Q3", "비교견적", "엠아이테크 적응가공 비교견적(24.00억) 외 존별 비교견적", "2026-10-15", "OneDrive Workspace / Customers / 이지로보틱스 / 2026-10-15"),
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
        zr = S.zone_rows(oz)
        top = [i for i, r in enumerate(zr) if not r[12]]
        items = Q[z["id"]]["items"]
        assert len(top) == len(items), z["id"]
        rows = []
        for i, (g, key, det, q, u, v, why, sym) in zip(top, items):
            r = zr[i]
            assert r[2] == sym and r[5] == q and abs(r[7] - u) < 1e-6, (z["id"], r[1], det)
            rows.append({"g": int(r[0][2]), "gt": r[0], "cat": S.row_cat(oz, zr, i), "label": r[9], "q": q, "u": u,
                         "dm": {"grp": g, "nm": name_of(key) if key else det, "dd": det if key else "", "v": v, "why": why}})
        zs.append({"id": z["id"], "slug": z["slug"], "name": z["name"], "short": oz["short"], "purpose": z["purpose"], "no": Q[z["id"]]["no"], "date": "2026.10.23",
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
  <h3 id="ql-zh3-{z["slug"]}">10/23 견적 구성과 검토 <span class="chg">(단위 천원)</span></h3>
  <p class="note-box" id="ql-zchg-{z["slug"]}">10/15 최종 견적 대비: {E(pick(CHANGES[z["id"]], CHANGES[z["id"]].split(". ", 1)[1]))}. 공통으로 항목 6→7개(PLC SW 분리·AMC 별도 항목), 일반관리비 기준 (항목1+2+3)의 10%, 표지·참고사항 VAT 포함으로 통일.</p>
  <div id="ql-qt-{z["slug"]}">{quote_table(z["id"])}</div>
</section>''' for z in ZONES)
    return f'''<title>DMWorks 존별 옵션 구성</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=IBM+Plex+Mono:wght@400;500&display=swap">
{CSS}{EXTRA}
<header class="mast"><div class="wrap">
  <p class="eyebrow">총괄5-세부1 기술실증 테스트베드 · <span id="ql-eb">이지로보틱스 10/23 견적서(1023-1~3) 기준</span> · 10/12 비용 조정 반영 · 2026.10.23 갱신 · 검토본</p>
  <h1>DMWorks 존별 옵션 구성</h1>
</div></header>
<nav class="toc" aria-label="바로가기"><div class="wrap">
  <a href="#sum">요약</a><a href="#why">구매 필요성</a><a href="#opt">단가·제품</a>{"".join(f'<a href="#{z["slug"]}">{z["id"]}</a>' for z in ZONES)}<a href="#z3">A-3</a><a href="#issues">확인 필요</a><a href="#refs">근거</a>
</div></nav>
<main class="wrap">
{ql.dmw_panel([(f"ocs_sim_{z['slug']}.html", z["short"]) for z in S.ZONES])}
<section id="sum" style="margin-top:8px">
  <p class="eyebrow">결론 및 핵심 요약 (Executive Summary)</p>
  <h2 id="ql-sumh2">10/23 견적 3개 존 · 합계 {won(QTOTAL)}</h2>
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
  <p class="note-box">정가표 옵션은 모두 정가 × 57.2%(10/8 견적 52% × 1.1, 10/15·10/23 같음). 아래 {len(NEW)}종은 정가표에 없는 제품(외산 구독 포함)으로 견적가만 있음. 오른쪽 열은 존별 10/23 견적 수량. 검토 표시: <b>적합</b> 존 목적에 맞음 · <b>확인</b> 계상 조건 확인 후 결정.</p>
  {price_table()}
</section>
{zsecs}
<section id="z3">
  <p class="eyebrow">A-3 · 셀 배치·물류·상태머신 검증 · 견적 없음</p>
  <h2>정밀조립존 (OCS 셀 없음 · DT 워크스테이션 1대)</h2>
  <p class="note-box">10/23 견적 대상에도 없음. 같은 견적 단가로 1좌석을 산정함. 협동로봇(국산)은 OLP 목록에 없어 제외.</p>
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
        print(z, k(sw), k(hw), k(loc), k(ts), k(ga), k(sw + hw + loc + ts + ga), "quote", k(Q[z]["total"]), "ga10%", k(sum(i[3] * i[4] for i in Q[z]["items"] if i[0][:4] in ("항목1.", "항목2.", "항목3.")) * 0.10))
    print("pz", k(pz_total()))
