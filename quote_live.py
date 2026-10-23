"""견적서 파일 선택(브라우저 업로드) — DMWorks 존별 옵션 구성 페이지에서 견적서 엑셀을 고르면 브라우저 안에서 읽어 페이지를 다시 그리고,
결과를 localStorage에 남겨 OCS 시뮬레이션 Cell 3종 페이지도 같은 견적서 기준으로 다시 그림(quote_live.js). 파일은 서버로 보내지 않음.
여기서는 기준 견적(빌드 시 데이터)을 #qlbase JSON으로 넣고 패널·스타일·스크립트를 붙임."""
import html
import json
import os

from privacy import PUBLIC

E = html.escape
SHEETJS = "https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"
BL, BLNO = "10/23 견적", "1023-1~3"  # 기준 견적(페이지 작성 기준) 표기
JS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "quote_live.js"), encoding="utf-8").read()

CSS = """<style>
.qlive{margin:14px 0 6px;padding:12px 16px;border:1px solid var(--rule);border-left:4px solid var(--teal);border-radius:8px;background:var(--paper);font-size:13.5px;line-height:1.55}
.qlive.on{border-left-color:var(--amber)} .qlive.drag{outline:2px dashed var(--teal);outline-offset:2px}
.ql-row{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center}
.ql-row>b:first-child{color:var(--navy2);font-size:14px}
.ql-pick,.ql-row button{font:600 13px var(--font);border-radius:4px;padding:6px 14px;cursor:pointer}
.ql-pick{color:#fff;background:var(--teal);border:0} .ql-pick:focus-within{outline:2px solid var(--amber);outline-offset:2px}
.ql-pick input{position:absolute;width:1px;height:1px;opacity:0;pointer-events:none}
.ql-row button{color:var(--teal);background:var(--paper);border:1px solid var(--rule)} .ql-row button:hover{border-color:var(--teal)}
.qlive p{max-width:none} .ql-help{margin:6px 0 0;color:var(--muted);font-size:12.5px} .ql-msg{margin:6px 0 0;color:var(--amber);font-weight:700;font-size:13px} .ql-msg:empty{display:none}
.ql-diff{margin:6px 0 0;padding-left:18px;font-size:12.5px} .ql-diff ul{margin:2px 0 4px;padding-left:16px} .ql-diff:empty{display:none}
.ql-diff li b{font:600 11px var(--mono);margin-right:4px} .ql-chg b{color:#9A4A00} .ql-new b{color:var(--teal)} .ql-del b,.ql-warn b{color:#A12020}
.note-box .ql-diff{margin-top:4px}
@media print{.qlive{display:none!important}}
</style>"""


def blob(obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/json" id="qlbase">{s}</script>'


def assets(page, base):
    """page: 'dmw' | 'ocs'. base: 기준 견적 데이터(zones 등)"""
    return CSS + blob(dict(base, page=page, public=PUBLIC, sheetjs=SHEETJS, bl=BL, blno=BLNO)) + f"<script>{JS}</script>"


def dmw_panel(ocs_pages):
    links = " · ".join(f'<a href="{E(f)}">{E(t)}</a>' for f, t in ocs_pages)
    return f'''<div class="qlive" id="qlive">
  <div class="ql-row"><b>견적서 파일</b><span id="ql-cur">기준 견적: <b>{BL} 3건({BLNO})</b> — 페이지 작성 기준</span>
    <label class="ql-pick">견적서 파일 선택<input type="file" id="ql-file" accept=".xlsx,.xls,.xlsm,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel"></label>
    <button type="button" id="ql-reset" hidden>기준 견적으로 되돌리기</button></div>
  <p class="ql-help">이지로보틱스 견적서 엑셀(존별 시트, 항목1~7)을 고르거나 이 상자에 끌어다 놓으면 브라우저 안에서 읽어 존별 견적 표·요약·단가표·정밀조립 산정을 다시 그리고, 기준 견적과 달라진 품목을 '확인'으로 표시함. 고른 견적은 이 브라우저에 기억되어 OCS 시뮬레이션 Cell 3종({links})에도 자동 반영됨(각 페이지에서 직접 골라도 됨). 파일은 어디에도 전송되지 않음. 구매 필요성·쟁점 등 서술형 내용과 PDF·Word 저장본은 기준 견적 기준.</p>
  <p class="ql-msg" id="ql-msg" role="status" aria-live="polite"></p>
  <ul class="ql-diff" id="ql-diff"></ul>
</div>'''


def ocs_banner():
    return f'''<div class="qlive" id="qlive">
  <div class="ql-row"><b>견적서 파일</b><span id="ql-cur">기준 견적: <b>{BL}</b> — 페이지 작성 기준</span>
    <label class="ql-pick">견적서 파일 선택<input type="file" id="ql-file" accept=".xlsx,.xls,.xlsm,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel"></label>
    <button type="button" id="ql-reset" hidden>기준 견적으로 되돌리기</button></div>
  <p class="ql-help">이지로보틱스 견적서 엑셀(존별 시트, 항목1~7)을 고르거나 이 상자에 끌어다 놓으면 이 존 시트를 읽어 요약·KPI·구성품 표·지침 점검 수치·토폴로지(스캐너·운영 PC 탑재 SW)를 다시 그림. <a href="dmworks_zones.html#qlive">DMWorks 존별 옵션 구성</a> 페이지에서 고른 견적도 같은 브라우저라면 자동 반영됨. 파일은 어디에도 전송되지 않음. 공간 배치도(2장)·서술형 설명·견적서 원본·PDF·Word 저장본은 기준 견적({BL}) 기준.</p>
  <p class="ql-msg" id="ql-msg" role="status" aria-live="polite"></p>
  <ul class="ql-diff" id="ql-diff"></ul>
</div>'''
