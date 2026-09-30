import json, glob, re, sys
from common import ROOT

RAM_HDR = re.compile(r"\d*\s*S\w{2,3}\s+RAMANUJA GITA BHASY\S*\s*\[?Ch\.?[^\]]{0,6}\]?\s*\d*")


def clean_field(v):
    if isinstance(v, str):
        return re.sub(r"\s+", " ", RAM_HDR.sub(" ", v)).strip() if RAM_HDR.search(v) else v
    return v


def main():
    for f in sorted(glob.glob(str(ROOT / "*/*.json"))):
        d = json.loads(open(f, encoding="utf-8").read())
        U, out, seen, dropped, renamed = d["units"], [], {}, 0, 0
        for u in U:
            for k in ("english", "english_mula", "english_bhashya", "english_tatparya", "english_clean"):
                if k in u:
                    u[k] = clean_field(u[k])
            if not u.get("sanskrit") and not u.get("english"):
                dropped += 1
                continue
            n = seen.get(u["ref"], 0) + 1
            seen[u["ref"]] = n
            if n > 1:
                first = next(x for x in out if x["ref"] == u["ref"])
                if u.get("english") and u.get("english") == first.get("english"):
                    for k in ("english", "english_mula", "english_bhashya", "english_tatparya", "english_clean"):
                        if k in u:
                            u[k] = None
                u["ref"] = f"{u['ref']}-{n}"
                renamed += 1
            out.append(u)
        if dropped or renamed:
            note = d.get("notes") or ""
            note = re.sub(r" \[normalized:.*?\]$", "", note)
            d["notes"] = note + f" [normalized: {dropped} empty heading-only units dropped, {renamed} repeated refs suffixed -2/-3 (the source repeats the number); a repeated unit never reuses the first unit's English.]"
        d["units"] = out
        open(f, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
        if dropped or renamed:
            print(f.split("/")[-2] + "/" + f.split("/")[-1], "dropped", dropped, "renamed", renamed)


if __name__ == "__main__":
    main()
