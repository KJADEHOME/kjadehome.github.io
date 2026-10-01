# -*- coding: utf-8 -*-
"""P1-8: 给三个产品页加 Product + BreadcrumbList schema（不写价格，用 eligibleQuantity 表达起订量）"""
import io, os

ROOT = r"D:\codex\kjadehome-website"

def block(name, slug, desc, material, category, kw):
    url = "https://www.kjadehome.com/%s" % slug
    return '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "%s",
  "description": "%s",
  "category": "%s",
  "material": "%s",
  "keywords": "%s",
  "brand": { "@type": "Brand", "name": "KJadeHome" },
  "manufacturer": { "@type": "Organization", "name": "KJadeHome" },
  "audience": { "@type": "BusinessAudience", "audienceType": "Importers, retailers, homeware and coffee brands" },
  "additionalProperty": [
    { "@type": "PropertyValue", "name": "Minimum order quantity", "value": "500 pcs per design" },
    { "@type": "PropertyValue", "name": "Production lead time", "value": "30-45 days" },
    { "@type": "PropertyValue", "name": "Service", "value": "OEM / ODM / private label" }
  ],
  "offers": {
    "@type": "Offer",
    "availability": "https://schema.org/InStock",
    "businessFunction": "https://schema.org/Sell",
    "eligibleQuantity": { "@type": "QuantitativeValue", "minValue": 500, "unitCode": "C62" },
    "url": "%s"
  },
  "url": "%s"
}
</script>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.kjadehome.com/" },
    { "@type": "ListItem", "position": 2, "name": "Products", "item": "https://www.kjadehome.com/products.html" },
    { "@type": "ListItem", "position": 3, "name": "%s", "item": "%s" }
  ]
}
</script>
''' % (name, desc, category, material, kw, url, url, name, url)

JOBS = [
    ("ceramic-decor.html",
     block("Custom Ceramic Mugs & Coffee Cups (OEM)", "ceramic-decor.html",
           "Factory-direct OEM ceramic mugs and coffee cups: speckled, two-tone, cork-base and printed styles. Private label, 500 pcs MOQ, 30-45 days.",
           "Stoneware, porcelain", "Ceramic drinkware",
           "custom ceramic mug, ceramic coffee cup, OEM mug manufacturer, private label mug")),
    ("glass-decor.html",
     block("Custom Glassware (OEM)", "glass-decor.html",
           "Factory-direct OEM glassware: double-wall cups, dry-flower glass, glass teapots, straw cups and jars. Private label, 500 pcs MOQ, 30-45 days.",
           "High borosilicate glass, soda-lime glass", "Glassware",
           "custom glassware, double wall glass cup, OEM glass manufacturer, private label glassware")),
    ("kitchen-storage.html",
     block("Custom Kitchen Storage & Spice Jar Sets (OEM)", "kitchen-storage.html",
           "Factory-direct OEM kitchen storage: glass and acrylic spice jar sets, oil bottles, toothpick boxes and condiment stands. Private label, 500 pcs MOQ, 30-45 days.",
           "Glass, acrylic", "Kitchen storage",
           "spice jar set, oil bottle, OEM kitchen storage manufacturer, private label kitchenware")),
]

log = []
for fn, blk in JOBS:
    p = os.path.join(ROOT, fn)
    s = io.open(p, encoding="utf-8").read()
    if '"@type": "Product"' in s:
        log.append("SKIP (already has Product schema): " + fn)
        continue
    idx = s.find("</head>")
    if idx < 0:
        log.append("FAIL no </head>: " + fn)
        continue
    s = s[:idx] + blk + s[idx:]
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    log.append("INSERTED: " + fn)

io.open(os.path.join(ROOT, "_schema_log.txt"), "w", encoding="utf-8").write("\n".join(log))
print("\n".join(log))
