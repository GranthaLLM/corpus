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
        pada = None
        for i in range(a, b if b else len(L)):
            pm = PADA.search(L[i])
            if pm and L[i].strip().startswith("अथ"):
                pada = L[i].strip()
            m = STARTRE.match(L[i])
            if m:
                out.append({"vol": v, "line": i, "name": clean_name(m.group(2)), "ord": m.group(1), "pada": pada})
    return out


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
    units, seen = [], {}
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
        ref = f"v{s['vol']}.{s['line']}"
        units.append({"ref": ref, "kind": None, "sanskrit": text or None, "english": en, "_name": s["name"]})
    return units, len(S), len(E), len(pair)


if __name__ == "__main__":
    units, ns, ne, npair = main()
    for u in units:
        del u["_name"]
    write("philosophical/bhattasangraha.json", dict(
        id="6", text="Bhāṭṭasaṃgraha of Rāghavendratīrtha", tradition="Dvaita", commentator="Rāghavendratīrtha", script="Devanagari", units=units,
        source_sanskrit={"citation": "Raghavendra Tirtha, Bhatta Sangraha (Purvamimamsa), ed. K.T. Pandurangi, Dvaita Vedanta Studies and Research Foundation, Bangalore 2004, vols 1-3 (archive.org djvu OCR)", "url": RAWURL.format("1") + " (also volumes 2 and 3)", "license": None},
        source_english={"citation": "K.T. Pandurangi, 'Exposition of Bhatta Sangraha in English', adhikarana-wise summaries printed in volumes 1 and 3 of the same edition", "url": RAWURL.format("1"), "license": None},
        bundled=False, needs_ocr=False, alignment="by_ref",
        notes=(f"Sanskrit: Raghavendra Tirtha's direct commentary on the Jaimini sutras, one unit per adhikarana (heading 'atha N ... adhikaranam' to the next heading), from archive.org djvu OCR of the three volumes (adhyayas 1-3, 4-6, 7-12); unproofread, Devanagari OCR noise remains. English: the exposition is a SUMMARY of each adhikarana (sangati, purvapaksa, siddhanta) by Pandurangi, not a translation, and it is printed only in volumes 1 and 3, so adhyayas 4-6 (volume 2) have no English. Each Sanskrit unit is paired with the exposition of the same adhikarana by matching the adhikarana names in order (OCR garbles many headings, so {npair} of {ns} units are paired and the rest have english null; {ne} exposition headings were found). The Kannada exposition is ignored. ref = volume.line of the heading in the djvu text, because the Sanskrit headings carry no reliable adhyaya.pada.number.")))
    print("bhattasangraha", len(units), "paired", npair)
