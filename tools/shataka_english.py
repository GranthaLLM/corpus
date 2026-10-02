import re
from common import *

HDR = re.compile(r"^(\d+\s+)?\S{0,6}\s*\S{0,6}\s*\S?\s*[SG]?ATAKA\.?\s*\d*\s*$|^[\(\)\s\d]+$|^Concerning|^The (Praise|Character|Way|Power|Evil|Mighty|Setting)|^Praise|^Dispraise|^Setting|^Condition|^Miscellaneous|^MISC|^Description|^[A-Z][a-z]+ [A-Za-z ]{3,30}\.\s*$")
START = re.compile(r"^[\{\(\[]?\s*(\d(?:\s?\d){0,2})\s*[./,)]+\s*(\S.*)$")

SPLITS = [
    ("niti", 76, ["So. The gods"]),
    ("niti", 8, ["( llj Fire"]),
    ("niti", 4, ["'He who would"]),
    ("vai", 108, ["no. The Creator", "in. The body is bent"]),
]
LEAD = re.compile(r"^(So\.|\( llj|'|\\ no\.|no\.|in\.)\s*")

MAP = {
    "1.1": "niti:1", "1.2": "vai:2", "1.3": "niti:3", "1.4": "niti:4", "1.5": "niti:5",
    "1.6": "niti:6", "1.7": "niti:7", "1.8": "niti:8", "1.9": "niti:9", "1.10": "niti:10",
    "1.11": "niti:11", "1.12": "niti:12", "1.13": "niti:13", "1.14": "niti:14", "1.15": "niti:15",
    "1.16": "niti:16", "1.17": "niti:17", "1.18": "niti:18", "1.19": "niti:19", "1.20": "niti:20",
    "1.21": "niti:21", "1.22": "niti:22", "1.23": "niti:23", "1.24": "niti:24", "1.25": "niti:25",
    "1.26": "niti:26", "1.27": "niti:27", "1.28": "niti:28", "1.29": "niti:29", "1.30": "niti:30",
    "1.31": "niti:31", "1.32": "niti:32", "1.33": "niti:33", "1.34": "niti:34", "1.35": "niti:35",
    "1.36": "niti:36", "1.37": "niti:38", "1.38": "niti:39", "1.40": "niti:40", "1.41": "niti:41",
    "1.42": "niti:42", "1.43": "niti:43", "1.44": "niti:44", "1.45": "niti:45", "1.46": "niti:46",
    "1.47": "niti:47", "1.48": "niti:48", "1.49": "niti:49", "1.50": "niti:50", "1.51": "niti:51",
    "1.52": "niti:52", "1.53": "niti:53", "1.54": "niti:54", "1.55": "niti:55", "1.56": "niti:56",
    "1.57": "niti:57", "1.58": "niti:58", "1.59": "niti:59", "1.60": "niti:60", "1.61": "niti:61",
    "1.62": "niti:62", "1.63": "niti:63", "1.64": "niti:64", "1.65": "niti:65", "1.66": "niti:66",
    "1.67": "niti:67", "1.68": "niti:68", "1.69": "niti_misc:5", "1.70": "niti:69", "1.71": "niti:70",
    "1.72": "niti:71", "1.73": "niti:72", "1.74": "niti:73", "1.75": "niti:74", "1.76": "niti:75",
    "1.77": "niti:76", "1.78": "niti:77", "1.79": "niti:78", "1.80": "niti:79", "1.81": "niti:80",
    "1.82": "niti:81", "1.83": "niti:82", "1.84": "niti:83", "1.85": "niti:84", "1.86": "niti:86",
    "1.87": "niti:87", "1.88": "niti:88", "1.89": "niti:89", "1.90": "niti:90", "1.91": "niti:91",
    "1.92": "niti:92", "1.93": "niti:93", "1.94": "niti:94", "1.95": "niti:95", "1.96": "niti:96",
    "1.97": "niti:97", "1.98": "niti:98", "1.99": "niti:99", "1.100": "niti:100", "1.101": "niti:101",
    "1.102": "niti:102", "1.103": "niti:103", "1.104": "niti:105", "1.105": "niti:106", "1.106": "niti:107",
    "1.107": "niti:108", "1.108": "niti:109", "3.-": "vai:43", "3.1": "vai_misc:16", "3.2": "vai:5",
    "3.--2": "vai:96", "3.3": "vai:4", "3.--3": "vai:74", "3.4": "vai:6", "3.5": "vai:36",
    "3.6": "vai:13", "3.7": "vai:12", "3.8": "vai:14", "3.8*1": "vai:17", "3.9": "vai:9",
    "3.10": "vai:45", "3.11": "vai:3", "3.12": "vai:16", "3.13": "vai:108", "3.14": "vai:103",
    "3.15": "vai:19", "3.16": "vai:20", "3.17": "vai_misc:8", "3.18": "vai:21", "3.19": "vai:92",
    "3.20": "vai_misc:19", "3.21": "vai:8", "3.22": "vai_misc:3", "3.23": "vai:55", "3.24": "vai:41",
    "3.25": "vai:69", "3.26": "vai:59", "3.27": "vai_misc:28", "3.28": "vai:47", "3.29": "niti_misc:16",
    "3.30": "vai_misc:31", "3.31": "vai:35", "3.32": "vai:104", "3.33": "vai:105", "3.34": "vai_misc:33",
    "3.35": "vai:54", "3.36": "vai:82", "3.37": "vai:106", "3.38": "vai:109", "3.39": "vai:102",
    "3.39*1": "vai:57", "3.41": "vai:37", "3.42": "vai:39", "3.43": "vai:7", "3.44": "vai:78",
    "3.45": "vai:11", "3.46": "vai:89", "3.47": "vai:48", "3.48": "vai:38", "3.49": "vai:107",
    "3.50": "vai:112", "3.51": "vai:24", "3.52": "vai:30", "3.53": "vai:50", "3.54": "vai:22",
    "3.55": "vai_misc:4", "3.56": "vai:27", "3.57": "vai:23", "3.58": "vai:25", "3.59": "vai:26",
    "3.60": "vai:29", "3.61": "vai:34", "3.61*1": "vai:95", "3.62": "vai_misc:24", "3.63": "vai:58",
    "3.64": "vai:60", "3.65": "vai_misc:17", "3.66": "vai:61", "3.67": "vai:73", "3.68": "vai:75",
    "3.69": "vai:76", "3.70": "vai:77", "3.71": "vai:81", "3.71*1": "vai:97", "3.72": "vai:71",
    "3.73": "vai:111", "3.74": "vai_misc:38", "3.75": "vai:88", "3.76": "vai:40", "3.77": "vai:53",
    "3.78": "vai:33", "3.79": "vai:85", "3.80": "vai:68", "3.81": "vai:46", "3.82": "vai:51",
    "3.83": "vai:91", "3.84": "vai:99", "3.85": "vai:42", "3.86": "vai:49", "3.87": "vai_misc:10",
    "3.88": "vai:93", "3.89": "vai:72", "3.90": "vai_misc:25", "3.91": "vai:101", "3.92": "vai:83",
    "3.93": "vai:64", "3.94": "vai:79", "3.95": "vai:86", "3.96": "vai:56", "3.97": "vai:10",
    "3.99": "vai:52", "3.99*1": "vai:80", "3.100": "vai:87", "3.100*1": "vai:94", "3.100*3": "vai:113",
}


def section(L, a, b):
    out, cur = [], None
    for ln in L[a - 1:b]:
        s = ln.strip()
        if not s:
            continue
        m = START.match(s)
        if HDR.match(s) and not m:
            continue
        if m:
            cur = [m.group(1).replace(" ", ""), m.group(2)]
            out.append(cur)
        elif cur:
            cur[1] += " " + s
    return [(n, re.sub(r"\s+", " ", t)) for n, t in out]


def split_merged(sec, idx, marks):
    k, rest = sec[idx]
    n, parts = int(k), []
    for mk in marks:
        a = rest.index(mk)
        parts.append((str(n), rest[:a].strip()))
        rest, n = rest[a:], n + 1
    parts.append((str(n), LEAD.sub("", rest.strip())))
    sec[idx:idx + 1] = parts


OCR_FIX = [("hejnay_wear an an gry: serpent^", "he may wear an angry serpent"), ("\u00a3irisha", "Sirisha"), ("Ke*sava", "Kesava"),
           ("~by", "by"), ("^iches", "riches"), ("brother 1 I", "brother ! I")]
RUNHEAD = re.compile(r"\s*\b(?:N\S{1,5}|V\S{2,8})\s+S\s?A\s?T\s?A\s?K\s?A\.?(?:\s+(?:\d+|[ivxl]+)\b\.?)?")
TAILHEAD = re.compile(r"(?<=[.!?])\s+(?:The|Praise|Dispraise|Concerning)\s[A-Z~][\w~ ]{3,50}\.$")


def clean(t):
    for a, b in OCR_FIX:
        t = t.replace(a, b)
    t = RUNHEAD.sub("", t)
    t = re.sub(r"(?<=\w)- (?=[a-z])", "", t)
    t = re.sub(r"\b0(?= )", "O", t)
    t = re.sub(r"\s+", " ", t).strip().rstrip("\\").strip()
    return TAILHEAD.sub("", t)


def wortham():
    L = (RAW / "wortham_satakas.txt").read_text(encoding="utf-8").split("\n")
    S = {"niti": section(L, 219, 978), "niti_misc": section(L, 981, 1143),
         "vai": section(L, 1923, 2795), "vai_misc": section(L, 2798, 3074)}
    for sec, idx, marks in SPLITS:
        split_merged(S[sec], idx, marks)
    S["vai"][89] = ("90", S["vai"][89][1])
    return {f"{k}:{n}": clean(t) for k, v in S.items() for n, t in v}


if __name__ == "__main__":
    W = wortham()
    p = ROOT / "sahitya/shatakatraya.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    n = 0
    for u in d["units"]:
        w = MAP.get(u["ref"])
        u["english"] = W[w] if w else None
        n += bool(w)
    d["alignment"] = "by_ref"
    d["notes"] = ("English: Wortham 1886 (archive.org djvu OCR text, unproofread; stray OCR noise remains). Wortham translates only the Niti and Vairagya "
                  "satakas, so all Shringarashataka units (2.x) have no English. Wortham follows Telang's order and numbering, which differs from GRETIL's, so units were "
                  "paired by content (machine translation of each GRETIL verse compared with Wortham, then checked by hand against the Sanskrit); the pairing is MAP "
                  "in tools/shataka_english.py. %d of 324 units have English. Wortham verses with no GRETIL counterpart are unused, and GRETIL verses with no Wortham "
                  "counterpart (1.39, 1.109, 3.40, 3.98, 3.100*2) have english null. ref = shataka.verse (1 Nitishataka, 2 Shringarashataka, 3 Vairagyashataka). "
                  "[normalized: 0 empty heading-only units dropped, 2 repeated refs suffixed -2/-3 (the source repeats the number); a repeated unit never reuses the first unit's English.]") % n
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("shatakatraya english", n)
