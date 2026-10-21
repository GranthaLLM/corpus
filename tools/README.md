# Tools

Scripts that built and check the corpus. Run them from `corpus/` as `python3 tools/<name>.py`. `common.py` sets `ROOT` and resolves the raw-source cache from `GRANTHA_RAW` (default `raw/`).

The committed JSON is the artifact. Most build scripts are one-off, read files from `GRANTHA_RAW`, and are kept for provenance rather than as a supported pipeline; see "Rebuilding" in the main README.

## Checks

| Script | Job |
|---|---|
| `validate.py` | Required fields, unit keys, scope/kind, junk strings, length ratios. Run this after any edit. |
| `status.py` | Regenerate the Works table in `../README.md`. |
| `lookup.py` | Print a unit or part by `file:ref` or `file:ref.role`. |
| `test_lookup.py` | Tests for `lookup.py`. |
| `audit.py`, `audit_sample.py` | Draw or render units for manual reading. |

`make check` runs `validate.py` and `test_lookup.py`. These need only the standard library.

## Build

| Pattern | Job |
|---|---|
| `build_*.py` | Create work files from the raw sources: `build_tsv.py` (Mitrasamgraha), `build_gretil.py`, `build_shankara.py`, `build_upanishads.py`, `build_bhagavata.py`, `build_bsb_madhva.py`, `build_aitareya_*.py`, `build_sonde_gita.py`, `build_taittiriya_madhva.py`, `build_tarkasamgraha.py`, `build_bhatta.py`, `build_rest.py`, `build_scans.py`. |
| `normalize.py`, `layout.py` | Normalise text and move to the current per-unit layout. |
| `clean_english.py`, `clean_legacy_english.py`, `clean_sanskrit_marks.py`, `strip_footnotes.py`, `strip_source_tags.py` | Remove page furniture, footnotes, embedded Sanskrit and source tags. |
| `drop_unscoreable.py`, `restore_units.py`, `sync_parts.py`, `tag_files.py` | Unit-level housekeeping: drop empty pairs, restore intros/colophons, keep `parts` in step, set file metadata. |

## Joins and repairs

| Pattern | Job |
|---|---|
| `*_english.py`, `*_fill.py`, `*_sonde.py`, `*_pick.py` | Join an English source onto units by verse number, Devanagari similarity or content. |
| `*_align.py`, `harivamsha_realign.py`, `harivamsha_repartition.py`, `merge_row_outliers.py` | Re-pair source rows or units. `harivamsha_repartition.py` redistributes English inside a shifted stretch. |
| `*_fix.py`, `*_relocate.py`, `*_dedupe.py`, `*_spill.py`, `*_resplit.py`, `*_omitted.py`, `harivamsha_prune.py` | Targeted repairs: moved boundaries, duplicated sutra lines, spilled heads/tails, omitted verses, dropped passages. |
| `labse_align_audit.py` | LaBSE offset-run and neighbour audit. Needs `sentence-transformers`. |

## Sources and scripts

| Pattern | Job |
|---|---|
| `sarvam_ocr.py`, `scanparse.py`, `shivaji_to_unicode.py`, `translit.py` | OCR, legacy-font decoding and IAST/Devanagari conversion. |
| `advaita_sharada.py`, `setu.py`, `wl*.py` | Source access: Advaita Sharada, Setutila JSON, wisdomlib cache. |
| `mbtn_english.py`, `mbtn_translate.py`, `sribhashya_sanskrit.py`, `gita_madhva_sanskrit.py` | Work-specific source extraction. |

Dependencies beyond the standard library are listed in `requirements.txt`.
