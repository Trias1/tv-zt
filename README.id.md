# TV ZT — IPTV gratis untuk STB Android TV bekas (ZTE B860H)

[![English](https://img.shields.io/badge/lang-English-2f81f7?style=for-the-badge)](README.md) [![Bahasa Indonesia](https://img.shields.io/badge/bahasa-Indonesia-d1242f?style=for-the-badge)](README.id.md)

Proyek oprek STB bekas IndiHome **ZTE B860H V5** (Android TV 10, RAM 2 GB) jadi TV internet yang bersih dan enak dipakai keluarga:

- **TV ZT** — aplikasi IPTV buatan sendiri (Java WebView + HTML/hls.js) untuk ribuan channel gratis dari [iptv-org](https://github.com/iptv-org/iptv).
- **Tema launcher** untuk [cleanyourtv](https://github.com/Gathin23/cleanyourtv), supaya beranda bebas iklan "Bersponsor".
- **Script Python** untuk menyusun, mengaudit, dan memperbarui daftar channel.

## Fitur TV ZT

- ±9.700 channel hidup dari ±170 negara (link yang mati dibuang lewat audit otomatis)
- TV nasional Indonesia (TVRI, Trans TV, Trans7, MNCTV, GTV, Metro TV, tvOne, iNews, dll.) dengan **jadwal acara** dan daftar "sedang tayang"
- Dashboard + navbar kategori: **Indonesia, Pilihan** (paket channel pilihan), **Islam** (live Makkah & Madinah), **Sub Indo, Anime, Anak, Film** (Hollywood), **Berita & Olahraga, Musik** (Indonesia & barat), **Lofi & Santai**, **Luar negeri**
- **Subtitle otomatis diterjemahkan ke bahasa Indonesia** untuk channel luar negeri yang mengirim subtitle teks (tanda **SUB ID**)
- Logo channel, layar pembuka, navigasi penuh pakai remote D-pad, ▲▼ ganti channel seperti TV biasa
- **Cari sinyal**: cek ulang channel per kelompok langsung dari box; yang mati disembunyikan otomatis, yang hidup lagi dimunculkan
- Playlist sendiri (.m3u dari link/file), bisa jadi kartu baru atau digabung ke negara — **logo terdeteksi otomatis** (`tvg-logo` atau dicocokkan dari nama channel) dan ikut tampil di **navbar**
- **Bola**: channel sepak bola dari playlist sendiri dikumpulkan jadi satu grup di navbar — tanpa bola wanita, olahraga lain, laga yang sudah lewat, atau nama dobel; laga live di paling atas
- **Ping & kecepatan** di baris info (mis. *Ping 53 ms · 5.2 MB/s*, merah kalau terlalu lambat), plus pemberitahuan **"server lambat"** kalau channel macet buffering 15 detik
- **Memberi tahu penyebab** channel lambat atau gagal, plus sarannya: server jauh & jalur luar negeri padat, channel hanya 1 kualitas, internet rumah lambat, atau server menolak (403), link hilang (404), membatasi penonton (429), server error (5xx)
- **Pengaturan per tab** (Tampilan · Pemutaran · Channel) dengan **lingkaran RAM** (RAM bawaan, TV ZT, aplikasi lain, sisa), kuota terpakai TV ZT, dan **Bersihkan cache**
- **Bahasa: Indonesia atau English** (Pengaturan → *Bahasa / Language*); versi publik bawaannya English
- **Zona waktu**: jam dan jadwal acara mengikuti zona pilihan — Otomatis (perangkat), WIB/WITA/WIT, atau zona negara lain
- Ringan untuk box 2 GB: daftar panjang dimuat bertahap, animasi berat dimatikan di box, siaran berhenti total di Dashboard

## Tema

Pilih tema di **Pengaturan → Tampilan** (mulai v1.4). Angka RAM diukur di ZTE B860H 2 GB, dibandingkan dengan tema Hemat (masing-masing sekali ukur, jadi anggap angka kira-kira).

| Tema | Tampilan | RAM tambahan |
|---|---|---|
| **Default** | Kartu grup dengan logo (tampilan klasik) | ±10 MB |
| **Konsol** | Gaya konsol game: deretan kotak grup di atas, latar besar, kartu channel di bawah | ±15 MB |
| **Streaming** | Banner besar channel yang disorot + baris channel yang bisa digeser | ±15 MB |
| **Bioskop** | Gaya aplikasi streaming: menu kiri, banner berganti, kotak grup, baris channel | ±25 MB |
| **Hemat** | Tanpa logo & hiasan — paling ringan | patokan |

- **Warna aksen**: emas, biru, hijau, ungu, atau merah.
- **Nama TV**: ganti tulisan "TV ZT" di pojok kiri atas dan layar pembuka dengan nama sendiri.
- **Latar tema**: **Gambar** (bawaan, ±0 MB) atau **Siaran live** — channel yang disorot diputar di latar Dashboard, maks. 360p kalau channel punya beberapa kualitas (**terukur: RAM tambahan ±70 MB di 360p, ±120 MB untuk channel yang hanya 1080p; kuota ±150–250 MB per jam, channel 1080p ±1,4 GB per jam**). Saat dinyalakan ada konfirmasi Ya/Tidak, dan kalau box mulai patah-patah (gambar terlewat, layar tersendat, atau sisa RAM < 200 MB) TV ZT menawarkan kembali ke Gambar; pilih "Tidak" = ditanya lagi setelah 5 menit.
- Di tema Konsol, Streaming, dan Bioskop, memilih grup atau channel **langsung layar penuh**; Back kembali ke Dashboard.

## Cara pasang (tanpa root, tanpa laptop)

Unduh **[TV-ZT-v1.4.1.apk](https://github.com/Trias1/tv-zt/releases/latest)** dari halaman Releases. Bisa dipasang di TV/STB Android 7 ke atas.

1. Di TV/STB, pasang **File Manager+** dan **Send Files to TV** dari Play Store. Di HP, pasang juga **Send Files to TV**.
2. Unduh `TV-ZT-v1.4.1.apk` di HP.
3. Kirim ke TV: di TV buka *Send Files to TV* → **Receive**; di HP *Send Files to TV* → **Send** → pilih APK → pilih TV. (Atau pakai flashdisk.)
4. Izinkan pemasangan: **Setelan → Aplikasi → Akses aplikasi khusus → Instal aplikasi tidak dikenal → File Manager+ → Izinkan**.
5. Buka **File Manager+** → folder *Download* → pilih APK → **Instal** (kalau Play Protect memperingatkan, pilih **Tetap instal**).
6. Buka **TV ZT** dari daftar aplikasi. TV harus tersambung ke internet.

Lewat laptop: `adb connect <ip-tv>:5555` lalu `adb install -r TV-ZT-v1.4.1.apk`.

## Cara pakai

| Tombol remote | Fungsi |
|---|---|
| ▲ ▼ ◀ ▶ + **OK** di Dashboard | pilih kelompok: Indonesia, Islam, Musik, Film, dll. |
| **▲** dari video beranda | naik ke navbar untuk pindah kategori |
| **OK** di video beranda | tonton layar penuh |
| **▲ / ▼** saat menonton | channel berikutnya / sebelumnya |
| **OK** saat menonton | daftar channel + jadwal acara |
| **◀ / ▶** saat menonton | subtitle (Indonesia/asli/mati) / bahasa suara |
| **Back** | kembali (di Dashboard: keluar) |
| **Menu** / ikon ⚙ | Pengaturan: kualitas, buffer, subtitle, **Cari sinyal**, Playlist saya |

## Masalah umum & cara memperbaiki

| Masalah | Cara memperbaiki |
|---|---|
| **APK tidak mau terpasang** ("Aplikasi tidak terpasang") | Izinkan File Manager+ memasang aplikasi: *Setelan → Aplikasi → Akses aplikasi khusus → Instal aplikasi tidak dikenal → File Manager+ → Izinkan*. Pastikan memori kosong minimal 50 MB. Kalau sebelumnya sudah ada TV ZT dari sumber lain, hapus dulu lalu pasang ulang. |
| **Muncul peringatan Play Protect** | Pilih **Tetap instal**. TV ZT tidak dari Play Store, jadi peringatan ini wajar. |
| **TV ZT tidak muncul di daftar aplikasi** | Cari di menu **Aplikasi / Semua aplikasi** TV. TV ZT dibuat untuk **Android TV / STB** (pakai remote), bukan untuk HP. |
| **Lama di layar "Memuat channel…"** | Cek internet TV (buka YouTube). Tutup TV ZT lalu buka lagi. Kalau tetap, hapus data: *Setelan → Aplikasi → TV ZT → Hapus data*, lalu buka ulang. |
| **Channel tidak bisa diputar** (pesan *manifestLoadError*, *HTTP 403/404*) | Link channel itu sedang mati. Tekan **▲/▼** untuk pindah channel; TV ZT otomatis menyembunyikan channel mati selama 3 hari. Untuk cek banyak channel sekaligus: **Pengaturan → Cari sinyal channel**. Matikan VPN kalau ada, karena beberapa channel menolak koneksi luar negeri. |
| **Siaran patah-patah / sering buffering** | *Pengaturan → Ukuran buffer → Besar* atau *Sangat besar*; *Pengaturan → Kualitas → 720p* atau *480p*. Dekatkan STB ke router atau pakai kabel LAN, lalu restart STB. |
| **Tidak ada suara** | Tekan tombol apa saja di remote sekali (suara aktif setelah tombol pertama). Cek volume TV. Kalau channel punya beberapa bahasa, tekan **▶** saat menonton. |
| **Subtitle Indonesia tidak muncul** | Hanya untuk channel bertanda **SUB ID**. Tekan **◀** saat menonton sampai tertulis *Subtitle: Indonesia*. Subtitle yang menempel di gambar (mis. Boruto) tidak bisa diterjemahkan. |
| **Jadwal acara kosong** | Jadwal hanya untuk channel Indonesia, diambil dari internet beberapa detik setelah aplikasi dibuka dan diperbarui tiap 6 jam. Tunggu sebentar atau buka ulang aplikasi. |
| **Logo channel tidak muncul** | Logo diunduh saat pertama dibuka, jadi butuh internet. Sebagian channel memang tidak punya logo; yang ditampilkan nomor dan namanya saja. |
| **Channel yang dicari hilang dari daftar** | Kemungkinan tersembunyi otomatis karena sempat mati. Buka *Pengaturan → Pulihkan channel tersembunyi*, atau ubah *Pengaturan → Channel gagal diputar → Tetap tampilkan*. |
| **Tekan Back aplikasi tertutup** | Di **Dashboard**, Back memang menutup aplikasi. Di layar lain, Back kembali ke layar sebelumnya. |
| **Mau mulai dari channel terakhir yang ditonton** | *Pengaturan → Lanjutkan channel terakhir → Aktif*. |
| **Masih error setelah update versi baru** | Hapus TV ZT (*Setelan → Aplikasi → TV ZT → Uninstal*), lalu pasang APK terbaru dari halaman Releases. |

Kalau sudah mencoba cara di atas tapi masalahnya belum beres, laporkan lewat bagian berikutnya.

## Masih bermasalah? Lapor / usul

Masih bermasalah atau punya ide? Buka **[Issues → New issue](https://github.com/Trias1/tv-zt/issues/new/choose)** (perlu akun GitHub gratis), lalu pilih:

- 🐞 **Report a bug** (lapor masalah): aplikasi error, tidak bisa dipasang, macet, tombol remote tidak jalan
- 📺 **Broken / wrong channel** (channel mati/salah): channel tidak bisa diputar, isinya tidak sesuai, logo atau jadwal keliru
- 💡 **Suggest a feature / channel** (usul): ide fitur baru atau link channel gratis

Isi kolom yang disediakan (perangkat, versi TV ZT, langkah sampai masalah muncul) dan lampirkan foto layar kalau bisa. Sebelum melapor channel mati, coba dulu **Pengaturan → Cari sinyal channel**, karena link dari iptv-org kadang mati sementara. Jangan tulis data pribadi di laporan, karena laporan bisa dilihat semua orang.

## Struktur

| Folder | Isi |
|---|---|
| `tvzt/` | Proyek Android TV ZT (`MainActivity.java`: WebView, header Referer/User-Agent per channel, remote, layar pembuka, cek sinyal) |
| `mockup/` | Tampilan TV ZT (`tv-zt.html`, bisa dibuka di browser; `python tools/mockup-server.py` sekalian menampilkan RAM asli laptop di Pengaturan), penyusun data (`build_channels.py`, `categories.py`, `logo.py`) |
| `iptv/` | Script data: `build_all.py` (semua negara), `build_national.py` (TV nasional), `audit.py` (cek mendalam), `check_subtitles.py` (subtitle), `check_logos.py`, `update-playlist.ps1` |
| `launcher-theme/` | `config.json` tema launcher cleanyourtv (wallpaper tidak ikut diunggah) |
| `wallpaper/` | Script pembuat wallpaper dari foto sendiri |
| `tools/` | Alat uji: menjalankan JavaScript di WebView TV ZT lewat ADB + Chrome DevTools Protocol |

## Build & pasang

Kebutuhan: Python 3 (+ Pillow), JDK 17+, Android SDK, ADB.

```powershell
# 1. (opsional) susun ulang data channel — butuh internet
python -I iptv\build_all.py
python -I mockup\build_channels.py

# 2. salin tampilan ke aplikasi + buat ikon, lalu build
cd tvzt
python prepare.py
.\gradlew.bat assembleRelease

# 3. pasang ke box lewat ADB jaringan
adb connect <ip-box>:5555
adb install -r app\build\outputs\apk\release\app-release.apk
```

Pembaruan rutin channel nasional: `iptv\update-playlist.ps1` (tambahkan `-Audit` untuk audit semua negara + cek subtitle, ±40 menit).

## Catatan

- TV ZT **tidak menyimpan atau menyiarkan ulang video**; aplikasi hanya memutar link publik dari iptv-org. Sebagian link adalah siaran ulang tidak resmi dan bisa mati sewaktu-waktu — gunakan dengan bijak.
- Jangan menonaktifkan semua launcher bawaan di box ZTE (bisa memicu reset pabrik); cukup arahkan tombol Home ke launcher baru.
- Dibuat dengan bantuan Claude (Anthropic).

## Lisensi

[MIT](LICENSE) © 2026 Trias. Komponen pihak ketiga (hls.js, data iptv-org) mengikuti lisensinya masing-masing — lihat [NOTICE.md](NOTICE.md).
