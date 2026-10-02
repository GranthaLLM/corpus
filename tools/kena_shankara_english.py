import json, re
from common import ROOT, RAW, write
import wl

SLUG = "kena-upanishad-shankara-bhashya"
CACHE = RAW / "kena_shankara_wl" / "pages.json"
VERSES = {"1.1": [1], "1.2": [2], "1.3": [3], "1.4": [3], "1.5": [4], "1.6": [5], "1.7": [6], "1.8": [7], "1.9": [8],
          "2.1": [9], "2.2": [10], "2.3": [11], "2.4": [12], "2.5": [13]}
VERSES.update({f"3.{k}": [13 + k] for k in range(1, 13)})
VERSES.update({f"4.{k}": [25 + k] for k in range(1, 10)})
TRANS = re.compile(r"^(\d+)\.\s+(.*)")
COMHEAD = re.compile(r"^Shankara[’']s Commentary", re.I)


def pages():
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    _, toc = wl.toc(SLUG)
    out = [{"id": i, "title": t, "lines": wl.page_text("https://www.wisdomlib.org" + h)} for i, t, h in toc]
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def parse(P):
    trans, com, intro = {}, {}, None
    for p in P:
        L = p["lines"] or []
        t = p["title"].lower()
        if t.startswith("shri shankara"):
            intro = L
            continue
        m = re.match(r"^verse (\d+)(?:-(\d+))?$", t)
        if not m:
            continue
        lo = int(m.group(1))
        hi = int(m.group(2) or lo)
        state, cur = "pre", None
        cl = []
        for l in L:
            if COMHEAD.match(l):
                state = "com"
                continue
            if state == "com":
                cl.append(re.sub(r"^Com\.?\s*[—-]\s*", "", l))
                continue
            mm = TRANS.match(l)
            if mm and lo <= int(mm.group(1)) <= hi and not re.search(r"[ऀ-ॿ]", l):
                cur = int(mm.group(1))
                trans[cur] = re.sub(r"\s*\(\d+\)\.?\s*$", "", mm.group(2)).strip()
            elif cur is not None and state == "pre" and not re.search(r"[ऀ-ॿ]", l) and not re.match(r"^[a-zāīūṛṃśṣḥṅñṭḍṇ' |0-9-]+$", l):
                trans[cur] += " " + l
        com[(lo, hi)] = cl
    return trans, com, intro


def main():
    P = pages()
    trans, com, intro = parse(P)
    d = json.loads((ROOT / "upanishads/kena_shankara.json").read_text(encoding="utf-8"))
    units = {u["ref"]: u for u in d["units"]}

    cut = max(i for i, l in enumerate(intro) if l.startswith("The Sratis say") or l.startswith("The Srutis say"))
    intro_head, intro_tail = intro[:cut], intro[cut:]
    sp = re.split(r"(?<=It\.)\s+(?=It is distinct)", trans[3])
    t3 = {"1.3": sp[0], "1.4": sp[1]} if len(sp) == 2 else None
    c3 = com[(3, 3)]

    def has_b(u):
        return any(p["role"] == "bhashya" and p.get("sanskrit") for p in u.get("parts", []))

    def put(u, mula_en, comm):
        for x in u.get("parts", []):
            x.pop("english", None)
        parts = list(u.get("parts", []))
        mp = next((x for x in parts if x["role"] == "mula"), None)
        bp = next((x for x in parts if x["role"] == "bhashya"), None)
        if mula_en and mp:
            mp["english"] = mula_en
        if comm:
            if bp is None:
                bp = {"role": "bhashya"}
                parts.append(bp)
            bp["english"] = comm
        u["english"] = "\n".join(x for x in (mula_en, comm) if x) or None
        parts = [x for x in parts if x.get("sanskrit") or x.get("english")]
        if parts:
            u["parts"] = parts

    for u in d["units"]:
        u["english"] = None
        for x in u.get("parts", []):
            x.pop("english", None)
        u.pop("meta", None)

    units["intro-1"]["english"] = "\n".join(intro_head)
    pagecom = {}
    for (lo, hi), cl in com.items():
        pagecom[(lo, hi)] = "\n".join(cl)
    parked = []
    for ref, vs in VERSES.items():
        u = units[ref]
        v = vs[0]
        mula_en = (t3[ref] if t3 and ref in t3 else None) if v == 3 else trans.get(v)
        key = next(k for k in com if k[0] <= v <= k[1])
        ukeys = [r for r, vv in VERSES.items() if key[0] <= vv[0] <= key[1]]
        carriers = [r for r in ukeys if has_b(units[r])]
        c = ""
        if ref == "1.3":
            c = c3[0][:c3[0].index("Considering that the previous portion")]
        elif ref == "1.4":
            c = "\n".join([c3[0][c3[0].index("Considering that the previous portion"):]] + c3[1:])
        elif ref in carriers and len(carriers) == 1:
            c = pagecom[key]
        elif ref in carriers:
            parked.append(ref)
        if ref == "1.1":
            c = "\n".join(intro_tail + [c])
        put(u, mula_en, c if has_b(u) else "")
        if c and not has_b(u):
            u.setdefault("meta", {})["english_unsplit"] = c

    n = sum(1 for u in d["units"] if u["english"])
    d["notes"] = ("Sanskrit (verse + Śaṃkara's bhashya, Devanagari) from Advaita Sharada /read/kena-pada-bhashya. mula part = verse, bhashya part = avatarika/bhashya paragraphs incl. interstitial intros and colophon lines. "
                  "English: Sitarama Sastri 1905 via wisdomlib, joined by verse number (Sastri numbers 1-34 straight through; Sharada's 1.3 and 1.4 are Sastri's verse 3, and its khanda 1 has 9 verses against Sastri's 8). "
                  "A unit's english is the verse translation plus, when the unit's Sanskrit holds the commentary, the commentary translation. Where Sastri comments on several verses together, the commentary English goes to the Sharada unit that holds the Sanskrit commentary (3.6, 3.10, 3.12); "
                  "the verses before it get translation only. Sastri's verse 3 comment is split between 1.3 and 1.4 where the Sanskrit of 1.4 begins ('Considering that the previous portion'). The end of Sastri's introduction (from 'The Sratis say') belongs to Sharada 1.1 and is placed there. "
                  f"{n} of {len(d['units'])} units have english; colophons have none.")
    write("upanishads/kena_shankara.json", d)
    print(n, "of", len(d["units"]), "parked", parked)


if __name__ == "__main__":
    main()
