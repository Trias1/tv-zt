"""Buat playlist TV nasional (urut seperti nomor channel TV biasa) dari id.m3u iptv-org.

Untuk tiap channel dicoba semua link-nya, lalu dipakai link pertama yang benar-benar sedang tayang:
playlist video dibaca dua kali berselang beberapa detik, dan dianggap LIVE kalau segmennya bertambah
(siaran berjalan) dan satu segmen video bisa diunduh.
Pemakaian: python -I build_national.py id.m3u id-national.m3u laporan-nasional.txt
"""
import concurrent.futures as cf
import gzip
import re
import ssl
import sys
import time
import urllib.request
from urllib.parse import urljoin

# Urutan dan nama tampilan; pola dicocokkan ke nama di iptv-org (huruf besar/kecil diabaikan).
NASIONAL = [
    ("TVRI", r"^TVRI( \(|$)"),
    ("RCTI", r"^RCTI\b"),
    ("SCTV", r"^SCTV\b"),
    ("MNCTV", r"^MNC ?TV\b"),
    ("GTV", r"^GTV\b"),
    ("Indosiar", r"^Indosiar\b"),
    ("Trans TV", r"^Trans ?TV\b"),
    ("Trans7", r"^Trans ?7\b"),
    ("ANTV", r"^ANTV\b"),
    ("Kompas TV", r"^Kompas ?TV\b"),
    ("Metro TV", r"^Metro ?TV\b"),
    ("tvOne", r"^tv ?One\b"),
    ("iNews", r"^iNews\b"),
    ("RTV", r"^(Rajawali TV|RTV)\b"),
    ("MDTV", r"^MDTV\b"),
    ("Moji", r"^Moji\b"),
    ("Nusantara TV", r"^Nusantara TV\b"),
    ("Garuda TV", r"^Garuda TV\b"),
    ("BTV", r"^BTV\b"),
    ("BeritaSatu", r"^Berita ?Satu\b"),
    ("CNN Indonesia", r"^CNN Indonesia\b"),
    ("CNBC Indonesia", r"^CNBC Indonesia\b"),
    ("TVRI World", r"^TVRI World\b"),
    ("TVRI Sport", r"^TVRI Sport\b"),
]

# Channel yang tidak ditampilkan sama sekali (atas permintaan pemilik). Tetap di daftar di atas
# supaya nomor channel lain tidak bergeser. MDTV: lolos tes dari laptop tapi selalu gagal di box.
DILEWATI = {"MDTV"}

# Kualitas yang dikunci per channel: ganti playlist.m3u8 (otomatis) dengan satu varian tetap.
# Server Trans (CNBC Indonesia/Wowza) punya b744100 = 720p, b544100 = 480p, b344100 = 360p.
KUNCI_KUALITAS = {
    "Trans TV": "chunklist_b544100_sleng.m3u8",
    "Trans7": "chunklist_b544100_sleng.m3u8",
}

# Sumber tambahan dari server siaran gratis RCTI+ (tanpa token/login), ikut dites seperti link iptv-org.
# Butuh Referer rctiplus.com dan IP Indonesia: kalau dijalankan lewat VPN/WARP, hasil tesnya "mati".
# RCTI sendiri di RCTI+ wajib token login, jadi sengaja tidak dimasukkan.
_RCTIPLUS = ['#EXTVLCOPT:http-referrer=https://www.rctiplus.com/',
             '#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)']
# Tidak dipakai: inisemar.my.id mengalihkan ke RCTI+ dengan auth_key buatannya sendiri (menembus login RCTI+).
TIDAK_DIPAKAI = ["inisemar.my.id"]
MIRROR = []  # host mirror tidak resmi yang boleh dipakai dengan label "(mirror)"

SUMBER_TAMBAHAN = [
    ['#EXTINF:-1 tvg-id="MNCTV.id@SD",MNCTV (RCTI+)', *_RCTIPLUS, "https://linier-mnctv.rctiplus.id/mnctv-sdi.m3u8"],
    ['#EXTINF:-1 tvg-id="iNews.id@SD",iNews (RCTI+)', *_RCTIPLUS, "https://linier-inews.rctiplus.id/inews-sdi.m3u8"],
    ['#EXTINF:-1 tvg-id="GTV.id@SD",GTV (RCTI+)', *_RCTIPLUS, "https://linier-gtv.rctiplus.id/gtv-sdi.m3u8"],
]

TIMEOUT = 8
UA = "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def parse(path):
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    entries, cur = [], []
    for line in lines[1:]:
        if not line.strip():
            continue
        cur.append(line)
        if not line.startswith("#"):
            entries.append(cur)
            cur = []
    return entries


def name(entry):
    return entry[0].split(",", 1)[-1].strip()


def headers(entry):
    h = {"User-Agent": UA}
    for line in entry:
        m = re.match(r"#EXTVLCOPT:http-(referrer|user-agent|origin)=(.*)", line, re.I)
        if m:
            h[{"referrer": "Referer", "user-agent": "User-Agent", "origin": "Origin"}[m.group(1).lower()]] = m.group(2).strip()
    return h


def get(url, h, limit=65536):
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=TIMEOUT, context=CTX) as r:
        body = r.read(limit)
        if body[:2] == b"\x1f\x8b":  # sebagian server (mis. Trans TV) selalu mengirim gzip
            body = gzip.decompress(body)
        return body.decode("utf-8", "ignore"), r.geturl()


def media_playlist(url, h):
    """Turun dari master playlist ke playlist video pertama."""
    text, final = get(url, h)
    for _ in range(3):
        if "#EXT-X-STREAM-INF" not in text:
            return text, final
        sub = next(l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#"))
        text, final = get(urljoin(final, sub), h)
    return text, final


def segments(text):
    seq = re.search(r"#EXT-X-MEDIA-SEQUENCE:(\d+)", text)
    segs = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")]
    return (int(seq.group(1)) if seq else None), segs


def live_check(entry):
    url, h = entry[-1].strip(), headers(entry)
    try:
        t1, final = media_playlist(url, h)
        if "#EXTM3U" not in t1:
            return False, "bukan HLS"
        s1, segs1 = segments(t1)
        if not segs1:
            return False, "playlist kosong"
        if "#EXT-X-ENDLIST" in t1:
            return False, "rekaman, bukan siaran langsung"
        # Satu segmen video harus bisa diunduh.
        req = urllib.request.Request(urljoin(final, segs1[-1]), headers=h)
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX) as r:
            if not r.read(2048):
                return False, "segmen kosong"
        time.sleep(7)
        t2, _ = media_playlist(url, h)
        s2, segs2 = segments(t2)
        if (s1 is not None and s2 is not None and s2 > s1) or (segs2 and segs2[-1] != segs1[-1]):
            return True, "LIVE (segmen bertambah)"
        return False, "macet (segmen tidak bertambah)"
    except Exception as e:
        return False, type(e).__name__ + ": " + str(e)[:50]


def main(src, dst, report):
    # Mirror pihak ketiga yang meneruskan siaran berbayar/ber-login tidak dipakai.
    entries = [e for e in parse(src) if not any(h in e[-1] for h in TIDAK_DIPAKAI)] + SUMBER_TAMBAHAN
    jobs = {}
    for label, pat in NASIONAL:
        jobs[label] = [e for e in entries if re.search(pat, name(e), re.I)]
        if label in KUNCI_KUALITAS:
            # Varian terkunci dicoba dulu; kalau server sedang tidak menyediakannya, pakai alamat aslinya.
            kunci = [e[:-1] + [re.sub(r"playlist\.m3u8$", KUNCI_KUALITAS[label], e[-1].strip())] for e in jobs[label]]
            jobs[label] = kunci + jobs[label]
    flat = [(label, e) for label, es in jobs.items() if label not in DILEWATI for e in es]

    def cek_dua_kali(e):
        # Server siaran sering gangguan sesaat (404/timeout); ulangi sekali sebelum dinyatakan mati.
        ok, why = live_check(e)
        if not ok:
            time.sleep(3)
            ok, why2 = live_check(e)
            why = why2 if ok else why
        return ok, why

    with cf.ThreadPoolExecutor(max_workers=16) as ex:
        results = dict(zip([id(e) for _, e in flat], ex.map(lambda x: cek_dua_kali(x[1]), flat)))

    out, lines = ["#EXTM3U"], []
    for no, (label, _) in enumerate(NASIONAL, 1):
        if label in DILEWATI:
            continue
        es = jobs[label]
        if not es:
            lines.append(f"TIDAK ADA  {label}  |  tidak tersedia di playlist iptv-org")
            continue
        ok = next((e for e in es if results[id(e)][0]), None)
        if ok is None:
            why = "; ".join(f"{name(e)}: {results[id(e)][1]}" for e in es)
            lines.append(f"MATI       {label}  |  {why}")
            continue
        shown = label + (" (mirror)" if any(h in ok[-1] for h in MIRROR) else "")
        extinf = re.sub(r",.*$", f",{shown}", ok[0])
        extinf = re.sub(r'#EXTINF:-1', f'#EXTINF:-1 tvg-chno="{no}" group-title="Nasional"', extinf, count=1)
        out.append(extinf)
        out.extend(ok[1:-1])
        out.append(ok[-1])
        lines.append(f"LIVE       {label}  |  {name(ok)}")
    open(dst, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    open(report, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nlive {sum(l.startswith('LIVE') for l in lines)} dari {len(NASIONAL)} channel nasional")


if __name__ == "__main__":
    main(*sys.argv[1:4])
