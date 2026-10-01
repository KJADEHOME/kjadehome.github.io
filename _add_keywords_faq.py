# -*- coding: utf-8 -*-
"""P1-10 / P1-12: 补买家高频词（coffee cup / microwave / dishwasher）+ 产品页到博客的内链"""
import io, os, re, json

ROOT = r"D:\codex\kjadehome-website"
log = []

# ---------- 1. intro 补 coffee cup 等词 ----------
INTRO = [
    ("ceramic-decor.html",
     "<p>Private-label ceramic mugs, speckled &amp; two-tone drinkware for retailers and importers.<br>MOQ 500pcs | 30-45 day production | FOB/CIF/DDP shipping</p>",
     "<p>Private-label ceramic mugs and coffee cups &mdash; speckled &amp; two-tone drinkware for retailers, importers, caf&eacute; chains and gift brands.<br>MOQ 500pcs | 30-45 day production | FOB/CIF/DDP shipping</p>"),
    ("glass-decor.html",
     "<p>Private-label double-wall cups, dry-flower glass, glass teapots and drinkware.<br>MOQ 500pcs | 30-45 day production | FOB/CIF/DDP shipping</p>",
     "<p>Private-label double-wall glass cups, coffee mugs, dry-flower glass, glass teapots and drinkware for caf&eacute;s, hotels and retail.<br>MOQ 500pcs | 30-45 day production | FOB/CIF/DDP shipping</p>"),
]
for fn, old, new in INTRO:
    p = os.path.join(ROOT, fn)
    s = io.open(p, encoding="utf-8").read()
    if old in s:
        s = s.replace(old, new, 1)
        io.open(p, "w", encoding="utf-8", newline="").write(s)
        log.append("intro updated: " + fn)
    else:
        log.append("!! intro pattern not found: " + fn)

# ---------- 2. 加 microwave / dishwasher FAQ（HTML + JSON-LD 同步） ----------
FAQ = [
    ("ceramic-decor.html",
     '<div class="faq"><h4>Q: Are your mugs food-safe and compliant?</h4><p>Yes. Food-contact glazes are used and we can supply FDA, Prop 65 and LFGB test reports from third-party labs.</p></div>',
     '<div class="faq"><h4>Q: Are the mugs microwave and dishwasher safe?</h4><p>Yes, standard food-safe glazes are microwave and dishwasher safe. Metallic lustre, gold rims and hand-applied decals are hand-wash only, and we flag this on the spec sheet for each style.</p></div>',
     '"text": "Yes. Food-contact glazes are used and we can supply FDA, Prop 65 and LFGB test reports from third-party labs."',
     'Are the mugs microwave and dishwasher safe?',
     'Yes, standard food-safe glazes are microwave and dishwasher safe. Metallic lustre, gold rims and hand-applied decals are hand-wash only, and we flag this on the spec sheet for each style.'),
    ("glass-decor.html",
     None, None, None,
     'Are double-wall glasses microwave and dishwasher safe?',
     'Borosilicate double-wall glass is microwave and dishwasher safe. Hand washing is recommended for styles with hand-painted decoration, dried-flower fills or metallic rims.'),
]

for item in FAQ:
    fn = item[0]
    p = os.path.join(ROOT, fn)
    s = io.open(p, encoding="utf-8").read()
    if item[1] and item[1] in s:
        s = s.replace(item[1], item[1] + "\n" + item[2], 1)
        log.append("html faq appended: " + fn)
    q, a = item[4], item[5]
    # JSON-LD: 在 mainEntity 最后一个 Question 后追加
    # 找到最后一个 "acceptedAnswer" 块结束的 "}\n    }\n  ]" 结构
    m = None
    for m in re.finditer(r'\n    \}\n  \]', s):
        pass
    if m:
        ins = ('\n    },\n    {\n      "@type": "Question",\n      "name": "%s",\n'
               '      "acceptedAnswer": {\n        "@type": "Answer",\n        "text": "%s"\n'
               '      }\n    }\n  ]' % (q, a))
        # 需要保留原来的 \n    }\n  ]
        s = s[:m.start()] + ins + s[m.end():]
        io.open(p, "w", encoding="utf-8", newline="").write(s)
        log.append("json faq appended: " + fn)
    else:
        log.append("!! json array end not found: " + fn)

# ---------- 3. 产品页底部加"相关阅读"内链 ----------
LINKS = {
    "ceramic-decor.html": [
        ("https://www.kjadehome.com/blog/ceramic-mug-moq-guide.html", "Custom Ceramic Mugs: MOQ, Pricing &amp; Lead Times Explained"),
        ("https://www.kjadehome.com/blog/bsci-certification-guide.html", "BSCI Certification: What Importers Should Verify"),
        ("https://www.kjadehome.com/how-to-choose-oem-manufacturer.html", "How to Choose a Reliable OEM Manufacturer in China"),
    ],
    "glass-decor.html": [
        ("https://www.kjadehome.com/blog/home-decor-trends-2025.html", "Home Decor Industry Trends 2025: What U.S. Importers Need to Know"),
        ("https://www.kjadehome.com/how-to-choose-oem-manufacturer.html", "How to Choose a Reliable OEM Manufacturer in China"),
    ],
    "kitchen-storage.html": [
        ("https://www.kjadehome.com/blog/consumer-desirability-home-furnishings-2026.html", "How Consumer Psychology Is Reshaping Home Furnishing"),
        ("https://www.kjadehome.com/how-to-choose-oem-manufacturer.html", "How to Choose a Reliable OEM Manufacturer in China"),
    ],
}
for fn, links in LINKS.items():
    p = os.path.join(ROOT, fn)
    s = io.open(p, encoding="utf-8").read()
    if "related-reading" in s:
        log.append("skip related block: " + fn)
        continue
    items = "".join('<li><a href="%s">%s</a></li>' % (u, t) for u, t in links)
    blk = ('<div class="related-reading" style="margin:28px 0;padding:16px 18px;background:#f7f9fc;'
           'border:1px solid #e3e8ef;border-radius:8px">'
           '<h3 style="margin:0 0 8px;font-size:16px">Related reading</h3>'
           '<ul style="margin:0;padding-left:20px;line-height:1.8">' + items + '</ul></div>')
    idx = s.find("</main>")
    anchor = -1
    for tag in ["</main>", '<div class="footer"', "<footer"]:
        anchor = s.find(tag)
        if anchor > 0:
            break
    if anchor > 0:
        s = s[:anchor] + blk + "\n" + s[anchor:]
        io.open(p, "w", encoding="utf-8", newline="").write(s)
        log.append("related links added: " + fn + " (anchor=" + tag + ")")
    else:
        log.append("!! no anchor for related links: " + fn)

# ---------- 校验 JSON ----------
for fn in ["ceramic-decor.html", "glass-decor.html", "kitchen-storage.html"]:
    s = io.open(os.path.join(ROOT, fn), encoding="utf-8").read()
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    bad = 0
    for b in blocks:
        try:
            json.loads(b)
        except Exception as e:
            bad += 1
            log.append("!! BAD JSON %s: %s" % (fn, str(e)[:90]))
    log.append("json check %s: blocks=%d bad=%d" % (fn, len(blocks), bad))

io.open(os.path.join(ROOT, "_kw_log.txt"), "w", encoding="utf-8").write("\n".join(log))
print("\n".join(log))
