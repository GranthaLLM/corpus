"""Move the 2.1.1 opener out of 2.1.0 in taittiriya_shankara and clean Sastri OCR junk.
Run from corpus/: python3 tools/shankara_taittiriya_align.py [--dry]"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv
F = ROOT / "upanishads" / "taittiriya_shankara.json"

TYPOS = [("BrahBan", "Brahman"), ("Omnicient", "Omniscient"), ("existense", "existence"), ("Vydhritis^", "Vydhritis"), ("mad©", "made"),
         ("himselL", "himself"), ("the AIL", "the All"), ("of alL", "of all"), ("A'k&sa", "Akasa"), ("Pr&na", "Prana")]


def main():
    d = json.loads(F.read_text(encoding="utf-8"))
    U = {u["ref"]: u for u in d["units"]}
    a, b = U["2.1.0"], U["2.1.1"]
    marker = '" The knower of Brahman reaches the highest etc.'
    i = a["english"].index(marker)
    moved = a["english"][i:].lstrip('" ').strip()
    a["english"] = a["english"][:i].rstrip()
    cut = "In the same sense is this hymn.\n"
    j = b["english"].index(cut) + len(cut)
    b["english"] = b["english"][:j] + moved + "\n" + b["english"][j:]
    for u in d["units"]:
        t = u["english"]
        if not t:
            continue
        t = re.sub(r"(^|\n)Com\.\s*[—-]+\s*", r"\1", t)
        if u["ref"] in ("2.1.0", "2.1.1"):
            for old, new in TYPOS:
                t = t.replace(old, new)
            t = re.sub(r"[£^•]", "", t)
            t = re.sub(r"(?<=\w)\*(?=\s|$)", "", t)
            t = t.replace("l BrahBan", "Brahman")
        u["english"] = t
    d["notes"] += (
        " [Alignment pass 2026-10-09: the english of 2.1.0 (peace invocation) had absorbed the opening of the 2.1.1 commentary ('The knower of Brahman "
        "reaches the highest etc.' to 'becomes Brahman himself'); it now sits in 2.1.1 after the mantra paragraph. 'Com.' prefixes stripped; obvious OCR "
        "slips fixed in 2.1.0 and 2.1.1 only.]"
    )
    if not DRY:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
