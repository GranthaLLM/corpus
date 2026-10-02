import json, re
from common import *
from scanparse import paragraphs, english_filter, seq_parse

GITA_COUNTS = [47, 72, 43, 42, 29, 47, 30, 28, 34, 42, 55, 20, 34, 27, 20, 24, 28, 78]


def clean_en(s):
    if not s:
        return None
    s = re.sub(r"(\[?Ch\.?\s*\d+\]?\s*)?(\d+\s+)?S[A-Za-z]{2,3}\s+RAMANUJA GITA BHASYA(\s*\[?Ch\.?\s*\d*\]?)?(\s+\d+)?", " ", s)
    s = re.sub(r"\[?\d+\s*[~\-–]+\s*\d+\]\s+[A-Z][A-Z .]+\s+\d+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s or None


def update(rel, parsed, label, refmap=None, note=""):
    p = ROOT / rel
    d = json.loads(p.read_text(encoding="utf-8"))
    got = 0
    for u in d["units"]:
        if u["kind"] not in ("mula+bhashya", "mula", "verse"):
            continue
        for f in ("english_mula", "english_bhashya", "english"):
            u.pop(f, None)
        u["english"] = None
        key = refmap(u["ref"]) if refmap else u["ref"]
        if key is None or key not in parsed:
            continue
        m, b = parsed[key]
        m, b = clean_en(m), clean_en(b)
        u["english_mula"], u["english_bhashya"] = m, b
        u["english"] = "\n".join(x for x in (m, b) if x) or None
        got += 1
    total = sum(1 for u in d["units"] if u["kind"] in ("mula+bhashya", "mula", "verse"))
    d["needs_ocr"] = True
    d["alignment"] = "by_ref"
    d["notes"] = (d["notes"] or "").split(" [scan English:")[0] + f" [scan English: {label}: {got} of {total} verse units filled from archive.org djvu OCR by verse-number sequence; missing ones are null because the OCR lost or garbled the verse number. OCR noise remains in the English (stray characters, footnote markers, occasional merged paragraphs); first pass only. {note}]"
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(rel, got, total)


def ramanuja_ref(ref):
    m = re.match(r"^(\d+\.\d+)ab$", ref)
    if m:
        return m.group(1)
    m = re.match(r"^(\d+\.\d+)$", ref)
    return m.group(1) if m else None


def bsb_counts():
    d = json.loads((ROOT / "philosophical/bsb_shankara.json").read_text(encoding="utf-8"))
    c = {}
    for u in d["units"]:
        m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", u["ref"])
        if m:
            k = (int(m.group(1)) - 1) * 4 + int(m.group(2))
            c[k] = max(c.get(k, 0), int(m.group(3)))
    return [c[i] for i in range(1, 17)]


def bsb_ref(ref):
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", ref)
    return f"{(int(m.group(1)) - 1) * 4 + int(m.group(2))}.{m.group(3)}" if m else None


if __name__ == "__main__":
    A = english_filter(paragraphs("Bhagavad-Gita.with.the.Commentary.of.Sri.Shankaracharya.txt"))
    update("philosophical/bg_shankara.json", seq_parse(A, GITA_COUNTS), "Sastri 1897 (archive.org djvu)")
    A = english_filter(paragraphs("gambhirananda_bsb_0.txt"))
    A = A[next(i for i, (p, e) in enumerate(A) if re.match(r"^Topic\s*[I1l]\s*:\s*DELIBERATION", p, re.I)):]
    parsed = seq_parse(A, bsb_counts(), window=5, cwin=6, tail=12)
    parsed = {k: v for k, v in parsed.items() if len(v[0].strip()) >= 70 or re.search(r"[.;:)]\s*$", v[0].strip())}
    update("philosophical/bsb_shankara.json", parsed, "Gambhirananda (archive.org djvu)", bsb_ref,
           "english_mula = the sutra translation, english_bhashya = Gambhirananda's translation of Śaṃkara's commentary up to the next sutra; his topic headings and footnote numbers may appear inside the text.")
    A = english_filter(paragraphs("adidevananda_2.txt"))
    update("philosophical/bg_ramanuja.json", seq_parse(A, GITA_COUNTS), "Adidevananda (archive.org djvu)", ramanuja_ref,
           "Where the GRETIL text splits a verse into ab/cd units, the English is attached to the ab unit only.")
