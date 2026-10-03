import glob, json, pathlib, re
from common import ROOT, write

TAGS = re.compile(r"[ \t]*\((?:BhGR?_[^)]*|BhG[_a-z0-9.\-]*)\)|[ \t]*भ्ग्र्_[०-९0-9.]*")


def clean(t):
    return re.sub(r"[ \t]+\n", "\n", TAGS.sub("", t)) if t else t


def main():
    for f in sorted(glob.glob(str(ROOT / "*/*.json"))):
        p = pathlib.Path(f)
        d = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(d, dict) or "units" not in d:
            continue
        n = 0
        for u in d["units"]:
            for t in [u] + u.get("parts", []):
                s = t.get("sanskrit")
                c = clean(s)
                if c != s:
                    t["sanskrit"] = c.strip()
                    n += 1
        if n:
            d["notes"] += " Source citation tags embedded in the Sanskrit by Setutila, such as (BhGR_2.12), were removed."
            write(str(p.relative_to(ROOT)), d)
            print(p.stem, n)


if __name__ == "__main__":
    main()
