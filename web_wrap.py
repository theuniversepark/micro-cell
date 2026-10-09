"""docs/*.html을 독립 웹 페이지로 감쌈(doctype·charset·viewport, 페이지 간 이동 바) + docs/index.html 생성. GitHub Pages용."""
import glob
import os
import re

PAGES = [("index.html", "목차"), ("ocs_precision.html", "로컬 OCS Zone 구성 - (예시) 정밀조립존"), ("dmworks_zones.html", "DMWorks 존별 옵션")]
HEAD = '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
BAR_CSS = ('<style>.webbar{background:#0A1636;display:flex;flex-wrap:wrap;gap:4px 14px;padding:8px 20px;'
           'font:600 13px "Noto Sans KR",sans-serif}.webbar a{color:#C9D6F0;text-decoration:none}.webbar a.on{color:#00C2D1}'
           '.webbar a:hover{color:#fff}body{margin:0}'
           '.webbar .dl{margin-left:auto;display:flex;gap:8px}.webbar .dl a{color:#0A1636;background:#00C2D1;border-radius:4px;padding:2px 10px}'
           '.webbar .dl a:hover{background:#fff;color:#0A1636}'
           '@page{size:A3 landscape;margin:10mm}'
           '@media print{.webbar,nav.toc,.where,a.tolink[href^="#topo-"]:not(.sw){display:none!important}'
           '.wrap{max-width:none!important;padding-inline:0!important;padding-block:0 8mm!important}'
           '.mast{max-width:none!important;margin:0 0 6mm!important;padding-inline:0!important}.mast>.wrap{padding:7mm 9mm!important}'
           'thead{display:table-header-group}tfoot{display:table-row-group}th{position:static!important;white-space:normal!important}'
           '.tbl-wrap,.fig{overflow:visible!important}table,table.wide{width:100%!important;min-width:0!important;table-layout:auto}'
           'td,th{min-width:0!important;white-space:normal!important;overflow-wrap:anywhere;word-break:keep-all}'
           'td.num,td.q,td.u,td.sym,td.dz,th.dz{white-space:nowrap!important}td.src a{word-break:break-all}'
           'table{font-size:9px!important}table.wide{font-size:7.5px!important}table.wide td.note,table.wide td.basis,table.wide td.uc,table.wide td.src,table.wide td.mk{font-size:7px!important}'
           'p,li{max-width:none!important}figure,svg,tr,.kpis{break-inside:avoid}h2,h3,.eyebrow,.tbl-title{break-after:avoid}'
           'main>section{break-inside:auto}main>section+section{break-before:page}'
           '.fig svg{max-height:175mm;width:auto!important;max-width:100%!important;height:auto;display:block;margin:0 auto}a{color:inherit;text-decoration:none}'
           ':root{color-scheme:light}}</style>')


EXPORTS = ("ocs_precision.html", "dmworks_zones.html")


def dl(name):
    b = name[:-5]
    return f'<span class="dl"><a href="{b}.pdf" download>PDF 저장</a><a href="{b}.docx" download>Word 저장</a></span>'


def bar(cur):
    return ('<nav class="webbar">' + "".join(f'<a href="{f}"{" class=on" if f == cur else ""}>{t}</a>' for f, t in PAGES)
            + (dl(cur) if cur in EXPORTS else "") + "</nav>")


def wrap(path):
    name = os.path.basename(path)
    s = open(path, encoding="utf-8").read()
    if s.startswith("<!doctype"):
        return
    m = re.search(r"<header|<nav|<main|<section", s)
    head, body = s[:m.start()], s[m.start():]
    open(path, "w", encoding="utf-8").write(HEAD + head + BAR_CSS + "\n</head>\n<body>\n" + bar(name) + "\n" + body + "\n</body>\n</html>\n")


INDEX = """<title>로컬 OCS 구성</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&family=IBM+Plex+Mono:wght@400&display=swap">
<style>
:root{--bg:#F5F7FB;--paper:#fff;--ink:#16213A;--muted:#5A6782;--rule:#D7DFEC;--navy:#10214B;--teal:#0090A0}
@media (prefers-color-scheme: dark){:root{--bg:#0B1430;--paper:#111D3F;--ink:#E6ECF8;--muted:#9AA8C6;--rule:#253661;--navy:#0A1636;--teal:#2BC0CF;color-scheme:dark}}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic",sans-serif;line-height:1.6}
.mast{background:var(--navy);color:#fff;padding:36px 20px 30px}
.wrap{max-width:1040px;margin:0 auto}
.eb{font-family:"IBM Plex Mono",monospace;font-size:12px;color:#7FE3EC;margin:0 0 8px;letter-spacing:.06em}
h1{margin:0;font-size:clamp(26px,4vw,36px);font-weight:900}
main{padding:28px 20px 56px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}
.card{display:flex;flex-direction:column;gap:10px;background:var(--paper);border:1px solid var(--rule);border-radius:10px;padding:18px 20px}
.card:hover{border-color:var(--teal)}
a.open{display:flex;flex-direction:column;gap:6px;color:var(--ink);text-decoration:none;flex:1}
.save{display:flex;gap:8px;margin:0}.save a{font-size:13px;font-weight:700;color:var(--teal);border:1px solid var(--teal);border-radius:4px;padding:2px 10px;text-decoration:none}
.save a:hover{background:var(--teal);color:var(--paper)}
.card b{font-size:17px}.card span{color:var(--muted);font-size:14px}.card em{font-style:normal;color:var(--teal);font-size:13px;font-weight:700;margin-top:auto}
.foot{margin-top:28px;color:var(--muted);font-size:13px}
.ref{margin-top:36px}.ref h2{font-size:18px;margin:2px 0 12px;color:var(--ink)}.eb2{font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--teal);margin:0;letter-spacing:.06em}
.ref img{display:block;width:100%;height:auto;border:1px solid var(--rule);border-radius:10px;background:#fff}.cap{color:var(--muted);font-size:13px;margin:8px 0 0}.foot a{color:var(--teal)}
</style>
</head>
<body>
<header class="mast"><div class="wrap"><p class="eb">총괄5-세부1 기술실증 테스트베드 · A-3 정밀조립(Micro) ZONE · 설계 추정본</p><h1>로컬 OCS 구성</h1></div></header>
<main><div class="wrap">
<div class="cards">
<div class="card"><a class="open" href="ocs_precision.html"><b>로컬 OCS Zone 구성 - (예시) 정밀조립존</b><span>AAS 기반 수집–저장 아키텍처, 장비 설치·연결 토폴로지, 데이터량·저장 용량 산정, 존/셀 HW·SW 목록</span><em>열기 →</em></a><p class="save"><a href="ocs_precision.pdf" download>PDF 저장</a><a href="ocs_precision.docx" download>Word 저장</a></p></div>
<div class="card"><a class="open" href="dmworks_zones.html"><b>DMWorks 존별 옵션 구성</b><span>이지로보틱스 10/8 견적 3건(정가×52%) 기준, 존별 구매 필요성·해야 할 일·옵션, 품목별 검토, 재견적 쟁점</span><em>열기 →</em></a><p class="save"><a href="dmworks_zones.pdf" download>PDF 저장</a><a href="dmworks_zones.docx" download>Word 저장</a></p></div>
</div>
<section class="ref"><p class="eb2">참고 자료</p><h2>피지컬AI를 위한 AAS 기반 데이터 수집–저장 표준 아키텍처(안)</h2><a href="data_collection_architecture.png" target="_blank" rel="noopener"><img src="data_collection_architecture.png" width="1919" height="1080" alt="중앙 Server·Local Server·Edge Gateway Server·Field 계층과 검증 영역으로 구성된 AAS 기반 데이터 수집–저장 표준 아키텍처"></a><p class="cap">출처: 기술실증 테스트베드 발표자료 「2-2. 피지컬AI 제조 데이터 구축(4/6)」 68쪽. 정밀조립존 OCS Cell(Local Server–Edge Gateway 데이터 계층) 설계의 기준 그림. 그림을 누르면 원본 크기로 열림.</p></section>
<p class="foot">금액 단위 천원, VAT 별도 · 소스: <a href="https://github.com/theuniversepark/micro-cell">github.com/theuniversepark/micro-cell</a></p>
</div></main>
</body>
</html>
"""

if __name__ == "__main__":
    for f in glob.glob("docs/*.html"):
        if not f.endswith("index.html"):
            wrap(f)
    open("docs/index.html", "w", encoding="utf-8").write(HEAD + INDEX)
    open("docs/.nojekyll", "w").close()
    print("wrapped")
