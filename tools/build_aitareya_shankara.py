import re, json
from common import *
from advaita_sharada import units as as_units
from scanparse import paragraphs, english_filter

AS = "https://advaitasharada.sringeri.net/read/"
AS_LIC = "Sringeri Sharada Peetham, Advaita Sharada (Vani Vilas Press Sri Shankara Granthavali edition); licence not stated on site"
HEADER = re.compile(r"(THE AIT\w+ UP\w+|WITH SRI SANKARA.S COMMENTARY|^\s*\d+\s*$)", re.I)


def sastri_parts():
    P = english_filter(paragraphs("sastri_aitareya_only.txt"))
    raw = paragraphs("sastri_aitareya_only.txt")
    idx = {}
    for i, p in enumerate(raw):
        if re.match(r"^KHANDA\s+I\.?\s*$", p): idx["k1"] = i
        elif re.match(r"^KHANDA\s+II\.?\s*$", p): idx["k2"] = i
        elif re.match(r"^KHANDA\s+(III|111|Ill|HI)\.?\s*$", p): idx["k3"] = i
        elif re.search(r"Here ends the third Part", p): idx["e3"] = i
        elif re.search(r"Here ends the commentary on the fourth Part", p): idx["e4"] = i
        elif re.search(r"Here ends the commentary upon the fifth Part", p): idx["e5"] = i
    bounds = [(0, idx["k1"]), (idx["k1"], idx["k2"]), (idx["k2"], idx["k3"]), (idx["k3"], idx["e3"] + 1), (idx["e3"] + 1, idx["e4"] + 1), (idx["e4"] + 1, idx["e5"] + 1)]
    out = []
    for a, b in bounds:
        paras_ = [p for (p, eng), q in zip(P, range(len(P))) if False]
        seg = []
        # english_filter keeps paragraph order but may drop some; realign by text membership
        rawset = raw[a:b]
        keep = {p for p, e in P if e}
        for p in rawset:
            if p in keep and not re.match(r"^(KHANDA|Here ends)", p) and not HEADER.search(p) and len(p) > 25:
                seg.append(p)
        out.append(re.sub(r"\s+", " ", "\n".join(seg)).strip() if False else "\n".join(seg))
    return out


def main():
    u = as_units("aitareya-bhashya", False)
    groups = {}
    order = []
    for x in u:
        m = re.match(r"^(?:intro-|colophon-)?(\d+)(?:\.(\d+))?", x["ref"])
        key = (int(m.group(1)), int(m.group(2) or 0))
        groups.setdefault(key, []).append(x)
        if key not in order:
            order.append(key)
    parts = sastri_parts()
    keys = [(1, 1), (1, 2), (1, 3), (2, 1), (3, 1)]
    units = []
    intro = [x for x in groups.get((1, 1), []) if x["ref"].startswith("intro-")]
    groups[(1, 1)] = [x for x in groups.get((1, 1), []) if not x["ref"].startswith("intro-")]
    units.append({"ref": "intro", "kind": "bhashya", "sanskrit": "\n".join(x["sanskrit_bhashya"] for x in intro if x.get("sanskrit_bhashya")),
                  "sanskrit_mula": None, "sanskrit_bhashya": "\n".join(x["sanskrit_bhashya"] for x in intro if x.get("sanskrit_bhashya")), "english": parts[0] or None})
    for k in keys:
        mem = [x for x in groups.get(k, [])]
        if k == (2, 1):
            mem += groups.get((2, 0), [])
        mula = "\n".join(x["sanskrit_mula"] for x in mem if x.get("sanskrit_mula")) or None
        bh = "\n".join(x["sanskrit_bhashya"] for x in mem if x.get("sanskrit_bhashya")) or None
        units.append({"ref": f"{k[0]}.{k[1]}", "kind": "mula+bhashya", "sanskrit": "\n".join(y for y in (mula, bh) if y),
                      "sanskrit_mula": mula, "sanskrit_bhashya": bh})
    for un, en in zip(units[1:], parts[1:]):
        un["english"] = en or None
    write("upanishads/aitareya_shankara.json", dict(
        id="aitareya_shankara", text="Aitareya Upaniṣad Śāṅkarabhāṣya", tradition="Advaita", commentator="Śaṅkara", script="Devanagari", units=units,
        source_sanskrit={"citation": "Advaita Sharada", "url": AS + "aitareya-bhashya/1", "license": AS_LIC},
        source_english={"citation": "S. Sitarama Sastri, The Aitareya and Taittiriya Upanishads and Sri Sankara's Commentary (Upanishads and Sri Sankara's Commentary Vol. 5), archive.org OCR text layer", "url": "https://archive.org/details/UpanishadsAndSriSankarasCommentaryVol.5", "license": None},
        bundled=False, needs_ocr=True, alignment="by_ref",
        notes=("Sanskrit from Advaita Sharada (mantras + Shankara's bhashya), grouped by khanda: 1.1, 1.2, 1.3 = the three khandas of the first adhyaya; 2.1 and 3.1 = adhyayas 2 and 3 (Sastri's 'fourth' and 'fifth' Parts). "
               "English from Sastri's translation as printed (mantra translations and commentary translation, not separable), cut at his own 'KHANDA I/II/III' and 'Here ends the ... Part' markers, so each unit's English matches its Sanskrit exactly at khanda level. "
               "Verse-level pairing was not possible: Sastri groups mantras differently from Advaita Sharada (22 'Com.' blocks against 33 verses) and his OCR lost most verse numbers. "
               "The 'intro' unit pairs Shankara's opening bhashya (sambandha-bhashya, Sanskrit) with Sastri's introductory text before Khanda I. "
               "Paragraphs with Sanskrit-script OCR garbage are dropped; OCR noise remains. Verse-level Advaita Sharada units are available in git history. First pass.")))
    print([(u['ref'], len(u['sanskrit']), len(u['english'] or '')) for u in units], 0)


if __name__ == "__main__":
    main()
