#!/usr/bin/env python3
"""Kontrola jedné stránky Rychloučení v Playwrightu (system/Kontrola_rychlouceni_vXX.py).

Použití (z rootu repozitáře, před každým pushem nového nebo změněného Rychloučení):
    python3 system/Kontrola_rychlouceni_v01.py <předmět>/<tema>_rychlouceni_vXX.html [--rychle]

Ověří:
  1. obsah (bez prohlížeče, přes Node): stránka je na šabloně system/Sablona_rychlouceni_vXX.html (kód mimo bloky
     HLAVIČKA, NÁZEV V PANELU a KONFIGURACE shodný), verze v panelu = název souboru = RYCHLO.version, téma = název,
     jednoznačná id faktů, známá kapitola, priorita jadro/doplnek, každý fakt 2+ varianty s různým zadáním,
     každá varianta 5 různých možností s právě jednou správnou (jinak vyjimka5), u každé špatné možnosti vysvětlení,
  2. plánovač (čistá funkce Rychlouceni.planovac přes page.evaluate): 1000 průchodů s chybovostí 0 %, 30 %, 60 %
     a se vzorem „střídavě správně a špatně“ – každý skončí, žádný fakt dvakrát po sobě (kromě posledního),
     v práci nikdy víc než 8, mezi chybou a návratem 2–4 otázky (kdykoli to jde), naučený = 2 správné za sebou
     s jinou otázkou mezi nimi, závěrečné kolo = každý chybný fakt jednou v jiné variantě; vypíše průměr,
     maximum a odhad času (14 s na otázku),
  3. stránka – Chromium a WebKit (je-li nainstalovaný), iPad 820 × 1180 a 1180 × 820, device_scale_factor 2,
     has_touch, is_mobile: načtení bez chyb v konzoli, žádné vodorovné přetečení, malá tlačítka, verze na stránce,
     kostra s „Ukázat možnosti“, možnosti se míchají, dvojklik na možnost nepřeskočí vysvětlení, „Další“ do 400 ms
     nereaguje, uložení a obnovení po reloadu uprostřed, celý průchod až po závěrečné kolo a souhrn, ranní opakování
     (nabídka po 30 otázkách), Začít znovu s potvrzením, události (rychlo_*; žádné start/vyhodnoceni/reseni/
     napoveda/souhrn), 100 % „Nevím“ s podvrženými hodinami – nezamrzne a po 25 min nabídne pauzu.
Adresa záznamu je podvržená (window.ANNSCHOOL_ENDPOINT + ctx.route), nic se neodesílá do skutečné tabulky.
Skončí „Vše v pořádku.“ (kód 0), jinak vypíše CHYBY (kód 1). --rychle = jen Chromium na výšku (při ladění).
"""
import asyncio, json, os, re, subprocess, sys, threading, http.server, socketserver, functools

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
CHYBY, INFO = [], []
chyba, info = CHYBY.append, INFO.append
ENDPOINT = "https://example.invalid/annschool-kontrola/exec"
ZAKAZANE = {"start", "vyhodnoceni", "reseni", "napoveda", "souhrn"}
HZ, HK = "<!-- ===== HLAVIČKA STRÁNKY", "<!-- ===== KONEC HLAVIČKY ===== -->"
NZ, NK = "<!-- ===== NÁZEV V PANELU", "<!-- ===== KONEC NÁZVU ===== -->"
KZ, KK = "/* =====================================================================\n   KONFIGURACE RYCHLOUČENÍ", \
    "/* ===================== KONEC KONFIGURACE ===================== */"


def obal(t):
    """kód mimo bloky HLAVIČKA, NÁZEV V PANELU a KONFIGURACE (pro porovnání se šablonou)"""
    try:
        a, b = t.index(HZ), t.index(HK)
        c, d = t.index(NZ), t.index(NK)
        e, f = t.index(KZ), t.index(KK)
    except ValueError:
        return None
    return t[:a] + t[b:c] + t[d:e] + t[f:]


NODE = r"""
const fs = require("fs"), vm = require("vm");
const t = fs.readFileSync(process.argv[1], "utf8");
const a = t.indexOf("const RYCHLO = {"), b = t.indexOf("/* ===================== KONEC KONFIGURACE");
const ctx = { out: null };
vm.runInNewContext(t.slice(a, b) + "; out = RYCHLO;", ctx);
console.log(JSON.stringify(ctx.out));
"""


def staticka(p):
    t = open(p, encoding="utf-8").read()
    m = re.match(r"^([a-z0-9-]+)/([a-z0-9-]+)_rychlouceni_v(\d\d)\.html$", p)
    if not m:
        chyba(f"{p}: název není <předmět>/<tema>_rychlouceni_vXX.html")
        return None
    ver = "v" + m.group(3)
    o = obal(t)
    sab = sorted(f for f in os.listdir("system") if re.match(r"Sablona_rychlouceni_v\d\d\.html$", f))
    if o is None:
        chyba(f"{p}: chybí bloky HLAVIČKA / NÁZEV V PANELU / KONFIGURACE RYCHLOUČENÍ")
    elif not sab:
        chyba("system/Sablona_rychlouceni_vXX.html nenalezena")
    else:
        shoda = [s for s in sab if obal(open("system/" + s, encoding="utf-8").read()) == o]
        if not shoda:
            chyba(f"{p}: kód mimo bloky se neshoduje s žádnou šablonou Rychloučení – šablona se měnit nesmí")
        elif shoda[-1] != sab[-1]:
            info(f"{p}: na starší šabloně {shoda[-1]} (aktuální {sab[-1]})")
    pt = re.search(r'class="panel-title">(.*?)</div>', t, re.S)
    vv = set(re.findall(r"\bv\d\d\b", pt.group(1))) if pt else set()
    if vv != {ver}:
        chyba(f"{p}: verze v panelu {sorted(vv)} ≠ {ver}")
    try:
        R = json.loads(subprocess.run(["node", "-e", NODE, p], capture_output=True, text=True, check=True).stdout)
    except Exception as e:  # noqa
        chyba(f"{p}: konfiguraci nejde načíst ({e})")
        return None
    if R.get("version") != ver:
        chyba(f"{p}: RYCHLO.version {R.get('version')} ≠ {ver}")
    if R.get("topic") != m.group(2):
        chyba(f"{p}: RYCHLO.topic {R.get('topic')} ≠ {m.group(2)}")
    kap = {k["id"] for k in R["kapitoly"]}
    ids = [f["id"] for f in R["fakta"]]
    for d in sorted({x for x in ids if ids.count(x) > 1}):
        chyba(f"{p}: id faktu „{d}“ víckrát")
    for f in R["fakta"]:
        if f.get("kap") not in kap:
            chyba(f"{p}: {f['id']}: neznámá kapitola {f.get('kap')}")
        if f.get("pri") not in ("jadro", "doplnek"):
            chyba(f"{p}: {f['id']}: priorita musí být jadro / doplnek")
        if not str(f.get("vysv", "")).strip():
            chyba(f"{p}: {f['id']}: chybí vysvětlení správné odpovědi")
        if len(f["var"]) < 2:
            chyba(f"{p}: {f['id']}: méně než 2 varianty")
        if len({v["t"] for v in f["var"]}) != len(f["var"]):
            chyba(f"{p}: {f['id']}: dvě varianty mají stejné zadání")
        for i, v in enumerate(f["var"], 1):
            opts = [v["ok"]] + [s[0] for s in v["s"]]
            low = [str(x).strip().lower() for x in opts]
            if any(not x for x in low):
                chyba(f"{p}: {f['id']} var{i}: prázdná možnost")
            if len(set(low)) != len(low):
                chyba(f"{p}: {f['id']} var{i}: dvě stejné možnosti (nebo správná mezi špatnými)")
            if len(opts) < 5 and not v.get("vyjimka5"):
                chyba(f"{p}: {f['id']} var{i}: méně než 5 možností (bez vyjimka5)")
            for s in v["s"]:
                if len(s) < 2 or not str(s[1]).strip():
                    chyba(f"{p}: {f['id']} var{i}: špatná možnost „{s[0]}“ nemá vysvětlení")
    info(f"obsah: {len(R['fakta'])} faktů, {sum(len(f['var']) for f in R['fakta'])} variant, {len(R['pojmy'])} pojmů, "
         f"kostra {sum(1 for f in R['fakta'] if any(k['id'] == f['kap'] and k.get('kostra') for k in R['kapitoly']))}")
    return R


SIM_JS = r"""
({ runs, vzor, err }) => {
  const P = Rychlouceni.planovac, F = Rychlouceni.poradiFaktu(), N = Rychlouceni.nastaveni;
  const out = { runs, otazek: [], chyby: [], gap: { celkem: 0, v24: 0, pod2: 0, nad4: 0 }, maxPrace: 0, zaver: [] };
  let rng = 12345 + runs * 7 + Math.round(err * 1000);
  const rnd = () => { rng = (rng * 1103515245 + 12345) & 0x7fffffff; return rng / 0x7fffffff; };
  for (let r = 0; r < runs; r++) {
    let stav = P.novy(F, r * 2654435761 + 1), d = P.dalsi(stav, F), q = 0, prev = null, alt = r % 2 === 0;
    const spatneKdy = {}, posledniSpravne = {}, varMinule = {};
    stav = d.stav; let ot = d.otazka; const vZaveru = [];
    while (ot && q < 20000) {
      const fr = stav.fronta;
      if (stav.rezim === "uceni") {
        const prace = Object.keys(fr.prace).length;
        out.maxPrace = Math.max(out.maxPrace, prace);
        if (prace > N.maxPrace) out.chyby.push(`běh ${r}: v práci ${prace} faktů`);
        const zbyva = F.filter(f => !stav.fakta[f.id].naucen).length;
        if (prev === ot.id && zbyva > 1) out.chyby.push(`běh ${r}: fakt ${ot.id} dvakrát po sobě (zbývá ${zbyva})`);
        if (spatneKdy[ot.id] !== undefined) {
          const g = q - spatneKdy[ot.id] - 1; out.gap.celkem++;
          if (g >= 2 && g <= 4) out.gap.v24++; else if (g < 2) { if (zbyva > 2) out.gap.pod2++; } else out.gap.nad4++;
          delete spatneKdy[ot.id];
        }
      } else if (stav.rezim === "zaver") {
        vZaveru.push(ot.id);
        if (varMinule[ot.id] === ot.v && F.find(f => f.id === ot.id).nVar > 1) out.chyby.push(`běh ${r}: závěrečné kolo ${ot.id} ve stejné variantě`);
      }
      if (varMinule[ot.id] === ot.v && F.find(f => f.id === ot.id).nVar > 1 && stav.rezim === "uceni") out.chyby.push(`běh ${r}: ${ot.id} stejná varianta jako minule`);
      let ok = vzor === "stridave" ? (alt = !alt) : rnd() >= err;
      const pred = stav;
      const o = P.odpoved(stav, F, ot, ok);
      if (stav.rezim === "uceni") {
        if (!ok) spatneKdy[ot.id] = q;
        if (o.naucen) {
          const ps = posledniSpravne[ot.id];
          const jediny = F.filter(f => !pred.fakta[f.id].naucen).length === 1;
          if (ps === undefined || (q - ps < 2 && !jediny)) out.chyby.push(`běh ${r}: ${ot.id} naučen bez 2 správných s otázkou mezi`);
        }
        if (ok) posledniSpravne[ot.id] = q; else delete posledniSpravne[ot.id];
      }
      varMinule[ot.id] = ot.v; prev = ot.id;
      const d2 = P.dalsi(o.stav, F); stav = d2.stav; ot = d2.otazka; q++;
    }
    if (ot) out.chyby.push(`běh ${r}: neskončil do 20000 otázek`);
    const chybne = F.filter(f => stav.fakta[f.id].spatne > 0).map(f => f.id).sort();
    const vz = vZaveru.slice().sort();
    if (JSON.stringify(chybne) !== JSON.stringify(vz)) out.chyby.push(`běh ${r}: závěrečné kolo neobsahuje každý chybný fakt právě jednou`);
    if (F.some(f => !stav.fakta[f.id].naucen)) out.chyby.push(`běh ${r}: na konci nejsou všechna fakta naučená`);
    out.otazek.push(q);
    if (out.chyby.length > 20) break;
  }
  const s = out.otazek;
  return { prumer: s.reduce((a, b) => a + b, 0) / s.length, max: Math.max(...s), min: Math.min(...s), maxPrace: out.maxPrace,
    gap: out.gap, chyby: out.chyby.slice(0, 20) };
}
"""


class Tichy(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def server():
    h = functools.partial(Tichy, directory=ROOT)
    s = socketserver.ThreadingTCPServer(("127.0.0.1", 0), h)
    s.daemon_threads = True
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, s.server_address[1]


async def kontext(pw, browser, w, h, udalosti):
    ctx = await browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=2, has_touch=True, is_mobile=True)
    await ctx.add_init_script(f"window.ANNSCHOOL_ENDPOINT = {json.dumps(ENDPOINT)};")

    async def on_route(route):
        try:
            b = json.loads(route.request.post_data or "{}")
            udalosti.extend(b.get("udalosti", []))
        except Exception:  # noqa
            pass
        await route.fulfill(status=200, content_type="application/json", body='{"ok":true}')
    await ctx.route(ENDPOINT + "*", on_route)
    return ctx


async def pretece(page):
    return await page.evaluate("document.documentElement.scrollWidth > innerWidth + 1")


async def odpovez(page, spravne=True, nevim=False):
    """odpoví na aktuální otázku klepnutím; vrátí otázku"""
    ot = await page.evaluate("Rychlouceni.otazka()")
    if ot is None:
        return None
    if nevim:
        await page.tap("#btnNevim")
    else:
        if not ot["odkryto"]:
            await page.tap("#btnUkazat")
        i = ot["spravna"] if spravne else (ot["spravna"] + 1) % len(ot["moznosti"])
        await page.locator("#moznosti .moznost").nth(i).tap()
    return ot


async def dalsi(page):
    await page.wait_for_timeout(420)
    await page.tap("#btnDalsi")


async def stranka(pw, nazev, browser, w, h, url, plne, R):
    tag = f"{nazev} {w}×{h}"
    udal = []
    ctx = await kontext(pw, browser, w, h, udal)
    page = await ctx.new_page()
    konzole = []
    page.on("console", lambda m: konzole.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: konzole.append(str(e)))
    await page.goto(url)
    await page.wait_for_load_state("networkidle")
    if await pretece(page):
        chyba(f"{tag}: úvod přetéká vodorovně")
    ver = re.search(r"_(v\d\d)\.html", url).group(1)
    pt = await page.inner_text(".panel-title")
    if ver not in pt:
        chyba(f"{tag}: v panelu není verze {ver} ({pt})")
    velke = await page.evaluate("""() => [...document.querySelectorAll('.btn')].filter(b => b.offsetParent).map(b => {
        const s = getComputedStyle(b); return [b.textContent.trim(), parseFloat(s.fontSize), parseFloat(s.paddingTop)]; })
        .filter(([, f, p]) => f > 15 || p > 6)""")
    if velke:
        chyba(f"{tag}: velká tlačítka (Pouceni bod 18): {velke}")
    sel = await page.evaluate("getComputedStyle(document.body).userSelect || getComputedStyle(document.body).webkitUserSelect")
    if sel != "none":
        chyba(f"{tag}: stránka nemá user-select: none ({sel})")
    if await page.is_visible("#btnPokracovat") or not await page.is_visible("#btnZacit"):
        chyba(f"{tag}: bez uloženého stavu má být vidět Začít, ne Pokračovat")
    await page.tap("#btnZacit")
    ot = await page.evaluate("Rychlouceni.otazka()")
    if not ot:
        chyba(f"{tag}: po Začít se neukázala otázka")
        await ctx.close()
        return
    # kostra: možnosti až po „Ukázat možnosti“
    if ot["kostra"]:
        if await page.is_visible("#moznosti .moznost") or not await page.is_visible("#btnUkazat"):
            chyba(f"{tag}: u kostry mají být možnosti skryté za „Ukázat možnosti“")
        await page.tap("#btnUkazat")
        if not await page.is_visible("#moznosti .moznost"):
            chyba(f"{tag}: „Ukázat možnosti“ neukázalo možnosti")
    else:
        chyba(f"{tag}: první otázka není z kostry")
    if await page.locator("#moznosti .moznost").count() != len(ot["moznosti"]) or len(set(ot["moznosti"])) != 5:
        chyba(f"{tag}: otázka nemá 5 různých možností")
    # dvojklik na možnost: vyhodnocení zůstane, „Další“ do 400 ms nereaguje
    i = (ot["spravna"] + 1) % 5
    await page.locator("#moznosti .moznost").nth(i).dblclick()
    await page.wait_for_timeout(100)
    po = await page.evaluate("Rychlouceni.otazka()")
    if not await page.is_visible("#vyhodnoceni") or po["id"] != ot["id"]:
        chyba(f"{tag}: dvojklik na možnost přeskočil vyhodnocení")
    if await pretece(page):
        chyba(f"{tag}: vyhodnocení přetéká vodorovně")
    box_d = await page.locator("#btnDalsi").bounding_box()
    box_m = await page.locator("#moznosti .moznost").nth(i).bounding_box()
    if box_d and box_m and not (box_d["y"] >= box_m["y"] + box_m["height"] or box_d["y"] + box_d["height"] <= box_m["y"]):
        chyba(f"{tag}: „Další“ je na místě klepnuté možnosti")
    if not await page.evaluate("!!document.querySelector('#vVolba') && !document.querySelector('#vVolba').hidden"):
        chyba(f"{tag}: u špatné možnosti chybí, co znamená")
    await page.evaluate("document.getElementById('btnDalsi').click()")   # hned – má se ignorovat
    if (await page.evaluate("Rychlouceni.otazka()"))["id"] != ot["id"] or not await page.is_visible("#vyhodnoceni"):
        chyba(f"{tag}: „Další“ do 400 ms po vyhodnocení zareagovalo")
    await dalsi(page)
    poradi = {}
    if not plne:
        for k in range(6):
            o = await odpovez(page, spravne=k % 3 != 0)
            poradi.setdefault((o["id"], o["varianta"]), set()).add(tuple(o["moznosti"]))
            await dalsi(page)
        if await pretece(page):
            chyba(f"{tag}: otázka přetéká vodorovně")
    else:
        # reload uprostřed: stav a aktuální otázka se obnoví
        for k in range(9):
            await odpovez(page, spravne=k % 4 != 1)
            await dalsi(page)
        pred = await page.evaluate("[Rychlouceni.stav().planovac.n, Rychlouceni.otazka().id, Rychlouceni.otazka().moznosti]")
        await page.reload()
        await page.wait_for_load_state("networkidle")
        if not await page.is_visible("#btnPokracovat"):
            chyba(f"{tag}: po reloadu chybí „Pokračovat“")
        await page.tap("#btnPokracovat")
        po = await page.evaluate("[Rychlouceni.stav().planovac.n, Rychlouceni.otazka().id, Rychlouceni.otazka().moznosti]")
        if po != pred:
            chyba(f"{tag}: po reloadu se neobnovil stav ({pred[:2]} → {po[:2]})")
        # celý průchod: 25 % chyb, pak závěrečné kolo a souhrn
        k, zaver, mezi = 0, [], False
        while k < 1500:
            if await page.is_visible("#btnZaver"):
                mezi = True
                await page.tap("#btnZaver")
            if await page.is_visible("#dialog"):
                await page.locator("#dTlacitka button").last.tap()
            if not await page.is_visible("#scOtazka"):
                break
            o = await odpovez(page, spravne=(k % 4 != 2))
            if o is None:
                break
            poradi.setdefault((o["id"], o["varianta"]), set()).add(tuple(o["moznosti"]))
            if o["rezim"] == "zaver":
                zaver.append(o["id"])
            k += 1
            await dalsi(page)
        st = await page.evaluate("Rychlouceni.stav().planovac")
        if st["rezim"] != "hotovo":
            chyba(f"{tag}: průchod neskončil (režim {st['rezim']} po {k} odpovědích)")
        if not mezi:
            chyba(f"{tag}: před závěrečným kolem chyběla mezistránka")
        chybne = sorted(f for f, x in st["fakta"].items() if x["spatne"] > 0)
        if sorted(zaver) != chybne:
            chyba(f"{tag}: závěrečné kolo nemá každý chybný fakt právě jednou ({len(zaver)} vs {len(chybne)})")
        if "Hotovo" not in await page.inner_text("#mNadpis"):
            chyba(f"{tag}: na konci není souhrn „Hotovo“")
        if await pretece(page):
            chyba(f"{tag}: souhrn přetéká vodorovně")
        info(f"{tag}: celý průchod s 25 % chyb: {k} odpovědí, závěrečné kolo {len(zaver)}")
        # ranní opakování: po 30 otázkách nabídne pokračovat
        await page.tap("#btnUvod")
        await page.tap("#btnRano")
        if (await page.evaluate("Rychlouceni.stav().planovac.rezim")) != "rano":
            chyba(f"{tag}: Ranní opakování nezapnulo režim rano")
        prvni = await page.evaluate("Rychlouceni.otazka().id")
        nejhorsi = max(st["fakta"].items(), key=lambda x: (x[1]["spatne"], -x[1]["spravne"]))[0]
        if st["fakta"][prvni]["spatne"] != st["fakta"][nejhorsi]["spatne"]:
            chyba(f"{tag}: ranní opakování nezačíná nejslabším faktem")
        nabidka = False
        for j in range(31):
            await odpovez(page, spravne=(j % 5 != 0))
            await dalsi(page)
            if await page.is_visible("#dialog"):
                nabidka = j + 1
                break
        if nabidka != 30:
            chyba(f"{tag}: ranní opakování nenabídlo pokračování po 30 otázkách ({nabidka})")
        else:
            await page.locator("#dTlacitka button").first.tap()   # Konec
        # Začít znovu s potvrzením
        await page.tap("#btnZnovu")
        if not await page.is_visible("#dialog"):
            chyba(f"{tag}: Začít znovu se neptá")
        await page.locator("#dTlacitka button").last.tap()
        st2 = await page.evaluate("Rychlouceni.stav().planovac")
        if st2["n"] != 0 or any(x["spatne"] or x["spravne"] for x in st2["fakta"].values()):
            chyba(f"{tag}: Začít znovu stav nesmazalo")
        if not await page.is_visible("#btnZacit"):
            chyba(f"{tag}: po Začít znovu chybí „Začít“")
    if not any(len(v) > 1 for v in poradi.values()) and plne:
        chyba(f"{tag}: možnosti se nemíchají (stejná otázka vždy ve stejném pořadí)")
    await page.evaluate("Sledovani.souhrn && Sledovani.souhrn()")
    await page.wait_for_timeout(2500)
    jmena = {u.get("udalost") for u in udal}
    if jmena & ZAKAZANE:
        chyba(f"{tag}: zakázané události {sorted(jmena & ZAKAZANE)}")
    potreba = {"otevreni", "rychlo_start", "rychlo_odpoved"} | ({"rychlo_naucen", "rychlo_souhrn", "rychlo_reset", "rychlo_rano"} if plne else set())
    if potreba - jmena:
        chyba(f"{tag}: chybí události {sorted(potreba - jmena)}")
    odp = [u for u in udal if u.get("udalost") == "rychlo_odpoved"]
    if odp:
        d = json.loads(odp[0].get("detail") or "{}")
        for k in ("id", "varianta", "kapitola", "vybrala", "spravne", "nevim", "doba_s", "poradi"):
            if k not in d:
                chyba(f"{tag}: rychlo_odpoved bez {k}")
        if any(u.get("typ") != "rychlouceni" for u in odp):
            chyba(f"{tag}: rychlo_odpoved nemá typ rychlouceni")
    if konzole:
        chyba(f"{tag}: chyby v konzoli: {konzole[:3]}")
    await ctx.close()


async def nevim_hodiny(pw, browser, url):
    """100 % Nevím: nespadne, nezamrzne a po 25 min nabídne pauzu (podvržené hodiny)"""
    udal = []
    ctx = await kontext(pw, browser, 820, 1180, udal)
    page = await ctx.new_page()
    err = []
    page.on("pageerror", lambda e: err.append(str(e)))
    await page.clock.install()
    await page.goto(url)
    await page.wait_for_load_state("domcontentloaded")
    await page.tap("#btnZacit")
    pauza = None
    for k in range(40):
        await page.tap("#btnNevim")
        await page.clock.run_for(60000)
        await page.tap("#btnDalsi")
        if await page.is_visible("#dialog"):
            pauza = k + 1
            break
    if pauza is None or not (24 <= pauza <= 27):
        chyba(f"100 % Nevím: pauza se nenabídla po 25 min (po {pauza} min)")
    else:
        info(f"100 % Nevím: pauza nabídnuta po {pauza} min, v práci {await page.evaluate('Object.keys(Rychlouceni.stav().planovac.fronta.prace).length')} faktů")
        await page.locator("#dTlacitka button").last.tap()
        if not await page.evaluate("!!Rychlouceni.otazka()"):
            chyba("100 % Nevím: po pauze nepokračuje otázka")
    if err:
        chyba(f"100 % Nevím: chyby {err[:3]}")
    await ctx.close()


async def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    rychle = "--rychle" in sys.argv
    if len(args) != 1:
        print(__doc__)
        sys.exit(2)
    p = args[0]
    R = staticka(p)
    from playwright.async_api import async_playwright
    srv, port = server()
    url = f"http://127.0.0.1:{port}/{p}"
    async with async_playwright() as pw:
        prohlizece = []
        for nazev in (["chromium"] if rychle else ["chromium", "webkit"]):
            try:
                prohlizece.append((nazev, await getattr(pw, nazev).launch()))
            except Exception as e:  # noqa
                info(f"{nazev}: nejde spustit ({str(e).splitlines()[0][:90]}) – NEOVĚŘENO")
        if not prohlizece:
            chyba("žádný prohlížeč")
        else:
            b0 = prohlizece[0][1]
            ctx = await kontext(pw, b0, 820, 1180, [])
            page = await ctx.new_page()
            await page.goto(url)
            await page.wait_for_load_state("domcontentloaded")
            for nazev, vzor, e in (("0 % chyb", "", 0), ("30 % chyb", "", .3), ("60 % chyb", "", .6), ("střídavě", "stridave", 0)):
                r = await page.evaluate(SIM_JS, {"runs": 1000, "vzor": vzor, "err": e})
                for c in r["chyby"]:
                    chyba(f"plánovač {nazev}: {c}")
                g = r["gap"]
                pct = 100 * g["v24"] / g["celkem"] if g["celkem"] else 100
                info(f"plánovač {nazev}: průměr {r['prumer']:.0f} otázek (min {r['min']}, max {r['max']}), odhad "
                     f"{r['prumer'] * 14 / 60:.0f} min (max {r['max'] * 14 / 60:.0f}); v práci max {r['maxPrace']}; "
                     f"návrat po chybě 2–4 otázky: {pct:.0f} % ({g['pod2']}× dřív, kdy šlo jinak; {g['nad4']}× později)")
                if g["pod2"]:
                    chyba(f"plánovač {nazev}: návrat po chybě dřív než za 2 otázky {g['pod2']}×, i když byla jiná fakta")
                if pct < 80:
                    chyba(f"plánovač {nazev}: návrat po chybě za 2–4 otázky jen v {pct:.0f} %")
            await ctx.close()
            for nazev, b in prohlizece:
                for i, (w, h) in enumerate([(820, 1180)] if rychle else [(820, 1180), (1180, 820)]):
                    await stranka(pw, nazev, b, w, h, url, plne=(i == 0), R=R)
            await nevim_hodiny(pw, b0, url)
            for _, b in prohlizece:
                await b.close()
    srv.shutdown()
    for i in INFO:
        print("  ·", i)
    if CHYBY:
        print("\nCHYBY:")
        for c in CHYBY:
            print("  -", c)
        sys.exit(1)
    print("\nVše v pořádku.")


asyncio.run(main())
