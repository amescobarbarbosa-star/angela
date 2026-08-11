# Proyecto Power BI (PBIP) — Scorecard SSC

Proyecto **Power BI en formato texto (PBIP)** que se abre directamente en Power BI
Desktop. Trae **el modelo ya montado**: las 3 tablas, las 2 relaciones y **las 19
medidas DAX**. Solo tienes que indicar dónde está el fichero de datos y actualizar.

## Estructura

```
pbip/
├── Scorecard.pbip                         ← abre este fichero en Power BI Desktop
├── Scorecard.SemanticModel/
│   ├── model.bim                          ← modelo (tablas, relaciones, medidas)
│   ├── definition.pbism
│   └── .platform
└── Scorecard.Report/
    ├── report.json                        ← informe con una página "Scorecard" (vacía)
    ├── definition.pbir
    └── .platform
```

## Cómo abrirlo (primera vez)

1. Doble clic en **`Scorecard.pbip`** (o Power BI Desktop → Archivo → Abrir → el `.pbip`).
   > Si Power BI te pide activar el formato de proyecto: Archivo → Opciones → Características
   > de versión preliminar → **Power BI Project (.pbip) save option** → reinicia.
2. Al abrir, el modelo carga con un error de origen (aún no sabe dónde está el Excel). Ve a
   **Transformar datos → Administrar parámetros** y pon **`SourceFile`** con la ruta local
   completa a tu fichero, por ejemplo:
   `C:\Users\TuUsuario\...\powerbi-scorecard\data\Scorecard_Model.xlsx`
3. **Cerrar y aplicar** → **Inicio → Actualizar**. Ya tienes el modelo con datos.

A partir de aquí tienes en el panel de campos las 3 tablas y, en **`Measures`**, las 19
medidas listas (KPI Value, RAG Status, RAG Color, Trend Arrow, % On Target, …).

## Montar los visuales de la página "Scorecard"

La página viene vacía a propósito (los visuales no se pueden pre-generar de forma fiable
en texto). Con el modelo ya cargado, se montan en un momento arrastrando campos:

1. **Segmentación (slicer)** → campo `Dim_Date[Month_Name]` (o `Fiscal_Year`).
2. **Fila de tarjetas** → 4 tarjetas con `[% On Target]`, `[KPIs Green]`, `[KPIs Amber]`,
   `[KPIs Red]`.
3. **Matriz del scorecard**:
   - Filas: `Dim_KPI[Perspective]` y debajo `Dim_KPI[Measure]`.
   - Valores: `[KPI Value (fmt)]`, `[KPI Target]`, `[Trend Arrow]`, `[RAG Status]`.
   - Formato condicional del fondo/icono con la medida **`[RAG Color]`**
     (Formato de la matriz → Elementos de celda → Color de fondo → *Según campo* → `RAG Color`).
4. **Gráfico de líneas (tendencia)** → Eje `Dim_Date[Date]`, Valores `[KPI Value]`,
   filtrado a un KPI (o con panel de obtención de detalles por `Measure`).

El diseño de referencia está en `../preview/scorecard_preview.html`.

## Cambiar la fuente a los CSV (opcional)

Si prefieres alimentar el modelo desde los CSV en vez del Excel, cambia el parámetro por
la carpeta y ajusta las consultas (Excel.Workbook → Csv.Document). El Excel es la opción
recomendada porque conserva los tipos y los nombres de tabla.

## Notas

- El modelo se genera con `../scripts/build_pbip.py` a partir de la definición única de
  medidas (`../scripts/measures_def.py`), de modo que el PBIP y `../dax/measures.dax`
  quedan siempre sincronizados.
- Formato `model.bim` (TMSL). Si tu versión de Power BI Desktop solo aceptara TMDL,
  avísame y regenero el modelo en ese formato.
