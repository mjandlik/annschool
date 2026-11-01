# Návod: studijní materiály pro Ann – HTML (system/Navod_material_v06)

Postup pro chat v projektu „Ann School“ při tvorbě studijního materiálu, taháku, pracovního listu, simulátoru nebo zápisků.
Struktura repozitáře, pojmenování, archiv a rozcestník jsou stejné jako v `system/Navod_test_vXX.md` (oddíly 0, 2, 5, 6).

**Od 01.11.2026 je všechno, co vytváří Claude pro Ann, jen HTML** (materiály, taháky, pracovní listy, simulátory, zápisky, testy).
PDF jsou jen **vstupy**: skeny sešitu a materiály ze školy (kap. 6). PDF se nesledují.
Starší vlastní PDF materiály (např. `fyzika/prevody-jednotek_material_v02.pdf`) zůstávají, nové verze už budou HTML.

---

## 1. Doptání

- Z projektu načti aktuální látku (`<předmět>/<téma>_vXX.md`) a podklady od Martina (sešit, pracovní listy).
- Zeptej se na to, co není jasné: rozsah látky, jestli materiál obsahuje i procvičování a výsledky, jestli jsou potřeba úlohy na rýsování nebo interaktivní prvky. U každého bodu navrhni výchozí volbu.
- Nic nevytvářej, dokud Martin neodpoví nebo nepotvrdí návrh.

---

## 2. Styl

- Nejdřív teorie, potom příklady. Oddíly odděluj jen vodorovnou čarou nebo nadpisem.
- Jednoduchý a přehledný styl, bez zbytečných rámečků a barevných podkladů. Vzhled jako rozcestník a testy (písmo systémové, barvy `#2b5cab` / `#1d1d1b`, pozadí `#fafaf7`).
- Ann čte na iPadu (Safari, na výšku i na šířku): základní text 17 px, obsah nejvýš asi 860 px široký, žádné vodorovné posouvání stránky (široké vzorce a tabulky jen s vlastním `overflow-x: auto`).
- Nahoře pevný panel: název · verze, tlačítko „Rozcestník“ (`../`).
- Vzorce: KaTeX předem vyrenderovaný do HTML (Node: `npm install katex`, `katex.renderToString(…)`), styl z `https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css`. Vzor: `matematika/mocniny-a-odmocniny_zapisky_vXX.html`. Jednoduché vzorce stačí Unicode (m², 10⁻³, ·, ≈).
- Vektor se šipkou: `<span class="vec">F</span>` se šipkou z CSS (jako v šabloně testu).
- Obrázky a grafy jako inline SVG (ostré na iPadu). Rýsování na čtverečkované síti s uvedeným měřítkem, interaktivní síť přes `system/lib/vektory.js` (Navod_test kap. 8).
- Kde má Ann psát (pracovní list, procvičování), dej plochu na psaní perem – stejné ovládání jako papír v testu: pero píše, prst posouvá. Plochu označ vlevo nahoře „Místo pro poznámky“.
- Pracovní list a tahák mají jít i vytisknout: `@media print` (bez panelu, A4, zalomení před velkými oddíly).
- Česká terminologie, desetinná čárka, jednotky SI. Vše musí být fyzikálně a matematicky správně, i když sešit obsahuje chybu. Opravy uveď v poznámce.

---

## 3. Tvorba

1. Soubor podle druhu (vždy HTML, o jednu složku pod rootem):
   - `<předmět>/<tema>_material_vXX.html`: studijní materiál (teorie + příklady),
   - `<předmět>/<tema>_tahak_vXX.html`: krátký tahák,
   - `<předmět>/<tema>_pracovni-list_vXX.html`: pracovní list,
   - `<předmět>/<tema>_simulator_vXX.html`: interaktivní pomůcka,
   - `<předmět>/<tema>_zapisky_vXX.html`: přepis zápisků ze sešitu.
   - V rozcestníku se zobrazí ve skupině **Výukové materiály** (zápisky ve skupině **Zápisky**) u daného tématu.
2. Celá stránka je jeden soubor (styly i skripty uvnitř). Knihovny jen z `../system/lib/` nebo CDN (KaTeX).
3. **Sledování** (povinné, kap. 7): do `<head>` za ostatní skripty
   ```html
   <script src="../system/lib/zaznam.js"></script>
   <script src="../system/lib/sledovani.js" data-typ="material"></script>
   ```
   `data-typ` = typ ze jména souboru (`material`, `tahak`, `pracovni-list`, `simulator`, `zapisky`). U delších materiálů nastavuj oblast podle kapitoly: `Sledovani.oblast("2. Sčítání vektorů")` (např. přes IntersectionObserver na nadpisech), jinak se počítá podle posunutí.
4. Existuje-li starší verze (i PDF), přesuň ji `git mv` do `archiv/<předmět>-<původní název>`.

---

## 4. Kontrola (povinná)

1. Přepočítej všechny výsledky v Pythonu.
2. V Playwrightu otevři stránku jako iPad na výšku (820 × 1180) i na šířku (1180 × 820), `device_scale_factor` 2, a prohlédni snímky: diakritika, vzorce, obrázky, žádné vodorovné posouvání, žádné chyby v konzoli.
3. Sledování: podvrhni adresu webové aplikace (`add_init_script`: `window.ANNSCHOOL_ENDPOINT = "https://zaznam.test/exec"`, `route` odpovídá `{"ok":true}`) a ověř, že po otevření přijde `otevreni` a po posunutí a `Sledovani.souhrn()` událost `stranka` s nenulovou aktivní dobou.
4. U pracovního listu a taháku zkontroluj i tisk (`page.pdf()` – jen pro kontrolu, PDF se nenahrává).

---

## 5. Zveřejnění

- Postupuj podle `Navod_test_vXX.md`, oddíly 5 a 6: název tématu do rozcestníku, commit, push a odkaz pro Martina.
- Odkaz: `https://mjandlik.github.io/annschool/<předmět>/<tema>_material_vXX.html`.
- Příklady z materiálu ulož do projektu Claude jako novou verzi `<předmět>/<téma>_vXX.md`.

---

## 6. Vstupy: zápisky ze sešitu a školní materiály (PDF, nevytváří Claude)

Skeny sešitu a materiály ze školy (pracovní listy, cvičení, pokyny, řešení od učitele) se na GitHub nahrávají **beze změny obsahu**, jen přejmenované:

- Zápisky ze sešitu: `<předmět>/sesit_zapisky_vXX.pdf` – celý sešit předmětu, téma „Sešit“. Nový sken (doplněné stránky) = nová verze, stará do archivu.
- Školní materiál: `<předmět>/<tema>_skolni-material[-<podtyp>]_vXX.pdf`, např. `fyzika/prevody-jednotek_skolni-material-pracovni-list_v01.pdf`. Téma podle obsahu; víc materiálů k jednomu tématu rozliš podtypem.
- Rozcestník je řadí do skupin **Zápisky** a **Školní materiály** u tématu a odkazuje na PDF přímo. Nové téma nebo podtyp doplň do `NAZVY` v `index.html` (např. `"skolni-material-pracovni-list": "Pracovní list"`).
- Duplicity a pracovní soubory (kopie v `_tmp`, xlsx) nenahrávej.
- PDF se nesledují.
- Z těchto souborů vycházej při tvorbě vlastních materiálů a testů (látka, značení, terminologie), ale vlastní materiály musí být fyzikálně a matematicky správné i tam, kde sešit obsahuje chybu.

---

## 7. Sledování čtení teorie

Otevírání HTML stránek s teorií se zapisuje do stejné Google tabulky jako výsledky testů (`system/lib/zaznam.js` → list Udalosti) a ukazuje v přehledu `vysledky.html`, záložka **Teorie a stránky**. Sleduje se i rozcestník. Testy mají vlastní záznam (Navod_test kap. 9), `sledovani.js` do nich nepatří. `vysledky.html` a `zarizeni.html` se nesledují.

Co se zaznamenává (`system/lib/sledovani.js`, popis v hlavičce souboru):

- **otevreni:** kdy, kdo (zařízení, přezdívka), odkud (z rozcestníku / webu, přímým odkazem, z jiné aplikace), rozměry a orientace.
- **odchod:** každý návrat z jiné aplikace, jiného panelu nebo po zamčení a jak dlouho byla pryč.
- **stranka (souhrn):** posílá se při odchodu ze stránky a každou minutu, když se něco změnilo:
  - doba otevření, doba na obrazovce, **aktivní doba** (stránka vidět a v posledních 30 s posouvání, klepnutí nebo psaní),
  - počet a doba odchodů, nejhlubší posunutí (% stránky), ujetá vzdálenost posouvání, klepnutí, klávesy, tahy perem,
  - aktivní čas podle **oblastí**: kapitola (`Sledovani.oblast(…)`), jinak desetina výšky stránky („20–30 %“).
- **klik:** na rozcestníku každé klepnutí na položku (co otevřela).
- Nezaznamenává se obsah psaní ani kam odešla.
