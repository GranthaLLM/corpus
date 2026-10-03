import json, re
from common import ROOT, write

KAN = re.compile(r"[ಀ-೿]")
RULES = {
    "philosophical/bsb_madhva.json": [(r"\[ॐ\]", "ॐ")],
    "philosophical/sribhashya_ramanuja.json": [(r"ankurnagpal108@", ""), (r"\\text\{[^}]*\}", ""), (r"\*", "")],
    "philosophical/samkhyakarika.json": [(r"Uncommented\s*", "")],
    "philosophical/vimshatika_trimshika.json": [(r"\s*\(Vvs_\)", "")],
    "upanishads/brihadaranyaka_madhva.json": [(r"॥\s*[0-9]+-[0-9]+॥", "॥")],
    "philosophical/bhattasangraha.json": [(r"\|\|", "॥"), (r"\|", "।"), (r"(?<=[ऀ-ॿ])5{1,2}(?=[ऀ-ॿ])", "ऽ"), (r"(?m)^\s*\d{1,3}\s*[ऀ-ॿ]{3,12}\*?\s*$", ""), (r"(?m)^[^\n]*[ಀ-೿][^\n]*$", ""), (r"(?m)^\s*[0-9]{1,3}\s*$", ""), (r"\n{3,}", "\n\n")],
}
STAR_FILES = ["philosophical/bg_madhva.json", "upanishads/brihadaranyaka_madhva.json", "upanishads/chandogya_madhva.json", "upanishads/isa_madhva.json", "upanishads/katha_madhva.json",
              "upanishads/kena_madhva.json", "upanishads/mandukya_madhva.json", "upanishads/mundaka_madhva.json", "upanishads/prashna_madhva.json", "upanishads/taittiriya_madhva.json", "sahitya/bhagavata_uddhava.json", "sahitya/harivamsha.json"]
for f in STAR_FILES:
    RULES.setdefault(f, []).append((r"[ \t]*\*[ \t]*(?=॥)", ""))
    RULES[f].append((r"(?m)^\s*\*\s*$", ""))


def main():
    for rel, rules in RULES.items():
        p = ROOT / rel
        d = json.loads(p.read_text(encoding="utf-8"))
        n = 0
        for u in d["units"]:
            for t in [u] + u.get("parts", []):
                s = t.get("sanskrit")
                if not s:
                    continue
                c = s
                for a, b in rules:
                    c = re.sub(a, b, c)
                c = re.sub(r"[ \t]+\n", "\n", c).strip()
                if c != s:
                    t["sanskrit"] = c
                    n += 1
        if n:
            d["notes"] += " Stray source marks were removed from the Sanskrit (editorial brackets, asterisks, page headers, watermark text, OCR pipes for dandas)."
            write(rel, d)
        print(rel, n)


if __name__ == "__main__":
    main()
