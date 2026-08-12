#!/usr/bin/env python3
"""Extrae el Balanced Scorecard del Excel (modelo de grupo) y genera un modelo
en esquema estrella listo para Power BI: Dim_KPI, Dim_Date, Fact_Scorecard."""
import openpyxl
from openpyxl.utils import get_column_letter
from datetime import datetime, date
import csv, os, json

SRC = "scorecard.xlsx"
OUT = "/home/user/angela/powerbi-scorecard"
DATA = os.path.join(OUT, "data")

wb = openpyxl.load_workbook(SRC, data_only=True)
ws = wb["Data_DE_Pack"]

# --- Perspectivas (con enunciado del objetivo, tomado de BSC_DE_Pack col B) ---
PERSPECTIVES = {
    "1": ("1. Efficient and Scalable",       "To increase efficiency and create a scalable platform"),
    "2": ("2. Customer Focused",             "To improve the customer experience"),
    "3": ("3. Robust Control and Compliance","To deliver high levels of control and compliance"),
    "4": ("4. Excellent People and Technology","To ensure staff are highly engaged and we leverage technology"),
    "5": ("5. Continuous Improvement",       "To continuously improve in everything we do"),
}

# --- Meses (fila 5, columnas K..CX) ---
month_cols = []  # (col_idx, date)
for i in range(11, 103):  # K=11 .. CX=102
    v = ws.cell(row=5, column=i).value
    if isinstance(v, datetime):
        month_cols.append((i, v.date()))

# --- Grupos KPI (header + filas de datos) ---
def build_groups():
    groups, cur = [], None
    for r in range(6, 91):
        b = ws.cell(row=r, column=2).value
        code = str(b).strip() if b is not None else ""
        if code and code[0].isdigit():
            if cur: groups.append(cur)
            cur = {"code": code, "header_row": r, "rows": [r]}
        elif cur is not None:
            cur["rows"].append(r)
    if cur: groups.append(cur)
    return groups

groups = build_groups()

# --- Config por KPI. key = header_row (para desambiguar duplicados) ---
# value_type: PCT (num/den, %) | RATE1000 | RATIO (num/den) | COUNT | CURRENCY
# dir: H (higher better) | L (lower better) | N (neutral/memo)
# num_idx/den_idx: índice dentro de group['rows'] (por defecto 0 y -1)
CFG = {
    6:  dict(code="1.1",  vt="CURRENCY", unit="€ '000",     dir="H", target=None),
    8:  dict(code="1.2",  vt="CURRENCY", unit="€ '000",     dir="H", target=None),
    10: dict(code="1.21", vt="CURRENCY", unit="€ '000",     dir="H", target=None),
    12: dict(code="1.3",  vt="COUNT",    unit="FTE",        dir="L", target=None),
    14: dict(code="1.4",  vt="RATIO",    unit="inv./FTE",   dir="H", target=None, num_idx=1, den_idx=0),
    17: dict(code="1.5",  vt="RATIO",    unit="receipts/FTE",dir="H", target=None, num_idx=1, den_idx=0),
    20: dict(code="1.6",  vt="RATIO",    unit="FTE/site",   dir="L", target=None),
    22: dict(code="2.1",  vt="PCT",      unit="%",          dir="H", target=0.90),
    24: dict(code="2.2",  vt="PCT",      unit="%",          dir="L", target=None),
    26: dict(code="2.3",  vt="PCT",      unit="%",          dir="L", target=None),
    28: dict(code="2.4",  vt="COUNT",    unit="adjustments",dir="L", target=0),
    29: dict(code="2.41", vt="PCT",      unit="%",          dir="H", target=1.0),
    38: dict(code="2.5",  vt="PCT",      unit="%",          dir="H", target=0.70, include=False),  # archived May-20
    40: dict(code="2.51", vt="PCT",      unit="%",          dir="H", target=0.70),
    42: dict(code="2.52", vt="PCT",      unit="%",          dir="N", target=None),
    44: dict(code="2.6",  vt="PCT",      unit="%",          dir="H", target=0.75),
    46: dict(code="2.7",  vt="CURRENCY", unit="€ '000",     dir="L", target=None),
    47: dict(code="2.71", vt="CURRENCY", unit="€ '000",     dir="L", target=None),
    49: dict(code="2.8",  vt="RATIO",    unit="journals/site",dir="L", target=70),
    51: dict(code="2.9",  vt="COUNT",    unit="journals",   dir="N", target=None),
    53: dict(code="2.10", vt="COUNT",    unit="journals",   dir="N", target=None),
    55: dict(code="2.99", vt="PCT",      unit="%",          dir="H", target=1.0),
    57: dict(code="3.1",  vt="COUNT",    unit="adjustments",dir="L", target=0),
    58: dict(code="3.2",  vt="COUNT",    unit="accounts",   dir="L", target=0),
    59: dict(code="3.3",  vt="COUNT",    unit="invoices",   dir="L", target=None),
    60: dict(code="3.31", vt="COUNT",    unit="invoices",   dir="L", target=None),
    62: dict(code="3.32", vt="RATE1000", unit="per 1,000 inv.",dir="L", target=None),
    64: dict(code="3.33", vt="PCT",      unit="%",          dir="H", target=None, num_idx=0, den_idx=-1),
    68: dict(code="3.4",  vt="PCT",      unit="%",          dir="L", target=0.1605),
    70: dict(code="3.5",  vt="PCT",      unit="%",          dir="L", target=0.0999),
    72: dict(code="3.6",  vt="PCT",      unit="%",          dir="H", target=0.9700),
    74: dict(code="4.1",  vt="PCT",      unit="%",          dir="H", target=0.9747),
    76: dict(code="4.11", vt="PCT",      unit="%",          dir="H", target=None),
    78: dict(code="4.12", vt="PCT",      unit="%",          dir="H", target=None),
    80: dict(code="4.2",  vt="PCT",      unit="%",          dir="H", target=0.65),
    82: dict(code="4.3",  vt="PCT",      unit="%",          dir="L", target=None),
    84: dict(code="5.1",  vt="COUNT",    unit="KPIs",       dir="H", target=None),
    85: dict(code="5.2",  vt="COUNT",    unit="opportunities",dir="H", target=None),
    87: dict(code="5.3",  vt="COUNT",    unit="opportunities",dir="H", target=None),
    89: dict(code="5.4",  vt="COUNT",    unit="opportunities",dir="H", target=None),
}

def cell(r, c): return ws.cell(row=r, column=c).value
def num(v):
    return v if isinstance(v, (int, float)) else None

dim_kpi = []   # dict rows
fact = []      # (KPI_ID, Date, Numerator, Denominator)
seen_codes = set()

for g in groups:
    hr = g["header_row"]
    if hr not in CFG:
        continue
    cfg = CFG[hr]
    if cfg.get("include", True) is False:
        continue
    code = cfg["code"]
    if code in seen_codes:  # solo el primer grupo de códigos duplicados (p.ej. 2.41)
        continue
    seen_codes.add(code)

    persp_key = code.split(".")[0]
    persp_name, persp_obj = PERSPECTIVES[persp_key]
    measure    = cell(hr, 6) or ""
    objective  = cell(hr, 4) or ""      # D = Objective (subtema)
    process    = cell(hr, 5) or "All"   # E = Process
    definition = cell(hr, 9) or ""      # I = Definitions

    rows = g["rows"]
    # nº de celdas numéricas por fila (para localizar dónde vive el dato)
    def row_datacount(r):
        return sum(1 for ci, _ in month_cols if isinstance(cell(r, ci), (int, float)))
    data_rows = [r for r in rows if row_datacount(r) > 0]

    is_ratio = cfg["vt"] in ("PCT", "RATE1000", "RATIO")
    if "num_idx" in cfg:                      # override explícito (p.ej. 1.4 productividad)
        num_row = rows[cfg["num_idx"]]
        den_row = rows[cfg["den_idx"]] if "den_idx" in cfg else None
        if den_row == num_row:
            den_row = None
    elif is_ratio:                            # ratio: 1ª fila con datos / última fila con datos
        num_row = data_rows[0] if data_rows else rows[0]
        den_row = data_rows[-1] if len(data_rows) > 1 else None
    else:                                     # COUNT / CURRENCY: la fila poblada (o la cabecera)
        num_row = data_rows[0] if data_rows else rows[0]
        den_row = None

    has_data = False
    for ci, d in month_cols:
        n = num(cell(num_row, ci))
        dd = num(cell(den_row, ci)) if den_row else None
        if n is None and dd is None:
            continue
        has_data = True
        fact.append((code, d.isoformat(), n, dd))

    dim_kpi.append(dict(
        KPI_ID=code,
        Perspective=persp_name,
        Perspective_Objective=persp_obj,
        Objective=str(objective).strip(),
        Process=str(process).strip(),
        Measure=str(measure).strip(),
        Definition=str(definition).strip().replace("\n", " "),
        Value_Type=cfg["vt"],
        Unit=cfg["unit"],
        Direction=cfg["dir"],
        Target=cfg["target"],
        Has_Data="Yes" if has_data else "No",
    ))

# --- Dim_Date (cubre todo el rango de meses + margen) ---
all_dates = sorted({date.fromisoformat(f[1]) for f in fact}) or [d for _, d in month_cols]
dmin, dmax = min(all_dates), max(all_dates)
dim_date = []
y, m = dmin.year, dmin.month
while (y < dmax.year) or (y == dmax.year and m <= dmax.month):
    dt = date(y, m, 1)
    fy_start = y if m >= 5 else y - 1   # año fiscal DS Smith: mayo–abril
    dim_date.append(dict(
        Date=dt.isoformat(),
        Year=y, Month=m,
        Month_Name=dt.strftime("%b %Y"),
        Quarter=f"Q{(m-1)//3+1}",
        Fiscal_Year=f"FY{str(fy_start)[2:]}/{str(fy_start+1)[2:]}",
        Month_Index=y*12+m,
    ))
    m += 1
    if m > 12: m = 1; y += 1

# --- Escritura CSV ---
def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows: w.writerow(r)

write_csv(os.path.join(DATA, "Dim_KPI.csv"), dim_kpi,
          ["KPI_ID","Perspective","Perspective_Objective","Objective","Process",
           "Measure","Definition","Value_Type","Unit","Direction","Target","Has_Data"])
fact_rows = [dict(KPI_ID=a, Date=b, Numerator=c, Denominator=d) for (a,b,c,d) in fact]
write_csv(os.path.join(DATA, "Fact_Scorecard.csv"), fact_rows,
          ["KPI_ID","Date","Numerator","Denominator"])
write_csv(os.path.join(DATA, "Dim_Date.csv"), dim_date,
          ["Date","Year","Month","Month_Name","Quarter","Fiscal_Year","Month_Index"])

print("KPIs:", len(dim_kpi), "| con datos:", sum(1 for k in dim_kpi if k["Has_Data"]=="Yes"))
print("Fact rows:", len(fact), "| Date rows:", len(dim_date))
print("Rango:", dmin, "->", dmax)

# guardar para el preview
with open("/tmp/claude-0/-home-user-angela/542e5d62-8f9d-5cfe-856e-1fd0725bcb15/scratchpad/model.json","w") as f:
    json.dump({"dim_kpi":dim_kpi,"fact":fact,"months":[d.isoformat() for _,d in month_cols]}, f, default=str)
print("OK")
