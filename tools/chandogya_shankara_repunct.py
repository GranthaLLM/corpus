"""Restore punctuation and spacing in chandogya_shankara english by aligning the
damaged english against freshly extracted wisdomlib (Jha) text on letters only."""
import sys, json, re, glob, difflib, os
from wl_text import page_text

RAW = os.environ["GRANTHA_WL"]
LOAD = {'1': (1145003, 1145016), '2': (1145221, 1145245), '3': (1145246, 1145263), '4': (1145264, 1145281),
        '5': (1145282, 1145303), '6': (1145304, 1145320), '7': (1145321, 1145347), '8': (1145348, 1145363)}
SKIP = ('Upaniṣad text:', 'Commentary (Śaṅkara Bhāṣya):')
OPEN = "‘“(["
CLOSE = ".,;:!?’”)]*"


def letters(s):
    pos, out = [], []
    for i, c in enumerate(s):
        if c.isalnum():
            out.append(c.lower())
            pos.append(i)
    return "".join(out), pos


def new_stream(ch):
    lo, hi = LOAD[ch]
    ids = open(RAW + "chand_keep.txt").read().split()
    lines = []
    for i in ids:
        if lo <= int(i) < hi:
            for l in page_text(open(RAW + f"chand/{i}.html", encoding="utf-8").read()):
                if l in SKIP or re.match(r"End of (Section|Discourse)", l):
                    continue
                lines.append(l)
    return "\n".join(lines)


def run(ch):
    d = json.load(open("upanishads/chandogya_shankara.json"))
    units = [u for u in d["units"] if u["ref"].split(".")[0].split("-")[-1] == ch]
    ntext = new_stream(ch)
    old, ranges = "", []
    for u in units:
        a = len(old)
        old += (u["english"] or "") + "\n"
        ranges.append((a, len(old)))
    nl, npos = letters(ntext)
    ol, opos = letters(old)
    sm = difflib.SequenceMatcher(None, ol, nl, autojunk=False)
    mp = {}
    for b in sm.get_matching_blocks():
        for k in range(b.size):
            mp[b.a + k] = b.b + k
    # letters index of old text start per unit
    import bisect
    out = {}
    prev_end = -1
    for u, (a, b) in zip(units, ranges):
        la = bisect.bisect_left(opos, a)
        lb = bisect.bisect_left(opos, b)
        idx = [mp[k] for k in range(la, lb) if k in mp]
        if not idx or not u["english"]:
            out[u["ref"]] = None
            continue
        n0, n1 = idx[0], idx[-1]
        s, e = npos[n0], npos[n1] + 1
        while s > 0 and ntext[s - 1] in OPEN:
            s -= 1
        while e < len(ntext) and ntext[e] in CLOSE:
            e += 1
        txt = ntext[s:e]
        out[u["ref"]] = {"new": txt, "old_letters": lb - la, "new_letters": n1 - n0 + 1, "matched": len(idx), "gap_before": n0 - prev_end - 1 if prev_end >= 0 else 0}
        prev_end = n1
    json.dump(out, open(RAW + f"chand_repunct_{ch}.json", "w"), ensure_ascii=False, indent=1)
    print(ch, "done", len(units))


if __name__ == "__main__":
    run(sys.argv[1])
