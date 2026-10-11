"""Cut Sastri's next-chapter heading and intro from the english of the last verse of seven chapters of bg_shankara.
The next chapter's first unit already carries its own intro english (Warrier), so the leaked text is a duplicate.
Run from corpus/: python3 tools/bg_shankara_chapter_leak.py [--dry]"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv
F = ROOT / "philosophical" / "bg_shankara.json"
REFS = {"1.47": "SECOND DISCOURSE", "3.43": "FOURTH DISCOURSE", "7.30": "EIGHTH DISCOURSE", "8.28": "NINTH DISCOURSE",
        "10.42": "ELEVENTH DISCOURSE", "13.34": "FOURTEENTH DISCOURSE", "17.28": "The teaching of the discourse summed up."}


def main():
    d = json.loads(F.read_text(encoding="utf-8"))
    U = {u["ref"]: u for u in d["units"]}
    for ref, marker in REFS.items():
        u = U[ref]
        for h in [u] + (u.get("parts") or []):
            e = h.get("english")
            if e and marker in e:
                h["english"] = e[: e.index(marker)].rstrip()
        assert u["english"] and len(u["english"]) > 30 and marker not in u["english"], ref
    d["notes"] += (
        " [Cleanup 2026-10-09: the chapter heading and introduction of the next chapter (Sastri's text, a duplicate of the Warrier intro already in the next "
        "chapter's first unit) were cut from the english of 1.47, 3.43, 7.30, 8.28, 10.42, 13.34 and 17.28.]"
    )
    if not DRY:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
