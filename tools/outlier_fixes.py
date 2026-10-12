"""Fixes found by reading the length-ratio outliers (2026-10-09).
- bhagavata_uddhava: the unit holding Uddhava's six-verse question had only the first verse's Sanskrit; Sanskrit of 11.19.27-31 added (Setutila skandha_11), ref 11.19.26-31.
- yaksha_prashna 23497, vidura_niti 27285: english carried narrative prose that has no Sanskrit row; cut to the part the row's Sanskrit covers.
- bg_shankara 18.25: english was OCR-garbled; replaced with a translation written for this corpus.
- bsb_madhva 1.3.43: english was a garbled fragment of the first half; replaced with a translation written for this corpus.
Run from corpus/: python3 tools/outlier_fixes.py [--dry]"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv

UDDHAVA_SA = """उद्धव उवाच
यमः कतिविधः प्रोक्तो नियमो वाऽरिकर्शन।
कः शमः को दमः कृष्ण का तितिक्षा धृतिः प्रभो॥ ११/१९/२६॥
किं दानं किं तपः शौर्यं किं सत्यं ऋतमुच्यते।
किमन्नं तृप्तिजनकं किञ्च शौचं जनार्दन॥ ११/१९/२७॥
कस्त्यागः किं धनं श्रेष्ठं को यज्ञः का च दक्षिणा।
पुंसः किं स्विद् बलं श्रीमद् भगो लाभश्च केशव॥ ११/१९/२८॥
का विद्या ह्वीः परा का श्रीः किं सुखं दुःखमेव च।
कः पण्डितः कश्च मूर्खः कः पन्था उत्पथश्च कः॥ ११/१९/२९॥
कः स्वर्गो नरकः कः स्वित् को बन्धुरुत किं गृहम्।
क आढ्यः को दरिद्रो वा कृपणः कः क ईश्वरः।
एतान् प्रश्नान् मम ब्रूहि विपरीतं च सत्पते॥ ११/१९/३१॥"""

G1825 = (
    "Without regard to the consequence, the loss, the injury and human capacity, the action that is begun out of delusion is said to be tamasic.\n"
    "‘Anubandha’ is that which will come about afterwards, the consequence; ‘kṣaya’ is the loss, the exhaustion of strength or of wealth that would result in doing the action; "
    "‘hiṃsā’ is injury to living beings; and ‘pauruṣa’ is human effort, one’s own capacity, in the form ‘I am able to complete this action’. "
    "Disregarding these, from the consequence down to capacity, the action that is undertaken out of delusion, that is, from want of discrimination, that is said to be tamasic, produced from tamas."
)
B1343 = (
    "‘This is the eternal greatness of the Brāhmaṇa’: by this, eternal greatness is found even of a Brāhmaṇa; and as for that Brāhmaṇa, by the word ‘aja’ in "
    "‘He indeed is that great unborn Self’ it would follow that he is Viriñci; and since the attainment of a position by the gods through knowledge and works is also suggested, "
    "it would follow that there is one above them too. Therefore he says: ‘from words such as lord’. From such words as ‘Lord of all, ruler of all, he who is “not this, not this”’, "
    "the eternal greatness belongs to Viṣṇu alone. From such Śruti texts as ‘And he is lord of immortality, which grows by food’, ‘The seven half-wombs, the seed of the world, "
    "abide by Viṣṇu’s command in their appointed quarters’ and ‘That which was unheard before’, those words belong to him alone.\n"
    "Thus ends the third pada of the first adhyaya of the Brahmasūtrabhāṣya composed by the revered Ānandatīrtha Bhagavatpāda."
)


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def save(rel, d):
    if not DRY:
        (ROOT / rel).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main():
    rel = "sahitya/bhagavata_uddhava.json"
    d = load(rel)
    u = next(x for x in d["units"] if x["ref"] == "11.19.26")
    u["sanskrit"] = UDDHAVA_SA
    u["ref"] = "11.19.26-31"
    d["notes"] += " [2026-10-09: the unit for Uddhava's question 11.19.26-31 now holds the Sanskrit of all six verses; it had only the first, while the english (Prabhupada's) covers all six.]"
    save(rel, d)

    rel = "sahitya/yaksha_prashna.json"
    d = load(rel)
    u = next(x for x in d["units"] if x["ref"] == "23497")
    u["english"] = u["english"][: u["english"].index("The Yaksha said")].rstrip()
    d["notes"] += " [2026-10-09: english of row 23497 cut to the part its Sanskrit covers; the narrative prose that followed has no Sanskrit row.]"
    save(rel, d)

    rel = "sahitya/vidura_niti.json"
    d = load(rel)
    u = next(x for x in d["units"] if x["ref"] == "27285")
    u["english"] = u["english"][: u["english"].index("Sudhanwan said, 'Let alone")].rstrip()
    d["notes"] += " [2026-10-09: english of row 27285 cut to the part its Sanskrit covers; the later speeches of Virochana and Sudhanwan have no Sanskrit row.]"
    save(rel, d)

    rel = "philosophical/bg_shankara.json"
    d = load(rel)
    u = next(x for x in d["units"] if x["ref"] == "18.25")
    verse = G1825.split("\n")[0]
    comm = G1825.split("\n", 1)[1]
    u["english"] = G1825
    for p in u.get("parts") or []:
        if p["role"] == "mula":
            p["english"] = verse
        elif p.get("sanskrit"):
            p["english"] = comm
    d["notes"] += " [2026-10-09: english of 18.25 was OCR-garbled and was replaced with a translation written for this corpus (Claude).]"
    save(rel, d)

    rel = "philosophical/bsb_madhva.json"
    d = load(rel)
    u = next(x for x in d["units"] if x["ref"] == "1.3.43")
    u["english"] = B1343
    for p in u.get("parts") or []:
        if p.get("sanskrit"):
            p["english"] = B1343
    d["notes"] += " [2026-10-09: english of 1.3.43 was a garbled fragment and was replaced with a translation written for this corpus (Claude).]"
    save(rel, d)


if __name__ == "__main__":
    main()
