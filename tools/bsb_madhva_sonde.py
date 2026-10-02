import json, re
from common import ROOT, RAW, write

FILES = {1: "Bramha-Sutra2-Chapter-I", 2: "Bramha-Sutra3-Chapter-II", 3: "Bramha-Sutra4-Chapter-III", 4: "Bramha-Sutra5-Chapter-IV"}
DEVN = str.maketrans("०१२३४५६७८९", "0123456789")
DEV = re.compile("[ऀ-ॿ]")
SKIP = {"2.4.10-2"}


def headers(L):
    out = []
    for i, l in enumerate(L):
        m = re.search(r"ॐ?\s*।+\s*([०-९0-9]+)\s*।+\s*$", l.strip())
        if m and "ॐ" in l:
            out.append((i, int(m.group(1).translate(DEVN))))
    return out


def padas(h):
    res, pada, prev = [], 1, 0
    for i, n in h:
        if n < prev - 3 and prev > 4:
            pada += 1
        res.append((i, pada, n))
        prev = n
    return res


def english(lines):
    out = []
    for l in lines:
        s = l.strip()
        if not s or re.fullmatch(r"\d{1,4}", s) or re.fullmatch(r"(Commentary|Cpmmentary|भाष्य)", s) or re.fullmatch(r"0+", s):
            continue
        d, a = len(DEV.findall(s)), sum(1 for c in s if c.isalpha())
        if d > 0 and d >= 0.35 * max(a, 1):
            continue
        out.append(s)
    return out


def main():
    d = json.loads((ROOT / "philosophical/bsb_madhva.json").read_text(encoding="utf-8"))
    H = {}
    for a, f in FILES.items():
        L = (RAW / "sonde" / f"{f}.txt").read_text(encoding="utf-8").split("\n")
        H[a] = (L, padas(headers(L)))
    n, parked = 0, []
    for u in d["units"]:
        m = re.match(r"^(\d)\.(\d)\.(\d+)$", u["ref"])
        if not m or u.get("english") or u["ref"] in SKIP or not u.get("sanskrit"):
            continue
        a, b, s = map(int, m.groups())
        L, hs = H[a]
        k = next((k for k, (i, p, nn) in enumerate(hs) if p == b and nn == s), None)
        if k is None:
            parked.append(u["ref"])
            continue
        end = hs[k + 1][0] if k + 1 < len(hs) else len(L)
        text = " ".join(english(L[hs[k][0]:end]))
        text = re.sub(r"(\w)- (\w)", r"\1\2", re.sub(r"\s+", " ", text)).strip()
        if len(text) < 20:
            parked.append(u["ref"])
            continue
        mp = next((p for p in u.get("parts", []) if p["role"] == "mula"), None)
        bp = next((p for p in u.get("parts", []) if p["role"] == "bhashya"), None)
        if bp is None:
            parked.append(u["ref"])
            continue
        bp["english"] = text
        u["english"] = "\n".join(x for x in ((mp or {}).get("english"), text) if x)
        u.setdefault("meta", {})["english_source"] = "Sonde, Brahmasutra Bhashya (bhashya translation only)"
        n += 1
    d["notes"] += (f" [Bhashya English for {n} sutras that Subba Rau's docx lacked, from Nagesh D. Sonde's Brahmasutra Bhashya translation (PDF text layer; his sutras are numbered per pada, "
                   f"so each sutra's block runs from its numbered line to the next); the sutra's mula english stays Subba Rau's. Not filled: 2.4.10-2 (a repeated number) {', '.join(parked)}.]")
    write("philosophical/bsb_madhva.json", d)
    print(n, "parked", parked)


if __name__ == "__main__":
    main()
