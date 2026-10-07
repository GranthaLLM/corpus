"""Madhva's bhashya opens by restating the sutra; Subba Rau and Sonde do not translate that restatement. Cut it from the bhashya Sanskrit when it is verbatim at the very start."""
import json, re, sys

SKIP = re.compile(r'[\d०-९/॥ॐ।\s]')

def key(s):
    return SKIP.sub('', s)

def strip_lead(b, k):
    i = j = 0
    while j < len(k) and i < len(b):
        if SKIP.match(b[i]):
            i += 1
        elif b[i] == k[j]:
            i += 1; j += 1
        else:
            return None
    if j < len(k):
        return None
    while i < len(b) and SKIP.match(b[i]):
        i += 1
    return b[i:]

def run(f="philosophical/bsb_madhva.json"):
    d = json.load(open(f)); n = 0
    for u in d["units"]:
        ps = u.get("parts") or []
        m = next((p for p in ps if p["role"] == "mula"), None)
        b = next((p for p in ps if p["role"] == "bhashya"), None)
        if not m or not b or not b.get("sanskrit"):
            continue
        k = key(m["sanskrit"])
        if not k:
            continue
        new = strip_lead(b["sanskrit"], k)
        if new is None or len(new) < 10:
            continue
        old = b["sanskrit"]
        if old in u["sanskrit"]:
            u["sanskrit"] = u["sanskrit"].replace(old, new, 1)
        b["sanskrit"] = new
        n += 1
    d["notes"] += f" [Sutra restatement cut from the start of the bhashya Sanskrit in {n} units (tools/bsb_madhva_dedupe_sutra.py); the restatement was untranslated.]"
    open(f, "w").write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    return n

if __name__ == "__main__":
    print(run())
