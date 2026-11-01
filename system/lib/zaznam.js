/* =====================================================================
   ZÁZNAM VÝSLEDKŮ – Ann School (system/lib/zaznam.js)
   Sdílený modul pro testy (šablona v16+), přehled výsledků (vysledky.html)
   a označení zařízení (zarizeni.html). Návod: system/Navod_test_vXX.md, kap. 9.

   - Události testu se posílají na webovou aplikaci Google Apps Script
     (system/Skript_vysledky_vXX.gs) a ta je zapíše do Google tabulky.
   - Když se odeslání nepovede (offline), události čekají ve frontě
     v prohlížeči a odešlou se později (i při příštím otevření testu).
   - Zařízení má náhodné ID (localStorage), přezdívku nastaví zarizeni.html?u=<přezdívka>.
   - Plné úložiště (01.11.2026, Pouceni bod 21): rozpracované testy (klíč annschool:test:<adresa>) zůstávají
     v prohlížeči, dokud se test nedokončí nebo nezačne znovu, a úložiště (Safari asi 5 MB) se zaplní.
     Pak se mažou uložené testy – nejdřív dokončené, potom nejstarší, nikdy test na této stránce.
     Při načtení stránky se ověří rezerva pro frontu s obrázkem papíru. Když se fronta ani tak nevejde,
     obrázky papíru zůstanou jen ve frontě v paměti (odešlou se, dokud je stránka otevřená) – dřív se zahodily.
     Co se smazalo, se pošle jako událost „uloziste“.
   ===================================================================== */
(function () {
  "use strict";

  /* ---------- NASTAVENÍ: adresa webové aplikace (…/exec) ---------- */
  const ENDPOINT = "https://script.google.com/macros/s/AKfycbye7QxraOWZfrZZ-hXfhySeELki89n3U63MA1zPjcZbrUseyDVIu3cT9qDIxz-CKAUPmQ/exec";

  const KEY = "annschool:";
  const endpoint = () => (typeof window.ANNSCHOOL_ENDPOINT === "string" ? window.ANNSCHOOL_ENDPOINT : ENDPOINT);

  function ls(k, v) {
    try {
      if (v === undefined) return localStorage.getItem(KEY + k);
      if (v === null) localStorage.removeItem(KEY + k); else localStorage.setItem(KEY + k, v);
    } catch (e) { /* soukromé okno, zablokované úložiště */ }
    return null;
  }
  function rid(n) {
    const a = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    const r = (window.crypto && crypto.getRandomValues) ? crypto.getRandomValues(new Uint8Array(n))
      : Array.from({ length: n }, () => Math.floor(Math.random() * 256));
    let s = ""; for (let i = 0; i < n; i++) s += a[r[i] % a.length];
    return s;
  }

  /* ---------- zařízení a přezdívka ---------- */
  let zarizeniId = ls("zarizeni");
  if (!zarizeniId) { zarizeniId = rid(6); ls("zarizeni", zarizeniId); }
  const prezdivka = () => ls("prezdivka") || "";
  function nastavPrezdivku(p) {
    p = String(p || "").trim().toLowerCase().replace(/[^a-z0-9áčďéěíňóřšťúůýž_-]/g, "").slice(0, 24);
    ls("prezdivka", p || null);
    return p;
  }

  /* ---------- fronta a odesílání ---------- */
  let fronta = [];
  try { fronta = JSON.parse(ls("fronta") || "[]"); if (!Array.isArray(fronta)) fronta = []; } catch (e) { fronta = []; }
  let kontext = {}, posilam = false, casovac = 0, stav = "", posledniChyba = "";
  const posluchaci = [];

  /* ---------- místo v úložišti ---------- */
  const TEST_KEY = KEY + "test:", MUJ_TEST = TEST_KEY + location.pathname, REZERVA = 500000;
  const uvolneno = [];                               // smazané uložené testy (událost „uloziste“)
  let jenVPameti = false, ulozisteHlaseno = false;
  function jePlne(e) {
    return !!e && (e.name === "QuotaExceededError" || e.name === "NS_ERROR_DOM_QUOTA_REACHED" || e.code === 22 || e.code === 1014);
  }
  // uložené testy jiných stránek: nejdřív dokončené, pak od nejstaršího
  function ulozeneTesty() {
    const out = [];
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (!k || k.indexOf(TEST_KEY) !== 0 || k === MUJ_TEST) continue;
        const v = localStorage.getItem(k) || "";
        let x = null; try { x = JSON.parse(v); } catch (e) { x = null; }
        const qs = x && Array.isArray(x.qs) ? x.qs : [];
        out.push({ k, vel: v.length, cas: (x && Number(x.ulozeno)) || 0, hotovo: qs.length > 0 && qs.every(q => q && q.st && q.st.hotovo) });
      }
    } catch (e) { /* úložiště nedostupné */ }
    return out.sort((a, b) => (b.hotovo - a.hotovo) || (a.cas - b.cas));
  }
  function uvolniJeden() {
    const t = ulozeneTesty()[0];
    if (!t) return false;
    try { localStorage.removeItem(t.k); } catch (e) { return false; }
    uvolneno.push({ test: t.k.slice(TEST_KEY.length), vel: t.vel, hotovo: t.hotovo, ulozeno: t.cas ? new Date(t.cas).toISOString() : "" });
    nahlasUloziste();
    return true;
  }
  // uloží; při plném úložišti maže uložené testy, dokud se nevejde (false = nevešlo se)
  function zkusUlozit(k, v) {
    for (let i = 0; i < 200; i++) {
      try { localStorage.setItem(k, v); return true; }
      catch (e) { if (!jePlne(e) || !uvolniJeden()) return false; }
    }
    return false;
  }
  function pridejDetail(d, x) {
    let o = {};
    try { o = typeof d === "string" ? JSON.parse(d) : (d || {}); } catch (e) { o = { puvodni: String(d) }; }
    if (!o || typeof o !== "object" || Array.isArray(o)) o = { puvodni: o };
    return JSON.stringify(Object.assign(o, x));
  }
  function obsazeno() {
    const k = [];
    try { for (let i = 0; i < localStorage.length; i++) { const n = localStorage.key(i); k.push({ k: n, vel: n.length + (localStorage.getItem(n) || "").length }); } }
    catch (e) { /* nic */ }
    return { celkem: k.reduce((a, x) => a + x.vel, 0), klicu: k.length, nejvetsi: k.sort((a, b) => b.vel - a.vel).slice(0, 8) };
  }
  // jednou za načtení stránky; se zpožděním, aby událost měla relaci a test (nastavKontext)
  function nahlasUloziste() {
    if (ulozisteHlaseno) return;
    ulozisteHlaseno = true;
    setTimeout(() => zapis({ udalost: "uloziste", detail: Object.assign({ smazano: uvolneno, obrazky_jen_v_pameti: jenVPameti }, obsazeno()) }), 3000);
  }

  function ulozFrontu() {
    if (zkusUlozit(KEY + "fronta", JSON.stringify(fronta))) return;
    // ani po uvolnění se nevejde: do úložiště jen texty, obrázky papíru zůstanou ve frontě v paměti
    jenVPameti = true; nahlasUloziste();
    const bez = fronta.map(u => typeof u.papir === "string" && u.papir.indexOf("data:") === 0
      ? Object.assign({}, u, { papir: "", detail: pridejDetail(u.detail, { papir_neulozen: true }) }) : u);
    try { localStorage.setItem(KEY + "fronta", JSON.stringify(bez)); } catch (e) { /* nevadí */ }
  }
  // rezerva při načtení stránky (fronta s obrázkem papíru, uložení rozpracovaného testu)
  (function rezerva() {
    const k = KEY + "rezerva";
    zkusUlozit(k, "x".repeat(REZERVA));
    try { localStorage.removeItem(k); } catch (e) { /* nic */ }
  })();
  function oznam() {
    stav = !endpoint() ? "vypnuto" : fronta.length ? (posledniChyba ? "čeká (offline)" : "odesílám") : "odesláno";
    posluchaci.forEach(f => { try { f(stav, fronta.length); } catch (e) { /* nic */ } });
  }

  function zapis(u) {
    const e = Object.assign({
      id: rid(10), cas: new Date().toISOString(), zarizeni: zarizeniId, prezdivka: prezdivka()
    }, kontext, u);
    if (e.detail && typeof e.detail !== "string") e.detail = JSON.stringify(e.detail);
    fronta.push(e);
    ulozFrontu();
    naplanuj(300);
    return e;
  }
  function naplanuj(ms) {
    clearTimeout(casovac);
    casovac = setTimeout(odesli, ms);
    oznam();
  }
  async function odesli() {
    if (posilam || !fronta.length || !endpoint()) { oznam(); return; }
    posilam = true;
    // dávka do ~3 MB (obrázky papíru jsou největší)
    const davka = []; let vel = 0;
    for (const u of fronta) {
      const s = JSON.stringify(u).length;
      if (davka.length && vel + s > 3e6) break;
      davka.push(u); vel += s;
      if (davka.length >= 25) break;
    }
    try {
      const r = await fetch(endpoint(), {
        method: "POST", redirect: "follow",
        headers: { "Content-Type": "text/plain;charset=utf-8" },     // „jednoduchý“ požadavek bez CORS preflight
        body: JSON.stringify({ app: "annschool", udalosti: davka })
      });
      const j = await r.json();
      if (!j || !j.ok) throw new Error((j && j.chyba) || "server neodpověděl ok");
      const ids = new Set(davka.map(u => u.id));
      fronta = fronta.filter(u => !ids.has(u.id));
      posledniChyba = "";
      ulozFrontu();
      posilam = false;
      if (fronta.length) naplanuj(200); else oznam();
    } catch (err) {
      posilam = false;
      posledniChyba = String(err && err.message || err);
      naplanuj(20000);                               // zkusí znovu za 20 s
    }
  }
  // při zavírání stránky ještě poslední pokus (beacon; duplicity server zahodí podle id)
  function beacon() {
    if (!fronta.length || !endpoint() || !navigator.sendBeacon) return;
    try {
      const davka = fronta.filter(u => !u.papir).slice(0, 50);
      if (davka.length) navigator.sendBeacon(endpoint(), new Blob([JSON.stringify({ app: "annschool", udalosti: davka })], { type: "text/plain;charset=utf-8" }));
    } catch (e) { /* nic */ }
  }
  window.addEventListener("online", () => naplanuj(500));
  window.addEventListener("pagehide", beacon);
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") naplanuj(1000); });

  /* ---------- čtení pro přehled ---------- */
  async function nacti(akce, param) {
    if (!endpoint()) throw new Error("Není nastavená adresa webové aplikace (system/lib/zaznam.js, ENDPOINT).");
    const q = new URLSearchParams(Object.assign({ akce }, param || {}));
    const r = await fetch(endpoint() + "?" + q.toString(), { redirect: "follow", cache: "no-store" });
    const j = await r.json();
    if (!j.ok) throw new Error(j.chyba || "chyba serveru");
    return j;
  }

  window.Zaznam = {
    get zarizeni() { return zarizeniId; },
    get prezdivka() { return prezdivka(); },
    nastavPrezdivku,
    nastavKontext(k) { kontext = Object.assign({}, k); },
    noveId: rid,
    zapis, odesli, nacti, beacon,
    get fronta() { return fronta.length; },
    get zapnuto() { return !!endpoint(); },
    naStav(f) { posluchaci.push(f); oznam(); }
  };
  naplanuj(1500);                                    // dodělat frontu z minula
})();
