"""Restore the 12 Brihadaranyaka Shankara mantras Madhavananda leaves untranslated.

4.6.1-3 (line of teachers): wisdomlib has them, labelled 4.5.1-3 on its section VI page; english is Madhavananda's, commentary included.
6.4.3-5, 9-11, 21-23: Madhavananda omits them; the mula english is Hume 1921 (public domain), the bhashya on them stays untranslated.
Needs GRANTHA_RAW/wl_4_6.html and the old revision of the file in git (bf2d645^).
"""
import html
import json
import os
import re
import subprocess
from pathlib import Path

RAW = Path(os.environ.get("GRANTHA_RAW", "."))
REL = "upanishads/brihadaranyaka_shankara.json"
NUM = re.compile(r"^\W*[\dIl]{1,3}[.,]\s*")

HUME = {
    "6.4.3": "Her lap is a sacrificial altar; her hairs, the sacrificial grass; her skin, the soma-press. The two lips of the vulva are the fire in the middle. Verily, indeed, as great as is the world of him who sacrifices with the Vajapeya ('Strength-libation') sacrifice, so great is the world of him who practises sexual intercourse, knowing this; he turns the good deeds of women to himself. But he who practises sexual intercourse without knowing this - women turn his good deeds unto themselves.",
    "6.4.4": "This, verily, indeed, it was that Uddalaka Aruni knew when he said: This, verily, indeed, it was that Naka Maudgalya knew when he said: This, verily, indeed, it was that Kumaraharita knew when he said: 'Many mortal men, Brahmans by descent, go forth from this world, impotent and devoid of merit, namely those who practise sexual intercourse without knowing this.' [If] even this much semen is spilled, whether of one asleep or of one awake,",
    "6.4.5": "then he should touch it, or [without touching] repeat: 'What semen has of mine to earth been spilt now, / Whate'er to herb has flowed, whatever to water / This very semen I reclaim! / Again to me let vigor come! / Again, my strength; again, my glow! / Again the altars and the fire / Be found in their accustomed place!' Having spoken thus, he should take it with ring-finger and thumb, and rub it on between his breasts or his eye-brows.",
    "6.4.9": "The woman whom one may desire with the thought, 'May she enjoy love with me!' - after coming together with her, joining mouth with mouth, and stroking her lap, he should mutter: 'Thou that from every limb art come, / That from the heart art generate, / Thou art the essence of the limbs! / Distract this woman here in me, / As if by poisoned arrow pierced!'",
    "6.4.10": "Now, the woman whom one may desire with the thought, 'May she not conceive offspring!' - after coming together with her and joining mouth with mouth, he should first inhale, then exhale, and say: 'With power, with semen, I reclaim the semen from you!' Thus she comes to be without seed.",
    "6.4.11": "Now, the woman whom one may desire with the thought, 'May she conceive!' - after coming together with her and joining mouth with mouth, he should first exhale, then inhale, and say: 'With power, with semen, I deposit semen in you!' Thus she becomes pregnant.",
    "6.4.21": "Then he spreads apart her thighs, saying: 'Spread yourselves apart, heaven and earth!' Coming together with her and joining mouth with mouth, he strokes her three times as the hair lies, saying: 'Let Vishnu make the womb prepared! / Let Tvashtri shape the various forms! / Prajapati - let him pour in! / Let Dhatri place the germ for thee! / O Sinivali, give the germ; / O give the germ, thou broad-tressed dame! / Let the Twin Gods implace thy germ - / The Asvins, crowned with lotus-wreaths!'",
    "6.4.22": "With twain attrition-sticks of gold / The Asvin Twins twirl forth a flame; / 'Tis such a germ we beg for thee, / In the tenth month to be brought forth. / As earth contains the germ of Fire (agni), / As heaven is pregnant with the Storm (indra), / As of the points the Wind (vayu) is germ, / E'en so a germ I place in thee, / So-and-so!",
    "6.4.23": "When she is about to bring forth, he sprinkles her with water, saying: 'Like as the wind doth agitate / A lotus-pond on every side, / So also let thy fetus stir. / Let it come with its chorion. / This fold of Indra's has been made / With barricade, enclosed around. / O Indra, cause him to come forth - / The after-birth along with babe!'",
}


def wisdomlib_46():
    t = (RAW / "wl_4_6.html").read_text(encoding="utf-8")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</div>|</h\d>", "\n", t)
    L = re.sub(r"\n\s*\n+", "\n", html.unescape(re.sub(r"<[^>]+>", "", t))).split("\n")
    out = {}
    for n in (1, 2, 3):
        i = next(k for k, l in enumerate(L) if l.startswith(f"Verse 4.5.{n}:"))
        win = [l.strip() for l in L[i + 1:i + 16] if l.strip() and not re.search(r"[ऀ-ॿ]", l)]
        eng = [l for l in win if re.match(rf"^{n}\.\s", l) or l.startswith("Now the line of teachers for the two chapters")]
        out[n] = eng
    return out


def main():
    old = json.loads(subprocess.run(["git", "show", "bf2d645^:" + REL], capture_output=True, text=True, check=True).stdout)
    oldu = {u["ref"]: u for u in old["units"]}
    order = [u["ref"] for u in old["units"]]
    d = json.loads(Path(REL).read_text(encoding="utf-8"))
    wl = wisdomlib_46()
    fills = {}
    for n in (1, 2, 3):
        fills[f"4.6.{n}"] = NUM.sub("", wl[n][0])
    comm = [l for l in wl[3] if l.startswith("Now the line of teachers for the two chapters")]
    new = []
    for ref in ["4.6.1", "4.6.2", "4.6.3"] + list(HUME):
        u = dict(oldu[ref])
        ps = {p["role"]: dict(p) for p in (u.get("parts") or [])}
        if ref in HUME:
            m = ps["mula"]
            m["english"] = HUME[ref]
            u["parts"] = [m] + ([ps["bhashya"]] if "bhashya" in ps else [])
            u["scope"], u["sanskrit"], u["english"] = "mula", m["sanskrit"], HUME[ref]
        elif ref == "4.6.3":
            ps["mula"]["english"] = fills[ref]
            ps["bhashya"]["english"] = comm[0]
            u["parts"] = [ps["mula"], ps["bhashya"]]
            u["scope"] = "mula+commentary"
            u["sanskrit"] = "\n".join(p["sanskrit"] for p in u["parts"])
            u["english"] = "\n".join(p["english"] for p in u["parts"])
        else:
            u["scope"], u["english"] = "mula", fills[ref]
            u.pop("parts", None)
        new.append(u)
    have = {u["ref"] for u in d["units"]}
    for u in new:
        if u["ref"] in have:
            continue
        k = order.index(u["ref"])
        idx = {x["ref"]: i for i, x in enumerate(d["units"])}
        prev = next((order[j] for j in range(k - 1, -1, -1) if order[j] in idx), None)
        d["units"].insert(idx[prev] + 1 if prev else 0, u)
    n = d["notes"]
    a = n.index("[12 Sanskrit units have no english")
    b = n.index("]", a) + 1
    d["notes"] = n[:a] + "[4.6.1-3 english is Madhavananda's (wisdomlib labels the section 4.5.1-3). Madhavananda leaves 6.4.3-5, 6.4.9-11 and 6.4.21-23 and Shankara's commentary on them untranslated; their mula english is Hume 1921 (public domain, from sacred-texts, Muller omitted them) and their bhashya Sanskrit is kept without english.]" + n[b:]
    Path(REL).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("restored", len(new))


main()
