"""Add english for the nine Katha Shankara commentary passages Sastri's translation skips (2.1.4, 2.1.5, 2.1.12-14, 2.3.9-11, 2.3.19).
The translations are written for this corpus and named in the file notes.
Run from corpus/: python3 tools/shankara_katha_fill.py [--dry]"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv
F = ROOT / "upanishads" / "katha_shankara.json"

T = {
    "2.1.4": "Thinking that it is hard to know because of its extreme subtlety, he repeats this very matter again and again: ‘svapnānta’ means the middle of dream, that is, what is known in dream; likewise ‘jāgaritānta’ is the middle of waking, what is known in waking. By which Ātman the world perceives both the end of dream and the end of waking: all as before. Knowing that great, all-pervading Ātman, realising it directly in the form of the Self, ‘I am the Paramātman’, the wise man does not grieve.",
    "2.1.5": "Further: whoever knows this honey-eater, that is, the jīva who enjoys the fruits of action, the sustainer of the group of prāṇa and the rest, the Ātman, near, close at hand, as the ruler of the past and the future, that is, of the three times, thereafter, from that knowledge onward, does not wish to protect himself, since he has attained fearlessness. For as long as one stands amid fear and thinks of oneself as non-eternal, so long he wishes to protect himself; but when he knows the Ātman as eternal and non-dual, then who would wish to protect what, or from what? ‘This verily is That’ as before.",
    "2.1.12": "Again he speaks of that same Brahman which is under discussion: ‘of the measure of a thumb’, of the size of a thumb. The lotus of the heart is of the size of a thumb, and the Ātman limited by the inner organ lodged in its cavity is ‘of thumb size’, like the space in the middle of a bamboo joint of thumb length. ‘Puruṣa’: full, since by him all is filled. In the middle, in the body, he abides. Knowing him, the Ātman, the ruler of the past and the future, he does not shrink from it, and so on, as before.",
    "2.1.13": "Further: the Puruṣa of thumb size is like a flame without smoke; ‘without smoke’ is fitting, since the comparison is with light. He who is thus marked out by the yogis in the heart, the ruler of the past and the future, he alone, the eternal, the unchanging, is present today in living beings and will be so tomorrow as well; no other like him exists or will be born: this is the meaning. Thereby the view ‘This Ātman does not exist’ (I.i.20), though it is not reached by reasoning, is refuted by the Śruti in its own words, and so is the doctrine of momentariness.",
    "2.1.14": "Again he speaks of the fault of seeing difference in Brahman: as water falling on a rugged, high place runs down in different directions among the mountains, that is, scattered, perishes, so he who sees the qualities as distinct from the Ātman, seeing them separately in each body, runs after those very qualities, the distinctions of the bodies; he attains again and again only distinctions of body. This is the meaning.",
    "2.3.9": "How then is that which has no mark seen? It is said: his form does not stand within the range of sight; therefore no one sees this innermost Ātman with the eye. ‘Eye’ is mentioned to stand for all the senses. How then is he seen? By the heart, that is, by the intellect lodged in the heart; by the manīṣā, the intellect free from doubts, which rules (īṣṭe) the mind of the nature of volition and the like; by the mind, that is, by right vision in the form of reflection, he is made manifest, revealed. The sentence is completed thus: ‘the Ātman can be known’. Those who know this Ātman, Brahman, become immortal.",
    "2.3.10": "How is that state of heart and mind reached? Yoga for that purpose is taught: when, at which time, the five organs of knowledge, turned back from their objects, stand still in the Ātman alone (the senses such as hearing are called ‘jñāna’ because they serve knowledge), together with the mind, that is, with the inner organ which they follow and which is withdrawn from volition and the like, and the intellect, of the nature of determination, does not stir, does not act in its own functions, that state they call the highest.",
    "2.3.11": "That state, such as it is, they regard as Yoga, though it is really disunion (viyoga); for this state of the yogi is marked by separation from union with all evil. In this state the Ātman is established in its own nature, free from the superimposition of ignorance. ‘The steady holding of the senses’ means the firm, unmoving holding of the external and internal organs. ‘Careful’: free from negligence, ever striving for concentration, ‘then’, at that time, that is, when he has begun Yoga, as is understood from the context; for when the activities of the intellect and the rest have ceased there can be no negligence. Therefore carefulness is enjoined even before the activities of the intellect cease. Or: as soon as the holding of the senses is steady, then at once unrestrained carelessness becomes possible, and so it is said ‘then he becomes careful’. Why? Because Yoga ‘is the origin and the end’, that is, it is subject to arising and ceasing. Therefore carefulness must be practised to avoid its loss: this is the intention.",
    "2.3.19": "Now this prayer for peace is said in order to quiet any fault arising from the wrong conduct, through negligence, of pupil and teacher in the taking and giving of knowledge. ‘May He protect us both’: may he guard us both by revealing the nature of knowledge. Who? That very Supreme Lord revealed by the Upaniṣad. Further, ‘may He nourish us both’ by revealing its fruit. Together let us bring about the vigour, the capacity produced by knowledge. Further, ‘may what we have studied be bright’: may what we, two bright ones, have studied be well studied; or, may what has been studied by us be exceedingly bright and powerful. ‘May we not hate’: may teacher and pupil not feel hatred toward each other on account of faults of study and teaching committed through negligence. The threefold ‘peace’ is for the quieting of all faults.\nThus ends the commentary on the Kaṭha Upaniṣad by Śrī Śaṅkara Bhagavat, disciple of Śrī Govinda Bhagavatpāda, the revered Paramahaṃsa wandering teacher.",
}


def main():
    d = json.loads(F.read_text(encoding="utf-8"))
    U = {u["ref"]: u for u in d["units"]}
    for ref, text in T.items():
        u = U[ref]
        m = next(p for p in u["parts"] if p["role"] == "mula")
        b = next(p for p in u["parts"] if p["role"] == "bhashya")
        m["english"] = u["english"]
        b["english"] = text
        u["scope"] = "mula+commentary"
        u["sanskrit"] = m["sanskrit"] + "\n" + b["sanskrit"]
        u["english"] = m["english"] + "\n" + text
    d["notes"] += (
        " [2026-10-09: Sastri's translation skips Śaṃkara's commentary on 2.1.4, 2.1.5, 2.1.12, 2.1.13, 2.1.14, 2.3.9, 2.3.10, 2.3.11 and 2.3.19; the english of "
        "that commentary in those nine units was translated for this corpus (Claude), in Sastri's plain style, and the units are now mula+commentary.]"
    )
    if not DRY:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
