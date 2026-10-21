# Shankara bhashya audit: Katha, Taittiriya (2026-10-09)

> Snapshot: some items below have since been fixed. Check the current file and `git log` before treating an entry as open.

Files: `upanishads/katha_shankara.json` (129 units), `taittiriya_shankara.json` (64 units).
Scope: Katha, every mula translation read, every bhashya part checked by length ratio, edge alignment, scrape scan; flagged units read in full. Taittiriya, every unit checked at both edges plus length ratio and OCR-junk count. Not every bhashya sentence read. No edits made.
Companions: `shankara_isa_kena_mandukya_audit.md`, `shankara_prashna_mundaka_aitareya_audit.md`.

Status key: [ ] open, [x] fixed.

## Summary

| Work | Units | Shifts | Sanskrit with no english | English with no Sanskrit | Artifacts |
|---|---|---|---|---|---|
| Katha | 129 (120 verses) | 1.3.10 holds english of 1.3.11-12 commentary | 11 bhashya parts (about 6,000 chars) | none | separator lines in 5 units, mixed translators in 12 verses |
| Taittiriya | 64 (33 non-colophon) | 2.1.0 holds english of 2.1.1 opener | 3.3 to 3.5 and 3.1.0 mula-only | headings in 1.1.1 | OCR junk about 155 chars, `Com.` prefix |

Verse counts: Katha 29+25+17+15+15+19 = 120 (119 verses plus the closing peace invocation at 2.3.19). Taittiriya has 12+9+10 anuvakas, all present. Taittiriya is held at anuvaka level (33 non-colophon units against the 120-150 structural units in the ranking table); no verse or mantra split exists.

## Katha

### Shift
- [ ] **1.3.10 bhashya english holds the commentary of 1.3.11 and 1.3.12.** Sanskrit 700 chars, english 2,068 (ratio 3.0; normal 1.5 to 1.8). The Sanskrit comments only on `इन्द्रियेभ्यः परा ह्यर्थाः`. The english continues past it with "Than the mind ... the intellect is subtler... Oh, how deep, unfathomable and marvellous this Maya... Are not these statements inconsistent?... Agryaya, like a point... By the subtle seers". That is Sastri's translation of the commentary of 1.3.11 (`महतोऽपि परं...`) and 1.3.12 (`ननु गतिश्चेदागत्यापि भवितव्यम्...`), whose Sanskrit sits in units 1.3.11 and 1.3.12, both of which have no english. About 1,350 chars to move; the commentary of 1.3.11 and 1.3.12 needs splitting by hand.

### Sanskrit with no english (bhashya part)
- [ ] 1.3.11 (711 chars), 1.3.12 (1,313), 2.1.4 (311), 2.1.5 (406), 2.1.12 (296), 2.1.13 (370), 2.1.14 (303), 2.3.9 (540), 2.3.10 (343), 2.3.11 (677), 2.3.19 (713). Total about 6,000 chars. File notes list these as the 12 units where the source gives verse only (1.1.10 is the twelfth and its commentary english is present, so only 11 have a gap). Source gap, not a pairing error. Options: leave and drop the bhashya Sanskrit from scoring, or find a second translation.
- [ ] **Mixed translator voice** in those same verses. The mula english of 1.3.11, 1.3.12, 2.1.4, 2.1.5, 2.1.12, 2.1.13, 2.1.14, 2.3.9, 2.3.10, 2.3.11 and 2.3.19 uses Atman, Puruṣa, "That" with diacritics, while the other 109 units use Sastri's plain "atman, Purusha". Probably from a second translation (Radhakrishnan or Gambhirananda style). Meaning is right; the voice differs. Record the source in `meta.english_source` or unify.

### Artifacts
- [ ] **Separator line `———`** at the end of bhashya english: 1.1.29, 1.2.25, 1.3.17, 2.1.15, 2.2.15. Strip.
- [ ] **Query marks** from OCR: `Nirindriah (?)` in 1.1.3 bhashya english; `(?)` also sits in Sanskrit bhashya of 1.3.12 (`अनध्वगा अध्वसु पारयिष्णवः’(?)`).
- [ ] **`Com.` prefix** on every bhashya english (Sastri's layout, not in the Sanskrit). Same policy question as Prashna and Mundaka.
- [ ] **Missing verse-number prefix** in mula english: 1.1.7, 1.1.9, 1.1.10 (all other Sastri verses carry `N.`). Also stray `(8)` after 1.1.8. Cosmetic.
- [ ] **OCR typos** in mula english: "Vaivasvaia" (1.1.7), "thind" (1.3.7), "be gets" (1.2.6), "of taught" (1.2.8), "Nachiketa" vs "Nachiketas" mixed, "ascertained".

### Checked and fine
- 109 other mula translations read against the verse; no content mismatches found. 2.3.19 is the closing peace invocation (`सह नाववतु`), carrying the right english.
- Ratios 0.8 to 0.9 for 1.1.10, 1.1.11, 1.1.13, 1.1.14, 2.1.3 look low, but each is a short, direct gloss and the english covers it. No action.

## Taittiriya

### Shift
- [ ] **2.1.0 english holds the opener of 2.1.1.** 2.1.0 Sanskrit is the peace invocation (803 chars); english is 3,132 (ratio 3.9). From `" The knower of Brahman reaches the highest etc. The utility of this knowledge of Brahman is the destruction of ignorance...` to `...becomes Brahman himself etc.` (about 1,400 chars) translates the first paragraph of 2.1.1 bhashya (`ब्रह्मविदाप्नोति परमित्यादि। प्रयोजनं चास्या ब्रह्मविद्याया अविद्यानिवृत्तिः...` to `...परं ब्रह्म वेद ब्रह्मैव भवति`). The 2.1.1 english starts at the mantra translation and lacks it. Move the tail to 2.1.1, placing it after the mantra block.

### Missing or thin
- [ ] **3.3.1, 3.4.1, 3.5.1 are mula-only** (277 / 264 / 285 chars, english 424 / 417 / 424). The Bhrigu Valli sections for prana, mind and knowledge. Sharada carries no bhashya for them and english is verse only, so they are consistent. Worth confirming Shankara's own comment ("पूर्ववत्" style) is not in the Sanskrit source elsewhere.
- [ ] **3.1.0** is the peace invocation, mula only.
- [ ] **Granularity.** Chapters 1.3-1.6, 1.11-1.12, 2.8, 3.10 are single multi-mantra units (`1.3.1-4`, `1.4.1-3`, `1.5.1-3`, `1.6.1-2`, `1.11.1-1.12.1`, `2.8.1-5`, `3.10.1-6`). The english interleaves mantra and commentary; the Sanskrit lists mantras then commentary (file notes). Units are 2,500 to 14,000 chars, too coarse for line-level scoring. Splitting needs a manual pass per chapter.
- [ ] **1.1.1 english opens** with `Om 7a£ &a£. Adoration to Brahman.` (OCR of the opening heading, no Sanskrit counterpart).

### OCR junk (Sastri 1903 text layer)
- [ ] About 155 junk characters (`£ & ^ • |`, doubled `**`, `J` before a capital) across the english, worst in 2.1.1 (20), 2.6.1 (18), 2.8.1-5 (17), 2.3.1 (11), 3.10.1-6 (11), 2.7.1 (9). Examples: `BrahBan`, `A'k&sa`, `Pr&na`, `Be-verend`, `Mdhdchamasya`, `Vydhritis^`, `existense`, `acqtiire`, `Sannomitra`, `CW` for Om, `n` for `ṃ`.
- [ ] Quotation marks degraded: `' 5`, `"*`, `u` and `**` for opening and closing quotes; verse counters left in text (`(1)` in 1.11.1-1.12.1).
- [ ] `Com. —` appears in the middle of the text in 2.1.0, 2.3.1, 2.6.1, 2.7.1, 2.8.1-5, 3.10.1-6, 1.11.1-1.12.1 (Sastri's heading between mantra and commentary).
- [ ] Sanskrit side is clean (`noise` below 5 per unit).

### Checked and fine
- All 33 non-colophon units: first and last english lines match first and last Sanskrit content, except the 2.1.0/2.1.1 shift above.
- Length ratios 1.3 to 2.1 throughout (outside 2.1.0).
- 31 colophon units carry formulaic english documented in `meta.english_source`.

## Proposed order
1. Fix the two shifts: Katha 1.3.10 (split between 1.3.10, 1.3.11, 1.3.12), Taittiriya 2.1.0 to 2.1.1.
2. Strip artifacts: separator lines (Katha 5), `Com.` prefix policy, `(?)`, verse counters, OCR junk (Taittiriya regex pass for `£&^•|` and doubled stars, then hand-fix the named typos).
3. Decide the Katha gap: leave 11 bhashya parts without english, or look for a second Shankara-bhashya translation (Gambhirananda or Sastri's printed book).
4. Decide Taittiriya granularity: split the seven grouped chapters, or accept anuvaka-level scoring.
5. Normalise Katha mula voice (Sastri vs the second translator) via `meta.english_source`.

## Method notes
- Katha parts carry `mula` and `bhashya`; Taittiriya english is unit-level only (no english on the parts), as file notes say.
- Edge check: first and last Sanskrit line against first and last english line, plus length ratio per part. The Katha shift was the only ratio outlier above 2.4 with matching english continuing past the Sanskrit.
