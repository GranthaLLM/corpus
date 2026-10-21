# Shankara bhashya audit: Isa, Kena, Mandukya (2026-10-09)

> Snapshot: some items below have since been fixed. Check the current file and `git log` before treating an entry as open.

Files: `upanishads/isa_shankara.json`, `kena_shankara.json`, `mandukya_shankara.json`.
Scope of check: Isa and Kena read at unit edges (every unit). Mandukya (225 units) checked by length ratio, footnote and scrape scan, plus about 40 flagged units read in full. Not every karika read. No edits made.

Status key: [ ] open, [x] fixed.

## Summary

| Work | Units | Shifted english | English with no Sanskrit | Sanskrit with no english | Artifacts |
|---|---|---|---|---|---|
| Isa | 20 | 9/10, 13/14, 2, 3 | 18 (about 2,700 chars) | 9 preamble (about 1,700 chars) | `[n]` markers in 12 units, `(?)` in Sanskrit of 2 |
| Kena | 40 | 4.6/4.7 | intro-1 header | none | "Com:" in 2.5 |
| Mandukya | 225 | none found | 2.K20-27 footnotes, translator remarks in about 15 units | 1.2 opener, 1.K24 colophon line | scrape lines in 8 units, OCR typos |

## Isa

- [ ] **9 / 10 shift.** 9 bhashya Sanskrit is 2,288 chars, english 922. The english tail ("Now follows a statement of the distinction between the respective fruits...") translates the opener of 10 (`तत्रावान्तरफलभेदं विद्याकर्मणोः...`). 10 english starts at "anyat-eva=". Move the tail to 10. The 9 preamble (`अत्राद्येन मन्त्रेण सर्वैषणापरित्यागेन...` to `...न्यायतः शास्त्रतो वा तदिहोच्यते...`) then has no english: park or find source.
- [ ] **13 / 14 shift.** english tail of 13 ("Since this is so, it is but right that meditation on both the effect and the cause...") translates the opener of 14 (`यत एवम्, अतः समुच्चयः...`). Move to 14.
- [ ] **2 opener.** Sanskrit `एवमात्मविदः पुत्राद्येषणात्रयसंन्यासेन...` has no english (english starts at "Kurvanneva=").
- [ ] **3 opener.** Sanskrit `अथेदानीमविद्वन्निन्दार्थोऽयं मन्त्र आरभ्यते` has no english.
- [ ] **18 extra english.** bhashya english 3,408 chars vs Sanskrit 632. From "Some entertain a doubt..." to "as we have explained" (about 2,700 chars) has no Sanskrit. Hiriyanna's vidya/avidya discussion; Sharada edition lacks it. Cut from unit or move to `meta`.
- [ ] **Footnote markers `[1]`..`[17]`** left in english of units 1, 3, 4, 8, 9, 11, 13, 15, 16, 17, 18.
- [ ] **`(?)` in Sanskrit** of 2 (two places, in the Taittiriya Aranyaka and Mokshadharma quotes). Source edition marks.
- [ ] 15 english says "verse 9" for `आत्मैवाभूद्विजानतः` (that is verse 7). Source error by translator; note only.
- Translation choices (no fix needed, record): 8 `परिभूः` as "superposed"; 12 and 13 `सम्भूति/असम्भूति` as "manifest/unmanifest".

## Kena

- [ ] **4.6 / 4.7 shift.** english tail of 4.6 ("Thus instructed, the disciple addressed the preceptor in the following manner.") translates the opener of 4.7 (`एवमनुशिष्टः शिष्य आचार्यमुवाच`). 4.7 english then starts "When the disciple said...", so the sentence appears twice. Remove from 4.6.
- [ ] **intro-1 header.** english opens "ADORATION TO THE BRAHMAN. OM TAT SAT." with no Sanskrit counterpart.
- [ ] **2.5** english begins "Com:--". Strip.
- [ ] **Interpretive mula english** (translation carries Sastri's gloss, not the mantra): 1.2 "Being disabused of the false notion" for `अतिमुच्य`; 2.4 "known well, when it is known as the witness of every state of consciousness"; 4.4 and 4.5 paraphrase ("as speedily as the mind goes to Brahman..."); 3.9, 3.10 `आददीय` as "blow away" (Shankara glosses `गृह्णीयाम्`, take); 4.9 `स्वर्गे लोके` as "blissful Brahman". Decide: leave and record, or replace with a literal rendering.
- [ ] Source typos: "Sratis", "hy" (by), "beard" (heard), "on e Atman" (2.5 mula).
- Numbering: Sharada has 35 units (1.1-1.9, 2.1-2.5, 3.1-3.12, 4.1-4.9), Sastri counts 34. Already handled in file notes (1.3/1.4).

## Mandukya

### Commentary with no Sanskrit
- [ ] **2.K20 to 2.K27 (minus K25).** `bhashya` part has english only (1,219 / 1,106 / 1,280 / 1,030 / 352 / 731 / 442 chars). Content is Nikhilananda's numbered footnotes ("1 Those--e.g., the Vaisheshikas..."), not Shankara. Each also ends with scrape junk: "Mandukya Karika, verse 2.NN: / Sanskrit text, IAST transliteration and English translation". Fix: drop these parts or move to `meta`; strip scrape lines.
- [ ] **2.K25** has no commentary english at all (unit has only mula).
- [ ] **2.K28** bhashya english order is jumbled: footnotes first, then header "Shankara Bhashya (commentary)", then "20-28." range label, then the real translation. Reorder, strip header and label, drop footnotes.
- [ ] **2.K29, 3.K33** footnotes mixed into english (2.K29: three; 3.K33: two).

### Translator's own remarks inside bhashya english
- [ ] "This Karika ..." closers: 2.K5, 3.K6, 3.K16, 3.K17, 3.K31, 3.K41, 4.K28, 4.K30, 4.K37, 4.K83, 4.K90, 4.K92. Also trailing explanatory paragraphs in 3.K18, 4.K12, 4.K40, 4.K77, 4.K84, 4.K87, 4.K89 (check each: some may be Shankara's own text translated, verify against Sanskrit tail before cutting).
- [ ] **1.8** paragraphs 3 and 4 ("In the first Upanisad it is said..." and "The Highest Truth as explained above...") are Nikhilananda's introduction, not in Sanskrit.
- Length-ratio outliers (english/Sanskrit over 4): 1.8, 2.K28, 2.K29, 3.K41, 4.K6. Normal is about 2.

### Sanskrit with no english
- [ ] **1.2** first about 480 chars of bhashya (`अभिधानाभिधेययोरेकत्वेऽपि...` to `...ब्रह्म प्रतिपद्येत।`) untranslated; english starts at the matching `तदाह -- सर्वं ह्येतद्ब्रह्म`. Ratio 1.09 is the tell.
- [ ] **1.K24** `इति माण्डूक्योपनिषत्समाप्ता ॥` at top of bhashya has no english.
- Mula only, no commentary in corpus: 1.K3, 1.K4, 4.K7 (check whether Sharada has commentary).

### Mantra-level style
- Nikhilananda's mula english carries long bracketed expansions: over 3x Sanskrit length in 1.K9, 2.K8, 3.K3, 3.K12, 4.K44, 4.K86, 4.K87, 4.K88 and more (35 units total with ratio over 3). Style mismatch, not wrong. Matters for exact-translation scoring. Decide policy.
- [ ] OCR typos: "Rut it" (1.K9 mula), "Tn the" (1.8 bhashya), "coining" for coming (4.K88 mula), "should he known" (1.K24 mula), "all sentiency" (1.7).
- Parked range units still merged: 2.K9-10, 4.K31-32, 4.K51-52, 4.K61-62, 4.K65-66, 4.K68-70.

## Proposed order
1. Isa shifts (9/10, 13/14), Kena 4.6/4.7: small, mechanical.
2. Strip artifacts: Isa `[n]`, Kena "Com:" and header, Mandukya scrape lines and typos.
3. Mandukya 2.K20-27 footnote parts, 2.K28 reorder, 2.K29 and 3.K33 footnotes.
4. Trim translator remarks (per-unit check against Sanskrit tail).
5. Decide: Isa 18 extra, Isa 9 preamble, Mandukya 1.2 opener, interpretive mula english policy.

## Method notes
- Layout: `parts` = mula + bhashya per unit; bhashya Sanskrit lines map to english paragraphs, so line counts and first/last lines make shifts visible.
- No LaBSE venv found in current scratchpad; alignment judged by reading and length ratios only.
- Rewrite JSON with indent=1 (`tools/common.write`).
