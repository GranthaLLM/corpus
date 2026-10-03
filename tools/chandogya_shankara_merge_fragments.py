import json, re, subprocess
from common import ROOT, write

SRC_REV = "1e28112^"

END = re.compile(r"[.?!:][”’\"')\]]*\s*$")


def main():
    d = json.loads(subprocess.check_output(["git", "show", f"{SRC_REV}:upanishads/chandogya_shankara.json"], cwd=ROOT))
    us = d["units"]
    part = lambda u, r: next((q for q in u.get("parts", []) if q["role"] == r), None)
    groups = []
    for u in us:
        en = (u.get("english") or "").strip()
        if groups and en and re.match(r"[a-z]", en):
            k = len(groups) - 1
            while k > 0 and all(x["ref"].startswith("colophon") for x in groups[k]):
                k -= 1
            last = next((x for x in reversed(groups[k]) if (x.get("english") or "").strip()), None)
            if last is not None and not END.search(last["english"].strip()):
                groups[k].extend(x for g in groups[k + 1:] for x in g)
                groups[k].append(u)
                del groups[k + 1:]
                continue
        groups.append([u])
    def piece(x, role):
        p = part(x, role)
        if p is not None:
            return p.get("sanskrit") or ""
        return x["sanskrit"] if (x["scope"] == "mula") == (role == "mula") else ""

    out, merged = [], 0
    for g in groups:
        if len(g) == 1:
            out.append(g[0])
            continue
        merged += len(g) - 1
        body = [x for x in g if not x["ref"].startswith("colophon")]
        def piece(x, role):
            p = part(x, role)
            if p is not None:
                return p.get("sanskrit") or ""
            return x["sanskrit"] if (x["scope"] == "mula") == (role == "mula") else ""
        sk = "\n".join(x["sanskrit"] for x in body)
        mula = next((piece(x, "mula") for x in body if piece(x, "mula")), "")
        bh = sk.replace(mula, "", 1).strip() if mula else sk
        parts = ([{"role": "mula", "sanskrit": mula}] if mula else []) + ([{"role": "bhashya", "sanskrit": bh}] if bh else [])
        refs = [x["ref"] for x in body]
        out.append({"ref": refs[0] if len(refs) == 1 else f"{refs[0]}-{refs[-1]}", "kind": "group", "scope": "mula+commentary" if mula and bh else "mula" if mula else "commentary", "sanskrit": sk,
                    "english": " ".join((x.get("english") or "").strip() for x in body).strip(), "parts": parts,
                    "meta": {"jha_rows": [min(r for x in body for r in (x.get("meta") or {}).get("jha_rows", [10 ** 9])), max(r for x in body for r in (x.get("meta") or {}).get("jha_rows", [0]))]}})
    d["units"] = out
    d["notes"] += (f" Where Jha's clause-level rows split one sentence between two units (the next unit's english starts in lower case and the previous one ends mid-sentence), the units were merged: {merged} units folded into their predecessors, "
                   "so a unit's english no longer starts or stops inside a clause that the next unit continues. In a merged unit the Sanskrit and the english both follow the text order (mula, its commentary, the next mula, its commentary); the mula part holds the first verse and the bhashya part the rest. Colophon lines that fell inside a merged group were dropped.")
    write("upanishads/chandogya_shankara.json", d)
    print(len(us), "->", len(out))


if __name__ == "__main__":
    main()
