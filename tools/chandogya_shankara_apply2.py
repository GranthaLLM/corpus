"""Second pass of chandogya_shankara_apply.py for the 16 units whose alignment was rejected by its thresholds. Each was
inspected by hand: where the old english had lost lines of Jha's translation, the full text is taken from the alignment;
a few units are special cases (see comments).
Run from corpus/: GRANTHA_WL=<dir>/ python3 tools/chandogya_shankara_apply2.py [--dry]"""
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv
F = ROOT / "upanishads" / "chandogya_shankara.json"
WL = pathlib.Path(os.environ["GRANTHA_WL"])

COUNTER = re.compile(r"\s*[—-]+\s*\(\d+(?:\.\d+)?\)\s*(?=\n|$)")

TAKE = ["1.6.2-1.6.3", "1.7.2", "3.6.1", "3.18.6", "4.7.1", "intro-4.16", "intro-5.3", "5.24.5", "6.6.3",
        "8.6.6-intro-8.7", "8.10.3", "8.10.4"]

TAIL_3_19 = (
    "It has been explained above how Vāyu and Prāṇa are to be viewed as the ‘feet’ of Brahman. Now proceeds the teaching that these same Vāyu and Prāṇa are "
    "to be meditated upon as Brahman itself. The story has been introduced for the purpose of making the teaching easily intelligible, and also for the "
    "purpose of laying down the procedure by which the Teaching is to be imparted and received; and the story also shows how the attainment of the "
    "knowledge of the Teaching is to be brought about by such means as faith, giving of food, absence of haughtiness, humility and so forth."
)


def clean(t):
    return "\n".join(l.strip() for l in COUNTER.sub("", t).strip().split("\n"))


def main():
    R = {}
    for i in range(1, 9):
        R.update(json.loads((WL / f"chand_repunct_{i}.json").read_text(encoding="utf-8")))
    d = json.loads(F.read_text(encoding="utf-8"))
    U = {u["ref"]: u for u in d["units"]}

    for ref in TAKE:
        U[ref]["english"] = clean(R[ref]["new"])

    # the alignment spans the mula of 3.9 and 3.10, which have units of their own
    lines = [l for l in R["3.8.4"]["new"].split("\n") if not re.search(r"\((?:9|10)\.\d\)\s*$", l)]
    U["3.8.4"]["english"] = clean("\n".join(lines))

    # the alignment stops before the introduction to chapter 4; the old text of that part is repunctuated by hand
    U["3.19.4-intro-4.1"]["english"] = clean(R["3.19.4-intro-4.1"]["new"]) + "\n" + TAIL_3_19

    # 2.3.1 lost the end of its mula and the commentary on Pratihara and Nidhana, which had slipped into 2.3.2
    new = R["2.3.2"]["new"].split("\n")
    assert new[0].startswith("The Lightning and Thunder are the Pratihāra; because both") and new[1].startswith("The Cessation is the Nidhana. One who")
    pratihara = COUNTER.sub("", new[0]).strip()
    nidhana_com = re.search(r"\nCessation is the Nidhana; because both represent the end of their respective processes\.", R["2.3.2"]["new"]).group(0).strip()
    e1 = U["2.3.1"]["english"].split("\n")
    assert e1[0].endswith("are the Pratihāra.")
    e1[0] += " The Cessation is the Nidhana."
    U["2.3.1"]["english"] = "\n".join(e1 + [pratihara, nidhana_com])
    rest = new[1].replace("The Cessation is the Nidhana. ", "") + "\n" + R["2.3.2"]["new"].split("\n", 2)[2].split("\n", 1)[1].split("The reward of such meditation")[0] if False else None
    body = R["2.3.2"]["new"].split("\n", 1)[1]
    first, second = body.split("\n", 1)
    first = first.replace("The Cessation is the Nidhana. ", "")
    second = second.replace("Cessation is the Nidhana; because both represent the end of their respective processes.—", "")
    U["2.3.2"]["english"] = (first + "\n" + second).strip()

    d["notes"] += (
        " [Punctuation pass 2 2026-10-13: 14 more units were re-aligned to Jha by hand-checked rules (their english had lost lines, or carried text of the "
        "neighbouring unit). 3.8.4 had its Jha text interleaved with the mula of 3.9 and 3.10 and took only its own part; 2.3.1 regained the end of its mula "
        "and the Pratihara and Nidhana commentary, which had slipped into 2.3.2; the second half of 3.19.4-intro-4.1 was punctuated by hand. Colophon units "
        "keep their formulaic english.]"
    )
    if not DRY:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for r in TAKE + ["3.8.4", "3.19.4-intro-4.1", "2.3.1", "2.3.2"]:
        print("##", r, len(U[r]["english"]))


if __name__ == "__main__":
    main()
