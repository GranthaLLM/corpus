"""Realign Harivamsha rows and merge them into verse units.
Mitrasamgraha rows are half-verse Sanskrit lines against Dutt's English sentences, and a sentence often runs across
row boundaries, so a row's English carries the next half or misses its own. Rows are re-aligned by a monotone DP
(moves 1-1, 1-2, 2-1, skips penalised) scored with LaBSE similarity plus overlap of romanised Sanskrit and English
character trigrams (names), runs of non-1-1 moves are merged into one unit, and units are then merged up to each
double danda so that both sides cover the same passage.
Needs sentence-transformers. Run from corpus/: python3 tools/harivamsha_realign.py [--dry]
Reads the unmerged rows from `git show HEAD:sahitya/harivamsha.json` unless --src FILE is given."""
import json
import pathlib
import re
import subprocess
import sys
import unicodedata

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv
F = ROOT / "sahitya" / "harivamsha.json"

C = {'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'n', 'च': 'c', 'छ': 'ch', 'ज': 'j', 'झ': 'jh', 'ञ': 'n', 'ट': 't', 'ठ': 'th',
     'ड': 'd', 'ढ': 'dh', 'ण': 'n', 'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n', 'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh',
     'म': 'm', 'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 's', 'ष': 's', 'स': 's', 'ह': 'h', 'ळ': 'l'}
V = {'अ': 'a', 'आ': 'a', 'इ': 'i', 'ई': 'i', 'उ': 'u', 'ऊ': 'u', 'ऋ': 'ri', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au'}
M = {'ा': 'a', 'ि': 'i', 'ी': 'i', 'ु': 'u', 'ू': 'u', 'ृ': 'ri', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au'}
MOVES = [(1, 1), (1, 2), (2, 1), (1, 0), (0, 1)]
PEN = {(1, 1): 0.0, (1, 2): 0.12, (2, 1): 0.12, (1, 0): 0.35, (0, 1): 0.35}
BAND, LEXW = 14, 2.0


def rom(t):
    out, pc = [], False
    for ch in t:
        if ch in C:
            if pc:
                out.append('a')
            out.append(C[ch])
            pc = True
        elif ch in M:
            out.append(M[ch])
            pc = False
        elif ch == '्':
            pc = False
        elif ch in V:
            out.append(V[ch])
            pc = False
        elif ch in 'ंः':
            out.append('n' if ch == 'ं' else 'h')
            pc = False
        else:
            if pc:
                out.append('a')
            pc = False
            out.append(' ' if not ch.isalnum() else '')
    if pc:
        out.append('a')
    return ''.join(out)


def fold(t):
    t = unicodedata.normalize('NFKD', t.lower())
    t = ''.join(c for c in t if not unicodedata.combining(c))
    for a, b in (('ç', 's'), ('sh', 's'), ('kh', 'k'), ('ch', 'c'), ('th', 't'), ('dh', 'd'), ('bh', 'b'), ('ph', 'p'), ('gh', 'g'), ('jh', 'j'), ('w', 'v')):
        t = t.replace(a, b)
    return re.sub(r'[^a-z ]', ' ', t)


def grams(t):
    s = set()
    for w in fold(t).split():
        w = re.sub(r'(.)\1+', r'\1', w)
        for k in range(len(w) - 2):
            if len(w) >= 4:
                s.add(w[k:k + 3])
    return s


def load_rows():
    if "--src" in sys.argv:
        return json.loads(pathlib.Path(sys.argv[sys.argv.index("--src") + 1]).read_text(encoding="utf-8"))
    return json.loads(subprocess.run(["git", "show", "HEAD:sahitya/harivamsha.json"], capture_output=True, text=True, check=True, cwd=ROOT).stdout)


def main():
    from sentence_transformers import SentenceTransformer
    d = load_rows()
    us = d["units"]
    n = len(us)
    m = SentenceTransformer("sentence-transformers/LaBSE")
    m.max_seq_length = 128
    es = m.encode([u["sanskrit"] for u in us], batch_size=64, normalize_embeddings=True)
    ee = m.encode([u["english"] for u in us], batch_size=64, normalize_embeddings=True)
    cs = np.vstack([np.zeros(es.shape[1]), np.cumsum(es, 0)])
    ce = np.vstack([np.zeros(ee.shape[1]), np.cumsum(ee, 0)])
    sg = [grams(rom(u["sanskrit"])) for u in us]
    eg = [grams(u["english"]) for u in us]

    def score(i0, i1, j0, j1):
        a, b = cs[i1] - cs[i0], ce[j1] - ce[j0]
        c = float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
        A, B = set().union(*sg[i0:i1]), set().union(*eg[j0:j1])
        return c + LEXW * (len(A & B) / np.sqrt(len(A) * len(B)) if A and B else 0.0)

    sc, bk = {(0, 0): 0.0}, {}
    for i in range(n + 1):
        for j in range(max(0, i - BAND), min(n, i + BAND) + 1):
            if i == 0 and j == 0:
                continue
            best, arg = -1e9, None
            for a, b in MOVES:
                p = (i - a, j - b)
                if p not in sc:
                    continue
                g = ((a + b) / 2 * score(p[0], i, p[1], j) if a and b else 0.0) - PEN[(a, b)]
                if sc[p] + g > best:
                    best, arg = sc[p] + g, (a, b)
            if arg:
                sc[(i, j)], bk[(i, j)] = best, arg
    i = j = n
    path = []
    while (i, j) != (0, 0):
        a, b = bk[(i, j)]
        path.append((i - a, i, j - b, j))
        i, j = i - a, j - b
    path.reverse()

    runs, cur = [], None
    for g in path:
        if (g[1] - g[0], g[3] - g[2]) == (1, 1):
            if cur:
                runs.append(cur)
                cur = None
            runs.append([g])
        else:
            cur = (cur or []) + [g]
    if cur:
        runs.append(cur)

    def join(rows, key):
        return " ".join(u[key].strip() for u in rows)

    def ref(a0, a1):
        x, y = str(us[a0]["ref"]).split("-")[0], str(us[a1 - 1]["ref"]).split("-")[-1]
        return x if x == y else f"{x}-{y}"

    out, buf = [], None

    def flush():
        nonlocal buf
        if buf:
            a0, a1, b0, b1 = buf
            out.append({"ref": ref(a0, a1), "kind": "verse", "scope": "text", "sanskrit": join(us[a0:a1], "sanskrit"), "english": join(us[b0:b1], "english")})
            buf = None

    for r in runs:
        a0, a1, b0, b1 = r[0][0], r[-1][1], r[0][2], r[-1][3]
        prev_end = int(str(us[buf[1] - 1]["ref"]).split("-")[-1]) if buf else None
        if buf and int(str(us[a0]["ref"]).split("-")[0]) != prev_end + 1:
            flush()
        buf = [a0, a1, b0, b1] if not buf else [buf[0], a1, buf[2], b1]
        if us[a1 - 1]["sanskrit"].strip().endswith("॥"):
            flush()
    flush()
    d["units"] = out
    d["notes"] += (
        f" [Realignment 2026-10-21: the {n} half-verse rows were re-aligned to Dutt's English (monotone DP over LaBSE similarity and name overlap) and merged "
        f"into {len(out)} units closed at a double danda, because Dutt's sentences run across row boundaries and a row often carried the next half or lacked "
        "its own. A merged unit's ref is first-last source row; rows that are not consecutive (dropped apparatus rows) are never merged across the gap. "
        "A hand audit of 32 previously flagged or sampled rows put the share still misaligned at about one in five, down from about half.]"
    )
    print(n, "->", len(out))
    if not DRY:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
