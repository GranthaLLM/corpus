import glob, json, pathlib
from common import ROOT, write

PD = "public_domain"
FREE = "free_to_copy_per_author"
CC = "cc_by_sa"
UNC = "in_copyright_or_unclear"

RIGHTS = {
    "bg_madhva": [FREE], "bg_ramanuja": [UNC], "bg_shankara": [PD, UNC], "bhattasangraha": [UNC], "bsb_madhva": [PD, FREE], "bsb_shankara": [UNC],
    "mbtn": [UNC], "samkhyakarika": [CC], "sarvadarshanasamgraha": [CC], "sribhashya_ramanuja": [PD], "tarkasamgraha": [PD], "vimshatika_trimshika": [CC],
    "bhagavata_kapila": [UNC], "bhagavata_uddhava": [UNC], "harivamsha": [CC], "kumarasambhava": [CC], "sanatsujatiya": [CC], "shatakatraya": [PD],
    "vidura_niti": [CC], "yaksha_prashna": [CC],
    "aitareya_madhva": [UNC], "aitareya_shankara": [PD], "brihadaranyaka_madhva": [FREE], "brihadaranyaka_shankara": [UNC], "chandogya_madhva": [PD],
    "chandogya_shankara": [CC], "isa_madhva": [PD], "isa_shankara": [PD], "katha_madhva": [PD, FREE], "katha_shankara": [PD], "kena_madhva": [PD, FREE],
    "kena_shankara": [PD], "mandukya_madhva": [PD], "mandukya_shankara": [UNC], "mundaka_madhva": [PD, FREE, UNC], "mundaka_shankara": [PD],
    "prashna_madhva": [PD], "prashna_shankara": [PD], "taittiriya_madhva": [FREE], "taittiriya_shankara": [PD],
}
KIND = {"bhattasangraha": "summary", "aitareya_madhva": "interpretive", "chandogya_madhva": "interpretive"}


def main():
    for f in sorted(glob.glob(str(ROOT / "*/*.json"))):
        p = pathlib.Path(f)
        d = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(d, dict) or "units" not in d:
            continue
        name = p.stem
        if name not in RIGHTS:
            print("no tag for", name)
            continue
        d["reference_type"] = KIND.get(name, "translation")
        d["english_rights"] = RIGHTS[name]
        write(str(p.relative_to(ROOT)), d)


if __name__ == "__main__":
    main()
