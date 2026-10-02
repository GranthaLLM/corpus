import json, re
from common import ROOT, RAW, write
import wl

SLUG = "the-brihadaranyaka-upanishad"
CACHE = RAW / "brihadaranyaka_shankara_wl" / "pages.json"
MARK = re.compile(r"^Verse (\d+)\.(\d+)\.(\d+)(?:\s*-\s*(\d+))?\s*:?\s*$")
DEV = re.compile("[ऀ-ॿ]")
IAST = re.compile(r"[āīūṛṝḷṃḥṅñṭḍṇśṣ]")


def pages():
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    _, toc = wl.toc(SLUG)
    out = [{"id": i, "title": t, "lines": wl.page_text("https://www.wisdomlib.org" + h) or []} for i, t, h in toc]
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def verses(P):
    out = {}
    for p in P:
        L = p["lines"]
        idx = [i for i, l in enumerate(L) if MARK.match(l)]
        for n, i in enumerate(idx):
            m = MARK.match(L[i])
            body = L[i + 1:(idx[n + 1] if n + 1 < len(idx) else len(L))]
            eng = [l for l in body if not DEV.search(l) and not (IAST.search(l) and re.search(r"[|]\s*$", l)) and not re.match(r"^[a-zāīūṛṃśṣḥṅñṭḍṇ,;:' |0-9-]+$", l)]
            eng = [l for l in eng if not l.startswith(("Verse ", "Notes", "Footnotes"))]
            out.setdefault((int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4) or m.group(3))), eng)
    return out


def main():
    P = pages()
    V = verses(P)
    d = json.loads((ROOT / "upanishads/brihadaranyaka_shankara.json").read_text(encoding="utf-8"))
    n, parked = 0, []
    for u in d["units"]:
        m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", u["ref"])
        if not m or u.get("english") or not u.get("sanskrit"):
            continue
        a, b, c = map(int, m.groups())
        key = next((k for k in V if k[:3] == (a, b, c) and k[3] == c), None)
        if key is None or not V[key]:
            parked.append(u["ref"])
            continue
        eng = V[key]
        trans = re.sub(r"^\W*[\dIl]{1,3}[.,]\s*", "", eng[0]).strip()
        comm = "\n".join(eng[1:])
        has_b = any(p["role"] == "bhashya" and p.get("sanskrit") for p in u.get("parts", []))
        for x in u.get("parts", []):
            x.pop("english", None)
        parts = list(u.get("parts", []))
        mp = next((x for x in parts if x["role"] == "mula"), None)
        bp = next((x for x in parts if x["role"] == "bhashya"), None)
        if mp:
            mp["english"] = trans
        if comm:
            if bp is None:
                bp = {"role": "bhashya"}
                parts.append(bp)
            bp["english"] = comm
        u["english"] = "\n".join(x for x in (trans, comm if has_b else "") if x)
        if parts:
            u["parts"] = [x for x in parts if x.get("sanskrit") or x.get("english")]
        u.setdefault("meta", {})["english_source"] = "wisdomlib, Madhavananda 1950 (joined by verse number)"
        n += 1
    d["notes"] += f" [{n} more units joined by verse number from the wisdomlib page marker 'Verse a.b.c', the earlier text-based join having failed on variant readings; no page found: {', '.join(parked)}.]"
    write("upanishads/brihadaranyaka_shankara.json", d)
    print(n, "parked", parked)


if __name__ == "__main__":
    main()
