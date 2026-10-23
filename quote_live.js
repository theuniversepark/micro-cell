/* 견적서 파일 선택 — DMWorks 존별 옵션 구성 페이지에서 고른 견적서 엑셀(.xlsx)을 브라우저 안에서 읽어(SheetJS) 견적 표·요약을 다시 그림.
   읽은 견적은 localStorage(ocsQuote.v1)에 남겨 OCS 시뮬레이션 Cell 3종 페이지도 같은 견적서 기준으로 다시 그림. 파일은 어디에도 전송하지 않음.
   기준 견적(빌드 시 데이터)은 #qlbase JSON. 업로드 품목은 기준 견적 품목과 키(옵션·장비 종류)로 대조해 같으면 기준 표기·검토 의견을 그대로 쓰고,
   수량·단가·구성이 바뀌거나 새로 생긴 품목은 '확인'으로 표시함. 서술형 설명·공간 배치도·PDF·Word 저장본은 기준 견적 그대로. */
(function (root) {
  'use strict';
  var KEY = 'ocsQuote.v2';  // v2: 10/23 양식(항목1~7, 항목 제목 gt) — v1 저장분은 읽지 않음
  var DETAIL = {CADI: 1, CADE: 1, OLP: 1, RRS: 1, PLC: 1, ACSO: 1, AIMSS: 1, AIMSC: 1};
  var ROBOT = {OLP: 1, RRS: 1, ACSO: 1, AIMSS: 1, AIMSC: 1};
  var LOCK = {LSV: 1, EGW: 1, NET: 1, RACK: 1, SEC: 1, LHW: 1, TSDB: 1}, SUBSCR = {DEL: 1, XCL: 1};
  var ZRE = [['A-1-4', /유연\s*제조/], ['A-2-5', /적응\s*가공/], ['A-4-5', /정밀\s*검사/]];
  var B = null, PUB = false;

  // ------------------------------------------------------------------ 공통
  function E(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#x27;'); }
  function k(n) { return Number(n).toLocaleString('en-US', {maximumFractionDigits: 0}); }
  function km(n) { return PUB ? '비공개' : k(n); }
  function won(n) { return PUB ? '비공개' : k(n) + '천원'; }
  function sum(a, f) { return a.reduce(function (s, x) { return s + (f(x) || 0); }, 0); }
  function pad(n) { return ('0' + n).slice(-2); }
  function str(v) {
    if (v == null) return '';
    if (v instanceof Date) { v = new Date(v.getTime() + 432e5); return v.getFullYear() + '.' + pad(v.getMonth() + 1) + '.' + pad(v.getDate()); }  // 엑셀 날짜가 시간대 탓에 전날 23시대로 읽히는 경우 반올림
    return String(v).trim();
  }
  function sq(v) { return str(v).replace(/\s+/g, ''); }
  function num(v) {
    if (typeof v === 'number') return isFinite(v) ? v : null;
    var s = str(v).replace(/[,\s₩원]/g, '');
    return s !== '' && isFinite(s) ? Number(s) : null;
  }
  function norm(s) { return str(s).toUpperCase().replace(/[^0-9A-Z가-힣]/g, ''); }
  function oneLine(s) { return str(s).split(/\n/).map(function (x) { return x.trim(); }).filter(Boolean).join(' · '); }
  function gtNorm(s) { return str(s).replace(/ㆍ/g, '·').replace(/\s+/g, ' ').trim(); }
  function toks(label) {
    var s = str(label), m = s.match(/\(([^)]*)\)\s*$/) || s.match(/-\s*([^-]+)$/);
    return m ? m[1].split(/[,·]/).map(function (t) { return t.trim().toUpperCase(); }).filter(Boolean) : [];
  }

  // ------------------------------------------------------------------ 엑셀 → 견적 (단위 천원)
  function zoneOf(texts) {
    for (var i = 0; i < texts.length; i++) for (var j = 0; j < ZRE.length; j++) if (ZRE[j][1].test(texts[i] || '')) return ZRE[j][0];
    return null;
  }
  function fmtDate(v) {
    var s = str(v), m = s.match(/(\d{4})\D+(\d{1,2})\D+(\d{1,2})/);
    return m ? m[1] + '.' + pad(m[2]) + '.' + pad(m[3]) : s;
  }
  function find(r, re, not) {
    for (var i = 0; i < r.length; i++) if (i !== not && re.test(sq(r[i]))) return i;
    return -1;
  }

  /* 견적서 시트 1장(2차원 배열) → {id, no, date, title, total, ga, items:[{g, gt, cat, label, q, u}], warn}
     '항목N. …' 절 머리 → 표 머리(수량·단가·금액) → 품목 행 → '항목N. 소계·합계', 일반관리비 절, 마지막 '합계' 행 순서를 따름.
     10/23 양식은 첫 열이 번호(1.1 · 3.2.1 …) — 3단계 이하 하위 구성품 중 단가 없는 행은 건너뛰고, 금액이 '무상'인 행은 0원 품목으로 읽음.
     10/15 양식(첫 열이 분류, '상세'·'견적가' 열)도 읽음 */
  function parseSheet(name, rows) {
    var z = {sheet: name, items: [], warn: [], ga: null, total: null}, sec = 0, gt = '', cat = '', col = null, sub = {}, head = null, gaSec = 0;
    rows.forEach(function (r) {
      r = r || [];
      var a = str(r[0]), as = sq(r[0]), m, v1 = '';
      for (var i = 1; i < r.length && !v1; i++) v1 = str(r[i]);
      if (as === '과제명' || as === '건명') z.title = v1;
      else if (as === '견적번호') z.no = v1;
      else if (as === '견적일자') z.date = fmtDate(r.slice(1).filter(function (x) { return x != null && x !== ''; })[0]);
      else if (/^견적금액/.test(as) && (m = v1.match(/₩\s*([\d,]+)/))) head = num(m[1]) / 1000;
      if (find(r, /^수량$/) >= 0) {
        var q = find(r, /^수량$/), u = find(r, /^단가$|기준금액/), am = find(r, /견적가/);
        if (am < 0) am = find(r, /금액/, u);
        var d = find(r, /상세|세부품목|세부내용/);
        col = {q: q, u: u, a: am, d: d < 0 ? 1 : d};
        return;
      }
      if ((m = as.match(/^항목(\d+)\./))) {
        if (/합계|소계/.test(as)) { if (col && num(r[col.a]) != null) sub[m[1]] = num(r[col.a]) / 1000; sec = 0; }
        else { sec = +m[1]; gt = gtNorm(a); cat = ''; if (/일반관리비/.test(a)) gaSec = sec; }
        return;
      }
      if (as === '합계' && col && num(r[col.a]) != null) { z.total = num(r[col.a]) / 1000; return; }
      if (!col || as === '항목' || !sec) return;
      if (sec === gaSec) { if (/일반관리비/.test(a) && num(r[col.a]) != null) z.ga = num(r[col.a]) / 1000; return; }
      var no = /^\d+(\.\d+)*$/.test(as) ? as : '', lv = no ? no.split('.').length : 1, qv = num(r[col.q]), uv = num(r[col.u]);
      var label = str(r[col.d]), sect = gt.replace(/^항목\d+\.\s*/, '');
      if (!label) label = r.slice(1, col.q).map(str).filter(Boolean).join(' ');
      if (qv != null && uv != null && (uv > 0 || lv <= 2)) {
        if (!no) cat = a || cat;  // 10/15 양식: 첫 열이 분류(빈 칸은 위 분류를 이어 씀)
        z.items.push({g: sec, gt: gt, cat: no ? sect : cat, label: label || a || cat, q: qv, u: uv / 1000});
      } else if (!no && a && /무상/.test(str(r[col.a]))) z.items.push({g: sec, gt: gt, cat: a, label: label || a, q: 1, u: 0});
    });
    if (!z.items.length) return null;
    z.id = zoneOf([z.title, name, z.no]);
    Object.keys(sub).forEach(function (n) {
      var s = +n === gaSec ? z.ga : sum(z.items, function (x) { return x.g === +n ? x.q * x.u : 0; });
      if (s != null && Math.abs(s - sub[n]) > 1) z.warn.push(name + ': 항목' + n + ' 품목 합 ' + k(s) + '천원 ≠ 견적서 소계 ' + k(sub[n]) + '천원');
    });
    var pre = sum(z.items, function (x) { return x.q * x.u; });
    if (z.ga == null) {
      z.ga = sum(z.items, function (x) { return x.g <= 3 ? x.q * x.u : 0; }) * 0.1;
      z.warn.push(name + ': 일반관리비 행이 없어 (항목1+2+3)의 10%로 계산');
    }
    if (z.total == null) z.total = head;
    if (z.total == null) { z.total = Math.floor((pre + z.ga) / 10000) * 10000; z.warn.push(name + ': 합계 행이 없어 천만 원 미만 절삭으로 계산'); }
    var gap = pre + z.ga - z.total;
    if (gap < -1 || gap >= 10000) z.warn.push(name + ': 항목 합계 ' + k(pre + z.ga) + '천원과 견적 합계 ' + k(z.total) + '천원 차이가 단위절삭(천만 원 미만)보다 큼');
    return z;
  }

  function parseBook(sheets, fileName) {
    var out = {name: fileName, at: new Date().toISOString(), zones: {}, warn: []};
    sheets.forEach(function (s) {
      var z = parseSheet(s.name, s.rows);
      if (!z) return;
      out.warn = out.warn.concat(z.warn);
      delete z.warn;
      if (!z.id) out.warn.push(s.name + ': 어느 존 견적인지 알 수 없어 제외(과제명·시트명에 유연제조·적응가공·정밀검사가 있어야 함)');
      else if (out.zones[z.id]) out.warn.push(s.name + ': ' + z.id + ' 견적이 이미 있어 제외');
      else out.zones[z.id] = z;
    });
    return out;
  }

  // ------------------------------------------------------------------ 품목 키·기준 견적 대조
  /* 키는 품목명으로만 정함 — 존마다 견적서 항목 구성이 달라(정밀검사는 운영 PC가 항목2, DM-Monitoring이 항목3) 항목 번호는 쓰지 않음 */
  var SWK = [[/AMC|ANNUAL\s*MAINT|유지보수/i, 'AMC'], [/OFFLINE\s*PROGRAM|ACS\s*OLP/i, 'ACSO'], [/AUTO\s*CONTROL|\bACS\b/i, 'ACSB'], [/AIMS.*SIM/i, 'AIMSS'], [/AIMS.*CONT/i, 'AIMSC'],
    [/TESCAR/i, 'TES'], [/^PIA\b|PREDICTIVE/i, 'PIA'], [/DELMIA/i, 'DEL'], [/X-?CLOUD|XCELERATOR/i, 'XCL'], [/경량화|표준\s*변환/, 'LWC'], [/CAD\s*IMPORT/i, 'CADI'],
    [/CAD\s*EXPORT/i, 'CADE'], [/\bRRS\b/i, 'RRS'], [/\bOLP\b/i, 'OLP'], [/POINT\s*CLOUD/i, 'PC'], [/MULTIPLE\s*PROCESS/i, 'MP'], [/PLC\s*SIM/i, 'PLC'],
    [/PLUG-?IN.*USER/i, 'PIU'], [/PLUG-?IN/i, 'PID'], [/\bUSD\b/i, 'USD'], [/LIVE\s*EDIT/i, 'LE'], [/DM-?\s*MONITORING/i, 'DMON'], [/DMWORKS\s*BASE|^BASE$/i, 'BASE']];
  var HWR = [[/스캐너|SCANNER/i, 'SCN'], [/LOCAL\s*SERVER|로컬\s*서버/i, 'LSV'], [/EDGE\s*GATE/i, 'EGW'], [/NETWORK|네트워크/i, 'NET'], [/기반\s*시설/, 'RACK'],
    [/TSDB/i, 'TSDB'], [/보안|IAM|PKI/i, 'SEC'], [/연산\s*서버|GPU/i, 'GPU'], [/모니터링/, 'MON'], [/노트북/, 'NB'], [/운영\s*PC/i, 'OPC'],
    [/데이터\s*(처리\s*)?서버/, 'LHW'], [/교육|기술\s*지원/, 'TS']];
  var SWSET = {};
  SWK.forEach(function (x) { SWSET[x[1]] = 1; });
  function isSW(key) { return !!SWSET[key]; }
  function isTS(key) { return /^TS/.test(key || ''); }
  function keyOf(g, cat, label) {
    var c = str(cat), l = str(label), i;
    if (/CUSTOMIZING/i.test(l)) return /ACS/i.test(l) ? 'TS4' : (/PLUG-?IN/i.test(l) ? 'TS3' : (/시각화|UI/i.test(l) ? 'TS2' : 'TS1'));  // 10/15 맞춤 개발
    if (/유지보수|^AMC/i.test(c)) return 'AMC';
    for (i = 0; i < SWK.length; i++) if (SWK[i][0].test(l)) return SWK[i][1];
    for (i = 0; i < HWR.length; i++) if (HWR[i][0].test(l)) return HWR[i][1];
    return 'X:' + norm(l);
  }
  function gtOf(m) { return m.gt || (m.base && m.base.gt) || ('항목' + m.g); }

  /* 기준 견적 행(base: {g, gt, cat, label, q, u, …표기}) ↔ 업로드 품목 대조 — 같은 키·같은 항목을 먼저, 없으면 같은 키(항목 이동).
     st: same(수량·단가·구성 같음) · chg(바뀜, diff에 내역) · new(기준에 없음). removed: 업로드에 없는 기준 품목 */
  function merge(base, up) {
    var bk = base.map(function (r) { return {r: r, key: keyOf(r.g, r.cat, r.label), used: false}; });
    if (!up) return {live: false, rows: bk.map(function (b) { return {g: b.r.g, gt: b.r.gt, cat: b.r.cat, label: b.r.label, key: b.key, q: b.r.q, u: b.r.u, base: b.r, st: 'same', diff: []}; }), removed: []};
    var rows = up.items.map(function (it) {
      var key = keyOf(it.g, it.cat, it.label), diff = [];
      var take = function (sameG) {
        for (var i = 0; i < bk.length; i++) if (!bk[i].used && bk[i].key === key && (!sameG || bk[i].r.g === it.g)) { bk[i].used = true; return bk[i]; }
        return null;
      };
      var b = take(true) || take(false);
      if (b) {
        var r = b.r;
        if (r.g !== it.g) diff.push('항목' + r.g + '→' + it.g);
        if (Math.abs(r.q - it.q) > 1e-9) diff.push('수량 ' + r.q + '→' + it.q);
        if (Math.abs(r.u - it.u) > 0.0005) diff.push(PUB && isSW(key) ? '단가 변경' : '단가 ' + k(r.u) + '→' + k(it.u));
        if (DETAIL[key] && toks(r.label).join('·') !== toks(it.label).join('·')) diff.push('구성 ' + toks(r.label).join('·') + '→' + toks(it.label).join('·'));
        if (key === 'SCN' && norm(r.label) !== norm(it.label)) diff.push('모델 변경');
      }
      return {g: it.g, gt: it.gt, cat: it.cat, label: it.label, key: key, q: it.q, u: it.u, base: b ? b.r : null, st: b ? (diff.length ? 'chg' : 'same') : 'new', diff: diff};
    });
    return {live: true, rows: rows, removed: bk.filter(function (b) { return !b.used; }).map(function (b) { return b.r; })};
  }

  function amcText(rows, amc) {
    var sw = sum(rows, function (x) { return isSW(x.key) && x.key !== 'AMC' && !SUBSCR[x.key] ? x.q * x.u : 0; });  // 외산 1년 구독은 AMC 대상 아님
    return '연 ' + (sw ? Math.round(amc.u / sw * 1000) / 10 : 0) + '% × ' + amc.q + '년';
  }
  function itemName(m) {
    if (m.base && m.base.dm) return m.base.dm.nm;
    if (B.names && B.names[m.key]) return B.names[m.key];
    if (m.base && m.base.o) return m.base.o.nm;
    return oneLine(m.label);
  }
  function diffList(mz) {
    var out = [];
    mz.rows.forEach(function (m) {
      if (m.st === 'chg') out.push({t: 'chg', s: itemName(m) + ' — ' + m.diff.join(', ')});
      if (m.st === 'new') out.push({t: 'new', s: itemName(m) + ' — 추가 (수량 ' + m.q + (PUB && isSW(m.key) ? '' : ', 금액 ' + k(m.q * m.u) + '천원') + ')'});
    });
    mz.removed.forEach(function (r) { out.push({t: 'del', s: itemName({base: r, g: r.g, label: r.label, key: keyOf(r.g, r.cat, r.label)}) + ' — 삭제'}); });
    return out;
  }
  function diffHtml(d) {
    var T = {chg: '변경', new: '추가', del: '삭제'};
    return d.map(function (x) { return '<li class="ql-' + x.t + '"><b>' + T[x.t] + '</b> ' + E(x.s) + '</li>'; }).join('');
  }

  // ------------------------------------------------------------------ 저장 (브라우저 안에서만)
  function load() {
    try { var s = root.localStorage.getItem(KEY); return s ? JSON.parse(s) : null; } catch (e) { return null; }
  }
  function save(q) {
    try { if (q) root.localStorage.setItem(KEY, JSON.stringify(q)); else root.localStorage.removeItem(KEY); return true; } catch (e) { return false; }
  }

  // ------------------------------------------------------------------ DMWorks 존별 옵션 구성 페이지
  var TAG = {ok: ['적합', 'ok'], chk: ['확인', 'chk'], adj: ['조정', 'adj']};
  function tag(v) { return '<span class="tag ' + TAG[v][1] + '">' + TAG[v][0] + '</span>'; }

  function dmTemplates() {
    var t = {};
    B.zones.forEach(function (z) { z.rows.forEach(function (r) { var key = keyOf(r.g, r.cat, r.label); if (!t[key]) t[key] = r.dm; }); });
    return t;
  }
  function dmRows(mz, tm) {
    return mz.rows.map(function (m) {
      if (m.st === 'same') return {grp: gtOf(m), nm: m.base.dm.nm, dd: m.base.dm.dd, q: m.q, u: m.u, v: m.base.dm.v, why: m.base.dm.why, key: m.key, g: m.g};
      var t = m.base ? m.base.dm : tm[m.key], grp = gtOf(m), nm, dd;
      if (B.names[m.key]) { nm = B.names[m.key]; dd = DETAIL[m.key] ? toks(m.label).join('·') : (m.key === 'AMC' ? amcText(mz.rows, m) : ''); }
      else if (t) { nm = t.nm; dd = t.dd; }
      else { nm = oneLine(m.label); dd = ''; }
      var why = m.st === 'new' ? '기준 견적에 없던 품목 — 존 목적에 맞는지 검토 필요'
        : '기준 견적 대비 ' + m.diff.join(', ') + (t && t.why ? ' · 기존 의견: ' + t.why : '');
      return {grp: grp, nm: nm, dd: dd, q: m.q, u: m.u, v: 'chk', why: why, key: m.key, g: m.g};
    });
  }
  function quoteTable(rs, z) {
    var h = [], cur = null, mg = {};
    rs.forEach(function (r) { if (isSW(r.key)) mg[r.grp] = 1; });
    var fm = function (g) { return mg[g] ? km : k; };  // SW 품목이 든 항목은 공개본에서 가림
    rs.forEach(function (r) {
      if (r.grp !== cur) {
        cur = r.grp;
        h.push('<tr class="grp"><th colspan="4" scope="rowgroup">' + E(cur) + '</th><td class="num">' + fm(cur)(sum(rs, function (x) { return x.grp === cur ? x.q * x.u : 0; })) + '</td><td colspan="2"></td></tr>');
      }
      h.push('<tr><td class="nm">' + E(r.nm) + '</td><td>' + E(r.dd) + '</td><td class="q"><b>' + r.q + '</b></td><td class="num">' + fm(r.grp)(r.u) + '</td>'
        + '<td class="num">' + fm(r.grp)(r.q * r.u) + '</td><td>' + tag(r.v) + '</td><td>' + E(r.why) + '</td></tr>');
    });
    var foot = '<tr class="tot"><th colspan="4">항목7. 일반관리비·기업이윤 ((항목1 + 항목2 + 항목3)의 10%, 견적서 기재값)</th><td class="num">' + km(z.ga) + '</td><td colspan="2"></td></tr>'
      + '<tr class="tot strong"><th colspan="4">견적 합계 (단위절삭 후)</th><td class="num">' + km(z.total) + '</td><td colspan="2">' + E(z.no) + '</td></tr>';
    return '<div class="tbl-wrap"><table class="bom"><thead><tr><th>품목</th><th>상세(포맷·컨트롤러·사양)</th><th style="text-align:center">수량</th>'
      + '<th class="r">단가</th><th class="r">금액</th><th>검토</th><th>검토 의견</th></tr></thead>'
      + '<tbody>' + h.join('') + '</tbody><tfoot>' + foot + '</tfoot></table></div>';
  }
  function parts(rs, z) {
    /* 품목 성격별 — SW(DMWorks·외산·AMC) · OCS HW(나머지) · 로컬 HW·보안 · 기술지원 · 일반관리비 */
    var f = function (c) { return sum(rs, function (x) { return c(x.key) ? x.q * x.u : 0; }); };
    return [f(isSW), f(function (y) { return !isSW(y) && !LOCK[y] && !isTS(y); }), f(function (y) { return !!LOCK[y]; }), f(isTS), z.ga];
  }
  function summaryTable(Z, pzt) {
    var F = [km, k, k, k, km], t = [0, 0, 0, 0, 0, 0], rows = [];
    Z.forEach(function (x) {
      var v = parts(x.rs, x.meta).concat([x.meta.total]);
      v.forEach(function (n, i) { t[i] += n; });
      rows.push('<tr><td><a href="#' + x.z.slug + '">' + E(x.z.id) + '</a></td><td class="nm">' + E(x.z.name) + '</td><td class="note">' + E(x.meta.no) + '</td>'
        + F.map(function (f, i) { return '<td class="num">' + f(v[i]) + '</td>'; }).join('') + '<td class="num"><b>' + km(v[5]) + '</b></td></tr>');
    });
    rows.push('<tr><td><a href="#z3">A-3</a></td><td class="nm">정밀조립존</td><td class="note">견적 없음 · 견적 단가로 산정</td>'
      + '<td class="num">' + km(pzt) + '</td>' + new Array(5).join('<td class="num">–</td>') + '<td class="num">' + km(pzt) + '</td></tr>');
    rows.push('<tr class="tot strong"><th colspan="3">견적 합계 (3개 존)</th>' + F.concat([km]).map(function (f, i) { return '<td class="num">' + f(t[i]) + '</td>'; }).join('') + '</tr>');
    return '<div class="tbl-wrap"><table class="bom"><thead><tr><th>존</th><th>구분</th><th>견적번호</th><th class="r">SW(DMWorks·외산·AMC)</th><th class="r">OCS HW(서버·PC·모니터링·스캐너)</th>'
      + '<th class="r">로컬 HW·보안</th><th class="r">기술지원</th><th class="r">일반관리비·이윤</th><th class="r">견적 합계</th></tr></thead>'
      + '<tbody>' + rows.join('') + '</tbody></table></div><p class="note-box">단위 천원. 열은 품목 성격별로 다시 묶은 것으로 견적서 항목 번호와 다름. 일반관리비·이윤은 견적서 기재값. 견적 합계는 업체 단위절삭 후 금액.</p>';
  }
  function unitOf(Z, key) {
    for (var i = 0; i < Z.length; i++) for (var j = 0; j < Z[i].rs.length; j++) if (Z[i].rs[j].key === key) return Z[i].rs[j].u;
    return null;
  }
  function pzRows(Z) {
    return B.pz.map(function (p) { var u = unitOf(Z, p.key); return {nm: p.nm, q: p.q, why: p.why, u: u == null ? p.u : u, base: u == null}; });
  }
  function pzTable(rs, live) {
    var tot = sum(rs, function (r) { return r.u * r.q; }), nb = rs.filter(function (r) { return r.base; }).length;
    return '<div class="tbl-wrap"><table class="bom"><thead><tr><th>옵션</th><th style="text-align:center">수량</th><th class="r">단가</th><th class="r">금액</th><th>쓰는 이유</th></tr></thead><tbody>'
      + rs.map(function (r) { return '<tr><td class="nm">' + E(r.nm) + '</td><td class="q"><b>' + r.q + '</b></td><td class="num">' + km(r.u) + '</td><td class="num">' + km(r.u * r.q) + '</td><td>' + E(r.why) + '</td></tr>'; }).join('')
      + '<tr class="tot strong"><th colspan="3">합계 (SW만, 일반관리비·AMC 제외)</th><td class="num">' + km(tot) + '</td><td>'
      + (live ? '업로드 견적 단가 적용' + (nb ? ' (견적에 없는 ' + nb + '종은 기준 견적 단가)' : '') : B.bl + ' 단가(정가×57.2%) 적용') + '</td></tr></tbody></table></div>';
  }

  function renderDmw(q, mzs) {
    var tm = dmTemplates(), Z = B.zones.map(function (z, i) {
      var up = q && q.zones[z.id];
      return {z: z, up: up, mz: mzs[i], meta: up || z, rs: dmRows(mzs[i], tm)};
    });
    Z.forEach(function (x) {
      var s = x.z.slug;
      setH('ql-qt-' + s, quoteTable(x.rs, x.meta));
      setT('ql-zeb-' + s, x.z.id + ' · ' + x.z.purpose + ' · ' + x.meta.no);
      setT('ql-zh2-' + s, x.z.name + ' · 견적 ' + won(x.meta.total));
      setH('ql-zh3-' + s, (x.up ? '업로드 견적' : '기준 견적(' + B.bl + ')') + ' 구성과 검토 <span class="chg">(단위 천원 · ' + E(x.meta.no) + (x.meta.date ? ' · ' + E(x.meta.date) : '') + ')</span>');
      var d = diffList(x.mz);
      setH('ql-zchg-' + s, x.up ? '<b>기준 견적(' + B.bl + ', ' + E(x.z.no) + ') 대비</b> ' + (d.length ? '변경 ' + d.filter(function (y) { return y.t === 'chg'; }).length + '건 · 추가 ' + d.filter(function (y) { return y.t === 'new'; }).length
        + '건 · 삭제 ' + d.filter(function (y) { return y.t === 'del'; }).length + '건' + (PUB ? '' : ' · 합계 ' + k(x.z.total) + ' → ' + k(x.meta.total) + '천원') + '<ul class="ql-diff">' + diffHtml(d) + '</ul>' : '— 품목·수량·단가가 같음')
        : '업로드한 견적서에 이 존 시트가 없어 기준 견적(' + B.bl + ')을 그대로 표시함.');
    });
    var pz = pzRows(Z), pzt = sum(pz, function (r) { return r.u * r.q; }), T = sum(Z, function (x) { return x.meta.total; });
    setH('ql-sumtbl', summaryTable(Z, pzt));
    setH('ql-pz', pzTable(pz, true));
    setT('ql-sumh2', '업로드 견적 3개 존 · 합계 ' + won(T));
    setT('ql-eb', '업로드 견적서 「' + q.name + '」 기준(기준 견적 ' + B.bl + '와 대조)');
    var B0 = sum(B.zones, function (z) { return z.total; });
    setT('ql-k-ov', '업로드 견적서 「' + q.name + '」 기준 — ' + Z.map(function (x) { return x.z.short + ' ' + (PUB ? '' : k(x.meta.total) + ' ') + '(' + x.meta.no + (x.up ? '' : ', 기준 유지') + ')'; }).join(' · ')
      + (PUB ? '. 견적 합계는 공개본에서 비공개.' : ' = 합계 ' + k(T) + '천원 (기준 ' + B.bl + ' ' + k(B0) + '천원 대비 ' + (T >= B0 ? '+' : '') + k(T - B0) + '천원).'));
    var all = [].concat.apply([], Z.map(function (x) { return x.rs; })), amt = function (f) { return sum(all, function (r) { return f(r) ? r.q * r.u : 0; }); };
    var loc = amt(function (r) { return LOCK[r.key]; }), srv = amt(function (r) { return r.key === 'GPU'; }), amc = amt(function (r) { return r.key === 'AMC'; }), scn = amt(function (r) { return r.key === 'SCN'; });
    var sub = amt(function (r) { return SUBSCR[r.key]; });
    var nsrv = sum(all, function (r) { return r.key === 'GPU' ? r.q : 0; }), nscn = sum(all, function (r) { return r.key === 'SCN' ? r.q : 0; });
    var yrs = all.filter(function (r) { return r.key === 'AMC'; }).map(function (r) { return r.q; })[0];
    setT('ql-k-big', PUB ? '로컬 HW 3존 ' + k(loc) + ' · 연산 서버 ' + nsrv + '대 ' + k(srv) + ' · 외산 구독 ' + k(sub) + ' · 스캐너 ' + nscn + '대 ' + k(scn) + '천원 · AMC ' + (yrs || 0) + '년(DMWorks SW 기준이라 비공개)'
      : '로컬 HW 3존 ' + k(loc) + ' · 연산 서버 ' + nsrv + '대 ' + k(srv) + ' · AMC ' + (yrs || 0) + '년 ' + k(amc) + ' · 외산 구독 ' + k(sub) + ' · 스캐너 ' + nscn + '대 ' + k(scn) + '천원 — 다섯 가지가 전체의 약 ' + Math.round((loc + srv + amc + sub + scn) / T * 100) + '%');
    // 단가·제품 표: 견적 단가·비율·존별 수량
    Array.prototype.forEach.call(document.querySelectorAll('[data-qlu]'), function (td) {
      var key = td.getAttribute('data-qlu'), u = unitOf(Z, key);
      if (u != null) td.innerHTML = '<b>' + km(u) + '</b>';
      var r = document.querySelector('[data-qlr="' + key + '"]');
      if (r && u != null && B.list[key]) r.textContent = (Math.round(u / B.list[key] * 1000) / 10).toFixed(1) + '%';
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-qlq]'), function (td) {
      var p = td.getAttribute('data-qlq').split('|'), x = Z.filter(function (y) { return y.z.id === p[1]; })[0];
      td.textContent = sum(x.rs, function (r) { return r.key === p[0] ? r.q : 0; }) || '–';
    });
    return Z;
  }

  // ------------------------------------------------------------------ OCS 시뮬레이션 Cell 페이지
  var CHKX = {chg: ['변경 확인', 'chk'], new: ['신규 품목', 'adj']};
  var CHKX_NOTE = {chg: '기준 견적 대비 수량·단가·구성 변경 — 사양·근거 재확인', new: '기준 견적에 없던 품목 — 일반 명칭·세부 사양 정리 필요'};
  function chkTag(c) { var t = B.chk[c] || CHKX[c]; return '<span class="tag ' + t[1] + '">' + t[0] + '</span>'; }
  var MG = {};  // SW 품목이 든 견적서 항목 — 공개본에서 금액을 가림 (renderOcs가 채움)
  function gk(g) { return MG[g] ? km : k; }

  function ocsTemplate(key, label) {
    for (var i = 0; i < B.tmpl.length; i++) {
      var t = B.tmpl[i];
      if (keyOf(t.g, t.cat, t.label) === key && (key !== 'SCN' || norm(t.label) === norm(label))) return t;
    }
    return null;
  }
  function ocsPres(m, mz) {
    if (m.st === 'same') return {sym: m.base.o.sym, nm: m.base.o.nm, sp: m.base.o.sp, unit: m.base.o.unit, node: m.base.o.node, chk: m.base.o.chk, lab: m.base.o.lab, cat: m.base.cat};
    var t = m.base || ocsTemplate(m.key, m.label), to = t && t.o, gen = B.gen[m.key], p;
    if (gen) {
      var det = '', n = toks(m.label).length || m.q, sp = gen[1];
      if (m.key === 'CADI' || m.key === 'CADE') det = toks(m.label).join('·') + ' ' + n + '종';
      else if (ROBOT[m.key]) det = 'Cell 로봇 제어기 ' + n + '종';
      else if (m.key === 'PLC') det = 'Cell PLC ' + n + '종';
      if (m.key === 'AMC') sp = sp.replace(/연 [\d.]+% × \d+년/, amcText(mz.rows, m));
      p = {sym: m.key, nm: gen[0], sp: det ? det + ' — ' + sp : sp, node: gen[2], unit: m.key === 'AMC' ? '년' : (SUBSCR[m.key] ? '년 구독' : (m.q === 1 ? '카피' : '모듈')),
        chk: ROBOT[m.key] || m.key === 'PLC' ? 'maker' : (m.key === 'AMC' ? 'amc' : (SUBSCR[m.key] ? 'sub' : (m.key === 'LWC' ? 'prod' : 'ok')))};
    } else if (to) p = {sym: to.sym, nm: to.nm, sp: to.sp, node: to.node, unit: to.unit, chk: to.chk};
    else {
      var scn = m.key === 'SCN';
      p = {sym: scn ? 'SCN' : (isSW(m.key) ? 'SW' : 'HW'), nm: scn ? '3D 스캐너 (HW·운영 SW 포함)' : oneLine(m.label).split(' · ')[0],
        sp: scn ? '측정 범위·정확도·스캔 속도는 견적서에 없음 — 규격서 기재 필요' : '견적서 기재 품목 — 일반 명칭·세부 사양 정리 필요',
        node: scn ? 'SCN' : null, unit: isSW(m.key) ? (m.q === 1 ? '카피' : '모듈') : (scn ? '대' : '식'), chk: 'ok'};
    }
    var bc = m.base ? m.base.o.chk : p.chk;
    p.chk = m.st === 'chg' ? (bc !== 'ok' ? bc : 'chg') : (p.chk !== 'ok' ? p.chk : 'new');
    p.lab = oneLine(m.label);
    p.cat = m.base ? m.base.cat : (B.catOf[m.key] || (isSW(m.key) ? 'DMWorks' : oneLine(str(m.cat).replace(/,\s*\n/g, '·'))));
    return p;
  }
  function ocsRows(mz) {
    var out = [], cnt = {}, done = {};
    mz.rows.forEach(function (m) {
      var n = cnt[m.g] = (cnt[m.g] || 0) + 1, no = m.g + '-' + n, p = ocsPres(m, mz), g = gtOf(m), ss = B.sub[m.key];
      out.push({g: g, no: no, sym: p.sym, nm: p.nm, sp: p.sp, q: m.q, unit: p.unit, u: m.u, amt: m.q * m.u, lab: p.lab, node: p.node, chk: p.chk, sub: 0, cat: p.cat, key: m.key});
      if (ss && !done[m.key]) {  // 1식 품목의 하위 구성품 (기준 견적 기준)
        done[m.key] = 1;
        ss.forEach(function (s) { out.push({g: g, no: no + '-' + s.sfx, sym: s.sym, nm: s.nm, sp: s.sp, q: s.q, unit: s.unit, u: null, amt: null, lab: s.lab, node: s.node, chk: s.chk, sub: s.sub, cat: p.cat}); });
      }
    });
    return out;
  }
  function itemTable(rows, z) {
    var gsum = {}, swBy = {}, csum = {}, ccnt = {}, push = function (o, key, v) { (o[key] = o[key] || []).push(v); };
    rows.forEach(function (r) { if (r.amt != null) gsum[r.g] = (gsum[r.g] || 0) + r.amt; });
    rows.forEach(function (r) { if (B.gen[r.sym] && r.node && !r.sub) push(swBy, r.node, r.no); });
    rows.forEach(function (r) { if (r.sym === 'SEC' || r.sym === 'TSDB') push(swBy, 'DPS', r.no); });
    rows.forEach(function (r) { var c = r.g + '|' + r.cat; csum[c] = (csum[c] || 0) + (r.amt || 0); ccnt[c] = (ccnt[c] || 0) + (r.sub ? 0 : 1); });
    var body = [], cur = null, ccur = null, seen = {}, cn = 0;
    rows.forEach(function (r) {
      if (r.g !== cur) { cur = r.g; body.push('<tr class="grp"><th colspan="6" scope="rowgroup">' + E(r.g) + '</th><td class="num">' + gk(r.g)(gsum[r.g] || 0) + '</td><td colspan="2"></td></tr>'); }
      var c = r.g + '|' + r.cat;
      if (c !== ccur) {
        ccur = c; cn++;
        body.push('<tr class="cat" data-cat="c' + cn + '" tabindex="0" role="button" aria-expanded="false" title="눌러서 접기·펼치기">'
          + '<td class="sym"><span class="tw" aria-hidden="true">▸</span>견적서 항목</td><th colspan="5" scope="rowgroup">' + E(r.cat) + ' <span>· ' + ccnt[c] + '품목</span></th>'
          + '<td class="num">' + gk(r.g)(csum[c]) + '</td><td colspan="2"></td></tr>');
      }
      var anchor = B.anch.indexOf(r.sym) >= 0 ? r.sym : null, rid = '';
      if (anchor && !seen[anchor]) { rid = ' id="it-' + anchor + '"'; seen[anchor] = 1; }
      var nmh = E(r.nm);
      if (anchor && swBy[anchor]) {
        var lst = swBy[anchor];
        nmh += '<span class="where">탑재: ' + E(lst.length <= 3 ? lst.join(', ') : 'SW ' + lst.length + '종 (' + lst[0] + '~' + lst[lst.length - 1] + ')')
          + ' <a href="#r-' + lst[0] + '" class="tolink" data-flash="' + lst.map(function (x) { return 'r-' + x; }).join(',') + '">↓</a></span>';
      }
      if (anchor) nmh += ' <a href="#topo-' + anchor + '" class="tolink">도면 ↑</a>';
      else if (r.node) nmh += '<span class="where">설치: ' + E(B.nodes[r.node] || r.node) + ' <a href="#topo-' + r.node + '" class="tolink">↑</a></span>';
      var cls = r.sub === 2 ? ' class="subrow sub2 cx"' : (r.sub ? ' class="subrow cx"' : ' class="cx"');
      if (rid) body.push('<tr id="r-' + r.no + '" hidden></tr>');
      body.push('<tr' + (rid || ' id="r-' + r.no + '"') + cls + ' data-in="c' + cn + '"><td class="sym">' + E(r.no) + '</td><td class="nm">' + nmh + '</td><td class="spec">' + E(r.sp) + '</td>'
        + '<td class="q"><b>' + E(String(r.q)) + '</b></td><td class="u">' + E(r.unit) + '</td>'
        + '<td class="num">' + (r.u != null ? gk(r.g)(r.u) : '–') + '</td><td class="num">' + (r.amt != null ? gk(r.g)(r.amt) : '미구분') + '</td>'
        + '<td>' + chkTag(r.chk) + '<span class="where">' + E(B.chkNote[r.chk] || CHKX_NOTE[r.chk] || '') + '</span></td><td class="note">' + E(r.lab) + '</td></tr>');
    });
    var amt = rows.filter(function (r) { return r.amt != null; }), pre = sum(amt, function (r) { return r.amt; });
    var base = sum(amt, function (r) { return /^항목[123]\./.test(r.g) ? r.amt : 0; });
    var foot = '<tr class="tot"><th colspan="6">항목7. 일반관리비·기업이윤 — (항목1 + 항목2 + 항목3)' + (PUB ? '' : ' ' + k(base)) + '의 10%, 견적서 기재값' + (Math.abs(base * 0.1 - z.ga) > 0.5 ? ' (산식에서 ' + k(base * 0.1 - z.ga) + '천원 차감)' : '') + '</th><td class="num">' + km(z.ga) + '</td><td colspan="2"></td></tr>'
      + '<tr class="tot"><th colspan="6">합계 (단위절삭 전)</th><td class="num">' + km(pre + z.ga) + '</td><td colspan="2"></td></tr>'
      + '<tr class="tot strong"><th colspan="6">견적 합계 (단위절삭 후)</th><td class="num">' + km(z.total) + '</td><td colspan="2">' + E(z.no) + '</td></tr>';
    return '<div class="tbl-wrap"><table class="bom wide2"><thead><tr><th>번호</th><th>구성품 (일반 명칭)</th><th>세부 사양</th><th style="text-align:center">수량</th><th>단위</th>'
      + '<th class="r">단가</th><th class="r">금액</th><th>지침 점검</th><th>견적서 기재 품목 <span class="chg">(내부 대조용 · 제출 문서에는 쓰지 않음)</span></th></tr></thead>'
      + '<tbody>' + body.join('') + '</tbody><tfoot>' + foot + '</tfoot></table></div>';
  }
  function opcBlock(rows) {
    var names = rows.filter(function (r) { return B.gen[r.sym] && !r.sub && r.node === 'OPC'; }).map(function (r) { return r.nm.split(' (')[0]; });
    var lines = [], cur = '';
    names.forEach(function (n) { var nx = (cur ? cur + ' · ' : '') + n; if (nx.length > 34) { lines.push(cur); cur = n; } else cur = nx; });
    lines.push(cur);
    return '<rect x="776" y="346" width="310" height="132" rx="4" class="dv3"/><text x="931" y="368" class="dvt" font-size="12">운영 PC 탑재 SW ' + names.length + '종 (항목1·2)</text>'
      + lines.slice(0, 8).map(function (l, i) { return '<text x="931" y="' + (386 + i * 12.5) + '" class="dvs" font-size="9.5">' + E(l) + '</text>'; }).join('');
  }

  function renderOcs(q, mz) {
    var z = B.zones[0], up = q && q.zones[z.id], meta = up || z, rows = ocsRows(mz);
    MG = {};
    rows.forEach(function (r) { if (B.gen[r.sym]) MG[r.g] = 1; });
    setH('ql-items', itemTable(rows, meta));
    var gs = {}, gl = [];
    rows.forEach(function (r) { if (r.amt != null) { if (!(r.g in gs)) { gs[r.g] = 0; gl.push(r.g); } gs[r.g] += r.amt; } });
    setH('ql-kpis', gl.map(function (g) { return '<div><b>' + gk(g)(gs[g] / 1000) + '</b><span>' + E(g.split('. ')[1]) + ' (백만원)</span></div>'; }).join(''));
    setT('ql-h2', '견적 ' + won(meta.total) + ' · 견적서 ' + (gl.length + 1) + '개 항목을 서버실·운영실·Cell 캐비닛에 배치');
    setT('ql-eb', up ? '업로드 견적(' + meta.no + ') 기준' : B.bl + '(' + z.no + ') 기준');
    setT('ql-s-quote', meta.no + ' (' + (meta.date || '') + ') · 합계 ' + won(meta.total) + ' · 비교견적 ' + k(z.cmp) + '천원(10/15 기준, 발표자료 별첨 3)');
    setT('ql-s-comp', gl.map(function (g) { return g.split('. ')[1] + ' ' + gk(g)(gs[g]); }).join(' · ') + ' · 일반관리비·이윤 ' + won(meta.ga));
    var amc = rows.filter(function (r) { return r.key === 'AMC'; })[0];
    setT('ql-s-lic', '네트워크 라이선스(Network-Lock), 모듈별 1카피(포맷·제어기·PLC 단위 모듈은 수량만큼). '
      + (amc ? '유지보수 ' + amcText(mz.rows, amc) + (PUB ? '' : ' ' + k(amc.q * amc.u) + '천원') + '은 ' + amc.g.split('. ')[0] + '에 별도 계상' : '유지보수(AMC)는 견적에 없음'));
    var scan = rows.some(function (r) { return r.sym === 'SCN'; });
    var nspec = rows.filter(function (r) { return r.chk === 'spec'; }).length + rows.filter(function (r) { return r.sub && (/없음|미기재/.test(r.sp) || !r.sp); }).length;
    var lumps = rows.filter(function (r) { return r.chk === 'lump'; }), ts = rows.filter(function (r) { return isTS(r.key); }), tsAmt = sum(ts, function (r) { return r.amt; });
    setT('ql-g-spec', '사양이 없는 구성품 ' + nspec + '건(로컬 서버·Edge Gateway·기반시설 하위 품목 등) — 공급사에 사양서 요청');
    setT('ql-g-lump', '1식 금액 ' + lumps.length + '건 ' + k(sum(lumps, function (r) { return r.amt; })) + "천원을 '금액 미구분'으로 표시");
    setT('ql-q-ts', (tsAmt ? '기술지원 ' + ts.length + '건 ' + k(tsAmt) + '천원 — 범위·산출물 명시 필요' : '교육·기술지원 무상 — 맞춤 개발 포함 여부·산출물 서면 확인 필요')
      + '. 유지보수 ' + (amc ? amcText(mz.rows, amc) + ' — ' + amc.g.split('. ')[0] : '없음'));
    var g = document.getElementById('ql-opc');
    if (g) g.innerHTML = opcBlock(rows);
    show('ql-scan', scan); show('ql-noscan', !scan);
    var role = document.getElementById('ql-role-SCN');
    if (role) role.hidden = !scan;
    return rows;
  }

  // ------------------------------------------------------------------ DOM
  var SNAP = {};
  function setH(id, h) { var n = document.getElementById(id); if (n) n.innerHTML = h; }
  function setT(id, t) { var n = document.getElementById(id); if (n) n.textContent = t; }
  function show(id, on) { var n = document.getElementById(id); if (n) { if (on) n.removeAttribute('display'); else n.setAttribute('display', 'none'); } }
  function snapshot() {
    Array.prototype.forEach.call(document.querySelectorAll('[id^="ql-"],[data-qlu],[data-qlr],[data-qlq]'), function (n, i) {
      if (n.closest('.qlive')) return;
      n.setAttribute('data-qls', i);
      SNAP[i] = {h: n.innerHTML, d: n.getAttribute('display'), hid: n.hidden};
    });
  }
  function restore() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-qls]'), function (n) {
      var s = SNAP[n.getAttribute('data-qls')];
      n.innerHTML = s.h;
      if (s.d == null) n.removeAttribute('display'); else n.setAttribute('display', s.d);
      n.hidden = s.hid;
    });
  }

  function apply(q) {
    restore();
    var panel = document.getElementById('qlive');
    if (q && !B.zones.some(function (z) { return q.zones[z.id]; })) q = B.page === 'dmw' ? q : null;
    var mzs = B.zones.map(function (z) { return merge(z.rows, q && q.zones[z.id]); });
    if (B.page === 'dmw') {
      if (q) renderDmw(q, mzs);
      dmwPanel(q, mzs);
    } else {
      if (q && q.zones[B.zones[0].id]) renderOcs(q, mzs[0]);
      ocsBanner(q, mzs[0]);
    }
    if (panel) panel.classList.toggle('on', !!q);
  }

  function dmwPanel(q, mzs) {
    var cur = document.getElementById('ql-cur'), msg = document.getElementById('ql-msg'), dl = document.getElementById('ql-diff'), rst = document.getElementById('ql-reset');
    rst.hidden = !q;
    if (!q) {
      cur.innerHTML = '기준 견적: <b>' + E(B.bl) + ' 3건(' + E(B.blno) + ')</b> — 페이지 작성 기준';
      dl.innerHTML = '';
      return;
    }
    var got = B.zones.filter(function (z) { return q.zones[z.id]; });
    cur.innerHTML = '적용 견적: <b>' + E(q.name) + '</b> — ' + (got.length ? got.map(function (z) { return E(z.short) + ' ' + E(q.zones[z.id].no || ''); }).join(' · ') : '읽은 존 없음');
    var n = 0, items = [];
    B.zones.forEach(function (z, i) {
      if (!q.zones[z.id]) return;
      var d = diffList(mzs[i]);
      n += d.length;
      if (d.length) items.push('<li><b>' + E(z.short) + '</b><ul>' + diffHtml(d) + '</ul></li>');
    });
    dl.innerHTML = items.join('') + (q.warn || []).map(function (w) { return '<li class="ql-warn"><b>주의</b> ' + E(w) + '</li>'; }).join('');
    if (!msg.textContent) msg.textContent = got.length ? '기준 견적 대비 변경·추가·삭제 ' + n + '건. OCS 시뮬레이션 Cell 3종 페이지에도 자동 반영됨.' : '견적서 시트를 찾지 못함 — 이지로보틱스 견적서 엑셀 양식(항목1~7)인지 확인';
  }

  function ocsBanner(q, mz) {
    var bn = document.getElementById('qlive');
    if (!bn) return;
    var z = B.zones[0], up = q && q.zones[z.id];
    document.getElementById('ql-reset').hidden = !q;
    if (!q) {
      document.getElementById('ql-cur').innerHTML = '기준 견적: <b>' + E(B.bl) + '</b> — 페이지 작성 기준';
      document.getElementById('ql-diff').innerHTML = '';
      return;
    }
    var d = up ? diffList(mz) : [];
    document.getElementById('ql-cur').innerHTML = up
      ? '적용 견적: <b>' + E(q.name) + '</b> — ' + E(up.no || '') + (up.date ? ' (' + E(up.date) + ')' : '') + ' · 기준 견적(' + E(B.bl) + ') 대비 ' + (d.length ? '변경·추가·삭제 ' + d.length + '건' : '변경 없음')
      : '적용 견적 <b>' + E(q.name) + '</b>에 이 존(' + E(z.short) + ') 시트가 없어 기준 견적(' + E(B.bl) + ')을 표시함';
    document.getElementById('ql-diff').innerHTML = diffHtml(d);
  }

  function readFile(file) {
    var msg = document.getElementById('ql-msg');
    msg.textContent = '읽는 중… (' + file.name + ')';
    loadXLSX().then(function (X) {
      return file.arrayBuffer().then(function (buf) {
        var wb = X.read(buf, {type: 'array', cellDates: true});
        return wb.SheetNames.map(function (n) { return {name: n, rows: X.utils.sheet_to_json(wb.Sheets[n], {header: 1, raw: true, defval: null})}; });
      });
    }).then(function (sheets) {
      var q = parseBook(sheets, file.name);
      if (!Object.keys(q.zones).length) { msg.textContent = '견적서 시트를 찾지 못함 — 이지로보틱스 견적서 엑셀 양식(항목1~7, 수량·단가·금액 열)인지 확인'; return; }
      var ok = save(q);
      msg.textContent = '';
      apply(q);
      if (!ok) msg.textContent = '이 브라우저에서 저장이 막혀 있어 다른 페이지에는 반영되지 않음(이 페이지에만 적용)';
    }).catch(function (e) { msg.textContent = '읽지 못함: ' + (e && e.message || e); });
  }
  function loadXLSX() {
    if (root.XLSX) return Promise.resolve(root.XLSX);
    return new Promise(function (res, rej) {
      var s = document.createElement('script');
      s.src = B.sheetjs;
      s.onload = function () { res(root.XLSX); };
      s.onerror = function () { rej(new Error('엑셀 읽기 모듈을 불러오지 못함 (인터넷 연결 필요)')); };
      document.head.appendChild(s);
    });
  }

  function init() {
    var el = document.getElementById('qlbase');
    if (!el) return;
    B = JSON.parse(el.textContent);
    PUB = B.public;
    snapshot();
    var inp = document.getElementById('ql-file'), panel = document.getElementById('qlive');
    if (inp) inp.addEventListener('change', function () { if (inp.files[0]) readFile(inp.files[0]); inp.value = ''; });
    if (panel && inp) {
      panel.addEventListener('dragover', function (e) { e.preventDefault(); panel.classList.add('drag'); });
      panel.addEventListener('dragleave', function () { panel.classList.remove('drag'); });
      panel.addEventListener('drop', function (e) { e.preventDefault(); panel.classList.remove('drag'); if (e.dataTransfer.files[0]) readFile(e.dataTransfer.files[0]); });
    }
    var rst = document.getElementById('ql-reset');
    if (rst) rst.addEventListener('click', function () { save(null); var m = document.getElementById('ql-msg'); if (m) m.textContent = '기준 견적(' + B.bl + ')으로 되돌림'; apply(null); });
    root.addEventListener('storage', function (e) { if (e.key === KEY) apply(load()); });
    apply(load());
  }

  root.QuoteLive = {parseSheet: parseSheet, parseBook: parseBook, keyOf: keyOf, merge: merge, dmRows: dmRows, quoteTable: quoteTable, summaryTable: summaryTable,
    pzRows: pzRows, pzTable: pzTable, ocsRows: ocsRows, itemTable: itemTable, dmTemplates: dmTemplates,
    _base: function (b) { B = b; PUB = b.public; }};
  if (root.document) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
  }
})(typeof window !== 'undefined' ? window : globalThis);
