# Návod: tvorba HTML testu pro Ann (system/Navod_test_v29)

Podrobný postup pro chat v projektu „Ann School“. Projektové instrukce obsahují jen krátké shrnutí a odkazují sem.
Platí vždy aktuální verze souborů (nejvyšší `_vXX`). Starší verze jsou v `archiv/`.
**Před prací si vždy přečti i `system/Pouceni_vXX.md`** (chyby, které se už staly, a pravidla proti nim). Po práci projdi **kontrolu po sobě** (kap. 4) – bez ní se nic nepushuje.

---

## 0. Přehled a struktura repozitáře

- Repozitář `mjandlik/annschool`, větev `main`, GitHub Pages: https://mjandlik.github.io/annschool/

```
index.html                         rozcestník pro Ann (stálá adresa, bez _vXX), tlačítko „Výsledky“
vysledky.html                      přehled výsledků testů (stálá adresa, kap. 9)
zarizeni.html                      označení zařízení přezdívkou (stálá adresa, kap. 9)
README.md
jak-to-funguje_vXX.html            technický popis pro zájemce (verzuje se, bez sledování, nikam neodkazuje)
system/                            šablona, návody, kontroly, poučení, knihovny
  Sablona_test_vXX.html
  Sablona_material_vXX.html        šablona stránky s teorií – materiál, zápisky (kapitoly, Chápu / Nechápu, Navod_material kap. 8)
  Vzorce_vXX.js                    předrenderování vzorců KaTeX 0.16.11 ve stránce (Navod_material kap. 2)
  Navod_test_vXX.md, Navod_material_vXX.md
  Pouceni_vXX.md                   registr chyb a pravidel proti nim (číst před prací, doplňovat)
  Kontrola_testu_vXX.py            kontrola jednoho testu v Playwrightu (kap. 4)
  Kontrola_repo_vXX.py             kontrola celého repozitáře před každým pushem (kap. 4)
  Skript_vysledky_vXX.gs           skript Google tabulky s výsledky (kap. 9)
  img/                             ikony rozcestníku
  lib/                             html2canvas 1.4.1, jsPDF 2.5.2, vektory.js + vektory.css (vektorová síť, kap. 8),
                                   zaznam.js (odesílání výsledků, adresa webové aplikace, kap. 9),
                                   sledovani.js (záznam čtení teorie, Navod_material kap. 7)
matematika/ fyzika/ chemie/ …      soubory pro Ann: <tema>_<typ>_vXX.<přípona>
archiv/                            plochý: <složka>-<původní název> (soubor z rootu: root-<název>)
```

- Předmět = složka: `matematika`, `fyzika`, `chemie` (další stejně, malými písmeny, bez diakritiky).
- `tema`: stejné jako v projektu Claude (`prevody-jednotek`), malými písmeny, bez diakritiky, s pomlčkami.
- `typ`: `test`, `test-<podtyp>`, `test-opravny`, `test-opravny-<n>`, `material`, `tahak`, `pracovni-list`, `simulator`, `zapisky` (vše vlastní je HTML, Navod_material) a `skolni-material[-<podtyp>]`, `zapisky` ze sešitu (PDF, jen vstupy).
  - Víc testů k jednomu tématu: `test-<podtyp>`, např. `vektory_test-1_vXX.html` (rýsování), `vektory_test-2_vXX.html` (výpočty).
  - Rozcestník řadí typy do skupin podle začátku: `test…` → **Testy**, `zapisky…` → **Zápisky**, `skolni-material…` → **Školní materiály**, ostatní → **Výukové materiály**.
- Příklad: `fyzika/prevody-jednotek_test_v01.html` → https://mjandlik.github.io/annschool/fyzika/prevody-jednotek_test_v01.html
- Ann test otevírá na iPadu (Safari, na výšku i na šířku) a píše Apple Pencilem. Od šablony v17 píše a kreslí jen pero (Pencil, stylus na Androidu) nebo myš, prst vždy jen posouvá. Martin jí posílá odkaz přes WhatsApp. Všechno najde i v rozcestníku.

---

## 1. Doptání (před jakoukoli prací na souborech)

1. Přečti `system/Pouceni_vXX.md` a z projektu aktuální látku (`<předmět>/<téma>_vXX.md`). Z ní vycházej.
2. Co z kontextu není jasné, zeptej se jedním souhrnným dotazem (AskUserQuestion). U každého bodu navrhni výchozí volbu:
   - **Téma a okruhy:** okruhy = sekce testu (skupiny na časové ose a řádky v souhrnu); vyhodnocuje se každý příklad zvlášť.
   - **Počet příkladů a obtížnost:** výchozí 10–15, stupňovaná, 2–5 příkladů na sekci.
   - **Pevná, nebo náhodná sada:** u náhodné se v panelu objeví „Nová sada“.
   - **Papír na psaní** se neptej: od šablony v16 má každý příklad vlastní stránku s papírem pod odpovědí.
   - **Necelé výsledky:** výsledek, který se ve škole píše jako zlomek (nebo s odmocninou, mocninou), je vždy výběr z 5 možností v tom tvaru (kap. 3). Na to se neptej.
   - **Zlomky** se zobrazují s vodorovnou zlomkovou čarou (od šablony v26, kap. 3). Na to se neptej.
   - **Odmocniny** se zobrazují jako ve škole – s čarou nad celým odmocněncem (od šablony v27, kap. 3). Na to se neptej.
   - **Výběr z možností:** aspoň 5 možností (a–e). Výjimka jen tam, kde smysluplně existují 2 (skalár/vektor, doprava/doleva, ano/ne). Špatné možnosti volit podle typických chyb (opačný směr převodu, záměna jednotky, chybný řád), aby z odpovědi bylo vidět, kde Ann chybuje.
   - **Nápovědy:** výchozí ano.
   - **Časový limit:** výchozí ne.
   - **U vektorů:** velikost sítě (výchozí 14 × 12, osy bez čísel), měřítko u slovních úloh (1 dílek = 100 N), bodování řetězu (výchozí: 1 bod jen při úplné správnosti).
3. Nic nevytvářej, dokud Martin neodpoví nebo nepotvrdí návrh.

---

## 2. Příprava repozitáře

1. Připoj repozitář: `add_repo(owner="mjandlik", repo="annschool", access="push")` a naklonuj ho podle pokynů nástroje.
2. Najdi aktuální `system/Sablona_test_vXX.html` a `system/Kontrola_testu_vXX.py` (nejvyšší verze).
3. Zvol typ (`test`, `test-<podtyp>`, `test-opravny[-<n>]`) a zjisti, jestli soubor `<předmět>/<tema>_<typ>_vXX.html` existuje:
   - **existuje:** nová verze `_vXX+1`, starou přesuň `git mv` do `archiv/<předmět>-<tema>_<typ>_vXX.html`,
   - **neexistuje:** `<předmět>/<tema>_<typ>_v01.html`; nový typ doplň do `NAZVY.typy` v `index.html` (kap. 5).
4. Nová verze testu vzniká vždy z **aktuální** šablony (jen konfiguraci přeneseš ze staré verze). Rozpracovaný test pak Ann začíná znovu.

---

## 3. Vytvoření testu

1. Zkopíruj aktuální šablonu na `<předmět>/<tema>_<typ>_vXX.html`.
2. Uprav **jen** blok „KONFIGURACE TESTU“:
   - `title`: čitelný název („Převody jednotek – plocha a objem“),
   - `version`: stejné jako v názvu souboru („v01“),
   - `intro`: krátký pokyn (1 věta) odpovídající aktuální šabloně (papír je pod příkladem – ne „vpravo“),
   - `topic`: stejné jako `<tema>` v názvu souboru,
   - `timeLimitMin`, `showHints`: podle odpovědí z bodu 1 (volby `finalScratch`, `sideScratch`, `scratch` od šablony v18 nepoužívej),
   - `questions`: `{ section: "…" }` začíná sekci (skupina na časové ose), příklad je `{ before, after, answer, tol, hint }` nebo jeden z typů v kap. 3a,
   - `generate`: jen u náhodné sady (funkce vrací pole ve stejném tvaru jako `questions`, vzor je v šabloně), jinak `null`.
3. Pravidla pro obsah:
   - Zadání ve tvaru „5 m = [ ] mm“. Jednotka je za polem (`after`), nikdy ne uvnitř odpovědi.
   - `answer` je číslo v JavaScriptu (desetinná **tečka**, bez mezer): `0.32`, `30000`.
   - **Necelý výsledek = výběr z 5 možností, ne desetinné číslo.** Když vyjde necelé číslo, které se ve škole zapisuje jako zlomek (počítání se zlomky, záporným nebo racionálním exponentem, mocninami, odmocninami, např. $(-\frac23)^{-3} = -\frac{27}{8}$, $2^{-1} = \frac12$), nedávej číselné pole s poznámkou „(desetinné číslo)“. Dej `vyber` s 5 možnostmi v tvaru, jak ho píšou ve škole (zlomek v základním tvaru `−[[27/8]]`, `[[1/4]]`, případně s odmocninou), špatné možnosti podle typických chyb (nepřevrácený zlomek, opačné znaménko, umocněný jen čitatel…). Číselné pole patří jen celým číslům a desetinným číslům tam, kde je desetinné číslo už v zadání nebo kde je desetinný zápis cílem (převody jednotek, tvar a · 10ᵏ, zaokrouhlování, fyzikální výsledky s jednotkou). Výjimka jen s klíčem `desetinne: "důvod"` v příkladu. Kontrola_testu (od v08) hlídá jen část případů (zadání se zlomkem, záporným exponentem, racionálním exponentem nebo odmocninou) – u ostatních (např. $(2^5\cdot4^3):8^4 = \frac12$) to ohlídej ručně.
   - U zaokrouhlení napiš přesnost do `after` („h (na 1 des. místo)“) a nastav `tol` (např. `0.05`).
   - Mocniny deseti: `after: "· 10³ m"`, Ann doplní jen číslo před mocninou.
   - `hint`: krátké vysvětlení postupu. Ann ho může otevřít kdykoli (otevření se zaznamená) a ukáže se i po 3. špatném pokusu. U převodů jednotek vždy směr a všechny zápisy, např. „mm → m: NAHORU na větší jednotku → dělím 1000 (:1000 = :10³ = ·10⁻³) → 45 : 1000 = 0,045“, resp. „km → m: DOLŮ na menší jednotku → násobím 1000 (·1000 = ·10³) → …“.
   - Unicode znaky (m², µm, 10⁻³, ·, ≈), žádný LaTeX.
   - **Zlomky s vodorovnou čarou (od šablony v26):** v každém textu, který Ann vidí (`section`, `text`, `before`, `after`, `options`, `hint`, `reseni`), piš zlomek jako `[[čitatel/jmenovatel]]`: `[[3/4]]`, `−[[27/8]]`, `[[√5 + 1/2]]` (čitatel = vše před prvním lomítkem, nesmí lomítko obsahovat), `[[a⁵/b⁶]]`, v exponentu `a^([[2/3]])`. Stránka i PDF ho ukážou s vodorovnou čarou, do záznamu jde jako `3/4` (složený čitatel/jmenovatel v závorce). Lomítko zůstává jen u jednotek (m/s, km/h) a tam, kde Ann výsledek sama píše na klávesnici. `Kontrola_testu` (v17) zlomek s lomítkem hlásí jako chybu. Starší testy (šablona v25 a dřív) se nepředělávají, dokud o to Martin nepožádá.
   - **Odmocniny jako ve škole (od šablony v27):** odmocnina má znak √ (∛, ∜, ⁿ√) a vodorovnou čáru nad **celým** odmocněncem, závorky kolem odmocněnce se nezobrazují (Martin 03.11.2026: „a + b pod odmocninou, ne závorka“). V konfiguraci piš odmocněnce o víc znacích vždy do závorky hned za znak odmocniny: `√(a + b)`, `√(36 · 2)`, `∛(−[[27/8]])`, `⁴√(a³)`, `ⁿ√(aᵏ)`, `√(2√2)`; jedno číslo nebo písmeno bez závorky: `√12`, `2√3`, `√0,0036`, `√a`. Závorka hned za √ jen ohraničuje odmocněnce – na stránce ani v PDF se neukáže, čára sahá přesně přes ni. Zlomek pod odmocninou `√([[50/2]])` (znak odmocniny se pak zvětší), odmocnina ve zlomku `[[√50/√2]]`, odmocnina v exponentu `a^(√2)`. Závorku, která má být vidět, dej vně odmocniny: `(√(2√2))²`. Do záznamu jde text tak, jak je v konfiguraci (`√(a + b)`). `Kontrola_testu` (v18) hlásí jako chybu odmocninu, která se nevykreslila s čarou.
   - **Vzhled odmocniny (od šablony v28):** znak odmocniny se kreslí (SVG) přes celou výšku odmocněnce a plynule navazuje na čáru nad ním, odmocnitel (∛, ∜, ⁴√, ⁿ√) je malý vlevo v háčku – stejně jako v zápiscích (KaTeX) a ve škole. V27 měla znak jako písmo a čáru odtrženou nad ním (Martin 03.11.2026: „vypadají špatně“, Pouceni bod 29). Zápis v konfiguraci se nemění; vzhled ověř snímkem i v PDF.
   - Výběr z možností: aspoň 5 možností (výjimky v kap. 1), správná možnost na různých místech. Povolená dvojice/trojice (ano/ne, skalár/vektor, doprava/doleva, <, =, >, …) se pozná sama; jiná výjimka jen s klíčem `vyjimka5: "důvod"` v příkladu.
   - **Každá špatná možnost musí být opravdu špatně.** Ke každé si poznamenej, jakou typickou chybu představuje a proč neplatí (výpočet, protipříklad). Pozor na tvrzení „právě když“, „vždy“, „každé“ – často existuje víc rovnocenných formulací (viz Pouceni, bod 1).
   - Úroveň 1. ročníku gymnázia. Vše musí být fyzikálně a matematicky správně.
4. Vzhled, panel, kreslení, časovou osu, vyhodnocení, záznam ani PDF v testu **neměň**. Úpravy šablony dělej jen na Martinův výslovný pokyn (nová verze šablony, stará do `archiv/system-…`). Nová systémová tlačítka patří do `<div class="panel-actions">`.
5. Stránka musí ležet přesně o jednu složku pod rootem, protože knihovny načítá z `../system/lib/`.

---

## 3a. Typy příkladů (od šablony v13)

Příklad je správně, jen když jsou správně **všechny** jeho části (pole, výběr, kresba). Body (v16): napoprvé 1, napodruhé ½, napotřetí nebo vůbec 0. V každém textu (`text`, `before`, `after`, `hint`, `options`) znamená `{F}` písmeno se šipkou nad ním (vektor), např. `"{N} = {k} + {m}"`. Šipka je z CSS a html2canvas ji přenese i do PDF. Velikost se píše bez šipky: `F = 3 N` nebo `|{F}| = 3 N`.

| Typ | Konfigurace | Vyhodnocení |
|---|---|---|
| číslo (bez `type`) | `{ before, after, answer, tol, hint, text }` | `text` (nepovinný) = zadání nad řádkem s polem |
| `vyber` | `{ type: "vyber", text, options: ["skalár", "vektor"], answer: 1 }` | klepnutí na možnost, `answer` = index |
| `pole` | `{ type: "pole", text, fields: [ { before, after, answer, tol }, { options: [...], answer } ] }` | víc čísel a výběrů v jednom příkladu (složky Δx a Δy, rozmezí, velikost + orientace) |
| `rysuj` | `{ type: "rysuj", text, dane, sit, nazev: "v", answer: { dx, dy }, start: { x, y } }` | Ann nakreslí jeden vektor kamkoli, porovnají se složky Δx, Δy |
| `retez` | `{ type: "retez", text, dane, sit, retez: [ { nazev: "A", dx, dy }, … ], vysledna: "R", start }` | šipka za šipku: složky každého vektoru, navázání, výslednice od začátku prvního ke konci posledního |
| `dukaz` | `{ type: "dukaz", text, hint, reseni: ["řádek 1", …] }` | neboduje se; Ann píše na papír, „Vyhodnotit“ ukáže vzorové řešení (modrá na časové ose) |

Společné pro příklady se sítí:

- **Síť** se vytvoří u `rysuj`, `retez` a u každého příkladu s `sit` nebo `dane`. Výchozí `sit`: `{ xmin: -7, xmax: 7, ymin: -6, ymax: 6, osy: true, cisla: false }` (14 × 12 dílků, osy bez čísel). Šířka sítě je nejvýš 560 px (dílek 38 px).
- **`dane`**: zadané vektory `[{ nazev: "F", x1, y1, x2, y2, barva, stranaNazvu }]`. Nejdou chytit ani posunout. Barvy postupně modrá, černá, šedá.
- **`pole` se sítí** = příklad typu „zapiš složky narýsovaného vektoru“. Pole jsou pod sítí.
- **Složky se znaménkem:** `answer: { dx: 5, dy: -2 }` = 5 doprava, 2 dolů. U polí Δx, Δy dej do `after` „(doleva = záporné)“, „(dolů = záporné)“.
- **`start`** (nepovinný): kam se nakreslí správný vektor, když Ann nic nenakreslila. Jinak se kreslí od začátku jejího vektoru. Vždy se posune, aby se vešel do sítě.
- **Měřítko** jiné než 1 dílek = 1 N napiš do textu (`1 dílek = 100 N`) a `answer` zadej v dílcích.

Ovládání sítě v testu:

- Nad sítí je řádek „Kreslím:“ s tlačítky vektorů (u `rysuj` jeden, u `retez` všechny + výslednice) a „Smazat“. V PDF se nezobrazí.
- U `retez` jde chytit jen právě vybraný vektor. Ostatní jsou „zamčené“, aby šlo začít kreslit přesně na konci předchozího (jinak by Pencil chytil jeho koncový bod). Po nakreslení se výběr sám přepne na další vektor.
- Barvy: Annin vektor u `rysuj` červeně, u `retez` modrá, červená, černá, růžová, výslednice fialově. Správná odpověď u chyby zeleně čárkovaně.
- **Vyhodnotit:** po 1. a 2. špatném pokusu jen „Špatně – zkus to znovu“, síť zůstává odemčená a Ann kresbu opraví. Po správné odpovědi nebo po 3. špatném pokusu se síť zamkne (`sit.o.upravy = false`, `sit.kresli = null`); u chyby se pak ukáže správný vektor (řetěz) čárkovaně a text, co je špatně („{B} nezačíná na konci {A}“, „{R} má být …“).
- U čísel se zaokrouhlením (`tol`) se správný výsledek ukáže zaokrouhlený (`tol: 0.05` → 1 des. místo). Záporná čísla se píšou se znakem −.

Vzor: `fyzika/vektory_test-1_vXX.html` (rýsování) a `fyzika/vektory_test-2_vXX.html` (výpočty), ukázka všech typů je v konfiguraci šablony.

Pravidla pro obsah vektorových příkladů:

- Zadané vektory aspoň 2 dílky dlouhé, jen celé složky, musí se vejít do sítě i s výsledkem.
- Vektory v zadání (`dane`) dej tam, kde Ann nebude kreslit výsledek (typicky do levé dolní části), a `start` do volného místa.
- Nepoužívat goniometrii (úhel se jen měří úhloměrem). Směr = přímka, orientace = kam míří šipka.
- Odčítání vždy vysvětlovat jako přičtení opačného vektoru, neznámý vektor jako „vyjádři si, co potřebuješ“ (`{k} = {N} − {m}`).

---

## 4. Kontrola po sobě (povinná, před každým pushem)

Cíl: aby se chyby z `system/Pouceni_vXX.md` neopakovaly. Bez všech bodů níže se nic nepushuje.

1. **Nezávislý přepočet.** Výsledky všech příkladů přepočítej v Pythonu **ze zadání** (ne z `answer`). U testu s víc než ~10 příklady nebo s výběry to udělej přes samostatného agenta (Agent), který test nevytvářel a dostane jen soubor a tento bod: přepočítat každou odpověď, ověřit nápovědy a `tol`, **ke každé špatné možnosti ve výběru uvést, proč je špatně**, a najít otázky, kde je správná víc než jedna možnost. Totéž platí pro každou navrženou opravu.
2. **Kontrola testu:** z rootu repozitáře `python3 system/Kontrola_testu_vXX.py <předmět>/<tema>_<typ>_vXX.html` (Playwright: `pip install playwright --break-system-packages && python3 -m playwright install chromium`). Musí skončit „Vše v pořádku.“
3. **Kontrola repozitáře:** `python3 system/Kontrola_repo_vXX.py`. Musí skončit „Repozitář bez chyb.“ Nová varování, která jsi způsobil, odstraň.
4. **Soulad dokumentace:** když se měnilo cokoli v `system/`, `index.html`, `vysledky.html` nebo `zarizeni.html`, vyhledej (`grep`) v návodech, `README.md` a v instrukcích projektu místa, která to popisují, a uprav je. Změna instrukcí = celý nový text pro Martina.
5. **Paměť projektu:** po `project_write` poznámku znovu přečti (`project_read`) a zkontroluj: počet příkladů = konfigurace testu, každý příklad má všech 5 polí (Zadání, Nápovědy, Řešení, Výsledek, Poznámka), výsledky čitelně a s jednotkami (zlomek `6/13`), odkazy vedou na existující aktuální soubory (porovnej se seznamem souborů repozitáře), žádné řádky z jiného tématu.
6. **Poučení:** prošel jsi body `Pouceni_vXX.md`, které se tvé práce týkají. Novou chybu (i nalezenou při kontrole) zapiš do nové verze `Pouceni` a, když to jde, doplň automatickou kontrolu.
7. **Kontrolní záznam pro Martina:** na konci odpovědi jeden blok „Kontrola“: výsledek kroků 1–3 (např. „přepočet 24/24, Kontrola_testu: Vše v pořádku, Kontrola_repo: bez chyb, 2 varování (starší testy)“) a co se ověřit nepodařilo.

Co kontrola testu v18 dělá (šablona v17 až v27; verzi šablony pozná z historie v hlavičce testu; náhled papíru v21 nekontroluje – ten se ověřuje ručně podle kap. 9):
- iPad na výšku 820 × 1180 i na šířku 1180 × 820, `device_scale_factor` 2: žádné chyby v konzoli, nic se neposouvá vodorovně, papír aspoň 260 px, časová osa celá vidět,
- prázdná odpověď se nepočítá jako pokus,
- správné odpovědi všech typů → zelená (čísla s desetinnou čárkou a mezerami, výběr klepnutím, rýsování a řetěz kreslením myší přes síť), důkaz → modrá a vzorové řešení,
- první příklad každého typu: špatně → šedá, správné řešení se neukáže, síť zůstane odemčená; pak správně → oranžová,
- druhý příklad téhož typu: 3× špatně → červená, zamčeno, správné řešení vidět (u sítě čárkovaně),
- papír: tah zůstane u příkladu po přechodu jinam i po otočení iPadu,
- záznam: start, vyhodnoceni (počet = počet pokusů, s obrázkem papíru), napoveda, odchod, souhrn (adresa webové aplikace je v kontrole podvržená, nic se nikam neodesílá),
- skóre v souhrnu, PDF (od v18 s tématem i typem v názvu), verze a téma v názvu souboru,
- obnovení po zavření: znovuotevření (dialog „Pokračovat?“) vrátí stavy příkladů i papír, zapíše `pokracovani` a žádný nový `start`,
- výběry: žádná prázdná ani dvojitá možnost, index v rozsahu, aspoň 5 možností (od v18 chyba, u v17 varování),
- (v08, šablona v18+) necelý výsledek v číselném poli, když zadání obsahuje zlomek, záporný či racionální exponent nebo odmocninu a žádné desetinné číslo (kap. 3; výjimka `desetinne: "důvod"`),
- (v09, šablona v19+) tlačítka papíru jsou vlevo nahoře, na výšku i na šířku (Pouceni bod 15); (v10, šablona v20+) lišta má jen Zpět a Smazat.
- (v11, šablona v21+) start posílá zadání a správné odpovědi všech příkladů, Zpět zvýší verzi papíru (Pouceni bod 16), náhled papíru se odešle jako událost `nahled` s obrázkem.
- (v12, šablona v22+) dlouhý stisk nic neoznačuje: stránka má `user-select: none`, pole odpovědí `text`, `selectstart` a místní nabídka mimo pole jsou potlačené, dvojklik na lištu papíru nic neoznačí (Pouceni bod 17).
- (v13, šablona v23+) přechod na jiný příklad pošle `presun`, `pozice` má příklad, čas v návštěvě a `aktivni` (po skrytí stránky `false`), start posílá i text nápovědy.
- (v14, šablona v24+) otevřený a přeskočený příklad zůstane bílý, po tahu na papír je šedý.
- (v17, šablona v26+) zlomky: text, který Ann vidí, nemá zlomek s lomítkem mimo `[[…]]` (jednotky m/s, km/h nevadí), `[[3/4]]` se vykreslí jako zlomek a `plain()` ho pro záznam převede na `3/4` (Pouceni bod 22).
- (v18, šablona v27+) odmocniny: každé √, ∛, ∜ v textech, které Ann vidí, je vykreslené s čarou nad odmocněncem (`.odm`); vzorové odmocniny (√(a + b), ∛(−[[27/8]]), ⁴√(a³), 2√3, √0,25, ve zlomku, vnořená) se vykreslí správně a `plain()` zápis pro záznam nemění (Pouceni bod 24).
- (v20, šablona v28+) odmocniny: znak odmocniny (SVG) sahá přes celou výšku odmocněnce, odmocnitel se vykreslí jako malé číslo (Pouceni bod 29).
- (v15, šablona v25+) dotyk pera (`touchType` „stylus“) na papíře a na sítích má potlačené výchozí chování (`touchstart`, `touchmove`, `touchend`), dotyk prstu ne (Pouceni bod 20). Jestli to opravdu zabrání Scribble, ověří jen iPad (ručně).
- (v16, všechny šablony, knihovna `zaznam.js`) plné úložiště (Pouceni bod 21): s podvrženým limitem úložiště se z uložených rozpracovaných testů smaže nejdřív dokončený, rozpracovaný zůstane; když místo nejde uvolnit, obrázek papíru se přesto odešle (fronta v paměti), do úložiště jde fronta bez obrázku; přijde událost `uloziste`, v konzoli nejsou chyby.
- **Neumí** poznat, že špatná možnost je ve skutečnosti také správná – to je bod 1.

Co kontrola repozitáře dělá: struktura a názvy, jedna verze mimo archiv, archiv, testy na šabloně (shoda kódu mimo konfiguraci), verze a téma, výběry, zastaralé texty, verze zobrazená na stránkách s teorií, stránky s teorií na šabloně (shoda kódu mimo bloky HLAVIČKA a OBSAH, kapitoly a sekce s Chápu / Nechápu, nevyrenderované vzorce, pravidlo bez příkladu na číslech – v03), sledování (`zaznam.js`, `sledovani.js`, `data-typ`), `ENDPOINT`, názvy v `NAZVY`, vlastní materiály jen HTML, jméno v souborech pro Ann, místní odkazy, velké soubory. Popis je v hlavičce skriptu.

U testů se sítí navíc ověř v Playwrightu přesun bodu a posun celého vektoru (kap. 8 „Testy v Playwrightu“).

---

## 5. Rozcestník

- `index.html` načítá seznam souborů automaticky z GitHubu a ukazuje vždy nejvyšší verzi každého tématu a typu.
- Rozcestník: předmět → téma → skupiny **Výukové materiály**, **Zápisky**, **Školní materiály** a **Testy** (podle začátku typu, kap. 0).
- U **nového tématu** (nebo předmětu) doplň český název do `NAZVY.temata` (`NAZVY.predmety`) v `index.html`, např. `"linearni-rovnice": "Lineární rovnice"`. Bez toho se zobrazí název odvozený z `tema` (bez diakritiky).
- U **nového typu** (např. `test-rysovani`, `test-opravny-2`) doplň název do `NAZVY.typy`, např. `"test-rysovani": "Test – rýsování"`. Chybějící název najde `Kontrola_repo`.
- `index.html` a `README.md` mají stálé adresy, proto se neverzují v názvu. Historie je v gitu.

---

## 6. Zveřejnění a předání

1. Až po kontrole po sobě (kap. 4): `git add -A`, commit (česky, co je nového) a `git push origin HEAD:main`.
2. GitHub Pages zveřejní stránku zhruba do minuty. Není potřeba čekat.
3. Martinovi napiš krátce:
   - odkaz `https://mjandlik.github.io/annschool/<předmět>/<tema>_<typ>_vXX.html`,
   - počet sekcí a příkladů,
   - archivovanou verzi (pokud nějaká je).
   - Rozcestník: https://mjandlik.github.io/annschool/
   - blok „Kontrola“ (kap. 4, bod 7).
4. Příklady z testu (všech 5 polí) ulož do projektu Claude jako novou verzi `<předmět>/<téma>_vXX.md` podle pravidel projektu a zkontroluj ji (kap. 4, bod 5).
5. Nový test se do přehledu výsledků (`vysledky.html`) přidá sám po prvním odeslaném výsledku. Nic dalšího se nenastavuje.

---

## 7. Jak stránka funguje (pro odpovědi na Martinovy dotazy)

- **Horní panel (pevný):** název · verze, barvy (černá, modrá, červená, zelená, růžová), tloušťka pera (tenká, střední, silná), Pero, Guma, Nová sada (jen u náhodné sady), PDF. Režim „Prst“ od v17 není – prst vždy posouvá. Tahy se vyhlazují a reagují na tlak Pencilu.
- **Stránka příkladu** (na výšku i na šířku stejně, odshora): hlavička „Příklad N / M · sekce · stav“ → zadání → odpověď (pole, výběr, síť) → Vyhodnotit, Nápověda → **papír**. Předchozí / další příklad: šipky ‹ › vpravo v časové ose. Papír vyplní zbytek obrazovky (aspoň 260 px); když je zadání vysoké (síť), posouvá se celá plocha.
- **Papír:** každý příklad má vlastní, pevně velký papír 1150 × 1600 px (šířka iPadu na šířku, výška asi 2 obrazovky). Pero (Pencil, stylus) a myš píšou, prst papír posouvá (na výšku i do strany). Posun prstem počítá šablona sama (`touch-action: none`), protože stylus na Androidu jinak posouval papír místo psaní. Totéž platí pro vektorové sítě (vektory.js). Lišta papíru: Zpět, Smazat – od v19 vlevo nahoře (vpravo překážela pravákovi), text „Místo na výpočty…“ za nimi; tlačítko „↖ Na začátek“ od v20 není (v17–v19 ho mají). Tahy se ukládají jako křivky, po otočení iPadu se nic neztratí ani nezmenší. Od v21 se papír průběžně posílá do přehledu jako náhled (kap. 9) a Zpět / Smazat se počítají jako změna papíru (u v17–v20 se po nich obrázek u dalšího pokusu neposlal znovu, Pouceni bod 16). Od v22 se na stránce nic neoznačuje dlouhým stiskem (dlaň, prst, pero) a neotevře se místní nabídka; označovat a psát jde jen v polích odpovědí (v17–v21 občas označily lištu papíru nebo zadání, Pouceni bod 17). Od v25 si papír dotyky pera bere sám (`touchstart`, `touchmove`, `touchend` s `touchType === "stylus"` → `preventDefault`) – se zapnutým Scribble na iPadu se v v17–v24 rychlý tah hned po předchozím ztratil (H bez vodorovné čárky, Pouceni bod 20). Prst a Scribble v polích odpovědí se nemění.
- **Pokusy:** nejvýš 3. Prázdná odpověď se nepočítá („Nejdřív doplň odpověď“). Po 1. a 2. špatném pokusu jen „Špatně – zkus to znovu“ (správný výsledek se neukáže). Po správné odpovědi nebo 3. špatném pokusu se příklad zamkne; u chyby se ukáže správný výsledek a nápověda. Vyhodnocený příklad jde znovu otevřít jen k prohlížení.
- **Časová osa (pevná dole, zalomí se):** kolečko s číslem (28 px) pro každý příklad, vpravo šipky ‹ › na předchozí / další, sekce oddělené názvem, nakonec „Σ Souhrn“. Klepnutí = skok na příklad. Barvy: bílá = nezačato (od v24 i otevřený a přeskočený příklad), šedá = rozpracováno (od v24 jen po otevření nápovědy, tahu na papír, vyplnění odpovědi nebo pokusu; v17–v23 každý otevřený příklad), zelená = napoprvé, oranžová = napodruhé, červená = napotřetí nebo vůbec, modrá = důkaz (řešení zobrazeno). Aktuální příklad má silnější černý okraj.
- **Souhrn:** body (zelená 1, oranžová ½, červená 0), tabulka sekcí s barevnými kolečky, stav odeslání výsledků, ID zařízení a přezdívka.
- **Odpovědi:** klávesnice. Čárka i tečka jsou v pořádku, mezery nevadí. Enter = další pole, v posledním poli Vyhodnotit. Vektory se kreslí Pencilem do sítě (kap. 3a), řádek „Kreslím:“ určuje, který vektor se kreslí.
- **PDF:** souhrn + každý příklad (zadání, odpověď, výsledek) a pod ním jeho popsaný papír. Jedno klepnutí vytvoří PDF a otevře sdílení na iPadu. Kdyby ho iPad zablokoval, tlačítko zezelená na „Uložit PDF“ a stačí klepnout znovu. Název: `Test_<tema>_<typ>_vXX_<datum>_NN.pdf` (od v18; v17: `Test_<tema>_vXX_<datum>_NN.pdf`).
- **Výsledky se odesílají** do Google tabulky (kap. 9).
- **Pokračování po zavření (v17):** stav testu (odpovědi, kresby na papíře, vektory v sítích, pokusy, barvy, časy, otevřené nápovědy, aktuální příklad, u náhodné sady i vygenerované příklady) se průběžně ukládá v prohlížeči (localStorage, klíč `annschool:test:<adresa>`). Po znovuotevření stejné verze testu se zeptá „Pokračovat?“ – OK = pokračuje ve stejné relaci (událost `pokracovani`), Zrušit = začne znovu. V souhrnu je tlačítko „Začít test znovu“, „Nová sada“ také začne znovu. Nová verze testu začíná vždy od začátku. V anonymním okně nebo po smazání dat Safari se stav neuloží.

---

## 8. Knihovna vektory.js (vektorová síť)

Sdílená knihovna `system/lib/vektory.js` + `system/lib/vektory.css`. Používá ji simulátor `fyzika/vektory_simulator_vXX.html` a od šablony v13 i testy (typy `rysuj`, `retez`, sítě u `pole`, kap. 3a). Úpravy knihovny jen na Martinův výslovný pokyn; změna musí zůstat zpětně kompatibilní se simulátorem.

### Načtení (stránka o jednu složku pod rootem)

```html
<link rel="stylesheet" href="../system/lib/vektory.css">
<script src="../system/lib/vektory.js"></script>
```

### Síť

```js
const sit = new Vektory.Sit(document.getElementById("misto"), {
  xmin: -10, xmax: 10, ymin: -10, ymax: 10,  // rozsah v dílcích (čtvercová síť, výška se dopočítá ze šířky)
  osy: true, cisla: true, popisOs: true,     // osy x, y, čísla na osách, písmena x a y
  upravy: true,                              // body jdou vybírat a přesouvat (false = jen zobrazení)
  posun: true,                               // celý vektor jde posunout za kroužek uprostřed
  onChange: (sit, info) => { … }             // při každé změně, i během táhnutí; info.typ: kresli | nakreslen | bod | posun | vyber | smazan
});
```

- Měřítko je 1 dílek = 1 N (jednotky jsou na stránce, knihovna počítá v dílcích).
- Kreslí se ve vysokém rozlišení (devicePixelRatio), překresluje se přes requestAnimationFrame, šířka se přizpůsobí kontejneru (ResizeObserver).
- `sit.nastavRozsah(xmin, xmax, ymin, ymax)` – změna rozsahu.

### Vektory

```js
sit.pridej({ id: "a", nazev: "a", barva: "#2b5cab", x1: 1, y1: 1, x2: 5, y2: 4,
  upravitelny: true,          // false = nejde chytit
  popisBodu: ["A", "B"],      // popisky počátečního a koncového bodu (nebo null)
  souradnice: true,           // připsat souřadnice: A[1; 1]
  tloustka: 2.6, carkovane: false, tucne: false, stranaNazvu: 1 });   // stranaNazvu −1 = název na druhé straně
sit.vektor("a"); sit.vektory;               // čtení (x1, y1, x2, y2 jsou celá čísla = uzly sítě)
sit.nastav("a", x1, y1, x2, y2); sit.odeber("a"); sit.vymaz();
sit.kresli = { id: "b", nazev: "b", barva: "#b3261e" };   // Pencil/myš táhnutím v prázdném místě nakreslí b (null = kreslení vypnuto)
sit.pomocne = [{ x1, y1, x2, y2, barva, carkovane: true, sipka: false, nazev: "OB" }];   // čáry/vektory bez ovládání
sit.body = [{ x, y, popis: "O", barva, dx: -12, dy: 12 }];                               // popsané body
sit.prekresli();                            // po ruční změně pomocne / body
```

- Barvy jako v šabloně testu: černá `#1d1d1b`, modrá `#2b5cab`, červená `#b3261e`, zelená `#1f8a3c`. Výslednice v simulátoru: fialová `#7a3db8`.
- Název vektoru se kreslí se šipkou nad písmeny; úvodní „−“ (`"−b"`) zůstane před šipkou.

### Ovládání (iPad)

- Pero (Pencil, stylus) a myš ovládají síť, prst posouvá stránku (ručně přes nejbližší posouvatelný kontejner, `touch-action: none` – funguje i na Androidu). `Vektory.nastavPrst(true)` by zapnulo ovládání prstem; testy ani simulátor (od v05) ho nepoužívají.
- Body se přichytávají k uzlům sítě. Terč bodu má poloměr 18 px, kroužek uprostřed 14 px.
- Bod táhnutím přesuneš rovnou. Klepnutím na bod ho vybereš (zvýrazní se), dalším klepnutím na uzel ho tam přesuneš.
- Za kroužek uprostřed posuneš celý vektor, velikost ani směr se nemění. Nulový vektor (oba body v jednom uzlu) nejde vytvořit.

### Výpočty (statické funkce)

| Funkce | Výsledek |
|---|---|
| `Vektory.slozky(v)` | `{ dx, dy }` |
| `Vektory.velikost(dx, dy)` | √(dx² + dy²) |
| `Vektory.soucet([{dx,dy}, …])` | součet po složkách |
| `Vektory.opacny({dx,dy})` | opačný vektor |
| `Vektory.popisSlozek(dx, dy)` | „4 doprava, 3 nahoru“ |
| `Vektory.odmocnina(n2)` | `{ text: "√34 ≈ 5,8", hodnota, presne }` (celé výsledky „√25 = 5“) |
| `Vektory.fmt(n, des)` | české číslo: desetinná čárka, znak − |
| `Vektory.zav(n)` | záporné číslo v závorce: (−3) |
| `Vektory.uhel(dx, dy)` | úhel s vodorovnou 0–90° (jen ukázka, Ann ho zatím nepočítá) |

### Události `onChange(sit, info)`

Volá se při každé změně, i během táhnutí (živý přepočet). `info.typ`:

- `kresli`: vektor se právě kreslí (každý posun o uzel),
- `nakreslen`: konec kreslení,
- `bod`: přesun bodu,
- `posun`: posun celého vektoru,
- `vyber`: klepnutí na bod (výběr nebo zrušení výběru),
- `smazan`: `sit.odeber(id)`,
- `nastaven`: `sit.nastav(…)`.

`info.id` je id vektoru. Výběr bodu je v `sit.vybrany = { id, bod: 1 | 2 } | null`.

### Vložení do šablony testu

Od šablony v13 je všechno níže v šabloně hotové (body 1–6). Popis zůstává pro úpravy šablony.

1. Do `<head>` šablony za skripty pro PDF:
   ```html
   <link rel="stylesheet" href="../system/lib/vektory.css">
   <script src="../system/lib/vektory.js"></script>
   ```
2. Síť patří do vlastního `<div>` uvnitř stránky příkladu (`.qpage`, v16). Šířka se bere z rodiče (nejvýš 560 px) a výška se dopočítá (čtvercové dílky), proto rodič musí mít šířku.
3. (v17) Režim „Prst“ v šabloně není: prst všude jen posouvá, pero kreslí.
4. **Vyhodnocení „narýsuj vektor“:** porovnej `Vektory.slozky(sit.vektor(id))` s očekávaným `{dx, dy}`. Poloha počátku je libovolná (vektor posunutý jinam je tentýž vektor). Chybějící vektor = chyba.
5. **Zobrazení správného vektoru u chyby:** vlož ho do `sit.pomocne` čárkovaně (`carkovane: true`, šedá nebo zelená), nejlépe se stejným počátkem jako Annin vektor. Když Ann nic nenakreslila, dej ho do volného místa. Pak `sit.prekresli()`.
6. **Po vyhodnocení** nastav `sit.o.upravy = false` a `sit.kresli = null`, aby se odpověď neměnila. (v16: zamyká se až po správné odpovědi nebo 3. pokusu; mezi pokusy zůstává odemčená a `pomocne` prázdné.) `sit.vymaz()` smaže i `pomocne`, `body` a `oblouky`.
7. **PDF:** html2canvas (šablona) obsah plátna sítě zachytí. Ověřeno 12. 10. 2026 na `#sit2` v simulátoru: vektory jsou v obrázku vidět.
8. **Vlastní kreslení navíc** (popisky, značky) bez změny knihovny: obal `sit.kresliHned`:
   ```js
   const puv = sit.kresliHned.bind(sit);
   sit.kresliHned = () => { puv(); /* kresli přes sit.ctx, sit.px(x), sit.py(y), sit.stitek(text, X, Y, barva) */ };
   ```
   Takhle simulátor kreslí popisky Δx, Δy a značku pravého úhlu.

### Velikost sítě na iPadu

- Dílek by měl mít aspoň **22 px** (čísla na osách se pak píšou u každého dílku). Při menších dílcích se čísla řídnou po 2 nebo 5 a body se hůř chytají.
- Šířka obsahu na iPadu na výšku je asi 790 px, sloupec vedle textu asi 420 px. Při 420 px vychází 20 dílků po 19 px, to je hranice.
- Pro test proto doporučuji síť **12 × 12 až 16 × 12** dílků, nebo širší síť přes celou šířku.
- Krátké vektory (1 dílek) mají body blízko sebe. Terče se překrývají a knihovna dává přednost vybranému vektoru, ale zadání raději stav na vektory dlouhé aspoň 2 dílky.

### Na co jsem narazil a jak je to vyřešené (pro další úpravy)

- **Zarovnání textu „prosakovalo“** (canvas drží `textAlign` mezi voláními): popisky bodů se kreslily posunuté doleva. Oprava: kreslení os je v `save()/restore()` a `stitek()` nastavuje `textAlign = "left"`. Při úpravách knihovny vždy ohraničit změny stavu plátna.
- **Posun celého vektoru** se nejdřív počítal ze zaokrouhleného uzlu pod prstem. Při uchopení přesně mezi uzly (střed vektoru je často v půlce dílku) pak vektor skočil o 2 dílky místo o 1. Teď se posun počítá ze vzdálenosti od místa uchopení: `Math.round((cx − x0) / cell)`.
- **Popisky u okraje:** `stitek()` drží text uvnitř plátna. Dlouhý popisek u okraje proto „sklouzne“ zpět přes čáru. Popisky na síti dělej krátké („Δx = 5“, celý výpočet patří do textu vedle) a před kreslením zkontroluj, jestli se vejdou (`sit.px(x) + šířka + 16 ≤ sit.W`), jinak je dej na druhou stranu.
- **Pero × prst:** reaguje se jen na `pointerType` `pen` a `mouse`. Dřív se Pencil blokoval přes `touchType === "stylus"` (jen Safari) – na Androidu pak stylus posouval stránku. Od 01.11.2026 má plátno `touch-action: none` a posun prstem se počítá ručně (`pointerType === "touch"` → `scrollLeft/scrollTop` nejbližšího posouvatelného rodiče). Stejně to dělá papír v šabloně v17. Dotyky pera (`touchType === "stylus"`) mají na plátně potlačené výchozí chování, aby je Safari nebralo pro Scribble nebo dvojité klepnutí (01.11.2026, Pouceni bod 20; papír v šabloně od v25). Platí pro všechny testy i simulátor, protože knihovna se neverzuje.
- **Ostrost:** plátno má rozměr `CSS × devicePixelRatio` a kreslí se s `setTransform(dpr, …)`. Velikost se přepočítá přes ResizeObserver (otočení iPadu) a všechno se překreslí. Překreslení jde vždy přes `requestAnimationFrame` (`sit.prekresli()`), nikdy ne přímo v každém `pointermove`.
- **Šipka nad písmenem:** kombinační znak U+20D7 (a⃗) se v Safari i Chrome vykresluje nespolehlivě (posunutý, malý). V HTML textu simulátoru je proto `<span class="vec">a</span>` se šipkou přes CSS (SVG na pozadí). V plátně kreslí šipku nad názvem knihovna sama. V `.md` a v zadáních testu (čistý text) lze a⃗ použít, v rychlém textu stačí „vektor a“.
- **Testy v Playwrightu:**
  - souřadnice bodu na obrazovce: `sit.cv.getBoundingClientRect()` + `sit.px(x)`, `sit.py(y)` (proměnné `const` ze stránky jsou v `page.evaluate` dostupné),
  - táhnutí myší po krocích: `mouse.move` v 10 krocích, jinak se nemusí poznat pohyb nad 6 px,
  - prvky, které stránka při změně překresluje (seznamy, zaškrtávátka), hledej přes `page.locator(...).nth(i)`, ne přes uložený ElementHandle (po překreslení je odpojený),
  - viewport iPadu: 820 × 1180 (na výšku) a 1180 × 820 (na šířku), `device_scale_factor=2`.

### Co nefunguje nebo se nedoporučuje

- Necelé souřadnice: body jsou vždy v uzlech sítě. Zadání musí mít celé složky.
- Měřítko jiné než 1 dílek = 1 N řeší jen text stránky (např. 1 dílek = 100 N u slovní úlohy). Knihovna počítá v dílcích, přepočet dělej v testu: velikost × měřítko.
- Úhel (`Vektory.uhel`) je jen ukázka, nevyhodnocovat. Goniometrie v 1. ročníku zatím není.
- Ukládání do prohlížeče (localStorage) knihovna vektory.js nepoužívá. Testy v něm drží jen ID zařízení, přezdívku a frontu neodeslaných výsledků (zaznam.js).
- Hodně sítí na jedné stránce je v pořádku (každá má své plátno). Kvůli PDF a výkonu ale nejvýš asi 15 sítí na test.

### Použití v testu

Typy `rysuj`, `retez`, `pole` a `vyber` jsou od šablony v13 hotové, popis konfigurace je v kap. 3a. Knihovna se pro ně neměnila: šablona jen řídí `upravitelny` (u řetězu jde chytit jen vybraný vektor), `kresli`, `pomocne` a `o.upravy`.

- **Šipka nad písmenem v HTML** (`{F}` v textu testu, třída `.vec`): v šabloně je z CSS čáry a trojúhelníku (rámečky), protože SVG obrázek na pozadí pseudoprvku (`.vec` v simulátoru) html2canvas do PDF nepřenese. Ověřeno 12. 10. 2026. Kdyby se šipka přidávala do PDF jinde (např. simulátor), použij stejný zápis.


---

## 9. Záznam výsledků a přehled (od šablony v16)

### Jak to funguje

```
test (iPad, Safari) ──POST──▶ webová aplikace Google Apps Script ──▶ Google tabulka (listy Udalosti, Zarizeni)
   system/lib/zaznam.js          system/Skript_vysledky_vXX.gs         + obrázky papíru ve složce na Disku
vysledky.html ──GET ?akce=data──▶ stejná webová aplikace (čtení)
```

- GitHub Pages neumí ukládat, proto výsledky jdou do Google tabulky Martina. V kódu není žádný klíč; adresa webové aplikace je veřejná (nejhorší zneužití = nesmyslné řádky v tabulce).
- **Adresa webové aplikace** je jen na jednom místě: `system/lib/zaznam.js`, konstanta `ENDPOINT` (…/exec). Testy, přehled i označení zařízení ji berou odtud. Když je prázdná, testy nic neodesílají (souhrn ukáže „Výsledky se neodesílají“). Změna adresy = jen úprava `zaznam.js` (bez nových verzí testů).
- **Fronta:** když odeslání selže (offline), události čekají v prohlížeči a odešlou se později, i při příštím otevření kteréhokoli testu. Duplicity (stejné `id`) skript zahodí.
- **Plné úložiště (`zaznam.js`, 01.11.2026, Pouceni bod 21):** rozpracované testy se ukládají v prohlížeči (`annschool:test:<adresa>`) a zůstávají tam, dokud se test nedokončí nebo nezačne znovu – úložiště (Safari asi 5 MB) se časem zaplní. Pak se mažou uložené testy jiných stránek: nejdřív dokončené, potom od nejstaršího (test na otevřené stránce nikdy). Při načtení každé stránky se ověří rezerva asi 0,5 MB. Když se fronta ani tak nevejde, obrázky papíru zůstanou ve frontě jen v paměti a odešlou se, dokud je stránka otevřená (do 01.11.2026 se zahodily – v tabulce `papir` prázdný a `detail` „[object Object]“). Co se smazalo, se jednou za načtení pošle jako událost `uloziste`.
- **Náhled papíru (šablona v21+, Skript v03):** test každých 20 s pošle obrázek papíru (událost `nahled`) u příkladu, kde se papír od posledního odeslání změnil – jen když je záznam zapnutý a ve frontě nic nečeká (offline se staré náhledy nehromadí; jeden příklad za kolo, aktuální přednostně). Prázdný papír po Smazat = `papir: "prazdne"`. Skript náhled **nezapisuje do listu Udalosti**, ale do listu **Nahledy** (jeden řádek na relaci a příklad, jen novější stav; předchozí obrázek náhledu jde do koše na Disku). Obrázky papíru u pokusů (`vyhodnoceni`, `reseni`) se tam zapíšou taky, ale nemažou se (odkazuje na ně list Udalosti). Čtení: `<ENDPOINT>?akce=nahled&relace=<relace>`.
- **Zadání všech příkladů (šablona v21+):** `start` posílá v `detail.priklady` u každého příkladu `n, sekce, typ, zadani, spravna` a v `detail.sablona` verzi šablony.
- **Text, ne čísla (Skript v02):** sloupce se zadáním, odpovědí, správnou odpovědí a dalšími texty se v tabulce ukládají jako prostý text, aby je tabulka nepřevedla na číslo nebo datum (Pouceni, bod 2). Starší řádky uložené jako číslo vrací skript bez exponentu (6.5e-7 → 0.00000065).

### Události (list Udalosti, jeden řádek = jedna událost)

| udalost | kdy | hlavní sloupce |
|---|---|---|
| `start` | otevření testu / nová sada | detail: počet příkladů, sekce, orientace, rozměry; od v21 i `sablona` a `priklady` (zadání a správná odpověď každého příkladu) |
| `nahled` | v21: každých 20 s, když se papír příkladu změnil | priklad, sekce, papir (obrázek nebo `prazdne`) – jen list Nahledy, ne Udalosti |
| `presun` | v23: přechod na jiný příklad (i na souhrn = příklad 0) | priklad, sekce, doba_s (čas na příkladu dosud), detail: z (odkud) |
| `pozice` | v23: každých 20 s, když je test vidět, při přechodu, odchodu a návratu | priklad (0 = souhrn), doba_s = čas na příkladu v této návštěvě, detail: aktivni, celkem_s, pocet – jen list Stav, ne Udalosti |
| `vyhodnoceni` | každé klepnutí na Vyhodnotit (každý pokus) | priklad, sekce, typ, zadani, pokus, vysledek (spravne/spatne), konecny, odpoved, spravna, doba_s (čas na příkladu dosud), napoveda, odchody, papir (ID obrázku papíru, jen když se změnil) |
| `reseni` | důkaz – Vyhodnotit | jako vyhodnoceni bez výsledku |
| `napoveda` | první otevření nápovědy u příkladu | priklad, pokus, doba_s |
| `odchod` | návrat z jiné aplikace / panelu / zamčení | priklad, doba_s (jak dlouho byla pryč) |
| `stav`, `souhrn` | odchod ze stránky / otevření souhrnu | detail: body, max, celkem_s a u každého příkladu stav, pokusy, doba_s, napoveda, odchody, zadani |
| `pdf` | uložení PDF | detail: název souboru |
| `pokracovani` | znovuotevření rozpracovaného testu (v17) | detail: kdy byl stav uložen, na kterém příkladu |
| `oznaceni` | zarizeni.html | detail: přezdívka |
| `uloziste` | plné úložiště prohlížeče (`zaznam.js`, jednou za načtení stránky) | detail: smazano (uložené testy: test, vel, hotovo, ulozeno), obrazky_jen_v_pameti, celkem, klicu, nejvetsi (8 největších klíčů s velikostí ve znacích) |
| `otevreni`, `stranka`, `odchod`, `klik`, `porozumeni` | stránky s teorií a rozcestník (`sledovani.js`) | typ (material, simulator, zapisky, rozcestnik…), doba_s = aktivní doba, detail: doby, odchody, posouvání, oblasti, stav Chápu / Nechápu; `porozumeni` = klepnutí na Chápu / Nechápu (sekce = část teorie) – Navod_material kap. 7 |

Společné sloupce: cas, zarizeni (náhodné ID), prezdivka, relace (jedno otevření testu), test (cesta), nazev, verze, id.

- **Čas na příkladu** = doba, kdy byl příklad na obrazovce a stránka viditelná (sčítá se i při návratu).
- **Odchod** pozná přepnutí na jinou aplikaci, jiný panel Safari a zamčení. Nepozná Split View / Slide Over, druhé zařízení ani to, kam Ann odešla. Kalkulačka v testu není, takže i kalkulačka = odchod.

### Zařízení a přezdívky

- Každý prohlížeč dostane náhodné ID (6 znaků). Přezdívku nastaví `https://mjandlik.github.io/annschool/zarizeni.html?u=<přezdívka>` (otevřít jednou v Safari na iPadu dítěte). Do repozitáře nepiš skutečná jména.
- Skript zapíše každé nové zařízení do listu **Zarizeni**. Martin tam zařízení schválí (`schvaleno` = ano) a případně přiřadí přezdívku (`prirazena_prezdivka`, přebije tu ze zařízení).
- V přehledu: neschválené zařízení má štítek, zařízení bez přezdívky = „neznámé“ (skryté, dokud se nezaškrtne „zobrazit i neznámá zařízení“). Tak se oddělí výsledky kamarádky, které Ann pošle odkaz.
- Safari může smazat data webu, který se 7 dní nepoužil. Pak zařízení dostane nové ID → v přehledu „neznámé“ → Martin v listu Zarizeni přiřadí přezdívku a schválí, nebo znovu otevře odkaz `zarizeni.html?u=…`.

### Přehled (vysledky.html)

- **Testy:** každé otevření testu – kdy, kdo, test, body, barevná kolečka příkladů, čas, štítky (rychlé odpovědi, odchody, nápověda, neschválené zařízení). Klepnutí = detail: **každý příklad testu včetně neotevřených a nevyhodnocených** se zadáním a správnou odpovědí, všechny pokusy (co napsala, správně/špatně, čas), nápověda, odchody, tlačítko „papír“ (obrázek papíru v době pokusu) a tlačítko **„papír teď“** (poslední stav papíru u příkladu s časem: průběžný náhled, nebo papír z posledního vyhodnocení, pokud je novější; po načtení se tlačítko změní na „obnovit“ a načte stav znovu).
- **Odkud přehled bere zadání:** u šablony v21+ ze startu testu (`detail.priklady`). U starších testů načte soubor testu z repozitáře (cesta z události, když tam není, `archiv/<předmět>-<soubor>`), z bloku KONFIGURACE TESTU spočítá zadání a správné odpovědi stejně jako šablona a použije je, jen když sedí `TEST.version`. Testy s náhodnou sadou (`generate`) na starší šabloně zadání neotevřených příkladů nemají. Cesta se bere jen ve tvaru `<předmět>/<tema>_test…_vXX.html`.
- **Kde je teď (šablona v23, Skript v04):** v seznamu Testy pod názvem testu a v detailu nahoře štítek „● teď: příklad N · čas na něm (celkem …)“, když je poslední `pozice` aktivní a mladší než 60 s; čas se počítá po sekundách. Jinak „neaktivní – naposledy na příkladu N před …“ (v seznamu jen 30 min). Řádek příkladu je v detailu zvýrazněný. Přehled se každých 20 s ptá `<ENDPOINT>?akce=stav`; při změně příkladu se překreslí, nový otevřený test načte celá data. Starší testy (před v23): „přibližně: poslední aktivita příklad N, před …“ podle poslední události (vyhodnocení, řešení, nápověda, odchod). Skript v03 akce=stav nezná – pak se ukazuje jen „přibližně“.
- **Odpověď po nápovědě:** u každého pokusu po otevření nápovědy „X s po nápovědě“ = čas na příkladu mezi prvním otevřením nápovědy (`napoveda.doba_s`) a pokusem (`vyhodnoceni.doba_s`); funguje i u starších testů. Správná odpověď rychleji než nastavený limit (výchozí 20 s, pole „Odpověď rychle po nápovědě“) = červený štítek u pokusu, v Poznámkách „správně X s po nápovědě“ a v seznamu „rychle po nápovědě: n“. U příkladu s otevřenou nápovědou se ukáže i text nápovědy (šablona v23 ze startu, jinak z konfigurace testu), aby šlo posoudit, jestli výsledek neprozrazuje.
- **Papír teď u starších testů (v17–v20):** test náhledy neposílá, ukáže se papír z posledního vyhodnocení a poznámka „tento test posílá papír jen při Vyhodnotit“.
- **Šedá v přehledu:** jen rozpracovaný příklad (pokus, nápověda, u v24+ i něco na papíře nebo v odpovědi – souhrn posílá `navstiveno`, `zacala`). Otevřený a přeskočený = bílý se štítkem „jen prohlédnuto“; u starších testů se papír nepozná, šedá jen podle pokusu nebo nápovědy. Šedý bez pokusu má štítek „rozpracováno“.
- **Chyby k procvičení:** všechny příklady, které nebyly správně napoprvé (oranžové, červené, nedokončené), s chybnými odpověďmi. Podklad pro opravné testy.
- **Teorie a stránky:** každé otevření HTML stránky s teorií (materiál, tahák, simulátor, zápisky) a rozcestníku – doba otevření, aktivní doba, odchody, kolik prošla (% stránky), štítek „většinou nečinná“. Nahoře „Aktuální stav porozumění“ (poslední volba Chápu / Nechápu u každé části teorie ze všech otevření, vývoj), v tabulce sloupec Chápe / nechápe. Detail: aktivní čas po částech stránky, Chápu / Nechápu v tom otevření, co otevřela z rozcestníku, odchody. PDF se nesledují.
- **Zařízení:** seznam z listu Zarizeni.
- **Rychlá odpověď** = první pokus rychleji než nastavený limit (výchozí 10 s).

### Opravné testy (Claude)

1. Data čti přes Google Drive konektor (tabulka s výsledky), nebo přes `WebFetch` na `<ENDPOINT>?akce=data` (JSON se všemi událostmi).
2. Pro vybrané dítě a období vezmi příklady, které nebyly zelené, a jejich chybné odpovědi. Přihlédni i k tomu, jestli a jak dlouho četla teorii k tématu (události `stranka`). Z odpovědí urči typ chyby (směr převodu, řád, znaménko, záměna pojmů…), ne jen téma.
3. Navrhni Martinovi opravný test: typy chyb → okruhy (sekce), ke každému 2–4 nové příklady, odpovědi ve výběru podle zjištěných chyb. Po potvrzení postupuj podle kap. 1–6 (typ `test-opravny` nebo `test-opravny-<n>`, název doplň do `NAZVY.typy`), včetně kontroly po sobě (kap. 4).

### Nastavení Google tabulky (jednorázově, dělá Martin)

1. Na drive.google.com vytvoř novou Google tabulku, např. „AnnSchool – výsledky“, a v **Soubor → Nastavení** nastav národní prostředí **Česko**.
2. V tabulce **Rozšíření → Apps Script**. Smaž obsah `Kód.gs` a vlož celý obsah `system/Skript_vysledky_vXX.gs`. Ulož (ikona diskety).
3. Nahoře vyber funkci **nastav** a klikni **Spustit**. Povol oprávnění (účet Google → Upřesnit → Přejít na projekt → Povolit). Založí listy Udalosti, Zarizeni a složku na Disku „AnnSchool – papír z testů“.
4. **Nasadit → Nové nasazení →** typ **Webová aplikace**. Spustit jako: **Já**, Kdo má přístup: **Kdokoli**. Nasadit a zkopírovat **adresu webové aplikace** (končí `/exec`).
5. Adresu pošli Claudovi → zapíše ji do `system/lib/zaznam.js` (`ENDPOINT`) a pushne.
6. Na iPadu dítěte v Safari otevři `zarizeni.html?u=<přezdívka>`, pak v tabulce v listu Zarizeni nastav u jeho zařízení `schvaleno` = ano. Ověř v `vysledky.html`, že se výsledky ukazují pod přezdívkou bez štítku „neschválené“ (Pouceni, bod 3).
7. **Změna skriptu** (nová verze `Skript_vysledky_vXX.gs`): vlož nový kód a **Nasadit → Spravovat nasazení → upravit (tužka) → Verze: Nová verze → Nasadit**. Adresa zůstane stejná. Samotné uložení kódu v editoru nestačí (webová aplikace běží dál na staré verzi). Nikdy „Nové nasazení“ a nikdy nearchivovat nasazení, na které vede `ENDPOINT` v `zaznam.js` – jinak se nic nezapisuje a přehled hlásí „Failed to fetch“ (Pouceni bod 23). Po nasazení otevři adresu z `zaznam.js` v prohlížeči – musí ukázat `{"ok":true,…}`. Po nasazení nové verze jednou spusť funkci **nastav** (v03 založí list Nahledy, v04 list Stav) a ověř v přehledu u testu na šabloně v21, že „papír teď“ ukazuje průběžný náhled (Pouceni bod 2: v listu Nahledy musí být relace a příklad text).
