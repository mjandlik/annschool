# Návod: studijní materiál (PDF) pro Ann (system/Navod_material_v04)

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
- Každou prázdnou plochu na psaní (síť, volné místo pro výpočet) označ vlevo nahoře malým šedým písmem „Místo pro poznámky“ – stejně jako v HTML testech.
- Vzorce správně sazené (např. přes matplotlib mathtext nebo Unicode), česká terminologie, desetinná čárka, jednotky SI.
- Vše musí být fyzikálně a matematicky správně, i když sešit obsahuje chybu. Opravy uveď v poznámce.

---

## 3. Tvorba

1. Načti skill `pdf` a podle něj PDF vytvoř (např. reportlab). Kvůli češtině použij písmo s diakritikou (např. DejaVu Sans).
2. Soubor podle druhu:
   - `<předmět>/<tema>_material_vXX.pdf`: studijní materiál (teorie + příklady),
   - `<předmět>/<tema>_tahak_vXX.pdf`: krátký tahák,
   - `<předmět>/<tema>_pracovni-list_vXX.pdf`: pracovní list.
   - V rozcestníku se zobrazí ve skupině **Výukové materiály** u daného tématu.
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

---

## 6. Zápisky ze sešitu a školní materiály (nevytváří Claude)

Skeny sešitu a materiály ze školy (pracovní listy, cvičení, pokyny, řešení od učitele) se na GitHub nahrávají **beze změny obsahu**, jen přejmenované:

- Zápisky ze sešitu: `<předmět>/sesit_zapisky_vXX.pdf` – celý sešit předmětu, téma „Sešit“. Nový sken (doplněné stránky) = nová verze, stará do archivu.
- Školní materiál: `<předmět>/<tema>_skolni-material[-<podtyp>]_vXX.pdf`, např. `fyzika/prevody-jednotek_skolni-material-pracovni-list_v01.pdf`. Téma podle obsahu; víc materiálů k jednomu tématu rozliš podtypem.
- Rozcestník je řadí do skupin **Zápisky** a **Školní materiály** u tématu. Nové téma nebo podtyp doplň do `NAZVY` v `index.html` (např. `"skolni-material-pracovni-list": "Pracovní list"`).
- Duplicity a pracovní soubory (kopie v `_tmp`, xlsx) nenahrávej.
- Z těchto souborů vycházej při tvorbě vlastních materiálů a testů (látka, značení, terminologie), ale vlastní materiály musí být fyzikálně a matematicky správné i tam, kde sešit obsahuje chybu.
