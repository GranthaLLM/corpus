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
        dip = " ".join(s["dipika"]).strip() or None
        mula = s["mula"]
        units.append({"ref": str(n), "kind": "mula+dipika", "sanskrit": " ".join(x for x in (mula, dip) if x),
                      "sanskrit_mula": mula, "sanskrit_dipika": dip, "english": english.get(n)})
    missing_en = [u["ref"] for u in units if not u["english"]]
    write("philosophical/tarkasamgraha.json", dict(
        id="5", text="Tarkasaṃgraha of Annambhaṭṭa with the Dīpikā", tradition="Nyaya", commentator="Annambhaṭṭa (Dīpikā)", script="Devanagari", units=units,
        source_sanskrit={"citation": "The Tarkasangraha of Annam Bhatta (Nirnayasagara, Bombay 1876; English from the 1851 Allahabad edition of Ballantyne and Hall), Sanskrit re-OCR'd with Sarvam Vision (sa-IN)", "url": "https://archive.org/details/tarkasangrahaofa00annaiala", "license": None},
        source_english={"citation": "same book: J.R. Ballantyne and F. Hall's English translation of the Tarkasangraha and its Dipika (archive.org scan, Sarvam Vision OCR)", "url": "https://archive.org/details/tarkasangrahaofa00annaiala", "license": None},
        bundled=True, needs_ocr=True, alignment="row_aligned",
        notes=(f"Sanskrit and English from the same scan, both via Sarvam Vision OCR of pages 8-58. Units follow the book's own numbering 1-70 (mula sentence + Annambhatta's Dipika gloss in Devanagari; GRETIL's 81-section numbering differs and was not used). english is the book's quoted translation for that number (it already folds in the Dipika content, translator's [brackets] kept). "
               f"Sections without English: {', '.join(missing_en) or 'none'}. Sections whose number the OCR could not read (mula numbers {', '.join(str(n) for n in range(1, 71) if n not in secs)}) have no Sanskrit unit here even where the book has their English; Dipika paragraphs are attached to the preceding mula by position, so a stray index or page-head line may occasionally sit in a sanskrit_dipika, and where mula and Dipika were OCR'd as one paragraph (e.g. 39) sanskrit_mula carries the Dipika too. First pass; Dipika text after section 70 (the book's indices) is excluded.")))
    print(len(units), len(missing_en), missing_en)


if __name__ == "__main__":
    main()
