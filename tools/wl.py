import re,html,subprocess,sys,json,time,os
UA='Mozilla/5.0'
def get(url):
    for i in range(4):
        r=subprocess.run(['curl','-sL','-m','60','-A',UA,url],capture_output=True)
        if r.returncode==0 and len(r.stdout)>2000: return r.stdout.decode('utf-8','replace')
        time.sleep(2)
    return None
def toc(slug):
    t=get(f'https://www.wisdomlib.org/hinduism/book/{slug}')
    seen=[];
    for m in re.finditer(r'<a href="(/hinduism/book/[^"]+/d/doc(\d+)\.html)">(.*?)</a>',t,re.S):
        if m.group(2) not in [s[0] for s in seen]: seen.append((m.group(2),html.unescape(re.sub(r'<[^>]+>','',m.group(3))).strip(),m.group(1)))
    return t,seen
def page_text(url):
    t=get(url)
    if t is None: return None
    m=re.search(r'id="scontent">(.*?)<div class="col-12 mb-3 chapter-dates',t,re.S)
    if not m: return None
    s=m.group(1)
    s=re.sub(r'<br ?/?>','\n',s); s=re.sub(r'</(p|li|blockquote|div|h\d)>','\n',s)
    s=html.unescape(re.sub(r'<[^>]+>','',s))
    return [l.strip() for l in s.split('\n') if l.strip()]
