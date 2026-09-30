import re, json
from common import *

CH_START = [624, 705, 2816, 3545, 4073, 4521, 5035, 5547, 5995, 6512, 6927, 7464, 7869, 8514, 8738, 8979, 9121, 9425, 10340]
COUNTS = [47, 72, 43, 42, 29, 47, 30, 28, 34, 42, 55, 20, 34, 27, 20, 24, 28, 78]
GARB = re.compile(r"[`@\[\]\\|%{}]")
QUOTE_SKT = re.compile(r"“[^”]*?[`@\[\]\\|%][^”]*?”\s*[-–]\s*", re.S)
VERSE = re.compile(r"^\x0c?((?:\d+\s*[-–]\s*)*\d+)(?:\s*\.|\s*[-–])\s+(?=\S)")


def garbled(line):
    toks = line.split()
    if not toks:
        return False
    bad = sum(1 for t in toks if GARB.search(t) or re.search(r"aa|oo|Ba|Qa|Ka|xa|Sa", t) and GARB.search(line))
    return len(GARB.findall(line)) >= 2 and bad / len(toks) > 0.25


def clean_block(lines):
    t = "\n".join(lines)
    t = QUOTE_SKT.sub("", t)
    out = []
    for l in t.split("\n"):
        s = l.strip()
        if not s or re.fullmatch(r"\d+", s) or re.fullmatch(r"[ivxl]+", s):
            continue
        if garbled(s):
            continue
        out.append(s)
    return out


def split_sections(lines):
    verse, bh, tp, cur = [], [], [], None
    sec = verse
    for l in lines:
        if re.match(r"^Bhashya\s*:?", l):
            sec = bh
            l = re.sub(r"^Bhashya\s*:?\s*", "", l)
        elif re.match(r"^Tatparya Nirnaya\s*:?", l):
            sec = tp
            l = re.sub(r"^Tatparya Nirnaya\s*:?\s*", "", l)
        if l:
            sec.append(l)
    j = lambda x: re.sub(r"\s+", " ", " ".join(x)).strip() or None
    return j(verse), j(bh), j(tp)


def parse():
    L = (RAW / "sonde_gita.txt").read_text(encoding="utf-8").split("\n")
    res = {}
    for c in range(1, 19):
        seg = L[CH_START[c - 1]:CH_START[c]]
        starts, v = [], 0
        for i, l in enumerate(seg):
            m = VERSE.match(l.strip("\n "))
            if not m:
                continue
            nums = [int(x) for x in re.findall(r"\d+", m.group(1))]
            n, n2 = nums[0], nums[-1]
            if v < n <= min(v + 6, COUNTS[c - 1]) or (v == 0 and n <= 3):
                starts.append((i, n, n2))
                v = n2
        for k, (i, n, n2) in enumerate(starts):
            j = starts[k + 1][0] if k + 1 < len(starts) else len(seg)
            block = [VERSE.sub("", seg[i].strip(), count=1)] + seg[i + 1:j]
            v_t, bh, tp = split_sections(clean_block(block))
            res[f"{c}/{n}"] = {"mula": v_t, "bh": bh, "tp": tp, "range": n2}
    return res


if __name__ == "__main__":
    r = parse()
    p = ROOT / "philosophical/bg_madhva.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    member = {}
    for k, e in r.items():
        c, n = map(int, k.split("/"))
        for m in range(n, e["range"] + 1):
            member[f"{c}/{m}"] = k
    byref = {u["ref"]: u for u in d["units"]}
    out, done, groups = [], set(), 0
    for u in d["units"]:
        g = member.get(u["ref"]) if u["kind"] == "mula+bhashya" else None
        if g is None:
            out.append(u)
            continue
        if g in done:
            continue
        done.add(g)
        c, n = map(int, g.split("/"))
        e = r[g]
        mem = [byref[f"{c}/{m}"] for m in range(n, e["range"] + 1) if f"{c}/{m}" in byref]
        j = lambda key: "\n".join(x[key] for x in mem if x.get(key)) or None
        mu, bh, tp = j("sanskrit_mula"), j("sanskrit_bhashya"), j("sanskrit_tatparya")
        ref = f"{c}/{n}" if e["range"] == n else f"{c}/{n}-{e['range']}"
        out.append({"ref": ref, "kind": "mula+bhashya", "sanskrit": "\n".join(x for x in (mu, bh, tp) if x) or None,
                    "sanskrit_mula": mu, "sanskrit_bhashya": bh, "sanskrit_tatparya": tp,
                    "english_mula": e["mula"], "english_bhashya": e["bh"], "english_tatparya": e["tp"],
                    "english": "\n".join(x for x in (e["mula"], e["bh"], e["tp"]) if x) or None})
        groups += 1
    d["units"] = out
    a_ = sum(1 for u in out if u.get("sanskrit_tatparya") and not u.get("english_tatparya"))
    b_ = sum(1 for u in out if u.get("english_tatparya") and not u.get("sanskrit_tatparya"))
    left = sum(1 for u in out if u["kind"] == "mula+bhashya" and not u.get("english"))
    d["source_english"] = {"citation": "Nagesh D. Sonde 2011, Sri Madhvacharya Bhagavada Gita Bhashya and Tatparya Nirnaya (Sanskrit text with English translation; free for copying per the author)", "url": "https://nageshsonde.com/", "license": "Author states: not protected by any copyright, free for copying and distribution"}
    d["needs_ocr"] = False
    d["alignment"] = "by_ref"
    d["notes"] = ("Sanskrit from Setutila: mula (gita_bhashya.json), Madhva's Gita Bhashya (gita_bhashya.json) and Gita Tatparya Nirnaya (gita_tatparya.json); Setutila puts each commentary block on the LAST verse of Madhva's verse group. "
                  "English from the Sonde PDF (born-digital Word PDF; its own Sanskrit is in a legacy font, garbled, not used), which translates verse groups (e.g. '5 - 6 - 7.') in one piece. "
                  f"So groups were merged into one unit each (ref like '3/5-7'; Sanskrit mula of all member verses concatenated, bhashya and tatparya as placed by Setutila) and paired with the group's English: {groups} groups built covering {sum(1 for _ in member)} verses; {left} other verse units have no English (verse number not found in the PDF). "
                  f"Tatparya coverage is uneven between sources: {b_} units have an English Tatparya translation but no Setutila Tatparya Sanskrit (Setutila's gita_tatparya.json looks incomplete), and {a_} have Tatparya Sanskrit but the PDF parse found no Tatparya English; in those units sanskrit and english cover different parts, so score only rows where both sides are present. "
                  "sanskrit = mula + bhashya + tatparya, english = verse + bhashya + tatparya translation, english_mula/english_bhashya/english_tatparya separate. Sanskrit-quote removal in the English is heuristic (legacy-font text detected by symbol density), so some garbled fragments may remain. The PDF contains the whole work twice; only the first copy is used. First pass.")
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(groups, left, len(out))
