#!/usr/bin/env python3
"""Check every referenced asset + internal link on the live site.
Run:  python _check_links.py
"""
import re, os, glob
from concurrent.futures import ThreadPoolExecutor
import urllib.request
import ssl

BASE = "https://www.kjadehome.com"
ROOT = os.path.dirname(os.path.abspath(__file__))
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HTML_FILES = []
for pat in ("*.html", "blog/*.html"):
    HTML_FILES += glob.glob(os.path.join(ROOT, pat))

def page_dir(p):
    return os.path.dirname(os.path.relpath(p, ROOT)) or "."

def head(url):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0

def local_ref(value, page_dirname):
    """Convert a relative ref into an absolute live URL, or None if not a local asset."""
    if value.startswith(("http", "mailto:", "tel:", "javascript:", "data:", "//", "#")):
        return None
    return BASE + "/" + os.path.normpath(os.path.join(page_dirname, value)).replace("\\", "/")


jobs = []  # (page, url)
for p in HTML_FILES:
    if "blog-template" in p:
        continue
    html = open(p, encoding="utf-8", errors="ignore").read()
    d = page_dir(p)

    def add(value, page):
        u = local_ref(value, d)
        if u:
            jobs.append((page, u))

    add_basename = os.path.basename(p)
    for m in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\']', html):
        add(m.group(1), add_basename)
    for m in re.finditer(r'href=["\']([^"\']+\.(?:html|pdf|webp|jpg|png))["\']', html):
        add(m.group(1), add_basename)

# also assets schema/og points at
for extra in ["/images/logo.png", "/images/og-share.jpg", "/favicon.ico", "/catalog.pdf"]:
    jobs.append(("(schema/global)", BASE + extra))

jobs = list(dict.fromkeys(jobs))
print(f"Checking {len(jobs)} URLs from {len(HTML_FILES)} pages ...\n")

bad = []
with ThreadPoolExecutor(max_workers=10) as ex:
    results = list(ex.map(lambda j: (j[0], j[1], head(j[1])), jobs))

for page, url, st in results:
    if st != 200:
        bad.append((page, url, st))

bad.sort()
print(f"BROKEN: {len(bad)} of {len(jobs)}  ({len(bad)*100//max(len(jobs),1)}%)\n")
cur = None
for page, url, st in bad:
    if page != cur:
        print(f"-- via {page}")
        cur = page
    print(f"     {st}  {url.replace(BASE,'')}")
print("\nDONE")
