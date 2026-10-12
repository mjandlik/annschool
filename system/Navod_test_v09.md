# Návod: tvorba HTML testu pro Ann (system/Navod_test_v09)

Podrobný postup pro chat v projektu „Ann School“. Projektové instrukce obsahují jen krátké shrnutí a odkazují sem.
Platí vždy aktuální verze souborů (nejvyšší `_vXX`). Starší verze jsou v `archiv/`.

---

## 0. Přehled a struktura repozitáře

- Repozitář `mjandlik/annschool`, větev `main`, GitHub Pages: https://mjandlik.github.io/annschool/

```
index.html                         rozcestník pro Ann (stálá adresa, bez _vXX)
README.md
system/                            šablona, návody, kontrola, knihovny
  Sablona_test_vXX.html
  Navod_test_vXX.md, Navod_material_vXX.md
  Kontrola_testu_vXX.py
  lib/                             html2canvas 1.4.1, jsPDF 2.5.2, vektory.js + vektory.css (vektorová síť, kap. 8)
matematika/ fyzika/ chemie/ …      soubory pro Ann: <tema>_<typ>_vXX.<přípona>
archiv/                            plochý: <složka>-<původní název>
```

- Předmět = složka: `matematika`, `fyzika`, `chemie` (další stejně, malými písmeny, bez diakritiky).
- `tema`: stejné jako v projektu Claude (`prevody-jednotek`), malými písmeny, bez diakritiky, s pomlčkami.
- `typ`: `test` (HTML), `material` (studijní PDF), `tahak`, `pracovni-list`, `simulator` (interaktivní HTML pomůcka, např. `fyzika/vektory_simulator_v01.html`).
  - Víc testů k jednomu tématu: `test-<podtyp>`, např. `vektory_test-rysovani_v01.html`.
  - Rozcestník řadí typy začínající `test` do skupiny **Testy**, ostatní do skupiny **Výukové materiály**.
- Příklad: `fyzika/prevody-jednotek_test_v01.html` → https://mjandlik.github.io/annschool/fyzika/prevody-jednotek_test_v01.html
- Ann test otevírá jen na iPadu (Safari) a píše Apple Pencilem. Martin jí posílá odkaz přes WhatsApp. Všechno najde i v rozcestníku.

---

## 1. Doptání (před jakoukoli prací na souborech)

1. Z projektu načti aktuální látku (`<předmět>/<téma>_vXX.md`). Z ní vycházej.
2. Co z kontextu není jasné, zeptej se jedním souhrnným dotazem (AskUserQuestion). U každého bodu navrhni výchozí volbu:
   - **Téma a okruhy:** okruhy = sekce testu, každá sekce má vlastní „Vyhodnotit“, „Zkusit znovu“ a skóre.
   - **Počet příkladů a obtížnost:** výchozí 10–15, stupňovaná, 2–5 příkladů na sekci.
   - **Pevná, nebo náhodná sada:** u náhodné se v panelu objeví „Nová sada“.
   - **Společná plocha na psaní vpravo vedle příkladů každé sekce** (`sideScratch`): výchozí ano. Je to jedna souvislá plocha na celou výšku sekce.
   - **Větší plocha pod příkladem** (`scratch`): jen u vícekrokových výpočtů a rýsování (návrh udělej sám). Velká plocha na konci: výchozí ano.
   - **Nápovědy:** výchozí ano.
   - **Časový limit:** výchozí ne.
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
   - `timeLimitMin`, `showHints`, `finalScratch`, `sideScratch` (true/false, výchozí true): podle odpovědí z bodu 1,
   - `questions`: `{ section: "…" }` začíná sekci, příklad je `{ before, after, answer, tol, hint, scratch }`,
   - `generate`: jen u náhodné sady (funkce vrací pole ve stejném tvaru jako `questions`, vzor je v šabloně), jinak `null`.
3. Pravidla pro obsah:
   - Zadání ve tvaru „5 m = [ ] mm“. Jednotka je za polem (`after`), nikdy ne uvnitř odpovědi.
   - `answer` je číslo v JavaScriptu (desetinná **tečka**, bez mezer): `0.32`, `30000`.
   - U zaokrouhlení napiš přesnost do `after` („h (na 1 des. místo)“) a nastav `tol` (např. `0.05`).
   - Mocniny deseti: `after: "· 10³ m"`, Ann doplní jen číslo před mocninou.
   - `hint`: krátké vysvětlení postupu, zobrazí se i u chybné odpovědi. U převodů jednotek vždy směr a všechny zápisy, např. „mm → m: NAHORU na větší jednotku → dělím 1000 (:1000 = :10³ = ·10⁻³) → 45 : 1000 = 0,045“, resp. „km → m: DOLŮ na menší jednotku → násobím 1000 (·1000 = ·10³) → …“.
   - Unicode znaky (m², µm, 10⁻³, ·, ≈), žádný LaTeX.
   - Úroveň 1. ročníku gymnázia. Vše musí být fyzikálně a matematicky správně.
4. Vzhled, panel, kreslení, vyhodnocení ani PDF v testu **neměň**. Úpravy šablony dělej jen na Martinův výslovný pokyn (nová verze šablony, stará do `archiv/system-…`). Nová systémová tlačítka patří do `<div class="panel-actions">`.
5. Stránka musí ležet přesně o jednu složku pod rootem, protože knihovny načítá z `../system/lib/`.

---

## 4. Kontrola (povinná)

1. Výsledky všech příkladů nezávisle přepočítej v Pythonu.
2. Z rootu repozitáře spusť `python3 system/Kontrola_testu_vXX.py <předmět>/<tema>_test_vXX.html`. Pokud chybí Playwright: `pip install playwright --break-system-packages && python3 -m playwright install chromium`.
3. Musí skončit „Vše v pořádku.“ Jinak oprav a spusť znovu.

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

---

## 7. Jak stránka funguje (pro odpovědi na Martinovy dotazy)

- **Horní panel:** název · verze, barvy (černá, modrá, červená, zelená, růžová), tloušťka pera (tenká, střední, silná), Pero, Prst (kreslení prstem), Guma, PDF. Tahy se vyhlazují a reagují na tlak Pencilu.
- **Kreslení:** Apple Pencil kreslí, prst posouvá stránku. Zpět a Smazat jsou u každé plochy.
- **Popisek ploch:** každá plocha na psaní má vlevo nahoře malým šedým písmem „Místo pro poznámky“ (je i v PDF). Řeší to šablona, v testu se nic nenastavuje.
- **Odpovědi:** klávesnice. Čárka i tečka jsou v pořádku, mezery nevadí.
- **PDF:** jedno klepnutí vytvoří PDF a otevře sdílení na iPadu. Kdyby ho iPad zablokoval, tlačítko zezelená na „Uložit PDF“ a stačí klepnout znovu. Po každé změně se PDF vytvoří znovu. Název: `Test_<tema>_vXX_<datum>_NN.pdf`, kde NN je pořadové číslo uložení.
- **Neukládá se:** odpovědi a kresby se po zavření stránky ztratí. Před zavřením je potřeba uložit PDF.

---

## 8. Knihovna vektory.js (vektorová síť)

Sdílená knihovna `system/lib/vektory.js` + `system/lib/vektory.css`. Používá ji simulátor `fyzika/vektory_simulator_vXX.html` a je připravená pro testy na vektory (typy otázek „narýsuj vektor“, „šipka za šipku“). Úpravy knihovny jen na Martinův výslovný pokyn; změna musí zůstat zpětně kompatibilní se simulátorem.

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

- Apple Pencil a myš ovládají síť, prst posouvá stránku. `Vektory.nastavPrst(true)` zapne ovládání prstem (tlačítko „Prst“ v panelu).
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

1. Do `<head>` šablony za skripty pro PDF:
   ```html
   <link rel="stylesheet" href="../system/lib/vektory.css">
   <script src="../system/lib/vektory.js"></script>
   ```
2. Síť patří do vlastního `<div>` uvnitř příkladu (`.q`). Šířka se bere z rodiče a výška se dopočítá (čtvercové dílky), proto rodič musí mít šířku. Ve sloupci vedle `sideScratch` je místa málo, sekce s rýsováním by měla mít `sideScratch: false`, nebo síť na celou šířku.
3. Tlačítko „Prst“ v šabloně přepíná `draw.finger` pro plochy na psaní. Stejným klepnutím přepni i `Vektory.nastavPrst(draw.finger)`, ať se prst chová všude stejně.
4. **Vyhodnocení „narýsuj vektor“:** porovnej `Vektory.slozky(sit.vektor(id))` s očekávaným `{dx, dy}`. Poloha počátku je libovolná (vektor posunutý jinam je tentýž vektor). Chybějící vektor = chyba.
5. **Zobrazení správného vektoru u chyby:** vlož ho do `sit.pomocne` čárkovaně (`carkovane: true`, šedá nebo zelená), nejlépe se stejným počátkem jako Annin vektor. Když Ann nic nenakreslila, dej ho do volného místa. Pak `sit.prekresli()`.
6. **Po vyhodnocení** nastav `sit.o.upravy = false` a `sit.kresli = null`, aby se odpověď neměnila. „Zkusit znovu“ vrátí `true` a nastaví `kresli` znovu. `sit.vymaz()` smaže i `pomocne`, `body` a `oblouky`.
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
- **Pencil × prst:** reaguje se jen na `pointerType` `pen` a `mouse` (a `touch` při zapnutém prstu). Pencil nesmí posouvat stránku, proto `touchstart`/`touchmove` s `touchType === "stylus"` volá `preventDefault()` (listener s `passive: false`). Stejně to dělá šablona testu. `touch-action` se nenastavuje, jinak by prst nemohl posouvat stránku.
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
- Ukládání do prohlížeče (localStorage) se nepoužívá. Stejně jako u testů se nic neukládá, výsledek je PDF.
- Hodně sítí na jedné stránce je v pořádku (každá má své plátno). Kvůli PDF a výkonu ale nejvýš asi 15 sítí na test.

### Použití v testu – doporučené typy otázek (návrh, zatím v šabloně nejsou)

- **Narýsuj vektor:** součet, rozdíl, násobek, opačný, neznámý k⃗ = N⃗ − m⃗. Kontroluje se `dx, dy`, poloha je libovolná.
- **Šipka za šipku:** Ann nakreslí 2–3 vektory navazující na sebe a výslednici. Kontrola:
  - složky každého vektoru,
  - navázání (konec předchozího = začátek dalšího),
  - výslednice od začátku prvního ke konci posledního.
- **Složky:** dvě číselná pole Δx a Δy.
- **Číslo:** stávající typ šablony.
- **Výběr:** skalár/vektor, ano/ne.

Nové typy patří do **nové verze šablony** a **kontroly** (`Kontrola_testu_vXX.py` musí umět správné i špatné odpovědi nových typů), ne jen do jednoho testu.
