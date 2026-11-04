# Návod: studijní materiály pro Ann – HTML (system/Navod_material_v13)

Postup pro chat v projektu „Ann School“ při tvorbě studijního materiálu, taháku, pracovního listu, simulátoru nebo zápisků.
Struktura repozitáře, pojmenování, archiv a rozcestník jsou stejné jako v `system/Navod_test_vXX.md` (oddíly 0, 2, 5, 6).
**Před prací si přečti `system/Pouceni_vXX.md`. Po práci projdi kontrolu po sobě (kap. 4) – bez ní se nic nepushuje.**

**Od 01.11.2026 je všechno, co vytváří Claude pro Ann, jen HTML** (materiály, taháky, pracovní listy, simulátory, zápisky, testy).
PDF jsou jen **vstupy**: skeny sešitu a materiály ze školy (kap. 6). PDF se nesledují.
Starší vlastní PDF materiály (např. `fyzika/prevody-jednotek_material_v02.pdf`) zůstávají, nové verze už budou HTML.

**Od 03.11.2026 (Martin):** studijní materiál a zápisky se dělají na **šabloně stránky s teorií** `system/Sablona_material_vXX.html` (kap. 8):
kapitola = jedna obrazovka, v kapitole sekce s Chápu / Nechápu, na další kapitolu se jde, až je u každé sekce volba, dole časová osa
jako v testu. **Ke každé definici nebo pravidlu zapsanému značkami patří příklad na konkrétních číslech** (`<div class="prakticky">`).
Teorie z PDF (sešit, školní materiály) se k tématu přepisuje do HTML zápisků `<tema>_zapisky_vXX.html` (kap. 6); PDF zůstávají jako vstup.

**Od 04.11.2026 (T02, šablona v02):** u každé sekce je vedle Chápu / Nechápu tlačítko **„Vyzkoušej se“** (Ann napíše, co si zapamatovala,
látka sekce se přitom zakryje; text jde do výsledků; od šablony v03 se píše perem na papír jako v testu) a kapitolu jde **přeskočit bez volby** (kap. 8). Tahák a pracovní list „Vyzkoušej se“ nemají.

---

## 1. Doptání

- Přečti `system/Pouceni_vXX.md`, z projektu aktuální látku (`<předmět>/<téma>_vXX.md`) a podklady od Martina (sešit, pracovní listy).
- Zeptej se na to, co není jasné: rozsah látky, jestli materiál obsahuje i procvičování a výsledky, jestli jsou potřeba úlohy na rýsování nebo interaktivní prvky. U každého bodu navrhni výchozí volbu.
- Nic nevytvářej, dokud Martin neodpoví nebo nepotvrdí návrh.

---

## 2. Styl

- Nejdřív teorie, potom příklady. Oddíly odděluj jen vodorovnou čarou nebo nadpisem.
- Jednoduchý a přehledný styl, bez zbytečných rámečků a barevných podkladů. Vzhled jako rozcestník a testy (písmo systémové, barvy `#2b5cab` / `#1d1d1b`, pozadí `#fafaf7`).
- Ann čte na iPadu (Safari, na výšku i na šířku): základní text 17 px, obsah nejvýš asi 860 px široký, žádné vodorovné posouvání stránky (široké vzorce a tabulky jen s vlastním `overflow-x: auto`).
- Nahoře pevný panel nebo hlavička: název · verze, tlačítko „Rozcestník“ (`../`). **Zobrazená verze musí sedět s verzí v názvu souboru** – při každé nové verzi ji oprav (Pouceni, bod 7; hlídá `Kontrola_repo`). Šablona stránky s teorií bere verzi z názvu souboru a název z `<title>` sama.
- Vzorce: KaTeX předem vyrenderovaný do HTML, styl z `https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css`. Piš LaTeX `$…$` (v textu) a `$$…$$` (samostatně) a pak spusť
  `npm install --prefix /tmp/katex katex@0.16.11` (jednou za sezení; **verze musí sedět se stylem 0.16.11 v šabloně**, skript jinou odmítne – Pouceni bod 28) a `NODE_PATH=/tmp/katex/node_modules node system/Vzorce_v01.js <soubor>` – vyrenderuje vzorce přímo v souboru (skripty, styly a komentáře nechá; `\$` = znak dolaru). Zlomky vždy `\frac`, desetinná čárka `{,}`. Jednoduché vzorce stačí Unicode (m², 10⁻³, ·, ≈).
- **Tlačítka malá** (asi 14 px písmo, odsazení 4 × 10 px, tenký okraj), aby nerušila text a obrázky (Pouceni, bod 18). Velká tlačítka jen tam, kde se píše perem.
- Vektor se šipkou: `<span class="vec">F</span>` se šipkou z CSS (jako v šabloně testu).
- Obrázky a grafy jako inline SVG (ostré na iPadu). Rýsování na čtverečkované síti s uvedeným měřítkem, interaktivní síť přes `system/lib/vektory.js` (Navod_test kap. 8).
- Kde má Ann psát (pracovní list, procvičování), dej plochu na psaní perem – stejné ovládání jako papír v testu: pero píše, prst posouvá. Plochu označ vlevo nahoře „Místo pro poznámky“. Papír není samostatná knihovna – převezmi kód z aktuální `system/Sablona_test_vXX.html`:
  - styly `#paperBox`, `.paper-bar`, `#paperView` (oddíl stylů u „papír“),
  - HTML `#paperBox` s lištou (Zpět, Smazat – od šablony v20 vlevo, text lišty za nimi) a `<canvas id="paper">`,
  - skript z oddílu `/* ---------- papír: … ---------- */` (objekt `draw`, kreslení perem a myší, posun prstem přes `touch-action: none`, od šablony v25 i potlačené dotyky pera kvůli Scribble – Pouceni bod 20, vyhlazení a tlak) a funkci `setEraser`.
  - Místo tahů u příkladu (`q._strokes`) drž jedno pole tahů pro stránku; vazbu na test (stav příkladu, PDF, ukládání) vynech. Ověř v Playwrightu, že pero (myš) píše a dotyk posouvá.
- Pracovní list a tahák mají jít i vytisknout: `@media print` (bez panelu, A4, zalomení před velkými oddíly).
- Česká terminologie, desetinná čárka, jednotky SI. Vše musí být fyzikálně a matematicky správně, i když sešit obsahuje chybu. Opravy uveď v poznámce.

---

## 3. Tvorba

1. Soubor podle druhu (vždy HTML, o jednu složku pod rootem). **Materiál a zápisky vždy z aktuální `system/Sablona_material_vXX.html`** (kap. 8); tahák, pracovní list a simulátor jsou jednostránkové (vlastní HTML podle kap. 2), tahák a pracovní list s tlačítky Chápu / Nechápu:
   - `<předmět>/<tema>_material_vXX.html`: studijní materiál (teorie + příklady),
   - `<předmět>/<tema>_tahak_vXX.html`: krátký tahák,
   - `<předmět>/<tema>_pracovni-list_vXX.html`: pracovní list,
   - `<předmět>/<tema>_simulator_vXX.html`: interaktivní pomůcka,
   - `<předmět>/<tema>_zapisky_vXX.html`: přepis zápisků ze sešitu.
   - V rozcestníku se zobrazí ve skupině **Výukové materiály** (zápisky ve skupině **Zápisky**) u daného tématu.
2. Celá stránka je jeden soubor (styly i skripty uvnitř). Knihovny jen z `../system/lib/` nebo CDN (KaTeX).
3. **Sledování** (povinné, kap. 7; šablona stránky s teorií ho už má v bloku HLAVIČKA – měníš jen `data-typ`): do `<head>` za ostatní skripty
   ```html
   <script src="../system/lib/zaznam.js"></script>
   <script src="../system/lib/sledovani.js" data-typ="material"></script>
   ```
   `data-typ` = typ ze jména souboru (`material`, `tahak`, `pracovni-list`, `simulator`, `zapisky`). U delších materiálů nastavuj oblast podle kapitoly: `Sledovani.oblast("2. Sčítání vektorů")` (např. přes IntersectionObserver na nadpisech), jinak se počítá podle posunutí.
4. **Chápu / Nechápu** (povinné u materiálu, taháku, pracovního listu a zápisků; od 01.11.2026): na konec každé části teorie dej prázdný prvek
   ```html
   <div data-porozumeni="3. Křížové pravidlo – proč do kříže"></div>
   ```
   `sledovani.js` do něj sám vloží malá tlačítka „Rozumíš tomu? Chápu / Nechápu“. **Část (sekce) = každé místo, kde je něco vysvětleno** – i jen jedna definice, jedno pravidlo nebo jeden důkaz (od 03.11.2026; dřív kapitola nebo podkapitola). Na šabloně stránky s teorií je sekce `<div class="sekce">…<div data-porozumeni="…"></div></div>` uvnitř kapitoly. Název části je jednoznačný, začíná číslem kapitoly a nemění se mezi verzemi (podle něj přehled spojuje volby z různých otevření a verzí) – při převodu starší stránky ponech dosavadní názvy u sekcí se stejným obsahem. Řešené příklady patří do sekce, kterou procvičují, vlastní tlačítka nemají; do testů se tlačítka nedávají. Bez tlačítek hlásí `Kontrola_repo` varování, na šabloně kapitolu bez tlačítek (mimo přílohu) chybou.
   Na šabloně v02+ je sekce `<div class="sekce"><h3>…</h3> látka … <div data-porozumeni="…"></div></div>` – **za `data-porozumeni` v sekci nic nepatří** (při „Vyzkoušej se“ se zakryje jen to, co je nad tlačítky; hlídá `Kontrola_repo` v04). Úvodní `<h3>` zůstane při zakrytí vidět – sekce bez nadpisu ukáže nad polem název sekce.
   **Příklad na konkrétních číslech** (od 03.11.2026): ke každé definici nebo pravidlu zapsanému značkami (ℕ = {1, 2, …}, $a^m \cdot a^n = a^{m+n}$, $|x|$, a | b, intervaly…) dej `<div class="prakticky">…</div>` s dosazenými čísly a výsledkem, u množin co do nich patří a co ne, kde to dává smysl i z běžného života (teplota −5 °C, cena 12,50 Kč). Šablona před něj napíše „Na konkrétních číslech:“. Sekci s `.rule` bez `.prakticky` hlásí `Kontrola_repo` (v03) varováním.
5. Existuje-li starší verze (i PDF), přesuň ji `git mv` do `archiv/<předmět>-<původní název>`.
6. Nový typ nebo téma doplň do `NAZVY` v `index.html` (Navod_test kap. 5).

---

## 4. Kontrola po sobě (povinná, před každým pushem)

Stejně jako u testu (Navod_test kap. 4, body 1, 3–7): nezávislý přepočet (u delších materiálů přes samostatného agenta), `python3 system/Kontrola_repo_vXX.py` → „Repozitář bez chyb.“, soulad dokumentace, kontrola poznámky v projektu, Poučení a blok „Kontrola“ pro Martina. Navíc:

1. Přepočítej všechny výsledky v Pythonu ze zadání (i příklady na konkrétních číslech). U každého tvrzení v teorii ověř, že platí i pro hraniční případy (podmínky typu a ≠ 0, a > 0).
2. V Playwrightu otevři stránku jako iPad na výšku (820 × 1180) i na šířku (1180 × 820), `device_scale_factor` 2, a prohlédni snímky: diakritika, vzorce, obrázky, žádné vodorovné posouvání, žádné chyby v konzoli.
3. Sledování: podvrhni adresu webové aplikace (`add_init_script`: `window.ANNSCHOOL_ENDPOINT = "https://zaznam.test/exec"`, `route` odpovídá `{"ok":true}`) a ověř, že po otevření přijde `otevreni` a po posunutí a `Sledovani.souhrn()` událost `stranka` s nenulovou aktivní dobou.
4. Chápu / Nechápu: u každé části teorie je `data-porozumeni`; klepnutí pošle událost `porozumeni`, volba je vidět i po znovuotevření stránky a druhé klepnutí ji zruší.
   Na šabloně v02+ navíc **Vyzkoušej se** u každé sekce (v03: papír 320 px, tah myší na plátně → `tahu`, po znovuotevření jsou tahy na papíře, událost má `papir` „data:image/jpeg…“; měření čekej déle než animace 0,4 s, jinak se měří zavírání předchozího pole – Pouceni bod 36): po klepnutí se pole rozbalí pod tlačítky, látka je zakrytá (nic z ní není vidět, výška sekce stejná), řádek s tlačítky se při otevření, „Ukázat / Skrýt látku“ ani „Hotovo“ na obrazovce nepohne (měř `getBoundingClientRect().top` po snímcích – obsah pod polem se smí jen plynule posouvat); text zůstane po znovuotevření, přijde událost `vyzkousej` a beze změny se znovu neposílá. **Přeskočení:** „Přeskočit bez volby ›“ → potvrzení → další kapitola, událost `preskoceni`. **Nová verze:** volby uložené pod starou verzí stránky se převezmou (otevreni → `prevzato`). Ověř na iPadu (na výšku i na šířku), mobilu (412 px) i počítači.
   Na šabloně stránky s teorií navíc: projdi **všechny kapitoly** (u všech sekcí Chápu, pak „Další kapitola“) a u každé udělej snímek; ověř, že bez volby nejde na další kapitolu (hláška), že se kolečka na časové ose barví, souhrn ukazuje všechny sekce a že `document.documentElement.scrollWidth ≤ innerWidth` v každé kapitole. CDN `katex.min.css` se v sandboxu nenačte – v Playwrightu ho **podvrhni z místního balíku** (`route` na `https://cdn.jsdelivr.net/npm/katex@0.16.11/**` → soubory z `/tmp/katex/node_modules/katex/dist/`), jinak jsou vzorce bez stylu a kontrola hlásí falešné vodorovné přetečení (Pouceni bod 27).
5. U pracovního listu a taháku zkontroluj i tisk (`page.pdf()` – jen pro kontrolu, PDF se nenahrává).

---

## 5. Zveřejnění

- Postupuj podle `Navod_test_vXX.md`, oddíly 5 a 6: název tématu do rozcestníku, kontrola po sobě, commit, push a odkaz pro Martina s blokem „Kontrola“.
- Odkaz: `https://mjandlik.github.io/annschool/<předmět>/<tema>_material_vXX.html`.
- Příklady z materiálu (všech 5 polí) ulož do projektu Claude jako novou verzi `<předmět>/<téma>_vXX.md` a zkontroluj ji (Navod_test kap. 4, bod 5).

---

## 6. Vstupy: zápisky ze sešitu a školní materiály (PDF, nevytváří Claude) a jejich převod do HTML

Skeny sešitu a materiály ze školy (pracovní listy, cvičení, pokyny, řešení od učitele) se na GitHub nahrávají **beze změny obsahu**, jen přejmenované:

- Zápisky ze sešitu: `<předmět>/sesit_zapisky_vXX.pdf` – celý sešit předmětu, téma „Sešit“. Nový sken (doplněné stránky) = nová verze, stará do archivu.
- Školní materiál: `<předmět>/<tema>_skolni-material[-<podtyp>]_vXX.pdf`, např. `fyzika/prevody-jednotek_skolni-material-pracovni-list_v01.pdf`. Téma podle obsahu; víc materiálů k jednomu tématu rozliš podtypem.
- Rozcestník je řadí do skupin **Zápisky** a **Školní materiály** u tématu a odkazuje na PDF přímo. Nové téma nebo podtyp doplň do `NAZVY` v `index.html` (např. `"skolni-material-pracovni-list": "Pracovní list"`).
- Duplicity a pracovní soubory (kopie v `_tmp`, xlsx) nenahrávej.
- PDF se nesledují.
- Z těchto souborů vycházej při tvorbě vlastních materiálů a testů (látka, značení, terminologie), ale vlastní materiály musí být fyzikálně a matematicky správné i tam, kde sešit obsahuje chybu.
- **Převod teorie do HTML** (od 03.11.2026): teorie z PDF (sešit, školní materiály, starší vlastní PDF tahák) se k tématu přepisuje do `<předmět>/<tema>_zapisky_vXX.html` na šabloně stránky s teorií – seřazeno podle učiva, opravené chyby, doplněná vysvětlení a příklady na konkrétních číslech, řešené příklady z PDF jako ukázky postupu. Opravy oproti sešitu do přílohy „Opravy oproti sešitu“. PDF zůstávají beze změny. Matematika je převedená (03.11.2026: přirozená a celá čísla, číselné obory, dělitelnost, absolutní hodnota, mocniny a odmocniny); fyzika a chemie jen na Martinův pokyn.

---

## 7. Sledování čtení teorie

Otevírání HTML stránek s teorií se zapisuje do stejné Google tabulky jako výsledky testů (`system/lib/zaznam.js` → list Udalosti) a ukazuje v přehledu `vysledky.html`, záložka **Teorie a stránky**. Sleduje se i rozcestník. Testy mají vlastní záznam (Navod_test kap. 9), `sledovani.js` do nich nepatří. `vysledky.html` a `zarizeni.html` se nesledují.

Co se zaznamenává (`system/lib/sledovani.js`, popis v hlavičce souboru):

- **otevreni:** kdy, kdo (zařízení, přezdívka), odkud (`web` = z rozcestníku nebo jiné stránky Ann School, `jinde` = z jiného webu, `primo` = bez odkazující stránky, např. z WhatsAppu nebo záložky), rozměry a orientace.
- **odchod:** každý návrat z jiné aplikace, jiného panelu nebo po zamčení a jak dlouho byla pryč.
- **stranka (souhrn):** posílá se při odchodu ze stránky a každou minutu, když se něco změnilo:
  - doba otevření, doba na obrazovce, **aktivní doba** (stránka vidět a v posledních 30 s posouvání, klepnutí nebo psaní),
  - počet a doba odchodů, nejhlubší posunutí (% stránky), ujetá vzdálenost posouvání, klepnutí, klávesy, tahy perem,
  - aktivní čas podle **oblastí**: kapitola (`Sledovani.oblast(…)`; šablona stránky s teorií ho nastavuje sama podle zobrazené kapitoly, souhrn = „Σ Souhrn“), jinak desetina výšky stránky („20–30 %“).
- **klik:** na rozcestníku každé klepnutí na položku (co otevřela).
- **vyzkousej** (šablona v02+): co Ann napsala ve „Vyzkoušej se“ u části teorie. `sekce` = název části, detail `{ cast, text (celý, nejvýš 4000 znaků), znaku, tahu (tahy perem na papíře, v03), papir_zmena, papir_prazdny, odkryto (kolikrát si celkem odkryla látku), odkryto_s, pred_odkrytim (znaků při prvním odkrytí, jinak null), pred_odkrytim_tahu (tahů při prvním odkrytí, v03), duvod: "hotovo" | "opusteni" | "pauza" | "odchod" | "kapitola", poradi }`; od v03 sloupec `papir` = obrázek papíru (JPEG oříznutý na tahy, s mřížkou) – jen když se papír od minula změnil, skript ho uloží na Disk jako papír z testů. Posílá se při „Hotovo“, opuštění pole, po 20 s bez psaní (i po posledním tahu perem), při přechodu na jinou kapitolu a odchodu ze stránky – vždy celý text, jen když se od minula změnil text, papír nebo počet odkrytí. Událost s obrázkem papíru neodchází přes beacon při zavření stránky, zůstane ve frontě a odešle se při příštím otevření (jako papír z testů). Text se pamatuje v prohlížeči (`annschool:vyzkousej:<adresa>`). Apps Script ani tabulka se kvůli tomu neměnily (list Udalosti, `detail` až 45 000 znaků).
- **preskoceni** (šablona v02+): kapitola přeskočená bez volby. `sekce` = kapitola, detail `{ kapitola, bez_volby: [části bez volby], pocet }`.
- **Nová verze stránky:** volby Chápu / Nechápu (a v šabloně přeskočení, texty a otevřené kapitoly) se v prohlížeči ukládají podle adresy i s verzí. Když nová verze ještě nic uloženého nemá, převezme to z nejvyšší starší verze téže stránky (od 04.11.2026; dřív se volby ztratily a kapitoly se znovu zamkly). `otevreni` pak nese `prevzato: "vNN"`.
- **porozumeni:** klepnutí na Chápu / Nechápu u části teorie (kap. 3, bod 4): `sekce` = název části, detail `{ cast, stav: "chapu" | "nechapu" | "zruseno", poradi }`. Volba se pamatuje v prohlížeči; souhrn `stranka` nese aktuální stav všech částí v `detail.porozumeni`. Po změně vyšle `sledovani.js` na `document` událost `porozumeni` a stav vrací `Sledovani.porozumeniStav()` (pro šablonu stránky s teorií).

V přehledu (záložka **Teorie a stránky**):
- nahoře **Aktuální stav porozumění** – pro každou stránku (bez ohledu na verzi) a osobu poslední volba u každé části ze všech otevření i zařízení, čas poslední změny a vývoj (např. „nechápu → chápu“), počty ✓ / ✗,
- v tabulce otevření sloupec **Chápe / nechápe** (stav při tom otevření) a štítek „nechápe: N“,
- pod částí obrázek papíru (poslední hned, starší po rozbalení) a text z „Vyzkoušej se“: poslední verze (delší než 3 řádky / 240 znaků rozbalením), štítek „látku odkryla celkem N× (doba), předtím napsáno K znaků“ nebo „bez odkrytí látky“, „dřívější verze (N)“ = poslední text z každého dalšího otevření; u stránky štítek „přeskočila kap. …“,
- v tabulce otevření štítky „✎ napsala: N“ a „přeskočila kap. …“,
- v detailu otevření seznam částí s volbou, klepnutí a texty „Vyzkoušej se“ z toho otevření.
- Zaznamenává se jen to, co napsala do „Vyzkoušej se“ (papír a text), jinak ne obsah psaní ani kam odešla.

---

## 8. Šablona stránky s teorií (`system/Sablona_material_vXX.html`, od 03.11.2026)

Popis chování je i v komentáři na začátku šablony. Šablona se v souboru **nemění** – měníš jen dva bloky (Kontrola_repo v03 porovnává zbytek se šablonou jako u testů):

- Aktuální šablona: **v03** (04.11.2026, T02: Vyzkoušej se s papírem na psaní perem, přeskočení kapitoly, převzetí z předchozí verze); v01 a v02 jsou v archivu.
- **HLAVIČKA STRÁNKY:** `<title>Název tématu – zápisky</title>` (část před „ – “ se ukáže v panelu, za ní typ a verze ze jména souboru) a `data-typ` u `sledovani.js` (`zapisky` / `material`).
- **OBSAH STRÁNKY:** obsah vkládej až **za** komentář s pravidly na začátku bloku (komentář sám obsahuje text `<div class="uvod">` – vložení podle tohoto textu skončí v komentáři a `Vzorce_v01.js` ho nevyrenderuje). Ve vzorcích piš `\lt`, `>`, ne HTML entity `&lt;` / `&gt;` (KaTeX na nich hlásí chybu).
  - `<div class="uvod"><h1>…</h1><div class="meta">…</div></div>` – ukáže se nad první kapitolou,
  - kapitoly `<section class="kapitola" data-kapitola="N. Název"><h2>N. Název</h2> … </section>` – kapitola = rozumný celek, typicky 2–6 sekcí,
  - sekce `<div class="sekce"><h3>…</h3> … <div data-porozumeni="N. Název sekce"></div></div>` – za `data-porozumeni` nic (v02),
  - poslední kapitola s opravami oproti sešitu `<section class="kapitola priloha" data-kapitola="Opravy oproti sešitu">` – bez tlačítek, nezamyká se, v časové ose je štítkem,
  - třídy: `.rule` (důležité pravidlo), `.prakticky` (příklad na konkrétních číslech), `.ex` + `<span class="lab">` (řešený příklad), `.note`, `details`, `table.tab`, `table.two`, `ul.fix`, `.siroke` (vodorovné posouvání širokého obsahu); vlastní styly stránky v `<style>` uvnitř bloku OBSAH.

Jak se stránka chová (pro odpovědi Martinovi):
- Na obrazovce je vždy jedna kapitola. Dole časová osa: kolečko = kapitola, štítek přílohy, „Σ Souhrn“, šipky ‹ ›; na konci kapitoly „‹ Zpět“, „Další kapitola ›“ a počet rozhodnutých sekcí.
- **Další kapitola se otevře, až má každá sekce všech předchozích kapitol volbu Chápu, nebo Nechápu** (Nechápu také pustí dál), **nebo když byla kapitola přeskočena**. Bez volby ukáže hlášku a posune na první nerozhodnutou sekci. Zpět se smí vždy. Druhé klepnutí volbu zruší a pozdější kapitoly se znovu zamknou (u přeskočené kapitoly ne).
- **Přeskočit bez volby** (v02): dokud kapitola nemá všechny volby, je na jejím konci „Přeskočit bez volby ›“; klepnutí ho na místě změní na „Opravdu? N částí nemá volbu. Ano, přeskočit / Ne“. Po „Ano“ se otevře další kapitola, přeskočení se pamatuje, kolečko dostane značku „›“, souhrn píše u chybějících částí „přeskočeno“ a do výsledků jde `preskoceni`. Tlačítko vidí každý (Martin uvidí přeskočení v přehledu).
- **Vyzkoušej se** (v02, papír od v03): v řádku „Rozumíš tomu? Chápu · Nechápu · Vyzkoušej se“. Klepnutí plynule (0,4 s) rozbalí pod řádkem **papír jako v testu**: okno 320 px, papír 820 × 1200 px s mřížkou, pero a myš píšou, prst papír posouvá (když papír dál nejde, posouvá stránku), dotyky pera se kvůli Scribble potlačí (Pouceni bod 20), na papíře se nic neoznačuje dlouhým stiskem. Lišta vlevo: Zpět, Smazat (potvrzení na místě „Opravdu smazat?“), 3 barvy, 3 tloušťky, Guma. Pod papírem „⌨ Psát textem“ (textové pole, 16 px písmo, aby iPad nezvětšoval stránku; ukáže se samo, když už text existuje), „Ukázat látku / Skrýt látku“ a „Hotovo“; látka sekce (vše kromě úvodního nadpisu) se zakryje **na místě** – rámeček „Látka je skrytá…“ stejné výšky, takže nic nad polem ani pod ním neposkočí. „Hotovo“ (nebo znovu „Vyzkoušej se“) pole plynule sbalí a látku odkryje; při sbalení se stránka nezkrátí (jinak by ji prohlížeč u konce stránky posunul skokem). Při přechodu na jinou kapitolu se otevřená pole zavřou. Po znovuotevření stránky je pole sbalené, tlačítko „Vyzkoušej se ✓“ ukazuje, že je něco napsané, a text je v poli. Tahy se pamatují v prohlížeči (`annschool:papir:<sekce>|<adresa>`, přebírají se do nové verze stránky); při plném úložišti se smažou nejstarší papíry jiných sekcí (do výsledků už odešly). Plátno papíru vzniká až při otevření a po zavření se uvolní (paměť iPadu). `main` má `overflow-anchor: none`, aby Chrome při rozbalení nepřesouval stránku. Psaní neovlivní Chápu / Nechápu ani zamykání. Souhrn u části ukáže „✎“. Při tisku se pole neukazuje. Omezení: pole se otevírá na místě, stránka se neposouvá – když je řádek dole u časové osy, je potřeba stránku trochu posunout.
- Barvy kolečka: bílá = neotevřená, šedá = otevřená a nerozhodnutá, zelená = všechno Chápu, červená = vše rozhodnuto a aspoň jedno Nechápu, poloprůhledná s čárkovaným okrajem = zamčená, silný okraj = aktuální.
- Souhrn: počty chápu / nechápu / nerozhodnuto a seznam všech sekcí se stavem; klepnutí skočí na sekci.
- Pamatuje se (v prohlížeči daného zařízení) poslední kapitola a otevřené kapitoly (v02 podle názvu kapitoly), přeskočené kapitoly a texty „Vyzkoušej se“; volby Chápu / Nechápu drží `sledovani.js`. Adresa `#k3` otevře kapitolu 3 (když je odemčená), `#souhrn` souhrn.
- Do přehledu výsledků jde: čas po kapitolách (oblasti), volby Chápu / Nechápu po sekcích, texty „Vyzkoušej se“ a přeskočení kapitol (kap. 7). Přehled `vysledky.html` je ukazuje od 04.11.2026.
- Tisk: všechny kapitoly pod sebou, bez ovládání.
- Změna šablony = nová verze `Sablona_material_vXX+1.html` (stará do `archiv/system-…`), jen na Martinův pokyn; stránky na starší verzi hlásí Kontrola_repo varováním.

