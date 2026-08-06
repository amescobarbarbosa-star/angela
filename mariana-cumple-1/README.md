# Primer cumpleaños de Mariana

Piezas gráficas hechas a partir de la decoración comprada (ColorParty, línea pastel
iridiscente con estrellas doradas): invitación para WhatsApp y cuatro propuestas de
tarta de dos pisos para encargar en la pastelería.

## Qué hay aquí

```
salida/
  invitacion-mariana.jpg          ← invitación principal, lista para WhatsApp
  invitacion-mariana.png          ← original sin pérdida (2160 × 3840)
  invitacion-alt-A-arco-de-globos.*  ← alternativas de invitación
  invitacion-alt-B-acuarela.*
  invitacion-alt-C-jardin.*

  tartas-fondant.jpg/.png         ← lámina fondant (línea de las fotos de referencia)
  fondant-01-jirafa-y-palmeras.*
  fondant-02-osito-y-banderines.*
  fondant-03-salvia-y-oro.*
  fondant-04-corona-de-flores.*

  tartas-dos-pisos.jpg/.png       ← lámina iridiscente (línea de la decoración)
  tarta-01-nube-iridiscente.*
  tarta-02-petalos-de-nube.*
  tarta-03-globos-de-azucar.*
  tarta-04-arcoiris-suave.*

  tarta-3d.jpg/.png               ← render 3D de la tarta «Jirafa y palmeras» (frente)
  tarta-3d-tres-cuartos.jpg/.png  ← el mismo render en vista de tres cuartos

mensaje-whatsapp.md               ← textos para acompañar la invitación
encargo-pasteleria.md             ← ficha técnica para la pastelería
filosofia-diseno.md               ← criterio visual que guía todas las piezas

src/
  invitacion.html                 ← fuente de la invitación principal
  invitaciones-alt.html           ← fuente de las tres alternativas
  tartas.html                     ← fuente de las tartas iridiscentes
  tartas-fondant.html             ← fuente de las tartas de fondant
  tarta3d.html                    ← escena 3D (three.js + WebGL)
  three.module.js                 ← biblioteca three.js (r0.169)
  render.js                       ← exporta los HTML 2D a PNG/JPG con Chromium
  render3d.js                     ← exporta la escena 3D (WebGL vía SwiftShader)
```

## Render 3D

`src/tarta3d.html` monta la tarta con three.js (geometría real, luces de estudio,
sombras). Se exporta con Chromium en modo WebGL por software:

```bash
node src/render3d.js src/tarta3d.html salida/tarta-3d.jpg 1200 1500
node "src/render3d.js" "src/tarta3d.html?v=tresqcuartos" salida/tarta-3d-tres-cuartos.jpg 1200 1500
```

El parámetro `?v=tresqcuartos` cambia la cámara a vista de tres cuartos.

## Dos paletas

La decoración comprada es pastel iridiscente; las fotos de tarta de referencia son
rosa empolvado, crema y verde salvia. Las piezas están hechas en las dos líneas para
poder elegir, y cualquiera de los diseños de fondant se puede repintar en los colores
de la decoración (o al revés) cambiando la paleta en el `<script>` del HTML.

## Paleta

Tomada directamente del papel de la decoración:

| | | |
|---|---|---|
| melocotón | `#FFD9B8` | fondo cálido |
| mantequilla | `#FBE7B0` | acento |
| rosa | `#F9C6D9` | dominante |
| lila | `#DCC8F0` | dominante |
| agua | `#C6E4F2` | transición |
| menta | `#BEEBD6` | cierre frío |
| oro | `#C79A3E` | tipografía y detalles |

## Volver a generar las imágenes

Requiere Node y Playwright con Chromium disponible en `/opt/pw-browsers/chromium`.

```bash
node src/render.js src/invitacion.html salida/invitacion-mariana.jpg 1080 1920

node src/render.js src/tartas.html salida/tartas-dos-pisos.jpg 1240 2100 \
  "#c1=salida/tarta-01-nube-iridiscente.jpg" \
  "#c2=salida/tarta-02-petalos-de-nube.jpg" \
  "#c3=salida/tarta-03-globos-de-azucar.jpg" \
  "#c4=salida/tarta-04-arcoiris-suave.jpg"
```

La extensión decide el formato: `.jpg` sale ligero para mensajería, `.png` sin pérdida.
Los datos de la fiesta (fecha, hora, lugar, teléfono) están en `src/invitacion.html`,
en el bloque `.datos` y en `.pie`.
