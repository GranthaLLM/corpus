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


def fold_into(rel, dropped_ref, target_ref, new_ref=None, mode="intro", note=None):
    """Fold a dropped unit's Sanskrit into an existing unit whose english already covers it.
    mode 'intro': dropped Sanskrit goes at the start of the target's bhashya part (after the verse, matching english order).
    mode 'next': dropped unit is the following verse; its mula and bhashya Sanskrit are appended to the target's parts."""
    cur = json.load(open(rel, encoding="utf-8"))
    d = next(u for u in old_file(rel)["units"] if u["ref"] == dropped_ref)
    t = next(u for u in cur["units"] if u["ref"] == target_ref)
    parts = t.get("parts") or [{"role": "mula", "sanskrit": t["sanskrit"], **({"english": t["english"]} if t.get("english") else {})}]
    byrole = {p["role"]: p for p in parts}
    if mode == "intro":
        b = byrole.get("bhashya")
        if b is None:
            b = {"role": "bhashya", "sanskrit": ""}
            parts.append(b)
        b["sanskrit"] = d["sanskrit"].strip() + ("\n" + b["sanskrit"] if b.get("sanskrit") else "")
    else:
        dp = {p["role"]: p for p in (d.get("parts") or [{"role": "mula", "sanskrit": d["sanskrit"]}])}
        for role in ("mula", "bhashya"):
            if role in dp and dp[role].get("sanskrit"):
                p = byrole.get(role)
                if p is None:
                    p = {"role": role, "sanskrit": ""}
                    parts.append(p)
                    byrole[role] = p
                p["sanskrit"] = (p["sanskrit"] + "\n" if p.get("sanskrit") else "") + dp[role]["sanskrit"]
    order = {"mula": 0, "bhashya": 1, "tatparya": 2}
    parts.sort(key=lambda p: order.get(p["role"], 9))
    t["parts"] = parts
    t["sanskrit"] = "\n".join(p["sanskrit"] for p in parts if p.get("sanskrit"))
    if new_ref:
        t["ref"] = new_ref
    if note:
        cur["notes"] = (cur["notes"] or "") + " " + note
    open(rel, "w", encoding="utf-8").write(json.dumps(cur, ensure_ascii=False, indent=1) + "\n")
