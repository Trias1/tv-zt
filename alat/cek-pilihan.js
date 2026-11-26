await new Promise(r => setTimeout(r, 4000));
const t = document.body.innerText;
return { lang: (JSON.parse(localStorage.getItem("tvzt.set") || "{}")).lang, indovision: /indovision/i.test(t), pilihan: /Pilihan/.test(t), nav: (document.querySelector("nav") || {}).innerText };
