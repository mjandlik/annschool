/* =====================================================================
   SLEDOVÁNÍ STRÁNEK – Ann School (system/lib/sledovani.js)
   Pro stránky s teorií v HTML (studijní materiály, taháky, simulátory, zápisky) a rozcestník. PDF se nesledují.
   Načítá se za zaznam.js:
     <script src="../system/lib/zaznam.js"></script>
     <script src="../system/lib/sledovani.js" data-typ="simulator"></script>
   data-typ: material | tahak | pracovni-list | simulator | zapisky | rozcestnik | … (nepovinné, jinak se odhadne z adresy)

   Zapisuje (system/lib/zaznam.js → Google tabulka):
   - „otevreni“  … otevření stránky (odkud: rozcestník / přímý odkaz, rozměry okna),
   - „odchod“    … návrat z jiné aplikace / panelu / zamčení (jak dlouho byla pryč),
   - „stranka“   … souhrn: doba otevření, viditelná a aktivní doba, odchody, posouvání,
                   klepnutí, tahy perem a čas v jednotlivých částech (oblastech) stránky.
                   Posílá se při odchodu ze stránky a každou minutu, pokud se něco změnilo.
   Aktivní = stránka je vidět a v posledních 30 s se posouvalo, klepalo nebo psalo.
   Oblast: desetina výšky stránky podle středu obrazovky („10–20 %“), nebo co nastaví stránka (kapitola).
   Stránka může oblast nastavit sama: Sledovani.oblast("s. 3"); Sledovani.pocetOblasti(12).
   Návod: system/Navod_material_vXX.md (sledování) a Navod_test_vXX.md, kap. 9.
   ===================================================================== */
(function () {
  "use strict";
  if (!window.Zaznam) return;
  const skript = document.currentScript;
  const AKTIVITA_MS = 30000;
  const cesta = location.pathname.replace(/^.*\/annschool\//, "").replace(/^\//, "") || "index.html";
  const odhadTyp = () => {
    if (/(^|\/)(index\.html)?$/.test(cesta)) return "rozcestnik";
    const m = cesta.match(/_([a-z0-9-]+)_v\d\d\.html$/);
    return m ? m[1] : "stranka";
  };
  const S = {
    typ: (skript && skript.dataset.typ) || odhadTyp(),
    adresa: cesta, nazev: document.title, verze: (cesta.match(/_(v\d\d)\./) || [])[1] || "",
    start: Date.now(), viditelne: 0, aktivni: 0, odchody: 0, odchodyMs: 0,
    scrollMax: 0, scrollPx: 0, klepnuti: 0, klavesy: 0, tahy: 0,
    oblasti: {}, pocetOblasti: 0, vlastniOblast: null
  };
  let posledniVstup = Date.now(), tik = Date.now(), skryto = 0, posledniY = window.scrollY, posledniPodpis = "";

  function oblastTed() {
    if (S.vlastniOblast) return S.vlastniOblast;
    const H = Math.max(1, document.documentElement.scrollHeight);
    const stred = (window.scrollY + innerHeight / 2) / H;
    const p = Math.min(9, Math.max(0, Math.floor(stred * 10)));
    return `${p * 10}–${p * 10 + 10} %`;
  }
  // každou sekundu přičti viditelný a aktivní čas a čas v aktuální oblasti
  function pricti() {
    const now = Date.now(), d = Math.min(now - tik, 5000);
    tik = now;
    if (document.visibilityState !== "visible") return;
    S.viditelne += d;
    if (now - posledniVstup <= AKTIVITA_MS) {
      S.aktivni += d;
      const o = oblastTed();
      if (o) S.oblasti[o] = (S.oblasti[o] || 0) + d;           // PDF: dokud se nenačte, oblast není
    }
  }
  function vstup() { pricti(); posledniVstup = Date.now(); }
  function scroll() {
    const y = window.scrollY;
    S.scrollPx += Math.abs(y - posledniY); posledniY = y;
    const H = document.documentElement.scrollHeight;
    if (H > 0) S.scrollMax = Math.max(S.scrollMax, Math.min(100, Math.round((y + innerHeight) / H * 100)));
    vstup();
  }
  function souhrn(vynutit) {
    pricti();
    const det = {
      typ: S.typ, otevreno_s: Math.round((Date.now() - S.start) / 1000), viditelne_s: Math.round(S.viditelne / 1000),
      aktivni_s: Math.round(S.aktivni / 1000), odchody: S.odchody, odchody_s: Math.round(S.odchodyMs / 1000),
      scroll_max_pct: S.scrollMax, scroll_px: Math.round(S.scrollPx), klepnuti: S.klepnuti, klavesy: S.klavesy, tahy_perem: S.tahy,
      pocet_oblasti: S.pocetOblasti || undefined,
      oblasti: Object.fromEntries(Object.entries(S.oblasti).map(([k, v]) => [k, Math.round(v / 1000)]).filter(([, v]) => v > 0))
    };
    const podpis = JSON.stringify([det.aktivni_s, det.odchody, det.scroll_max_pct, det.klepnuti, det.oblasti]);
    if (!vynutit && podpis === posledniPodpis) return;
    posledniPodpis = podpis;
    Zaznam.zapis({ udalost: "stranka", typ: S.typ, doba_s: det.aktivni_s, odchody: S.odchody, odchody_s: det.odchody_s, detail: det });
  }

  Zaznam.nastavKontext({ relace: Zaznam.noveId(8), test: S.adresa, nazev: S.nazev, verze: S.verze });
  const odkud = new URLSearchParams(location.search).get("z") ||
    (document.referrer && document.referrer.indexOf(location.host) >= 0 ? "web" : (document.referrer ? "jinde" : "primo"));
  Zaznam.zapis({ udalost: "otevreni", typ: S.typ, detail: { typ: S.typ, odkud, sirka: innerWidth, vyska: innerHeight,
    orientace: innerWidth > innerHeight ? "na šířku" : "na výšku" } });

  window.addEventListener("scroll", scroll, { passive: true });
  ["pointerdown", "touchstart"].forEach(t => window.addEventListener(t, e => {
    if (t === "pointerdown") { S.klepnuti++; if (e.pointerType === "pen") S.tahy++; }
    vstup();
  }, { passive: true, capture: true }));
  window.addEventListener("pointermove", () => { if (Date.now() - posledniVstup > 2000) vstup(); }, { passive: true });
  window.addEventListener("wheel", vstup, { passive: true });
  window.addEventListener("keydown", () => { S.klavesy++; vstup(); }, { capture: true });
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") { pricti(); skryto = Date.now(); souhrn(false); Zaznam.beacon(); }
    else if (skryto) {
      const d = Date.now() - skryto; skryto = 0; tik = Date.now();
      S.odchody++; S.odchodyMs += d; posledniVstup = Date.now();
      Zaznam.zapis({ udalost: "odchod", typ: S.typ, doba_s: Math.round(d / 1000) });
    }
  });
  window.addEventListener("pagehide", () => { souhrn(false); Zaznam.beacon(); });
  setInterval(pricti, 1000);
  setInterval(() => { if (document.visibilityState === "visible") souhrn(false); }, 60000);

  window.Sledovani = {
    oblast(k) { pricti(); S.vlastniOblast = k; },
    pocetOblasti(n) { S.pocetOblasti = n; },
    klik(cil, text) { Zaznam.zapis({ udalost: "klik", typ: S.typ, detail: { cil, text } }); },
    souhrn: () => souhrn(true),
    get stav() { pricti(); return JSON.parse(JSON.stringify(S)); }
  };
})();
