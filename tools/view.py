import html, json, pathlib, re, subprocess, sys, tempfile

CSS = """
:root{color-scheme:light dark;--bg:#fbfaf7;--fg:#1d1c1a;--mut:#77736b;--line:#ddd8cc}
@media(prefers-color-scheme:dark){:root{--bg:#171614;--fg:#ece8df;--mut:#9a958a;--line:#34312c}}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,sans-serif}
header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:.6rem 1rem;display:flex;gap:1rem;align-items:center;flex-wrap:wrap}
header input{font:inherit;padding:.3rem .5rem;border:1px solid var(--line);background:transparent;color:inherit;border-radius:4px;min-width:14rem}
.u{display:grid;grid-template-columns:7rem 1fr 1fr;gap:1rem;padding:1rem;border-bottom:1px solid var(--line)}
.ref{color:var(--mut);font-size:.85rem;word-break:break-all}
.sk{font-family:"Noto Sans Devanagari","Kohinoor Devanagari","Devanagari MT",serif;font-size:1.2rem;line-height:1.9;white-space:pre-wrap}
.en{white-space:pre-wrap}
.null{color:var(--mut);font-style:italic}
@media(max-width:800px){.u{grid-template-columns:1fr}}
"""

JS = """
const q=document.getElementById('q');
q.addEventListener('input',()=>{const t=q.value.toLowerCase();
document.querySelectorAll('.u').forEach(e=>{e.hidden=t&&!e.textContent.toLowerCase().includes(t)})});
"""


def main():
    path = pathlib.Path(sys.argv[1])
    d = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for u in d["units"]:
        en = html.escape(u.get("english") or "")
        rows.append(f'<div class="u"><div class="ref">{html.escape(u["ref"])}<br>{html.escape(u.get("scope", ""))}</div>'
                    f'<div class="sk">{html.escape(u["sanskrit"])}</div>'
                    f'<div class="en">{en or "<span class=null>no english</span>"}</div></div>')
    page = (f'<!doctype html><meta charset="utf-8"><title>{html.escape(path.stem)}</title><style>{CSS}</style>'
            f'<header><b>{html.escape(path.stem)}</b><input id="q" placeholder="filter by ref or text"><span>{len(rows)} units</span></header>'
            + "".join(rows) + f"<script>{JS}</script>")
    out = pathlib.Path(tempfile.gettempdir()) / f"grantha_{path.stem}.html"
    out.write_text(page, encoding="utf-8")
    subprocess.run(["open", str(out)])
    print(out)


if __name__ == "__main__":
    main()
