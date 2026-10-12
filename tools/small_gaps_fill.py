"""Add english for a handful of short commentary passages that no source translates (bg_shankara 5.27, 7.30; brihadaranyaka_shankara 6.4.2;
bsb_madhva 2.3.39, 3.1.22, 3.3.68 closing line; bg_ramanuja 1.1). The translations are written for this corpus and named in the file notes.
Run from corpus/: python3 tools/small_gaps_fill.py [--dry]"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv

FILL = {
    "philosophical/bg_shankara.json": {
        "5.27": "It has been said that liberation is immediate for the renouncers who are established in right knowledge; and that Karma Yoga, performed by placing all actions in the Lord, in Brahman, leads to liberation through purity of mind, the attainment of knowledge and the renunciation of all action, in that order. So the Lord said at every step, and will say again. Now, intending to explain at length the Yoga of meditation, the inner aid of right knowledge, he teaches the verses that serve as its aphorisms:",
        "7.30": "‘Sādhibhūtādhidaivam’: adhibhūta and adhidaiva together; those who know Me as abiding with adhibhūta and adhidaiva, and ‘sādhiyajñam’, with adhiyajña, they know Me also at the time of departure, at the time of death, with concentrated minds, that is, with steady, collected minds.",
    },
    "upanishads/brihadaranyaka_shankara.json": {
        "6.4.2": "Since this seed is thus the quintessence of all beings, ‘what then is a fit abode for it?’: so the Creator Prajāpati thought. Having thought, he created woman. And having created her, he ‘worshipped below’; that is, he performed the act called union, which is named ‘worship below’. Therefore one should worship woman below; for creatures follow the best. Here he states a likeness to the Vājapeya: ‘he made his own stone’, the organ of generation, which by its hardness resembles the stone for pressing soma, moving forward, of excellent motion, ‘he raised up’ towards the woman’s organ; with that he united with her.",
    },
    "philosophical/bsb_madhva.json": {
        "2.3.39": "And from the absence of composure, lack of independence is evident.",
        "3.1.22": "In the third: from the mere hearing of the third and darkest, bewilderment born of grief arises, in keeping with the word.",
    },
    "philosophical/bg_ramanuja.json": {
        "1.1": "Though he knew thus, Dhṛtarāṣṭra, utterly blind, asked Sañjaya, wishing to know of Suyodhana’s victory.",
    },
}
NOTE = " [2026-10-09: english of a few short commentary passages that no source translates was written for this corpus (Claude): {refs}.]"


def main():
    for rel, refs in FILL.items():
        p = ROOT / rel
        d = json.loads(p.read_text(encoding="utf-8"))
        U = {u["ref"]: u for u in d["units"]}
        for ref, text in refs.items():
            u = U[ref]
            m = next(q for q in u["parts"] if q["role"] == "mula")
            b = next(q for q in u["parts"] if q["role"] != "mula" and q.get("sanskrit"))
            m["english"] = m.get("english") or u["english"]
            b["english"] = text
            u["english"] = m["english"] + "\n" + text
        if rel.endswith("bsb_madhva.json"):
            u = U["3.3.68"]
            u["english"] = u["english"].rstrip() + "\nThus ends the third pada of the third adhyaya of the Brahmasūtrabhāṣya composed by the revered Ānandatīrtha Bhagavatpāda."
        if rel.endswith("bg_shankara.json"):
            u = U["11.42"]
            for h in [u] + u["parts"]:
                if h.get("english") and h["english"].rstrip().endswith("Because,"):
                    h["english"] = h["english"].rstrip()[: -len("Because,")].rstrip()
        d["notes"] += NOTE.format(refs=", ".join(refs))
        if not DRY:
            p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
