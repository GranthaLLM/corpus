import json, subprocess

OLD_REV = "bf2d645^"


def old_file(rel):
    out = subprocess.run(["git", "show", f"{OLD_REV}:corpus/{rel}"], capture_output=True, text=True, cwd=".").stdout
    if not out:
        out = subprocess.run(["git", "show", f"{OLD_REV}:{rel}"], capture_output=True, text=True).stdout
    return json.loads(out)


def restore(rel, fills, source, note=None):
    """fills: ref -> english (str). Reinserts units dropped by drop_unscoreable at their old position."""
    cur = json.load(open(rel, encoding="utf-8"))
    old = old_file(rel)
    have = {u["ref"] for u in cur["units"]}
    order = [u["ref"] for u in old["units"]]
    oldu = {u["ref"]: u for u in old["units"]}
    idx = {u["ref"]: i for i, u in enumerate(cur["units"])}
    added = 0
    for ref, en in fills.items():
        if ref in have or ref not in oldu:
            continue
        u = dict(oldu[ref])
        u["english"] = en
        u.setdefault("meta", {})["english_source"] = source
        k = order.index(ref)
        prev = next((order[j] for j in range(k - 1, -1, -1) if order[j] in idx), None)
        pos = idx[prev] + 1 if prev is not None else 0
        cur["units"].insert(pos, u)
        idx = {x["ref"]: i for i, x in enumerate(cur["units"])}
        have.add(ref)
        added += 1
    if note and added:
        cur["notes"] = (cur["notes"] or "") + " " + note.format(n=added)
    open(rel, "w", encoding="utf-8").write(json.dumps(cur, ensure_ascii=False, indent=1) + "\n")
    return added
