import sys, re, pathlib, urllib.request, concurrent.futures as cf


def get(url, out):
    out = pathlib.Path(out)
    if out.exists() and out.stat().st_size > 2000:
        return out.read_text(encoding="utf-8")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for _ in range(3):
        try:
            t = urllib.request.urlopen(req, timeout=40).read().decode("utf-8")
            out.write_text(t, encoding="utf-8")
            return t
        except Exception:
            pass
    return ""


def crawl(base, ids, outdir):
    outdir = pathlib.Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    with cf.ThreadPoolExecutor(6) as ex:
        res = list(ex.map(lambda i: get(f"{base}/d/doc{i}.html", outdir / f"{i}.html"), ids))
    return dict(zip(ids, res))
