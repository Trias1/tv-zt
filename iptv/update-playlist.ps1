# Perbarui playlist TV Indonesia: unduh dari iptv-org, tes setiap channel, kirim yang hidup ke box.
# Pemakaian (dari folder ini):  .\update-playlist.ps1          (cepat, channel Indonesia saja)
#                               .\update-playlist.ps1 -Audit   (plus audit semua negara & cek subtitle, ~40 menit)
# Syarat: ADB jaringan box sedang terbuka (192.168.1.4:5555) dan Python ada di PATH.
param([string]$TvHost = '192.168.1.4:5555', [switch]$Audit)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

Write-Host 'Mengunduh playlist iptv-org...'
Invoke-WebRequest -UseBasicParsing -TimeoutSec 60 -Uri 'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/id.m3u' -OutFile 'id.m3u'

Write-Host 'Mengetes setiap channel (sekitar 20 detik)...'
python -I .\cek_m3u.py id.m3u id-aktif.m3u laporan-cek.txt
if ($LASTEXITCODE -ne 0) { throw 'Tes channel gagal' }

Write-Host 'Mengetes channel nasional yang sedang tayang (sekitar 30 detik)...'
python -I .\buat_nasional.py id.m3u id-nasional.m3u laporan-nasional.txt
if ($LASTEXITCODE -ne 0) { throw 'Tes channel nasional gagal' }

Write-Host 'Memperbarui data prototipe HTML (mockup\tv-kita.html)...'
python -I ..\mockup\buat_channels.py | Out-Null

if ($Audit) {
    # Audit mendalam semua channel (~25 menit) + cek subtitle teks, lalu susun ulang data.
    Write-Host 'Audit semua channel (sekitar 25 menit)...'
    python -I .\audit.py 48
    Write-Host 'Mencari channel bersubtitle...'
    python -I .\cek_sub.py 24
    python -I .\cek_sub.py --verifikasi 64
    python -I ..\mockup\buat_channels.py
}

adb connect $TvHost | Out-Null
adb -s $TvHost push id-aktif.m3u /sdcard/Download/id-aktif.m3u
adb -s $TvHost push id-nasional.m3u /sdcard/Download/id-nasional.m3u
# TV ZT membaca playlist dari folder aplikasinya sendiri; dibaca ulang setiap aplikasi dibuka.
adb -s $TvHost shell mkdir -p /sdcard/Android/data/id.zt.tv/files
adb -s $TvHost push id-nasional.m3u /sdcard/Android/data/id.zt.tv/files/playlist.m3u
if ($LASTEXITCODE -ne 0) { throw "Gagal kirim ke box; cek ADB di $TvHost" }
adb -s $TvHost shell am force-stop id.zt.tv | Out-Null
Write-Host 'Selesai. TV ZT langsung memakai playlist baru saat dibuka lagi.'
Write-Host 'Catatan: jalankan dengan WARP/VPN mati, supaya channel RCTI+ (MNCTV, iNews, GTV) lolos tes.'
