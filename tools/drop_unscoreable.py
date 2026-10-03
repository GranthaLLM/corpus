import glob, json, re
from common import ROOT, write

SKIP = ("bhattasangraha",)


def main():
    total = 0
    for p in sorted(glob.glob(str(ROOT / "*" / "*.json"))):
        if "schema" in p or any(s in p for s in SKIP):
            continue
        d = json.loads(open(p, encoding="utf-8").read())
        if not isinstance(d, dict) or "units" not in d:
            continue
        keep, gone = [], []
        for u in d["units"]:
            (keep if u.get("english") and u.get("sanskrit") else gone).append(u)
        if not gone:
            continue
        col = [u["ref"] for u in gone if str(u["ref"]).startswith("colophon")]
        rest = [str(u["ref"]) for u in gone if not str(u["ref"]).startswith("colophon")]
        msg = f" [{len(gone)} units with no english in any source were dropped so every unit is scoreable: {len(col)} colophon units"
        msg += f" and {len(rest)} others ({', '.join(rest)})." if rest else "."
        d["units"] = keep
        d["notes"] = (d["notes"] or "") + msg + "]"
        rel = p[len(str(ROOT)) + 1:]
        write(rel, d)
        total += len(gone)
        print(rel, len(gone))
    print("dropped", total)


if __name__ == "__main__":
    main()
