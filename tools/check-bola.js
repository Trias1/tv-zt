await new Promise(r => setTimeout(r, 25000));
const pl = JSON.parse(localStorage.getItem("tvzt.playlists") || "[]");
const nav = [...document.querySelectorAll("#navbar .nv")].map(x => x.textContent);
const card = [...document.querySelectorAll("#dgrid .dtile")].find(t => /bola|football/i.test((t.querySelector(".t") || {}).textContent || ""));
return { pl: pl.map(p => `${p.name}: ${p.channels.length} ch, lv ${p.lv}`), nav: nav.join(" · "), bola: card ? card.innerText.replace(/\n/g, " | ") : "no card", logos: card ? card.querySelectorAll(".logos img").length : 0 };
