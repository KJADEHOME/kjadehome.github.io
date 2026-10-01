# -*- coding: utf-8 -*-
"""P1 注入后校验：标签平衡、表单在场、schema 合法、内链回路"""
import io, os, re, json
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.abspath(__file__))
VOID = {"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}

class Check(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.err = []
    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.err.append("多余闭合 </%s>" % tag)
            return
        if self.stack[-1] == tag:
            self.stack.pop()
        else:
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.err.append("未闭合 <%s>" % self.stack.pop())
                if self.stack:
                    self.stack.pop()
            else:
                self.err.append("孤立闭合 </%s>" % tag)

PAGES = ["index.html", "products.html", "ceramic-decor.html", "glass-decor.html",
         "kitchen-storage.html", "inquiry.html", "blog/ceramic-mug-moq-guide.html",
         "blog/bsci-certification-guide.html", "about.html"]

print("=== 1) HTML 标签平衡 ===")
for f in PAGES:
    p = os.path.join(ROOT, f)
    if not os.path.exists(p):
        print("  MISS", f); continue
    c = Check(); c.feed(io.open(p, encoding="utf-8").read())
    bad = c.err + ["残留 <" + t for t in c.stack]
    print("  %-36s %s" % (f, "OK" if not bad else "⚠ " + "; ".join(bad[:4])))

print("\n=== 2) 三产品页：快速询价表单 + GA4 打点 + schema ===")
for f in ["ceramic-decor.html", "glass-decor.html", "kitchen-storage.html"]:
    s = io.open(os.path.join(ROOT, f), encoding="utf-8").read()
    print("  %-22s 表单=%s 打点=%s Breadcrumb=%s Product=%s" % (
        f,
        "quick-quote" in s,
        "inquiry_submit" in s,
        '"BreadcrumbList"' in s,
        '"@type": "Product"' in s,
    ))

print("\n=== 3) 内链回路（每页出链到另外两个产品页） ===")
for f in ["ceramic-decor.html", "glass-decor.html", "kitchen-storage.html"]:
    s = io.open(os.path.join(ROOT, f), encoding="utf-8").read()
    hits = [x for x in ["ceramic-decor.html", "glass-decor.html", "kitchen-storage.html"]
            if x in s]
    print("  %-22s 引用 %d/3 个兄弟页: %s" % (f, len(hits), ", ".join(hits)))

print("\n=== 4) blog 正文链到产品页 ===")
for f in ["blog/ceramic-mug-moq-guide.html", "blog/bsci-certification-guide.html"]:
    s = io.open(os.path.join(ROOT, f), encoding="utf-8").read()
    n = len(re.findall(r'kjadehome\.com/(ceramic|glass|kitchen)-decor\.html|kitchen-storage\.html', s))
    print("  %-36s %d 个产品页链接" % (f, n))

print("\n=== 5) 全站 JSON-LD 合法性 ===")
bad = 0
for dp, _, fns in os.walk(ROOT):
    if ".git" in dp or ".workbuddy" in dp:
        continue
    for fn in fns:
        if not fn.endswith(".html"):
            continue
        p = os.path.join(dp, fn)
        txt = io.open(p, encoding="utf-8", errors="ignore").read()
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', txt, re.S):
            try:
                json.loads(m.group(1))
            except Exception as e:
                bad += 1
                print("  INVALID", os.path.relpath(p, ROOT), e)
print("  全站 JSON-LD 非法段数：%d" % bad)

print("\n=== 6) 邮箱口径一致性 ===")
for f in ["index.html", "about.html", "inquiry.html", "ceramic-decor.html"]:
    s = io.open(os.path.join(ROOT, f), encoding="utf-8").read()
    emails = sorted(set(re.findall(r'[\w.\-+]+@[\w\-]+\.[\w.]+', s)))
    emails = [e for e in emails if "formsubmit" not in e and "googletagmanager" not in e
              and "schema.org" not in e and "example.com" not in e]
    print("  %-22s %s" % (f, ", ".join(emails)))
