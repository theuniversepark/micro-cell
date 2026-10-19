"""대외비 단가 분리. private_prices.py가 있으면 실제 단가를 쓰고(2026-10-08 사용자 결정으로 전체본은 공개),
없거나 PUBLIC=1이면 공개본으로 빌드함. 공개본은 DMWorks 정가·견적 단가와 그 금액을 포함하는 소계·일반관리비·합계를
'비공개'로 가림(정밀조립존 DMWorks 1좌석은 0원 처리). OUT_DIR로 출력 폴더 지정."""
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
MASK = "비공개"
PUBLIC_NOTE = ("공개본: DMWorks 정가·견적 단가와 이를 포함하는 소계·일반관리비·견적 합계는 '비공개'로 가림. "
               "OCS HW·로컬 HW·로컬 OCS·보안·기술지원 금액은 그대로 표시함.")


def money(n):
    """DMWorks 금액(또는 DMWorks 금액이 들어간 소계·합계) 표기 — 공개본은 '비공개'"""
    return MASK if PUBLIC else f"{n:,.0f}"


def pick(full, public):
    """금액이 들어간 문장 — 공개본은 금액을 뺀 문장"""
    return public if PUBLIC else full


def out(name):
    os.makedirs(OUT_DIR, exist_ok=True)
    return os.path.join(OUT_DIR, name)
