"""Ubah id-national.m3u (+ laporan-nasional.txt) jadi channels.js untuk tv-zt.html.

File HTML yang dibuka langsung dari disk (file://) tidak boleh membaca file .m3u lewat fetch(),
jadi daftar channel dibungkus sebagai skrip biasa yang dimuat dengan <script src="channels.js">.
Pemakaian (dari folder mockup):  python -I build_channels.py
"""
import json
import re
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from categories import susun  # noqa: E402

IPTV = Path(__file__).resolve().parent.parent / "iptv"
M3U = IPTV / "id-national.m3u"
LAPORAN = IPTV / "laporan-nasional.txt"
OUT = Path(__file__).resolve().parent / "channels.js"

# Nomor channel untuk yang tidak tersedia, sama dengan urutan di build_national.py.
URUTAN = ["TVRI", "RCTI", "SCTV", "MNCTV", "GTV", "Indosiar", "Trans TV", "Trans7", "ANTV", "Kompas TV",
          "Metro TV", "tvOne", "iNews", "RTV", "MDTV", "Moji", "Nusantara TV", "Garuda TV", "BTV",
          "BeritaSatu", "CNN Indonesia", "CNBC Indonesia", "TVRI World", "TVRI Sport"]


def parse_m3u(path):
    channels, cur = [], {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#EXTINF"):
            cur = {"name": line.split(",", 1)[-1].strip()}
            no = re.search(r'tvg-chno="(\d+)"', line)
            cur["no"] = int(no.group(1)) if no else len(channels) + 1
        elif line.startswith("#EXTVLCOPT:http-referrer="):
            cur["referer"] = line.split("=", 1)[1]
        elif line.startswith("#EXTVLCOPT:http-user-agent="):
            cur["ua"] = line.split("=", 1)[1]
        elif line and not line.startswith("#") and cur:
            cur["url"] = line
            channels.append(cur)
            cur = {}
    return channels


def unavailable(path):
    out = []
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"(MATI|TIDAK ADA)\s+(.+?)\s+\|\s+(.*)", line)
        if m:
            name = m.group(2).strip()
            reason = "Tidak ada di playlist iptv-org" if m.group(1) == "TIDAK ADA" else "Link sedang mati"
            no = URUTAN.index(name) + 1 if name in URUTAN else 99
            out.append({"no": no, "name": name, "reason": reason})
    return out


def daerah(nasional):
    """Channel Indonesia lain yang hidup (id-active.m3u), di luar yang sudah ada di daftar nasional."""
    path = IPTV / "id-active.m3u"
    if not path.exists():
        return []
    pakai = {c["name"].lower() for c in nasional}
    out, lihat = [], set()
    for c in parse_m3u(path):
        name = re.sub(r"\s*\[[^\]]*\]|\s*\(\d{3,4}[pi]\)", "", c["name"]).strip()
        low = name.lower()
        # Hanya duplikat yang namanya persis sama dengan channel nasional yang dibuang
        # (dulu memakai "diawali", sehingga TVRI Jawa Tengah/Jogja/Bali, dll. ikut terbuang).
        if low in lihat or low in pakai or low.startswith("mdtv") \
                or "inisemar" in c["url"]:
            continue
        lihat.add(low)
        out.append({**c, "name": name, "group": "Daerah"})
    for i, c in enumerate(sorted(out, key=lambda x: x["name"].lower()), 101):
        c["no"] = i
    return sorted(out, key=lambda x: x["no"])


nasional = [{**c, "group": "Nasional"} for c in parse_m3u(M3U)]
indonesia = {"code": "ID", "region": "Asia Tenggara", "channels": nasional + daerah(nasional),
             "unavailable": unavailable(LAPORAN)}
negara = [indonesia]
SEMUA = IPTV / "semua.json"
if SEMUA.exists():
    negara += json.loads(SEMUA.read_text(encoding="utf-8"))["countries"]

# Tandai channel yang mengirim subtitle teks (iptv/check_subtitles.py) → tanda "SUB ID" + kategori Sub Indo.
SUBJSON = IPTV / "subtitle.json"
if SUBJSON.exists():
    bersub = json.loads(SUBJSON.read_text(encoding="utf-8"))
    for n in negara:
        for c in n["channels"]:
            if c["url"] in bersub:
                c["sub"] = 1

# Sembunyikan channel yang gagal audit mendalam (iptv/audit.py: playlist → varian → potongan video).
AUDIT = IPTV / "audit.json"
# Daftar lengkap (belum disaring) untuk audit berikutnya, supaya channel yang hidup lagi bisa lolos kembali.
(IPTV / "audit-input.json").write_text(json.dumps([c for n in negara for c in n["channels"]], ensure_ascii=False), encoding="utf-8")
disembunyikan = 0
if AUDIT.exists():
    hasil = json.loads(AUDIT.read_text(encoding="utf-8"))["hasil"]
    # "Sertifikat rusak" bisa jadi hanya di laptop (cara cek sertifikat berbeda dengan box), jadi tidak disembunyikan;
    # kalau di box memang gagal, fitur sembunyi otomatis di aplikasi yang menanganinya.
    for r in hasil.values():
        if not r["ok"] and r["why"] == "sertifikat HTTPS rusak":
            r["ok"] = True
    for n in negara:
        sebelum = len(n["channels"])
        n["channels"] = [c for c in n["channels"] if hasil.get(c["url"], {"ok": True})["ok"]]
        disembunyikan += sebelum - len(n["channels"])
    negara = [n for n in negara if n["channels"] or n["code"] == "ID"]
    nasional = [c for c in nasional if hasil.get(c["url"], {"ok": True})["ok"]]
    print(f"audit: {disembunyikan} channel gagal disembunyikan")

from logo import buat as buat_logo  # noqa: E402
print(f"logos.js: {buat_logo(negara)} logo channel")

data = {
    "source": M3U.name,
    "generated": datetime.now().strftime("%d %b %Y %H:%M"),
    # Bentuk lama (hanya nasional) tetap disertakan untuk aplikasi TV ZT versi sekarang.
    "channels": nasional,
    "unavailable": indonesia["unavailable"],
    "countries": negara,
    "kategori": susun(negara) if (IPTV / "api" / "channels.json").exists() else [],
}
js = "window.TVKITA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";"
OUT.write_text(js + "\n", encoding="utf-8")

# Tanam juga langsung di tv-zt.html supaya cukup satu file yang dibuka.
HTML = Path(__file__).resolve().parent / "tv-zt.html"
page = HTML.read_text(encoding="utf-8")
page = re.sub(r"(<!-- DATA-CHANNEL:MULAI[^>]*-->\n).*?(\n<!-- DATA-CHANNEL:SELESAI -->)",
              lambda m: m.group(1) + "<script>" + js.replace("</", "<\\/") + "</script>" + m.group(2), page, flags=re.S)
HTML.write_text(page, encoding="utf-8")
total = sum(len(c["channels"]) for c in negara)
print(f"{OUT.name} + {HTML.name}: {len(negara)} negara, {total} channel "
      f"(Indonesia {len(indonesia['channels'])}: {len(nasional)} nasional), {len(js) // 1024} KB")
