#!/usr/bin/env python3
"""
AP09: el proceso de nomina llega ahora como "P2P" y como "P2P Vuelta".

1. Payroll!K2:K5000  -> IF($Fr="P2P",...) pasa a IF(LEFT($Fr,3)="P2P",...)
   para que ambas variantes bajen por la rama AP (subproceso/equipo).
2. Payroll!K176:K180 -> faltaban las 5 celdas (se pegaron datos encima y
   se borro la formula). Se reponen.
3. DS Reconciliation B4,B5,B6,B7,B9:B17 y IP Reconciliation B4:B9
   -> el filtro Payroll!$F:$F,"P2P" pasa a "P2P*".
4. Mapping A13/B13 -> NL = AP BE. Al pasar "P2P Vuelta" por la rama AP,
   el equipo NL se queda sin categoria: solo estaba en la tabla de paises
   (NL -> BE), no en la de categorias AP. Se amplia el rango de la formula
   de $A$3:$A$12 a $A$3:$A$13.
5. Instrucciones A39 -> se documenta la regla.

Edicion directa del XML: openpyxl destruiria Power Query.
"""
import re, shutil, zipfile, sys

SRC = "/tmp/claude-0/-home-user-angela/a1c2222b-76f0-5b30-92dd-06e641a27042/scratchpad/ap09/AP09.xlsx"
OUT = "/home/user/angela/FTE_Scorecard_vs_nomina_FORMULADO.xlsx"

KTPL = ('IF($D{r}="","",IFERROR(INDEX(Mapping!$H$3:$H$32,MATCH($B{r},Mapping!$G$3:$G$32,0)),'
        'IF(LEFT($F{r},3)="P2P",'
        'IFERROR(INDEX(Mapping!$E$3:$E$6,MATCH($G{r},Mapping!$D$3:$D$6,0)),'
        'IFERROR(INDEX(Mapping!$B$3:$B$13,MATCH($J{r},Mapping!$A$3:$A$13,0)),"(unmapped)")),'
        'IFERROR(INDEX(Mapping!$B$17:$B$22,MATCH($F{r},Mapping!$A$17:$A$22,0)),$F{r})&" "&'
        'IF($G{r}="Banking","Banking",'
        'IFERROR(INDEX(Mapping!$E$17:$E$28,MATCH($J{r},Mapping!$D$17:$D$28,0)),"(unmapped)")))))')

NOTA = ("  El proceso puede venir como 'P2P' o como 'P2P Vuelta': las formulas tratan "
        "las dos variantes como P2P (cualquier proceso que empiece por P2P), de modo que "
        "esas personas caen en las filas AP igual que el resto.")

zin = zipfile.ZipFile(SRC)
parts = {n: zin.read(n) for n in zin.namelist()}
order = [n for n in zin.namelist()]
zin.close()
log = []

# ---------------------------------------------------------------- 1 y 2: Payroll
s = parts['xl/worksheets/sheet4.xml'].decode('utf8')

s, n = re.subn(r'IF\(\$F(\d+)="P2P",', r'IF(LEFT($F\1,3)="P2P",', s)
log.append(f"Payroll K: IF($Fr=\"P2P\") -> IF(LEFT($Fr,3)=\"P2P\")  en {n} celdas")
assert n == 4994, n

# el rango de la tabla Team -> categoria AP crece una fila (entra NL)
for a, b in (('Mapping!$B$3:$B$12', 'Mapping!$B$3:$B$13'),
             ('Mapping!$A$3:$A$12', 'Mapping!$A$3:$A$13')):
    s, n = re.subn(re.escape(a), b, s)
    assert n == 4994, (a, n)
log.append("Payroll K: rango Team->AP ampliado a $A$3:$A$13 / $B$3:$B$13  en 4994 celdas")

for rn in (176, 177, 178, 179, 180):
    assert f'<c r="K{rn}"' not in s, f"K{rn} ya existe"
    f = KTPL.format(r=rn).replace('&', '&amp;')
    cell = f'<c r="K{rn}" t="str"><f>{f}</f></c>'
    m = re.search(r'<row r="%d"[^>]*>.*?</row>' % rn, s, re.S)
    assert m, rn
    row = m.group(0)
    s = s[:m.start()] + row[:-len('</row>')] + cell + '</row>' + s[m.end():]
log.append("Payroll K176:K180: 5 celdas repuestas (estaban vacias)")

parts['xl/worksheets/sheet4.xml'] = s.encode('utf8')

# ------------------------------------------- 3: filtros de proceso en los cuadres
for part, sheet, exp in (('xl/worksheets/sheet1.xml', 'DS Reconciliation', 13),
                         ('xl/worksheets/sheet2.xml', 'IP Reconciliation', 6)):
    t = parts[part].decode('utf8')
    t, n = re.subn(re.escape('Payroll!$F:$F,"P2P"'), 'Payroll!$F:$F,"P2P*"', t)
    assert n == exp, (sheet, n, exp)
    log.append(f'{sheet}: filtro "P2P" -> "P2P*"  en {n} SUMIFS')
    parts[part] = t.encode('utf8')

# --------------------------------------------- 4: Mapping A13/B13 = NL / AP BE
mp = parts['xl/worksheets/sheet6.xml'].decode('utf8')
ss0 = parts['xl/sharedStrings.xml'].decode('utf8')
sis0 = re.findall(r'<si>.*?</si>', ss0, re.S)


def idx_cadena(texto):
    """indice de una cadena ya existente en sharedStrings (se reutiliza)"""
    for i, si in enumerate(sis0):
        t = re.findall(r'<t[^>]*>(.*?)</t>', si, re.S)
        if len(t) == 1 and t[0] == texto:
            return i
    return None


for ref in ('A13', 'B13'):
    assert f'<c r="{ref}"' not in mp, f"Mapping {ref} ya tiene contenido"
i_nl, i_be = idx_cadena('NL'), idx_cadena('AP BE')
assert i_nl is not None and i_be is not None, (i_nl, i_be)
m12 = re.search(r'<c r="A12"([^>]*)>', mp)
est = re.search(r's="(\d+)"', m12.group(1))
est = f' s="{est.group(1)}"' if est else ''
m13 = re.search(r'<row r="13"[^>]*>', mp)
assert m13, "no existe la fila 13 de Mapping"
etiqueta = m13.group(0)
# A13/B13 van al principio de la fila: el orden de columnas tiene que ser A,B,I
nuevas = (f'<c r="A13"{est} t="s"><v>{i_nl}</v></c>'
          f'<c r="B13"{est} t="s"><v>{i_be}</v></c>')
sp = re.search(r'spans="(\d+):(\d+)"', etiqueta)
if sp and int(sp.group(1)) > 1:
    etiqueta = etiqueta.replace(sp.group(0), f'spans="1:{sp.group(2)}"')
mp = mp[:m13.start()] + etiqueta + nuevas + mp[m13.end():]
parts['xl/worksheets/sheet6.xml'] = mp.encode('utf8')
log.append(f"Mapping A13/B13: NL -> AP BE  (sharedStrings {i_nl} y {i_be} reutilizadas)")

# ------------------------------------------------------- 5: Instrucciones A39
ins = parts['xl/worksheets/sheet7.xml'].decode('utf8')
m = re.search(r'<c r="A39"[^>]*t="s"[^>]*><v>(\d+)</v></c>', ins)
assert m, "A39 no es sharedString"
old_idx = int(m.group(1))
ss = parts['xl/sharedStrings.xml'].decode('utf8')
sis = re.findall(r'<si>.*?</si>', ss, re.S)
old_si = sis[old_idx]
txt = re.search(r'<t[^>]*>(.*?)</t>', old_si, re.S).group(1)
new_txt = txt + NOTA.replace('&', '&amp;')
new_si = f'<si><t xml:space="preserve">{new_txt}</t></si>'
new_idx = len(sis)
ss = ss.replace('</sst>', new_si + '</sst>')
ss = re.sub(r'(<sst[^>]*?)count="(\d+)"', lambda g: g.group(1) + 'count="%d"' % (int(g.group(2)) + 1), ss, count=1)
ss = re.sub(r'uniqueCount="(\d+)"', lambda g: 'uniqueCount="%d"' % (int(g.group(1)) + 1), ss, count=1)
parts['xl/sharedStrings.xml'] = ss.encode('utf8')
ins = ins[:m.start()] + m.group(0).replace(f'<v>{old_idx}</v>', f'<v>{new_idx}</v>') + ins[m.end():]
parts['xl/worksheets/sheet7.xml'] = ins.encode('utf8')
log.append(f"Instrucciones A39: nota P2P/P2P Vuelta (sharedString {old_idx} -> {new_idx})")

# ---------------------------------- recalculo completo al abrir + fuera calcChain
wb = parts['xl/workbook.xml'].decode('utf8')
assert 'fullCalcOnLoad' not in wb
wb = re.sub(r'<calcPr([^>]*?)/>', r'<calcPr\1 fullCalcOnLoad="1"/>', wb, count=1)
parts['xl/workbook.xml'] = wb.encode('utf8')

if 'xl/calcChain.xml' in parts:
    del parts['xl/calcChain.xml']
    order = [n for n in order if n != 'xl/calcChain.xml']
    ct = parts['[Content_Types].xml'].decode('utf8')
    ct = re.sub(r'<Override PartName="/xl/calcChain\.xml"[^>]*/>', '', ct)
    parts['[Content_Types].xml'] = ct.encode('utf8')
    rl = parts['xl/_rels/workbook.xml.rels'].decode('utf8')
    rl = re.sub(r'<Relationship[^>]*Target="calcChain\.xml"[^>]*/>', '', rl)
    parts['xl/_rels/workbook.xml.rels'] = rl.encode('utf8')
    log.append("calcChain.xml eliminado + fullCalcOnLoad=1 (evita el aviso de reparacion)")

zout = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
for n in order:
    zout.writestr(n, parts[n])
zout.close()

print("\n".join("  - " + l for l in log))
print("\nEscrito:", OUT)
