/* =====================================================================
   ZÁZNAM VÝSLEDKŮ – Ann School (system/lib/zaznam.js)
   Sdílený modul pro testy (šablona v16+), přehled výsledků (vysledky.html)
   a označení zařízení (zarizeni.html). Návod: system/Navod_test_vXX.md, kap. 9.

   - Události testu se posílají na webovou aplikaci Google Apps Script
     (system/Skript_vysledky_vXX.gs) a ta je zapíše do Google tabulky.
   - Když se odeslání nepovede (offline), události čekají ve frontě
     v prohlížeči a odešlou se později (i při příštím otevření testu).
   - Zařízení má náhodné ID (localStorage), přezdívku nastaví zarizeni.html?u=<přezdívka>.
   ===================================================================== */
(function () {
  "use strict";

  /* ---------- NASTAVENÍ: adresa webové aplikace (…/exec) ---------- */
  const ENDPOINT = "";

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

  function ulozFrontu() {
    try { localStorage.setItem(KEY + "fronta", JSON.stringify(fronta)); }
    catch (e) {
      // úložiště plné: obrázky papíru se zahodí, texty zůstanou
      fronta.forEach(u => { if (u.papir) { u.papir = ""; u.detail = Object.assign({}, u.detail, { papir_zahozen: true }); } });
      try { localStorage.setItem(KEY + "fronta", JSON.stringify(fronta)); } catch (e2) { /* nevadí */ }
    }
  }
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
    zapis, odesli, nacti,
    get fronta() { return fronta.length; },
    get zapnuto() { return !!endpoint(); },
    naStav(f) { posluchaci.push(f); oznam(); }
  };
  naplanuj(1500);                                    // dodělat frontu z minula
})();
