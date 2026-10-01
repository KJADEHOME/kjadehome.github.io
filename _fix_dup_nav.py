#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Remove duplicated <nav class="nav"> block on blog pages that already carry
the standard inline-styled site nav (same as every root page)."""
import re, pathlib, sys

ROOT = pathlib.Path(r"D:/codex/kjadehome-website")
MARK = "导航栏 - 站点统一组件"
PAT = re.compile(r"\n[ \t]*\n?<nav class=\"nav\">.*?</nav>\n", re.S)

changed, errors = [], []
files = sorted([p for p in ROOT.glob("blog/*.html")] + [p for p in ROOT.glob("*.html")])
for p in files:
    if p.name in ("robots",):
        continue
    s0 = p.read_text(encoding="utf-8")
    s = s0
    has_inline = MARK in s
    n_class = s.count('<nav class="nav">')
    if n_class == 0:
        continue  # no duplicate
    if has_inline:
        # keep the inline nav (used by all root pages), drop the stale template nav
        s, n = PAT.subn("\n", s)
        if n != 1:
            errors.append(f"{p.name}: matched {n} blocks, keep original")
            continue
        # tidy: collapse the blank line left before the remaining nav
        s = s.replace("<!-- ========== 导航栏结束 ========== -->\n\n\n\n",
                      "<!-- ========== 导航栏结束 ========== -->\n\n")
        # fix Blog active link inside /blog/ -> relative
        s = s.replace('href="/blog/" class="active"', 'href="./" class="active"')
    else:
        # only the template nav exists -> keep it but repair absolute Blog href
        s = s.replace('href="/blog/" class="active"', 'href="./" class="active"')
        s = s.replace('<a href="https://www.kjadehome.com">Home</a>',
                      '<a href="../index.html">Home</a>')
        s = s.replace('<a href="https://www.kjadehome.com/products.html">Products</a>',
                      '<a href="../products.html">Products</a>')
        s = s.replace('<a href="https://www.kjadehome.com/about.html">About</a>',
                      '<a href="../about.html">About</a>')
        s = s.replace('<a href="https://www.kjadehome.com/inquiry.html">Get Quote</a>',
                      '<a href="../inquiry.html">Get Quote</a>')
    if s != s0:
        p.write_text(s, encoding="utf-8")
        changed.append(f"{p.relative_to(ROOT)}  (nav blocks before {n_class})")

print("CHANGED:")
for c in changed:
    print("  ", c)
print("ERRORS:", errors or "none")
print("count:", len(changed))
