from common import *


def units(name, start=0, end=None):
    return [{"ref": str(i), "kind": None, "sanskrit": sa, "english": en} for i, sa, en in tsv_rows(name, start, end)]


def sk(url_name, cite, lic=MITRA_LIC):
    d = {"citation": cite, "url": MITRA + url_name, "license": lic}
    return d


def simple(rel, id_, text, trad, tsv, cite, notes, script="IAST", commentator=None, start=0, end=None, slice_of=None, english_cite=None):
    src = sk(tsv, cite)
    n = write(rel, dict(id=id_, text=text, tradition=trad, commentator=commentator, script=script,
                        units=units(tsv, start, end), source_sanskrit=src, source_english=dict(src),
                        bundled=True, needs_ocr=False, alignment="row_aligned", slice_of=slice_of, notes=notes))
    print(rel, n)


ROWNOTE = "ref = row number in the source TSV (1-based line). Rows are sentence-aligned Sanskrit/English pairs from Mitrasamgraha; row boundaries follow the dataset, not verse numbering. "

if __name__ == "__main__":
    simple("philosophical/sarvadarshanasamgraha.json", "7", "Sarvadarśanasaṃgraha", "All schools", "GSP36sadha.tsv",
           "Mādhava, Sarvadarśanasaṃgraha, Cowell & Gough translation (Mitrasamgraha GSP36sadha)",
           ROWNOTE + "Sanskrit column is unsplit Devanagari-to-IAST text.")
    simple("philosophical/vimshatika_trimshika.json", "8", "Viṃśatikā and Triṃśikā of Vasubandhu", "Yogacara", "T06vasvvmsu.tsv",
           "Vasubandhu, Viṃśatikā with vṛtti, Anacker translation (Mitrasamgraha T06vasvvmsu)",
           ROWNOTE + "TSV file name and content indicate the Viṃśatikā with its commentary (The Twenty Verses and Their Commentary); check whether the Triṃśikā is present before treating this as covering both works.")
    simple("philosophical/samkhyakarika.json", "9", "Sāṃkhyakārikā of Īśvarakṛṣṇa", "Samkhya", "GSP31iskamatu.tsv",
           "Īśvarakṛṣṇa, Sāṃkhyakārikā with Māṭharavṛtti, Wilson translation (Mitrasamgraha GSP31iskamatu)",
           ROWNOTE + "File name indicates the Māṭharavṛtti; rows interleave kārikā and commentary.", commentator="Māṭhara (per file name)")
    simple("upanishads/chandogya_shankara_jha.json", "chandogya_shankara_jha", "Chāndogya Upaniṣad Śāṅkarabhāṣya", "Advaita", "GV05chupsau.tsv",
           "Chāndogya Upaniṣad with Śaṅkara's commentary, Jha translation (Mitrasamgraha GV05chupsau)",
           ROWNOTE + "Bundled sentence-aligned TSV (Jha). Alternative to chandogya_shankara.json, whose Sanskrit comes from Advaita Sharada; this file is kept because it pairs Sanskrit and English per row.", commentator="Śaṅkara")
    simple("sahitya/harivamsha.json", "25", "Harivaṃśa", None, "GE07hv_conpu.tsv",
           "Harivaṃśa, Dutt translation (Mitrasamgraha GE07hv_conpu)", ROWNOTE)
    simple("sahitya/kumarasambhava.json", "26", "Kumārasambhava", None, "GK19kaku.tsv",
           "Kālidāsa, Kumārasambhava, Kale edition/translation (Mitrasamgraha GK19kaku)",
           ROWNOTE + "424 rows hold 519 verses (some rows pack two verses, '//' ends a verse). The source file ends at the wedding of Shiva and Parvati (canto 7); cantos 8-17 are not in the Mitrasamgraha dataset, so this file is partial relative to the full poem.")
    g = "GE07mbh-ganguly.tsv"
    base = "Mahābhārata, Ganguli translation (Mitrasamgraha GE07mbh-ganguly). Sanskrit column is padaccheda-split IAST. "
    simple("sahitya/sanatsujatiya.json", "23a", "Mahābhārata: Sanatsujātīya", None, g, base,
           ROWNOTE + "Slice = Udyoga Parva Sections XLI-XLVI (Sanat-sujata Parva), rows 27805-28144 of the source TSV; Section XLVII narrative conclusion excluded. Boundaries set by where the Sanskrit of each section begins; the first row's English carries a verbatim tail of the preceding section (source English column lags mid-row). Verify against the printed text before use.",
           start=27804, end=28144, slice_of={"file": g, "rows": "27805-28144"})
    simple("sahitya/vidura_niti.json", "23b", "Mahābhārata: Viduranīti (Prajāgara)", None, g, base,
           ROWNOTE + "Slice = Udyoga Parva Sections XXXIII-XL (Vidura-Prajagara), rows 27070-27804. Boundaries set by where the Sanskrit of Section XXXIII begins; verify. English of the first row carries the verbatim tail of the preceding section because the source English column lags mid-row.",
           start=27069, end=27804, slice_of={"file": g, "rows": "27070-27804"})
    simple("sahitya/yaksha_prashna.json", "23c", "Mahābhārata: Yakṣapraśna", None, g, base,
           ROWNOTE + "Slice = Vana (Aranyaka) Parva Sections CCCXI-CCCXII and the closing rows of the episode, rows 23390-23505. Boundaries set by where the Sanskrit of Section CCCXI begins; first row's English carries a verbatim tail of the preceding text. Verify.",
           start=23389, end=23505, slice_of={"file": g, "rows": "23390-23505"})
