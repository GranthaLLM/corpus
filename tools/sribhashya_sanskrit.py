import re, math, difflib
from common import RAW

SRC = "sribhashya_bodhan/sb_full.txt"
DV = str.maketrans("०१२३४५६७८९", "0123456789")
D = "[०-९]+"
SEP = r"\s*(?:[-।|॥\.]|\s)\s*"
MARK = re.compile(rf"(?<![०-९])(?:[॥।]{{1,2}}\s*)?([१-४]){SEP}([१-४]){SEP}({D})\s*[॥।]{{1,2}}")
HEADER = re.compile(r"ग्रन्थमाला|^(प्रथम|द्वितीय|तृतीय|चतुर्थ)[ा]?ध्याये|^<<PAGE|^\$\$.*\$\$$|Please do not")
PAGENO = re.compile(r"^[०-९\s\.]{1,5}$")
CUT = re.compile(r"(?:इत्या?ह|त्राह|आह|\u2014|।|ॐ)\s*")


def _norm(s):
    return re.sub(r"[^ऀ-ॿ]", "", re.sub(r"[०-९।॥]", "", s))


def _markers(t):
    ms = []
    for m in MARK.finditer(t):
        raw = tuple(int(x.translate(DV)) for x in m.groups())
        if ms:
            prev = ms[-1]
            a = _norm(t[max(0, prev["start"] - 40):prev["start"]])[-18:]
            b = _norm(t[max(0, m.start() - 40):m.start()])[-18:]
            r = difflib.SequenceMatcher(None, a, b).ratio()
            if a and prev["raw"][:2] == raw[:2] and m.start() - prev["end"] < 400 and (
                    (prev["raw"][2] == raw[2] and r > 0.4) or (abs(prev["raw"][2] - raw[2]) <= 1 and r > 0.75)):
                continue
        ms.append({"start": m.start(), "end": m.end(), "raw": raw})
    return ms


def _smooth_padas(ms):
    pid = lambda r: (r[0] - 1) * 4 + (r[1] - 1)
    prev = 0
    for i, m in enumerate(ms):
        p = pid(m["raw"])
        nxt = pid(ms[i + 1]["raw"]) if i + 1 < len(ms) else p
        if p == prev or (p == prev + 1 and nxt >= p):
            prev = p
        m["pada"] = prev


def _stmt_start(t, m):
    ls = t.rfind("\n", 0, m["start"]) + 1
    line = t[ls:m["start"]]
    if len(_norm(line)) < 6 and not re.match(rf"\s*{D}\s*[\.।]", line):
        pe = len(t[:ls].rstrip())
        ls = t.rfind("\n", 0, pe) + 1
        line = t[ls:m["start"]]
    if re.match(rf"\s*{D}\s*[\.।]", line):
        return ls
    cuts = [c.end() for c in CUT.finditer(line)]
    while cuts and len(_norm(line[cuts[-1]:])) < 6:
        cuts.pop()
    return ls + (cuts[-1] if cuts else 0)


def _clean(seg):
    paras, cur = [], []
    for ln in seg.split("\n"):
        s = ln.strip()
        if not s:
            if cur:
                paras.append(cur)
                cur = []
            continue
        if HEADER.search(s) or PAGENO.match(s):
            continue
        cur.append(s)
    if cur:
        paras.append(cur)
    out = []
    for p in paras:
        txt = ""
        for s in p:
            if txt.endswith("-") and not txt.endswith(" -"):
                txt = txt[:-1] + s
            else:
                txt = (txt + " " + s).strip()
        out.append(txt)
    txt = "\n\n".join(out)
    txt = re.sub(r"[ঀ-෿$]", "", txt)
    return re.sub(r"[•❋]", "*", txt).strip()


def _segments():
    t = (RAW / SRC).read_text(encoding="utf-8")
    ms = _markers(t)
    _smooth_padas(ms)
    for m in ms:
        m["s"] = _stmt_start(t, m)
    byp = {}
    for i, m in enumerate(ms):
        e = ms[i + 1]["s"] if i + 1 < len(ms) else len(t)
        byp.setdefault(m["pada"], []).append(_clean(t[m["s"]:e]))
    return byp


def _cost(a, b, k=0.54):
    return abs(math.log(max(a, 1) / (k * max(b, 1))))


def _align(el, sl, can_merge, p_merge=0.7, p_split=1.0):
    n, m = len(el), len(sl)
    INF = float("inf")
    dp = [[INF] * (m + 1) for _ in range(n + 1)]
    bp = {}
    dp[0][0] = 0.0
    for i in range(n + 1):
        for j in range(m + 1):
            d = dp[i][j]
            if d == INF:
                continue
            for di, dj, c, op in (
                (1, 1, lambda: _cost(sl[j], el[i]), "1-1") if i < n and j < m else (0, 0, None, None),
                (1, 2, lambda: _cost(sl[j] + sl[j + 1], el[i]) + p_merge, "merge") if i < n and j + 1 < m and can_merge[i] else (0, 0, None, None),
                (2, 1, lambda: _cost(sl[j], el[i] + el[i + 1]) + p_split, "split") if i + 1 < n and j < m else (0, 0, None, None),
            ):
                if op is None:
                    continue
                v = d + c()
                if v < dp[i + di][j + dj]:
                    dp[i + di][j + dj] = v
                    bp[(i + di, j + dj)] = (i, j, op)
    ops, i, j = [], n, m
    while (i, j) != (0, 0):
        pi, pj, op = bp[(i, j)]
        ops.append((pi, pj, op))
        i, j = pi, pj
    return ops[::-1]


def attach_sanskrit(units):
    segs = _segments()
    byp = {}
    for u in units:
        a, b, _ = u["ref"].split(".")
        byp.setdefault((int(a) - 1) * 4 + int(b) - 1, []).append(u)
    stats = {"1-1": 0, "merge": 0, "split": 0}
    for pada, us in byp.items():
        sl = segs.get(pada, [])
        el = [len(u["english"] or "") for u in us]
        cs = [int(u["ref"].split(".")[2]) for u in us]
        can_merge = [k + 1 < len(cs) and cs[k + 1] > cs[k] + 1 for k in range(len(cs))]
        for i, j, op in _align(el, [len(x) for x in sl], can_merge):
            stats[op] += 1
            if op == "1-1":
                us[i]["sanskrit"] = sl[j]
            elif op == "merge":
                us[i]["sanskrit"] = sl[j] + "\n\n" + sl[j + 1]
    return stats
