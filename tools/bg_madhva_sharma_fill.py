import json
from pathlib import Path

F = Path(__file__).resolve().parent.parent / "philosophical" / "bg_madhva.json"

SHARMA = {
    "8/14-16": (
        "'Nityayukta' stands for one who goes on with the means of Yoga as well as for one who has "
        "successfully completed his sadhanas. Praises the attainment of the Lord. The highest Siddhi is "
        "the attainment of the Lord Himself. Riddance of births and deaths is the result of attaining Him. "
        "There is no return (to samsara) from the abode of the Caturmukha-Brahma on Mount Mahameru (and "
        "elsewhere and the worlds beyond them such as Svetadvipa and Anantasana) as well as from Janaloka "
        "and others beyond. This has been made clear in Narayana Gopalakalpa: Beginning with the abode of "
        "Brahma on Mt. Meru and with Janaloka (and others beyond) there is no rebirth on earth."
    ),
    "16/18-20": (
        "\"Hating Me present in one's own body and in others\" - This is said with reference to the insolent "
        "attitude of the Asuric-natured, who tell themselves \"God is not the causal agent of any of our "
        "actions. If there be such a God, let Him make me do a thing here and now when I am doing nothing or "
        "stop me from doing the thing I am doing.\" Of such conceited creatures, the Yaska Sruti says: Anyone "
        "who says if God be the one who makes creatures do a thing let Him make me do something now when I am "
        "not doing anything - to such a one, the reply shall be \"thou shalt be consigned to the nether regions\"."
    ),
    "17/8": (
        "Foods promoting happiness (priti) do so immediately after they are consumed while those that are "
        "'agreeable' (hrdyam) are pleasing to the sight (darsana) while the 'sthira' (substantial) are those "
        "which take time to be digested and confer permanent benefits after being well digested, such as ghee."
    ),
    "18/62": (
        "The reference to Isvara here (as existing in the hearts of all) and exhorting Arjuna to seek refuge "
        "in Him and attain His eternal place - all in the third person is to be explained in the manner of "
        "Bhima's words addressed to Drona, on the battle field, in the Mahabharata (VII. 102. 86) as an "
        "example of referring to one's own self in the third person by way of stating a decisive fact that is "
        "unalterable and will happen come what may (niscitartha)."
    ),
}
NOTE = (
    " [Bhashya english of 8/14-16, 16/18-20, 17/8 and 18/62 filled from B.N.K. Sharma 1989 (Anandatirtha "
    "Pratishthana, archive.org OCR), the only source that renders those bhashya passages; Sharma is an "
    "expository rendering, lightly OCR-cleaned, and the four units therefore mix Sonde (verse, tatparya) "
    "with Sharma (bhashya). 16/18-20 now has scope mula+commentary. 12/17-18 and the intro are not in Sharma.]"
)

d = json.loads(F.read_text(encoding="utf-8"))
by = {u["ref"]: u for u in d["units"]}
for ref, en in SHARMA.items():
    u = by[ref]
    b = next(p for p in u["parts"] if p["role"] == "bhashya")
    assert b.get("sanskrit") and not b.get("english"), ref
    b["english"] = en
    both = [p for p in u["parts"] if p.get("sanskrit") and p.get("english")]
    u["sanskrit"] = "\n".join(p["sanskrit"] for p in both)
    u["english"] = "\n".join(p["english"] for p in both)
    u["scope"] = "mula+commentary"
d["notes"] += NOTE
if "in_copyright_or_unclear" not in d["english_rights"]:
    d["english_rights"].append("in_copyright_or_unclear")
F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
