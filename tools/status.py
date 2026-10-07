import glob, json, re
from common import ROOT

ROWS = [
    ("1a", "Gita, Śaṃkara", ["philosophical/bg_shankara"], "Sanskrit Advaita Sharada; English Warrier (Ramakrishna Math) and Sastri 1897 scan (OCR), matched by verse"),
    ("1b", "Gita, Rāmānuja", ["philosophical/bg_ramanuja"], "Sanskrit GRETIL; English Adidevananda scan (OCR), matched by verse; some verses merged where the translation covers two"),
    ("1c", "Gita, Madhva", ["philosophical/bg_madhva"], "Sanskrit Setutila (commentary gaps decoded from Sonde legacy font); English Sonde, four bhashya passages from Sharma 1989; verse groups"),
    ("2", "Brahmasutra, Śaṃkara", ["philosophical/bsb_shankara"], "Sanskrit Advaita Sharada; English Gambhirananda scan (OCR), every sutra"),
    ("3", "Sri Bhashya, Rāmānuja", ["philosophical/sribhashya_ramanuja"], "English Thibaut via wisdomlib; Sanskrit Bodhan OCR of the Annangaracharya scan (unproofread), aligned per sutra; 6 units hold two sutras"),
    ("4", "Brahmasutra, Madhva", ["philosophical/bsb_madhva"], "Sanskrit from the project docx; English Subba Rau (1904) where its OCR is clean, otherwise Sonde (decoded and translated PDFs); every sutra has English"),
    ("5", "Tarkasaṃgraha", ["philosophical/tarkasamgraha"], "Mula only (Dipika dropped); Sanskrit + English from the 1876/1851 scan (Sarvam OCR), book numbering 1-70; 63 sections, 7 lost to OCR numbering"),
    ("6", "Bhattasangraha", ["philosophical/bhattasangraha"], "Sanskrit archive.org OCR (adhyayas 1-12, one unit per adhikarana, unproofread, some headings lost); English is Pandurangi's summary of each adhikarana (not a translation): exposition in vols 1 and 3 paired by heading name, introduction summary in vol 2 paired by adhyaya.pada.number"),
    ("7", "Sarvadarshanasamgraha", ["philosophical/sarvadarshanasamgraha"], "Mitrasamgraha rows, bundled"),
    ("8", "Vimshatika/Trimshika", ["philosophical/vimshatika_trimshika"], "Mitrasamgraha rows; appears to be the Vimshatika only"),
    ("9", "Samkhyakarika", ["philosophical/samkhyakarika"], "Mitrasamgraha rows (Matharavritti)"),
    ("10", "MBTN", ["philosophical/mbtn"], "Sanskrit Setutila; English Nellitheertha 2021, aligned per chapter by order (names, length, machine-translation similarity); units over 16 verses split into ~8-verse groups"),
    ("11-20 Śaṃkara", "Upanishads, Śaṃkara track", [f"upanishads/{u}_shankara" for u in ["isa", "kena", "katha", "prashna", "mundaka", "mandukya", "brihadaranyaka", "taittiriya", "aitareya"]] + ["upanishads/chandogya_shankara"], "Sanskrit Advaita Sharada; English wisdomlib (Isa..Mundaka, Mandukya, Brihadaranyaka), Sastri scan (Aitareya, Taittiriya), Jha via Mitrasamgraha (Chandogya, joined by content)"),
    ("11-20 Madhva", "Upanishads, Madhva track", [f"upanishads/{u}_madhva" for u in ["isa", "kena", "katha", "prashna", "mundaka", "mandukya", "taittiriya", "aitareya", "chandogya", "brihadaranyaka"]], "Sanskrit Setutila; English wisdomlib (Isa, Kena, Katha, Prashna, Mundaka, Mandukya), Sonde (Taittiriya, Chandogya, Brihadaranyaka), Pandurangi (Aitareya, interpretive)"),
    ("21a-c", "Mahabharata: Sanatsujatiya, Vidura Niti, Yaksha Prashna", ["sahitya/sanatsujatiya", "sahitya/vidura_niti", "sahitya/yaksha_prashna"], "Mitrasamgraha slices of the Ganguli file"),
    ("22a-b", "Bhagavata: Kapila (3.25-33), Uddhava Gita (11.7-29)", ["sahitya/bhagavata_kapila", "sahitya/bhagavata_uddhava"], "Sanskrit Setutila; English Prabhupada via Vedabase (neutralised terms; verbatim in meta.english_verbatim)"),
    ("23", "Harivamsha", ["sahitya/harivamsha"], "Mitrasamgraha rows"),
    ("24", "Kumarasambhava", ["sahitya/kumarasambhava"], "Mitrasamgraha rows; cantos 1-7 only (source ends there)"),
    ("25", "Shatakatraya", ["sahitya/shatakatraya"], "Sanskrit GRETIL; English Wortham 1886 (OCR, unproofread) paired by content, Niti and Vairagya; Shringarashataka gaps from Kennedy 1913 and Gopalachariar 1954 (in copyright)"),
]


def table():
    lines = ["| Row | Work | Files | Units | Sanskrit+English units | Status |", "|---|---|---|---|---|---|"]
    for row, name, files, status in ROWS:
        n = both = 0
        for f in files:
            d = json.loads((ROOT / (f + ".json")).read_text(encoding="utf-8"))
            n += len(d["units"])
            both += sum(1 for u in d["units"] if u.get("sanskrit") and u.get("english"))
        fl = ", ".join(f"`{f.split('/')[-1]}`" for f in files) if files else "-"
        lines.append(f"| {row} | {name} | {fl} | {n} | {both} | {status} |")
    return "\n".join(lines)


MIX = {"text": "whole text", "mula": "mula only", "commentary": "commentary only", "mula+commentary": "mula + commentary"}


AUTHOR = {
    "samkhyakarika": "Īśvarakṛṣṇa", "sarvadarshanasamgraha": "Mādhava", "tarkasamgraha": "Annambhaṭṭa",
    "vimshatika_trimshika": "Vasubandhu", "harivamsha": "Vyāsa (traditional)", "kumarasambhava": "Kālidāsa",
    "shatakatraya": "Bhartṛhari", "sanatsujatiya": "Vyāsa (traditional)", "vidura_niti": "Vyāsa (traditional)",
    "yaksha_prashna": "Vyāsa (traditional)", "bhagavata_kapila": "Vyāsa (traditional)", "bhagavata_uddhava": "Vyāsa (traditional)",
}


def title(t):
    t = re.sub(r"(Madhva|Śāṃkara|Rāmānuja)bhāṣya\b", "Bhāṣya", t)
    t = t.replace(" (Padabhāṣya)", "")
    return re.sub(r"\s+of\s+(Madhva|Rāmānuja|Rāghavendratīrtha|Annambhaṭṭa|Mādhava|Vasubandhu|Īśvarakṛṣṇa)$", "", t)


def files_table():
    lines = ["| Work | Author | Units | Scope mix |", "|---|---|---|---|"]
    tot = 0
    for f in sorted(glob.glob(str(ROOT / "*" / "*.json"))):
        rel = f[len(str(ROOT)) + 1:]
        if rel.split("/")[0] in ("raw", "spotcheck") or rel == "schema.json":
            continue
        d = json.loads(open(f, encoding="utf-8").read())
        us = d["units"]
        tot += len(us)
        mix = {}
        for u in us:
            mix[u["scope"]] = mix.get(u["scope"], 0) + 1
        mx = ", ".join(f"{MIX[k]} {v}" for k, v in sorted(mix.items(), key=lambda kv: -kv[1]))
        stem = rel.split("/")[-1][:-5]
        author = AUTHOR.get(stem) or d.get("commentator") or "-"
        lines.append(f"| {title(d['text'])} | {author} | {len(us)} | {mx} |")
    lines.append(f"| **Total** | | **{tot}** | |")
    return "\n".join(lines)


if __name__ == "__main__":
    p = ROOT / "README.md"
    t = p.read_text(encoding="utf-8")
    block = "<!-- status:start -->\n## Status\n\nGenerated by `tools/status.py`. 'Sanskrit+English units' counts units where both fields are filled; 'first pass' OCR-derived English can be noisy.\n\n" + table() + "\n<!-- status:end -->"
    if "<!-- status:start -->" in t:
        t = re.sub(r"<!-- status:start -->.*<!-- status:end -->", lambda m: block, t, flags=re.S)
    fblock = "<!-- files:start -->\n" + files_table() + "\n<!-- files:end -->"
    if "<!-- files:start -->" in t:
        t = re.sub(r"<!-- files:start -->.*<!-- files:end -->", lambda m: fblock, t, flags=re.S)
    p.write_text(t, encoding="utf-8")
    print(table())
