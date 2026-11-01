#!/usr/bin/env python3
"""Kontrola HTML testu Ann School (system/Kontrola_testu_vXX.py).

Použití (z rootu repozitáře):
    python3 system/Kontrola_testu_v03.py <předmět>/<tema>_test_vXX.html

Co ověří:
  1. stránka se načte bez chyb v konzoli a bez vodorovného posouvání (iPad 820 × 1180),
  2. správné odpovědi z konfigurace dají v každé sekci 100 %:
     - čísla zapsaná s desetinnou čárkou a mezerami,
     - výběr klepnutím na správnou možnost,
     - „rysuj“ a „retez“ nakreslením vektorů myší přes síť,
  3. špatná odpověď se vyhodnotí jako chyba – u každého typu, který test obsahuje
     (u rýsování se musí ukázat správný vektor čárkovaně a síť se zamkne),
  4. „Zkusit znovu“ smaže odpovědi i kresbu a síť zase odemkne,
  5. tlačítko PDF vytvoří PDF s pořadovým číslem v názvu,
  6. verze v názvu souboru odpovídá TEST.version a téma odpovídá TEST.topic.

Funguje i pro starší testy (jen číselné příklady, šablona v12 a starší).
Potřebuje: pip install playwright && python3 -m playwright install chromium
"""
import asyncio, http.server, os, re, socketserver, sys, threading
from playwright.async_api import async_playwright


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


# popis příkladů ze stránky (šablona v13+ má q._typ a q._fields, starší jen q.answer)
INFO_JS = """SECTIONS.map(s => s.questions.map(q => ({
  typ: q._typ || "cislo",
  fields: q._fields ? q._fields.map(f => ({ answer: f.answer, opt: !!f.options, n: f.options ? f.options.length : 0 }))
                    : [{ answer: q.answer, opt: false, n: 0 }],
  answer: q.answer || null, retez: q.retez || null,
  sit: q._sit ? { xmin: q._sit.o.xmin, xmax: q._sit.o.xmax, ymin: q._sit.o.ymin, ymax: q._sit.o.ymax } : null })))"""


def fit_start(sit, pts, x=0, y=0):
    """Počátek tak, aby se všechny body (průběžné součty) vešly do sítě."""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x = min(sit["xmax"] - max(xs), max(sit["xmin"] - min(xs), x))
    y = min(sit["ymax"] - max(ys), max(sit["ymin"] - min(ys), y))
    return x, y


async def draw(page, si, qi, x1, y1, x2, y2):
    """Nakreslí vektor myší z uzlu [x1; y1] do uzlu [x2; y2] v síti příkladu."""
    await page.evaluate(f"SECTIONS[{si}].questions[{qi}]._sit.cv.scrollIntoView({{block: 'center'}})")
    await page.wait_for_timeout(50)
    X1, Y1, X2, Y2 = await page.evaluate(f"""(() => {{ const s = SECTIONS[{si}].questions[{qi}]._sit, r = s.cv.getBoundingClientRect();
        return [r.left + s.px({x1}), r.top + s.py({y1}), r.left + s.px({x2}), r.top + s.py({y2})]; }})()""")
    await page.mouse.move(X1, Y1)
    await page.mouse.down()
    await page.mouse.move(X2, Y2, steps=10)
    await page.mouse.up()
    await page.wait_for_timeout(30)


async def fill_fields(qloc, fields, wrong=False):
    """Vyplní pole příkladu (správně, nebo u prvního pole záměrně špatně)."""
    ni = oi = 0
    for k, f in enumerate(fields):
        bad = wrong and k == 0
        if f["opt"]:
            idx = (f["answer"] + 1) % f["n"] if bad else f["answer"]
            await qloc.locator(".opts").nth(oi).locator("button").nth(idx).click()
            oi += 1
        else:
            val = f["answer"] * 7 + 13 if bad else f["answer"]
            await qloc.locator("input.ans").nth(ni).fill(cz(val))
            ni += 1


async def do_drawing(page, si, qi, q, wrong=False):
    """Nakreslí odpověď u typu rysuj / retez (wrong: špatně)."""
    sit = q["sit"]
    if q["typ"] == "rysuj":
        dx, dy = q["answer"]["dx"], q["answer"]["dy"]
        if wrong:
            dx = dx + 1 if dx != -1 or dy else dx - 1      # o dílek jinak (nikdy nulový vektor)
        x, y = fit_start(sit, [(0, 0), (dx, dy)], 0, 0)
        await draw(page, si, qi, x, y, x + dx, y + dy)
        return
    chain = q["retez"]
    pts = [(0, 0)]
    for r in chain:
        pts.append((pts[-1][0] + r["dx"], pts[-1][1] + r["dy"]))
    x, y = fit_start(sit, pts, 0, 0)
    qloc_btn = lambda i: page.locator(".sec:not(#finalScratch)").nth(si).locator(".q").nth(qi).locator(".grid-tools button[data-i]").nth(i)
    for i in range(len(chain)):
        await qloc_btn(i).click()
        await draw(page, si, qi, x + pts[i][0], y + pts[i][1], x + pts[i + 1][0], y + pts[i + 1][1])
    if wrong:
        return                                   # výslednice chybí → chyba
    await qloc_btn(len(chain)).click()
    await draw(page, si, qi, x, y, x + pts[-1][0], y + pts[-1][1])


async def main(path):
    full = os.path.abspath(path)
    name = os.path.basename(full)
    root = os.path.dirname(full)          # root repozitáře = složka, ve které je system/
    while not os.path.isdir(os.path.join(root, "system")) and os.path.dirname(root) != root:
        root = os.path.dirname(root)
    httpd = serve(root)
    rel = os.path.relpath(full, root).replace(os.sep, "/")
    url = f"http://127.0.0.1:{httpd.server_address[1]}/{rel}"
    problems = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(viewport={"width": 820, "height": 1180}, device_scale_factor=2,
                                        accept_downloads=True)
        page = await ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: m.type == "error" and errors.append(m.text))
        page.on("dialog", lambda d: asyncio.ensure_future(d.accept()))
        await page.goto(url)
        await page.wait_for_timeout(300)

        version = await page.evaluate("TEST.version")
        m = re.search(r"_(v\d\d)\.html$", name)
        if m and m.group(1) != version:
            problems.append(f"verze v názvu souboru ({m.group(1)}) ≠ TEST.version ({version})")
        topic = await page.evaluate("TEST.topic")
        mt = re.match(r"(.+)_test(-[a-z0-9-]+)?_v\d\d\.html$", name)
        if mt and not name.startswith("Sablona_") and mt.group(1) != topic:
            problems.append(f"téma v názvu souboru ({mt.group(1)}) ≠ TEST.topic ({topic})")
        if await page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1"):
            problems.append("stránka se posouvá vodorovně")

        info = await page.evaluate(INFO_JS)
        sections = page.locator(".sec:not(#finalScratch)")
        n_q = sum(len(s) for s in info)
        typy = sorted({q["typ"] for s in info for q in s})
        print(f"Test: {await page.evaluate('TEST.title')} ({version}) – {len(info)} sekcí, {n_q} příkladů, typy: {', '.join(typy)}")

        # 1) správné odpovědi -> 100 % v každé sekci
        for si, qs in enumerate(info):
            sec = sections.nth(si)
            for qi, q in enumerate(qs):
                qloc = sec.locator(".q").nth(qi)
                await fill_fields(qloc, q["fields"])
                if q["typ"] in ("rysuj", "retez"):
                    await do_drawing(page, si, qi, q)
            await sec.locator(".sec-btns .btn.primary").click()
            score = (await sec.locator(".sec-score").inner_text()).strip()
            name_s = await sec.locator("h2").inner_text()
            ok = "(100 %)" in score
            print(f"  {'OK ' if ok else 'CHYBA'} {name_s}: {score}")
            if not ok:
                bad = await sec.locator(".q.bad").all_inner_texts()
                problems.append(f"sekce „{name_s}“ nemá 100 % se správnými odpověďmi: {bad}")

        # 2) špatná odpověď = chyba (první příklad každého typu), 3) Zkusit znovu
        hotove = set()
        for si, qs in enumerate(info):
            for qi, q in enumerate(qs):
                t = q["typ"]
                if t in hotove:
                    continue
                hotove.add(t)
                sec = sections.nth(si)
                qloc = sec.locator(".q").nth(qi)
                await sec.locator(".sec-btns .btn").nth(1).click()          # Zkusit znovu (dialog se potvrdí)
                await page.wait_for_timeout(50)
                if t in ("rysuj", "retez"):
                    st = await page.evaluate(f"""(() => {{ const q = SECTIONS[{si}].questions[{qi}];
                        return {{ upravy: q._sit.o.upravy, kresli: !!q._sit.kresli, n: annIds(q).filter(id => q._sit.vektor(id)).length }}; }})()""")
                    if not st["upravy"] or not st["kresli"] or st["n"]:
                        problems.append(f"Zkusit znovu neodemklo nebo nesmazalo síť ({t}): {st}")
                    if q["fields"]:
                        await fill_fields(qloc, q["fields"])
                    await do_drawing(page, si, qi, q, wrong=True)
                else:
                    await fill_fields(qloc, q["fields"], wrong=True)
                await sec.locator(".sec-btns .btn.primary").click()
                bad = await qloc.evaluate("e => e.classList.contains('bad')")
                fb = (await qloc.locator(".fb").inner_text()).strip()
                print(f"  {'OK ' if bad else 'CHYBA'} špatná odpověď ({t}): {fb[:90]}")
                if not bad:
                    problems.append(f"špatná odpověď typu {t} nebyla označena jako chyba")
                if t in ("rysuj", "retez"):
                    st = await page.evaluate(f"""(() => {{ const s = SECTIONS[{si}].questions[{qi}]._sit;
                        return {{ pomocne: s.pomocne.length, upravy: s.o.upravy, kresli: !!s.kresli }}; }})()""")
                    if not st["pomocne"]:
                        problems.append(f"u chybného rýsování ({t}) se neukázal správný vektor")
                    if st["upravy"] or st["kresli"]:
                        problems.append(f"po vyhodnocení ({t}) zůstala síť odemčená")

        # 4) PDF
        async with page.expect_download(timeout=90000) as d:
            await page.click("#btnPdf")
        dl = await d.value
        fn = dl.suggested_filename
        print(f"  PDF: {fn}")
        if not re.search(r"_\d\d\.pdf$", fn):
            problems.append(f"PDF nemá pořadové číslo: {fn}")

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
