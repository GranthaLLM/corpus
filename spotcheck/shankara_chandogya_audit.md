# Shankara bhashya audit: Chandogya (2026-10-09)

> Snapshot: some items below have since been fixed. Check the current file and `git log` before treating an entry as open.

File: `upanishads/chandogya_shankara.json` (760 units; 250 verse, 241 prose mula+commentary, 167 commentary, 35+2 group, 65 mula-only; 432K chars Sanskrit, 757K chars english).
English: Jha (Mitrasamgraha GV05chupsau), joined onto Sharada units by Sanskrit anchors. English sits on the unit; the 1,054 parts hold Sanskrit only (2 parts have english).
Scope: whole file scanned by length ratio, adjacent-pair ratio anomalies, name-lexicon shift check (35 proper names), boundary and artifact regexes, punctuation and spacing profile. Flagged units read in full. Semantic mid-unit alignment was not read unit by unit (760 units; no LaBSE venv on this machine). No edits made.
Companions: `shankara_isa_kena_mandukya_audit.md`, `shankara_prashna_mundaka_aitareya_audit.md`, `shankara_katha_taittiriya_audit.md`.

Status key: [ ] open, [x] fixed.

## Summary

Alignment is good. Length ratio median 1.66 (sd 0.21 in log), only 6 units outside 0.9 to 2.8, only 4 adjacent-pair spill signals, and the proper-name check found 20 cases, mostly legitimate pronoun resolution.
The real defect is the english text itself: the Jha source rows have lost punctuation and glued words. This is the largest single quality problem seen so far across the Shankara tracks.

## 1. English text damage (whole file)

Measured over 749,606 chars of english in non-colophon units:

| Defect | Count | Units hit |
|---|---|---|
| Full stops `.` | 29 in total (expected about 30,000) | 152 units have any |
| Standalone pronoun `I` | 0 (every "I" deleted) | all |
| Comma with no following space (`,as`, `,the`) | 2,603 | 474 |
| Semicolon with no following space | 700 | 289 |
| Fused lower+Upper words (`thesehe`, `AnswerWater`, `youBeing`) | 170 | 126 |
| `Answer`, `Question`, `Objection` glued to next word | 155 | 71 |
| `i.e.` as `ie`, `etc.` as `etc` | 344 / 337 | many |
| Hyphenated compounds fused (`goodsmelling`, `twolegged`, `fourfactored`, `wellknown`) | many | many |
| Lone-quote spacing (`‘ turn to`) | 112 | 53 |

Effect on meaning: "if drank this water, would be drinking what is contaminated" (1.10.3), "what meant to say" (3.15.6), "Yes, Sir would declare to thee" (4.7.2), "when did not find you" (1.11.2), "if had said so to you" (1.11.5). Dozens of sentences read as ungrammatical and a scorer or judge will treat them as wrong. The pre-merge revision `af8dedf` already had 0 periods and 0 "I", so the loss is in the Jha rows as extracted, not in later cleanup.

- [ ] Re-extract english from the wisdomlib edition of Jha (already used for intro-1.1, intro-3.16, intro-4.10) or from the original PDF and re-join with the existing anchor tool (`tools/merge_chandogya.py`). This is the fix.
- [ ] Interim repair if re-extraction is not possible: restore "I" before verbs where a pronoun is clearly missing (regex list of about 181 sites matched), restore space after `,` and `;`, split fused words at lower-to-upper boundaries, restore `i.e.`. Sentence-final periods cannot be restored reliably this way.
- Other works checked with the same profile: only `sahitya/kumarasambhava.json` shows 0 periods (104K chars, poetry, check separately). All other works are normal.

## 2. Shifted or truncated english

- [ ] **4.7.1 / 4.7.2 / 4.7.3 (worst, already named in file notes).**
  - 4.7.1 (Sanskrit 153 chars, verse only) carries english of 378 chars. Its tail ("Agni said to him 'The flamingo will declare to thee the other foot'; and having said this, he kept quiet. On the morrow etc, etc, just as before") translates the commentary that sits in the Sanskrit of 4.7.2 (`सोऽग्निः हंसः ते पादं वक्तेत्युक्त्वा उपरराम... स ह श्वोभूते इत्यादि समानम्`).
  - 4.7.2 english ends "...He answered 'Yes, Sir would declare to thee, my Boy, the foot of Brahman'". The last clause is the start of the verse in 4.7.3 (`ब्रह्मणः सोम्य ते पादं ब्रवाणीति`); the 4.7.3 english then starts at "Do tell it to me".
  - Ratios: 4.7.1 2.5, 4.7.2 0.64.
- [ ] **intro-4.16** english is 61 chars: "The next section is introduced now, for the following reasons". The reasons themselves are not translated; the Sanskrit (157 chars) states them (`रहस्यप्रकरणे प्रसङ्गात्... मौनमित्यत इदमारभ्यते`). Truncated at a Jha row edge.
- [ ] **1.10.3** english repeats itself ("Give me of these... said" twice): the verse translation and the commentary translation are both present, but the verse text is duplicated in a second paraphrase. Ratio 0.89.
- [ ] **3.15.6, 4.17.1, 3.6.1** have low ratios (0.65, 0.68, 0.82). 3.15.6 and 4.17.1 translate the verse and the commentary is a short restatement, so likely complete; 3.6.1 english omits the middle of the commentary (the five stacked citations `(छा. उ. ३ । १ । ३) (छा. उ. ३ । २ । २)...` are one run of references). Read before touching.
- [ ] **Name-lexicon hits worth reading:** 1.8.8 and 1.12.2 (Dalbhya), 1.10.3 / 1.11.5 (Usasti), 4.1.2 (Janasruti), 5.3.2 (Pravahana), 5.17.1 (Uddalaka, name found in next unit's Sanskrit), 8.9.1 (Virocana), intro-6.1 / 6.8.4 (Svetaketu), 4.16.5-intro-4.17 and 4.17.1 (Prajapati). Most are likely the translator naming the speaker; 5.17.1, 8.9.1, 4.17.1 and intro-6.1 are the ones where the name sits in the neighbouring unit and a shift is possible.
- [ ] File notes list about 100 boundary-shifted units as "still open". The whole-file pair-ratio check finds only 4 pairs, so most of those are sub-sentence shifts inside the tolerance of the unit ratio; they need a sentence-level pass after the english is re-extracted.

## 3. Coverage

- 0 units with null english. Colophons: 149 carry formulaic english (documented). intro-3.19 has no source translation and was dropped.
- 3.9.2 to 3.10.4 have english only through merged units `3.9.1-3.9.4` and `3.10.1-3.10.4` (Jha translates them as one passage).
- intro-1.1 is partly translated: ratio 2.7 because english covers the whole intro while the Sanskrit was trimmed at the etymology (see file notes).
- intro-5.1 (500 / 1,389) and intro-8.1 (1,040 / 2,754) have ratio 2.5 to 2.6; the english carries Jha's section synopsis. Check against Sanskrit.

## 4. Sanskrit side

- [ ] **Vedic anusvara `ꣳ` (U+A8F3)** in 191 units (316 occurrences), e.g. `हꣳस`, `तꣳ ह`. Same normalisation question as Prashna.
- [ ] **ZWNJ/ZWJ** characters in 20 units (43 occurrences), e.g. `व्रजन्‌रथो`. Strip with `clean_sanskrit_marks.py`.
- [ ] **`(?)`** editorial marks in 12 units: 1.8.7, 2.6.1, 2.20.2, 2.24.2, 3.1.1, 3.12.9, 4.2.5-4.3.1, 4.17.6, 5.2.1, 5.10.1-5.10.2, 6.8.6-6.8.7, 6.16.3.
- [ ] **Stacked citation run** in 3.6.1 (`(छा. उ. ३ । १ । ३) (छा. उ. ३ । २ । २) ... (छा. उ. ३ । ५ । २)`). Source artifact; collapse to one.
- No Latin script in Sanskrit.

## 5. Other artifacts in english

- "End of Section / Discourse" fragments remain in 1.2.1, 3.18.6, intro-2.24, 2.24.16, intro-3.1, 4.17.10, 7.26.2 (file notes say they were stripped; 7 got through).
- 1.2.14 english ends "...described below End of the Section Khaṇḍa ii of Discourse Adhyāya".
- Typo seen: "mooes" (moves), "subsubtratum", "thesehe", "Jis" in 1.2.5.
- intro-1.13 english begins lowercase (mid-sentence).
- Merged-unit text order (mula, comment, next mula, next comment) is documented; english and Sanskrit both follow it.

## Proposed order
1. Decide how to repair the english text (section 1): re-extract from wisdomlib or the PDF (recommended), or regex repair.
2. Fix 4.7.1/4.7.2/4.7.3 and intro-4.16 by hand.
3. Read the six name-lexicon candidates in section 2.
4. Sanskrit hygiene pass: `ꣳ` policy, ZWNJ, `(?)`, 3.6.1 citations.
5. Strip the seven residual "End of Section/Discourse" fragments.
6. After the text is clean, run the sentence-level boundary pass (LaBSE or a manual sample) to size the remaining ~100 shifted units.

## Method notes
- Ratio profile: median english/Sanskrit 1.66 (p10 1.32, p90 2.06), log sd 0.21. Pair-spill rule: adjacent units with opposite-sign z above 1.4 and Sanskrit above 100 chars.
- Name lexicon: 35 Sanskrit proper names against ASCII-folded english. A hit requires the name in the english of unit i but not in the Sanskrit of i, with the name present in the Sanskrit of i-1 or i+1 (or the reverse).
- Rewrite JSON with indent=1 (`tools/common.write`).
