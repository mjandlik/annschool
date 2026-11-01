# Návod: tvorba HTML testu pro Ann (system/Navod_test_v13)

Podrobný postup pro chat v projektu „Ann School“. Projektové instrukce obsahují jen krátké shrnutí a odkazují sem.
Platí vždy aktuální verze souborů (nejvyšší `_vXX`). Starší verze jsou v `archiv/`.

---

## 0. Přehled a struktura repozitáře

- Repozitář `mjandlik/annschool`, větev `main`, GitHub Pages: https://mjandlik.github.io/annschool/

```
index.html                         rozcestník pro Ann (stálá adresa, bez _vXX), tlačítko „Výsledky“
vysledky.html                      přehled výsledků testů (stálá adresa, kap. 9)
zarizeni.html                      označení zařízení přezdívkou (stálá adresa, kap. 9)
README.md
system/                            šablona, návody, kontrola, knihovny
  Sablona_test_vXX.html
  Navod_test_vXX.md, Navod_material_vXX.md
  Kontrola_testu_vXX.py
  Skript_vysledky_vXX.gs           skript Google tabulky s výsledky (kap. 9)
  lib/                             html2canvas 1.4.1, jsPDF 2.5.2, vektory.js + vektory.css (vektorová síť, kap. 8),
                                   zaznam.js (odesílání výsledků, adresa webové aplikace, kap. 9),
                                   sledovani.js (záznam čtení teorie, Navod_material kap. 7)
matematika/ fyzika/ chemie/ …      soubory pro Ann: <tema>_<typ>_vXX.<přípona>
archiv/                            plochý: <složka>-<původní název>
```

- Předmět = složka: `matematika`, `fyzika`, `chemie` (další stejně, malými písmeny, bez diakritiky).
- `tema`: stejné jako v projektu Claude (`prevody-jednotek`), malými písmeny, bez diakritiky, s pomlčkami.
- `typ`: `test`, `material`, `tahak`, `pracovni-list`, `simulator`, `zapisky` (vše vlastní je HTML, Navod_material) a `skolni-material`, `zapisky` ze sešitu (PDF, jen vstupy).
  - Víc testů k jednomu tématu: `test-<podtyp>`, např. `vektory_test-1_vXX.html` (rýsování), `vektory_test-2_vXX.html` (výpočty).
  - Rozcestník řadí typy začínající `test` do skupiny **Testy**, ostatní do skupiny **Výukové materiály**.
- Příklad: `fyzika/prevody-jednotek_test_v01.html` → https://mjandlik.github.io/annschool/fyzika/prevody-jednotek_test_v01.html
- Ann test otevírá na iPadu (Safari, na výšku i na šířku) a píše Apple Pencilem. Od šablony v17 píše a kreslí jen pero (Pencil, stylus na Androidu) nebo myš, prst vždy jen posouvá. Martin jí posílá odkaz přes WhatsApp. Všechno najde i v rozcestníku.

---

## 1. Doptání (před jakoukoli prací na souborech)

1. Z projektu načti aktuální látku (`<předmět>/<téma>_vXX.md`). Z ní vycházej.
2. Co z kontextu není jasné, zeptej se jedním souhrnným dotazem (AskUserQuestion). U každého bodu navrhni výchozí volbu:
   - **Téma a okruhy:** okruhy = sekce testu (skupiny na časové ose a řádky v souhrnu); vyhodnocuje se každý příklad zvlášť.
   - **Počet příkladů a obtížnost:** výchozí 10–15, stupňovaná, 2–5 příkladů na sekci.
   - **Pevná, nebo náhodná sada:** u náhodné se v panelu objeví „Nová sada“.
   - **Papír na psaní** se neptej: od šablony v16 má každý příklad vlastní stránku s papírem pod odpovědí.
   - **Výběr z možností:** aspoň 5 možností (a–e). Výjimka jen tam, kde smysluplně existují 2 (skalár/vektor, doprava/doleva, ano/ne). Špatné možnosti volit podle typických chyb (opačný směr převodu, záměna jednotky, chybný řád), aby z odpovědi bylo vidět, kde Ann chybuje.
   - **Nápovědy:** výchozí ano.
   - **Časový limit:** výchozí ne.
   - **U vektorů:** velikost sítě (výchozí 14 × 12, osy bez čísel), měřítko u slovních úloh (1 dílek = 100 N), bodování řetězu (výchozí: 1 bod jen při úplné správnosti).
3. Nic nevytvářej, dokud Martin neodpoví nebo nepotvrdí návrh.

---

## 2. Příprava repozitáře

1. Připoj repozitář: `add_repo(owner="mjandlik", repo="annschool", access="push")` a naklonuj ho podle pokynů nástroje.
2. Najdi aktuální `system/Sablona_test_vXX.html` a `system/Kontrola_testu_vXX.py` (nejvyšší verze).
3. Zjisti, jestli test k tématu existuje (`<předmět>/<tema>_test_vXX.html`):
   - **existuje:** nová verze `_vXX+1`, starou přesuň `git mv` do `archiv/<předmět>-<tema>_test_vXX.html`,
   - **neexistuje:** `<předmět>/<tema>_test_v01.html`.

---

## 3. Vytvoření testu

1. Zkopíruj aktuální šablonu na `<předmět>/<tema>_test_vXX.html`.
2. Uprav **jen** blok „KONFIGURACE TESTU“:
   - `title`: čitelný název („Převody jednotek – plocha a objem“),
   - `version`: stejné jako v názvu souboru („v01“),
   - `intro`: krátký pokyn (1 věta),
   - `topic`: stejné jako `<tema>` v názvu souboru,
   - `timeLimitMin`, `showHints`: podle odpovědí z bodu 1 (`finalScratch`, `sideScratch` a `scratch` od v16 nemají účinek, mohou zůstat),
   - `questions`: `{ section: "…" }` začíná sekci (skupina na časové ose), příklad je `{ before, after, answer, tol, hint }` nebo jeden z typů v kap. 3a,
   - `generate`: jen u náhodné sady (funkce vrací pole ve stejném tvaru jako `questions`, vzor je v šabloně), jinak `null`.
3. Pravidla pro obsah:
   - Zadání ve tvaru „5 m = [ ] mm“. Jednotka je za polem (`after`), nikdy ne uvnitř odpovědi.
   - `answer` je číslo v JavaScriptu (desetinná **tečka**, bez mezer): `0.32`, `30000`.
   - U zaokrouhlení napiš přesnost do `after` („h (na 1 des. místo)“) a nastav `tol` (např. `0.05`).
   - Mocniny deseti: `after: "· 10³ m"`, Ann doplní jen číslo před mocninou.
   - `hint`: krátké vysvětlení postupu. Ann ho může otevřít kdykoli (otevření se zaznamená) a ukáže se i po 3. špatném pokusu. U převodů jednotek vždy směr a všechny zápisy, např. „mm → m: NAHORU na větší jednotku → dělím 1000 (:1000 = :10³ = ·10⁻³) → 45 : 1000 = 0,045“, resp. „km → m: DOLŮ na menší jednotku → násobím 1000 (·1000 = ·10³) → …“.
   - Unicode znaky (m², µm, 10⁻³, ·, ≈), žádný LaTeX.
   - Výběr z možností: aspoň 5 možností (výjimky v kap. 1), správná možnost na různých místech.
   - Úroveň 1. ročníku gymnázia. Vše musí být fyzikálně a matematicky správně.
4. Vzhled, panel, kreslení, časovou osu, vyhodnocení, záznam ani PDF v testu **neměň**. Úpravy šablony dělej jen na Martinův výslovný pokyn (nová verze šablony, stará do `archiv/system-…`). Nová systémová tlačítka patří do `<div class="panel-actions">`.
5. Stránka musí ležet přesně o jednu složku pod rootem, protože knihovny načítá z `../system/lib/`.

---

## 3a. Typy příkladů (od šablony v13)

Příklad je správně, jen když jsou správně **všechny** jeho části (pole, výběr, kresba). Body (v16): napoprvé 1, napodruhé ½, napotřetí nebo vůbec 0. V každém textu (`text`, `before`, `after`, `hint`, `options`) znamená `{F}` písmeno se šipkou nad ním (vektor), např. `"{N} = {k} + {m}"`. Šipka je z CSS a html2canvas ji přenese i do PDF. Velikost se píše bez šipky: `F = 3 N` nebo `|{F}| = 3 N`.

| Typ | Konfigurace | Vyhodnocení |
|---|---|---|
| číslo (bez `type`) | `{ before, after, answer, tol, hint, scratch, text }` | jako dřív; `text` (nepovinný) = zadání nad řádkem s polem |
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

## 4. Kontrola (povinná)

1. Výsledky všech příkladů nezávisle přepočítej v Pythonu.
2. Z rootu repozitáře spusť `python3 system/Kontrola_testu_vXX.py <předmět>/<tema>_test_vXX.html`. Pokud chybí Playwright: `pip install playwright --break-system-packages && python3 -m playwright install chromium`.
3. Musí skončit „Vše v pořádku.“ Jinak oprav a spusť znovu.
4. Co kontrola v06 dělá (šablona v17+; v16 kontroluje archivní v05, starší v04):
   - iPad na výšku 820 × 1180 i na šířku 1180 × 820, `device_scale_factor` 2: žádné chyby v konzoli, nic se neposouvá vodorovně, papír aspoň 260 px, časová osa celá vidět,
   - prázdná odpověď se nepočítá jako pokus,
   - správné odpovědi všech typů → zelená (čísla s desetinnou čárkou a mezerami, výběr klepnutím, rýsování a řetěz kreslením myší přes síť), důkaz → modrá a vzorové řešení,
   - první příklad každého typu: špatně → šedá, správné řešení se neukáže, síť zůstane odemčená; pak správně → oranžová,
   - druhý příklad téhož typu: 3× špatně → červená, zamčeno, správné řešení vidět (u sítě čárkovaně),
   - papír: tah zůstane u příkladu po přechodu jinam i po otočení iPadu,
   - záznam: start, vyhodnoceni (počet = počet pokusů, s obrázkem papíru), napoveda, odchod, souhrn (adresa webové aplikace je v kontrole podvržená, nic se nikam neodesílá),
   - skóre v souhrnu, PDF, verze a téma v názvu souboru (i `test-<podtyp>`),
   - obnovení po zavření: znovuotevření (dialog „Pokračovat?“) vrátí stavy příkladů i papír, zapíše `pokracovani` a žádný nový `start`.
5. U testů se sítí navíc ověř v Playwrightu přesun bodu a posun celého vektoru (kap. 8 „Testy v Playwrightu“).

---

## 5. Rozcestník

- `index.html` načítá seznam souborů automaticky z GitHubu a ukazuje vždy nejvyšší verzi každého tématu a typu.
- Rozcestník: předmět → téma → skupiny **Výukové materiály** a **Testy**.
- U **nového tématu** (nebo předmětu) doplň český název do `NAZVY.temata` (`NAZVY.predmety`) v `index.html`, např. `"linearni-rovnice": "Lineární rovnice"`. Bez toho se zobrazí název odvozený z `tema` (bez diakritiky).
- U **nového typu** (např. `test-rysovani`) doplň název do `NAZVY.typy`, např. `"test-rysovani": "Test – rýsování"`.
- `index.html` a `README.md` mají stálé adresy, proto se neverzují v názvu. Historie je v gitu.

---

## 6. Zveřejnění a předání

1. `git add -A`, commit (česky, co je nového) a `git push origin HEAD:main`.
2. GitHub Pages zveřejní stránku zhruba do minuty. Není potřeba čekat.
3. Martinovi napiš krátce:
   - odkaz `https://mjandlik.github.io/annschool/<předmět>/<tema>_test_vXX.html`,
   - počet sekcí a příkladů,
   - archivovanou verzi (pokud nějaká je).
   - Rozcestník: https://mjandlik.github.io/annschool/
4. Příklady z testu (zadání + výsledky) ulož do projektu Claude jako novou verzi `<předmět>/<téma>_vXX.md` podle pravidel projektu.
5. Nový test se do přehledu výsledků (`vysledky.html`) přidá sám po prvním odeslaném výsledku. Nic dalšího se nenastavuje.

---

## 7. Jak stránka funguje (pro odpovědi na Martinovy dotazy)

- **Horní panel (pevný):** název · verze, barvy (černá, modrá, červená, zelená, růžová), tloušťka pera (tenká, střední, silná), Pero, Guma, Nová sada (jen u náhodné sady), PDF. Režim „Prst“ od v17 není – prst vždy posouvá. Tahy se vyhlazují a reagují na tlak Pencilu.
- **Stránka příkladu** (na výšku i na šířku stejně, odshora): hlavička „Příklad N / M · sekce · stav“ → zadání → odpověď (pole, výběr, síť) → Vyhodnotit, Nápověda → **papír**. Předchozí / další příklad: šipky ‹ › vpravo v časové ose. Papír vyplní zbytek obrazovky (aspoň 260 px); když je zadání vysoké (síť), posouvá se celá plocha.
- **Papír:** každý příklad má vlastní, pevně velký papír 1150 × 1600 px (šířka iPadu na šířku, výška asi 2 obrazovky). Pero (Pencil, stylus) a myš píšou, prst papír posouvá (na výšku i do strany). Posun prstem počítá šablona sama (`touch-action: none`), protože stylus na Androidu jinak posouval papír místo psaní. Totéž platí pro vektorové sítě (vektory.js). Lišta papíru: Zpět, Smazat, ↖ Na začátek. Tahy se ukládají jako křivky, po otočení iPadu se nic neztratí ani nezmenší.
- **Pokusy:** nejvýš 3. Prázdná odpověď se nepočítá („Nejdřív doplň odpověď“). Po 1. a 2. špatném pokusu jen „Špatně – zkus to znovu“ (správný výsledek se neukáže). Po správné odpovědi nebo 3. špatném pokusu se příklad zamkne; u chyby se ukáže správný výsledek a nápověda. Vyhodnocený příklad jde znovu otevřít jen k prohlížení.
- **Časová osa (pevná dole, zalomí se):** kolečko s číslem (28 px) pro každý příklad, vpravo šipky ‹ › na předchozí / další, sekce oddělené názvem, nakonec „Σ Souhrn“. Klepnutí = skok na příklad. Barvy: bílá = neotevřeno, šedá = otevřeno / nedokončeno, zelená = napoprvé, oranžová = napodruhé, červená = napotřetí nebo vůbec, modrá = důkaz (řešení zobrazeno). Aktuální příklad má silnější černý okraj.
- **Souhrn:** body (zelená 1, oranžová ½, červená 0), tabulka sekcí s barevnými kolečky, stav odeslání výsledků, ID zařízení a přezdívka.
- **Odpovědi:** klávesnice. Čárka i tečka jsou v pořádku, mezery nevadí. Enter = další pole, v posledním poli Vyhodnotit. Vektory se kreslí Pencilem do sítě (kap. 3a), řádek „Kreslím:“ určuje, který vektor se kreslí.
- **PDF:** souhrn + každý příklad (zadání, odpověď, výsledek) a pod ním jeho popsaný papír. Jedno klepnutí vytvoří PDF a otevře sdílení na iPadu. Kdyby ho iPad zablokoval, tlačítko zezelená na „Uložit PDF“ a stačí klepnout znovu. Název: `Test_<tema>_vXX_<datum>_NN.pdf`.
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
- **Pero × prst:** reaguje se jen na `pointerType` `pen` a `mouse`. Dřív se Pencil blokoval přes `touchType === "stylus"` (jen Safari) – na Androidu pak stylus posouval stránku. Od 01.11.2026 má plátno `touch-action: none` a posun prstem se počítá ručně (`pointerType === "touch"` → `scrollLeft/scrollTop` nejbližšího posouvatelného rodiče). Stejně to dělá papír v šabloně v17.
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

### Události (list Udalosti, jeden řádek = jedna událost)

| udalost | kdy | hlavní sloupce |
|---|---|---|
| `start` | otevření testu / nová sada | detail: počet příkladů, sekce, orientace, rozměry |
| `vyhodnoceni` | každé klepnutí na Vyhodnotit (každý pokus) | priklad, sekce, typ, zadani, pokus, vysledek (spravne/spatne), konecny, odpoved, spravna, doba_s (čas na příkladu dosud), napoveda, odchody, papir (ID obrázku papíru, jen když se změnil) |
| `reseni` | důkaz – Vyhodnotit | jako vyhodnoceni bez výsledku |
| `napoveda` | první otevření nápovědy u příkladu | priklad, pokus, doba_s |
| `odchod` | návrat z jiné aplikace / panelu / zamčení | priklad, doba_s (jak dlouho byla pryč) |
| `stav`, `souhrn` | odchod ze stránky / otevření souhrnu | detail: body, max, celkem_s a u každého příkladu stav, pokusy, doba_s, napoveda, odchody, zadani |
| `pdf` | uložení PDF | detail: název souboru |
| `pokracovani` | znovuotevření rozpracovaného testu (v17) | detail: kdy byl stav uložen, na kterém příkladu |
| `oznaceni` | zarizeni.html | detail: přezdívka |
| `otevreni`, `stranka`, `odchod`, `klik` | stránky s teorií a rozcestník (`sledovani.js`) | typ (material, simulator, zapisky, rozcestnik…), doba_s = aktivní doba, detail: doby, odchody, posouvání, oblasti – Navod_material kap. 7 |

Společné sloupce: cas, zarizeni (náhodné ID), prezdivka, relace (jedno otevření testu), test (cesta), nazev, verze, id.

- **Čas na příkladu** = doba, kdy byl příklad na obrazovce a stránka viditelná (sčítá se i při návratu).
- **Odchod** pozná přepnutí na jinou aplikaci, jiný panel Safari a zamčení. Nepozná Split View / Slide Over, druhé zařízení ani to, kam Ann odešla. Kalkulačka v testu není, takže i kalkulačka = odchod.

### Zařízení a přezdívky

- Každý prohlížeč dostane náhodné ID (6 znaků). Přezdívku nastaví `https://mjandlik.github.io/annschool/zarizeni.html?u=<přezdívka>` (otevřít jednou v Safari na iPadu dítěte). Do repozitáře nepiš skutečná jména.
- Skript zapíše každé nové zařízení do listu **Zarizeni**. Martin tam zařízení schválí (`schvaleno` = ano) a případně přiřadí přezdívku (`prirazena_prezdivka`, přebije tu ze zařízení).
- V přehledu: neschválené zařízení má štítek, zařízení bez přezdívky = „neznámé“ (skryté, dokud se nezaškrtne „zobrazit i neznámá zařízení“). Tak se oddělí výsledky kamarádky, které Ann pošle odkaz.
- Safari může smazat data webu, který se 7 dní nepoužil. Pak zařízení dostane nové ID → v přehledu „neznámé“ → Martin v listu Zarizeni přiřadí přezdívku a schválí, nebo znovu otevře odkaz `zarizeni.html?u=…`.

### Přehled (vysledky.html)

- **Testy:** každé otevření testu – kdy, kdo, test, body, barevná kolečka příkladů, čas, štítky (rychlé odpovědi, odchody, nápověda, neschválené zařízení). Klepnutí = detail: každý příklad se všemi pokusy (co napsala, správně/špatně, čas), správná odpověď, nápověda, odchody, tlačítko „papír“ (obrázek papíru v době pokusu).
- **Chyby k procvičení:** všechny příklady, které nebyly správně napoprvé (oranžové, červené, nedokončené), s chybnými odpověďmi. Podklad pro opravné testy.
- **Teorie a stránky:** každé otevření HTML stránky s teorií (materiál, tahák, simulátor, zápisky) a rozcestníku – doba otevření, aktivní doba, odchody, kolik prošla (% stránky), štítek „většinou nečinná“. Detail: aktivní čas po částech stránky, co otevřela z rozcestníku, odchody. PDF se nesledují.
- **Zařízení:** seznam z listu Zarizeni.
- **Rychlá odpověď** = první pokus rychleji než nastavený limit (výchozí 10 s).

### Opravné testy (Claude)

1. Data čti přes Google Drive konektor (tabulka s výsledky), nebo přes `WebFetch` na `<ENDPOINT>?akce=data` (JSON se všemi událostmi).
2. Pro vybrané dítě a období vezmi příklady, které nebyly zelené, a jejich chybné odpovědi. Přihlédni i k tomu, jestli a jak dlouho četla teorii k tématu (události `stranka`). Z odpovědí urči typ chyby (směr převodu, řád, znaménko, záměna pojmů…), ne jen téma.
3. Navrhni Martinovi opravný test: typy chyb → okruhy (sekce), ke každému 2–4 nové příklady, odpovědi ve výběru podle zjištěných chyb. Po potvrzení postupuj podle kap. 1–6 (typ `test-opravny` nebo `test-opravny-<n>`, název doplň do `NAZVY.typy`).

### Nastavení Google tabulky (jednorázově, dělá Martin)

1. Na drive.google.com vytvoř novou Google tabulku, např. „AnnSchool – výsledky“.
2. V tabulce **Rozšíření → Apps Script**. Smaž obsah `Kód.gs` a vlož celý obsah `system/Skript_vysledky_vXX.gs`. Ulož (ikona diskety).
3. Nahoře vyber funkci **nastav** a klikni **Spustit**. Povol oprávnění (účet Google → Upřesnit → Přejít na projekt → Povolit). Založí listy Udalosti, Zarizeni a složku na Disku „AnnSchool – papír z testů“.
4. **Nasadit → Nové nasazení →** typ **Webová aplikace**. Spustit jako: **Já**, Kdo má přístup: **Kdokoli**. Nasadit a zkopírovat **adresu webové aplikace** (končí `/exec`).
5. Adresu pošli Claudovi → zapíše ji do `system/lib/zaznam.js` (`ENDPOINT`) a pushne.
6. Na Annině iPadu v Safari otevři `zarizeni.html?u=<přezdívka>`, pak v tabulce v listu Zarizeni nastav u jejího zařízení `schvaleno` = ano.
7. **Změna skriptu** (nová verze `Skript_vysledky_vXX.gs`): vlož nový kód a **Nasadit → Spravovat nasazení → upravit (tužka) → Verze: Nová verze → Nasadit**. Adresa zůstane stejná.
