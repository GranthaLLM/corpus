import json, glob, re
from common import ROOT

DEV_RUN = re.compile(r"[ऀ-ॿ][ऀ-ॿ \t|।॥.,;:()\[\]‘’'\"\-–—]{23,}[ऀ-ॿ]")
VERSE_MARK = re.compile(r"[ \t]*(?:[|।॥]{1,2}|[Il]{1,2})[ \t]*\d{1,3}[ \t]*(?:[|।॥]{1,2}|[Il]{1,2})(?=\s|$)")
GITA_HDR = re.compile(r"\s*\d{0,3}\s*THE B[A-Z]{2,5}VAD GITA\.?\s*[\[|\]]\s*\w{1,5}[.\-–]*\s*[IVXL]{1,5}\.?(?=\s)")
OVERRUN = {("bsb_shankara", "1.2.6"), ("bsb_shankara", "4.4.22")}


def strip_dev(t):
    if not t:
        return t
    t = DEV_RUN.sub("", t)
    t = VERSE_MARK.sub("", t)
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip() or None


def clean_unit(u, name):
    log = []
    for holder in [u] + list(u.get("parts") or []):
        e = holder.get("english")
        if not e:
            continue
        n = strip_dev(e)
        n = GITA_HDR.sub("", n) if n and name == "bg_shankara" else n
        if n != e:
            log.append(holder.get("role", "unit"))
            if n:
                holder["english"] = n
            else:
                holder.pop("english")
    if (name, u["ref"]) in OVERRUN and u.get("english"):
        u.setdefault("meta", {})["english_misaligned"] = u["english"]
        u["english"] = None
        log.append("overrun")
    return log


def main():
    for f in sorted(glob.glob(str(ROOT / "*/*.json"))):
        d = json.loads(open(f, encoding="utf-8").read())
        name = f.rsplit("/", 1)[1][:-5]
        changed = [(u["ref"], l) for u in d["units"] if (l := clean_unit(u, name))]
        if changed:
            open(f, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
            print(name, len(changed))


if __name__ == "__main__":
    main()
