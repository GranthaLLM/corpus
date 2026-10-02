import json, re, sys
from common import ROOT, RAW
import shivaji_to_unicode as sh

DEVRE = re.compile("[ऀ-ॿ]")
STRIP = re.compile(r"[^ऀ-ॿ]|[।॥ऽ॒॑᳚॓॔०-९ः‌‍ँं]")
VERSE_END = re.compile(r"\|\|\s*(\d+)\s*\|\|[”\"]?\s*$")


def norm(s):
    return STRIP.sub("", s or "")


def tri(s):
    return {s[i:i + 3] for i in range(len(s) - 2)}


def conv(s):
    return sh.convert(s)


def sections(text):
    """Split the pdftotext dump at 'Upanishad' / 'Bhashya' / 'Further Explanation' headings."""
    out, cur, kind = [], [], None
    for l in text.split("\n"):
        s = l.strip()
        m = re.fullmatch(r"(Upanishad|Bhashya|Bhasya|Further [Ee]xplanation)\s*:?", s)
        if m:
            if cur:
                out.append((kind, "\n".join(cur)))
            kind = "mula" if m.group(1) == "Upanishad" else "bhashya" if m.group(1).startswith("Bh") else "further"
            cur = []
        elif re.search(r"Thus ends|^\s*The (First|Second|Third|Fourth|Fifth|Sixth)\b|Chapter|Question|Valli|Khanda|\|\|\s*[a-z`]+ [A-Za-z`]+\s*\|\|\s*$", s) and kind:
            out.append((kind, "\n".join(cur)))
            kind, cur = None, []
        elif kind:
            cur.append(l)
    if cur and kind:
        out.append((kind, "\n".join(cur)))
    return out


def mantra_items(body):
    """Mantra Sanskrit lines end with '|| n ||'; the English paragraph follows."""
    lines = [l.strip() for l in body.split("\n")]
    out, i = [], 0
    while i < len(lines):
        if lines[i] and VERSE_END.search(lines[i]):
            j = i
            while j > 0 and lines[j - 1] and not sh.is_english(lines[j - 1]) and not VERSE_END.search(lines[j - 1]):
                j -= 1
            dev = conv(" ".join(lines[j:i + 1]))
            k, en = i + 1, []
            while k < len(lines) and (lines[k] == "" and not en or (lines[k] and sh.is_english(lines[k]) and not VERSE_END.search(lines[k]))):
                if lines[k]:
                    en.append(lines[k])
                k += 1
            out.append((dev, " ".join(en)))
            i = k
        else:
            i += 1
    return out


QUOTE = re.compile(r"[“\"]([^”\"]+)[”\"]\s*[–\-—]\s*(.*?)(?=[“\"][^”\"]*[A-Za-z`|\\]{3}|\Z)", re.S)


def bhashya_items(body):
    out = []
    for m in QUOTE.finditer(body):
        raw, en = m.group(1), m.group(2)
        if sh.is_english(raw):
            continue
        out.append((conv(raw.replace("\n", " ")), re.sub(r"\s+", " ", en).strip()))
    return out


def parse(path):
    text = path.read_text(encoding="utf-8")
    M, Bh = [], []
    for kind, body in sections(text):
        if kind == "mula":
            M += mantra_items(body)
        elif kind == "bhashya":
            Bh += bhashya_items(body)
    return M, Bh


if False:
    M, Bh = parse(RAW / "sonde" / sys.argv[1])
    print(len(M), len(Bh))
    for dev, en in M[:5]:
        print("M", dev[:80], "|", en[:80])
    for dev, en in Bh[:5]:
        print("B", dev[:80], "|", en[:80])


def cover(q, text):
    t = tri(q)
    return len(t & tri(text)) / max(1, len(t))


def fill(name, sonde_file, replace=True):
    path = ROOT / "upanishads" / f"{name}.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    M, Bh = parse(RAW / "sonde" / sonde_file)
    units = d["units"]
    part = lambda u, r: next((p for p in u.get("parts", []) if p["role"] == r), None)
    mula_txt = [norm((part(u, "mula") or {}).get("sanskrit") or (u["sanskrit"] if u["scope"] == "mula" else "")) for u in units]
    bh_txt = [norm((part(u, "bhashya") or {}).get("sanskrit") or "") for u in units]
    mm, bb = {}, {}
    for dev, en in M:
        nd = norm(dev)
        if len(nd) < 10 or not en:
            continue
        sc = [(cover(nd, t), i) for i, t in enumerate(mula_txt) if t]
        if not sc:
            continue
        c, i = max(sc)
        if c >= 0.5 and i not in mm:
            mm[i] = en
    for dev, en in Bh:
        nd = norm(dev)
        if len(nd) < 10 or not en:
            continue
        sc = [(cover(nd, t), i) for i, t in enumerate(bh_txt) if t]
        if not sc:
            continue
        c, i = max(sc)
        if c >= 0.5:
            bb.setdefault(i, []).append((nd, en))
    stats = {"complete": 0, "filled": 0, "replaced": 0, "kept": 0, "partial": []}
    for i, u in enumerate(units):
        if u["ref"].startswith(("colophon", "intro")) or not u.get("sanskrit"):
            continue
        has_b = bool(bh_txt[i])
        mula_ok = (i in mm) if mula_txt[i] else True
        b_ok = True
        if has_b:
            cov = sum(len(q) for q, _ in bb.get(i, [])) / len(bh_txt[i])
            b_ok = cov >= 0.55
        if not (mula_ok and b_ok and (i in mm or bb.get(i))):
            if not u.get("english"):
                stats["partial"].append(u["ref"])
            else:
                stats["kept"] += 1
            continue
        mula_en = mm.get(i)
        bh_en = " ".join(e for _, e in bb.get(i, []))
        had = bool(u.get("english"))
        if had and not replace:
            continue
        for p in u.get("parts", []):
            p.pop("english", None)
        mp, bp = part(u, "mula"), part(u, "bhashya")
        if mp is not None and mula_en:
            mp["english"] = mula_en
        if bp is not None and bh_en:
            bp["english"] = bh_en
        u["english"] = "\n".join(x for x in (mula_en, bh_en) if x) or None
        stats["replaced" if had else "filled"] += 1
    return d, stats


def apply(name, sonde_file, cite):
    from common import write
    d, st = fill(name, sonde_file)
    n = st["filled"] + st["replaced"]
    d["notes"] += (f" English for {n} units is now Nagesh D. Sonde's translation (his Sanskrit decoded with tools/shivaji_to_unicode.py and matched to the units by trigram coverage); "
                   f"{st['filled']} of them had no English before. Units where Sonde's quotes cover under 55% of the bhashya Sanskrit keep the wisdomlib English.")
    src = d["source_english"]
    d["source_english"] = (src if isinstance(src, list) else [src]) + [{"citation": cite, "url": "https://nageshsonde.com/", "license": "Author states: not protected by any copyright; free to copy and distribute"}]
    write(f"upanishads/{name}.json", d)
    return st


if __name__ == "__main__" and len(sys.argv) == 1:
    for name, f, cite in (("kena_madhva", "kena.txt", "Nagesh D. Sonde, Bhashya on Kena Upanishad (Madhva)"),
                          ("katha_madhva", "katha.txt", "Nagesh D. Sonde, Katha Upanishad with Madhva's commentary"),
                          ("mundaka_madhva", "mundaka.txt", "Nagesh D. Sonde, Atharvan (Mundaka) Upanishad, Madhva's Bhashya")):
        print(name, apply(name, f, cite))
