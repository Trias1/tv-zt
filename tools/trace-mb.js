TVZT.putar("CZ", 30);
const out = [];
for (let i = 0; i < 10; i++) {
  await new Promise(r => setTimeout(r, 3000));
  out.push([(i + 1) * 3, document.getElementById("osdState").textContent, document.getElementById("osdNet").textContent, document.getElementById("bufLambat").hidden ? "-" : "NOTICE"].join(" | "));
}
return out;
