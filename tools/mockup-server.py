"""Server lokal untuk membuka mockup TV ZT di browser laptop, plus /api/ram (RAM laptop asli).

Pemakaian (dari folder proyek):  python -I tools/mockup-server.py [port]
Lalu buka http://localhost:8765/tv-zt.html atau tv-zt-tema.html.

Hanya mendengarkan 127.0.0.1 (tidak bisa dibuka dari perangkat lain). Panel RAM di Pengaturan mockup
memakai /api/ram kalau ada; dengan server statis biasa panel itu kembali ke angka contoh.
"""
import ctypes
import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MOCKUP = Path(__file__).resolve().parent.parent / "mockup"


def ram_laptop():
    """(total, tersedia) dalam byte."""
    if os.name == "nt":
        class Status(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        st = Status(); st.dwLength = ctypes.sizeof(Status)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st))
        return st.ullTotalPhys, st.ullAvailPhys
    info = {}
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            k, v = line.split(":", 1); info[k] = int(v.split()[0]) * 1024
        return info["MemTotal"], info.get("MemAvailable", info.get("MemFree", 0))
    except OSError:
        total = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        return total, 0


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(MOCKUP), **kw)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")  # mockup selalu versi terbaru setelah diedit
        super().end_headers()

    def do_GET(self):
        if self.path.split("?")[0] == "/api/ram":
            total, sisa = ram_laptop()
            body = json.dumps({"memTotal": total, "memAvail": sisa}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"Mockup TV ZT: http://localhost:{port}/tv-zt.html  (RAM laptop: /api/ram)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
