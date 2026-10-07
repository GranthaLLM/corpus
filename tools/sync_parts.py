"""Make `parts` agree with the scored pair when they drifted. The pair is taken as the truth.
mula+commentary units: english of the pair must equal the join (newline) of the english of the parts that have both sides.
Repair: pair = mula_en + newline + rest  ->  bhashya english = rest.  Run with --apply to write."""
import glob
import json
import re
import sys

APPLY = "--apply" in sys.argv
ws = lambda s: re.sub(r"\s+", " ", s or "").strip()
stats = {}
left = []
for f in sorted(glob.glob("*/*.json")):
    if f.split("/")[0] not in ("philosophical", "upanishads", "sahitya"):
        continue
    d = json.load(open(f, encoding="utf-8"))
    n = f.split("/")[-1][:-5]
    ch = False
    for u in d["units"]:
        ps = u.get("parts") or []
        if not ps or u["scope"] != "mula+commentary":
            continue
        bo = [p for p in ps if p.get("sanskrit") and p.get("english")]
        if not bo:
            continue
        je = "\n".join(p["english"] for p in bo)
        js = "\n".join(p["sanskrit"] for p in bo)
        if u["english"] == je and u["sanskrit"] == js:
            continue
        by = {p["role"]: p for p in ps}
        m, b = by.get("mula"), by.get("bhashya")
        kind = None
        if u["sanskrit"] == js and ws(u["english"]) == ws(je):
            kind = "whitespace"
            for p in bo:
                p["english"] = p["english"].strip()
            if "\n".join(p["english"] for p in bo) != u["english"]:
                u["english"] = "\n".join(p["english"] for p in bo)
        elif m and b and len(bo) == 2 and m.get("english") and b.get("sanskrit") and u["english"].startswith(m["english"] + "\n") and u["sanskrit"] == js:
            kind = "bhashya english rebuilt from pair"
            b["english"] = u["english"][len(m["english"]) + 1:]
        else:
            kind = "left"
            left.append((n, u["ref"]))
        stats.setdefault(n, {}).setdefault(kind, 0)
        stats[n][kind] += 1
        ch = True
    if ch and APPLY:
        open(f, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
for n, c in stats.items():
    print(n, c)
print("left:", len(left), left[:60])
