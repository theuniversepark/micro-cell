"""대외비 단가 분리. private_prices.py(로컬 전용, .gitignore)가 있으면 실제 단가를 쓰고,
없거나 PUBLIC=1이면 공개본으로 빌드함(DMWorks 금액 0 · '비공개' 표기). OUT_DIR로 출력 폴더 지정."""
import os

PV = None
if os.environ.get("PUBLIC") != "1":
    try:
        import private_prices as PV
    except ImportError:
        PV = None
PUBLIC = PV is None
OUT_DIR = os.environ.get("OUT_DIR", ".")
HIDDEN = "비공개(대외비 정가) — 공개본은 0원 처리"


def out(name):
    os.makedirs(OUT_DIR, exist_ok=True)
    return os.path.join(OUT_DIR, name)
