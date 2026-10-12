# Návod: studijní materiál (PDF) pro Ann (system/Navod_material_v01)

Postup pro chat v projektu „Ann School“ při tvorbě studijního materiálu, taháku nebo pracovního listu v PDF.
Struktura repozitáře, pojmenování, archiv a rozcestník jsou stejné jako v `system/Navod_test_vXX.md` (oddíly 0, 2, 5, 6).

---

## 1. Doptání

- Z projektu načti aktuální látku (`<předmět>/<téma>_vXX.md`) a podklady od Martina (sešit, pracovní listy).
- Zeptej se na to, co není jasné: rozsah látky, jestli materiál obsahuje i procvičování a výsledky, a jestli jsou potřeba úlohy na rýsování.
- Nic nevytvářej, dokud Martin neodpoví nebo nepotvrdí návrh.

---

## 2. Styl (vzor: fyzika/prevody-jednotek_material_v02.pdf)

- Nejdřív teorie, potom příklady. Oddíly odděluj jen vodorovnou čarou.
- Jednoduchý a přehledný styl, bez rámečků, boxů a barevných podkladů.
- Formát A4. Ann PDF čte na iPadu, proto čitelné písmo (základní text 11–12 pt) a rozumné okraje.
- Úlohy na rýsování dávej na čtverečkovanou síť s uvedeným měřítkem.
- Vzorce správně sazené (např. přes matplotlib mathtext nebo Unicode), česká terminologie, desetinná čárka, jednotky SI.
- Vše musí být fyzikálně a matematicky správně, i když sešit obsahuje chybu. Opravy uveď v poznámce.

---

## 3. Tvorba

1. Načti skill `pdf` a podle něj PDF vytvoř (např. reportlab). Kvůli češtině použij písmo s diakritikou (např. DejaVu Sans).
2. Soubor: `<předmět>/<tema>_material_vXX.pdf` (tahák a teorie) nebo `<předmět>/<tema>_pracovni-list_vXX.pdf`.
3. Existuje-li starší verze, přesuň ji `git mv` do `archiv/<předmět>-<tema>_material_vXX.pdf`.

---

## 4. Kontrola (povinná)

1. Přepočítej všechny výsledky v Pythonu.
2. Vyrenderuj stránky do PNG (`pdftoppm -r 60 -png`) a prohlédni je: diakritika, vzorce, zalomení stran, síť.

---

## 5. Zveřejnění

- Postupuj podle `Navod_test_vXX.md`, oddíly 5 a 6: název tématu do rozcestníku, commit, push a odkaz pro Martina.
- Odkaz: `https://mjandlik.github.io/annschool/<předmět>/<tema>_material_vXX.pdf`.
- Příklady z materiálu ulož do projektu Claude jako novou verzi `<předmět>/<téma>_vXX.md`.
