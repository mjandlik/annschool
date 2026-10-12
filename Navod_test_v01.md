# Návod: tvorba HTML testu pro Ann (Navod_test_v01)

Podrobný postup pro chat v projektu „Ann School“. Projektové instrukce obsahují jen krátké shrnutí a odkazují sem.
Platí vždy aktuální verze souborů v rootu repozitáře (nejvyšší `_vXX`). Starší verze jsou v `archiv/`.

---

## 0. Přehled

- Repozitář: `mjandlik/annschool`, větev `main`, zveřejnění přes GitHub Pages: https://mjandlik.github.io/annschool/
- Šablona: `Sablona_test_vXX.html`. Každý test je její kopie, mění se jen blok „KONFIGURACE TESTU“.
- Kontrola: `Kontrola_testu_vXX.py`. Automatický test stránky před zveřejněním.
- Knihovny pro PDF: `lib/` (html2canvas 1.4.1, jsPDF 2.5.2), na stránku se odkazují relativně.
- Ann otevírá test jen na iPadu (Safari) a píše Apple Pencilem. Martin jí posílá odkaz přes WhatsApp.
- Výsledky se nikam neodesílají. Ann si může stav uložit tlačítkem PDF.

---

## 1. Doptání (před jakoukoli prací na souborech)

1. Z projektu načti aktuální látku (`<předmět>/<téma>_vXX.md`). Z ní vycházej.
2. Co z kontextu není jasné, zeptej se jedním souhrnným dotazem (AskUserQuestion). U každého bodu navrhni výchozí volbu:
   - **Téma a okruhy:** okruhy = sekce testu, každá sekce má vlastní „Vyhodnotit“, „Zkusit znovu“ a skóre.
   - **Počet příkladů a obtížnost:** výchozí 10–15, stupňovaná, 2–5 příkladů na sekci.
   - **Pevná, nebo náhodná sada:** u náhodné se v panelu objeví „Nová sada“.
   - **Plocha na výpočty:** pod příkladem jen u vícekrokových výpočtů a rýsování (návrh udělej sám). Velká plocha na konci: výchozí ano.
   - **Nápovědy:** výchozí ano.
   - **Časový limit:** výchozí ne.
3. Nic nevytvářej, dokud Martin neodpoví nebo nepotvrdí návrh.

---

## 2. Příprava repozitáře

1. Připoj repozitář: `add_repo(owner="mjandlik", repo="annschool", access="push")` a naklonuj ho podle pokynů nástroje.
2. Najdi aktuální šablonu, návod a kontrolu: v rootu soubory s nejvyšší `_vXX`.
3. Zjisti, jestli už test k tématu existuje (`Test_<tema>_vXX.html`):
   - **existuje:** nová verze `_vXX+1`, starou přesuň `git mv` do `archiv/`,
   - **neexistuje:** `Test_<tema>_v01.html`.
   - `<tema>`: malými písmeny, bez diakritiky, slova oddělená pomlčkou (např. `prevody-jednotek`).

---

## 3. Vytvoření testu

1. Zkopíruj aktuální šablonu na `Test_<tema>_vXX.html`.
2. Uprav **jen** blok „KONFIGURACE TESTU“:
   - `title`: čitelný název („Převody jednotek – plocha a objem“),
   - `version`: stejné jako v názvu souboru („v01“),
   - `intro`: krátký pokyn (1 věta),
   - `topic`: stejné jako `<tema>` v názvu souboru,
   - `timeLimitMin`, `showHints`, `finalScratch`: podle odpovědí z bodu 1,
   - `questions`: `{ section: "…" }` začíná sekci, příklad je `{ before, after, answer, tol, hint, scratch }`,
   - `generate`: jen u náhodné sady (funkce vrací pole ve stejném tvaru jako `questions`, vzor je v šabloně), jinak `null`.
3. Pravidla pro obsah:
   - Zadání ve tvaru „5 m = [ ] mm“. Jednotka je za polem (`after`), nikdy ne uvnitř odpovědi.
   - `answer` je číslo v JavaScriptu (desetinná **tečka**, bez mezer): `0.32`, `30000`.
   - U zaokrouhlení napiš přesnost do `after` („h (na 1 des. místo)“) a nastav `tol` (např. `0.05`).
   - Mocniny deseti: `after: "· 10³ m"`, Ann doplní jen číslo před mocninou.
   - `hint`: krátké vysvětlení postupu (směr a násobek), zobrazí se i u chybné odpovědi.
   - Unicode znaky (m², µm, 10⁻³, ·, ≈), žádný LaTeX.
   - Úroveň 1. ročníku gymnázia. Vše musí být fyzikálně a matematicky správně.
4. Vzhled, panel, kreslení, vyhodnocení ani PDF v testu **neměň**. Úpravy šablony dělej jen na Martinův výslovný pokyn (nová verze šablony, stará do `archiv/`). Nová systémová tlačítka patří do `<div class="panel-actions">`.

---

## 4. Kontrola (povinná)

1. Výsledky všech příkladů nezávisle přepočítej v Pythonu.
2. Spusť `python3 Kontrola_testu_vXX.py Test_<tema>_vXX.html`. Pokud chybí Playwright: `pip install playwright --break-system-packages && python3 -m playwright install chromium`.
3. Musí skončit „Vše v pořádku.“ Jinak oprav a spusť znovu.

---

## 5. Zveřejnění a předání

1. `git add -A`, commit (česky, co je nového) a `git push origin HEAD:main`.
2. GitHub Pages zveřejní stránku zhruba do minuty. Není potřeba čekat.
3. Martinovi napiš krátce:
   - odkaz `https://mjandlik.github.io/annschool/Test_<tema>_vXX.html`,
   - počet sekcí a příkladů,
   - archivovanou verzi (pokud nějaká je).
4. Příklady z testu (zadání + výsledky) ulož do projektu jako novou verzi `<předmět>/<téma>_vXX.md` podle pravidel projektu.

---

## 6. Jak stránka funguje (pro odpovědi na Martinovy dotazy)

- **Horní panel:** název · verze, barvy (černá, modrá, červená, zelená, růžová), Pero, Prst (kreslení prstem), Guma, PDF.
- **Kreslení:** Apple Pencil kreslí, prst posouvá stránku. Zpět a Smazat jsou u každé plochy.
- **Odpovědi:** klávesnice. Čárka i tečka jsou v pořádku, mezery nevadí.
- **PDF:** jedno klepnutí vytvoří PDF a otevře sdílení na iPadu. Kdyby ho iPad zablokoval, tlačítko zezelená na „Uložit PDF“ a stačí klepnout znovu. Po každé změně se PDF vytvoří znovu. Název: `Test_<tema>_vXX_<datum>_NN.pdf`, kde NN je pořadové číslo uložení.
- **Neukládá se:** odpovědi a kresby se po zavření stránky ztratí. Před zavřením je potřeba uložit PDF.
