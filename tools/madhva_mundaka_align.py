"""Align english with sanskrit in mundaka_madhva. Sources: wisdomlib Vasu pages, Sonde's PDF.
Run from corpus/: python3 tools/madhva_mundaka_align.py [--dry]"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv
F = ROOT / "upanishads" / "mundaka_madhva.json"


def part(u, role):
    return next(p for p in u["parts"] if p["role"] == role)


def drop_part(u, role):
    u["parts"] = [p for p in u["parts"] if p["role"] != role]


def edit(u, old, new):
    hit = False
    for h in [u] + (u.get("parts") or []):
        e = h.get("english")
        if e and old in e:
            h["english"] = e.replace(old, new)
            hit = True
    assert hit, (u["ref"], old[:50])


def tail_cut(u, start):
    for h in [u] + (u.get("parts") or []):
        e = h.get("english")
        if e and start in e:
            h["english"] = e[: e.index(start)].rstrip()


def to_commentary(u, bhashya_en):
    m, b = part(u, "mula"), part(u, "bhashya")
    b["english"] = bhashya_en
    u["scope"] = "mula+commentary"
    u["sanskrit"] = m["sanskrit"] + "\n" + b["sanskrit"]
    u["english"] = m["english"] + "\n" + bhashya_en


def main():
    d = json.loads(F.read_text(encoding="utf-8"))
    U = {u["ref"]: u for u in d["units"]}

    for u in d["units"]:
        for h in [u] + (u.get("parts") or []):
            e = h.get("english")
            if e:
                e = re.sub(r"(^|\n)\d+\.\s*(?=\S)", r"\1", e)
                e = re.sub(r"[—-]\s*\d+\.?\s*(?=\n|$)", "", e)
                h["english"] = e.strip()

    for r in ("1/1/7", "1/1/8", "2/1/1", "3/2/3"):
        drop_part(U[r], "bhashya")

    edit(U["1/1/3"], "does all this becomes", "does all this become known?”")
    edit(U["1/2/3"], "new Moon, four", "new Moon, four month’s sacrifice, rituals, honoured guests, oblations, propitiation of divinities, traditional offerings or giving offerings contrary to traditions, his seven worlds are destroyed.")
    edit(U["1/2/4"], "are the seven", "are the seven flaming tongues.")
    edit(U["1/2/8"], "considering themselves to be", "considering themselves to be learned, these misguided ones, suffering misfortunes, go around like the blind led by the blind.")
    edit(U["2/2/4"], "target that immutable Brahman", "target, that immutable Brahman.")
    edit(U["2/2/4"], "Seizing Upanishada as", "Seizing the Upanishad as")
    edit(U["2/2/4"], "one should aim the arrow with Mind concentrated", "one should aim the arrow with the mind concentrated on the")

    tail_cut(U["1/1/5"], "8 Further Explanations:")
    tail_cut(U["1/2/1"], "Further Explanations:")

    u = U["2/1/4"]
    b = part(u, "bhashya")
    b["english"] = b["english"].split("\n")[0]
    u["english"] = part(u, "mula")["english"] + "\n" + b["english"]

    u = U["2/1/10"]
    lines = part(u, "bhashya")["english"].split("\n")
    assert lines[0].startswith("Madhva")
    to_commentary(u, "\n".join(lines[1:4]))

    u = U["3/1/7"]
    to_commentary(u, "As he is all-pervading he is said to be both far and near.")

    u = U["3/2/9"]
    b = part(u, "bhashya")
    e = b["english"]
    e = e[: e.index("Moreover, the Lord Bādarāyana")].replace(" [?m]", "")
    e += (
        "Moreover, the Lord Bādarāyaṇa also in his aphorisms indicates that the Jīva remains distinct from the Brahman even in the state of release. "
        "Thus in the Vedānta Sūtra, I, 3, 2, he shows that Brahman is the goal to be reached by the Muktas. The object reached must be different from "
        "the object reaching. So also in the Vedānta Sūtras, IV, 4, 17 and 18, Bādarāyaṇa clearly indicates the fundamental difference between the Muktas "
        "and the Lord. The Muktas never possess the power of creating a Universe—that is the unique attribute of the Lord. Thus Bādarāyaṇa and this "
        "Upaniṣad show that the Muktas remain different from the Lord.\n"
        "So also says the Rig Veda VII. 99. 1: “O Viṣṇu, Thou art beyond measure. None reaches Thy Greatness, be he a Mukta or a bound soul. Thou art "
        "Infinitely Full in Thy essential Form.” “He enjoys all desires along with the Omniscient Brahman” (Taitt. Up. II, 1, 1).\n"
        "“That Kaivalya which neither Brahmā nor Īśāna nor any other deva can ever attain, that art Thou, O Lord Hari, in Thy own nature.”\n"
        "The Devas are greater in attributes than even the Mukta men; Vāyu is greater than all the Devas. Higher than Vāyu is Viṣṇu, full of all "
        "auspicious attributes. Those who think otherwise go to deep darkness; those who know it properly attain even the Supreme Hari.\n"
        "In the family of Devas following the dharma of the Kṛta age, knowers of Brahman alone are born, as a general rule; exceptionally, owing to some "
        "extraordinary cause (such as a curse), non-knowers may be born in the family of a Deva. In the family of human knowers of Brahman, as a general "
        "rule, a knower of Brahman is not necessarily born. Such is the law made in the Kṛta age.\n"
        "Therefore the Lord Viṣṇu, the best of all beings, full of all qualities, infinite, the Highest Person, should always be known."
    )
    b["english"] = e
    u["english"] = part(u, "mula")["english"] + "\n" + e
    assert "[?" not in u["english"]

    d["notes"] += (
        " [Alignment pass 2026-10-09: verse numbers and wisdomlib dashes-and-numbers stripped from english; english cut off at a line break in the Sonde text "
        "completed (1/1/3, 1/2/3, 1/2/4, 1/2/8, 2/2/4); Sonde's 'Further Explanations' cut from 1/1/5 and 1/2/1 and Vasu's notes from 2/1/4; Vasu's notes "
        "held as english-only parts under 1/1/7, 1/1/8, 2/1/1, 3/2/3 dropped; 2/1/10 and 3/1/7 are mula+commentary since Setutila has their commentary and "
        "Vasu translates it; 3/2/9 had [?] gaps from wisdomlib's scan, which were restored from the Sanskrit (Vedanta Sutra numbers 4.4.17-18 from the "
        "quoted sutra words) and Vasu's closing notes cut.]"
    )
    if not DRY:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
