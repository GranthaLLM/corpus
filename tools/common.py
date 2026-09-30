import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
import os
RAW = pathlib.Path(os.environ.get("GRANTHA_RAW", "raw")).resolve()
GRETIL = "https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/"
MITRA = "https://github.com/dharmamitra/mitrasamgraha-dataset/blob/main/data/train/cc-by-sa/"
GRETIL_LIC = "CC BY-NC-SA 4.0 (GRETIL)"
MITRA_LIC = "CC BY-SA (Mitrasamgraha)"


def write(rel, obj):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    full = {"id": None, "text": None, "tradition": None, "commentator": None, "script": "IAST",
            "units": [], "source_sanskrit": None, "source_english": None, "bundled": False,
            "needs_ocr": False, "alignment": "not_applicable", "slice_of": None, "notes": None}
    full.update(obj)
    p.write_text(json.dumps(full, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return len(full["units"])


def gretil_body(name):
    t = (RAW / name).read_text(encoding="utf-8")
    return t.split("# Text", 1)[1]


def tsv_rows(name, start=0, end=None):
    rows = (RAW / name).read_text(encoding="utf-8").split("\n")
    out = []
    for i, line in enumerate(rows[start:end], start + 1):
        if not line.strip():
            continue
        parts = line.split("\t")
        sa = parts[0].strip() or None
        en = "\t".join(parts[1:]).strip() or None
        out.append((i, sa, en))
    return out
