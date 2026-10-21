# Shankara bhashya audit: Brihadaranyaka (2026-10-09)

> Snapshot: some items below have since been fixed. Check the current file and `git log` before treating an entry as open.

File: `upanishads/brihadaranyaka_shankara.json` (504 units: 255 prose mula+commentary, 107 verse mula+commentary, 70 commentary, 72 mula-only; 742K chars Sanskrit, 1.20M chars english).
English: Madhavananda 1950 via wisdomlib, joined by verse text or ref; Hume 1921 for 6.4.3-5, 9-11, 21-23 mula (Madhavananda omits them). Parts carry english per part (mula, bhashya).
Scope: whole file scanned per part (length ratios, edge alignment, avatarika spill, artifacts, footnote leftovers, Sanskrit hygiene). Flagged units read in full. Not read: the other ~330 mula translations and bhashya bodies sentence by sentence (1.2M chars of english). No edits made.
Companions: `shankara_isa_kena_mandukya_audit.md`, `shankara_prashna_mundaka_aitareya_audit.md`, `shankara_katha_taittiriya_audit.md`, `shankara_chandogya_audit.md`.

Status key: [ ] open, [x] fixed.

## Summary

Unit-level pairing is sound. Median english/Sanskrit ratio 1.56 (log sd 0.20); english text is clean (10.7 periods per 1,000 chars, 622 uses of "I", spacing normal), unlike Chandogya.
Defects are structural: english parked on the wrong part inside a unit, avatarika sentences shifted to the end of the previous unit, leftover footnotes, thin or missing commentary english for about 24 parts.

## 1. Part-level english in the wrong part (inside the unit)

- [ ] **1.4.17** mula part holds 8,287 chars of english (the whole translation, verse plus commentary) for 562 chars of Sanskrit. The bhashya part (4,591 chars Sanskrit) holds 1,396 chars of english which is 25 lines of `:` + footnote text ("The teacher.", "The suffix Satr, denoting concurrence.", "See footnote on p. 121."). Unit total is fine; part split is not.
- [ ] **2.1.20** mula part holds 44,325 chars of english for 221 chars of Sanskrit (the whole unit's translation). Bhashya part (25,253 chars Sanskrit) holds 434 chars of english, all `:` + footnote lines ("The reference is to Dravidacarya.", ...).
- [ ] **4.1.7** bhashya english is 124 chars of `:` + footnotes ("One born of a Ksatriya father and a sudra mother...", "See commentary on III. ix. 24.") with 301 chars of Sanskrit: the commentary translation is missing, only footnotes remain.
- [ ] **3.6.1** mula english is 72 chars ("Then Gargi, the daughter of Vacaknu, asked him. 'Yajnavalkya,' she said,") for 920 chars of Sanskrit. The rest of the verse translation (the whole chain of "By what is water pervaded?") sits at the start of the bhashya part's english, followed by the commentary.
- [ ] **3.9.21** mula english is 176 chars and breaks off at "'On what does the sacrifice rest?'"; the verse translation resumes at the start of the bhashya english ("'On the remuneration (of the priests).'...").
- [ ] **6.4.2** mula english carries the verse translation plus a one-sentence commentary paraphrase; the bhashya part (495 chars Sanskrit) has no english.
- [ ] **6.3.4** mula english (572 chars) is longer than the verse (ratio 2.6); it carries the translator's parenthetical glosses. Not an error, check that the commentary line `अथैनमभिमृशति...` (41 chars) pairs with its sentence "Then he touches the paste uttering the Mantra".
- Fix: repartition english within these units by sentence; unit-level english can stay.

## 2. Avatarika shifted to the end of the previous unit

16 cases where the english of verse N ends with Madhavananda's introduction to verse N+1 ("...The following (three) paragraphs deal with their manifestations relating to the gods:"), while the Sanskrit places that sentence at the top of verse N+1's bhashya.
- [ ] 1.4.1 to 1.4.2, 1.4.9 to 1.4.10, 1.4.15 to 1.4.16, 1.5.3 to 1.5.4, 1.5.10 to 1.5.11, 2.1.19 to 2.1.20, 2.2.1 to 2.2.2, 2.5.10 to 2.5.11, 3.8.10 to 3.8.11, 3.9.9 to 3.9.10, 3.9.26 to 3.9.27, 4.3.8 to 4.3.9, 4.3.9 to 4.3.10, 4.3.16 to 4.3.17, 4.4.3 to 4.4.4, 4.4.4 to 4.4.5.
- Evidence: 2.5.10 bhashya has 33 chars of Sanskrit and 380 chars of english (ratio 11.5): the english is only the avatarika for 2.5.11. 4.1.7, 4.5.5 and others show the same pattern.
- [ ] A further 20 to 25 bhashya parts start with a Sanskrit avatarika (first line ends with a dash or colon) but the english does not start with one (1.3.7, 1.3.8, 1.3.10, 1.3.19, 1.3.20, 1.3.24, 1.4.16, 1.5.4, 1.5.11, 1.5.14, 1.5.16, 1.5.18, 1.5.21, 2.2.2, 2.4.12, 2.5.11, 3.8.11, 3.9.10, 4.2.2, 4.3.10, 4.3.15, 4.3.17, 4.3.18, 4.3.19, 4.3.20, 4.3.23, 4.4.4, 4.4.5, 4.4.7). Some are the 16 spills above landing on the receiving unit; others may be paraphrase the heuristic missed. Read each against the Sanskrit.

## 3. Sanskrit with no english (bhashya parts)

- [ ] About 6,400 chars of Sanskrit in 24 parts have no english: 1.3.14 (36), 2.4.2 (575), 2.4.9 (384), 2.5.2 (49), 4.3.4 (51), 4.5.6 (309), 4.5.10 (116), 4.5.12 (175), 6.2.6 (93), 6.3.3 (314), 6.4.2 (495), 6.4.3 (436), 6.4.4 (644), 6.4.5 (214), 6.4.9 (174), 6.4.10 (231), 6.4.11 (152), 6.4.12 (542 plus 460 of mula Sanskrit), 6.4.21 (167), 6.4.22 (37), 6.4.23 (134), 6.4.26 (73), 6.5.1 (536). Source gaps listed in file notes (Madhavananda omits the sexual-rites passages 6.4.3-5, 9-11, 21-23 and Shankara's comments on them). Decision: leave, drop from scoring, or find another translation (Gambhirananda covers them).
- [ ] **6.4.12 mula** (460 chars Sanskrit) has no part-level english; unit english (1,655 chars) holds the text per file notes (translation moved from 6.4.9). Check which verse it translates: 6.4.12's Sanskrit is the abhicara rite against a wife's lover.
- [ ] **Thin commentary english** (english shorter than Sanskrit, ratio below 0.75): 2.3.1 (0.6), 3.2.9 (0.3, 556 chars of Sanskrit and 146 of english), 3.9.27 (0.6), 4.3.37 (0.7), 4.4.3 (0.7), 1.4.17 and 2.1.20 (parts, see section 1). Partial commentary translation.
- Source mixing: 6.4.3-5, 9-11, 21-23 mula english is Hume 1921 (archaic: "Thou that from every limb art come, / That from the heart art generate"). File notes record it; consider recording in `meta.english_source` for those parts only.

## 4. Artifacts in english

- [ ] **`(?)` OCR holes mid-word** in 1.4.9 (3), 1.4.10 mula (14) and bhashya (20): `t(?)roduct`, `i(?) passage`, `alread(?)en said`, `liberatio(?)neither`, `identification with(?)the word`. 37 marks; need re-OCR or manual repair from the wisdomlib page. 1.4.10 is the largest unit (bhashya 24,148 chars Sanskrit, 42,096 english), so a long stretch of text is affected.
- [ ] **`Vere 4.5.6:`** stray at the end of 4.5.5 english.
- [ ] **Footnote leftovers:** 1.4.17 (25 lines), 2.1.20 (8 lines), 4.1.7 (2 lines); 9 footnote-style lines elsewhere ("See p. 118.", "Viz. those meant for the gods..."). File notes say footnotes were stripped; these three units escaped, probably because the bhashya part was empty after cleanup.
- [ ] **Page refs** like `p. 118` inside english in 17 units (1.4.7, 1.4.10, 1.4.17, 2.1.20, 3.2.13, intro-3.3, 3.5.1, 3.8.9 ...).
- [ ] **Lowercase starts** in 4.4.9 and 6.4.5 (mid-sentence).
- Separator, `Com.`, and Sastri-style prefix artifacts do not occur in this file.

## 5. Sanskrit side

- [ ] `(?)` editorial marks in 9 units: 1.4.10, 1.5.2, 2.1.20, 3.5.1, 3.9.22, 4.5.15, 5.1.1, 5.14.1, 6.2.15.
- [ ] Zero-width joiners in 5 units.
- No Vedic `ꣳ`, no Latin script.

## 6. Coverage vs the ranking table

The table lists "over 700 verses". The file holds 504 Sharada units (about 30 prose sections per chapter group) rather than mantra-level verses, with prose kanda sections as single units (up to 24,000 chars of Sanskrit in 1.4.10, 25,000 in 2.1.20). Units of that size dilute any per-passage score. Splitting needs a manual pass.
Left out per file notes: 12 verses Madhavananda omits (4.6.1-3, 6.4.3-5, 9-11, 21-23) now carry Hume as mula english; brihadaranyaka_madhva has 4 gaps.

## Proposed order
1. Mechanical: repartition english between mula and bhashya parts for 1.4.17, 2.1.20, 3.6.1, 3.9.21, 4.1.7, 6.4.2 (section 1).
2. Move the 16 avatarika spills to the receiving unit; then re-run the avatarika heuristic to catch the remaining 20 to 25.
3. Strip `Vere 4.5.6:`, footnote leftovers, page refs, Sanskrit `(?)` and ZWJ.
4. Repair the 37 `(?)` OCR holes in 1.4.9 and 1.4.10 from the wisdomlib page.
5. Decide the 24 missing-commentary parts (6,400 chars): leave, drop, or fill from a second translation.
6. Decide whether to split the very large prose units.

## Method notes
- Per-part flags: no english on Sanskrit, english on no Sanskrit, bhashya ratio above 2.5 or below 0.9, mula ratio above 3.5, artifact regexes, and first/last-line checks. Avatarika spill: previous unit's english ends with a short paragraph ending in colon or dash while the next unit's Sanskrit bhashya starts with a line ending in a dash or colon.
- Rewrite JSON with indent=1 (`tools/common.write`).
