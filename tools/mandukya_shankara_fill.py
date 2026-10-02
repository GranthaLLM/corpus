import json, re
from common import ROOT, RAW, write
import wl

SLUG = "mandukya-upanishad-karika-bhashya"
CACHE = RAW / "mandukya_shankara_wl" / "pages.json"
TITLE = re.compile(r"^Mandukya Karika, verse (\d+)\.(\d+)(?:-(\d+))?$")


def pages():
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    _, toc = wl.toc(SLUG)
    out = [{"id": i, "title": t, "lines": wl.page_text("https://www.wisdomlib.org" + h) or []} for i, t, h in toc]
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def parse(lines, lo, hi):
    trans, comm, state, cur, alias = {}, [], "pre", None, {}
    for l in lines:
        if l.startswith("Shankara Bhashya"):
            state = "com"
            continue
        if l.startswith("Anandagiri") or l.startswith("Notes") or l.startswith("Footnotes"):
            state = "end"
            continue
        if state == "pre":
            m = re.match(r"^(\d+)(?:\s*-\s*(\d+))?\.\s+(.*)", l)
            if m and not re.search(r"[ऀ-ॿ]", l) and lo <= int(m.group(1)) <= hi:
                cur = int(m.group(1))
                trans[cur] = m.group(3).strip()
                for k in range(cur + 1, int(m.group(2) or cur) + 1):
                    trans[k] = None
                    alias[k] = cur
            elif cur is not None and not re.search(r"[ऀ-ॿ]", l) and not re.match(r"^[A-Za-zāīūṛṃśṣḥṅñṭḍṇ' |0-9-]+\|", l):
                trans[cur] += " " + l
        elif state == "com":
            comm.append(l)
    for k, a in alias.items():
        trans[k] = trans[a]
    return trans, "\n".join(comm).strip()


def merge_ranges(d, by):
    units, merged = d["units"], []
    for (a, lo, hi), lines in sorted(by.items()):
        if hi == lo:
            continue
        refs = [f"{a}.K{k}" for k in range(lo, hi + 1)]
        have = {u["ref"]: u for u in units}
        if not all(r in have for r in refs):
            continue
        grp = [have[r] for r in refs]
        if all(u.get("english") for u in grp) and len(grp) == 1:
            continue
        if not any(not u.get("english") for u in grp):
            continue
        trans, comm = parse(lines, lo, hi)
        if not all(k in trans for k in range(lo, hi + 1)):
            continue
        base = grp[0]
        for x in grp[1:]:
            for role in ("mula", "bhashya"):
                bp = next((p for p in base.get("parts", []) if p["role"] == role), None)
                xp = next((p for p in x.get("parts", []) if p["role"] == role), None)
                if xp and xp.get("sanskrit"):
                    if bp is None:
                        bp = {"role": role, "sanskrit": xp["sanskrit"]}
                        base.setdefault("parts", []).append(bp)
                    else:
                        bp["sanskrit"] = (bp.get("sanskrit") or "") + "\n" + xp["sanskrit"]
            base["sanskrit"] = "\n".join(p["sanskrit"] for p in base["parts"] if p.get("sanskrit")) if base.get("parts") else base["sanskrit"] + "\n" + x["sanskrit"]
            units.remove(x)
        has_b = any(p["role"] == "bhashya" and p.get("sanskrit") for p in base.get("parts", []))
        mula_en = " ".join(dict.fromkeys(trans[k] for k in range(lo, hi + 1)))
        comm_en = comm if has_b else ""
        for x in base.get("parts", []):
            x.pop("english", None)
        for p in base.get("parts", []):
            if p["role"] == "mula":
                p["english"] = mula_en
            if p["role"] == "bhashya" and comm_en:
                p["english"] = comm_en
        base["english"] = "\n".join(x for x in (mula_en, comm_en) if x)
        base["scope"] = "mula+commentary" if has_b else base["scope"]
        base["ref"] = f"{a}.K{lo}-{hi}"
        base.setdefault("meta", {})["english_source"] = "wisdomlib, Nikhilananda 1949 (range page)"
        merged.append(base["ref"])
    return merged


def main():
    P = pages()
    by = {}
    for p in P:
        m = TITLE.match(p["title"])
        if m:
            a, lo = int(m.group(1)), int(m.group(2))
            by[(a, lo, int(m.group(3) or lo))] = p["lines"]
    d = json.loads((ROOT / "upanishads/mandukya_shankara.json").read_text(encoding="utf-8"))
    n, parked = 0, []
    for u in d["units"]:
        m = re.match(r"^(\d)\.K(\d+)$", u["ref"])
        if not m or u.get("english"):
            continue
        a, k = int(m.group(1)), int(m.group(2))
        key = next((x for x in by if x[0] == a and x[1] <= k <= x[2]), None)
        if key is None:
            parked.append(u["ref"])
            continue
        trans, comm = parse(by[key], key[1], key[2])
        if key[1] != key[2] or k not in trans:
            parked.append(u["ref"])
            continue
        has_b = any(p["role"] == "bhashya" and p.get("sanskrit") for p in u.get("parts", []))
        mula_en, comm_en = trans[k], comm if has_b else ""
        for x in u.get("parts", []):
            x.pop("english", None)
        parts = list(u.get("parts", []))
        mp = next((x for x in parts if x["role"] == "mula"), None)
        bp = next((x for x in parts if x["role"] == "bhashya"), None)
        if mp:
            mp["english"] = mula_en
        if bp and comm_en:
            bp["english"] = comm_en
        u["english"] = "\n".join(x for x in (mula_en, comm_en) if x)
        u.setdefault("meta", {})["english_source"] = "wisdomlib, Nikhilananda 1949 (joined by karika number)"
        n += 1
    merged = merge_ranges(d, by)
    d["notes"] += f" [Range pages: units {', '.join(merged)} were merged because wisdomlib translates those karikas and their commentary together. {n} more units joined by karika number from the wisdomlib page of the same number, the earlier text-based join having failed on variant readings; parked (range pages or no page): {', '.join(parked)}.]"
    write("upanishads/mandukya_shankara.json", d)
    print(n, "parked", parked)


if __name__ == "__main__":
    main()
