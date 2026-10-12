"""Move Gambhirananda topic headers and topic intros that leaked into the tail of the previous unit (bsb_shankara)."""
import json,re,sys
from rapidfuzz import fuzz
from common import write
F="philosophical/bsb_shankara.json"
HDR=re.compile(r'\b(?:Topic|TOPIC|Tonic|Tobic)\s*[\d.]+\s*[:\-.]?')
MOVE="""1.1.3 1.1.4 1.1.21 1.1.22 1.1.23 1.3.9 2.1.12 2.1.25 2.1.31 2.2.36 2.3.7 2.3.9 2.3.13 2.3.17 2.4.4 2.4.7 2.4.8 3.1.23 3.2.10 3.2.30 3.3.28 3.3.30 3.3.42 3.3.52 3.3.56 3.3.57 3.3.58 3.3.59 3.4.25 3.4.31 3.4.42 4.1.3 4.1.5 4.1.6 4.1.11 4.1.13 4.1.17 4.2.3 4.2.6 4.2.16 4.3.1 4.3.3 4.3.14 4.4.3 4.4.7 4.4.16""".split()
TITLE={"2.3.7":"Topic 2: ORIGIN OF AIR","3.3.42":"Topic 28: MEDITATIONS ON PRANA AND VAYU","3.3.59":"Topic 35: MEDITATIONS YIELDING WORLDLY RESULTS","1.1.23":"Topic 10: LIGHT","4.3.1":"Topic 2: THE DEPARTING SOUL REACHES AIR AFTER YEAR"}
def fixhdr(s): return re.sub(r'\b(?:Tonic|Tobic|TOPIC)(?=\s*\d)','Topic',s,count=1)
def run(apply):
    d=json.load(open(F));U=d["units"];ix={u["ref"]:i for i,u in enumerate(U)}
    for ref in MOVE:
        i=ix[ref];u=U[i];nx=U[i+1];e=u["english"]
        m=list(HDR.finditer(e))[-1];C=e[m.start():].rstrip();e0=e[:m.start()].rstrip()
        L=nx["english"].split("\n",1)[0]
        C2=C
        cut=max(C.rfind(". ",0),C.rfind("? ",0))
        if cut>0 and len(C)-cut<=330:
            tail=C[cut+2:]
            if fuzz.partial_ratio(L.lower(),tail.lower())>=58 or re.match(r"\s*Ved\w*\s*:",tail) and len(tail)<=200: C2=C[:cut+1]
        if ref in TITLE: C2=TITLE[ref]
        elif len(C2)<160 or C2==C and len(C)<330:
            toks=C2.split();out=[];mm=re.match(r'(?:Topic|TOPIC|Tonic|Tobic)\s*[\d.]+\s*:',C2)
            out=[mm.group(0)] if mm else []
            for t in C2[len(out[0]) if out else 0:].split():
                if re.fullmatch(r"[A-Z][A-Z'’,&.\-]*|No|Do|Soul,?",t): out.append(t)
                else: break
            C2=" ".join(out)
        C2=fixhdr(C2)
        print("   REMOVED:",repr(C[len(C2):][:340]) if C2 in C else "");print(f"{ref}->{nx['ref']} len={len(C)}->{len(C2)} | {C2[:75]!r} ...{C2[-45:]!r}")
        if apply:
            u["english"]=e0
            rest=nx["english"].split("\n",1)
            nx["english"]=rest[0]+"\n"+C2+(" "+rest[1] if len(rest)>1 else "")
            for x in (u,nx):
                p=x.get("parts") or []
                by={q["role"]:q for q in p}
                if "mula" in by and len(p)==2:
                    o=[q for q in p if q["role"]!="mula"][0]
                    f,_,r=x["english"].partition("\n");by["mula"]["english"]=f;o["english"]=r
    if apply: write(F,d)
run("--apply" in sys.argv)
