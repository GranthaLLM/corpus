"""Give the Sanskrit-only Madhva bhashya units of aitareya_madhva.json an english from Pandurangi's 'Expl.' notes.

Pandurangi (1989) follows each passage translation with 'Expl.' notes: extracts of Madhva's bhashya in Devanagari
with his English rendering interleaved. Each Expl. block is assigned to the bhashya unit whose Sanskrit its Devanagari
lines match (rapidfuzz), and the block's English lines (pure Devanagari lines dropped) become that unit's english.

Run: uv run --with rapidfuzz python tools/aitareya_madhva_bhashya_english.py [--apply]
Needs the OCR text in GRANTHA_RAW/pand_clean.txt (the book's page OCR joined, byte tokens decoded).
"""
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

from rapidfuzz import fuzz

RAW = Path(os.environ.get("GRANTHA_RAW", "."))
REL = Path(__file__).resolve().parent.parent / "upanishads" / "aitareya_madhva.json"
DEVRE = re.compile(r"[ऀ-ॿ]")
LAT = re.compile(r"[A-Za-zāīūṛṣṇṭḍśṃṅñḥ]")
UP = re.compile(r"^(उप|उपं|उपः)\s*[-—–:]+")
NOISE = re.compile(r"Jangamwadi|eGangotri|^<<PAGE|AITAR|ATTAR|AITAR[ĒE]YOP|^\[?\s*(CH|ARAN|CM|CA|ca)\.?\s*[IVX\d]*\]?\s*\.?$|^\d{1,3}\.?$", re.I)


def norm(s):
    return "".join(c for c in s if "ऄ" <= c <= "ह" or c in "ािीुूृॄेैोौंः्ऽ")


def lines():
    out = []
    for l in (RAW / "pand_clean.txt").read_text(encoding="utf-8").split("\n"):
        s = l.strip()
        if not s or NOISE.search(s) or re.fullmatch(r"[\W\d]*", s):
            continue
        out.append(s)
    return out


def kind(s):
    d, a = len(DEVRE.findall(s)), len(LAT.findall(s))
    return "D" if d > a else "E"


def regions(L):
    regs, cur = [], None
    for s in L:
        if UP.match(s):
            if cur:
                regs.append(cur)
            cur = None
            continue
        if s.startswith("Expl."):
            if cur:
                regs.append(cur)
            cur = []
        if cur is not None:
            cur.append(s)
    if cur:
        regs.append(cur)
    return regs


def best_unit(dev_lines, units):
    votes = defaultdict(float)
    for l in dev_lines:
        n = norm(l)
        if len(n) < 25:
            continue
        sc = [(fuzz.partial_ratio(n, u["_n"]), u["ref"]) for u in units]
        top = max(sc)
        if top[0] >= 85:
            votes[top[1]] += len(n)
    return max(votes, key=votes.get) if votes else None


def english_of(block):
    en = []
    for s in block:
        if kind(s) == "D" and len(LAT.findall(s)) < 3:
            continue
        en.append(s)
    t = " ".join(en)
    t = re.sub(r"([a-z])- ([a-z])", r"\1\2", t)
    return re.sub(r"\s+", " ", t).strip()


def main():
    d = json.loads(REL.read_text(encoding="utf-8"))
    units = [u for u in d["units"] if u["ref"].endswith("-bhashya") or u["ref"] in ("mangalacharana", "intro-bhashya") or u["ref"].startswith("closing")]
    for u in units:
        u["_n"] = norm(u["sanskrit"])
    per = defaultdict(list)
    unmatched = 0
    for blk in regions(lines()):
        dev = [s for s in blk if kind(s) == "D"]
        ref = best_unit(dev, units)
        if ref is None:
            unmatched += 1
            continue
        per[ref].append(english_of(blk))
    print("regions unmatched", unmatched)
    byref = {u["ref"]: u for u in d["units"]}
    for u in units:
        if per[u["ref"]]:
            en = "\n".join(x for x in per[u["ref"]] if x)
            print(f"{u['ref']:20} sk={len(u['sanskrit']):6} en={len(en):6} ratio={len(en)/len(u['sanskrit']):.2f}")
            if "--apply" in sys.argv and not byref[u["ref"]].get("english"):
                byref[u["ref"]]["english"] = en
        else:
            print(f"{u['ref']:20} sk={len(u['sanskrit']):6} en=     0")
    if "--apply" in sys.argv:
        for u in d["units"]:
            u.pop("_n", None)
        REL.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


main()
