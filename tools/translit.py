import re

_V = {"a": "अ", "ā": "आ", "i": "इ", "ī": "ई", "u": "उ", "ū": "ऊ", "ṛ": "ऋ", "ṝ": "ॠ", "ḷ": "ऌ", "e": "ए", "ai": "ऐ", "o": "ओ", "au": "औ"}
_M = {"ā": "ा", "i": "ि", "ī": "ी", "u": "ु", "ū": "ू", "ṛ": "ृ", "ṝ": "ॄ", "ḷ": "ॢ", "e": "े", "ai": "ै", "o": "ो", "au": "ौ"}
_C = {"k": "क", "kh": "ख", "g": "ग", "gh": "घ", "ṅ": "ङ", "c": "च", "ch": "छ", "j": "ज", "jh": "झ", "ñ": "ञ", "ṭ": "ट", "ṭh": "ठ",
      "ḍ": "ड", "ḍh": "ढ", "ṇ": "ण", "t": "त", "th": "थ", "d": "द", "dh": "ध", "n": "न", "p": "प", "ph": "फ", "b": "ब", "bh": "भ",
      "m": "म", "y": "य", "r": "र", "l": "ल", "v": "व", "ś": "श", "ṣ": "ष", "s": "स", "h": "ह"}
_TOK = sorted(list(_V) + list(_C), key=len, reverse=True)
_LET = "a-zāīūṛṝḷṅñṭḍṇśṣ"
_MARK = {"ṃ": "ं", "ṁ": "ं", "ḥ": "ः"}
_DIGIT = str.maketrans("0123456789", "०१२३४५६७८९")
_PROTECT = re.compile(r"\(BhGR_[^)]*\)|bbs_[\d,.]+[a-z]?|\bfn\.?:|_{2,}")
_APPARATUS = re.compile(r"^.*?:[a-z]\]", re.S)
_META = re.compile(r"transliterated by|proof-read|\bafter\b|\bins\b|\brepeat")
_LATIN = re.compile(r"[A-Z]|[fqwxz]")


def _word(w):
    w = re.sub(rf"(?<=[{_LET}ṃḥ])-(?=[{_LET}])", "", w)
    out, i, after_c = [], 0, False
    while i < len(w):
        ch = w[i]
        t = next((t for t in _TOK if w.startswith(t, i)), None)
        if t is None:
            if after_c:
                out.append("्")
                after_c = False
            if ch in _MARK:
                out.append(_MARK[ch])
            elif ch == "'":
                out.append("'" if i > 0 and w[i - 1] in _LET + "ṃḥ" and not (i + 1 < len(w) and w[i + 1] in _LET) else "ऽ")
            else:
                out.append(ch.translate(_DIGIT))
            i += 1
            continue
        i += len(t)
        if t in _C:
            if after_c:
                out.append("्")
            out.append(_C[t])
            after_c = True
        elif after_c:
            if t != "a":
                out.append(_M[t])
            after_c = False
        else:
            out.append(_V[t])
    if after_c:
        out.append("्")
    return "".join(out)


def _danda(s):
    s = s.replace("||", "॥").replace("//", "॥")
    s = s.replace("|", "।")
    return re.sub(r"(?<!\d)/|/(?!\d)", "।", s)


def _plain(s):
    parts = re.split(r"(\s+)", _danda(s))
    return "".join(p if p.isspace() or _LATIN.search(p) else _word(p.lower()) for p in parts)


def iast_to_dev(s):
    s = re.sub(rf"(?<=[{_LET}ṃḥ])-[ \t]+(?=[{_LET}])", "", s)
    s = re.sub(r"-(?=\n)", "", s)
    pre = ""
    m = _APPARATUS.match(s)
    if m:
        pre, s = m.group(), s[m.end():]
    elif _META.search(s):
        return s
    out, pos = [], 0
    for m in _PROTECT.finditer(s):
        out.append(_plain(s[pos:m.start()]))
        out.append(m.group())
        pos = m.end()
    out.append(_plain(s[pos:]))
    return pre + "".join(out)


def devanagari_units(obj):
    if obj.get("script") != "IAST":
        return obj
    for u in obj["units"]:
        for k in ("sanskrit", "sanskrit_mula", "sanskrit_bhashya"):
            if u.get(k):
                u[k] = iast_to_dev(u[k])
    obj["script"] = "Devanagari"
    obj["notes"] = ((obj.get("notes") or "") + " [sanskrit transliterated from IAST to Devanagari by tools/translit.py: hyphens in compounds dropped, source markers and apparatus left as is]").strip()
    return obj
