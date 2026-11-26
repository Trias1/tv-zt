"""Audit mendalam semua channel TV ZT: playlist → varian → potongan video, dengan header seperti di box.

Hasil: iptv/audit.json  {"generated": ..., "hasil": {url: {"ok": bool, "why": str, "info": str}}}
       iptv/laporan-audit.txt (ringkasan per alasan)
Dipakai mockup/buat_channels.py untuk menyembunyikan channel yang gagal.

Jalankan dari jaringan rumah (sama dengan box) dan Cloudflare WARP mati:  python -I iptv/audit.py
"""
import gzip
import json
import re
import ssl
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "mockup" / "channels.js"
OUT = ROOT / "audit.json"
LAPORAN = ROOT / "laporan-audit.txt"
UA_BOX = "Mozilla/5.0 (Linux; Android 10; B860H V5.0 Build/QTT8.201201.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/158.0.8127.46 Mobile Safari/537.36"
CTX = ssl.create_default_context()
CTX_LONGGAR = ssl._create_unverified_context()  # WebView juga menolak sertifikat rusak, tapi dicatat terpisah

# Jenis stream di MPEG-TS (PMT)
VIDEO_OK = {0x1B: "H.264", 0x24: "H.265"}
VIDEO_TIDAK = {0x01: "MPEG-1 video", 0x02: "MPEG-2 video", 0x10: "MPEG-4 part 2", 0xEA: "VC-1", 0x42: "AVS"}
AUDIO = {0x0F: "AAC", 0x11: "AAC-LATM", 0x03: "MP3", 0x04: "MP2", 0x81: "AC-3", 0x87: "E-AC-3"}


class Gagal(Exception):
    pass


def ambil(url, h, batas=None, timeout=12):
    req = urllib.request.Request(url, headers=h)
    try:
        r = urllib.request.urlopen(req, timeout=timeout, context=CTX)
    except ssl.SSLError:
        raise Gagal("sertifikat HTTPS rusak")
    except urllib.error.HTTPError as e:
        raise Gagal(f"HTTP {e.code}")
    except urllib.error.URLError as e:
        r = getattr(e, "reason", e)
        if isinstance(r, ssl.SSLError) or "CERTIFICATE" in str(r).upper():
            raise Gagal("sertifikat HTTPS rusak")
        raise Gagal("tidak tersambung")
    except (TimeoutError, OSError):
        raise Gagal("timeout")
    try:
        b = r.read(batas) if batas else r.read()
    except Exception:
        raise Gagal("putus saat mengunduh")
    if r.headers.get("Content-Encoding") == "gzip" or b[:2] == b"\x1f\x8b":
        try:
            b = gzip.decompress(b)
        except Exception:
            pass
    return r.geturl(), b


def jenis_ts(b):
    """Cari PMT di potongan TS, kembalikan set jenis stream."""
    pmt, types = None, set()
    start = b.find(b"\x47")
    for i in range(start, len(b) - 188, 188):
        p = b[i:i + 188]
        if p[0] != 0x47:
            continue
        pid = ((p[1] & 0x1F) << 8) | p[2]
        if not p[1] & 0x40:
            continue
        off = 4 + (1 + p[4] if (p[3] >> 4) & 2 else 0)
        if off >= 188:
            continue
        try:
            if pid == 0 and pmt is None:
                s = off + 1 + p[off]
                pmt = ((p[s + 10] & 0x1F) << 8) | p[s + 11]
            elif pmt is not None and pid == pmt:
                s = off + 1 + p[off]
                L = ((p[s + 1] & 0x0F) << 8) | p[s + 2]
                pil = ((p[s + 10] & 0x0F) << 8) | p[s + 11]
                j, end = s + 12 + pil, min(s + 3 + L - 4, 188)
                while j + 5 <= end:
                    st, el = p[j], ((p[j + 3] & 0x0F) << 8) | p[j + 4]
                    desc = p[j + 5:j + 5 + el]
                    if st == 0x06 and (b"\x6a" in desc[:1] or b"AC-3" in desc):
                        st = 0x81
                    types.add(st)
                    j += 5 + el
                return types
        except IndexError:
            continue
    return types


def cek(c):
    h = {"User-Agent": c.get("ua") or UA_BOX, "Accept": "*/*"}
    if c.get("referer"):
        h["Referer"] = c["referer"]  # sama seperti box: Referer + User-Agent, tanpa Origin
    url, b = ambil(c["url"], h, batas=2_000_000)
    if b[:1] == b"\x47":
        raise Gagal("bukan HLS (siaran TS langsung)")
    t = b.decode("utf-8", "replace").lstrip("﻿ \r\n")
    if not t.startswith("#EXTM3U"):
        raise Gagal("bukan playlist (halaman/error)")
    codecs = ""
    if "#EXT-X-STREAM-INF" in t:
        lines = t.splitlines()
        var = []
        for i, l in enumerate(lines):
            if l.startswith("#EXT-X-STREAM-INF"):
                bw = re.search(r"BANDWIDTH=(\d+)", l)
                cd = re.search(r'CODECS="([^"]+)"', l)
                for nx in lines[i + 1:]:
                    if nx and not nx.startswith("#"):
                        var.append((int(bw.group(1)) if bw else 0, cd.group(1) if cd else "", nx.strip()))
                        break
        if not var:
            raise Gagal("playlist kosong")
        var.sort()
        _, codecs, v = var[len(var) // 2]  # varian tengah, mirip pilihan awal hls.js
        url, b = ambil(urljoin(url, v), h, batas=2_000_000)
        t = b.decode("utf-8", "replace")
        if not t.lstrip().startswith("#EXTM3U"):
            raise Gagal("varian bukan playlist")
    if re.search(r"#EXT-X-(SESSION-)?KEY:[^\n]*(SAMPLE-AES|widevine|playready|fairplay|com\.apple)", t, re.I):
        raise Gagal("DRM (terkunci)")
    if re.search(r"avc1|hvc1|hev1|mp4a", codecs) is None and codecs and re.search(r"mp4v|vp08|dvh", codecs):
        raise Gagal(f"codec tidak didukung ({codecs})")
    segs = [l.strip() for l in t.splitlines() if l.strip() and not l.startswith("#")]
    if not segs:
        raise Gagal("tidak ada potongan video")
    init = re.search(r'#EXT-X-MAP:URI="([^"]+)"', t)
    seg = segs[-3] if len(segs) >= 3 and "#EXT-X-ENDLIST" not in t else segs[0]
    _, sb = ambil(urljoin(url, seg), h, batas=400_000, timeout=15)
    if len(sb) < 200:
        raise Gagal("potongan video kosong")
    head = sb[:16]
    if head.lstrip()[:1] in (b"<", b"{") or b"<html" in sb[:300].lower():
        raise Gagal("potongan video berisi halaman/error")
    info = codecs
    if sb[0] == 0x47 or (len(sb) > 188 and sb[188] == 0x47):
        ty = jenis_ts(sb)
        vid = [VIDEO_OK[x] for x in ty if x in VIDEO_OK]
        bad = [VIDEO_TIDAK[x] for x in ty if x in VIDEO_TIDAK]
        aud = [AUDIO.get(x, hex(x)) for x in ty if x in AUDIO]
        info = "+".join(vid + bad + aud) or "TS"
        if bad and not vid:
            raise Gagal(f"video {bad[0]} (tidak didukung)")
    elif head[4:8] in (b"ftyp", b"styp", b"moof", b"sidx") or init:
        info = codecs or "fMP4"
    elif head[:3] == b"ID3" or (head[0] == 0xFF and head[1] & 0xF0 == 0xF0):
        info = "audio saja"
    elif head[:6] == b"WEBVTT":
        raise Gagal("hanya subtitle")
    elif not re.search(rb"[\x00-\x08]", sb[:64]):
        raise Gagal("potongan video bukan video")
    return info


def uji(c):
    for coba in range(2):
        try:
            return {"ok": True, "why": "", "info": cek(c)}
        except Gagal as e:
            why = str(e)
        except Exception as e:  # noqa: BLE001
            why = "error " + type(e).__name__
        if why.startswith(("bukan", "DRM", "video", "codec", "hanya")):
            break
        time.sleep(2)
    return {"ok": False, "why": why, "info": ""}


def main():
    chans = {}
    masukan = ROOT / "audit-input.json"  # daftar lengkap dari buat_channels.py (belum disaring audit)
    if masukan.exists():
        for c in json.loads(masukan.read_text(encoding="utf-8")):
            chans.setdefault(c["url"], c)
    else:
        raw = DATA.read_text(encoding="utf-8")
        d = json.loads(raw[raw.index("{"):raw.rstrip().rindex("}") + 1])
        for n in d["countries"]:
            for c in n["channels"]:
                chans.setdefault(c["url"], c)
    print(f"Mengaudit {len(chans)} link…", flush=True)
    hasil, t0 = {}, time.time()
    with ThreadPoolExecutor(max_workers=int(sys.argv[1]) if len(sys.argv) > 1 else 48) as ex:
        fut = {ex.submit(uji, c): u for u, c in chans.items()}
        for k, f in enumerate(as_completed(fut), 1):
            hasil[fut[f]] = f.result()
            if k % 500 == 0:
                ok = sum(r["ok"] for r in hasil.values())
                print(f"  {k}/{len(chans)} · lolos {ok} · {time.time() - t0:.0f} dtk", flush=True)
    OUT.write_text(json.dumps({"generated": datetime.now().strftime("%d %b %Y %H:%M"), "hasil": hasil},
                              ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    alasan = {}
    for r in hasil.values():
        if not r["ok"]:
            alasan[r["why"]] = alasan.get(r["why"], 0) + 1
    ok = sum(r["ok"] for r in hasil.values())
    rows = [f"Audit {datetime.now():%d %b %Y %H:%M} · {len(hasil)} link · lolos {ok} · gagal {len(hasil) - ok}", ""]
    rows += [f"{v:6d}  {k}" for k, v in sorted(alasan.items(), key=lambda x: -x[1])]
    LAPORAN.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
