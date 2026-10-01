import re
from common import *
from build_upanishads import setu_units, setu_sections, SETU, SETU_LIC, WL
from wlparse import load
from sribhashya_sanskrit import attach_sanskrit

BOOK = "brahma-sutras-ramanuja"


def sri_bhashya_english():
    groups, cur = [], None
    for p in load(BOOK):
        t = p["title"]
        m = re.match(r"^Sutra\s+(\d+\.\d+\.\d+(?:\s*[-–]\s*\d+)?)", t)
        if m:
            cur = {"ref": m.group(1).replace(" ", ""), "pages": []}
            groups.append(cur)
        elif re.match(r"^(First|Second|Third|Fourth)\s+Ad", t) or not p["lines"]:
            cur = None if re.match(r"^(First|Second|Third|Fourth)\s+Ad", t) else cur
            continue
        if cur is None or not p["lines"]:
            continue
        body = [l for l in p["lines"] if not re.match(r"^p\.\s*\d+$", l)]
        cur["pages"].append((t, "\n".join(body)))
    units = []
    for g in groups:
        txt = "\n\n".join((f"[{t}]\n" if not t.startswith("Sutra") else "") + b for t, b in g["pages"]).strip()
        units.append({"ref": g["ref"], "kind": "mula+bhashya", "sanskrit": None, "english": txt or None})
    return units


def write_sri_bhashya(u):
    ss = attach_sanskrit(u)
    write("philosophical/sribhashya_ramanuja.json", dict(
        id="3", text="Śrī Bhāṣya of Rāmānuja", tradition="Vishishtadvaita", commentator="Rāmānuja", script="Devanagari", units=u,
        source_sanskrit={"citation": "Annangaracharya 1971 ed., Sri Bhashyam Sanskrit text (scan), OCR by Bodhan indic-ocr", "url": "https://archive.org/details/ShriBhasyamOfRamanujaSanskritText", "license": None},
        source_english={"citation": "Thibaut 1904, The Vedanta-Sutras with Ramanuja's Sri-Bhashya, as hosted on wisdomlib", "url": WL + BOOK, "license": None},
        bundled=False, needs_ocr=True, alignment="by_ref",
        notes=f"English: Thibaut via wisdomlib, grouped per sutra (all wisdomlib sub-pages under each 'Sutra a.b.c' page are concatenated in page order, sub-page titles in brackets, page-number markers removed); wisdomlib footnotes are left in. Sanskrit: Bodhan indic-ocr on the Annangaracharya scan (archive.org ShriBhasyamOfRamanujaSanskritText, 188 spreads split into 376 half pages; cache in raw/sribhashya_bodhan), then split on the printed sutra markers and aligned to the English units by order within each pada (sutra statement + bhashya per unit). The edition's refs differ from Thibaut's from 2.2.33 on (English 2.2.33 is Sanskrit 2.2.32), and wisdomlib folds 1.3.32, 2.1.6, 2.1.18, 2.2.24, 3.3.58, 3.4.44 into the preceding sutra, so those units carry two consecutive sutras of Sanskrit ({ss['merge']} merges). The English numbers the sutras as printed in the Sanskrit marker in all but the OCR digit slips (9 read as 6). Sanskrit is OCR text: '*' marks the quotation glyph, a few conjuncts and sandhi are wrong, and it is not proofread. Alt English: Rangacharya and Varadaraja Aiyangar 1899."))
    print("sribhashya", len(u))


if __name__ == "__main__":
    u = setu_units("gita_bhashya")
    tp = {x["ref"]: x for x in setu_units("gita_tatparya")}
    n_tp = 0
    for x in u:
        t = tp.get(x["ref"])
        x["sanskrit_tatparya"] = t["sanskrit_bhashya"] if t else None
        if x["sanskrit_tatparya"]:
            n_tp += 1
            x["sanskrit"] = "\n".join(y for y in (x["sanskrit_mula"], x["sanskrit_bhashya"], x["sanskrit_tatparya"]) if y)
    write("philosophical/bg_madhva.json", dict(
        id="1c", text="Bhagavadgītā Madhvabhāṣya", tradition="Dvaita", commentator="Madhva", script="Devanagari", units=u,
        source_sanskrit={"citation": "Setutila/Sarvamula gita_bhashya.json (Sanskrit; used instead of the OCR of the Sharma scan)", "url": SETU + "gita_bhashya.json", "license": SETU_LIC},
        source_english={"citation": "B.N.K. Sharma 1989, Bhagavadgita Bhashya of Sri Madhvacharya", "url": "https://archive.org/details/bhagavadgita-bhashya-of-sri-madhvacharya-bnk-sharma", "license": None},
        bundled=False, needs_ocr=True, alignment="unaligned",
        notes=f"Sanskrit from Setutila (clean, proofread): mula + Gita Bhashya (gita_bhashya.json) + Gita Tatparya Nirnaya (gita_tatparya.json, joined by verse ref; {n_tp} units have a Tatparya block). sanskrit = mula + bhashya + tatparya. English: see Sonde note.  ref = chapter/verse as printed in Setutila. Some verses may be grouped where Setutila blocks carry several numbers."))
    print("bg_madhva", len(u))

    u = setu_sections("mbtn", 1)
    write("philosophical/mbtn.json", dict(
        id="10", text="Mahābhārata Tātparya Nirṇaya", tradition="Dvaita", commentator="Madhva", script="Devanagari", units=u,
        source_sanskrit={"citation": "Setutila/Sarvamula mbtn.json (Sanskrit, 32 adhyayas)", "url": SETU + "mbtn.json", "license": SETU_LIC},
        source_english={"citation": "Anuradha Sridhar 2015, Mahabharata Tatparya Nirnaya (Tattvasamshodhana Samsat, Udupi)", "url": "https://archive.org/details/shrimad-mahabharata-tatparya-nirnaya-smt-anuradha-sridhar-eng-tatwasamshodhana-samsat-udupi-2015", "license": None},
        bundled=False, needs_ocr=True, alignment="unaligned",
        notes="Sanskrit from Setutila; file has no verse-level numbering, so units are heading sections (ref = heading path in Devanagari). English pending OCR pass 2 (Sridhar scan)."))
    print("mbtn", len(u))

    body = (RAW / "btn.txt").read_text(encoding="utf-8")
    units, cur, skandha = [], None, None
    for line in body.split("\n"):
        m = re.match(r"^=== (.+?) ===$", line.strip())
        if m:
            h = m.group(1)
            if "स्कन्ध" in h:
                skandha = h
            elif "ध्याय" in h:
                cur = {"ref": f"{skandha} / {h}" if skandha else h, "kind": "verse", "sanskrit": [], "english": None}
                units.append(cur)
            continue
        if cur is not None and line.strip():
            cur["sanskrit"].append(line.strip())
    for x in units:
        x["sanskrit"] = "\n".join(x["sanskrit"]) or None
    write("philosophical/btn.json", dict(
        id="11", text="Bhāgavata Tātparya Nirṇaya", tradition="Dvaita", commentator="Madhva", script="Devanagari", units=units,
        source_sanskrit={"citation": "Setutila/Sarvamula texts/btn.txt (plain text)", "url": "https://github.com/Setutila/Sarvamula/blob/main/texts/btn.txt", "license": SETU_LIC},
        source_english=None, bundled=False, needs_ocr=False, alignment="not_applicable",
        notes="translation not located. Sanskrit from Setutila plain text (clean) instead of the Govindacharya scan; units = skandha / adhyaya. The Govindacharya scan in the corpus doc is not needed for Sanskrit."))
    print("btn", len(units))

    write_sri_bhashya(sri_bhashya_english())
