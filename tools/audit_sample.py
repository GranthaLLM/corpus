"""Draw a stratified random sample of scoreable units and write a self-contained HTML sheet to mark them.

Usage: python3 tools/audit_sample.py [--total 300] [--seed 7] [--out DIR] [--only stem,stem] [--ids PREVIOUS_SAMPLE.json]
Output: DIR/audit.html (open in a browser; marks live in the browser's localStorage and export as JSON or CSV)
        DIR/sample.json (the drawn units with their stratum sizes, for weighting the estimate)
Allocation: 5 units per file plus the remainder split by the square root of file size, so small works are seen
and large ones are not drowned. Each stratum keeps n (scoreable units in the file) and m (units drawn), so a
whole-corpus rate is sum(n_i * rate_i) / sum(n_i).
"""
import glob
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def arg(name, default):
    return type(default)(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


TOTAL, SEED = arg("--total", 300), arg("--seed", 7)
ONLY = arg("--only", "").split(",") if arg("--only", "") else []
IDS = set(u["id"] for u in json.loads(Path(arg("--ids", "")).read_text(encoding="utf-8"))["units"]) if arg("--ids", "") else set()
OUT = Path(arg("--out", str(ROOT.parent / "audit")))

LABELS = [
    ("ok", "Correct", "Sanskrit is right and the English translates exactly this Sanskrit"),
    ("sk", "Sanskrit wrong", "OCR or transcription errors, wrong or missing words"),
    ("en", "English does not match", "English is of another passage, or mistranslates"),
    ("trunc", "English short or long", "English truncated, or carries extra text from a neighbour"),
    ("place", "Misplaced", "Right text but in the wrong unit, or split in the wrong place"),
    ("na", "Cannot judge", "Skip, not counted"),
]


def files():
    for f in sorted(glob.glob(str(ROOT / "*" / "*.json"))):
        if f.split("/")[-2] in ("philosophical", "upanishads", "sahitya"):
            yield f


def main():
    rnd = random.Random(SEED)
    pools = []
    for f in files():
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        us = [u for u in d["units"] if u.get("sanskrit") and u.get("english")]
        pools.append((Path(f).stem, d, us))
    if ONLY:
        pools = [x for x in pools if x[0] in ONLY]
    base = 5 if not ONLY else TOTAL // max(1, len(pools))
    rest = max(0, TOTAL - base * len(pools))
    wsum = sum(math.sqrt(len(us)) for _, _, us in pools)
    sample, strata = [], []
    for stem, d, us in pools:
        m = min(len(us), base + round(rest * math.sqrt(len(us)) / wsum))
        strata.append({"file": stem, "work": d["text"], "author": d.get("commentator") or "", "n": len(us), "m": m})
        for u in (us if IDS else rnd.sample(us, m)):
            sample.append({
                "id": f"{stem}:{u['ref']}", "file": stem, "work": d["text"], "author": d.get("commentator") or "",
                "scope": u["scope"], "kind": u["kind"], "reftype": d.get("reference_type") or "",
                "sanskrit": u["sanskrit"], "english": u["english"],
                "parts": [{"role": p["role"], "sanskrit": p.get("sanskrit") or "", "english": p.get("english") or ""} for p in u.get("parts") or []],
            })
    if IDS:
        sample = [u for u in sample if u["id"] in IDS]
    rnd.shuffle(sample)
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {"seed": SEED, "labels": LABELS, "strata": strata, "units": sample}
    (OUT / "sample.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    html = (Path(__file__).with_name("audit_sheet.html")).read_text(encoding="utf-8")
    (OUT / "audit.html").write_text(html.replace("__PAYLOAD__", json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")), encoding="utf-8")
    print(f"{len(sample)} units from {len(strata)} files -> {OUT / 'audit.html'}")


main()
