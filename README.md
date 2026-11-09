# Ann School – materiály a testy

Rozcestník pro Ann: https://mjandlik.github.io/annschool/

- `index.html` – rozcestník (seznam se načítá automaticky, tlačítka „Výsledky“ a „Stáhnout ZIP“).
- `vysledky.html` – přehled výsledků testů a čtení teorie (Chápu / Nechápu, papír a texty „Vyzkoušej se“, u testů „📋 Pro Clauda“ = obrázek zadání a papíru pro rozbor chyby; data z Google tabulky, viz `system/Navod_test_vXX.md`, kap. 9).
- `zarizeni.html` – označení zařízení přezdívkou (`zarizeni.html?u=<přezdívka>`).
- `matematika/`, `fyzika/`, `chemie/` – soubory pro Ann: `<tema>_<typ>_vXX.html` (vlastní materiály a testy jsou HTML; PDF jsou jen vstupy – sešit a školní materiály).
- `system/` – šablona testu (`Sablona_test_vXX.html` – rozpracovaný test pokračuje po zavření i po „⌂ Rozcestník“, „Začít znovu“ pošle stav do výsledků jako „resetováno“, od v32 volitelně bez papíru – test pojmů), šablona stránky s teorií (`Sablona_material_vXX.html` – kapitoly s Chápu / Nechápu, „Vyzkoušej se“ – papír na psaní perem, obrázek a text jdou do výsledků, „Přeskočit bez volby“, od v04 volitelně volný přechod bez zamykání), předrenderování vzorců (`Vzorce_vXX.js`), návody pro chat (`Navod_test_vXX.md`, `Navod_material_vXX.md`), poučení z chyb (`Pouceni_vXX.md`), kontroly (`Kontrola_testu_vXX.py` – jeden test, `Kontrola_repo_vXX.py` – celý repozitář před každým pushem), skript Google tabulky, knihovny.
- `jak-to-funguje_vXX.html` – technický popis systému pro zájemce.
- `archiv/` – starší verze (plochý archiv, `<složka>-<původní název>`).

Platí vždy soubor s nejvyšší verzí `_vXX`.
