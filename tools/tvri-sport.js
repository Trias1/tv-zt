const c = window.TVKITA.countries[0].channels.find(c => /tvri sport/i.test(c.name));
if (!c) return "no TVRI Sport";
TVZT.putar("ID", c.no); await new Promise(r => setTimeout(r, 15000));
const v = document.querySelector("video");
return { no: c.no, name: c.name, state: document.getElementById("osdState").textContent, h: v.videoHeight, epg: (document.getElementById("osdEpg") || {}).innerText };
