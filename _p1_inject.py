# -*- coding: utf-8 -*-
"""P1 批量注入脚本（可重复执行，幂等：已注入过的页面会跳过）
1. 三产品页：BreadcrumbList + Product schema
2. 三产品页：页内精简询价表单（含 GA4 inquiry_submit 打点）
3. 三产品页 + blog：上下文内链（三座孤岛打通）
4. inquiry.html：读取 ?product= 预填产品线
5. index.html：Organization schema 邮箱统一为 bonnie@kjadehome.com
"""
import io, os, re, json

ROOT = os.path.dirname(os.path.abspath(__file__))
LOG = []

def read(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()

def write(p, s):
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)

def done(name):
    LOG.append("SKIP (already applied): " + name)

# ---------------------------------------------------------------- 页级配置
PAGES = {
    "ceramic-decor.html": {
        "sku": "KJH-CER-001",
        "product_name": "Custom Ceramic Mugs (Private Label)",
        "desc": "Private-label ceramic mugs with glazed, speckled, two-tone and printed finishes. MOQ 500 pcs per design, 30-45 day production, FOB/CIF/DDP.",
        "img": "/images/ceramic/ceramic-001.webp",
        "crumb_h3": "Ceramic Mugs",
        "crumb_prev": "Custom Ceramic Mug Manufacturer",
        "quick_subject": "Quick quote request: Ceramic Mugs",
        "product_param": "ceramic",
    },
    "glass-decor.html": {
        "sku": "KJH-GLS-001",
        "product_name": "Custom Glassware: Double-Wall Cups, Dry-Flower Glass (Private Label)",
        "desc": "Private-label double-wall cups, dry-flower decorated glass, borosilicate teapots and straw cups. MOQ 500 pcs per design, 30-45 day production, FOB/CIF/DDP.",
        "img": "/images/glass/glass-001.webp",
        "crumb_h3": "Glassware",
        "crumb_prev": "Custom Glassware Manufacturer",
        "quick_subject": "Quick quote request: Glassware",
        "product_param": "glass",
    },
    "kitchen-storage.html": {
        "sku": "KJH-KIT-001",
        "product_name": "OEM Kitchen Storage: Spice Jar Sets & Oil Bottles",
        "desc": "Private-label spice jar sets, oil and vinegar bottles, toothpick boxes and acrylic organisers. MOQ 500 pcs per design, 30-45 day production, FOB/CIF/DDP.",
        "img": "/images/kitchen/kitchen-001.webp",
        "crumb_h3": "Kitchen Storage",
        "crumb_prev": "OEM Kitchen Storage Manufacturer",
        "quick_subject": "Quick quote request: Kitchen Storage",
        "product_param": "kitchen-storage",
    },
}

# 三页互链的上下文段落（正文内， Product Gallery 之前）
SIBLING_LINKS = """
<p style="margin:18px 0 0;color:#555;"> exploring other ranges? we also produce <a href="ceramic-decor.html" style="color:#C9A86A;font-weight:600;">custom ceramic mugs</a>,
<a href="glass-decor.html" style="color:#C9A86A;font-weight:600;">double-wall and dry-flower glassware</a>,
<a href="kitchen-storage.html" style="color:#C9A86A;font-weight:600;">spice jars and oil bottles</a>
&mdash; all from the same BSCI audited line, mixed containers supported.</p>
"""

QUOTE_CSS = """
.quick-quote{max-width:520px;margin:0 auto;text-align:left;}
.quick-quote input,.quick-quote select,.quick-quote textarea{width:100%;padding:12px;margin-bottom:12px;border:1px solid #ddd;border-radius:4px;font-size:15px;box-sizing:border-box;font-family:inherit;}
.quick-quote textarea{min-height:88px;resize:vertical;}
.quick-quote button{width:100%;padding:15px;background:#C9A86A;color:#fff;border:none;border-radius:5px;font-size:17px;cursor:pointer;font-weight:bold;}
.quick-quote button:hover{background:#b8965a;}
.quick-quote .hp{position:absolute;left:-9999px;}
.quick-quote .qnote{margin-top:12px;text-align:center;font-size:13px;color:#666;}
.quick-quote .qnote a{color:#C9A86A;}
"""


def inject_page(fname, cfg):
    p = os.path.join(ROOT, fname)
    s = read(p)
    if "quick-quote" in s:
        done(fname + " quick quote form")
    else:
        # 样式追加到现有 <style> 块末尾
        if ".quick-quote{" not in s:
            s = s.replace("</style>", QUOTE_CSS + "</style>", 1)

        # 1) schema：canonical 之前插入 BreadcrumbList + Product
        schema = (
            '<!-- P1: breadcrumb + product structured data -->\n'
            '<script type="application/ld+json">\n'
            '{\n'
            '  "@context": "https://schema.org",\n'
            '  "@type": "BreadcrumbList",\n'
            '  "itemListElement": [\n'
            '    {"@type":"ListItem","position":1,"name":"Home","item":"https://www.kjadehome.com/"},\n'
            '    {"@type":"ListItem","position":2,"name":"Products","item":"https://www.kjadehome.com/products.html"},\n'
            '    {"@type":"ListItem","position":3,"name":"' + cfg["crumb_prev"] + '","item":"https://www.kjadehome.com/' + fname + '"}\n'
            '  ]\n'
            '}\n'
            '</script>\n'
            '<script type="application/ld+json">\n'
            '{\n'
            '  "@context": "https://schema.org",\n'
            '  "@type": "Product",\n'
            '  "name": "' + cfg["product_name"] + '",\n'
            '  "sku": "' + cfg["sku"] + '",\n'
            '  "image": "https://www.kjadehome.com' + cfg["img"] + '",\n'
            '  "description": "' + cfg["desc"] + '",\n'
            '  "brand": {"@type":"Brand","name":"KJadeHome"},\n'
            '  "manufacturer": {"@type":"Organization","name":"KJadeHome"},\n'
            '  "countryOfOrigin": "CN",\n'
            '  "additionalProperty": [\n'
            '    {"@type":"PropertyValue","name":"Minimum order quantity","value":"500 pcs per design"},\n'
            '    {"@type":"PropertyValue","name":"Production lead time","value":"30-45 days after sample approval"},\n'
            '    {"@type":"PropertyValue","name":"Shipping terms","value":"FOB / CIF / DDP"},\n'
            '    {"@type":"PropertyValue","name":"Certification","value":"BSCI audited"}\n'
            '  ],\n'
            '  "offers": {\n'
            '    "@type": "Offer",\n'
            '    "availability": "https://schema.org/InStock",\n'
            '    "priceCurrency": "USD",\n'
            '    "priceSpecification": {\n'
            '      "@type": "UnitPriceSpecification",\n'
            '      "priceCurrency": "USD",\n'
            '      "description": "Quote on request based on design, quantity and destination"\n'
            '    },\n'
            '    "seller": {"@type":"Organization","name":"KJadeHome"}\n'
            '  }\n'
            '}\n'
            '</script>\n'
        )
        s = s.replace('<link rel="canonical"', schema + '<link rel="canonical"', 1)

        # 2) 正文上下文互链（Product Gallery 之前）
        s = s.replace('<h2>Product Gallery</h2>',
                      SIBLING_LINKS.strip() + '\n\n<h2>Product Gallery</h2>', 1)

        # 3) 页内精简询价表单（cta-box 之后、footer 之前）
        form = (
            '\n<div class="section">\n'
            '<div class="cta-box" style="background:#fff;color:#222;text-align:center;border:1px solid #e6e6e6;">\n'
            '<h3 style="color:#0B1F3A;font-size:24px;">Request a Quote for This Range</h3>\n'
            '<p style="color:#666;margin-bottom:22px;">MOQ 500 pcs per design &middot; 30-45 day production &middot; FOB / CIF / DDP &middot; reply within 24 hours</p>\n'
            '<form class="quick-quote" method="POST" action="https://formsubmit.co/bonnie@kjadehome.com" target="_blank">\n'
            '<input type="hidden" name="_subject" value="' + cfg["quick_subject"] + '">\n'
            '<div class="hp" aria-hidden="true"><label>Leave empty<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>\n'
            '<input type="text" name="name" placeholder="Your name *" required>\n'
            '<input type="email" name="email" placeholder="Business email *" required>\n'
            '<select name="quantity" required>\n'
            '<option value="">Estimated quantity *</option>\n'
            '<option value="500-1000">500 - 1,000 pcs</option>\n'
            '<option value="1000-5000">1,000 - 5,000 pcs</option>\n'
            '<option value="5000+">5,000+ pcs</option>\n'
            '</select>\n'
            '<textarea name="message" placeholder="Shapes, finishes, colours, target market or deadline?"></textarea>\n'
            '<button type="submit">Send Quote Request &rarr;</button>\n'
            '<p class="qnote">Prefer email? Write to <a href="mailto:bonnie@kjadehome.com">bonnie@kjadehome.com</a></p>\n'
            '</form>\n'
            '</div>\n'
            '</div>\n'
        )
        s = s.replace('</div>\n\n<div class="footer">', '</div>\n' + form + '\n<div class="footer">', 1)

        # 4) GA4 打点（产品页快速询价表单）
        s = s.replace('<script src="float-buttons.js"></script>',
            '<!-- P1: ga4 event for product page quick quote form -->\n'
            '<script>\n'
            'document.addEventListener("submit", function (e) {\n'
            '  var f = e.target;\n'
            '  if (!f || !f.classList || !f.classList.contains("quick-quote")) return;\n'
            '  try {\n'
            '    if (typeof gtag === "function") {\n'
            '      gtag("event", "inquiry_submit", {\n'
            '        form_location: "product_page_quick_quote",\n'
            '        product_context: "' + cfg["product_name"] + '",\n'
            '        page_path: location.pathname\n'
            '      });\n'
            '    }\n'
            '  } catch (err) {}\n'
            '});\n'
            '</script>\n\n<script src="float-buttons.js"></script>', 1)

        write(p, s)
        LOG.append("OK " + fname + " (schema + 上下文互链 + 询价表单 + GA4 打点)")


# ---------------------------------------------------------------- blog 内链
BLOG_LINKS = {
    "ceramic-mug-moq-guide.html": (
        '<h3 style="font-size:19px;margin-top:34px;">Matching This Guide to a Product Line</h3>'
        '<p style="color:#555;line-height:1.75;">Once you know your MOQ and price band, the next step is seeing the actual tooling and finishes. '
        'Our <a href="https://www.kjadehome.com/ceramic-decor.html" style="color:#C9A86A;font-weight:600;">custom ceramic mug ranges</a> cover glazed, speckled, two-tone and printed programs, '
        'while <a href="https://www.kjadehome.com/glass-decor.html" style="color:#C9A86A;font-weight:600;">double-wall glassware</a> and '
        '<a href="https://www.kjadehome.com/kitchen-storage.html" style="color:#C9A86A;font-weight:600;">kitchen storage sets</a> share the same 500 pc MOQ and can be mixed into one container.</p>'
    ),
    "bsci-certification-guide.html": (
        '<h3 style="font-size:19px;margin-top:34px;">What This Audit Means for Your Order</h3>'
        '<p style="color:#555;line-height:1.75;">A BSCI report only covers the lines that were audited. Our audited lines cover '
        '<a href="https://www.kjadehome.com/ceramic-decor.html" style="color:#C9A86A;font-weight:600;">ceramic mugs</a>, '
        '<a href="https://www.kjadehome.com/glass-decor.html" style="color:#C9A86A;font-weight:600;">glassware</a> and '
        '<a href="https://www.kjadehome.com/kitchen-storage.html" style="color:#C9A86A;font-weight:600;">kitchen storage</a>. '
        'Upload the report to us with your brief and we will confirm scope before you place the order.</p>'
    ),
}


def inject_blog():
    blog_dir = os.path.join(ROOT, "blog")
    for fn, block in BLOG_LINKS.items():
        p = os.path.join(blog_dir, fn)
        if not os.path.exists(p):
            LOG.append("MISS " + fn)
            continue
        s = read(p)
        if "Matching This Guide to a Product Line" in s or "What This Audit Means for Your Order" in s:
            done("blog/" + fn)
            continue
        if "</article>" not in s:
            LOG.append("MISS(</article>) " + fn)
            continue
        s = s.replace("</article>", block + "\n</article>", 1)
        write(p, s)
        LOG.append("OK blog/" + fn + " (正文上下文链到三产品页)")


# ---------------------------------------------------------------- inquiry.html
def inject_inquiry():
    p = os.path.join(ROOT, "inquiry.html")
    s = read(p)
    if "productBySlug" in s:
        done("inquiry.html ?product= preset")
        return
    anchor = "  if (initialParams.get('message'))"
    if anchor not in s:
        LOG.append("MISS(inquiry anchor)")
        return
    preset = """  // P1: 预填产品线（产品页 CTA 带 ?product=ceramic|glass|kitchen-storage|acrylic）
  var productBySlug = {
    'ceramic': 'ceramic',
    'glass': 'glass',
    'kitchen-storage': 'kitchen-storage',
    'acrylic': 'kitchen-storage'
  };
  var presetProduct = productBySlug[String(initialParams.get('product') || '').trim()];
  if (presetProduct) {
    var boxes = form.querySelectorAll('input[name="products"]');
    for (var i = 0; i < boxes.length; i++) {
      if (boxes[i].value === presetProduct) { boxes[i].checked = true; }
    }
  }
"""
    if "const initialParams" not in s:
        LOG.append("MISS(initialParams) inquiry.html")
        return
    # 在 const initialParams 行之后插入
    s = s.replace("const initialParams = new URLSearchParams(window.location.search);",
                  "const initialParams = new URLSearchParams(window.location.search);\n" + preset, 1)
    write(p, s)
    LOG.append("OK inquiry.html (?product= 现在会预填产品线)")


# ---------------------------------------------------------------- index.html 邮箱
def fix_index_email():
    p = os.path.join(ROOT, "index.html")
    s = read(p)
    if '"email": "info@kjadehome.com"' not in s:
        done("index.html schema email")
        return
    s = s.replace('"email": "info@kjadehome.com"', '"email": "bonnie@kjadehome.com"', 1)
    write(p, s)
    LOG.append("OK index.html (Organization contactPoint email -> bonnie@kjadehome.com)")


for f, c in PAGES.items():
    inject_page(f, c)
inject_blog()
inject_inquiry()
fix_index_email()

print("\n".join(LOG))
print("\n--- 校验 schema JSON 合法性 ---")
for f in list(PAGES) + ["blog/" + b for b in BLOG_LINKS]:
    path = os.path.join(ROOT, f)
    txt = read(path)
    n = 0
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', txt, re.S):
        try:
            json.loads(m.group(1))
            n += 1
        except Exception as ex:
            print("  INVALID", f, ex)
    print("  %-34s %d 段 JSON-LD 全部合法" % (f, n))
