import re

_V = {"a": "अ", "ā": "आ", "i": "इ", "ī": "ई", "u": "उ", "ū": "ऊ", "ṛ": "ऋ", "ṝ": "ॠ", "e": "ए", "ai": "ऐ", "o": "ओ", "au": "औ"}
_M = {"ā": "ा", "i": "ि", "ī": "ी", "u": "ु", "ū": "ू", "ṛ": "ृ", "ṝ": "ॄ", "e": "े", "ai": "ै", "o": "ो", "au": "ौ"}
_C = {"k": "क", "kh": "ख", "g": "ग", "gh": "घ", "ṅ": "ङ", "c": "च", "ch": "छ", "j": "ज", "jh": "झ", "ñ": "ञ", "ṭ": "ट", "ṭh": "ठ",
      "ḍ": "ड", "ḍh": "ढ", "ṇ": "ण", "t": "त", "th": "थ", "d": "द", "dh": "ध", "n": "न", "p": "प", "ph": "फ", "b": "ब", "bh": "भ",
      "m": "म", "y": "य", "r": "र", "l": "ल", "v": "व", "ś": "श", "ṣ": "ष", "s": "स", "h": "ह"}
_TOK = sorted(list(_V) + list(_C), key=len, reverse=True)
_OTHER = {"ṃ": "ं", "ḥ": "ः", "'": "ऽ", "|": "।", "\n": "\n", " ": " "}


def iast_to_dev(s):
    s = s.lower().replace("||", "॥").replace("-", "")
    out, i, after_c = [], 0, False
    while i < len(s):
        ch = s[i]
        if ch in _OTHER or ch == "॥" or ch.isdigit():
            if after_c:
                out.append("्")
            out.append(_OTHER.get(ch, ch))
            after_c = False
            i += 1
            continue
        t = next((t for t in _TOK if s.startswith(t, i)), None)
        if t is None:
            raise ValueError(f"unmapped {ch!r} in {s[max(0, i - 10):i + 10]!r}")
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
