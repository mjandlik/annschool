/* =====================================================================
   vektory.js – vektorová síť pro Ann School (system/lib/vektory.js)
   ---------------------------------------------------------------------
   Sdílená knihovna pro simulátor i HTML testy (rýsování vektorů).
   Popis API: system/Navod_test_vXX.md, kapitola „Knihovna vektory.js“.

   Použití:
     <link rel="stylesheet" href="../system/lib/vektory.css">
     <script src="../system/lib/vektory.js"></script>
     const sit = new Vektory.Sit(document.getElementById("misto"), {
       xmin: -10, xmax: 10, ymin: -10, ymax: 10, osy: true, cisla: true,
       onChange: (sit, info) => { … }
     });
     sit.pridej({ id: "a", nazev: "a", barva: "#2b5cab", x1: 1, y1: 1, x2: 5, y2: 4 });
     sit.kresli = { id: "b", nazev: "b", barva: "#b3261e" };   // Pencil nakreslí b

   Ovládání: Apple Pencil a myš kreslí a tahají body, prst posouvá stránku
   (Vektory.nastavPrst(true) zapne ovládání prstem).
   ===================================================================== */
(function (global) {
  "use strict";

  /* ---------- čísla a výpočty ---------- */
  const MINUS = "−";

  // české číslo: desetinná čárka, znak minus
  function fmt(n, dec) {
    if (dec === undefined) dec = 1;
    const k = Math.pow(10, dec);
    let r = Math.round(n * k) / k;
    if (Object.is(r, -0) || r === 0) r = 0;
    let s = String(Math.abs(r)).replace(".", ",");
    return (r < 0 ? MINUS : "") + s;
  }
  // číslo v závorce, pokud je záporné: (−3)
  function zav(n) { return n < 0 ? "(" + fmt(n) + ")" : fmt(n); }

  function slozky(v) { return { dx: v.x2 - v.x1, dy: v.y2 - v.y1 }; }
  function velikost(dx, dy) {
    if (typeof dx === "object") { const s = dx.dx !== undefined ? dx : slozky(dx); return Math.hypot(s.dx, s.dy); }
    return Math.hypot(dx, dy);
  }
  function soucet(list) {
    return list.reduce((a, s) => ({ dx: a.dx + s.dx, dy: a.dy + s.dy }), { dx: 0, dy: 0 });
  }
  function opacny(s) { return { dx: -s.dx, dy: -s.dy }; }

  // úhel směru s vodorovnou přímkou ve stupních (0–90°)
  function uhel(dx, dy) {
    if (dx === 0 && dy === 0) return null;
    return Math.atan2(Math.abs(dy), Math.abs(dx)) * 180 / Math.PI;
  }

  // „4 doprava, 3 nahoru“
  function popisSlozek(dx, dy) {
    const p = [];
    if (dx) p.push(fmt(Math.abs(dx)) + (dx > 0 ? " doprava" : " doleva"));
    if (dy) p.push(fmt(Math.abs(dy)) + (dy > 0 ? " nahoru" : " dolů"));
    return p.length ? p.join(", ") : "nulový vektor";
  }

  // √25 = 5 | √34 ≈ 5,8  (n2 = součet čtverců, celé číslo)
  function odmocnina(n2, dec) {
    if (dec === undefined) dec = 1;
    const r = Math.sqrt(n2), ri = Math.round(r);
    if (Math.abs(ri * ri - n2) < 1e-9) return { text: "√" + fmt(n2, 6) + " = " + fmt(ri, 0), hodnota: ri, presne: true };
    return { text: "√" + fmt(n2, 6) + " ≈ " + fmt(r, dec), hodnota: r, presne: false };
  }

  /* ---------- ovládání prstem (společné pro všechny sítě na stránce) ---------- */
  let prst = false;
  function nastavPrst(on) { prst = !!on; }

  /* ---------- síť ---------- */
  const DEF = {
    xmin: 0, xmax: 20, ymin: 0, ymax: 20,
    osy: false,            // osy x, y (pokud leží v rozsahu)
    cisla: false,          // čísla na osách
    popisOs: true,         // písmena x, y u os
    meritko: 1,            // 1 dílek = meritko jednotek
    jednotka: "N",
    upravy: true,          // body jdou vybírat a přesouvat
    posun: true,           // celý vektor jde posunout za střed
    onChange: null         // (sit, info) – při každé změně (i během táhnutí)
  };

  class Sit {
    constructor(el, opt) {
      this.el = el;
      this.o = Object.assign({}, DEF, opt || {});
      this.vektory = [];      // { id, nazev, barva, x1, y1, x2, y2, upravitelny, tloustka, carkovane, popisBodu, souradnice }
      this.pomocne = [];      // čáry a vektory bez ovládání: { x1, y1, x2, y2, barva, carkovane, sipka, nazev, tloustka }
      this.body = [];         // popsané body: { x, y, popis, barva }
      this.oblouky = [];      // { x, y, r, a1, a2, barva, popis } – úhel (v dílcích, radiány)
      this.kresli = null;     // šablona nového vektoru pro kreslení Pencilem, nebo null
      this.vybrany = null;    // { id, bod: 1 | 2 }
      this.akce = null;
      this.raf = 0;
      el.classList.add("vk-sit");
      this.cv = document.createElement("canvas");
      el.appendChild(this.cv);
      this.ctx = this.cv.getContext("2d");
      this.bind();
      this.resize();
      if (global.ResizeObserver) {
        this.ro = new ResizeObserver(() => this.resize());
        this.ro.observe(el);
      } else {
        global.addEventListener("resize", () => this.resize());
      }
    }

    /* ---- rozsah a geometrie ---- */
    nastavRozsah(xmin, xmax, ymin, ymax) {
      const o = this.o;
      if (o.xmin === xmin && o.xmax === xmax && o.ymin === ymin && o.ymax === ymax) return;
      Object.assign(o, { xmin, xmax, ymin, ymax });
      this.resize();
    }
    resize() {
      const o = this.o;
      const W = Math.max(120, this.el.clientWidth || 300);
      const nx = o.xmax - o.xmin, ny = o.ymax - o.ymin;
      const okraj = o.cisla ? 24 : 10;
      this.pad = { l: okraj, r: o.osy && o.popisOs ? 16 : 10, t: o.osy && o.popisOs ? 16 : 10, b: okraj };
      this.cell = (W - this.pad.l - this.pad.r) / nx;
      const H = Math.round(this.pad.t + this.pad.b + this.cell * ny);
      this.W = W; this.H = H;
      const dpr = global.devicePixelRatio || 1;
      this.dpr = dpr;
      this.cv.width = Math.round(W * dpr); this.cv.height = Math.round(H * dpr);
      this.cv.style.width = W + "px"; this.cv.style.height = H + "px";
      this.kresliHned();
    }
    px(x) { return this.pad.l + (x - this.o.xmin) * this.cell; }
    py(y) { return this.pad.t + (this.o.ymax - y) * this.cell; }
    uzel(cx, cy) {   // nejbližší uzel sítě k bodu na obrazovce (v rozsahu)
      const o = this.o;
      let x = Math.round(o.xmin + (cx - this.pad.l) / this.cell);
      let y = Math.round(o.ymax - (cy - this.pad.t) / this.cell);
      x = Math.min(o.xmax, Math.max(o.xmin, x)); y = Math.min(o.ymax, Math.max(o.ymin, y));
      return { x, y };
    }

    /* ---- vektory ---- */
    pridej(v) {
      const n = Object.assign({ upravitelny: true, tloustka: 2.6, carkovane: false, popisBodu: null, souradnice: false }, v);
      const i = this.vektory.findIndex(w => w.id === n.id);
      if (i >= 0) this.vektory[i] = Object.assign(this.vektory[i], n); else this.vektory.push(n);
      this.prekresli();
      return n;
    }
    vektor(id) { return this.vektory.find(v => v.id === id) || null; }
    odeber(id) {
      this.vektory = this.vektory.filter(v => v.id !== id);
      if (this.vybrany && this.vybrany.id === id) this.vybrany = null;
      this.prekresli(); this.zmena({ typ: "smazan", id });
    }
    vymaz() { this.vektory = []; this.pomocne = []; this.body = []; this.oblouky = []; this.vybrany = null; this.prekresli(); }
    nastav(id, x1, y1, x2, y2) {
      const v = this.vektor(id); if (!v) return;
      Object.assign(v, { x1, y1, x2, y2 }); this.prekresli(); this.zmena({ typ: "nastaven", id });
    }
    vyber(id, bod) { this.vybrany = id ? { id, bod } : null; this.prekresli(); }
    zmena(info) { if (this.o.onChange) this.o.onChange(this, info); }

    /* ---- kreslení ---- */
    prekresli() { if (!this.raf) this.raf = requestAnimationFrame(() => { this.raf = 0; this.kresliHned(); }); }
    kresliHned() {
      const c = this.ctx, o = this.o, d = this.dpr;
      c.setTransform(d, 0, 0, d, 0, 0);
      c.clearRect(0, 0, this.W, this.H);
      c.fillStyle = "#ffffff"; c.fillRect(0, 0, this.W, this.H);
      // mřížka
      c.lineWidth = 1; c.strokeStyle = "#e3e3dc"; c.beginPath();
      for (let x = o.xmin; x <= o.xmax; x++) { const X = Math.round(this.px(x)) + .5; c.moveTo(X, this.py(o.ymax)); c.lineTo(X, this.py(o.ymin)); }
      for (let y = o.ymin; y <= o.ymax; y++) { const Y = Math.round(this.py(y)) + .5; c.moveTo(this.px(o.xmin), Y); c.lineTo(this.px(o.xmax), Y); }
      c.stroke();
      if (o.osy) this.kresliOsy();
      this.oblouky.forEach(a => this.kresliOblouk(a));
      this.pomocne.forEach(p => this.kresliVektor(p, true));
      this.vektory.forEach(v => this.kresliVektor(v, false));
      this.body.forEach(b => this.kresliBod(b));
      this.vektory.forEach(v => this.kresliPopisy(v));
      if (this.akce && this.akce.typ === "kresli" && !this.akce.vytvoren) {
        const s = this.akce.start; c.fillStyle = this.kresli ? this.kresli.barva : "#1d1d1b";
        c.beginPath(); c.arc(this.px(s.x), this.py(s.y), 4.5, 0, 7); c.fill();
      }
    }
    kresliOsy() {
      const c = this.ctx, o = this.o;
      c.save();
      c.strokeStyle = "#55554f"; c.fillStyle = "#55554f"; c.lineWidth = 1.4;
      const hrot = (x, y, ux, uy) => {
        c.beginPath(); c.moveTo(x, y); c.lineTo(x - ux * 8 - uy * 4, y - uy * 8 + ux * 4); c.lineTo(x - ux * 8 + uy * 4, y - uy * 8 - ux * 4); c.closePath(); c.fill();
      };
      c.font = "12px -apple-system, 'Segoe UI', Roboto, sans-serif";
      const krok = this.cell >= 22 ? 1 : this.cell >= 11 ? 2 : 5;
      if (o.ymin <= 0 && o.ymax >= 0) {   // osa x
        const Y = Math.round(this.py(0)) + .5, x2 = this.px(o.xmax) + this.pad.r - 2;
        c.beginPath(); c.moveTo(this.px(o.xmin), Y); c.lineTo(x2, Y); c.stroke(); hrot(x2, Y, 1, 0);
        if (o.popisOs) { c.textAlign = "right"; c.textBaseline = "bottom"; c.font = "italic 14px Georgia, serif"; c.fillText("x", x2 - 2, Y - 4); }
        if (o.cisla) {
          c.font = "11px -apple-system, 'Segoe UI', Roboto, sans-serif"; c.textAlign = "center"; c.textBaseline = "top";
          for (let x = o.xmin; x <= o.xmax; x++) if (x !== 0 && x % krok === 0) {
            c.fillRect(this.px(x) - .5, Y - 3, 1, 6); c.fillText(fmt(x), this.px(x), Y + 4);
          }
        }
      }
      if (o.xmin <= 0 && o.xmax >= 0) {   // osa y
        const X = Math.round(this.px(0)) + .5, y2 = this.py(o.ymax) - this.pad.t + 2;
        c.beginPath(); c.moveTo(X, this.py(o.ymin)); c.lineTo(X, y2); c.stroke(); hrot(X, y2, 0, -1);
        if (o.popisOs) { c.textAlign = "left"; c.textBaseline = "top"; c.font = "italic 14px Georgia, serif"; c.fillText("y", X + 6, y2); }
        if (o.cisla) {
          c.font = "11px -apple-system, 'Segoe UI', Roboto, sans-serif"; c.textAlign = "right"; c.textBaseline = "middle";
          for (let y = o.ymin; y <= o.ymax; y++) if (y !== 0 && y % krok === 0) {
            c.fillRect(X - 3, this.py(y) - .5, 6, 1); c.fillText(fmt(y), X - 5, this.py(y));
          }
        }
        if (o.cisla && o.ymin <= 0 && o.ymax >= 0) { c.textAlign = "right"; c.textBaseline = "top"; c.fillText("0", X - 4, this.py(0) + 3); }
      }
      c.restore();
    }
    kresliVektor(v, pomocny) {
      const c = this.ctx;
      const X1 = this.px(v.x1), Y1 = this.py(v.y1), X2 = this.px(v.x2), Y2 = this.py(v.y2);
      const L = Math.hypot(X2 - X1, Y2 - Y1);
      if (L < 0.5) return;
      const ux = (X2 - X1) / L, uy = (Y2 - Y1) / L;
      const w = v.tloustka || (pomocny ? 1.6 : 2.6);
      const sipka = v.sipka !== false;
      const hl = sipka ? Math.min(L * .45, 8 + w * 2.2) : 0, hw = hl * .45;
      c.save();
      c.strokeStyle = v.barva || "#1d1d1b"; c.fillStyle = v.barva || "#1d1d1b";
      c.lineWidth = w; c.lineCap = "round";
      if (v.carkovane) c.setLineDash([6, 5]);
      c.beginPath(); c.moveTo(X1, Y1); c.lineTo(X2 - ux * hl * .8, Y2 - uy * hl * .8); c.stroke();
      c.setLineDash([]);
      if (sipka) {
        c.beginPath(); c.moveTo(X2, Y2);
        c.lineTo(X2 - ux * hl - uy * hw, Y2 - uy * hl + ux * hw);
        c.lineTo(X2 - ux * hl + uy * hw, Y2 - uy * hl - ux * hw); c.closePath(); c.fill();
      }
      if (!pomocny) {   // počáteční bod
        c.beginPath(); c.arc(X1, Y1, 3.6 + w * .3, 0, 7); c.fill();
      }
      c.restore();
      if (v.nazev) this.kresliNazev(v, X1, Y1, X2, Y2, ux, uy);
    }
    // název vektoru se šipkou nad písmeny, kolmo vedle středu
    kresliNazev(v, X1, Y1, X2, Y2, ux, uy) {
      const c = this.ctx;
      const strana = v.stranaNazvu || 1;
      let nx = uy * strana, ny = -ux * strana;   // kolmice (vlevo od směru)
      const mx = (X1 + X2) / 2 + nx * 15, my = (Y1 + Y2) / 2 + ny * 15;
      const t = String(v.nazev);
      const m = /^([−-]?)(.*)$/.exec(t);
      const pred = m[1] ? MINUS : "", hlavni = m[2];
      c.save();
      c.font = (v.tucne ? "bold " : "") + "italic 16px Georgia, 'Times New Roman', serif";
      c.textBaseline = "middle"; c.textAlign = "left";
      const w1 = c.measureText(pred).width, w2 = c.measureText(hlavni).width;
      const x0 = mx - (w1 + w2) / 2;
      // podklad pro čitelnost
      c.fillStyle = "rgba(255,255,255,.85)"; c.fillRect(x0 - 3, my - 14, w1 + w2 + 6, 24);
      c.fillStyle = v.barva || "#1d1d1b";
      c.fillText(pred, x0, my + 2); c.fillText(hlavni, x0 + w1, my + 2);
      // šipka nad
      const ax1 = x0 + w1 + 1, ax2 = x0 + w1 + w2 + 1, ay = my - 9;
      c.strokeStyle = v.barva || "#1d1d1b"; c.lineWidth = 1.2;
      c.beginPath(); c.moveTo(ax1, ay); c.lineTo(ax2, ay); c.moveTo(ax2 - 3.5, ay - 2.5); c.lineTo(ax2, ay); c.lineTo(ax2 - 3.5, ay + 2.5); c.stroke();
      c.restore();
    }
    kresliPopisy(v) {
      const c = this.ctx, sel = this.vybrany && this.vybrany.id === v.id ? this.vybrany.bod : 0;
      const X1 = this.px(v.x1), Y1 = this.py(v.y1), X2 = this.px(v.x2), Y2 = this.py(v.y2);
      // zvýraznění vybraného bodu
      if (sel) {
        const X = sel === 1 ? X1 : X2, Y = sel === 1 ? Y1 : Y2;
        c.save(); c.globalAlpha = .22; c.fillStyle = v.barva; c.beginPath(); c.arc(X, Y, 14, 0, 7); c.fill();
        c.globalAlpha = 1; c.strokeStyle = v.barva; c.lineWidth = 2; c.beginPath(); c.arc(X, Y, 14, 0, 7); c.stroke(); c.restore();
      }
      // úchyt pro posun celého vektoru
      if (v.upravitelny && this.o.upravy && this.o.posun && (X1 !== X2 || Y1 !== Y2)) {
        c.save(); c.strokeStyle = v.barva; c.fillStyle = "#fff"; c.lineWidth = 1.6;
        c.beginPath(); c.arc((X1 + X2) / 2, (Y1 + Y2) / 2, 5, 0, 7); c.fill(); c.stroke(); c.restore();
      }
      if (!v.popisBodu) return;
      const L = Math.hypot(X2 - X1, Y2 - Y1) || 1, ux = (X2 - X1) / L, uy = (Y2 - Y1) / L;
      const txt = (nm, x, y) => nm + (v.souradnice ? "[" + fmt(x) + "; " + fmt(y) + "]" : "");
      this.stitek(txt(v.popisBodu[0], v.x1, v.y1), X1 - ux * 16, Y1 - uy * 16, v.barva);
      this.stitek(txt(v.popisBodu[1], v.x2, v.y2), X2 + ux * 16, Y2 + uy * 16, v.barva);
    }
    stitek(t, X, Y, barva) {
      const c = this.ctx;
      c.save(); c.font = "600 13px -apple-system, 'Segoe UI', Roboto, sans-serif";
      const w = c.measureText(t).width;
      let x = Math.min(this.W - w - 4, Math.max(4, X - w / 2)), y = Math.min(this.H - 10, Math.max(10, Y));
      c.fillStyle = "rgba(255,255,255,.88)"; c.fillRect(x - 3, y - 9, w + 6, 18);
      c.fillStyle = barva || "#1d1d1b"; c.textBaseline = "middle"; c.textAlign = "left"; c.fillText(t, x, y + 1);
      c.restore();
    }
    kresliBod(b) {
      const c = this.ctx, X = this.px(b.x), Y = this.py(b.y);
      c.save(); c.fillStyle = b.barva || "#1d1d1b";
      c.beginPath(); c.arc(X, Y, 3.4, 0, 7); c.fill(); c.restore();
      if (b.popis) {
        const dx = b.dx === undefined ? -12 : b.dx, dy = b.dy === undefined ? 12 : b.dy;
        this.stitek(b.popis, X + dx, Y + dy, b.barva);
      }
    }
    kresliOblouk(a) {
      const c = this.ctx, X = this.px(a.x), Y = this.py(a.y), r = a.r * this.cell;
      c.save(); c.strokeStyle = a.barva || "#6b6b66"; c.lineWidth = 1.3;
      // úhly v matematickém smyslu → na obrazovce je y obrácené
      c.beginPath(); c.arc(X, Y, r, -a.a1, -a.a2, a.a2 > a.a1); c.stroke();
      if (a.vodorovna) { c.setLineDash([4, 4]); c.beginPath(); c.moveTo(X, Y); c.lineTo(X + a.vodorovna * this.cell, Y); c.stroke(); }
      c.restore();
      if (a.popis) {
        const am = (a.a1 + a.a2) / 2, rr = r + 16;
        this.stitek(a.popis, X + Math.cos(am) * rr, Y - Math.sin(am) * rr, a.barva || "#6b6b66");
      }
    }

    /* ---- ovládání ---- */
    trefa(cx, cy) {   // co je pod prstem/Pencilem: { v, bod: 1|2|0 (0 = střed) }
      if (!this.o.upravy) return null;
      let best = null, bd = 1e9;
      const zkus = (v, bod, X, Y, lim, pen) => {
        const d = Math.hypot(cx - X, cy - Y);
        if (d <= lim && d + pen < bd) { bd = d + pen; best = { v, bod }; }
      };
      for (const v of this.vektory) {
        if (!v.upravitelny) continue;
        const X1 = this.px(v.x1), Y1 = this.py(v.y1), X2 = this.px(v.x2), Y2 = this.py(v.y2);
        const pen = this.vybrany && this.vybrany.id === v.id ? -2 : 0;
        zkus(v, 2, X2, Y2, 18, pen); zkus(v, 1, X1, Y1, 18, pen);
        if (this.o.posun) zkus(v, 0, (X1 + X2) / 2, (Y1 + Y2) / 2, 14, pen + 4);
      }
      return best;
    }
    bind() {
      const cv = this.cv;
      const smi = e => e.pointerType === "pen" || e.pointerType === "mouse" || (e.pointerType === "touch" && prst);
      const pos = e => { const r = cv.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
      cv.addEventListener("pointerdown", e => {
        if (!smi(e) || this.akce) return;
        e.preventDefault();
        try { cv.setPointerCapture(e.pointerId); } catch (_) { /* bez capture */ }
        const [cx, cy] = pos(e), u = this.uzel(cx, cy), t = this.trefa(cx, cy);
        if (t) {
          const v = t.v;
          this.akce = { typ: t.bod ? "bod" : "posun", v, bod: t.bod, start: u, x0: cx, y0: cy, pohyb: false,
            puv: { x1: v.x1, y1: v.y1, x2: v.x2, y2: v.y2 } };
        } else {
          this.akce = { typ: "kresli", start: u, x0: cx, y0: cy, pohyb: false, vytvoren: false };
        }
        this.prekresli();
      });
      cv.addEventListener("pointermove", e => {
        const a = this.akce; if (!a) return;
        e.preventDefault();
        const [cx, cy] = pos(e), u = this.uzel(cx, cy);
        if (Math.hypot(cx - a.x0, cy - a.y0) > 6) a.pohyb = true;
        if (!a.pohyb) return;
        const o = this.o;
        if (a.typ === "bod") {
          const v = a.v, jiny = a.bod === 1 ? [v.x2, v.y2] : [v.x1, v.y1];
          if (u.x === jiny[0] && u.y === jiny[1]) return;   // nulový vektor nepovolit
          const k = a.bod === 1 ? ["x1", "y1"] : ["x2", "y2"];
          if (v[k[0]] !== u.x || v[k[1]] !== u.y) { v[k[0]] = u.x; v[k[1]] = u.y; this.vybrany = { id: v.id, bod: a.bod }; this.prekresli(); this.zmena({ typ: "bod", id: v.id }); }
        } else if (a.typ === "posun") {
          const v = a.v, p = a.puv;
          // posun o celé dílky podle vzdálenosti od místa uchopení (ne podle zaokrouhleného uzlu)
          let ddx = Math.round((cx - a.x0) / this.cell), ddy = Math.round((a.y0 - cy) / this.cell);
          ddx = Math.max(o.xmin - Math.min(p.x1, p.x2), Math.min(o.xmax - Math.max(p.x1, p.x2), ddx));
          ddy = Math.max(o.ymin - Math.min(p.y1, p.y2), Math.min(o.ymax - Math.max(p.y1, p.y2), ddy));
          if (v.x1 !== p.x1 + ddx || v.y1 !== p.y1 + ddy) {
            Object.assign(v, { x1: p.x1 + ddx, y1: p.y1 + ddy, x2: p.x2 + ddx, y2: p.y2 + ddy });
            this.prekresli(); this.zmena({ typ: "posun", id: v.id });
          }
        } else if (a.typ === "kresli" && this.kresli) {
          if (u.x === a.start.x && u.y === a.start.y) return;
          const k = this.kresli;
          const v = this.pridej(Object.assign({}, k, { x1: a.start.x, y1: a.start.y, x2: u.x, y2: u.y }));
          a.vytvoren = true; this.vybrany = { id: v.id, bod: 2 };
          this.prekresli(); this.zmena({ typ: "kresli", id: v.id });
        }
      });
      const konec = e => {
        const a = this.akce; if (!a) return;
        this.akce = null;
        if (!a.pohyb) {   // klepnutí
          if (a.typ === "bod") {
            const s = this.vybrany;
            this.vybrany = s && s.id === a.v.id && s.bod === a.bod ? null : { id: a.v.id, bod: a.bod };
            this.zmena({ typ: "vyber", id: a.v.id });
          } else if (a.typ === "kresli" && this.vybrany && e.type === "pointerup") {
            const v = this.vektor(this.vybrany.id), u = a.start;
            if (v) {
              const jiny = this.vybrany.bod === 1 ? [v.x2, v.y2] : [v.x1, v.y1];
              if (u.x !== jiny[0] || u.y !== jiny[1]) {
                if (this.vybrany.bod === 1) { v.x1 = u.x; v.y1 = u.y; } else { v.x2 = u.x; v.y2 = u.y; }
                this.zmena({ typ: "bod", id: v.id });
              }
            }
          } else if (a.typ === "posun") {
            this.vybrany = null;
          }
        } else if (a.typ === "kresli" && a.vytvoren) {
          this.vybrany = null; this.zmena({ typ: "nakreslen", id: this.kresli && this.kresli.id });
        }
        this.prekresli();
      };
      cv.addEventListener("pointerup", konec);
      cv.addEventListener("pointercancel", konec);
      // iPad: Pencil nesmí posouvat stránku; prst posouvá (pokud není zapnuté ovládání prstem)
      const block = e => { const t = e.touches[0]; if (t && (t.touchType === "stylus" || prst)) e.preventDefault(); };
      cv.addEventListener("touchstart", block, { passive: false });
      cv.addEventListener("touchmove", block, { passive: false });
    }
  }

  global.Vektory = { Sit, fmt, zav, slozky, velikost, soucet, opacny, uhel, popisSlozek, odmocnina, nastavPrst, MINUS };
})(window);
