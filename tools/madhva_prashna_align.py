"""Align english with sanskrit in prashna_madhva. Source: wisdomlib Vasu pages.
Run from corpus/: python3 tools/madhva_prashna_align.py [--dry]"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv
F = ROOT / "upanishads" / "prashna_madhva.json"


def part(u, role):
    return next(p for p in u["parts"] if p["role"] == role)


def drop_part(u, role):
    u["parts"] = [p for p in u["parts"] if p["role"] != role]


def to_commentary(u, bhashya_en):
    """Make u a mula+commentary unit: sanskrit and english are the joins of the mula and bhashya parts."""
    m, b = part(u, "mula"), part(u, "bhashya")
    b["english"] = bhashya_en
    u["scope"] = "mula+commentary"
    u["sanskrit"] = m["sanskrit"] + "\n" + b["sanskrit"]
    u["english"] = m["english"] + "\n" + bhashya_en


def main():
    d = json.loads(F.read_text(encoding="utf-8"))
    U = {u["ref"]: u for u in d["units"]}

    for r in ("1/4", "1/5", "1/6", "1/7", "1/8", "1/12", "2/7", "3/6", "3/9", "4/1", "5/3", "6/2"):
        drop_part(U[r], "bhashya")

    to_commentary(
        U["1/15"],
        "Viṣṇu is called the Prajāpati because He protects (pati) all creatures (prajā). He, the Supreme Spirit, the Highest Person sends out, in the "
        "beginning of every Kalpa, Vāyu called also the Sūrya (the sun) and Sarasvatī called also the moon. He makes these Vāyu and Sarasvatī take their "
        "abode in the Sun and the Moon. Then entering these two, Viṣṇu Himself the Unborn creates all this Universe. He dwelling in Vāyu, is formless "
        "(amūrta.) He dwelling in Sarasvatī is with form.\n"
        "The Vāyu dwelling in the Sun takes up all the spirits of various Quarters and makes them enter into his rays. The spirits or the Prāṇas of the East "
        "are Indra and the rest, of the South, are the Yama and the rest, of the West, are the Varuṇa, and the rest, of the North, are the Soma, and the "
        "rest: Śeṣa and Mitra are the prāṇas of the Nadir, Vīndra and Kāma of the Zenith. Four are in each quarter, counting their consorts and the "
        "intermediate quarters.\n"
        "The Lord dwells in the year: in the winter half dwells His Sarasvatī aspect, in the northern or summer half, His Prāṇa aspect. The Lord dwells in "
        "the month. In the Bright fortnight is His Prāṇa aspect, in the Dark fortnight, is His Sarasvatī aspect. The Lord dwells in the day and night. His "
        "Prāṇa aspect is in the day, His Sarasvatī aspect is in the night.\n"
        "The Lord Viṣṇu dwells in the husband and wife—Vāyu dwells in the husband, Sarasvatī in the wife. He who knows thus gets Release. Thus we find in "
        "the Prajāpati Saṃhitā.",
    )

    u = U["1/13"]
    u["english"] = u["english"].split("—13. Note.")[0].rstrip("—")
    if u.get("parts"):
        part(u, "mula")["english"] = u["english"]

    u = U["2/1"]
    b = part(u, "bhashya")
    b["english"] = (
        "To him he said: Ether verily, and this always moving the air, fire, water, earth, speech, mind, eye and ear (are the Devas). They the Shining Ones, "
        "once loudly disputed with each other saying: We (alone) uphold this body by supporting it.\n"
        "In this verse by Vāyu is meant the elemental air: while Prāṇa denotes the chief air or the first-begotten."
    )
    u["english"] = part(u, "mula")["english"] + "\n" + b["english"]

    u = U["3/3"]
    to_commentary(u, "The words “from the Ātman” mean from the Supreme Atman, from God.")
    u = U["3/5"]
    b = part(u, "bhashya")
    b["english"] = (
        "As in the Prabhañjana:—“From Viṣṇu came out Vāyu, from Vāyu were produced all other Shining Ones, like prāṇa, apāna, etc. The first begotten rules "
        "and commands them, as a king commands his officers. Himself being five-fold, the Lord thus gives salvation to men.”"
    )
    u["english"] = part(u, "mula")["english"] + "\n" + b["english"]

    u = U["3/8"]
    u["english"] = u["english"].replace("(The Cosmic correspondences are).—", "")
    if u.get("parts"):
        part(u, "mula")["english"] = u["english"]

    com65 = part(U["6/5"], "bhashya")["english"].split("\n", 1)[1]
    com65 = com65.replace("dees not", "does not").replace(" (Note: Viśvedevas denote form)", "")
    drop_part(U["6/5"], "bhashya")
    to_commentary(U["6/8"], com65)

    u = U["6/4"]
    for h in [u] + u["parts"]:
        if h.get("english"):
            h["english"] = h["english"].replace(" (Note:—does not the activity of the mind arise after the senses have supplied the material)?", ".")

    d["notes"] += (
        " [Alignment pass 2026-10-09: Madhva's one Prajapati quote (Sanskrit in 1/15) is translated by Vasu in four pieces under 1.4, 1.8, 1.12 and 1.15; "
        "those four pieces now sit in 1/15 with the Sanskrit, 1/15 is mula+commentary, and the english-only parts holding Vasu's notes and the Shankara and "
        "Ramanuja readings were dropped (1/4-1/8, 1/12, 2/7, 3/6, 3/9, 4/1, 5/3, 6/2, 6/5). Setutila's 2/1 holds mantras 2.1 and 2.2 with the commentary on 2.2, "
        "so 2/1 now translates both; the Prabhanjana quote Setutila places at 3/5 carries Vasu's translation of it, and 3/3 keeps the line on 'from the Atman'; "
        "the commentary on 6.5 (Sanskrit under 6/8) is translated in 6/8.]"
    )
    if not DRY:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
