# -*- coding: utf-8 -*-
"""P2 生成结果校验：JSON-LD 合法性 / 图片落盘 / title·desc 长度 / 区块完整性 / sitemap 可解析。"""
import os, re, io, json, glob, xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = "https://www.kjadehome.com"
NEW = ["ceramic-mug-manufacturer.html", "stoneware-tableware-manufacturer.html",
       "double-wall-glass-tumbler.html", "glass-water-glasses-manufacturer.html",
       "acrylic-spice-jar-manufacturer.html", "acrylic-kitchen-organiser.html"]

fails, warns = [], []
for f in NEW:
    p = os.path.join(ROOT, f)
    if not os.path.exists(p):
        fails.append("%s: 文件不存在" % f); continue
    s = io.open(p, encoding="utf-8").read()

    # JSON-LD
    for i, m in enumerate(re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)):
        try:
            json.loads(m)
        except Exception as e:
            fails.append("%s: JSON-LD #%d 解析失败 %s" % (f, i, e))
    types = re.findall(r'"@type":\s*"(\w+)"', s)
    for need in ("Product", "BreadcrumbList", "FAQPage"):
        if need not in types:
            fails.append("%s: 缺 %s schema" % (f, need))

    # 区块
    for need in ('class="header"', 'class="breadcrumb"', 'class="gallery"',
                 'class="specs"', 'class="faq"', 'class="quick-quote"',
                 'src="float-buttons.js"', 'G-1XM8EP6HP5', 'class="footer"'):
        if need not in s:
            fails.append("%s: 缺 %s" % (f, need))

    # 图片落盘
    for src in re.findall(r'<figure><img src="([^"]+)"', s):
        if not os.path.exists(os.path.join(ROOT, src)):
            fails.append("%s: 图片缺失 %s" % (f, src))

    # canonical / 自链
    if '<link rel="canonical" href="%s/%s">' % (BASE, f) not in s:
        fails.append("%s: canonical 不正确" % f)

    # title / desc 长度
    t = re.search(r"<title>(.*?)</title>", s).group(1)
    d = re.search(r'<meta name="description" content="(.*?)">', s).group(1)
    if len(t) > 65:
        warns.append("%s: title %d 字符偏长 -> %s" % (f, len(t), t))
    if len(t) < 30:
        warns.append("%s: title 过短 (%d)" % (f, len(t)))
    if len(d) > 160:
        warns.append("%s: desc %d 字符偏长" % (f, len(d)))
    if len(d) < 90:
        warns.append("%s: desc 过短 (%d)" % (f, len(d)))
    print("  %-40s title=%2d desc=%3d  imgs=%2d" % (f, len(t), len(d), len(re.findall(r'<figure>', s))))

# sitemap
sm = io.open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
try:
    root = ET.fromstring(sm)
    locs = [x.text for x in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    print("  sitemap: %d url, 含新页 %d 个" % (len(locs), sum(1 for f in NEW if BASE + "/" + f in locs)))
    for f in NEW:
        if BASE + "/" + f not in locs:
            fails.append("sitemap: 缺 %s" % f)
except Exception as e:
    fails.append("sitemap 解析失败: %s" % e)

# 内链回路：新页之间 + 新页回主品类页
print("\n--- 内链回路 ---")
for f in NEW:
    s = io.open(os.path.join(ROOT, f), encoding="utf-8").read()
    linked = [g for g in NEW if g != f and g in s]
    print("  %-40s -> 同层 %d 个 / 回主品类页 %s" % (f, len(linked),
          [x for x in ("ceramic-decor.html", "glass-decor.html", "kitchen-storage.html") if x in s]))

print("\n=== FAILS (%d) ===" % len(fails))
for x in fails: print("  x " + x)
print("=== WARNS (%d) ===" % len(warns))
for x in warns: print("  ! " + x)
print("OK" if not fails else "FAILED")
