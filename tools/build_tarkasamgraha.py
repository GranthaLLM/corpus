import re, html
from common import *

GRETIL_TARKA = "https://gretil.sub.uni-goettingen.de/gretil/1_sanskr/6_sastra/3_phil/nyaya/antarkau.htm"


def mula():
    t = (RAW / "tarka_ono.htm").read_text(encoding="utf-8", errors="replace")
    txt = html.unescape(re.sub(r"<[^>]+>", "", t))
    out = []
    for m in re.finditer(r"^AnTs_(\S+)\s+(.*)$", txt, re.M):
        ref, s = m.group(1), m.group(2).strip()
        s = re.sub(r"\d", "", s).replace("-", "")
        s = re.sub(r"\s+", " ", s).replace(" //", " ||").replace(" /", " |")
        out.append((ref, s))
    return out


def english_sections():
    P = paragraphs("tarkasangrahaofa00annaiala.txt")
    secs, cur = [], None
    for p in P:
        m = re.match(r"^(\d+)\s*\.\s*['‘’\"“]", p)
        if m and len(p) < 1500:
            cur = {"n": int(m.group(1)), "first": p[m.end() - 1:], "rest": []}
            secs.append(cur)
        elif cur is not None:
            cur["rest"].append(p)
    return secs


def align(keys, E):
    import math
    n, m = len(keys), len(E)
    ls = [max(len(re.sub(r"[^\w]", "", " ".join(k[1]))), 1) for k in keys]
    le = [max(len(e["first"]), 1) for e in E]
    r = sum(le) / sum(ls)
    INF = 1e18
    C = [[INF] * (m + 1) for _ in range(n + 1)]
    B = [[None] * (m + 1) for _ in range(n + 1)]
    C[0][0] = 0
    GAPS, GAPE = 1.3, 0.6
    for i in range(n + 1):
        for j in range(m + 1):
            if C[i][j] >= INF:
                continue
            if i < n and C[i][j] + GAPS < C[i + 1][j]:
                C[i + 1][j], B[i + 1][j] = C[i][j] + GAPS, (i, j, "skipS")
            if j < m and C[i][j] + GAPE < C[i][j + 1]:
                C[i][j + 1], B[i][j + 1] = C[i][j] + GAPE, (i, j, "skipE")
            if i < n and j < m:
                num = int(keys[i][0])
                prior = 0.0 if 0 <= num - E[j]["n"] <= 1 else 0.6 * min(abs(num - E[j]["n"] - 0.5), 6)
                c = abs(math.log(le[j] / (ls[i] * r))) + prior
                if C[i][j] + c < C[i + 1][j + 1]:
                    C[i + 1][j + 1], B[i + 1][j + 1] = C[i][j] + c, (i, j, "pair")
    i, j, pairs = n, m, {}
    while (i, j) != (0, 0):
        pi, pj, how = B[i][j]
        if how == "pair":
            pairs[pi] = pj
        i, j = pi, pj
    return pairs


def main():
    M = mula()
    keys = []
    for ref, s_ in M:
        if ref.endswith("cd"):
            keys[-1][1].append(s_)
        else:
            keys.append([re.sub(r"[a-z]+$", "", ref), [s_]])
    units = [{"ref": k, "kind": "mula", "sanskrit": " ".join(lines), "english": None} for k, lines in keys]
    write("philosophical/tarkasamgraha.json", dict(
        id="5", text="Tarkasaṃgraha of Annambhaṭṭa", tradition="Nyaya", commentator=None, script="IAST", units=units,
        source_sanskrit={"citation": "Annambhatta, Tarkasamgraha, analytic text input by Takuya Ono (GRETIL); sandhi and compound markers removed", "url": GRETIL_TARKA, "license": "GRETIL: for reference purposes only, terms as for source file"},
        source_english={"citation": "The Tarkasangraha of Annambhatta with the author's gloss Dipika and an English translation (1851 Allahabad ed., archive.org scan)", "url": "https://archive.org/details/tarkasangrahaofa00annaiala", "license": None},
        bundled=False, needs_ocr=True, alignment="unaligned",
        notes=("Sanskrit only (81 mula sections, GRETIL analytic text with sandhi markers removed; verse 1 ab+cd is one unit). The scan's English is deliberately NOT attached: its printed section numbers do not follow GRETIL's (offset by one early, equal in the middle, drifting later, because the translator also numbers pieces of the Dipika gloss), and trial pairings by number or by length put the wrong translation on about a third of the sections. A reliable pairing needs the scan's Devanagari to be OCR'd (Sarvam Vision or similar) and matched to these sections by text, as was done for the Taittiriya Madhva file."),
        ))
    print(len(units))


if __name__ == "__main__":
    main()
