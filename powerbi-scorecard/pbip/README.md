# Proyecto Power BI (PBIP) — Scorecard SSC

Proyecto **Power BI en formato texto (PBIP)** que se abre directamente en Power BI
Desktop. Trae **el modelo montado** (3 tablas, 2 relaciones, 19 medidas DAX) **y la
página "Scorecard" con 6 visuales ya colocados**: segmentación por mes, 4 tarjetas de
resumen y la tabla del scorecard.

## Estructura

```
pbip/
├── Scorecard.pbip                         ← abre este fichero en Power BI Desktop
├── Scorecard.SemanticModel/
│   ├── model.bim                          ← modelo (tablas, relaciones, medidas)
│   ├── definition.pbism
│   └── .platform
└── Scorecard.Report/                      ← informe en formato PBIR (por carpetas)
    ├── definition.pbir
    ├── .platform
    └── definition/
        ├── version.json                   ← obligatorio (versión del formato PBIR)
        ├── report.json
        └── pages/
            ├── pages.json
            └── scorecard/
                ├── page.json
                └── visuals/                ← 1 carpeta por visual (6 en total)
```

> **Importante:** mantén el árbol de carpetas intacto. Power BI necesita esta estructura
> tal cual para abrir el `.pbip`.

## Sobre los visuales — léelo antes de abrir

Los 6 visuales de la página están escritos directamente en los ficheros del proyecto
(no se han podido probar en un Power BI Desktop real antes de entregártelos; están
basados en la documentación pública del formato PBIR). Cada visual es un fichero
independiente, así que si alguno no cargara bien, **no afecta a los demás ni rompe el
proyecto**: basta con borrar su carpeta dentro de `.../scorecard/visuals/` y rehacerlo
a mano (2 minutos, ver más abajo).

Los 6 visuales, de mayor a menor confianza:

| Visual | Contenido | Tipo |
|---|---|---|
| Segmentación | `Dim_Date[Month_Name]` | `slicer` |
| 4 tarjetas | `% On Target`, `KPIs Green`, `KPIs Amber`, `KPIs Red` | `card` |
| Tabla scorecard | Perspective, Measure, Process, KPI Value (fmt), KPI Target, Trend Arrow, RAG Status | `tableEx` |

No llevan formato ni colores todavía (título, RAG Color de fondo, anchos de columna) —
eso se añade en 2 clics una vez confirmes que cargan (ver "Pulir el resultado" abajo).

## Cómo abrirlo

1. Doble clic en **`Scorecard.pbip`** (o Power BI Desktop → Archivo → Abrir → el `.pbip`).
   > Si Power BI te pide activar el formato de proyecto: Archivo → Opciones → Características
   > de versión preliminar → **Power BI Project (.pbip) save option** → reinicia.
2. El parámetro **`SourceFile`** ya viene pre-rellenado a
   `C:\Users\esangesc\Downloads\powerbiscorecard\powerbi-scorecard\data\Scorecard_Model.xlsx`.
   - Si mantienes la carpeta ahí, no tienes que tocar nada.
   - Si la mueves, ve a **Transformar datos → Administrar parámetros** y cambia `SourceFile`
     por la nueva ruta completa al `Scorecard_Model.xlsx`.
3. **Inicio → Actualizar** (o *Cerrar y aplicar* si estás en el editor de Power Query). Ya
   tienes el modelo con datos.

Las 19 medidas (KPI Value, RAG Status, RAG Color, Trend Arrow, % On Target, …) están dentro
de **`Fact_Scorecard`** (icono de calculadora). Puedes moverlas luego a una carpeta de
visualización o a una tabla de medidas propia desde Power BI.

## Pulir el resultado (una vez cargue la página)

1. **Semáforo RAG** en la tabla: selecciónala → **Formato** (pincel) → busca la columna
   `RAG Status` en **Elementos de celda** → activa **Color de fondo** → **Según campo** →
   elige la medida `RAG Color` → Aceptar. Las filas se pintan verde/ámbar/rojo.
2. **Títulos de las tarjetas**: por defecto muestran el nombre de la medida debajo del
   número; si quieres un texto distinto, Formato → Título de categoría/etiqueta.
3. **Anchos de columna** de la tabla: arrastra los bordes de cabecera a tu gusto.
4. (Opcional) **Gráfico de tendencia**: Insertar → Gráfico de líneas → Eje
   `Dim_Date[Date]`, Valores `[KPI Value]`, filtrado a un KPI.

El diseño de referencia está en `../preview/scorecard_preview.html`.

## Si algún visual no carga (plan B)

Borra su carpeta en `Scorecard.Report/definition/pages/scorecard/visuals/` (identifícala
abriendo cada `visual.json` y mirando `"visualType"`) y rehazlo a mano:

1. Clic en zona vacía del lienzo → elige el icono del visual en **Visualizaciones**
   (Segmentación de datos / Tarjeta / Tabla).
2. Arrastra el campo o medida correspondiente (ver tabla de arriba) a **Valores**.

2 minutos por visual. El modelo (tablas, relaciones, medidas) no se ve afectado por esto.

## Notas

- El modelo y el informe se generan con `../scripts/build_pbip.py` a partir de la definición
  única de medidas (`../scripts/measures_def.py`), de modo que el PBIP y `../dax/measures.dax`
  quedan siempre sincronizados.
- Modelo en formato `model.bim` (TMSL); informe en formato PBIR (carpetas). Si tu versión de
  Power BI Desktop diera algún problema, avísame con el mensaje de error y lo regenero.
