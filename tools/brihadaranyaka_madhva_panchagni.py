"""Give the last unit of brihadaranyaka_madhva (Panchagni verses, Madhva's closing salutation, Hanuman-Bhima-Madhva verses) an english.
No source translates it as a whole: Vasu's block mixes in his own notes. The english is written for this corpus (Claude), line by line from the Sanskrit,
with Vasu 1916 pp. 747-749 consulted for the Hanuman-Bhima-Madhva passage.
Run from corpus/: python3 tools/brihadaranyaka_madhva_panchagni.py [--dry]"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv
F = ROOT / "upanishads" / "brihadaranyaka_madhva.json"
REF = "अष्टमोऽध्यायः / पञ्चमं ब्राह्मणम्"

EN = """“Meditating always in due order on Narayana, Vasudeva, the Lord Sankarshana, Pradyumna and Aniruddha, the five-formed One who abides in heaven, the rain-cloud, the earth, man and woman, one is called a knower of the five fires and attains the highest state. No fault of association will ever touch him.” So says the Traividya.
The greatness of the seen and the unseen. The procreation rite means that a son born by the procedure taught in this Upanishad is, as a rule, fit for heaven and for release.
“One born according to the Upanishad is fit for heaven and release, provided the minds of the parents do not go anywhere but to Vishnu. If the parents' minds go to Vishnu but this rite is not performed, the child lacks visible capacity, yet is fit for release if he is steady; and he may at times have visible capacity through causes such as a command. Where there is no special cause, it is as stated and not otherwise.” So also it is said.
“Narayana is spoken of by the word ‘heaven’ (dyu), because he is always the cause of radiance. Vasudeva is the rain-cloud (parjanya), because from him the Supreme is brought forth. Sankarshana is the earth, because of his extent. Pradyumna is called the man (purusha), because he fills the world. Aniruddha is spoken of by the word ‘woman’, because he is always present together with the three. Aniruddha is ever established in the three among the gods. By connection with the well-known heaven and the rest, the words heaven and the rest denote him; likewise the words fire and the rest, because he consumes, he who is supreme. He is angara because he is made a limb (anga); arcis because he is worthy of worship; visphulinga because he is everywhere (vishvak); samidh because he kindles. Hari, abiding in each of these, is always denoted by those words; the others only through their connection with him. Words such as Aditya and rashmi stand in the same way. In each there are five distinctions, by the division into arcis and the rest, taught likewise by the distinction of Narayana and the rest.” So it is said in the Pravritta.
“He is dhuma because of the sound ‘dhut’ made towards enemies, the Supreme Person; arcis because he is most worthy of worship; angara is said of his own limb, because being the possessor of limbs he abides as one in the form of limbs.” And so on, in the Traividya.
“Even those of low birth may at times listen to knowledge in play; this distinction of hearer and speaker does not show superiority. He whose superiority is declared in the Veda, the Pancharatra, or the Itihasa and Purana, he alone is superior, none other, ever.” So in the Brahmatarka.
He is Aditya because he takes in (adana). The rays (rashmi) because he delights and restrains. Aha (day) because he is not diminished. Chandra because he gladdens. Nakshatra because he has no other power (kshatra); the plural is because of his many forms. Vayu because of knowing and of living. Abhra because he cannot be borne by others. Vidyut because he illumines. Ashani because he consumes. Hradunih because he sounds forth. Akasha because he shines all around. Samvatsara because he fully delights the calves. The directions (dishah) because he points out; the intermediate directions because he points out the intermediate. Ratri because he gives delight. Speech (vak) because of speaking. Breath (prana) because of leading forth. The tongue (jihva) because he leaves and makes go. The eye (chakshu) because he sees. The ear (shrotra) because he hears. The organ of generation (upastha) because he stands near. The womb (yoni) because he makes go and leads. Abhinanda because he gladdens. And he alone does the inner converse and the work of the inner organ.
“Since everything depends on him, Hari is spoken of by all words; he is the primary meaning, and the others are meant by transfer through association with him.” So in the Brahmatarka.
“Because they depend on him, they have meaning” is the Lord's own saying; and also “because of drawing together”.
“By the five-fire knowledge, by the knowledge of breath, by the rite of procreation, by the giving of knowledge, and by knowledge of the lineage of teachers, the Supreme Person is to be honoured, the inner ruler of all, the eternal. Salutation to that Supreme Self.” So in the Sadbhava.
We worship always the Dearest, the most beloved of my beloved: of eternal and unequalled bliss, unborn, all-pervading, firmly established, omniscient, pure awareness itself, spotless, full of imperishable qualities, the highest cause of the creation, maintenance and dissolution of the universe, of knowledge and of right release.
He of whom three divine forms are declared in the Vedic text, and of whom the great radiance of the god is thus laid down: the first is Vayu who carried Rama's words, the second is the body of Prikshu (Bhima), and the third is Madhva; by him this commentary has been made for the Lord.
“The word hanu denotes knowledge, and Hanuman is called so by the word mati (wisdom); by him were carried the words of Rama, whose form is truth. Bhima is called the supporter (bhrit) of authorities; the mothers are the measures of the word: the Rig and the other Vedas, the Itihasa, the Purana and the Pancharatra are said to be the seven auspicious ones, and he who rests in them is Bhima. Madhu is said to mean bliss, and va means tirtha; Madhva is Anandatirtha, the third body of Maruti. He who knows these three forms of the great soul given in the hymn is a knower of the Veda, and through his grace a knower of the truth.”
“The helper in Rama's works, always near him, is to be known as Hanuman, the first. Bhima, the great eater, the destroyer of armies, is the second; the third is celebrated under the name Purnaprajna, Anandatirtha. ‘Dasha’ indicates all; here ‘full’ (purna) means all. Prajna means wisdom (pramati); hence Purnaprajna. Hari being hidden in the Kali age, concealed by those who declare this world unreal, without foundation and without a Lord, the third one churns the demons; by him the wise (the Isanas) came to know the supreme qualities of Vishnu, which had been hidden by assertions of attributelessness. In the Treta, the Dvapara and the Kali, these three come in order. Of them the supreme leader is Vishnu, the Lord of the lords of all; he is called Svayambhu and Brahma. Salutation to the Supreme Brahman.” So also is it said.
Salutation to Vishnu, the beloved, whose abode is full of countless noble qualities, the eternal Creator, dense with unfailing bliss.
Thus ends the eighth chapter of the Brihadaranyaka Upanishad Bhashya composed by the venerable Anandatirtha Bhagavatpada.
Thus ends the Brihadaranyaka Upanishad Bhashya composed by the venerable Anandatirtha Bhagavatpada."""


def main():
    d = json.loads(F.read_text(encoding="utf-8"))
    u = next(x for x in d["units"] if x["ref"] == REF)
    assert not u["english"]
    u["english"] = EN
    u["meta"] = {"english_source": "written for this corpus (Claude); Vasu 1916 consulted for the Hanuman-Bhima-Madhva passage"}
    d["notes"] += (
        " [2026-10-13: the last unit (8th adhyaya, 5th brahmana: Panchagni verses, salutations, Hanuman-Bhima-Madhva verses) had no english; its english was "
        "written for this corpus (Claude), since Vasu's block for it mixes in his own notes. Some verses there are corrupt in Setutila, and the rendering of "
        "those lines is tentative.]"
    )
    if not DRY:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
