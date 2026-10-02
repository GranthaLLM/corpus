import re
from common import *
from advaita_sharada import units as as_units
from build_upanishads import wl_units, WL, tidy

AS = "https://advaitasharada.sringeri.net/read/"
AS_LIC = "Sringeri Sharada Peetham, Advaita Sharada (Vani Vilas Press Sri Shankara Granthavali edition); licence not stated on site"
DROP = set("।॥ऽ॒॑᳚॓॔ ‌‍\n\t.,;:-'\"’‘“”()[]") | set("0123456789०१२३४५६७८९")


def norm(s):
    s = re.sub(r"[A-Za-z]", "", s or "")
    s = "".join(c for c in s if c not in DROP)
    return s.replace("ँ", "ं").replace("ꣳ", "ं").replace("ः", "")


def attach_english(units, wl):
    byref, bytext = {}, {}
    for w in wl:
        byref.setdefault(w["ref"], w)
        k = norm(w["sanskrit_devanagari"])
        if len(k) >= 12:
            bytext.setdefault(k[:30], w)
    used, hit_text, hit_ref = set(), 0, 0

    def put(u, ws):
        en_m = "\n".join(x["english"] for x in ws if x["english"]) or None
        en_b = "\n".join(x["english_bhashya"] for x in ws if x["english_bhashya"]) or None
        en = "\n".join(x for x in (en_m, en_b) if x)
        if not en:
            return False
        u["english_mula"], u["english_bhashya"], u["english"] = en_m, en_b, en
        for w in ws:
            used.add(id(w))
        return True

    def lead_num(w):
        m = re.match(r"^\(?\[?(\d+)[\.\)\]]", w["english"] or "")
        return m.group(1) if m else None

    def num_ok(u, w):
        ln = lead_num(w)
        return ln is None or ln == u["ref"].rpartition(".")[2]

    verse_units = [u for u in units if u["kind"] == "mula+bhashya"]
    for u in verse_units:
        k = norm(u["sanskrit_mula"])[:30]
        w = bytext.get(k)
        if w is not None and id(w) not in used and put(u, [w]):
            hit_text += 1
    for u in verse_units:
        if u["english"]:
            continue
        w = byref.get(u["ref"])
        if w is not None and id(w) not in used and num_ok(u, w) and put(u, [w]):
            hit_ref += 1
    for u in verse_units:
        if u["english"]:
            continue
        pre, _, last = u["ref"].rpartition(".")
        cand = [w for w in wl if id(w) not in used and w["ref"].rpartition(".")[0] == pre and lead_num(w) == last]
        if len(cand) == 1 and put(u, cand):
            hit_ref += 1
    for u in verse_units:
        if u["english"]:
            continue
        k = norm(u["sanskrit_mula"])[:14]
        cand = [w for w in wl if id(w) not in used and len(norm(w["sanskrit_devanagari"])) >= 12 and norm(w["sanskrit_devanagari"])[:14] == k]
        if cand and put(u, cand[:1]):
            hit_text += 1
    for u in verse_units:
        if u["english"]:
            continue
        full = norm(u["sanskrit_mula"])
        cand = [w for w in wl if id(w) not in used and len(norm(w["sanskrit_devanagari"])) >= 16 and norm(w["sanskrit_devanagari"]) in full]
        if cand and put(u, cand):
            hit_text += 1
    return hit_text, hit_ref


if __name__ == "__main__":
    specs = [
        ("isa", "Īśāvāsya Upaniṣad", "isha-bhashya", True, "ishavasya-upanishad-shankara-bhashya", "Hiriyanna 1911"),
        ("kena", "Kena Upaniṣad (Padabhāṣya)", "kena-pada-bhashya", False, "kena-upanishad-shankara-bhashya", "Sitarama Sastri 1905"),
        ("katha", "Kaṭha Upaniṣad", "kathaka-bhashya", False, "katha-upanishad-shankara-bhashya", "Sitarama Sastri 1928"),
        ("prashna", "Praśna Upaniṣad", "prashna-bhashya", False, "prashna-upanishad-shankara-bhashya", "Sitarama Sastri 1928"),
        ("mundaka", "Muṇḍaka Upaniṣad", "mundaka-bhashya", False, "mundaka-upanishad-shankara-bhashya", "Sitarama Sastri 1905"),
        ("mandukya", "Māṇḍūkya Upaniṣad with Gauḍapāda's Kārikā", "mandukya-karika-bhashya", False, "mandukya-upanishad-karika-bhashya", "Nikhilananda 1949"),
        ("brihadaranyaka", "Bṛhadāraṇyaka Upaniṣad", "brihadaranyaka-bhashya", False, "the-brihadaranyaka-upanishad", "Madhavananda 1950"),
        ("taittiriya", "Taittirīya Upaniṣad", "taittiriya-bhashya", False, "the-taittiriya-upanishad", "A. Mahadeva Sastri 1903"),
    ]
    for id_, text, book, dc, wlbook, cite in specs:
        u = as_units(book, dc)
        wl = tidy(wl_units(wlbook))
        t, r = attach_english(u, wl) if id_ != "taittiriya" else (0, 0)
        n_v = sum(1 for x in u if x["kind"] == "mula+bhashya")
        notes = (f"Sanskrit (verse + Śaṃkara's bhashya, Devanagari) from Advaita Sharada /read/{book}. sanskrit_mula = verse, sanskrit_bhashya = avatarika/bhashya paragraphs incl. interstitial intros and colophon lines. "
                 + (f"English from wisdomlib ({cite}), joined by Devanagari verse text ({t}) or number-checked ref ({r}): {t + r} of {n_v} verse units have english; the rest are null. " if id_ != "taittiriya" else f"English source: wisdomlib ({cite}), not joined. ")
                 + "english = translation of verse + translation of commentary (english_mula / english_bhashya separate). "
                 + "Intro and colophon units have english null. Ref scheme follows Advaita Sharada ids (chapter.section.verse; K = Gaudapada karika). ")
        if id_ == "taittiriya":
            notes += "english deliberately null: wisdomlib's Mahadeva Sastri edition is split per mantra with interleaved Sureshvara and Sayana commentary and numbering that does not map to Advaita Sharada's anuvaka blocks, and trial joins paired the wrong passages. Needs a manual or scan-based alignment. "
        write(f"upanishads/{id_}_shankara.json", dict(
            id=f"{id_}_shankara", text=f"{text} Śāṃkarabhāṣya", tradition="Advaita", commentator="Śaṃkara", script="Devanagari",
            units=u, source_sanskrit={"citation": "Advaita Sharada (Sringeri Sharada Peetham)", "url": AS + book + "/1", "license": AS_LIC},
            source_english={"citation": f"wisdomlib, {cite}", "url": WL + wlbook, "license": None},
            bundled=False, needs_ocr=False, alignment="by_ref", notes=notes.strip()))
        print(id_, len(u), "verse units", n_v, "english text/ref", t, r)

    u = as_units("kena-vakya-bhashya", False)
    write("upanishads/kena_vakya_shankara.json", dict(
        id="kena_vakya_shankara", text="Kena Upaniṣad Vākyabhāṣya", tradition="Advaita", commentator="Śaṃkara", script="Devanagari",
        units=u, source_sanskrit={"citation": "Advaita Sharada", "url": AS + "kena-vakya-bhashya/1", "license": AS_LIC}, source_english=None,
        alignment="not_applicable", notes="Śaṃkara's second Kena commentary (Vakyabhashya). No English source identified; english null."))
    u = as_units("aitareya-bhashya", False)
    write("upanishads/aitareya_shankara.json", dict(
        id="aitareya_shankara", text="Aitareya Upaniṣad Śāṃkarabhāṣya", tradition="Advaita", commentator="Śaṃkara", script="Devanagari",
        units=u, source_sanskrit={"citation": "Advaita Sharada", "url": AS + "aitareya-bhashya/1", "license": AS_LIC},
        source_english={"citation": "Sastri, The Upanishads and Sri Sankara's Commentary Vol. 5", "url": "https://archive.org/details/UpanishadsAndSriSankarasCommentaryVol.5", "license": None},
        alignment="unaligned", needs_ocr=True,
        notes="Sanskrit from Advaita Sharada (verse-structured). English pending OCR pass 2 (Sastri scan); null. Alt Sanskrit: GRETIL sa_aitareyopaniSad-comm.txt (no verse markers)."))
    u = as_units("bhagavadgita-bhashya", False)
    write("philosophical/bg_shankara.json", dict(
        id="1a", text="Bhagavadgītā Śāṃkarabhāṣya", tradition="Advaita", commentator="Śaṃkara", script="Devanagari",
        units=u, source_sanskrit={"citation": "Advaita Sharada", "url": AS + "bhagavadgita-bhashya/1", "license": AS_LIC},
        source_english={"citation": "Sastri 1897, Bhagavad-Gita with the Commentary of Sri Shankaracharya", "url": "https://archive.org/details/Bhagavad-Gita.with.the.Commentary.of.Sri.Shankaracharya", "license": None},
        alignment="unaligned", needs_ocr=True,
        notes="Sanskrit from Advaita Sharada (clean text, so no OCR on the Sanskrit side; the Vani Vilas 1910 scan in the corpus doc is not needed for Sanskrit). English pending OCR pass 2 (Sastri scan); null. ref = chapter.verse; avatarika paragraphs folded into sanskrit_bhashya."))
    u = as_units("chandogya-bhashya", False)
    write("upanishads/chandogya_shankara.json", dict(
        id="chandogya_shankara", text="Chāndogya Upaniṣad Śāṃkarabhāṣya", tradition="Advaita", commentator="Śaṃkara", script="Devanagari",
        units=u, source_sanskrit={"citation": "Advaita Sharada", "url": AS + "chandogya-bhashya/1", "license": AS_LIC},
        source_english={"citation": "Jha, Chandogyopanishad (Mitrasamgraha GV05chupsau), see chandogya_shankara_jha.json", "url": MITRA + "GV05chupsau.tsv", "license": MITRA_LIC},
        alignment="unaligned",
        notes="Sanskrit (verse + bhashya) from Advaita Sharada. english null: the only English (Jha) is sentence-aligned to a different Sanskrit segmentation and lives in chandogya_shankara_jha.json, which pairs them per row."))
    u = as_units("brahmasutra-bhashya", False)
    write("philosophical/bsb_shankara.json", dict(
        id="bsb_shankara", text="Brahmasūtra Śāṃkarabhāṣya", tradition="Advaita", commentator="Śaṃkara", script="Devanagari",
        units=u, source_sanskrit={"citation": "Advaita Sharada (Vani Vilas Sri Shankara Granthavali edition)", "url": AS + "brahmasutra-bhashya/1", "license": AS_LIC},
        source_english={"citation": "Gambhirananda, Brahma-Sutra Bhasya of Sankaracharya", "url": "https://archive.org/details/brahma-sutra-bhasya-of-sankaracharya-swami-gambhirananda", "license": None},
        alignment="unaligned", needs_ocr=True,
        notes="Sanskrit (sutra + Śaṃkara bhashya) from Advaita Sharada, chosen over GRETIL (bsb_shankara_gretil.json, unproofread Sansknet text) as the orthodox edition. English pending OCR pass 2 (Gambhirananda scan); null. ref = adhyaya.pada.sutra; avatarika paragraphs folded into sanskrit_bhashya."))
    print("done")
