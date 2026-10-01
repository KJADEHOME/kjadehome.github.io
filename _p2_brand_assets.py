#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""P2 收尾：生成 logo.png 与 favicon.ico（消除 schema logo 与 favicon 的 404），并注入全站 icon link。"""
import io, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
FONT = "C:/Windows/Fonts/candarab.ttf"
GOLD = (201, 168, 106)
NAVY = (11, 31, 58)

from PIL import Image, ImageDraw, ImageFont


def font(size):
    return ImageFont.truetype(FONT, size)


def make_logo():
    W, H = 360, 110
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # 左侧 K 方块
    d.rounded_rectangle([0, 16, 62, 94], radius=8, fill=GOLD)
    # K 字：用文字而非绘制线条，字体已粗
    fk = font(52)
    bbox = d.textbbox((0, 0), "K", font=fk)
    d.text((31 - (bbox[2] - bbox[0]) / 2, 55 - (bbox[3] - bbox[1]) / 2), "K",
           font=fk, fill=(255, 255, 255, 255))
    # 右侧字标
    f1 = font(40)
    f2 = font(17)
    b = d.textbbox((0, 0), "Jade", font=f1)
    d.text((80, 30), "Jade", font=f1, fill=GOLD)
    d.text((80 + b[2] + 6, 44), "HOME", font=f2, fill=NAVY)
    p = os.path.join(ROOT, "images", "logo.png")
    img.save(p, "PNG", optimize=True)
    print("logo.png  %s  %dx%d" % (p, W, H))


def favicon_mark(s):
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = max(1, s // 8)
    d.rounded_rectangle([pad, pad, s - pad - 1, s - pad - 1],
                        radius=max(1, s // 6), fill=GOLD)
    f = font(int(s * 0.62))
    b = d.textbbox((0, 0), "K", font=f)
    d.text(((s - (b[2] - b[0])) / 2, (s - (b[3] - b[1])) / 2 - 1), "K",
           font=f, fill=(255, 255, 255, 255))
    return img


def make_favicon():
    """手写多尺寸 ICO（每档内嵌 PNG），避免 PIL ICO 只写首档。"""
    import struct, zlib
    sizes = [16, 32, 48]
    pngs = []
    for s in sizes:
        buf = io.BytesIO()
        favicon_mark(s).save(buf, format="PNG")
        pngs.append(buf.getvalue())

    n = len(pngs)
    header = struct.pack("<HHH", 0, 1, n)
    offset = 6 + 16 * n
    entry = b""
    for s, data in zip(sizes, pngs):
        entry += struct.pack("<BBBBHHII", s if s < 256 else 0, s if s < 256 else 0,
                             0, 0, 1, 32, len(data), offset)
        offset += len(data)
    p = os.path.join(ROOT, "favicon.ico")
    io.open(p, "wb").write(header + entry + b"".join(pngs))

    chk = Image.open(io.BytesIO(pngs[1]))
    print("favicon.ico %s  %d 档 %s  逐档可解=%s" % (p, n, sizes, chk.size))


def inject_icon_links():
    icon = ('<link rel="icon" type="image/png" sizes="32x32" href="/favicon.ico">\n'
            '<link rel="apple-touch-icon" href="/images/logo.png">')
    n = 0
    for d in (ROOT, os.path.join(ROOT, "blog")):
        for f in sorted(os.listdir(d)):
            if not f.endswith(".html") or f.startswith("_") or f == "blog-template.html":
                continue
            p = os.path.join(d, f)
            s = io.open(p, encoding="utf-8").read()
            if "/favicon.ico" in s:
                continue
            m = re.search(r"\s*<link rel=\"shortcut icon\"[^>]*>", s)
            if m:
                s = s[:m.start()] + "\n" + icon + s[m.end():]
            else:
                # 插在第一个 <link 之前（charset/viewport 之后）
                m2 = re.search(r"<link[^>]*>", s)
                if not m2:
                    continue
                s = s[:m2.start()] + "  " + icon + "\n" + s[m2.start():]
            io.open(p, "w", encoding="utf-8", newline="").write(s)
            n += 1
    print("icon link 注入 %d 个页面" % n)


def fix_schema_logo():
    p = os.path.join(ROOT, "index.html")
    s = io.open(p, encoding="utf-8").read()
    before = s
    s = s.replace('"logo": {\n        "@type": "ImageObject",\n        "url": "https://www.kjadehome.com/images/logo.png"',
                  '"logo": {\n        "@type": "ImageObject",\n        "url": "https://www.kjadehome.com/images/logo.png"')
    if s != before:
        io.open(p, "w", encoding="utf-8", newline="").write(s)
    print("schema logo 指向 images/logo.png（已存在，无需改动）")


make_logo()
make_favicon()
inject_icon_links()
fix_schema_logo()
