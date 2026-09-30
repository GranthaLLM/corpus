import re, zipfile, html
from common import *

SETU_LIC = "CC0 1.0 (Setutila/Sarvamula)"


def paras(path):
    x = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
    out = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", x, re.S):
        sty = re.search(r'<w:pStyle w:val="([^"]+)"', p)
        t = html.unescape("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)))
        out.append((sty.group(1) if sty else "", t.strip()))
    return out


def build(path):
    P = paras(path)
    units, cur, mode, pada, adh = [], None, None, 0, 0
    ordn = {"First": 1, "Second": 2, "Third": 3, "Fourth": 4}

    def flush():
        nonlocal cur
        if cur:
            u = cur
            bh = "\n".join(u.pop("_be")) or None
            u["english_bhashya"] = bh
            if bh:
                u["sanskrit"] = "\n".join(x for x in (u["sanskrit_mula"], u["sanskrit_bhashya"]) if x) or None
            else:
                u["sanskrit"] = u["sanskrit_mula"]
            u["english"] = "\n".join(x for x in (u["english_mula"], bh) if x) or None
            units.append(u)
            cur = None

    special = None
    for sty, t in P[1:]:
        if not t:
            continue
        if sty == "Heading2":
            flush(); adh = ordn.get(t.split()[0], adh); continue
        if sty == "Heading3":
            flush(); pada = ordn.get(t.split()[0], pada); mode = None; continue
        m = re.match(r"^Sutra (\d+\.\d+\.\d+)$", t)
        if m:
            flush()
            cur = {"ref": m.group(1), "kind": "mula+bhashya", "sanskrit_mula": None, "sanskrit_bhashya": None,
                   "english_mula": None, "_be": []}
            mode = None
            continue
        m = re.match(r"^(Mangalacharana|Introduction to the Bhashya) \((Sanskrit|English)\): (.*)$", t)
        if m:
            nm, lang, body = m.groups()
            key = "mangalacharana" if nm.startswith("Mang") else "intro-bhashya"
            u = next((x for x in units if x["ref"] == key), None)
            if u is None:
                u = {"ref": key, "kind": "bhashya", "sanskrit_mula": None, "sanskrit_bhashya": None, "english_mula": None,
                     "english_bhashya": None, "sanskrit": None, "english": None}
                units.append(u)
            if lang == "Sanskrit":
                u["sanskrit"] = u["sanskrit_bhashya"] = body
            else:
                u["english"] = u["english_bhashya"] = body
            continue
        m = re.match(r"^Introduction: (.*)$", t)
        if m and cur is None:
            units.append({"ref": f"{adh}.{pada}.intro", "kind": "prose", "sanskrit": None, "english": m.group(1)})
            continue
        if cur is not None:
            m = re.match(r"^(Sutra|Bhashya) \((Sanskrit|English)\):\s*(.*)$", t)
            if m:
                w, lang, body = m.groups()
                if w == "Sutra" and lang == "Sanskrit":
                    cur["sanskrit_mula"] = body
                elif w == "Sutra":
                    cur["english_mula"] = None if body.startswith("[") else (body or None)
                elif lang == "Sanskrit":
                    cur["sanskrit_bhashya"] = body or None
                else:
                    mode = "be"
                    if body:
                        cur["_be"].append(body)
                continue
            if mode == "be":
                cur["_be"].append(t)
    flush()
    return units


if __name__ == "__main__":
    u = build(RAW / "BSB_Complete_AllAdhyayas.docx")
    sutras = [x for x in u if x["kind"] == "mula+bhashya"]
    miss = [x["ref"] for x in sutras if not x["english_bhashya"]]
    write("philosophical/bsb_madhva.json", dict(
        id="4", text="Brahmasūtra Bhāṣya of Madhva", tradition="Dvaita", commentator="Madhva", script="Devanagari", units=u,
        source_sanskrit={"citation": "Setutila/Sarvamula sutra_bhashya.json (mula + bhashya, all 564 sutras), as compiled in the project's BSB_Complete_AllAdhyayas.docx", "url": "https://github.com/Setutila/Sarvamula/blob/main/JSON/sutra_bhashya.json", "license": SETU_LIC},
        source_english={"citation": "Subba Rau 1904, Vedanta-Sutras with the commentary of Sri Madhwacharya, re-OCR'd with Sarvam Vision from a higher-resolution scan (project compilation, BSB_Complete_AllAdhyayas.docx; author notes say 'not so accurate', treat as first pass)", "url": "https://archive.org/details/vedantasutrasmadhwacharyassubbarau1904ocr", "license": None},
        bundled=False, needs_ocr=False, alignment="by_ref",
        notes=("Parsed from the project's BSB_Complete_AllAdhyayas.docx. english_mula = Subba Rau's numbered sutra translation, english_bhashya = translation of Madhva's bhashya; sanskrit = sutra + bhashya. ref = adhyaya.pada.sutra. "
               "Units 'mangalacharana' and 'intro-bhashya' are the opening of 1.1.1's Sanskrit bhashya split out as in the docx; sutra 1.1.1's own bhashya starts where Madhva restates the sutra. "
               "'a.b.intro' units are Subba Rau's unnumbered pada introductions (English only). "
               f"Bhashya English missing for {len(miss)} sutras ({', '.join(miss)}); the docx carries bracketed placeholder notes there, which are dropped, so english is null for those units (sanskrit holds the sutra only; sanskrit_bhashya kept separately): source-book pages 90-91 (2.1.8-12), 264-265 (4.1.15-18), 274-275 (4.2.18-22) are missing from the exemplar, and Setutila splits 1.3.42-43 differently from Subba Rau. "
               "Docx author reports 0.999 average fuzzy-match confidence on 548 extracted sutras; English quality otherwise unreviewed.")))
    print(len(u), len(sutras), len(miss), miss)
