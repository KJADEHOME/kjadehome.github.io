# -*- coding: utf-8 -*-
"""KJadeHome site technical/SEO audit -> _audit_report.txt"""
import os, re, io, glob, sys

ROOT = r"D:\codex\kjadehome-website"
OUT = os.path.join(ROOT, "_audit_report.txt")
lines = []
def add(s): lines.append(str(s))

def read(p):
    return io.open(p, encoding="utf-8", errors="ignore").read()

files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if ".git" in dirpath: continue
    for fn in filenames:
        if fn.endswith(".html"):
            files.append(os.path.join(dirpath, fn))
files.sort()
add("Total HTML files: %d" % len(files))
add("=" * 78)

for p in files:
    rel = os.path.relpath(p, ROOT).replace("\\", "/")
    s = read(p)
    size = len(s) / 1024.0
    title = re.search(r"<title[^>]*>(.*?)</title>", s, re.S)
    desc = re.search(r'<meta[^>]+name=["\']description["\'][^>]*content=["\']([^"\']*)', s, re.I)
    canon = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']*)', s, re.I)
    h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", s, re.S)
    h2 = re.findall(r"<h2[^>]*>(.*?)</h2>", s, re.S)
    lang = re.search(r'<html[^>]*lang=["\']([^"\']*)', s, re.I)
    viewport = "viewport" in s.lower()
    ga = "G-1XM8EP6HP5" in s or "googletagmanager" in s
    fb = "float-buttons.js" in s
    ld = re.findall(r'application/ld\+json', s)
    ldtypes = re.findall(r'"@type"\s*:\s*"([^"]+)"', s)
    ogimg = bool(re.search(r'og:image', s))
    imgs = re.findall(r"<img[^>]*>", s)
    noalt = [i for i in imgs if not re.search(r'alt=["\'][^"\']+["\']', i)]
    lazy = len([i for i in imgs if "loading=" in i])
    forms = re.findall(r"<form[^>]*>", s)
    fsaction = re.findall(r'formsubmit\.co/([^"\']+)', s)
    internal = re.findall(r'href="(?!http|mailto|tel|#)([^"]+)"', s)
    txt = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    txt = re.sub(r"<style.*?</style>", " ", txt, flags=re.S)
    txt = re.sub(r"<[^>]+>", " ", txt)
    words = len(re.findall(r"[A-Za-z]{3,}", txt))

    add("")
    add("### %s  (%.0f KB, ~%d words)" % (rel, size, words))
    add("  title     : %s" % (title.group(1).strip()[:100] if title else "!! MISSING"))
    add("  desc      : %s" % (("OK len=%d" % len(desc.group(1))) if desc else "!! MISSING"))
    add("  canonical : %s" % (canon.group(1) if canon else "!! MISSING"))
    add("  lang      : %s | viewport: %s" % (lang.group(1) if lang else "!! MISSING", viewport))
    add("  H1 x%d | H2 x%d" % (len(h1), len(h2)))
    add("  GA4/GTM   : %s | float-buttons: %s | og:image: %s" % (ga, fb, ogimg))
    add("  JSON-LD   : %d block(s) types=%s" % (len(ld), sorted(set(ldtypes))[:8]))
    add("  imgs      : %d (no-alt %d, has-loading %d)" % (len(imgs), len(noalt), lazy))
    add("  forms     : %d  endpoint=%s" % (len(forms), sorted(set(fsaction))))
    add("  internal links: %d" % len(internal))
    for h in h1:
        add("    H1> %s" % re.sub(r"<[^>]+>", "", h).strip()[:80])

# global checks
add("")
add("=" * 78)
add("GLOBAL CHECKS")
home = read(os.path.join(ROOT, "index.html"))
add("robots.txt exists: %s" % os.path.exists(os.path.join(ROOT, "robots.txt")))
add("sitemap.xml exists: %s" % os.path.exists(os.path.join(ROOT, "sitemap.xml")))
sm = read(os.path.join(ROOT, "sitemap.xml"))
smurls = re.findall(r"<loc>([^<]+)</loc>", sm)
add("sitemap urls: %d" % len(smurls))
allhtml = {os.path.relpath(p, ROOT).replace("\\", "/") for p in files}
for u in smurls:
    path = u.replace("https://www.kjadehome.com/", "")
    if path.endswith("/"):
        path = path + "index.html"
    if path == "": path = "index.html"
    if path not in allhtml:
        add("  !! sitemap points to missing file: %s" % path)
# pages not in sitemap
for f in sorted(allhtml):
    if f.startswith("_"): continue
    if not any(f == u.replace("https://www.kjadehome.com/", "") or
               (u.replace("https://www.kjadehome.com/", "").rstrip("/") + "/index.html") == f
               for u in smurls):
        add("  ?? page NOT in sitemap: %s" % f)

io.open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print("WROTE", OUT, "lines", len(lines))
