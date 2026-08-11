# Diseño del modelo – Scorecard SSC en Power BI

## Esquema estrella

```
                 ┌─────────────────┐
                 │    Dim_Date     │
                 │  (calendario)   │
                 └────────┬────────┘
                          │ 1
                          │  Date → Date
                          ▼ *
   ┌──────────────┐  * ┌──────────────────┐
   │   Dim_KPI    │────│  Fact_Scorecard  │
   │ (catálogo)   │ 1  │  (datos crudos)  │
   └──────────────┘    └──────────────────┘
        KPI_ID → KPI_ID
```

- **Fact_Scorecard** — grano: **un KPI × un mes**. Columnas: `KPI_ID`, `Date`,
  `Numerator`, `Denominator`. No guarda valores calculados: el valor se deriva en DAX.
- **Dim_KPI** — un registro por KPI.
- **Dim_Date** — un registro por mes, con año fiscal DS Smith (mayo–abril).

## Dim_KPI: columnas

| Columna | Descripción |
|---|---|
| `KPI_ID` | Código del KPI (1.1, 2.1, 3.33…). Clave de relación. |
| `Perspective` | Perspectiva del BSC (1–5). |
| `Perspective_Objective` | Enunciado del objetivo de la perspectiva. |
| `Objective` | Subtema (Timeliness, Accuracy, Compliance, Productivity…). |
| `Process` | Área de proceso: AP / AR / R2R / All. |
| `Measure` | Nombre del indicador. |
| `Definition` | Definición del numerador (de la hoja de definiciones del Excel). |
| `Value_Type` | Cómo se calcula el valor (ver abajo). |
| `Unit` | Unidad de presentación. |
| `Direction` | `H` = más alto mejor · `L` = más bajo mejor · `N` = neutral/memo. |
| `Target` | Objetivo numérico (si existe). |
| `Has_Data` | `Yes`/`No` — si hoy tiene datos en el hecho. |

## Value_Type → cómo se obtiene el valor (en DAX)

| Value_Type | Cálculo | Formato | Ejemplo de KPI |
|---|---|---|---|
| `PCT` | `SUM(Numerator) / SUM(Denominator)` | % | 2.1 Invoices on time, 3.6 % electronic |
| `RATE1000` | `Num / Den × 1000` | nº /1.000 | 3.32 Queries per 1.000 invoices |
| `RATIO` | `Num / Den` | nº | 1.4 Invoice productivity, 2.8 Journals/site |
| `COUNT` | `SUM(Numerator)` | entero | 3.1 Unexpected adjustments |
| `CURRENCY`| `SUM(Numerator)` | k€ | 1.1 Cost variance, 2.7 Unallocated cash |

Que numerador y denominador se agreguen con `SUM` hace que los ratios se **ponderen
correctamente** en cualquier periodo (SUM(num)/SUM(den)), no como media de medias.

## Estado RAG

Banda ámbar = ±5 % respecto al target.

- **Higher better (`H`)**: Verde si `valor ≥ target`; Ámbar si `≥ target×0,95`; Rojo si no.
- **Lower better (`L`)**: Verde si `valor ≤ target`; Ámbar si `≤ target×1,05`; Rojo si no.
- Sin target o `N` → "No target" (gris).

Ajusta el ±5 % en la medida `RAG Status` si el negocio define otras bandas.

## Tendencia

`Trend Arrow` compara el mes con el anterior (vía `Dim_Date[Month_Index] - 1`, sin
depender del marcado de tabla de fechas) y muestra ↗ / → / ↘
(umbral de "sin cambio" = ±0,5 %). `Trend Color` la pinta verde/rojo según si el
movimiento es **favorable** para la dirección del KPI (subir es bueno en un `H`, malo
en un `L`).

## Simplificaciones respecto al Excel de grupo

El Excel calcula algunos KPIs con "meses equivalentes" a partir de días laborables.
En esta versión simplificada:

| KPI | Excel (bespoke) | Aquí (simplificado) |
|---|---|---|
| 1.4 Invoice productivity | Invoices anualizados / FTE con días laborables | `Numerator` (invoices/mes) / `Denominator` (FTEs) |
| 3.31 Work Flow resolution | Ajuste por meses equivalentes | Recuento de facturas pendientes (`COUNT`) |
| 3.32 Queries | — | Ratio por 1.000 facturas (`RATE1000`) |

Todos los KPIs de tipo `PCT` reconcilian **exactamente** con el Excel. Los tres
anteriores difieren por diseño (más simples y transparentes); si se necesita la cifra
idéntica del grupo, añádela como columna extra en el hecho.

## Reproducir la extracción

La capa de datos se generó desde la hoja `Data_DE_Pack` del Excel con los scripts de
extracción (`build_model.py` → CSVs, `build_xlsx.py` → libro). Para regenerar tras un
cierre mensual: actualiza el Excel de grupo y vuelve a ejecutarlos apuntando al fichero
nuevo. La configuración por KPI (tipo, unidad, dirección, target) vive en el diccionario
`CFG` de `build_model.py`.

## Fuente y trazabilidad

- Origen: `2026_AP07_DE_DSS_Balanced_Scorecard_SSC_v3_new_23_24_25_26_RWv1.xlsx`,
  hoja `Data_DE_Pack` (datos) y `BSC_DE_Pack` (targets y reconciliación).
- Rango temporal: **may-2019 → dic-2026** (92 meses).
- Perspectivas: 5 · KPIs en catálogo: 39 · con datos: 16.
