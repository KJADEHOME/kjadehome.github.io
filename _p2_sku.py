# -*- coding: utf-8 -*-
"""
P2: 建 SKU 级落地页。

背景：ceramic(151) / glass(56) / acrylic(25) 共 232 张图全堆在一个 gallery 页里，
double wall glass tumbler manufacturer 这类 B2B 长尾词没有任何页面承接 —— 这是
曝光上不去的根因。本脚本产出 6 个 SKU 落地页，每页有：专属图集 / 规格表 /
品类卡片 / 定制段 / FAQ(+FAQPage schema) / Product+Breadcrumb schema / 页内询价表单 /
跨 SKU 互链。

所有页面复用 ceramic-decor.html 的 <style>、footer、GA4 片段，保证视觉与既有交付一致。
图集从对应主品类页的现有 gallery 按序抽取（沿用站主对这批图的命名口径），
caption / alt 用中性表述，避免出现无法核实的形态断言。
"""
import os, re, io, json, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = "https://www.kjadehome.com"
EMAIL = "bonnie@kjadehome.com"
GA = "G-1XM8EP6HP5"
YEAR = "2026"
TODAY = "2026-10-01"

SRC = os.path.join(ROOT, "ceramic-decor.html")
_stylesrc = io.open(SRC, encoding="utf-8").read()
STYLE = re.search(r"<style>.*?</style>", _stylesrc, re.S).group(0)
FOOTER = re.search(r'<div class="footer">.*?</div>\s*</div>', _stylesrc, re.S)
FOOTER = FOOTER.group(0) if FOOTER else re.search(r'<div class="footer">.*', _stylesrc, re.S).group(0)


def gallery_imgs(pagefile, n):
    """从主品类页 gallery 里按序取前 n 张，返回 (src, alt, caption) 三元组。"""
    s = io.open(os.path.join(ROOT, pagefile), encoding="utf-8").read()
    srcs = re.findall(r'<figure><img src="([^"]+)"', s)
    out = []
    for i, src in enumerate(srcs[:n]):
        out.append((src, src, "Style %03d" % (i + 1)))
    return out


GA4 = """<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '%s');
</script>""" % (GA, GA)


def ld(obj):
    return '<script type="application/ld+json">\n%s\n</script>' % json.dumps(obj, ensure_ascii=False, indent=2)


def breadcrumb(items):
    """items: [(name, url)] 首项 Home"""
    return ld({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u}
            for i, (n, u) in enumerate(items)
        ]
    })


def product_ld(p):
    props = []
    for k, v in p["specs"]:
        props.append({"@type": "PropertyValue", "name": k, "value": v})
    return ld({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": p["prodname"],
        "sku": p["sku"],
        "image": [BASE + "/" + s for s, _, _ in p["imgs"]],
        "description": p["desc_meta"],
        "brand": {"@type": "Brand", "name": "KJadeHome"},
        "manufacturer": {"@type": "Organization", "name": "KJadeHome"},
        "countryOfOrigin": "CN",
        "additionalProperty": props,
        "offers": {
            "@type": "Offer",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
            "url": BASE + "/" + p["file"],
            "seller": {"@type": "Organization", "name": "KJadeHome"},
            "eligibleQuantity": {"@type": "QuantitativeValue", "minValue": 500, "unitText": "pcs"}
        }
    })


def faq_ld(p):
    return ld({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a}
            } for q, a in p["faq"]
        ]
    })


def head(p):
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%s</title>
<meta name="description" content="%s">
%s
""" % (p["title"], p["desc_meta"], STYLE)


def social(p):
    return """<!-- align-seo:social -->
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:image" content="%s/images/og-share.jpg">
<meta property="og:url" content="%s/%s">
<meta property="og:type" content="website">
<meta property="og:site_name" content="KJadeHome">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%s">
<meta name="twitter:description" content="%s">
<meta name="twitter:image" content="%s/images/og-share.jpg">
<meta name="robots" content="index,follow">
<link rel="canonical" href="%s/%s">
""" % (p["title"], p["desc_meta"], BASE, BASE, p["file"],
       p["title"], p["desc_meta"], BASE, BASE, p["file"])


def body(p):
    crumbs = [("Home", BASE + "/"),
              ("Products", BASE + "/products.html"),
              ("Ceramic Mugs", BASE + "/ceramic-decor.html"),
              (p["crumb"], BASE + "/" + p["file"])] if p["pool"] == "ceramic" else \
             [("Home", BASE + "/"),
              ("Products", BASE + "/products.html"),
              ("Glassware", BASE + "/glass-decor.html"),
              (p["crumb"], BASE + "/" + p["file"])] if p["pool"] == "glass" else \
             [("Home", BASE + "/"),
              ("Products", BASE + "/products.html"),
              ("Kitchen Storage", BASE + "/kitchen-storage.html"),
              (p["crumb"], BASE + "/" + p["file"])]

    crumb_html = '<div class="breadcrumb">' + " &rsaquo; ".join(
        '<a href="%s">%s</a>' % (u, n) for n, u in crumbs) + '</div>'

    # alt 必须每张图唯一，否则图片搜索无法区分（早期实现误用了统一 alt_prefix）
    imgs = "".join(
        '<figure><img src="%s" alt="%s %s" loading="lazy" data-full="%s"><figcaption>%s</figcaption></figure>'
        % (s, p["alt_prefix"], c.replace("Style ", ""), s, c) for s, _, c in p["imgs"])

    cards = "".join('<div class="card"><h3>%s</h3><p>%s</p><ul>%s</ul></div>'
                    % (h, t, "".join("<li>%s</li>" % x for x in li)) for h, t, li in p["cards"])

    specs = "".join("<tr><td>%s</td><td>%s</td></tr>" % (k, v) for k, v in p["specs"])
    custom = "".join('<h3>%s</h3><p>%s</p>' % (h, t) for h, t in p["custom"])
    faqs = "".join('<div class="faq"><h4>%s</h4><p>%s</p></div>' % (q, a) for q, a in p["faq"])
    mixhtml = "".join('<a href="%s">%s</a>' % (u, n) for n, u in p["mix"])

    return """</head>
<body>
<div class="header">
<h1>%s</h1>
<p>%s</p>
</div>
%s
<div class="section">
<h2>Product Range</h2>
<div class="grid">%s</div>
<p style="color:#666;margin-top:14px;">Looking for the full range? Browse the complete
<a href="%s" style="color:#C9A86A;font-weight:600;">%s gallery</a> with model numbers and spec sheets.</p>
</div>

<div class="section" style="background:#f8f9fa;">
<h2>Product Gallery</h2>
<p class="gcount">%d models shown in this series &mdash; click any photo to enlarge. Full model list with dimensions available on request.</p>
<div class="gallery">%s</div>
</div>

<div class="section">
<h2>Technical Specifications</h2>
<div class="specs"><table>%s</table></div>
</div>

<div class="section" style="background:#f8f9fa;">
<h2>Make It Your Brand</h2>
%s
</div>

<div class="section">
<h2>Related Ranges We Produce</h2>
<p style="color:#555;margin-top:0;">All lines share the same BSCI audited production base, and we can consolidate several categories into one container.
%s</p>
<p style="margin:18px 0 0;">Main ranges: <a href="ceramic-decor.html" style="color:#C9A86A;font-weight:600;">ceramic mugs</a> &middot;
<a href="glass-decor.html" style="color:#C9A86A;font-weight:600;">glassware</a> &middot;
<a href="kitchen-storage.html" style="color:#C9A86A;font-weight:600;">kitchen storage</a> &middot;
<a href="products.html" style="color:#C9A86A;font-weight:600;">all products</a></p>
</div>

<div class="section" style="background:#f8f9fa;">
<h2>Frequently Asked Questions</h2>
%s
</div>

<div class="section">
<div class="cta-box">
<h3 style="color:#0B1F3A;font-size:24px;">Request a Quote for This Range</h3>
<p style="color:#666;margin-bottom:22px;">MOQ 500 pcs per design &middot; 30-45 day production &middot; FOB / CIF / DDP &middot; reply within 24 hours</p>
<form class="quick-quote" method="POST" action="https://formsubmit.co/%s" target="_blank">
<input type="hidden" name="_subject" value="Quick quote request: %s">
<div class="hp" aria-hidden="true"><label>Leave empty<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
<input type="text" name="name" placeholder="Your name *" required>
<input type="email" name="email" placeholder="Business email *" required>
<select name="quantity" required>
<option value="">Estimated quantity *</option>
<option value="500-1000">500 - 1,000 pcs</option>
<option value="1000-5000">1,000 - 5,000 pcs</option>
<option value="5000+">5,000+ pcs</option>
</select>
<textarea name="message" placeholder="Sizes, finishes, colours, target market or deadline?"></textarea>
<button type="submit">Send Quote Request &rarr;</button>
<p class="qnote">Prefer email? Write to <a href="mailto:%s">%s</a></p>
</form>
</div>
</div>

%s
<script src="float-buttons.js"></script>
<script>
document.addEventListener('submit', function (e) {
  if (e.target && e.target.classList && e.target.classList.contains('quick-quote')) {
    if (typeof gtag === "function") {
      gtag("event", "inquiry_submit", { event_category: "lead", event_label: "%s", value: 1 });
    }
  }
});
</script>
%s
</body>
</html>
""" % (p["h1"], p["h1_sub"], crumb_html, cards, BASE + "/" + p["poolpage"], p["poolname"],
       len(p["imgs"]), imgs, specs, custom, mixhtml, faqs,
       EMAIL, p["crumb"], EMAIL, EMAIL,
       faq_ld(p), "sku:" + p["file"], FOOTER)


def build(p):
    html = head(p) + social(p) + "\n" + GA4 + "\n" + faq_ld(p) + "\n" + breadcrumb(
        [("Home", BASE + "/"), ("Products", BASE + "/products.html"),
         (p["poolname"], BASE + "/" + p["poolpage"]),
         (p["crumb"], BASE + "/" + p["file"])]) + "\n" + product_ld(p) + "\n" + body(p)
    path = os.path.join(ROOT, p["file"])
    io.open(path, "w", encoding="utf-8", newline="").write(html)
    return path, len(html)


# ---------------------------------------------------------------- 页面数据
POOL = {
    "ceramic": ("ceramic-decor.html", "Custom Ceramic Mug Manufacturer", 12),
    "glass": ("glass-decor.html", "Double-Wall Glassware", 12),
    "acrylic": ("kitchen-storage.html", "Acrylic Kitchen Storage", 10),
}

COMMON_MIX = [
    ("custom ceramic mugs", "/ceramic-mug-manufacturer.html"),
    ("stoneware tableware", "/stoneware-tableware-manufacturer.html"),
    ("double wall glass tumblers", "/double-wall-glass-tumbler.html"),
    ("glass water glasses", "/glass-water-glasses-manufacturer.html"),
    ("acrylic spice jars", "/acrylic-spice-jar-manufacturer.html"),
    ("acrylic kitchen organisers", "/acrylic-kitchen-organiser.html"),
]
MIX = [(n, BASE + u) for n, u in COMMON_MIX]

PAGES = []

# --- 1. 陶瓷马克杯 -------------------------------------------------------
PAGES.append(dict(
    file="ceramic-mug-manufacturer.html",
    pool="ceramic", poolpage="ceramic-decor.html", poolname="Custom Ceramic Mug Manufacturer",
    crumb="Ceramic Mug Manufacturer",
    title="Ceramic Mug Manufacturer | Wholesale Coffee Mugs | KJadeHome",
    desc_meta="Custom ceramic mug manufacturer. Glazed, speckled and printed mugs with private label. MOQ 500 pcs, 30-45 day production. Request a quote today.",
    prodname="Custom Ceramic Mugs (Private Label)",
    sku="KJH-CER-001",
    alt_prefix="Ceramic mug OEM range - style",
    h1="Custom Ceramic Mug Manufacturer",
    h1_sub="Wholesale and private-label coffee mugs from a BSCI audited ceramic line. MOQ 500 pcs, 30-45 day production, FDA and Prop 65 reports available.",
    cards=[
        ("Classic Glazed Mugs", "Everyday coffee and tea mugs in 250-450ml, round and tapered bodies with comfortable handle shapes.",
         ["250ml / 350ml / 450ml capacities", "Lead-free glaze, food-safe", "Glossy, matte and reactive finishes"]),
        ("Speckled &amp; Textured Mugs", "Speckled and reactive-glaze mugs that read as handmade on shelf, popular in cafe and gift retail.",
         ["Speckled, terracotta and volcanic glazes", "Raised texture and embossed bodies", "Food-safe and dishwasher tested"]),
        ("Cork-Base &amp; Gift Mugs", "Mugs with cork or silicone bases, gift-boxed for seasonal and corporate programmes.",
         ["Cork, silicone and wooden coaster bases", "Gift box, sleeve and ribbon packing", "Seasonal and limited-run shapes"]),
    ],
    specs=[("Material", "High-white ceramic stoneware"),
           ("Capacity", "250ml / 300ml / 350ml / 450ml"),
           ("Surface", "Glazed, matte, speckled, reactive, embossed"),
           ("Logo", "Inside / outside / full-wrap print, decal or per-colour"),
           ("MOQ", "500 pcs per design"),
           ("Lead time", "30-45 days after sample approval"),
           ("Certification", "FDA, Prop 65, LFGB reports on request"),
           ("Packing", "Bubble wrap + master carton, drop tested")],
    custom=[("Shape, Size and Glaze", "Choose from existing moulds or develop a new shape. We quote tooling separately for custom bodies. Send a reference photo and we come back with comparable options."),
            ("Private Label and Packaging", "Decal printing, underglaze colour separation, retail gift box, shrink sleeve and hangtag. Barcode and retail labelling done in-house."),
            ("Consolidation and Shipping", "Mugs ship from the same base as glassware and kitchen storage, so one order can fill one container across categories.")],
    faq=[("What is the MOQ for custom ceramic mugs?", "MOQ is 500 pieces per design. You may mix colours within the same design. Volume pricing improves from 3,000 pieces."),
         ("Can you print our logo on the mugs?", "Yes. Send vector artwork (AI or PDF) and we produce a print proof first. Inside print, outside print and full-wrap print are all available."),
         ("Do you have food-contact compliance reports?", "We use food-safe lead-free glazes and can supply FDA, California Prop 65 and LFGB test reports from accredited third-party labs."),
         ("Can I mix different mug styles in one container?", "Yes. Mixed styles and categories in a single container are supported, which lowers your per-unit shipping cost.")],
))

# --- 2. 粗陶餐具 ---------------------------------------------------------
PAGES.append(dict(
    file="stoneware-tableware-manufacturer.html",
    pool="ceramic", poolpage="ceramic-decor.html", poolname="Custom Ceramic Mug Manufacturer",
    crumb="Stoneware Tableware Manufacturer",
    title="Stoneware Tableware Manufacturer | Wholesale Bowls | KJadeHome",
    desc_meta="Stoneware and glazed tableware manufacturer. Bowls, plates and serveware from 8-40cm. MOQ 500 pcs, 30-45 days, FDA and Prop 65 reports.",
    prodname="Stoneware Tableware Bowls &amp; Plates",
    sku="KJH-CER-002",
    alt_prefix="Stoneware tableware range - style",
    h1="Stoneware Tableware Manufacturer",
    h1_sub="Wholesale bowls, plates and serveware in glazed stoneware. MOQ 500 pcs, 30-45 day production, FDA and Prop 65 reports available.",
    cards=[
        ("Stoneware Bowls", "Ramen, cereal and serving bowls in 12-20cm, with deep walls and stable bases.",
         ["12cm / 15cm / 18cm / 20cm", "Glazed interior, protective foot ring", "Stackable for retail shelves"]),
        ("Dinner and Side Plates", "Full dinner set plates alongside side plates and dessert plates in matching glazes.",
         ["20cm / 26cm / 28cm diameters", "Matching bowl-and-plate sets", "Round, square and organic shapes"]),
        ("Serveware and Platters", "Oval platters, double-boiled servers and tapas dishes for restaurant and hotel supply.",
         ["Oval, round and split shapes", "Matte and reactive glaze finishes", "Microwave and dishwasher safe"]),
    ],
    specs=[("Material", "Stoneware / porcelain body"),
           ("Diameter", "8cm - 40cm"),
           ("Finish", "Glazed, matte, reactive, embossed"),
           ("Usage", "Microwave and dishwasher safe"),
           ("MOQ", "500 pcs per design"),
           ("Lead time", "30-45 days after sample approval"),
           ("Certification", "FDA, Prop 65, LFGB reports on request"),
           ("Packing", "Foam sleeve + master carton, drop tested")],
    custom=[("Glaze and Shape Development", "Pick from existing moulds or develop new shapes. Reactive and matte glazes are the fastest options for private-label tableware."),
            ("Set Assembly", "We assemble bowls, plates and serveware into retail sets with outer carton and barcode labelling."),
            ("Export Packing", "Tableware is fragile goods, so we use individual foam sleeves plus double-wall master cartons validated by drop testing.")],
    faq=[("Are your bowls microwave and dishwasher safe?", "Yes. Bothstoneware and porcelain bodies are fired to vitrified levels and are tested for microwave and dishwasher use. Test reports are available on request."),
         ("What is the MOQ per design?", "MOQ is 500 pieces per design, and you can mix sizes within the same design. Dinner set components can be mixed in one order."),
         ("Can we develop a proprietary shape?", "Yes. New mould development is quoted separately depending on the body type and annual volume commitment."),
         ("How do you pack fragile tableware for export?", "Each piece gets an individual foam sleeve, then a double-wall master carton. We run drop tests on the carton before bulk production.")],
))

# --- 3. 双层玻璃杯 -------------------------------------------------------
PAGES.append(dict(
    file="double-wall-glass-tumbler.html",
    pool="glass", poolpage="glass-decor.html", poolname="Double-Wall Glassware",
    crumb="Double Wall Glass Tumbler Manufacturer",
    title="Double Wall Glass Tumbler Manufacturer | Wholesale | KJadeHome",
    desc_meta="Double wall glass tumbler manufacturer. 250-500ml borosilicate tumblers for hot and cold drinks. MOQ 500 pcs, OEM logo, FDA and LFGB reports.",
    prodname="Double Wall Glass Tumblers",
    sku="KJH-GLS-001",
    alt_prefix="Double wall glass tumbler range - style",
    h1="Double Wall Glass Tumbler Manufacturer",
    h1_sub="Borosilicate double wall tumblers in 250-500ml, hot and cold drinks, for cafes, retail chains and private label. MOQ 500 pcs.",
    cards=[
        ("Straight Tumblers", "Straight-wall tumblers in 300ml and 400ml, the easiest line to ship and stack.",
         ["300ml / 400ml / 500ml", "Borosilicate, thermal shock resistant", "Straight, slightly tapered bodies"]),
        ("Tapered and Shaped Tumblers", "Tapered, ribbed and geometric tumblers that stand out on shelf and in photos.",
         ["Injection-moulded and hand-blown options", "Ribbed, fluted and faceted surfaces", "Matte or glossy external coating"]),
        ("Tumbler Gift Sets", "Two-piece and four-piece glass sets boxed for gifting and seasonal campaigns.",
         ["2-pcs, 4-pcs and 6-pcs sets", "Gift box with insert and barcode", "Matte box, kraft box or sleeve"]),
    ],
    specs=[("Material", "Borosilicate glass / soda-lime glass"),
           ("Capacity", "250ml - 500ml"),
           ("Structure", "Double wall, air gap insulated"),
           ("Temperature", "-20&deg;C to 150&deg;C"),
           ("Logo", "Laser engraving, frosting, decal, colour spray"),
           ("MOQ", "500 pcs per design"),
           ("Lead time", "30-45 days after sample approval"),
           ("Certification", "FDA, LFGB, Prop 65 reports on request")],
    custom=[("Decoration Method", "Laser engraving, frosted satin spray, colour coating and ceramic decal are the four common options. We send a physical sample of each method before mass order."),
            ("Gift Set Configuration", "We pack 2-pcs, 4-pcs and 6-pcs sets with inserts, then apply your barcode and retail labelling."),
            ("Container Consolidation", "Double wall glass ships well together with flat-packed acrylic and ceramic goods in one container.")],
    faq=[("Do double wall tumblers keep drinks hot?", "Yes. The air gap between the two walls slows heat transfer, so a hot drink stays hot noticeably longer and the outer wall stays comfortable to hold. It is insulation, not vacuum sealing."),
         ("Will the outer wall get hot with hot coffee?", "The outer wall stays noticeably cooler than the inner wall, but it is not cold. For very hot fills we recommend a sleeve or cork base."),
         ("Can the tumbler go in the dishwasher?", "Borosilicate glass itself is dishwasher safe, but painted, sprayed or coated exteriors should be hand washed to protect the decoration. We specify this in the packing note."),
         ("What is the MOQ for a custom logo tumbler?", "MOQ is 500 pieces per design with your logo. Decoration setup such as a laser plate or decal screen is quoted separately.")],
))

# --- 4. 玻璃水杯 ---------------------------------------------------------
PAGES.append(dict(
    file="glass-water-glasses-manufacturer.html",
    pool="glass", poolpage="glass-decor.html", poolname="Double-Wall Glassware",
    crumb="Glass Water Glass Manufacturer",
    title="Wholesale Glass Water Glasses | Manufacturer | KJadeHome",
    desc_meta="Glass water glass manufacturer. Soda-lime and borosilicate drinking glasses, 200-500ml, wholesale and private label. MOQ 500 pcs, 30-45 days.",
    prodname="Glass Drinking Water Glasses",
    sku="KJH-GLS-002",
    alt_prefix="Glass drinking glass range - style",
    h1="Glass Water Glass Manufacturer",
    h1_sub="Wholesale drinking glasses in soda-lime and borosilicate glass, 200-500ml, private label from MOQ 500 pcs. FDA and LFGB reports available.",
    cards=[
        ("Everyday Drinking Glasses", "Basic water glasses for hotels, restaurants and supermarket private label.",
         ["200ml / 250ml / 300ml / 350ml", "Soda-lime and borosilicate options", "Straight, tumbler and footed bases"]),
        ("Rock and Whiskey Glasses", "Short heavy-based glasses for spirits, with pressed and faceted patterns.",
         ["180ml / 240ml / 300ml", "Pressed and faceted patterns", "Thick heavy base for balance"]),
        ("Juice and Beverage Glasses", "Tall juice, soda and beer glasses for beverage service and retail packs.",
         ["250ml / 330ml / 450ml", "Straight tapered and footed", "Multi-pack shrink or carton"]),
    ],
    specs=[("Material", "Soda-lime glass / borosilicate glass"),
           ("Capacity", "180ml - 500ml"),
           ("Production", "Machine pressed and machine blown"),
           ("Wall", "Regular wall and heavy wall"),
           ("MOQ", "500 pcs per design"),
           ("Lead time", "30-45 days after sample approval"),
           ("Certification", "FDA, LFGB, Prop 65 reports on request"),
           ("Packing", "Bubble wrap + master carton, drop tested")],
    custom=[("Mould and Pattern", "Existing pressed patterns cover most requests. A new pattern is quoted separately with a tooling fee."),
            ("Retail Packaging", "Bulk carton, shrink pack, multi-pack carton or gift box, with your barcode and labelling applied."),
            ("Mixed Container", "Drinking glass ranges can be combined with tumblers, ceramic mugs and acrylic organiser into one shipment.")],
    faq=[("What is the difference between soda-lime and borosilicate?", "Soda-lime glass is cheaper and fine for cold drinks. Borosilicate resists thermal shock, so it is the safer choice for hot fills and repeated dishwashing."),
         ("What is your MOQ for wholesale glasses?", "MOQ is 500 pieces per design. Mixed designs can share one container to reduce freight per unit."),
         ("Do you provide compliance certificates?", "Yes. FDA food-contact, LFGB and California Prop 65 reports are available from accredited labs."),
         ("How fragile are shipped glasses?", "We pack each glass in bubble wrap with double-wall master cartons and validate the pack with drop testing before bulk production.")],
))

# --- 5. 亚克力香料罐 -----------------------------------------------------
PAGES.append(dict(
    file="acrylic-spice-jar-manufacturer.html",
    pool="acrylic", poolpage="kitchen-storage.html", poolname="Acrylic Kitchen Storage",
    crumb="Acrylic Spice Jar Manufacturer",
    title="Acrylic Spice Jar Manufacturer | Wholesale Canisters | KJadeHome",
    desc_meta="Acrylic spice jar manufacturer. 80-250ml canisters with sealed lids and spoons, acrylic stands and trays. MOQ 500 sets, FDA food-grade.",
    prodname="Acrylic Spice Jars &amp; Canisters",
    sku="KJH-ACL-001",
    alt_prefix="Acrylic spice jar range - style",
    h1="Acrylic Spice Jar Manufacturer",
    h1_sub="Wholesale acrylic spice jars and canisters, 80-250ml, with sealed lids, spoons and display stands. MOQ 500 sets, FDA food-grade material.",
    cards=[
        ("Single Spice Jars", "Individual jars for supermarket shelf packs and bulk refill programmes.",
         ["80ml / 120ml / 180ml / 250ml", "Sifter, shaker or spoon lids", "Clear, frosted and coloured bodies"]),
        ("Jar Sets on Stands", "Three-jar and four-jar sets mounted on an acrylic stand or lazy Susan.",
         ["3-pcs and 4-pcs sets", "Acrylic stand, tray or rotating base", "Colour-coded caps per jar"]),
        ("Oil and Condiment Bottles", "Graduated oil and vinegar bottles with drip-free spouts for the same aisle.",
         ["180ml / 250ml / 320ml", "Drip-free spout and sealed cap", "Private-label sleeve or gift box"]),
    ],
    specs=[("Material", "Food-grade PMMA / PET / PS acrylic"),
           ("Capacity", "80ml - 250ml"),
           ("Lid", "Sifter, shaker, spoon or flip cap"),
           ("Base", "Acrylic stand, tray or lazy Susan"),
           ("MOQ", "500 sets per design"),
           ("Lead time", "30-45 days after sample approval"),
           ("Certification", "FDA food-grade, Prop 65 on request"),
           ("Packing", " Individual polybag + master carton")],
    custom=[("Cap and Lid Choice", "Sifter caps, shaker caps and integrated spoons are tooling options. We send lid samples so you can check the flow before committing."),
            ("Label and Branding", "Laser marking, UV printing and sticker sleeve all work on acrylic. Barcodes and retail labels are applied before dispatch."),
            ("Set Configuration", "We assemble mixed jar sets with stands and inserts, then pack them into your retail carton.")],
    faq=[("Is the acrylic food safe?", "Yes. We use food-grade PMMA or PET resin and can supply FDA food-contact and California Prop 65 reports."),
         ("Can I mix jars and stands in one order?", "Yes. The 500-set MOQ applies per configuration, and jars, lids and stands can be packed as a set under one order number."),
         ("Do spoons fit inside the jars?", "Most 120ml and larger jars take an integrated spoon. For smaller jars we recommend an external spoon lid."),
         ("How do you pack acrylic for export?", "Each piece is individually bagged and separated, then boxed in double-wall cartons. Acrylic scratches easily, so separation is standard.")],
))

# --- 6. 亚克力厨房收纳 ---------------------------------------------------
PAGES.append(dict(
    file="acrylic-kitchen-organiser.html",
    pool="acrylic", poolpage="kitchen-storage.html", poolname="Acrylic Kitchen Storage",
    crumb="Acrylic Kitchen Organiser Manufacturer",
    title="Acrylic Kitchen Organiser Manufacturer | Wholesale | KJadeHome",
    desc_meta="Acrylic kitchen organiser manufacturer. Stackable bins, transparent canisters and countertop organisers for retail. MOQ 500 pcs, 30-45 days.",
    prodname="Acrylic Kitchen Storage Organisers",
    sku="KJH-ACL-002",
    alt_prefix="Acrylic kitchen organiser range - style",
    h1="Acrylic Kitchen Organiser Manufacturer",
    h1_sub="Wholesale stackable acrylic organisers, transparent canisters and countertop storage for kitchen retail and supermarket private label.",
    cards=[
        ("Stackable Storage Bins", "Interlocking bins that stack in pantries and refrigerator doors.",
         ["Medium, large and extra-large", "Stackable and interlocking lips", "Clear, frosted and tinted"]),
        ("Transparent Canisters", "Visible pantry canisters for cookies, cereals and dry goods.",
         ["600ml - 2L capacities", "Sealed domed or flip lids", "Set of 3 and set of 5"]),
        ("Countertop Organisers", "Spice racks, holder trays and toothpick boxes for the counter.",
         ["3-tier and 4-tier racks", "Acrylic, bamboo and metal bases", "Retail box packing"]),
    ],
    specs=[("Material", "Food-grade PMMA / PET / PS acrylic"),
           ("Size", "From 10cm to 32cm"),
           ("Structure", "Stackable, interlocking, open-top"),
           ("Colour", "Clear, frosted, amber, opaque"),
           ("MOQ", "500 pcs per design"),
           ("Lead time", "30-45 days after sample approval"),
           ("Certification", "FDA food-grade, Prop 65 on request"),
           ("Packing", " Individual polybag + master carton")],
    custom=[("Mould and Size", "Existing moulds cover most shelf and bin sizes. New tooling is quoted by volume."),
            ("Branding", "Laser logo, UV print and sticker sleeve. Retail barcode and hangtag applied in-house."),
            ("Retail Ready Packing", "We pack sets into your retail carton with inserts, so the goods arrive shelf-ready.")],
    faq=[("Is the acrylic clear enough for retail display?", "We use high-transmission PMMA for display-grade clarity. Frosted and tinted variants are available when you want a softer look."),
         ("Can these bins go in the dishwasher?", "Hand wash is recommended. Acrylic withstands low-temperature wash cycles but can cloud under prolonged high heat."),
         ("What is the MOQ for a custom size?", "MOQ is 500 pieces per size using existing moulds. New mould tooling is quoted separately."),
         ("Do you pack sets for retail?", "Yes. Sets are assembled with inserts and packed into retail cartons with your barcode and labelling.")],
))

# 注入图片并生成
for p in PAGES:
    poolfile, poolname, n = POOL[p["pool"]]
    p["imgs"] = gallery_imgs(poolfile, n)
    p["mix"] = MIX
    path, size = build(p)
    print("built %-42s %6d bytes  imgs=%d" % (p["file"], size, len(p["imgs"])))

# ---------------------------------------------------------------- sitemap
sm = io.open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
TODAY_ISO = "2026-10-01"
added = []
for p in PAGES:
    url = BASE + "/" + p["file"]
    if url not in sm:
        added.append(
            '  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n'
            '    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>' % (url, TODAY_ISO))
# 三条主品类页提到 0.9
for u in [BASE + "/ceramic-decor.html", BASE + "/glass-decor.html", BASE + "/kitchen-storage.html", BASE + "/products.html"]:
    sm = re.sub(re.escape(u) + r'</loc>\s*<lastmod>[^<]*</lastmod>',
                u + '</loc>\n    <lastmod>' + TODAY_ISO + '</lastmod>', sm)
if added:
    # 插到最后一个 <url> 块的 </url> 之前，保持 </url></url> 结构完整
    idx = sm.rfind("</url>")
    sm = sm[:idx] + "\n".join(added) + "\n" + sm[idx:]
    io.open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="").write(sm)

print("sitemap updated: +%d urls" % len(added))
