import re, json, difflib
from common import *
from setu import blocks, block_text
from build_upanishads import SETU, SETU_LIC

DEVRE = re.compile("[ऀ-ॿ]")
STRIP = re.compile(r"[^ऀ-ॿ]|[।॥ऽ॒॑᳚॓॔०-९ः‌‍ँंऺ़]")
NOISE = re.compile(r"CC-0\.?.*|.*eGangotri.*|.*AITAREYOPANISAD.*|.*Jangamwadi.*", re.I)
# Devanagari OCR confusions in the archive text layer
FIX = str.maketrans({"ऽ": "", "‌": "", "‍": ""})


def norm(s):
    return STRIP.sub("", (s or "").translate(FIX))


def tri(s):
    return {s[i:i + 3] for i in range(len(s) - 2)}


def dev_frac(p):
    d = len(DEVRE.findall(p))
    a = sum(1 for c in p if c.isalpha())
    return d / max(a, 1)


def paras():
    t = (RAW / "ia" / "pandurangi_aitareya_0.txt").read_text(encoding="utf-8", errors="replace")
    t = t[t.index("ऐतरेयोपनिषत्"):]
    out = []
    for blk in re.split(r"\n\s*\n", t):
        ls = [re.sub(r"\s+", " ", l).strip() for l in blk.split("\n")]
        ls = [l for l in ls if l and not NOISE.match(l)]
        if ls:
            out.append(" ".join(ls))
    return out


def items():
    res, cur = [], None
    for p in paras():
        if dev_frac(p) > 0.5 and len(norm(p)) >= 8:
            if cur is None or cur["en"]:
                cur = {"dev": [], "en": []}
                res.append(cur)
            cur["dev"].append(p)
        elif cur is not None:
            cur["en"].append(p)
    return [(" ".join(i["dev"]), " ".join(i["en"])) for i in res]


def khandas():
    """Khanda skeleton from Setutila: mula (aitareya.json) and bhashya (aitareya_bhashya.json) grouped by Heading3."""
    out = []
    for fname, key in (("set_aitareya.json", "mula"), ("set_aitareya_bhashya.json", "bhashya")):
        t, c = blocks(RAW / fname)
        ks, path = [], {}
        cur = None
        for b in c:
            ct = b["content_type"]
            tx = block_text(b)
            if ct.startswith("Heading"):
                lvl = int(ct[7:])
                path = {k: v for k, v in path.items() if k < lvl}
                path[lvl] = tx
                if lvl == 3:
                    cur = {"head": " / ".join(path[k] for k in sorted(path)), "txt": []}
                    ks.append(cur)
                continue
            if cur is not None and ct in ("Mula", "Sarvamula", "Colophon_Mula", "Colophon_Sarvamula"):
                cur["txt"].append((ct, tx))
        out.append(ks)
    return out


def build():
    km, kb = khandas()
    assert len(km) == len(kb), (len(km), len(kb))
    mula_blocks = [(ki, tx) for ki, k in enumerate(km) for ct, tx in k["txt"] if ct == "Mula"]
    NM = [norm(t) for _, t in mula_blocks]
    TM = [tri(x) for x in NM]
    its = items()
    last = -1
    pos = []  # (item index, khanda)
    for n_, (dev, en) in enumerate(its):
        nd = norm(dev)
        if len(nd) < 25:
            continue
        td = tri(nd)
        top = sorted(((len(td & TM[k]) / max(1, len(td)), k) for k in range(len(NM))), reverse=True)[:5]
        best = None
        for _, k in top:
            sm = difflib.SequenceMatcher(None, nd[:1500], NM[k][:3000], autojunk=False)
            cov = sum(mb.size for mb in sm.get_matching_blocks()) / max(1, min(len(nd), 1500))
            if best is None or cov > best[0]:
                best = (cov, k)
        if best and best[0] >= 0.5:
            pos.append((n_, mula_blocks[best[1]][0], round(best[0], 2)))
    # keep the max-weight monotone (non-decreasing khanda) subsequence
    dp = []
    for i, (n_, ki, w) in enumerate(pos):
        bestp, bestw = -1, 0.0
        for j in range(i):
            if pos[j][1] <= ki and dp[j][0] > bestw:
                bestp, bestw = j, dp[j][0]
        dp.append((bestw + w, bestp))
    if pos:
        i = max(range(len(pos)), key=lambda x: dp[x][0])
        keep = []
        while i != -1:
            keep.append(pos[i])
            i = dp[i][1]
        pos = keep[::-1]
    return km, kb, its, pos


def write_file():
    km, kb, its, pos = build()
    first = {}
    for n_, ki, w in pos:
        first.setdefault(ki, (n_, w))
    anchored = sorted(first)
    groups = []
    for a, k in enumerate(anchored):
        end = anchored[a + 1] - 1 if a + 1 < len(anchored) else len(km) - 1
        start_k = 0 if a == 0 else k
        groups.append((start_k, end, first[k][0], first[anchored[a + 1]][0] if a + 1 < len(anchored) else len(its),
                       [w for n_, ki, w in pos if start_k <= ki <= end]))
    units = []
    for gk, (k0, k1, i0, i1, ws) in enumerate(groups):
        mula = "\n".join(tx for k in range(k0, k1 + 1) for ct, tx in km[k]["txt"])
        bh = "\n".join(tx for k in range(k0, k1 + 1) for ct, tx in kb[k]["txt"])
        en = "\n".join(e for d, e in its[i0:i1] if e)
        en = re.sub(r"\n\s*\n", "\n", en)
        units.append({"ref": f"{km[k0]['head']}" + (f" .. {km[k1]['head'].split(' / ')[-1]}" if k1 > k0 else ""), "kind": "mula+bhashya",
                      "sanskrit": "\n".join(x for x in (mula, bh) if x), "sanskrit_mula": mula, "sanskrit_bhashya": bh,
                      "english": en or None, "match_min": min(ws) if ws else None})
    write("upanishads/aitareya_madhva.json", dict(
        id="aitareya_madhva", text="Aitareya Upaniṣad Madhvabhāṣya", tradition="Dvaita", commentator="Madhva", script="Devanagari", units=units,
        source_sanskrit={"citation": "Setutila/Sarvamula aitareya.json (mula) and aitareya_bhashya.json (Madhva's bhashya)", "url": SETU + "aitareya_bhashya.json", "license": SETU_LIC},
        source_english={"citation": "K. T. Pandurangi 1989, Aitareya Upanishat translation (Shriman Madhva Siddhantonnahini Sabha, Chitrapur/Chirtanur), archive.org OCR text layer", "url": "https://archive.org/details/yOyz_aitareya-upanishat-translation-by-k-t-pandurangai-shriman-madhva-siddhantonnahini-sabh-chirtanu", "license": None},
        bundled=False, needs_ocr=True, alignment="by_ref",
        notes=(f"Sanskrit = Setutila mula (aitareya.json) + Madhva bhashya (aitareya_bhashya.json), both cut into the same 37 khandas by their own headings. English = Pandurangi's translation of the mantras plus Madhva's bhashya plus his 'Expl.' notes, as printed (not separable here), from the archive.org OCR of the scan (the PDF has no text layer; Sarvam Vision was not used because 216 pages exceeds the remaining credit). "
               f"Pandurangi's Devanagari mantras were matched to Setutila's mula blocks by character alignment (coverage >= 0.5); the best monotone chain gave {len(pos)} anchors over {len(first)} of {len(km)} khandas (median coverage {sorted(p[2] for p in pos)[len(pos)//2]:.2f}). Khandas with no anchor are merged into the preceding anchored khanda's unit, so units are khanda groups ({len(units)} units), each pairing all its Sanskrit with the English printed between its first anchor and the next group's first anchor. "
               "Caveat: Pandurangi does not translate Madhva's bhashya line by line; he translates each mantra as Madhva interprets it and adds short 'Expl.' notes, so the English is complete for sanskrit_mula but only a summary of sanskrit_bhashya (English is often 0.1-0.5x the Sanskrit length). Use sanskrit_mula against the English for translation scoring; do not treat sanskrit as fully translated. Introductory matter before the first mantra is excluded. Archive OCR noise in English and Devanagari is expected. Treat as a first pass; a Sarvam Vision re-OCR would allow a finer match.")))
    print(len(units), [(u['ref'][:40], len(u['sanskrit']), len(u['english'] or '')) for u in units])


if __name__ == "__main__":
    write_file()
