import re, json, glob, sys
sys.path.insert(0, ".")
from common import *
from wlparse import verses, load, is_dev
from setu import blocks, block_text, DEV

SETU = "https://github.com/Setutila/Sarvamula/blob/main/JSON/"
WL = "https://www.wisdomlib.org/hinduism/book/"
SETU_LIC = "CC0 1.0 (Setutila/Sarvamula)"
HDR = re.compile(r"(commentary|bh[aā]ṣya|bhashya|ṭīkā|tika)\b", re.I)


def split_english(rest):
    trans, bh, mode, pre_lines = [], [], "pre", []
    for l in rest:
        if mode == "pre":
            if re.match(r"^\(?\d+[\.\)]\s", l) or re.match(r"^\[\d+\]", l):
                mode = "t"; trans.append(l)
            pre_lines.append(l)
            continue
        if mode == "t":
            if HDR.search(l) and len(l) < 120 and not re.match(r"^\d+\.", l):
                mode = "b"; continue
            if re.match(r"^(Notes?[:.]|\[Note)", l):
                mode = "b"; bh.append(l); continue
            trans.append(l)
        else:
            bh.append(l)
    if not trans and pre_lines:
        i = next((k for k, l in enumerate(pre_lines) if HDR.search(l) and len(l) < 120), len(pre_lines))
        trans, bh = pre_lines[:i], pre_lines[i + 1:]
    for part in (trans, bh):
        while part and re.match(r"^(Verse|Mantra)\s+[\d.]+\d:?\s*$", part[-1].strip()):
            part.pop()
    return "\n".join(trans) or None, "\n".join(bh) or None


def wl_units(book, skip_title=re.compile(r"Title Page|Preface|Note$|Photograph|Dedication|Quotes", re.I)):
    units, seen = [], {}
    for p in load(book):
        if not p["lines"] or skip_title.search(p["title"]):
            continue
        recs, _ = verses(p["lines"])
        m = re.search(r"(?:[Vv]erse|[Mm]antra)s?\s+([\d.]+\d)\b", p["title"])
        prefix = None
        for idx, v in enumerate(recs):
            if not v["rest"]:
                continue
            num = None
            for l in (v["iast"][-1:] + v["dev"][-1:]):
                mm = re.search(r"\|\|\s*(\d+)\s*\|\|", l) or re.search(r"॥\s*([०-९]+)\s*॥", l)
                if mm:
                    num = mm.group(1).translate(DEV)
            pm = re.search(r"[Vv]erse\s+(\d+(?:\.\d+)+)", v["pre"])
            short = p["title"].split(" - ")[0].strip()
            is_range = bool(re.search(r"\d\s*[-–]\s*\d", short))
            if pm:
                ref = pm.group(1)
                prefix = ref.rsplit(".", 1)[0] if "." in ref else None
            elif m and not is_range and idx == 0:
                ref = m.group(1)
                prefix = ref.rsplit(".", 1)[0] if "." in ref else None
            elif num and prefix:
                ref = f"{prefix}.{num}"
            elif num and re.match(r"(?i)(verse|mantra)", short):
                ref = num
            elif num:
                ref = f"{short}/{num}"
            else:
                ref = short
            k = seen.get(ref, 0) + 1
            seen[ref] = k
            if k > 1:
                ref += f"-{k}"
            trans, bh = split_english(v["rest"])
            iast = "\n".join(v["iast"]) or None
            dev = "\n".join(v["dev"])
            units.append({"ref": ref, "kind": "mula", "sanskrit": iast or dev, "sanskrit_devanagari": dev,
                          "english": trans, "english_bhashya": bh, "_title": p["title"], "_num": num})
    return units


def tidy(units):
    for u in units:
        for k in [k for k in u if k.startswith("_")]:
            del u[k]
    return units


MARK = re.compile(r"॥\s*([०-९]+(?:/[०-९]+)*)\s*॥?")


def setu_units(fname, mula_key=True):
    t, c = blocks(RAW / ("set_" + fname + ".json"))
    groups = []
    cur = None

    def new():
        g = {"ref": None, "mula": [], "bh": [], "closed": False, "colophon": False}
        groups.append(g)
        return g

    for b in c:
        ct = b["content_type"]
        txt = block_text(b)
        if ct.startswith("Heading"):
            continue
        if ct in ("Mula", "Colophon_Mula"):
            if ct == "Colophon_Mula":
                g = new()
                g["mula"].append(txt)
                g["colophon"] = g["closed"] = True
                cur = g
                continue
            pos = 0
            for m in MARK.finditer(txt):
                seg = txt[pos:m.end()].strip()
                pos = m.end()
                if cur is None or cur["closed"]:
                    cur = new()
                cur["mula"].append(seg)
                cur["ref"] = m.group(1).translate(DEV)
                cur["closed"] = True
            tail = txt[pos:].strip()
            if tail:
                if cur is None or cur["closed"]:
                    cur = new()
                cur["mula"].append(tail)
                if "शान्तिः" in tail and cur["ref"] is None:
                    cur["closed"] = True
        else:
            if cur is None:
                cur = new()
                cur["closed"] = True
            cur["bh"].append(txt)
    units, seen, k = [], {}, 0
    for g in groups:
        k += 1
        ref = g["ref"]
        if g["colophon"]:
            ref = f"colophon{k}"
        elif ref is None:
            ref = "intro" if any("शान्तिः" in x for x in g["mula"]) or not g["mula"] else f"unnumbered{k}"
        elif ref.startswith("0") and "/" not in ref:
            ref = "intro"
        mula = "\n".join(g["mula"]) or None
        bh = "\n".join(g["bh"]) or None
        n = seen.get(ref, 0) + 1
        seen[ref] = n
        if n > 1:
            ref += f"-{n}"
        units.append({"ref": ref, "kind": "mula+bhashya" if mula else "bhashya", "sanskrit_mula": mula,
                      "sanskrit_bhashya": bh, "sanskrit": "\n".join(x for x in (mula, bh) if x) or None, "english": None})
    return units


def setu_sections(fname, leaf_level):
    t, c = blocks(RAW / ("set_" + fname + ".json"))
    units, cur, path = [], None, {}
    for b in c:
        ct = b["content_type"]
        txt = block_text(b)
        if ct.startswith("Heading"):
            lvl = int(ct[7:])
            path = {k: v for k, v in path.items() if k < lvl}
            path[lvl] = txt
            if lvl >= leaf_level:
                cur = {"ref": " / ".join(path[k] for k in sorted(path)), "kind": "bhashya", "sanskrit_mula": None, "_bh": []}
                units.append(cur)
            continue
        if cur is None:
            cur = {"ref": "preface", "kind": "bhashya", "sanskrit_mula": None, "_bh": []}
            units.append(cur)
        cur["_bh"].append(txt)
    for u in units:
        u["sanskrit_bhashya"] = "\n".join(u.pop("_bh")) or None
        u["sanskrit"] = u["sanskrit_bhashya"]
        u["english"] = None
    return units


def wl_index(units):
    return {u["ref"]: u for u in units}


def en_units(book):
    units = []
    for p in load(book):
        if not p["lines"]:
            continue
        L = p["lines"]
        starts = [i for i, l in enumerate(L) if re.match(r"^Mantra\s+[\d.]+\d\.?\s*$", l)]
        tm = re.search(r"Mantra\s+([\d.]+\d)", p["title"])
        if starts:
            bounds = starts + [len(L)]
            for a, b in zip(bounds, bounds[1:]):
                ref = re.search(r"([\d.]+\d)", L[a]).group(1)
                t, bh = split_english(L[a + 1:b])
                units.append({"ref": ref, "english_mula": t, "english_bhashya": bh})
        elif tm:
            t, bh = split_english(L)
            units.append({"ref": tm.group(1), "english_mula": t, "english_bhashya": bh})
    return units


def madhva_english(book):
    wu = wl_units(book)
    if wu and any(re.match(r"^[\d.]+$", u["ref"]) for u in wu):
        return [{"ref": u["ref"], "english_mula": u["english"], "english_bhashya": u["english_bhashya"]} for u in wu]
    return en_units(book)


def key(ref):
    return ref.replace(".", "/")


def katha_map(ref):
    a, b = ref.split(".")[:2]
    v = int(a)
    return f"{(v - 1) // 3 + 1}/{(v - 1) % 3 + 1}/{ref.split('.')[2] if ref.count('.') > 1 else b}" if ref.count(".") == 1 and False else None


def madhva_file(rel, id_, text, setu_name, wl_book, wl_slug, wl_cite, mapper=None, leaf_level=None, english=True):
    units = setu_sections(setu_name, leaf_level) if leaf_level else setu_units(setu_name)
    matched = 0
    skipped = []
    if wl_book and english:
        idx = {}
        for e in madhva_english(wl_book):
            r = key(e["ref"])
            if mapper:
                r = mapper(r)
            if r:
                idx.setdefault(r, []).append(e)
        for u in units:
            es = idx.get(key(u["ref"]))
            if es:
                ln = re.match(r"^\(?\[?(\d+)[\.\)\]]", es[0]["english_mula"] or "")
                last = u["ref"].split("/")[-1]
                if ln and last.isdigit() and ln.group(1) != last:
                    skipped.append((u["ref"], ln.group(1)))
                    es = None
            if es and not leaf_level:
                e = es[0]
                u["english_mula"], u["english_bhashya"] = e["english_mula"], e["english_bhashya"]
                u["english"] = "\n".join(x for x in (e["english_mula"], e["english_bhashya"]) if x) or None
                if u["english"]:
                    matched += 1
    n_mapped = sum(1 for u in units if u["english"])
    src_en = {"citation": wl_cite, "url": WL + wl_slug, "license": None} if wl_book and english else None
    if skipped:
        for u in units:
            u["_skipped"] = None
        units[0]["_skipped"] = skipped
    return units, n_mapped, src_en


if __name__ == "__main__":
    TR = "Upaniṣad Madhvabhāṣya"
    specs = [
        ("isa", "Īśāvāsya Upaniṣad", "ishavasya_bhashya", "isopanisad-madhva-commentary", "isopanisad-madhva-commentary", None, None),
        ("kena", "Kena (Talavakāra) Upaniṣad", "talavakara_bhashya", "kena-upanishad-madhva-commentary", "kena-upanishad-madhva-commentary", None, None),
        ("katha", "Kaṭha Upaniṣad", "kathaka_bhashya", "kathopanishad-madhva-commentary", "kathopanishad-madhva-commentary",
         lambda r: (lambda p: f"{(int(p[0]) - 1) // 3 + 1}/{(int(p[0]) - 1) % 3 + 1}/{p[1]}")(r.split("/")) if r.count("/") == 1 else None, None),
        ("prashna", "Praśna Upaniṣad", "shatprashna_bhashya", "prashna-upanishad-madhva-commentary", "prashna-upanishad-madhva-commentary", None, None),
        ("mundaka", "Muṇḍaka Upaniṣad", "atharvana_bhashya", "mundaka-upanishad-madhva-commentary", "mundaka-upanishad-madhva-commentary", None, None),
        ("mandukya", "Māṇḍūkya Upaniṣad", "manduka_bhashya", "mandukya-upanishad-madhva-commentary", "mandukya-upanishad-madhva-commentary", None, None),
        ("taittiriya", "Taittirīya Upaniṣad", "taittiriya_bhashya", None, None, None, None),
        ("aitareya", "Aitareya Upaniṣad", "aitareya_bhashya", None, None, None, 3),
        ("chandogya", "Chāndogya Upaniṣad", "chandogya_bhashya", None, None, None, 2),
        ("brihadaranyaka", "Bṛhadāraṇyaka Upaniṣad (Kāṇva)", "kanva_bhashya", None, None, None, 2),
    ]
    SCANS = {
        "taittiriya": ("Nagesh Sonde, Sri Madhvacharya Bhashya on Taittiriya Upanishad", "https://nageshsonde.com/images/Sri-Madhvachachaarya-Bhashya-On-Taittiriya-Upanishad.pdf", "bundled with its own Sanskrit in the PDF"),
        "aitareya": ("Pandurangi 1989, Aitareya Upanishat translation", "https://archive.org/details/yOyz_aitareya-upanishat-translation-by-k-t-pandurangai-shriman-madhva-siddhantonnahini-sabh-chirtanu/page/n5/mode/2up", None),
        "brihadaranyaka": ("Vasu and Sinha 1933, Brihadaranyaka Upanishad", "https://archive.org/details/brihadaranyakaup0000unse", "lending library only"),
    }
    for id_, text, sname, wlb, wls, mapper, leaf in specs:
        english_avail = wlb is not None
        if id_ == "chandogya":
            wlb, wls = "chandogya-upanishad-madhva-commentary", "chandogya-upanishad-madhva-commentary"
        units, nmap, src_en = madhva_file(None, id_, text, sname, wlb, wls, "wisdomlib, Madhva commentary translation (Sri Madhvacharya's Bhashya, Rao/Srinivasachar edition as hosted)", mapper, leaf)
        notes = f"Sanskrit from Setutila/Sarvamula JSON/{sname}.json (CC0, Tattvavada corpus; Madhva bhashya). ref = verse number path as printed in Setutila (Devanagari digits converted). sanskrit = mula + bhashya, sanskrit_mula/sanskrit_bhashya separate. "
        needs_ocr = False
        alignment = "by_ref"
        if id_ == "chandogya":
            e = en_units(wls)
            notes += ("Setutila file is bhashya-only with no mula blocks; units = khanda sections by Setutila heading. wisdomlib English is per mantra (see english_by_mantra below is NOT included); english left null at khanda level in pass 1, alignment unaligned. "
                      f"wisdomlib has {len(e)} mantra-level English records available for a later khanda-level join. ")
            src_en = {"citation": "wisdomlib, Chandogya Upanishad Madhva commentary", "url": WL + wls, "license": None}
            alignment = "unaligned"
        elif id_ in SCANS:
            c, u_, extra = SCANS[id_]
            src_en = {"citation": c, "url": u_, "license": None}
            notes += f"English pending OCR pass 2 ({c}{'; ' + extra if extra else ''}); english null. "
            if id_ in ("aitareya", "brihadaranyaka"):
                notes += "Setutila file is bhashya-only (no mula blocks); units = sections by Setutila headings. "
            alignment = "unaligned"
            needs_ocr = True
        else:
            sk = units[0].pop("_skipped", None) if units else None
            for x in units:
                x.pop("_skipped", None)
            notes += (f"Joins rejected because the wisdomlib translation number differs from the ref: {sk}. " if sk else "")
            notes += f"English from wisdomlib matched by ref: {nmap} of {len(units)} units have english (english = mula translation + commentary translation; english_mula/english_bhashya separate). Unmatched units have english null. "
        write(f"upanishads/{id_}_madhva.json", dict(
            id=f"{id_}_madhva", text=f"{text} Madhvabhāṣya", tradition="Dvaita", commentator="Madhva", script="Devanagari",
            units=units, source_sanskrit={"citation": f"Setutila/Sarvamula {sname}.json", "url": SETU + sname + ".json", "license": SETU_LIC},
            source_english=src_en, bundled=False, needs_ocr=needs_ocr, alignment=alignment, notes=notes.strip()))
        print(id_, "madhva", len(units), "with_english", nmap)
