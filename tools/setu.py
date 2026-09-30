import json,re
DEV=str.maketrans('०१२३४५६७८९','0123456789')
def leafs(node,out,pad=False):
    # returns list of str lines
    if 'text' in node and 'children' not in node:
        out.append((node['text'],pad))
    for c in node.get('children',[]):
        leafs(c,out,pad or bool(node.get('padya')))
def block_text(b):
    lines=[]
    def walk(n,inpad):
        if isinstance(n,dict):
            ip=inpad or bool(n.get('padya'))
            if 'text' in n: lines.append((n['text'],ip))
            for c in n.get('children',[]): walk(c,ip)
    walk(b,False)
    out=''
    prev=None
    for t,ip in lines:
        if not out: out=t
        else: out+=('\n' if (ip or prev) else ' ')+t
        prev=ip
    return out
def blocks(path):
    d=json.load(open(path))
    return d['title'],d['content']
