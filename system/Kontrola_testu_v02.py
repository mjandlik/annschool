#!/usr/bin/env python3
"""Kontrola HTML testu Ann School (system/Kontrola_testu_vXX.py).

Použití (z rootu repozitáře):
    python3 system/Kontrola_testu_v02.py <předmět>/<tema>_test_vXX.html

Co ověří:
  1. stránka se načte bez chyb v konzoli,
  2. správné odpovědi z konfigurace (zapsané s desetinnou čárkou a mezerami)
     dají v každé sekci 100 %,
  3. zjevně špatná odpověď se vyhodnotí jako chyba,
  4. tlačítko PDF vytvoří PDF s pořadovým číslem v názvu,
  5. verze v názvu souboru odpovídá TEST.version a téma odpovídá TEST.topic.

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
        ctx = await browser.new_context(viewport={"width": 820, "height": 1180}, accept_downloads=True)
        page = await ctx.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: m.type == "error" and errors.append(m.text))
        await page.goto(url)

        version = await page.evaluate("TEST.version")
        m = re.search(r"_(v\d\d)\.html$", name)
        if m and m.group(1) != version:
            problems.append(f"verze v názvu souboru ({m.group(1)}) ≠ TEST.version ({version})")
        topic = await page.evaluate("TEST.topic")
        mt = re.match(r"(.+)_test_v\d\d\.html$", name)
        if mt and not name.startswith("Sablona_") and mt.group(1) != topic:
            problems.append(f"téma v názvu souboru ({mt.group(1)}) ≠ TEST.topic ({topic})")

        answers = await page.evaluate(
            "SECTIONS.map(s => s.questions.map(q => q.answer))")
        sections = await page.locator(".sec:not(#finalScratch)").all()
        n_q = sum(len(a) for a in answers)
        print(f"Test: {await page.evaluate('TEST.title')} ({version}) – {len(answers)} sekcí, {n_q} příkladů")

        # 1) správné odpovědi -> 100 % v každé sekci
        for si, sec in enumerate(sections):
            inputs = sec.locator("input.ans")
            for qi, ans in enumerate(answers[si]):
                await inputs.nth(qi).fill(cz(ans))
            await sec.locator(".sec-btns .btn.primary").click()
            score = (await sec.locator(".sec-score").inner_text()).strip()
            name_s = await sec.locator("h2").inner_text()
            ok = "(100 %)" in score
            print(f"  {'OK ' if ok else 'CHYBA'} {name_s}: {score}")
            if not ok:
                bad = await sec.locator(".q.bad .q-row").all_inner_texts()
                problems.append(f"sekce „{name_s}“ nemá 100 % se správnými odpověďmi: {bad}")

        # 2) špatná odpověď musí být chyba
        sec0 = sections[0]
        await sec0.locator("input.ans").first.fill(cz(answers[0][0] * 7 + 13))
        await sec0.locator(".sec-btns .btn.primary").click()
        if not await sec0.locator(".q").first.evaluate("e => e.classList.contains('bad')"):
            problems.append("špatná odpověď nebyla označena jako chyba")
        await sec0.locator("input.ans").first.fill(cz(answers[0][0]))

        # 3) PDF
        async with page.expect_download(timeout=60000) as d:
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
