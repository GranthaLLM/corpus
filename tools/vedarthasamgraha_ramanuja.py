"""Build philosophical/vedarthasamgraha.json: GRETIL Sanskrit (Ishitobi, IAST converted to Devanagari) paired with Raghavachar's English (1978), aligned by content.

Sources are read from GRANTHA_RAW: ramvaspu.txt (GRETIL plain text) and vedartha_sangraha.pdf text (pdftotext -layout, as vs.txt).
"""
import json
import os
import re
import sys
from pathlib import Path

RAW = Path(os.environ.get("GRANTHA_RAW", "."))

IAST_V = {"a": "अ", "ā": "आ", "i": "इ", "ī": "ई", "u": "उ", "ū": "ऊ", "ṛ": "ऋ", "ṝ": "ॠ", "ḷ": "ऌ", "e": "ए", "ai": "ऐ", "o": "ओ", "au": "औ"}
IAST_M = {"ā": "ा", "i": "ि", "ī": "ी", "u": "ु", "ū": "ू", "ṛ": "ृ", "ṝ": "ॄ", "ḷ": "ॢ", "e": "े", "ai": "ै", "o": "ो", "au": "ौ"}
IAST_C = {"k": "क", "kh": "ख", "g": "ग", "gh": "घ", "ṅ": "ङ", "c": "च", "ch": "छ", "j": "ज", "jh": "झ", "ñ": "ञ", "ṭ": "ट", "ṭh": "ठ", "ḍ": "ड", "ḍh": "ढ", "ṇ": "ण",
          "t": "त", "th": "थ", "d": "द", "dh": "ध", "n": "न", "p": "प", "ph": "फ", "b": "ब", "bh": "भ", "m": "म", "y": "य", "r": "र", "l": "ल", "v": "व", "ś": "श", "ṣ": "ष", "s": "स", "h": "ह"}
VIRAMA = "्"


def tokens(s):
    keys = sorted(set(IAST_V) | set(IAST_C) | {"ṃ", "ṁ", "ḥ", "'", "’", "//", "/"}, key=len, reverse=True)
    i = 0
    while i < len(s):
        for k in keys:
            if s.startswith(k, i):
                yield k
                i += len(k)
                break
        else:
            yield s[i]
            i += 1


def to_devanagari(s):
    out = []
    prev_cons = False
    for tk in tokens(s):
        if tk in IAST_C:
            if prev_cons:
                out.append(VIRAMA)
            out.append(IAST_C[tk])
            prev_cons = True
        elif tk in IAST_V:
            if prev_cons:
                if tk != "a":
                    out.append(IAST_M[tk])
            else:
                out.append(IAST_V[tk])
            prev_cons = False
        else:
            if prev_cons:
                out.append(VIRAMA)
                prev_cons = False
            if tk == "//":
                out.append("॥")
            elif tk == "/":
                out.append("।")
            elif tk in ("ṃ", "ṁ"):
                out.append("ं")
            elif tk == "ḥ":
                out.append("ः")
            elif tk in ("'", "’"):
                out.append("ऽ")
            else:
                out.append(tk)
    if prev_cons:
        out.append(VIRAMA)
    return "".join(out)


def sanskrit_paragraphs():
    t = (RAW / "ramvaspu.txt").read_text(encoding="utf-8")
    t = t[t.index("# Text"):]
    paras = {}
    for m in re.finditer(r"(.+?)\s*\(?RVas_(\d+)\)?", t, re.S):
        n = int(m.group(2))
        txt = re.sub(r"^# Text\s*", "", m.group(1)).strip()
        paras[n] = txt
    return paras


def clean_iast(s):
    s = s.replace("pitqn", "pitṝn")
    s = re.sub(r"/\s*/", "//", s)
    s = re.sub(r"\s*//", " //", s)
    s = re.sub(r"(?<!/)\s*/(?!/)", " /", s)
    return re.sub(r"\s+", " ", s).strip()


def english_paragraphs():
    t = (RAW / "vs.txt").read_text(encoding="utf-8")
    body = t[t.index("|| SRI ||"):]
    lines = [l.rstrip() for l in body.split("\n")]
    lines = [l for l in lines if not re.fullmatch(r"\s*\d{1,3}\s*", l)]
    pre, paras, cur, exp = [], {}, None, 1
    for l in lines:
        m = re.match(r"^(\d{1,3})\.\s+(\S.*)", l)
        if m and exp <= int(m.group(1)) <= exp + 2:
            cur = int(m.group(1))
            exp = cur + 1
            paras[cur] = [m.group(2)]
            continue
        (pre if cur is None else paras[cur]).append(l)
    norm = lambda ls: re.sub(r"\s+", " ", " ".join(x.strip() for x in ls)).strip()
    return norm(pre), {k: norm(v) for k, v in paras.items()}


import math
import unicodedata

VOW = re.compile(r"[aeiouy]")


def skel(w):
    w = unicodedata.normalize("NFKD", w.lower())
    w = "".join(c for c in w if not unicodedata.combining(c))
    w = w.replace("sh", "s").replace("ch", "c").replace("th", "t").replace("dh", "d").replace("kh", "k").replace("gh", "g").replace("bh", "b").replace("ph", "p").replace("jh", "j")
    return VOW.sub("", w)


def sk_skeleton(iast):
    t = unicodedata.normalize("NFC", iast.lower())
    t = t.replace("ṛ", "r").replace("ṝ", "r")
    return skel(re.sub(r"[^a-zāīūṛṝḷṃḥṅñṭḍṇśṣ]", "", t))


def en_terms(text):
    ws = re.findall(r"[A-Za-zāīūṛṝṃḥṅñṭḍṇśṣ]{4,}", text)
    return {skel(w) for w in ws if len(skel(w)) >= 3}


def align(sk_ids, sk_iast, en_ids, en_text, w_ov=4.0, w_len=1.5):
    from collections import Counter

    sk_sk = [sk_skeleton(sk_iast[i]) for i in sk_ids]
    et = [en_terms(en_text[j]) for j in en_ids]
    df = Counter(t for ts in et for t in ts)
    N = len(en_ids)
    idf = {t: math.log(N / c) for t, c in df.items()}
    slen = [len(to_devanagari(clean_iast(sk_iast[i]))) for i in sk_ids]
    elen = [len(en_text[j]) for j in en_ids]
    r = sum(elen) / sum(slen)

    def score(a, b, c, d):
        sk_text = "".join(sk_sk[a:b])
        terms = set().union(*et[c:d])
        w = sum(idf[t] for t in terms)
        hit = sum(idf[t] for t in terms if t in sk_text)
        ov = hit / w if w else 0
        ls = sum(slen[a:b]) * r
        le = sum(elen[c:d])
        return w_ov * ov - w_len * abs(math.log((le + 40) / (ls + 40)))

    n, m = len(sk_ids), len(en_ids)
    NEG = -1e18
    best = [[NEG] * (m + 1) for _ in range(n + 1)]
    back = [[None] * (m + 1) for _ in range(n + 1)]
    best[0][0] = 0.0
    steps = [(1, k) for k in range(1, 13)] + [(k, 1) for k in range(2, 4)]
    for i in range(n + 1):
        for j in range(m + 1):
            if best[i][j] == NEG:
                continue
            for di, dj in steps:
                a, c = i + di, j + dj
                if a > n or c > m:
                    continue
                v = best[i][j] + score(i, a, j, c)
                if v > best[a][c]:
                    best[a][c] = v
                    back[a][c] = (i, j)
    out, i, j = [], n, m
    while (i, j) != (0, 0):
        pi, pj = back[i][j]
        out.append((pi, i, pj, j))
        i, j = pi, pj
    return list(reversed(out))


def split_preamble(pre):
    pre = re.sub(r"^\|\| SRI \|\|\s*VEDARTHA SANGRAHAH\s*", "", pre).strip()
    v1, rest = pre.split("(1)", 1)
    v2 = rest.split("(2)", 1)[0]
    return v1.strip(), v2.strip()


def strip_footnote_marks(t):
    return re.sub(r"(?<=[\)\.\'\u2019\u201d])(\d{1,2})(?=[\s\.,;]|$)", "", t)


def build():
    sk = sanskrit_paragraphs()
    pre, en = english_paragraphs()
    iast = {i: clean_iast(sk[i]) for i in sk}
    last = re.search(r"This work, Vedanta-sangraha.*$", en[252])
    en = dict(en)
    closing = en[252][last.start():]
    en[252] = en[252][: last.start()].strip()
    sk_ids = [i for i in sorted(sk) if 3 <= i < 145]
    en_ids = sorted(en)
    runs = align(sk_ids, iast, en_ids, en, 6.0, 1.0)
    dev = lambda i: to_devanagari(iast[i])
    v1, v2 = split_preamble(pre)
    units = [
        {"ref": "1", "kind": "verse", "scope": "text", "sanskrit": dev(1), "english": v1},
        {"ref": "2", "kind": "verse", "scope": "text", "sanskrit": dev(2), "english": v2},
    ]
    for a, b, c, d in runs:
        ids = sk_ids[a:b]
        ref = str(ids[0]) if len(ids) == 1 else f"{ids[0]}-{ids[-1]}"
        e_ids = en_ids[c:d]
        e_ref = str(e_ids[0]) if len(e_ids) == 1 else f"{e_ids[0]}-{e_ids[-1]}"
        units.append({
            "ref": ref, "kind": "prose", "scope": "text",
            "sanskrit": "\n".join(dev(i) for i in ids),
            "english": "\n".join(strip_footnote_marks(en[j]) for j in e_ids),
            "meta": {"english_paras": e_ref},
        })
    units.append({"ref": "145", "kind": "verse", "scope": "text", "sanskrit": dev(145), "english": closing, "meta": {"english_paras": "252 (last sentence)"}})
    return units


if __name__ == "__main__":
    from common import write

    units = build()
    write("philosophical/vedarthasamgraha.json", {
        "id": "26",
        "text": "Vedārthasaṃgraha",
        "tradition": "Vishishtadvaita",
        "commentator": "Rāmānuja",
        "script": "Devanagari",
        "units": units,
        "source_sanskrit": {"citation": "Rāmānuja, Vedārthasaṃgraha, GRETIL (input Sadanori Ishitobi, analytic text), IAST converted to Devanagari", "url": "https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/html/sa_rAmAnuja-vedArthasaMgraha.htm", "license": "CC BY-NC-SA 4.0 (GRETIL)"},
        "source_english": {"citation": "S. S. Raghavachar, Vedartha Sangraha of Sri Ramanujacarya (Sri Ramakrishna Ashrama, Mysore, 1978), as hosted by Srimatham", "url": "https://www.srimatham.com/uploads/5/5/4/9/5549439/vedartha_sangraha.pdf", "license": None},
        "bundled": False,
        "needs_ocr": False,
        "alignment": "by_ref",
        "notes": "Independent prose treatise (Ramanuja's account of the Upanishadic teaching), not a verse-by-verse commentary. GRETIL's 144 paragraphs (ref = GRETIL RVas number, 93 missing in the source) were paired with Raghavachar's 248 numbered paragraphs (119 and a few others are skipped in the translation) by monotone alignment on shared transliterated terms and length, then checked by eye; meta.english_paras gives the English paragraph numbers in each unit. Sanskrit is GRETIL's analytic text (sandhi-split spacing kept), converted from IAST. Raghavachar adds bracketed words and footnote marks were stripped. The two opening verses and the closing verse are their own units.",
        "reference_type": "translation",
        "english_rights": ["in_copyright_or_unclear"],
    })
    print(len(units), "units")
