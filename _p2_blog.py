#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""P2 第二批：生成采购决策类博客，复用现有博客壳，正文末尾一律回链 SKU 页。"""
import io, os, re, json

BASE = "https://www.kjadehome.com"
BLOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blog")
SRC = os.path.join(BLOG, "ceramic-mug-moq-guide.html")

s = io.open(SRC, encoding="utf-8").read()

L = lambda x: '<a href="%s" style="color:#C9A86A;font-weight:600;">%s</a>' % x


def art(slug, cat, title, desc, h1, date, body, related, toc):
    """把所有可替换锚点一次性替换掉。"""
    out = s
    rep = [
        ("<title>.*?</title>", "<title>%s | KJadeHome Blog</title>" % title),
        ('<meta name="description" content="[^"]*">',
         '<meta name="description" content="%s">' % desc),
        ('<meta property="og:title" content="[^"]*">',
         '<meta property="og:title" content="%s">' % title),
        ('<meta property="og:description" content="[^"]*">',
         '<meta property="og:description" content="%s">' % desc),
        ('<meta property="og:url" content="[^"]*">',
         '<meta property="og:url" content="%s/blog/%s.html">' % (BASE, slug)),
        ('<span class="article-category">[^<]*</span>',
         '<span class="article-category">%s</span>' % cat),
        ('<h1>[^<]*</h1>', "<h1>%s</h1>" % h1),
        ('<span>September 13, 2026</span>', "<span>%s</span>" % date),
        ('"@type": "BlogPosting",', '"@type": "BlogPosting",'),
        ('"headline": "[^"]*"', '"headline": "%s"' % h1.replace('"', "'")),
        ('"description": "[^"]*"', '"description": "%s"' % desc.replace('"', "'")),
        ('"datePublished": "[^"]*"', '"datePublished": "%s"' % date[:16]),
        ('"dateModified": "[^"]*"', '"dateModified": "%s"' % date[:16]),
        ('"@id": "[^"]*"', '"@id": "%s/blog/%s.html"' % (BASE, slug)),
        ('<link rel="canonical" href="[^"]*">',
         '<link rel="canonical" href="%s/blog/%s.html">' % (BASE, slug)),
        ('<meta name="twitter:title" content="[^"]*"',
         '<meta name="twitter:title" content="%s | KJadeHome"' % title),
        ('<meta name="twitter:description" content="[^"]*"',
         '<meta name="twitter:description" content="%s">' % desc),
    ]
    for a, b in rep:
        out, n = re.subn(a, b, out, count=1, flags=re.S)
        if n == 0:
            raise SystemExit("锚点未命中：%s" % a[:60])

    # 正文整段替换：从 <article class="article-content"> 到 </article>
    a = out.index('<article class="article-content">')
    b = out.index("</article>", a)
    out = out[:a] + '<article class="article-content">\n' + body + "\n</article>" + out[b + len("</article>"):]

    # 侧边栏目录
    a = out.index('<h3>Table of Contents</h3>')
    b = out.index("</ul>", a)
    out = out[:a] + "<h3>Table of Contents</h3>\n<ul>\n" + toc + "\n</ul>" + out[b:]

    # 相关文章卡（3 张）
    a = out.index('<div class="related-grid">')
    b = out.index("</div>\n  </div>\n</div>", a)
    out = out[:a] + '<div class="related-grid">\n' + related + "\n    " + out[b:]

    io.open(os.path.join(BLOG, slug + ".html"), "w", encoding="utf-8", newline="").write(out)
    return out


def card(t, p, href):
    return ('      <div class="related-card">\n'
            '        <h4>%s</h4>\n'
            '        <p>%s</p>\n'
            '        <a href="%s">Read More →</a>\n'
            '      </div>' % (t, p, href))


def toc_item(t, anchor):
    return '        <li><a href="#%s">%s</a></li>' % (anchor, t)


# ═════════════════════ 1. FDA / Prop65 合规 ═════════════════════
art(
    "fda-prop65-drinkware-compliance",
    "Compliance",
    "FDA &amp; California Prop 65 Compliance for Drinkware: An Importer's Checklist",
    "What importers must verify before shipping ceramic mugs, glass tumblers and water glasses to the U.S. — lead, cadmium, food-contact testing and the certificates that actually hold up at customs.",
    "FDA &amp; California Prop 65 Compliance for Drinkware: An Importer's Checklist",
    "October 2, 2026",
    """<p>Drinkware is one of the few categories where a product can look perfect on a shelf and still be unsellable in a U.S. store. The failure mode is never visual — it is a <strong>lead or cadmium number that crossed a limit</strong>, discovered by a retailer's lab rather than by your factory. This checklist covers what U.S. importers are actually asked to prove, and which documents survive a container inspection.</p>

<h2>Why Drinkware Triggers More Compliance Questions Than Decorative Ceramics</h2>
<p>A ceramic vase touches a surface. A mug, a tumbler and a water glass touch <strong>food and drink</strong>, so they fall under food-contact regulation in most jurisdictions. That changes the burden of proof: you are not only declaring what the product is made of, you are declaring that the materials will not migrate into what the consumer drinks.</p>
<p>In practice this means three separate exposures can sit on the same SKU:</p>
<ul>
  <li><strong>Food-contact approval</strong> — the glaze, the liner, the glass itself must be rated for contact with food or beverage.</li>
  <li><strong>Lead and cadmium limits</strong> — set for the <em>finished article</em>, including decoration, not just the clay body.</li>
  <li><strong>Total-lead testing on painted or printed surfaces</strong> — the most common failure point on mugs, because the colour layer is the part most likely to carry the pigment.</li>
</ul>

<h2>Food-contact Certification: What to Ask the Factory For</h2>
<p>Ask for a certification that names the <strong>material</strong> and the <strong>standard</strong>, not a generic "food safe" statement. A usable document states:</p>
<ol>
  <li>The product and material it covers (e.g. "glazed ceramic mug body", "soda-lime glass wall").</li>
  <li>The standard applied — FDA 21 CFR 175-190 for the U.S. market, plus LFGB or EU 10/2011 where you also sell into the EU.</li>
  <li>Test report date and the laboratory that issued it.</li>
  <li>Whether the <em>decoration</em> is included in scope. This is the clause that gets skipped, and it is the clause that matters.</li>
</ol>

<h3 id="lead-cadmium">Lead and Cadmium: The Numbers That Actually Get Checked</h3>
<p>Two numbers are commonly reported and they are not interchangeable:</p>
<ul>
  <li><strong>Total lead</strong> — measured by digesting the whole article. Easier to test, but a weak proxy for real risk.</li>
  <li><strong>Leachable lead</strong> — measured by extracting under acidic conditions, which is a far better predictor of real-world migration.</li>
</ul>
<p>For <a href="https://www.kjadehome.com/ceramic-mug-manufacturer.html">custom ceramic mugs</a>, the decoration is the usual culprit: a bright red or orange underglaze on the rim can carry far more lead than the body. For <a href="https://www.kjadehome.com/double-wall-glass-tumbler.html">double-wall glass tumblers</a> and <a href="https://www.kjadehome.com/glass-water-glasses-manufacturer.html">water glasses</a>, the risk sits in the mill finishing and any printed logo. Ask the factory specifically for leachable results on the decorated area — if they cannot separate the two, you do not have the data you need.</p>

<h2 id="prop65">California Prop 65: A Different Test From FDA</h2>
<p>Prop 65 is not a safety standard; it is a <strong>warning</strong> standard. An importer can have full FDA compliance and still be exposed if California exposure levels are exceeded and no warning is delivered. The practical consequences:</p>
<blockquote><p>Warnings must reach the consumer before purchase. A warning printed only on a warehouse carton, or only on a compliance sheet in your supplier file, does not satisfy the requirement.</p></blockquote>
<p>The trap for importers is that most compliance documents are produced <strong>by the factory, for the factory's domestic market</strong>. A Chinese mill test confirms material suitability; it is not evidence that a California warning is correctly worded or that your specific decoration passes. Treat Prop 65 labelling as a <em>documentation</em> task you own, not a testing task you delegate.</p>

<h2 id="documents">The Document Set That Holds Up at customs and at a Retail Audit</h2>
<p>When a U.S. retailer or a customs officer asks for the file on a drinkware SKU, these five items cover almost every request:</p>
<ol>
  <li>Food-contact test report naming the finished article and standard.</li>
  <li>Lead and cadmium report covering both total and leachable figures.</li>
  <li>A written material declaration from the factory naming glaze, body and decoration layers.</li>
  <li>Prop 65 warning text, where applicable, approved before the run is scheduled.</li>
  <li>Production batch traceability — which kiln, which date, which lot the tested samples came from.</li>
</ol>
<p>Item 5 is the one most factories cannot produce retroactively. If you need it, request it <strong>before</strong> the run, not after the container is loaded.</p>

<h2 id="program">Turning Compliance Into a Product Decision</h2>
<p>The cheapest compliance outcome is designed in, not tested in. Three decisions at sampling stage remove most of the risk:</p>
<ul>
  <li>Choose food-safe <strong>reactive or lead-free glaze systems</strong> for any rim that contacts a lip.</li>
  <li>Avoid heavy <strong>overglaze colours</strong> on the drinking surface; move graphics below the rim.</li>
  <li>For glass, confirm the <strong>mill's food-contact grade</strong> before tooling, not after the mould is cut.</li>
</ul>
<p>On our side, <a href="https://www.kjadehome.com/glass-decor.html">our glassware programme</a> and <a href="https://www.kjadehome.com/kitchen-storage.html">kitchen storage ranges</a> ship under the same BSCI-audited process and the same 500 pc MOQ, so a mixed compliance file can cover several categories at once rather than one SKU at a time.</p>

<h2 id="faq">Frequently Asked</h2>
<h3>Does FDA approval cover the decoration on a mug?</h3>
<p>Only if the test report explicitly includes the decoration. Reports scoped to "ceramic body" or "glass wall" exclude the printed or glazed surface, which is where most failures occur. Ask for the decorated finished article to be in scope.</p>
<h3>Is a Prop 65 warning needed for glass tumblers?</h3>
<p>It depends on the measured exposure level and how the product is marketed — a "drinkware" positioning can attract scrutiny that a purely decorative item would not. The correct step is a warning assessment against your finished product, not a blanket assumption either way.</p>
<h3>How far ahead should compliance be confirmed?</h3>
<p>Before the production run. Batching and retesting after casting means scrapping or re-decorating an entire order, not just a sample.</p>""",
    "\n".join([card("FDA &amp; Prop 65 Compliance for Drinkware",
                    "The document set U.S. importers actually get asked for.",
                    "fda-prop65-drinkware-compliance.html"),
               card("Double-Wall Glass Tumblers: Specification Guide",
                    "How to write a spec that prevents the five common defects.",
                    "double-wall-glass-buying-guide.html"),
               card("Mixed Container vs Full Container",
                    "Ship several categories from one factory in one shipment.",
                    "mixed-container-shipping-guide.html")]),
    "\n".join([toc_item("Why Drinkware Triggers More Claims", "lead-cadmium"),
               toc_item("Food-contact Certification", "documents"),
               toc_item("Lead and Cadmium", "lead-cadmium"),
               toc_item("California Prop 65", "prop65"),
               toc_item("The Document Set", "documents"),
               toc_item("Turning Compliance Into a Product Decision", "program")]),
)

# ═════════════════════ 2. 双层玻璃选购 ═════════════════════
art(
    "double-wall-glass-buying-guide",
    "Sourcing Tips",
    "Double-Wall Glass Tumblers: How to Write a Spec That Avoids the 5 Common Defects",
    "A buyer's specification for double-wall glass — wall gap, annealing, thermal shock, printing and packaging — written before tooling so defects are designed out instead of sorted out.",
    "Double-Wall Glass Tumblers: How to Write a Spec That Avoids the 5 Common Defects",
    "October 3, 2026",
    """<p>Double-wall glass looks like a single product and behaves like three: a press-moulded outer shell, a moulded inner shell, and an air gap between them that does the insulating work. Every defect that matters lives in the relationship between those three parts — which is why "the same design" from two factories can pass one buyer's inbound check and fail the next one's.</p>

<h2 id="gap">1. The Air Gap Is the Product — Specify Its Tolerance</h2>
<p>The insulation comes from trapped still air, so gap consistency is the specification that decides whether a tumbler performs like a double wall or like a single wall with decoration. On sampling, measure at three heights, not one:</p>
<ul>
  <li><strong>Top rim</strong> — should be consistent all the way around; a wobble here is visible as a ripple in the filled drink.</li>
  <li><strong>Mid body</strong> — the widest section, where gap collapse is most likely under load.</li>
  <li><strong>Base</strong> — where the inner shell is pinned; the transition is the most common place for a visible pinch.</li>
</ul>
<p>A spec written as "double wall" is not enforceable. Written as "minimum 4 mm annular gap, verified at three heights on 5% of samples", it is.</p>

<h2 id="anneal">2. Annealing: The Defect You Cannot See Until the Shelf</h2>
<p>Inside stress from a too-fast cool leaves a tumbler that passes inspection and then cracks in a warehouse in three months, or breaks the first time a consumer pours boiling water. The control is a defined <strong>annealing cycle</strong> with measurable exit temperature, and a thermal shock test in your inbound spec rather than the factory's.</p>
<p>This is also the parameter that separates a press-mould product from a cheap cast one — which is why <a href="https://www.kjadehome.com/double-wall-glass-tumbler.html">our double-wall programme</a> specifies annealing explicitly instead of treating it as a factory default.</p>

<h2 id="thermal">3. Thermal Shock Rated for Your Market's Use Pattern</h2>
<p>Rated thermal shock means the temperature delta the wall survives. It is worth matching to real use: iced-drink-first-then-hot is a café habit, but at home the common failure is hot coffee left in a tumbler that then meets a dishwasher. State the delta and the number of cycles in the spec, and test the <strong>finished decorated</strong> part — decoration changes stress distribution at the surface.</p>

<h2 id="print">4. Print and Decoration: Where Branding Creates Risk</h2>
<p>Fired-on ceramic decoration and acid-etched matte finishes are the two common routes. The buyer's question is not which looks better in a sample, but which survives:</p>
<ul>
  <li><strong>Fired decoration</strong> is part of the glass — good durability, and it raises the compliance question you should already be asking, since the colour layer sits on the food-contact surface.</li>
  <li><strong>Acid etch</strong> is a surface texture, not a coating, so it carries less migration risk but can trap residue.</li>
</ul>
<p>Whichever route you pick, confirm it in writing for the <em>drinking surface</em>, not the lower third of the tumbler.</p>

<h2 id="pack">5. Packaging Is Part of the Spec, Not an Afterthought</h2>
<p>Double-wall tumblers are hollow, so a case holds fewer units and shock transmission between units is high. Minimum viable inbound packaging:</p>
<ol>
  <li>Individual <strong>edge-crush corrugate divider</strong> or moulded pulp cradle per unit.</li>
  <li>Case drop-test rating matched to your destination's handling, not to a domestic default.</li>
  <li>A declared <strong>cases per pallet layer</strong> — over-stacking is what turns a packaging spec into a breakage claim.</li>
  <li>Carton label stating the shipped quantity; the gap between declared and actual is common and expensive.</li>
</ol>

<h2 id="sample">Sampling Order That Saves a Round Trip</h2>
<p>Sample in this sequence and reject on the earliest failing gate, rather than accumulating defects and arguing about them after tooling:</p>
<ul>
  <li><strong>Geometry</strong> — gap at three heights, weight, height, mouth diameter.</li>
  <li><strong>Thermal</strong> — anneal exit temperature and thermal shock cycles.</li>
  <li><strong>Finish</strong> — decoration adhesion and surface quality after a wash cycle.</li>
  <li><strong>Packaging trial</strong> — drop the packed case, not the glass.</li>
</ul>

<h2 id="sourcing">What This Looks Like in a Real Programme</h2>
<p>Our standard double-wall and <a href="https://www.kjadehome.com/glass-water-glasses-manufacturer.html">water glass</a> programmes start at <strong>500 pc MOQ</strong> with 30–45 day production, and can be combined with <a href="https://www.kjadehome.com/stoneware-tableware-manufacturer.html">stoneware tableware</a> or <a href="https://www.kjadehome.com/ceramic-mug-manufacturer.html">ceramic mugs</a> under one BSCI-audited process — so one compliance file and one container cover several lines instead of one.</p>

<h2 id="faq">Frequently Asked</h2>
<h3>Is a thicker double wall always better?</h3>
<p>No. Thicker walls with an uneven gap insulate worse and weigh more per unit, which raises your case count and freight. Consistent gap beats raw thickness.</p>
<h3>Can double-wall go through a commercial dishwasher?</h3>
<p>It depends on the anneal and the decoration, not the wall type. Ask for dishwasher-cycle data on the finished decorated part, plus the thermal shock delta it survived.</p>
<h3>Why do two factories quote the same design so differently?</h3>
<p>Because "same design" does not specify annealing, gap tolerance or press versus cast. The difference in quote is usually the difference in those three, not in margin.</p>""",
    "\n".join([card("Double-Wall Glass Tumblers: Specification Guide",
                    "Defects designed out at spec stage, not sorted at inbound.",
                    "double-wall-glass-buying-guide.html"),
               card("FDA &amp; Prop 65 Compliance for Drinkware",
                    "Which documents actually hold up at a U.S. audit.",
                    "fda-prop65-drinkware-compliance.html"),
               card("Mixed Container vs Full Container",
                    "Combine glass with ceramics to cut per-SKU freight.",
                    "mixed-container-shipping-guide.html")]),
    "\n".join([toc_item("The Air Gap Is the Product", "gap"),
               toc_item("Annealing", "anneal"),
               toc_item("Thermal Shock", "thermal"),
               toc_item("Print and Decoration", "print"),
               toc_item("Packaging as Spec", "pack"),
               toc_item("Sampling Order", "sample")]),
)

# ═════════════════════ 3. 拼柜/整柜 ═════════════════════
art(
    "mixed-container-shipping-guide",
    "Logistics",
    "Mixed Container vs Full Container: Multi-Category Orders from One Factory",
    "How to plan a mixed container across ceramics, glass and acrylic — volume maths, category limits and the paperwork that keeps one shipment from holding up the rest.",
    "Mixed Container vs Full Container: Multi-Category Orders from One Factory",
    "October 4, 2026",
    """<p>An importer with three product lines does not have three problems, they have one problem: three separate minimum container loads. Consolidating them into a single mixed shipment changes the freight maths, the production planning and the risk profile of the order — usually in the importer's favour, but only if the category limits are understood first.</p>

<h2 id="volume">Start With Volume, Not With SKUs</h2>
<p>Container economics are driven by <strong>cubic metres</strong>, not by units or by weight. The practical sequence:</p>
<ol>
  <li>Convert each SKU to packed cubic metres per case, including the divider and the carton wall.</li>
  <li>Multiply by your planned quantity.</li>
  <li>Sort the running total into categories that share a factory process.</li>
  <li>Check the remainder against a minimum economical line-haul, not against zero.</li>
</ol>
<p>Doing this in SKU order instead of volume order is why most mixed shipments end up 60–70% full: the last few SKUs quietly consume the remaining space.</p>

<h2 id="limits">Category Limits: What Cannot Be Merged</h2>
<p>Some combinations are routine and some are restricted. The ones that bite in practice:</p>
<ul>
  <li><strong>Firing temperature compatibility</strong> — a glaze and a body that must share a kiln run is a scheduling constraint, not a hard limit; incompatible glazes simply need separate fires, which is why mixed ceramic orders sometimes quote as two production windows.</li>
  <li><strong>Food-contact documentation per material</strong> — ceramic, glass and each acrylic compound each need their own compliance file. They can travel together; they cannot share a certificate.</li>
  <li><strong>Soft plastics and food-contact acrylic</strong> — packing and labelling requirements differ from ceramics and glass, and customs often wants them listed separately.</li>
  <li><strong>Weight class</strong> — dense stoneware and light acrylic have very different case weights; over-weight cartons fail a retail distribution check even when the volume fits.</li>
</ul>
<p>Our <a href="https://www.kjadehome.com/acrylic-spice-jar-manufacturer.html">acrylic spice jar</a> and <a href="https://www.kjadehome.com/acrylic-kitchen-organiser.html">kitchen organiser</a> ranges typically sit in a different weight and documentation class from <a href="https://www.kjadehome.com/ceramic-mug-manufacturer.html">ceramic mugs</a> and <a href="https://www.kjadehome.com/stoneware-tableware-manufacturer.html">stoneware tableware</a> — that is normal and is handled at booking, not at loading.</p>

<h2 id="cost">Where the Savings Actually Come From</h2>
<p>A mixed container wins on three lines, and only one of them is freight:</p>
<ul>
  <li><strong>Freight per unit</strong> — one line-haul across all categories instead of three.</li>
  <li><strong>Handling</strong> — one booking, one loading dock, one set of documents.</li>
  <li><strong>Cash cycle</strong> — one payment event instead of three staggered ones, which is frequently larger in absolute terms than the freight saving.</li>
</ul>
<p>What it does <em>not</em> save automatically is unit price. Consolidating does not lower the factory's per-unit cost; the per-unit price is set by quantity within each category. Do not expect a volume discount for mixing — expect a freight and administrative saving.</p>

<h2 id="risk">The One Real Risk: One Delay Blocks Everything</h2>
<p>In a single-category shipment a problem costs you one category. In a mixed shipment the same problem delays the whole vessel, because the container leaves once, not once per SKU. That means:</p>
<blockquote><p>Mixed containers raise the cost of a late category. It is worth confirming lead-time <em>per category</em> before booking, not after.</p></blockquote>
<p>The mitigation is sequencing: schedule the category with the longest lead time first, and treat the others as fill. If two categories on the same container have materially different lead times, that alone justifies confirming them with the factory before you commit to a ship date.</p>

<h2 id="paperwork">Paperwork for a Mixed Shipment</h2>
<p>Keep the commercial documents consolidated and the compliance documents separate:</p>
<ul>
  <li><strong>One</strong> commercial invoice and packing list, with quantities split by category.</li>
  <li><strong>Separate</strong> food-contact and material declarations per material.</li>
  <li><strong>One</strong> certificate of origin, provided the shipment qualifies as originating.</li>
  <li><strong>Case marks</strong> that identify category, so a unit-level recall is not a shipment-level recall.</li>
  <li><strong>Photos</strong> of the loaded container before sealing — cheapest protection available if a dispute later touches the loading.</li>
</ul>

<h2 id="plan">A Workable Sequence</h2>
<ol>
  <li>Fix quantities per category from volume maths, not from a wish list.</li>
  <li>Confirm lead time per category with the factory and sequence longest-first.</li>
  <li>Confirm compliance files exist for every material in the shipment.</li>
  <li>Book the container against the <em>longest</em> category, not the average.</li>
  <li>Photograph loading, then seal.</li>
</ol>
<p>Because our programmes share a 500 pc MOQ and a 30–45 day production window across <a href="https://www.kjadehome.com/ceramic-decor.html">ceramics</a>, <a href="https://www.kjadehome.com/glass-decor.html">glassware</a> and <a href="https://www.kjadehome.com/kitchen-storage.html">kitchen storage</a>, most mixed orders can be planned as a single schedule rather than three. Ask for the per-category lead time before you book — that is the number that decides whether the plan holds.</p>

<h2 id="faq">Frequently Asked</h2>
<h3>Is a mixed container always cheaper?</h3>
<p>For freight and handling, yes. It does not reduce per-unit factory pricing, and it increases the cost of any single category running late.</p>
<h3>Can ceramics, glass and acrylic ship in one container?</h3>
<p>Yes, subject to separate compliance documentation per material and to case-weight suitability for your destination's distribution handling.</p>
<h3>What MOQ applies to a mixed order?</h3>
<p>The 500 pc MOQ applies per category, not to the container total. Three categories at 500 pc each is a valid mixed shipment.</p>""",
    "\n".join([card("Mixed Container vs Full Container",
                    "Volume maths, category limits and the paperwork that keeps one shipment on schedule.",
                    "mixed-container-shipping-guide.html"),
               card("Double-Wall Glass Tumblers: Specification Guide",
                    "Packaging is part of the container maths — specify it early.",
                    "double-wall-glass-buying-guide.html"),
               card("FDA &amp; Prop 65 Compliance for Drinkware",
                    "Each material needs its own file, even in one container.",
                    "fda-prop65-drinkware-compliance.html")]),
    "\n".join([toc_item("Start With Volume", "volume"),
               toc_item("Category Limits", "limits"),
               toc_item("Where the Savings Come From", "cost"),
               toc_item("The One Real Risk", "risk"),
               toc_item("Paperwork", "paperwork"),
               toc_item("A Workable Sequence", "plan")]),
)

print("3 blog posts generated")

# ═════════════════════ 登记：blog/index.html + sitemap.xml ═════════════════════
NEW = ["fda-prop65-drinkware-compliance", "double-wall-glass-buying-guide",
       "mixed-container-shipping-guide"]

# blog/index.html
idx = os.path.join(BLOG, "index.html")
s_idx = io.open(idx, encoding="utf-8").read()
a = s_idx.index('<div class="blog-grid">') if '<div class="blog-grid">' in s_idx else s_idx.index("blog-card")
b = s_idx.index("</div>", s_idx.index("blog-card", a))
TITLES = {
    "fda-prop65-drinkware-compliance": "FDA &amp; Prop 65 Compliance for Drinkware",
    "double-wall-glass-buying-guide": "Double-Wall Glass: Write the Spec Right",
    "mixed-container-shipping-guide": "Mixed Container vs Full Container",
}
DESCS = {
    "fda-prop65-drinkware-compliance": "The document set U.S. importers actually get asked for at an audit.",
    "double-wall-glass-buying-guide": "Air gap, annealing, thermal shock, print and packaging — specified before tooling.",
    "mixed-container-shipping-guide": "Volume maths, category limits and the paperwork for one consolidated shipment.",
}
CARDS = "\n".join(
    '      <div class="blog-card">\n'
    '        <div class="blog-card-img"><img src="../images/og-share.jpg" alt="%s" loading="lazy"></div>\n'
    '        <div class="blog-card-body">\n'
    '          <span class="blog-card-category">Sourcing</span>\n'
    '          <h3><a href="%s.html">%s</a></h3>\n'
    '          <p>%s</p>\n'
    '          <div class="blog-card-meta"><span>4 min read</span></div>\n'
    '        </div>\n'
    '      </div>' % (TITLES[k], k, TITLES[k], DESCS[k])
    for k in NEW
)
s_idx = s_idx[:b] + CARDS + s_idx[b:]
io.open(idx, "w", encoding="utf-8", newline="").write(s_idx)
print("blog/index.html updated")

# sitemap.xml
full = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sitemap.xml")
sm = io.open(full, encoding="utf-8").read()
for k in NEW:
    if k not in sm:
        sm = sm.replace("</url>", "  <url>\n    <loc>%s/blog/%s.html</loc>\n  </url>\n</url>" % (BASE, k), 1)
io.open(full, "w", encoding="utf-8", newline="").write(sm)
print("sitemap.xml updated")
