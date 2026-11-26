"""Ukur berapa lama siaran bisa dimundurkan (jendela DVR) di tiap channel: total durasi potongan di playlist.

Hasil: iptv/dvr.json {url: detik} dan ringkasan di layar.  Pemakaian: python -I iptv/check_dvr.py [pekerja]
Hanya channel yang lolos audit (audit.json) yang diukur.
"""
import gzip
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parent
UA = "Mozilla/5.0 (Linux; Android 10; B860H V5.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/158.0 Mobile Safari/537.36"


def get(u, c):
    h = {"User-Agent": c.get("ua") or UA}
    if c.get("referer"):
        h["Referer"] = c["referer"]
    r = urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=12)
    b = r.read(5_000_000)
    if b[:2] == b"\x1f\x8b":
        b = gzip.decompress(b)
    return r.geturl(), b.decode("utf-8", "replace")


def jendela(c):
    try:
        u, t = get(c["url"], c)
        if "#EXT-X-STREAM-INF" in t:
            v = [l.strip() for l in t.splitlines() if l.strip() and not l.startswith("#")][0]
            u, t = get(urljoin(u, v), c)
        if "#EXT-X-ENDLIST" in t or re.search(r"#EXT-X-PLAYLIST-TYPE:VOD", t):
            return -1  # rekaman (bukan siaran langsung)
        return round(sum(float(x) for x in re.findall(r"#EXTINF:\s*([\d.]+)", t)))
    except Exception:  # noqa: BLE001
        return None


def main():
    audit = json.loads((ROOT / "audit.json").read_text(encoding="utf-8"))["hasil"]
    chans = {c["url"]: c for c in json.loads((ROOT / "audit-input.json").read_text(encoding="utf-8"))
             if audit.get(c["url"], {"ok": True})["ok"]}
    hasil = {}
    with ThreadPoolExecutor(max_workers=int(sys.argv[1]) if len(sys.argv) > 1 else 48) as ex:
        fut = {ex.submit(jendela, c): u for u, c in chans.items()}
        for k, f in enumerate(as_completed(fut), 1):
            if f.result() is not None:
                hasil[fut[f]] = f.result()
            if k % 1000 == 0:
                print(f"  {k}/{len(chans)}", flush=True)
    (ROOT / "dvr.json").write_text(json.dumps(hasil), encoding="utf-8")
    live = [v for v in hasil.values() if v >= 0]
    batas = [(60, "< 1 menit"), (300, "1–5 menit"), (900, "5–15 menit"), (3600, "15–60 menit"), (6 * 3600, "1–6 jam"),
             (24 * 3600, "6–24 jam"), (7 * 86400, "1–7 hari"), (10**12, "> 7 hari")]
    print(f"selesai: {len(hasil)} terukur, {len(hasil) - len(live)} rekaman/VOD")
    lo = 0
    for hi, nama in batas:
        print(f"  {nama:12} {sum(lo <= v < hi for v in live)}")
        lo = hi


if __name__ == "__main__":
    main()
