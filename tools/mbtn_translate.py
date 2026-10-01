import json, os, pathlib, re, subprocess, sys, time, urllib.error, urllib.request

from common import RAW
import mbtn_english as m

CACHE = RAW / "mbtn_hariprasad" / "verse_en.json"
KEY_FILE = pathlib.Path(os.environ.get("BODHAN_KEY_FILE", "~/.bodhan_key_translate")).expanduser()
BATCH = 10


def _call(text, key):
    body = json.dumps({"model": "indic-translate", "messages": [{"role": "user", "content": text}],
                       "source_language_code": "sa", "target_language_code": "en"}).encode()
    for _ in range(12):
        try:
            r = urllib.request.Request("https://api.bodhan.ai/v1/chat/completions", body,
                                       {"Authorization": "Bearer " + key, "Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(r, timeout=120))["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            time.sleep(float(e.headers.get("Retry-After") or 10) + 1)
        except Exception:
            time.sleep(10)
    return None


def _batch(items, key):
    out = _call("\n".join(f"[{i + 1}] {t}" for i, (_, t) in enumerate(items)), key)
    got = {}
    if out:
        for mm in re.finditer(r"(?ms)^\[(\d+)\]\s*(.*?)(?=^\[\d+\]|\Z)", out):
            got[int(mm.group(1))] = mm.group(2).strip()
    return {h: got[i + 1] for i, (h, _) in enumerate(items) if got.get(i + 1)}


def run(units):
    key = KEY_FILE.read_text().strip()
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    todo = {}
    for S in m._chapter_verses(units).values():
        for x in S:
            h = m._sha(x["t"])
            if h not in cache and x["t"].strip():
                todo[h] = x["t"].strip()
    items = list(todo.items())
    print("to translate", len(items), "cached", len(cache), flush=True)
    for k in range(0, len(items), BATCH):
        chunk = items[k:k + BATCH]
        got = _batch(chunk, key)
        for h, t in chunk:
            if h not in got:
                got.update(_batch([(h, t)], key))
        cache.update(got)
        CACHE.write_text(json.dumps(cache, ensure_ascii=False))
        print(min(k + BATCH, len(items)), "of", len(items), "cache", len(cache), flush=True)


def redo(units):
    key = KEY_FILE.read_text().strip()
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    byc = m._chapter_verses(units)
    order, seen = [], set()
    for ch in sorted(byc):
        for x in byc[ch]:
            h = m._sha(x["t"])
            if h not in seen and x["t"].strip():
                seen.add(h)
                order.append((h, x["t"].strip()))
    shifted = set()
    for S in byc.values():
        ns = [m._names_s(x["t"]) for x in S]
        ne = [m._names_e(cache[m._sha(x["t"])]) if m._sha(x["t"]) in cache else set() for x in S]
        for j in range(1, len(S) - 1):
            near = max(len(ns[j] & ne[j - 1]), len(ns[j] & ne[j + 1]))
            if len(ns[j]) >= 2 and near >= 2 and near > len(ns[j] & ne[j]):
                shifted.add(m._sha(S[j]["t"]))
    bad = {order[k][0] for b in range(0, len(order), BATCH) if any(h in shifted for h, _ in order[b:b + BATCH])
           for k in range(b, min(b + BATCH, len(order)))}
    todo = [(h, t) for h, t in order if h in bad or h not in cache]
    print("redo", len(todo), "of", len(order), flush=True)
    for n, (h, t) in enumerate(todo, 1):
        out = _call(t, key)
        if out:
            cache[h] = out.strip()
        if n % 25 == 0 or n == len(todo):
            CACHE.write_text(json.dumps(cache, ensure_ascii=False))
            print(n, "of", len(todo), flush=True)


if __name__ == "__main__":
    units = json.loads(subprocess.check_output(["git", "show", "567767d:philosophical/mbtn.json"], cwd=RAW.parent).decode())["units"]
    redo(units) if "--redo" in sys.argv else run(units)
