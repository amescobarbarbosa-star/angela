#!/usr/bin/env python3
"""Regenera dax/measures.dax desde la definición central measures_def.py."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measures_def import MEASURES

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dax", "measures.dax")

HEADER = """// =====================================================================
// DS Smith SSC - Balanced Scorecard | Medidas DAX para Power BI
// ---------------------------------------------------------------------
// Estas medidas ya vienen incrustadas en el proyecto PBIP (pbip/), en la
// tabla "Measures". Este fichero es la referencia legible / para copiar a
// mano si montas el modelo desde el Excel.
//
// Modelo esperado:
//   Dim_KPI[KPI_ID]  1 --- *  Fact_Scorecard[KPI_ID]
//   Dim_Date[Date]   1 --- *  Fact_Scorecard[Date]
// Las medidas de mes anterior y YTD usan Dim_Date[Month_Index] (mes
// consecutivo), por lo que NO dependen de marcar Dim_Date como tabla de fechas.
// =====================================================================

"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(HEADER)
    for name, fmt, lines in MEASURES:
        f.write(f"{name} =\n")
        for ln in lines:
            f.write(f"    {ln}\n")
        if fmt:
            f.write(f"    // formato: {fmt}\n")
        f.write("\n\n")
print("Escrito", OUT, "|", len(MEASURES), "medidas")
