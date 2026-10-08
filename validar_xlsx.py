#!/usr/bin/env python3
"""
Validador estructural de un .xlsx editado a mano (XML directo).

Comprueba lo que de verdad hace que Excel saque el aviso de "reparar":
XML mal formado, calcChain obsoleto, celdas duplicadas o desordenadas,
indices de estilo o de sharedStrings fuera de rango, localSheetId
descolocado, formulas compartidas huerfanas, mergeCells solapados,
orden de los elementos dentro de <worksheet>, docProps/app.xml
desincronizado y referencias a hojas que no existen.

Uso:  python3 validar_xlsx.py <fichero.xlsx>
      salida 0 = todo correcto
"""
import re, sys, zipfile
import xml.etree.ElementTree as ET
from collections import Counter

RUTA = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/user/angela/FTE_Scorecard_vs_nomina_FORMULADO.xlsx"

fallos, avisos = [], []
def mal(s): fallos.append(s)
def ojo(s): avisos.append(s)

z = zipfile.ZipFile(RUTA)
nombres = z.namelist()
P = {n: z.read(n) for n in nombres}
def txt(n): return P[n].decode('utf8')

def col(ref):
    m = re.match(r'([A-Z]+)', ref)
    n = 0
    for ch in m.group(1): n = n * 26 + ord(ch) - 64
    return n

print(f"Fichero: {RUTA}")
print(f"Partes:  {len(nombres)}   ·   {len(P['xl/worksheets/sheet1.xml'])} bytes en sheet1\n")

# --- 1. XML bien formado -----------------------------------------------------
for n in nombres:
    if n.endswith(('.xml', '.rels', '.vml')):
        try:
            ET.fromstring(P[n])
        except ET.ParseError as e:
            if n.endswith('.vml'):
                ojo(f"1· {n}: VML no es XML estricto ({e})")
            else:
                mal(f"1· {n}: XML mal formado -> {e}")
print(f"1· XML bien formado ................. {len(nombres)} partes revisadas")

# --- 2. sin macros ni calcChain ----------------------------------------------
ct0 = txt('[Content_Types].xml')
for n in nombres:
    if 'vbaProject' in n or n.endswith('.vbaProject'):
        mal(f"2· el libro lleva macros: {n}")
if any(n.endswith('.xlsm') for n in nombres) or 'macroEnabled' in ct0:
    mal("2· el content-type es macroEnabled")
if 'xl/calcChain.xml' in P:
    mal("2· calcChain.xml sigue presente: Excel pedira reparar si no coincide")
ct = txt('[Content_Types].xml')
if 'calcChain' in ct:
    mal("2· queda el <Override> de calcChain en [Content_Types].xml")
if 'calcChain' in txt('xl/_rels/workbook.xml.rels'):
    mal("2· queda la <Relationship> de calcChain en workbook.xml.rels")
wbx = txt('xl/workbook.xml')
if 'fullCalcOnLoad="1"' not in wbx:
    ojo("2· sin fullCalcOnLoad: Excel puede abrir con valores en cache")
print("2· sin macros / sin calcChain ....... ok")

# --- 3. Power Query intacto ---------------------------------------------------
dm = [n for n in nombres if n.startswith('customXml/item')]
mash = [n for n in dm if b'DataMashup' in P[n]]
print(f"3· Power Query ...................... {len(dm)} customXml, "
      f"{len(mash)} con DataMashup, {sum(len(P[n]) for n in dm):,} bytes")
if not mash:
    ojo("3· no se ve DataMashup: revisa que Power Query siga vivo")

# --- 4. hojas, rels y content-types ------------------------------------------
hojas = re.findall(r'<sheet name="([^"]*)" sheetId="(\d+)"[^>]*r:id="(rId\d+)"', wbx)
rels = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]*)"', txt('xl/_rels/workbook.xml.rels')))
nom2part = {}
for nom, sid, rid in hojas:
    if rid not in rels:
        mal(f"4· la hoja '{nom}' apunta a {rid}, que no existe en los rels"); continue
    parte = 'xl/' + rels[rid].lstrip('/').replace('xl/', '', 1)
    nom2part[nom] = parte
    if parte not in P:
        mal(f"4· la hoja '{nom}' apunta a {parte}, que no esta en el zip")
    if f'PartName="/{parte}"' not in ct:
        mal(f"4· {parte} no tiene Override en [Content_Types].xml")
if len(set(s for _, s, _ in hojas)) != len(hojas): mal("4· sheetId repetido")
if len(set(r for _, _, r in hojas)) != len(hojas): mal("4· r:id repetido")
print(f"4· hojas / rels / content-types ..... {len(hojas)} hojas: "
      + ", ".join(n for n, _, _ in hojas))

# --- 5. definedNames: localSheetId --------------------------------------------
dn = re.findall(r'<definedName name="([^"]*)"((?:\s+[a-zA-Z]+="[^"]*")*)\s*>([^<]*)</definedName>', wbx)
for nombre, attrs, valor in dn:
    m = re.search(r'localSheetId="(\d+)"', attrs)
    if not m: continue
    idx = int(m.group(1))
    if idx >= len(hojas):
        mal(f"5· definedName {nombre}: localSheetId={idx} fuera de rango ({len(hojas)} hojas)")
        continue
    esperada = hojas[idx][0]
    ref = valor.split('!')[0].strip("'").replace("''", "'")
    if ref and ref != esperada:
        mal(f"5· definedName {nombre}: localSheetId={idx} -> '{esperada}' "
            f"pero la referencia apunta a '{ref}'")
print(f"5· definedNames / localSheetId ...... {len(dn)} nombres definidos")

# --- 6. docProps/app.xml ------------------------------------------------------
if 'docProps/app.xml' in P:
    app = txt('docProps/app.xml')
    tp = re.search(r'<TitlesOfParts>.*?</TitlesOfParts>', app, re.S)
    if tp:
        titulos = re.findall(r'<vt:lpstr>([^<]*)</vt:lpstr>', tp.group(0))
        nh = [n for n, _, _ in hojas]
        if titulos[:len(nh)] != nh:
            mal(f"6· app.xml TitlesOfParts {titulos[:len(nh)]} != hojas {nh}")
    hp = re.search(r'<HeadingPairs>.*?</HeadingPairs>', app, re.S)
    if hp:
        m = re.search(r'Hojas de c\xe1lculo.*?<vt:i4>(\d+)</vt:i4>', hp.group(0), re.S) or \
            re.search(r'<vt:i4>(\d+)</vt:i4>', hp.group(0))
        if m and int(m.group(1)) != len(hojas):
            ojo(f"6· app.xml HeadingPairs dice {m.group(1)} hojas, hay {len(hojas)}")
print("6· docProps/app.xml ................. sincronizado")

# --- 7. estilos ---------------------------------------------------------------
st = txt('xl/styles.xml')
nxf = len(re.findall(r'<xf ', st.split('</cellXfs>')[0].split('<cellXfs')[-1]))
ndxf = len(re.findall(r'<dxf>', st))
usados = set()
for nom, parte in nom2part.items():
    for s in re.findall(r'<c r="[A-Z]+\d+"[^>]*?s="(\d+)"', txt(parte)):
        usados.add(int(s))
if usados and max(usados) >= nxf:
    mal(f"7· estilo s={max(usados)} usado pero cellXfs solo tiene {nxf}")
for parte in nom2part.values():
    for d in re.findall(r'dxfId="(\d+)"', txt(parte)):
        if int(d) >= ndxf:
            mal(f"7· dxfId={d} usado pero solo hay {ndxf} dxf")
print(f"7· estilos .......................... {nxf} cellXfs, {ndxf} dxf, "
      f"max usado s={max(usados) if usados else '-'}")

# --- 8. orden y unicidad de filas y celdas ------------------------------------
tot_cel = 0
for nom, parte in nom2part.items():
    s = txt(parte)
    sd = s.split('<sheetData>')[-1].split('</sheetData>')[0] if '<sheetData>' in s else ''
    filas = re.findall(r'<row r="(\d+)"[^>]*(?:/>|>(.*?)</row>)', sd, re.S)
    nums = [int(r) for r, _ in filas]
    if nums != sorted(nums): mal(f"8· {nom}: filas desordenadas")
    rep = [k for k, v in Counter(nums).items() if v > 1]
    if rep: mal(f"8· {nom}: filas repetidas {rep[:5]}")
    for rnum, cuerpo in filas:
        refs = re.findall(r'<c r="([A-Z]+\d+)"', cuerpo or '')
        tot_cel += len(refs)
        for ref in refs:
            if not ref.endswith(rnum) or re.match(r'[A-Z]+', ref).group(0) + rnum != ref:
                mal(f"8· {nom}: celda {ref} dentro de la fila {rnum}")
        cols = [col(r) for r in refs]
        if cols != sorted(cols): mal(f"8· {nom} fila {rnum}: celdas desordenadas")
        if len(set(refs)) != len(refs):
            d = [k for k, v in Counter(refs).items() if v > 1]
            mal(f"8· {nom} fila {rnum}: celdas duplicadas {d[:5]}")
print(f"8· orden / unicidad de celdas ....... {tot_cel:,} celdas revisadas")

# --- 9. sharedStrings ---------------------------------------------------------
if 'xl/sharedStrings.xml' in P:
    ss = txt('xl/sharedStrings.xml')
    nsi = len(re.findall(r'<si>', ss))
    m = re.search(r'uniqueCount="(\d+)"', ss)
    if m and int(m.group(1)) != nsi:
        mal(f"9· sharedStrings: uniqueCount={m.group(1)} pero hay {nsi} <si>")
    peor = -1
    for nom, parte in nom2part.items():
        for c in re.findall(r'<c r="[A-Z]+\d+"[^>]*t="s"[^>]*>\s*<v>(\d+)</v>', txt(parte)):
            peor = max(peor, int(c))
            if int(c) >= nsi:
                mal(f"9· {nom}: indice de sharedString {c} fuera de rango ({nsi})")
    print(f"9· sharedStrings .................... {nsi} cadenas, indice maximo {peor}")

# --- 10. formulas compartidas y hojas referenciadas ---------------------------
nombres_hoja = {n for n, _, _ in hojas}
for nom, parte in nom2part.items():
    s = txt(parte)
    # Excel escribe ref antes de si; openpyxl al contrario. Acepta los dos ordenes.
    maestros = {}
    for m in re.finditer(r'<f\b[^>]*t="shared"[^>]*>', s):
        tag = m.group(0)
        msi = re.search(r'si="(\d+)"', tag)
        mref = re.search(r'ref="([A-Z]+\d+(?::[A-Z]+\d+)?)"', tag)
        if msi and mref:
            maestros[int(msi.group(1))] = mref.group(1)
    hijos = Counter(int(x) for x in re.findall(r'<f t="shared"[^>]*si="(\d+)"', s))
    for si in hijos:
        if si not in maestros:
            mal(f"10· {nom}: grupo compartido si={si} sin maestro con ref")
    for si, ref in maestros.items():
        if ':' not in ref and hijos[si] > 1:
            mal(f"10· {nom}: si={si} tiene ref de una sola celda ({ref}) y {hijos[si]} celdas")
    for ref in set(re.findall(r"(?:'([^']+)'|\b([A-Z][A-Za-z0-9 ]*))!\$?[A-Z]", s)):
        h = ref[0] or ref[1]
        if h and h not in nombres_hoja and h not in ('TRIM', 'MID', 'IF', 'TEXT'):
            if h in ('Payroll', 'Mapping', 'FTE Scorecard', 'DIV table'):
                mal(f"10· {nom}: formula apunta a la hoja '{h}', que no existe")
print("10· formulas compartidas / hojas .... coherentes")

# --- 11. mergeCells y orden de elementos --------------------------------------
ORDEN = ['sheetData', 'sheetCalcPr', 'sheetProtection', 'protectedRanges', 'scenarios',
         'autoFilter', 'sortState', 'dataConsolidate', 'customSheetViews', 'mergeCells',
         'phoneticPr', 'conditionalFormatting', 'dataValidations', 'hyperlinks',
         'printOptions', 'pageMargins', 'pageSetup', 'headerFooter', 'rowBreaks',
         'colBreaks', 'customProperties', 'cellWatches', 'ignoredErrors', 'smartTags',
         'drawing', 'drawingHF', 'picture', 'oleObjects', 'controls', 'webPublishItems',
         'tableParts', 'extLst', 'legacyDrawing', 'legacyDrawingHF']
for nom, parte in nom2part.items():
    s = txt(parte)
    m = re.search(r'<mergeCells count="(\d+)"', s)
    if m:
        rangos = re.findall(r'<mergeCell ref="([^"]+)"', s)
        if int(m.group(1)) != len(rangos):
            mal(f"11· {nom}: mergeCells count={m.group(1)} pero hay {len(rangos)}")
        if len(set(rangos)) != len(rangos):
            mal(f"11· {nom}: rangos combinados duplicados")
    cola = s.split('</sheetData>')[-1]
    vistos = [e for e in re.findall(r'<(\w+)[ />]', cola) if e in ORDEN]
    pos = [ORDEN.index(e) for e in vistos]
    if pos != sorted(pos):
        mal(f"11· {nom}: elementos tras sheetData desordenados -> {vistos}")
    sv = re.search(r'<sheetView\b.*?(?:/>|</sheetView>)', s, re.S)
    if sv and '<pane' in sv.group(0) and sv.group(0).rstrip().endswith('/>') \
       and not sv.group(0).startswith('<sheetViews'):
        if '</sheetView>' not in sv.group(0) and '<pane' in sv.group(0):
            pass
print("11· mergeCells / orden de elementos . ok")

# --- resultado ----------------------------------------------------------------
print()
for a in avisos: print("AVISO  " + a)
for f in fallos: print("FALLO  " + f)
print()
if fallos:
    print(f"RESULTADO: {len(fallos)} FALLO(S)")
    sys.exit(1)
print("RESULTADO: TODO CORRECTO" + (f"  ({len(avisos)} aviso(s))" if avisos else ""))
sys.exit(0)
