# Grantha corpus data card

**What it is.** A Sanskrit-to-English translation benchmark: each unit pairs a Sanskrit passage with a published English translation of the same passage. A model is given the Sanskrit and scored against the English.

**Version.** 2026-10-21. 41 files, 16,742 units, 16,653 scoreable.

**Repository.** `github.com/GranthaLLM/corpus` (private).

**Intended use.** Internal evaluation of Sanskrit translation. Not training data, not a public release. Several English sources are in copyright, so the corpus must not be redistributed.

## Task and scoring

- Input: `sanskrit` of a unit.
- Reference: `english` of the same unit.
- Rule: the two sides must cover the same passage, nothing more and nothing less.
- Units with either side `null` are skipped, not guessed.
- Filter on `reference_type` before averaging: `translation` is a close rendering; `interpretive` is a translator's reading; `summary` is an exposition, not a translation.
- Filter on `english_rights` before any sharing.

## Composition

| Folder | Files | Units | Scoreable |
|---|---:|---:|---:|
| `philosophical/` | 13 | 7,566 | 7,504 |
| `sahitya/` | 8 | 6,672 | 6,672 |
| `upanishads/` | 20 | 2,504 | 2,477 |
| **Total** | **41** | **16,742** | **16,653** |

| Scope | Units | What the pair holds |
|---|---:|---|
| `text` | 9,546 | An independent work, no mula/commentary split |
| `mula` | 2,035 | The verse or sutra only |
| `mula+commentary` | 4,678 | Verse or sutra followed by its commentary |
| `commentary` | 483 | Commentary or intro prose only |

4,703 units carry `parts` (separate mula, bhashya or tatparya), so the mula and commentary can be scored separately.

## References

| `reference_type` | Units | Files | Meaning |
|---|---:|---:|---|
| `translation` | 15,850 | 39 | English translates the Sanskrit |
| `summary` | 771 | 1 | Bhattasangraha: Pandurangi's summary of each adhikarana |
| `interpretive` | 121 | 1 | Aitareya Madhva: Pandurangi's reading as Madhva interprets it |

89 units have no English and are skipped: Bhattasangraha (62) and the Sanskrit-only Madhva bhashya units of Aitareya (27).

## Rights

Best-effort status, recorded per file in `english_rights`:

| Status | Units |
|---|---:|
| CC BY-SA (Mitrasamgraha) | 8,287 |
| Public domain (alone) | 1,153 |
| Public domain mixed with another status | 1,850 |
| Free to copy per author (alone) | 107 |
| Free to copy mixed with another status | 332 |
| In copyright or unclear | 5,013 |

The in-copyright group includes Warrier (Ramakrishna Math), Adidevananda, Gambhirananda, wisdomlib and Prabhupada/Vedabase. This is why the repository stays private.

## Sources

| Source | Used for | Licence |
|---|---|---|
| GRETIL | Sanskrit of several works | CC BY-NC-SA 4.0 |
| Mitrasamgraha | Row-aligned Sanskrit/English pairs (Harivamsha, Kumarasambhava, Mahabharata excerpts, several shastra works) | CC BY-SA |
| Setutila / Sarvamula | Madhva Sanskrit | CC0 |
| Advaita Sharada (Sringeri) | Shankara Sanskrit | No licence stated; kept private |
| wisdomlib | English of many Upanishads and the Gita | Publisher terms; private use |
| Nagesh D. Sonde | Madhva Gita, Brahmasutra and Upanishad English | Author states free to copy |
| OCR of published scans | Gambhirananda, Sastri, Adidevananda, Pandurangi, Subba Rau | Public domain or in copyright, per edition |
| Vedabase / Prabhupada | Bhagavata English | In copyright; terms neutralised, verbatim kept in `meta` |

Each file's `source_sanskrit` and `source_english` give the citation, URL and licence for that file.

## Construction and validation

- Sanskrit is stored in Devanagari. IAST sources were transliterated; legacy-font OCR was decoded.
- English is joined to units by source row, verse number, Devanagari similarity or content. Where the two sides split a passage differently, units are grouped; where a side is missing, it stays `null`.
- `tools/validate.py` checks structure, required fields, scope/kind, junk strings and length ratios. `make check` runs it with the lookup tests.
- `tools/labse_align_audit.py` runs a LaBSE offset-run and neighbour audit. The Harivamsha repartition pass (`tools/harivamsha_repartition.py`) removed the last offset runs.
- Manual audits live in `spotcheck/`. They are dated snapshots, not a live issue tracker.

## Known limitations

- **Reference quality varies.** 892 units are `summary` or `interpretive`, and OCR-derived English can carry slips.
- **Source looseness.** Some translations paraphrase more than others; a few Harivamsha stretches still follow the source TSV's own drift and are listed in the README.
- **Coverage is uneven.** 89 units are unscored, and some works are slices rather than complete texts (e.g. Kumarasambhava cantos 1-7).
- **Hand verification is uneven.** The Harivamsha and Shankara sweeps included hand reading, but there has been no systematic random sample across every file.
- **Not redistributable.** Treat the repository as private; check `english_rights` before sharing any file.

## Maintenance

- Run `make check` after any edit.
- `tools/status.py` regenerates the works table in `README.md`.
- New work files follow `schema.json` and are written with `indent=1`.
- Record source quirks and edits in the file's `notes`; record rights in `english_rights`.
