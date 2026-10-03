import json, re, sys
from common import ROOT, RAW, write

SRC = {"mundaka_madhva": "mundaka.txt", "katha_madhva": "katha.txt", "taittiriya_madhva": "taittiriya.txt", "brihadaranyaka_madhva": "brihad.txt", "kena_madhva": "kena.txt"}
END = re.compile(r"[.?!:;\"”’)\]]\s*$")


def norm(t):
    return re.sub(r"\s+", " ", t)


def complete(name):
    p = ROOT / f"upanishads/{name}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    raw = norm((RAW / "sonde" / SRC[name]).read_text(encoding="utf-8", errors="replace"))
    done = []
    for u in d["units"]:
        e = (u.get("english") or "").rstrip()
        if len(e) < 200 or END.search(e):
            continue
        key = norm(e[-45:])
        i = raw.find(key)
        if i < 0 or raw.count(key) != 1:
            continue
        tail = raw[i + len(key):i + len(key) + 400]
        m = re.match(r"\s*(.{1,170}?)(?:([.?!])(?=\s|$)|(?=\s*(?:Further Explanation|\d+\s*\|\||[“”]|Upanishad\s*:|Bhashya\s*:|Aqa|\[it)))", tail)
        if not m or re.search(r"[|\\`~]|[A-Za-z][|`]", m.group(1)) or len(m.group(1).split()) > 28:
            continue
        add = (m.group(1) + (m.group(2) or ".")).strip()
        for t in [u] + u.get("parts", []):
            te = (t.get("english") or "").rstrip()
            if te.endswith(e[-45:]):
                t["english"] = te + " " + add
        done.append(u["ref"])
    if done:
        d["notes"] += f" [english cut off at a page or line break in the first extraction was completed from Sonde's text: {', '.join(done)}]"
        write(f"upanishads/{name}.json", d)
    print(name, len(done), done)


if __name__ == "__main__":
    for n in (sys.argv[1:] or SRC):
        complete(n)
