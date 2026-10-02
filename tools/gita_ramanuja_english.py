import collections, html, json, re
from common import ROOT, RAW, write
import gita_warrier_english as gw

SRC = RAW / "adidevananda_gita_djvu.txt"
SPEAKER = re.compile(r"^(?:(?:Sanjaya|Sarijaya|Samjaya|Dhrt\w+|Dhrta\w+|The Blessed Lord|The Lord|Arjuna|Sri Bhagavan|Bhagavan|Krsna|Krishna)\s+said\s*[:.]?\s*)", re.I)
LABEL = re.compile(r"^\(?[\dIlOo!|]{1,3}\s*[.,)]\s+")


def lines():
    t = SRC.read_text(encoding="utf-8")
    return t.split("\n") if "<pre>" not in t else html.unescape(t[t.index("<pre>") + 5:t.index("</pre>")]).split("\n")


RUNHEAD = re.compile(r"\b\d{1,2}\s*-\s*\d{1,3}\]\s+[A-Z’'.,;: -]{6,}?\s+\d{1,3}\b|\b\d{1,3}\s+SRI RAMANUJA \w+ BHASYA\s*[\[\(I]?\s*Ch\.?\s*\d+\]?|\bSRI RAMANUJA \w+ BHASYA\s*[\[\(I]?\s*Ch\.?\s*\d+\]?|\b[IVX]*\d*-\d+\]\s+[A-Z’'.,;: -]{6,}?\s+\d{1,3}\b")


def clean(t):
    t = RUNHEAD.sub(" ", t)
    t = SPEAKER.sub("", t.strip())
    t = LABEL.sub("", t, count=1)
    return re.sub(r"(\w)- (\w)", r"\1\2", re.sub(r"\s+", " ", t)).strip()


def mula_of(u):
    m = [p for p in u.get("parts", []) if p["role"] == "mula"]
    return m[0]["sanskrit"] if m else u["sanskrit"].split("\n")[0]


def merge_halves(units):
    out, i = [], 0
    while i < len(units):
        u = units[i]
        m = re.match(r"^(\d+\.\d+)ab(-\d+)?$", u["ref"])
        if m and i + 1 < len(units) and re.match(r"^" + re.escape(m.group(1)) + r"cd", units[i + 1]["ref"]):
            v = units[i + 1]
            u["sanskrit"] = u["sanskrit"].split("\n")[0] + "\n" + v["sanskrit"].split("\n")[0] + ("\n" + "\n".join(u["sanskrit"].split("\n")[1:]) if "\n" in u["sanskrit"] else "")
            u["ref"] = m.group(1)
            for p in u.get("parts", []):
                if p["role"] == "mula":
                    p["sanskrit"] = p["sanskrit"] + "\n" + v["sanskrit"].split("\n")[0]
            out.append(u)
            i += 2
            continue
        out.append(u)
        i += 1
    return out


def main(write_out=True):
    B = lines()
    heads, want = [], 1
    for i, l in enumerate(B):
        if i > 2300 and re.match(r"^\s*Chapter\s+%d\s*$" % want, l):
            heads.append(i)
            want += 1
            if want == 19:
                break
    assert len(heads) == 18, len(heads)
    end = next(i for i in range(heads[-1] + 50, len(B)) if re.match(r"^\s*(APPENDIX|INDEX|Index|Appendix|BIBLIOGRAPHY)", B[i])) if any(re.match(r"^\s*(APPENDIX|INDEX|Index|Appendix|BIBLIOGRAPHY)", B[i]) for i in range(heads[-1] + 50, len(B))) else len(B)
    p = ROOT / "philosophical/bg_ramanuja.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["units"] = merge_halves(d["units"])
    by_ch = collections.defaultdict(list)
    for u in d["units"]:
        if not u["ref"].startswith(("intro", "colophon")):
            by_ch[int(u["ref"].split(".")[0])].append(u)
    old = {u["ref"]: u.get("english") for u in d["units"]}
    stats = collections.Counter()
    weak = []
    for c in range(1, 19):
        a = heads[c - 1] + 1
        b = heads[c] if c < 18 else end
        P = gw.pairs(B, a, b)
        U = by_ch[c]
        got = gw.align([gw.grams(mula_of(u)) for u in U], [gw.grams(x[0]) for x in P])
        idx = sorted((got[i][0], i) for i in got)
        starts = {i: j for j, i in idx}
        order = [i for _, i in idx]
        for n, i in enumerate(order):
            u = U[i]
            j = starts[i]
            nxt = starts[order[n + 1]] if n + 1 < len(order) else len(P)
            if got[i][1] < 0.3:
                weak.append((u["ref"], round(got[i][1], 2)))
                continue
            trans = clean(P[j][1])
            comm = "\n".join(clean_c(x[1]) for x in P[j + 1:nxt] if x[1].strip())
            u["_new"] = (trans, comm, u["scope"] == "mula+commentary")
            u["_dice"] = got[i][1]
        stats["units"] += len(U)
    if write_out:
        apply(d, weak)
    return d, old, weak, stats


def clean_c(t):
    return re.sub(r"(\w)- (\w)", r"\1\2", re.sub(r"\s+", " ", RUNHEAD.sub(" ", t))).strip()


def apply(d, weak):
    filled, short = 0, []
    for u in d["units"]:
        for tgt in [u] + u.get("parts", []):
            tgt.pop("english", None)
        u["english"] = None
        u.pop("meta", None)
        nw = u.pop("_new", None)
        u.pop("_dice", None)
        if not nw:
            continue
        trans, comm, hb = nw
        if hb and len(trans) + len(comm) < 0.5 * len(u["sanskrit"]):
            short.append(u["ref"])
            continue
        parts = list(u.get("parts", []))
        mp = next((x for x in parts if x["role"] == "mula"), None)
        bp = next((x for x in parts if x["role"] == "bhashya"), None)
        if mp is None:
            mp = {"role": "mula", "sanskrit": u["sanskrit"] if u["scope"] == "mula" else None}
            parts.insert(0, mp)
        mp["english"] = trans
        if comm:
            if bp is None:
                bp = {"role": "bhashya"}
                parts.append(bp)
            bp["english"] = comm
        u["english"] = "\n".join(x for x in (trans, comm if hb else "") if x) or None
        parts = [x for x in parts if x.get("sanskrit") or x.get("english")]
        if parts and not (u["scope"] == "mula" and len(parts) == 1 and not comm):
            u["parts"] = parts
        if u["english"]:
            filled += 1
    d["notes"] += (f" [English rebuilt from Adidevananda's printed book (archive.org djvu): the earlier join by verse-number sequence had drifted (chapter 1 carried the book's introduction text on verses). "
                   f"Verse blocks were matched to units by Devanagari similarity (3-gram dice, monotone alignment); a unit's english is the verse translation plus, for mula+commentary units, the commentary paragraphs up to the next verse. "
                   f"ab/cd half-verse units were merged into whole verses. {filled} units filled; left null: weak matches {', '.join(w[0] for w in weak)}; too short: {', '.join(short)}. Book footnotes and running heads can remain.]")
    write("philosophical/bg_ramanuja.json", d)
    print("filled", filled, "weak", weak, "short", short)


if __name__ == "__main__":
    d, old, weak, stats = main()
    print(stats, "weak", weak)
    n = same = 0
    for u in d["units"]:
        if "_new" in u:
            n += 1
            t, c, hb = u["_new"]
            e = "\n".join(x for x in (t, c if hb else "") if x)
            if old.get(u["ref"]) and old[u["ref"]][:60] == e[:60]:
                same += 1
    print("new",n,"same-start-as-old",same)
