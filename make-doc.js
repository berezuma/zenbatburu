#!/usr/bin/env node
/* AURKEZPENA.md → AURKEZPENA.pdf (A4), izapidera eransteko.
 *
 * Markdown-etik HTMLra bihurtzen du (dokumentu honek erabiltzen dituen
 * egiturak bakarrik: izenburuak, taulak, zerrendak, lodia, etzana, kodea,
 * estekak), orriaren tipografia bera jartzen dio, eta Chromeri inprimatzeko
 * eskatzen dio CDP bidez. Liburutegirik gabe.
 *
 *   node make-doc.js        → AURKEZPENA.pdf
 */
const { spawn } = require("child_process");
const fs = require("fs"), path = require("path");

const HERE = __dirname;
const SRC = path.resolve(HERE, "AURKEZPENA.md");
const OUT = path.resolve(HERE, "AURKEZPENA.pdf");

const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

/* Lerro barruko markak. Kodea lehenik, haren barruan ez dadin ezer ukitu. */
function inline(s){
  const code = [];
  s = s.replace(/`([^`]+)`/g, (_, c) => `\u0000${code.push(c) - 1}\u0000`);
  s = esc(s);
  s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
  s = s.replace(/(^|[\s(])(https?:\/\/[^\s)<]+)/g, '$1<a href="$2">$2</a>');
  s = s.replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
  s = s.replace(/\*([^*]+)\*/g, "<i>$1</i>");
  return s.replace(/\u0000(\d+)\u0000/g, (_, i) => `<code>${esc(code[+i])}</code>`);
}

function markdown(src){
  const out = [];
  const lines = src.split("\n");
  let i = 0, para = [];
  const flush = () => { if (para.length){ out.push(`<p>${inline(para.join(" "))}</p>`); para = []; } };

  while (i < lines.length){
    const l = lines[i];

    if (/^\s*$/.test(l)){ flush(); i++; continue; }

    if (/^#{1,4} /.test(l)){
      flush();
      const n = l.match(/^#+/)[0].length;
      out.push(`<h${n}>${inline(l.slice(n + 1))}</h${n}>`);
      i++; continue;
    }

    if (/^---+\s*$/.test(l)){ flush(); out.push("<hr>"); i++; continue; }

    /* Taula: goiburua, bereizlea, ilarak */
    if (/^\|/.test(l) && /^\|[\s:|-]+\|\s*$/.test(lines[i + 1] || "")){
      flush();
      const cells = r => r.split("|").slice(1, -1).map(c => c.trim());
      const head = cells(l);
      const align = cells(lines[i + 1]).map(c =>
        c.endsWith(":") && c.startsWith(":") ? "center" : c.endsWith(":") ? "right" : "left");
      i += 2;
      const body = [];
      while (i < lines.length && /^\|/.test(lines[i])){ body.push(cells(lines[i])); i++; }
      out.push(`<table><thead><tr>${head.map((c, k) =>
        `<th style="text-align:${align[k] || "left"}">${inline(c)}</th>`).join("")}</tr></thead><tbody>${
        body.map(r => `<tr>${r.map((c, k) =>
          `<td style="text-align:${align[k] || "left"}">${inline(c)}</td>`).join("")}</tr>`).join("")
        }</tbody></table>`);
      continue;
    }

    /* Zerrendak, puntudunak eta zenbakituak. Jarraipen-lerroak koskatuta
       datoz, eta aurreko elementuari gehitzen zaizkio. */
    const bullet = /^[-*] /, ordered = /^\d+\. /;
    if (bullet.test(l) || ordered.test(l)){
      flush();
      const tag = ordered.test(l) ? "ol" : "ul";
      const mark = ordered.test(l) ? ordered : bullet;
      const items = [];
      while (i < lines.length && (mark.test(lines[i]) || /^\s{2,}\S/.test(lines[i]))){
        if (mark.test(lines[i])) items.push(lines[i].replace(mark, ""));
        else if (items.length) items[items.length - 1] += " " + lines[i].trim();
        else break;
        i++;
      }
      out.push(`<${tag}>${items.map(x => `<li>${inline(x)}</li>`).join("")}</${tag}>`);
      continue;
    }

    para.push(l.trim());
    i++;
  }
  flush();
  return out.join("\n");
}

const body = markdown(fs.readFileSync(SRC, "utf8"));
const html = `<!doctype html><html lang="eu"><meta charset="utf-8">
<title>Zenbat buru? · Dokumentazio teknikoa</title>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Spectral:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap">
<style>
  @page{ size:A4; margin:19mm 17mm 17mm }
  body{ font:400 10.5pt/1.55 "Spectral", Georgia, serif; color:#1d1a14; margin:0;
        font-variant-numeric:tabular-nums lining-nums }
  h1{ font:400 23pt/1.1 "Instrument Serif", Georgia, serif; margin:0 0 .8em;
      border-bottom:1px solid #cfc7b4; padding-bottom:.25em }
  h1+p{ margin-top:0 }
  h1:not(:first-child){ break-before:page; margin-top:0 }
  h2{ font:400 15pt/1.2 "Instrument Serif", Georgia, serif; margin:1.6em 0 .5em;
      break-after:avoid }
  h3{ font:500 10.5pt/1.3 "Spectral", Georgia, serif; letter-spacing:.06em;
      text-transform:uppercase; color:#55503f; margin:1.3em 0 .4em; break-after:avoid }
  p{ margin:0 0 .72em; text-align:justify; hyphens:auto }
  b{ font-weight:600 }
  code{ font:400 9.2pt/1.4 ui-monospace, "SFMono-Regular", Menlo, monospace;
        background:#eae4d7; padding:.05em .3em; border-radius:2px }
  a{ color:inherit; text-decoration:none; border-bottom:.4pt solid #cfc7b4 }
  hr{ border:0; border-top:1px solid #cfc7b4; margin:1.6em 0 }
  ul,ol{ margin:0 0 .8em; padding-inline-start:1.3em }
  ol li{ padding-inline-start:.15em }
  li{ margin:0 0 .3em }
  table{ border-collapse:collapse; width:100%; margin:.5em 0 1em; font-size:9.6pt;
         break-inside:avoid }
  th{ text-align:start; font-weight:500; font-size:8.4pt; letter-spacing:.07em;
      text-transform:uppercase; color:#55503f; border-bottom:.8pt solid #cfc7b4;
      padding:.35em .5em }
  td{ padding:.32em .5em; border-bottom:.4pt solid #e2dbc9; vertical-align:top }
</style>
${body}
</html>`;

const TMP = path.join(HERE, ".aurkezpena.tmp.html");
fs.writeFileSync(TMP, html);

const CHROME = ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium", "/usr/bin/chromium-browser"].find(fs.existsSync);
if (!CHROME){ console.error("Ez dut Chrome aurkitu."); process.exit(1); }

const chrome = spawn(CHROME, ["--headless=new","--disable-gpu","--no-first-run",
  "--no-default-browser-check","--remote-debugging-pipe","about:blank"],
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
  await send("Page.enable", {}, s);
  await send("Page.navigate", {url: "file://" + TMP}, s);
  await send("Runtime.enable", {}, s);
  await send("Runtime.evaluate", {expression: "document.fonts.ready", awaitPromise: true}, s);
  await sleep(700);
  const r = await send("Page.printToPDF", {
    printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate: '<div style="width:100%;font:8pt Georgia,serif;color:#87806a;'
      + 'padding:0 17mm;display:flex;justify-content:space-between">'
      + '<span>Zenbat buru? · zenbatburu.berezuma.com</span>'
      + '<span class="pageNumber"></span></div>',
  }, s);
  if (!r.result){ console.error("Huts:", JSON.stringify(r).slice(0, 300)); chrome.kill(); process.exit(1); }
  fs.writeFileSync(OUT, Buffer.from(r.result.data, "base64"));
  fs.unlinkSync(TMP);
  console.log(`${path.relative(HERE, OUT)}: ${fs.statSync(OUT).size.toLocaleString("es-ES")} byte`);
  chrome.kill(); process.exit(0);
})().catch(e => { console.error(e); chrome.kill(); process.exit(1); });
