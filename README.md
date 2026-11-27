# TV ZT — free IPTV for second-hand Android TV boxes (ZTE B860H)

[![English](https://img.shields.io/badge/lang-English-2f81f7?style=for-the-badge)](README.md) [![Bahasa Indonesia](https://img.shields.io/badge/bahasa-Indonesia-d1242f?style=for-the-badge)](README.id.md)

A weekend project that turns a second-hand IndiHome **ZTE B860H V5** set-top box (Android TV 10, 2 GB RAM) into a clean, family-friendly internet TV:

- **TV ZT** — a home-made IPTV app (Java WebView + HTML/hls.js) for thousands of free channels from [iptv-org](https://github.com/iptv-org/iptv). The app UI is available in English and Indonesian.
- **A launcher theme** for [cleanyourtv](https://github.com/Gathin23/cleanyourtv), so the home screen has no "Sponsored" ads.
- **Python scripts** that build, audit and refresh the channel list.

## Features

- ~9,700 live channels from ~170 countries; dead links are removed by an automated deep audit (playlist → variant → video segment)
- Indonesian national TV (TVRI, Trans TV, Trans7, MNCTV, GTV, Metro TV, tvOne, iNews, …) with a **programme guide (EPG)** and a "now playing" list
- Dashboard + navbar categories: **Indonesia, Top Picks** (curated package), **Islam** (live Makkah & Madinah), **Subtitled, Anime, Kids, Movies** (Hollywood), **News & Sports, Music** (Indonesian & Western), **Lo-fi & Relax**, **All countries**
- **Automatic subtitle translation** into the app language for foreign channels that send text subtitles (WebVTT / CEA-608), marked **SUB EN** / **SUB ID**
- Channel logos, splash screen, full D-pad remote navigation, ▲▼ channel zapping like a regular TV
- **Signal scan**: tick the groups you want and re-check them directly from the box; dead channels are hidden for 3 days, recovered ones come back
- Your own .m3u playlists (from a URL or file), as a new card or merged into a country — with **logos detected automatically** (`tvg-logo`, or matched by channel name) and a place in the **navbar**
- **Bola (football)**: football channels gathered from your own playlists into one navbar group — no women's football, other sports, past matches or duplicates; live matches on top
- **Ping & speed** in the info bar (e.g. *Ping 53 ms · 5.2 MB/s*, red when too slow), and a **"server is slow"** notice when a channel is stuck buffering for 15 s
- **Tells you why** a channel is slow or fails, with a tip: far-away server on a busy international route, single-quality channel, slow home network, or the server refusing (403), gone (404), limiting viewers (429) or erroring (5xx)
- **Settings in tabs** (Display · Playback · Channels) with a **RAM ring** (built-in RAM, TV ZT, other apps, free), data used by TV ZT, and **Clear cache**
- **Language: English or Indonesian** (Settings → *Bahasa / Language*); English by default
- **Time zone**: clock and programme guide follow your zone — Auto (device), WIB/WITA/WIT, Singapore, Tokyo, Makkah, Dubai, London, Berlin, New York, Los Angeles, Sydney or UTC
- Tuned for a 2 GB box: lazy-loaded long lists, heavy animations disabled on-device, playback fully stopped on the dashboard

## Themes

Pick a theme in **Settings → Display** (since v1.4). The RAM figures were measured on a 2 GB ZTE B860H, compared with Hemat (one measurement each, so treat them as approximate).

| Theme | Look | Extra RAM |
|---|---|---|
| **Default** | Group cards with logos (the classic look) | ±10 MB |
| **Konsol** | Console-style: a row of group tiles on top, a big background, channel cards below | ±15 MB |
| **Streaming** | A large banner for the highlighted channel + scrollable channel rows | ±15 MB |
| **Bioskop** | Streaming-app style: side menu, rotating banner, group tiles, channel rows | ±25 MB |
| **Hemat** | No logos or decoration — the lightest | baseline |

- **Accent colour**: gold, blue, green, purple or red.
- **TV name**: replace "TV ZT" in the top-left corner and on the splash screen with your own name.
- **Theme background**: **Image** (default, ±0 MB) or **Live broadcast** — the highlighted channel plays behind the dashboard at max 360p when the channel offers several qualities (**measured: ±70 MB extra RAM at 360p, ±120 MB for 1080p-only channels; data ±150–250 MB per hour, 1080p channels ±1.4 GB per hour**). Turning it on asks Yes/No first, and if the box starts stuttering (dropped frames, slow screen, or under 200 MB RAM free) TV ZT offers to switch back to Image; "No" waits 5 minutes before asking again.
- In Konsol, Streaming and Bioskop, picking a group or channel goes **straight to full screen**; Back returns to the dashboard.

## Install (no root, no computer)

Download **[TV-ZT-v1.4.1.apk](https://github.com/Trias1/tv-zt/releases/latest)** from Releases. Works on Android TV / Android set-top boxes running Android 7.0 or newer.

1. On the TV/box, install **File Manager+** and **Send Files to TV** from the Play Store. Install **Send Files to TV** on your phone too.
2. Download `TV-ZT-v1.4.1.apk` on your phone.
3. Send it to the TV: on the TV open *Send Files to TV* → **Receive**; on the phone *Send Files to TV* → **Send** → pick the APK → pick the TV. (A USB stick works too.)
4. Allow installs: **Settings → Apps → Special app access → Install unknown apps → File Manager+ → Allow**.
5. Open **File Manager+** → *Download* folder → select the APK → **Install** (if Play Protect warns you, choose **Install anyway**).
6. Open **TV ZT** from the app list. The TV needs an internet connection.

With a computer: `adb connect <tv-ip>:5555` then `adb install -r TV-ZT-v1.4.1.apk`.

## How to use

| Remote button | Action |
|---|---|
| ▲ ▼ ◀ ▶ + **OK** on the Dashboard | pick a group: Indonesia, Islam, Music, Movies, … |
| **▲** from the home video | go up to the navbar to switch category |
| **OK** on the home video | watch full screen |
| **▲ / ▼** while watching | next / previous channel |
| **OK** while watching | channel list + programme guide |
| **◀ / ▶** while watching | subtitles (translated/original/off) / audio language |
| **Back** | go back (on the Dashboard: exit) |
| **Menu** / ⚙ icon | Settings: quality, buffer, subtitles, **signal scan**, my playlists |

## Troubleshooting

| Problem | Fix |
|---|---|
| **The APK won't install** ("App not installed") | Allow File Manager+ to install apps: *Settings → Apps → Special app access → Install unknown apps → File Manager+ → Allow*. Keep at least 50 MB free. If an older TV ZT from another source is installed, uninstall it first. |
| **Play Protect warning** | Choose **Install anyway**. TV ZT is not on the Play Store, so this warning is expected. |
| **TV ZT is not in the app list** | Look under **Apps / All apps**. TV ZT is made for **Android TV / set-top boxes** (remote control), not phones. |
| **Stuck on "Loading channels…"** | Check the TV's internet (try YouTube). Close and reopen TV ZT. If it persists: *Settings → Apps → TV ZT → Clear data*, then reopen. |
| **A channel won't play** (*manifestLoadError*, *HTTP 403/404*) | That link is down. Press **▲/▼** to change channel; TV ZT hides dead channels for 3 days. To check many at once: **Settings → Scan channel signals**. Turn off any VPN — some channels block foreign connections. |
| **Stuttering / constant buffering** | *Settings → Buffer size → Large* or *Very large*; *Settings → Quality → 720p* or *480p*. Move the box closer to the router or use a LAN cable, then restart the box. |
| **No sound** | Press any button on the remote once (sound turns on after the first key). Check the TV volume. If a channel has several languages, press **▶** while watching. |
| **Translated subtitles don't show** | Only for channels marked **SUB EN** / **SUB ID**. Press **◀** while watching until the translated subtitle is selected. Subtitles burned into the picture (e.g. Boruto) cannot be translated. |
| **Programme guide is empty** | The guide covers Indonesian channels only; it is fetched a few seconds after start and refreshed every 6 hours. Wait a moment or reopen the app. |
| **Channel logos are missing** | Logos are downloaded on first use, so internet is needed. Some channels simply have no logo; their number and name are shown instead. |
| **A channel disappeared from the list** | It was probably hidden after failing. Use *Settings → Restore hidden channels*, or set *Channels that fail to play → Keep showing*. |
| **Back closes the app** | On the **Dashboard**, Back exits. Elsewhere it goes back one screen. |
| **Start from the last watched channel** | *Settings → Resume last channel → On*. |
| **Errors after updating** | Uninstall TV ZT (*Settings → Apps → TV ZT → Uninstall*) and install the latest APK from Releases. |

## Still stuck? Report / suggest

Open **[Issues → New issue](https://github.com/Trias1/tv-zt/issues/new/choose)** (free GitHub account needed) and pick 🐞 *Report a bug*, 📺 *Broken / wrong channel* or 💡 *Suggest a feature / channel*. Fill in your device, TV ZT version and the steps to reproduce, and attach a photo of the screen if you can. Please don't post personal data — issues are public.

## Project layout

| Folder | Contents |
|---|---|
| `tvzt/` | Android project (`MainActivity.java`: WebView, per-channel Referer/User-Agent, remote keys, native splash, signal checker) |
| `mockup/` | TV ZT UI (`tv-zt.html`, opens in any browser; `python tools/mockup-server.py` also shows your computer's real RAM in Settings) and data builders (`build_channels.py`, `categories.py`, `logo.py`) |
| `iptv/` | Data scripts: `build_all.py` (all countries), `build_national.py` (Indonesian national TV), `audit.py` (deep check), `check_subtitles.py` (subtitles), `check_logos.py`, `update-playlist.ps1` |
| `launcher-theme/` | cleanyourtv launcher theme `config.json` (the wallpaper photo is not included) |
| `wallpaper/` | Script that builds a wallpaper from your own photo |
| `tools/` | Test tools: run JavaScript inside the TV ZT WebView over ADB + Chrome DevTools Protocol |

## Build

Requirements: Python 3 (+ Pillow), JDK 17+, Android SDK, ADB.

```powershell
# 1. (optional) rebuild channel data — needs internet
python -I iptv\build_all.py
python -I mockup\build_channels.py

# 2. copy the UI into the app + generate icons, then build
cd tvzt
python prepare.py
.\gradlew.bat assembleRelease

# 3. install on the box over network ADB
adb connect <box-ip>:5555
adb install -r app\build\outputs\apk\release\app-release.apk
```

Routine refresh of Indonesian channels: `iptv\update-playlist.ps1` (add `-Audit` for a full audit of all countries + subtitle check, ~40 minutes).

## Notes

- TV ZT **does not host or re-broadcast any video**; it only plays public links listed by iptv-org. Some are unofficial restreams and may go offline at any time — use responsibly.
- On ZTE boxes, don't disable every built-in launcher (it can trigger a factory reset); just point the Home key to the new launcher.
- Built with help from Claude (Anthropic).

## License

[MIT](LICENSE) © 2026 Trias. Third-party components (hls.js, iptv-org data) keep their own licenses — see [NOTICE.md](NOTICE.md).
