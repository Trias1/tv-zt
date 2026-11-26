"""Cek setiap logo di mockup/logos.js: bisa dimuat? dan perlu alas terang atau tidak.

- Rusak (tidak bisa dimuat / bukan gambar)         → dibuang
- Transparan dan gelap (mis. tulisan hitam)          → perlu alas terang ("alas")
- Terang (mis. tulisan putih) atau punya latar sendiri → tampil apa adanya di latar gelap
Hasil: iptv/logo-cek.json {"rusak": [...], "alas": [...]}, dipakai mockup/logo.py.
Pemakaian: python -I iptv/check_logos.py [pekerja]
"""
import io
import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
LOGOS = ROOT.parent / "mockup" / "logos.js"
AWAL = {"i:": "https://i.imgur.com/", "w:": "https://upload.wikimedia.org/wikipedia/", "p:": "https://images.pluto.tv/"}
UA = "Mozilla/5.0 (Linux; Android 10; B860H V5.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/158.0 Mobile Safari/537.36"


def penuh(u):
    return AWAL[u[:2]] + u[2:] if u[:2] in AWAL else u


def nilai(b):
    """'alas' kalau transparan & gelap, 'ok' kalau tidak, None kalau bukan gambar yang bisa dibaca."""
    if b.lstrip()[:4] in (b"<svg", b"<?xm"):
        return "alas"  # SVG tidak bisa diukur di sini; kebanyakan logo SVG berwarna gelap
    try:
        im = Image.open(io.BytesIO(b)).convert("RGBA")
    except Exception:  # noqa: BLE001
        return None
    im.thumbnail((64, 64))
    px = list(im.getdata())
    transparan = sum(1 for p in px if p[3] < 40) / max(1, len(px))
    padat = [p for p in px if p[3] >= 40]
    if not padat:
        return None
    lum = sum((0.2126 * r + 0.7152 * g + 0.0722 * b_) / 255 for r, g, b_, a in padat) / len(padat)
    return "alas" if transparan > 0.08 and lum < 0.55 else "ok"


def cek(u):
    for _ in range(2):
        try:
            r = urllib.request.urlopen(urllib.request.Request(penuh(u), headers={"User-Agent": UA}), timeout=15)
            return nilai(r.read(3_000_000))
        except urllib.error.HTTPError as e:
            if e.code in (400, 403, 404, 410):
                return None
        except Exception:  # noqa: BLE001
            pass
    return None


def main():
    s = LOGOS.read_text(encoding="utf-8")
    data = json.loads(s[s.index("{"):s.index(";\n")])
    urls = sorted({v.lstrip("#") for v in data.values()})
    rusak, alas = [], []
    with ThreadPoolExecutor(max_workers=int(sys.argv[1]) if len(sys.argv) > 1 else 48) as ex:
        fut = {ex.submit(cek, u): u for u in urls}
        for k, f in enumerate(as_completed(fut), 1):
            v = f.result()
            if v is None:
                rusak.append(fut[f])
            elif v == "alas":
                alas.append(fut[f])
            if k % 1000 == 0:
                print(f"  {k}/{len(urls)} · rusak {len(rusak)} · perlu alas {len(alas)}", flush=True)
    (ROOT / "logo-cek.json").write_text(json.dumps({"rusak": sorted(rusak), "alas": sorted(alas)}), encoding="utf-8")
    print(f"selesai: {len(urls)} logo · rusak {len(rusak)} · perlu alas terang {len(alas)}")


if __name__ == "__main__":
    main()
