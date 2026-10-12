"""bsb_shankara 1.2.5 carried 1002 characters that belong to the Topic 7 preamble (1.1.20); its own english, from the Gambhirananda scan, is restored.
Run from corpus/: python3 tools/bsb_shankara_relocate2.py [--dry]"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv
F = ROOT / "philosophical" / "bsb_shankara.json"

MULA = "Owing to the difference in the (case-endings of the two) words."
BHASHYA = (
    "The one possessed of such characteristics as identity with the mind and so on must be different from the embodied being for this additional reason that a "
    "difference in the case-endings of the words occurs in a similar context in another Vedic text: \"Just as a grain of paddy or barley or Syamaka (a kind of millet) "
    "or a seed of Syamaka is (very small), so is the effulgent Puru$a (i.e. the conscious all-pervasive Entity) inside the (individual) soul (antaratman)\" (S. B. X. vi. 3. 2). "
    "Here the word Puru$a, used in the singular number, nominative case, means the Self endowed with the qualities of being identified with the mind and so on; and this word "
    "is different from the term antaratmane which is used with a seventh case-ending and refers to the embodied soul. Therefore their difference becomes obvious (so that the one "
    "identified with the mind is not the individual soul)."
)


def main():
    d = json.loads(F.read_text(encoding="utf-8"))
    U = {u["ref"]: u for u in d["units"]}
    u = U["1.2.5"]
    m = next(p for p in u["parts"] if p["role"] == "mula")
    b = next(p for p in u["parts"] if p["role"] != "mula")
    m["english"], b["english"] = MULA, BHASHYA
    u["english"] = MULA + "\n" + BHASHYA
    for h in [U["1.2.4"]] + U["1.2.4"]["parts"]:
        if h.get("english"):
            h["english"] = h["english"].replace("ohjee~", "object")
    d["notes"] += " [1.2.5 english restored 2026-10-09 from the Gambhirananda scan; it had held the Topic 7 preamble of 1.1.20.]"
    if not DRY:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
