# -*- coding: utf-8 -*-
"""P2b: 给 6 个新 SKU 页补主站入链。
products.html 与首页 Product Categories 是权重入口，三个主品类页是同层导权。
锚定用精确字符串替换，匹配不到直接抛错（不静默通过）。"""
import os, io

ROOT = os.path.dirname(os.path.abspath(__file__))
EMAIL = "bonnie@kjadehome.com"

def rw(fn, pairs):
    p = os.path.join(ROOT, fn)
    s = io.open(p, encoding="utf-8").read()
    for old, new, cnt in pairs:
        n = s.count(old)
        if n != cnt:
            raise SystemExit("ANCHOR MISS [%s] expected %d got %d for:\n%s" % (fn, cnt, n, old[:120]))
        s = s.replace(old, new)
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    print("  %-28s ok" % fn)

# ---------------------------------------------------------------- 1. products.html
MOQ = '<p><strong>MOQ:</strong> 500pcs | <strong>Lead Time:</strong> 30-45 days</p>'
REL_CER = ('<p style="margin-top:10px;font-size:14px;color:#555;">Related pages: '
           '<a href="ceramic-mug-manufacturer.html">ceramic mug manufacturer</a> &middot; '
           '<a href="stoneware-tableware-manufacturer.html">stoneware tableware</a></p>')
REL_GLS = ('<p style="margin-top:10px;font-size:14px;color:#555;">Related pages: '
           '<a href="double-wall-glass-tumbler.html">double wall glass tumbler</a> &middot; '
           '<a href="glass-water-glasses-manufacturer.html">glass water glasses</a></p>')
REL_ACC = ('<p style="margin-top:10px;font-size:14px;color:#555;">Related pages: '
           '<a href="acrylic-spice-jar-manufacturer.html">acrylic spice jars</a> &middot; '
           '<a href="acrylic-kitchen-organiser.html">acrylic kitchen organisers</a></p>')

def insert_after_nth(s, old, news):
    """old 在 s 中按出现顺序，第 i 次出现后依次插入 news[i]（原地累积）。"""
    for i, new in enumerate(news):
        idx = -1
        for _ in range(i + 1):
            idx = s.index(old, idx + 1)
        s = s[:idx + len(old)] + new + s[idx + len(old):]
    return s

_sp = os.path.join(ROOT, "products.html")
_s = io.open(_sp, encoding="utf-8").read()
_s = insert_after_nth(_s, MOQ, [REL_CER, REL_GLS, REL_ACC])  # 卡顺序 Ceramic / Glassware / Kitchen
io.open(_sp, "w", encoding="utf-8", newline="").write(_s)
print("  %-28s ok" % "products.html")

# ---------------------------------------------------------------- 2. index.html 首页权重入口
IDX_CARDS = """
<h2 style="font-size:22px;text-align:center;color:#0B1F3A;margin-top:10px;">Popular Product Lines</h2>
<p style="text-align:center;color:#555;margin:-6px 0 18px;">The lines B2B buyers ask about most &mdash; each carries full specifications, compliance reports and a direct quote form.</p>
<div class="grid">

<div class="card">
<a href="ceramic-mug-manufacturer.html">
<h3>Ceramic Mug Manufacturer</h3>
<p>Glazed, speckled and printed coffee mugs, MOQ 500 pcs, FDA and Prop 65 reports.</p>
</a>
</div>

<div class="card">
<a href="stoneware-tableware-manufacturer.html">
<h3>Stoneware Tableware</h3>
<p>Bowls, plates and serveware from 8-40cm, microwave and dishwasher safe.</p>
</a>
</div>

<div class="card">
<a href="double-wall-glass-tumbler.html">
<h3>Double Wall Glass Tumbler</h3>
<p>Borosilicate tumblers 250-500ml for hot and cold drinks, private label from 500 pcs.</p>
</a>
</div>

<div class="card">
<a href="glass-water-glasses-manufacturer.html">
<h3>Glass Water Glasses</h3>
<p>Drinking glasses in soda-lime and borosilicate, 180-500ml, wholesale and OEM.</p>
</a>
</div>

<div class="card">
<a href="acrylic-spice-jar-manufacturer.html">
<h3>Acrylic Spice Jars</h3>
<p>80-250ml canisters with sifter, shaker and spoon lids, plus display stands.</p>
</a>
</div>

<div class="card">
<a href="acrylic-kitchen-organiser.html">
<h3>Acrylic Kitchen Organisers</h3>
<p>Stackable bins, transparent canisters and countertop racks for retail shelves.</p>
</a>
</div>

</div>
</div>
"""
OLD_IDX = "</div>\n\n<div style=\"text-align:center;margin-top:40px;\">"
if io.open(os.path.join(ROOT, "index.html"), encoding="utf-8").read().count(OLD_IDX) != 1:
    raise SystemExit("ANCHOR MISS [index.html] Product Categories 收尾块不唯一")
rw("index.html", [(OLD_IDX, IDX_CARDS + "</div>\n\n<div style=\"text-align:center;margin-top:40px;\">", 1)])

# ---------------------------------------------------------------- 3. 三个主品类页同层导权
LINK_CER = ('<p style="margin:-8px 0 20px;color:#555;">Looking for a specific line? Go straight to our '
            '<a href="ceramic-mug-manufacturer.html">ceramic mug manufacturer</a> page or '
            '<a href="stoneware-tableware-manufacturer.html">stoneware tableware</a> page for specs and MOQ.</p>')
LINK_GLS = ('<p style="margin:-8px 0 20px;color:#555;">Looking for a specific line? Go straight to our '
            '<a href="double-wall-glass-tumbler.html">double wall glass tumbler</a> page or '
            '<a href="glass-water-glasses-manufacturer.html">glass water glasses</a> page for specs and MOQ.</p>')
LINK_KIT = ('<p style="margin:-8px 0 20px;color:#555;">Looking for a specific line? Go straight to our '
            '<a href="acrylic-spice-jar-manufacturer.html">acrylic spice jar</a> page or '
            '<a href="acrylic-kitchen-organiser.html">acrylic kitchen organiser</a> page for specs and MOQ.</p>')

rw("ceramic-decor.html", [("<h2>Product Range</h2>", "<h2>Product Range</h2>\n" + LINK_CER, 1)])
rw("glass-decor.html", [("<h2>Product Range</h2>", "<h2>Product Range</h2>\n" + LINK_GLS, 1)])
rw("kitchen-storage.html", [("<h2>Product Range</h2>", "<h2>Product Range</h2>\n" + LINK_KIT, 1)])

print("P2b 入链注入完成")
