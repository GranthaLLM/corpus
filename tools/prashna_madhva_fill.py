import json, re
from common import ROOT, RAW, write
import wl

CACHE = RAW / "prashna_madhva_wl" / "pages.json"
# Setutila refs that are mis-numbered in the source -> (prashna, mantra) on wisdomlib
MAP = {"1/14-2": (1, 15), "8": (4, 8), "5": (5, 5), "5/8": (5, 7), "6/6": (6, 6), "6/7": (6, 7)}
MARK = re.compile(r"^Mantra\s+(\d)\.(\d+)\.?(?:\d+\.)?\s*$", re.I)


def pages():
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    _, toc = wl.toc("prashna-upanishad-madhva-commentary")
    out = [{"id": i, "title": t, "lines": wl.page_text("https://www.wisdomlib.org" + h) or []} for i, t, h in toc]
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def translations():
    out = {}
    for p in pages():
        L = p["lines"]
        for i, l in enumerate(L):
            m = MARK.match(l.strip())
            if m and i + 1 < len(L):
                nxt = L[i + 1].strip()
                t = re.sub(r"^(?:Mantra\s+[\d.]+\s*)?\d*\.?\s*", "", nxt)
                t = re.sub(r"\s*[—-]\s*\d+\.?\s*$", "", t)
                out[(int(m.group(1)), int(m.group(2)))] = t
    return out


def main():
    T = translations()
    d = json.loads((ROOT / "upanishads/prashna_madhva.json").read_text(encoding="utf-8"))
    n = 0
    for u in d["units"]:
        key = MAP.get(u["ref"])
        if key is None or u.get("english") or key not in T:
            continue
        mp = next((p for p in u.get("parts", []) if p["role"] == "mula"), None)
        if mp is not None:
            mp["english"] = T[key]
        u["english"] = T[key]
        n += 1
    d["notes"] += (f" [{n} units whose Setutila ref is mis-numbered (1/14-2 is mantra 1.15, 8 is 4.8, 5 is 5.5, 5/8 is 5.7, 6/6 and 6/7 as printed) got the verse translation of the wisdomlib mantra they hold, matched by reading the Sanskrit; "
                   "the unit 'unnumbered31' is a stray verse number with no text.]")
    write("upanishads/prashna_madhva.json", d)
    print(n)
    return d, T


if __name__ == "__main__":
    d, T = main()
    for k in MAP.values():
        print(k, T.get(k, "")[:110])
