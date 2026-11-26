"""Siapkan aset TV ZT sebelum build: salin tampilan HTML, hls.js, playlist bawaan, dan gambar banner/ikon.

Pemakaian (dari folder tvzt):  python -I siapkan.py
Sumber tampilan ada di ../mockup/tv-kita.html, jadi desain cukup diubah di satu tempat.
"""
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
MOCK = ROOT.parent / "mockup"
IPTV = ROOT.parent / "iptv"
ASSETS = ROOT / "app/src/main/assets"
RES = ROOT / "app/src/main/res"

ASSETS.mkdir(parents=True, exist_ok=True)
shutil.copyfile(MOCK / "tv-kita.html", ASSETS / "index.html")
shutil.copyfile(MOCK / "hls.min.js", ASSETS / "hls.min.js")
if (MOCK / "logos.js").exists():  # alamat logo channel, dimuat setelah Dashboard tampil
    shutil.copyfile(MOCK / "logos.js", ASSETS / "logos.js")
shutil.copyfile(IPTV / "id-nasional.m3u", ASSETS / "default.m3u")

NIGHT, AMBER, INK = (10, 18, 32), (244, 183, 64), (238, 242, 248)


def font(size, bold=True):
    for name in (["arialbd.ttf", "segoeuib.ttf"] if bold else ["arial.ttf", "segoeui.ttf"]):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def banner(path, w, h):
    im = Image.new("RGB", (w, h), NIGHT)
    d = ImageDraw.Draw(im)
    d.rectangle([0, h - h // 14, w, h], fill=AMBER)                     # garis amber di bawah
    f = font(int(h * 0.42))
    tv_w = d.textlength("TV ", font=f)
    zt_w = d.textlength("ZT", font=f)
    x = (w - tv_w - zt_w) / 2
    y = h * 0.20
    d.text((x, y), "TV ", font=f, fill=INK)
    d.text((x + tv_w, y), "ZT", font=f, fill=AMBER)
    d.ellipse([w * 0.86, h * 0.12, w * 0.86 + h * 0.08, h * 0.20], fill=(240, 72, 78))  # lampu LIVE
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)


def icon(path, s):
    im = Image.new("RGB", (s, s), NIGHT)
    d = ImageDraw.Draw(im)
    f = font(int(s * 0.46))
    w = d.textlength("ZT", font=f)
    d.text(((s - w) / 2, s * 0.2), "ZT", font=f, fill=AMBER)
    d.rectangle([0, s - s // 10, s, s], fill=AMBER)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)


banner(RES / "drawable-xhdpi/banner.png", 640, 360)   # banner Android TV 320x180 dp
icon(RES / "mipmap-xxhdpi/ic_launcher.png", 144)
for p in sorted(ASSETS.iterdir()):
    print(f"assets/{p.name}: {p.stat().st_size} B")
print("banner & ikon dibuat")
