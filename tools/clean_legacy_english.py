import json, re
from common import ROOT, write

FILES = ["philosophical/bg_madhva.json", "upanishads/kena_madhva.json", "upanishads/brihadaranyaka_madhva.json", "upanishads/taittiriya_madhva.json", "upanishads/katha_madhva.json"]
BAD = re.compile(r"^[\"'‘“(]*(?:\]|\[[a-z]{1,3}$|\[-|[^\s]*[\$`\\\^]|[^\s]*[a-z][A-Z][^\s]*)")


def garble(tok):
    t = tok.strip(".,;:()'\"‘’“”!?—-")
    if not t or t.startswith("\\underline"):
        return False
    return bool(BAD.match(t)) and not re.match(r"^(?:Mc|Mac)", t)


def clean(e):
    e = re.sub(r"\bjaIva", "Jiva", e)
    out, drop = [], 0
    for tok in e.split(" "):
        if garble(tok):
            drop += 1
            continue
        out.append(tok)
    e = " ".join(out)
    e = re.sub(r"\s+([,.;:!?])", r"\1", e)
    return re.sub(r"[ \t]{2,}", " ", e).strip(), drop


def main():
    for rel in FILES:
        p = ROOT / rel
        d = json.loads(p.read_text(encoding="utf-8"))
        n = 0
        for u in d["units"]:
            for t in [u] + u.get("parts", []):
                e = t.get("english")
                if not e:
                    continue
                c = "\n".join(clean(x)[0] for x in e.split("\n"))
                if c != e:
                    t["english"] = c
                    n += 1
        if n:
            d["notes"] += " Words left in the legacy-font encoding in the english (tokens such as ']paiQa' or '[it') were removed."
            write(rel, d)
        print(rel, n)


if __name__ == "__main__":
    main()
