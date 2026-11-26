// Pakai: node alat/cdp.mjs <ws-url> <file-js>  → jalankan JS di WebView TV ZT (lewat adb forward), cetak hasilnya.
import { readFileSync } from "node:fs";
const [ws, file] = process.argv.slice(2);
const expr = readFileSync(file, "utf8");
const sock = new WebSocket(ws);
sock.onopen = () => sock.send(JSON.stringify({ id: 1, method: "Runtime.evaluate",
  params: { expression: `(async () => { ${expr} })()`, awaitPromise: true, returnByValue: true } }));
sock.onmessage = (m) => {
  const d = JSON.parse(m.data);
  if (d.id !== 1) return;
  console.log(JSON.stringify(d.result?.result?.value ?? d.result ?? d.error, null, 1));
  sock.close();
};
sock.onerror = (e) => { console.error("ws error", e.message); process.exit(1); };
