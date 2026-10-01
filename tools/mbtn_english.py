import hashlib, json, math, re
from common import RAW

SRC = "mbtn_hariprasad/all.txt"
CH16 = "mbtn_hariprasad/mbtn-chapter16.txt"
DV = str.maketrans("०१२३४५६७८९", "0123456789")
MARK = re.compile(r"॥\s*[”’\"']?\s*([०-९]+)\s*/\s*([०-९]+)(?:\s*[-–]\s*([०-९]+))?\s*॥")
HEAD = re.compile(r"(?m)^\s*Chapter\s+(\d+)\s*:")
NUM = re.compile(r"^\s*(\d+(?:\s*(?:,|&|-|–|to|and|\s)\s*\d+)*)\s*[\.\)]?\s+([^\d\s].*)$")


def _verses(tok):
    nums = [int(x) for x in re.findall(r"\d+", tok)]
    if len(nums) == 2 and re.search(r"to|-|–", tok):
        return list(range(nums[0], nums[1] + 1))
    return nums


def _bullet_groups(txt):
    paras = []
    for ln in txt.split("\n"):
        if re.match(r"^\s*\uf0b7", ln):
            paras.append(re.sub(r"^\s*\uf0b7\s*", "", ln).strip())
        elif paras and ln.strip() and not ln.strip().startswith("||"):
            paras[-1] += " " + ln.strip()
    groups, exp = [], 1
    for p in paras:
        m = re.match(r"^(\d+(?:\s*(?:,|&|and)\s*\d+)*)\)\s*(.*)$", p)
        v = [int(x) for x in re.findall(r"\d+", m.group(1))] if m else [exp]
        groups.append({"v": v, "t": m.group(2) if m else p})
        exp = v[-1] + 1
    return groups


def english_groups():
    t = (RAW / SRC).read_text(encoding="utf-8")
    last = {}
    for m in HEAD.finditer(t):
        last[int(m.group(1))] = m.start()
    starts = sorted((p, n) for n, p in last.items())
    out = {}
    for i, (p, n) in enumerate(starts):
        e = starts[i + 1][0] if i + 1 < len(starts) else len(t)
        exp, groups, cur = 1, [], None
        for ln in t[p:e].split("\n"):
            m = NUM.match(ln)
            if m:
                v = _verses(m.group(1))
                if v and exp <= v[0] <= exp + 3:
                    cur = {"v": v, "t": m.group(2).strip()}
                    groups.append(cur)
                    exp = v[-1] + 1
                    continue
            if cur is not None and ln.strip() and not re.match(r"^\s*(Chapter \d+|\d+\s*$|\|\| End)", ln):
                cur["t"] += " " + ln.strip()
        out[n] = groups
    if (RAW / CH16).exists():
        out[16] = _bullet_groups((RAW / CH16).read_text(encoding="utf-8"))
    return out


_VOW = {"अ": "a", "आ": "a", "इ": "i", "ई": "i", "उ": "u", "ऊ": "u", "ऋ": "ri", "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au"}
_MAT = {"ा": "a", "ि": "i", "ी": "i", "ु": "u", "ू": "u", "ृ": "ri", "े": "e", "ै": "ai", "ो": "o", "ौ": "au"}
_CON = dict(zip("कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह",
                ["k", "k", "g", "g", "n", "c", "c", "j", "j", "n", "t", "t", "d", "d", "n", "t", "t", "d", "d", "n",
                 "p", "p", "w", "w", "m", "y", "r", "l", "w", "s", "s", "s", "h"]))


def _roman(txt):
    out, prev_con = [], False
    for ch in txt:
        if ch in _CON:
            if prev_con:
                out.append("a")
            out.append(_CON[ch])
            prev_con = True
        elif ch == "्":
            prev_con = False
        elif ch in _MAT:
            out.append(_MAT[ch])
            prev_con = False
        else:
            if prev_con:
                out.append("a")
            prev_con = False
            out.append(_VOW.get(ch, " "))
    if prev_con:
        out.append("a")
    return "".join(out)


def _key(w):
    w = w.lower().replace("sh", "s").replace("v", "w").replace("b", "w").replace("th", "t").replace("dh", "d")
    w = w.replace("ee", "i").replace("oo", "u").replace("aa", "a")
    return re.sub(r"(.)\1+", r"\1", w)[:5]


def _names_s(txt):
    return {_key(w) for w in _roman(txt).split() if len(w) >= 4}


def _names_e(txt):
    return {_key(w) for w in re.findall(r"\b[A-Z][a-z]{3,}\b", txt)}


def sanskrit_verses(unit):
    vs = []
    for a, b, c in MARK.findall(unit["sanskrit"] or ""):
        ch, v = int(a.translate(DV)), int(b.translate(DV))
        vs.extend((ch, x) for x in range(v, int(c.translate(DV)) + 1 if c else v + 1))
    return vs


def _chapter_verses(units):
    byc = {}
    for ui, u in enumerate(units):
        t, prev = u["sanskrit"] or "", 0
        for a in MARK.finditer(t):
            ch, v = int(a.group(1).translate(DV)), int(a.group(2).translate(DV))
            byc.setdefault(ch, []).append({"v": v, "u": ui, "t": t[prev:a.start()], "m": a.group(0)})
            prev = a.end()
    return byc


_STOP = set("the and that with from this have they their them which were will been also then thus such when what there into only about other these those could would should shall whom whose even very more most much many some all any each every both than over under after before again while where because through during without within upon among between having being does done make made".split())
MT = "mbtn_hariprasad/verse_en.json"
MT_W = 100.0


def _sha(t):
    return hashlib.sha1(t.strip().encode("utf-8")).hexdigest()


def _toks(t):
    return {w[:5] for w in re.findall(r"[a-z]{3,}", t.lower()) if w not in _STOP}


def _align(E, S, k, mt=None, prior=None):
    INF = float("inf")
    n, m = len(E), len(S)
    band = abs(n - m) + 25
    el = [len(e["t"]) for e in E]
    sl = [max(len(x["t"]), 1) for x in S]
    ne = [_names_e(e["t"]) for e in E]
    ns = [_names_s(x["t"]) for x in S]
    if mt:
        idf, te, tm = mt["idf"], [_toks(e["t"]) for e in E], [mt["tok"].get(_sha(x["t"]), set()) for x in S]
        wt = lambda a: sum(idf.get(z, 0.0) for z in a)
    cache = {}

    def cost(i0, i1, j0, j1):
        key = (i0, i1, j0, j1)
        if key in cache:
            return cache[key]
        le = sum(el[i0:i1]) or 1
        ls = sum(sl[j0:j1])
        c = 0.8 * abs(math.log(le / (k * ls))) - 1.2 * min(len(set().union(*ne[i0:i1]) & set().union(*ns[j0:j1])), 3)
        if mt:
            a, b = set().union(*te[i0:i1]), set().union(*tm[j0:j1])
            if a and b:
                c -= MT_W * wt(a & b) / math.sqrt(wt(a) * wt(b) or 1.0)
        if prior:
            c += prior(i0, j0)
        cache[key] = c
        return c

    dp = {(0, 0): 0.0}
    bp = {}
    for i in range(n + 1):
        for j in range(max(0, i - band), min(m, i + band) + 1):
            d = dp.get((i, j))
            if d is None:
                continue
            for di, dj, pen in ((1, 1, 0.0), (1, 2, 0.4), (1, 3, 1.0), (2, 1, 0.6), (1, 0, 2.5), (0, 1, 2.5)):
                a, b = i + di, j + dj
                if a > n or b > m or abs(a - b) > band:
                    continue
                c = d + pen + (cost(i, a, j, b) if di and dj else 0.0)
                if c < dp.get((a, b), INF):
                    dp[(a, b)] = c
                    bp[(a, b)] = (i, j)
    pairs, cur = [], (n, m)
    while cur != (0, 0):
        pv = bp[cur]
        pairs.append((pv, cur))
        cur = pv
    return pairs[::-1]


def _prior(E, S, pairs, weight=1.2):
    ne = [_names_e(e["t"]) for e in E]
    ns = [_names_s(x["t"]) for x in S]
    anchors = [(j0, S[j0]["v"] - E[i0]["v"][0]) for (i0, j0), (i1, j1) in pairs
               if i1 - i0 == 1 and j1 - j0 == 1 and ne[i0] & ns[j0]]
    if len(anchors) < 3:
        return None

    def local(j, rad=14):
        near = sorted(o for jj, o in anchors if abs(jj - j) <= rad)
        if len(near) < 2:
            near = sorted(o for _, o in sorted(anchors, key=lambda a: abs(a[0] - j))[:3])
        return near[len(near) // 2]

    est = [local(j) for j in range(len(S))]
    return lambda i, j: weight * min(abs(S[j]["v"] - E[i]["v"][0] - est[j]), 4)


def _mt_model(groups, byc=None):
    path = RAW / MT
    if not path.exists():
        return None
    tr = json.loads(path.read_text(encoding="utf-8"))
    tok = {h: _toks(t) for h, t in tr.items()}
    if byc:
        for S in byc.values():
            mts = [tr.get(_sha(x["t"])) for x in S]
            ns = [_names_s(x["t"]) for x in S]
            ne = [_names_e(t) if t else set() for t in mts]
            for j in range(1, len(S) - 1):
                if mts[j] and len(ns[j]) >= 2:
                    near = max(len(ns[j] & ne[j - 1]), len(ns[j] & ne[j + 1]))
                    if near >= 2 and near > len(ns[j] & ne[j]):
                        tok[_sha(S[j]["t"])] = set()
    docs = [_toks(e["t"]) for gs in groups.values() for e in gs] + list(tok.values())
    df = {}
    for d in docs:
        for z in d:
            df[z] = df.get(z, 0) + 1
    return {"tok": tok, "idf": {z: math.log(len(docs) / c) for z, c in df.items()}}


def _all_alignments(byc, groups):
    mt = _mt_model(groups, byc)
    out, cfg = {}, {}
    for ch, S in byc.items():
        E = groups.get(ch) or []
        if len(E) < 3:
            continue
        k = sum(len(e["t"]) for e in E) / sum(max(len(x["t"]), 1) for x in S)
        cfg[ch] = (E, S, k)
        first = _align(E, S, k, mt)
        out[ch] = _align(E, S, k, mt, _prior(E, S, first))
    return out, cfg


CHUNK = 8
SPLIT_OVER = 16


def _chunks(n):
    k = max(1, round(n / CHUNK))
    base, extra = divmod(n, k)
    out, a = [], 0
    for c in range(k):
        b = a + base + (c < extra)
        out.append((a, b))
        a = b
    return out


def _english(vs, eng, cover):
    own = [eng[(ch, j)] for ch, j, _ in vs if (ch, j) in eng]
    if own:
        return "\n\n".join(own)
    seen = []
    for ch, j, _ in vs:
        k = cover.get((ch, j))
        if k and eng.get(k) and eng[k] not in seen:
            seen.append(eng[k])
    return "\n\n".join(seen) or None


def attach_english(units):
    groups = english_groups()
    byc = _chapter_verses(units)
    eng = {}
    cover = {}
    stats = {"units": len(units), "verses": sum(len(S) for S in byc.values()), "matched": 0}
    allp, cfg = _all_alignments(byc, groups)
    for ch, pairs in allp.items():
        E, S, _ = cfg[ch]
        for (i0, j0), (i1, j1) in pairs:
            if i1 > i0 and j1 > j0:
                stats["matched"] += j1 - j0
                eng[(ch, j0)] = " ".join(e["t"] for e in E[i0:i1])
                cover.update({(ch, j): (ch, j0) for j in range(j0, j1)})
    pos = {}
    for ch, S in byc.items():
        for j, x in enumerate(S):
            pos.setdefault(x["u"], []).append((ch, j, x))
    out = []
    for ui, u in enumerate(units):
        vs = pos.get(ui, [])
        if len(vs) <= SPLIT_OVER:
            u["english"] = _english(vs, eng, cover)
            out.append(u)
            continue
        t = u["sanskrit"]
        tail = t[list(MARK.finditer(t))[-1].end():].strip()
        for a, b in _chunks(len(vs)):
            sub = vs[a:b]
            sk = "\n".join(x["t"].strip() + " " + x["m"] for _, _, x in sub)
            if b == len(vs) and tail:
                sk += "\n" + tail
            out.append({"ref": f"{u['ref']} / verses {sub[0][0]}.{sub[0][2]['v']}-{sub[-1][0]}.{sub[-1][2]['v']}", "kind": u["kind"],
                        "sanskrit_mula": None, "sanskrit_bhashya": sk, "sanskrit": sk,
                        "english": _english(sub, eng, cover)})
    stats["units_out"] = len(out)
    stats["with_english"] = sum(1 for x in out if x["english"])
    return out, stats
