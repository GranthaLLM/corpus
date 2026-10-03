import json, re
from common import ROOT, write


def main():
    p = ROOT / "sahitya/harivamsha.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    out, stripped, dropped = [], 0, []
    for u in d["units"]:
        s = u["sanskrit"]
        t = re.sub(r"^.*?:[kh]\]\s*", "", s, flags=re.S) if re.search(r":[kh]\]", s) else s
        if t != s:
            stripped += 1
        if len(re.findall(r"[ऀ-ॿ]", t)) < 12 or re.search(r"proof-read|transliterated by", t):
            dropped.append(u["ref"])
            continue
        u["sanskrit"] = t.strip()
        out.append(u)
    d["units"] = out
    d["notes"] += (f" Critical-apparatus text that the Mitrasamgraha rows carry in front of some verses (variant readings, 'transliterated by ...') was stripped from {stripped} units; "
                   f"{len(dropped)} units whose Sanskrit was apparatus only (no verse) were dropped: {', '.join(dropped)}.")
    write("sahitya/harivamsha.json", d)
    print(stripped, len(dropped), len(out))


if __name__ == "__main__":
    main()
