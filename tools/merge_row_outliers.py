"""Merge length-outlier units with a neighbour in row_aligned files when the merged english/sanskrit ratio moves toward the file median."""
import json, math, statistics as st, glob, sys

def run(f, lo=3.0):
    d = json.load(open(f))
    if d.get("alignment") != "row_aligned":
        return 0
    us = d["units"]
    ok = lambda k: us[k].get("english") and us[k].get("sanskrit")
    med = st.median(len(u["english"]) / max(1, len(u["sanskrit"])) for u in us if u.get("english") and u.get("sanskrit"))
    q = lambda s, e: len(e) / max(1, len(s)) / med
    spans = []
    for i, u in enumerate(us):
        if not ok(i):
            continue
        qq = q(u["sanskrit"], u["english"])
        if not (qq > lo or qq < 1 / lo):
            continue
        best = None
        for a, b in ((a, b) for a in range(i - 3, i + 1) for b in range(max(a + 1, i), a + 4)):
            if a < 0 or b >= len(us) or b <= a or not all(ok(k) for k in range(a, b + 1)):
                continue
            m = q(" ".join(us[k]["sanskrit"] for k in range(a, b + 1)), " ".join(us[k]["english"] for k in range(a, b + 1)))
            if best is None or abs(math.log(m)) < abs(math.log(best[0])):
                best = (m, a, b)
        if best and abs(math.log(best[0])) < abs(math.log(qq)) * 0.5 and 0.6 < best[0] < 1.7:
            spans.append([best[1], best[2]])
    spans.sort()
    merged = []
    for s in spans:
        if merged and s[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], s[1])
        else:
            merged.append(s)
    for a, b in reversed(merged):
        g = us[a:b + 1]
        u = dict(g[0])
        u["ref"] = f"{g[0]['ref']}-{g[-1]['ref']}"
        u["sanskrit"] = " ".join(x["sanskrit"] for x in g)
        u["english"] = " ".join(x["english"] for x in g)
        us[a:b + 1] = [u]
    if merged:
        d["notes"] = (d.get("notes") or "") + f" [Length-outlier repair: {len(merged)} runs of units merged with neighbours so both columns cover the same passage.]"
        open(f, "w").write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    return len(merged)

if __name__ == "__main__":
    for f in sys.argv[1:] or sorted(glob.glob("*/*.json")):
        if "bhatta" in f:
            continue
        n = run(f)
        if n:
            print(f, n)
