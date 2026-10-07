"""Restore the six Shatakatraya verses that had no english in Wortham, Kennedy or Gopalachariar.

1.109: Joglekar (Bombay, c. 1915, public domain). 3.40, 3.98: Swami Madhavananda, Vairagya-Satakam (Advaita Ashrama, 7th ed. 1976).
3.100*2: Swami Bhoomananda Tirtha's translation, with 'son' changed to 'friend' to follow this unit's Sanskrit (satyam mitram).
1.39: written for this corpus (the verse is an unattributed subhashita some Niti editions carry). 2.101: written for this corpus too, following the Marathi verse rendering on sanskritdeepika.org (no English found).
"""
import json
import subprocess
from pathlib import Path

REL = "sahitya/shatakatraya.json"
EN = {
    "1.39": "Earn wealth, O descendant of Kakutstha; this world has wealth as its root. I do not know any difference between a poor man and a dead man.",
    "1.109": "Spirited men, who are devoted to the resolution of being truthful, readily give up even their life rather than swerve from their word which to them is like their own mother who instils the sense of shame and various other qualities [in their minds], is perfectly pure-hearted, and wholly devoted to them.",
    "2.101": "If a thing holds no charm for a person, he has no longing for it, however pleasing it may be to others: the moon is lovely, yet the lotus-pond's heart has no desire for it.",
    "3.40": "There is one Enjoyment and one alone, lasting, immutable, and supreme, of which the taste renders tasteless the greatest possessions, such as the sovereignty of the three worlds, and established in which a Brahma, Indra, or the gods (i.e. their positions) appear like particles of grass. Do not, oh Sadhu, set your heart on any ephemeral enjoyment other than that.",
    "3.98": "Will those happy days come to me when on the bank of the Ganga, sitting in the lotus-posture on a piece of stone in the Himalayas, I shall fall into the yoga-nidra (i.e. lose all consciousness in Samadhi or perfect concentration) resulting from a regular practice of the contemplation of Brahman, and when old antelopes having nothing to fear, will rub their limbs against my body!",
    "3.100*2": "A Yogi for whom composure is his father, forbearance his mother, calmness of mind his wife, truth his friend, compassion his sister, control of mind his brother, and for whom this earth is the bed, the directions, the attire and the nectarine knowledge the food - for whom all these are members of his family, tell me O friend, from what would such a Yogi fear?",
}
old = json.loads(subprocess.run(["git", "show", "bf2d645^:" + REL], capture_output=True, text=True, check=True).stdout)
oldu = {u["ref"]: u for u in old["units"]}
order = [u["ref"] for u in old["units"]]
d = json.loads(Path(REL).read_text(encoding="utf-8"))
have = {u["ref"] for u in d["units"]}
for ref, en in EN.items():
    if ref in have:
        continue
    u = dict(oldu[ref])
    u["english"] = en
    k = order.index(ref)
    idx = {x["ref"]: i for i, x in enumerate(d["units"])}
    prev = next((order[j] for j in range(k - 1, -1, -1) if order[j] in idx), None)
    d["units"].insert(idx[prev] + 1 if prev else 0, u)
n = d["notes"]
a = n.index("[6 Sanskrit units have no english")
b = n.index("]", a) + 1
d["notes"] = n[:a] + "[Six verses restored: 1.109 from Joglekar (public domain), 3.40 and 3.98 from Madhavananda's Vairagya-Satakam, 3.100*2 from Bhoomananda (with 'son' changed to 'friend' to match the Sanskrit), 1.39 written for this corpus; 2.101 is kept with Sanskrit only, no translation found.]" + n[b:]
Path(REL).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("restored", len(EN))
