"""Buat mockup/logos.js: alamat logo tiap channel ("KODE:nomor" → url singkat) dari iptv-org api/logos.json.

Dipisah dari data channel supaya layar pembuka tidak tambah lama: tv-zt.html memuat logos.js setelah Dashboard tampil.
Alamat disingkat: "i:" = https://i.imgur.com/, "w:" = https://upload.wikimedia.org/wikipedia/, "p:" = https://images.pluto.tv/
"""
import json
import re
from pathlib import Path

API = Path(__file__).resolve().parent.parent / "iptv" / "api"
OUT = Path(__file__).resolve().parent / "logos.js"
SINGKAT = [("https://i.imgur.com/", "i:"), ("https://upload.wikimedia.org/wikipedia/", "w:"), ("https://images.pluto.tv/", "p:")]
FORMAT = {"PNG": 0, "SVG": 1, "WebP": 2, None: 3, "GIF": 4, "JPEG": 5}  # transparan dulu


def kunci(s):
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\(.*?\)|\[.*?\]|\b(hd|sd|fhd|uhd|4k)\b", "", s.lower()))


def buat(negara):
    if not (API / "logos.json").exists():
        return 0
    pilih = {}
    for lg in json.loads((API / "logos.json").read_text(encoding="utf-8")):
        if not lg.get("url") or lg.get("in_use") is False:
            continue
        skor = (lg.get("feed") is not None, FORMAT.get(lg.get("format"), 3), abs((lg.get("width") or 300) - 300))
        if lg["channel"] not in pilih or skor < pilih[lg["channel"]][0]:
            pilih[lg["channel"]] = (skor, lg["url"])
    u2c = {s["url"]: s["channel"] for s in json.loads((API / "streams.json").read_text(encoding="utf-8")) if s.get("channel")}
    # Channel Indonesia (link sendiri, mis. RCTI+) dicocokkan lewat nama ke channel Indonesia di iptv-org.
    nama_id = {}
    for c in json.loads((API / "channels.json").read_text(encoding="utf-8")):
        if c.get("country") == "ID":
            nama_id.setdefault(kunci(c["name"]), c["id"])
    # Hasil iptv/check_logos.py: logo rusak dibuang, logo gelap-transparan diberi tanda "#" (perlu alas terang).
    cekf = API.parent / "logo-cek.json"
    cek = json.loads(cekf.read_text(encoding="utf-8")) if cekf.exists() else {"rusak": [], "alas": []}
    rusak, alas = set(cek["rusak"]), set(cek["alas"])
    out = {}
    for n in negara:
        for c in n["channels"]:
            cid = u2c.get(c["url"]) or (nama_id.get(kunci(c["name"])) if n["code"] == "ID" else None)
            if cid in pilih:
                u = pilih[cid][1]
                if "upload.wikimedia.org" in u and "/thumb/" in u:
                    u = re.sub(r"/\d+px-", "/250px-", u)  # ukuran standar Wikimedia yang kecil (~6 KB)
                for awal, s in SINGKAT:
                    if u.startswith(awal):
                        u = s + u[len(awal):]
                        break
                if u in rusak:
                    continue
                out[f'{n["code"]}:{c["no"]}'] = ("#" + u) if u in alas else u
    OUT.write_text("window.LOGOS = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n"
                   "if (window.TVZT_LOGO) window.TVZT_LOGO();\n", encoding="utf-8")
    return len(out)
