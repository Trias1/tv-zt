"""Tes setiap channel di playlist M3U dan tulis playlist baru berisi channel yang hidup.

Pemakaian: python -I cek_m3u.py <input.m3u> <output.m3u> <laporan.txt>
File input tidak diubah.
"""
import concurrent.futures as cf
import re
import ssl
import sys
import urllib.request
from urllib.parse import urljoin

TIMEOUT = 8
UA = "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE  # banyak server siaran lokal pakai sertifikat kedaluwarsa


def parse(path):
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    header, entries, cur = lines[0] if lines else "#EXTM3U", [], []
    for line in lines[1:]:
        if not line.strip():
            continue
        cur.append(line)
        if not line.startswith("#"):
            entries.append(cur)
            cur = []
    return header, entries


def opts(entry):
    headers = {"User-Agent": UA}
    for line in entry:
        m = re.match(r"#EXTVLCOPT:http-(referrer|user-agent|origin)=(.*)", line, re.I)
        if m:
            key = {"referrer": "Referer", "user-agent": "User-Agent", "origin": "Origin"}[m.group(1).lower()]
            headers[key] = m.group(2).strip()
    return headers


def get(url, headers, limit=4096):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read(limit), r.geturl()


def check(entry):
    url = entry[-1].strip()
    headers = opts(entry)
    try:
        status, ctype, body, final = get(url, headers)
        if status != 200:
            return False, f"HTTP {status}"
        text = body.decode("utf-8", "ignore")
        if "#EXTM3U" in text:
            # Playlist master: pastikan satu sub-playlist juga bisa dibuka.
            sub = next((l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")), None)
            if sub and (".m3u8" in sub or "#EXT-X-STREAM-INF" in text):
                s2, _, b2, _ = get(urljoin(final, sub), headers)
                if s2 != 200:
                    return False, f"sub HTTP {s2}"
            return True, "m3u8 ok"
        if any(k in ctype for k in ("video", "mpegurl", "octet-stream", "mp2t")) or body[:1] == b"G":
            return True, f"stream ok ({ctype or 'binary'})"
        return False, f"bukan stream ({ctype})"
    except Exception as e:  # timeout, DNS, 403, 404, dsb.
        return False, type(e).__name__ + ": " + str(e)[:60]


def name(entry):
    return entry[0].split(",", 1)[-1] if entry[0].startswith("#EXTINF") else entry[-1]


def main(src, dst, report):
    header, entries = parse(src)
    with cf.ThreadPoolExecutor(max_workers=24) as ex:
        results = list(ex.map(check, entries))
    alive = [e for e, (ok, _) in zip(entries, results) if ok]
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(header + "\n")
        for e in alive:
            f.write("\n".join(e) + "\n")
    with open(report, "w", encoding="utf-8", newline="\n") as f:
        for e, (ok, why) in sorted(zip(entries, results), key=lambda x: (not x[1][0], name(x[0]).lower())):
            f.write(f"{'HIDUP' if ok else 'MATI '}  {name(e)}  |  {why}\n")
    print(f"total {len(entries)}  hidup {len(alive)}  mati {len(entries) - len(alive)}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
