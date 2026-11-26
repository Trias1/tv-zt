"""Susun kelompok kategori (Indovision, Anime, Anak & Kartun, Film & Hiburan, Berita & Olahraga, Lofi & Santai).

Kategori channel diambil dari data resmi iptv-org (iptv/api/channels.json + streams.json, dicocokkan lewat URL),
ditambah pencocokan nama untuk anime dan lofi. Hasilnya hanya rujukan [kode negara, nomor, grup] supaya data
channel tidak tertulis dua kali; tampilan (tv-kita.html) menyusun kelompoknya saat dibuka.
Di nama grup, "{n}" diganti nama negara oleh tampilan.
"""
import json
import re
from pathlib import Path

API = Path(__file__).resolve().parent.parent / "iptv" / "api"

# Negara yang didahulukan (bahasa Inggris / Asia dulu), sisanya mengikuti urutan data.
PRIORITAS = ["ID", "SG", "US", "GB", "AU", "CA", "PH", "MY", "IN", "HK", "JP", "KR", "TW", "TH", "NZ", "IE",
             "FR", "DE", "ES", "IT", "NL", "BR", "MX", "AR", "TR", "AE", "SA"]
# Versi bahasa lain dari channel internasional dilewati untuk paket Indovision.
BAHASA_LAIN = re.compile(r"espa[nñ]ol|spanish|latin|brasil|brazil|portugu|deutsch|germany|france|fran[cç]ais|arab|t[uü]rk|polsk|"
                         r"poland|czech|bulgar|hungar|romania|ukrain|russia|ital|hindi|tamil|telugu|\bcee\b|balkan|adria", re.I)
ANIME = re.compile(r"anime|naruto|boruto|one piece|pok[eé]mon|dragon ?ball|yu-?gi|sailor moon|crunchyroll|retrocrush|toonami|"
                   r"hidive|animax|aniplus|doraemon|gundam|\bmangas\b|wasabi", re.I)
LOFI = re.compile(r"lo-?fi|chill|ambient|lounge|relax|calm|sleep|fireplace|\bzen|bizaar|aquarium|slow ?tv|naturescape|"
                  r"nature moments|screen dreams|space live|smooth jazz|djazz|jazz tv|jazz &", re.I)
RADIO = re.compile(r"\bradio", re.I)
FILM_ID = re.compile(r"\bfilm|movie|bioskop|cinema|sinema", re.I)
BUKAN_FILM = re.compile(r"\bcine\b|cinecanal|bonanza|rawhide|star trek|battlestar|wild wild west|wu tang|\bNOST\b|WFXT|girlfriends", re.I)
HARAMAIN = re.compile(r"quran al kareem|sunnah al nabawiyah|makkah|madinah|haramain", re.I)
ISLAM_ID = re.compile(r"rodja|mq\s?tv|tv9 nusantara|ashiil|surau|madani|dmi|ahsan|alwafa|tarim|i am channel|dakwah|quran|sunnah", re.I)
ISLAM_EN = re.compile(r"peace tv english|huda tv|muslim network|deen tv|islamic network", re.I)
ISLAM_DUNIA = re.compile(r"iqraa|peace tv|tv muslim|diyanet|semerkand|lalegul|sunna tv|^alquran$|holy quran|bahrain quran", re.I)
BUKAN_ISLAM = re.compile(r"daai|MTA|christ|church|gospel|jesus", re.I)  # DAAI = Buddha, MTA = Ahmadiyah
ANIME_JP = re.compile(r"^retrocrush$|^pluto tv anime$|^boruto", re.I)
BARAT = {"US", "GB", "CA", "AU", "NZ", "IE"}
BUKAN_BARAT = re.compile(r"\bFM\b|sexy|pamir|jalwa|\bMBC\b", re.I)  # radio FM, channel non-barat, dan yang berbau dewasa
LATIN = re.compile(r"latin|latino|reggaeton|salsa|m[uú]sica|bachata|cumbia|mariachi|ranchera|banda\b|tropical|norte[nñ]", re.I)
MUSIK_ID = re.compile(r"music|musik|dangdut|karaoke|lagu|campursari|keroncong|\bsmtv\b|suara surabaya", re.I)
MEREK_MUSIK = re.compile(r"\bMTV|\bVH1\b|vevo|stingray|clubbing|trace|deluxe|mezzo|qwest|\bCMT\b|\bkiss\b|hits|pop|rock|jazz|country|dance|"
                         r"\bedm\b|billboard|r&b|hip ?hop|80s|90s|00s|retro", re.I)
ROHANI = re.compile(r"gospel|praise|worship|christ|church|jesus|faith|hymn|3abn|\bgod\b|holy|bible|catholic|evangel|messian|"
                    r"hillsong|rohani|islam|quran|qur'an|nasheed|nasyid|sholawat|shalawat|dakwah|muslim|sufi|hindu|bhakti|bhajan|"
                    r"devotion|spirit|zion|shalom|kingdom|miracle|salvation|grace|glory|angel", re.I)

# Paket Indovision: grup → daftar merek (regex nama, berapa yang diambil).
PAKET = [
    ("Film", [r"\bHBO\b", r"cinemax", r"\bAXN\b", r"^warner (tv|bros\.? tv)$", r"universal", r"paramount", r"^AMC$|^AMC (asia|thrillers|presents)", r"^FXX?$|^FX movie", r"star movies",
              r"sony (max|movies|one)", r"hallmark", r"lionsgate", r"filmrise (movies|action|western|classic)", r"pluto tv (movies|action|comedy)",
              r"rakuten", r"movies? ?(one|now)"]),
    ("Berita", [r"cnn international", r"^cnn( headlines)?$", r"bbc (news|world)", r"al jazeera( english)?$", r"^cna\b|channel ?news ?asia",
                r"^dw( english)?$", r"france 24 english", r"nhk world", r"arirang", r"^cgtn$", r"bloomberg", r"^cnbc", r"^sky news$",
                r"euronews english|^euronews$", r"abc news", r"trt world", r"\bwion\b", r"reuters", r"nbc news", r"cbs news"]),
    ("Dokumenter", [r"discovery", r"national geographic|nat ?geo", r"animal planet", r"\bhistory\b", r"love nature", r"bbc earth",
                    r"smithsonian", r"^travel channel$", r"food network", r"\bTLC\b", r"\bHGTV\b", r"wildearth", r"pluto tv nature"]),
    ("Anak", [r"cartoon network", r"cartoonito", r"boomerang", r"nickelodeon|^nick\b", r"nick jr", r"disney channel", r"disney jr|disney junior",
              r"baby ?tv", r"duck ?tv", r"pluto tv kids", r"pbs kids", r"kartoon", r"cartoon classics"]),
    ("Olahraga", [r"\bESPN", r"bein", r"fox sports", r"eurosport", r"red bull", r"sky sports", r"\bNBA\b", r"\bWWE\b", r"\bDAZN\b",
                  r"sportsnet", r"golf", r"motorvision", r"olympic", r"fight ?network"]),
    ("Musik & Santai", [r"\bMTV", r"\bVH1\b", r"trace", r"vevo", r"clubbing", r"mezzo", r"bizaar", r"zenlife", r"fireplace", r"space live",
                        r"stingray (smooth jazz|djazz)", r"deluxe lounge"]),
    ("Anime", [r"pluto tv anime$", r"^naruto$", r"^boruto", r"^one piece$", r"^pok[eé]mon$", r"^dragon ball$", r"crunchyroll", r"retrocrush",
               r"toonami aftermath east", r"filmrise anime"]),
]


def kunci(s):
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\(.*?\)|\[.*?\]|\b(hd|sd|fhd|uhd|4k)\b", "", s.lower()))


def susun(negara):
    ch = {c["id"]: c for c in json.loads((API / "channels.json").read_text(encoding="utf-8"))}
    u2c = {s["url"]: s["channel"] for s in json.loads((API / "streams.json").read_text(encoding="utf-8")) if s.get("channel")}

    def kat(c):
        x = ch.get(u2c.get(c["url"]))
        return set(x["categories"]) if x else set(), bool(x and x["is_nsfw"])

    rank = {k: i for i, k in enumerate(PRIORITAS)}
    urut = sorted(negara, key=lambda n: rank.get(n["code"], len(PRIORITAS)))
    semua = []  # (negara, channel, kategori) tanpa NSFW
    for n in urut:
        for c in n["channels"]:
            k, nsfw = kat(c)
            if not nsfw and "xxx" not in k:
                semua.append((n, c, k))

    def kelompok(code, name, desc, aturan):
        """aturan: daftar (label grup, fungsi saring). Satu nama channel hanya sekali per kategori."""
        items, sudah = [], set()
        for label, cocok in aturan:
            for n, c, k in semua:
                key = kunci(c["name"])
                if key in sudah or n["code"] == "ID" or not cocok(c, k):
                    continue
                sudah.add(key)
                items.append([n["code"], c["no"], label])
        return {"code": code, "name": name, "desc": desc, "items": items}

    # Bahasa tiap channel dari feeds.json iptv-org (gabungan semua feed channel itu).
    bahasa = {}
    fp = API / "feeds.json"
    if fp.exists():
        for f in json.loads(fp.read_text(encoding="utf-8")):
            bahasa.setdefault(f["channel"], set()).update(f.get("languages") or [])
    bhs = lambda c: bahasa.get(u2c.get(c["url"]), set())

    def musik_indo_barat():
        """Musik: Indonesia dulu, lalu barat = channel musik berbahasa Inggris saja (data bahasa iptv-org),
        atau merek musik internasional tanpa bahasa tercatat. Tanpa rohani, radio, dan versi Latin/bahasa lain."""
        items, sudah = [], set()
        def barat(n, c, k):
            if "music" not in k or BAHASA_LAIN.search(c["name"]) or LATIN.search(c["name"]) or BUKAN_BARAT.search(c["name"]):
                return False
            b = bhs(c)
            return b == {"eng"} or ("eng" in b and n["code"] in BARAT) or (not b and n["code"] in BARAT and bool(MEREK_MUSIK.search(c["name"])))
        for label, ok in (("Favorit", lambda n, c, k: c["name"].lower() == "music box hits"),  # permintaan: paling atas
                          ("Musik Indonesia", lambda n, c, k: n["code"] == "ID" and ("music" in k or bool(MUSIK_ID.search(c["name"])))),
                          ("Musik Barat", barat)):
            for n, c, k in semua:
                key = kunci(c["name"])
                # radio bervideo Indonesia (mis. Suara Surabaya) tetap boleh di Musik Indonesia
                if key in sudah or (RADIO.search(c["name"]) and n["code"] != "ID") or rohani(c, k) or not ok(n, c, k):
                    continue
                sudah.add(key)
                items.append([n["code"], c["no"], label])
        return {"code": "MUSIK", "name": "Musik", "desc": "musik Indonesia & barat", "items": items}

    def film_indo_hollywood():
        """Film: hanya channel film (bukan serial/hiburan umum) Indonesia, lalu Hollywood = channel film berbahasa Inggris
        dari negara barat. Tanpa versi Latin/bahasa lain dan tanpa rohani."""
        items, sudah = [], set()
        def indo(n, c, k):
            return n["code"] == "ID" and ("movies" in k or bool(FILM_ID.search(c["name"])))
        def hollywood(n, c, k):
            if "movies" not in k or BAHASA_LAIN.search(c["name"]) or LATIN.search(c["name"]) or rohani(c, k) or BUKAN_FILM.search(c["name"]):
                return False
            # Channel serial dilewati kecuali namanya jelas channel film.
            if "series" in k and not FILM_ID.search(c["name"]):
                return False
            b = bhs(c)
            return n["code"] in BARAT and (not b or "eng" in b) and not (b and b - {"eng"} and "eng" not in b)
        for label, ok in (("Film Indonesia", indo), ("Film Hollywood", hollywood)):
            for n, c, k in semua:
                key = kunci(c["name"])
                if key in sudah or RADIO.search(c["name"]) or not ok(n, c, k):
                    continue
                sudah.add(key)
                items.append([n["code"], c["no"], label])
        return {"code": "FILM", "name": "Film", "desc": "film Indonesia & Hollywood", "items": items}

    def islam():
        """Islam saja (tidak dicampur agama lain): Baitullah (Makkah) & Madinah paling atas, dakwah Indonesia,
        lalu Islam dunia (berbahasa Inggris dulu). Tanpa radio."""
        items, sudah = [], set()
        aturan = (
            ("Baitullah & Madinah", lambda n, c, k: n["code"] == "SA" and "quran al kareem" in c["name"].lower()),  # Ka'bah dulu
            ("Baitullah & Madinah", lambda n, c, k: n["code"] == "SA" and bool(HARAMAIN.search(c["name"]))),
            ("Islam Indonesia", lambda n, c, k: n["code"] == "ID" and ("religious" in k or bool(ISLAM_ID.search(c["name"])))),
            ("Islam Dunia", lambda n, c, k: bool(ISLAM_EN.search(c["name"]))),
            ("Islam Dunia", lambda n, c, k: bool(ISLAM_DUNIA.search(c["name"]))),
        )
        for label, ok in aturan:
            for n, c, k in semua:
                key = kunci(c["name"])
                if key in sudah or RADIO.search(c["name"]) or BUKAN_ISLAM.search(c["name"]) or not ok(n, c, k):
                    continue
                sudah.add(key)
                items.append([n["code"], c["no"], label])
        return {"code": "ISLAM", "name": "Islam", "desc": "Baitullah & Madinah live, dakwah, murottal", "items": items}

    anime = lambda c, k: bool(ANIME.search(c["name"])) and not RADIO.search(c["name"])
    # Musik/Lofi tanpa musik rohani: kategori "religious" iptv-org atau nama yang jelas bernuansa rohani.
    rohani = lambda c, k: "religious" in k or bool(ROHANI.search(c["name"]))
    out = [
        islam(),
        kelompok("SUB", "Sub Indo", "subtitle diterjemahkan ke Indonesia", [("{n}", lambda c, k: bool(c.get("sub")))]),
        # Paling atas: anime bersuara Jepang (dicek 26 Nov 2026: Pluto TV Anime & Boruto AS bersuara Jepang,
        # RetroCrush anime klasik dengan subtitle teks → bisa diterjemahkan ke Indonesia).
        kelompok("ANIME", "Anime", "Naruto, One Piece, Pokémon, Dragon Ball", [("Suara Jepang", lambda c, k: c["name"].lower() == "retrocrush"),  # pertama: bisa subtitle Indonesia
                                                                              ("Suara Jepang", lambda c, k: anime(c, k) and bool(ANIME_JP.search(c["name"]))),
                                                                              ("{n}", anime)]),
        kelompok("ANAK", "Anak & Kartun", "kartun dan acara anak", [("{n}", lambda c, k: bool(k & {"kids", "animation"}) and not anime(c, k))]),
        film_indo_hollywood(),
        kelompok("BERITA", "Berita & Olahraga", "berita dunia dan olahraga", [("Berita · {n}", lambda c, k: "news" in k),
                                                                         ("Olahraga · {n}", lambda c, k: "sports" in k)]),
        musik_indo_barat(),
        kelompok("SANTAI", "Lofi & Santai", "lofi, jazz, lounge, alam", [("{n}", lambda c, k: ("relax" in k or bool(LOFI.search(c["name"]))) and not RADIO.search(c["name"]) and not rohani(c, k))]),
    ]

    # Indovision: nasional Indonesia + satu channel terbaik per merek internasional, bernomor seperti paket TV.
    iv, sudah = [], set()
    idn = next(n for n in negara if n["code"] == "ID")
    for c in idn["channels"]:
        if c.get("group") == "Nasional":
            iv.append(["ID", c["no"], "Indonesia", c["no"]])
    for gi, (grup, merek) in enumerate(PAKET):
        no = 101 + gi * 100
        for pola in merek:
            r = re.compile(pola, re.I)
            for n, c, k in semua:
                key = kunci(c["name"])
                if n["code"] in ("ID", "IR", "PL", "RU", "UA") or key in sudah or not r.search(c["name"]) or BAHASA_LAIN.search(c["name"]) or RADIO.search(c["name"]):
                    continue
                sudah.add(key)
                iv.append([n["code"], c["no"], grup, no]); no += 1
                break
    out.insert(0, {"code": "IV", "name": "Indovision", "desc": "paket pilihan Indonesia + internasional", "items": iv})
    return out


if __name__ == "__main__":
    # Uji cepat: python -I kategori.py
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    semua = json.loads((API.parent / "semua.json").read_text(encoding="utf-8"))["countries"]
    idn = {"code": "ID", "channels": [{"no": 1, "name": "TVRI", "url": "x", "group": "Nasional"}]}
    for k in susun([idn] + semua):
        grup = {}
        for it in k["items"]:
            grup[it[2]] = grup.get(it[2], 0) + 1
        print(k["code"], k["name"], len(k["items"]), dict(list(grup.items())[:8]))
