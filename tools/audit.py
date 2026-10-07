"""Corpus audit: flags suspicious units without changing anything. Run: python3 tools/audit.py [--examples N]"""
import glob
import json
import re
import statistics as st
import sys
from collections import defaultdict

DEV = re.compile(r"[ऀ-ॿ]")
DIAC = re.compile(r"[āīūṛṝḷṃḥṅñṭḍṇśṣĀĪŪṚŚṢ]")
WORD = re.compile(r"\b(the|is|of|and|that|to|in|he|his|who|which|with)\b", re.I)
JUNK = re.compile(r"Footnotes and references|back to top|NOTE:|Tranlsation|^verse \d|Next >|< Previous|wisdomlib|Click here|\[\d+\]:|Article published|Last Updated", re.I | re.M)
EX = int(sys.argv[sys.argv.index("--examples") + 1]) if "--examples" in sys.argv else 3


def files():
    for f in sorted(glob.glob("*/*.json")):
        if f.split("/")[0] in ("philosophical", "upanishads", "sahitya"):
            yield f, json.load(open(f, encoding="utf-8"))


def ratio(sk, en):
    return len(en) / max(1, len(sk))


def lines_iast(en):
    out = []
    for l in en.split("\n"):
        l = l.strip()
        if len(l) > 25 and len(DIAC.findall(l)) / len(l) > 0.04 and len(WORD.findall(l)) < 2:
            out.append(l[:80])
    return out


res = defaultdict(lambda: defaultdict(list))
for f, d in files():
    n = f.split("/")[-1][:-5]
    us = d["units"]
    both = [u for u in us if u.get("sanskrit") and u.get("english")]
    if len(both) >= 15:
        med = st.median(ratio(u["sanskrit"], u["english"]) for u in both)
        for u in both:
            r = ratio(u["sanskrit"], u["english"]) / med
            if len(u["sanskrit"]) > 40 and (r > 3.5 or r < 1 / 3.5):
                res["ratio outlier (pair)"][n].append((u["ref"], round(r, 1)))
        for u in us:
            for p in u.get("parts") or []:
                if p.get("sanskrit") and p.get("english") and len(p["sanskrit"]) > 40:
                    r = ratio(p["sanskrit"], p["english"]) / med
                    if r > 4.5 or r < 1 / 4.5:
                        res["ratio outlier (part)"][n].append((u["ref"] + ":" + p["role"], round(r, 1)))
    for u in us:
        for k in ("english",):
            e = u.get(k) or ""
            if JUNK.search(e):
                res["junk string in english"][n].append((u["ref"], JUNK.search(e).group(0)))
            if DEV.search(e):
                res["devanagari in english"][n].append((u["ref"], ""))
            li = lines_iast(e)
            if li:
                res["transliteration line in english"][n].append((u["ref"], li[0]))
        ps = u.get("parts") or []
        if ps:
            bo = [p for p in ps if p.get("sanskrit") and p.get("english")]
            sc = u["scope"]
            if sc == "mula+commentary":
                if u.get("sanskrit") != "\n".join(p["sanskrit"] for p in bo) or u.get("english") != "\n".join(p["english"] for p in bo):
                    res["pair != join(parts with both)"][n].append((u["ref"], ""))
            elif sc == "mula":
                m = next((p for p in ps if p["role"] == "mula"), None)
                if m and (u.get("sanskrit") != m.get("sanskrit") or u.get("english") != m.get("english")):
                    res["scope mula but pair != mula part"][n].append((u["ref"], ""))
    seen = defaultdict(list)
    for u in us:
        if u.get("english") and len(u["english"]) > 60:
            seen[u["english"]].append(u["ref"])
    for e, rs in seen.items():
        if len(rs) > 1:
            res["identical english in several units"][n].append((",".join(rs[:3]), e[:40]))

order = ["ratio outlier (pair)", "ratio outlier (part)", "junk string in english", "devanagari in english", "transliteration line in english", "pair != join(parts with both)", "scope mula but pair != mula part", "identical english in several units"]
for chk in order:
    tot = sum(len(v) for v in res[chk].values())
    print(f"\n== {chk}: {tot} units in {len(res[chk])} files")
    for n, v in sorted(res[chk].items(), key=lambda kv: -len(kv[1])):
        print(f"   {n:26} {len(v):4}  {v[:EX]}")
