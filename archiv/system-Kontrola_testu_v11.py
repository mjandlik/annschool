#!/usr/bin/env python3
"""Kontrola HTML testu Ann School (system/Kontrola_testu_vXX.py) – pro šablonu v17 až v21.

Použití (z rootu repozitáře):
    python3 system/Kontrola_testu_v11.py <předmět>/<tema>_<typ>_vXX.html

Co ověří (iPad na výšku 820 × 1180 i na šířku 1180 × 820, device_scale_factor 2):
  1. stránka se načte bez chyb v konzoli, nic se neposouvá vodorovně, papír je aspoň 260 px vysoký,
     časová osa má kolečko pro každý příklad + „Souhrn“,
  2. prázdná odpověď se nepočítá jako pokus,
  3. správné odpovědi všech příkladů → zelená (čísla s desetinnou čárkou a mezerami, výběr klepnutím,
     rýsování a řetěz kreslením myší přes síť), důkaz → „Vyhodnotit“ ukáže vzorové řešení → modrá,
  4. u prvního příkladu každého typu: špatně → šedá, správné řešení se neukáže, síť zůstane odemčená,
     pak správně → oranžová,
  5. když má typ víc příkladů: 3× špatně → červená, příklad zamčený, správné řešení vidět (u sítě čárkovaně),
  6. papír: tah se uloží k příkladu, po přechodu jinam a zpět zůstane, po otočení iPadu taky,
  7. záznam: události start, vyhodnoceni (počet = počet pokusů, s obrázkem papíru), napoveda, odchod, souhrn
     se odešlou na adresu webové aplikace (v kontrole podvržená),
  8. skóre v souhrnu odpovídá barvám (zelená 1, oranžová ½, červená 0),
  9. tlačítko PDF vytvoří PDF s pořadovým číslem v názvu,
 10. verze v názvu souboru odpovídá TEST.version a téma odpovídá TEST.topic,
 11. (v06) po zavření a znovuotevření se test obnoví (stavy příkladů, papír, událost „pokracovani“, žádný nový „start“),
 12. (v07) obsah výběrů: žádná prázdná ani dvakrát stejná možnost, index správné možnosti v rozsahu;
     u šablony v18+ CHYBA, když má výběr méně než 5 možností a není to povolená dvojice/trojice
     (ano/ne, skalár/vektor, doprava/doleva, nahoru/dolů, <, =, >, …) ani nemá v příkladu
     klíč  vyjimka5: "důvod"  (u starších testů jen VAROVÁNÍ),
 13. (v07) šablona v18+: název PDF obsahuje téma i typ testu ze jména souboru,
 14. (v08) šablona v18+: CHYBA, když číselné pole čeká necelé číslo (bez tol), zadání neobsahuje desetinné číslo
     a obsahuje zlomek, záporný exponent, racionální exponent nebo odmocninu (/, ⁻, ^(, √, ∛) – takový výsledek
     se ve škole píše jako zlomek, má být výběr z 5 možností (Navod_test kap. 3, Pouceni bod 14);
     výjimka jen s klíčem  desetinne: "důvod"  v příkladu.
 15. (v09) šablona v19+: tlačítka papíru (Zpět, Smazat, ↖ Na začátek) jsou vlevo nahoře na papíře
     (na výšku i na šířku) – vpravo překážejí pravákovi (Pouceni bod 15);
     (v10) šablona v20+: lišta papíru má jen Zpět a Smazat (bez „↖ Na začátek“).
 16. (v11) šablona v21+: start posílá sablona a priklady (zadání u každého příkladu, správná odpověď u každého
     kromě důkazu), Zpět na papíře zvýší verzi papíru (Pouceni bod 16) a náhled papíru se pošle jako událost
     „nahled“ s obrázkem (posliNahled), dokud je fronta prázdná.
  Verze šablony se pozná z historie v hlavičce testu (nejvyšší řádek „vNN:“).
Ručně (skript to neumí): že žádná špatná možnost není ve skutečnosti také správná – viz Navod_test, kap. 4.
Potřebuje: pip install playwright && python3 -m playwright install chromium
"""
import asyncio, http.server, json, os, re, socketserver, sys, threading
from playwright.async_api import async_playwright

ENDPOINT = "https://zaznam.test/exec"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve(root):
    handler = lambda *a, **k: QuietHandler(*a, directory=root, **k)
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def cz(n):
    """Číslo jako by ho psala Ann: desetinná čárka, mezery po tisících."""
    s = f"{n:.10f}".rstrip("0").rstrip(".")
    ip, _, dp = s.partition(".")
    neg = ip.startswith("-")
    ip = ip.lstrip("-")
    ip = " ".join([ip[max(0, i - 3):i] for i in range(len(ip), 0, -3)][::-1])
    return ("-" if neg else "") + ip + ("," + dp if dp else "")


INFO_JS = """QS.map(q => ({
  typ: q._typ,
  fields: q._fields.map(f => ({ answer: f.answer, opt: !!f.options, n: f.options ? f.options.length : 0 })),
  answer: q.answer || null, retez: q.retez || null,
  sit: q._sit ? { xmin: q._sit.o.xmin, xmax: q._sit.o.xmax, ymin: q._sit.o.ymin, ymax: q._sit.o.ymax } : null }))"""


def fit_start(sit, pts, x=0, y=0):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x = min(sit["xmax"] - max(xs), max(sit["xmin"] - min(xs), x))
    y = min(sit["ymax"] - max(ys), max(sit["ymin"] - min(ys), y))
    return x, y


async def draw(page, qi, x1, y1, x2, y2):
    """Nakreslí vektor myší z uzlu [x1; y1] do uzlu [x2; y2] v síti příkladu."""
    await page.evaluate(f"QS[{qi}]._sit.cv.scrollIntoView({{block: 'center'}})")
    await page.wait_for_timeout(50)
    X1, Y1, X2, Y2 = await page.evaluate(f"""(() => {{ const s = QS[{qi}]._sit, r = s.cv.getBoundingClientRect();
        return [r.left + s.px({x1}), r.top + s.py({y1}), r.left + s.px({x2}), r.top + s.py({y2})]; }})()""")
    await page.mouse.move(X1, Y1)
    await page.mouse.down()
    await page.mouse.move(X2, Y2, steps=10)
    await page.mouse.up()
    await page.wait_for_timeout(30)


def qpage(page, qi):
    return page.locator(".qpage:not(.sum)").nth(qi)


async def fill_fields(page, qi, fields, wrong=False):
    loc = qpage(page, qi)
    ni = oi = 0
    for k, f in enumerate(fields):
        bad = wrong and k == 0
        if f["opt"]:
            idx = (f["answer"] + 1) % f["n"] if bad else f["answer"]
            await loc.locator(".opts").nth(oi).locator("button").nth(idx).click()
            oi += 1
        else:
            val = f["answer"] * 7 + 13 if bad else f["answer"]
            await loc.locator("input.ans").nth(ni).fill(cz(val))
            ni += 1


async def clear_drawing(page, qi):
    await page.evaluate(f"(() => {{ const q = QS[{qi}]; annIds(q).forEach(id => {{ if (q._sit.vektor(id)) q._sit.odeber(id); }}); setActive(q, 0); }})()")


async def do_drawing(page, qi, q, wrong=False):
    sit = q["sit"]
    await clear_drawing(page, qi)
    if q["typ"] == "rysuj":
        dx, dy = q["answer"]["dx"], q["answer"]["dy"]
        if wrong:
            dx = dx + 1 if dx != -1 or dy else dx - 1
        x, y = fit_start(sit, [(0, 0), (dx, dy)], 0, 0)
        await draw(page, qi, x, y, x + dx, y + dy)
        return
    chain = q["retez"]
    pts = [(0, 0)]
    for r in chain:
        pts.append((pts[-1][0] + r["dx"], pts[-1][1] + r["dy"]))
    x, y = fit_start(sit, pts, 0, 0)
    btn = lambda i: qpage(page, qi).locator(".grid-tools button[data-i]").nth(i)
    for i in range(len(chain)):
        await btn(i).click()
        await draw(page, qi, x + pts[i][0], y + pts[i][1], x + pts[i + 1][0], y + pts[i + 1][1])
    if wrong:
        return
    await btn(len(chain)).click()
    await draw(page, qi, x, y, x + pts[-1][0], y + pts[-1][1])


async def answer(page, qi, q, wrong=False):
    if q["fields"]:
        await fill_fields(page, qi, q["fields"], wrong=wrong and q["typ"] not in ("rysuj", "retez"))
    if q["typ"] in ("rysuj", "retez"):
        await do_drawing(page, qi, q, wrong=wrong)


async def evaluate(page, qi):
    await qpage(page, qi).locator('[data-a="eval"]').click()
    await page.wait_for_timeout(40)
    return await page.evaluate(f"stav(QS[{qi}])")


SAB = [0]  # verze šablony testu (z hlavičky)


async def layout_ok(page, label, problems):
    await page.wait_for_timeout(250)
    # 15) tlačítka papíru vlevo nahoře (šablona v19+)
    if SAB[0] >= 19 and await page.evaluate("cur < QS.length"):
        tl = await page.evaluate("""(() => { const box = $("paperBox").getBoundingClientRect();
            return { w: box.width, l: box.left, t: box.top, home: !!$("pHome"), b: [...document.querySelectorAll("#paperBox .paper-bar button")].map(el => { const r = el.getBoundingClientRect();
              return { id: el.id, l: r.left - box.left, r: r.right - box.left, t: r.top - box.top }; }) }; })()""")
        spatne = [x["id"] for x in tl["b"] if x["r"] > tl["w"] * 0.4 or x["t"] > 40]
        if SAB[0] >= 20 and (tl["home"] or [x["id"] for x in tl["b"]] != ["pUndo", "pClear"]):
            problems.append(f"{label}: lišta papíru má mít jen Zpět a Smazat (šablona v20+), má {[x['id'] for x in tl['b']]}")
        if spatne or tl["b"][0]["l"] > 20:
            problems.append(f"{label}: tlačítka papíru nejsou vlevo nahoře ({', '.join(spatne) or 'Zpět není u levého okraje'})")
        else:
            print(f"  OK  tlačítka papíru vlevo nahoře ({label})")
    st = await page.evaluate("""(() => ({ hs: document.documentElement.scrollWidth > innerWidth + 1,
        stage: $("stage").scrollWidth > $("stage").clientWidth + 1,
        paper: $("paperView").offsetHeight, tl: $("timeline").getBoundingClientRect().bottom <= innerHeight + 1 }))()""")
    if st["hs"] or st["stage"]:
        problems.append(f"{label}: stránka se posouvá vodorovně")
    if cur := await page.evaluate("cur < QS.length"):
        if st["paper"] < 260:
            problems.append(f"{label}: papír je nízký ({st['paper']} px)")
    if not st["tl"]:
        problems.append(f"{label}: časová osa není celá vidět")
    print(f"  {'OK ' if not (st['hs'] or st['stage']) else 'CHYBA'} rozložení {label}: papír {st['paper']} px")


async def main(path):
    full = os.path.abspath(path)
    name = os.path.basename(full)
    root = os.path.dirname(full)
    while not os.path.isdir(os.path.join(root, "system")) and os.path.dirname(root) != root:
        root = os.path.dirname(root)
    httpd = serve(root)
    rel = os.path.relpath(full, root).replace(os.sep, "/")
    url = f"http://127.0.0.1:{httpd.server_address[1]}/{rel}"
    problems, events = [], []

    async def on_route(route):
        try:
            body = json.loads(route.request.post_data or "{}")
            events.extend(body.get("udalosti", []))
        except Exception as e:  # noqa
            problems.append(f"záznam: neplatná data ({e})")
        await route.fulfill(status=200, content_type="application/json", body='{"ok":true}',
                            headers={"Access-Control-Allow-Origin": "*"})

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 820, "height": 1180}, device_scale_factor=2,
                                        accept_downloads=True)
        await ctx.add_init_script(f"window.ANNSCHOOL_ENDPOINT = {json.dumps(ENDPOINT)};")
        await ctx.route(ENDPOINT + "*", on_route)
        page = await ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: m.type == "error" and errors.append(m.text))
        page.on("dialog", lambda d: asyncio.ensure_future(d.accept()))
        await page.goto(url)
        await page.wait_for_timeout(400)

        version = await page.evaluate("TEST.version")
        m = re.search(r"_(v\d\d)\.html$", name)
        if m and m.group(1) != version:
            problems.append(f"verze v názvu souboru ({m.group(1)}) ≠ TEST.version ({version})")
        topic = await page.evaluate("TEST.topic")
        mt = re.match(r"(.+)_test(-[a-z0-9-]+)?_v\d\d\.html$", name)
        if mt and not name.startswith("Sablona_") and mt.group(1) != topic:
            problems.append(f"téma v názvu souboru ({mt.group(1)}) ≠ TEST.topic ({topic})")

        info = await page.evaluate(INFO_JS)
        hlava = (await page.content()).split("const TEST = {")[0]
        SAB[0] = max([int(x) for x in re.findall(r"^\s*v(\d\d):", hlava, re.M)] or [0])
        sab18 = SAB[0] >= 18
        # 12) obsah výběrů
        cfg = await page.evaluate("""QS.map(q => ({ text: q.text || q.before || '', vyj: q.vyjimka5 || '', des: q.desetinne || '',
            num: q._fields.filter(f => !f.options).map(f => ({ a: f.answer, tol: f.tol || 0, t: (q.text || '') + ' ' + (f.before || '') + ' ' + (f.after || '') })),
            opts: q._fields.filter(f => f.options).map(f => ({ o: f.options.map(String), a: f.answer })) }))""")
        POVOLENE = [{"ano", "ne"}, {"skalár", "vektor"}, {"doprava", "doleva"}, {"nahoru", "dolů"}, {"<", "=", ">"},
                    {"na východ", "na západ"}, {"na sever", "na jih"}, {"pravda", "nepravda"},
                    {"komutativní", "asociativní", "distributivní"}, {"prvočíslo", "složené číslo", "ani prvočíslo, ani složené"}]
        malo = []
        for i, q in enumerate(cfg):
            for f in q["opts"]:
                o = [x.strip() for x in f["o"]]
                if any(not x for x in o):
                    problems.append(f"příklad {i + 1}: prázdná možnost ve výběru")
                low = [x.lower() for x in o]
                if len(set(low)) != len(low):
                    problems.append(f"příklad {i + 1}: dvě stejné možnosti ve výběru {o}")
                if not (isinstance(f["a"], int) and 0 <= f["a"] < len(o)):
                    problems.append(f"příklad {i + 1}: index správné možnosti {f['a']} mimo rozsah")
                if len(o) < 5 and set(low) not in POVOLENE and not q["vyj"]:
                    malo.append(f"příklad {i + 1} ({len(o)} možnosti: {' | '.join(o)})")
        for m_ in malo:
            if sab18:
                problems.append(f"méně než 5 možností: {m_} – doplň možnosti podle typických chyb, nebo vyjimka5: \"důvod\"")
            else:
                print(f"  VAROVÁNÍ méně než 5 možností (starší test): {m_}")
        if not malo:
            print("  OK  výběry mají aspoň 5 možností (nebo povolenou dvojici/trojici)")
        # 14) zlomkový výsledek jako desetinné číslo v poli (v08)
        if sab18:
            zlom = []
            for i, q in enumerate(cfg):
                for f in q["num"]:
                    a, t = f["a"], f["t"].replace("(desetinné číslo)", "")
                    if (isinstance(a, (int, float)) and a != int(a) and not f["tol"] and not q["des"]
                            and not re.search(r"\d,\d", t) and re.search(r"/|⁻|\^\(|√|∛", t)):
                        zlom.append(f"příklad {i + 1} ({t.strip()[:40]} → {cz(a)})")
            for z in zlom:
                problems.append(f"necelý výsledek ze zlomků/mocnin jako desetinné číslo: {z} – dej výběr z 5 možností ve tvaru ze školy (zlomek), nebo desetinne: \"důvod\"")
            if not zlom:
                print("  OK  necelé výsledky ze zlomků a mocnin nejsou v číselném poli")
        n_q = len(info)
        typy = sorted({q["typ"] for q in info})
        print(f"Test: {await page.evaluate('TEST.title')} ({version}) – {await page.evaluate('SECTIONS.length')} sekcí, "
              f"{n_q} příkladů, typy: {', '.join(typy)}")
        n_tl = await page.locator("#timeline .tl-b").count()
        if n_tl != n_q + 1:
            problems.append(f"časová osa má {n_tl} tlačítek, čekám {n_q + 1}")
        await layout_ok(page, "na výšku", problems)

        # vyhrazené příklady: první každého typu = špatně→správně (oranžová), druhý téhož typu = 3× špatně (červená)
        first, red, seen = {}, {}, {}
        for i, q in enumerate(info):
            t = q["typ"]
            if t == "dukaz":
                continue
            seen[t] = seen.get(t, 0) + 1
            if seen[t] == 1:
                first[t] = i
            elif seen[t] == 2:
                red[t] = i
        expected = {}

        # 2) prázdná odpověď se nepočítá
        q0 = next((i for i, q in enumerate(info) if q["typ"] != "dukaz"), None)
        if q0 is not None:
            await page.locator("#timeline .tl-b").nth(q0).click()
            await qpage(page, q0).locator('[data-a="eval"]').click()
            pk = await page.evaluate(f"QS[{q0}]._st.pokusy")
            print(f"  {'OK ' if pk == 0 else 'CHYBA'} prázdná odpověď se nepočítá jako pokus")
            if pk:
                problems.append("prázdná odpověď se započítala jako pokus")
            # 6) papír: tah na papír příkladu q0
            box = await page.evaluate("(() => { const r = $('paper').getBoundingClientRect(); return [r.left, r.top]; })()")
            await page.mouse.move(box[0] + 60, box[1] + 40)
            await page.mouse.down()
            await page.mouse.move(box[0] + 220, box[1] + 90, steps=12)
            await page.mouse.up()
            # nápověda (pokud je)
            hb = qpage(page, q0).locator('[data-a="hint"]')
            if await hb.count():
                await hb.click()

        # 3)–5) všechny příklady
        for i, q in enumerate(info):
            t = q["typ"]
            await page.locator("#timeline .tl-b").nth(i).click()
            await page.wait_for_timeout(30)
            if t == "dukaz":
                st = await evaluate(page, i)
                vis = await qpage(page, i).locator(".reseni").evaluate("e => !e.hidden")
                ok = st == "hotovo" and vis
                print(f"  {'OK ' if ok else 'CHYBA'} {i + 1}. důkaz: vzorové řešení {'vidět' if vis else 'NEVIDĚT'}")
                if not ok:
                    problems.append(f"příklad {i + 1} (důkaz): stav {st}, řešení vidět: {vis}")
                expected[i] = "hotovo"
                continue
            if first.get(t) == i:
                await answer(page, i, q, wrong=True)
                st = await evaluate(page, i)
                chk = await page.evaluate(f"""(() => {{ const q = QS[{i}]; return {{ locked: q._locked,
                    pom: q._sit ? q._sit.pomocne.length : 0, kresli: q._sit ? !!q._sit.kresli : null }}; }})()""")
                fb = (await qpage(page, i).locator(".fb").inner_text()).strip()
                ok = st == "seda" and not chk["locked"] and not chk["pom"] and "Správně je" not in fb
                if t in ("rysuj", "retez") and not chk["kresli"]:
                    ok = False
                print(f"  {'OK ' if ok else 'CHYBA'} {i + 1}. {t}: 1. pokus špatně → {st}: {fb[:70]}")
                if not ok:
                    problems.append(f"příklad {i + 1} ({t}) po 1. špatném pokusu: stav {st}, {chk}, „{fb}“")
                await answer(page, i, q)
                st = await evaluate(page, i)
                ok = st == "oranzova"
                print(f"  {'OK ' if ok else 'CHYBA'} {i + 1}. {t}: 2. pokus správně → {st}")
                if not ok:
                    problems.append(f"příklad {i + 1} ({t}) správně napodruhé: stav {st} (čekám oranzova)")
                expected[i] = "oranzova"
            elif red.get(t) == i:
                for k in range(3):
                    await answer(page, i, q, wrong=True)
                    st = await evaluate(page, i)
                chk = await page.evaluate(f"""(() => {{ const q = QS[{i}]; return {{ locked: q._locked,
                    dis: q._evalBtn.disabled, pom: q._sit ? q._sit.pomocne.length : 0 }}; }})()""")
                fb = (await qpage(page, i).locator(".fb").inner_text()).strip()
                ok = st == "cervena" and chk["locked"] and chk["dis"]
                if t in ("rysuj", "retez") and not chk["pom"]:
                    ok = False
                if q["fields"] and "Správně je" not in fb and t not in ("rysuj", "retez"):
                    ok = False
                print(f"  {'OK ' if ok else 'CHYBA'} {i + 1}. {t}: 3× špatně → {st}, zamčeno: {fb[:70]}")
                if not ok:
                    problems.append(f"příklad {i + 1} ({t}) po 3 špatných pokusech: stav {st}, {chk}, „{fb}“")
                expected[i] = "cervena"
            else:
                await answer(page, i, q)
                st = await evaluate(page, i)
                if st != "zelena":
                    fb = (await qpage(page, i).locator(".fb").inner_text()).strip()
                    problems.append(f"příklad {i + 1} ({t}) se správnou odpovědí: stav {st}: „{fb}“")
                    print(f"  CHYBA {i + 1}. {t}: {st}")
                expected[i] = "zelena"
        n_ok = sum(1 for v in expected.values() if v == "zelena")
        print(f"  OK  správné odpovědi napoprvé: {n_ok} příkladů zeleně" if not any("se správnou odpovědí" in x for x in problems) else "  CHYBA správné odpovědi")

        # 6) papír po přechodu a otočení
        if q0 is not None:
            await page.locator("#timeline .tl-b").nth(q0).click()
            n_s = await page.evaluate(f"QS[{q0}]._strokes.length")
            await page.set_viewport_size({"width": 1180, "height": 820})
            await layout_ok(page, "na šířku", problems)
            n_s2 = await page.evaluate(f"QS[{q0}]._strokes.length")
            px = await page.evaluate("(() => { const c = $('paper').getContext('2d').getImageData(0, 0, $('paper').width, $('paper').height).data; let n = 0; for (let i = 3; i < c.length; i += 4) if (c[i]) n++; return n; })()")
            ok = n_s == 1 and n_s2 == 1 and px > 0
            print(f"  {'OK ' if ok else 'CHYBA'} papír: tah zůstal u příkladu i po otočení")
            if not ok:
                problems.append(f"papír: tahů {n_s} → {n_s2}, vykreslených bodů {px}")
            await page.set_viewport_size({"width": 820, "height": 1180})

        # odchod z testu (jiná aplikace)
        await page.evaluate("""(() => { Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => 'hidden' });
            document.dispatchEvent(new Event('visibilitychange')); })()""")
        await page.wait_for_timeout(1100)
        await page.evaluate("""(() => { Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => 'visible' });
            document.dispatchEvent(new Event('visibilitychange')); })()""")

        # 8) souhrn a skóre
        await page.locator("#timeline .sum-b").click()
        await page.wait_for_timeout(100)
        body = sum(1 if v == "zelena" else 0.5 if v == "oranzova" else 0 for v in expected.values())
        mx = sum(1 for v in expected.values() if v != "hotovo")
        sk = await page.evaluate("skore()")
        ok = abs(sk["b"] - body) < 1e-9 and sk["max"] == mx
        print(f"  {'OK ' if ok else 'CHYBA'} souhrn: {sk['b']} / {sk['max']} bodů")
        if not ok:
            problems.append(f"skóre {sk} ≠ očekávané {body} / {mx}")
        await layout_ok(page, "souhrn", problems)

        # 11) obnovení rozpracovaného testu po zavření (dialog „Pokračovat?“ se potvrdí)
        pred = await page.evaluate("QS.map(q => [stav(q), q._st.pokusy, q._strokes.length])")
        await page.wait_for_timeout(700)
        await page.reload()
        await page.wait_for_timeout(800)
        po = await page.evaluate("QS.map(q => [stav(q), q._st.pokusy, q._strokes.length])")
        ok = pred == po
        print(f"  {'OK ' if ok else 'CHYBA'} obnovení po zavření: {sum(1 for x in po if x[0] != 'nove')} příkladů se stavem")
        if not ok:
            problems.append(f"obnovení po zavření nesouhlasí: před {pred}, po {po}")

        # 9) PDF
        async with page.expect_download(timeout=120000) as d:
            await page.click("#btnPdf")
        dl = await d.value
        fn = dl.suggested_filename
        print(f"  PDF: {fn}")
        if not re.search(r"_\d\d\.pdf$", fn):
            problems.append(f"PDF nemá pořadové číslo: {fn}")
        mtyp = re.search(r"_(test[a-z0-9-]*)_v\d\d\.html$", name)
        if sab18 and mtyp and not name.startswith("Sablona_") and f"_{topic}_{mtyp.group(1)}_{version}_" not in fn:
            problems.append(f"název PDF {fn} neobsahuje téma a typ testu ({topic}_{mtyp.group(1)}_{version})")

        # 7) záznam
        for _ in range(40):
            if await page.evaluate("Zaznam.fronta") == 0:
                break
            await page.wait_for_timeout(250)
        # 16) šablona v21+: zadání všech příkladů ve startu, verze papíru po Zpět, náhled papíru
        if SAB[0] >= 21:
            ch21 = []
            st = next((e for e in events if e.get("udalost") == "start"), None)
            try:
                det = json.loads(st["detail"]) if st else {}
            except Exception:  # noqa
                det = {}
            pr = det.get("priklady") or []
            if not re.fullmatch(r"v(\d\d)", str(det.get("sablona", ""))) or int(str(det["sablona"])[1:]) < 21:
                ch21.append(f"start: detail.sablona = {det.get('sablona')!r}")
            if len(pr) != len(info) or any(not p.get("zadani") for p in pr) or any(not p.get("spravna") for p in pr if p.get("typ") != "dukaz"):
                ch21.append(f"start: detail.priklady {len(pr)} ≠ příkladů {len(info)} nebo chybí zadání / správná odpověď")
            qi = q0 if q0 is not None else 0
            await page.evaluate(f"show({qi})")
            ver = await page.evaluate(f"""(() => {{ const q = QS[{qi}], v0 = q._paperVer || 0;
                q._strokes.push({{ color: "#1d1d1b", width: 1.1, eraser: false, pts: [[20, 20, .5], [80, 60, .5]] }});
                $("pUndo").click(); return [v0, q._paperVer || 0]; }})()""")
            if not ver[1] > ver[0]:
                ch21.append(f"Zpět na papíře nezměnil verzi papíru ({ver[0]} → {ver[1]})")
            for _ in range(40):
                if await page.evaluate("Zaznam.fronta === 0"):
                    break
                await page.wait_for_timeout(100)
            await page.evaluate(f"""(() => {{ const q = QS[{qi}];
                q._strokes.push({{ color: "#1d1d1b", width: 1.1, eraser: false, pts: [[20, 20, .5], [80, 60, .5]] }});
                q._paperVer = (q._paperVer || 0) + 1; }})()""")
            poslal = await page.evaluate(f"posliNahled(QS[{qi}])")
            await page.wait_for_timeout(1200)
            nh = [e for e in events if e.get("udalost") == "nahled" and e.get("priklad") == qi + 1]
            if not poslal or not nh or not str(nh[-1].get("papir", "")).startswith("data:image"):
                ch21.append("náhled papíru se neposlal (událost nahled s obrázkem)")
            print(f"  {'OK ' if not ch21 else 'CHYBA'} v21: zadání ve startu ({len(pr)}), verze papíru po Zpět, náhled papíru")
            problems.extend("v21: " + c for c in ch21)

        druhy = {}
        for e in events:
            druhy[e.get("udalost")] = druhy.get(e.get("udalost"), 0) + 1
        pokusy = await page.evaluate("QS.reduce((a, q) => a + (q._typ === 'dukaz' ? 0 : q._st.pokusy), 0)")
        n_dk = sum(1 for q in info if q["typ"] == "dukaz")
        chyby_z = []
        if not druhy.get("pokracovani"):
            chyby_z.append("chybí pokracovani (obnovení testu)")
        if druhy.get("start") != 1:
            chyby_z.append(f"start {druhy.get('start')}")
        if druhy.get("vyhodnoceni", 0) != pokusy:
            chyby_z.append(f"vyhodnoceni {druhy.get('vyhodnoceni', 0)} ≠ pokusů {pokusy}")
        if druhy.get("reseni", 0) != n_dk:
            chyby_z.append(f"reseni {druhy.get('reseni', 0)} ≠ důkazů {n_dk}")
        if not druhy.get("odchod"):
            chyby_z.append("chybí odchod")
        if not druhy.get("souhrn"):
            chyby_z.append("chybí souhrn")
        if q0 is not None and await page.evaluate(f"!!QS[{q0}].hint && TEST.showHints") and not druhy.get("napoveda"):
            chyby_z.append("chybí napoveda")
        if q0 is not None and not any(e.get("udalost") == "vyhodnoceni" and e.get("priklad") == q0 + 1
                                      and str(e.get("papir", "")).startswith("data:image") for e in events):
            chyby_z.append("vyhodnocení příkladu s papírem nemá obrázek papíru")
        if any(not e.get("id") or not e.get("zarizeni") or not e.get("relace") for e in events):
            chyby_z.append("některé události nemají id / zařízení / relaci")
        print(f"  {'OK ' if not chyby_z else 'CHYBA'} záznam: " + ", ".join(f"{k} {v}" for k, v in sorted(druhy.items())))
        if chyby_z:
            problems.append("záznam: " + "; ".join(chyby_z))

        if errors:
            problems.append(f"chyby v konzoli: {errors}")
        await browser.close()
    httpd.shutdown()

    if problems:
        print("\nNALEZENÉ PROBLÉMY:")
        for pr in problems:
            print("  -", pr)
        sys.exit(1)
    print("\nVše v pořádku.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    asyncio.run(main(sys.argv[1]))
