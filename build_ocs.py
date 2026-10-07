"""1차년도 통합 OCS 시뮬레이션 Cell 3종 장비 목록 페이지 → ocs_cells.html"""
import re
import html
import build_page as bp
from ocs_data import OCS
from privacy import PV, PUBLIC, out

E = html.escape
bp.GROUP_ORDER = ["SW", "HW", "서비스"]
bp.GROUP_LABEL = {"SW": "SW 구성품", "HW": "HW 구성품", "서비스": "구축 서비스 (DT 라이브러리·설치·교육)"}

CSS = re.search(r"<style>.*?</style>", bp.page(), re.S).group(0)
EXTRA = """<style>
.arch text{font-family:var(--font)}
.ly{stroke:none}
.ly1{fill:var(--navy)} .ly2{fill:var(--navy2)} .ly3{fill:#2E5AA8} .ly4{fill:#5E86C8}
.lyt{fill:#fff;font-size:15px;font-weight:700}
.box{fill:var(--paper);stroke:none}
.boxt{fill:var(--ink);font-size:12.5px;text-anchor:middle}
.boxs{fill:var(--muted);font-size:10.5px;text-anchor:middle}
.own{fill:none;stroke:var(--amber);stroke-width:3;stroke-dasharray:0}
.owntag{fill:var(--amber);font-size:12px;font-weight:700}
.fl-d{stroke:var(--cyan);stroke-width:2.2;fill:none}
.fl-c{stroke:#9DB8E8;stroke-width:2.2;fill:none;stroke-dasharray:6 4}
.fl-t{font-size:11px;fill:var(--ink);paint-order:stroke;stroke:var(--bg);stroke-width:4px}
.mx td,.mx th{text-align:center}
.mx td:first-child,.mx th:first-child{text-align:left}
.dot{color:var(--teal);font-weight:900}
.dash{color:var(--muted)}
.purpose{display:inline-block;font:500 12px var(--mono);color:#fff;background:var(--teal);border-radius:3px;padding:1px 8px;margin-left:8px;vertical-align:middle}
</style>"""


def arch_svg():
    W = 1000
    o = [f'<svg class="arch plan" viewBox="0 0 {W} 640" role="img" aria-label="OCS 셀 계층 구성도" style="max-width:1000px">',
         '<defs><marker id="ad" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--cyan)"/></marker>'
         '<marker id="ac" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#9DB8E8"/></marker></defs>']
    layers = [
        (20, "중앙 계층", "ly1", [("중앙 DCC (D-2-1)", "통합관제·KPI 대시보드"), ("AAS 통합서버 (D-1-1)", "AAS Repository·AI-Ready 데이터")]),
        (160, "OCS 셀 = 존 계층", "ly2", [("로컬 DCC 서버", "존 오케스트레이터·OCS 실행"), ("검증 DT · DMWorks", "공정·물류·PLC 가상 시운전"),
                                       ("학습 DT · Omniverse", "GPU 서버·RL·합성데이터"), ("존별 운영 SW", "APS / MES·DAQ / QMS·OPT"), ("로컬 스토리지", "원시데이터 200~300TB")]),
        (340, "엣지 계층", "ly3", [("엣지 AI 추론기 × 30", "Jetson Thor급·로봇당 1"), ("국산 NPU 엣지", "GPU 대비 추론 비교"), ("PLC/PAC·HIL 랙", "셀 지정 PLC 1사 통일")]),
        (480, "현장 계층", "ly4", [("Sim-to-Real 키트", "협동로봇·AMR·카메라"), ("3D 스캐너", "점군 → DT 라이브러리(USD)"), ("2차년도 실물 셀", "A-1-3 · A-2-x · A-4-x")]),
    ]
    centers = {}
    for y, name, cls, boxes in layers:
        o.append(f'<rect x="0" y="{y}" width="{W}" height="118" rx="6" class="ly {cls}"/>')
        o.append(f'<text x="16" y="{y + 26}" class="lyt">{E(name)}</text>')
        n = len(boxes)
        gx, bw = 160, (W - 160 - 16 - (n - 1) * 12) / n
        for i, (t, s) in enumerate(boxes):
            x = gx + i * (bw + 12)
            o.append(f'<rect x="{x:.0f}" y="{y + 18}" width="{bw:.0f}" height="82" rx="5" class="box"/>')
            o.append(f'<text x="{x + bw / 2:.0f}" y="{y + 54}" class="boxt">{E(t)}</text>')
            o.append(f'<text x="{x + bw / 2:.0f}" y="{y + 74}" class="boxs">{E(s)}</text>')
            centers[t] = (x + bw / 2, y + 18, y + 100)
    # own scope
    o.append(f'<rect x="150" y="166" width="{W - 158}" height="106" rx="7" class="own"/>')
    o.append(f'<text x="{W - 10}" y="158" class="owntag" text-anchor="end">본 장비 심의 범위 (셀 = 시스템)</text>')

    def arrow(x1, y1, x2, y2, label, kind="d", dx=6, anchor="start"):
        m = "ad" if kind == "d" else "ac"
        o.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" class="fl-{kind}" marker-end="url(#{m})"/>')
        o.append(f'<text x="{(x1 + x2) / 2 + dx:.0f}" y="{(y1 + y2) / 2 + 4:.0f}" class="fl-t" text-anchor="{anchor}">{E(label)}</text>')

    c = centers
    lx = c["로컬 DCC 서버"][0]
    arrow(lx - 30, 160 + 18, lx - 30, 20 + 100, "AAS 서브모델·KPI", dx=-8, anchor="end")
    arrow(lx + 30, 20 + 100, lx + 30, 160 + 18, "작업지시·재계획", "c", dx=8)
    ex = c["엣지 AI 추론기 × 30"][0]
    arrow(ex - 30, 340 + 18, ex - 30, 160 + 100, "추론결과·상태 (OPC UA/MQTT)")
    ox = c["학습 DT · Omniverse"][0]
    arrow(ox, 160 + 100, ex + 60, 340 + 18, "스킬·모델 배포", "c")
    hx = c["PLC/PAC·HIL 랙"][0]
    dx_ = c["검증 DT · DMWorks"][0]
    arrow(hx, 340 + 18, dx_ + 40, 160 + 100, "PLC Read·핸드셰이크")
    kx = c["Sim-to-Real 키트"][0]
    arrow(kx, 480 + 18, ex - 60, 340 + 100, "센서·로봇 원시데이터")
    rx = c["2차년도 실물 셀"][0]
    arrow(rx, 480 + 18, hx + 40, 340 + 100, "실설비 I/O (2차년도~)", "c")
    o.append('<text x="160" y="622" class="fl-t" style="fill:var(--muted)">실선 = 데이터·검증 흐름 · 점선 = 명령·배포 흐름 · DMWorks↔Omniverse는 USD 커넥터로 씬 연계</text>')
    o.append("</svg>")
    return "".join(o)


MATRIX = [
    ("DMWorks BASE·MULTIPLE PROCESS", ["DM-B", "DM-MP"]),
    ("DMWorks PLC SIMULATION (가상 시운전)", ["DM-PLC"]),
    ("DMWorks HUMAN·VR (작업자)", ["DM-H"]),
    ("DMWorks POINT CLOUD", ["DM-PC"]),
    ("Omniverse 학습 DT", ["OV"]),
    ("GPU 8장 연산 서버", ["SRV"]),
    ("생산 스케줄링(APS)", ["APS"]),
    ("CNC 가공 시뮬레이션·NC 검증", ["NCV"]),
    ("작업지시·생산·품질(MES)", ["MES"]),
    ("가공 데이터 수집 키트", ["DAQ"]),
    ("형상측정·분석 SW", ["SCN-SW"]),
    ("QMS·OCS 통합운영", ["QMS"]),
    ("검사조건 최적화 플랫폼", ["OPT"]),
    ("대형 공간 3D 스캐너", ["SCN-L"]),
    ("핸드헬드 정밀 3D 스캐너", ["SCN-H"]),
    ("PLC/PAC·HIL 랙", ["HIL"]),
    ("엣지 30대·로컬 DCC·스토리지", ["EDGE", "LDCC", "STO"]),
    ("Sim-to-Real 검증 키트", ["S2R"]),
]


def matrix():
    rows = []
    for label, syms in MATRIX:
        cells = []
        for c in OCS:
            have = [s for s in syms if any(i[1] == s for i in c["items"])]
            cells.append('<td><span class="dot">●</span></td>' if len(have) == len(syms)
                         else ('<td><span class="dot">◐</span></td>' if have else '<td><span class="dash">–</span></td>'))
        rows.append(f"<tr><td>{E(label)}</td>{''.join(cells)}</tr>")
    head = "".join(f'<th>{E(c["id"])}<br><small>{E(c["purpose"])}</small></th>' for c in OCS)
    return f'<div class="tbl-wrap"><table class="mx"><thead><tr><th>구성 요소</th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def _ratios():
    return [round(sum(i[6] * i[8] for i in c["items"]) / c["budget"] * 100) for c in OCS]


RATIOS = _ratios()


def page():
    secs, summ = [], []
    grand = budget = 0
    for c in OCS:
        tbl, total, hw, sw, sv = bp.bom_table(c["items"], c["budget"], "t-" + c["slug"], kunit=True)
        grand += total
        budget += c["budget"]
        r = total / c["budget"] * 100
        summ.append(f'<tr><td><a href="#{c["slug"]}">{E(c["id"])}</a></td><td class="nm">{E(c["name"])}</td><td>{E(c["purpose"])}</td>'
                    f'<td class="num">{bp.k(c["budget"])}</td><td class="num">{bp.k(sw)}</td><td class="num">{bp.k(hw)}</td>'
                    f'<td class="num">{bp.k(total)}</td><td class="num"><span class="meter"><span style="width:{min(r, 100):.0f}%"></span></span>{r:.0f}%</td></tr>')
        goals = "".join(f"<li>{E(g)}</li>" for g in c["goal"])
        secs.append(f'''
<section class="cell" id="{c["slug"]}">
  <header class="cell-h"><p class="eyebrow">{E(c["id"])} · 1차년도('26) · {E(c["place"])}</p>
  <h2>{E(c["name"])}<span class="purpose">{E(c["purpose"])}</span></h2></header>
  <dl class="facts">
    <div><dt>협약 예산 [R2]</dt><dd>{bp.k(c["budget"])}천원</dd></div>
    <div><dt>추정 합계</dt><dd>{bp.k(total)}천원 ({r:.0f}%)</dd></div>
    <div><dt>SW / HW / 서비스 (천원)</dt><dd>{bp.k(sw)} / {bp.k(hw)} / {bp.k(sv)}</dd></div>
    <div><dt>담당</dt><dd>{E(c["owner"])}</dd></div>
  </dl>
  <h3>구축 목적</h3><ul>{goals}</ul>
  <h3>다른 OCS 셀과 다른 점</h3><p>{E(c["diff"])}</p>
  <h3 class="tbl-title">장비 목록 <span>(단가·금액 단위: 천원, VAT 별도)</span></h3>
  {tbl}
</section>''')
    return f'''<title>OCS 셀 장비 목록</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=IBM+Plex+Mono:wght@400;500&display=swap">
{CSS}{EXTRA}
<header class="mast"><div class="wrap">
  <p class="eyebrow">총괄5-세부1 기술실증 테스트베드 · 1차년도 통합 OCS 시뮬레이션 Cell · 2026.10.07 작성 · 설계 추정본 · {"대외비 단가 포함" if not PUBLIC else "공개본(DMWorks 단가 비공개)"}</p>
  <h1>OCS 셀 장비 목록</h1>
  <p>유연제조(A-1-4)·적응가공(A-2-5)·AI정밀검사(A-4-5) OCS 셀의 존별 구축 목적, 계층 구성도, HW·SW 장비 목록을 정리함. 10/6 결정에 따라 3개 셀을 같은 구성으로 두지 않고 존별 목적에 맞춰 차별화함.</p>
</div></header>
<nav class="toc" aria-label="바로가기"><div class="wrap">
  <a href="#sum">요약</a><a href="#arch">구성도</a><a href="#mx">구성 비교</a>
  {''.join(f'<a href="#{c["slug"]}">{c["id"]}</a>' for c in OCS)}
  <a href="#issues">확인 필요</a><a href="#refs">근거</a>
</div></nav>
<main class="wrap">
<section class="summary" id="sum" style="margin-top:8px">
  <p class="eyebrow">결론 및 핵심 요약 (Executive Summary)</p>
  <h2>3개 셀 · 협약 {bp.k(budget)}천원 · 추정 {bp.k(grand)}천원 ({grand / budget * 100:.0f}%)</h2>
  <ul>
    <li><b>심의 단위</b>: SW만 올리지 않고 SW + 워크스테이션 + GPU 서버 + 엣지 + 로컬 DCC + 스토리지 + HIL을 묶은 '셀 = 시스템'으로 상정함. NIPA 9/23 회신(장비 전용 SW는 장비 구축비 포함)과 맞음 [W7]</li>
    <li><b>존별 차별화</b>: 유연제조는 공정 최적화·가상 시운전, 적응가공은 데이터·강화학습, 정밀검사는 역설계 DT·품질 운영을 목적으로 둠. 공통 골격(DMWorks·Omniverse·로컬 DCC·엣지)만 같고 존별 SW·스캐너·서버 구성은 다름 [W7]</li>
    <li><b>시뮬레이션 역할 분리</b>: 공정·PLC 검증은 국산 DMWorks, 물리 기반 학습·합성데이터는 Omniverse/Isaac으로 나눔. DMWorks에 물리엔진이 없고 USD는 지오메트리만 내보내기 때문임 [W5]</li>
    <li><b>집행률</b>: 국산 SW 전환으로 SW 비중이 줄어든 만큼 9/28 방침대로 엣지(존당 30대)·로컬 스토리지·Sim-to-Real 키트를 넣었고, 오픈소스 기반 개발·구축(DMWorks 커스텀, 강화학습 환경, 합성데이터, DT 라이브러리)은 연구 인력 자체 개발(0원)로 빼서 현재 예산의 {min(RATIOS)}~{max(RATIOS)}% 수준임. 20% 넘게 줄면 NIPA 사전승인·중장위 변경심의 대상이 될 수 있음 [W6][W7]</li>
  </ul>
  <div class="tbl-wrap"><table class="sum">
    <thead><tr><th>셀</th><th>명칭</th><th>목적</th><th>협약(천원)</th><th>SW(천원)</th><th>HW(천원)</th><th>추정(천원)</th><th>예산 대비</th></tr></thead>
    <tbody>{''.join(summ)}</tbody>
  </table></div>
</section>
<section id="arch">
  <p class="eyebrow">아키텍처</p>
  <h2>OCS 셀 계층 구성도 (3개 셀 공통 골격)</h2>
  <figure class="fig">{arch_svg()}<figcaption>OCS 셀은 존 오케스트레이터 겸 로컬 서버 역할을 함. 엣지는 로봇마다, 원시데이터는 로컬 스토리지, AI-Ready 데이터는 중앙 AAS 통합서버로 보냄 [W6].</figcaption></figure>
</section>
<section id="mx">
  <p class="eyebrow">구성 비교</p>
  <h2>셀별 구성 요소 비교</h2>
  {matrix()}
  <p class="note-box">● 포함 · ◐ 일부 포함 · – 미포함. 3D 스캐너는 셀마다 사지 않고 유연제조에 대형 공간형, 정밀검사에 핸드헬드형을 하나씩 두고 공동활용함.</p>
</section>
{''.join(secs)}
<section id="issues" class="issues">
  <p class="eyebrow">확인 필요 사항</p>
  <h2>확정 전에 정리할 쟁점</h2>
  <ul>
    <li><b>DMWorks 옵션 단가</b>: OLP·RRS·CAD IMPORT/EXPORT 상세 옵션표를 받지 못해 추정값을 넣었음. {PV.DM_PROPOSAL if PV else "제안가·예상치는 대외비라 공개본에서 뺐음. 재견적으로 확정해야 함"}</li>
    <li><b>비교견적</b>: 국산 단일 벤더라 제조사가 다른 비교견적 2건이 필요함. 지멘스 Process Simulate 등을 비교 대상으로 받아야 함</li>
    <li><b>구독형 SW</b>: Omniverse Enterprise·CAD→USD 도구는 연 구독이라 장비비 계상 가능 여부를 NIPA에 확인해야 함. 안 되면 Isaac Sim(무료)만 쓰고 그 금액을 HW로 돌림</li>
    <li><b>엣지 30대 선행 확보</b>: 1차년도 OCS 셀에는 실물 로봇이 없음. 엣지를 2차년도로 미루면 셀당 약 300,000천원이 줄어 집행률이 80% 밑으로 떨어짐. 엣지 SW 개발 주체도 아직 정해지지 않았음</li>
    <li><b>GPU 서버 금액</b>: 적응가공 GPU 8장 서버가 405,000천원인지 450,000천원인지 확인해야 함. 유연제조·정밀검사도 같은 구성을 적용했음</li>
    <li><b>3D 스캐너 구분</b>: 10/6 견적 130,000천원·250,000천원 중 어느 쪽이 대형 공간형이고 어느 쪽이 핸드헬드형인지 확인해야 함</li>
    <li><b>PLC 메이커</b>: DMWorks 동시 시뮬레이션 경험이 2개 기종까지이므로 셀별 PLC 메이커를 1사로 지정해 HIL 랙과 2차년도 실물 셀 발주 사양에 같이 넣어야 함 [W4]</li>
    <li><b>정밀조립존</b>: 정밀조립존에는 OCS 셀이 없음. A-3-5 DT 검증은 이 3개 셀의 DMWorks 카피 공동활용이나 별도 라이선스 1카피로 확보해야 함</li>
    <li><b>대외비</b>: {"DMWorks 금액은 이지로보틱스 대외비 정가표에서 산출했으므로 원내 담당자 외에는 공유하지 않음" if not PUBLIC else "공개본은 DMWorks 정가 기반 금액을 0원으로 두고 비공개 표기함. 합계·집행률도 DMWorks를 뺀 값임"}</li>
  </ul>
</section>
<section id="refs" class="refs">
  <p class="eyebrow">근거 문서</p>
  <h2>참조</h2>
  <ul>
    <li><code>[R2]</code> 연구개발계획서 부록(협약용, 2026.08.19) — A-1-4 2,100,000·A-2-5 2,320,000·A-4-5 2,600,000천원, 기자재 구입 및 활용계획서 주요사양</li>
    <li><code>[S1]</code> DMWorks 3.0 Solution List Price(이지로보틱스, 2026.01, 대외비) — 모듈별 정가, 60% 내외 할인 예정</li>
    <li><code>[S2]</code> 아이티마야 RTX PRO 6000 Max-Q 견적(2026.09.23) — GPU 공급단가 25,670천원</li>
    <li><code>[W4]</code> DMWorks 도입 조건(9/30) — AAS 규격 캠틱 정의, PLC Read+핸드셰이크, 셀별 PLC 통일, 라이선스 후속 제안</li>
    <li><code>[W5]</code> 피지컬AI 학습·검증 시뮬레이션 역할 분리(옴니버스·DMWorks, 9/17·9/21)</li>
    <li><code>[W6]</code> 피지컬AI 의사결정 미팅(9/28·10/6) — 엣지 존당 30대·토르 약 10,000천원, 로컬 데이터 서버, GPU 서버·3D 스캐너·DT 라이브러리 단가</li>
    <li><code>[W7]</code> OCS 셀 '셀=시스템' 중장위 상정(9/21) → 존별 목적·HW/SW 구성도 문서화 후 확정(10/6)</li>
  </ul>
</section>
</main>
'''


if __name__ == "__main__":
    open(out("ocs_cells.html"), "w", encoding="utf-8").write(page())
    print("ok")
