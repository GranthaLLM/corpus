import glob, json
from common import ROOT, write


def main():
    for f in sorted(glob.glob(str(ROOT / "*/*.json"))):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(d, dict) or "units" not in d:
            continue
        done = []
        for u in d["units"]:
            e, s, pa = u.get("english"), u.get("sanskrit"), u.get("parts") or []
            if not e or not s or u["scope"] != "mula+commentary" or len(e) / len(s) >= 0.6:
                continue
            mp = next((q for q in pa if q["role"] == "mula"), None)
            others = [q for q in pa if q["role"] != "mula" and q.get("english")]
            if not mp or not mp.get("sanskrit") or others or len(mp.get("english") or "") < 0.8 * len(e):
                continue
            u["sanskrit"], u["english"], u["scope"] = mp["sanskrit"], mp["english"], "mula"
            done.append(u["ref"])
        if done:
            d["notes"] += f" [{len(done)} units whose english translates the verse only now carry sanskrit = the verse, with the commentary left in the bhashya part: {', '.join(done)}]"
            rel = str(pathlib_rel(f))
            write(rel, d)
            print(rel, len(done), done)


def pathlib_rel(f):
    import pathlib
    return pathlib.Path(f).relative_to(ROOT)


if __name__ == "__main__":
    main()
