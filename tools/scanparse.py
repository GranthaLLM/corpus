import re, collections, json
from common import RAW

IA = RAW / "ia"
HDRS = [re.compile(r"^\s*\d+\s*[~\-–]+\s*\d+\]\s+[A-Z ]+\s+\d+\s*$"), re.compile(r"^\s*[A-Z][A-Z .,'-]{4,}\s+\d+\s*$"), re.compile(r"^\s*\d+\s+[A-Z][A-Z .,'-]{4,}\s*$"),
        re.compile(r"^\s*\[?\d+[~\-–]*\d*\]\s+[A-Z ]+\s*$")]


def paragraphs(path):
    t = (IA / path).read_text(encoding="utf-8", errors="replace")
    t = t.replace("\x0c", "\n\n")
    out = []
    for blk in re.split(r"\n\s*\n", t):
        ls = [re.sub(r"\s+", " ", l).strip() for l in blk.split("\n")]
        ls = [l for l in ls if l and not any(h.match(l) for h in HDRS)]
        if not ls:
            continue
        s = ""
        for l in ls:
            if s.endswith("-") and l[:1].islower():
                s = s[:-1] + l
            else:
                s = (s + " " + l).strip()
        out.append(s)
    return out


def english_filter(paras, min_frac=0.6):
    cnt = collections.Counter(w for p in paras for w in re.findall(r"[a-z]{2,}", p.lower()))
    common = {w for w, c in cnt.items() if c >= 8}
    keep = []
    for p in paras:
        toks = re.findall(r"[A-Za-z]+", p)
        if not toks:
            continue
        frac = sum(1 for w in toks if w.lower() in common) / len(toks)
        keep.append((p, frac))
    return [(p, f >= min_frac or bool(re.match(r"^\d+\.\s", p))) for p, f in keep]


def seq_parse(ann, counts, start_chapter=1, pat=r"^(\d+)\s*[\.\)]\s+(?=\S)", window=8, need_prev_garbage=False, tail=12, cwin=6):
    """ann: [(para, is_english)]. Verse N starts at a paragraph matching a number close to the expected next verse,
    optionally only when the previous paragraph was non-English (the Sanskrit verse line)."""
    units, cur = {}, None
    ch, v = start_chapter, 0
    rx = re.compile(pat)
    prev_eng = False
    for p, eng in ann:
        if not eng:
            prev_eng = False
            continue
        m = rx.match(p)
        ok_prev = (not need_prev_garbage) or (not prev_eng)
        prev_eng = True
        if m and ok_prev:
            n = int(m.group(1))
            cands = []
            if ch <= len(counts):
                if v < counts[ch - 1] and v < n <= min(v + window, counts[ch - 1]):
                    cands.append((ch, n))
                if v >= counts[ch - 1] - tail and ch < len(counts) and 1 <= n <= cwin:
                    cands.append((ch + 1, n))
                if v == 0 and ch == start_chapter and 1 <= n <= cwin:
                    cands.append((ch, n))
            if cands:
                ch, v = cands[0]
                cur = {"mula": p[m.end():], "b": []}
                units[f"{ch}.{v}"] = cur
                continue
        if cur is not None:
            cur["b"].append(p)
    return {k: (u["mula"], "\n".join(u["b"]) or None) for k, u in units.items()}


def multi_parse(ann, counts, **kw):
    """Run seq_parse; if later chapters were never reached, restart at the next chapter after the last accepted verse."""
    res = {}
    start, idx = 1, 0
    for _ in range(len(counts) + 1):
        sub = ann[idx:]
        r = seq_parse(sub, counts, start_chapter=start, **kw)
        if not r:
            break
        for k, vv in r.items():
            res.setdefault(k, vv)
        chs = [int(k.split(".")[0]) for k in r]
        last = max(chs)
        if last >= len(counts):
            break
        # find paragraph index of the last accepted verse's start
        lastkey = max(r, key=lambda k: (int(k.split(".")[0]), int(k.split(".")[1])))
        pos = next((i for i, (p, e) in enumerate(sub) if e and r[lastkey][0] and p.endswith(r[lastkey][0][-20:])), None) if False else None
        # restart just past the chapter the parse stalled in
        pos = next((i for i, (p, e) in enumerate(sub) if e and p[:80] in (lastkey,) or (r[lastkey][0] and r[lastkey][0][:40] in p)), 0)
        idx += pos + 1
        start = last + 1
    return res
