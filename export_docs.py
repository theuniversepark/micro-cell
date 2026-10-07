"""docs/*.html → docs/*.pdf (Chrome 인쇄) · docs/*.docx (도면 PNG 변환 후 LibreOffice). GitHub Pages 저장 버튼용.
Chrome·soffice가 없으면 건너뜀."""
import base64
import os
import re
import shutil
import subprocess
import sys
import tempfile

PAGES = ["precision_zone.html", "ocs_precision.html"]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SOFFICE = shutil.which("soffice")
FIG_W = 1400  # 도면 PNG 폭(px)


def chrome(*args):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", *args],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False, timeout=180)


def pdf(src, dst):
    chrome("--no-pdf-header-footer", f"--print-to-pdf={dst}", "file://" + os.path.abspath(src))


def svg_png(svg, css, tmp, n):
    vb = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"', svg)
    w, h = (float(vb.group(3)), float(vb.group(4))) if vb else (1000.0, 600.0)
    H = max(40, round(FIG_W * h / w))
    svg = re.sub(r'style="max-width:[^"]*"', "", svg, count=1)
    page = os.path.join(tmp, f"f{n}.html")
    shot = os.path.join(tmp, f"f{n}.png")
    open(page, "w", encoding="utf-8").write(
        f'<!doctype html><meta charset="utf-8">{css}<style>html,body{{margin:0;background:#fff}}'
        f'svg{{display:block;width:{FIG_W}px;height:{H}px;max-width:none!important}}</style>{svg}')
    chrome(f"--window-size={FIG_W},{H}", "--force-device-scale-factor=1", f"--screenshot={shot}", "file://" + page)
    return base64.b64encode(open(shot, "rb").read()).decode() if os.path.exists(shot) else None


def docx(src, dst):
    s = open(src, encoding="utf-8").read()
    css = "".join(re.findall(r"<style>.*?</style>", s, re.S))
    body = s[s.index("<body>") + 6:s.rindex("</body>")]
    body = re.sub(r'<nav class="(webbar|toc)".*?</nav>', "", body, flags=re.S)
    body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
    tmp = tempfile.mkdtemp()
    figs = []

    def rep(m):
        if "viewBox" not in m.group(0)[:300]:      # 범례 견본 등 작은 아이콘은 뺌
            return ""
        b64 = svg_png(m.group(0), css, tmp, len(figs))
        figs.append(1)
        return f'<p><img src="data:image/png;base64,{b64}" width="640"></p>' if b64 else ""

    body = re.sub(r"<svg\b.*?</svg>", rep, body, flags=re.S)
    body = re.sub(r"<table\b[^>]*>", '<table border="1" cellspacing="0" cellpadding="4" width="100%">', body)
    body = re.sub(r'<th scope="row"[^>]*>', '<th scope="row" style="background:#EEF2F9;color:#1B3A73">', body)
    body = re.sub(r'<tr class="grp[^"]*"><th', '<tr><th style="background:#E4F6F8;color:#10214B"', body)
    title = re.search(r"<title>(.*?)</title>", s).group(1)
    simple = ('<style>body{font-family:"Malgun Gothic","Apple SD Gothic Neo",sans-serif;font-size:9pt;color:#13203F}'
              'h1,h2,h3{font-family:"Malgun Gothic","Apple SD Gothic Neo",sans-serif}h1{font-size:18pt;color:#10214B}h2{font-size:13pt;color:#10214B;margin-top:14pt}h3{font-size:11pt;color:#1B3A73}'
              'th{background:#10214B;color:#ffffff;font-size:8pt;text-align:left}td{font-size:8pt;vertical-align:top}'
              '.eyebrow{color:#0090A0;font-size:8pt}a{color:#13203F;text-decoration:none}</style>')
    html = os.path.join(tmp, os.path.basename(dst).replace(".docx", ".html"))
    open(html, "w", encoding="utf-8").write(f'<html><head><meta charset="utf-8"><title>{title}</title>{simple}</head><body>{body}</body></html>')
    subprocess.run([SOFFICE, "--headless", "--norestore", "--convert-to", "docx:MS Word 2007 XML", "--outdir", tmp, html],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False, timeout=300)
    out = html.replace(".html", ".docx")
    if os.path.exists(out):
        shutil.move(out, dst)
    shutil.rmtree(tmp, ignore_errors=True)
    return len(figs)


if __name__ == "__main__":
    if not os.path.exists(CHROME):
        sys.exit("Chrome 없음 — PDF·Word 생성 건너뜀")
    for p in PAGES:
        src = os.path.join("docs", p)
        pdf(src, src.replace(".html", ".pdf"))
        n = docx(src, src.replace(".html", ".docx")) if SOFFICE else 0
        print(p, "pdf", os.path.exists(src.replace(".html", ".pdf")), "docx", os.path.exists(src.replace(".html", ".docx")), f"figs={n}")
