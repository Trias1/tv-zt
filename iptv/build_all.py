"""Kumpulkan SEMUA negara di iptv-org/iptv, tes setiap link, simpan yang hidup ke iptv/semua.json.

Pemakaian (dari folder iptv, WARP/VPN mati):  python -I build_all.py
- Daftar file diambil dari repo iptv-org/iptv (streams/<kode>*.m3u); file seperti us_pluto.m3u digabung ke negaranya.
- Link [Geo-blocked] dibuang; sisanya dites dengan check_m3u.check (playlist + satu sub-playlist harus terbuka).
- Nama yang sama dalam satu negara hanya diambil sekali (link hidup pertama).
- Wilayah (benua) diambil dari iptv-org API regions.json.
Indonesia tidak diambil dari sini: TV ZT memakai id-national.m3u + id-active.m3u (lihat mockup/build_channels.py).
"""
import concurrent.futures as cf
import json
import re
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_m3u import check  # noqa: E402

HERE = Path(__file__).resolve().parent
RAW = "https://raw.githubusercontent.com/iptv-org/iptv/master/"
WILAYAH = [  # urutan prioritas: negara masuk ke wilayah pertama yang memuatnya
    ("SEA", "Asia Tenggara"), ("MIDEAST", "Timur Tengah"), ("ASIA", "Asia"), ("EUR", "Eropa"),
    ("SOUTHAM", "Amerika Selatan"), ("AMER", "Amerika Utara & Tengah"), ("AFR", "Afrika"), ("OCE", "Oseania"),
]


def get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "tvzt-playlist-builder"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")


def parse_text(text):
    entries, cur = [], []
    for line in text.splitlines()[1:]:
        if not line.strip():
            continue
        cur.append(line)
        if not line.startswith("#"):
            entries.append(cur)
            cur = []
    return entries


def nama_bersih(extinf):
    n = extinf.split(",", 1)[-1]
    n = re.sub(r"\s*\[[^\]]*\]", "", n)
    n = re.sub(r"\s*\(\d{3,4}[pi]\)", "", n)
    return n.strip()


def to_channel(e, no):
    c = {"no": no, "name": nama_bersih(e[0]), "url": e[-1].strip()}
    for line in e[1:-1]:
        m = re.match(r"#EXTVLCOPT:http-(referrer|user-agent)=(.*)", line, re.I)
        if m:
            c["referer" if m.group(1).lower() == "referrer" else "ua"] = m.group(2).strip()
    if "Not 24/7" in e[0]:
        c["part"] = 1  # tidak siaran 24 jam
    return c


def main():
    t0 = time.time()
    tree = json.loads(get("https://api.github.com/repos/iptv-org/iptv/git/trees/master?recursive=1"))
    files = [t["path"] for t in tree["tree"] if re.match(r"streams/[a-z]{2}(_[a-z0-9_]+)?\.m3u$", t["path"])]
    regions = json.loads(get("https://iptv-org.github.io/api/regions.json"))
    reg = {r["code"]: set(r.get("countries", [])) for r in regions}

    per_negara = defaultdict(list)
    for f in files:
        kode = re.match(r"streams/([a-z]{2})", f).group(1)
        if kode == "id":
            continue
        try:
            per_negara[kode] += [e for e in parse_text(get(RAW + f)) if "Geo-blocked" not in e[0]]
        except Exception as ex:
            print(f"  lewati {f}: {ex}", flush=True)
    semua = [(k, e) for k, es in per_negara.items() for e in es]
    print(f"{len(per_negara)} negara, {len(semua)} link dites…", flush=True)

    with cf.ThreadPoolExecutor(max_workers=64) as ex:
        hasil = list(ex.map(lambda x: check(x[1])[0], semua))

    hidup = defaultdict(list)
    for (k, e), ok in zip(semua, hasil):
        if ok:
            hidup[k].append(e)

    out = []
    for kode, es in hidup.items():
        es.sort(key=lambda e: ("Not 24/7" in e[0], nama_bersih(e[0]).lower()))
        pilih, lihat = [], set()
        for e in es:
            n = nama_bersih(e[0]).lower()
            if n not in lihat:
                lihat.add(n)
                pilih.append(e)
        pilih.sort(key=lambda e: nama_bersih(e[0]).lower())
        iso = "GB" if kode == "uk" else kode.upper()
        wilayah = next((nama for code, nama in WILAYAH if iso in reg.get(code, ())), "Lainnya")
        out.append({"code": iso, "region": wilayah,
                    "channels": [to_channel(e, i) for i, e in enumerate(pilih, 1)]})
    out.sort(key=lambda c: -len(c["channels"]))
    data = {"generated": time.strftime("%d %b %Y %H:%M"), "countries": out}
    (HERE / "semua.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    total = sum(len(c["channels"]) for c in out)
    print(f"selesai dalam {time.time() - t0:.0f} dtk: {len(out)} negara punya channel hidup, {total} channel", flush=True)


if __name__ == "__main__":
    main()
