import json, re
from common import ROOT, RAW, write
import wl

SLUG = "mandukya-upanishad-madhva-commentary"
CACHE = RAW / "mandukya_madhva_wl" / "pages.json"
BHASYA = re.compile(r"^Madhva[’']s commentary called the Bh[āa]ṣya", re.I)
SALUT = re.compile(r"^Madhva[’']s salutation", re.I)
NOTE = re.compile(r"^[\[\(]?\s*Notes?\b", re.I)
TITLE = re.compile(r"^(?:Mantra|Karika verses?)\s+(\d+)\.(\d+)(?:-(\d+))?$")
LABEL = re.compile(r"^(\d+)\.?\s*\((?:U|K)\d+\)\.?\s*")
TAIL = re.compile(r"\s*[—-]\s*\d+\.?\s*$")


def pages():
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    _, toc = wl.toc(SLUG)
    out = [{"id": i, "title": t, "lines": wl.page_text("https://www.wisdomlib.org" + h)} for i, t, h in toc]
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def split_page(lines):
    mula, salut, comm, state = [], [], [], "mula"
    has_b = any(BHASYA.match(l) for l in lines)
    for l in lines:
        if state == "notes" and not has_b and not NOTE.match(l):
            state = "comm"
        if BHASYA.match(l):
            state = "comm"
        elif SALUT.match(l):
            state = "salut"
        elif l.strip() == "Finis.":
            state = "end"
        elif state == "mula" and NOTE.match(l):
            state = "notes"
        elif state == "comm" and NOTE.match(l):
            continue
        elif state == "mula":
            mula.append(l)
        elif state == "salut":
            salut.append(l)
        elif state == "comm":
            comm.append(l)
    return mula, salut, comm


def clean_verse(t):
    return TAIL.sub("", LABEL.sub("", t.strip())).strip()


def verses(mula, a, lo, hi):
    n = hi - lo + 1
    if n == 1:
        return {lo: clean_verse(" ".join(mula))}
    out, cur = {}, None
    for l in mula:
        m = re.match(r"^(\d+)\.?\s*\((?:U|K)\d+\)", l)
        if m and lo <= int(m.group(1)) <= hi:
            cur = int(m.group(1))
            out[cur] = clean_verse(l)
        elif cur is not None:
            out[cur] += " " + l
    return out


def main():
    P = pages()
    path = ROOT / "upanishads/mandukya_madhva.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    units = {u["ref"]: u for u in d["units"]}
    verse_en, comm_en, kind = {}, {}, {}
    for p in P:
        m = TITLE.match(p["title"])
        if not m or not p["lines"]:
            continue
        a, lo = int(m.group(1)), int(m.group(2))
        hi = int(m.group(3)) if m.group(3) else lo
        mula, _, comm = split_page(p["lines"])
        for k, v in verses(mula, a, lo, hi).items():
            verse_en[(a, k)] = v
        key = (a, lo, hi)
        comm_en[key] = "\n".join(comm).strip()
        kind[key] = p["title"].startswith("Mantra")

    chant = next(p for p in P if p["title"] == "Peace chant")
    cm, cs, cc = split_page(chant["lines"])

    def has_comm(u):
        return any(x["role"] == "bhashya" and x.get("sanskrit") for x in u.get("parts", []))

    def put(u, mula_en, comm):
        parts = [x for x in u.get("parts", [])]
        for x in parts:
            x.pop("english", None)
        mp = next((x for x in parts if x["role"] == "mula"), None)
        if mp is None:
            mp = {"role": "mula", "sanskrit": u["sanskrit"] if u["scope"] == "mula" else None}
            parts.insert(0, mp)
        bp = next((x for x in parts if x["role"] == "bhashya"), None)
        if comm and bp is None:
            bp = {"role": "bhashya"}
            parts.append(bp)
        if mula_en:
            mp["english"] = mula_en
        if comm:
            bp["english"] = comm
        if u["scope"] == "mula+commentary":
            u["english"] = "\n".join(x for x in (mula_en, comm) if x) or None
        else:
            u["english"] = mula_en or None
        parts = [x for x in parts if x.get("sanskrit") or x.get("english")]
        if parts and not (u["scope"] == "mula" and len(parts) == 1 and not comm):
            u["parts"] = parts
        else:
            u.pop("parts", None)

    for ref in list(units):
        u = units[ref]
        if ref == "intro":
            put(u, " ".join(cm), "\n".join(cs + cc).strip())
        elif ref == "intro-2":
            u["english"] = " ".join(cm) or None
        elif re.match(r"^\d/\d+$", ref):
            u["english"] = None
            for x in u.get("parts", []):
                x.pop("english", None)

    pending = []
    for ref in [r for r in units if re.match(r"^\d/\d+$", r)]:
        u = units[ref]
        a, b = map(int, ref.split("/"))
        key = next((k for k in comm_en if k[0] == a and k[1] <= b <= k[2]), None)
        if key is None:
            continue
        shared = key[2] > key[1]
        carriers = [f"{a}/{i}" for i in range(key[1], key[2] + 1) if f"{a}/{i}" in units and has_comm(units[f"{a}/{i}"])]
        carrier = max(carriers, key=lambda r: len(units[r]["sanskrit"])) if carriers else None
        c = comm_en[key] if (not shared or carrier == ref) else ""
        mula_en = verse_en.get((a, b))
        if has_comm(u):
            put(u, mula_en, "\n".join(x for x in pending + [c] if x))
            pending = []
        else:
            if c and not kind[key] and not shared or (c and shared and carrier is None and not kind[key]):
                pending.append(c)
                c = ""
            elif c and not kind[key] and shared:
                pending.append(c)
                c = ""
            put(u, mula_en, c)
        if shared and carrier and carrier != ref and not has_comm(u):
            pass

    n = sum(1 for u in d["units"] if u["english"])
    d["notes"] = ("Sanskrit from Setutila/Sarvamula JSON/manduka_bhashya.json (CC0, Tattvavada corpus; Madhva bhashya). ref = chapter/verse as printed in Setutila; "
                  "chapters 1-4 number Mantras and Gaudapada Karikas straight through, as wisdomlib does. Setutila holds the verse (mula) and, for some verses, Madhva's commentary. "
                  "English: Srisa Chandra Vasu, wisdomlib. A unit's english is the verse translation, plus the commentary translation when the unit's Sanskrit holds the commentary "
                  "(mula+commentary scope). Vasu's notes are left out. Commentary pages for Karika verses whose Sanskrit has no commentary of its own are added to the next unit that has it "
                  "(1/15, 2/6, 3/9, 4/7), because Madhva comments on those verses together. Commentary on Mantras 1, 3.1-3.3 and 4.1 has no Sanskrit in Setutila, so it is kept only in parts "
                  "(bhashya, english only). Range commentary for 2/6-7 sits on 2/6. Colophons and the repeated peace chant (intro-2 carries its translation) are the only other gaps. "
                  f"{n} of {len(d['units'])} units have english.")
    d["alignment"] = "by_ref"
    write("upanishads/mandukya_madhva.json", d)
    print(n, "of", len(d["units"]))


if __name__ == "__main__":
    main()
