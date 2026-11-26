TVZT.putar("ID", 1); await new Promise(r => setTimeout(r, 15000));
const v = document.querySelector("video");
return { state: document.getElementById("osdState").textContent, net: document.getElementById("osdNet").textContent, h: v.videoHeight, t: +v.currentTime.toFixed(1), url: (window.TVKITA.countries[0].channels.find(c => c.no === 1) || {}).url, epg: (document.getElementById("osdEpg") || {}).innerText };
