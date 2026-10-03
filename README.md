# Grantha corpus

Benchmark corpus for the Sarvamoola/Grantha LLM project (advised by Dr. Prathosh, IISc). Companion to the "Grantha LLM: Internal Benchmarking Corpus" doc, which lists the works and the source chosen for each.

Eval use: the model is given `sanskrit`, produces a translation, and that is scored against `english` of the same unit. A unit with a null `sanskrit` or `english` is skipped. `tools/validate.py` checks every file against the layout below.

## Layout

```
philosophical/   Philosophical works (Gita bhashyas, Brahmasutra bhashyas, Nyaya, Samkhya, ...)
upanishads/      One file per Upanishad per commentator track, e.g. isa_shankara.json, isa_madhva.json
sahitya/         Sahitya Sanskrit (Mahabharata excerpts, Harivamsha, Kumarasambhava, Shatakatraya, ...)
schema.json      JSON Schema for a work file
tools/           Scripts that built the files from the cached sources (need a local source cache, see below)
```

## Schema

See `schema.json`. Every file has `id`, `text`, `tradition`, `script` (always Devanagari), `units[]`, `source_sanskrit`, `source_english`, `bundled`, `needs_ocr`, `alignment`, `notes`. Every unit has the same core:

```json
{ "ref": "...", "kind": "verse|sutra|prose|group", "scope": "...", "sanskrit": "...", "english": "..." }
```

- `sanskrit` / `english`: the eval pair. `english` is the translation of exactly what `sanskrit` holds, never more or less.
- `scope` says what that pair covers: `text` (an independent work: Shatakatraya, Tarkasaṃgraha, Harivamsha, MBTN, ...), `mula` (verse or sutra only), `commentary` (commentary or intro prose only), `mula+commentary` (both, joined with a newline).
- `parts` (optional, never scored): the pieces of a commentary unit, `[{"role": "mula|bhashya|tatparya", "sanskrit": ..., "english": ...}]`. A part may lack `english` when the source does not split its translation. A part may sit outside `scope`: the Bhagavata files keep Madhva's commentary as a part with Sanskrit only, while the pair covers the verse alone.
- `meta` (optional): source-specific extras. Bhagavata keeps `english_verbatim` (Prabhupada as published), `english_edits`, `english_flags`, `align`, `vedabase_texts` there; `english` is the neutralised variant made for this benchmark, so cite `meta.english_verbatim`.
- `reference_type` (file level, optional): `translation` (english translates the sanskrit), `interpretive` (the translator's reading or expansion, e.g. Pandurangi's Madhva-guided Aitareya, Vasu's Chandogya), `summary` (Bhattasangraha). Filter on it when scoring.
- `english_rights` (file level, optional): rights status of the english sources, best effort and to be verified before any release: `public_domain`, `free_to_copy_per_author` (Sonde), `cc_by_sa` (Mitrasamgraha), `in_copyright_or_unclear`.
- `alignment`: `row_aligned` (source pairs them), `by_ref` (two sources joined on ref, not verified), `unaligned` (one side missing or not split per unit)
- `slice_of`: row range when a file is a slice of a larger source file
- `notes`: anything a user must know (source quirks, gaps, deviations from the corpus doc)

### How a commentary work is organised

- Verses and the commentary on them stay in order. Inside a unit with `scope` `mula+commentary`, `sanskrit` and `english` hold the verse first, then the commentary; `parts` names each piece (`mula`, `bhashya`, `tatparya`) with its own Sanskrit and English.
- The opening of a work is its own units: `intro` holds the shanti invocation (`mula` part) and the commentator's mangalacharana (`bhashya` part); a second `intro-2` repeats the closing shanti where the Sanskrit source does; `colophon*` units hold the closing lines.
- A commentary that the source gives as one continuous block, not mantra by mantra, is a unit of its own with `scope` `commentary` (Madhva's Kena commentary is the unit `bhashya` in `kena_madhva.json`).
- A commentary part whose English is missing says so by having no `english`; the unit's own pair never mixes in text from outside it.

Nothing is invented: a string is either verbatim from the cited source or `null`. A `null` `english` with `needs_ocr` or a note means the source is a scan that pass 2 will fill.

Build order: the `build_*.py` scripts, then `normalize.py`, then `layout.py` (old per-field layout to the layout above), then `clean_english.py` (drops embedded Sanskrit verses and page headers from `english`), then `validate.py`.

## Known issues

What a user of the corpus should know before relying on a file. The unit count in the status table includes all of these.

- **Dropped units**: every file except Bhattasangraha holds only units with both Sanskrit and english. 465 units with no english in any source (317 colophons, intros and some commentary-only or untranslated verse units) were removed; the refs are listed in each file's notes, and `tools/drop_unscoreable.py` reproduces the cut. Git history before this commit still has them.
- **Alignment audit**: a LaBSE sentence-embedding sequence test (`tools/labse_align_audit.py`) found no offset runs left in any file after repairs: Bhagavata Kapila/Uddhava were re-paired by content (Setutila and Vedabase verse numbers drift), 12 Harivamsha stretches and one each in Sarvadarshanasamgraha and Vidura Niti where english sat 1-3 rows off were merged into single units. The test cannot see a unit whose neighbours are all equally off, and LaBSE is weak on verse, so some Bhagavata pairs (roughly 1 in 7 in a sample) can still be wrong.
- **Bhattasangraha** (`reference_type: summary`): english is Pandurangi's summary of each adhikarana, not a translation, and 57 units have none; its Sanskrit is unproofread OCR.
- **Chandogya, Madhva track** (`translation`): english is Sonde's, matched to units by decoded Sanskrit; units are Setutila's khanda ranges (up to 5k-37k chars), and some undecoded legacy tokens remain.
- **Chandogya, Shankara track**: Jha's english is clause by clause with the sentence-final periods stripped; in the 35 merged units the Sanskrit and the english both follow the text order (mula, its commentary, the next mula, its commentary); some intro units have no english.
- **Aitareya, Madhva track** (`interpretive`): units are passages of the Upanishad with Pandurangi's translation as Madhva reads it; about 12% of the mula text is in no unit, and Madhva's commentary is Sanskrit-only (`-bhashya` units).
- **Gita, Shankara track**: about 24 units still have english somewhat shorter than the Sanskrit commentary (52 others were replaced with Warrier fuller translation); 14 units have none; OCR slips in diacritics (`^`, `~`) remain.
- **Gita, Ramanuja track**: the english of a few verses covers two verses jointly (those are merged units); translator's bracketed notes and running heads were stripped, but OCR slips can remain; intro units have no english.
- **Gita, Madhva track**: a unit pairs only the parts whose Sanskrit and english are comparable in length, so many commentary parts sit in `parts` outside the scored pair; the Sanskrit decoded from Sonde's legacy-font PDF can contain stray misspellings; 12 colophon units have none; 7/30, 8/8 and 18/33 were filled from Sonde.
- **Harivamsha**: the Mitrasamgraha rows carried critical-apparatus text in front of some verses, which was stripped; 106 units whose Sanskrit was apparatus only or whose rows were shifted against the english were dropped.
- **Shatakatraya**: 6 verses have no english (1.39, 1.109, 3.40, 3.98, 3.100 twice) plus 2.101 (no counterpart in Gopalachariar). Shringarashataka English is partly Kennedy 1913 (free paraphrase) and partly Gopalachariar 1954 (in copyright).
- **Invocations**: the opening shanti and mangalacharana of `katha_madhva`, `prashna_madhva` and `isa_madhva` are translated from Vasu 1909 (wisdomlib).
- **Scans**: english taken from OCR of scans (Gambhirananda, Sastri, Adidevananda, Pandurangi, Subba Rau) can still hold OCR slips.
- **Intro and colophon units** are mostly Sanskrit only.

## Two-pass approach

1. **Pass 1, clean sources.** Advaita Sharada (Sringeri, Vani Vilas edition) for every Śaṃkara Sanskrit text (Gita, Brahmasutra, all Upanishads), Setutila JSON (CC0) for Madhva Sanskrit, wisdomlib for English of the Upanishads, Mitrasamgraha TSVs, GRETIL plaintext. No OCR. Where the paired side is a scan, that side is `null` until pass 2.
2. **Pass 2, OCR backfill.** The archive.org scans marked `needs_ocr` in the corpus doc. `_djvu.txt` as a stopgap, Sarvam Vision or Tesseract where quality is too poor. Each refined file records the OCR method in `notes`.

## Licences and provenance

- GRETIL: CC BY-NC-SA 4.0
- Mitrasamgraha: CC BY-SA
- Setutila/Sarvamula: CC0
- Advaita Sharada: Sringeri Sharada Peetham; no licence stated on the site, `robots.txt` allows crawling. Kept private.
- Nagesh D. Sonde (Madhva Gita, Brahmasutra, Taittiriya, Bṛhadāraṇyaka, Kena, Kaṭha, Muṇḍaka, Chāndogya translations): the author states they are not protected by copyright and free to copy and distribute.
- Kennedy 1913 (Śṛṅgāraśataka English), Sastri 1903/1905 (Taittiriya and Kena Śaṃkara), Subba Rau 1904 (Madhva Brahmasutra): public domain.
- Warrier (Ramakrishna Math, Śaṃkara Gita), Adidevananda (Rāmānuja Gita), Gambhirananda (Śaṃkara Brahmasutra): in copyright; hence the repo stays private.
- wisdomlib: translations are copyrighted by their publishers and hosted there under wisdomlib's terms. This repo is private for that reason; check before any redistribution.

## Tools added late

- `tools/shivaji_to_unicode.py`: decodes text typed in the legacy Shivaji01 Devanagari font (Sonde's PDFs) to Unicode, about 93-95% character agreement against our Sanskrit.
- `tools/gita_madhva_sanskrit.py`, `tools/aitareya_madhva_pandurangi.py`: fill commentary Sanskrit decoded from Sonde's Gita PDF; rebuild `aitareya_madhva` from Pandurangi's scan, OCR'd with Bodhan's IndicOCR (needs `rapidfuzz`).
- `tools/*_english.py`, `*_fill.py`, `*_sonde.py`: per-work joins of English onto the units (by verse number, by Devanagari similarity, or by content). Each reads its source from `GRANTHA_RAW`, so none can be re-run without that cache.
- Files that took English from two sources say so in `notes`; a unit never mixes sources.

## Rebuilding

`tools/` expects a cache of the raw sources in the directory named by `GRANTHA_RAW` (GRETIL txt, Mitrasamgraha TSV, Setutila `set_*.json`, `wl_cache/` of wisdomlib page text, `sribhashya_bodhan/` Bodhan OCR text of the Sri Bhashya scan, `mbtn_hariprasad/` text layer of the Nellitheertha MBTN PDF, chapter 16 PDF and `verse_en.json`, Bodhan machine translations of the Sanskrit verses used only to align). The cache is not committed.

<!-- status:start -->
## Status

Generated by `tools/status.py`. 'Sanskrit+English units' counts units where both fields are filled; 'first pass' OCR-derived English can be noisy.

| Row | Work | Files | Units | Sanskrit+English units | Status |
|---|---|---|---|---|---|
| 1a | Gita, Śaṃkara | `bg_shankara` | 697 | 697 | English from Sastri scan (archive OCR), verse-matched; 77% of verses |
| 1b | Gita, Rāmānuja | `bg_ramanuja` | 692 | 692 | English from Adidevananda scan (archive OCR), verse-matched; 82% |
| 1c | Gita, Madhva | `bg_madhva` | 319 | 319 | Bhashya + Tatparya Sanskrit (Setutila), English from Sonde PDF; verse groups |
| 2 | Brahmasutra, Śaṃkara | `bsb_shankara` | 555 | 555 | Sanskrit Advaita Sharada; English Gambhirananda scan, 509/555 sutras |
| 3 | Sri Bhashya, Rāmānuja | `sribhashya_ramanuja` | 539 | 539 | English Thibaut via wisdomlib; Sanskrit Bodhan OCR of the Annangaracharya scan (unproofread), aligned per sutra; 6 units hold two sutras |
| 4 | Brahmasutra, Madhva | `bsb_madhva` | 566 | 566 | Sanskrit from the project docx; English Subba Rau (1904) where its OCR is clean, otherwise Sonde (decoded and translated PDFs); every sutra has English |
| 5 | Tarkasaṃgraha | `tarkasamgraha` | 62 | 62 | Mula only (Dipika dropped); Sanskrit + English from the 1876/1851 scan (Sarvam OCR), book numbering 1-70; 63 sections, 7 lost to OCR numbering |
| 6 | Bhattasangraha | `bhattasangraha` | 771 | 709 | Sanskrit archive.org OCR (adhyayas 1-12, one unit per adhikarana, unproofread, some headings lost); English is Pandurangi's summary of each adhikarana (not a translation): exposition in vols 1 and 3 paired by heading name, introduction summary in vol 2 paired by adhyaya.pada.number |
| 7 | Sarvadarshanasamgraha | `sarvadarshanasamgraha` | 1746 | 1746 | Mitrasamgraha rows, bundled |
| 8 | Vimshatika/Trimshika | `vimshatika_trimshika` | 162 | 162 | Mitrasamgraha rows; appears to be the Vimshatika only |
| 9 | Samkhyakarika | `samkhyakarika` | 606 | 606 | Mitrasamgraha rows (Matharavritti) |
| 10 | MBTN | `mbtn` | 723 | 723 | Sanskrit Setutila; English Nellitheertha 2021, aligned per chapter by order (names, length, machine-translation similarity); units over 16 verses split into ~8-verse groups |
| 11-20 Śaṃkara | Upanishads, Śaṃkara track | `isa_shankara`, `kena_shankara`, `katha_shankara`, `prashna_shankara`, `mundaka_shankara`, `mandukya_shankara`, `brihadaranyaka_shankara`, `taittiriya_shankara`, `aitareya_shankara`, `chandogya_shankara` | 1592 | 1592 | Sanskrit Advaita Sharada; English wisdomlib (Taittiriya none), Sastri scan (Aitareya, khanda level); Chandogya English from Jha (joined by content) |
| 11-20 Madhva | Upanishads, Madhva track | `isa_madhva`, `kena_madhva`, `katha_madhva`, `prashna_madhva`, `mundaka_madhva`, `mandukya_madhva`, `taittiriya_madhva`, `aitareya_madhva`, `chandogya_madhva`, `brihadaranyaka_madhva` | 541 | 541 | Sanskrit Setutila; English wisdomlib (Isa..Mandukya), Sonde+Sarvam OCR (Taittiriya), Pandurangi (Aitareya); Chandogya English Sonde (commentary only, khanda ranges joined); Brihadaranyaka English missing |
| 21a-c | Mahabharata: Sanatsujatiya, Vidura Niti, Yaksha Prashna | `sanatsujatiya`, `vidura_niti`, `yaksha_prashna` | 1183 | 1183 | Mitrasamgraha slices of the Ganguli file |
| 22a-b | Bhagavata: Kapila (3.25-33), Uddhava Gita (11.7-29) | `bhagavata_kapila`, `bhagavata_uddhava` | 1270 | 1270 | Sanskrit Setutila; English Prabhupada via Vedabase (neutralised terms; verbatim in meta.english_verbatim) |
| 23 | Harivamsha | `harivamsha` | 7244 | 7244 | Mitrasamgraha rows |
| 24 | Kumarasambhava | `kumarasambhava` | 424 | 424 | Mitrasamgraha rows; cantos 1-7 only (source ends there) |
| 25 | Shatakatraya | `shatakatraya` | 318 | 318 | Sanskrit GRETIL; English Wortham 1886 (OCR, unproofread) paired by content, Niti and Vairagya; Shringarashataka gaps from Kennedy 1913 and Gopalachariar 1954 (in copyright) |
<!-- status:end -->
