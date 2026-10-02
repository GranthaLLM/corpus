import difflib, re
from common import *

ZW = str.maketrans("", "", "‌‍ \t")
STARTRE = re.compile(r"^\s*अथ\s+(\S+)\s+(.*?\S*करणम्)")
EXPRE = re.compile(r"^(.*?)\s*(?:अ)?धिकरणम्[‌‍ ]*\(\s*(\d{1,2})\s*[-–—]\s*(\d)\s*[-–—]\s*(\d{1,3})\s*\)")
PADA = re.compile(r"(\S*ाध्यायस्य|\S*अध्यायस्य)\s+(\S+)\s+पाद")
ORD = re.compile(r"^(?:प्रथम\S*|द्वितीय\S*|तृतीय\S*|तुरीय\S*|चतुर्थ\S*|पञ्चम\S*|पश्चम\S*|षष्ठ\S*|सप्तम\S*|अष्टम\S*|नवम\S*|दशम\S*|एकादश\S*|द्वादश\S*|त्रयोदश\S*|चतुर्दश\S*|पञ्चदश\S*|षोडश\S*|सप्तदश\S*|अष्टादश\S*|एकोनविंश\S*|विंश\S*)\s*")
HDR = re.compile(r"^\s*\d{0,4}\s*(?:भा\S{1,3}सङ्?[गक]हः?|अधिकरणार्थस\S*|Bhatta\s+Sa\S*)\s*\d{0,4}\s*$|^\s*\d{0,4}\s*\S*ाध्याये\s+\S+\s+पादः\s*\d{0,4}\s*$|^\s*\d{1,4}\s*$|^\s*\S*ाध्यायस्य\s+\S+\s+पादः\s*\d{0,4}\s*$|^\s*(?:[ivxl\d]+\s+)?Bhatta\s+Sa\S*(?:\s+-?\s*\S*)?\s*\d*\s*$")
VOLS = {1: (340, 8760, 10600, 21050), 2: (3230, None, None, None), 3: (370, 13800, 13800, None)}
SRC_FILE = "bhatta_v{}.txt"
RAWURL = "https://archive.org/stream/bhaatta-sangraha-ocr/Bhaatta-Sangraha_Volume_{}-compressed_OCR_djvu.txt"



ORDS = [("प्रथम", 1), ("द्वितीय", 2), ("तृतीय", 3), ("तुरीय", 4), ("चतुर्थ", 4), ("पञ्चम", 5), ("पश्चम", 5), ("षष्ठ", 6), ("षष्ट", 6), ("सप्तम", 7), ("अष्टम", 8),
        ("नवम", 9), ("नबम", 9), ("दशम", 10), ("एकादश", 11), ("द्वादश", 12), ("त्रयोदश", 13), ("चतुर्दश", 14), ("पञ्चदश", 15), ("पश्चदश", 15), ("षोडश", 16),
        ("सप्तदश", 17), ("अष्टादश", 18), ("एकोनविंश", 19), ("एकोनबिंश", 19), ("विंश", 20), ("बिंश", 20), ("एकविंश", 21), ("एकबिंश", 21), ("द्वाविंश", 22)]
ORDS.sort(key=lambda x: -len(x[0]))
START2 = re.compile(r"^\s*अ[थध]([ाैौ]\S*)\s+(.*?\S*करणम्)")
VOW = {"ा": "अ", "ै": "ए", "ौ": "ओ"}
PADAS = {1: [(1, 4), (2, 4), (3, 8)], 2: [(4, 4), (5, 4), (6, 8)], 3: [(7, 4), (8, 4), (9, 4), (10, 8), (11, 4), (12, 4)]}
PADA_END = re.compile(r"पादे\s+अधिकरणानि")
SUMMARY = {"start": "brief summary of Chapter IV", "end": "above brief summary of the contents"}


def ordnum(w):
    w = w.replace("\u200c", "").replace("\u200d", "")
    return next((v for k, v in ORDS if w.startswith(k)), None)


def norm(s):
    s = s.translate(ZW)
    s = re.sub(r"[ंँ]", "म्", s).replace("ऽ", "")
    return re.sub(r"[|॥।\.\(\)\[\]\-–—:,;'‘’\"“”0-9०-९]", "", s)


def clean_name(n):
    n = n.strip()
    for _ in range(2):
        n = ORD.sub("", n)
    return re.sub(r"(?:अ)?धिकरणम्.*$", "", n)


def sim(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def load(v):
    return (RAW / SRC_FILE.format(v)).read_text(encoding="utf-8").split("\n")


def sanskrit_starts():
    out = []
    for v, (a, b, _, _) in VOLS.items():
        L = load(v)
        hi = b if b else len(L)
        ends = [i for i in range(a, hi) if PADA_END.search(L[i])]
        padas = [(ad, pd) for ad, n in PADAS[v] for pd in range(1, n + 1)]
        lo = a
        for k, e in enumerate(ends[:len(padas)]):
            ad, pd = padas[k]
            n = 0
            for i in range(lo, e):
                m = STARTRE.match(L[i])
                nm = None
                if m:
                    nm = (ordnum(m.group(1)), m.group(2))
                else:
                    m = START2.match(L[i])
                    if m:
                        nm = (ordnum(VOW[m.group(1)[0]] + m.group(1)[1:]), m.group(2))
                if nm:
                    n = nm[0] if nm[0] else n + 1
                    out.append({"vol": v, "line": i, "name": clean_name(nm[1]), "adh": ad, "pada": pd, "n": n, "ref": f"{ad}.{pd}.{n}"})
            lo = e + 1
    seen = {}
    for s in out:
        seen[s["ref"]] = seen.get(s["ref"], 0) + 1
        if seen[s["ref"]] > 1:
            s["ref"] += f"-{seen[s['ref']]}"
    return out


def summary_items():
    L = load(2)
    a = next(i for i, l in enumerate(L) if SUMMARY["start"] in l)
    b = next(i for i, l in enumerate(L) if SUMMARY["end"] in l)
    item = re.compile(r"^\((\d+)([ab]?)((?:\s*,\s*\d+)*)\)\s*(.*)")
    noise = re.compile(r"^\s*(?:[ivxl]+\s+Introduction|Introduction\s+[ivxlXx]+\w*|\d{1,2}|[A-Z]|1D|2A|3A|Introduction\s+\S{1,6})\s*$", re.I)
    chap, sec, prev, items, cur = 4, 1, 0, [], None
    for l in L[a:b]:
        s = l.strip()
        if not s or noise.match(s):
            continue
        m = re.match(r"^Chapter\s+(V|VI)\s+Section\s+I\b", s)
        if m:
            chap, sec, prev, cur = {"V": 5, "VI": 6}[m.group(1)], 1, 0, None
            continue
        if re.match(r"^(?:A brief summary of )?Chapter IV Section I", s) or re.match(r"^Section\s+(?:I{1,3}|IV|V|VI{1,3}|VIII)\s*$", s):
            cur = None
            continue
        mi = item.match(s)
        if mi:
            n = int(mi.group(1))
            if (n <= prev and not mi.group(2)) or (mi.group(2) and n < prev):
                sec += 1
            prev = n
            cur = {"ref": f"{chap}.{sec}.{n}", "covers": [n] + [int(x) for x in re.findall(r"\d+", mi.group(3))], "text": mi.group(4)}
            items.append(cur)
        elif cur is not None:
            cur["text"] += " " + s
    out = {}
    for it in items:
        t = re.sub(r"\s*\(\s*[IVXlvx1]{1,4}\s*[-–]\s*(?:[IVXlvx1]{1,5}|\d)\s*[-–]?\s*\d+[ab]?(?:\s*,\s*\d+)*\s*\)\s*\.?\s*$", "", it["text"]).strip()
        e = out.setdefault(it["ref"], {"text": [], "covers": it["covers"]})
        e["text"].append(t)
    return {k: {"text": "\n".join(v["text"]), "covers": v["covers"]} for k, v in out.items()}


def expo_heads():
    out = []
    for v in (1, 3):
        _, _, a, b = VOLS[v]
        L = load(v)
        for i in range(a, min(b or len(L), len(L))):
            m = EXPRE.match(L[i])
            if m:
                out.append({"vol": v, "line": i, "name": m.group(1), "nname": norm(m.group(1))})
    return out


def dp(S, E, thr):
    n, m = len(S), len(E)
    cache, D, B = {}, [[0] * (m + 1) for _ in range(n + 1)], [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            s = cache[(i, j)] = sim(S[i - 1]["nname"], E[j - 1]["nname"])
            best, b = D[i - 1][j], "u"
            if D[i][j - 1] > best:
                best, b = D[i][j - 1], "w"
            if s >= thr and D[i - 1][j - 1] + s > best:
                best, b = D[i - 1][j - 1] + s, "m"
            D[i][j], B[i][j] = best, b
    i, j, P = n, m, []
    while i > 0 and j > 0:
        b = B[i][j]
        if b == "m":
            P.append((i - 1, j - 1, cache[(i, j)]))
            i, j = i - 1, j - 1
        elif b == "u":
            i -= 1
        else:
            j -= 1
    return P[::-1]


JUNK = re.compile(r"(?<!\S)[0-9*€!?|]*[ಀ-೿A-Za-z][ಀ-೿A-Za-z0-9*€!?|]{0,4}(?!\S)")


def block(L, a, b, sanskrit=False):
    out = []
    for l in L[a:b]:
        if HDR.match(l) or not l.strip():
            continue
        if sanskrit:
            l = re.sub(r"[ \t]{2,}", " ", JUNK.sub("", l)).strip()
            if not l:
                continue
        out.append(l.strip())
    return "\n".join(out)


def main():
    S = sanskrit_starts()
    for s in S:
        s["nname"] = norm(s["name"])
    E = expo_heads()
    S13 = [s for s in S if s["vol"] in (1, 3)]
    P = dp(S13, E, 0.6)
    pair = {S13[a]["line"] + 100000 * S13[a]["vol"]: (b, sc) for a, b, sc in P}
    anchors = [(-1, -1)] + [(a, b) for a, b, _ in P] + [(len(S13), len(E))]
    for (a1, b1), (a2, b2) in zip(anchors, anchors[1:]):
        gi, gj = list(range(a1 + 1, a2)), list(range(b1 + 1, b2))
        if not gi or not gj:
            continue
        for a, b, sc in dp([S13[x] for x in gi], [E[y] for y in gj], 0.45):
            pair[S13[gi[a]]["line"] + 100000 * S13[gi[a]]["vol"]] = (gj[b], sc)
    units, seen, used = [], {}, set()
    summ = summary_items()
    byvol = {v: load(v) for v in (1, 2, 3)}
    for k, s in enumerate(S):
        nxt = next((x for x in S[k + 1:] if x["vol"] == s["vol"]), None)
        L = byvol[s["vol"]]
        end = nxt["line"] if nxt else (8760 if s["vol"] == 1 else (13800 if s["vol"] == 3 else len(L)))
        text = block(L, s["line"], end, sanskrit=True)
        key = s["line"] + 100000 * s["vol"]
        en = None
        if key in pair:
            j = pair[key][0]
            e = E[j]
            nxt_e = next((x for x in E[j + 1:] if x["vol"] == e["vol"]), None)
            eend = nxt_e["line"] if nxt_e else min(len(byvol[e["vol"]]), 21050 if e["vol"] == 1 else len(byvol[3]))
            en = block(byvol[e["vol"]], e["line"] + 1, eend) or None
        meta_cov = None
        if s["vol"] == 2 and s["ref"] in summ:
            en = summ[s["ref"]]["text"] or None
            cov = summ[s["ref"]]["covers"]
            meta_cov = f"{cov[0]}-{cov[-1]}" if len(cov) > 1 else None
            used.add(s["ref"])
        u = {"ref": s["ref"], "kind": None, "sanskrit": text or None, "english": en, "_name": s["name"]}
        if meta_cov:
            u["english_covers"] = meta_cov
        units.append(u)
    return units, len(S), len(E), len(pair), len(summ), len(used)


if __name__ == "__main__":
    units, ns, ne, npair, nsum, nused = main()
    for u in units:
        del u["_name"]
    write("philosophical/bhattasangraha.json", dict(
        id="6", text="Bhāṭṭasaṃgraha of Rāghavendratīrtha", tradition="Dvaita", commentator="Rāghavendratīrtha", script="Devanagari", units=units,
        source_sanskrit={"citation": "Raghavendra Tirtha, Bhatta Sangraha (Purvamimamsa), ed. K.T. Pandurangi, Dvaita Vedanta Studies and Research Foundation, Bangalore 2004, vols 1-3 (archive.org djvu OCR)", "url": RAWURL.format("1") + " (also volumes 2 and 3)", "license": None},
        source_english={"citation": "K.T. Pandurangi, 'Exposition of Bhatta Sangraha in English', adhikarana-wise summaries printed in volumes 1 and 3 of the same edition", "url": RAWURL.format("1"), "license": None},
        bundled=False, needs_ocr=False, alignment="by_ref",
        notes=(f"Sanskrit: Raghavendra Tirtha's direct commentary on the Jaimini sutras, one unit per adhikarana (heading 'atha N ... adhikaranam' to the next heading), from archive.org djvu OCR of the three volumes (adhyayas 1-3, 4-6, 7-12); unproofread, Devanagari OCR noise remains and some adhikarana headings were lost to OCR, so a few adhikaranas are missing or merged. ref = adhyaya.pada.n, with n read from the ordinal word in the heading (-2, -3 where OCR repeats one). English is NOT a translation: it is Pandurangi's summary of each adhikarana. Volumes 1 and 3 print it as an adhikarana-wise 'Exposition in English' (sangati, purvapaksa, siddhanta), paired to the Sanskrit by heading name in order; volume 2 prints it as a brief numbered summary in its introduction, paired by adhyaya.pada.number (a few items cover two adhikaranas and sit on the first, see english_covers; the summary skips some adhikaranas). Inline Sanskrit terms and quoted verses inside the English are left or stripped as in the other files. {npair} of {ns} units are paired in total in this run; the rest have english null. The Kannada exposition is ignored.")))
    print("bhattasangraha", len(units), "paired", npair, "summary items", nsum, "used", nused)
