"""Align english with sanskrit in isa_madhva, mandukya_madhva and kena_madhva.
Sources: wisdomlib Vasu pages (Isa, Mandukya, Kena) and Sonde's Kena PDF.
Run from corpus/: python3 tools/madhva_small_upanishads_align.py [--dry]"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv


def load(n):
    return json.loads((ROOT / "upanishads" / f"{n}.json").read_text(encoding="utf-8"))


def save(n, d):
    if not DRY:
        (ROOT / "upanishads" / f"{n}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def idx(d):
    return {u["ref"]: u for u in d["units"]}


def part(u, role):
    return next(p for p in u["parts"] if p["role"] == role)


def edit(u, old, new):
    hit = False
    for h in [u] + (u.get("parts") or []):
        e = h.get("english")
        if e and old in e:
            h["english"] = e.replace(old, new)
            hit = True
    assert hit, (u["ref"], old[:50])


def resync(u):
    ps = [p for p in u["parts"] if p.get("sanskrit") and p.get("english")]
    u["english"] = "\n".join(p["english"] for p in ps)


def set_mula(u, text):
    u["english"] = text
    if u.get("parts"):
        part(u, "mula")["english"] = text


def drop_part(u, role):
    u["parts"] = [p for p in u["parts"] if p["role"] != role]


def cut(s, start, end=None):
    i = s.index(start)
    j = len(s) if end is None else s.index(end, i) + len(end)
    return s[:i] + s[j:]


def cut_to(s, start, stop):
    i = s.index(start)
    return s[:i] + s[s.index(stop, i):]


def isa():
    d = load("isa_madhva")
    U = idx(d)

    manu = (
        "Manu called Svāyambhuva praised the Lord Viṣṇu when He appeared as Yajña, the son of Ākuti, with the verses of this Upaniṣad.\n"
        "Thus we learn from the Brahmāṇḍa Purāṇa: “Svāyambhuva Manu praised with collected mind Viṣṇu who had incarnated as his daughter’s son, "
        "and was named Yajña, by means of these verses of the Īśāvāsya Upaniṣad.\n"
        "“The ferocious Rākṣasas, who had come to devour him, as soon as they heard the chant of these mantras, could not bear (the strong vibrations "
        "of these) and so they left him unmolested, and thus he was delivered by Yajña from them. These Rākṣasas, who could not otherwise be destroyed, "
        "were killed by Yajña.\n"
        "“The Lord Hara had given two boons to these Rākṣasas, by which they had themselves become incapable of being slain; and they could kill with "
        "impunity everybody else. But Hari is Lord of all, and so He transcended Śiva also, for who is higher than He?”\n"
        "In the Bhāgavata Purāṇa also this is the meaning given to this Upaniṣad."
    )
    u = U["1"]
    b = part(u, "bhashya")
    b["english"] = manu + "\n" + b["english"]
    resync(u)
    edit(u, "Thus says the Brahmāṇḍa Purāṇa:—", "Thus says the Brāhma Purāṇa:—")
    edit(u, "Yiṣṇu", "Viṣṇu")
    edit(u, "all its motion? Since", "all its motion.’ Since")

    edit(U["3"], "Yamana Parana", "Vāmana Purāṇa")
    edit(U["4"], "lie surpasses", "he surpasses")
    edit(U["4"], "Brahmāṇḍa Parana", "Brahmāṇḍa Purāṇa")
    edit(U["6"], "Saṅkarāyaṇas", "Saukarāyaṇas")

    u = U["7"]
    edit(u, "\n(But verse 5 also expressed the same idea that Brahman is the support of all and is All-pervading—for the phrase ‘He is far, he is near, He is outside, He is inside’ denotes the same thing. What was then the necessity of verse 6, which expresses the same proposition? This objection is next answered by the commentator.)", "")
    edit(u, "ail creatures", "all creatures")
    edit(u, "Viṣnu everywhere", "Viṣṇu everywhere")
    edit(u, "All-pervading-ness of Brahman,", "All-pervading-ness of Brahman.")

    u = U["8"]
    b = part(u, "bhashya")
    b["english"] = cut(b["english"], "\nBut how can God who is without body create?")
    resync(u)
    edit(u, "Eternal and Kull", "Eternal and Full")

    m11 = part(U["11"], "bhashya")["english"].replace(" (and fail to??????????? their mistakes)", "")
    assert "?" not in m11
    drop_part(U["11"], "bhashya")
    u = U["14"]
    b = part(u, "bhashya")
    rest = b["english"].split("\n", 1)[1]
    rest = cut(rest, "\n[Having described")
    b["english"] = m11 + "\n" + rest
    resync(u)
    edit(u, "that oven among", "that even among")

    b15 = part(U["15"], "bhashya")["english"]
    drop_part(U["15"], "bhashya")
    u = U["16"]
    set_mula(
        u,
        "O All-full One! O Sole-wise One! O All-Judge! O Goal of the Wise! O Lord of Prajāpati! Expand my knowledge of the self, and increase my knowledge "
        "of the non-self, so that through Thy grace I may see that form of Thine which is the most auspicious. That yonder person who dwells in Asu (Life) "
        "is known by the name of Aham “I” (i.e., the Supreme) and Asmi “I am” (i.e., the only standard of existence.)",
    )
    ekarse = (
        "The word Ekarṣe means “O thou who art principally (eka), all knowledge and wisdom (ṛṣi).” The word ekarṣi is thus the name of Viṣṇu. "
        "Hari is called Yama because he controls and punishes all—He is the Great Judge. He is called Sūrya because he is the Goal of the wise (sūris). "
        "He is called Prājāpatya, because he is specially the Goal of Hiraṇyagarbha Prajāpati."
    )
    kratu = "He is Kratu because He is of the nature of knowledge, and Agni because He leads the limbs (of the sacrifice)."
    b = part(u, "bhashya")
    old = b["english"].split("\n")
    assert len(old) == 2
    b["english"] = "\n".join([b15, ekarse, old[0], kratu, old[1]])
    resync(u)

    u = U["17"]
    set_mula(
        u,
        "Vāyu, whose abode (anila) is Brahman, is immortal; and this body ends in ashes. Om. O All-pervading Creator! remember me. Have mercy on me. "
        "O Soul, remember thy duty.",
    )
    b = part(u, "bhashya")
    lead = (
        "Because the Supreme Lord is in Vāyu, the Vāyu has become an Immortal (how great must He be whose very presence makes others immortal)—"
        "how great must be the Immortality of the Supreme then? The word anila is compounded of two words meaning Brahman, and nilayanam, abode. "
        "The Vāyu is called Anila because it is the abode of Brahman (Brahma-dhāma): or because it is supported by Brahman.\n"
        "Vāyu is called Immortal, because His knowledge does not get obscured even in the Pralaya. (In the case of other jīvas there is an obscuration "
        "of consciousness in the Pralaya.)\n"
        "For thus says Rāma Saṃhitā:—“The Lord Himself is the Chief Immortal, (others are immortal in a secondary sense only). The Supreme Self is alone "
        "the Eternal, with his Nada (or voice ever vibrating through the eternities of the Pralaya).”"
    )
    b["english"] = lead + "\n" + b["english"]
    resync(u)

    u = U["18"]
    b = part(u, "bhashya")
    tail = (
        "Vayuna means knowledge, as the text says, “By the knowledge given by You he beheld this universe.” Juhurāṇa means that which makes us small; "
        "yuyodhi means separate.\n"
        "“Since it makes us exceedingly small, separate that sin from us. Lead us to the wealth of liberation,” thus Manu Svāyambhuva, the self-luminous, "
        "praised Yajña. (Skanda Purāṇa.) The root is “yu yu”, in the sense of separation.\n"
        "With devotion and knowledge may we offer the fullest salutation."
    )
    b["english"] = b["english"] + "\n" + tail
    resync(u)

    d["notes"] += (
        " [Alignment pass 2026-10-09: Vasu's translation of Madhva's opening on Manu and the Brahmanda quotes (wisdomlib peace chant page) restored to unit 1; "
        "the Kurma quote of 9-14 and the Brahmanda quote of 15-16 each sit in one unit with their whole english (11 and 15 no longer carry english-only "
        "commentary parts); Vasu's editorial notes cut from 7, 8, 14; 16 and 17 mula english rebuilt from Vasu's 16a/16b/17a/17b (his 17a is corrupted on "
        "wisdomlib, so 17a here is written from his word glosses); one line of the 16 quote (Kratu, Agni) and the Skanda verse and the last lines of 18, "
        "which Vasu does not translate, were translated for this corpus.]"
    )
    save("isa_madhva", d)
    return d


def mandukya():
    d = load("mandukya_madhva")
    U = idx(d)

    u = U["1/1"]
    b1 = part(u, "bhashya")["english"]
    b1 = cut(b1, "\nThe word ‘eternal’ is sometimes used")
    drop_part(u, "bhashya")
    set_mula(
        u,
        "That which is denoted by the word Om is verily this Imperishable Brahman. That (Brahman) is Full (because He is full of all auspicious attributes). "
        "This (Upaniṣad) is an explanation of that Om. The Imperishable is in the Past, Present and Future.",
    )
    u = U["1/2"]
    set_mula(
        u,
        "The Full is verily Om. That Lord, designated by Om, is even other than that which is beyond the three times. The Full is verily this imperishable "
        "Brahman. This conscience or controller (Ātman) in Śrī, Brahmā, etc., is Brahman.",
    )
    part(u, "bhashya")["english"] = b1 + "\n" + part(u, "bhashya")["english"]
    resync(u)
    edit(u, "though they bo essentially", "though they are essentially")
    edit(u, "all-prevading", "all-pervading")
    edit(U["1/3"], "In the region of waking, the Lord causes", "This Ātman has four parts or aspects. In the region of waking, the Lord causes")
    edit(U["1/3"], "resides hi the body", "resides in the body")
    edit(U["1/3"], "an. Elephant face", "an Elephant face")

    u = U["1/5"]
    edit(u, " (The commentator next explains the word ekībhūta).", "")
    edit(u, "(Next the word prajñāna-ghana is explained). ", "")
    edit(U["1/7"], "The Lord is called Viśva when", "On this there are the following verses: The Lord is called Viśva when")

    u = U["1/15"]
    garuda = (
        "Thus we read in the Garuḍa Purāṇa:—“O sage! sometime a precept itself authoritative may be supported by another authority in order to strengthen it; "
        "as Varuṇa, the Lord of the Ocean himself an authority, strengthens his revealed mantras “Om, etc.” by quoting the authority of another seer, with "
        "the words “on this there are the following verses.” Moreover these verses are not mere repetitions, but an analysis of the mantras revealed to "
        "Varuṇa. They state explicitly what was suggested implicitly before. They show the four-fold nature of this triad."
    )
    b = part(u, "bhashya")
    b["english"] = cut(b["english"], "\nIf the creation proceeds from the mere will of God", "answered next.")
    b["english"] = garuda + "\n" + b["english"]
    resync(u)

    edit(U["2/1"], "When Ho does not", "When He does not")
    edit(U["2/1"], "cannot bo an object", "cannot be an object")
    edit(U["2/1"], "seen by mon leading", "seen by men leading")
    edit(U["2/1"], "Tūryia", "Turīya")
    edit(U["2/1"], "Ho is indefinable", "He is indefinable")
    edit(U["2/2"], "On this are the following verses:— 2. (K10) ", "On this are the following verses: ")

    u = U["2/3"]
    for old, new in [
        ("[?]eant", "meant"), ("everything [?se] is bound", "everything else is bound"), ("As [?ys] the", "As says the"),
        ("applied to [?ari] mean", "applied to Hari mean"), ("non-eternal, mean [??e] makes", "non-eternal,’ mean ‘He makes"),
        ("the phrases [?e] is Jīva, He is prakriti, mean", "the phrases ‘He is Jīva, He is prakriti,’ mean"),
        ("fashions [??e] world", "fashions the world"), ("Sara-ati", "Sarasvatī"), ("is to [???claim] the", "is ever to proclaim the"),
        ("others [??e] Brahmā", "others like Brahmā"), ("But if be found", "But if anything be found"),
        ("have [??ended] it", "have intended it"), ("towards Him [??nifying]", "towards Him magnifying"),
        ("derogatory to glory", "derogatory to His glory"), ("as to [??ound] to", "as to redound to"),
    ]:
        edit(u, old, new)
    assert "[?" not in u["english"], u["english"]

    u = U["2/6"]
    b = part(u, "bhashya")
    s = b["english"]
    s = cut(s, " From one wrong knowledge arises another wrong knowledge", "may cease.)")
    s = cut(s, "\nThe waking and dream are perceiving of inverted")
    b["english"] = s
    resync(u)
    edit(u, "they are said to bo different", "they are said to be different")
    edit(u, "It only moans", "It only means")
    edit(u, "which He doos as", "which He does as")
    edit(u, "sets ofactiviti.es", "sets of activities")
    edit(u, "“Ho shows all.”", "“He shows all.”")
    edit(u, "must bo interpreted", "must be interpreted")
    edit(U["2/7"], "lias independent", "has independent")
    edit(U["2/7"], " (Thus a wrong notion of a person’s entertaining In his waking state that he is an independent agent reproduces itself in dream, when he also thinks himself to be an independent agent, but with regard to objects which are merely revived impressions of the objects perceived in the waking state and which the dreamer mistakes for real objects. The next verse describes how this eternal circle of wrong notions may cease.)", "")
    edit(U["2/8"], "Vīṣnu", "Viṣṇu")
    edit(U["2/10"], "arc mine", "are mine")
    edit(U["2/10"], "it is nob Svabhāvika", "it is not Svabhāvika")
    edit(U["3/3"], "Tie is called", "He is called")
    edit(U["3/1"], "called.measures", "called measures")

    u = U["3/4"]
    edit(u, "\n(Having explained the above three Upaniṣad verses in his own words, Śrī Madhva now quotes Brahma Tarka in support of his interpretation).", "")
    edit(u, "\nTwo reasons are given for the Viśva being called namely, that is the contracted form of either “āpti” “the Bringer,” or of “ādi,” the Saviour. We can derive the noun “a” the Bringer from the √āp, ‘pervade’ taken in a causative sense and adding the affix “डa”. The derivation of from is problematic.", "")
    edit(u, "(Ho whose", "(He whose")
    edit(u, "beginningdess", "beginningless")

    edit(U["3/5"], "[On this there are the following verses.] 5. (K19) ", "On this there are the following verses: ")
    edit(U["3/6"], "On this there are the following verses:— 6. (K20) ", "")

    u = U["3/9"]
    b = part(u, "bhashya")
    s = b["english"]
    s = cut_to(s, "\nBy understanding this portion of the Lord, first there takes place utkarṣa", "\nThe words are na vidyate")
    s = cut(s, "-sāmānya are taught of the Jīva", "without equality.]")
    b["english"] = s
    resync(u)
    assert "hypnot" not in u["english"]

    u = U["4/7"]
    b = part(u, "bhashya")
    s = b["english"]
    lest = "\n(Lest the phrase “advaita oṃkāra” of the verse may be mistaken to mean “the undivided entire Om denotes Turīya” the commentator says.)"
    assert lest in s
    s = s.replace(lest, "")
    s = cut(s, "\n(Lest one should fall into the mistake that Vāsudeva", "quotes Brahma Tarka).")
    s = s.replace("so io complete", "so to complete").replace("lie is called Anapara", "He is called Anapara").replace("arc never equal", "are never equal")
    s = s.replace(
        "The same four-aspected Prāṇava is called Brahman also",
        "The Viṣṇu in His four-fold aspect as Viśva, etc., is called Praṇava also: because He controls or leads (praṇayana) the waking, etc., states of the Jīva.\n"
        "The same four-aspected Prāṇava is called Brahman also",
    )
    b["english"] = s
    resync(u)

    edit(U["intro"], "the nourish er", "the nourisher")
    edit(U["2/6"], "to bo an illusion", "to be an illusion")
    edit(U["2/6"], "the pharse", "the phrase")
    edit(U["2/6"], "on the. Jīva", "on the Jīva")
    edit(U["4/7"], "as the. destroyer", "as the destroyer")
    d["notes"] += (
        " [Alignment pass 2026-10-09: the english of 1/1, 1/2 and the lead of 1/3 now follows where Setutila cuts Mantras 1 and 2 (Vasu's U1 commentary moved from "
        "1/1 into 1/2, whose Sanskrit holds it); Vasu's editorial notes, bracketed asides and the hypnotism and camera notes were removed from 1/15, 2/6, 2/7, 3/4, "
        "3/9 and 4/7; Vasu's Garuda translation (1.7-11) added to 1/15 and his Pranava line (4.2-3) to 4/7; the damaged [?] strings on wisdomlib's Karika 2.3 page "
        "were restored from context; OCR slips fixed.]"
    )
    save("mandukya_madhva", d)
    return d


def kena():
    d = load("kena_madhva")
    U = idx(d)
    edit(U["intro"], "Aum! Let there be peace on earth; let there be peace in space; let there be peace in the heavens.", "Aum! Peace, peace, peace.")

    set_mula(
        U["1/2"],
        "He who is the ear of the ear, the mind of the mind, the speech of the speech, He verily is the life of life and the eye of the eye. "
        "The wise, freeing themselves (from the final body) and going forth from this world, become immortal.",
    )
    set_mula(
        U["2/1"],
        "(O Maheśvara!) If you think “I know Brahman well,” then you know, indeed, only a minor manifestation of Brahman. Therefore that aspect of Brahman "
        "which is in you and that which is in the Devas must now be inquired into by you. I think it is (still) not known (to you).",
    )
    set_mula(
        U["2/2"],
        "I do not think I know Him fully; though others (say) ‘we know Him fully.’ Nor do I say I know Him not at all, for I know. Amongst us who says "
        "“I know Him,” he knows Him not. He who says “I do not know Him,” he knows indeed.",
    )
    set_mula(
        U["2/4"],
        "Understanding Him according to one’s intelligence, as a direct object of intuition, verily he obtains immortality. Through the Self (by one’s own "
        "exertion) he obtains strength, and through direct knowledge of Brahman he obtains immortality.",
    )
    edit(U["2/5"], "casts of this world", "casts off this world")
    set_mula(
        U["3/1"],
        "Brahman verily won the victory for the sake of the Devas. But though the victory was His, the Devas became puffed up. They thought, "
        "“This victory is ours only, ours only is this greatness.”",
    )
    set_mula(
        U["3/2"],
        "Brahman was aware of this. In their presence, He appeared. They did not recognize who this strange appearance could be.",
    )
    set_mula(
        U["4/2"],
        "Therefore these Devas, Agni, Vāyu and Indra, are, as it were, superior to the other Devas, because they touched Him the nearest and were the first "
        "to know “This Yakṣa is Brahman.”",
    )
    edit(U["4/8"], "8. (Of this", "(Of this")
    edit(U["4/9"], "9. He who", "He who")
    drop_part(U["4/8"], "bhashya")

    set_mula(U["colophon11"], "Thus ends the first section of the Talavakara Upanishad.")
    set_mula(U["colophon17"], "Thus ends the second section of the Talavakara Upanishad.")
    set_mula(U["colophon30"], "Thus ends the third section of the Talavakara Upanishad.")
    edit(U["colophon41"], "Thus ends the Fourth Chapter of Talavakaropnishad.", "Thus the Talavakara Upanishad is complete.")

    u = U["bhashya"]
    e = u["english"]
    e = cut(e, "Further Clarifications:", "even so mind over all other organs. ")
    for old, new in [
        ("Mediating on", "Meditating on"), ("thus in Brahmasara.. lightening means", "thus in Brahmasara. Vidyutaḥ, lightning, means"),
        ("Te splendor", "The splendor"), ("having been said. | means being", "having been said. Nyamimiṣat means being"),
        ("like sa%va and others", "like sattva and others"), ("Sa%ya is what", "Satya is what"), ("thse are verily", "these are verily"),
        ("Aa: means in fullness, entirety. sa=klp means", "Ā means in fullness, entirety. “Abhīkṣṇaṃ saṅkalpaḥ” means"),
    ]:
        assert old in e, old
        e = e.replace(old, new)
    sonde_43 = (
        "Uma comprehensively instructed him (Indra) about the supreme abiding place of Vishnu, known to the liberated ones, like Brahma, Vayu, Shesha Garuda, "
        "Shiva and others along with their spouses (energies), since they all were not conceited. Since Indra was the first one to know, he was the foremost "
        "among all gods. Kaama was superior to Daksha and others having known earlier than they did. By Kaama were instructed Daksha, Brihaspati, Manu and "
        "likewise Kama’s own son. Later the Surya, Chandrama, Yama, and Varuna (were instructed), who uttered Aum. Breath in the nostrils and fire were the "
        "first who saw Him. Therefore, of all gods, they are known as the superior ones; among them are Indra and Kaama and superior to them are Brahma and "
        "others. Among gods, Agni is lower than and Vishnu is superior. In between them exist all other gods like Brahma and others. Agni is said to be "
        "inferior because he came to know of Brahman from Indra. This is the gradation (taratamya) among the gods according to the order in which they knew "
        "Vishnu, fully or partially."
    )
    mark = "she was made herself visible to them. What is communicated"
    assert mark in e
    e = e.replace(mark, "she was made herself visible to them. " + sonde_43 + " What is communicated")
    u["english"] = e
    assert not re.search(r"[|%$]|sa=", e), re.findall(r".{20}[|%$=].{20}", e)
    d["notes"] += (
        " [Alignment pass 2026-10-09: english of 1/2, 2/1, 2/2, 2/4, 3/1, 3/2, 4/2 replaced because Sonde's rendering or the earlier pick did not translate the "
        "Sanskrit (1/2 missed the 'ear of the ear' reading, 3/1 carried the first sentence of 3/2); the replacements are Vasu's wisdomlib mantra translations "
        "(2/2, 3/1 lightly trimmed of his parenthetical glosses) except 4/2, which follows the verse rather than Madhva's gloss; the english-only Vasu "
        "commentary part under 4/8 (headed with the wrong Upanishad) dropped since the 'bhashya' unit translates the whole commentary; Sonde's own "
        "'Further Clarifications' comment cut from the 'bhashya' unit, whose english now also holds Sonde's translation of the commentary on 4.2-3 (Uma's teaching and the gradation of the gods) that it had dropped; section colophons say section, not chapter.]"
    )
    for u in d["units"]:
        for h in [u] + (u.get("parts") or []):
            if h.get("english"):
                h["english"] = h["english"].replace("„", "‘").replace("‟", "’")
    save("kena_madhva", d)
    return d


if __name__ == "__main__":
    isa()
    mandukya()
    kena()
