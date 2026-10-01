# -*- coding: utf-8 -*-
"""P1-7: 给三个产品页的图片加 SKU 编号（CM-/GL-/KS-），caption + alt 同步改造。

ceramic-decor.html : CM-001 ... (images/ceramic/)
glass-decor.html   : GL-001 ... (images/glass/)
kitchen-storage.html: KS-001 ... (images/acrylic/)
编号取原图文件名末尾数字，保持与图片文件一一对应。
"""
import io, os, re

ROOT = r"D:\codex\kjadehome-website"
JOBS = [
    ("ceramic-decor.html", "CM", "Custom Ceramic Mug", "custom ceramic mug OEM"),
    ("glass-decor.html",   "GL", "Glassware",          "custom glassware OEM"),
    ("kitchen-storage.html", "KS", "Kitchen Storage",  "kitchen storage OEM"),
]

log = []

for fn, prefix, label, altkw in JOBS:
    p = os.path.join(ROOT, fn)
    s = io.open(p, encoding="utf-8").read()
    orig = s

    # 1) figcaption: "<label> 001" -> "<SKU> · <label>"
    def cap(m):
        num = m.group(1)
        return "<figcaption>%s-%s · %s</figcaption>" % (prefix, num.zfill(3), label)
    s, n1 = re.subn(r"<figcaption>%s (\d+)</figcaption>" % re.escape(label), cap, s)

    # 2) alt: "<Label-ish> OEM manufacturer - style 001" -> "<SKU> <altkw>"
    pat = re.compile(r'alt="[A-Za-z \-]*OEM manufacturer - style (\d+)"')
    def al(m):
        return 'alt="%s-%s %s"' % (prefix, m.group(1).zfill(3), altkw)
    s, n2 = pat.subn(al, s)

    # 3) 在 gallery 前插入"按编号询价"提示
    if "quote-tip" not in s:
        tip = ('<p class="quote-tip" style="background:#f4f7fb;border-left:4px solid #2f6b1f;'
               'padding:10px 14px;margin:0 0 18px;font-size:14px;line-height:1.6">'
               '<strong>How to enquire:</strong> note the style number under each image '
               '(for example <code>%s-012</code>) and send us the list &mdash; '
               'we will confirm material, capacity, MOQ, packaging and lead time for each code.</p>\n'
               % prefix)
        s = s.replace('<div class="gallery">', tip + '<div class="gallery">', 1)

    if s != orig:
        io.open(p, "w", encoding="utf-8", newline="").write(s)
    log.append("%-24s caption=%d alt=%d tip=%s" % (fn, n1, n2, "yes" if "quote-tip" in s else "no"))

io.open(os.path.join(ROOT, "_sku_log.txt"), "w", encoding="utf-8").write("\n".join(log))
print("\n".join(log))
