const s = JSON.parse(localStorage.getItem("tvzt.set") || "{}");
const v = document.querySelector("video");
return { quality: s.quality, buffer: s.buffer, name: (document.getElementById("osdName") || {}).textContent, res: (document.getElementById("osdRes") || {}).textContent, net: (document.getElementById("osdNet") || {}).textContent, h: v && v.videoHeight, screen: document.querySelector(".tv").dataset.screen };
