"""bsb_shankara: drop repeated lines in the Sanskrit (Setutila prints some paragraphs twice), and drop from 3.3.21
the adhyaya 3 / pada 1-3 intro paragraphs that already stand in intro-3.1, intro-3.2 and 3.3.1.
Run from corpus/: python3 tools/bsb_shankara_dedupe.py [--dry]"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv
F = ROOT / "philosophical" / "bsb_shankara.json"


def dedupe(text):
    seen, out = set(), []
    for line in text.split("\n"):
        k = line.strip()
        if len(k) > 30 and k in seen:
            continue
        seen.add(k)
        out.append(line)
    return "\n".join(out)


def main():
    d = json.loads(F.read_text(encoding="utf-8"))
    U = {u["ref"]: u for u in d["units"]}

    b = next(p for p in U["3.3.21"]["parts"] if p["role"] == "bhashya")
    lines = b["sanskrit"].split("\n")
    i = next(k for k, l in enumerate(lines) if l.startswith("न वा उभयोः उभयत्र"))
    assert lines[0].startswith("द्वितीयेऽध्याये") and i == 7, i
    b["sanskrit"] = "\n".join(lines[i:])

    fixed = 0
    for u in d["units"]:
        joined = "\n".join(p["sanskrit"] for p in u.get("parts") or [] if p.get("sanskrit"))
        for p in u.get("parts") or []:
            if p.get("sanskrit"):
                n = dedupe(p["sanskrit"])
                if n != p["sanskrit"]:
                    p["sanskrit"] = n
                    fixed += 1
        if u.get("parts") and u["scope"] == "mula+commentary":
            u["sanskrit"] = "\n".join(p["sanskrit"] for p in u["parts"] if p.get("sanskrit"))
        else:
            u["sanskrit"] = dedupe(u["sanskrit"])
    d["notes"] += (
        f" [Dedupe pass 2026-10-13: Setutila prints some paragraphs twice; repeated lines were dropped from the Sanskrit of {fixed} parts. 3.3.21 also "
        "carried the introductions of adhyaya 3 and padas 3.1-3.3 (already present in intro-3.1, intro-3.2 and 3.3.1), now removed.]"
    )
    print("parts deduped", fixed)
    if not DRY:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
