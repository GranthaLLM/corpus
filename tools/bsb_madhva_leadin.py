"""Subba Rau closes a sutra's bhashya with the lead-in to the next sutra ('To remove this doubt, the Sutrakara says :'). Move it to the next unit when that unit's Sanskrit opens with the same lead-in, else cut it."""
import json, re, sys
from pathlib import Path

F = Path(__file__).resolve().parent.parent / "philosophical" / "bsb_madhva.json"
LEAD = re.compile(r"[^.;?\n]*\b(?:Sutrakara|Badarayana|[Ss]utra)\b[^.;?\n]*[:—\-]\s*$")
SK_LEAD = re.compile(r"^[^।॥\n]{0,80}?(?:ाह|आह|वक्ति)\s*[-–]")


def split_lead(en):
    t = en.rstrip()
    m = LEAD.search(t)
    if not m or len(m.group(0).strip()) > 110:
        return None
    if re.search(r"\?[\s\)\"'’”]*$", t[: m.start()]):
        return ("SKIP", t[max(0, m.start() - 120): m.start()].strip() + " || " + m.group(0).strip())
    return t[: m.start()].rstrip(), m.group(0).strip()


def part(u, role):
    return next((p for p in u.get("parts", []) if p["role"] == role), None)


def rebuild(u):
    both = [p for p in u["parts"] if p.get("sanskrit") and p.get("english")]
    u["sanskrit"] = "\n".join(p["sanskrit"] for p in both)
    u["english"] = "\n".join(p["english"] for p in both)


def main(apply):
    d = json.loads(F.read_text(encoding="utf-8"))
    us = d["units"]
    idx = [i for i, u in enumerate(us) if re.match(r"\d", u["ref"])]
    moved = cut = 0
    for a, b in zip(idx, idx[1:]):
        u, n = us[a], us[b]
        bh = part(u, "bhashya")
        if not bh or not bh.get("english"):
            continue
        r = split_lead(bh["english"])
        if not r:
            continue
        if r[0] == "SKIP":
            print("SKIP", u["ref"], "|", r[1][-230:])
            continue
        rest, lead = r
        nb = part(n, "bhashya")
        move = bool(nb and nb.get("sanskrit") and nb.get("english") and SK_LEAD.match(nb["sanskrit"].lstrip()))
        print(("MOVE" if move else "CUT "), u["ref"], "->", n["ref"], "|", lead[:100])
        bh["english"] = rest
        if move:
            nb["english"] = lead + "\n" + nb["english"]
            rebuild(n)
            moved += 1
        else:
            cut += 1
        rebuild(u)
    print("moved", moved, "cut", cut)
    if apply:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


main("--apply" in sys.argv)
