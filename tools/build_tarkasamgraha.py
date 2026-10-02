import re
from common import *

DEV = str.maketrans("०१२३४५६७८९", "0123456789")
MULA_END = re.compile(r"॥\s*([०-९]{1,3})\s*॥\s*$")
MULA_LOOSE = re.compile(r"॥\s*\S{1,4}\s*॥\s*$")


def paras():
    md = (RAW / "tarka_ocr.md").read_text(encoding="utf-8").replace("<!--PAGEBREAK-->", "\n")
    out = []
    for blk in re.split(r"\n\s*\n", md):
        b = blk.strip()
        if not b or b == "---":
            continue
        b = re.sub(r"^#+\s*", "", b)
        b = re.sub(r"^---\s*", "", b).strip()
        if b:
            out.append(b)
    return out


def sections():
    P = paras()
    secs, cur, last = {}, None, 0
    english = {}
    for b in P:
        m = re.match(r"^\[\^\d+\]:\s*(\d+)\.\s*(.*)$", b, re.S)
        if m:
            english[int(m.group(1))] = re.sub(r"\s+", " ", m.group(2)).strip()
            continue
        m = re.match(r"^(\d+)\.\s*['‘’“\"](.*)$", b, re.S)
        if m and not re.search(r"[ऀ-ॿ]", b[:40]):
            english.setdefault(int(m.group(1)), re.sub(r"\s+", " ", b[len(m.group(1)) + 1:]).strip())
            continue
        if not re.search(r"[ऀ-ॿ]", b) or len(b) < 6:
            continue
        mm = MULA_END.search(b)
        if mm:
            n = int(mm.group(1).translate(DEV))
            if n <= last:
                continue
            last = n
            body = re.sub(r"\s+", " ", b.replace("-\n", "")).strip()
            cut = body[:mm.start() if mm.start() < len(body) else len(body)]
            k = body.rfind("॥", 0, body.rfind("॥", 0, len(body) - 1) - 0) if False else -1
            marker = MULA_END.search(body)
            pre = body[:marker.start()].rstrip()
            k = pre.rfind("॥")
            if k != -1 and cur is not None:
                cur["dipika"].append(pre[:k + 1].strip())
                mula = (pre[k + 1:].strip() + " " + body[marker.start():]).strip()
            else:
                mula = body
            cur = {"n": n, "mula": mula, "dipika": []}
            secs[n] = cur
        elif cur is not None and len(b) > 40:
            if re.search(r"(\. ?){3,}|\.\. \.\.", b):
                cur = None
                continue
            cur["dipika"].append(re.sub(r"\s+", " ", b.replace("-\n", "")).strip())
    return secs, english


def main():
    secs, english = sections()
    globals()['secs'] = secs
    units = []
    for n in sorted(secs):
        if n > 70:
            continue
        s = secs[n]
        units.append({"ref": str(n), "kind": "mula", "sanskrit": s["mula"], "english": english.get(n)})
    missing_en = [u["ref"] for u in units if not u["english"]]
    write("philosophical/tarkasamgraha.json", dict(
        id="5", text="Tarkasaṃgraha of Annambhaṭṭa", tradition="Nyaya", commentator=None, script="Devanagari", units=units,
        source_sanskrit={"citation": "The Tarkasangraha of Annam Bhatta (Nirnayasagara, Bombay 1876; English from the 1851 Allahabad edition of Ballantyne and Hall), Sanskrit re-OCR'd with Sarvam Vision (sa-IN)", "url": "https://archive.org/details/tarkasangrahaofa00annaiala", "license": None},
        source_english={"citation": "same book: J.R. Ballantyne and F. Hall's English translation of the Tarkasangraha and its Dipika (archive.org scan, Sarvam Vision OCR)", "url": "https://archive.org/details/tarkasangrahaofa00annaiala", "license": None},
        bundled=True, needs_ocr=True, alignment="row_aligned",
        notes=(f"Mula only: Annambhatta's Tarkasaṃgraha sentences, without his own Dipika gloss, which is a commentary and was dropped as out of scope. Sanskrit and English are from the same scan, both via Sarvam Vision OCR of pages 8-58. Units follow the book's own numbering 1-70 (GRETIL's 81-section numbering differs and was not used); english is the book's quoted translation of that mula number, translator's [brackets] kept (some brackets paraphrase the Dipika). "
               f"Sections without English: {', '.join(missing_en) or 'none'}. Sections whose number the OCR could not read (mula numbers {', '.join(str(n) for n in range(1, 71) if n not in secs)}) have no unit here even where the book has their English. Where the OCR fused a Dipika sentence into the mula paragraph, it was split at the last double danda before the section number, so a stray Dipika fragment may remain at the start of a few sanskrit values. First pass.")))
    print(len(units), len(missing_en), missing_en)


if __name__ == "__main__":
    main()
