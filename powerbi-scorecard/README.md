# DS Smith SSC – Balanced Scorecard en Power BI

Versión **simplificada** del Balanced Scorecard del SSC, lista para montar en Power BI,
extraída del fichero Excel de grupo
`2026_AP07_DE_DSS_Balanced_Scorecard_SSC_v3_new_23_24_25_26_RWv1.xlsx`.

> El fichero Excel de grupo **no se modifica**: sigue siendo el modelo oficial. Este
> paquete es una capa de datos limpia + medidas + guía para reconstruir el scorecard
> en Power BI y mantener **ambos** en paralelo.

---

## Qué contiene este paquete

```
powerbi-scorecard/
├── README.md                      ← esta guía (empieza aquí)
├── data/
│   ├── Scorecard_Model.xlsx       ← FUENTE para Power BI (3 tablas con nombre)
│   ├── Dim_KPI.csv                ← catálogo de KPIs
│   ├── Dim_Date.csv               ← calendario mensual (año fiscal mayo–abril)
│   └── Fact_Scorecard.csv         ← 1 fila por KPI y mes (Numerator / Denominator)
├── dax/
│   └── measures.dax               ← todas las medidas DAX (valor, RAG, tendencia, YTD…)
└── docs/
    └── model_design.md            ← esquema estrella, relaciones y decisiones de diseño
```

## Por qué este diseño (y no copiar el Excel tal cual)

El Excel de grupo guarda los datos **en horizontal** (un KPI por fila, 92 meses en
columnas) y mezcla datos, cálculos y presentación en la misma hoja — con muchas
celdas `#REF!` heredadas de enlaces rotos del modelo de grupo.

Power BI trabaja mucho mejor con datos **en vertical (formato largo / tidy)** y un
**esquema estrella**. Por eso el modelo separa:

- **Hechos** (`Fact_Scorecard`): los datos crudos `Numerator` y `Denominator` por KPI y mes.
- **Dimensiones** (`Dim_KPI`, `Dim_Date`): el contexto por el que se filtra y agrupa.
- **Medidas** (DAX): todos los cálculos (valor del KPI, RAG, tendencia, YTD).

Ventaja añadida: el modelo trae **todo el histórico mensual (may-2019 → dic-2026)**,
no solo la ventana de 12 meses que muestra el Excel.

---

## Montaje en Power BI Desktop (≈15 min)

### 1. Importar los datos
1. **Inicio → Obtener datos → Excel** y selecciona `data/Scorecard_Model.xlsx`.
2. En el navegador marca las **3 tablas**: `Dim_KPI`, `Dim_Date`, `Fact_Scorecard`
   (elige las **tablas**, no las hojas) → **Cargar**.
   *(Alternativa: importar los 3 CSV; el resultado es el mismo.)*

### 2. Crear las relaciones (Vista de modelo)
| Desde (1) | Hacia (*) | Cardinalidad |
|---|---|---|
| `Dim_KPI[KPI_ID]` | `Fact_Scorecard[KPI_ID]` | uno a varios |
| `Dim_Date[Date]`  | `Fact_Scorecard[Date]`   | uno a varios |

Ambas con **dirección de filtro único** (de la dimensión al hecho).

### 3. Marcar Dim_Date como tabla de fechas
Selecciona `Dim_Date` → **Herramientas de tabla → Marcar como tabla de fechas** →
columna `Date`. *(Necesario para las medidas de mes anterior y YTD.)*

### 4. Añadir las medidas
Abre `dax/measures.dax` y crea cada medida (**Herramientas de tabla → Nueva medida**).
Sugerencia: crea una tabla vacía llamada `Measures` y aloja todas ahí para tenerlas
ordenadas.

### 5. Construir el informe (ver `docs/model_design.md` para el detalle visual)
Distribución recomendada, una página por las 5 perspectivas o todo en una:

- **Cabecera** – Segmentación `Dim_Date[Month_Name]` (o `Fiscal_Year`) + tarjeta
  `[Selected Month Label]`.
- **Fila de resumen** – tarjetas `[KPIs Green]`, `[KPIs Amber]`, `[KPIs Red]`,
  `[% On Target]`.
- **Tabla/Matriz del scorecard** – Matriz con filas `Dim_KPI[Perspective]` ▸
  `Dim_KPI[Measure]` y valores `[KPI Value (fmt)]`, `[KPI Target]`, `[Trend Arrow]`,
  `[RAG Status]`.
  - Formato condicional del icono/fondo con la medida **`[RAG Color]`**
    (Formato → Elementos de celda → Color de fondo → *Según campo* → `RAG Color`,
    resumido por Primero/Último).
  - Color de la flecha con **`[Trend Color]`**.
- **Gráfico de tendencia** – Gráfico de líneas: eje `Dim_Date[Date]`, valor
  `[KPI Value]`, leyenda `Dim_KPI[Measure]` (filtra a un KPI o usa panel de detalle).

---

## Actualización mensual

1. En el Excel de grupo, ve a la hoja `Data_DE_Pack` y copia la columna del nuevo mes.
2. Añade las filas correspondientes a `Fact_Scorecard` (una por KPI: `KPI_ID`, `Date`,
   `Numerator`, `Denominator`) y añade el mes a `Dim_Date`.
   *(O re-ejecuta el script de extracción sobre el Excel actualizado — ver
   `docs/model_design.md`.)*
3. En Power BI: **Inicio → Actualizar**.

Las medidas, el RAG y las tendencias se recalculan solos.

---

## Notas de la simplificación

- Se incluyen **39 KPIs** de las 5 perspectivas; **16 tienen datos** hoy (el resto
  quedan en el catálogo listos para rellenar — su `Value_Type` ya está definido).
- Los valores calculados se han **reconciliado al 100 %** con el scorecard del Excel
  para los 11 KPIs verificables (AP invoices on time, 3-way match, PO exempt, PO
  coverage, % electronic, automatización, etc.).
- Cálculos bespoke del Excel basados en "días laborables equivalentes" (p. ej. la
  anualización de la productividad 1.4 o el ajuste de workflow 3.31) se han
  **simplificado** a ratios/recuentos directos y mensuales. Se documenta en
  `docs/model_design.md`.
- El año fiscal sigue la convención DS Smith: **mayo–abril**.
