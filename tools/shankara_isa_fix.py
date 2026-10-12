import re
from shk_fix import *

p, d, U = load("isa_shankara")

OPEN2 = "Thus the purport of the text is that after renouncing the three-fold desire for offspring etc., the knower of Self should save himself by devotion to true knowledge. And to the rest who, not being knowers of Self, are unable to realise it, the next verse states as follows-"
OPEN3 = "Now this verse is begun for the purpose of disparaging those who are without knowledge."
PRE9 = open(ROOT / "tools/data/isa_9_preamble.txt", encoding="utf-8").read().strip()

b = part(U["2"], "bhashya"); b["english"] = OPEN2 + "\n" + b["english"]
b = part(U["3"], "bhashya"); b["english"] = OPEN3 + "\n" + b["english"]

def move_tail(src, dst, marker):
    s = part(U[src], "bhashya"); t = part(U[dst], "bhashya")
    i = s["english"].index(marker)
    tail = s["english"][i:].strip()
    s["english"] = s["english"][:i].rstrip()
    t["english"] = tail + "\n" + t["english"]

move_tail("9", "10", "Now follows a statement of the distinction")
move_tail("13", "14", "Since this is so, it is but right")
b = part(U["9"], "bhashya"); b["english"] = PRE9 + "\n" + b["english"]

b = part(U["18"], "bhashya")
i = b["english"].index("Some entertain a doubt")
removed_len = len(b["english"]) - i
b["english"] = b["english"][:i].rstrip()

for u in d["units"]:
    for q in u.get("parts") or []:
        if q.get("english"):
            q["english"] = re.sub(r"\[\d+\]", "", q["english"])
    rebuild(u)

note(d, f"Shankara Isa fixes 2026-10-09: openers of 2, 3 and 9 supplied (2, 9 from Hiriyanna on wisdomlib; 3 written for this corpus); english tails that translate the next verse's opener moved 9 to 10 and 13 to 14; footnote markers stripped; {removed_len} chars of Hiriyanna's closing discussion removed from 18 (no Sanskrit in source)")
save(p, d)
