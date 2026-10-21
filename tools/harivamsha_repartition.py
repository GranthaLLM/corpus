"""Redistribute Harivamsha English inside stretches the monotone realignment shifted.

harivamsha_realign.py aligned rows to units with a monotone DP, which can keep a whole stretch in order
while slipping a boundary: a unit then carries the English of the next row, the following unit the row
after that, and so on, until the run catches up. Every unit in the stretch is wrong even though the
stretch as a whole covers the right passage.

This script finds those stretches against the source TSV and, for each unit, writes the English of
exactly the source rows its Sanskrit ref names. It only touches a stretch when

  * the rows whose English appears in the stretch's units are exactly the stretch's Sanskrit row span,
  * the units' English joined equals that span's source English joined (whitespace-normalised),

so no wording is invented and no edited text is overwritten. Everything else is left for hand review.

Run from corpus/: python3 tools/harivamsha_repartition.py [--dry] [--tsv FILE]
The TSV defaults to $GRANTHA_RAW/GE07hv_conpu.tsv (mitrasamgraha-dataset, data/train/cc-by-sa/).
"""
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
F = ROOT / "sahitya" / "harivamsha.json"
DRY = "--dry" in sys.argv
TSV = pathlib.Path(sys.argv[sys.argv.index("--tsv") + 1]) if "--tsv" in sys.argv else \
    pathlib.Path(os.environ.get("GRANTHA_RAW", "raw")) / "GE07hv_conpu.tsv"


def norm(t):
    return " ".join((t or "").split())


def fold(t):
    t = (t or "").lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return " ".join(t.split())


def refspan(ref):
    a, _, b = str(ref).partition("-")
    try:
        return int(a), int(b or a)
    except ValueError:
        return None


def load_rows(path):
    lines = path.read_text(encoding="utf-8").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    rows = []
    for line in lines:
        parts = line.split("\t")
        rows.append((parts[0].strip(), "\t".join(parts[1:]).strip()))
    return rows


def main():
    if not TSV.exists():
        sys.exit(f"source TSV not found: {TSV} (set GRANTHA_RAW or pass --tsv)")
    rows = load_rows(TSV)
    rown = [fold(en) for _, en in rows]

    d = json.loads(F.read_text(encoding="utf-8"))
    us = d["units"]

    flags = []
    for ui, u in enumerate(us):
        span = refspan(u["ref"])
        if not span:
            continue
        a, b = span
        en = fold(u["english"])
        found = []
        for i in range(max(1, a - 8), min(len(rows), b + 8) + 1):
            e = rown[i - 1]
            if not e:
                continue
            if len(e) >= 12 and e in en:
                found.append(i)
            elif len(e) < 12 and re.search(r"\b" + re.escape(e) + r"\b", en):
                found.append(i)
        found = sorted(set(found))
        if found != list(range(a, b + 1)):
            flags.append((ui, a, b, found))

    groups = []
    for t in flags:
        if groups and t[0] == groups[-1][-1][0] + 1 and t[1] == groups[-1][-1][2] + 1:
            groups[-1].append(t)
        else:
            groups.append([t])

    fixed = skipped = changed = 0
    skipped_spans = []
    for g in groups:
        sa0, sa1 = g[0][1], g[-1][2]
        ens = sorted({x for t in g for x in t[3]})
        if ens != list(range(sa0, sa1 + 1)):
            skipped += 1
            skipped_spans.append(f"{sa0}-{sa1}")
            continue
        src = norm(" ".join(rows[i - 1][1] for i in range(sa0, sa1 + 1)))
        cur = norm(" ".join((us[t[0]]["english"] or "") for t in g))
        if src != cur:
            skipped += 1
            skipped_spans.append(f"{sa0}-{sa1}")
            continue
        plan = []
        for ui, a, b, _ in g:
            new = " ".join(rows[i - 1][1] for i in range(a, b + 1))
            if not new.strip():
                plan = None
                break
            plan.append((ui, new))
        if not plan:
            skipped += 1
            skipped_spans.append(f"{sa0}-{sa1}")
            continue
        fixed += 1
        for ui, new in plan:
            if us[ui]["english"] != new:
                us[ui]["english"] = new
                changed += 1

    d["units"] = us
    if changed:
        d["notes"] += (
            f" [Repartition 2026-10-21: english of {changed} units in {fixed} stretches was redistributed to the source row ranges "
            "their Sanskrit refs name; the earlier monotone realignment had shifted a run of rows by one or more units inside the "
            "stretch. Only stretches whose units carried exactly the source English of their combined Sanskrit span were touched, "
            "so the wording is the source's. Stretches where the English was edited, missing or of another passage were left for hand review.]"
        )
    print(f"flags {len(flags)} groups {len(groups)} fixed {fixed} units changed {changed} skipped {len(skipped_spans)}")
    if skipped_spans:
        print("left for review:", " ".join(skipped_spans))
    if not DRY and changed:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
