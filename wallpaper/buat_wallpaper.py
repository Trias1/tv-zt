"""Buat wallpaper 16:9 untuk launcher cleanyourtv dari foto pernikahan.

Potong ke 16:9 dengan kepala pasangan tetap utuh, kecilkan ke 1280x720,
lalu gelapkan kiri atas (jam dan info) dan bawah (ubin aplikasi) supaya tetap terbaca.
Pemakaian: python -I buat_wallpaper.py foto-nikah.jpg ../launcher-theme/wallpaper.jpg
"""
import sys

from PIL import Image, ImageChops, ImageDraw, ImageEnhance

W, H = 1280, 720
BG = 14  # abu-abu dari latar tema #0E0F12


def main(src, dst):
    im = Image.open(src).convert("L")  # foto memang hitam-putih
    w, h = im.size

    # 16:9 selebar foto; mulai sedikit di bawah tepi atas supaya peci dan kerudung tetap utuh.
    crop_h = round(w * 9 / 16)
    top = min(max(int(h * 0.10), 0), h - crop_h)
    im = im.crop((0, top, w, top + crop_h)).resize((W, H), Image.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(0.8)

    # Peta bayangan: 0 = foto apa adanya, 255 = latar gelap penuh.
    bottom = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(bottom)
    for y in range(H):
        d.line([(0, y), (W - 1, y)], fill=int(max(0.0, (y - 380) / (H - 380)) * 150))
    # Kiri atas: memudar ke kanan dan ke bawah, tanpa tepi tajam.
    corner = Image.new("L", (W, H), 0)
    px = corner.load()
    for y in range(300):
        fy = (1 - y / 300) ** 1.5
        for x in range(W // 2):
            px[x, y] = int((1 - x / (W // 2)) * fy * 130)
    shade = ImageChops.lighter(bottom, corner)

    im = Image.composite(Image.new("L", (W, H), BG), im, shade)
    out = im.convert("RGB")
    out.save(dst, "JPEG", quality=84, optimize=True, progressive=True)
    print(dst, out.size)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
