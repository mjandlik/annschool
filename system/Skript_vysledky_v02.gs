/* =====================================================================
   SKRIPT PRO VÝSLEDKY TESTŮ – Ann School (system/Skript_vysledky_vXX.gs)
   Vloží se do Google tabulky (Rozšíření → Apps Script) a zveřejní jako
   webová aplikace (Spustit jako: já, Přístup: kdokoli). Postup: Navod_test_vXX.md, kap. 9.

   POST (z testů, system/lib/zaznam.js): { app: "annschool", udalosti: [ … ] }
        → zapíše řádky do listu „Udalosti“, obrázky papíru uloží na Disk,
          zařízení zapíše do listu „Zarizeni“. Duplicity (stejné id) zahodí.
   GET  ?akce=data[&od=YYYY-MM-DD]  → všechny události (bez obrázků) + zařízení (vysledky.html, Claude)
   GET  ?akce=obrazek&id=<id souboru> → obrázek papíru jako data URL
   v02: textové sloupce (zadani, odpoved, spravna, …) se zapisují jako prostý text, aby je tabulka
        nepřevedla na číslo nebo datum (dřív „0.00000065“ → 6.5e-7, „3/4“ → datum, „1,500“ → 1500).
   ===================================================================== */

const LIST_UDALOSTI = "Udalosti";
const LIST_ZARIZENI = "Zarizeni";
const SLOZKA = "AnnSchool – papír z testů";
const SLOUPCE = ["cas", "zarizeni", "prezdivka", "relace", "test", "nazev", "verze", "udalost", "priklad", "sekce", "typ",
  "zadani", "pokus", "vysledek", "konecny", "odpoved", "spravna", "doba_s", "napoveda", "odchody", "odchody_s",
  "papir", "detail", "id"];
// sloupce, které musí zůstat textem přesně tak, jak je Ann napsala (ne číslo, ne datum)
const TEXTOVE = ["zarizeni", "prezdivka", "relace", "test", "nazev", "verze", "udalost", "sekce", "typ", "zadani",
  "vysledek", "konecny", "odpoved", "spravna", "papir", "detail", "id"];
const SLOUPCE_Z = ["zarizeni", "prezdivka_ze_zarizeni", "prirazena_prezdivka", "schvaleno", "prvni", "posledni", "udalosti", "poznamka"];

function list_(nazev, hlavicka) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(nazev);
  if (!sh) {
    sh = ss.insertSheet(nazev);
    sh.appendRow(hlavicka);
    sh.setFrozenRows(1);
    sh.getRange(1, 1, 1, hlavicka.length).setFontWeight("bold");
  }
  if (nazev === LIST_UDALOSTI) textoveSloupce_(sh);
  return sh;
}
// celé textové sloupce listu Udalosti nastaví na formát „prostý text“ (jednou, pak si to pamatuje)
function textoveSloupce_(sh) {
  const p = PropertiesService.getScriptProperties();
  if (p.getProperty("TEXT_FORMAT") === "2") return;
  TEXTOVE.forEach(k => { const c = SLOUPCE.indexOf(k) + 1; if (c > 0) sh.getRange(1, c, sh.getMaxRows(), 1).setNumberFormat("@"); });
  p.setProperty("TEXT_FORMAT", "2");
}
// číslo uložené dřív (v01) jako číslo → text bez exponentu (6.5e-7 → "0.00000065")
function cislo_(x) {
  const s = String(x);
  if (!/e/i.test(s)) return s;
  const [m, e] = s.split(/e/i), dec = (m.split(".")[1] || "").length;
  return x.toFixed(Math.min(100, Math.max(0, dec - Number(e))));
}
function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
function slozka_() {
  const p = PropertiesService.getScriptProperties();
  const id = p.getProperty("SLOZKA_ID");
  if (id) { try { return DriveApp.getFolderById(id); } catch (e) { /* smazaná – vytvoří se znovu */ } }
  const f = DriveApp.createFolder(SLOZKA);
  p.setProperty("SLOZKA_ID", f.getId());
  return f;
}
function txt_(v, max) {
  if (v === null || v === undefined) return "";
  if (typeof v === "boolean") return v ? "ano" : "ne";
  let s = String(v);
  if (/^[=+@]/.test(s) && isNaN(Number(s))) s = "'" + s;      // text nesmí začínat jako vzorec
  return s.length > (max || 2000) ? s.slice(0, max || 2000) + "…" : s;
}

/* ---------- příjem událostí ---------- */
function doPost(e) {
  let data;
  try { data = JSON.parse(e.postData.contents); } catch (err) { return json_({ ok: false, chyba: "neplatná data" }); }
  if (!data || data.app !== "annschool" || !Array.isArray(data.udalosti)) return json_({ ok: false, chyba: "neznámý odesílatel" });
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const sh = list_(LIST_UDALOSTI, SLOUPCE);
    // id posledních ~5000 řádků kvůli duplicitám (opakované odeslání z fronty / beacon)
    const n = sh.getLastRow(), od = Math.max(2, n - 5000);
    const ids = new Set(n >= 2 ? sh.getRange(od, SLOUPCE.length, n - od + 1, 1).getValues().map(r => String(r[0])) : []);
    const radky = [], zar = {};
    data.udalosti.slice(0, 100).forEach(u => {
      if (!u || !u.id || ids.has(String(u.id))) return;
      ids.add(String(u.id));
      let papir = "";
      if (typeof u.papir === "string" && u.papir.indexOf("data:image/") === 0 && u.papir.length < 4e6) {
        try {
          const m = u.papir.match(/^data:(image\/\w+);base64,(.*)$/);
          const blob = Utilities.newBlob(Utilities.base64Decode(m[2]), m[1],
            [txt_(u.prezdivka) || txt_(u.zarizeni), txt_(u.test).replace(/\//g, "_"), "p" + txt_(u.priklad), "pokus" + txt_(u.pokus), txt_(u.id)].join("_") + (m[1] === "image/png" ? ".png" : ".jpg"));
          papir = slozka_().createFile(blob).getId();
        } catch (err) { papir = "chyba: " + err; }
      }
      const r = SLOUPCE.map(k => k === "papir" ? papir : k === "cas" ? (u.cas ? new Date(u.cas) : new Date())
        : txt_(u[k], k === "detail" ? 45000 : 2000));
      radky.push(r);
      if (u.zarizeni) {
        const z = zar[u.zarizeni] || (zar[u.zarizeni] = { prezdivka: "", n: 0, cas: u.cas });
        if (u.prezdivka) z.prezdivka = txt_(u.prezdivka);
        z.n++; z.cas = u.cas || z.cas;
      }
    });
    if (radky.length) {
      const rng = sh.getRange(sh.getLastRow() + 1, 1, radky.length, SLOUPCE.length);
      // nové řádky: textové sloupce jako prostý text (i když list přesáhne původní počet řádků)
      TEXTOVE.forEach(k => { const c = SLOUPCE.indexOf(k) + 1; if (c > 0) rng.offset(0, c - 1, radky.length, 1).setNumberFormat("@"); });
      rng.setValues(radky);
    }
    zapisZarizeni_(zar);
    return json_({ ok: true, zapsano: radky.length });
  } finally {
    lock.releaseLock();
  }
}
function zapisZarizeni_(zar) {
  const ids = Object.keys(zar);
  if (!ids.length) return;
  const sh = list_(LIST_ZARIZENI, SLOUPCE_Z);
  const n = sh.getLastRow();
  const vals = n >= 2 ? sh.getRange(2, 1, n - 1, SLOUPCE_Z.length).getValues() : [];
  const radek = {}; vals.forEach((r, i) => radek[String(r[0])] = i);
  ids.forEach(id => {
    const z = zar[id], cas = z.cas ? new Date(z.cas) : new Date();
    if (radek[id] === undefined) {
      sh.appendRow([id, z.prezdivka, "", "", cas, cas, z.n, ""]);
    } else {
      const r = radek[id] + 2, v = vals[radek[id]];
      if (z.prezdivka && z.prezdivka !== v[1]) sh.getRange(r, 2).setValue(z.prezdivka);
      sh.getRange(r, 6, 1, 2).setValues([[cas, (Number(v[6]) || 0) + z.n]]);
    }
  });
}

/* ---------- čtení ---------- */
function doGet(e) {
  const p = (e && e.parameter) || {};
  if (p.akce === "data") {
    const sh = list_(LIST_UDALOSTI, SLOUPCE), n = sh.getLastRow();
    const od = p.od ? new Date(p.od) : null;
    const rows = n >= 2 ? sh.getRange(2, 1, n - 1, SLOUPCE.length).getValues() : [];
    const out = [];
    rows.forEach(r => {
      if (od && r[0] instanceof Date && r[0] < od) return;
      const o = {};
      SLOUPCE.forEach((k, i) => o[k] = r[i] instanceof Date ? r[i].toISOString()
        : (TEXTOVE.indexOf(k) >= 0 && typeof r[i] === "number") ? cislo_(r[i]) : r[i]);
      out.push(o);
    });
    const zs = list_(LIST_ZARIZENI, SLOUPCE_Z), m = zs.getLastRow();
    const zar = (m >= 2 ? zs.getRange(2, 1, m - 1, SLOUPCE_Z.length).getValues() : []).map(r => {
      const o = {}; SLOUPCE_Z.forEach((k, i) => o[k] = r[i] instanceof Date ? r[i].toISOString() : r[i]); return o;
    });
    return json_({ ok: true, udalosti: out, zarizeni: zar, cas: new Date().toISOString() });
  }
  if (p.akce === "obrazek" && p.id) {
    try {
      const f = DriveApp.getFileById(p.id);
      const parents = f.getParents(), sid = slozka_().getId();
      let ok = false; while (parents.hasNext()) if (parents.next().getId() === sid) ok = true;
      if (!ok) return json_({ ok: false, chyba: "soubor není ze složky papíru" });
      const b = f.getBlob();
      return json_({ ok: true, url: "data:" + b.getContentType() + ";base64," + Utilities.base64Encode(b.getBytes()) });
    } catch (err) { return json_({ ok: false, chyba: String(err) }); }
  }
  return json_({ ok: true, info: "Ann School – záznam výsledků běží." });
}

/* Ruční spuštění v editoru (▶ nastav): založí listy a složku a vyžádá oprávnění. */
function nastav() {
  list_(LIST_UDALOSTI, SLOUPCE);
  list_(LIST_ZARIZENI, SLOUPCE_Z);
  Logger.log("Složka na papír: " + slozka_().getUrl());
}
