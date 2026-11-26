"""Ambil playlist beberapa negara dari iptv-org, tes setiap channel, simpan yang hidup ke iptv/negara/<kode>.m3u.

Pemakaian (dari folder iptv):  python -I build_country.py
Channel bertanda [Geo-blocked] dibuang (hampir pasti tidak jalan dari Indonesia). Tiap negara dibatasi
MAKS channel; yang siaran 24 jam didahulukan, dan nama yang sama hanya diambil satu (link hidup pertama).
"""
import concurrent.futures as cf
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_m3u import check, parse  # noqa: E402  (tes yang sama dengan id-active.m3u)

NEGARA = [  # (kode iptv-org, kode tampil, nama)
    ("my", "MY", "Malaysia"),
    ("sg", "SG", "Singapura"),
    ("th", "TH", "Thailand"),
    ("jp", "JP", "Jepang"),
    ("kr", "KR", "Korea Selatan"),
    ("sa", "SA", "Arab Saudi"),
    ("qa", "QA", "Qatar"),
    ("uk", "GB", "Inggris"),
    ("us", "US", "Amerika Serikat"),
]
MAKS = 40
OUT = Path(__file__).resolve().parent / "negara"


def nama_bersih(extinf):
    n = extinf.split(",", 1)[-1]
    n = re.sub(r"\s*\[[^\]]*\]", "", n)          # [Not 24/7], [Geo-blocked]
    n = re.sub(r"\s*\(\d{3,4}[pi]\)", "", n)      # (720p)
    return n.strip()


def proses(kode, tampil, nama):
    url = f"https://raw.githubusercontent.com/iptv-org/iptv/master/streams/{kode}.m3u"
    teks = urllib.request.urlopen(url, timeout=30).read().decode("utf-8", "replace")
    tmp = OUT / f"_{kode}.src.m3u"
    tmp.write_text(teks, encoding="utf-8")
    _, entries = parse(tmp)
    tmp.unlink()
    entries = [e for e in entries if "Geo-blocked" not in e[0]]
    with cf.ThreadPoolExecutor(max_workers=32) as ex:
        hasil = list(ex.map(check, entries))
    hidup = [e for e, (ok, _) in zip(entries, hasil) if ok]
    hidup.sort(key=lambda e: ("Not 24/7" in e[0], nama_bersih(e[0]).lower()))
    dipilih, lihat = [], set()
    for e in hidup:
        k = nama_bersih(e[0]).lower()
        if k in lihat:
            continue
        lihat.add(k)
        dipilih.append(e)
        if len(dipilih) >= MAKS:
            break
    dipilih.sort(key=lambda e: nama_bersih(e[0]).lower())
    baris = [f'#EXTM3U x-negara="{tampil}" x-nama="{nama}"']
    for no, e in enumerate(dipilih, 1):
        extinf = re.sub(r",.*$", "," + nama_bersih(e[0]), e[0])
        extinf = extinf.replace("#EXTINF:-1", f'#EXTINF:-1 tvg-chno="{no}" group-title="{nama}"', 1)
        baris += [extinf, *e[1:]]
    (OUT / f"{tampil.lower()}.m3u").write_text("\n".join(baris) + "\n", encoding="utf-8")
    return f"{tampil} {nama}: {len(entries)} dites, {len(hidup)} hidup, {len(dipilih)} dipakai"


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for args in NEGARA:
        try:
            print(proses(*args), flush=True)
        except Exception as ex:
            print(f"{args[1]} {args[2]}: gagal ({ex})", flush=True)
