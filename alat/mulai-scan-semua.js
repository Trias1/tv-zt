const w = (ms) => new Promise((r) => setTimeout(r, ms));
TVZT.key("home"); await w(500);
TVZT.key("menu"); await w(800);
document.querySelector('#setwrap [data-act="sinyal"]').click(); await w(500);
// centang Indonesia (sudah) + Luar negeri (baris ke-2), lalu ke tombol Mulai
TVZT.key("down"); TVZT.key("ok"); await w(200);
const teks = document.querySelector("#scan .mulai").innerText;
for (let i = 0; i < 20; i++) TVZT.key("down");
TVZT.key("ok"); await w(3000);
return { tombol: teks, status: document.querySelector("#scan").innerText.replace(/\n/g, " | ") };
