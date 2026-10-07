"""docs/*.html을 독립 웹 페이지로 감쌈(doctype·charset·viewport, 페이지 간 이동 바) + docs/index.html 생성. GitHub Pages용."""
import glob
import os
import re

PAGES = [("index.html", "목차"), ("precision_zone.html", "셀 구성 계획"), ("ocs_precision.html", "정밀조립존 OCS Cell")]
HEAD = '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
BAR_CSS = ('<style>.webbar{background:#0A1636;display:flex;flex-wrap:wrap;gap:4px 14px;padding:8px 20px;'
           'font:600 13px "Noto Sans KR",sans-serif}.webbar a{color:#C9D6F0;text-decoration:none}.webbar a.on{color:#00C2D1}'
           '.webbar a:hover{color:#fff}body{margin:0}</style>')


def bar(cur):
    return '<nav class="webbar">' + "".join(f'<a href="{f}"{" class=on" if f == cur else ""}>{t}</a>' for f, t in PAGES) + "</nav>"


def wrap(path):
    name = os.path.basename(path)
    s = open(path, encoding="utf-8").read()
    if s.startswith("<!doctype"):
        return
    m = re.search(r"<header|<nav|<main|<section", s)
    head, body = s[:m.start()], s[m.start():]
    open(path, "w", encoding="utf-8").write(HEAD + head + BAR_CSS + "\n</head>\n<body>\n" + bar(name) + "\n" + body + "\n</body>\n</html>\n")


INDEX = """<title>정밀조립존 설계 페이지</title>
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
a.card{display:flex;flex-direction:column;gap:6px;background:var(--paper);border:1px solid var(--rule);border-radius:10px;padding:18px 20px;color:var(--ink);text-decoration:none}
a.card:hover{border-color:var(--teal)}
.card b{font-size:17px}.card span{color:var(--muted);font-size:14px}.card em{font-style:normal;color:var(--teal);font-size:13px;font-weight:700;margin-top:auto}
.foot{margin-top:28px;color:var(--muted);font-size:13px}.foot a{color:var(--teal)}
</style>
</head>
<body>
<header class="mast"><div class="wrap"><p class="eb">총괄5-세부1 기술실증 테스트베드 · A-3 정밀조립(Micro) ZONE · 설계 추정본</p><h1>정밀조립존 설계 페이지</h1></div></header>
<main><div class="wrap">
<div class="cards">
<a class="card" href="precision_zone.html"><b>정밀조립존 셀 구성 계획</b><span>존 2D 배치도와 A-3-1~A-3-5 셀별 HW·SW 구성품(협동로봇·AMR·카메라·센서·PLC·그리퍼)·수량·단가</span><em>열기 →</em></a>
<a class="card" href="ocs_precision.html"><b>정밀조립존 OCS Cell</b><span>AAS 기반 수집–저장 아키텍처, 장비 설치·연결 토폴로지, 데이터량·저장 용량 산정, 존/셀 HW·SW 목록</span><em>열기 →</em></a>
</div>
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
