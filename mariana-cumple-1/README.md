# Primer cumpleaños de Mariana

Piezas gráficas hechas a partir de la decoración comprada (ColorParty, línea pastel
iridiscente con estrellas doradas): invitación para WhatsApp y cuatro propuestas de
tarta de dos pisos para encargar en la pastelería.

## Qué hay aquí

```
salida/
  invitacion-mariana.jpg          ← invitación lista para enviar por WhatsApp
  invitacion-mariana.png          ← original sin pérdida (2160 × 3840)
  tartas-dos-pisos.jpg/.png       ← lámina con los cuatro diseños
  tarta-01-nube-iridiscente.*     ← ficha suelta de cada diseño
  tarta-02-petalos-de-nube.*
  tarta-03-globos-de-azucar.*
  tarta-04-arcoiris-suave.*

mensaje-whatsapp.md               ← textos para acompañar la invitación
encargo-pasteleria.md             ← ficha técnica para la pastelería
filosofia-diseno.md               ← criterio visual que guía todas las piezas

src/
  invitacion.html                 ← fuente de la invitación
  tartas.html                     ← fuente de las tartas
  render.js                       ← exporta los HTML a PNG/JPG con Chromium
```

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
