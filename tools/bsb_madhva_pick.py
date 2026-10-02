import json, re, subprocess
from common import ROOT, write

PRE_SONDE = "75d6645"
PATH = "philosophical/bsb_madhva.json"


def noise(t):
    if not t:
        return 1.0
    bad = len(re.findall(r"[^A-Za-z0-9\s.,;:'\"()\-?!’‘“”—–\[\]/]", t)) + 3 * len(re.findall(r"_ _|\.\.\.\.|\s[,;:]\s", t))
    return bad / len(t)


def bhashya(u):
    return next((p for p in u.get("parts", []) if p["role"] == "bhashya"), None)


def main():
    pre = {u["ref"]: u for u in json.loads(subprocess.check_output(["git", "show", f"{PRE_SONDE}:{PATH}"], cwd=ROOT))["units"]}
    d = json.loads((ROOT / PATH).read_text(encoding="utf-8"))
    n_rau = n_son = n_both = 0
    for u in d["units"]:
        bp = bhashya(u)
        if not bp or "Sonde" not in u.get("meta", {}).get("english_source", ""):
            continue
        sonde = bp.get("english") or ""
        o = pre.get(u["ref"])
        ob = bhashya(o) if o else None
        rau = (ob or {}).get("english") if o and "Sonde" not in o.get("meta", {}).get("english_source", "") else None
        sk = len(bp.get("sanskrit") or "") or 1
        mula = next((p for p in u.get("parts", []) if p["role"] == "mula"), {})
        use_rau = bool(rau) and noise(rau) < 0.02 and len(rau) / sk >= 0.5
        main_b, alt_b = (rau, sonde) if use_rau else (sonde, rau)
        bp["english"] = main_b
        u["english"] = "\n".join(x for x in (mula.get("english"), main_b) if x)
        n_rau += use_rau
        n_son += not use_rau
    for u in d["units"]:
        m = u.get("meta", {})
        if str(m.get("english_source", "")).startswith(("Sonde", "Subba Rau")):
            m.pop("english_source")
            if not m:
                u.pop("meta")
    d["notes"] = re.sub(r" \[(?:Bhashya English for|Bhashya English replaced|One file)[^\]]*\]", "", d["notes"])
    d["notes"] += (" Bhashya english is Subba Rau 1904 where it is present, clean and at least half the Sanskrit length, otherwise Nagesh D. Sonde's Brahmasutra Bhashya translation "
                   f"({n_son} sutras); sutra english is Subba Rau's.")
    src = d["source_english"]
    d["source_english"] = (src if isinstance(src, list) else [src]) + [{"citation": "Nagesh D. Sonde, Brahmasutra Bhashya of Sri Madhvacharya (translation)", "url": "https://nageshsonde.com/", "license": "Author states: not protected by any copyright; free to copy and distribute"}]
    write(PATH, d)
    print("rau", n_rau, "sonde", n_son, "both", n_both)


if __name__ == "__main__":
    main()
