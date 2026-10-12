import json, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
UP = ROOT / "upanishads"


def load(name):
    p = UP / f"{name}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    return p, d, {u["ref"]: u for u in d["units"]}


def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def part(u, role):
    for q in u.get("parts") or []:
        if q["role"] == role:
            return q
    raise KeyError((u["ref"], role))


def rebuild(u):
    if u.get("parts"):
        u["english"] = "\n".join(q["english"] for q in u["parts"] if q.get("english")) or None


def note(d, text):
    d["notes"] = (d.get("notes") or "") + " [" + text + "]"
