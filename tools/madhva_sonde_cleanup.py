"""Clean Sonde-derived english in chandogya_madhva, taittiriya_madhva and brihadaranyaka_madhva:
legacy-font tokens, cut-off endings, one stray Sonde note.
Run from corpus/: python3 tools/madhva_sonde_cleanup.py [--dry]"""
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


def holders(d):
    for u in d["units"]:
        for h in [u] + (u.get("parts") or []):
            if h.get("english"):
                yield u, h


def sub_all(d, pairs):
    for _, h in holders(d):
        e = h["english"]
        for old, new in pairs:
            e = e.replace(old, new)
        h["english"] = e


def stop(d):
    for _, h in holders(d):
        e = h["english"].rstrip()
        if re.search(r"[A-Za-z0-9ṛāīūṇḥ’)]$", e):
            e += "."
        h["english"] = e


def chandogya():
    d = load("chandogya_madhva")
    sub_all(d, [
        ("Bagava na Bagava tdahr na ivavaod yaqaa AM%yaadacaama vaava ikla ", ""),
        ("Asa%ya", "Asatya"), ("Sa%ya", "Satya"), ("sa%ya", "satya"),
        ("Aaid%ya", "Aditya"), ("Parmaa%maa", "Paramatma"), ("Aa%maa", "Atma"),
        ("Aa%marit:", "Atmarati"), ("Aa%marit", "Atmarati"), ("Aa%mat:", "Atmatah"), ("Aa%mat", "Atmatah"), ("Aa%ma", "Atma"),
        ("prmat%vao", "supremacy"), ("imaqyaa", "mithya"),
        ("Brahma?i%vaja", "Brahma priest"), ("Bau:", "Bhuh"), ("Aja:", "Ajah"), ("as?gvaod", "Rigveda"),
        ("vyaadda%yaova", "vyadadatyeva"), ("Adata%yaova", "adadatyeva"),
        (" pra%manao Since", " Since"), ("according to?t,", "according to Rita,"), ("Since? is the derivative", "Since it is the derivative"),
    ])
    U = {u["ref"]: u for u in d["units"]}
    for ref, old, new in [("1.4", "means the", "Urdhvah means the best."), ("2.5", "thus having been", "thus having been said.")]:
        for h in [U[ref]] + (U[ref].get("parts") or []):
            e = h.get("english")
            if e and e.rstrip().endswith(old):
                h["english"] = e.rstrip()[: -len(old)] + new
    stop(d)
    left = [(u["ref"], m.group(0)) for _, h in holders(d) for u in [_] for m in re.finditer(r"\S*%\S*", h["english"])]
    assert not left, left[:5]
    d["notes"] += (
        " [Cleanup 2026-10-09: legacy-font tokens left in Sonde's english (sa%ya, Aaid%ya, Aa%maa and the like) read back as Satya, Aditya, Atma; one "
        "garbled Sanskrit fragment in 6.3-16 removed; english cut off at a page break completed or given a full stop.]"
    )
    save("chandogya_madhva", d)


def taittiriya():
    d = load("taittiriya_madhva")
    sub_all(d, [("\\underline{Brahma}", "Brahma"), ("and special adjective,", "and special adjective.")])
    stop(d)
    d["notes"] += " [Cleanup 2026-10-09: a LaTeX fragment removed and cut-off endings given a full stop.]"
    save("taittiriya_madhva", d)


def brihadaranyaka():
    d = load("brihadaranyaka_madhva")
    for _, h in holders(d):
        e = h["english"]
        if "Further Exlanation:" in e:
            i = e.index("Further Exlanation:")
            j = e.index("The rest of the mantra is similarly", i) + len("The rest of the mantra is similarly")
            h["english"] = (e[:i] + e[j:].lstrip("\n")).replace("success is\n", "success is assured.\n")
    for u, h in holders(d):
        e = h["english"].rstrip()
        if u["ref"].endswith("गार्गिब्राह्मणम्") and e.endswith("has now been designated as"):
            h["english"] = e + " ‘kham’."
    stop(d)
    d["notes"] += " [Cleanup 2026-10-09: Sonde's note on the opening words of the 20th brahmana cut; the Gargi unit's last sentence completed.]"
    save("brihadaranyaka_madhva", d)


if __name__ == "__main__":
    chandogya()
    taittiriya()
    brihadaranyaka()
