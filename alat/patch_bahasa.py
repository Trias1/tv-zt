"""Patch tv-kita.html: pilihan Bahasa (Indonesia/English) + Zona waktu.

Cara kerja bahasa: teks dasar tetap Indonesia; kalau bahasa = English, lapisan penerjemah (MutationObserver)
mengganti teks tampilan memakai kamus EN di bawah. Nama channel, judul acara, dan subtitle tidak disentuh.
Ganti bahasa = halaman dimuat ulang (nama negara & format angka ikut berganti).
"""
import sys
from pathlib import Path

p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


KAMUS = r'''
  /* ---------- bahasa (Indonesia / English) ---------- */
  // Bahasa dibaca sekali saat aplikasi dibuka (bawaan English untuk versi publik); ganti bahasa = muat ulang.
  const BAHASA = (() => { try { const v = JSON.parse(localStorage.getItem("tvzt.set") || "{}").lang; return v === 0 ? "id" : "en"; } catch { return "en"; } })();
  const LOC = BAHASA === "en" ? "en-US" : "id-ID";
  document.documentElement.lang = BAHASA;
  const EN_PAS = {
    "Memuat channel…": "Loading channels…", "memuat playlist…": "loading playlist…",
    "Terakhir ditonton": "Recently watched", "Channel": "Channels", "Kualitas": "Quality", "daftar channel": "channel list",
    "Semua negara": "All countries", "Playlist saya": "My playlists", "+ Tambah dari link": "+ Add from link", "+ Tambah dari file": "+ Add from file",
    "Pengaturan": "Settings", "Semua gratis.": "Everything is free.", "Tidak ada pilihan yang dikunci versi Premium.": "Nothing is locked behind a Premium version.",
    "Kiri/kanan mengganti nilai. Back kembali ke beranda.": "Left/right changes the value. Back returns home.",
    "Beranda": "Home", "Negara": "Country", "Menonton": "Watching", "Daftar channel": "Channel list", "Suara": "Sound",
    "menyambung…": "connecting…", "lancar": "playing", "gagal": "failed", "berhenti": "stop",
    "Menyambung ke siaran…": "Connecting to the stream…", "Disembunyikan, pindah ke channel berikutnya…": "Hidden, moving to the next channel…",
    "Tekan ▲/▼ untuk pindah channel.": "Press ▲/▼ to change channel.",
    "Server channel ini sedang menolak atau mati. Coba lagi nanti, atau perbarui playlist.": "This channel's server is refusing or down. Try again later, or refresh the playlist.",
    "Kemungkinan server menolak browser (CORS) atau koneksi lewat VPN/IP luar negeri. Di box TV bisa berbeda.": "The server probably refuses browsers (CORS) or foreign VPN/IP connections. It may work on the TV box.",
    "Channel ini butuh header Referer/User-Agent khusus yang tidak bisa dikirim browser. Di aplikasi TV nanti header ini dikirim.": "This channel needs a special Referer/User-Agent header that browsers can't send. The TV app sends it.",
    "hls.js tidak termuat (cek internet)": "hls.js failed to load (check the internet)",
    "Jadwal acara": "Programme guide", "Sekarang": "Now", "Berikutnya": "Next",
    "Cari sinyal": "Signal scan", "Centang kelompok yang mau dicek": "Tick the groups to check", "pilih": "select", "centang": "tick", "tutup": "close",
    "Mencari sinyal…": "Scanning…", "Selesai": "Done", "Pencarian dihentikan": "Scan stopped", "Luar negeri": "Other countries",
    "Channel tanpa sinyal disembunyikan 3 hari (channel nasional tetap tampil).": "Channels without signal are hidden for 3 days (national channels stay visible).",
    "Di browser hasil ini hanya perkiraan; cek sebenarnya dilakukan di box.": "In a browser this is only an estimate; the real check runs on the TV box.",
    "Lanjut menonton · tekan OK untuk layar penuh": "Continue watching · press OK for full screen",
    "Semua channel": "All channels", "Pilih negara dulu": "Pick a country first", "Terakhir:": "Last:", "Belum ada yang ditonton": "Nothing watched yet",
    "● sedang diputar": "● playing", "● diputar": "● playing", "siaran langsung": "live", "tidak 24 jam": "not 24/7", "tidak tersedia": "unavailable",
    "lanjut menonton": "continue watching", "tekan OK untuk layar penuh": "press OK for full screen", "nasional & daerah": "national & regional", "ada jadwal acara": "with TV guide", "sedang diputar": "playing", "▶ Mulai cari": "▶ Start scan", "kartu sendiri di beranda": "own card on the dashboard",
    "Status": "Status", "Header khusus": "Custom headers", "tidak perlu": "not needed", "siap diputar": "ready", "siap diputar · tidak 24 jam": "ready · not 24/7",
    "tonton": "watch", "ganti negara": "change country", "Alternatif": "Alternative",
    "Aplikasi Vidio atau antena digital": "Vidio app or a digital antenna", "Aplikasi RCTI+ atau antena digital": "RCTI+ app or a digital antenna", "Antena digital (DVB-T2)": "Digital antenna (DVB-T2)",
    "belum ada playlist": "no playlists yet", "kartu sendiri di beranda": "own card on the dashboard", "Lihat channel": "View channels",
    "Jadikan kartu": "Make a card", "Gabungkan": "Merge", "Perbarui": "Refresh", "Hapus": "Delete", "Yakin hapus?": "Delete for sure?", "Gagal": "Failed",
    "Belum ada playlist tambahan.": "No extra playlists yet.", "Tambahkan file": "Add a", "dari link (misalnya raw GitHub) atau dari file.": "file from a link (e.g. raw GitHub) or from a file.",
    "Anda bisa memilih tampil sebagai": "You can show it as a", "kartu baru": "new card", "atau": "or", "digabung": "merged", "ke negara yang sudah ada.": "into an existing country.",
    "Tambah dari link": "Add from link", "Tambah dari file": "Add from file", "Link playlist (.m3u)": "Playlist link (.m3u)", "Nama": "Name",
    "Tampilkan sebagai": "Show as", "Kartu baru": "New card", "Simpan": "Save", "Batal": "Cancel",
    "Kiri/kanan di tombol Gabung untuk memilih negara.": "Left/right on the Merge button picks the country.", "Muncul sebagai kartu sendiri di beranda.": "Shows up as its own card on the dashboard.",
    "Link harus diawali http:// atau https://": "The link must start with http:// or https://", "Mengunduh playlist…": "Downloading playlist…",
    "Tidak ada channel di playlist itu. Pastikan isinya format M3U.": "No channels in that playlist. Make sure it is in M3U format.",
    "Penyimpanan penuh. Hapus playlist lain dulu.": "Storage is full. Delete another playlist first.", "File itu tidak berisi channel M3U.": "That file has no M3U channels.",
    "Misalnya: Film Gratis": "e.g. Free Movies",
    // Pengaturan
    "Ukuran buffer": "Buffer size", "Lebih besar = lebih tahan macet, tapi ganti channel sedikit lebih lama": "Bigger = fewer stalls, but channel changes take a bit longer",
    "Normal · 10 dtk": "Normal · 10 s", "Besar · 30 dtk": "Large · 30 s", "Sangat besar · 60 dtk": "Very large · 60 s",
    "Batasi kualitas supaya hemat kuota": "Limit quality to save data", "Otomatis": "Auto",
    "Lanjutkan channel terakhir": "Resume last channel", "Saat membuka kelompok, mulai dari channel yang terakhir ditonton": "When opening a group, start from the last watched channel",
    "Aktif": "On", "Mati": "Off", "Subtitle luar negeri": "Foreign subtitles",
    "Untuk channel yang menyediakan subtitle · terjemahan otomatis lewat Google Translate": "For channels that send subtitles · automatic translation via Google Translate",
    "Terjemahan Indonesia": "Translate to English", "Bahasa asli": "Original language",
    "Channel gagal diputar": "Channels that fail to play", "Disembunyikan 3 hari lalu dicoba lagi · langsung pindah ke channel berikutnya": "Hidden for 3 days, then retried · jumps to the next channel",
    "Sembunyikan & lewati": "Hide & skip", "Tetap tampilkan": "Keep showing", "Channel tidak tersedia": "Unavailable channels",
    "SCTV, Indosiar, dan lainnya yang linknya mati": "SCTV, Indosiar and others with dead links", "Tampilkan abu-abu": "Show greyed out", "Sembunyikan": "Hide",
    "Cari sinyal channel": "Scan channel signals", "Pilih ▶": "Choose ▶",
    "Pilih kelompok (Indonesia, luar negeri, kategori) lalu cek ulang · yang mati disembunyikan, yang hidup lagi dimunculkan": "Pick groups (Indonesia, other countries, categories) and re-check · dead ones are hidden, recovered ones come back",
    "Tambah playlist .m3u dari link atau file, jadi kartu baru atau digabung ke negara": "Add an .m3u playlist from a link or file, as a new card or merged into a country",
    "Pulihkan channel tersembunyi": "Restore hidden channels", "Tampilkan lagi channel yang tadi gagal diputar": "Show the channels that failed earlier again",
    "Zona waktu": "Time zone", "Jam dan jadwal acara mengikuti zona ini": "The clock and programme guide follow this zone", "Otomatis (perangkat)": "Auto (device)",
    // kategori, grup, wilayah
    "Anak & Kartun": "Kids & Cartoons", "Film": "Movies", "Berita & Olahraga": "News & Sports", "Musik": "Music", "Lofi & Santai": "Lo-fi & Relax", "Sub Indo": "Subtitled",
    "Anak": "Kids", "Berita": "News", "Lofi": "Lo-fi", "Nasional": "National", "Daerah": "Regional", "Baitullah & Madinah": "Baitullah & Madinah (live)",
    "Islam Indonesia": "Islam · Indonesia", "Islam Dunia": "Islam · World", "Suara Jepang": "Japanese audio", "Favorit": "Favourites",
    "Musik Indonesia": "Indonesian music", "Musik Barat": "Western music", "Film Indonesia": "Indonesian movies", "Film Hollywood": "Hollywood movies",
    "Dokumenter": "Documentary", "Olahraga": "Sports", "Musik & Santai": "Music & Relax", "Lainnya": "Other", "Semua": "All",
    "Asia Tenggara": "Southeast Asia", "Timur Tengah": "Middle East", "Eropa": "Europe", "Amerika Selatan": "South America",
    "Amerika Utara & Tengah": "North & Central America", "Afrika": "Africa", "Oseania": "Oceania", "Kategori": "Category",
    "paket pilihan Indonesia + internasional": "curated Indonesian + international package", "Baitullah & Madinah live, dakwah, murottal": "live Makkah & Madinah, sermons, Quran recitation",
    "subtitle diterjemahkan ke Indonesia": "subtitles translated to English", "kartun dan acara anak": "cartoons and kids' shows", "film Indonesia & Hollywood": "Indonesian & Hollywood movies",
    "berita dunia dan olahraga": "world news and sports", "musik Indonesia & barat": "Indonesian & Western music", "lofi, jazz, lounge, alam": "lo-fi, jazz, lounge, nature", "playlist saya": "my playlist",
  };
  // Pola per bagian (teks dipecah di " · " lalu tiap bagian diterjemahkan).
  const EN_POLA = [
    [/^([\d.,]+) channel$/, "$1 channels"], [/^([\d.,]+) channel hidup$/, "$1 live channels"], [/^([\d.,]+) negara$/, "$1 countries"],
    [/^([\d.,]+) kelompok$/, "$1 groups"], [/^([\d.,]+)\/([\d.,]+) channel$/, "$1/$2 channels"], [/^([\d.,]+) playlist$/, "$1 playlists"],
    [/^([\d]+) dtk$/, "$1 s"], [/^([\d.,]+) \/ ([\d]+) dtk$/, "$1 / $2 s"], [/^\u00b1([\d]+) menit$/, "~$1 min"],
    [/^Sekarang: /, "Now: "], [/^lalu /, "then "], [/^semua ([\d.,]+) negara$/, "all $1 countries"], [/^Luar$/, "Abroad"],
    [/ sedang tidak bisa diputar$/, " is not playable right now"], [/ belum bisa diputar di browser$/, " can't play in this browser yet"],
    [/^Subtitle: Indonesia$/, "Subtitle: English"], [/^Subtitle: asli$/, "Subtitle: original"], [/^Subtitle: mati$/, "Subtitle: off"], [/^Suara: /, "Audio: "],
    [/^\u25cf ([\d.,]+) ada sinyal$/, "\u25cf $1 with signal"], [/^\u25cf ([\d.,]+) tidak ada sinyal$/, "\u25cf $1 no signal"], [/^\u21ba ([\d.,]+) muncul lagi$/, "\u21ba $1 back again"],
    [/^sisa \u00b1([\d]+) menit \u00b7$/, "about $1 min left \u00b7"], [/^digabung ke /, "merged into "], [/^dari link$/, "from link"], [/^dari file$/, "from file"],
    [/^Gabung ke (.*) \u25c0 \u25b6$/, "Merge into $1 \u25c0 \u25b6"], [/^terakhir (.+)$/, "last $1"], [/^([\d.,]+) hidup$/, "$1 alive"],
    [/^Berita$/, "News"], [/^Olahraga$/, "Sports"],
  ];
  // Teks yang tidak boleh diterjemahkan: nama channel, judul acara, subtitle.
  const JANGAN = "#subs, .ccard .t, .rcard .t, #osdEpg b, #heroName, #osdName, #bufName, .kini, .chead .nm, #detail .t, .plrow .t, .jadwal .r, .lhead";
  function terjemahBagian(x) {
    if (EN_PAS[x] != null) return EN_PAS[x];
    let r = x; for (const [re, ganti] of EN_POLA) r = r.replace(re, ganti);
    return r;
  }
  function terjemahTeks(k) {
    if (EN_PAS[k] != null) return EN_PAS[k];
    if (k.includes(" \u00b7 ")) return k.split(" \u00b7 ").map(terjemahBagian).join(" \u00b7 ");
    return terjemahBagian(k);
  }
  function terjemahSimpul(n) {
    const p = n.parentElement; if (!p || p.classList.contains("li") || p.closest(JANGAN)) return;  // nama channel di daftar = teks langsung di .li
    const s0 = n.nodeValue, k = s0.trim(); if (!k || !/[a-z]/i.test(k)) return;
    const r = terjemahTeks(k); if (r !== k) n.nodeValue = s0.replace(k, r);
  }
  function terjemahDi(root) {
    if (root.nodeType === 3) { terjemahSimpul(root); return; }
    if (root.nodeType !== 1) return;
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT); let n;
    while ((n = w.nextNode())) terjemahSimpul(n);
    for (const el of root.querySelectorAll ? root.querySelectorAll("input[placeholder]") : []) { const t = terjemahTeks(el.placeholder); if (t !== el.placeholder) el.placeholder = t; }
  }
  if (BAHASA === "en") {
    terjemahDi(document.body);
    new MutationObserver((ms) => { for (const m of ms) { if (m.type === "characterData") terjemahSimpul(m.target); else for (const a of m.addedNodes) terjemahDi(a); } })
      .observe(document.body, { childList: true, subtree: true, characterData: true });
  }

  /* ---------- zona waktu ---------- */
  const ZONA = [["Otomatis (perangkat)", ""], ["WIB · Jakarta", "Asia/Jakarta"], ["WITA · Makassar", "Asia/Makassar"], ["WIT · Jayapura", "Asia/Jayapura"],
    ["Singapore / Kuala Lumpur", "Asia/Singapore"], ["Tokyo", "Asia/Tokyo"], ["Riyadh / Makkah", "Asia/Riyadh"], ["Dubai", "Asia/Dubai"],
    ["London", "Europe/London"], ["Berlin / Paris", "Europe/Berlin"], ["New York", "America/New_York"], ["Los Angeles", "America/Los_Angeles"], ["Sydney", "Australia/Sydney"], ["UTC", "UTC"]];
  const zonaIANA = () => { const z = ZONA[(S && S.set && S.set.tz) || 0]; return (z && z[1]) || Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Jakarta"; };
  function labelZona() {
    const z = zonaIANA(), id = { "Asia/Jakarta": "WIB", "Asia/Pontianak": "WIB", "Asia/Makassar": "WITA", "Asia/Jayapura": "WIT" }[z];
    if (id) return id;
    try { return new Intl.DateTimeFormat(LOC, { timeZone: z, timeZoneName: "short" }).formatToParts(new Date()).find((x) => x.type === "timeZoneName").value; } catch { return ""; }
  }
'''

# Sisipkan setelah namaNegara (store sudah ada); namaNegara memakai bahasa aktif.
rep('    let dn = null; try { dn = new Intl.DisplayNames(["id"], { type: "region" }); } catch {}',
    '    let dn = null; try { dn = new Intl.DisplayNames([BAHASA], { type: "region" }); } catch {}')
rep("  const namaNegara = (() => {", KAMUS + "\n  const namaNegara = (() => {")

# Angka & jam mengikuti bahasa dan zona
s = s.replace('toLocaleString("id-ID")', "toLocaleString(LOC)")
rep('  const jam = (ms) => new Date(ms).toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit", hour12: false, timeZone: "Asia/Jakarta" });',
    '  const jam = (ms) => new Date(ms).toLocaleTimeString(LOC, { hour: "2-digit", minute: "2-digit", hour12: false, timeZone: zonaIANA() });')
rep('  const fmt = new Intl.DateTimeFormat("id-ID", { hour: "2-digit", minute: "2-digit", timeZone: "Asia/Jakarta" });',
    '  const fmtJam = () => new Intl.DateTimeFormat(LOC, { hour: "2-digit", minute: "2-digit", hour12: false, timeZone: zonaIANA() });')
rep('  const tick = () => { const t = fmt.format(new Date()).replace(".", ":");', '  const tick = () => { const t = fmtJam().format(new Date()).replace(".", ":"), zl = labelZona();')
s = s.replace("<small>WIB</small>", "<small>${zl}</small>")

# Pengaturan: Bahasa & Zona waktu
rep('set: { buffer: 1, quality: 0, resume: 0, showOff: 0, subs: 0, failShow: 0 } };',
    'set: { buffer: 1, quality: 0, resume: 0, showOff: 0, subs: 0, failShow: 0, lang: 1, tz: 0 } };')
rep('  const OPTS = {\n', '''  const OPTS = {
    lang: { label: "Bahasa / Language", help: "Indonesia atau English · aplikasi dimuat ulang", vals: ["Indonesia", "English"] },
    tz: { label: "Zona waktu", help: "Jam dan jadwal acara mengikuti zona ini", vals: ZONA.map((z) => z[0]) },
''')
rep('    if (k === "subs") terapkanSub();', '    if (k === "subs") terapkanSub();\n    if (k === "lang") { setTimeout(() => location.reload(), 300); }\n    if (k === "tz") { tick(); isiAcara(); }')

# Subtitle diterjemahkan ke bahasa aktif; label tanda SUB
rep('&tl=id&dt=t&q=', '&tl=${BAHASA}&dt=t&q=')
s = s.replace('"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=${BAHASA}&dt=t&q="', '`https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=${BAHASA}&dt=t&q=`')
rep('`<span class="subid">SUB ID</span>`', '`<span class="subid">${BAHASA === "en" ? "SUB EN" : "SUB ID"}</span>`')
rep('<span class="subid besar" id="osdSub" hidden>SUB ID</span>', '<span class="subid besar" id="osdSub" hidden>SUB</span>')

p.write_text(s, encoding="utf-8")
print("patch bahasa OK")
