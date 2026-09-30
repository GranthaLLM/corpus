import re,json,glob,os
from common import RAW
DEVRE=re.compile('[ऀ-ॿ]')
def is_dev(l):
    d=len(DEVRE.findall(l)); a=sum(1 for c in l if c.isalpha())
    return d>0 and d>=0.5*max(a,1)
def is_iast_v(l): return (not is_dev(l)) and bool(re.search(r'[|॥]\s*$|[|॥]\s*[\w.\-–/ ]*\s*[|॥]\s*$',l)) and len(l)<400
def verses(lines):
    recs=[];cur=None;pre=[];i=0
    n=len(lines)
    while i<n:
        l=lines[i]
        if is_dev(l):
            if cur is None or cur['_after']:
                cur={'pre':pre[-1] if pre else '', 'dev':[],'iast':[],'rest':[],'_after':False}
                recs.append(cur); pre=[]
            cur['dev'].append(l)
        elif cur is not None and not cur['_after'] and is_iast_v(l):
            cur['iast'].append(l)
        else:
            if cur is not None:
                cur['_after']=True; cur['rest'].append(l)
            else: pre.append(l)
        i+=1
    return recs,pre
def load(book):
    pages=[]
    for p in glob.glob(str(RAW/'wl_cache'/'*.json')):
        d=json.load(open(p))
        if d['book']==book: pages.append(d)
    return sorted(pages,key=lambda d:int(d['id']))
