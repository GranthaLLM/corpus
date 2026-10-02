import json, re, subprocess
from common import ROOT, RAW, write

SRC = RAW / "brihadaranyaka_madhva_sonde.txt"
STOP = set("the of and to in is are was were be by for with that this it as at on or not but from his her their they he she we you i me my our your its have has had will shall may can do does so if then than no all any one who which what when where whom whose also even such these those them us him into upon there thus therefore because since being been which only more most very each same other another own both few much many how why while about between through during before after above below up down out off over under again further here there once".split())
BEGIN = re.compile(r"Thus\s+begins?\s+(?:the\s+)?(\w+)", re.I)
MARK_BH = re.compile(r"^\s*Bh\w{2,6}\s*:?\s*$", re.I)
MARK_UP = re.compile(r"^\s*Upanishad\s*:?\s*$", re.I)
MARK_FE = re.compile(r"^\s*(Further explanation|Explanatory note|Note)\s*:?", re.I)
RUN = re.compile(r"^\s*(Ea\w+|\d{1,4}|[IVX]{1,5}\.?|\|\|.*\|\||Thus\s+(ends|begins).*)\s*$", re.I)
GARB = re.compile(r"[|\\^<>@~$`]")


def is_english(l):
    s = l.strip()
    if not s or RUN.match(s):
        return False
    toks = re.findall(r"[A-Za-z']+", s)
    if len(toks) < 2:
        return False
    if len(GARB.findall(s)) / max(len(s), 1) > 0.02:
        return len(toks) > 8 and sum(1 for t in toks if t.lower() in STOP) / len(toks) > 0.3
    return sum(1 for t in toks if t.lower() in STOP) / len(toks) >= 0.22


def sections(lines):
    idx = [(i, BEGIN.search(l).group(1).lower()) for i, l in enumerate(lines) if BEGIN.search(l) and len(l.strip()) < 70]
    idx = [(i, w) for i, w in idx]
    out = []
    for k, (i, w) in enumerate(idx):
        j = idx[k + 1][0] if k + 1 < len(idx) else len(lines)
        out.append((w, i, j))
    return out


def bhashya_english(lines):
    state, paras, cur = None, [], []
    def flush():
        nonlocal cur
        if cur:
            paras.append(re.sub(r"(\w)- (\w)", r"\1\2", " ".join(cur)))
            cur = []
    for l in lines:
        if MARK_UP.match(l):
            flush(); state = "up"; continue
        if MARK_BH.match(l):
            flush(); state = "bh"; continue
        if MARK_FE.match(l):
            flush(); state = "fe"; continue
        if state != "bh":
            continue
        if not l.strip():
            flush(); continue
        if is_english(l):
            cur.append(l.strip())
        else:
            flush()
    flush()
    return [p for p in paras if len(p) > 25]


def main(write_out=True):
    lines = SRC.read_text(encoding="utf-8").split("\n")
    secs = sections(lines)
    d = json.loads((ROOT / "upanishads/brihadaranyaka_madhva.json").read_text(encoding="utf-8"))
    units = d["units"]
    short, n = [], 0
    pairs = list(zip(units[:28], secs[:28]))
    tail = secs[28:]
    for u, (w, a, b) in pairs:
        paras = bhashya_english(lines[a:b])
        assign(u, paras, w, short)
    paras = []
    for w, a, b in tail:
        paras += bhashya_english(lines[a:b])
    assign(units[28], paras, "first to twentieth", short)
    n = sum(1 for u in units if u.get("english"))
    d["notes"] += (f" [English from Nagesh D. Sonde, Brihad Aranyaka Upanishad Bhashya by Sri Madhvacharya (2012, free to copy; PDF text layer, his Devanagari is in a legacy font and unused). "
                   f"Sonde's sections 'Thus begins the X Braahmana' were matched in order to the Setutila units; only the English of his 'Bhashya:' blocks is used (not the mantra translations under 'Upanishad:' or his 'Further explanation'). "
                   f"Setutila's last unit of adhyaya 7 (Vimsham) holds the commentary of brahmanas 1 to 20, so it gets Sonde's First to Twentieth. {n} of {len(units)} units have english. "
                   f"Left null because Sonde's translation is much shorter than the Sanskrit (under half): {', '.join(short)}; the last two units (adhyaya 8) are not in Sonde.]")
    d["source_english"] = {"citation": "Sonde, Brihad Aranyaka Upanishad Bhashya by Sri Madhvacharya (2012)", "url": "https://nageshsonde.com/", "license": "Author states: not protected by any copyright; free to copy and distribute"}
    d["alignment"] = "by_ref"
    if write_out:
        write("upanishads/brihadaranyaka_madhva.json", d)
    return d, n, short


def assign(u, paras, w, short):
    en = "\n".join(paras)
    u["english"] = None
    for x in u.get("parts", []):
        x.pop("english", None)
    if not en or len(en) < 0.5 * len(u["sanskrit"]):
        short.append(u["ref"].split(" / ")[-1])
        return
    u["english"] = en
    u["parts"] = [{"role": "bhashya", "sanskrit": u["sanskrit"], "english": en}]
    u.setdefault("meta", {})["sonde_section"] = w


if __name__ == "__main__":
    d, n, short = main()
    print(n, "units; short:", short)
