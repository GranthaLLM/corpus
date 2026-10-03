import json, re
from common import ROOT, RAW, write
import shivaji_to_unicode as sh
from upanishad_madhva_sonde import norm, tri
from clean_legacy_english import clean

ORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8}
CITE = {"citation": "Nagesh D. Sonde, Sri Madhvacharya Bhashya on Chhandogya Upanishad", "url": "https://nageshsonde.com/images/chhandogya-upanishad.pdf",
        "license": "Author states: not protected by any copyright; free to copy and distribute"}


def pairs(path):
    ch, kind, leg, en, out = None, None, [], [], []

    def flush():
        nonlocal leg, en
        if leg and en:
            out.append((ch, sh.convert(" ".join(leg)), re.sub(r"\s+", " ", " ".join(en))))
        leg, en = [], []

    for l in path.read_text(encoding="utf-8").split("\n"):
        s = l.strip()
        m = re.search(r"(?i)thus begins the (\w+?) ?chapter", s)
        if m:
            flush()
            ch, kind = ORD.get(m.group(1).lower(), ch), None
            continue
        m = re.fullmatch(r"(Upanishad|Bhashya|Bhasya)\s*:?", s)
        if m:
            flush()
            kind = "mula" if m.group(1) == "Upanishad" else "bhashya"
            continue
        if re.search(r"Thus ends|Thus begins|KND", s):
            flush()
            kind = None
            continue
        if kind != "bhashya" or not s or re.fullmatch(r"\d+|\*+", s):
            continue
        if sh.is_english(s):
            en.append(s)
        else:
            if en:
                flush()
            leg.append(s)
    flush()
    return out


def cov(q, t):
    a = tri(q)
    return len(a & tri(t)) / max(1, len(a))


def main():
    path = ROOT / "upanishads" / "chandogya_madhva.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    units = [(u["ref"], norm(u["sanskrit"])) for u in d["units"]]
    got, cur = {}, None
    for ch, dev, en in pairs(RAW / "sonde" / "chand.txt"):
        nd = norm(dev)
        e = clean(en)[0]
        e = " ".join(t for t in e.split(" ") if not re.search(r"[|}]|^[\[\]\"'-]*[;\[\]-]+$", t))
        if len(nd) >= 15 or cur is None:
            pre = (str(ch), "preface") if ch else ("preface", "1")
            sc = [(cov(nd, t), r) for r, t in units if r.split(".")[0] in pre]
            if sc:
                v, r = max(sc)
                if v >= 0.4:
                    cur = r
        if cur is not None:
            got.setdefault(cur, []).append(e)
    n = 0
    for u in d["units"]:
        if u["ref"] in got:
            u["english"] = " ".join(got[u["ref"]])
            n += 1
    d["source_english"] = [CITE]
    d["english_rights"] = ["free_to_copy_per_author"]
    d["reference_type"] = "translation"
    d["notes"] = re.sub(r" \[English: Srisa.*", "", d["notes"], flags=re.S)
    d["notes"] += (f" [English: Nagesh D. Sonde's translation of Madhva's Chandogya bhashya for all {n} units (replaces Vasu 1909 via wisdomlib, whose text ran 3 to 15 times longer than the Sanskrit). "
                   "Sonde's Sanskrit (legacy Shivaji01 font) was decoded with tools/shivaji_to_unicode.py and each Sonde passage matched to a unit by trigram coverage; passages that did not match stay with the previous unit. "
                   "Sonde's translations of the mantras themselves are not used. Words left in the legacy encoding were removed.]")
    write("upanishads/chandogya_madhva.json", d)
    print(n)


if __name__ == "__main__":
    main()
