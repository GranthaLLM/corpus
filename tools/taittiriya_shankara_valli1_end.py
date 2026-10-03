import json, re
from common import ROOT, write
import taittiriya_shankara_english as t


def main():
    B = t.lines()
    start = next(i for i, l in enumerate(B) if "INTRODUCTION TO THE SI" in l)
    end = next(i for i, l in enumerate(B) if l.startswith("Thus ends the Bhrigu Valli"))
    heads = [i for i in range(start, end + 1) if re.match(r"^CHAPTER\b", B[i])]
    en = []
    for c in (11, 12):
        e = heads[c] if c < len(heads) else end
        en += t.paras(B[heads[c - 1] + 1:e])
    p = ROOT / "upanishads/taittiriya_shankara.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    us = d["units"]
    grp = [u for u in us if u["ref"] in ("1.11.1", "1.11.2", "1.11.3", "1.11.4", "1.12.1")]
    mula = "\n".join(x["sanskrit"] for x in grp if x["scope"] == "mula")
    mp = [q for x in grp for q in x.get("parts", []) if q["role"] == "mula"]
    bh = [q for x in grp for q in x.get("parts", []) if q["role"] == "bhashya"]
    mula = "\n".join([x["sanskrit"] for x in grp if x["scope"] == "mula"] + [q["sanskrit"] for q in mp])
    bhs = "\n".join(q["sanskrit"] for q in bh)
    parts = [{"role": "mula", "sanskrit": mula}, {"role": "bhashya", "sanskrit": bhs}]
    new = {"ref": "1.11.1-1.12.1", "kind": "group", "scope": "mula+commentary", "sanskrit": mula + "\n" + bhs, "english": "\n".join(en), "parts": parts}
    first = us.index(grp[0])
    for x in grp:
        us.remove(x)
    us.insert(first, new)
    d["notes"] = d["notes"].replace("Chapters 1.11 (Sharada splits it into four units) and 1.12 have null english: the Sastri text is not in the repo for them.", "Chapters 1.11 and 1.12 are one unit (1.11.1-1.12.1): Sharada puts the commentary of both on 1.11.4, so Sastri's two chapters are attached to the whole of them.")
    write("upanishads/taittiriya_shankara.json", d)
    print(len(grp), len(new["sanskrit"]), len(new["english"]))


if __name__ == "__main__":
    main()
