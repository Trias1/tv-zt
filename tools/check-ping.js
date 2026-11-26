const g = () => { const e = document.getElementById("osdNet"); return e.textContent + " [" + e.className + "]"; };
TVZT.putar("ID", 1); await new Promise(r => setTimeout(r, 12000));
const r2 = document.querySelector(".row2"), spans = [...r2.children].map(x => Math.round(x.getBoundingClientRect().top));
const tvri = g();
TVZT.putar("CZ", 30); await new Promise(r => setTimeout(r, 20000));
const mb = g(), box = document.getElementById("bufLambat");
return { tvri, mb, oneLine: new Set(spans).size === 1, notice: box.hidden ? "hidden" : box.innerText };
