const v = document.querySelector("video"); let waits = 0; const on = () => waits++; v.addEventListener("waiting", on);
const t0 = v.currentTime, r0 = Date.now(), nets = [];
for (let i = 0; i < 6; i++) { await new Promise(r => setTimeout(r, 5000)); nets.push(document.getElementById("osdNet").textContent); }
v.removeEventListener("waiting", on);
const b = v.buffered; let ahead = 0; for (let i = 0; i < b.length; i++) if (b.start(i) <= v.currentTime + .2 && b.end(i) > v.currentTime) ahead = b.end(i) - v.currentTime;
return { name: document.getElementById("osdName").textContent, played: +(v.currentTime - t0).toFixed(1), real: (Date.now() - r0) / 1000, waits, bufferAhead: +ahead.toFixed(1), nets };
