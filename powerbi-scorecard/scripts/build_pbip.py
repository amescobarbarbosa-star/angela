#!/usr/bin/env python3
"""Genera el proyecto Power BI (PBIP) que se abre directamente en Power BI
Desktop: modelo semántico (TMSL) con las 3 tablas, relaciones y TODAS las
medidas ya incrustadas, más un informe base con una página vacía.

La fuente de datos es un parámetro `SourceFile` (ruta al Scorecard_Model.xlsx).
Al abrir el .pbip, ajusta ese parámetro a tu ruta local y pulsa Actualizar."""
import json, os, sys, uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measures_def import MEASURES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PBIP = os.path.join(ROOT, "pbip")
SM = os.path.join(PBIP, "Scorecard.SemanticModel")
RP = os.path.join(PBIP, "Scorecard.Report")
for d in (SM, RP):
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

# ---- Report (una página vacía; los visuales se montan con la guía) ----
report_config = {
    "version": "5.50",
    "activeSectionIndex": 0,
    "settings": {"useStylableVisualContainerHeader": True},
}
report_json = {
    "config": json.dumps(report_config),
    "layoutOptimization": 0,
    "sections": [{
        "name": "sectionScorecard",
        "displayName": "Scorecard",
        "filters": "[]",
        "ordinal": 0,
        "visualContainers": [],
        "config": "{}",
        "displayOption": 1,
        "width": 1280,
        "height": 720,
    }],
}
wj(os.path.join(RP, "report.json"), report_json)
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
