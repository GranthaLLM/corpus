import json, os, subprocess, sys, time, zipfile, io

BASE = "https://api.sarvam.ai/doc-ai/v1/job"


def curl(args):
    r = subprocess.run(["curl", "-sS", "-m", "300"] + args, capture_output=True)
    if r.returncode:
        raise RuntimeError(r.stderr.decode())
    return r.stdout


def digitise(pdf, language="en-IN", fmt="md", out=None):
    key = os.environ["SARVAM_API_KEY"]
    hdr = ["-H", f"api-subscription-key: {key}"]
    resp = json.loads(curl(hdr + ["-F", f"file=@{pdf}", "-F", f"language={language}", "-F", f"output_format={fmt}", BASE + "/digitise"]))
    job = resp["job_id"]
    for _ in range(120):
        st = json.loads(curl(hdr + [f"{BASE}/{job}/status"]))
        if st.get("status") in ("completed", "failed", "partially_completed"):
            break
        time.sleep(3)
    if st.get("status") not in ("completed", "partially_completed"):
        raise RuntimeError(json.dumps(st))
    dl = json.loads(curl(hdr + [f"{BASE}/{job}/download-url"]))
    data = curl(["-L", dl["url"]])
    if out:
        open(out, "wb").write(data)
    return st, data


if __name__ == "__main__":
    pdf, lang, out = sys.argv[1], sys.argv[2], sys.argv[3]
    st, data = digitise(pdf, lang, "md", out)
    print(json.dumps(st.get("usage")), len(data))


def ocr_pages(pdf, first, last, outdir, language="sa-IN", chunk=10):
    """Split pdf pages first..last into <=10 page chunks (API limit), OCR each with Sarvam Vision, save zips in outdir."""
    import glob
    os.makedirs(outdir, exist_ok=True)
    a = first
    while a <= last:
        b = min(a + chunk - 1, last)
        out = os.path.join(outdir, f"chunk_{a}_{b}.zip")
        if not (os.path.exists(out) and os.path.getsize(out) > 1000):
            for f in glob.glob(os.path.join(outdir, "pp*.pdf")):
                os.remove(f)
            subprocess.run(["pdfseparate", "-f", str(a), "-l", str(b), pdf, os.path.join(outdir, "pp%d.pdf")], check=True)
            subprocess.run(["pdfunite"] + [os.path.join(outdir, f"pp{i}.pdf") for i in range(a, b + 1)] + [os.path.join(outdir, f"chunk_{a}_{b}.pdf")], check=True)
            digitise(os.path.join(outdir, f"chunk_{a}_{b}.pdf"), language, "md", out)
        a = b + 1
