"""Madhavananda's translation of a mantra and of Shankara's commentary on it sat together in the mula part's english (bhashya part empty). Split: transliteration line dropped, first paragraph is the mantra, the rest is the bhashya."""
import json
import re
from pathlib import Path

F = Path(__file__).resolve().parent.parent / "upanishads" / "brihadaranyaka_shankara.json"
WORD = re.compile(r"\b(the|is|of|and|that|to|in)\b")
DIAC = re.compile(r"[āīūṛṝḷṃḥṅñṭḍṇśṣ|]")
NUM = re.compile(r"^\W*[\dIl]{1,3}[.,]\s*")


def split(en):
    lines = [l.strip() for l in en.split("\n") if l.strip()]
    lines = [l for l in lines if not re.match(r"(?i)^verse\s+[\d.]+\s*:?$", l)]
    lines = [l for l in lines if not (DIAC.search(l) and not WORD.search(l))]
    if len(lines) < 2:
        return None
    return NUM.sub("", lines[0]), "\n".join(lines[1:])


d = json.loads(F.read_text(encoding="utf-8"))
fixed, flagged = 0, []
for u in d["units"]:
    ps = {p["role"]: p for p in u.get("parts") or []}
    m, b = ps.get("mula"), ps.get("bhashya")
    if not (m and b and b.get("sanskrit") and not b.get("english") and m.get("sanskrit")):
        continue
    en = m.get("english", "")
    if len(en) <= 3 * len(m["sanskrit"]) or len(en) <= 300:
        continue
    r = split(en)
    if not r:
        flagged.append((u["ref"], "single paragraph"))
        continue
    trans, comm = r
    if len(trans) > 3 * len(m["sanskrit"]) + 400:
        flagged.append((u["ref"], f"mantra paragraph {len(trans)} vs sanskrit {len(m['sanskrit'])}"))
    m["english"], b["english"] = trans, comm
    both = [p for p in u["parts"] if p.get("sanskrit") and p.get("english")]
    u["sanskrit"] = "\n".join(p["sanskrit"] for p in both)
    u["english"] = "\n".join(p["english"] for p in both)
    u["scope"] = "mula+commentary"
    fixed += 1
print("fixed", fixed, "flagged", len(flagged))
for f in flagged:
    print(" ", f)
F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
