"""Subba Rau abridges Madhva's bhashya on five sutras (1.1.24, 1.3.1, 1.4.29, 2.1.8, 2.4.1), leaving the quoted Śruti and Purana texts untranslated.
The english of the commentary part of those five units was replaced with a full translation written for this corpus; the sutra translations stay Subba Rau's.
Run from corpus/: python3 tools/bsb_madhva_fill.py [--dry]"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv
F = ROOT / "philosophical" / "bsb_madhva.json"

T = {
    "1.1.24": "It was said, ‘He who knows what is hidden in the cave’. And that which is hidden in the cave is spoken of as light in the text: ‘My ears and eyes fly apart; this light that is set in the heart, and my mind wandering far, intent on the distant: what shall I say, what shall I think?’ Because of the Agni-sūkta and by common usage, that light would be taken to be Agni alone. Therefore he says: ‘from the mention of straying’. Viṣṇu alone is the light, since the straying of the ears and the rest is mentioned. For he is far from the ears and the other senses, as in ‘beyond measure, growing by his body’ and the like.",
    "1.3.1": "In this pada he shows, for the most part, the harmony in Viṣṇu of words well known both in this context and elsewhere. It has been said that Viṣṇu is the subject of the higher knowledge. There, in ‘He in whom heaven, earth and the sky are woven, and the mind with all the breaths, know him alone as the Self’, Rudra is understood to be the support of the breaths from such texts as ‘You are the knot of the breaths, Rudra; do not enter me as the destroyer’ and ‘Lord of the breaths, clad in a hide, bearing the Pināka’; and from the mark of the individual soul in ‘This one moves within, born in many ways’, it would follow that those two are the abode of heaven and earth. Therefore he says: ‘The abode of heaven and earth, from its own word.’ By the word ‘Self’ in ‘know him alone as the Self’, the support of heaven, earth and the rest is Viṣṇu alone. ‘The words Self, Brahman and the like do not apply except to the imperishable Viṣṇu, since perfection in qualities is not attained by others through them’: thus in the Brahmavaivarta.",
    "1.4.29": "By this, all the words such as ‘void’ are also explained. ‘He alone is void; he alone is insignificant; he alone is non-being; he alone is unmanifest, invisible, inconceivable and without qualities’: so in the Mahopaniṣad. ‘Viṣṇu, being himself invisible and supreme, makes the happiness of others deficient; therefore he is called void. Because he afflicts, he is called insignificant. No one is able to conceive this Supreme Person; therefore they call him non-being, and also destruction, since he is to be destroyed (in thought). Since everything depends on him, he is the meaning of those several words; for others it is admitted for the sake of usage by speakers’: so in the Mahākūrma. ‘By this’ means by the whole group of arguments already given, beginning with dependence on him. ‘The wise repeat at the end of a chapter, in the conclusion, for emphasis, all that has been said from the beginning of the chapter’: so in the Vārāhasaṃhitā.\nThus ends the fourth pada of the first adhyaya of the Brahmasūtrabhāṣya composed by the revered Ānandatīrtha Bhagavatpāda.",
    "2.1.8": "By ‘In the beginning this was non-being only’ and ‘From non-being, being was born’ and the like, a contradiction arises, since non-being is declared to be the cause. Therefore he says: ‘If you say non-being, no, because it is mere negation.’ Because it is mere negation, it is not reasonable that non-being be a cause. The Vedic statement that non-being is a cause is contrary to reason, and this is refuted here. Although all words are harmonised in Brahman, non-being might be reached because another is also accepted as denoted in a secondary sense, by ‘because of dependence on him, it has meaning’ and the like. Likewise, a doctrine of non-being that is reached through Śruti is refuted here, since it is rejected beyond mere convention. In effect, the contradiction with reason is also removed.",
    "2.4.1": "By this pada he removes the contradictions among the Śruti texts, together with reasoning. In the Kāṣāyaṇa Śruti, ‘The breaths alone were here in the beginning; from them the elements were born; from the elements the egg, and within the egg these worlds; thus the breaths alone are beginningless, the breaths are eternal’, the non-origination of the breaths appears. ‘There is no material cause of the senses; therefore non-origination is held; yet creation made from a material cause is seen in all worlds’: so in the Bhaviṣya Parva. And also: ‘From him are born breath, mind and all the senses.’ Therefore it is said: ‘So also the breaths.’ As ether and the rest are born from the Supreme Self, so are the breaths also.",
}


def main():
    d = json.loads(F.read_text(encoding="utf-8"))
    U = {u["ref"]: u for u in d["units"]}
    for ref, text in T.items():
        u = U[ref]
        m = next(p for p in u["parts"] if p["role"] == "mula")
        b = next(p for p in u["parts"] if p["role"] == "bhashya")
        b["english"] = text
        u["english"] = (m["english"] + "\n" + text) if m.get("english") else text
    d["notes"] += " [2026-10-09: Subba Rau abridges Madhva's bhashya on 1.1.24, 1.3.1, 1.4.29, 2.1.8 and 2.4.1 and skips the quoted texts; the english of the commentary in those five units was replaced with a full translation written for this corpus (Claude).]"
    if not DRY:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
