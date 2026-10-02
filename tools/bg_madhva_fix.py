import html, json, re
from common import ROOT, RAW, write

SRC = RAW / "sonde_gita_djvu.txt"
CH1_START = re.compile(r"^\s*Chapter\s+1\s*$")
LAB = re.compile(r"^\s*(\d{1,2})(?:\s*[-–—]\s*(\d{1,2}))?\s*\.+\s*(?=\S)")
COLOPHON = re.compile(r"(Thus ends the Bhashya and Tatparya Nir\w+.*?[.”\"]\s*(?:\.\s*)?)(?:ooooo.*)?$", re.S | re.I)
MERGES = [(["3/20-25", "3/26"], "3/20-26"), (["4/14-15", "4/16"], "4/14-16"), (["13/31", "13/32", "13/33", "13/34"], "13/31-34"),
          (["16/18-19", "16/20"], "16/18-20"), (["18/72-76", "18/77", "18/78"], "18/72-78")]


def ch1():
    t = SRC.read_text(encoding="utf-8")
    B = html.unescape(t[t.index("<pre>") + 5:t.index("</pre>")]).split("\n")
    a = next(i for i, l in enumerate(B) if i > 700 and CH1_START.match(l))
    b = next(i for i in range(a + 1, len(B)) if re.match(r"^\s*Chapter\s+[UI]{1,2}\s*$", B[i]) or re.match(r"^\s*Chapter\s+II\s*$", B[i]))
    groups, cur = [], None
    for l in B[a + 1:b]:
        m = LAB.match(l)
        if m:
            lo, hi = int(m.group(1)), int(m.group(2) or m.group(1))
            if cur is None or lo >= cur["hi"] or lo == 30:
                if lo == 30 and cur is not None:
                    cur["lines"].append(l[m.end():])
                    continue
                cur = {"lo": lo, "hi": hi, "lines": [l[m.end():]]}
                groups.append(cur)
                continue
        if cur is not None:
            cur["lines"].append(l)
    out = []
    for g in groups:
        t = re.sub(r"\s+", " ", " ".join(g["lines"])).replace("¬ ", "").strip()
        out.append((g["lo"], g["hi"], t))
    return out


def clean_tail(e):
    m = COLOPHON.search(e)
    if not m:
        return e, None
    return e[:m.start()].rstrip(), re.sub(r"\s+", " ", m.group(1)).strip()


def join_sk(u):
    return "\n".join(p["sanskrit"] for p in u["parts"] if p.get("sanskrit")) if u.get("parts") else u["sanskrit"]


def merge(units, refs, new):
    by = {u["ref"]: u for u in units}
    base = by[refs[0]]
    for r in refs[1:]:
        x = by[r]
        if base.get("parts"):
            mp = next(p for p in base["parts"] if p["role"] == "mula")
            mp["sanskrit"] = mp["sanskrit"] + "\n" + x["sanskrit"]
            base["sanskrit"] = join_sk(base)
        else:
            base["sanskrit"] += "\n" + x["sanskrit"]
        units.remove(x)
    base["ref"] = new


def main():
    p = ROOT / "philosophical/bg_madhva.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    units = d["units"]
    for refs, new in MERGES:
        merge(units, refs, new)

    G = ch1()
    assert [(g[0], g[1]) for g in G] == [(1, 1), (2, 12), (12, 19), (20, 23), (24, 46), (47, 47)], [(g[0], g[1]) for g in G]
    texts = {"1/1": G[0][2], "1/2-12": G[1][2], "1/13-19": G[2][2], "1/20-23": G[3][2], "1/24-46": G[4][2], "1/47": G[5][2]}
    colo = None
    texts["1/47"], colo = clean_tail(texts["1/47"])
    for refs, new in [([f"1/{k}" for k in range(13, 20)], "1/13-19"), ([f"1/{k}" for k in range(20, 24)], "1/20-23"), ([f"1/{k}" for k in range(24, 47)], "1/24-46")]:
        merge(units, refs, new)
    by = {u["ref"]: u for u in units}
    for r, t in texts.items():
        by[r]["english"] = t

    lead = re.compile(r"^(?:\d{1,2}\s*[-–.]*\s*){1,3}(?=[A-Z“\"'])")
    for u in units:
        for tgt in [u] + u.get("parts", []):
            if tgt.get("english") and lead.match(tgt["english"]):
                tgt["english"] = lead.sub("", tgt["english"], count=1)

    for i, u in enumerate(units):
        e = u.get("english")
        if not e or u["ref"].startswith("colophon"):
            continue
        e2, c = clean_tail(e)
        if c is None:
            continue
        u["english"] = e2 or None
        for part in u.get("parts", []):
            if part.get("english"):
                part["english"], _ = clean_tail(part["english"])
        if i + 1 < len(units) and units[i + 1]["ref"].startswith("colophon") and not units[i + 1].get("english") and len(units[i + 1]["sanskrit"]) < 400:
            units[i + 1]["english"] = c
    if colo and by["1/47"]:
        nxt = units[units.index(by["1/47"]) + 1]
        if nxt["ref"].startswith("colophon") and not nxt.get("english"):
            nxt["english"] = colo
    d["notes"] += (" [Chapter 1 regrouped to Sonde's verse groups (1; 2-12; 13-19; 20-23; 24-46; 47), with English from the archive.org djvu text of Sonde's book (the Devanagari in that text is garbled and unused); the earlier 1/2-12 unit had the whole chapter's English. "
                   "Units 3/20-26, 4/14-16, 13/31-34, 16/18-20 and 18/72-78 merge the Setutila verses that Sonde translates together with the group before them. The colophon translation that had been appended to the last unit of each chapter was removed from it; it is kept on the colophon unit only where that unit holds just the colophon (Setutila puts commentary text after some colophons).]")
    write("philosophical/bg_madhva.json", d)
    print(len(units))


if __name__ == "__main__":
    main()
