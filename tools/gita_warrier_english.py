import collections, html, json, re
from common import ROOT, RAW, write

SRC = RAW / "warrier_gita_bhashya_djvu.txt"
DEV = re.compile("[ऀ-ॿ]")
JUNK = re.compile(r"Bhagavad\s*Gita\s*Bhasyam|Bhagayad|\[Ch\.|^\W*\d+\W*$|\b(?:Yoga|Samkhya|Sankhya)\b.*\d|\d.*\b(?:Yoga|Samkhya|Sankhya)\b", re.I)
SPEAKER = re.compile(r"^(?:(?:Sanjaya|Samjaya|The blessed Lord|The Lord|Arjuna|Dhrtarastra|Dhrtarastra|Krsna)\s+said\s*[:.]?\s*)", re.I)
LABEL = re.compile(r"^[\dIlOoMS!|]{1,3}\s*[.,]\s+")
ZERO = re.compile(r"^[IilL!|M\d\W]{0,5}[0O]\s*[.,]?\s*[a-zA-Zत]\s*[.,\s]")


def lines():
    t = SRC.read_text(encoding="utf-8")
    body = html.unescape(t[t.index("<pre>") + 5:t.index("</pre>")]) if "<pre>" in t else t
    return body.split("\n")


def cls(l):
    s = l.strip()
    if not s:
        return "B"
    d = len(DEV.findall(s))
    a = sum(1 for c in s if c.isalpha())
    return "D" if d > 0 and d >= 0.4 * max(a, 1) else "E"


def blocks(B, a, b):
    out = []
    for l in B[a:b]:
        c = cls(l)
        if c == "B":
            continue
        if c == "E" and len(l.strip()) < 80 and JUNK.search(l):
            continue
        if out and out[-1][0] == c:
            out[-1][1].append(l.strip())
        else:
            out.append([c, [l.strip()]])
    changed = True
    while changed:
        changed = False
        for i in range(1, len(out) - 1):
            if out[i][0] == "E" and len(" ".join(out[i][1])) < 25 and out[i - 1][0] == out[i + 1][0] == "D":
                out[i - 1][1] += out[i + 1][1]
                del out[i:i + 2]
                changed = True
                break
    return out


def pairs(B, a, b):
    bl = blocks(B, a, b)
    out = []
    for i, (c, L) in enumerate(bl):
        if c == "D":
            e = bl[i + 1][1] if i + 1 < len(bl) and bl[i + 1][0] == "E" else []
            out.append((" ".join(L), " ".join(e)))
    return out


def grams(t, n=3):
    t = re.sub(r"[^क-हऽ]", "", t)
    return collections.Counter(t[i:i + n] for i in range(max(len(t) - n + 1, 0)))


def dice(a, b):
    if not a or not b:
        return 0.0
    return 2 * sum((a & b).values()) / (sum(a.values()) + sum(b.values()))


def align(ug, pg):
    U, P = len(ug), len(pg)
    sc = [[dice(ug[i], pg[j]) for j in range(P)] for i in range(U)]
    NEG = -1e9
    dp = [[NEG] * (P + 1) for _ in range(U + 1)]
    bp = [[None] * (P + 1) for _ in range(U + 1)]
    for j in range(P + 1):
        dp[0][j] = 0
    for i in range(1, U + 1):
        for j in range(P + 1):
            best, b = dp[i - 1][j] - 0.5, (i - 1, j, 0)
            if j > 0:
                if dp[i][j - 1] > best:
                    best, b = dp[i][j - 1], (i, j - 1, 0)
                m = dp[i - 1][j - 1] + sc[i - 1][j - 1]
                if m > best:
                    best, b = m, (i - 1, j - 1, 1)
            dp[i][j], bp[i][j] = best, b
    i, j, got = U, P, {}
    while i > 0 and j >= 0:
        pi, pj, m = bp[i][j]
        if m:
            got[i - 1] = (j - 1, sc[i - 1][j - 1])
        i, j = pi, pj
    return got


CLABEL = re.compile(r"^.{0,25}?[\dIlLO!|]{1,3}(?:\s*[-–]\s*[\dIlLO!|]{1,3})?\s*[.\]]+\s*(?=[A-Z‘“\"(\'])")


def clean_comm(t):
    t = re.sub(r"(\w)- (\w)", r"\1\2", re.sub(r"\s+", " ", t)).strip()
    t = CLABEL.sub("", t, count=1) if CLABEL.match(t) else t
    return re.sub(r"^.{0,15}?\]\.?\s*(?=[*A-Z‘“\"(\'])", "", t) if "]" in t[:16] else t


def clean(t):
    t = SPEAKER.sub("", t.strip())
    t = LABEL.sub("", t, count=1)
    return re.sub(r"(\w)- (\w)", r"\1\2", re.sub(r"\s+", " ", t)).strip()


def mula_of(u):
    m = [p for p in u.get("parts", []) if p["role"] == "mula"]
    return m[0]["sanskrit"] if m else u["sanskrit"]


def main(fill_only=True):
    B = lines()
    heads = [i for i, l in enumerate(B) if re.match(r"^CHAPTER\b", l.strip()) and i > 1000]
    assert len(heads) == 18, len(heads)
    p = ROOT / "philosophical/bg_shankara.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    by_ch = collections.defaultdict(list)
    for u in d["units"]:
        if not u["ref"].startswith(("intro", "colophon")):
            by_ch[int(u["ref"].split(".")[0])].append(u)
    filled, weak, short = 0, [], []
    for c in range(1, 19):
        a = heads[c - 1] + 1
        b = heads[c] if c < 18 else len(B)
        P = pairs(B, a, b)
        U = by_ch[c]
        got = align([grams(mula_of(u)) for u in U], [grams(x[0]) for x in P])
        idx = sorted((got[i][0], i) for i in got)
        starts = {i: j for j, i in idx}
        order = [i for _, i in idx]
        for n, i in enumerate(order):
            u = U[i]
            j = starts[i]
            nxt = starts[order[n + 1]] if n + 1 < len(order) else len(P)
            trans = clean(P[j][1])
            comm = [P[k] for k in range(j + 1, nxt)]
            while comm and (ZERO.match(comm[-1][0]) or ZERO.match(comm[-1][1])) and n + 1 < len(order):
                comm.pop()
            comm_en = "\n".join(clean_comm(x[1]) for x in comm if x[1].strip())
            if got[i][1] < 0.5:
                weak.append((u["ref"], round(got[i][1], 2)))
                continue
            if fill_only and u.get("english"):
                continue
            if u["scope"] == "mula+commentary" and len(trans) + len(comm_en) < 0.5 * len(u["sanskrit"]):
                short.append(u["ref"])
                continue
            parts = list(u.get("parts", []))
            mp = next((x for x in parts if x["role"] == "mula"), None)
            bp = next((x for x in parts if x["role"] == "bhashya"), None)
            has_b = bool(bp and bp.get("sanskrit"))
            if mp is None:
                mp = {"role": "mula", "sanskrit": u["sanskrit"] if u["scope"] == "mula" else None}
                parts.insert(0, mp)
            mp["english"] = trans
            if comm_en:
                if bp is None:
                    bp = {"role": "bhashya"}
                    parts.append(bp)
                bp["english"] = comm_en
            u["english"] = "\n".join(x for x in (trans, comm_en if has_b else "") if x) or None
            parts = [x for x in parts if x.get("sanskrit") or x.get("english")]
            if parts and not (u["scope"] == "mula" and len(parts) == 1 and not comm_en):
                u["parts"] = parts
            if u["english"]:
                u.setdefault("meta", {})["english_source"] = "Warrier, Ramakrishna Math"
                filled += 1
    print("filled", filled, "weak", weak, "short", short)
    d["notes"] += (f" [Gaps in the Sastri OCR filled from A. G. Krishna Warrier, Bhagavad Gita Bhashya of Shankaracharya (Ramakrishna Math), OCR from archive.org: {filled} units, "
                   "marked meta.english_source. Warrier's verse blocks were matched to units by Devanagari similarity (3-gram dice, monotone alignment), then his commentary paragraphs up to the next verse were attached; "
                   "his commentary paragraphs before a verse that are numbered .0 (chapter 2 introduction) go to the next verse. Units whose match was weak (dice below 0.5) or whose English was under half the Sanskrit length were left null: "
                   f"{', '.join([w[0] for w in weak] + short)}. Footnotes of the printed book can remain inside the English. intro-1 was not filled.]")
    src = d["source_english"]
    d["source_english"] = (src if isinstance(src, list) else [src]) + [{"citation": "Warrier, Bhagavad Gita Bhashya of Shankaracharya, Ramakrishna Math (OCR)", "url": "https://archive.org/details/GEDy_bhagavad-gita-bhashya-of-shankaracharya-with-translation-by-dr.-a.-g-krishna-war", "license": None}]
    write("philosophical/bg_shankara.json", d)
    return d, filled, weak


if __name__ == "__main__":
    main()
