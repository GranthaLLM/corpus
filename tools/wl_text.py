import re, html
from html.parser import HTMLParser

BLOCK = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "tr", "ul", "ol", "table"}


class Content(HTMLParser):
    def __init__(self, cid="scontent"):
        super().__init__(convert_charrefs=True)
        self.cid, self.depth, self.on = cid, 0, False
        self.out, self.skip = [], 0
        self.stack = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if not self.on:
            if a.get("id") == self.cid:
                self.on, self.depth = True, 1
            return
        if tag in ("br", "img", "hr", "input", "meta", "link"):
            if tag == "br":
                self.out.append("\n")
            return
        self.depth += 1
        cls = a.get("class") or ""
        href = a.get("href") or ""
        skip = tag in ("script", "style") or (tag == "a" and href.startswith("#note")) or (tag == "a" and "backref" in cls)
        self.stack.append((tag, skip))
        if skip:
            self.skip += 1
        if tag in BLOCK:
            self.out.append("\n")

    def handle_endtag(self, tag):
        if not self.on:
            return
        if tag in ("br", "img", "hr", "input", "meta", "link"):
            return
        self.depth -= 1
        if self.stack:
            t, skip = self.stack.pop()
            if skip:
                self.skip -= 1
        if tag in BLOCK:
            self.out.append("\n")
        if self.depth <= 0:
            self.on = False

    def handle_data(self, data):
        if self.on and not self.skip:
            self.out.append(data)


def page_text(h, cid="scontent"):
    p = Content(cid)
    p.feed(h)
    t = "".join(p.out).replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", l).strip() for l in t.split("\n")]
    return [l for l in lines if l]
