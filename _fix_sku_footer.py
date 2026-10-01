#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SKU pages were missing the site footer entirely (CSS existed, markup didn't)."""
import pathlib

ROOT = pathlib.Path(r"D:/codex/kjadehome-website")
TARGETS = [
    "acrylic-kitchen-organiser.html",
    "acrylic-spice-jar-manufacturer.html",
    "ceramic-mug-manufacturer.html",
    "double-wall-glass-tumbler.html",
    "glass-water-glasses-manufacturer.html",
    "stoneware-tableware-manufacturer.html",
]

FOOTER = (
    '\n<!-- Footer -->\n'
    '<div class="footer">\n'
    '<p>© 2026 KJadeHome. All rights reserved.</p>\n'
    '<p>Connect on <a href="https://www.linkedin.com/company/kjadehome" target="_blank">LinkedIn</a> '
    '| Factory: China</p>\n'
    '<p>Multi-category China sourcing by <a href="https://www.masadvp.com">MASA Development International</a> '
    '&mdash; toy, home textile, pet and lifestyle products.</p>\n'
    '</div>\n'
)

ANCHOR = '<script src="float-buttons.js"></script>'
for name in TARGETS:
    p = ROOT / name
    s0 = p.read_text(encoding="utf-8")
    if 'class="footer"' in s0 and '</div>' in s0:
        print("skip", name)
        continue
    s = s0
    n = s.count(ANCHOR)
    if n != 1:
        print("WARN", name, "anchors", n)
        continue
    s = s.replace(ANCHOR, FOOTER + ANCHOR)
    p.write_text(s, encoding="utf-8")
    print(f"{name}: footer injected (float anchors {n})")
