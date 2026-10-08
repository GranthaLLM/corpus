"""Rebuild bg_shankara english from Warrier's parallel edition (Ramakrishna Math): Sanskrit paragraph, then its English.

Each Devanagari paragraph group in the OCR is matched (rapidfuzz) to the unit whose Sanskrit holds it, and the English
that follows becomes that unit's: the verse's own translation is mula, the rest (intro and commentary, in print order)
is bhashya. Units whose matched Sanskrit covers 0.8 to 1.2 of their own keep the new english, the rest are left alone.

Run: uv run --with rapidfuzz python tools/bg_shankara_warrier.py [--apply]
Needs GRANTHA_RAW/warrier_gita.txt (archive.org djvu text of the Warrier edition).
"""
import json
import os
import re
import sys
from pathlib import Path

from rapidfuzz import fuzz

RAW = Path(os.environ.get("GRANTHA_RAW", "."))
REL = Path(__file__).resolve().parent.parent / "philosophical" / "bg_shankara.json"
DEV = re.compile(r"[ऀ-ॿ]")
LAT = re.compile(r"[A-Za-z]")
HEAD_LINE = re.compile(r"^[\-\dIl\]\.\+\[ ]{0,14}\]?\s*[A-Z][A-Za-z’'\- ]{2,42}\s+\d{1,3}\s*[॥|]*\s*$|Bhagavad Gita Bhasyam|\[Ch\. [IVX]+|^\s*\d{1,3}\s*$|CC-0")
LABEL = re.compile(r"^\s*(?:[Il1!]?[\dOo]{1,2}[\.\,]{0,3}\s*[\d\]]?[\.\,\]]{0,3}\s*)")


def kind(b):
    return "D" if len(DEV.findall(b)) > len(LAT.findall(b)) else "E"


def clean_block(b):
    ls = [l for l in b.split("\n") if l.strip() and not HEAD_LINE.search(l.strip())]
    return " ".join(" ".join(ls).split())


INLINE_HEAD = re.compile(r"[-\dIl]{1,6}\s*[\]|]\s*(?:The\s+)?[A-Z][A-Za-z’'\- ]{2,40}?\s*\d{1,3}\s*\]?")


def tidy_english(t):
    t = re.sub(r"\S*[ऀ-ॿ]\S*", " ", t)
    t = INLINE_HEAD.sub(" ", t)
    t = re.sub(r"(\w)- (?=[a-z])", r"\1", t)
    return re.sub(r"\s+", " ", t).strip()


def pairs_from_raw():
    raw = (RAW / "warrier_gita.txt").read_text(encoding="utf-8", errors="ignore")
    blocks = [b for b in re.split(r"\n\s*\n+", raw) if b.strip()]
    seq = []
    for b in blocks:
        k = kind(b)
        c = clean_block(b)
        if len(c) < 14 and not DEV.search(c):
            continue
        if c:
            seq.append((k, c))
    groups = []
    for k, c in seq:
        if groups and groups[-1][0] == k:
            groups[-1][1].append(c)
        else:
            groups.append([k, [c]])
    pairs, i = [], 0
    while i < len(groups):
        if groups[i][0] == "D":
            dt, et = " ".join(groups[i][1]), []
            if i + 1 < len(groups) and groups[i + 1][0] == "E":
                et = [LABEL.sub("", e, count=1) for e in groups[i + 1][1]]
                i += 1
            pairs.append((dt, " ".join(et)))
        i += 1
    return pairs


def norm(s):
    return "".join(c for c in s if "ऄ" <= c <= "ह" or c in "ािीुूृॄेैोौंःऽ्")


def main():
    d = json.loads(REL.read_text(encoding="utf-8"))
    us = d["units"]
    cand = [i for i, u in enumerate(us) if re.fullmatch(r"\d+\.\d+", u["ref"])]
    unorm = {i: norm(us[i]["sanskrit"]) for i in cand}
    vnorm = {}
    for i in cand:
        L = us[i]["sanskrit"].split("\n")
        k = next((j for j, l in enumerate(L) if re.search(r"॥\s*[\d०-९]+\s*॥\s*$", l)), None)
        vnorm[i] = norm("\n".join(L[: k + 1])) if k is not None else ""
    ptr, got, cov = 0, {}, {}
    for n, (dt, et) in enumerate(pairs_from_raw()):
        dn = norm(dt)
        if len(dn) < 12:
            continue
        best = None
        for ci in range(max(0, ptr - 1), min(len(cand), ptr + 4)):
            u = cand[ci]
            sc = fuzz.partial_ratio(dn, unorm[u]) if len(dn) < len(unorm[u]) else fuzz.ratio(dn, unorm[u])
            if best is None or sc > best[0]:
                best = (sc, ci, u)
        if best is None or best[0] < 72:
            continue
        _, ci, u = best
        ptr = ci
        vs = fuzz.partial_ratio(dn, vnorm[u]) if vnorm[u] else 0
        role = "mula" if vs >= 78 and len(dn) <= len(vnorm[u]) * 1.15 else "bhashya"
        got.setdefault(u, []).append((role, tidy_english(et)))
        cov[u] = cov.get(u, 0) + len(dn)
    n_ok = 0
    for u, items in got.items():
        m = " ".join(t for r, t in items if r == "mula").strip()
        b = " ".join(t for r, t in items if r == "bhashya").strip()
        c = cov[u] / max(1, len(unorm[u]))
        unit = us[u]
        mp = next((x for x in unit.get("parts") or [] if x["role"] == "mula"), None)
        bp = next((x for x in unit.get("parts") or [] if x["role"] == "bhashya"), None)
        if not (m and b and mp and bp and 0.8 <= c <= 1.2):
            continue
        mp["english"], bp["english"] = m, b
        both = [q for q in unit["parts"] if q.get("sanskrit") and q.get("english")]
        unit["sanskrit"] = "\n".join(q["sanskrit"] for q in both)
        unit["english"] = "\n".join(q["english"] for q in both)
        n_ok += 1
    print(f"matched units {len(got)}, rebuilt {n_ok} of {len(cand)}")
    if "--apply" in sys.argv:
        REL.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


main()
