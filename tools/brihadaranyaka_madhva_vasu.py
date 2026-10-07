"""Restore three Brihadaranyaka Madhva bhashya units Sonde does not translate (he gives only the first line of each), with english from Vasu's 1916 'Madhva's Commentary' blocks (public domain, archive.org 1974 AMS reprint, OCR cleaned by hand).

Skipped: the Panchagni unit (8th adhyaya, 5th brahmana); Vasu's block there mixes in his own notes.
"""
import json
import subprocess
from pathlib import Path

REL = "upanishads/brihadaranyaka_madhva.json"

VASU = {
    "चतुर्थोऽध्यायः / वंशब्राह्मणम्": "It has been said in the Brahmanda Purana that Parasarya and Jatukarnya are the two sons of Parasara; and they were born of a Brahman wife of his. So the word Parasarya in the mantra is a different person from Krisna Dvaipayana Veda Vyasa. It has been said in the Garuda Purana that Brahma studied this Brahmavidya from Hayagriva who is no other than the supreme Brahman Visnu; and Sanaka got it from Brahma. So it is not that (Paramesthi Virat) got this vidya from Brahma the Hiranyagarbha.",
    "पञ्चमोऽध्यायः / भुज्युब्राह्मणम्": "Pariksitas are Pradyumnas. It is Pradyumna whose name is Kama. It is He who has been termed Pariksita. Lord Visnu is called Pariksita, because it is He who sees all; and Pariksita means the son of Pariksit, Kamadeva. Indras are called Asvamedhins, because it is they who performed a hundred sacrifices each. It has been said in the Vedas that one and the same is the place of residence of all the Kamadevas, and all the Indras, that existed in the past and who will flourish in the future. As the terms Indra and Garuda are synonymous, therefore, the term Indra, in the Mantra, stands for Garuda and not for Indra (the performer of hundred sacrifices). Garuda has two forms, one of a bird, and the other of a Purusa (man). Garuda, though of the form of a Purusa, assumes the form of a bird and carries the Kamadevas and makes them over to Vayu for their Mukti. Vayu accepts them in his own body and takes them to Lord Visnu, named Pradyumna, in whom there are all the Indras that have attained Mukti by performing Asvamedha sacrifices. It is in this way that Vayu gives Mukti. Thus the Almighty Vayu is superior to all, because He leads up (1) the devas, (2) the rsis, (3) the Pitris, (4) the Yaksas, (5) the Gandharvas, (6) men, (7) snakes and (8) the Asuras to Mukti. It is this Vayu who leads up all the (1) Supernas, (2) Idas, (3) Sesas and (4) Indras and (5-8) their wives to Mukti. Vayu is, therefore, called Vyasti, the Deliverer of the eight classes of devas, etc., and He is called Samasti, the Deliverer of the eight classes of Suparnas, etc. Whoever knows this Vayu, how he is Vyasti and how he is Samasti, and that the Lord Hari only is superior to him, gets Mukti. Thus in Parama Samhita.\nBy the word Charaka it is to be understood one who travels as a pilgrim; but others explain it - one who is travelling as a Brahmacharin (a student). The word Ahan has many meanings, such as a Muhurta, a month, a day, illumination or shining, knowledge, strength, etc. But here it is to be taken in the sense of a Muhurta, which is a short space of time, one and seven-eighth of a Ghati. It is generally one-thirty-second part of a day. The sun's car travels [figure unclear in the scan] Yojanas a day in the sky; and the wheel of his car goes over that distance and a third more. This measurement is according to the men of Kritayuga. It is all light on both sides of the sun, wherever he may be at day or night. Up to this Loka, there is twice as many Yojanas, the world of darkness called Tamasloka. It is also called Prithivi, because of its hardness. Beyond that, there is the ocean, called Mandodaka, which is twice as extensive as the Tamoloka. Thus the extremity of the egg is fifty krors of Yojanas wide. Then is the golden egg split up by the Lord Hari; there is this cut in the sphere fine like the edge of a razor. Thus has been said in the Tatvasamhita - that Suparna gives over the Kamadevas to Vayu, who gives them Mukti.",
    "अष्टमोऽध्यायः / प्रथमं ब्राह्मणम्": "Vayu was the leader of the Devas, without whom they were all unable to preserve their existence. The devas quarrelled over their superiority; every one said - I am superior to others. Thus quarrelling, they went to the Lord Narayana. The Lord said - 'Amongst you he must be regarded to be superior on whose departure the others will not be able to maintain their existence.' On hearing this, all the gods came back. They all went out of the body separately, one after the other, in order to ascertain which was their chief. Suparna, Sesa, Rudra, Indra, Surya, &c., went out separately, one after the other, of the body of Brahma, but the body did not become a corpse; the rest of the gods remained in the body, even though one went out of it at a time. When Prana was about to go out of the body, the rest of the gods could not maintain their position there. Brahma cannot exist without Prana, and Prana cannot exist without Brahma. They are mutually dependent upon each other; how could then the rest live without Prana? Then all the gods admitted that Prana was their superior.",
    "अष्टमोऽध्यायः / पञ्चमं ब्राह्मणम्": None,
}

old = json.loads(subprocess.run(["git", "show", "bf2d645^:" + REL], capture_output=True, text=True, check=True).stdout)
oldu = {u["ref"]: u for u in old["units"]}
order = [u["ref"] for u in old["units"]]
d = json.loads(Path(REL).read_text(encoding="utf-8"))
have = {u["ref"] for u in d["units"]}
for ref, en in VASU.items():
    if ref in have:
        continue
    u = dict(oldu[ref])
    u["english"] = en
    k = order.index(ref)
    idx = {x["ref"]: i for i, x in enumerate(d["units"])}
    prev = next((order[j] for j in range(k - 1, -1, -1) if order[j] in idx), None)
    d["units"].insert(idx[prev] + 1 if prev else 0, u)
n = d["notes"]
a = n.index("[4 Sanskrit units have no english") if "[4 Sanskrit units have no english" in n else -1
b = n.index("]", a) + 1 if a >= 0 else 0
d["notes"] = (n[:a] if a >= 0 else n) + "[Three bhashya units (Vamsa, Bhujyu, 8th adhyaya 1st brahmana) take their english from Vasu 1916 (Madhva's Commentary blocks, public domain), because Sonde translates only their first line; it is Vasu's explanatory rendering, hand-cleaned from the OCR. The Panchagni unit (8th adhyaya, 5th brahmana, 'द्युपर्जन्यधरा...') is kept with Sanskrit only: Vasu's block there mixes in his own notes.]" + n[b:]
Path(REL).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("restored", len(VASU))
