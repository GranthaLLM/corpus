"""Rebuild aitareya_madhva.json from Pandurangi's book, OCR'd page by page (tools: Bodhan IndicOCR run_mac.py).

Needs rapidfuzz (uv run --with rapidfuzz python tools/aitareya_madhva_pandurangi.py) and the OCR pages in
GRANTHA_RAW/aitareya_ocr/page_NNNN.txt. The Sanskrit text of the Upanishad comes from Setutila (the earlier
version of this file, SRC_REV); Pandurangi's own Devanagari is only used to find where each passage sits.
"""
import json, re, subprocess, unicodedata
from rapidfuzz import fuzz
from common import ROOT, RAW, write

SRC_REV = "6dbadfa"
SRC = "upanishads/aitareya_madhva.json"
SKIP = "।॥०१२३४५६७८९॒॑॓॔ ऽ"
UP = re.compile(r"^(उप|उपं|उपः)\s*[-—–:]+\s*")
ORD = {"प्रथम": 1, "द्वितीय": 2, "तृतीय": 3, "चतुर्थ": 4, "पञ्चम": 5, "षष्ठ": 6, "सप्तम": 7, "अष्टम": 8, "नवम": 9, "दशम": 10}


def clean_text(t):
    t = t.replace("▁", " ")
    return re.sub(r"(?:<0x[0-9A-Fa-f]{2}>)+", lambda m: bytes(int(x, 16) for x in re.findall(r"<0x([0-9A-Fa-f]{2})>", m.group(0))).decode("utf-8", "replace"), t)


def kind(s):
    dev = len(re.findall(r"[ऀ-ॿ]", s))
    lat = len(re.findall(r"[A-Za-zāīūṛṣṇṭḍśṃṅñḥ]", s))
    return "D" if dev > lat else "E"


def page_lines(n):
    out = []
    for l in clean_text((RAW / "aitareya_ocr" / f"page_{n:04d}.txt").read_text(encoding="utf-8")).split("\n"):
        s = l.strip()
        if not s or re.search(r"Jangamwadi|eGangotri", s) or re.match(r"</?t(able|head|body|r|d|h)\b", s):
            continue
        if re.fullmatch(r"\d{1,3}\.?", s) or re.fullmatch(r"(?i)AITAREYOPANI\W?\w?AD", s):
            continue
        if len(s) < 40 and re.search(r"(?i)AITAREYOPI|AITAREYOPAN|\bARAN\b|\bARAN\.|\[?\s*(CH|CM|OR|CA|OH)\.?\s*\d+\]?\s*$", s):
            continue
        if len(s) < 22 and re.search(r"RAN\b|ARAN|\bCH\b|\bCM\b", s):
            continue
        if len(s) < 12 and (not re.search(r"[A-Za-zऀ-ॿ]{3}", s) or re.search(r"[ఀ-౿଀-୿]", s)):
            continue
        out.append(s)
    return out


def join_en(ls):
    s = ""
    for l in ls:
        s = s[:-1] + l if s.endswith("-") and l[:1].islower() else (s + " " + l).strip()
    s = re.sub(r"\d*\s*-?\s*\[\W?\s*A?RAN\.?\s*[IVX]+\]?", "", s)
    s = re.sub(r"\[?\s*(?:CH|CM|OH|OR)\.?\s*\d+\s*\]", "", s)
    s = re.sub(r"\[C[XVI]+\.?\s*\d*\]?", "", s).replace("\ufffd", "ñ")
    return re.sub(r"\s+", " ", s).strip()


def passages():
    lines = [l for n in range(1, 217) for l in page_lines(n)]
    items, i = [], 0
    while i < len(lines):
        if not UP.match(lines[i]):
            i += 1
            continue
        dev, j = [UP.sub("", lines[i])], i + 1
        while j < len(lines) and kind(lines[j]) == "D" and not UP.match(lines[j]):
            dev.append(lines[j])
            j += 1
        en = []
        while j < len(lines):
            s = lines[j]
            if s.startswith("Expl") or UP.match(s) or (kind(s) == "D" and len(re.findall(r"[ऀ-ॿ]", s)) > 25):
                break
            en.append(s)
            j += 1
        items.append({"dev": " ".join(dev), "en": join_en(en)})
        i = j
    out = []
    for k, it in enumerate(items):
        if not it["en"] and k + 1 < len(items) and items[k + 1]["dev"][:25] == it["dev"][:25]:
            continue
        out.append(it)
    return out


def norm_keep(s):
    s = unicodedata.normalize("NFC", s)
    pos = [k for k, c in enumerate(s) if "ऀ" <= c <= "ॿ" and c not in SKIP]
    return "".join(s[k] for k in pos), pos


COLO = re.compile(r"(?:[०-९]+/[०-९]+/[०-९]+\s*(?:\([०-९/]+\))?\s*॥?\s*॥?\s*|॥\s*[०-९]+/[०-९]+/[०-९]+\s*॥\s*॥?\s*)?इत्यैतरेयब्राह्मणारण्यककाण्डे[^॥]*(?:॥|$)\s*(?:\([०-९]+\)\s*)?")


def sanitize(t):
    t = re.sub(r"^समाप्त[^॥]*॥\s*(?:ॐ\s*॥\s*)?", "", t.strip())
    t = COLO.sub(" ", t)
    t = re.sub(r"\s*॥\s*[०-९]+/[०-९]+/[०-९]+\s*॥?\s*॥?\s*$", "॥", t)
    t = re.sub(r"\s*\*\s*॥", "॥", re.sub(r"\s*[0-9]+\s*॥", "॥", t))
    return re.sub(r"[ \t]+", " ", t).strip()


def ordinal(tok):
    return next((v for k, v in ORD.items() if tok.startswith(k)), None)


def coords(heading):
    ar = ordinal(heading.split("/")[0].strip())
    parts = [p.strip() for p in heading.split("/")]
    ad = ordinal(parts[1]) if len(parts) > 1 else None
    kh = ordinal(parts[2]) if len(parts) > 2 else None
    return ar, ad, kh


def main():
    old = json.loads(subprocess.check_output(["git", "show", f"{SRC_REV}:{SRC}"], cwd=ROOT))
    part = lambda u, r: next((q for q in u.get("parts", []) if q["role"] == r), None)
    pieces, starts = [], []
    R = ""
    for ui, u in enumerate(old["units"]):
        m = part(u, "mula")["sanskrit"] if part(u, "mula") else u["sanskrit"]
        starts.append(len(R))
        R += m + "\n"
    N, pos = norm_keep(R)
    items = passages()
    spans, prev = [], 0
    for n, it in enumerate(items):
        q, _ = norm_keep(it["dev"])
        if len(q) < 12:
            continue
        lo = max(0, prev - 300)
        a = fuzz.partial_ratio_alignment(q, N[lo:lo + 6000], score_cutoff=70)
        if a is None:
            print("no match", n, it["dev"][:50])
            continue
        s, e = lo + a.dest_start, lo + a.dest_end
        head, tail = q[:36], q[-36:]
        h = fuzz.partial_ratio_alignment(head, N[max(0, s - 250):s + 250], score_cutoff=70)
        if h is not None and len(q) > 80:
            s = max(0, s - 250) + h.dest_start
        t_ = fuzz.partial_ratio_alignment(tail, N[max(0, e - 250):e + 250], score_cutoff=70)
        if t_ is not None and len(q) > 80:
            e = max(0, e - 250) + t_.dest_end
        prev = e
        rs, re_ = pos[s], pos[e - 1] + 1
        while rs > 0 and R[rs - 1] not in " \n":
            rs -= 1
        while re_ < len(R) and R[re_] not in " \n।॥":
            re_ += 1
        while re_ < len(R) and R[re_] in "।॥":
            re_ += 1
        spans.append([rs, re_, it])
    for a, b in zip(spans, spans[1:]):
        a[1] = min(a[1], b[0])
        if len(a[2]["en"]) > 5 * (a[1] - a[0]):
            a[1] = b[0]
    spans = [s for s in spans if s[1] > s[0]]

    units, used = [], {}
    by_unit = {}
    for rs, re_, it in spans:
        ui = max(k for k, st in enumerate(starts) if st <= rs)
        by_unit.setdefault(ui, []).append((rs, re_, it))
    for ui, u in enumerate(old["units"]):
        ar, ad, kh = coords(u["ref"])
        for rs, re_, it in by_unit.get(ui, []):
            key = (ar, ad, kh)
            used[key] = used.get(key, 0) + 1
            sk = re.sub(r"[ \t]+", " ", R[rs:re_]).strip()
            sk = sanitize(sk)
            if not it["en"]:
                continue
            units.append({"ref": f"{ar}.{ad}.{kh}.{used[key]}", "kind": "prose", "scope": "mula", "sanskrit": sk, "english": it["en"]})
        b = part(u, "bhashya")
        if b and b.get("sanskrit"):
            units.append({"ref": f"{ar}.{ad}.{kh}-bhashya", "kind": "prose", "scope": "commentary", "sanskrit": sanitize(b["sanskrit"]), "english": None})
    covered = sum(len(u["sanskrit"]) for u in units if u["scope"] == "mula")
    d = {k: v for k, v in old.items() if k != "units"}
    d["units"] = units
    d["alignment"] = "by_ref"
    d["needs_ocr"] = False
    d["source_english"] = {"citation": "K. T. Pandurangi 1989, Aitareya Upanishat translation (Shriman Madhva Siddhantonnahini Sabha, Chirtanur), scan OCR'd with Bodhan IndicOCR",
                           "url": "https://archive.org/details/yOyz_aitareya-upanishat-translation-by-k-t-pandurangai-shriman-madhva-siddhantonnahini-sabh-chirtanu", "license": None}
    d["notes"] = ("Sanskrit from Setutila/Sarvamula (aitareya.json mula and aitareya_bhashya.json). English: Pandurangi's translation of each Upanishad passage as Madhva reads it, "
                  "from the scan OCR'd page by page with Bodhan's IndicOCR (the Devanagari in his book marks each passage with 'Upanishad:'; those passages were matched to the Setutila mula by character alignment, "
                  f"{len(spans)} found, and the Sanskrit of each unit is the matching stretch of Setutila's text). Units 'A.B.C.n' (aranyaka.adhyaya.khanda.passage) are scope mula: the passage and its translation. "
                  "Pandurangi's 'Expl.' notes and his quotations from Madhva's bhashya are not part of the translation and are left out. "
                  "Madhva's bhashya is kept as one Sanskrit-only unit per khanda ('...-bhashya', scope commentary, no english) because Pandurangi translates it only in summary. "
                  f"Mula text not matched by any passage ({len(R) - covered} of {len(R)} characters) is not in the units. Refs take the aranyaka, adhyaya and khanda of the Setutila unit that holds the start of the passage; Setutila groups some khandas, so a few labels lag one section behind the colophons inside the Sanskrit. Section colophons and numbering that Setutila leaves inside the mula text are stripped. Earlier versions of this file (khanda groups with english that also covered the bhashya) are in git history.")
    n = write(SRC, d)
    print(n, "units;", len(spans), "passages;", covered, "of", len(R), "mula characters covered")


if __name__ == "__main__":
    main()
