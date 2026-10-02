import bisect, collections, json, re, subprocess
from common import *

JHA_REV = "42353ef"
JHA_PATH = "upanishads/chandogya_shankara_jha.json"
K = 14


def norm(t):
    return re.sub(r"[^क-हा-ौअ-औ]", "", t or "")


def concat(texts):
    buf, off, n = [], [], 0
    for t in texts:
        x = norm(t)
        off.append(n)
        buf.append(x)
        n += len(x)
    return "".join(buf), off


def anchors(S, J):
    def shingles(T):
        d = collections.defaultdict(list)
        for i in range(len(T) - K + 1):
            d[T[i:i + K]].append(i)
        return d
    ds, dj = shingles(S), shingles(J)
    pairs = sorted((v[0], dj[k][0]) for k, v in ds.items() if len(v) == 1 and len(dj.get(k, [])) == 1)
    tails, idx, prev = [], [], [-1] * len(pairs)
    for i, (_, b) in enumerate(pairs):
        p = bisect.bisect_left(tails, b)
        if p == len(tails):
            tails.append(b)
            idx.append(i)
        else:
            tails[p] = b
            idx[p] = i
        prev[i] = idx[p - 1] if p else -1
    k, out = idx[-1], []
    while k >= 0:
        out.append(pairs[k])
        k = prev[k]
    return out[::-1]


def main():
    d = json.load(open(ROOT / "upanishads/chandogya_shankara.json"))
    s = d["units"]
    j = json.loads(subprocess.check_output(["git", "show", f"{JHA_REV}:{JHA_PATH}"], cwd=ROOT))["units"]
    S, so = concat([u["sanskrit"] for u in s])
    J, jo = concat([u["sanskrit"] for u in j])
    lis = anchors(S, J)
    Sp, Jp = [a for a, _ in lis], [b for _, b in lis]

    def j2s(x):
        i = bisect.bisect_right(Jp, x) - 1
        return 0 if i < 0 else Sp[i] + (x - Jp[i])

    rows = collections.defaultdict(list)
    for r, u in enumerate(j):
        mid = jo[r] + len(norm(u["sanskrit"])) // 2
        rows[bisect.bisect_right(so, j2s(mid)) - 1].append(r)

    for i, u in enumerate(s):
        ref = u["ref"]
        if ref.startswith("colophon") and i and rows.get(i):
            rows[i - 1] += rows.pop(i)
        elif ref.startswith("intro") and rows.get(i) and len(u["sanskrit"]) < 200 \
                and sum(len(j[r]["english"] or "") for r in rows[i]) > 3 * len(u["sanskrit"]) and i + 1 < len(s):
            rows[i + 1] = rows.pop(i) + rows.get(i + 1, [])

    n = 0
    for i, u in enumerate(s):
        rs = sorted(rows.get(i, []))
        en = " ".join((j[r]["english"] or "").strip() for r in rs).strip()
        u["english"] = en or None
        if en:
            n += 1
            u.setdefault("meta", {})["jha_rows"] = [rs[0] + 1, rs[-1] + 1]
    d["alignment"] = "by_ref"
    d["source_english"] = {"citation": "Jha, Chandogyopanishad (Mitrasamgraha GV05chupsau)", "url": MITRA + "GV05chupsau.tsv", "license": MITRA_LIC}
    d["notes"] = ("Sanskrit (verse + bhashya) from Advaita Sharada. English: Jha translation (Mitrasamgraha GV05chupsau, CC BY-SA), "
                  "whose sentence rows were joined to these units by matching their Sanskrit (14-char shingle anchors, longest increasing subsequence, "
                  "row assigned to the unit holding its midpoint). meta.jha_rows gives the 1-based source row range. "
                  "Colophon units and the verses of 3.9.2-3.10.4 have no English because Jha omits them; intro-1.1 is only partly translated. "
                  "The former chandogya_shankara_jha.json (raw row-per-unit file) was merged in here and removed; it is in git history.")
    write("upanishads/chandogya_shankara.json", d)
    print(n, "of", len(s), "units with english")


if __name__ == "__main__":
    main()
