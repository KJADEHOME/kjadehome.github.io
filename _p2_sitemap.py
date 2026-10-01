#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""sitemap.xml 对账：扫描全站 html，把缺登记的一律补进 sitemap（按 loc 去重、排序、输出合法 XML）。

用法：python _p2_sitemap.py [--check]
      --check 只报告不写入（CI/回归用）
"""
import io, os, re, datetime, sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = "https://www.kjadehome.com"
EXCLUDE_MARK = ('noindex',)


def discover():
    """返回需要收录的页面：根 + blog/ 下所有 html。"""
    out = []
    for d, prefix in ((ROOT, ""), (os.path.join(ROOT, "blog"), "blog")):
        for f in sorted(os.listdir(d)):
            if not f.endswith(".html"):
                continue
            p = os.path.join(d, f)
            s = io.open(p, encoding="utf-8", errors="ignore").read()
            low = s.lower()
            if any(m in low for m in EXCLUDE_MARK):
                continue
            if f.startswith("_") or f.startswith("blog-template"):
                continue
            out.append("%s/%s%s" % (BASE, prefix + "/" if prefix else "", f))
    return out


def build(locs):
    today = datetime.date.today().isoformat()
    rows = []
    for loc in sorted(set(locs)):
        is_home = loc.rstrip("/") == BASE
        rows.append("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
                    "    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n  </url>"
                    % (loc, today, "weekly" if is_home else "monthly",
                       "1.0" if is_home else "0.8"))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(rows) + "\n</urlset>\n")


P = os.path.join(ROOT, "sitemap.xml")
check_only = "--check" in sys.argv

have = set()
if os.path.exists(P):
    try:
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        have = {x.text for x in ET.parse(P).getroot().iter(ns + "loc")}
    except Exception as e:
        print("sitemap 当前不可解析，将整体重建: %s" % e)

want = discover()
missing = [u for u in want if u not in have]
extra = sorted(u for u in have if u not in set(want))

print("sitemap 现有 %d 条 / 应收录 %d 条" % (len(have), len(want)))
for u in want:
    flag = "OK  " if u in have else "MISS"
    if u in missing:
        print("  [%s] %s" % (flag, u))
for u in extra:
    print("  [多余] %s" % u)

if not check_only:
    allu = sorted(set(have) | set(want))
    io.open(P, "w", encoding="utf-8", newline="").write(build(allu))
    # 写后自验
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    after = {x.text for x in ET.parse(P).getroot().iter(ns + "loc")}
    bad = [u for u in want if u not in after]
    print("写出 %d 条；回读校验 %s" % (len(after), "通过（无缺失）" if not bad else "失败 %s" % bad))
    sys.exit(1 if bad else 0)
else:
    sys.exit(1 if missing else 0)
