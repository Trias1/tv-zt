const g = () => document.getElementById("osdRes").textContent;
TVZT.putar("ID", 1); await new Promise(r => setTimeout(r, 10000)); const tvri = g();
TVZT.putar("CZ", 30); let mb = "—"; for (let i = 0; i < 12 && mb === "—"; i++) { await new Promise(r => setTimeout(r, 5000)); mb = g(); }
return { tvri, mb };
