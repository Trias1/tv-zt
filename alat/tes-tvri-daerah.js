const w = (ms) => new Promise((r) => setTimeout(r, ms));
const v = document.querySelector("#video");
const id = window.TVKITA.countries.find((n) => n.code === "ID");
const jt = id.channels.find((c) => c.name === "TVRI Jawa Tengah");
TVZT.putar("ID", jt.no);
let ok = false; for (let i = 0; i < 15; i++) { await w(1000); if (v.currentTime > 1 && !v.paused) { ok = true; break; } }
const hasil = { lang: document.documentElement.lang, tvri: id.channels.filter((c) => /^TVRI /.test(c.name)).length, nama: document.querySelector("#osdName").textContent, main: ok, res: v.videoHeight,
  musikIndo: window.TVKITA.kategori.find((k) => k.code === "MUSIK").items.filter((i) => i[2] === "Musik Indonesia").length };
TVZT.key("home"); await w(400);
return hasil;
