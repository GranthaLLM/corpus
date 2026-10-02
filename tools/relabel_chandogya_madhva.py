import json, re
from common import *

ORD = {"प्रथम": 1, "द्वितीय": 2, "तृतीय": 3, "चतुर्थ": 4, "पञ्चम": 5, "षष्ट": 6, "षष्ठ": 6, "सप्तम": 7, "अष्टम": 8, "नवम": 9,
       "दशम": 10, "एकादश": 11, "द्वादश": 12, "त्रयोदश": 13}
KHANDAS = {1: 13, 2: 24, 3: 19, 4: 17, 5: 24, 6: 16, 7: 26, 8: 15}


def num(word):
    for k, v in sorted(ORD.items(), key=lambda kv: -len(kv[0])):
        if word.startswith(k):
            return v
    raise ValueError(word)


def main():
    p = ROOT / "upanishads/chandogya_madhva.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    for u in d["units"]:
        m = re.match(r"(\S+)ोऽध्यायः / (\S+?)ः खण्डः$", u["ref"])
        if not m:
            continue
        a, k = num(m.group(1)), num(m.group(2))
        nxt = [x for x in d["units"] if x is not u]
        last = k == KHANDAS[a] or not any(
            (mm := re.match(r"(\S+)ोऽध्यायः / (\S+?)ः खण्डः$", x["ref"])) and num(mm.group(1)) == a and num(mm.group(2)) > k
            for x in nxt)
        u["ref"] = f"{a}.{k}-{KHANDAS[a]}" if last and k < KHANDAS[a] else f"{a}.{k}"
        if "-" in u["ref"]:
            u.setdefault("meta", {})["khandas"] = [a, k, KHANDAS[a]]
    d["notes"] += (" [Refs are adhyaya.khanda. A ref such as 3.5-19 means the Setutila source has no heading after khanda 5, so that unit holds Madhva's"
                   " commentary from khanda 5 to the end of the adhyaya; the source has no Madhva text for khandas 3.1-3.4, 4.1-4.3 and the other khandas below the first heading of each adhyaya, nor for 1.8.]")
    write("upanishads/chandogya_madhva.json", d)
    print([u["ref"] for u in d["units"]])


if __name__ == "__main__":
    main()
