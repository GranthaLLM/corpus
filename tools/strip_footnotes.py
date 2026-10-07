"""Remove wisdomlib footnote blocks ('Footnotes and references:', '[back to top]', then '[n]:' + one text line each) from english."""
import glob
import json
import re

HEAD = "Footnotes and references:"
MARK = re.compile(r"^\[\d+\]:$")


def strip(en):
    L = en.split("\n")
    out, i = [], 0
    while i < len(L):
        if L[i].strip() == HEAD:
            i += 1
            if i < len(L) and L[i].strip() == "[back to top]":
                i += 1
            while i < len(L) and MARK.match(L[i].strip()):
                i += 2
            continue
        out.append(L[i])
        i += 1
    return "\n".join(out).rstrip()


def rebuild(u):
    ps = u.get("parts") or []
    both = [p for p in ps if p.get("sanskrit") and p.get("english")]
    if ps and u["scope"] == "mula+commentary":
        u["sanskrit"] = "\n".join(p["sanskrit"] for p in both)
        u["english"] = "\n".join(p["english"] for p in both)


tot = 0
for f in sorted(glob.glob("*/*.json")):
    if f.split("/")[0] not in ("philosophical", "upanishads", "sahitya"):
        continue
    d = json.load(open(f, encoding="utf-8"))
    ch = 0
    for u in d["units"]:
        hit = HEAD in (u.get("english") or "") or any(HEAD in (p.get("english") or "") for p in u.get("parts") or [])
        if not hit:
            continue
        if u.get("english"):
            u["english"] = strip(u["english"])
        for p in u.get("parts") or []:
            if p.get("english"):
                p["english"] = strip(p["english"])
        rebuild(u)
        ch += 1
    if ch:
        open(f, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
        print(f, ch)
        tot += ch
print("units changed", tot)
