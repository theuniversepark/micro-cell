"""정밀조립존 5개 셀 배치도·구성품 페이지 생성기 → precision_zone.html"""
import html
from cells_data import ZONE, CELLS, COMMON
from privacy import out as out_path

E = html.escape
U = 100  # 1 m = 100 drawing units


def fmt(n):
    return f"{n:,.0f}"


def eok(n):  # 만원 → 억원
    return f"{n / 10000:,.2f}"


def fit_font(text, w_units, base, minimum=11):
    n = max(len(text), 1)
    return max(minimum, min(base, (w_units - 8) / (n * 0.92)))


# ------------------------------------------------------------------ cell svg
def cell_svg(c):
    W, H = c["W"] * U, c["H"] * U
    m = 90
    vb = f"{-m} {-m} {W + 2 * m} {H + 2 * m + 70}"
    o = [f'<svg class="plan" viewBox="{vb}" style="max-width:{c["W"] * 64 + 120:.0f}px" role="img" '
         f'aria-label="{E(c["id"])} 셀 개념 배치도">']
    o.append('<defs><marker id="ar-' + c["slug"] + '" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
             '<path d="M0,0 L10,5 L0,10 z" class="ar"/></marker></defs>')
    o.append(f'<rect x="0" y="0" width="{W}" height="{H}" class="fence"/>')
    layers = {"area": [], "path": [], "eq": [], "robot": [], "top": [], "door": [], "label": []}
    for el in c["layout"]:
        k = el[0]
        if k == "area":
            _, x, y, w, h, lab = el
            layers["area"].append(
                f'<rect x="{x * U}" y="{y * U}" width="{w * U}" height="{h * U}" class="area"/>')
            layers["label"].append(f'<text x="{x * U + 10}" y="{y * U - 8}" class="area-t">{E(lab)}</text>')
        elif k == "path":
            _, pts, kind = el
            d = " ".join(f"{x * U},{y * U}" for x, y in pts)
            layers["path"].append(f'<polyline points="{d}" class="lane {kind}" marker-end="url(#ar-{c["slug"]})"/>')
        elif k == "eq":
            _, x, y, w, h, lab = el
            fs = fit_font(lab, w * U, 21)
            layers["eq"].append(
                f'<rect x="{x * U}" y="{y * U}" width="{w * U}" height="{h * U}" rx="4" class="eq"/>'
                f'<text x="{(x + w / 2) * U}" y="{(y + h / 2) * U + fs * 0.35}" class="eq-t" font-size="{fs:.1f}">{E(lab)}</text>')
        elif k == "robot":
            _, x, y, r, lab = el
            layers["robot"].append(
                f'<circle cx="{x * U}" cy="{y * U}" r="{r * U}" class="reach"/>'
                f'<circle cx="{x * U}" cy="{y * U}" r="30" class="rob"/>'
                f'<text x="{x * U}" y="{y * U + 8}" class="rob-t">{E(lab)}</text>')
        elif k == "hum":
            _, x, y, lab = el
            layers["top"].append(
                f'<rect x="{x * U - 32}" y="{y * U - 32}" width="64" height="64" rx="18" class="hum"/>'
                f'<text x="{x * U}" y="{y * U + 8}" class="rob-t">{E(lab)}</text>')
        elif k == "amr":
            _, x, y, lab = el
            layers["top"].append(
                f'<rect x="{x * U - 45}" y="{y * U - 28}" width="90" height="56" rx="8" class="amr"/>'
                f'<text x="{x * U}" y="{y * U + 6}" class="amr-t">{E(lab)}</text>')
        elif k == "cam":
            _, x, y = el
            X, Y = x * U, y * U
            layers["top"].append(f'<path d="M{X},{Y - 14} L{X + 13},{Y + 10} L{X - 13},{Y + 10} z" class="cam"/>')
        elif k == "door":
            _, x1, x2, lab = el
            if "부스" in lab:
                continue
            layers["door"].append(
                f'<line x1="{x1 * U}" y1="{H}" x2="{x2 * U}" y2="{H}" class="gap"/>'
                f'<line x1="{x1 * U}" y1="{H - 12}" x2="{x1 * U}" y2="{H + 12}" class="jamb"/>'
                f'<line x1="{x2 * U}" y1="{H - 12}" x2="{x2 * U}" y2="{H + 12}" class="jamb"/>'
                f'<text x="{(x1 + x2) / 2 * U}" y="{H + 40}" class="door-t">▲ {E(lab)}</text>')
    for k in ("area", "path", "eq", "robot", "top", "door", "label"):
        o.extend(layers[k])
    # dimensions
    o.append(f'<line x1="0" y1="-45" x2="{W}" y2="-45" class="dim"/>'
             f'<line x1="0" y1="-58" x2="0" y2="-32" class="dim"/><line x1="{W}" y1="-58" x2="{W}" y2="-32" class="dim"/>'
             f'<text x="{W / 2}" y="-56" class="dim-t">{c["W"]:.1f} m</text>')
    o.append(f'<line x1="-45" y1="0" x2="-45" y2="{H}" class="dim"/>'
             f'<line x1="-58" y1="0" x2="-32" y2="0" class="dim"/><line x1="-58" y1="{H}" x2="-32" y2="{H}" class="dim"/>'
             f'<text x="-56" y="{H / 2}" class="dim-t" transform="rotate(-90 -56 {H / 2})">{c["H"]:.1f} m</text>')
    # scale bar + aisle note
    sy = H + 92
    o.append(f'<g class="scale"><rect x="0" y="{sy}" width="100" height="10" class="sb1"/>'
             f'<rect x="100" y="{sy}" width="100" height="10" class="sb2"/>'
             f'<rect x="200" y="{sy}" width="100" height="10" class="sb1"/>'
             f'<text x="0" y="{sy - 8}" class="sc-t">0</text><text x="300" y="{sy - 8}" class="sc-t">3 m</text></g>')
    o.append(f'<text x="{W}" y="{sy + 8}" class="sc-t" text-anchor="end">아래쪽 = 존 AMR 주통로 측</text>')
    o.append("</svg>")
    return "".join(o)


# ------------------------------------------------------------------ zone svg
def zone_svg():
    W, H = ZONE["W"] * U, ZONE["H"] * U
    m = 260
    o = [f'<svg class="plan zone" viewBox="{-m} {-m} {W + 2 * m} {H + 2 * m}" role="img" aria-label="정밀조립존 전체 배치도">']
    o.append('<defs><marker id="ar-z" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">'
             '<path d="M0,0 L10,5 L0,10 z" class="ar"/></marker></defs>')
    o.append(f'<rect x="0" y="0" width="{W}" height="{H}" class="bldg"/>')
    # aisle
    o.append(f'<rect x="50" y="1320" width="{W - 100}" height="320" class="aisle"/>')
    o.append(f'<line x1="200" y1="1430" x2="{W - 300}" y2="1430" class="lane main" marker-end="url(#ar-z)"/>')
    o.append(f'<line x1="{W - 300}" y1="1530" x2="200" y2="1530" class="lane main" marker-end="url(#ar-z)"/>')
    o.append(f'<text x="{W / 2 - 600}" y="1497" class="aisle-t">AMR 주통로 3.2 m (양방향) · 보행 구획 1.0 m 병행</text>')
    for b in ZONE["blocks"]:
        x, y, w, h, kind, title, sub = b
        X, Y, Wd, Hd = x * U, y * U, w * U, h * U
        slug = next((c["slug"] for c in CELLS if c["id"] == title), None)
        open_a = f'<a href="#{slug}" class="cell-link">' if slug else ""
        close_a = "</a>" if slug else ""
        o.append(open_a)
        o.append(f'<rect x="{X}" y="{Y}" width="{Wd}" height="{Hd}" class="blk {kind}"/>')
        tfs = 120 if kind == "cell" else min(78, (Wd - 30) / (len(title) * 0.95))
        o.append(f'<text x="{X + Wd / 2}" y="{Y + Hd / 2 - (40 if sub else -20)}" class="blk-t {kind}" font-size="{tfs:.0f}">{E(title)}</text>')
        lines = [s for s in sub.split("|") if s]
        for i, ln in enumerate(lines):
            fs = min(62 if kind == "cell" else 46, (Wd - 40) / (len(ln) * 0.95))
            o.append(f'<text x="{X + Wd / 2}" y="{Y + Hd / 2 + 60 + i * fs * 1.35}" class="blk-s" font-size="{fs:.0f}">{E(ln)}</text>')
        o.append(close_a)
        if kind == "cell":
            dy = Y + Hd if y < 13 else Y
            cx = X + Wd * (0.78 if slug == "c35" or slug == "c34" else 0.6)
            o.append(f'<rect x="{cx - 60}" y="{dy - 14}" width="120" height="28" class="door-z"/>')
            px = X + Wd * 0.18
            o.append(f'<rect x="{px - 45}" y="{dy - 14}" width="90" height="28" class="door-p"/>')
    # walkway labels
    for x, y in ((1600, 700), (3400, 700), (1230, 2280)):
        o.append(f'<text x="{x}" y="{y}" class="walk-t" transform="rotate(-90 {x} {y})">보행 1.0 m</text>')
    # dimensions
    o.append(f'<line x1="0" y1="-110" x2="{W}" y2="-110" class="dim"/>'
             f'<line x1="0" y1="-150" x2="0" y2="-70" class="dim"/><line x1="{W}" y1="-150" x2="{W}" y2="-70" class="dim"/>'
             f'<text x="{W / 2}" y="-140" class="dim-t z">46.0 m</text>')
    o.append(f'<line x1="-110" y1="0" x2="-110" y2="{H}" class="dim"/>'
             f'<line x1="-150" y1="0" x2="-70" y2="0" class="dim"/><line x1="-150" y1="{H}" x2="-70" y2="{H}" class="dim"/>'
             f'<text x="-140" y="{H / 2}" class="dim-t z" transform="rotate(-90 -140 {H / 2})">29.6 m</text>')
    sy = H + 150
    o.append(f'<rect x="0" y="{sy}" width="500" height="36" class="sb1"/><rect x="500" y="{sy}" width="500" height="36" class="sb2"/>'
             f'<text x="0" y="{sy - 20}" class="sc-t z">0</text><text x="1000" y="{sy - 20}" class="sc-t z">10 m</text>')
    o.append(f'<text x="{W}" y="{sy + 30}" class="sc-t z" text-anchor="end">전북대 창조2관 2층 · 1,361.3 ㎡ (46.0 × 29.6 m 환산)</text>')
    o.append("</svg>")
    return "".join(o)


# ------------------------------------------------------------------ tables
GROUP_ORDER = ["로봇", "이송", "공정설비", "비전·센서", "그리퍼·툴", "제어·엣지", "안전·인프라", "SW", "서비스"]
GROUP_LABEL = {"로봇": "로봇", "이송": "이송·AMR·지그", "공정설비": "공정 설비", "비전·센서": "비전·센서",
               "그리퍼·툴": "그리퍼·툴·부품공급", "제어·엣지": "제어·PLC·엣지", "안전·인프라": "안전·인프라",
               "SW": "SW 구성품", "서비스": "SI·설치·교육"}


def k(n):  # 만원 → 천원 표시
    return fmt(n * 10)


def bom_table(items, budget=None, tid="", kunit=False):
    m = k if kunit else fmt
    rows = []
    hw = sw = sv = 0
    for g in GROUP_ORDER:
        its = [i for i in items if i[0] == g]
        if not its:
            continue
        sub = sum(i[6] * i[8] for i in its)
        if g == "SW":
            sw += sub
        elif g == "서비스":
            sv += sub
        else:
            hw += sub
        cls = "sw" if g == "SW" else ("sv" if g == "서비스" else "hw")
        rows.append(f'<tr class="grp {cls}"><th colspan="8" scope="rowgroup">{E(GROUP_LABEL[g])}</th>'
                    f'<td class="num">{m(sub)}</td><td></td></tr>')
        for (_, sym, name, spec, func, use, q, unit, price, note) in its:
            rows.append(
                f'<tr><td class="sym">{E(sym)}</td><td class="nm">{E(name)}</td><td class="spec">{E(spec)}</td>'
                f'<td>{E(func)}</td><td>{E(use)}</td><td class="num">{q}</td><td class="u">{E(unit)}</td>'
                f'<td class="num">{m(price)}</td><td class="num">{m(q * price)}</td>'
                f'<td class="note">{E(note)}</td></tr>')
    total = hw + sw + sv
    foot = [f'<tr class="tot"><th colspan="8">HW 소계 / SW 소계 / SI</th><td class="num" colspan="2">{m(hw)} / {m(sw)} / {m(sv)}</td></tr>',
            f'<tr class="tot strong"><th colspan="8">추정 합계</th><td class="num" colspan="2">{m(total) + (' 천원' if kunit else ' 만원 (' + eok(total) + '억)')}</td></tr>']
    if budget:
        rest = budget - total
        foot.append(f'<tr class="tot"><th colspan="8">협약 예산 [R2] · 잔여(존 공용 분담·예비)</th>'
                    f'<td class="num" colspan="2">{m(budget)} · {"+" if rest >= 0 else "−"}{m(abs(rest))}</td></tr>')
    head = ('<thead><tr><th>기호</th><th>품목</th><th>주요 스펙</th><th>기능</th><th>용도(공정)</th>'
            '<th>수량</th><th>단위</th><th>단가</th><th>금액</th><th>비고</th></tr></thead>')
    return (f'<div class="tbl-wrap" id="{tid}"><table class="bom">{head}<tbody>{"".join(rows)}</tbody>'
            f'<tfoot>{"".join(foot)}</tfoot></table></div>'), total, hw, sw, sv


def count(items, group, unit="대"):
    return sum(i[6] for i in items if i[0] == group and i[7] == unit)


# ------------------------------------------------------------------ page
def _over():
    out = []
    for c in CELLS:
        tot = sum(i[6] * i[8] for i in c["items"])
        if tot > c["budget"]:
            out.append(round((tot / c["budget"] - 1) * 100))
    return out


OVER = _over()


def key_table(grand, total_budget):
    rows = [
        ("배치", "창조2관 2층(1,361.3㎡)에 셀 5개를 남북 2열로 두고 가운데 3.2m AMR 주통로로 연결함. 셀 출입구·AMR 포트는 모두 주통로 측에 둠", "[R1] [R3 s52]"),
        ("구축 순서", "1차년도 A-3-5(실장비, '27.4 입고) → 2차년도 A-3-2·A-3-3 → 3차년도 A-3-1·A-3-4", "[R2]"),
        ("표준 로봇·카메라", "셀마다 협동로봇 10 · AMR 4 · AMMR 양팔로봇 1 = 로봇 15대, 로봇별 카메라 3대(팔·상부·정면) = 45대", "2026-10-07 기준 변경"),
        ("공통 구성", "모든 셀에 로봇별 Edge 추론기, F/T 센서, PTP 시각동기 로거, AAS 어댑터, 셀 상태머신(IDLE/READY/RUN/HOLD/RECOVER/SAFE-STOP)을 넣어 셀–존–공장 운영 계층과 데이터 플라이휠에 바로 연결함", "[W2]"),
        ("조달 원칙", "중국산 전면 배제, 국산 우선. 국산 동급이 없는 ±0.01mm 고정밀 로봇·나노 스테이지·mN급 F/T·공초점 변위센서만 외산 예외 후보로 둠", "[W1]"),
        ("금액", f"5셀 추정 {k(grand)}천원 = 협약 {k(total_budget)}천원의 {grand / total_budget * 100:.0f}%. A-3-2만 예산 안이고 나머지 4셀은 {min(OVER)}~{max(OVER)}% 초과 → 로봇 대수 단계 도입(연차 분할)·AMMR 공동활용·예산 변경 중 선택 필요", "아래 셀별 표"),
    ]
    body = "".join(f'<tr><th scope="row">{E(a)}</th><td>{E(b)}</td><td class="note">{E(c)}</td></tr>' for a, b, c in rows)
    return ('<div class="tbl-wrap"><table class="bom keytbl"><thead><tr><th>항목</th><th>내용</th><th>근거</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


ISSUES = [
    ("사업계획", "로봇 대수 변경", "셀당 협동로봇 10대 기준. 9/17 결정(고정 3대+레일)·계획서(A-3-5 6축 5식)보다 많고 10/6 v3 시나리오(R1~R10)와는 맞음 [W1][W2]",
     "계획서 장비 대수와 달라져 사업계획 변경 대상", "변경 범위를 NIPA와 확인"),
    ("공정", "대상 품목", "10/6 결정에 따라 장비 체계를 E-Axle 기준으로 짰음 [W1]",
     "도어트림(가로 약 1.5m) 시나리오는 지그 팔레트·AMR 가반·스테이션 폭 부족", "도어트림 병행 시 지그·AMR·스테이션 폭 상향 검토"),
    ("공급", "AMR 공급 주체", "유일 자사 AMR(9/29)과 기존 협업 AMR 업체(10/6 유보) 중 미정",
     "AMR 사양·단가·셀 간 물류 인터페이스 미확정", "공급사 확정, 셀 간 물류는 KAIST B-1 존과 과제 간 협의"),
    ("예산·공간", "AMMR·면적", "AMMR 양팔로봇은 유일 범위 밖이라 별도 입찰. A-3-2(100㎡)는 로봇 15대에 비해 좁음",
     "2~3차년도 AMMR을 공동활용하면 셀당 약 150,000천원 절감 가능", "전북대 NPU 실증존 장비 공동활용 협의, A-3-2 면적 재배분 검토"),
    ("조달", "외산 예외", "고정밀 6축(±0.01mm)·헥사포드·nm 스테이지·mN F/T·공초점 변위센서는 국산 동급 없음",
     "국산 우선 원칙 예외 → 심의 지연 위험", "국산 불가 사유서 작성, NIPA 사전 협의"),
    ("시설", "층·진동", "9/15 협의에서 고중량 장비 1층 우선 배치 요구. 정밀조립존은 2층",
     "나노 스테이지 셀(A-3-3·A-3-4) 정밀도 저하 위험", "2층 바닥 진동 실측 후 제진 사양 확정"),
    ("단가", "견적 전환", "표의 단가는 2026년 국내 시장가 기준 설계 추정이며 견적이 아님",
     "자체 심의·중장위 제출 시 근거 부족", "제조사가 다른 비교견적 2건 이상으로 교체"),
]


def issues_table():
    body = "".join(f'<tr><td class="u">{E(a)}</td><th scope="row">{E(b)}</th><td>{E(c)}</td><td>{E(d)}</td><td>{E(e)}</td></tr>' for a, b, c, d, e in ISSUES)
    return ('<div class="tbl-wrap"><table class="bom issuetbl"><thead><tr><th>구분</th><th>쟁점</th><th>현재 안·상황</th><th>영향</th><th>다음 조치</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


REFS = [
    ("R1", "협약 문서", "기술실증 테스트베드 플랫폼화 추진 연구개발계획서(협약용) — 연도별 목표(2차 A-3-2·A-3-3 각 7종, 3차 A-3-1·A-3-4 각 7종), 전용공간(창조2관 2층 1,361.3㎡)",
     "2026-08-19", "OneDrive 피지컬AI 테스트베드 / 4. 사업계획서(수정)", "셀 구축 연차, 층 면적, 연차 논란"),
    ("R2", "협약 문서", "연구개발계획서 부록(협약용) — 셀별 예산(A-3-5 2,800,000·A-3-2 3,000,000·A-3-3 2,200,000·A-3-1 2,300,000·A-3-4 2,300,000천원), A-3-5 기자재 구입 및 활용계획서(주요사양 7종)",
     "2026-08-19", "OneDrive 피지컬AI 테스트베드 / 4. 사업계획서(수정)", "셀별 협약 예산, A-3-5 장비 체계"),
    ("R3", "발표자료", "테스트베드 플랫폼화 추진 선정평가 발표자료(최종제출본) — s27 정밀조립존 12,600,000천원·76대·주요장비, s32 A-3-5 대상공정, s52 셀별 면적",
     "2026-08-04", "OneDrive 피지컬AI 테스트베드 / 2. Proposal / 최종자료", "셀별 면적·존 배치"),
    ("R4", "기획서", "협업지능 피지컬AI SW 플랫폼 연구개발과제 세부 기획서(1-1) — A-3-1~A-3-5 구축장비 주요사양",
     "-", "OneDrive 피지컬AI 테스트베드", "A-3-1~A-3-4 셀 장비 사양"),
    ("W1", "llm-wiki 결정", "조립셀 기본 구성(9/17), 비전 카메라 국산 우선(9/17), 공급기업·로봇 국산 우선(9/21), 유일로보틱스 협의 조건(9/29·10/6), E-Axle 장비 체계 유지(10/6)",
     "2026-09-17 ~ 10-06", "llm-wiki decisions", "조달 원칙(국산 우선·중국산 배제), A-3-5 구성 방침, 확인 필요 사항"),
    ("W2", "llm-wiki 자료", "정밀조립 Zone 운영 시나리오 수정 v3 — Agent 위계, 셀 상태머신, 수집 데이터 항목",
     "2026-10-06", "llm-wiki sources", "셀 상태머신·에피소드 수집 구성, 로봇 대수(R1~R10)"),
    ("W3", "llm-wiki 자료", "이기종 마이크로장비 연동 협업 셀 SI 협의용 자료 — 물류 2계통, 구역 구성, 데이터 OPEN·납품 조건",
     "2026-09-29", "llm-wiki sources", "A-3-5 물류 2계통, 프로그램 원본 납품 조건"),
]


def refs_table():
    body = "".join(f'<tr><td class="sym">[{a}]</td><td class="u">{E(b)}</td><td>{E(c)}</td><td class="u">{E(d)}</td><td class="note">{E(e)}</td><td class="note">{E(f)}</td></tr>'
                   for a, b, c, d, e, f in REFS)
    return ('<div class="tbl-wrap"><table class="bom"><thead><tr><th>표기</th><th>구분</th><th>문서·내용</th><th>일자</th><th>위치</th><th>이 페이지에서 쓴 곳</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


def page():
    zone = zone_svg()
    summary_rows = []
    sections = []
    grand = 0
    for c in CELLS:
        tbl, total, hw, sw, sv = bom_table(c["items"], c["budget"], "t-" + c["slug"], kunit=True)
        grand += total
        n_rob = count(c["items"], "로봇")
        n_amr = count(c["items"], "이송")
        n_cam = sum(i[6] for i in c["items"] if i[1].startswith("CAM-"))
        n_vis = sum(i[6] for i in c["items"] if i[0] == "비전·센서" and i[7] in ("대", "세트") and not i[1].startswith("CAM-"))
        ratio = total / c["budget"] * 100
        summary_rows.append(
            f'<tr><td><a href="#{c["slug"]}">{E(c["id"])}</a></td><td class="nm">{E(c["name"])}</td><td>{E(c["year"].split(" ")[0])}</td>'
            f'<td class="num">{E(c["area"].split(" ")[0])}</td><td class="num">{n_rob}</td><td class="num">{n_amr}</td>'
            f'<td class="num">{n_cam}</td><td class="num">{n_vis}</td><td class="num">{k(c["budget"])}</td><td class="num">{k(total)}</td>'
            f'<td class="num"><span class="meter"><span style="width:{min(ratio, 100):.0f}%"></span></span>{ratio:.0f}%</td></tr>')
        concept = "".join(f"<li>{E(t)}</li>" for t in c["concept"])
        sections.append(f'''
<section class="cell" id="{c["slug"]}">
  <header class="cell-h">
    <p class="eyebrow">{E(c["id"])} · {E(c["year"])}</p>
    <h2>{E(c["name"])}</h2>
  </header>
  <dl class="facts">
    <div><dt>면적</dt><dd>{E(c["area"])}</dd></div>
    <div><dt>협약 예산</dt><dd>{k(c["budget"])}천원</dd></div>
    <div><dt>추정 합계</dt><dd>{k(total)}천원 ({total / c["budget"] * 100:.0f}%)</dd></div>
    <div><dt>로봇·이송체</dt><dd>로봇 {n_rob}대 · AMR {n_amr}대</dd></div>
  </dl>
  <div class="two">
    <div class="txt">
      <h3>대상 품목</h3><p>{E(c["target"])}</p>
      <h3>공정 흐름</h3><p class="flow">{E(c["process"])}</p>
      <h3>구성 방침</h3><ul>{concept}</ul>
    </div>
    <figure class="fig">{cell_svg(c)}<figcaption>{E(c["id"])} 개념 배치도 (설계 추정 · 실측 전) — 아래쪽이 존 주통로</figcaption></figure>
  </div>
  <h3 class="tbl-title">HW·SW 구성품 목록 <span>(단가·금액 단위: 천원, VAT 별도)</span></h3>
  {tbl}
</section>''')
    common_tbl, ctotal, *_ = bom_table(COMMON, None, "t-common", kunit=True)

    total_budget = sum(c["budget"] for c in CELLS)
    return f'''<title>정밀조립존 셀 구성 계획</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: 도면 시트 — 좌측 정렬 문서 + 도면 그림, 표는 가로 스크롤 컨테이너 */
:root{{
  --navy:#10214B; --navy2:#1B3A73; --cyan:#00C2D1; --teal:#0090A0; --amber:#E07A1F;
  --bg:#F5F7FB; --paper:#FFFFFF; --ink:#13203F; --muted:#56637F; --rule:#D5DCEA;
  --area:#EAF2FB; --eq:#FFFFFF; --eqline:#1B3A73; --robot:#1B3A73; --reachf:#1B3A73;
  --hum:#7B4FC4; --amr:#0090A0; --cam:#E07A1F; --aisle:#E4F6F8; --cellbg:#FBFCFE;
  --blk-cell:#DCE6F5; --blk-common:#E3F4F1; --blk-service:#ECEEF2; --grp:#EEF2F9;
  --font:"Malgun Gothic","Noto Sans KR","Apple SD Gothic Neo",sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{
  --bg:#0A1430; --paper:#101C3D; --ink:#E6ECF8; --muted:#9AA8C6; --rule:#26365F;
  --area:#15264D; --eq:#0F1B3A; --eqline:#7FA6E8; --robot:#5B8DE0; --reachf:#5B8DE0;
  --hum:#A585E6; --amr:#00C2D1; --cam:#F2994A; --aisle:#0E2A3A; --cellbg:#0E1936;
  --blk-cell:#1A2E5C; --blk-common:#123A3A; --blk-service:#1C2440; --grp:#16244A; --teal:#00C2D1; color-scheme:dark}}}}
:root[data-theme="dark"]{{
  --bg:#0A1430; --paper:#101C3D; --ink:#E6ECF8; --muted:#9AA8C6; --rule:#26365F;
  --area:#15264D; --eq:#0F1B3A; --eqline:#7FA6E8; --robot:#5B8DE0; --reachf:#5B8DE0;
  --hum:#A585E6; --amr:#00C2D1; --cam:#F2994A; --aisle:#0E2A3A; --cellbg:#0E1936;
  --blk-cell:#1A2E5C; --blk-common:#123A3A; --blk-service:#1C2440; --grp:#16244A; --teal:#00C2D1; color-scheme:dark}}
*{{box-sizing:border-box}}
body{{background:var(--bg);color:var(--ink);font:15px/1.65 var(--font);margin:0}}
.wrap{{max-width:1240px;margin:0 auto;padding-inline:20px;padding-block:28px 64px}}
.mast{{background:var(--navy);color:#fff;border-radius:0 0 4px 4px}}
.mast .wrap{{padding-block:30px 26px}}
.mast .eyebrow{{color:var(--cyan)}}
.mast h1{{font-size:clamp(26px,4vw,38px);font-weight:900;margin:.2em 0 .3em;letter-spacing:-.01em;text-wrap:balance}}
.mast p{{margin:0;color:#C9D4EE;max-width:none}}
.eyebrow{{font:500 12px/1.4 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--teal);margin:0}}
nav.toc{{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);border-bottom:1px solid var(--rule)}}
nav.toc .wrap{{padding-block:10px;display:flex;gap:8px;flex-wrap:wrap}}
nav.toc a{{font:500 13px var(--mono);color:var(--ink);text-decoration:none;border:1px solid var(--rule);padding:4px 10px;border-radius:999px;background:var(--paper)}}
nav.toc a:hover,nav.toc a:focus-visible{{border-color:var(--teal);color:var(--teal);outline:none}}
h2{{font-size:24px;font-weight:900;margin:.15em 0 .5em;text-wrap:balance;color:var(--ink)}}
h3{{font-size:15px;font-weight:700;margin:1.2em 0 .35em;color:var(--navy2)}}
:root[data-theme="dark"] h3{{color:#8FB3F0}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]) h3{{color:#8FB3F0}}}}
p,li{{max-width:72ch}}
section{{margin-top:44px}}
.summary ul{{padding-left:1.1em;margin:.3em 0}}
.summary li{{margin:.25em 0}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:18px 0 6px}}
.kpis div{{background:var(--paper);border:1px solid var(--rule);border-radius:6px;padding:12px 14px}}
.kpis b{{display:block;font:500 24px/1.2 var(--mono);color:var(--teal);font-variant-numeric:tabular-nums}}
.kpis span{{font-size:13px;color:var(--muted)}}
.tbl-wrap{{overflow-x:auto;background:var(--paper);border:1px solid var(--rule);border-radius:6px;margin:8px 0 6px}}
table{{border-collapse:collapse;width:100%;font-size:13px}}
th,td{{padding:7px 9px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}}
thead th{{background:var(--navy);color:#fff;font-weight:700;white-space:nowrap;position:sticky;top:0}}
td.num,th.num{{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums;white-space:nowrap}}
td.sym{{font-family:var(--mono);font-size:12px;color:var(--teal);white-space:nowrap}}
td.nm{{font-weight:700;min-width:150px}}
td.spec{{min-width:210px;color:var(--ink)}}
td.note{{color:var(--muted);font-size:12px;min-width:150px}}
td.u{{white-space:nowrap}}
table.bom td:nth-child(4),table.bom td:nth-child(5){{min-width:140px}}
tr.grp th,tr.grp td{{background:var(--grp);font-weight:700;color:var(--navy2)}}
tr.grp.sw th{{color:var(--teal)}}
tfoot th{{text-align:right;font-weight:500;color:var(--muted)}}
tfoot td{{font-weight:700}}
tr.tot.strong th,tr.tot.strong td{{color:var(--ink);font-weight:900;font-size:14px}}
.meter{{display:inline-block;width:56px;height:6px;background:var(--rule);border-radius:3px;margin-right:8px;vertical-align:middle;overflow:hidden}}
.meter span{{display:block;height:100%;background:var(--teal)}}
.sum td a{{font-family:var(--mono);color:var(--teal);font-weight:500}}
figure{{margin:0}}
.fig{{background:var(--paper);border:1px solid var(--rule);border-radius:6px;padding:12px;overflow-x:auto;min-width:0}}
figcaption{{font-size:12px;color:var(--muted);margin-top:6px}}
.plan{{width:100%;height:auto;display:block;margin:0 auto}}
.plan text{{font-family:var(--font)}}
.fence{{fill:var(--cellbg);stroke:var(--ink);stroke-width:7}}
.area{{fill:var(--area);stroke:var(--eqline);stroke-width:2;stroke-dasharray:10 7;opacity:.95}}
.area-t{{font-size:21px;fill:var(--teal);font-weight:700;paint-order:stroke;stroke:var(--cellbg);stroke-width:7px;stroke-linejoin:round}}
.eq{{fill:var(--eq);stroke:var(--eqline);stroke-width:2.5}}
.eq-t{{fill:var(--ink);text-anchor:middle;font-weight:500}}
.reach{{fill:var(--reachf);fill-opacity:.07;stroke:var(--robot);stroke-width:2;stroke-dasharray:6 6}}
.rob{{fill:var(--robot)}}
.rob-t{{fill:#fff;font-size:22px;font-weight:700;text-anchor:middle}}
.hum{{fill:var(--hum)}}
.amr{{fill:var(--amr)}}
.amr-t{{fill:#fff;font-size:15px;font-weight:700;text-anchor:middle}}
.cam{{fill:var(--cam)}}
.lane{{fill:none;stroke-width:6;stroke-dasharray:18 10}}
.lane.main{{stroke:var(--teal)}}
.lane.sub{{stroke:var(--hum)}}
.ar{{fill:var(--teal)}}
.gap{{stroke:var(--cellbg);stroke-width:12}}
.jamb{{stroke:var(--ink);stroke-width:4}}
.door-t{{font-size:19px;fill:var(--amber);text-anchor:middle;font-weight:700}}
.dim{{stroke:var(--muted);stroke-width:2}}
.dim-t{{font-size:24px;fill:var(--muted);text-anchor:middle;font-family:var(--mono)!important}}
.dim-t.z{{font-size:64px}}
.sb1{{fill:var(--ink)}} .sb2{{fill:var(--paper);stroke:var(--ink);stroke-width:2}}
.sc-t{{font-size:20px;fill:var(--muted);font-family:var(--mono)!important}}
.sc-t.z{{font-size:56px}}
.bldg{{fill:var(--paper);stroke:var(--ink);stroke-width:22}}
.aisle{{fill:var(--aisle)}}
.aisle-t{{font-size:66px;fill:var(--teal);font-weight:700}}
.blk{{stroke:var(--ink);stroke-width:10}}
.blk.cell{{fill:var(--blk-cell)}} .blk.common{{fill:var(--blk-common)}} .blk.service{{fill:var(--blk-service)}}
.blk-t{{text-anchor:middle;font-weight:900;fill:var(--navy2);font-family:var(--mono)!important}}
:root[data-theme="dark"] .blk-t{{fill:#BFD3F7}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]) .blk-t{{fill:#BFD3F7}}}}
.blk-t.common,.blk-t.service{{font-family:var(--font)!important}}
.blk-s{{text-anchor:middle;fill:var(--ink)}}
.cell-link:hover .blk.cell,.cell-link:focus .blk.cell{{stroke:var(--amber);stroke-width:18}}
.door-z{{fill:var(--teal)}} .door-p{{fill:var(--amber)}}
.walk-t{{font-size:44px;fill:var(--muted);text-anchor:middle}}
.legend{{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:13px;color:var(--muted);margin:10px 2px 0;padding:0;list-style:none}}
.legend li{{display:flex;align-items:center;gap:6px}}
.legend i{{display:inline-block;width:16px;height:12px;border-radius:2px}}
.cell{{border-top:3px solid var(--navy2);padding-top:18px}}
.facts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px;margin:6px 0 4px}}
.facts div{{border-left:3px solid var(--cyan);padding:2px 10px}}
.facts dt{{font-size:12px;color:var(--muted)}}
.facts dd{{margin:0;font-weight:700;font-variant-numeric:tabular-nums}}
.two{{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:22px;align-items:start;margin-top:8px}}
.two .txt{{min-width:0}}
.two ul{{padding-left:1.1em;margin:.2em 0}}
.flow{{font-size:14px}}
.tbl-title span{{font-weight:400;color:var(--muted);font-size:13px}}
.refs li,.issues li{{margin:.35em 0}}
.keytbl th[scope=row],.issuetbl th[scope=row]{{white-space:nowrap;color:var(--navy2);font-weight:700;background:var(--grp);text-align:left}}
table.sum th.r{{text-align:right}}
.keytbl td,.issuetbl td{{font-size:13px;line-height:1.55}}
.issuetbl td:nth-child(3){{min-width:320px}}
.refs code{{font-family:var(--mono);color:var(--teal);font-size:13px}}
.note-box{{background:var(--paper);border:1px solid var(--rule);border-left:4px solid var(--amber);border-radius:4px;padding:10px 14px;font-size:13.5px;color:var(--ink);max-width:none}}
@media (max-width:900px){{.two{{grid-template-columns:1fr}}}}
@media (prefers-reduced-motion:reduce){{*{{scroll-behavior:auto}}}}
html{{scroll-behavior:smooth}}
</style>

<header class="mast"><div class="wrap">
  <p class="eyebrow">총괄5-세부1 기술실증 테스트베드 · A-3 정밀조립(Micro) Zone · 2026.10.07 작성 · 설계 추정본</p>
  <h1>정밀조립존 셀 구성 계획</h1>
</div></header>
<nav class="toc" aria-label="바로가기"><div class="wrap">
  <a href="#sum">요약</a><a href="#zone">존 배치도</a>
  {''.join(f'<a href="#{c["slug"]}">{c["id"]}</a>' for c in CELLS)}
  <a href="#common">존 공용</a><a href="#issues">확인 필요</a><a href="#refs">근거</a>
</div></nav>

<main class="wrap">
<section class="summary" id="sum" style="margin-top:8px">
  <p class="eyebrow">결론 및 핵심 요약 (Executive Summary)</p>
  <h2>5개 셀 · 793.4㎡ · 협약 12,600,000천원</h2>
  {key_table(grand, total_budget)}
  <div class="kpis">
    <div><b>5</b><span>Cell (A-3-1 ~ A-3-5)</span></div>
    <div><b>793.4㎡</b><span>셀 면적 합 / 층 1,361.3㎡</span></div>
    <div><b>{k(total_budget)}</b><span>협약 예산 합계 (천원) [R2]</span></div>
    <div><b>{k(grand)}</b><span>구성품 추정 합계 (천원)</span></div>
  </div>
  <div class="tbl-wrap"><table class="sum">
    <thead><tr><th>셀</th><th>명칭</th><th>구축</th><th class="r">면적</th><th class="r">로봇</th><th class="r">AMR</th><th class="r">로봇 카메라</th><th class="r">공정 비전</th><th class="r">협약(천원)</th><th class="r">추정(천원)</th><th class="r">예산 대비</th></tr></thead>
    <tbody>{''.join(summary_rows)}</tbody>
  </table></div>
</section>

<section id="zone">
  <p class="eyebrow">1. 정밀조립존 2D 배치도</p>
  <h2>존 전체 배치 (창조2관 2층)</h2>
  <figure class="fig">{zone}
    <ul class="legend">
      <li><i style="background:var(--blk-cell)"></i>실증 셀 (클릭 시 해당 셀로 이동)</li>
      <li><i style="background:var(--blk-common)"></i>존 공용</li>
      <li><i style="background:var(--blk-service)"></i>건물 서비스</li>
      <li><i style="background:var(--aisle);border:1px solid var(--teal)"></i>AMR 주통로</li>
      <li><i style="background:var(--teal)"></i>AMR 게이트</li>
      <li><i style="background:var(--amber)"></i>작업자 출입(인터록)</li>
    </ul>
    <figcaption>개념 배치도(설계 추정). 층 면적 1,361.3㎡를 46.0×29.6m 직사각형으로 환산한 값이며, 기둥·창호·EV 위치는 실측과 4개 존 상세 레이아웃 용역 결과로 확정해야 함.</figcaption>
  </figure>
  <ul class="legend" style="margin-top:14px">
    <li><i style="background:var(--robot);border-radius:50%"></i>로봇(점선 원 = 작업 반경)</li>
    <li><i style="background:var(--hum);border-radius:4px"></i>AMMR 양팔로봇 (AM)</li>
    <li><i style="background:var(--amr)"></i>AMR</li>
    <li><i style="background:var(--teal);height:4px"></i>MAIN JIG 경로</li>
    <li><i style="background:var(--hum);height:4px"></i>서브부품 경로</li>
    <li><i style="background:var(--cam);clip-path:polygon(50% 0,100% 100%,0 100%)"></i>카메라(탑뷰·관찰)</li>
  </ul>
  <p class="note-box">셀 상세도 공통 범례임. 셀 도면의 기호(R1, ST1, DS-G 등)는 각 셀 구성품 표의 <b>기호</b> 열과 같음.</p>
</section>

{''.join(sections)}

<section id="common">
  <p class="eyebrow">존 공용 설비 (셀 예산 외 · 2·3차년도 셀 잔여분으로 분담 검토)</p>
  <h2>존 공용 구성품</h2>
  {common_tbl}
</section>

<section id="issues">
  <p class="eyebrow">확인 필요 사항</p>
  <h2>확정 전에 정리할 쟁점</h2>
  {issues_table()}
</section>

<section id="refs">
  <p class="eyebrow">근거 문서</p>
  <h2>참조</h2>
  {refs_table()}
  <p class="note-box">표준 로봇·카메라 기준(셀당 협동로봇 10·AMR 4·AMMR 1, 로봇별 카메라 3대)과 연구 인력 자체 개발 처리(오픈소스 기반 SW 0원)는 이번 작업에서 사용자가 지정한 기준임. 단가는 2026년 국내 시장가 기준 설계 추정이며 견적이 아님.</p>
</section>
</main>
'''


if __name__ == "__main__":
    out = page()
    open(out_path("precision_zone.html"), "w", encoding="utf-8").write(out)
    print("written", len(out))
