# Návod: tvorba HTML testu pro Ann (system/Navod_test_v07)

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
  lib/                             html2canvas 1.4.1, jsPDF 2.5.2
matematika/ fyzika/ chemie/ …      soubory pro Ann: <tema>_<typ>_vXX.<přípona>
archiv/                            plochý: <složka>-<původní název>
```

- Předmět = složka: `matematika`, `fyzika`, `chemie` (další stejně, malými písmeny, bez diakritiky).
- `tema`: stejné jako v projektu Claude (`prevody-jednotek`), malými písmeny, bez diakritiky, s pomlčkami.
- `typ`: `test` (HTML), `material` (studijní PDF), `tahak`, `pracovni-list`.
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
