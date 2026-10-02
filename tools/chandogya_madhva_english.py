import json, re, time
from common import ROOT, RAW
import wl

SLUG = "chandogya-upanishad-madhva-commentary"
CACHE = RAW / "chandogya_madhva_wl"
ORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8, "eight": 8, "ninth": 9, "tenth": 10,
       "eleventh": 11, "twelfth": 12, "thirteenth": 13, "fourteenth": 14, "fifteenth": 15, "sixteenth": 16, "seventeenth": 17, "eighteenth": 18, "nineteenth": 19,
       "twentieth": 20, "twenty": 20}
DEV = {"प्रथम": 1, "द्वितीय": 2, "तृतीय": 3, "चतुर्थ": 4, "पञ्चम": 5, "षष्ठ": 6, "षष्ट": 6, "सप्तम": 7, "अष्टम": 8, "नवम": 9, "दशम": 10, "एकादश": 11,
       "द्वादश": 12, "त्रयोदश": 13, "चतुर्दश": 14, "पञ्चदश": 15, "षोडश": 16, "सप्तदश": 17, "अष्टादश": 18, "एकोनविंश": 19, "विंश": 20}
HEAD = re.compile(r"(?i)^(?:General commentary of\s+)?(\w+)\s+adhyaya,\s+(?:khandas\s+)?([\w-]+)(?:\s+(?:through|and|to)\s+([\w-]+))?")
BHASYA = re.compile(r"^Madhva[’']s commentary called the Bh[āa]ṣya", re.I)
MANTRA = re.compile(r"^Mantra\s+(\d+)\.(\d+)\.(\d+)")
NOTE = re.compile(r"^(?:\[?\s*Note\b|\[?Notes?\.)")


def dev_num(w):
    return next((v for k, v in sorted(DEV.items(), key=lambda x: -len(x[0])) if w.startswith(k)), None)


def en_num(w):
    w = w.lower()
    if w in ORD:
        return ORD[w]
    if w.startswith("twenty-") or w.startswith("twenty "):
        return 20 + ORD.get(re.split(r"[- ]", w, maxsplit=1)[1])
    return None


def pages():
    CACHE.mkdir(parents=True, exist_ok=True)
    idx = CACHE / "toc.json"
    if idx.exists():
        toc = json.loads(idx.read_text())
    else:
        _, seen = wl.toc(SLUG)
        toc = [(i, t, u) for i, t, u in seen if HEAD.match(t)]
        idx.write_text(json.dumps(toc, ensure_ascii=False))
    out = []
    for i, t, u in toc:
        m = HEAD.match(t)
        a, k0 = en_num(m.group(1)), en_num(m.group(2))
        k1 = en_num(m.group(3)) if m.group(3) else k0
        if t.lower().startswith("general commentary"):
            k0, k1 = 8, 16
        f = CACHE / f"{i}.json"
        if f.exists():
            lines = json.loads(f.read_text())
        else:
            lines = wl.page_text("https://www.wisdomlib.org" + u)
            if lines is None:
                raise SystemExit(f"fetch failed {t}")
            f.write_text(json.dumps(lines, ensure_ascii=False))
            time.sleep(0.5)
        out.append(((a, k0, k1), t, lines))
    return out


def entries(P):
    out = []
    for (a0, k0, k1), title, lines in P:
        cur, on, buf = (a0, k0, 0), title.lower().startswith("general"), []
        if on:
            cur = (a0, 8, 0)

        def flush():
            if buf:
                out.append((cur, "\n".join(buf)))
                buf.clear()
        for l in lines:
            m = MANTRA.match(l)
            if m:
                flush()
                cur, on = tuple(int(x) for x in m.groups()), False
            elif BHASYA.match(l):
                on = True
            elif on and not NOTE.match(l):
                buf.append(l)
        flush()
    return out


def salutation(lines):
    for i, l in enumerate(lines):
        if l.lower().startswith("madhva") and "salutation" in l.lower():
            return lines[i + 1]
    return None


def main():
    P = pages()
    p = ROOT / "upanishads/chandogya_madhva.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    keys = []
    for u in d["units"]:
        m = re.match(r"(\S+)ोऽध्यायः / (\S+?)(?:ः)? खण्डः", u["ref"])
        keys.append((dev_num(m.group(1)), dev_num(m.group(2))) if m else None)
    E = entries(P)
    n = 0
    for i, u in enumerate(d["units"]):
        if u["ref"] == "preface":
            en = salutation(P[0][2])
        else:
            nxt = next((keys[j] for j in range(i + 1, len(keys)) if keys[j] and keys[j][0] == keys[i][0]), None)
            lo = (keys[i][0], keys[i][1], 0)
            hi = (keys[i][0], nxt[1], 0) if nxt else (keys[i][0] + 1, 0, 0)
            en = "\n".join(t for k, t in E if lo <= k < hi) or None
        u["english"] = en
        n += bool(en)
    d["alignment"] = "by_ref"
    d["notes"] = (d["notes"] or "") + f" [English: Srisa Chandra Vasu 1909 via wisdomlib, only the translation of Madhva's commentary (the blocks after 'Madhva's commentary called the Bhashya'), without Vasu's notes and without the mantra translations. Setutila units start at a khanda and run to the next unit's khanda, so each unit's english joins the commentary blocks of every mantra from its khanda up to the next unit's khanda, or to the end of its adhyaya (a unit's Sanskrit ends at the adhyaya colophon). {n} of {len(d['units'])} units have english.]"
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("chandogya_madhva english", n, "of", len(d["units"]))


if __name__ == "__main__":
    main()
