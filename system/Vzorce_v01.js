#!/usr/bin/env node
/* =====================================================================
   VZORCE – předem vyrenderuje LaTeX v HTML stránce přes KaTeX (system/Vzorce_v01.js)
   Použití (z rootu repozitáře):
     npm install --prefix /tmp/katex katex@0.16.11   (jednou za sezení – verze MUSÍ sedět se stylem v šabloně)
     NODE_PATH=/tmp/katex/node_modules node system/Vzorce_v01.js matematika/<tema>_zapisky_vXX.html
   Nahradí $$…$$ (blokový vzorec) a $…$ (vzorec v textu) hotovým HTML z KaTeXu, přímo v souboru.
   Mimo <script>, <style> a HTML komentáře. Už vyrenderované vzorce nemění (nemají $), takže jde spustit opakovaně.
   Dolar jako znak napiš \$ (zůstane „$“). Chyba ve vzorci = výpis řádku a konec s kódem 1 (soubor se nezmění).
   Styl: v šabloně je odkaz na katex.min.css 0.16.11. Návod: system/Navod_material_vXX.md, kap. 2.
   ===================================================================== */
"use strict";
const fs = require("fs");
let katex;
try { katex = require("katex"); } catch (e) {
  console.error("Chybí balík katex: npm install --prefix /tmp/katex katex@0.16.11 a spusť s NODE_PATH=/tmp/katex/node_modules");
  process.exit(2);
}
// HTML z KaTeXu musí sedět s katex.min.css, který načítá šablona (jinak se vzorce zobrazí chybně, např. ≠ jako „/=“)
const VERZE = "0.16.11";
if (katex.version !== VERZE) {
  console.error(`Balík katex má verzi ${katex.version}, šablona načítá styl ${VERZE}: npm install --prefix /tmp/katex katex@${VERZE}`);
  process.exit(2);
}
const soubor = process.argv[2];
if (!soubor) { console.error("Použití: node system/Vzorce_v01.js <soubor.html>"); process.exit(2); }
const t = fs.readFileSync(soubor, "utf8");
const chyby = [];
const radek = i => t.slice(0, i).split("\n").length;
function vyrenderuj(tex, blok, pozice) {
  try {
    return katex.renderToString(tex, { displayMode: blok, throwOnError: true, strict: "ignore", output: "html" });
  } catch (e) { chyby.push(`řádek ${radek(pozice)}: ${e.message}`); return null; }
}
// rozdělit na chráněné části (script, style, komentáře) a text
const chranene = /<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>|<!--[\s\S]*?-->/g;
let out = "", posl = 0, m;
function zpracuj(kus, start) {
  return kus.replace(/\\\$|\$\$([\s\S]+?)\$\$|\$([^$\n]+?)\$/g, (cele, blok, inl, off) => {
    if (cele === "\\$") return "&#36;";
    const r = vyrenderuj(blok !== undefined ? blok : inl, blok !== undefined, start + off);
    return r === null ? cele : r;
  });
}
while ((m = chranene.exec(t))) { out += zpracuj(t.slice(posl, m.index), posl) + m[0]; posl = m.index + m[0].length; }
out += zpracuj(t.slice(posl), posl);
if (chyby.length) { console.error("Chyby ve vzorcích:\n  " + chyby.join("\n  ")); process.exit(1); }
fs.writeFileSync(soubor, out);
const n = (t.match(/\$/g) || []).length - (out.match(/\$/g) || []).length;
console.log(`Hotovo: ${soubor} (vyrenderováno, odstraněno ${n} znaků $).`);
