TVZT.putar("CZ", 30);
await new Promise(r => setTimeout(r, 19000));
const el = document.getElementById("bufLambat");
return { screen: document.querySelector(".tv").dataset.screen, buffering: document.querySelector(".tv").classList.contains("buffer"), shown: !el.hidden, text: el.innerText };
