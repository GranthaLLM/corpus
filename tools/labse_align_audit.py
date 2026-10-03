"""LaBSE alignment audit. Needs sentence-transformers; not part of the build.
embed(): writes per-file Sanskrit and english embeddings. runs(): flags stretches where english sits 1-3 units off (window mean similarity). align(): monotone DP re-pairing used for the Bhagavata files."""
import json,glob,numpy as np,sys
from sentence_transformers import SentenceTransformer
m=SentenceTransformer('sentence-transformers/LaBSE',device='mps'); m.max_seq_length=128
R="/Users/anirudh/Projects/GranthaLLM/corpus/"
out={}
for f in sorted(glob.glob(R+"*/*.json")):
    d=json.load(open(f))
    if not isinstance(d,dict) or "units" not in d or "bhatta" in f: continue
    U=d["units"]
    s=m.encode([u["sanskrit"][:350] for u in U],batch_size=64,normalize_embeddings=True)
    e=m.encode([u["english"][:350] for u in U],batch_size=64,normalize_embeddings=True)
    k=f[len(R):]
    np.save("/tmp/labse/"+k.replace("/","__")+".s.npy",s);np.save("/tmp/labse/"+k.replace("/","__")+".e.npy",e)
    print(k,len(U),flush=True)

# ---- dp
import json,numpy as np,sys
R="/Users/anirudh/Projects/GranthaLLM/corpus/"
def align(M,band=12,base=0.12,gs=0.12,ge=0.03):
    n,m=M.shape; NEG=-1e9
    D=np.full((n+1,m+1),NEG); B=np.zeros((n+1,m+1),dtype=np.int8)
    D[0,0]=0
    for j in range(1,min(m,band)+1): D[0,j]=-ge*j; B[0,j]=2
    for i in range(1,n+1):
        for j in range(max(0,i-band),min(m,i+band)+1):
            best,b=NEG,0
            if D[i-1,j]>NEG: best,b=D[i-1,j]-gs,1
            if j>0 and D[i,j-1]>NEG and D[i,j-1]-ge>best: best,b=D[i,j-1]-ge,2
            if j>0 and D[i-1,j-1]>NEG:
                v=D[i-1,j-1]+M[i-1,j-1]-base
                if v>best: best,b=v,0
            D[i,j],B[i,j]=best,b
    i,j=n,m
    if D[i,j]<=NEG/2:
        j=int(np.argmax(D[n]))
    pairs={}
    while i>0 or j>0:
        b=B[i,j]
        if i>0 and j>0 and b==0: pairs[i-1]=j-1; i-=1;j-=1
        elif i>0 and b==1: i-=1
        elif j>0: j-=1
        else: break
    return pairs
# ---- offset runs
import json,glob,numpy as np
R="/Users/anirudh/Projects/GranthaLLM/corpus/"
W=5;K=3;res={}
for f in sorted(glob.glob(R+"*/*.json")):
    k=f[len(R):]
    try: S=np.load("/tmp/labse/"+k.replace("/","__")+".s.npy");E=np.load("/tmp/labse/"+k.replace("/","__")+".e.npy")
    except: continue
    U=json.load(open(f))["units"];n=len(U)
    if n<W+2*K: continue
    M=S@E.T
    diag={o:np.array([M[i,i+o] if 0<=i+o<n else np.nan for i in range(n)]) for o in range(-K,K+1)}
    flagged=[]
    for i in range(0,n-W+1):
        sc={o:np.nanmean(diag[o][i:i+W]) if not np.isnan(diag[o][i:i+W]).all() else -9 for o in diag}
        best=max(sc,key=sc.get)
        if best!=0 and sc[best]>sc[0]+0.06: flagged.append((i,best,round(sc[0],2),round(sc[best],2)))
    # merge consecutive windows
    runs=[]
    for t in flagged:
        if runs and t[0]<=runs[-1][1]+1 and t[1]==runs[-1][2]: runs[-1][1]=t[0]+W-1
        else: runs.append([t[0],t[0]+W-1,t[1]])
    res[k]=[(U[a]["ref"],U[b]["ref"],o) for a,b,o in runs]
    print(k,n,len(runs),sum(b-a+1 for a,b,o in runs))
json.dump(res,open("/tmp/labse/runs.json","w"))
