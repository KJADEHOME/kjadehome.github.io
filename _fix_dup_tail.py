#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SKU pages: drop the duplicated tail
   (<script src="float-buttons.js"> + </body></html> + stray </body></html>)
   so each page closes exactly once and the float script is included once."""
import re, pathlib

ROOT = pathlib.Path(r"D:/codex/kjadehome-website")
TARGETS = [
    "acrylic-kitchen-organiser.html",
    "acrylic-spice-jar-manufacturer.html",
    "ceramic-mug-manufacturer.html",
    "double-wall-glass-tumbler.html",
    "glass-water-glasses-manufacturer.html",
    "stoneware-tableware-manufacturer.html",
]

TAIL = re.compile(
    r"(<script src=\"float-buttons\.js\"></script>\s*\n)"
    r"(.*?</body>\s*\n\s*</html>\s*\n?)"
    r"(</body>\s*\n\s*</html>\s*\n?)\s*$",
    re.S,
)

for name in TARGETS:
    p = ROOT / name
    s0 = p.read_text(encoding="utf-8")
    s = s0
    nb, nh = s.count("</body>"), s.count("</html>")
    # collapse duplicated closing tags
    if nb > 1 or nh > 1:
        s = s[: s.rindex("</body>")].rstrip() + "\n</body>\n</html>\n"
    # remove the second (trailing) float-buttons include
    s, n = TAIL.subn(r"\1", s)
    if n != 1:
        print("WARN", name, "tail match", n)
    if s != s0:
        p.write_text(s, encoding="utf-8")
        print(f"{name}: </body> {nb}->{s.count('</body>')}, "
              f"</html> {nh}->{s.count('</html>')}, "
              f"float {s0.count('float-buttons.js')}->{s.count('float-buttons.js')}")
