import json, re
from common import ROOT, RAW, write

FILES = {1: "Bramha-Sutra2-Chapter-I", 2: "Bramha-Sutra3-Chapter-II", 3: "Bramha-Sutra4-Chapter-III", 4: "Bramha-Sutra5-Chapter-IV"}
DEVN = str.maketrans("०१२३४५६७८९", "0123456789")
DEV = re.compile("[ऀ-ॿ]")
SKIP = {"2.4.10-2"}


def headers(L):
    out = []
    for i, l in enumerate(L):
        s = l.strip()
        m = re.search(r"।+\s*([०-९0-9]{1,3})\s*(?:।+)?\s*$", s)
        if m and "ॐ" in s and s.startswith(("।", "ॐ", "॥")):
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


TAIL = re.compile(r"^(0{3,}|First Chap\w*|Second Chap\w*|Third Chap\w*|Fourth Chap\w*|\w+ Step|Step \w+)\s*$", re.I)


def clean(lines):
    out = [l for l in english(lines)]
    while out and TAIL.match(out[-1].strip()):
        out.pop()
    text = " ".join(out)
    text = re.sub(r"\bCpmmentary\b|\bCommentary\b", "", text)
    return re.sub(r"(\w)- (\w)", r"\1\2", re.sub(r"\s+", " ", text)).strip()


def main(replace_all=True):
    d = json.loads((ROOT / "philosophical/bsb_madhva.json").read_text(encoding="utf-8"))
    H = {}
    for a, f in FILES.items():
        L = (RAW / "sonde" / f"{f}.txt").read_text(encoding="utf-8").split("\n")
        hs = padas(headers(L))
        H[a] = (L, hs, {(p, n): k for k, (i, p, n) in enumerate(hs)})
    maxn = {}
    for u in d["units"]:
        m = re.match(r"^(\d)\.(\d)\.(\d+)$", u["ref"])
        if m:
            key = (int(m.group(1)), int(m.group(2)))
            maxn[key] = max(maxn.get(key, 0), int(m.group(3)))
    replaced, kept, filled = [], [], 0
    for u in d["units"]:
        m = re.match(r"^(\d)\.(\d)\.(\d+)$", u["ref"])
        if not m or u["ref"] in SKIP or not u.get("sanskrit"):
            continue
        a, b, s = map(int, m.groups())
        L, hs, idx = H[a]
        k = idx.get((b, s))
        reliable = k is not None and ((b, s + 1) in idx or s == maxn[(a, b)])
        bp = next((p for p in u.get("parts", []) if p["role"] == "bhashya"), None)
        mp = next((p for p in u.get("parts", []) if p["role"] == "mula"), None)
        if not reliable or bp is None:
            kept.append(u["ref"])
            continue
        end = hs[k + 1][0] if k + 1 < len(hs) else len(L)
        text = clean(L[hs[k][0]:end])
        if len(text) < 20:
            kept.append(u["ref"])
            continue
        sk = len(bp.get("sanskrit") or "") or 1
        old_b = len(bp.get("english") or "")
        if len(text) / sk < 0.3 or len(text) / sk > 6 or (old_b and not 0.35 <= len(text) / old_b <= 2.8):
            kept.append(u["ref"])
            continue
        had = bool(u.get("english"))
        if not replace_all and had:
            continue
        bp["english"] = text
        u["english"] = "\n".join(x for x in ((mp or {}).get("english"), text) if x)
        u.setdefault("meta", {})["english_source"] = "Sonde, Brahmasutra Bhashya (bhashya); Subba Rau 1904 (sutra)" if (mp or {}).get("english") else "Sonde, Brahmasutra Bhashya (bhashya)"
        replaced.append(u["ref"])
        filled += not had
    d["notes"] += (f" [Bhashya English replaced with Nagesh D. Sonde's Brahmasutra Bhashya translation for {len(replaced)} sutras ({filled} of them previously had none); the sutra's own english (mula part) stays Subba Rau's. "
                   "Sonde's sutras are found by their numbered Sanskrit lines (his Devanagari is partly broken, a few headers are lost), and each sutra's block runs to the next numbered line. "
                   f"A sutra keeps Subba Rau's English when its next header was not found (its block would also hold the next sutra) or when Sonde's block is implausibly short or long against the Sanskrit or against Subba Rau's: {', '.join(kept)}.]")
    write("philosophical/bsb_madhva.json", d)
    print("replaced", len(replaced), "kept", len(kept), kept)
    return d


if __name__ == "__main__":
    main()
