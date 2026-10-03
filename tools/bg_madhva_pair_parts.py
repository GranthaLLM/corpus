import json
from common import ROOT, write


def main():
    p = ROOT / "philosophical/bg_madhva.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    n = 0
    for u in d["units"]:
        pa = u.get("parts")
        if not pa or u["ref"].startswith("colophon") or u["ref"] == "intro":
            continue
        both = [q for q in pa if q.get("sanskrit") and q.get("english") and (q["role"] == "mula" or 0.3 <= len(q["english"]) / len(q["sanskrit"]) <= 3.5)]
        if not both or len(both) == len([q for q in pa if q.get("sanskrit") or q.get("english")]):
            continue
        sk = "\n".join(q["sanskrit"] for q in both)
        en = "\n".join(q["english"] for q in both)
        if sk == u["sanskrit"] and en == (u.get("english") or ""):
            continue
        u["sanskrit"], u["english"] = sk, en
        u["scope"] = "mula" if all(q["role"] == "mula" for q in both) else "mula+commentary"
        n += 1
    d["notes"] += (f" In {n} units a part had Sanskrit but no english, or english but no Sanskrit (Sonde's translation does not cover every passage Setutila has, and the reverse); "
                   "the unit's pair (sanskrit, english) now holds only the parts that have both and whose english is between 0.3 and 3.5 times the Sanskrit in length, so the english translates the sanskrit it sits with. The other parts stay in 'parts', outside the scored pair.")
    write("philosophical/bg_madhva.json", d)
    print(n)


if __name__ == "__main__":
    main()
