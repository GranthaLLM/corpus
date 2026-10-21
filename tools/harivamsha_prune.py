"""Drop or merge the stretches of harivamsha.json where the English belongs to other passages.
After harivamsha_realign.py the file was read (head of Sanskrit against head of English): every unit from source row 2852 on and around the dropped-row gaps, every third or fourth unit elsewhere. Five stretches
were found where the English is of another passage or a vulgate interpolation the Sanskrit does not have:
  - source rows 4962-4995 (five units), 5046-5115 and 5619-5686 (the Dvaravati description): English of other passages, dropped;
  - rows 6881-6927 (Hara and Hari battle): five units carry the Markandeya dialogue and a hymn that have no Sanskrit, dropped;
  - rows 7379-7468 (end of the Bhavishya parva): English of other passages, dropped;
  - rows 5954-5970 (Pradyumna and Mayavati): English runs one to two units behind its Sanskrit, so its eight units are merged into one.
Run from corpus/: python3 tools/harivamsha_prune.py [--dry]"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv
F = ROOT / "sahitya" / "harivamsha.json"

DROP = ["4962-4974", "4980-4981", "4988-4989", "4990", "4995", "5619-5623", "5624", "5625-5628", "5629-5630", "5631-5632", "5633-5634", "5635-5636", "5637-5645", "5646-5647", "5648-5650", "5651-5652", "5653-5654", "5655-5656", "5657-5658", "5659-5660", "5661-5662", "5663-5664", "5665-5666", "5667-5668", "5669", "5670", "5671-5677", "5678-5679", "5680-5682", "5683-5686", "5046-5050", "5051-5053", "5054", "5063-5066", "5067-5070", "5071-5083", "5084-5087", "5088-5090", "5091-5092", "5093-5104", "5110-5111", "5112-5115", "6881", "6882-6902", "6903-6909", "6920-6926", "6927", "7379", "7380-7381", "7382-7392", "7393-7394", "7395-7416", "7417", "7418-7419", "7420-7423", "7424-7427", "7428-7431", "7432-7434", "7435-7436", "7437-7438", "7439-7440", "7441-7444", "7445-7446", "7454-7462", "7463-7468"]
MERGES = [["5954-5955", "5956-5957", "5958-5961", "5962-5963", "5964-5965", "5966-5967", "5968", "5969-5970"], ["2953", "2954"], ["3700-3703", "3704", "3705-3708"]]


def main():
    d = json.loads(F.read_text(encoding="utf-8"))
    us = d["units"]
    refs = [u["ref"] for u in us]
    flat = [r for g in MERGES for r in g]
    assert all(r in refs for r in DROP + flat), [r for r in DROP + flat if r not in refs]
    n0 = len(us)
    first = {g[0]: g for g in MERGES}
    skip = {r for g in MERGES for r in g[1:]}
    by = {u["ref"]: u for u in us}
    out = []
    for u in us:
        r = u["ref"]
        if r in DROP or r in skip:
            continue
        if r in first:
            parts = [by[x] for x in first[r]]
            a, b = parts[0]["ref"].split("-")[0], parts[-1]["ref"].split("-")[-1]
            u = {"ref": f"{a}-{b}", "kind": "verse", "scope": "text",
                 "sanskrit": " ".join(x["sanskrit"].strip() for x in parts), "english": " ".join(x["english"].strip() for x in parts)}
        out.append(u)
    d["units"] = out
    d["notes"] += (
        f" [Prune 2026-10-21: after reading the realigned file (every unit in its second half and around the gaps, every third or fourth elsewhere), {len(DROP)} units whose English is of other passages (source rows 4962-4995, 5046-5115, "
        "5619-5686, 6881-6927 in part, 7379-7468) were dropped, and three stretches where the English runs behind the Sanskrit (rows 5954-5970, 3700-3708, 2953-2954) were merged into one unit each. "
        f" {n0} -> {len(out)} units.]"
    )
    print(n0, "->", len(out))
    if not DRY:
        F.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
