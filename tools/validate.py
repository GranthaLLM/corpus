import json, glob, re, sys, collections
from common import ROOT

SCOPES = {"text", "mula", "commentary", "mula+commentary"}
KINDS = {"verse", "sutra", "prose", "group"}
UNIT_KEYS = {"ref", "kind", "scope", "sanskrit", "english", "parts", "meta"}
REQUIRED = {"ref", "kind", "scope", "sanskrit", "english"}
ROLES = {"mula", "bhashya", "tatparya"}
TOP = {"id", "text", "tradition", "commentator", "script", "units", "source_sanskrit", "source_english", "bundled", "needs_ocr", "alignment", "slice_of", "notes"}


def check(f):
    errs, warns = [], []
    d = json.loads(open(f, encoding="utf-8").read())
    name = f.rsplit("/", 1)[1]
    for k in ("id", "text", "units", "script", "notes"):
        if k not in d:
            errs.append(f"missing top-level {k}")
    if set(d) - TOP:
        errs.append(f"unknown top-level {sorted(set(d) - TOP)}")
    if d.get("script") != "Devanagari":
        errs.append(f"script {d.get('script')}")
    seen = set()
    for u in d["units"]:
        r = u.get("ref")
        if set(u) - UNIT_KEYS or REQUIRED - set(u):
            errs.append(f"{r}: keys {sorted(set(u) ^ UNIT_KEYS)}")
            continue
        if r in seen:
            errs.append(f"{r}: duplicate ref")
        seen.add(r)
        if u["scope"] not in SCOPES or u["kind"] not in KINDS:
            errs.append(f"{r}: scope/kind {u['scope']}/{u['kind']}")
        for k in ("sanskrit", "english"):
            if u[k] is not None and (not isinstance(u[k], str) or not u[k].strip()):
                errs.append(f"{r}: {k} empty or not a string")
        s = u["sanskrit"] or ""
        parts = u.get("parts") or []
        by = {p.get("role"): p for p in parts}
        if set(p.get("role") for p in parts) - ROLES or len(by) != len(parts):
            errs.append(f"{r}: bad parts roles")
        if parts and u["scope"] in ("mula", "mula+commentary"):
            m = (by.get("mula") or {}).get("sanskrit")
            if m and m.strip() not in s:
                errs.append(f"{r}: mula part not in sanskrit")
            if u["scope"] == "mula":
                for role in ("bhashya", "tatparya"):
                    t = (by.get(role) or {}).get("sanskrit")
                    if t and t.strip() in s and t.strip() != (m or "").strip():
                        errs.append(f"{r}: scope mula but {role} is in sanskrit")
        if u["scope"] == "mula+commentary" and parts and not any(p.get("sanskrit") and p["role"] != "mula" for p in parts):
            errs.append(f"{r}: mula+commentary without commentary part")
        if u["sanskrit"] and u["english"] and u["scope"] == "mula+commentary" and len(u["english"]) < 0.8 * len(s):
            warns.append(f"{r}: english much shorter than sanskrit for scope mula+commentary")
        if re.search(r"[a-zA-Z]", re.sub(r"\(BhGR_[^)]*\)|bbs_[\d,.]+[a-z]?|\bfn\.?:|_+", "", s)) and name not in ("harivamsha.json", "chandogya_shankara_jha.json"):
            warns.append(f"{r}: latin letters in sanskrit")
    return d, errs, warns


def main():
    bad = 0
    tot = collections.Counter()
    for f in sorted(glob.glob(str(ROOT / "*/*.json"))):
        d, errs, warns = check(f)
        n = len(d["units"])
        both = sum(1 for u in d["units"] if u.get("sanskrit") and u.get("english"))
        tot["units"] += n
        tot["scoreable"] += both
        tot["warn"] += len(warns)
        if errs:
            bad += 1
            print(f"FAIL {f.rsplit('/', 1)[1]}: {len(errs)} errors, e.g. {errs[:3]}")
        if warns:
            print(f"warn {f.rsplit('/', 1)[1]}: {len(warns)}, e.g. {warns[:2]}")
    print(f"{tot['units']} units, {tot['scoreable']} scoreable, {tot['warn']} warnings, {bad} failing files")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
