# Presentación Expensys — director del centro

Presentación de 2 diapositivas para explicar al director el proceso semanal de
contabilización de notas de gasto (Expensys → SAP), a partir de las notas de
la reunión *"304 - Expensys: Estandarización y automatización"* (22/06/2026).

## Qué hay aquí

```
salida/
  Expensys-Proceso-Contabilizacion.pptx   ← la presentación (2 diapositivas)

src/
  generate.js    ← genera la presentación con pptxgenjs
  icons.js       ← helper: compone iconos (react-icons) dentro de círculos de color

package.json     ← dependencias para volver a generar el archivo
```

## Contenido de las diapositivas

1. **Visión general y timing** — cadencia semanal (jueves), la ventana crítica
   de exportación (antes de las 9:30h, antes de que el robot genere a las
   12:00h los batch inputs de P02) y el cierre mensual de tarjetas (día 16-17).
2. **Detalle del proceso** — los 4 pasos: exportar desde Expenses → guardar en
   la carpeta compartida (R2R) → contabilizar en SAP (P02 automático vía robot
   / SM35, frente a SFR manual vía JV) → verificar y controlar (cuadre SAP vs.
   Expenses + control semanal con semáforos).

Cada diapositiva incluye notas del orador (visibles en la vista de presentador
de PowerPoint) con los puntos clave para exponer.

## Volver a generar el archivo

Requiere Node.js.

```bash
npm install
npm run generate
```

Esto vuelve a escribir `salida/Expensys-Proceso-Contabilizacion.pptx`.

## Nota sobre la verificación visual

En el entorno donde se generó esta presentación, la instalación de
LibreOffice solo tiene el paquete `libreoffice-core` (sin los módulos de
Impress/Writer), por lo que `soffice --convert-to pdf` no puede convertir
ningún archivo y no fue posible renderizar capturas de las diapositivas para
una revisión visual automática. En su lugar se comprobó el archivo con:

- validación estructural del OOXML (esquema, relaciones, tipos de contenido);
- extracción del texto (`markitdown`) para revisar contenido y orden;
- una simulación de ajuste de línea con métricas de fuente reales (Liberation
  Sans/Serif, sustitutas métricas de Calibri/Cambria) para comprobar que cada
  cuadro de texto cabe en su altura asignada;
- un volcado de las coordenadas de cada elemento para confirmar que nada
  queda fuera de los límites de la diapositiva.

Conviene abrirla una vez en PowerPoint antes de presentarla, por si algún
detalle visual fino no se detectó por esta vía.

Desde <https://teams.microsoft.com/v2/> (notas de la reunión original)
