import re
from common import *


def ramanuja():
    body = gretil_body("sa_rAmAnuja-bhagavadgItAbhASya.txt")
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    units, cur = [], None
    pg = re.compile(r"\s*\(?BhGR_p\d+\)?")
    for p in paras:
        m = re.search(r"BhG_(\d+\.\d+[a-z]*)\s*$", p)
        if m:
            cur = {"ref": m.group(1), "kind": "mula+bhashya",
                   "sanskrit_mula": re.sub(r"\s*BhG_\S+\s*$", "", p).strip(), "_b": []}
            units.append(cur)
            continue
        p = pg.sub("", p).strip()
        if not p:
            continue
        if cur is None:
            units.append({"ref": "intro", "kind": "bhashya", "sanskrit_mula": None, "_b": [p]})
            cur = units[-1]
            cur = None
            continue
        cur["_b"].append(p)
    out = []
    for u in units:
        b = u.pop("_b")
        bh = "\n".join(b) if b else None
        u["sanskrit_bhashya"] = bh
        parts = [x for x in (u["sanskrit_mula"], bh) if x]
        u["sanskrit"] = "\n".join(parts) if parts else None
        u["english"] = None
        out.append(u)
    return out


def aitareya():
    body = gretil_body("sa_aitareyopaniSad-comm.txt")
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    return [{"ref": f"para {i}", "kind": "mula+bhashya", "sanskrit": p, "english": None}
            for i, p in enumerate(paras, 1)]


def shataka():
    body = gretil_body("sa_bhatRhari-zatakatraya.txt")
    out = []
    buf = []
    for l in body.split("\n"):
        s = l.strip()
        if not s:
            continue
        m = re.search(r"\|\|\s*bharst_(\d+)\.(\d+|-)(\*\d+)?\s*\|\|", s)
        if m:
            buf.append(re.sub(r"\s*\|\|\s*bharst_\S+\s*\|\|", " ||", s).strip())
            out.append({"ref": f"{m.group(1)}.{m.group(2)}{m.group(3) or ''}", "kind": "verse",
                        "sanskrit": "\n".join(buf), "english": None})
            buf = []
        elif re.search(r"(śatakam|śataka-m)", s) or s.startswith("bhatṛhari:") or s.startswith("bhartṛhareḥ"):
            buf = []
        else:
            buf.append(s)
    return out


if __name__ == "__main__":
    src = {"citation": "Rāmānuja, Bhagavadgītābhāṣya, GRETIL (input S. Ishitobi, analytic text)", "url": GRETIL + "sa_rAmAnuja-bhagavadgItAbhASya.txt", "license": GRETIL_LIC}
    n = write("philosophical/bg_ramanuja.json", dict(
        id="bg_ramanuja", text="Bhagavadgītā Rāmānujabhāṣya", tradition="Vishishtadvaita", commentator="Rāmānuja",
        units=ramanuja(), source_sanskrit=src,
        source_english={"citation": "Adidevananda, Sri Ramanuja Gita Bhasya (Devanagari and English)", "url": "https://archive.org/details/gita-ramanuja-gita-bhasya-devanagari-and-english-rendering-by-swami-adidevananda", "license": None},
        alignment="unaligned", notes="Sanskrit only in pass 1. English (Adidevananda scan) pending OCR pass. ref = chapter.verse; ab/cd suffix kept where source splits a verse. BhGR_p page markers removed from bhashya text. Analytic text (sandhi split per BHELA conventions)."))
    print("bg_ramanuja", n)

    src = {"citation": "Bhartṛhari, Śatakatraya, GRETIL (J. Brzezinski; 'needs critical reading', edition numberings vary)", "url": GRETIL + "sa_bhatRhari-zatakatraya.txt", "license": GRETIL_LIC}
    n = write("sahitya/shatakatraya.json", dict(
        id="25", text="Śatakatraya", tradition=None, units=shataka(), source_sanskrit=src,
        source_english={"citation": "Wortham, The Satakas of Bhartrihari (1886)", "url": "https://archive.org/details/satakasofbhartri00bharuoft", "license": None},
        alignment="unaligned", notes="Sanskrit only in pass 1; Wortham English pending OCR. ref = shataka.verse (1 Nitishataka, 2 Shringarashataka, 3 Vairagyashataka). Verse numbering is GRETIL's and may differ from Wortham's."))
    print("shatakatraya", n)
