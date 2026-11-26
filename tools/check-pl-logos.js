await new Promise(r => setTimeout(r, 14000));
const pl = JSON.parse(localStorage.getItem("tvzt.playlists") || "[]");
const tiles = [...document.querySelectorAll("#dgrid .dtile")].filter(t => /sports/i.test((t.querySelector(".t") || {}).textContent || ""))
  .map(t => t.querySelector(".t").textContent + ": " + t.querySelectorAll(".logos img").length + " logo");
return { saved: pl.map(p => `${p.name} ${p.channels.length} ch, tvg-logo ${p.channels.filter(c => c.logo).length}, lv=${p.lv}`), tiles, screen: document.querySelector(".tv").dataset.screen };
