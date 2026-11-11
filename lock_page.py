"""docs/의 DMWorks 존별 옵션 구성·OCS 시뮬레이션 Cell 3종 페이지를 암호 입력 화면으로 바꿈 — 본문·PDF·Word를 AES-256-GCM으로 암호화하고 브라우저에서 암호를 넣어야 복호화됨.

암호는 prep_quotes.py와 같은 곳(.quote_pw 파일 또는 QUOTE_PW 환경변수, 저장소 제외)에서 읽음. 암호가 없으면 평문이 공개되지 않도록 빌드를 실패로 끝냄.
web_wrap.py·export_docs.py 뒤에 실행함(PDF·Word는 평문 HTML로 만든 뒤 암호화). 같은 내용·같은 암호면 결과가 같도록 salt는 페이지별 고정, IV는 평문의 HMAC에서 만듦.
한 번 맞게 넣은 암호는 탭을 닫을 때까지 기억(sessionStorage)해 네 페이지를 오갈 때 다시 묻지 않음.
실행: uv run --with cryptography python lock_page.py"""
import base64
import hashlib
import hmac
import html
import json
import os
import re
import sys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import web_wrap

PAGES = ("dmworks_zones", "ocs_sim_fms", "ocs_sim_adaptive", "ocs_sim_qms")
ITER = 600000


def salt(page):
    return hashlib.sha256(b"micro-cell/lock_page/" + page.encode()).digest()[:16]


MIME = {"pdf": "application/pdf", "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}

GATE = """<title>%(title)s</title>
<meta name="robots" content="noindex">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&family=IBM+Plex+Mono:wght@400&display=swap">
<style>
:root{--bg:#F5F7FB;--paper:#fff;--ink:#16213A;--muted:#5A6782;--rule:#D7DFEC;--navy:#10214B;--teal:#0090A0;--bad:#B3261E}
@media (prefers-color-scheme: dark){:root{--bg:#0B1430;--paper:#111D3F;--ink:#E6ECF8;--muted:#9AA8C6;--rule:#253661;--navy:#0A1636;--teal:#2BC0CF;--bad:#FF8A80;color-scheme:dark}}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic",sans-serif;line-height:1.6}
.webbar{background:#0A1636;display:flex;flex-wrap:wrap;gap:4px 14px;padding:8px 20px;font:600 13px "Noto Sans KR",sans-serif}
.webbar a{color:#C9D6F0;text-decoration:none}.webbar a.on{color:#00C2D1}.webbar a:hover{color:#fff}
.mast{background:var(--navy);color:#fff;padding:36px 20px 30px}
.wrap{max-width:1040px;margin:0 auto}
.eb{font-family:"IBM Plex Mono",monospace;font-size:12px;color:#7FE3EC;margin:0 0 8px;letter-spacing:.06em}
h1{margin:0;font-size:clamp(26px,4vw,36px);font-weight:900}
main{padding:28px 20px 56px}
.lock{max-width:420px;background:var(--paper);border:1px solid var(--rule);border-radius:10px;padding:22px 24px}
.lock p{margin:0 0 14px;color:var(--muted);font-size:14px}
.lock label{display:block;font-size:13px;font-weight:700;margin-bottom:6px}
.row{display:flex;gap:8px}
.lock input{flex:1;min-width:0;font:inherit;font-size:16px;padding:8px 10px;border:1px solid var(--rule);border-radius:6px;background:var(--bg);color:var(--ink)}
.lock input:focus-visible,.lock button:focus-visible{outline:2px solid var(--teal);outline-offset:2px}
.lock button{font:inherit;font-weight:700;padding:8px 18px;border:0;border-radius:6px;background:var(--teal);color:#fff;cursor:pointer}
.lock button:disabled{opacity:.6;cursor:default}
#lkmsg{min-height:1.6em;margin:10px 0 0;font-size:13px;color:var(--bad)}
</style>
</head>
<body>
%(bar)s
<header class="mast"><div class="wrap"><p class="eb">암호 필요</p><h1>%(title)s</h1></div></header>
<main><div class="wrap">
<form class="lock" id="lk">
<p>업체 견적 내용이 들어 있어 암호를 넣어야 열림. 암호는 어디에도 전송되지 않고 이 브라우저 안에서만 확인함.</p>
<label for="lkpw">암호</label>
<div class="row"><input id="lkpw" type="password" inputmode="numeric" autocomplete="off" required autofocus><button id="lkgo">열기</button></div>
<p id="lkmsg" role="status" aria-live="polite"></p>
</form>
</div></main>
<script id="lkdata" type="application/json">%(data)s</script>
<script>
(function(){
  var d = JSON.parse(document.getElementById('lkdata').textContent), SK = 'lock:micro-cell';
  var form = document.getElementById('lk'), pw = document.getElementById('lkpw'), go = document.getElementById('lkgo'), msg = document.getElementById('lkmsg');
  function b64(s){ var b = atob(s), a = new Uint8Array(b.length); for (var i = 0; i < b.length; i++) a[i] = b.charCodeAt(i); return a; }
  function store(v){ try { if (v === null) sessionStorage.removeItem(SK); else sessionStorage.setItem(SK, v); } catch (e) {} }
  function saved(){ try { return sessionStorage.getItem(SK); } catch (e) { return null; } }
  // 복호화된 본문의 PDF·Word 저장 버튼 — 암호화 파일을 받아 풀어서 저장
  function save(e, key){
    var a = e.target.closest && e.target.closest('a[download][href^="%(page)s."]');
    if (!a) return;
    e.preventDefault();
    var f = a.getAttribute('href'), label = a.textContent;
    a.textContent = '여는 중…';
    fetch(f + '.enc').then(function(r){ if (!r.ok) throw 0; return r.arrayBuffer(); }).then(function(b){
      return crypto.subtle.decrypt({name: 'AES-GCM', iv: new Uint8Array(b, 0, 12)}, key, new Uint8Array(b, 12));
    }).then(function(p){
      var u = URL.createObjectURL(new Blob([p], {type: d.mime[f.split('.').pop()]})), l = document.createElement('a');
      l.href = u; l.download = f; document.body.appendChild(l); l.click(); l.remove();
      setTimeout(function(){ URL.revokeObjectURL(u); }, 60000);
      a.textContent = label;
    }).catch(function(){ a.textContent = '저장 실패'; setTimeout(function(){ a.textContent = label; }, 2500); });
  }
  function open(p, quiet){
    if (!(window.crypto && crypto.subtle)) { msg.textContent = '이 브라우저에서는 열 수 없음 (HTTPS 필요)'; return; }
    go.disabled = true; msg.textContent = quiet ? '' : '확인 중…';
    var key;
    crypto.subtle.importKey('raw', new TextEncoder().encode(p), 'PBKDF2', false, ['deriveKey']).then(function(k){
      return crypto.subtle.deriveKey({name: 'PBKDF2', salt: b64(d.salt), iterations: d.iter, hash: 'SHA-256'}, k, {name: 'AES-GCM', length: 256}, false, ['decrypt']);
    }).then(function(k){
      key = k;
      return crypto.subtle.decrypt({name: 'AES-GCM', iv: b64(d.iv)}, k, b64(d.ct));
    }).then(function(buf){
      store(p);
      var html = new TextDecoder().decode(buf), h = location.hash;
      document.open(); document.write(html); document.close();
      document.addEventListener('click', function(e){ save(e, key); });
      if (h.length > 1) window.addEventListener('load', function(){ var t = document.getElementById(decodeURIComponent(h.slice(1))); if (t) t.scrollIntoView(); });
    }).catch(function(){
      store(null); go.disabled = false;
      msg.textContent = quiet ? '' : '암호가 맞지 않음';
      if (!quiet) pw.select();
    });
  }
  form.addEventListener('submit', function(e){ e.preventDefault(); open(pw.value.trim(), false); });
  var s = saved();
  if (s) open(s, true);
})();
</script>
</body>
</html>
"""


def password():
    pw = os.environ.get("QUOTE_PW")
    if not pw and os.path.exists(".quote_pw"):
        pw = open(".quote_pw").read().strip()
    if not pw:
        sys.exit("암호가 없음 — .quote_pw 파일 또는 QUOTE_PW 환경변수 필요 (DMWorks 페이지를 평문으로 내보내지 않음)")
    return pw


def seal(key, data):
    """(iv, ciphertext) — IV는 평문 HMAC에서 만들어 같은 내용이면 같은 결과"""
    iv = hmac.new(key, data, hashlib.sha256).digest()[:12]
    return iv, AESGCM(key).encrypt(iv, data, None)


def lock(page, pw):
    html_path = f"docs/{page}.html"
    s = open(html_path, encoding="utf-8").read()
    if 'id="lkdata"' in s:
        sys.exit(f"{html_path} 가 이미 암호 화면임 — ./build.sh 로 평문부터 다시 만들어야 함")
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt(page), iterations=ITER).derive(pw.encode())
    b = lambda x: base64.b64encode(x).decode()

    for ext in MIME:
        src = f"docs/{page}.{ext}"
        if os.path.exists(src):
            iv, ct = seal(key, open(src, "rb").read())
            open(src + ".enc", "wb").write(iv + ct)
            os.remove(src)
        elif not os.path.exists(src + ".enc"):
            print(f"주의: {src} 없음 — {ext.upper()} 저장 버튼이 동작하지 않음")

    iv, ct = seal(key, s.encode("utf-8"))
    data = json.dumps({"iter": ITER, "salt": b(salt(page)), "iv": b(iv), "ct": b(ct), "mime": MIME})
    title = html.escape(html.unescape(re.search(r"<title>(.*?)</title>", s, re.S).group(1).strip()))
    bar = web_wrap.bar(f"{page}.html").replace(web_wrap.dl(f"{page}.html"), "")
    open(html_path, "w", encoding="utf-8").write(web_wrap.HEAD + GATE % {"title": title, "bar": bar, "data": data, "page": page})
    print("locked", html_path)


def main():
    pw = password()
    for page in PAGES:
        lock(page, pw)


if __name__ == "__main__":
    main()
