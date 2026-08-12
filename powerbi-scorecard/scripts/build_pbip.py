#!/usr/bin/env python3
"""Genera el proyecto Power BI (PBIP) que se abre directamente en Power BI
Desktop: modelo semántico (TMSL) con las 3 tablas, relaciones y TODAS las
medidas ya incrustadas, más un informe base con una página vacía.

La fuente de datos es un parámetro `SourceFile` (ruta al Scorecard_Model.xlsx).
Al abrir el .pbip, ajusta ese parámetro a tu ruta local y pulsa Actualizar."""
import json, os, sys, uuid, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measures_def import MEASURES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PBIP = os.path.join(ROOT, "pbip")
SM = os.path.join(PBIP, "Scorecard.SemanticModel")
RP = os.path.join(PBIP, "Scorecard.Report")
# Limpia solo las carpetas de artefactos (conserva pbip/README.md y otros).
for d in (SM, RP):
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d, exist_ok=True)

# ---- esquema de las tablas: (col, dataType TMSL, tipo M, summarizeBy) ----
SCHEMA = {
    "Dim_KPI": [
        ("KPI_ID","string","type text","none"),
        ("Perspective","string","type text","none"),
        ("Perspective_Objective","string","type text","none"),
        ("Objective","string","type text","none"),
        ("Process","string","type text","none"),
        ("Measure","string","type text","none"),
        ("Definition","string","type text","none"),
        ("Value_Type","string","type text","none"),
        ("Unit","string","type text","none"),
        ("Direction","string","type text","none"),
        ("Target","double","type number","none"),
        ("Has_Data","string","type text","none"),
    ],
    "Dim_Date": [
        ("Date","dateTime","type datetime","none"),
        ("Year","int64","Int64.Type","none"),
        ("Month","int64","Int64.Type","none"),
        ("Month_Name","string","type text","none"),
        ("Quarter","string","type text","none"),
        ("Fiscal_Year","string","type text","none"),
        ("Month_Index","int64","Int64.Type","none"),
    ],
    "Fact_Scorecard": [
        ("KPI_ID","string","type text","none"),
        ("Date","dateTime","type datetime","none"),
        ("Numerator","double","type number","sum"),
        ("Denominator","double","type number","sum"),
    ],
}

def m_partition(table):
    types = ", ".join(f'{{"{c}", {mt}}}' for c, _, mt, _ in SCHEMA[table])
    return [
        "let",
        "    Source = Excel.Workbook(File.Contents(SourceFile), null, true),",
        f'    Nav = Source{{[Item="{table}",Kind="Table"]}}[Data],',
        f"    Typed = Table.TransformColumnTypes(Nav, {{{types}}})",
        "in",
        "    Typed",
    ]

def table_obj(name):
    cols = [{"name": c, "dataType": dt, "sourceColumn": c, "summarizeBy": sb}
            for c, dt, _, sb in SCHEMA[name]]
    return {
        "name": name,
        "columns": cols,
        "partitions": [{"name": name, "mode": "import",
                        "source": {"type": "m", "expression": m_partition(name)}}],
    }

# Las medidas se alojan en Fact_Scorecard (tabla con datos reales). Una tabla
# "solo-medidas" vacía no la admiten todas las versiones de Power BI Desktop.
def measure_objs():
    out = []
    for name, fmt, lines in MEASURES:
        mo = {"name": name, "expression": lines}
        if fmt:
            mo["formatString"] = fmt
        out.append(mo)
    return out

source_file_param = {
    "name": "SourceFile",
    "kind": "m",
    "expression": [
        '"C:\\Users\\esangesc\\Downloads\\powerbiscorecard\\powerbi-scorecard\\data\\Scorecard_Model.xlsx"',
        '  meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]',
    ],
}

model_bim = {
    "name": "Scorecard",
    "compatibilityLevel": 1567,
    "model": {
        "culture": "en-US",
        "defaultPowerBIDataSourceVersion": "powerBI_V3",
        "sourceQueryCulture": "en-US",
        "dataAccessOptions": {"legacyRedirects": True, "returnErrorValuesAsNull": True},
        "expressions": [source_file_param],
        "tables": [table_obj("Dim_KPI"), table_obj("Dim_Date"),
                   {**table_obj("Fact_Scorecard"), "measures": measure_objs()}],
        "relationships": [
            {"name": str(uuid.uuid4()), "fromTable": "Fact_Scorecard", "fromColumn": "KPI_ID",
             "toTable": "Dim_KPI", "toColumn": "KPI_ID"},
            {"name": str(uuid.uuid4()), "fromTable": "Fact_Scorecard", "fromColumn": "Date",
             "toTable": "Dim_Date", "toColumn": "Date"},
        ],
        "annotations": [
            {"name": "PBI_QueryOrder",
             "value": json.dumps(["SourceFile", "Dim_KPI", "Dim_Date", "Fact_Scorecard"])},
        ],
    },
}

def wj(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

# ---- Semantic model (formato TMSL: model.bim en la raíz de .SemanticModel) ----
wj(os.path.join(SM, "model.bim"), model_bim)
wj(os.path.join(SM, "definition.pbism"), {"version": "4.0", "settings": {}})
wj(os.path.join(SM, ".platform"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
    "metadata": {"type": "SemanticModel", "displayName": "Scorecard"},
    "config": {"version": "2.0", "logicalId": str(uuid.uuid4())},
})

# ---- Report en formato PBIR (carpeta definition/) — una página vacía ----
# El Power BI Desktop reciente usa PBIR (por carpetas), no el report.json plano.
RPDEF = os.path.join(RP, "definition")
RPPAGES = os.path.join(RPDEF, "pages")
PAGE = "scorecard"
os.makedirs(os.path.join(RPPAGES, PAGE), exist_ok=True)

FABRIC_REPORT_DEF = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"

wj(os.path.join(RPDEF, "report.json"), {
    "$schema": f"{FABRIC_REPORT_DEF}/report/3.0.0/schema.json",
    "themeCollection": {},
    "filterConfig": {},
    "objects": {},
    "settings": {"useStylableVisualContainerHeader": True},
    "resourcePackages": [],
    "annotations": [],
})
wj(os.path.join(RPPAGES, "pages.json"), {
    "$schema": f"{FABRIC_REPORT_DEF}/pagesMetadata/1.0.0/schema.json",
    "pageOrder": [PAGE],
    "activePageName": PAGE,
})
wj(os.path.join(RPPAGES, PAGE, "page.json"), {
    "$schema": f"{FABRIC_REPORT_DEF}/page/2.0.0/schema.json",
    "name": PAGE,
    "displayName": "Scorecard",
    "displayOption": "FitToPage",
    "height": 720,
    "width": 1280,
})

# ---- Visuales de la página (mejor esfuerzo: cada visual es un fichero PBIR
# independiente -- si alguno no renderiza en tu versión de Desktop, se borra
# su carpeta sin afectar a los demás ni al resto del proyecto). ----
VIS = os.path.join(RPPAGES, PAGE, "visuals")
FACT = "Fact_Scorecard"

def col_proj(table, col):
    return {"field": {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": col}},
            "queryRef": f"{table}.{col}", "nativeQueryRef": col}

def meas_proj(table, meas):
    return {"field": {"Measure": {"Expression": {"SourceRef": {"Entity": table}}, "Property": meas}},
            "queryRef": f"{table}.{meas}", "nativeQueryRef": meas}

def write_visual(vtype, x, y, w, h, query_state, tab_order, z=None):
    vid = str(uuid.uuid4())
    vdir = os.path.join(VIS, vid)
    os.makedirs(vdir, exist_ok=True)
    wj(os.path.join(vdir, "visual.json"), {
        "$schema": f"{FABRIC_REPORT_DEF}/visualContainer/2.4.0/schema.json",
        "name": vid,
        "position": {"x": x, "y": y, "z": z if z is not None else 1000 + tab_order,
                     "width": w, "height": h, "tabOrder": tab_order},
        "visual": {
            "visualType": vtype,
            "query": {"queryState": query_state},
            "objects": {},
            "visualContainerObjects": {},
            "drillFilterOtherVisuals": True,
        },
        "filterConfig": {},
    })
    return vid

# Segmentación por mes (columna izquierda)
write_visual("slicer", 0, 0, 170, 700,
             {"Values": {"projections": [col_proj("Dim_Date", "Month_Name")]}}, 0)

# Tarjetas de resumen (fila superior)
for i, (meas, x, w) in enumerate([
    ("% On Target", 190, 260), ("KPIs Green", 460, 200),
    ("KPIs Amber", 670, 200), ("KPIs Red", 880, 200),
]):
    write_visual("card", x, 0, w, 110,
                 {"Values": {"projections": [meas_proj(FACT, meas)]}}, i + 1)

# Tabla del scorecard (cuerpo principal)
write_visual("tableEx", 190, 130, 1090, 570, {"Values": {"projections": [
    col_proj("Dim_KPI", "Perspective"), col_proj("Dim_KPI", "Measure"),
    col_proj("Dim_KPI", "Process"), meas_proj(FACT, "KPI Value (fmt)"),
    meas_proj(FACT, "KPI Target"), meas_proj(FACT, "Trend Arrow"),
    meas_proj(FACT, "RAG Status"),
]}}, 10)

wj(os.path.join(RP, "definition.pbir"), {
    "version": "1.0",
    "datasetReference": {"byPath": {"path": "../Scorecard.SemanticModel"}},
})
wj(os.path.join(RP, ".platform"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
    "metadata": {"type": "Report", "displayName": "Scorecard"},
    "config": {"version": "2.0", "logicalId": str(uuid.uuid4())},
})

# ---- .pbip raíz ----
wj(os.path.join(PBIP, "Scorecard.pbip"), {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
    "version": "1.0",
    "artifacts": [{"report": {"path": "Scorecard.Report"}}],
    "settings": {"enableAutoRecovery": True},
})

print("PBIP generado en", PBIP)
print("Tablas:", [t["name"] for t in model_bim["model"]["tables"]])
print("Medidas (en Fact_Scorecard):", len(MEASURES))
