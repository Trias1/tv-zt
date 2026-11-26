"""Cari channel yang mengirim subtitle teks (WebVTT atau closed caption) — hanya membaca playlist utama.

Hasil: iptv/subtitle.json  {url: "sub" | "cc"}  dipakai build_channels.py untuk tanda "SUB ID".
Pemakaian:  python -I iptv/check_subtitles.py [jumlah_pekerja]
"""
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UA_BOX = "Mozilla/5.0 (Linux; Android 10; B860H V5.0) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/158.0.8127.46 Mobile Safari/537.36"


def cek(c):
    h = {"User-Agent": c.get("ua") or UA_BOX}
    if c.get("referer"):
        h["Referer"] = c["referer"]
    try:
        r = urllib.request.urlopen(urllib.request.Request(c["url"], headers=h), timeout=10)
        t = r.read(300_000).decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return None
    if re.search(r"#EXT-X-MEDIA:[^\n]*TYPE=SUBTITLES", t):
        return "sub"
    if re.search(r"#EXT-X-MEDIA:[^\n]*TYPE=CLOSED-CAPTIONS", t):
        return "cc"
    return None


def ada_teks(c):
    """Pastikan trek subtitle benar-benar berisi teks (Boruto: trek ada tapi kosong, teksnya tertanam di gambar).
    Diperiksa 8 potongan terakhir (~40 dtk); dicoba lagi sekali 60 dtk kemudian supaya jeda iklan tidak salah dianggap kosong."""
    from urllib.parse import urljoin
    import time
    h = {"User-Agent": c.get("ua") or UA_BOX}
    if c.get("referer"):
        h["Referer"] = c["referer"]
    for coba in range(2):
        try:
            r = urllib.request.urlopen(urllib.request.Request(c["url"], headers=h), timeout=10)
            base, t = r.geturl(), r.read(300_000).decode("utf-8", "replace")
            m = re.search(r'#EXT-X-MEDIA:[^\n]*TYPE=SUBTITLES[^\n]*URI="([^"]+)"', t)
            if not m:
                return False
            su = urljoin(base, m.group(1))
            r = urllib.request.urlopen(urllib.request.Request(su, headers=h), timeout=10)
            su, st = r.geturl(), r.read().decode("utf-8", "replace")
            segs = [l.strip() for l in st.splitlines() if l.strip() and not l.startswith("#")][-8:]
            for sg in reversed(segs):
                vt = urllib.request.urlopen(urllib.request.Request(urljoin(su, sg), headers=h), timeout=10).read(200_000)
                if b"-->" in vt and re.search(rb"-->[^\n]*\n\s*\S", vt):
                    return True
        except Exception:  # noqa: BLE001
            pass
        if coba == 0:
            time.sleep(60)
    return False


def verifikasi(n_pekerja):
    """Saring subtitle.json: tanda "sub" hanya untuk yang trek subtitlenya berisi teks."""
    chans = {c["url"]: c for c in json.loads((ROOT / "audit-input.json").read_text(encoding="utf-8"))}
    data = json.loads((ROOT / "subtitle.json").read_text(encoding="utf-8"))
    cek_ini = [u for u, v in data.items() if v == "sub" and u in chans]
    kosong = 0
    with ThreadPoolExecutor(max_workers=n_pekerja) as ex:
        fut = {ex.submit(ada_teks, chans[u]): u for u in cek_ini}
        for k, f in enumerate(as_completed(fut), 1):
            if not f.result():
                data.pop(fut[f], None); kosong += 1
            if k % 500 == 0:
                print(f"  {k}/{len(cek_ini)} · kosong {kosong}", flush=True)
    (ROOT / "subtitle.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"verifikasi selesai: {kosong} trek subtitle kosong dibuang, tersisa {len(data)} channel bersubtitle")


def main():
    if "--verifikasi" in sys.argv:
        verifikasi(int(sys.argv[-1]) if sys.argv[-1].isdigit() else 24)
        return
    chans = {c["url"]: c for c in json.loads((ROOT / "audit-input.json").read_text(encoding="utf-8"))}
    hasil = {}
    with ThreadPoolExecutor(max_workers=int(sys.argv[1]) if len(sys.argv) > 1 else 24) as ex:
        fut = {ex.submit(cek, c): u for u, c in chans.items()}
        for k, f in enumerate(as_completed(fut), 1):
            if f.result():
                hasil[fut[f]] = f.result()
            if k % 1000 == 0:
                print(f"  {k}/{len(chans)} · bersubtitle {len(hasil)}", flush=True)
    (ROOT / "subtitle.json").write_text(json.dumps(hasil, ensure_ascii=False), encoding="utf-8")
    print(f"selesai: {len(hasil)} channel bersubtitle (sub {sum(v == 'sub' for v in hasil.values())}, cc {sum(v == 'cc' for v in hasil.values())})")


if __name__ == "__main__":
    main()
