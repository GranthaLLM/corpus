# Shankara bhashya audit: Prashna, Mundaka, Aitareya (2026-10-09)

> Snapshot: some items below have since been fixed. Check the current file and `git log` before treating an entry as open.

Files: `upanishads/prashna_shankara.json` (72 units), `mundaka_shankara.json` (71), `aitareya_shankara.json` (6).
Scope: every Prashna and Mundaka mula translation read against what the verse says; bhashya parts checked by length ratio, avatarika/edge alignment, scrape and OCR scan; Aitareya checked at unit edges and for noise. Not every bhashya sentence read. No edits made.
Companion to `shankara_isa_kena_mandukya_audit.md`.

Status key: [ ] open, [x] fixed.

## Summary

| Work | Verses | Shifts | Mula translation errors | Artifacts | Notes |
|---|---|---|---|---|---|
| Prashna | 67 (16+13+12+11+7+8, all present) | none found | 4.8 omits four items, 6.1 wrong name, 3.11 lost "not", 1.3 | separator lines in 5 units, `Com.` prefix, OCR typos | 4 Vedic `ꣳ` in Sanskrit |
| Mundaka | 64 (9+13+10+11+10+11, 2.2.7-8 merged) | none found | 3.2.11 does not translate the Sanskrit | separator lines in 6 units, stray verse counters, OCR typos | Sastri numbering offset in 2.2 |
| Aitareya | 33 mantras, only 6 khanda-level units | n/a | n/a | heavy OCR noise, page headers | no verse or part-level english at all |

Prashna and Mundaka are clean on alignment. Avatarika lines sit with the right verse; length ratios are 1.3 to 2.0 throughout.

## Prashna

- [ ] **4.8 mula english omits items.** Sanskrit lists `श्रोत्रं च श्रोतव्यं च` (ear, hearing object) and `घ्राणं च घ्रातव्यं च` (nose, smell object). English goes "sight and its objects, taste and its objects, touch..." with no ear or nose. Translator dropped them. Add or note.
- [ ] **6.1 mula english name.** Sanskrit `हिरण्यनाभः कौसल्यः`; english "Hiranyagarbha of Kosala". Should be Hiranyanabha. Source error.
- [ ] **3.11 mula english lost the negation.** Sanskrit `न ह अस्य प्रजा हीयते` ("his offspring does not decline"); english "of his offspring there is break". Bhashya english of 3.11 is right ("do not suffer break in continuity"). Fix mula to "there is no break".
- [ ] **1.3 mula english** makes Kabandhi and Katyayana two people ("Kabandhi, having approached Katyayana asked"). Sanskrit `कबन्धी कात्यायन उपेत्य पप्रच्छ`; Katyayana is his patronym (1.1 english says "Kabandhi, son of Katya"). Source error.
- [ ] **Separator lines** at end of bhashya english: 1.16, 2.13, 3.12, 4.11, 5.7 (`———`). Strip.
- [ ] **`Com.` prefix** on 64 of 66 bhashya english parts. 4.1 reads `Cow.—` and 5.1 reads `Com,—` (OCR). Decide: strip the prefix everywhere (it is not in the Sanskrit) or keep.
- [ ] **Bracket glosses** `Word] explanation` left from Sastri's layout in english of 1.8, 1.11, 3.12, 5.4 (13 occurrences). Fine as translation, but note the format.
- [ ] OCR typos in mula english: "brandies" for branches (3.6), "mot" for not (4.2), "good youth I" (4.7), "Âtman" diacritic style differs from other works.
- [ ] Sanskrit: 4 lines carry Vedic `ꣳ` (U+A8F3) instead of `ं` (e.g. 2.4 `तस्मिꣳश्च`). Normalise with `clean_sanskrit_marks.py` if policy is plain anusvara.
- [x] n/a. 1.1 (intro folded) and 6.7-8 (merged) already documented in file notes.

## Mundaka

- [ ] **3.2.11 mula english does not translate the verse.** Sanskrit `तदेतत्सत्यमृषिरङ्गिराः पुरोवाच...` ("This is the truth, which the seer Angiras told of old"). English: "This external purusha did the seer Angiras teach in ancient times". "external" is an OCR slip for "eternal", and "truth" is dropped. The bhashya english below it is right ("This undecaying and true purusha...").
- [ ] **Stray verse counters** in mula english: `(3)` in 1.1.3, `(6)` in 1.1.6, `(7)` in 3.1.7, `(10)` in 2.1.10, `(20)` in 3.2.10. Strip.
- [ ] **Separator lines** at end of bhashya english: 1.1.9, 1.2.13, 2.1.10, 2.2.12, 3.1.10, 3.2.11 (`——o——`, `——:o:——`). Strip.
- [ ] **Sastri numbering offset in 2.2.** After the 2.2.7-8 merge, mula english numbers run one behind the ref: ref 2.2.9 english says "8.", 2.2.10 "9.", 2.2.11 "10.", 2.2.12 "11.". Content is correct. Renumber or strip leading verse numbers.
- [ ] **`(preceptor?)`** in 1.2.12 mula english (OCR query mark). Strip.
- [ ] **OCR typos** in mula english: "sulothia" for sulohita (1.2.4), "Hut" and "lie" for But and he (3.1.2), "doing nets" for acts (3.1.4), "how" for bow (2.2.3, 2.2.4), "horn" for born (2.2.6), "blight" for bright (2.2.7-8), "perceptor" (1.2.12), "Brahma n" (3.2.6).
- [ ] **1.2.4 bhashya Sanskrit** repeats the whole verse as a pratika before the gloss (197 chars vs english 127, ratio 0.6). Not an error, but it inflates Sanskrit length for scoring.
- [ ] `Com.—` prefix on all 64 bhashya english parts (same policy question as Prashna).
- [x] n/a. Intro-1.1, intro-2.1, intro-3.1 and 2.2.7-8 already documented in file notes.

## Aitareya

Units: intro, 1.1, 1.2, 1.3, 2.1, 3.1 (khanda or adhyaya level). Sastri groups mantras differently from Sharada, so verse pairing was never possible (file notes say so).

- [ ] **No part-level english.** Every unit has mula and bhashya Sanskrit parts but english only at unit level. The scorer cannot align mantra against its translation.
- [ ] **OCR noise in english**, all units: `LJldha`, `Fr ana`, `ont` for one (intro); `deitjr`, `procreac ting`, `Apdna` (1.1); `yespeefeive ^deities` (1.2); `Hence the?©`, `Bevas`, `food*` (1.3); `Sdmswra`, `&e.` (2.1). About 30 to 100 stray non-ASCII characters per unit.
- [ ] **Printed page headers inside english:** `WITH SHI SANKARA'S COMMENTARY.` plus page number in 1.2, 1.3, 2.1 (twice), 3.1 (twice). 2.1 opens with `with sri sankara ? s commentary. 39 *`. Strip.
- [ ] **Verse-number remnants** in english: `(1)`, `(!)•`, `(1)*`. Strip.
- [ ] **Quote marks garbled:** `5 '` for closing quote, `55` for `"`. Normalise.
- [ ] **intro** english opens with Sastri's heading "SRI SANKARA'S INTRODUCTION. / Adoration to the Brahman." No Sanskrit counterpart. Strip.
- [ ] **Chapter-end summary check:** 2.1 english opens with Shankara's adhyaya summary ("The purport of this fourth chapter..."), which does match the first Sanskrit bhashya paragraph (`अस्मिन्नध्याये एष वाक्यार्थः`). Sastri calls it the "fourth chapter" (his Part IV); text is right, label is not.
- [ ] Decide: re-OCR from archive.org text layer versus find a cleaner Sastri/Gambhirananda source. Verse-level units are available in git history (file notes).

## Proposed order
1. Strip artifacts: separator lines (Prashna 5, Mundaka 6), `Com.` prefix policy, Mundaka stray counters and `(preceptor?)`, Aitareya headers and verse remnants.
2. Fix mula english: Prashna 3.11 (add "no"), 4.8 (add ear, nose), 6.1 (name), Mundaka 3.2.11 (translate the verse).
3. OCR typo pass (Mundaka mula, Prashna mula, Aitareya).
4. Mundaka 2.2 renumbering.
5. Decide Aitareya path: clean current OCR, or rebuild with verse-level pairing from history.
6. Normalise Vedic `ꣳ` if policy requires.
