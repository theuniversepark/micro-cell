"""견적서 원본(이지로보틱스 견적서, 1쪽=유연제조·2쪽=적응가공·3쪽=AI정밀검사)을 쪽 이미지로 변환·암호화 → 페이지 끝 '견적서 원본' 절에 삽입.
엑셀 견적서(.xlsx, 10/23)는 LibreOffice로 인쇄 설정 그대로 PDF로 바꾼 뒤(시트당 1쪽) 내용 영역만 잘라 고해상도로 렌더링함.
암호(.quote_pw 파일 또는 QUOTE_PW 환경변수, 저장소 제외)로 PBKDF2-SHA256 키를 만들어 AES-256-GCM으로 암호화함. 브라우저에서 암호를 넣어야 복호화됨.
quote_private/{slug}.json : 원본 그대로 (로컬·아티팩트용, .gitignore)
quote_public/{slug}.json  : 담당자 연락처(휴대폰·메일)·직인을 가린 공개본 (GitHub Pages용)
실행: uv run --with pypdfium2 --with pillow --with cryptography python prep_quotes.py [견적서.pdf|.xlsx]"""
import base64
import io
import json
import os
import subprocess
import sys
import tempfile

import pypdfium2 as pdfium
import pypdfium2.raw as R
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PIL import ImageDraw

SRC = ("/Users/jin/Library/CloudStorage/OneDrive2-(사)캠틱종합기술원/Workspace/Customers/이지로보틱스/2026-10-23/"
       "캠틱종합기술원 디지털 트윈 시뮬레이션 시스템 구축 견적서 (이지로보틱스) _20261023.xlsx")
SLUGS = ["fms", "adaptive", "qms"]
SCALE = 2.2
WIDTH = 1500  # 잘라 낸 내용 영역의 렌더링 폭(px) — 엑셀을 한 쪽에 맞춰 줄인 견적서도 글자를 읽을 수 있게
ITER = 600000


def password():
    pw = os.environ.get("QUOTE_PW")
    if not pw and os.path.exists(".quote_pw"):
        pw = open(".quote_pw").read().strip()
    if not pw:
        sys.exit("암호가 없음 — .quote_pw 파일 또는 QUOTE_PW 환경변수 필요")
    return pw


def encrypt(data, pw):
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pw.encode())
    b = lambda x: base64.b64encode(x).decode()
    return {"alg": "PBKDF2-SHA256/AES-256-GCM", "iter": ITER, "salt": b(salt), "iv": b(iv),
            "type": "image/jpeg", "ct": b(AESGCM(key).encrypt(iv, data, None))}


def mask_boxes(page):
    """가릴 영역(PDF 좌표, 좌하단 원점): 담당자 연락처 한 줄, 직인 이미지"""
    tp = page.get_textpage()
    boxes = []
    s = tp.search("010-")
    hit = s.get_next()
    if hit:
        l, b, _, t = tp.get_charbox(hit[0])
        e = tp.search("ezrobotics.com)").get_next()
        r = tp.get_charbox(e[0] + e[1] - 1)[2] if e else l + 90
        boxes.append((l - 3, b - 3, r + 3, t + 3))
    for o in page.get_objects():
        if o.type == R.FPDF_PAGEOBJ_IMAGE:
            l, b, r, t = o.get_bounds()
            if t - b > 15 and 0.6 < (r - l) / (t - b) < 1.6:  # 공급자란의 직인(정사각형에 가까움 — 로고는 가로로 김)
                boxes.append((l - 2, b - 2, r + 2, t + 2))
    return boxes


def jpeg(img):
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=86)
    return buf.getvalue()


def to_pdf(src):
    """엑셀 견적서 → PDF (LibreOffice). 견적서 시트는 '한 쪽에 맞춤' 인쇄 설정이라 시트당 1쪽"""
    out = tempfile.mkdtemp()
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", out, src], check=True, capture_output=True)
    return os.path.join(out, os.path.splitext(os.path.basename(src))[0] + ".pdf")


def content_box(page, pad=6):
    """인쇄 내용이 있는 영역(PDF 좌표, 좌하단 원점)"""
    w, h = page.get_size()
    bs = [o.get_bounds() for o in page.get_objects()]
    l, b = max(0, min(x[0] for x in bs) - pad), max(0, min(x[1] for x in bs) - pad)
    r, t = min(w, max(x[2] for x in bs) + pad), min(h, max(x[3] for x in bs) + pad)
    return l, b, r, t


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else SRC
    pw = password()
    pdf = pdfium.PdfDocument(to_pdf(src) if src.lower().endswith((".xlsx", ".xls")) else src)
    os.makedirs("quote_private", exist_ok=True)
    os.makedirs("quote_public", exist_ok=True)
    for slug, page in zip(SLUGS, pdf):
        w, h = page.get_size()
        cl, cb, cr, ct = content_box(page)
        s = max(SCALE, WIDTH / (cr - cl))
        img = page.render(scale=s, crop=(cl, cb, w - cr, h - ct)).to_pil().convert("RGB")
        json.dump(encrypt(jpeg(img), pw), open(f"quote_private/{slug}.json", "w"))
        d = ImageDraw.Draw(img)
        for l, b, r, t in mask_boxes(page):
            d.rectangle(((l - cl) * s, (ct - t) * s, (r - cl) * s, (ct - b) * s), fill="#D5DCEA")
        json.dump(encrypt(jpeg(img), pw), open(f"quote_public/{slug}.json", "w"))
        print(slug, img.size)


if __name__ == "__main__":
    main()
