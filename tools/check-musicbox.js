const g = JSON.parse(localStorage.getItem("tvzt.gagal") || "{}");
const hidden = Object.keys(g).filter(k => /mb_hits|CZ.?30/i.test(k));
TVZT.putar("CZ", 30);
const log = [];
for (let i = 0; i < 12; i++) {
  await new Promise(r => setTimeout(r, 2500));
  const v = document.querySelector("video");
  log.push({ t: (i + 1) * 2.5, ready: v && v.readyState, cur: v && +v.currentTime.toFixed(1), buf: v && v.buffered.length ? +v.buffered.end(v.buffered.length - 1).toFixed(1) : 0,
             status: (document.querySelector("#osd .status, #stat, .status") || {}).textContent });
}
return { hidden, log, err: (document.querySelector(".err, #err, .notes code") || {}).textContent };
