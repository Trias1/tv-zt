const pl = JSON.parse(localStorage.getItem("tvzt.playlists") || "[]"); return pl.map(p => p.url);
