#!/usr/bin/env node
/* Partekatzeko txartela sortu (1200x630) orritik bertatik.
 *
 * Ez du diseinu propiorik: orria kargatzen du, `og` klasea jartzen dio
 * <html>-i (CSSak zer erakutsi eta zer ezkutatu badaki) eta argazkia ateratzen
 * du. Hala txartela ezin da inoiz orritik aldendu.
 *
 *   node make-og.js            → zenbat-buru-og.png
 *
 * Chrome pipe bidez gidatzen da (CDP), liburutegirik gabe.
 */
const { spawn } = require("child_process");
const fs = require("fs"), path = require("path");

const HERE = __dirname;
const PAGE = "file://" + path.resolve(HERE, "index.html");
const OUT  = path.resolve(HERE, "zenbat-buru-og.png");
const W = 1200, H = 630;

const CHROME = ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium", "/usr/bin/chromium-browser"].find(fs.existsSync);
if (!CHROME){ console.error("Ez dut Chrome aurkitu."); process.exit(1); }

const chrome = spawn(CHROME, ["--headless=new","--disable-gpu","--hide-scrollbars",
  "--remote-debugging-pipe","--no-first-run","--no-default-browser-check",
  "--force-prefers-reduced-motion", `--window-size=${W},${H}`, "about:blank"],
  {stdio:["ignore","ignore","ignore","pipe","pipe"]});

const wr = chrome.stdio[3], rd = chrome.stdio[4];
let id = 0, buf = "", waiters = new Map();
rd.on("data", d => {
  buf += d.toString();
  let i;
  while ((i = buf.indexOf("\0")) >= 0){
    const m = JSON.parse(buf.slice(0, i)); buf = buf.slice(i + 1);
    if (m.id && waiters.has(m.id)){ waiters.get(m.id)(m); waiters.delete(m.id); }
  }
});
const send = (method, params, sessionId) => new Promise(res => {
  const m = {id: ++id, method, params: params || {}};
  if (sessionId) m.sessionId = sessionId;
  waiters.set(m.id, res);
  wr.write(JSON.stringify(m) + "\0");
});
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const t = await send("Target.createTarget", {url: "about:blank"});
  const a = await send("Target.attachToTarget", {targetId: t.result.targetId, flatten: true});
  const s = a.result.sessionId;
  await send("Emulation.setDeviceMetricsOverride",
    {width: W, height: H, deviceScaleFactor: 1, mobile: false}, s);
  await send("Page.enable", {}, s);
  await send("Page.navigate", {url: PAGE}, s);

  /* Letra-tipoak kargatu arte itxaron: bestela izenburua beste neurri batean
     marraztuko litzateke eta eraztuna beste leku batean geratuko. */
  await send("Runtime.evaluate", {expression: "document.fonts.ready", awaitPromise: true}, s);
  await sleep(600);

  /* `og` klaseak diseinua txartelera egokitzen du; `resize`-k eraztuna
     birkalkulatzera behartzen du (140 ms-ko atzerapena du). */
  await send("Runtime.evaluate", {expression:
    "document.documentElement.classList.add('og'); dispatchEvent(new Event('resize'))"}, s);

  /* Eraztuna marraztuta dagoela egiaztatu argazkia atera aurretik. Hau gabe
     noizean behin txartel hutsa ateratzen zen: canvasa oraindik garbi zegoen
     kaptura egitean. */
  let ink = 0;
  for (let i = 0; i < 40; i++){
    await sleep(250);
    const r = await send("Runtime.evaluate", {returnByValue: true, expression: `(() => {
      const c = document.getElementById("heroCanvas");
      if (!c || !c.width) return 0;
      const d = c.getContext("2d").getImageData(0, 0, c.width, c.height).data;
      let n = 0;
      for (let k = 3; k < d.length; k += 4 * 53) if (d[k] > 8) n++;
      return n;
    })()`}, s);
    ink = (r.result && r.result.result && r.result.result.value) || 0;
    if (ink > 200) break;
  }
  if (ink <= 200){
    console.error(`Eraztuna ez da marraztu (${ink}). Ez da txartelik idatzi.`);
    chrome.kill(); process.exit(1);
  }
  await sleep(300);
  const shot = await send("Page.captureScreenshot", {format: "png"}, s);
  if (!shot.result){ console.error("Huts:", JSON.stringify(shot).slice(0, 300)); chrome.kill(); process.exit(1); }
  fs.writeFileSync(OUT, Buffer.from(shot.result.data, "base64"));
  console.log(`${path.relative(HERE, OUT)}: ${W}x${H}, ${fs.statSync(OUT).size.toLocaleString("es-ES")} byte`);
  chrome.kill(); process.exit(0);
})().catch(e => { console.error(e); chrome.kill(); process.exit(1); });
