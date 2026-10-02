import json, glob, re
from common import ROOT

ROLES = (("mula", "sanskrit_mula", "english_mula"), ("bhashya", "sanskrit_bhashya", "english_bhashya"), ("tatparya", "sanskrit_tatparya", "english_tatparya"))
EXTRA = ("match_min", "align", "english_edits", "english_flags", "vedabase_texts")
SUTRA_FILES = ("bsb_madhva", "bsb_shankara", "bsb_shankara_gretil", "sribhashya_ramanuja")
TEXT_FILES = ("mbtn",)
KEYS = ("ref", "kind", "scope", "sanskrit", "english", "parts", "meta")


def _has(s, piece):
    return bool(piece and piece.strip() and piece.strip() in s)


def scope_of(u, name):
    s = (u.get("sanskrit") or "").strip()
    pieces = {r: (u.get(sk) or "") for r, sk, _ in ROLES}
    if name in TEXT_FILES:
        return "text"
    if not s:
        return "commentary"
    if not any(pieces.values()):
        k = u.get("kind")
        if name == "taittiriya_madhva" and k in ("mula", "bhashya"):
            return "mula" if k == "mula" else "commentary"
        return {"mula+bhashya": "mula+commentary", "bhashya": "commentary"}.get(k, "text")
    inn = [r for r in pieces if _has(s, pieces[r])]
    if not inn:
        inn = [r for r in pieces if pieces[r]]
    if inn == ["mula"]:
        return "mula"
    if "mula" not in inn:
        return "commentary"
    return "mula+commentary"


def kind_of(u, name, scope):
    if scope == "commentary":
        return "prose"
    if name in SUTRA_FILES and scope in ("mula", "mula+commentary"):
        return "sutra"
    if u.get("kind") == "group":
        return "group"
    base = u.get("sanskrit_mula") or u.get("sanskrit") or ""
    return "verse" if "॥" in base else "prose"


def convert(u, name):
    scope = scope_of(u, name)
    out = {"ref": u["ref"], "kind": kind_of(u, name, scope), "scope": scope,
           "sanskrit": u.get("sanskrit") or None, "english": u.get("english") or None}
    meta = {k: u[k] for k in EXTRA if u.get(k) not in (None, [], "")}
    if u.get("english_clean"):
        meta["english_verbatim"] = out["english"]
        out["english"] = u["english_clean"]
    if name not in TEXT_FILES:
        parts = []
        for r, sk, ek in ROLES:
            if u.get(sk) or u.get(ek):
                p = {"role": r}
                if u.get(sk):
                    p["sanskrit"] = u[sk]
                if u.get(ek):
                    p["english"] = u[ek]
                parts.append(p)
        if len([p for p in parts if p.get("sanskrit")]) >= 2 or (len(parts) >= 2 and scope == "mula+commentary"):
            out["parts"] = parts
    if meta:
        out["meta"] = meta
    return {k: out[k] for k in KEYS if k in out}


def convert_file(d, name):
    if d["units"] and all("scope" in u for u in d["units"]):
        return d
    d["units"] = [convert(u, name) for u in d["units"]]
    return d


def main():
    for f in sorted(glob.glob(str(ROOT / "*/*.json"))):
        d = json.loads(open(f, encoding="utf-8").read())
        name = f.rsplit("/", 1)[1][:-5]
        convert_file(d, name)
        open(f, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    main()
