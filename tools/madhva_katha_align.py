"""Align english with sanskrit in katha_madhva. Source: wisdomlib Vasu pages (kathopanishad-madhva-commentary).
Run from corpus/: python3 tools/madhva_katha_align.py [--dry]"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv
F = ROOT / "upanishads" / "katha_madhva.json"


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


def mula_only(u, text):
    u["english"] = text
    if u.get("parts"):
        part(u, "mula")["english"] = text


def commentary(u, bhashya_en):
    m, b = part(u, "mula"), part(u, "bhashya")
    b["english"] = bhashya_en
    u["scope"] = "mula+commentary"
    u["sanskrit"] = m["sanskrit"] + "\n" + b["sanskrit"]
    u["english"] = m["english"] + "\n" + bhashya_en


def main():
    d = json.loads(F.read_text(encoding="utf-8"))
    U = {u["ref"]: u for u in d["units"]}

    vasu_49 = part(U["2/1/10"], "bhashya")["english"].split("\n", 1)[1]
    vasu_411 = part(U["2/1/11"], "bhashya")["english"]
    vasu_52 = part(U["2/2/2"], "bhashya")["english"].split("\n", 1)[1]
    vasu_510 = part(U["2/2/10"], "bhashya")["english"]
    vasu_511 = part(U["2/2/11"], "bhashya")["english"]
    for r in ("1/2/8", "2/1/10", "2/1/11", "2/2/2", "2/2/10", "2/2/11"):
        drop_part(U[r], "bhashya")

    vasu_411 = re.sub(r"^\[[^\]]*\]\n", "", vasu_411)
    vasu_411 = re.sub(r"\n\[The word iva has three meanings[^\]]*\]", "", vasu_411)
    vasu_411 = re.sub(r"\n\(The word Kiñcana being a Pronoun.*?\n(?=Lest one)", "\n", vasu_411, flags=re.S)
    vasu_510 = vasu_510.strip()
    vasu_511 = re.sub(r" \[But the Jīva and Īśvara[^\]]*\]\.", "", vasu_511)
    vasu_511 = re.sub(r"\n\[Having explained the above three verses[^\]]*\]", "", vasu_511)
    vasu_511 = re.sub(r"\n\[If the Jīvas as reflections have no beginning[^\]]*\]", "", vasu_511)
    vasu_511 = re.sub(r" \[The āsīt shows[^\]]*\]", "", vasu_511)
    vasu_511 = re.sub(r"\n\[If the Lord as the Inner Self of all[^\]]*\]\.?", "", vasu_511)
    vasu_511 = re.sub(r" \[[^\]\n ]{1,12}\]", "", vasu_511)
    vasu_52 = vasu_52.replace("[He is in?????]called Vyoma", "He is in Prakṛti called Vyoma")
    vasu_52 = re.sub(r" \[[^\]\n ]{1,12}\]", "", vasu_52).replace("universeis", "universe is")
    assert "?" not in vasu_52 and "[" not in vasu_511 and not vasu_411.startswith("[")

    u = U["2/1/14"]
    mula_only(u, u["english"].split("\n")[0])
    u = U["2/1/15"]
    b = part(u, "bhashya")
    vasu_414 = "As the rain water falling on the tops of hills quickly runs down, similarly he who sees the attributes of Viṣṇu as separate from Him runs down quickly to Darkness."
    commentary(u, "\n".join([vasu_49, vasu_411, vasu_414, b["english"]]))

    u = U["2/2/5"]
    five = u["english"].split("\n")
    mula_only(u, five[0])
    u = U["2/2/6"]
    mula_only(u, u["english"].split("\n")[0].replace("6(a) ", ""))
    u = U["2/2/8"]
    mula_only(u, u["english"].split("\n")[0])
    u = U["2/2/14"]
    b = part(u, "bhashya")
    commentary(u, "\n".join([vasu_52, five[1], vasu_510, vasu_511, b["english"]]))

    commentary(U["1/2/9"], "\n".join(["The word Ananya means “he who does not realise that the Lord is separate (anya) and he is separate (anya).” If such a person teaches another, then there is no understanding of Brahman. Gati means knowledge. (In other words, the teaching of a person who is a monist, and does not know the difference between jīva and the Lord, and thinks them to be identical is anfractuous.) While if the “anya” or the person who realises that he is separate from the Lord, declares Brahman then there is understanding of Brahman: as the mantra (II. 9) says: “when declared by an Anya, there is clear knowledge, O dear.” So also in the Brahma Vaivarta Purāṇa “The man who does not know the difference between the jīvas and Viṣṇu, and those also who follow the teachings of such a person, can never get Supreme wisdom—jñāna—so long as they entertain this erroneous notion.”"]))
    commentary(U["1/2/17"], "This indestructible Brahman is called Viṣṇu. He is the Supreme and unchangeable, knowing Him as the Supreme, the refuge of all, the jīva undoubtedly gets liberation.")

    u = U["2/1/1"]
    mula = part(u, "mula")["english"].split("\n")[0]
    mula_en = u["english"].split("\n")[0]
    part(u, "mula")["english"] = mula_en
    b = part(u, "bhashya")
    b["english"] = "The root is “tṛṇu kātkaraṇe”, ‘to humiliate’, ‘to lay flat.’ Hence the word means to subdue and make low."
    u["english"] = mula_en + "\n" + b["english"]

    commentary(
        U["2/1/3"],
        "Now I shall tell thee this secret Brahman, and I shall also tell thee the condition of the Jīva after death: this is said in order to indicate the "
        "difference between the Jīva and Īśvara. The Jīva is that which experiences the fruits of action, and is subject to obscuration of consciousness in "
        "deep sleep, pralaya, etc. The Supreme Brahman is the Lord Viṣṇu who remains awake when all the Jīvas are asleep in the deep sleep of Pralaya or "
        "Suṣupti, etc.\n"
        "The Brahman is not affected by the Jīva’s entering the womb when re-incarnating.\n"
        "The Brahman is known rightly then only when He is known as separate from the Jīva.",
    )
    edit(U["2/1/5"], "always standing near the Jīva", "always standing near the Jīva, thereafter does not shrink (from anything). This verily is That.")
    commentary(
        U["2/1/5"],
        "Jīvam antikāt is Jīvasya antike, “near to the Jīva.” A thing cannot be near or distant to itself; it is only in relation to another object that a "
        "thing is said to be near or distant.",
    )

    edit(U["1/1/20"], "[The second and the third questions both relate to the mystery of the Lord. Yama answers the second question very promptly, but the third he answers with great reluctance.] ", "")
    edit(U["2/1/7"], re.search(r"\[The word Aditi in this verse[^\]]*\]\n?", part(U["2/1/7"], "bhashya")["english"]).group(0), "")
    for u in d["units"]:
        for h in [u] + (u.get("parts") or []):
            if h.get("english"):
                h["english"] = re.sub(r" \[[^\]\n]{1,30}\?\]", "", h["english"])
    edit(U["1/1/2"], "He reflected -", "He reflected:")
    edit(U["1/1/8"], "without any food;", "without any food.")
    edit(U["2/2/3"], "surround and adore", "surround and adore.")
    for u in d["units"]:
        for h in [u] + (u.get("parts") or []):
            if h.get("english"):
                h["english"] = re.sub(r"^—\s*", "", h["english"]).strip()

    d["notes"] += (
        " [Alignment pass 2026-10-09: Setutila holds Madhva's commentary on 2.1.10-15 in 2/1/15 and on 2.2.2-14 in 2/2/14, so Vasu's translation of both "
        "(which sat in english-only parts under 2/1/10, 2/1/11, 2/2/2, 2/2/10, 2/2/11, and in the english of 2/1/14 and 2/2/5) is gathered there, with his "
        "bracketed lead-ins and the damaged '?' span in 5.2 repaired from the Sanskrit; the Shankara readings in 1/2/8 were dropped and Vasu's commentary on "
        "1.2.8 moved to 1/2/9; 1/2/9, 1/2/17, 2/1/3 and 2/1/5 are mula+commentary with Vasu's translation of their commentary (2/1/3 and 2/1/5 from his "
        "bracketed explanations under 4.1); 2/1/1 lost a stray Sonde fragment that translated 2/1/2; second alternate translations in 2/2/6 and 2/2/8 dropped.]"
    )
    if not DRY:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
