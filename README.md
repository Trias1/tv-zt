# TV ZT — IPTV gratis untuk STB Android TV bekas (ZTE B860H)

Proyek oprek STB bekas IndiHome **ZTE B860H V5** (Android TV 10, RAM 2 GB) jadi TV internet yang bersih dan enak dipakai keluarga:

- **TV ZT** — aplikasi IPTV buatan sendiri (Java WebView + HTML/hls.js) untuk ribuan channel gratis dari [iptv-org](https://github.com/iptv-org/iptv).
- **Tema launcher** untuk [cleanyourtv](https://github.com/Gathin23/cleanyourtv), supaya beranda bebas iklan "Bersponsor".
- **Script Python** untuk menyusun, mengaudit, dan memperbarui daftar channel.

## Fitur TV ZT

- ±9.700 channel hidup dari ±170 negara (link yang mati dibuang lewat audit otomatis)
- TV nasional Indonesia (TVRI, Trans TV, Trans7, MNCTV, GTV, Metro TV, tvOne, iNews, dll.) dengan **jadwal acara** dan daftar "sedang tayang"
- Dashboard + navbar kategori: **Indonesia, Indovision** (paket pilihan), **Islam** (live Makkah & Madinah), **Sub Indo, Anime, Anak, Film** (Hollywood), **Berita & Olahraga, Musik** (Indonesia & barat), **Lofi & Santai**, **Luar negeri**
- **Subtitle otomatis diterjemahkan ke bahasa Indonesia** untuk channel luar negeri yang mengirim subtitle teks (tanda **SUB ID**)
- Logo channel, layar pembuka, navigasi penuh pakai remote D-pad, ▲▼ ganti channel seperti TV biasa
- **Cari sinyal**: cek ulang channel per kelompok langsung dari box; yang mati disembunyikan otomatis, yang hidup lagi dimunculkan
- Playlist sendiri (.m3u dari link/file), bisa jadi kartu baru atau digabung ke negara
- Ringan untuk box 2 GB: daftar panjang dimuat bertahap, animasi berat dimatikan di box, siaran berhenti total di Dashboard

## Cara pasang (tanpa root, tanpa laptop)

Unduh **[TV-ZT-v1.0.apk](https://github.com/Trias1/tv-zt/releases/latest)** dari halaman Releases. Bisa dipasang di TV/STB Android 7 ke atas.

1. Di TV/STB, pasang **File Manager+** dan **Send Files to TV** dari Play Store. Di HP, pasang juga **Send Files to TV**.
2. Unduh `TV-ZT-v1.0.apk` di HP.
3. Kirim ke TV: di TV buka *Send Files to TV* → **Receive**; di HP *Send Files to TV* → **Send** → pilih APK → pilih TV. (Atau pakai flashdisk.)
4. Izinkan pemasangan: **Setelan → Aplikasi → Akses aplikasi khusus → Instal aplikasi tidak dikenal → File Manager+ → Izinkan**.
5. Buka **File Manager+** → folder *Download* → pilih APK → **Instal** (kalau Play Protect memperingatkan, pilih **Tetap instal**).
6. Buka **TV ZT** dari daftar aplikasi. TV harus tersambung ke internet.

Lewat laptop: `adb connect <ip-tv>:5555` lalu `adb install -r TV-ZT-v1.0.apk`.

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

## Lapor masalah / usul

Ketemu masalah atau punya ide? Buka **[Issues → New issue](https://github.com/Trias1/tv-zt/issues/new/choose)** (perlu akun GitHub gratis), lalu pilih:

- 🐞 **Lapor masalah**: aplikasi error, tidak bisa dipasang, macet, tombol remote tidak jalan
- 📺 **Channel mati / salah**: channel tidak bisa diputar, isinya tidak sesuai, logo atau jadwal keliru
- 💡 **Usul fitur / channel**: ide fitur baru atau link channel gratis

Isi kolom yang disediakan (perangkat, versi TV ZT, langkah sampai masalah muncul) dan lampirkan foto layar kalau bisa. Sebelum melapor channel mati, coba dulu **Pengaturan → Cari sinyal channel**, karena link dari iptv-org kadang mati sementara. Jangan tulis data pribadi di laporan, karena laporan bisa dilihat semua orang.

## Struktur

| Folder | Isi |
|---|---|
| `tvzt/` | Proyek Android TV ZT (`MainActivity.java`: WebView, header Referer/User-Agent per channel, remote, layar pembuka, cek sinyal) |
| `mockup/` | Tampilan TV ZT (`tv-kita.html`, bisa dibuka di browser), penyusun data (`buat_channels.py`, `kategori.py`, `logo.py`) |
| `iptv/` | Script data: `buat_semua.py` (semua negara), `buat_nasional.py` (TV nasional), `audit.py` (cek mendalam), `cek_sub.py` (subtitle), `cek_logo.py`, `update-playlist.ps1` |
| `tema-ringan/` | `config.json` tema launcher cleanyourtv (wallpaper tidak ikut diunggah) |
| `wallpaper/` | Script pembuat wallpaper dari foto sendiri |
| `alat/` | Alat uji: menjalankan JavaScript di WebView TV ZT lewat ADB + Chrome DevTools Protocol |

## Build & pasang

Kebutuhan: Python 3 (+ Pillow), JDK 17+, Android SDK, ADB.

```powershell
# 1. (opsional) susun ulang data channel — butuh internet
python -I iptv\buat_semua.py
python -I mockup\buat_channels.py

# 2. salin tampilan ke aplikasi + buat ikon, lalu build
cd tvzt
python siapkan.py
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
