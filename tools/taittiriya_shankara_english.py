import html, json, re
from common import ROOT, RAW, write

SRC = RAW / "aitareya_taittiriya_sastri_djvu.txt"
SIZES = [12, 9, 10]
HDR = re.compile(r"^(WITH S\w* \w+ ?SANKAR|\d+\s+THE TAITT|.{0,8}THE TAITTIRI)")
COM = re.compile(r"^[CQG]o[mn][.,*\s—-]")
END = re.compile(r"^(H ?ere|Thus) ends")


def lines():
    t = SRC.read_text(encoding="utf-8")
    a = t.index("<pre>") + 5 if "<pre>" in t else 0
    b = t.index("</pre>") if "</pre>" in t else len(t)
    return html.unescape(t[a:b]).split("\n")


def junk(l):
    s = l.strip()
    if not s:
        return False
    if HDR.search(s) or re.match(r"^WITH S", s):
        return True
    bad = sum(1 for c in s if c in "^|~{}_\\<>")
    if bad >= 2 or bad / len(s) > 0.05:
        return True
    words = re.findall(r"[A-Za-z']+", s)
    if not words:
        return True
    return sum(1 for w in words if len(w) >= 2 and re.search(r"[aeiouAEIOU]", w)) / len(words) < 0.5


def paras(ls):
    out, cur = [], []
    for l in ls:
        if junk(l):
            continue
        if not l.strip():
            if cur:
                out.append(" ".join(cur))
                cur = []
        else:
            cur.append(l.strip())
    if cur:
        out.append(" ".join(cur))
    m = []
    for p in out:
        if m and (not re.search(r"[.?)\"'”’*]\s*$", m[-1]) or re.match(r"[a-z]", p)) and not COM.match(p):
            m[-1] += " " + p
        else:
            m.append(p)
    return [re.sub(r"(\w)- (\w)", r"\1\2", p) for p in m if not END.match(p)]


def items(ps):
    out = []
    for p in ps:
        if COM.match(p) and out:
            out[-1].append(p)
        else:
            out.append([p])
    return out


def main():
    B = lines()
    start = next(i for i, l in enumerate(B) if "INTRODUCTION TO THE SI" in l)
    end = next(i for i, l in enumerate(B) if l.startswith("Thus ends the Bhrigu Valli"))
    heads = [i for i in range(start, end + 1) if re.match(r"^CHAPTER\b", B[i])]
    assert len(heads) == sum(SIZES), len(heads)
    chap = {}
    k = 0
    for v, n in enumerate(SIZES, 1):
        for c in range(1, n + 1):
            e = heads[k + 1] if k + 1 < len(heads) else end
            chap[(v, c)] = paras(B[heads[k] + 1:e])
            k += 1
    intro = paras(B[start + 1:heads[0]])
    intro = [p for p in intro if not re.match(r"^THE SI", p)]

    d = json.loads((ROOT / "upanishads/taittiriya_shankara.json").read_text(encoding="utf-8"))
    units = d["units"]
    by_ch = {}
    for u in units:
        m = re.match(r"^(\d)\.(\d+)\.(\d+)$", u["ref"])
        if m:
            by_ch.setdefault((int(m.group(1)), int(m.group(2))), []).append(u)
    for u in units:
        u["english"] = None
        u.pop("meta", None)
    parked, joined = [], 0

    ch = (u for u in units if u["ref"] == "intro-1.1").__next__()
    ch["english"] = "\n".join(intro)
    joined += 1

    peace = " ".join(l.strip() for l in B[heads[21] - 40:heads[21]] if l.strip() and not junk(l))
    m = re.search(r"May it \(the knowledge of Brahman\) protect us both.*?Peace, Peace, Peace\.?", peace)
    for u in units:
        if u["ref"] == "3.1.0" and m:
            u["english"] = m.group(0)
            joined += 1

    for key, us in by_ch.items():
        ps = chap[key]
        if key == (2, 1):
            u0 = next(u for u in us if u["ref"] == "2.1.0")
            u0["english"] = "\n".join(ps[:2])
            us = [u for u in us if u is not u0]
            ps = ps[2:]
            joined += 1
        if key == (3, 1):
            us = [u for u in us if u["ref"] != "3.1.0"]
        its = items(ps)
        ok = lambda u, e: 0.6 <= len(e) / len(u["sanskrit"]) <= 3.5
        if len(us) == 1 and ok(us[0], "\n".join(ps)):
            us[0]["english"] = "\n".join(ps)
            joined += 1
        elif len(us) > 1 and len(its) == len(us) and all(ok(u, "\n".join(it)) for u, it in zip(us, its)):
            for u, it in zip(us, its):
                u["english"] = "\n".join(it)
                joined += 1
        else:
            us[0].setdefault("meta", {})["english_unsplit"] = "\n".join(ps)
            parked.append(f"{key[0]}.{key[1]}")

    d["notes"] = ("Sanskrit (verse + Śaṃkara's bhashya, Devanagari) from Advaita Sharada /read/taittiriya-bhashya. mula part = verse, bhashya part = avatarika/bhashya paragraphs incl. interstitial intros and colophon lines. "
                  "English: Sitarama (Mahadeva) Sastri, Aitareya and Taittiriya Upanishads with Sri Sankara's commentary (Madras 1903), OCR from archive.org, "
                  "chapters = Sharada anuvakas. A chapter's translation and commentary translation are one english string on its unit (not split into parts). "
                  "A chapter's English goes to its Sharada unit only when the chapter has one unit (or Sastri's items match the units one to one) and the English/Sanskrit length ratio is plausible. "
                  f"For {', '.join(parked)} the Sharada segmentation differs from Sastri's, so the chapter English is parked in meta.english_unsplit of its first unit and english stays null. "
                  "Colophons have english null.")
    d["source_english"] = {"citation": "Sastri, Aitareya and Taittiriya Upanishads with Sri Sankara's commentary (1903), OCR", "url": "https://archive.org/details/AitareyataittiriyaUpanishadsWithShankaraBhashya-English", "license": "public domain (1903)"}
    write("upanishads/taittiriya_shankara.json", d)
    print("joined", joined, "parked", parked, "of", len(units))


if __name__ == "__main__":
    main()
