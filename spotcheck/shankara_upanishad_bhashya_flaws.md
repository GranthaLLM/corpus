# Shankara Upanishad bhashya: all flaws found (audit of 2026-10-09)

> Snapshot: some items below have since been fixed. Check the current file and `git log` before treating an entry as open.

Covers the ten Shankara tracks in `corpus/upanishads/`: Isa, Kena, Mandukya, Prashna, Mundaka, Aitareya, Katha, Taittiriya, Chandogya, Brihadaranyaka.
Detail per work lives in the six audit files next to this one (`shankara_*_audit.md`). This file is the merged list, ordered by how much each flaw hurts scoring.
No edits were made at the time of this audit; some items have since been fixed. Status key: [ ] open, [x] fixed.

## How far each work was checked

| Work | Units | How it was checked | Not checked |
|---|---|---|---|
| Isa | 20 | every unit at the edges, 5 units in full | none material |
| Kena | 40 | every unit at the edges | translations read for gloss, not word by word |
| Mandukya | 225 | length ratios, artifact scan, about 40 flagged units in full | most karikas not read |
| Prashna | 72 | every mula translation read; bhashya by ratio and edges | bhashya bodies |
| Mundaka | 71 | every mula translation read; bhashya by ratio and edges | bhashya bodies |
| Aitareya | 6 | unit edges, noise scan | no verse-level pairing exists |
| Katha | 129 | every mula translation read; bhashya by ratio and edges | bhashya bodies |
| Taittiriya | 64 | both edges of every unit, ratios, OCR count | mid-unit text |
| Chandogya | 760 | whole-file scripts (ratios, name lexicon, punctuation profile), flagged units in full | sentence-level alignment |
| Brihadaranyaka | 504 | whole-file per-part scripts, flagged units in full | about 330 mula translations, bhashya bodies |

## A. Worst problems (affect many units or score validity)

1. **Chandogya english is mechanically damaged.** 749,606 chars contain 29 full stops, zero standalone "I", 2,603 commas with no following space, 700 semicolons with no following space, 170 fused words (`thesehe`, `AnswerWater`), fused hyphen compounds (`goodsmelling`, `twolegged`), `ie` for i.e. Reads as ungrammatical ("if drank this water, would be drinking what is contaminated", 1.10.3). The loss is in the Jha source rows already at `af8dedf`. Fix: re-extract from the wisdomlib edition of Jha and re-join with `tools/merge_chandogya.py`.
2. **Aitareya has no verse-level or part-level english.** Only 6 khanda units; english sits at unit level, with heavy OCR noise (`LJldha`, `Fr ana`, `yespeefeive ^deities`), printed page headers (`WITH SHI SANKARA'S COMMENTARY.`), garbled quote marks. Needs a rebuild (verse-level units exist in git history) or a cleaner source.
3. **Commentary english missing where Sanskrit exists.** Roughly 17,000 chars of Sanskrit bhashya have no english anywhere in these works: Brihadaranyaka 24 parts (about 6,400 chars, mostly 6.4), Katha 11 parts (about 6,000), Mandukya 2.K20-27 and 1.2 opener, Isa 9 preamble (about 1,700), Chandogya intro-4.16. Source gaps for the most part.
4. **Taittiriya granularity.** 33 non-colophon units; chapters 1.3-1.6, 1.11-1.12, 2.8, 3.10 are single multi-mantra units up to 14,000 chars. The ranking table's "120 to 150 structural units" is not what the file holds.
5. **Brihadaranyaka granularity.** 504 Sharada units against "over 700 verses"; prose units up to 24,000 to 25,000 chars of Sanskrit (1.4.10, 2.1.20).

## B. Shifted english (translation sits on the neighbouring unit or part)

| Where | What |
|---|---|
| Isa 9 to 10 | 9's english tail ("Now follows a statement of the distinction between the respective fruits...") is the opener of 10 (`तत्रावान्तरफलभेदं...`) |
| Isa 13 to 14 | 13's english tail ("Since this is so, it is but right...") is 14's opener (`यत एवम्, अतः समुच्चयः...`) |
| Kena 4.6 to 4.7 | 4.6 ends with the opener of 4.7; 4.7 then translates it again |
| Katha 1.3.10 | english 2,068 chars for 700 of Sanskrit; about 1,350 chars translate the commentary of 1.3.11 and 1.3.12 |
| Taittiriya 2.1.0 to 2.1.1 | 2.1.0 (peace invocation) carries about 1,400 chars that translate the first paragraph of 2.1.1's bhashya |
| Chandogya 4.7.1 / 4.7.2 / 4.7.3 | 4.7.1 holds english of 4.7.2's commentary; 4.7.2's tail ("I would declare to thee...") is 4.7.3's verse start |
| Chandogya intro-4.16 | english is 61 chars; the stated reasons are not translated |
| Brihadaranyaka (16 avatarika spills) | english of verse N ends with the introduction to verse N+1: 1.4.1, 1.4.9, 1.4.15, 1.5.3, 1.5.10, 2.1.19, 2.2.1, 2.5.10, 3.8.10, 3.9.9, 3.9.26, 4.3.8, 4.3.9, 4.3.16, 4.4.3, 4.4.4. A further 20 to 25 parts start with a Sanskrit avatarika the english does not start with |
| Brihadaranyaka part splits | 1.4.17, 2.1.20 (mula part holds the whole unit's english, bhashya part holds footnotes only); 3.6.1, 3.9.21 (verse translation breaks off in mula, resumes in bhashya); 4.1.7, 6.4.2 |
| Chandogya, others | file notes list about 100 sub-sentence boundary shifts as open; name-lexicon candidates to read: 5.17.1, 8.9.1, 4.17.1, intro-6.1 |

## C. English with no Sanskrit counterpart

| Where | What |
|---|---|
| Isa 18 | about 2,700 chars (Hiriyanna's vidya/avidya discussion, "Some entertain a doubt...") with no Sanskrit |
| Mandukya 2.K20 to 2.K27 (minus K25) | `bhashya` english is Nikhilananda's footnotes, with no Sanskrit commentary in the source |
| Mandukya, translator remarks inside bhashya | "This Karika gives us an idea of..." closers in 2.K5, 3.K6, 3.K16, 3.K17, 3.K31, 3.K41, 4.K28, 4.K30, 4.K37, 4.K83, 4.K90, 4.K92; trailing explanatory paragraphs in 3.K18, 4.K12, 4.K40, 4.K77, 4.K84, 4.K87, 4.K89 (verify each); 1.8 paragraphs 3 and 4 are the translator's introduction. Length ratio 4 to 5 against a normal 2 in 1.8, 2.K28, 2.K29, 3.K41, 4.K6 |
| Kena intro-1 | opens "ADORATION TO THE BRAHMAN. OM TAT SAT." |
| Taittiriya 1.1.1 | opens `Om 7a£ &a£. Adoration to Brahman.` |
| Aitareya intro | heading "SRI SANKARA'S INTRODUCTION. / Adoration to the Brahman." |

## D. Sanskrit with no english (non-source-gap cases)

- Mandukya 1.2: first about 480 chars of bhashya (`अभिधानाभिधेययोरेकत्वेऽपि...` to `...ब्रह्म प्रतिपद्येत`) untranslated; ratio 1.09 is the tell.
- Mandukya 1.K24: `इति माण्डूक्योपनिषत्समाप्ता ॥` untranslated.
- Isa 2 and 3: bhashya openers (`एवमात्मविदः...`, `अथेदानीमविद्वन्निन्दार्थोऽयं...`) untranslated; 10 and 14 lose theirs through the shifts above.
- Mandukya 1.K3, 1.K4, 4.K7 and Chandogya 3.3-3.5 style mula-only units: check the Sanskrit source for commentary.
- Taittiriya 3.3.1, 3.4.1, 3.5.1 and 3.1.0 mula only.
- Mandukya 2.K25: no commentary english.

## E. Mula translation errors (the english does not say what the verse says)

| Where | Error |
|---|---|
| Prashna 4.8 | english omits ear and hearing-object, nose and smell-object that the Sanskrit lists |
| Prashna 6.1 | "Hiranyagarbha of Kosala" for `हिरण्यनाभः कौसल्यः` |
| Prashna 3.11 | "of his offspring there is break" for `न ह अस्य प्रजा हीयते` (negation lost; bhashya english is right) |
| Prashna 1.3 | Kabandhi and Katyayana made two people; Katyayana is his patronym |
| Mundaka 3.2.11 | translates as "This external purusha did the seer Angiras teach..." for `तदेतत्सत्यम्...` ("This is the truth..."); "external" is an OCR slip for eternal |
| Kena (gloss inside translation) | 1.2 "Being disabused of the false notion"; 2.4 "known well, when it is known as the witness of every state of consciousness"; 4.4, 4.5 paraphrase; 3.9, 3.10 `आददीय` as "blow away" (Shankara glosses take); 4.9 `स्वर्गे लोके` as "blissful Brahman" |
| Isa (translator choices, record only) | 8 `परिभूः` as "superposed"; 12 and 13 `सम्भूति/असम्भूति` as "manifest/unmanifest"; 15 "verse 9" where verse 7 is meant |
| Mandukya mula | Nikhilananda's long bracketed expansions: mula english over 3x Sanskrit in 1.K9, 2.K8, 3.K3, 3.K12, 4.K44, 4.K86, 4.K87, 4.K88 and more (about 35 units over 3x). Style mismatch, not wrong |
| Katha | 11 mula verses (1.3.11, 1.3.12, 2.1.4, 2.1.5, 2.1.12 to 2.1.14, 2.3.9 to 2.3.11, 2.3.19) use a second translator's voice (Ātman, Puruṣa); meaning right |
| Brihadaranyaka | 6.4.3-5, 9-11, 21-23 mula is Hume 1921 (archaic), not Madhavananda |

## F. Artifacts to strip

| Artifact | Where |
|---|---|
| Separator lines (`———`, `——o——`, `——:o:——`) | Prashna 1.16, 2.13, 3.12, 4.11, 5.7; Mundaka 1.1.9, 1.2.13, 2.1.10, 2.2.12, 3.1.10, 3.2.11; Katha 1.1.29, 1.2.25, 1.3.17, 2.1.15, 2.2.15 |
| `Com.—` prefix on bhashya english (not in the Sanskrit) | about 128 parts in Prashna and Mundaka, all Katha bhashya english, Taittiriya mid-text. Policy needed: strip everywhere or keep. Prashna 4.1 `Cow.—`, 5.1 `Com,—`; Kena 2.5 `Com:—` |
| Footnote markers `[n]` | Isa units 1, 3, 4, 8, 9, 11, 13, 15, 16, 17, 18 |
| Footnote text / colon lines | Mandukya 2.K20-27, 2.K29, 3.K33; Brihadaranyaka 1.4.17 (25 lines), 2.1.20 (8), 4.1.7 (2); Brihadaranyaka page refs `p. 118` in 17 units |
| Web-scrape junk ("Mandukya Karika, verse 2.NN: / Sanskrit text, IAST transliteration and English translation") | Mandukya 2.K20 to 2.K27 (minus K25); Mandukya 2.K28 has a header "Shankara Bhashya (commentary)" and range label "20-28." |
| Stray verse counters `(3)`, `(6)`, `(7)`, `(10)`, `(20)`, `(8)`, `(1)` | Mundaka 1.1.3, 1.1.6, 3.1.7, 2.1.10, 3.2.10; Katha 1.1.8; Prashna 6.1; Aitareya `(1)`, `(!)•`; Taittiriya 1.11.1-1.12.1 |
| Page headers in english | Aitareya 1.2, 1.3, 2.1 (twice), 3.1 (twice) |
| `Vere 4.5.6:` | Brihadaranyaka 4.5.5 |
| `(?)` OCR holes in english | Brihadaranyaka 1.4.9 (3), 1.4.10 (34), mid-word; Mundaka 1.2.12 `(preceptor?)`; Katha 1.1.3 `Nirindriah (?)` |
| Mid-sentence start | Brihadaranyaka 4.4.9, 6.4.5; Chandogya intro-1.13 |
| Residual "End of Section / Discourse" | Chandogya 1.2.1, 1.2.14, 3.18.6, intro-2.24, 2.24.16, intro-3.1, 4.17.10, 7.26.2 |
| Mundaka 2.2 numbering offset | english numbers run one behind the ref after the 2.2.7-8 merge (ref 2.2.9 says "8."); content correct |
| Missing verse-number prefix | Katha 1.1.7, 1.1.9, 1.1.10 |
| Prashna / Mandukya 2.K28 | English reordered (footnotes before commentary) |

## G. OCR and spelling typos in english

- **Aitareya, Taittiriya:** heavy; Taittiriya about 155 junk characters (`£ & ^ •`, doubled `**`), worst in 2.1.1 (20), 2.6.1 (18), 2.8.1-5 (17), 2.3.1 (11), 3.10.1-6 (11), 2.7.1 (9). Examples `BrahBan`, `A'k&sa`, `Pr&na`, `Be-verend`, `Mdhdchamasya`, `existense`, `acqtiire`.
- **Mundaka:** `sulothia` (1.2.4), `Hut`/`lie` (3.1.2), `doing nets` (3.1.4), `how` for bow (2.2.3, 2.2.4), `horn` for born (2.2.6), `blight` (2.2.7-8), `perceptor`, `Brahma n`.
- **Prashna:** `brandies` (3.6), `mot` (4.2), `good youth I` (4.7).
- **Katha:** `Vaivasvaia` (1.1.7), `thind` (1.3.7), `be gets` (1.2.6), `of taught` (1.2.8).
- **Kena:** `Sratis`, `hy`, `beard`, `on e Atman`.
- **Mandukya:** `Rut it` (1.K9), `Tn the` (1.8), `coining` (4.K88), `should he known` (1.K24), `all sentiency` (1.7).
- **Chandogya:** `mooes`, `subsubtratum`, `thesehe`, `Jis` (1.2.5).

## H. Sanskrit-side hygiene

- **Vedic anusvara `ꣳ` (U+A8F3):** Chandogya 191 units (316 occurrences); Prashna 4 lines (e.g. 2.4 `तस्मिꣳश्च`). None in Brihadaranyaka. Policy: normalise to `ं` with `clean_sanskrit_marks.py`, or keep.
- **ZWNJ/ZWJ:** Chandogya 20 units (43), Brihadaranyaka 5 units.
- **`(?)` editorial marks:** Isa 2; Kena 1.5, 4.7; Katha 1.3.12; Chandogya 12 units (1.8.7, 2.6.1, 2.20.2, 2.24.2, 3.1.1, 3.12.9, 4.2.5-4.3.1, 4.17.6, 5.2.1, 5.10.1-5.10.2, 6.8.6-6.8.7, 6.16.3); Brihadaranyaka 9 units (1.4.10, 1.5.2, 2.1.20, 3.5.1, 3.9.22, 4.5.15, 5.1.1, 5.14.1, 6.2.15).
- **Stacked citation run:** Chandogya 3.6.1 (five `(छा. उ. ...)` in a row).
- **Verse repeated inside bhashya** as a pratika: Mundaka 1.2.4 (ratio 0.6), Mandukya `अत्रैते श्लोका भवन्ति` doubled in 1.K19, 1.K24.

## I. Other works with the same family of problem (spotted while scanning)

- `sahitya/kumarasambhava.json` english has 0 full stops (104,101 chars); may be intentional for verse translation, check separately.
- All other works scanned for stripped punctuation: normal.

## J. Decisions I need from you

1. `Com.—` prefix on bhashya english: strip or keep (affects Prashna, Mundaka, Katha, Taittiriya).
2. Chandogya english: re-extract from wisdomlib Jha (recommended) or regex repair first.
3. Aitareya: clean current OCR or rebuild with verse-level pairing from history.
4. Katha and Brihadaranyaka source gaps: leave, drop from scoring, or fill from a second translation (Gambhirananda covers the 6.4 passages).
5. Taittiriya and Brihadaranyaka: split the large grouped units, or accept section-level scoring.
6. Interpretive mula english (Kena, Mandukya): leave and record, or replace with literal renderings.
7. Vedic `ꣳ`: normalise or keep.

## K. Proposed fix order

1. Mechanical shifts: Isa 9/10 and 13/14, Kena 4.6/4.7, Taittiriya 2.1.0 to 2.1.1, Chandogya 4.7.x and intro-4.16, Katha 1.3.10 (hand split), Brihadaranyaka part repartition and 16 avatarika spills.
2. Strip artifacts (section F) and Sanskrit hygiene (section H).
3. Fix the 8 clear mula translation errors in section E (Prashna 3.11, 4.8, 6.1, 1.3; Mundaka 3.2.11) and the typo passes (section G).
4. Mandukya footnote and remark cleanup (2.K20-29, 3.K33, the "This Karika..." closers, 1.8).
5. Decisions in section J, then Chandogya re-extract, Aitareya rebuild, gap-filling.
6. Final pass: LaBSE or manual sample audit on Chandogya and Brihadaranyaka to size the remaining boundary shifts; rerun `validate.py`.
