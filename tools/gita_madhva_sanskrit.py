import json, re, sys
from common import ROOT, RAW, write
from shivaji_to_unicode import convert_text

SRC = RAW / "sonde_gita_pdf.txt"
ROMAN = {"II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10, "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15, "XVI": 16, "XVII": 17, "XVIII": 18}
CH = re.compile(r"^\s{20,}Chapter\s+([IVX]+)\s*$")
LAB = re.compile(r"^\s*(\d{1,2})((?:\s*[-–—]\s*\d{1,2})*)\s*[.:]\s+(?=\S)")
SEC = re.compile(r"^\s*(Bhashya|Tatparya Nirnaya)\s*:?\s*(.*)$")
QUOTE = re.compile(r"[“\"](.*?)[”\"]\s*[-–—]", re.S)


def groups():
    L = SRC.read_text(encoding="utf-8", errors="replace").split("\n")
    end = next(i for i, l in enumerate(L) if "Eighteenth Chapter" in l)
    ch, cur, out, sec = None, None, [], None
    for l in L[:end]:
        m = CH.match(l)
        if m:
            ch, cur, sec = ROMAN[m.group(1)], None, None
            continue
        if ch is None:
            continue
        m = LAB.match(l)
        if m:
            nums = [int(m.group(1))] + [int(x) for x in re.findall(r"\d+", m.group(2))]
            lo, hi = nums[0], nums[-1]
            if ch == 7 and cur is not None and cur["hi"] >= 25 and lo <= 3:
                ch, cur = 8, None
            if cur is None or lo > cur["hi"] or (lo == cur["hi"] + 1):
                cur = {"ch": ch, "lo": lo, "hi": hi, "Bhashya": [], "Tatparya Nirnaya": []}
                out.append(cur)
                sec = None
                continue
        m = SEC.match(l)
        if m and cur is not None:
            sec = m.group(1)
            cur[sec].append(m.group(2))
            continue
        if cur is not None and sec:
            cur[sec].append(l)
    return out


def sanskrit_of(lines):
    t = " ".join(re.sub(r"\s+", " ", l).strip() for l in lines)
    qs = QUOTE.findall(t)
    return "\n".join(convert_text(q).strip() for q in qs if q.strip())



def unit_range(ref):
    m = re.fullmatch(r"(\d+)/(\d+)(?:-(\d+))?", ref)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3) or m.group(2))) if m else None


def plan(units, G):
    out = []
    for u in units:
        r = unit_range(u["ref"])
        if r is None or not u.get("parts"):
            continue
        gs = [g for g in G if g["ch"] == r[0] and g["lo"] >= r[1] and g["hi"] <= r[2]]
        for q in u["parts"]:
            if q["role"] not in ("bhashya", "tatparya") or q.get("sanskrit") or not q.get("english"):
                continue
            key = "Bhashya" if q["role"] == "bhashya" else "Tatparya Nirnaya"
            sk = "\n".join(s for s in (sanskrit_of(g[key]) for g in gs) if s)
            out.append((u["ref"], q["role"], len(q["english"]), len(sk), [(g["lo"], g["hi"]) for g in gs], sk, q))
    return out


def apply():
    p = ROOT / "philosophical/bg_madhva.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    n = 0
    for r, role, le, ls, gs, sk, q in plan(d["units"], groups()):
        if not (0.25 <= ls / le <= 1.3) or re.search(r"[A-Za-z]", sk) and len(re.findall(r"[A-Za-z]", sk)) / ls > 0.03:
            continue
        q["sanskrit"] = sk
        n += 1
    for r, role, ls, le, gs, en, q in plan_en(d["units"], groups()):
        if le and 1.0 <= le / ls <= 3.5 and len(en) > 20:
            q["english"] = en
    for u in d["units"]:
        if u.get("parts"):
            u["english"] = "\n".join(q["english"] for q in u["parts"] if q.get("english")) or None
    for u in d["units"]:
        if u.get("parts"):
            if u.get("scope") == "mula" and any(q["role"] != "mula" and q.get("sanskrit") for q in u["parts"]):
                u["scope"] = "mula+commentary"
            u["sanskrit"] = "\n".join(q["sanskrit"] for q in u["parts"] if q.get("sanskrit"))
    d["notes"] += (f" Bhashya or Tatparya Sanskrit missing from Setutila for {n} parts was decoded from the Shivaji01 legacy font of Sonde's book (tools/gita_madhva_sanskrit.py); "
                   "about 95% of characters match where both sources exist, so stray misspellings can occur in that Sanskrit.")
    write("philosophical/bg_madhva.json", d)
    print(n)



PAGE = re.compile(r"^\s*\d{1,3}\s*$")


def english_of(lines):
    t = " ".join(re.sub(r"\s+", " ", l).strip() for l in lines if not PAGE.match(l))
    segs = QUOTE.split(t)
    en = [segs[0]] if len(segs) == 1 else segs[2::2]
    return re.sub(r"\s+", " ", " ".join(en)).strip()


def plan_en(units, G):
    out = []
    for u in units:
        r = unit_range(u["ref"])
        if r is None or not u.get("parts"):
            continue
        gs = [g for g in G if g["ch"] == r[0] and g["lo"] >= r[1] and g["hi"] <= r[2]]
        for q in u["parts"]:
            if q["role"] not in ("bhashya", "tatparya") or q.get("english") or not q.get("sanskrit"):
                continue
            key = "Bhashya" if q["role"] == "bhashya" else "Tatparya Nirnaya"
            en = " ".join(s for s in (english_of(g[key]) for g in gs) if s)
            out.append((u["ref"], q["role"], len(q["sanskrit"]), len(en), [(g["lo"], g["hi"]) for g in gs], en, q))
    return out


if __name__ == "__main__":
    apply()
