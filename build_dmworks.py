"""DMWorks 존별 옵션 구성 페이지 → dmworks_zones.html
근거: DMWorks 3.0 Solution List Price(이지로보틱스, 2026.01), 9/30 방문 Q&A, 10/6 의사결정 미팅(60% 할인 제안), 10/7 OCS 셀 3종 표(git a54f74f)."""
import html
import re

import build_page as bp
from privacy import out

E = html.escape
DISC = 0.4  # 10/6 제안 60% 할인 → 정가 × 40%

# ------------------------------------------------------------------ 옵션 (정가: 천원)
# key: (No, 옵션, 코드, Node-Lock, Floating, 기능, 9/30 확인·제약)
OPT = {
    "BASE": ("1", "DMWORKS BASE", "DMW-001-0000", 142200, 184860,
             "Device Modeler(기구학·CAD 생성/수정·좌표계) + Factory Simulator(설비 배치·로봇 라이브러리·모션/Task·충돌검사·케이블 시뮬레이션·단일 공정 Single Station·비디오/3D PDF). CAD IMPORT 1종 포함",
             "단일 공정만 지원(라인·물류는 MULTIPLE PROCESS 필요). 물리엔진 없음 → 학습은 Omniverse. USD 내보내기는 지오메트리만(Assembly·Kinematic·Metadata 미전달)"),
    "CADI": ("2", "CAD IMPORT", "DMW-002-00**", 9000, 11700,
             "외부 CAD 변환·경량화 (STEP·CATIA V4/V5/V6·NX·SolidWorks·Creo·Parasolid·JT·STL 등 22종, 포맷당 1옵션)",
             "BASE에 1종 포함. 수요기업·설비사 CAD 원본 포맷에 맞춰 추가"),
    "CADE": ("3", "CAD EXPORT", "DMW-003-00**", 9000, 11700,
             "DMWorks 데이터를 STL·STEP·IGES·Parasolid·JT·VRML로 내보내기 (포맷당 1옵션)",
             "업체 고지: 원하는 결과가 안 나올 수 있음. DT 라이브러리는 원본 CAD→USD 파이프라인을 쓰므로 필수 아님"),
    "OLP": ("4", "DM OLP", "DMW-004-00**", 24000, 31200,
            "로봇 컨트롤러별 오프라인 프로그래밍. 스폿·핸들링 27종 24,000 / 아크 용접(현대 Hi5) 33,000 / 도장 28,000~33,000",
            "목록에 협동로봇·휴머노이드 컨트롤러 없음(두산·레인보우는 '요청 시 지원', 가격 미정). Upload→수정→Download 오프라인 방식"),
    "PC": ("5", "DM POINT CLOUD", "DMW-005-0000", 38000, 49400,
           "3D 스캔 데이터를 DMWorks에서 확인·수정해 실제 공간 기반 가상 작업장 구축",
           "공장 공간 스캔 개념. 부품 계측·역설계(로봇 스캐닝 경로)는 별도 SW(AIMS) + PolyWorks 연계"),
    "PAN": ("5'", "DM PANORAMA", "DMW-006-0000", 12500, 16250,
            "스캔 지점 파노라마 이미지와 연계한 팩토리 네비게이터(클릭으로 지점 이동)",
            "POINT CLOUD와 함께 쓸 때 의미 있음"),
    "MP": ("6", "DM MULTIPLE PROCESS", "DMW-007-0000", 46000, 59800,
           "다공정 라인(Multiple Station)·물류(컨베이어·셔틀·포크리프트 버퍼) 시뮬레이션, 다차종, UPH·가동률",
           "AMR 대수 산정은 시뮬레이션형(3→4→5대 증가 비교). AMR 실운영 속도·가감속 파라미터 필요. 병목 분석 UI는 커스터마이징"),
    "HUM": ("7", "DM HUMAN", "DMW-008-0000", 38000, 49400,
            "휴먼 디바이스 모델·모션, 작업 자세 분석 리포트 (7-1~7-3 서브옵션의 필수 옵션)",
            ""),
    "MVN": ("7-1", "DM MVN", "DMW-008-0100", 24000, 31200,
            "Movella MVN 착용형 모션캡처 실시간·오프라인 연동", "착용형 MVN 장비 별도 필요(업체 미보유)"),
    "VICON": ("7-2", "DM VICON", "DMW-008-0200", 30000, 39000,
              "VICON 광학식 모션캡처(두리시스템) 연동", "VICON 장비 보유 시에만"),
    "VR": ("7-3", "DM VR", "DMW-008-0300", 20000, 26000,
           "가상 작업장을 VR(Oculus Rift·HTC Vive)로 확인", "HUMAN 필수"),
    "RRS": ("8", "DM RRS", "DMW-009-00**", 20000, 26000,
            "로봇 제조사 RCS 모듈 연동으로 정확한 경로·사이클타임 계산",
            "지원 컨트롤러 2종뿐(현대 Hi5·FANUC RJ3). 로봇 RCS 모듈은 미포함(로봇사 별도 구매)"),
    "PLC": ("9", "DM PLC SIMULATION", "DMW-010-0000", 44200, 57460,
            "PLC 프로그램을 가상 설비와 연동해 공정 로직·I/O 매핑·인터록·이상 시나리오 검증(가상 시운전)",
            "PLC→DMWorks Read + 핸드셰이크만(Write 제어 불가). 이기종 PLC 동시 시뮬레이션 경험 2종까지 → 셀별 PLC 메이커 통일"),
    "PID": ("10", "DM PLUG-IN for Developer", "DMW-011-0000", 42000, 54600,
            "Visual Studio 기반 API로 DMWorks 기능 직접 개발 (AAS 출력·OpenUSD 물성 전달·OCS/VLA 연동)",
            "VLA 실증·AAS 환류·충돌/병목 리포트는 기성 기능 아님 → 플러그인 커스텀"),
    "PIU": ("11", "DM PLUG-IN for User", "DMW-012-0000", 14000, 18200,
            "Developer로 만든 플러그인을 다른 DMWorks에서 실행", "개발은 1곳, 실행 좌석에는 User로 충분"),
}
USE_ORDER = ["BASE", "CADI", "CADE", "OLP", "RRS", "PC", "PAN", "MP", "HUM", "VR", "MVN", "VICON", "PLC", "PID", "PIU"]

# ------------------------------------------------------------------ 존별 해야 할 일 → 기능
ZONES = [
    {"id": "A-1-4", "slug": "z14", "name": "유연제조 OCS 시뮬레이션 Cell", "purpose": "공정 최적화 + 가상 시운전",
     "tasks": [
         ("삼진산업 도어·차체 혼류 공정 DT 모델링, 설비 배치·로봇 경로 사전 검증", "BASE · CAD IMPORT"),
         ("다공정 라인·AMR 물류·작업 스케줄 최적화(UPH·가동률·AMR 대수)", "MULTIPLE PROCESS"),
         ("2차년도 실물 셀(A-1-3) 투입 전 PLC 제어로직·이상 상황 가상 시운전(HIL)", "PLC SIMULATION"),
         ("용접·핸들링 산업용 로봇 오프라인 프로그램 생성·사이클타임 산출", "OLP (컨트롤러별)"),
         ("작업자–로봇 협업 구간 안전거리·동선·작업 자세 검증, VR 리뷰", "HUMAN · VR"),
         ("AAS 출력·OpenUSD 물성 전달·OCS 연동 플러그인 개발(3존 공통 개발 거점)", "PLUG-IN Developer"),
     ],
     "items": [  # key, 수량, 구분, 이 존에서 쓰는 이유, 이전 수량(10/7)
         ("BASE", 2, "필수", "DT 모니터링 1 + 시뮬레이션 1 (업체: 1카피로는 운영 곤란). STEP Import 포함", 2),
         ("CADI", 1, "선택", "수요기업(삼진산업) 차체·도어 원본 CAD 포맷(예: CATIA V5) 확인 후 1종 추가", 0),
         ("MP", 2, "필수", "혼류 라인·AMR 물류 시뮬레이션. 모니터링 DT에서도 라인 단위 재생 필요", 2),
         ("PLC", 1, "필수", "가상 시운전은 시뮬레이션 좌석 1곳에서 수행", 1),
         ("OLP", 2, "조건부", "산업용 로봇 메이커 2종 가정(예: 현대 Hi6·FANUC R30iB). 로봇 기종 확정 후 컨트롤러 선택", 2),
         ("RRS", 0, "조건부", "현대 Hi5·FANUC RJ3 컨트롤러일 때만 1종당 20,000 추가", 0),
         ("HUM", 1, "필수", "협업 구간 작업자 모델·자세 분석", 1),
         ("VR", 1, "선택", "몰입형 배치·안전거리 리뷰(VR 헤드셋 별도)", 1),
         ("PID", 1, "필수", "3존 공통 플러그인 개발 거점(AAS·OpenUSD·OCS 연동)", 1),
         ("PIU", 1, "필수", "모니터링 DT 좌석에서 플러그인 실행", 0),
     ]},
    {"id": "A-2-5", "slug": "z25", "name": "적응가공 OCS 시뮬레이션 Cell", "purpose": "데이터 + 강화학습",
     "tasks": [
         ("가공기·로봇·팔레트·AMR 경로·간섭 가상검증", "BASE"),
         ("공정 배정·팔레트·AMR 물류 흐름 최적화", "MULTIPLE PROCESS"),
         ("머신텐딩 로봇 셀 제어로직·가공기 인터록(핸드셰이크) 사전검증", "PLC SIMULATION"),
         ("로딩·언로딩 로봇 오프라인 프로그램. 가공기 경로→로봇 경로 변환(DMWorks 보유 기능)", "OLP (컨트롤러별)"),
         ("시뮬레이션 결과를 AAS·강화학습 환경(Omniverse)으로 환류", "PLUG-IN User"),
         ("※ CNC 가공 경로·NC 검증은 DMWorks에 CAM이 없어 별도 SW(NC 검증)로 수행", "—"),
     ],
     "items": [
         ("BASE", 2, "필수", "DT 모니터링 1 + 시뮬레이션 1. STEP Import 포함(가공기·지그 STEP)", 2),
         ("MP", 1, "필수", "팔레트·AMR 물류는 시뮬레이션 좌석에서", 1),
         ("PLC", 1, "필수", "로봇 셀 제어로직·가공기 인터록 검증", 1),
         ("OLP", 1, "조건부", "머신텐딩 로봇이 산업용이면 1종. 협동로봇이면 '요청 시 지원'(가격 미정)", 1),
         ("PIU", 2, "필수", "A-1-4에서 개발한 AAS·환류 플러그인을 두 좌석에서 실행", 0),
         ("PID", 0, "—", "개발은 A-1-4 1곳으로 통합(이전 구성의 Developer 1카피 제외)", 1),
     ]},
    {"id": "A-4-5", "slug": "z45", "name": "AI정밀검사 OCS 시뮬레이션 Cell", "purpose": "DT(역설계) + 품질 운영",
     "tasks": [
         ("3D 스캔으로 검사 셀·수요기업 현장을 가상 작업장으로 구축", "POINT CLOUD"),
         ("스캔 지점 파노라마로 현장 원격 리뷰", "PANORAMA (선택)"),
         ("검사·로봇·AMR 공정 시뮬레이션, 검사 대기·흐름 분석", "BASE · MULTIPLE PROCESS"),
         ("QMS 판정→재검사→리워크 폐루프와 검사 결과 데이터 연계", "PLUG-IN User"),
         ("※ 부품 계측용 로봇 스캐닝 경로는 별도 SW(AIMS)·PolyWorks 연계 — 가격표 외, 별도 견적", "—"),
         ("※ PLC 가상 시운전은 이 존 목적(품질 운영)에 해당 없음", "—"),
     ],
     "items": [
         ("BASE", 1, "필수", "검사 셀 레이아웃·공정 시뮬레이션. 운영 모니터링은 QMS가 담당", 1),
         ("MP", 1, "필수", "검사 라인·AMR 물류·대기 분석", 1),
         ("PC", 1, "필수", "3D 스캐너(핸드헬드·대형) 점군을 가상 작업장으로", 1),
         ("PAN", 1, "선택", "POINT CLOUD와 짝. 수요기업 현장 원격 리뷰 필요 시", 0),
         ("PIU", 1, "필수", "QMS·AAS 연동 플러그인 실행", 0),
         ("PID", 0, "—", "개발은 A-1-4로 통합(이전 구성의 Developer 1카피 제외)", 1),
     ]},
    {"id": "A-3", "slug": "z3", "name": "정밀조립존 (OCS 셀 없음 · DT 워크스테이션 1대)", "purpose": "셀 배치·물류·상태머신 검증",
     "tasks": [
         ("5개 셀 레이아웃·협동로봇 10대/셀 작업영역 간섭 검증", "BASE"),
         ("셀 간 AMR 물류(셀당 4대)·대수 산정, 셀 재배정 흐름", "MULTIPLE PROCESS"),
         ("셀 상태머신(IDLE~SAFE-STOP)·셀 PLC 시퀀스 가상검증", "PLC SIMULATION"),
         ("AAS 출력 플러그인 실행(존 Local Server AAS Repository 연계)", "PLUG-IN User"),
         ("※ 협동로봇(국산)은 OLP 목록에 없어 제외. 로봇 동작은 VLA·티칭과 Isaac Sim 학습 DT로 처리", "—"),
     ],
     "items": [
         ("BASE", 1, "필수", "DT 워크스테이션(DWS) 1대용. STEP Import 포함", 1),
         ("MP", 1, "필수", "셀 간 AMR 물류·배치", 1),
         ("PLC", 1, "필수", "셀 상태머신·PLC 시퀀스 검증", 1),
         ("PIU", 1, "필수", "AAS 출력 플러그인 실행", 0),
     ]},
]


def k(n):
    return f"{n:,.0f}"


def zone_total(z):
    return sum(OPT[key][3] * q for key, q, *_ in z["items"])


GRAND = sum(zone_total(z) for z in ZONES)

CSS = re.search(r"<style>.*?</style>", bp.page(), re.S).group(0)
EXTRA = """<style>
.mast p{max-width:none}
.mast{background:none;border-radius:0;max-width:1240px;margin:16px auto 0;padding-inline:20px;box-sizing:border-box}
.mast .wrap{background:var(--navy);border-radius:6px;max-width:none;padding-inline:24px}
table.bom th.r{text-align:right}
.tag{display:inline-block;font:600 11px var(--mono);padding:1px 7px;border-radius:3px;white-space:nowrap}
.tag.req{background:var(--teal);color:#fff} .tag.opt{background:var(--grp);color:var(--navy2);border:1px solid var(--rule)}
.tag.cond{background:#FFF1E2;color:#9A4A00;border:1px solid #F0C08A} .tag.na{color:var(--muted)}
td.zero{color:var(--muted)}
td.dz,th.dz{text-align:center;white-space:nowrap} table.bom td a{white-space:nowrap}
.dot{color:var(--teal);font-weight:900}
.chg{font:500 11px var(--mono);color:var(--muted)}
.chg.up{color:#B45309} .chg.down{color:var(--teal)}
.keytbl th[scope=row],.issuetbl th[scope=row]{white-space:nowrap;color:var(--navy2);font-weight:700;background:var(--grp);text-align:left}
.keytbl td,.issuetbl td{font-size:13px;line-height:1.55}
</style>"""


def tag(kind):
    cls = {"필수": "req", "선택": "opt", "조건부": "cond"}.get(kind, "na")
    return f'<span class="tag {cls}">{E(kind)}</span>'


def option_table():
    rows = []
    for key in USE_ORDER:
        no, name, code, nl, fl, func, note = OPT[key]
        use = "".join('<td class="dz"><span class="dot">●</span></td>' if any(i[0] == key and i[1] > 0 for i in z["items"]) else '<td class="dz">–</td>' for z in ZONES)
        rows.append(f'<tr><td class="sym">{E(no)}</td><td class="nm">{E(name)}<br><span class="chg">{E(code)}</span></td>'
                    f'<td class="num">{k(nl)}</td><td class="num">{k(fl)}</td><td>{E(func)}</td><td class="note">{E(note)}</td>{use}</tr>')
    head = "".join(f"<th class='dz'>{E(z['id'])}</th>" for z in ZONES)
    return ('<div class="tbl-wrap"><table class="bom wide mx"><thead><tr><th>No</th><th>옵션</th><th class="r">Node-Lock</th><th class="r">Floating</th>'
            f'<th>기능</th><th>9/30 확인·제약</th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def task_table(z):
    body = "".join(f"<tr><td>{E(t)}</td><td class='nm'>{E(o)}</td></tr>" for t, o in z["tasks"])
    return f'<div class="tbl-wrap"><table class="bom"><thead><tr><th>이 존에서 해야 할 일</th><th>DMWorks 기능·옵션</th></tr></thead><tbody>{body}</tbody></table></div>'


def bom(z):
    rows, tot = [], 0
    for key, q, kind, why, prev in z["items"]:
        no, name, code, nl, *_ = OPT[key]
        amt = nl * q
        tot += amt
        d = q - prev
        chg = "" if d == 0 else (f'<span class="chg up">+{d}</span>' if d > 0 else f'<span class="chg down">{d}</span>')
        z_ = " zero" if q == 0 else ""
        rows.append(f'<tr><td class="nm">{E(name)}<br><span class="chg">{E(code)}</span></td><td>{tag(kind)}</td>'
                    f'<td class="q{z_}"><b>{q}</b></td><td class="q">{prev} {chg}</td><td class="num{z_}">{k(nl)}</td><td class="num{z_}">{k(amt)}</td>'
                    f'<td class="num{z_}">{k(amt * DISC)}</td><td>{E(why)}</td></tr>')
    foot = (f'<tr class="tot strong"><th colspan="5">합계</th><td class="num">{k(tot)}</td><td class="num">{k(tot * DISC)}</td>'
            f'<td>정가 / 60% 할인 가정 추정가</td></tr>')
    return ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>옵션</th><th>구분</th><th style="text-align:center">수량</th>'
            '<th style="text-align:center">이전(10/7)</th><th class="r">정가 단가</th><th class="r">정가 금액</th><th class="r">추정가(×40%)</th><th>이 존에서 쓰는 이유</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody><tfoot>{foot}</tfoot></table></div>')


def summary_table():
    rows = []
    for z in ZONES:
        t = zone_total(z)
        names = " · ".join(f"{OPT[key][1].replace('DM ', '').replace('DMWORKS ', '')}{'×' + str(q) if q > 1 else ''}"
                           for key, q, *_ in z["items"] if q > 0)
        rows.append(f'<tr><td><a href="#{z["slug"]}">{E(z["id"])}</a></td><td class="nm">{E(z["name"])}</td><td>{E(z["purpose"])}</td>'
                    f'<td>{E(names)}</td><td class="num">{k(t)}</td><td class="num"><b>{k(t * DISC)}</b></td></tr>')
    rows.append(f'<tr class="tot strong"><th colspan="4">합계 (4개 존)</th><td class="num">{k(GRAND)}</td><td class="num">{k(GRAND * DISC)}</td></tr>')
    return ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>존</th><th>구분</th><th>목적</th><th>옵션 구성</th>'
            '<th class="r">정가 합계</th><th class="r">추정가(×40%)</th></tr></thead>' + f'<tbody>{"".join(rows)}</tbody></table></div>')


def key_table():
    pid_prev = 3 * OPT["PID"][3]
    pid_now = OPT["PID"][3] + 4 * OPT["PIU"][3]
    rows = [
        ("견적 기준", f"이지로보틱스 DMWorks 3.0 정가표(2026.01, Node-Lock) × 40%. 10/6 제안이 60% 할인가였음. 단위 천원, VAT 별도", "가격표 · 10/6 의사결정"),
        ("4개 존 합계", f"정가 {k(GRAND)}천원 → 추정 {k(GRAND * DISC)}천원. 유지보수는 1년 무상 후 매년 구매가의 18%(협의 시 15%) ≈ {k(GRAND * DISC * 0.18)}천원/년", "가격표 주석 · 9/30 Q&A"),
        ("존별 차별화", "유연제조는 가상 시운전·작업자·OLP, 적응가공은 PLC·OLP·환류, AI정밀검사는 POINT CLOUD·PANORAMA(PLC 제외), 정밀조립은 BASE·MULTIPLE PROCESS·PLC 1좌석", "존별 목적(10/6)"),
        ("플러그인 개발 통합", f"Developer를 존마다 사던 구성(3카피, 정가 {k(pid_prev)})을 개발 거점 1카피 + 실행용 User 5카피(정가 {k(pid_now + OPT['PIU'][3])})로 바꿈. AAS 출력·OpenUSD·OCS 연동 코드를 한 번 만들어 모든 존에서 실행", "가격표 옵션 10·11"),
        ("협동로봇 OLP 공백", "OLP·RRS 목록에 협동로봇·휴머노이드 컨트롤러가 없음. 정밀조립(협동로봇 50대)은 OLP를 넣지 않았고, 적응가공 머신텐딩이 협동로봇이면 '요청 시 지원' 가격을 따로 받아야 함", "가격표 · 9/30 Q&A"),
        ("이전 표와 차이", "10/7 OCS 셀 3종 표 대비 PLUG-IN Developer 3→1, User +5, CAD IMPORT·PANORAMA 선택 추가, RRS를 OLP에서 분리(조건부), 정밀조립에 User 추가", "이전 산출물(git a54f74f)"),
    ]
    body = "".join(f'<tr><th scope="row">{E(a)}</th><td>{E(b)}</td><td class="note">{E(c)}</td></tr>' for a, b, c in rows)
    return f'<div class="tbl-wrap"><table class="bom keytbl"><thead><tr><th>항목</th><th>내용</th><th>근거</th></tr></thead><tbody>{body}</tbody></table></div>'


ISSUES = [
    ("견적", "할인율·범위", "10/6 제안 2억 9,500만 원(60% 할인)이 존당인지 3존 합계인지, 어떤 옵션이 들어갔는지 기록 없음. '옵션 포함 시 존당 약 5억' 발언도 있음", "추정가가 실제 견적과 크게 다를 수 있음", "옵션 목록을 붙여 존별 재견적 요청(10/7 협의 결과 확인)"),
    ("로봇", "협동로봇 OLP", "OLP·RRS 목록에 협동로봇 컨트롤러 없음. 두산·레인보우는 '요청 시 지원'", "정밀조립·적응가공 로봇 프로그램 검증 범위 불확실", "로봇 기종 확정 후 지원 여부·가격 서면 확인"),
    ("로봇", "OLP 컨트롤러", "유연제조 OLP 2종은 메이커 미정 가정", "컨트롤러가 아크 용접·도장이면 단가 28,000~33,000", "산업용 로봇 메이커·용도(스폿·핸들링·실링) 확정"),
    ("연동", "OpenUSD·AAS", "USD 내보내기는 지오메트리만, AAS 출력은 고객 정의 포맷 방식. 커스텀 개발비는 가격표 외", "플러그인 개발 공수·비용 추가", "캠틱이 OpenUSD 구조·AAS 규격 정의 후 개발 범위·비용 제안 요청"),
    ("검사", "로봇 스캐닝 SW", "부품 계측 경로는 AIMS(별도 SW)·PolyWorks 연계 구조", "가격표 외 비용, PolyWorks는 외산", "AIMS 견적·국산 대체 가능 여부 확인"),
    ("PLC", "PLC 메이커", "이기종 PLC 동시 시뮬레이션 경험 2종까지", "셀마다 PLC가 다르면 가상 시운전 통합 곤란", "존·셀별 PLC 메이커 1사 지정(발주 사양 명시)"),
    ("라이선스", "Node-Lock vs Floating", "Floating은 정가 1.3배, 구매 카피 수 = 동시 사용자 수", "좌석 공유가 많으면 Floating이 유리할 수 있음", "존별 실제 사용자 수 확정 후 혼합 구성 검토"),
    ("교육·SI", "교육·컨설팅", "기본 교육 3일 + 추가 1회, 시뮬레이션 수행·결과 영상 제공 가능. 비용 미제시", "SI·교육비 별도", "재견적 시 교육·SI 범위 포함 요청"),
]


def issues_table():
    body = "".join(f'<tr><td class="u">{E(a)}</td><th scope="row">{E(b)}</th><td>{E(c)}</td><td>{E(d)}</td><td>{E(e)}</td></tr>' for a, b, c, d, e in ISSUES)
    return ('<div class="tbl-wrap"><table class="bom issuetbl"><thead><tr><th>구분</th><th>쟁점</th><th>현재 상황</th><th>영향</th><th>다음 조치</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


REFS = [
    ("S1", "견적", "DMWorks 3.0 Solution List Price (이지로보틱스) — 옵션 11종·서브옵션·CAD/OLP/RRS 상세 옵션표, 유지보수 18%", "2026-01", "OneDrive Workspace / Customers / 이지로보틱스"),
    ("M1", "회의록", "이지로보틱스 DMWorks 방문 Q&A — 기능 충족 여부 26개 항목, USD·PLC·AAS·OLP 제약, 라이선스·교육", "2026-09-30", "OneDrive Workspace / MoM / 2026-09-30"),
    ("M2", "회의록", "국산 프로세스 시뮬레이션(DMWorks) 세미나 — 학습(Omniverse)·검증(DMWorks) 역할 분리", "2026-09-17", "OneDrive Workspace / MoM / 2026-09-17"),
    ("W1", "llm-wiki 결정", "OCS 시뮬레이션 셀 존별 목적·구성 문서화 후 견적 확정 — 제안 2억 9,500만 원(60% 할인), 옵션 포함 시 존당 약 5억", "2026-10-06", "llm-wiki decisions"),
    ("W2", "llm-wiki 결정", "DMWorks 도입 조건 — AAS 규격 캠틱 정의·PLC Read·핸드셰이크·셀별 PLC 통일·라이선스 후속 제안", "2026-09-30", "llm-wiki decisions"),
    ("P1", "이전 산출물", "OCS 셀 3종 장비 목록(존별 DMWorks 모듈 표) — 삭제 전 버전", "2026-10-07", "github.com/theuniversepark/micro-cell 커밋 a54f74f"),
]


def refs_table():
    body = "".join(f'<tr><td class="sym">[{a}]</td><td class="u">{E(b)}</td><td>{E(c)}</td><td class="u">{E(d)}</td><td class="note">{E(e)}</td></tr>' for a, b, c, d, e in REFS)
    return ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>표기</th><th>구분</th><th>문서·내용</th><th>일자</th><th>위치</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


def page():
    zsecs = "".join(f'''
<section id="{z["slug"]}">
  <p class="eyebrow">{E(z["id"])} · {E(z["purpose"])}</p>
  <h2>{E(z["name"])}</h2>
  <h3>해야 할 일과 필요한 기능</h3>
  {task_table(z)}
  <h3>옵션 구성 <span class="chg">(단위 천원 · VAT 별도 · 정가 = Node-Lock)</span></h3>
  {bom(z)}
</section>''' for z in ZONES)
    return f'''<title>DMWorks 존별 옵션 구성</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=IBM+Plex+Mono:wght@400;500&display=swap">
{CSS}{EXTRA}
<header class="mast"><div class="wrap">
  <p class="eyebrow">총괄5-세부1 기술실증 테스트베드 · 이지로보틱스 DMWorks 3.0 · 정가표(2026.01) 기반 · 2026.10.08 작성 · 설계 추정본</p>
  <h1>DMWorks 존별 옵션 구성</h1>
</div></header>
<nav class="toc" aria-label="바로가기"><div class="wrap">
  <a href="#sum">요약</a><a href="#opt">옵션 기능</a>{"".join(f'<a href="#{z["slug"]}">{z["id"]}</a>' for z in ZONES)}<a href="#issues">확인 필요</a><a href="#refs">근거</a>
</div></nav>
<main class="wrap">
<section id="sum" style="margin-top:8px">
  <p class="eyebrow">결론 및 핵심 요약 (Executive Summary)</p>
  <h2>4개 존 · 정가 {k(GRAND)}천원 → 추정 {k(GRAND * DISC)}천원</h2>
  {key_table()}
  <h3>존별 합계</h3>
  {summary_table()}
</section>
<section id="opt">
  <p class="eyebrow">1. 옵션 기능</p>
  <h2>DMWorks 3.0 옵션별 기능·가격·제약</h2>
  <p class="note-box">정가(천원, VAT 별도). [S1] 가격표 기준이며 9/30 Q&A [M1]에서 확인한 제약을 함께 적음. 오른쪽 열은 이 구성에서 해당 옵션을 쓰는 존(●).</p>
  {option_table()}
</section>
{zsecs}
<section id="issues">
  <p class="eyebrow">확인 필요 사항</p>
  <h2>재견적 전에 정리할 쟁점</h2>
  {issues_table()}
</section>
<section id="refs">
  <p class="eyebrow">근거 문서</p>
  <h2>참조</h2>
  {refs_table()}
  <p class="note-box">구분 표기: <b>필수</b> 존 목적상 꼭 필요 · <b>선택</b> 있으면 좋으나 빼도 목적 달성 · <b>조건부</b> 로봇 기종·CAD 포맷 등 확정에 따라 결정. '이전(10/7)'은 삭제 전 OCS 셀 3종 표의 수량이며, 정밀조립은 OCS Cell 페이지의 DMWorks 1카피(BASE+MULTIPLE PROCESS+PLC) 기준.</p>
</section>
</main>
'''


if __name__ == "__main__":
    open(out("dmworks_zones.html"), "w", encoding="utf-8").write(page())
    print("ok", k(GRAND), k(GRAND * DISC))
