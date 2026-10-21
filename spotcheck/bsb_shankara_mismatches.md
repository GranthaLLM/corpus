# bsb_shankara: Sanskrit/English unit mismatches

> Snapshot: some items below have since been fixed. Check the current file and `git log` before treating an entry as open.

Method: read all 566 units (sutra line vs English head/tail), regex for Gambhirananda "Topic N" headers, length ratio outliers. Sutra translation at the head of each unit matches its sutra in every unit except those in A. LaBSE is useless on this Sanskrit (median cosine 0.13), so the audit is by reading.

## A. Head wrong: sutra translation missing or boundary cut
- 1.1.20 (starts "Topic 7... Doubt", sutra translation absent; english 0.5x of Sanskrit)
- 1.2.5 (Sanskrit lacks the sutra line; English starts with commentary, no sutra translation)
- 1.2.6 (English starts mid-sentence ", where a limit is set..."; tail of 1.2.5 commentary cut off)
- 3.1.1, 4.1.1, 4.3.1, 4.4.1 (start "Doubt"/"Opponent", no sutra translation; sits in tail of previous unit or lost)

## B. Tail spill: English ends with the next unit's topic header and sutra translation
1.1.4, 1.1.23, 1.3.9, 2.1.12, 2.1.25, 2.1.31, 2.3.7, 2.3.9, 2.3.13, 2.3.17, 2.4.7, 2.4.8, 3.1.23, 3.2.10, 3.3.28, 3.3.30, 3.3.42, 3.3.52, 3.3.56, 3.3.57, 3.3.58, 3.3.59, 3.4.25, 3.4.42, 4.1.3, 4.1.6, 4.1.13, 4.2.3, 4.3.1, 4.3.14, 4.4.3

## C. Mid-unit spill: English holds translation of the next unit's opening Sanskrit (english 3-8x Sanskrit)
- 4.4.7 (Topic 4 + Doubt = 4.4.8 opening; 4.4.8 English lacks it)
- 3.3.48 (Opponent paragraph = 3.3.49 "ननु लिङ्गमपि..."; Sanskrit 135 chars vs English 681)
- 1.1.21 (Topic 8: SPACE block, = 1.1.22 opening)
- 2.2.36, 2.4.4, 3.4.25, 3.4.31, 4.1.5, 4.1.11, 4.1.17, 4.2.6, 4.2.20, 4.3.3, 1.1.3
- 1.2.7 ("Topic 8: SPACE" at 5%, topic 8 header already used in 1.1.21; wrong or duplicated header)

## D. Length ratio outliers, unchecked
- English short (Sanskrit longer): 3.3.21 (0.42x), 3.1.21, 3.1.27
- English long: 4.4.7, 1.1.21, 1.2.6, 4.1.17, 2.2.36, 3.4.31, 3.3.48, 4.3.3, 1.2.7, 1.1.3 (all in C)

## E. OCR junk not a mismatch but nearby
Many tails end in garbled Devanagari OCR ("aRgs", "qq;q", "ftfo ll^ll") = Gambhirananda's printed Sanskrit of next sutra. Strip when fixing B.
