import re, glob, html
from common import RAW

ASDIR = RAW / "as"
ELEM = re.compile(r'<(p|div) class="(unit [^"]*)" id="([^"]+)"[^>]*>(.*?)</\1>', re.S)
IDP = re.compile(r"^([A-Za-z]+)_C(\d+)(?:_S(\d+))?(?:_([VK])(\d+))?(?:_([IBE])(\d+))?$")


def clean(s):
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r'<span class="verse-no".*?</span>', "", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("­", "")
    s = "\n".join(re.sub(r"[ \t]+", " ", l).strip() for l in s.split("\n"))
    return s.strip()


def pages(book):
    fs = sorted(glob.glob(str(ASDIR / f"{book}_*.html")), key=lambda f: [int(i) for i in re.search(r"_(\d+(?:-\d+)?)\.html$", f).group(1).split("-")])
    for f in fs:
        yield open(f, encoding="utf-8").read()


def units(book, drop_chapter=False):
    groups, order, pending = {}, [], []
    for t in pages(book):
        for m in ELEM.finditer(t):
            cls, id_, inner = m.group(2), m.group(3), m.group(4)
            mm = IDP.match(id_)
            if not mm:
                continue
            _, c, s, vt, v, kind, n = mm.groups()
            if "kind-heading" in cls:
                continue
            txt = clean(inner)
            if not txt:
                continue
            if v is None and kind == "I" and any(k[0] == c and k[1] == s and k[2] != "x" for k in groups):
                pending.append(txt)
                continue
            if v is None:
                key = (c, s, "x", kind or "S")
            else:
                key = (c, s, vt + v)
            g = groups.get(key)
            if g is None:
                g = groups[key] = {"c": c, "s": s, "v": v, "vt": vt, "verse": None, "pre": pending[:] if v else [], "b": [], "col": []}
                if v:
                    pending.clear()
                order.append(key)
            if "verse" in cls.split() and kind is None:
                g["verse"] = txt
            elif "colophon" in cls or kind == "E":
                g["col"].append(txt)
            elif kind == "I" or "kind-avatarika" in cls:
                g["pre"].append(txt)
            else:
                g["b"].append(txt)
    out = []
    for key in order:
        g = groups[key]
        parts = [str(int(x)) for x in (g["c"], g["s"], g["v"]) if x is not None]
        if g.get("vt") == "K":
            parts = [parts[0], "K" + parts[-1]]
        if drop_chapter and len(parts) > 1 and g["s"] is None:
            parts = parts[1:]
        if g["v"] is None:
            ref = ("intro" if not g["col"] or g["pre"] or g["b"] else "colophon") + "-" + ".".join(parts[:2])
            body = g["pre"] + g["b"] + g["col"]
            out.append({"ref": ref, "kind": "bhashya", "sanskrit_mula": None,
                        "sanskrit_bhashya": "\n".join(body) or None, "sanskrit": "\n".join(body) or None, "english": None})
            continue
        bh = g["pre"] + g["b"] + g["col"]
        bhs = "\n".join(bh) or None
        out.append({"ref": ".".join(parts), "kind": "mula+bhashya", "sanskrit_mula": g["verse"],
                    "sanskrit_bhashya": bhs, "sanskrit": "\n".join(x for x in (g["verse"], bhs) if x), "english": None})
    return out
