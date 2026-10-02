"""Convert text typed in the legacy Shivaji01 Devanagari font to Unicode.

Shivaji01 is a glyph-concatenation font. ASCII codes select glyphs, the short-i
matra and reph are typed in visual order, and some consonants are stored only as
half forms that become full when the bar glyph 'a' follows. A second 'a' is the
aa matra.
"""
import re
import sys

VIRAMA = "्"
H = {"b": "ब", "B": "भ", "c": "च", "g": "ग", "j": "ज", "l": "ल", "m": "म", "n": "न", "q": "थ", "s": "स", "v": "व",
     "y": "य", "S": "श", "Q": "ध", "Y": "ष", "N": "ण", "V": "द", "w": "ध", "G": "घ", "x": "क्ष", "L": "ळ", "H": "उ", "P": "प"}
F = {"k": "क", "K": "ख", "d": "द", "t": "त", "p": "प", "r": "र", "h": "ह", "f": "फ", "z": "ठ", "T": "ट",
     "J": "झ", "C": "छ", "D": "ड", "Z": "ढ", "~": "त्र", "&": "ज्ञ", "E": "श्र", "W": "द्व"}
X = {"@": "क्", "#": "ख्", "<": "त्", "=": "ङ्", "%": "त्", "*": "ह्", ";": "ल्"}
CONJ = {">": "क्त", "(": "ह्य", ")": "हृ", "$": "रू"}
VOW = {"A": "अ", "e": "ए", "[": "इ", "]": "उ", "?": "ऋ", "}": "ऊ", "!": "ॐ"}
MAT = {"u": "ु", "U": "ू", "R": "ृ", "o": "े", "O": "ै", "I": "ी", "M": "ं", ":": "ः", "^": "ँ"}
DIG = {str(i): "०१२३४५६७८९"[i] for i in range(10)}


def convert(s, trace=None):
    out = []
    src = []
    cluster = None
    last = None
    pend_i = False
    i = 0
    n = len(s)

    def add(piece, ch):
        out.append(piece)
        src.append(ch)

    while i < n:
        c = s[i]
        if c in H:
            if last not in ("half", "xhalf"):
                cluster = len(out)
            add(H[c] + VIRAMA, c)
            last = "half"
        elif c in CONJ or c in F:
            if last not in ("half", "xhalf"):
                cluster = len(out)
            add(CONJ[c] if c in CONJ else F[c], c)
            last = "full"
        elif c in X:
            if last not in ("half", "xhalf"):
                cluster = len(out)
            add(X[c], c)
            last = "xhalf"
        elif c == "a":
            if last in ("half", "xhalf"):
                out[-1] = out[-1][:-1]
                last = "full"
            else:
                add("ा", c)
                last = "matra"
        elif c == "`":
            if last in ("full", "half", "xhalf") and out:
                out[-1] = out[-1].rstrip(VIRAMA) + VIRAMA + "र"
                last = "full"
            else:
                add("्र", c)
        elif c == "\\":
            if out and last in ("full", "half") and not out[-1].endswith(VIRAMA):
                out[-1] = out[-1] + VIRAMA
            last = "matra"
        elif c == "i":
            pend_i = True
            i += 1
            continue
        elif c == "-":
            if cluster is not None:
                out.insert(cluster, "र्")
                src.insert(cluster, c)
                last = "matra"
            else:
                add("-", c)
        elif c in VOW:
            add(VOW[c], c)
            last = "vowel"
            cluster = None
        elif c in MAT:
            if c in "oO" and out and out[-1] == "ा":
                out[-1] = "ो" if c == "o" else "ौ"
            else:
                add(MAT[c], c)
            last = "matra"
        elif c == "|":
            add("।", c)
            last = None
            cluster = None
        elif c in DIG:
            add(DIG[c], c)
            last = None
            cluster = None
        else:
            add(c, c)
            last = None
            cluster = None
        i += 1
        if pend_i and last in ("full", "matra") and (i >= n or s[i] not in "a`\\"):
            add("ि", "i")
            pend_i = False
    r = "".join(out).replace("।।", "॥")
    if trace is not None:
        for piece, ch in zip(out, src):
            trace.extend([ch] * len(piece))
    return r


STOP = set("the of and to in is are was were be by for with that this it as at on or not but from his her their they he she we you i me my our your its have has had will shall may can do does so if then than no all any one who which what when where also even such these those them us him there thus therefore because since being been only".split())


def is_english(line):
    toks = re.findall(r"[A-Za-z']+", line)
    return len(toks) >= 2 and sum(1 for w in toks if w.lower() in STOP) / len(toks) >= 0.22


def convert_text(text):
    """Convert the legacy-font lines of a pdftotext dump, leaving English lines alone."""
    out = []
    for line in text.split("\n"):
        s = line.strip()
        out.append(line if not s or is_english(s) or not re.search(r"[a-zA-Z]", s) else convert(line))
    return "\n".join(out)


if __name__ == "__main__":
    data = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    sys.stdout.write(convert_text(data) if len(sys.argv) > 1 else convert(data))
