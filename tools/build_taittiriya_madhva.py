import re, json, difflib
from common import *
from setu import blocks, block_text
from build_upanishads import SETU, SETU_LIC

DEVRE = re.compile("[ऀ-ॿ]")
STRIP = re.compile(r"[^ऀ-ॿ]|[।॥ऽ॒॑᳚॓॔०-९ः‌‍ँं]")

# Setutila block runs (mula run, bhashya run) -> group label, used only to name refs
GROUPS = [
    ("1.1", (1, 4)), ("1.2-4", (6, 17)), ("1.5-7", (18, 30)), ("1.8", (31, 32)), ("1.9", (33, 43)), ("1.10", (44, 45)),
    ("1.11-12", (46, 51)), ("2.1-9", (54, 82)), ("3.1-10", (84, 109)),
]


def norm(s):
    return STRIP.sub("", s or "")


def tri(s):
    return {s[i:i + 3] for i in range(len(s) - 2)}


def sections(md):
    md = md.replace("<!--PAGEBREAK-->", "\n").replace("\n---\n", "\n")
    parts = re.split(r"^##\s+(.*)$", md, flags=re.M)
    return [(parts[i].strip(), parts[i + 1].strip()) for i in range(1, len(parts) - 1, 2)]


def items(md):
    out, secs = [], sections(md)
    for k, (h, body) in enumerate(secs):
        hl = h.lower().rstrip(":").strip()
        if hl.startswith("further"):
            continue
        if DEVRE.search(h) and ("मन्त्र" in h) and k + 1 < len(secs) and secs[k + 1][0].lower().startswith("hymn"):
            out.append(("mula", body, secs[k + 1][1]))
            continue
        if hl.startswith("upanishad") or hl.startswith("bhashya"):
            kind = "mula" if hl.startswith("upanishad") else "bhashya"
            starts = [m.start() for m in re.finditer(r"“(?=\s*[ऀ-ॿ])", body)]
            if not starts:
                continue
            for a, b in zip(starts, starts[1:] + [len(body)]):
                seg = body[a:b]
                m = re.match(r"“([^”]*)”\s*[–\--]?\s*(.*)$", seg, re.S)
                if not m:
                    continue
                en = re.sub(r"\s+", " ", m.group(2)).strip()
                out.append((kind, m.group(1), en or None))
    return out


def main():
    md = (RAW / "sonde_taitt_ocr.md").read_text(encoding="utf-8")
    t, c = blocks(RAW / "set_taittiriya_bhashya.json")
    B = []
    for i, b in enumerate(c):
        if b["content_type"] in ("Mula", "Sarvamula"):
            B.append((i, b["content_type"], block_text(b)))
    its = items(md)
    idx = {B[k][0]: k for k in range(len(B))}
    NB = [norm(B[k][2]) for k in range(len(B))]
    TB = [tri(x) for x in NB]
    spans = []
    assign = []
    for n_, (kind, dev, en) in enumerate(its):
        want = "Mula" if kind == "mula" else "Sarvamula"
        nd = norm(dev)
        if len(nd) < 12 or not en:
            continue
        td = tri(nd)
        top = sorted(((len(td & TB[k]) / max(1, len(td)), k) for k in range(len(B)) if B[k][1] == want), reverse=True)[:6]
        starts = set()
        for _, k in top:
            for d in range(0, 4):
                if k - d >= 0:
                    starts.add(k - d)
        best = None
        for k in sorted(starts):
            if B[k][1] != want:
                continue
            txt = ""
            for ln in range(1, 5):
                if k + ln > len(B) or B[k + ln - 1][1] != want:
                    break
                txt += NB[k + ln - 1]
                if len(tri(nd) & tri(txt)) < 0.2 * len(td):
                    continue
                sm = difflib.SequenceMatcher(None, nd[:2000], txt[:5000], autojunk=False)
                cov = sum(mb.size for mb in sm.get_matching_blocks()) / max(1, min(len(nd), 2000))
                if best is None or cov > best[0] + 0.03 or (abs(cov - best[0]) <= 0.03 and ln < best[2]):
                    best = (cov, k, ln)
        if best and best[0] >= 0.55:
            spans.append((best[1], best[1] + best[2] - 1, n_, en, round(best[0], 2)))
            assign.append(best)
    spans.sort()
    merged = []
    for a_, b_, n_, en, cov in spans:
        if merged and a_ <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b_)
            merged[-1][2].append((n_, en, cov))
        else:
            merged.append([a_, b_, [(n_, en, cov)]])
    label = lambda bi: next((g for g, (a, b) in GROUPS if a <= bi <= b), "?")
    units, k = [], 0
    mi = {m[0]: m for m in merged}
    while k < len(B):
        if k in mi:
            _, e_, its_ = mi[k]
            blk = B[k:e_ + 1]
            units.append({"ref": f"{label(blk[0][0])}#{blk[0][0]}" + (f"-{blk[-1][0]}" if e_ > k else ""),
                          "kind": "mula" if blk[0][1] == "Mula" else "bhashya", "sanskrit": "\n".join(x[2] for x in blk),
                          "english": "\n".join(e for _, e, _ in sorted(its_)), "match": [c for _, _, c in sorted(its_)]})
            k = e_ + 1
        else:
            units.append({"ref": f"{label(B[k][0])}#{B[k][0]}", "kind": "mula" if B[k][1] == "Mula" else "bhashya",
                          "sanskrit": B[k][2], "english": None, "match": None})
            k += 1
    return units, len(its), assign


def write_file():
    units, n_items, assign = main()
    out = []
    for u in units:
        mn = min(u["match"]) if u["match"] else None
        out.append({"ref": u["ref"], "kind": u["kind"], "sanskrit": u["sanskrit"], "english": u["english"], "match_min": mn})
    with_en = sum(1 for u in out if u["english"])
    mins = [u["match_min"] for u in out if u["match_min"] is not None]
    write("upanishads/taittiriya_madhva.json", dict(
        id="taittiriya_madhva", text="Taittirīya Upaniṣad Madhvabhāṣya", tradition="Dvaita", commentator="Madhva", script="Devanagari", units=out,
        source_sanskrit={"citation": "Setutila/Sarvamula taittiriya_bhashya.json (colophon: Anandatirtha Bhagavatpada's Taittiriya Upanishad Bhashya, i.e. Madhva)", "url": SETU + "taittiriya_bhashya.json", "license": SETU_LIC},
        source_english={"citation": "Nagesh D. Sonde, Sri Madhvacharya Bhashya on Taittiriya Upanishad, with explanatory notes; pages 11-58 re-OCR'd with Sarvam Vision (sa-IN) because the PDF's own Sanskrit is a garbled legacy font", "url": "https://nageshsonde.com/images/Sri-Madhvachachaarya-Bhashya-On-Taittiriya-Upanishad.pdf", "license": "Author states: not protected by copyright, free for copying"},
        bundled=False, needs_ocr=True, alignment="by_ref",
        notes=(f"Setutila's file is Madhva's bhashya (its colophon names Anandatirtha). English is Sonde's translation from the Sarvam Vision OCR of the PDF, which recovers the Devanagari of every quoted mantra and bhashya passage. "
               f"Each Sonde quote (Devanagari + English) was matched to the Setutila block or run of consecutive same-type blocks whose text it covers (character-level alignment, coverage >= 0.55; adjacent quotes hitting overlapping blocks are merged); {n_items} Sonde quotes found, {len(assign)} matched, {with_en} of {len(out)} units have English, minimum coverage {min(mins):.2f}, median {sorted(mins)[len(mins)//2]:.2f}. "
               "kind = mula (mantra text, Upanishad sections of Sonde) or bhashya (Madhva's commentary, Bhashya sections); the unit's english translates exactly its sanskrit. ref = group label (Sikshavalli anuvakas etc.) + '#' + Setutila block index(es); match_min = lowest alignment coverage among the quotes merged into the unit. "
               "Sonde's 'Further Explanation' notes are his own commentary and are excluded. Units without English: the repeated peace chants Sonde does not restate and a few short bhashya fragments whose quotes were absorbed into neighbours' translations. OCR errors possible in both scripts (e.g. मनोमय, वह्म for ब्रह्म). First pass.")))
    print(len(out), with_en)


if __name__ == "__main__":
    write_file()
