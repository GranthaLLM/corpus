"""Apply repunctuated english (Jha via wisdomlib, see chandogya_shankara_repunct.py) to chandogya_shankara.
Run from corpus/: GRANTHA_WL=<dir>/ python3 tools/chandogya_shankara_apply.py [--dry]"""
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv
F = ROOT / "upanishads" / "chandogya_shankara.json"
WL = pathlib.Path(os.environ["GRANTHA_WL"])


def main():
    R = {}
    for i in range(1, 9):
        R.update(json.loads((WL / f"chand_repunct_{i}.json").read_text(encoding="utf-8")))
    d = json.loads(F.read_text(encoding="utf-8"))
    n = 0
    skipped = []
    for u in d["units"]:
        v = R.get(u["ref"])
        if not v:
            continue
        m = v["matched"] / v["old_letters"]
        r = v["new_letters"] / v["old_letters"]
        if m < 0.97 or not 0.95 <= r <= 1.35:
            skipped.append(u["ref"])
            continue
        new = re.sub(r"\s*[—-]+\s*\(\d+\)\s*(?=\n|$)", "", v["new"]).strip()
        u["english"] = new
        n += 1
    d["notes"] += (
        " [Punctuation pass 2026-10-13: the english had lost most punctuation and spacing in extraction (run-together words, almost no full stops). "
        f"{n} units were re-aligned letter by letter to Jha's translation on wisdomlib and now carry its punctuation and spacing; the wording is unchanged. "
        f"Units left as they were: {len(skipped)} (colophons, and units where the letters did not match closely enough).]"
    )
    print(n, "applied; skipped", skipped)
    if not DRY:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
