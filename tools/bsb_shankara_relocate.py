"""Relocate Gambhirananda's English for bsb_shankara 1.1.20, 1.2.6, 1.1.22 and 1.2.7.
The commentary on 1.1.20 had been attached to 1.2.6 (and 1.2.6's own commentary was missing), and the preamble of Topic 8 (1.1.22) sat inside 1.2.7.
Text is the book's own (archive.org brahma-sutra-bhasya-of-sankaracharya-swami-gambhirananda), joined from its OCR lines.
Run from corpus/: python3 tools/bsb_shankara_relocate.py [--dry]"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv
F = ROOT / "philosophical" / "bsb_shankara.json"

T120 = "Topic 7: THE BEING INSIDE Doubt : It is stated in the Upanipd: \"Now, again, He, the Puru$a that is seen in the sun is golden in colour; His beard is golden, hair is golden, everything up to the tip of the nails is golden. His eyes are like the pink lotus that is itself as pink as the seat of a monkey. His name is ut (uprisen). This Purina, that is such, remains lifted above all sins. Anyone meditating thus does certainly rise above sins\" (Ch. I. vi. 6-8); \"This is the meditation on the divine plane\" (ibid.); \"Then follows the meditation on the bodily plane. He, the Puru$a, that is seen in the eye\" etc. (Ch. I. vii. 5-8). Here arises a doubt: Is the Puru$a (lit. person), who is to be worshipped in the sun and the eyes, a human being who had attained a high eminence on account of the perfection of his meditation and action, or is He the ever existing God? What is the conclusion to be arrived at? Opponent: He must be a transmigrating soul. Why? Because the Upani$ad mentions his form. For instance, such a form as possession of golden beard is mentioned for the person in the sun. For the person in the eye also we get that very form by a process of extension shown in, \"Of this One that is such, the form is the same as of that One\" (Ch. I. vii. 5) . Not that the supreme Lord can reasonably have any form, for the Upani$ad says, \"Soundless, touchless, formless, undiminishing\" (Ka. I. iii. 15). This conclusion is supported by the mention of a place of residence in the texts: \"He that is in the sun\" (Ch. I. vi. 6), \"He that is in the eye\" (Ch. I. vii.). No residence can be asserted for the supreme Lord who is without any support, exists in His own glory, and is all-pervasive. There are also these Vedic texts in support: \"On what, 0 venerable sir, is He seated? On His own glory\" (Ch. VII. xxiv. 1), \"He is allpervasive like space and is eternal\". There is this additional reason, that a limit to His glory is specified in the texts, \" (He the Purina in the sun) rules over the worlds that are above the sun and also over the things enjoyable to the gods\" (Ch. I. vi. 8), where a limit is set to the majesty of the person in the sun; and \"He, who is such, rules over the worlds below the eyes as also over the things enjoyable to men\" (Ch. I. vii. 6) , where a limit is set to the majesty of the person in the eye. But it is not reasonable that God's majesty should have any limitation, since it is spoken of without any reservation in the text, \"This One is the lord of all, this One is the ruler (i.e. Death) of all beings, this One is the protector (i.e. Indra and other gods) of all beings; this One is like a dam that impounds so that these worlds (i.e. castes and stages of life etc.) may not get mixed up and destroyed\" (Br. IV. iv. 22). Therefore it is not the supreme Lord that resides in the sun and the eyes. Vedantin : Such being the position, we say: 20. The Being inside is God, His qualities having been taught. The PuruSal I s of whom the Upanigad speaks thus, \"He who is in the sun, He who is in the eye\" (Ch. I. vi, I. vii), must be God Himself, and not any transmigratory soul. Why? Because His qualities are taught. For it is God's qualities that are taught here. Thus having revealed the name of the Person in the sun by saying, \"His name is ut (the uprisen)\" (Ch. I. vi. 7), the derivation of that name is shown as arising from the fact of .remaining free from sin, in the text, \"This Puru$a that is such, remains lifted above all sins\". And that name, of which the derivation has been shown, is extended to the Person in the eye by saying. \"He has the same name as the other One has\" (Ch. I. vii. 5). Freedom from all sins is declared about the supreme Self alone in, \"That which is the Self beyond all sins\" (Ch. VIII. vii), and such sentences. Similarly in the text, \"He (the Person in the eye) is the Rk-mantra, the Selma-mantra, the uktha (a kind of hymn), the Yajur-mantra, the three Vedas\" (Ch. I. vii. 5), the Upanisad points out the identity of the Person in the eye with Rk, Selma, etc.; and that is possible only in the case of the supreme Lord, it being reasonable that He should be everything by virtue of His being the source of all. Again, commencing with the Rk and Selma mantras that are the same as the earth, fire, and so on, in the divine context, and speech, vital force, and so on, in. the physical context, it is said, \"Of Him the Rk and Selma mantras are two bodily joints. This is in the divine context\" (Ch. I. vi. 8). Similarly in the bodily context, \"He (the Person in the eye) has the same two joints as the Person in the sun\" (Ch. I. vii. 5). This becomes proper only if He is the Self of all. And the text, \"Therefore when these people play on the Vied (lute), they sing of Him; and hence they become prosperous\" (Ch. I. vii. 6), shows how He is present as music even in the human songs. This can be so if God is accepted as that Person, as is shown in the Bhagavad-Giza, \"Whatever being there is great, prosperous, or powerful, that know thou to be a product of a part of My splendour\" (X. 41). Besides, the absolute power of ruling over the worlds and desires that is mentioned in the Upanipd, points to God. In answer to the objection that the reference in the Upani$ad to such forms as the possession of golden beard etc. does not befit God, we say: Even for God there may be forms created at His will out of Maya for the sake of favouring the aspirants, as is declared in the Smrti, \"0 Narada, it is a Maya, created by Me, thatyou see Me in this form possessed of all the substances and qualities. You must not understand Me thus\". On the contrary, when the divine aspect bereft of all qualities is spoken of, then the relevant text runs thus: \"Soundless, touchless, formless, and undiminishing\" (Ka. I. iii. 15), and so on. But since God is the cause of everything, He is sometimes spoken of, for the sake of adoration, as possessed of certain mundane qualities, as in, \"He is possessed of all (good) action, all (good) des;res, all (good) smell, all (good) tastes\" (Ch. III. xiv. 2), and so on. In the same way there can be the mention of His golden beard. As for the criticism that He cannot be God, since a residence is mentioned, we say, even for the One who is established in His own glory, there can be an instruction about some seat for the sake of adoration; for being all-pervasive like space, He can very well dwell inside everything. The mention of the limitation to His majesty also occurs with reference to the bodily and divine contexts for the sake of worship. Therefore God Himself is spoken of as residing within the eye and the sun."
T126 = "The embodied soul and the supreme Self are shown differently in the Smrti also: \"The Lord, 0 Arjuna, dwells in the hearts of all beings, causing all beings by His Maya to revolve, (as if) mounted on a machine\" (Gita, XVIII. 61). Here the opponent puts in: What is this entity, called the embodied soul different from the supreme Self, which is denied by the aphorism, \"The individual soul is not certainly referred to, because the qualities do not fit in with it\" (I. ii. 3) etc.? As a matter of fact, the Vedic texts, as for instance, \"There is no other witness but Him\" (Br. III. vii. 23), deny any Self other than the supreme Self. So also do the Smxti texts, as for instance, \"Me do thou also know, 0 descendant of Bharata, to be the knower of the kgetra (i.e. body) in all the k,etras\" (Gita, XIII. 2). Vedantin : To this we say: It is quite true that the supreme Self Itself, as delimited by the conditioning factors-body, senses, mind, intellect, etc.-is spoken of in a roundabout way as the embodied soul by the ignorant. The case is similar to the appearance of space, undivided though it is, as if divided owing to such conditioning factors as a pot, a jar, etc. And before obtaining the instruction about the unity of the Self as in, \"That thou art\" (Ch. VI. viii. 7), it is nothing incongruous to talk from that point of view in terms of such differences as are implied by subjects and objects. But once the unity of the Self is accepted, there will surely be an end to all empirical dealings, involving notions of bondage, liberation, etc."


def setpair(u, mula, bhashya):
    m = next(p for p in u["parts"] if p["role"] == "mula")
    b = next(p for p in u["parts"] if p["role"] != "mula")
    m["english"] = mula
    b["english"] = bhashya
    u["english"] = mula + "\n" + bhashya


def main():
    d = json.loads(F.read_text(encoding="utf-8"))
    U = {u["ref"]: u for u in d["units"]}
    setpair(U["1.1.20"], "The One inside (is God), for His qualities are taught.", T120)
    setpair(U["1.2.6"], "(This follows) from the Smrti also.", T126)

    u7 = U["1.2.7"]
    b7 = next(p for p in u7["parts"] if p["role"] != "mula")
    e = b7["english"]
    i = e.index("Topic 8: SPACE")
    j = e.index("the material space is meant.", i) + len("the material space is meant.")
    block = e[i:j].strip() + " Vedantin : Such being the position, we say:"
    b7["english"] = (e[:i] + e[j:].lstrip()).strip()
    u7["english"] = next(p for p in u7["parts"] if p["role"] == "mula")["english"] + "\n" + b7["english"]

    u22 = U["1.1.22"]
    m22 = next(p for p in u22["parts"] if p["role"] == "mula")
    b22 = next(p for p in u22["parts"] if p["role"] != "mula")
    b22["english"] = block + " " + b22["english"]
    u22["english"] = m22["english"] + "\n" + b22["english"]

    d["notes"] += (
        " [Relocation 2026-10-09: the commentary on 1.1.20 had been attached to 1.2.6 and 1.2.6's own commentary was missing; both now hold the right text from the "
        "Gambhirananda scan. The Topic 8 preamble that had been pasted into 1.2.7 now opens the commentary of 1.1.22.]"
    )
    if not DRY:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
