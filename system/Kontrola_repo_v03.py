#!/usr/bin/env python3
"""Kontrola celého repozitáře Ann School (system/Kontrola_repo_vXX.py).

Použití (z rootu repozitáře, PŘED KAŽDÝM PUSHEM):
    python3 system/Kontrola_repo_v03.py

Rychlá statická kontrola (bez prohlížeče, pár sekund). Doplňuje Kontrola_testu_vXX.py (ta zkouší test v Playwrightu).
Ověří:
  1. strukturu: <předmět>/<tema>_<typ>_vXX.<html|pdf>, v rootu jen soubory se stálou adresou a jak-to-funguje_vXX.html,
  2. verze: ke každému tématu a typu (a souboru v system/) jen jedna verze mimo archiv; archiv plochý,
     název <složka>-<původní název>, v archivu není vyšší verze než aktuální,
  3. testy: blok mimo „KONFIGURACE TESTU“ je shodný s aktuální šablonou (nebo s archivní v17+ → VAROVÁNÍ),
     TEST.version a TEST.topic sedí s názvem souboru, výběry: žádné prázdné ani dvojité možnosti,
     index odpovědi v rozsahu, méně než 5 možností = CHYBA u šablony v18+ (VAROVÁNÍ u starších),
     nepoužívané volby (finalScratch, sideScratch, scratch) a zastaralé texty (VAROVÁNÍ),
  4. sledování: stránky s teorií (HTML mimo testy) načítají zaznam.js a sledovani.js se správným data-typ,
     materiál, tahák, pracovní list a zápisky mají tlačítka Chápu / Nechápu (data-porozumeni) – v02, VAROVÁNÍ,
     testy sledovani.js nenačítají, ENDPOINT v zaznam.js je vyplněný,
  4a. stránky s teorií na šabloně (v03, od 03.11.2026): materiál a zápisky mají být na aktuální
     system/Sablona_material_vXX.html – kód mimo bloky HLAVIČKA a OBSAH shodný se šablonou (jiná verze šablony
     nebo žádná = VAROVÁNÍ), každá kapitola mimo přílohy má aspoň jednu sekci s Chápu / Nechápu (CHYBA),
     data-porozumeni jen uvnitř kapitol a jednoznačné (CHYBA), název sekce začíná číslem kapitoly (VAROVÁNÍ),
     nevyrenderovaný LaTeX ($…$) mimo skripty a komentáře (CHYBA), sekce s pravidlem (.rule) bez příkladu
     na konkrétních číslech (.prakticky) – VAROVÁNÍ,
  5. rozcestník: každé téma, typ a předmět má český název v NAZVY v index.html,
  6. vlastní materiály jsou HTML (PDF jen sešit, školní materiály a starší vlastní PDF ze seznamu níže),
  7. jméno: „Ann“ v souborech pro Ann (složky předmětů) = CHYBA, jinde mimo archiv VAROVÁNÍ,
  8. odkazy: místní href/src v HTML vedou na existující soubory,
  9. velikost: soubory nad 1,5 MB (VAROVÁNÍ).
Skončí „Repozitář bez chyb.“ (kód 0), jinak vypíše CHYBY (kód 1). VAROVÁNÍ chybou nejsou, ale ber je vážně.
Potřebuje Node (pro načtení konfigurace testů).
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
CHYBY, VAROVANI = [], []
chyba = CHYBY.append
varovani = VAROVANI.append

ROOT_STALE = {"index.html", "vysledky.html", "zarizeni.html", "README.md", ".gitignore", ".nojekyll", "CNAME"}
ROOT_VERZOVANE = re.compile(r"^jak-to-funguje_v\d\d\.html$")
SOUBOR = re.compile(r"^([a-z0-9-]+)_([a-z0-9-]+)_v(\d\d)\.(html|pdf)$")
SYSTEM = re.compile(r"^([A-Za-z_]+?)_v(\d\d)\.(md|html|py|gs|js)$")
# starší vlastní PDF materiály (před 01.11.2026) – smí zůstat, nové verze už jen HTML
STARSI_PDF = {"fyzika/prevody-jednotek_material_v02.pdf", "fyzika/vektory_material_v02.pdf",
              "matematika/prirozena-a-cela-cisla_material_v01.pdf"}
TEORIE_TYPY = ("material", "tahak", "pracovni-list", "simulator", "zapisky")
ZASTARALE = ["pdf.html", "sideScratch", "finalScratch", "režim „Prst“", "Vpravo od příkladů"]
POVOLENE = [{"ano", "ne"}, {"skalár", "vektor"}, {"doprava", "doleva"}, {"nahoru", "dolů"}, {"<", "=", ">"},
            {"na východ", "na západ"}, {"na sever", "na jih"}, {"pravda", "nepravda"},
            {"komutativní", "asociativní", "distributivní"}, {"prvočíslo", "složené číslo", "ani prvočíslo, ani složené"}]
ZAC, KON = "/* =====================================================================\n   KONFIGURACE TESTU", \
    "/* ===================== KONEC KONFIGURACE ===================== */"


def soubory():
    out = []
    for d, ds, fs in os.walk("."):
        ds[:] = [x for x in ds if x != ".git" and x != "node_modules"]
        for f in fs:
            out.append(os.path.relpath(os.path.join(d, f), ".").replace(os.sep, "/"))
    return sorted(out)


def precti(p):
    with open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def rozdel(t):
    try:
        a, b = t.index(ZAC), t.index(KON)
    except ValueError:
        return None, None, None
    return t[:a], t[a:b], t[b:]


VSE = soubory()
predmety = sorted({p.split("/")[0] for p in VSE if "/" in p and p.split("/")[0] not in ("system", "archiv")})

# ---------- 1) struktura ----------
for p in VSE:
    casti = p.split("/")
    if len(casti) == 1:
        if p not in ROOT_STALE and not ROOT_VERZOVANE.match(p):
            chyba(f"root: nečekaný soubor {p} (v rootu jen index.html, vysledky.html, zarizeni.html, README.md, jak-to-funguje_vXX.html)")
    elif casti[0] == "archiv":
        if len(casti) > 2:
            chyba(f"archiv není plochý: {p}")
    elif casti[0] == "system":
        pass
    elif len(casti) != 2:
        chyba(f"soubor pro Ann musí ležet přesně o jednu složku pod rootem: {p}")
    elif not SOUBOR.match(casti[1]):
        chyba(f"název neodpovídá <tema>_<typ>_vXX.<html|pdf>: {p}")
    if re.search(r"(_tmp|~$|\.bak$|\.orig$|copy|kopie|\.xlsx$|\.docx$|\.DS_Store$)", p, re.I) and not p.startswith(".git"):
        chyba(f"pracovní nebo duplicitní soubor: {p}")

# ---------- 2) verze ----------
aktualni = {}
for p in VSE:
    c = p.split("/")
    if len(c) == 2 and c[0] not in ("system", "archiv"):
        m = SOUBOR.match(c[1])
        if m:
            aktualni.setdefault((c[0], m.group(1), m.group(2)), []).append((int(m.group(3)), p))
    elif len(c) == 1 and ROOT_VERZOVANE.match(p):
        aktualni.setdefault(("", "jak-to-funguje", ""), []).append((int(p[-7:-5]), p))
    elif len(c) == 2 and c[0] == "system":
        m = SYSTEM.match(c[1])
        if m:
            aktualni.setdefault(("system", m.group(1), ""), []).append((int(m.group(2)), p))
for k, v in aktualni.items():
    if len(v) > 1:
        chyba(f"víc verzí mimo archiv: {', '.join(x[1] for x in sorted(v))} – starší přesuň git mv do archiv/")
for p in VSE:
    if not p.startswith("archiv/") or p == "archiv/README.md":
        continue
    jm = p.split("/")[1]
    m = re.match(r"^([a-z0-9]+|system)-(.+)$", jm)
    if not m:
        chyba(f"archiv: název není <složka>-<původní název>: {p}")
        continue
    slozka, puvodni = m.groups()
    ma = SOUBOR.match(puvodni) if slozka != "system" else SYSTEM.match(puvodni)
    if not ma:
        continue
    if slozka == "system":
        klic, ver = ("system", ma.group(1), ""), int(ma.group(2))
    elif slozka == "jak":
        continue
    else:
        klic, ver = (slozka, ma.group(1), ma.group(2)), int(ma.group(3))
    if klic in aktualni and ver >= max(x[0] for x in aktualni[klic]):
        chyba(f"archiv obsahuje stejnou nebo vyšší verzi než aktuální: {p}")

# ---------- 3) testy ----------
sablony = {}
for p in VSE:
    m = re.search(r"Sablona_test_v(\d\d)\.html$", p)
    if m:
        sablony[int(m.group(1))] = p
nejvyssi = max(int(re.search(r"v(\d\d)", p).group(1)) for p in VSE if re.match(r"system/Sablona_test_v\d\d\.html$", p))
sab_obal = {}
for v, p in sablony.items():
    a, _, b = rozdel(precti(p))
    if a is not None:
        sab_obal[v] = a + b

NODE = r"""
const fs = require("fs"), vm = require("vm");
const out = {};
for (const p of JSON.parse(process.argv[1])) {
  const t = fs.readFileSync(p, "utf8");
  const a = t.indexOf("const TEST = {"), b = t.indexOf("/* ===================== KONEC KONFIGURACE");
  try {
    const ctx = { fmt: n => String(n), Math, out: null };
    vm.runInNewContext(t.slice(a, b) + "; out = TEST;", ctx);
    const T = ctx.out;
    const qs = typeof T.generate === "function" ? T.generate() : T.questions;
    out[p] = { version: T.version, topic: T.topic, intro: T.intro || "", keys: Object.keys(T),
      q: qs.filter(q => !(Object.keys(q).length <= 2 && "section" in q && !q.type && q.answer === undefined)).map(q => ({
        keys: Object.keys(q), vyj: q.vyjimka5 || "", text: q.text || q.before || "",
        opts: [].concat(q.options ? [{ o: q.options, a: q.answer }] : [],
          (q.fields || []).filter(f => f.options).map(f => ({ o: f.options, a: f.answer }))) })) };
  } catch (e) { out[p] = { chyba: String(e) }; }
}
console.log(JSON.stringify(out));
"""
testy = [p for p in VSE if re.match(r"^[a-z0-9-]+/[a-z0-9-]+_test[a-z0-9-]*_v\d\d\.html$", p) and not p.startswith(("archiv/", "system/"))]
try:
    konf = json.loads(subprocess.run(["node", "-e", NODE, json.dumps(testy)], capture_output=True, text=True, check=True).stdout)
except Exception as e:  # noqa
    konf = {}
    chyba(f"nepodařilo se načíst konfiguraci testů přes Node ({e})")
for p in testy:
    t = precti(p)
    a, _, b = rozdel(t)
    if a is None:
        chyba(f"{p}: chybí blok KONFIGURACE TESTU")
        continue
    ver_sab = next((v for v, o in sab_obal.items() if o == a + b), None)
    if ver_sab is None:
        chyba(f"{p}: kód mimo konfiguraci se neshoduje s žádnou šablonou – šablona se v testu měnit nesmí")
    elif ver_sab != nejvyssi:
        varovani(f"{p}: na starší šabloně v{ver_sab} (aktuální v{nejvyssi})")
    if "sledovani.js" in t:
        chyba(f"{p}: test nesmí načítat sledovani.js")
    k = konf.get(p, {})
    if "chyba" in k:
        chyba(f"{p}: konfiguraci nejde načíst ({k['chyba']})")
        continue
    if not k:
        continue
    m = SOUBOR.match(p.split("/")[1])
    if k["version"] != "v" + m.group(3):
        chyba(f"{p}: TEST.version {k['version']} ≠ verze v názvu v{m.group(3)}")
    if k["topic"] != m.group(1):
        chyba(f"{p}: TEST.topic {k['topic']} ≠ téma v názvu {m.group(1)}")
    nove = ver_sab is not None and ver_sab >= 18
    for z in ZASTARALE:
        if z in k["intro"]:
            (chyba if nove else varovani)(f"{p}: zastaralý text v intro („{z}…“) – papír je pod příkladem")
    if nove and any(x in k["keys"] for x in ("finalScratch", "sideScratch")):
        chyba(f"{p}: volby finalScratch/sideScratch od šablony v18 nepatří do konfigurace")
    malo = []
    for i, q in enumerate(k["q"], 1):
        if nove and "scratch" in q["keys"]:
            chyba(f"{p}: příklad {i} má zastaralou volbu scratch")
        for f in q["opts"]:
            o = [str(x).strip() for x in f["o"]]
            low = [x.lower() for x in o]
            if any(not x for x in o):
                chyba(f"{p}: příklad {i}: prázdná možnost")
            if len(set(low)) != len(low):
                chyba(f"{p}: příklad {i}: dvě stejné možnosti {o}")
            if not (isinstance(f["a"], int) and 0 <= f["a"] < len(o)):
                chyba(f"{p}: příklad {i}: index správné možnosti {f['a']} mimo rozsah")
            if len(o) < 5 and set(low) not in POVOLENE and not q["vyj"]:
                malo.append(str(i))
    if malo:
        (chyba if nove else varovani)(f"{p}: méně než 5 možností u příkladů {', '.join(malo)}"
                                      + ("" if nove else " (starší test, jen pro informaci)"))

# ---------- 4) sledování ----------
zaznam = precti("system/lib/zaznam.js") if os.path.exists("system/lib/zaznam.js") else ""
if not re.search(r'const ENDPOINT = "https://script\.google\.com/macros/s/[^"]+/exec"', zaznam):
    chyba("system/lib/zaznam.js: ENDPOINT není vyplněný (…/exec)")
for p in VSE:
    c = p.split("/")
    if len(c) != 2 or c[0] in ("system", "archiv") or not p.endswith(".html"):
        continue
    m = SOUBOR.match(c[1])
    if not m or m.group(2).startswith("test"):
        continue
    t = precti(p)
    typ = m.group(2)
    zakl = next((x for x in TEORIE_TYPY if typ == x or typ.startswith(x + "-")), typ)
    if '<script src="../system/lib/zaznam.js"></script>' not in t:
        chyba(f"{p}: nenačítá ../system/lib/zaznam.js")
    ms = re.search(r'<script src="\.\./system/lib/sledovani\.js" data-typ="([^"]+)"></script>', t)
    if not ms:
        chyba(f"{p}: nenačítá ../system/lib/sledovani.js s data-typ")
    elif ms.group(1) not in (typ, zakl):
        chyba(f"{p}: data-typ=\"{ms.group(1)}\" neodpovídá typu ze jména ({typ})")
    elif t.index('<script src="../system/lib/zaznam.js"') > t.index('<script src="../system/lib/sledovani.js"'):
        chyba(f"{p}: sledovani.js musí být načtený až za zaznam.js")
    # v02: u každé části teorie tlačítka Chápu / Nechápu (Navod_material kap. 3 a 7)
    if zakl in ("material", "tahak", "pracovni-list", "zapisky") and "data-porozumeni=" not in t:
        varovani(f"{p}: chybí tlačítka Chápu / Nechápu (data-porozumeni) – nová verze stránky je má mít")
    # verze zobrazená v hlavičce / panelu musí sedět s verzí v názvu souboru
    hl = re.search(r"<header[^>]*>(.*?)</header>|class=\"panel-title\">(.*?)</div>", t, re.S)
    if hl:
        vv = set(re.findall(r"\bv(\d\d)\b", hl.group(1) or hl.group(2) or ""))
        if vv and vv != {m.group(3)}:
            chyba(f"{p}: v hlavičce stránky je verze v{', v'.join(sorted(vv))}, soubor je v{m.group(3)}")
    else:
        varovani(f"{p}: nenašel jsem hlavičku s verzí (<header> nebo .panel-title)")
ix = precti("index.html")
if 'sledovani.js" data-typ="rozcestnik"' not in ix:
    chyba("index.html: rozcestník nenačítá sledovani.js s data-typ=\"rozcestnik\"")
for p in ("vysledky.html", "zarizeni.html"):
    if "sledovani.js" in precti(p):
        chyba(f"{p}: nesmí načítat sledovani.js")

# ---------- 4a) stránky s teorií na šabloně (Sablona_material) ----------
HZ, HK = "<!-- ===== HLAVIČKA STRÁNKY", "<!-- ===== KONEC HLAVIČKY ===== -->"
OZ, OK = "<!-- ===== OBSAH STRÁNKY", "<!-- ===== KONEC OBSAHU ===== -->"


def obal_teorie(t):
    try:
        a, b = t.index(HZ), t.index(HK)
        c, d = t.index(OZ), t.index(OK)
    except ValueError:
        return None
    return t[:a] + t[b:c] + t[d:]


sab_teorie = {}
for p in VSE:
    m = re.search(r"Sablona_material_v(\d\d)\.html$", p)
    if m:
        o = obal_teorie(precti(p))
        if o is not None:
            sab_teorie[int(m.group(1))] = o
nejvyssi_teorie = max([int(re.search(r"v(\d\d)", p).group(1)) for p in VSE if re.match(r"system/Sablona_material_v\d\d\.html$", p)] or [0])
for p in VSE:
    c = p.split("/")
    if len(c) != 2 or c[0] in ("system", "archiv") or not p.endswith(".html"):
        continue
    m = SOUBOR.match(c[1])
    if not m or not (m.group(2) in ("material", "zapisky") or m.group(2).startswith(("material-", "zapisky-"))):
        continue
    t = precti(p)
    o = obal_teorie(t)
    ver = next((v for v, s in sab_teorie.items() if s == o), None) if o is not None else None
    if o is None:
        varovani(f"{p}: není na šabloně stránky s teorií (system/Sablona_material_v{nejvyssi_teorie:02d}.html) – nová verze má být")
        continue
    if ver is None:
        chyba(f"{p}: kód mimo bloky HLAVIČKA a OBSAH se neshoduje s žádnou šablonou stránky s teorií – šablona se měnit nesmí")
        continue
    if ver != nejvyssi_teorie:
        varovani(f"{p}: na starší šabloně stránky s teorií v{ver:02d} (aktuální v{nejvyssi_teorie:02d})")
    obsah = t[t.index(OZ):t.index(OK)]
    bez = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>|<!--[\s\S]*?-->", "", obsah)
    if re.search(r"(?<![\\&#])\$[^$\n]{1,200}\$", bez):
        chyba(f"{p}: nevyrenderovaný vzorec $…$ – spusť node system/Vzorce_v01.js")
    kap = re.findall(r'<section class="kapitola( priloha)?" data-kapitola="([^"]*)">([\s\S]*?)</section>', bez)
    if not kap:
        chyba(f"{p}: žádná kapitola <section class=\"kapitola\" data-kapitola=\"…\">")
    vsechny = re.findall(r'data-porozumeni="([^"]*)"', bez)
    v_kap = []
    for pril, nazev, telo in kap:
        casti = re.findall(r'data-porozumeni="([^"]*)"', telo)
        v_kap += casti
        if not pril and not casti:
            chyba(f"{p}: kapitola „{nazev}“ nemá žádnou sekci s Chápu / Nechápu (nebo ji označ class=\"kapitola priloha\")")
        cislo = (re.match(r"(\d+)\.", nazev) or [None, None])[1]
        for c_ in casti:
            if cislo and not c_.startswith(cislo + "."):
                varovani(f"{p}: sekce „{c_}“ nezačíná číslem své kapitoly ({cislo}.)")
        for s in re.split(r'<div class="sekce">', telo)[1:]:
            if 'class="rule"' in s and 'class="prakticky"' not in s:
                pr = re.search(r'data-porozumeni="([^"]*)"', s)
                varovani(f"{p}: sekce „{pr.group(1) if pr else '?'}“ má pravidlo (.rule), ale žádný příklad na konkrétních číslech (.prakticky)")
    if len(v_kap) != len(vsechny):
        chyba(f"{p}: data-porozumeni mimo kapitolu (patří na konec sekce uvnitř <section class=\"kapitola\">)")
    dup = sorted({x for x in vsechny if vsechny.count(x) > 1})
    if dup:
        chyba(f"{p}: stejný název sekce víckrát: {', '.join(dup)}")

# ---------- 5) rozcestník: NAZVY ----------
def klice(blok):
    return set(re.findall(r'"?([a-z0-9-]+)"?\s*:\s*"', blok))
mz = re.search(r"const NAZVY = \{(.*?)\n\};", ix, re.S)
if not mz:
    chyba("index.html: nenašel jsem NAZVY")
else:
    nz = mz.group(1)
    bloky = {k: re.search(k + r"\s*:\s*\{(.*?)\}", nz, re.S) for k in ("predmety", "temata", "typy")}
    kl = {k: klice(v.group(1)) if v else set() for k, v in bloky.items()}
    for s in predmety:
        if s not in kl["predmety"]:
            chyba(f"index.html: předmět „{s}“ nemá název v NAZVY.predmety")
    for (s, tema, typ) in aktualni:
        if s in ("", "system"):
            continue
        if tema not in kl["temata"]:
            chyba(f"index.html: téma „{tema}“ nemá název v NAZVY.temata")
        if typ not in kl["typy"]:
            chyba(f"index.html: typ „{typ}“ nemá název v NAZVY.typy")

# ---------- 6) vlastní materiály jen HTML ----------
for p in VSE:
    c = p.split("/")
    if len(c) == 2 and c[0] not in ("system", "archiv") and p.endswith(".pdf"):
        m = SOUBOR.match(c[1])
        if m and not (m.group(2).startswith("skolni-material") or m.group(1) in ("sesit", "pokyny")) and p not in STARSI_PDF:
            chyba(f"{p}: vlastní materiály jsou od 01.11.2026 jen HTML (PDF jen sešit a školní materiály)")

# ---------- 7) jméno ----------
JMENO = re.compile(r"\bAnn(?! School)\b|\bAnn[aiyěouě]\w*\b|\bAnič\w*|\bAnink\w*")
for p in VSE:
    if p.startswith(("archiv/", ".git")) or not p.endswith((".html", ".md", ".js", ".py", ".gs")) or p.endswith(".min.js"):
        continue
    t = precti(p)
    nal = sorted(set(JMENO.findall(t)))
    if not nal:
        continue
    pro_ann = len(p.split("/")) == 2 and p.split("/")[0] not in ("system", "archiv")
    if pro_ann:
        # komentáře v kódu Ann nevidí, ale repozitář je veřejný – u stránek pro Ann je to chyba
        chyba(f"{p}: obsahuje jméno ({', '.join(nal)}) – do souborů pro Ann ho nepiš")

# ---------- 8) odkazy ----------
for p in VSE:
    if not p.endswith(".html") or p.startswith("archiv/"):
        continue
    t = precti(p)
    for u in re.findall(r'(?:href|src)="([^"#?]+)', t):
        if re.match(r"^(https?:|mailto:|data:|javascript:|\$\{|\.\./system/lib/\$)", u) or "${" in u or u.startswith("//"):
            continue
        cil = os.path.normpath(os.path.join(os.path.dirname(p), u)).replace(os.sep, "/")
        if u.endswith("/") or u in ("../", "./"):
            cil = os.path.normpath(os.path.join(os.path.dirname(p), u, "index.html")).replace(os.sep, "/")
        if not os.path.exists(cil):
            chyba(f"{p}: odkaz na neexistující soubor {u}")

# ---------- 9) zastaralé texty mimo testy a velikost ----------
for p in VSE:
    if p.startswith(("archiv/", ".git")) or not p.endswith((".html", ".md", ".js")) or p in testy:
        continue
    if re.match(r"system/(Sablona_test|Sablona_material|Navod_|Pouceni_|Kontrola_repo)", p):
        continue
    t = precti(p)
    for z in ("pdf.html", "sideScratch", "finalScratch"):
        if z in t:
            varovani(f"{p}: zastaralý odkaz „{z}“")
for p in VSE:
    if not p.startswith(".git") and os.path.getsize(p) > 1.5e6:
        varovani(f"velký soubor {p} ({os.path.getsize(p) / 1e6:.1f} MB) – nahrávej znovu jen při skutečné změně")

# ---------- výpis ----------
print(f"Kontrola repozitáře: {len(VSE)} souborů, {len(testy)} testů, šablona testu v{nejvyssi}, šablona stránky s teorií v{nejvyssi_teorie:02d}.")
if VAROVANI:
    print("\nVAROVÁNÍ:")
    for v in VAROVANI:
        print("  -", v)
if CHYBY:
    print("\nCHYBY:")
    for c in CHYBY:
        print("  -", c)
    sys.exit(1)
print("\nRepozitář bez chyb.")
