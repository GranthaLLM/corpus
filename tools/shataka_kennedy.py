import html, json, re
from common import ROOT, RAW, write

SRC = RAW / "kennedy_satakas_djvu.txt"
MAP = {"2.1": 1, "2.2": 2, "2.3": 3, "2.4": 4, "2.5": 5, "2.6": 6, "2.7": 7, "2.8": 8, "2.9": 9, "2.10": 10, "2.11": 11, "2.12": 12, "2.13": 13, "2.14": 14, "2.15": 15, "2.16": 20, "2.18": 17, "2.22": 23, "2.23": 24, "2.24": 25, "2.25": 26, "2.27": 28, "2.28": 69, "2.29": 70, "2.31": 66, "2.32": 67, "2.33": 68, "2.35*1": 29, "2.37": 19, "2.38": 31, "2.42": 73, "2.43": 74, "2.44": 75, "2.45": 76, "2.46": 77, "2.47": 78, "2.47*1": 21, "2.48": 79, "2.49": 80, "2.50": 81, "2.51": 82, "2.52": 83, "2.53": 84, "2.54": 85, "2.55": 86, "2.56": 87, "2.57": 88, "2.58": 89, "2.59": 90, "2.60": 91, "2.61": 92, "2.62": 93, "2.63": 94, "2.69": 98, "2.72": 57, "2.73": 58, "2.74": 59, "2.75": 60, "2.76": 61, "2.77": 62, "2.79": 64, "2.80": 65, "2.82": 34, "2.87": 38, "2.88": 39, "2.89": 40, "2.90": 41, "2.91": 42, "2.92": 43, "2.93": 44, "2.94": 45, "2.95": 46, "2.96": 47, "2.97": 48, "2.102": 99}
HDR = re.compile(r"\b[\dIiloO]{0,4}\s*THE\s+[vV]?SRINGA\s+SATAKA\s*[\dIil]*|\b[\dIiloO]{0,4}\s*THE\s+SATAKAS\s*[\dIil]*")
CAND = re.compile(r'(?<=[.?!:;"\'»\)\^\s])\s+(\S{1,5}\s?\.)\s+(?=[A-Z"\'])')
OCR = [(r"\s*\[C[/f]\..*?\]", ""), (r"3r", "y"), (r"(\w)- ([a-z])", r"\1\2"), (r"3\^", "y"), (r"\^", ""), (r"\}", "y"), (r"\bvS", "S"), (r"\s+([.,;:?!])", r"\1")]


def garbled(t):
    return bool(re.search(r"[\d\^\]\[\"'\-]", t)) or bool(re.fullmatch(r"[A-Za-z]{1,2}\.?", t.replace(" ", "").rstrip(".")))


def verses():
    t = SRC.read_text(encoding="utf-8")
    body = html.unescape(t[t.index("<pre>") + 5:t.index("</pre>")]) if "<pre>" in t else t
    L = body.split("\n")
    a = next(i for i, l in enumerate(L) if re.match(r"^THE\s+SRINGA\s+SATAKA\s*$", l.strip()))
    blocks, cur = [], []
    for l in L[a + 1:]:
        if l.strip():
            cur.append(l.strip())
        elif cur:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    out = []
    for b in blocks:
        first = b[0]
        if re.match(r"^[*'^\"®†‡]", first) and (len(first) < 4 or re.match(r"^[*'^\"®†‡]\s", first)):
            continue
        if re.match(r"^(?:I?\d+\s+)?THE\s+(?:SRINGA\s+)?SATAKAS?\b|^\d+\s*$", first, re.I) and len(b) <= 2:
            continue
        txt = re.sub(r"\s*[\^*®]\s+", " ", " ".join(b))
        m = re.match(r"^(\d{1,3})\s*\.\s+(.*)", txt, re.S)
        if m:
            out.append([int(m.group(1)), m.group(2)])
        elif out:
            out[-1][1] += " " + txt
    res = {}
    for idx, (n, t) in enumerate(out):
        t = re.sub(r"\s+", " ", HDR.sub(" ", re.split(r"THE\s+NORTHUMBERLAND", t)[0]))
        nxt = out[idx + 1][0] if idx + 1 < len(out) else n + 1
        k = nxt - n - 1
        parts = [t]
        if k > 0:
            cs = [m for m in CAND.finditer(t) if garbled(m.group(1))][:k]
            parts, prev = [], 0
            for m in cs:
                parts.append(t[prev:m.start()])
                prev = m.end()
            parts.append(t[prev:])
        for j, p in enumerate(parts):
            for pat, rep in OCR:
                p = re.sub(pat, rep, p)
            res[n + j] = re.sub(r"\s+", " ", p).strip()
    return res


def main():
    K = verses()
    p = ROOT / "sahitya/shatakatraya.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    n = 0
    for u in d["units"]:
        k = MAP.get(u["ref"])
        if k is None or u["english"]:
            continue
        u["english"] = K[k]
        u.setdefault("meta", {})["english_source"] = f"Kennedy 1913, Sringa Satakas verse {k}"
        n += 1
    d["notes"] += (f" [Shringarashataka English from J. M. Kennedy, The Satakas or Wise Sayings of Bhartrihari (1913), OCR from archive.org, a free paraphrase; {n} of 104 units paired. "
                   "Kennedy orders the verses differently from GRETIL, so units were paired by content (machine translation + TF-IDF to propose, then each pair read against the Sanskrit) and chains of constant offset were filled in; "
                   "the MAP is in tools/shataka_kennedy.py. Units not in MAP have no counterpart found: Kennedy omits some verses, replaces some with Latin or a cross reference, and his verse 63 only points to Vairagya 18. "
                   "meta.english_source names Kennedy on these units.]")
    write("sahitya/shatakatraya.json", d)
    print(n, "units filled")


if __name__ == "__main__":
    main()
