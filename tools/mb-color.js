TVZT.putar("CZ", 30); await new Promise(r => setTimeout(r, 30000));
const e = document.getElementById("osdNet");
return { net: e.textContent, cls: e.className, state: document.getElementById("osdState").textContent, buf: document.getElementById("osdBuf").textContent };
