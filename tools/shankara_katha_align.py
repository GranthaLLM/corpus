"""Align english with sanskrit in katha_shankara (Sastri via wisdomlib).
Run from corpus/: python3 tools/shankara_katha_align.py [--dry]"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv
F = ROOT / "upanishads" / "katha_shankara.json"


def part(u, role):
    return next(p for p in u["parts"] if p["role"] == role)


def resync(u):
    ps = [p for p in u["parts"] if p.get("sanskrit") and p.get("english")]
    u["english"] = "\n".join(p["english"] for p in ps)
    u["sanskrit"] = "\n".join(p["sanskrit"] for p in u["parts"] if p.get("sanskrit")) if u["scope"] == "mula+commentary" else u["sanskrit"]


B10 = (
    "Beyond the mind is the intellect, subtler, greater, and the inner self of the mind; by the word intellect is meant the subtle element that is the origin "
    "of determination and the like. Beyond the intellect is the Atman, the Great: being the inner self of the intellects of all beings, and the greatest "
    "of all, it is the first principle born of the Unmanifested, the principle of Hiranyagarbha, of the nature of knowledge and ignorance; this Great "
    "Atman is said to be beyond the intellect."
)
B11 = (
    "Beyond the Great is the Unmanifested, subtler, greater than all, and the inner self of all: the seed of the whole world, undifferentiated name and "
    "form, the totality of the powers of all causes and effects, called unmanifested space and so on; it rests on the Paramatman as warp and woof, as the "
    "power of the banyan tree rests in the banyan seed. Beyond that Unmanifested is the Purusha, subtler still, being the cause of all causes and the inner "
    "self of all, and great; he is the Purusha because he fills all. Anticipating the thought of anything else beyond him, the text says ‘beyond the "
    "Purusha there is nothing’: since there is no other entity whatever beyond the Purusha, who is pure compact consciousness, in him subtlety, greatness "
    "and inwardness reach their limit and end. For here, from the senses onward, subtlety and the rest are completed. For this very reason he is the "
    "highest goal of all travellers, of all transmigrating beings that go, as the smriti says ‘Having gone where they do not return’."
)
B12_HEAD = (
    "If it is a goal, one must also arrive there; how then ‘from which he is not born again’? There is no fault: since he is the inmost self of all, the "
    "attaining is only figuratively called a goal. That he is the inner self of all has been shown by placing him beyond the senses, mind and intellect. "
    "For one who travels reaches something distinct from himself and does not find by its own nature what is not himself. So the Sruti says "
    "‘Not travelling on the roads, able to cross the roads’ and so on. Likewise it shows that he is the inner self of all: this Purusha, hidden in all "
    "beings from Brahma down to a clump of grass, enveloped, engaged in seeing, hearing and the like, covered by ignorance and Maya, therefore does not "
    "shine as the Self of anyone."
)


def main():
    d = json.loads(F.read_text(encoding="utf-8"))
    U = {u["ref"]: u for u in d["units"]}

    u10 = part(U["1.3.10"], "bhashya")
    e = u10["english"]
    a = e.index("Than the mind which is the origin")
    b = e.index("Oh, how deep")
    first = e[:a].rstrip()
    tail = e[b:]
    u10["english"] = first + " " + B10
    for ref, text in (("1.3.11", B11), ("1.3.12", B12_HEAD + " " + tail)):
        u = U[ref]
        u["scope"] = "mula+commentary"
        part(u, "bhashya")["english"] = text
        resync(u)
    resync(U["1.3.10"])

    for u in d["units"]:
        for h in [u] + (u.get("parts") or []):
            t = h.get("english")
            if not t:
                continue
            t = re.sub(r"^Com\.\s*[—-]+\s*", "", t)
            t = re.sub(r"\n+\s*———+\s*$", "", t).rstrip()
            t = re.sub(r"^\d+\.\s+", "", t)
            t = t.replace(" Nirindriah (?)", " Nirindriah").replace("Nirindriah (?)", "Nirindriah")
            t = re.sub(r" \(\d+\)$", "", t)
            t = t.replace("Vaivasvaia", "Vaivasvata").replace("be gets", "gets")
            h["english"] = t
    for u in d["units"]:
        if u.get("parts"):
            ps = [p for p in u["parts"] if p.get("sanskrit") and p.get("english")]
            if u["scope"] == "mula+commentary" and ps:
                u["english"] = "\n".join(p["english"] for p in ps)
    d["notes"] += (
        " [Alignment pass 2026-10-09: the english of 1.3.10 had absorbed pieces of the commentary of 1.3.11 and 1.3.12 with part of Sastri's translation "
        "lost in the splice. The 1.3.10 part now ends where its Sanskrit does; the intellect-and-Mahat sentence, all of the 1.3.11 commentary and the first "
        "half of the 1.3.12 commentary were translated for this corpus (the rest of 1.3.12 is Sastri's). 'Com.' prefixes, verse-number prefixes and the "
        "'———' separator lines were stripped.]"
    )
    if not DRY:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
