"""Resolve a corpus address to its text. Usage: python3 tools/lookup.py FILE:REF[.ROLE] [--json]

FILE is the file stem (bsb_madhva), REF the unit ref as the file spells it (1.1.1, 3/4, mangalacharana), and ROLE
(mula, bhashya, tatparya) optionally selects one part of the unit. Without ROLE the whole unit is returned,
including its parts.  Examples:
  bsb_madhva:1.1.1            sutra plus bhashya, and the split parts
  bsb_madhva:1.1.1.bhashya    the commentary only
  bg_madhva:3/4.tatparya      Sanskrit-only parts return no english
"""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROLES = ("mula", "bhashya", "tatparya")


class NotFound(LookupError):
    pass


def split_address(addr):
    if ":" not in addr:
        raise NotFound(f"address needs FILE:REF, got {addr!r}")
    stem, rest = addr.split(":", 1)
    role = None
    for r in ROLES:
        if rest.endswith("." + r):
            rest, role = rest[: -len(r) - 1], r
            break
    return stem, rest, role


def load(stem):
    hits = glob.glob(str(ROOT / "*" / f"{stem}.json"))
    if not hits:
        raise NotFound(f"no file {stem}")
    return json.loads(Path(hits[0]).read_text(encoding="utf-8"))


def get(addr):
    stem, ref, role = split_address(addr)
    d = load(stem)
    u = next((x for x in d["units"] if x["ref"] == ref), None)
    if u is None:
        raise NotFound(f"{stem} has no unit {ref!r}")
    out = {"address": addr, "work": d["text"], "author": d.get("commentator"), "scope": u["scope"], "kind": u["kind"]}
    if role is None:
        out.update(sanskrit=u["sanskrit"], english=u["english"], parts=u.get("parts") or [])
        return out
    p = next((x for x in u.get("parts") or [] if x["role"] == role), None)
    if p is not None:
        out.update(sanskrit=p.get("sanskrit"), english=p.get("english"))
    elif u["scope"] == "mula" and role == "mula" or u["scope"] == "commentary" and role == "bhashya":
        out.update(sanskrit=u["sanskrit"], english=u["english"])
    else:
        raise NotFound(f"{stem}:{ref} has no {role} part (scope {u['scope']}, parts {[x['role'] for x in u.get('parts') or []]})")
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        sys.exit(2)
    try:
        r = get(args[0])
    except NotFound as e:
        print(f"not found: {e}")
        sys.exit(1)
    if "--json" in sys.argv:
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return
    print(f"{r['address']}  ({r['work']}, {r['author'] or '-'}; {r['scope']} {r['kind']})")
    print("\nSANSKRIT\n" + (r["sanskrit"] or "-"))
    print("\nENGLISH\n" + (r["english"] or "-"))
    for p in r.get("parts") or []:
        print(f"\n[{p['role']}] sanskrit {len(p.get('sanskrit') or '')} chars, english {len(p.get('english') or '')} chars")


if __name__ == "__main__":
    main()
