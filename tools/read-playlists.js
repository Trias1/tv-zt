const pl = JSON.parse(localStorage.getItem("tvzt.playlists") || "[]");
return pl.map(p => ({ name: p.name, mode: p.mode, src: p.src, n: p.channels.length,
  withTvgLogo: p.channels.filter(c => c.logo).length,
  sample: p.channels.slice(0, 10).map(c => c.name) }));
