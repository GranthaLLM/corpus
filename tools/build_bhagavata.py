import re, html, glob, json
from common import *
from setu import blocks, block_text
from build_upanishads import SETU, SETU_LIC

DEV = str.maketrans("०१२३४५६७८९", "0123456789")
VERSE_NO = re.compile(r"॥\s*([०-९]+)/([०-९]+)/([०-९]+)\s*॥")


def vb_english(canto, ch):
    t = (RAW / "vb" / f"sb_{canto}_{ch}.html").read_text(encoding="utf-8", errors="replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))
    out = {}
    for m in re.finditer(r"Texts? (\d+)(?:\s*[-–]\s*(\d+))? : (.*?)(?= Texts? \d+(?:\s*[-–]\s*\d+)? :| Donate | Previous |$)", txt):
        a = int(m.group(1)); b = int(m.group(2) or a)
        body = re.sub(r"\s*(CHAPTER [A-Z\-]+\s*)+(Canto \d+:.*)?$", "", re.sub(r"\s+", " ", m.group(3)).strip()).strip()
        out[(a, b)] = body
    return out


def setutila_verses(skandha):
    t, c = blocks(RAW / f"set_skandha_{skandha}.json")
    verses, pending, cur = {}, [], None
    ch = 0
    for b in c:
        ct = b["content_type"]
        tx = block_text(b)
        if ct == "Heading2":
            continue
        if ct == "Mula":
            m = VERSE_NO.search(tx)
            if m:
                key = (int(m.group(1).translate(DEV)), int(m.group(2).translate(DEV)), int(m.group(3).translate(DEV)))
                cur = {"key": key, "mula": "\n".join(pending + [tx]), "bh": []}
                pending = []
                verses.setdefault(key, cur)
            else:
                pending.append(tx)
        elif ct == "Sarvamula" and cur is not None:
            cur["bh"].append(tx)
        elif ct in ("Colophon_Mula", "Colophon_Sarvamula"):
            pending = []
    return verses



def _art(m, word, vocative=None):
    s = m.group(0)
    if s.lower().startswith("the "):
        return ("The " if s[0] == "T" else "the ") + word
    before = m.string[:m.start()]
    if vocative and re.search(r"\bO $", before):
        return vocative
    if not before.strip() or re.search(r"([.:;!?\]]|\])\s$", before):
        return "The " + word
    return "the " + word


def _case(s, dst):
    return dst[0].upper() + dst[1:] if s[:1].isupper() else dst


SWAPS = [
    (r"\b(?:[Tt]he )?(?:Supreme |Absolute )?Personality of Godhead, (?=(?:Lord |Śrī |)(?:Śrī )?Kṛṣṇa)", lambda m: "", "'the Supreme Personality of Godhead, Lord Kṛṣṇa' -> 'Lord Kṛṣṇa' (appositive dropped)"),
    (r"\b(?:Śrī )?Sūta Gosvām[iī]\b", lambda m: "Sūta Paurāṇika", "(Śrī) Sūta Gosvāmī -> Sūta Paurāṇika"),
    (r"\b(?:Śrī )?Śukadeva Gosvām[iī]\b", lambda m: "Śukācārya", "(Śrī) Śukadeva Gosvāmī -> Śukācārya"),
    (r"\b([A-ZŚṢ][\wāīūṛṇṭḍśṣṅñḥṁ\-]+) Gosvām[iī]\b", lambda m: m.group(1), "X Gosvāmī -> X"),
    (r"\bŚrīla ", lambda m: "", "Śrīla removed"),
    (r"\bMahārāja (?=[A-ZŚṢ])", lambda m: "King ", "Mahārāja X -> King X"),
    (r"\b(?<!King )([A-ZŚṢ][\wāīūṛṇṭḍśṣṅñḥṁ\-]+) Mahārāja\b", lambda m: "King " + m.group(1), "X Mahārāja -> King X"),
    (r"\bŚrī (?=[A-ZŚṢ])", lambda m: "", "honorific Śrī before a name removed"),
    (r"\b(?:[Tt]he )?(?:Supreme |Absolute )?Personality of Godhead\b", lambda m: _art(m, "Lord", "Lord"), "(the) Supreme Personality of Godhead -> the Lord"),
    (r"\bdevotional service\b", lambda m: "devotion", "devotional service -> devotion"),
    (r"\bliving entit(?:y|ies)\b", lambda m: "living being" if m.group(0).endswith("y") else "living beings", "living entity/entities -> living being(s)"),
    (r"\b(?:[Tt]he )?Supersoul\b", lambda m: _art(m, "Supreme Self", "Supreme Self"), "(the) Supersoul -> the Supreme Self"),
    (r"\b[Dd]emigods?\b", lambda m: _case(m.group(0), "gods" if m.group(0).endswith("s") else "god"), "demigod(s) -> god(s)"),
    (r"\bsense gratification\b", lambda m: "sense enjoyment", "sense gratification -> sense enjoyment"),
    (r"\bfruitive (?:activities|actions|work)\b", lambda m: "actions aimed at results", "fruitive activities -> actions aimed at results"),
    (r"\bspiritual masters?\b", lambda m: "teachers" if m.group(0).endswith("s") else "teacher", "spiritual master(s) -> teacher(s)"),
    (r"\bpure devotees?\b", lambda m: m.group(0).replace("pure ", ""), "pure devotee(s) -> devotee(s)"),
]
FLAGS = ["Kṛṣṇa consciousness", "Godhead", "fruitive", "Absolute Truth", "impersonal", "Vaiṣṇava"]


def clean_en(en):
    if not en:
        return None, [], []
    edits, out = [], en
    for rx, fn, label in SWAPS:
        out, n = re.subn(rx, fn, out)
        if n:
            edits.append({"rule": label, "count": n})
    flags = [f for f in FLAGS if f in out]
    return out, edits, flags


SPEAKER = re.compile(r"^[^:]{2,90}?\b(said|continued|asked|inquired|replied|spoke|stated|declared|narrated|answered|submitted|remarked)\b[^:]{0,40}:")


def setutila_chapter(V, skandha, ch):
    items = sorted((k[2], v) for k, v in V.items() if k[0] == int(skandha) and k[1] == ch)
    out = []
    for n, v in items:
        first = v["mula"].split("\n")[0]
        out.append({"n": n, "mula": v["mula"], "bh": "\n".join(v["bh"]) or None, "spk": bool(re.search(r"उवाच\W*$", first.strip()) and len(first) < 40)})
    return out


def vb_slots(e):
    ent = sorted(e.items())
    return [{"a": a, "b": b, "en": t, "spk": bool(SPEAKER.match(t))} for (a, b), t in ent]


def align(S, E):
    """Pair by verse number; if the number pairing looks length-inconsistent (recensions split verses differently) use length alignment."""
    if not S or not E:
        return [(S, E, "none")]
    pairs = []
    for x in E:
        sv = [v for v in S if x["a"] <= v["n"] <= x["b"]]
        pairs.append((sv, [x]))
    ratios = sorted(len(x["en"]) / max(len(re.sub(r"[^ऀ-ॿ]", "", "".join(v["mula"] for v in sv))), 1) for sv, (x,) in [(p[0], p[1]) for p in pairs] if sv)
    med = ratios[len(ratios) // 2] if ratios else 1
    good = sum(1 for r in ratios if 0.55 * med <= r <= 1.8 * med)
    if ratios and good / len(ratios) >= 0.85 and len(ratios) >= 0.9 * len(E):
        out = [(sv, ev, "number") for sv, ev in pairs if sv]
        used = {v["n"] for sv, ev in pairs for v in sv}
        rest = [v for v in S if v["n"] not in used]
        out += [([v], [], "none") for v in rest]
        out.sort(key=lambda t: t[0][0]["n"])
        return out
    return [(sv, ev, "length") for sv, ev in dp_align(S, E)]


def dp_align(S, E):
    """Gale-Church style monotone alignment by length when counts differ; beads 1-1, 1-2, 2-1, 1-3, 3-1."""
    import math
    ls = [max(len(re.sub(r"[^ऀ-ॿ]", "", v["mula"])), 1) for v in S]
    le = [max(len(x["en"]), 1) for x in E]
    r = sum(le) / max(sum(ls), 1)
    n, m = len(S), len(E)
    INF = 1e18
    cost = [[INF] * (m + 1) for _ in range(n + 1)]
    back = [[None] * (m + 1) for _ in range(n + 1)]
    cost[0][0] = 0
    beads = [(1, 1, 0.0), (1, 2, 0.5), (2, 1, 0.5), (1, 3, 1.0), (3, 1, 1.0), (2, 2, 0.8)]
    for i in range(n + 1):
        for j in range(m + 1):
            if cost[i][j] >= INF:
                continue
            for di, dj, pen in beads:
                ni, nj = i + di, j + dj
                if ni > n or nj > m:
                    continue
                a = sum(ls[i:ni]) * r
                b = sum(le[j:nj])
                c = abs(math.log(b / a)) + pen
                if cost[i][j] + c < cost[ni][nj]:
                    cost[ni][nj] = cost[i][j] + c
                    back[ni][nj] = (i, j)
    if cost[n][m] >= INF:
        return [(S, E)]
    path, i, j = [], n, m
    while (i, j) != (0, 0):
        pi, pj = back[i][j]
        path.append((S[pi:i], E[pj:j]))
        i, j = pi, pj
    return path[::-1]


def build(skandha, vb_chs, offset, title, id_, fname, cite_extra):
    V = setutila_verses(skandha)
    units, stats = [], {"verse": 0, "group": 0, "chapter": 0}
    stats_n = stats_l = 0
    for ch in vb_chs:
        sch = ch + offset
        S = setutila_chapter(V, skandha, sch)
        E = vb_slots(vb_english(skandha, ch))
        groups = align(S, E)
        chapter_level = False
        for sv, ev, how in groups:
            if not sv:
                continue
            mula = "\n".join(v["mula"] for v in sv)
            bh = "\n".join(v["bh"] for v in sv if v["bh"]) or None
            en = "\n".join(f"[Text {x['a']}{'-' + str(x['b']) if x['b'] != x['a'] else ''}] {x['en']}" for x in ev) or None
            if chapter_level:
                kind, ref = "chapter", f"{skandha}.{ch}"
                stats["chapter"] += 1
            elif len(sv) == 1 and len(ev) == 1 and ev[0]["a"] == ev[0]["b"]:
                kind, ref = "verse", f"{skandha}.{ch}.{sv[0]['n']}"
                stats["verse"] += 1
            else:
                kind, ref = ("group", f"{skandha}.{ch}.{sv[0]['n']}-{sv[-1]['n']}") if sv[0]["n"] != sv[-1]["n"] else ("verse", f"{skandha}.{ch}.{sv[0]['n']}")
                stats["group"] += 1
            stats_n += how == "number"
            stats_l += how == "length"
            units.append({"ref": ref, "kind": kind, "sanskrit": mula, "sanskrit_mula": mula, "sanskrit_bhashya": bh,
                          "english": en, "english_clean": clean_en(en)[0], "english_edits": clean_en(en)[1], "english_flags": clean_en(en)[2], "align": how, "vedabase_texts": [f"{x['a']}-{x['b']}" for x in ev]})
    write(fname, dict(
        id=id_, text=title, tradition="Dvaita (Setutila Sanskrit) / Gaudiya (Vedabase English)", commentator=None, script="Devanagari", units=units,
        source_sanskrit={"citation": f"Setutila/Sarvamula skandha_{skandha}.json (Bhagavata verses in the Madhva-tradition text, with Madhva's Bhagavata-tatparya commentary as sanskrit_bhashya)", "url": SETU + f"skandha_{skandha}.json", "license": SETU_LIC},
        source_english={"citation": f"A.C. Bhaktivedanta Swami Prabhupada, Srimad-Bhagavatam, Canto {skandha} translations as published on Vedabase.io (Bhaktivedanta Book Trust). Used instead of the corpus doc's Goswami/Gita Press translation, which would need OCR", "url": "https://vedabase.io/en/library/sb/", "license": "(c) Bhaktivedanta Book Trust; fetched at vedabase.io's 10 s crawl delay for private benchmarking"},
        bundled=False, needs_ocr=False, alignment="by_ref",
        notes=(f"{cite_extra} Sanskrit is verse-only in 'sanskrit' (Setutila mula, speaker lines attached to the verse they introduce); Madhva's commentary blocks are in sanskrit_bhashya and are NOT translated by the English. "
               f"English = Prabhupada's verse translation per Vedabase 'Text' entry, fetched from the chapter pages. Setutila's verse numbers (from its own '॥ s/c/v ॥' marks) were matched to Vedabase 'Text' numbers; a chapter keeps number pairing only if the Sanskrit and English lengths stay proportional for at least 85% of pairs (align='number'; {stats_n} units). In the other chapters (the two recensions split or number some verses differently, e.g. Setutila 11.8.20 = Vedabase Text 21) the whole chapter was aligned by Sanskrit-to-English length with 1-1, 1-2, 2-1 beads (align='length'; {stats_l} units); spot checks were right but errors can accumulate, so filter on align == 'number' for the safest pairs. Units with align='none' have Sanskrit only (no Vedabase text found for that verse, typically the speaker-intro verse 1). A unit with several Sanskrit verses or Vedabase texts is a group. "
               "Prabhupada's translation is interpretive (purport-influenced) rather than literal, so `english` keeps his published wording untouched and `english_clean` is a rule-based neutral variant: only the term swaps listed in english_edits (per unit, with counts) were applied, e.g. '(Supreme) Personality of Godhead' -> 'the Lord', 'devotional service' -> 'devotion', 'living entity' -> 'living being', 'Supersoul' -> 'the Supreme Self', 'demigod' -> 'god', 'sense gratification' -> 'sense enjoyment', 'fruitive activities' -> 'actions aimed at results', 'spiritual master' -> 'teacher', 'pure devotee' -> 'devotee'; honorifics are dropped ('Sūta Gosvāmī' -> 'Sūta Paurāṇika', 'Śukadeva Gosvāmī' -> 'Śukācārya', other 'X Gosvāmī' -> 'X', 'Śrīla' and the honorific 'Śrī' before a name removed; 'Mahārāja X' and 'X Mahārāja' become 'King X'). Nothing was deleted or rewritten beyond these swaps; terms with no neutral equivalent are only listed in english_flags (e.g. 'Kṛṣṇa consciousness'). english_clean is an edit of the source text made for this benchmark, not a published translation; use `english` when citing.")))
    print(fname, len(units), stats)


if __name__ == "__main__":
    build("3", range(25, 34), 1, "Bhāgavata Purāṇa: Kapila's Upadeśa to Devahūti (Skandha 3, chapters 25-33)", "22a", "sahitya/bhagavata_kapila.json",
          "Vedabase SB 3.25-3.33 correspond to Setutila's chapters 26-34 (Setutila numbers one chapter higher in Skandha 3).")
    build("11", range(7, 30), 0, "Bhāgavata Purāṇa: Uddhava Gītā (Skandha 11, chapters 7-29)", "22b", "sahitya/bhagavata_uddhava.json",
          "Vedabase SB 11.7-11.29 correspond to Setutila's chapters 7-29.")
