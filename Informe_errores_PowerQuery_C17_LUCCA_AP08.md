# Revisión Power Query – Control C17 LUCCA FY2027 AP08

**Limitación:** no puedo ejecutar Power Query desde aquí, así que no he visto el mensaje de error literal de Excel. Todo lo de abajo sale de leer el código M (21 consultas), las conexiones, las tablas, los nombres definidos y los valores guardados de la última actualización. Si me pasas el texto exacto del error (Datos → Consultas y conexiones → panel de errores), lo confirmo contra esta lista.

El código corregido está en `Section1_corregido.m`. Hay que pegarlo en Excel, porque no he modificado el .xlsx (ver el final).

## A. Causas con evidencia directa en el fichero (probable origen manual)

| # | Dónde | Qué se ve | Por qué da error o resultado erróneo | Probable origen manual | Corrección |
|---|---|---|---|---|---|
| 1 | Hoja **DB** (tabla DB A1:AB1582) | 867 filas reales (filas 2–868) y **714 filas vacías** (869–1582). Esas filas vacías solo tienen valores en N, R–T, V–X y Z–AB (`F.6`=1, `F.7`=1, `E.x`=1, `F.4` y `Ftot` vacíos). Además hay un valor suelto en **N1606** (400001109), fuera de la tabla. | El Excel descargado de SAP (`Sheet1`) trae ~714 filas vacías al final (rango usado ampliado por formato o restos). La consulta `Download` las carga como filas con todo `null`. `F.4` evalúa `null > valor` y falla (`if null`), por eso `F.4`/`Ftot` quedan vacíos. Todos los checks (`Check #N/D`, `Random`, `3 OR MORE`) arrastran esas filas. | Edición manual del Excel de origen (borrar contenido sin borrar filas, o pegar/copiar de otro periodo) y el valor suelto escrito a mano en N1606. | Filtro de filas vacías en `Download` (paso `Filas vacias quitadas`). Borrar N1606 y, en el origen, eliminar las filas sobrantes (no solo el contenido). |
| 2 | Consulta **DB**, paso `F.1` | `F.1` = 0 en **las 1.581 filas**. | `([Entry Date] - [Period.Last_Day]) > 0` compara una *duración* con un número, lo que da error de tipo. El `try ... otherwise 0` lo oculta y devuelve siempre 0. El flag de entradas fuera de plazo **nunca puede marcar**. | Un `try` añadido para quitar un error visible; tapó el fallo en lugar de arreglarlo. | `if [Entry Date] > [Period.Last_Day] then 1 else 0` (con control de nulos), sin `try`. **Revisar los resultados de AP anteriores:** `F.1` pudo salir siempre a 0. |
| 3 | Hoja **Plan de Cuentas**, col. D | 33 celdas `#N/A` (filas 73–75, 216, 218…). | Es la columna "Group Account Long Text", una fórmula que falla. La consulta la convierte a `type text`. Si algún paso toca la columna entera (expandir, buscar duplicados, etc.), el error aparece. La consulta no usa esa columna. | Fórmula/BUSCARV copiada sobre cuentas nuevas que no existen en la tabla de grupos. | La consulta carga solo `G/L Account`, `Group Account` y `Unmapped`. Corregir o eliminar la fórmula en la hoja. |
| 4 | **Plan de Cuentas**, col. A | **23 cuentas duplicadas** (131000, 164000, 241300, 231000…). Afectan a 68 filas de DB; hay 43 grupos de filas idénticas. | `NestedJoin` contra una tabla con clave repetida **duplica** las líneas de DB. Infla importes, `Ftot` y la población de muestreo. No lanza error, solo da datos incorrectos. | Cuentas pegadas dos veces al actualizar el plan (algunas como texto `'131000'` y otras como número). | `Table.Distinct` por `G/L Account` en la consulta. Limpiar los duplicados en la hoja. |
| 5 | Hoja **RANDOM V2** y nombres definidos | `DatosExternos_1` y `DatosExternos_2` de RANDOM V2 apuntan a `#REF!`. También `DynamicPath` y `DATA6` = `#REF!`. `Random (2)` no tiene destino válido. | La tabla de resultados de la consulta se borró a mano (borrar columnas, filas o la tabla). La conexión sigue activa y falla al actualizar ("no se encuentra el destino"). Los nombres `#REF!` son restos de rangos eliminados. | Borrado manual de la tabla de RANDOM V2 y de hojas o rangos. | Eliminar nombres `DATA6`, `DynamicPath` y los `DatosExternos_*` rotos (Fórmulas → Administrador de nombres). En RANDOM V2: borrar la conexión `Random (2)` si no se usa, o volver a cargarla en una tabla. |

## B. Riesgos lógicos del M que pueden dar error o resultado incorrecto

| # | Consulta | Problema | Corrección en `Section1_corregido.m` |
|---|---|---|---|
| 6 | `DB` (E.1, E.3) | `E1` y `E3` se agrupan por `Company Code` + documento + cuenta/grupo, pero el cruce en DB usa solo `Document Number` + cuenta/grupo. Si el mismo nº de documento existe en dos sociedades, las líneas se duplican o se cruzan mal. | Se añade `Company Code` a las claves de los cruces. |
| 7 | `DB` (F.4) | `Number.Abs(null) > …` produce el error "no se puede convertir null a lógico" si falta el periodo en `SODA VALUE` (hoy hay 202701–202712) o el importe viene vacío. | Se controlan los nulos. |
| 8 | `Random` y `Random (2)` | `Number.RandomBetween` se reevalúa en cada actualización y el `Table.Distinct` posterior no tiene garantizado el orden. **La muestra cambia cada vez** y no se puede reproducir para auditoría. | Se añade `Table.Buffer`. Para fijar la muestra hay que copiar los valores a la hoja RANDOM. |
| 9 | `Download` | Ruta UNC fija (`\\dss-ib-dfs-228\...\AP08\LUCCA\Datos control C17 Lucca AP08.XLSX`). Al copiar el libro a otro periodo falla con "No se pudo encontrar el archivo". | No cambiado. Recomiendo una celda de parámetros con la ruta (Setting). |
| 10 | Hoja **Setting**, USERS | Revisor escrito de dos formas: `Iris López` / `Iris Lopez`. En `LASTDAY`, solo 202701–202709 tienen fecha límite. | Corregir el dato en la hoja. |

## C. Qué evitar para que no vuelva a pasar

1. No borrar contenido de las tablas de resultados (DB, 3 OR MORE, RANDOM…): todo se regenera con Actualizar. Si hay que quitar una, eliminar la conexión.
2. No pegar datos a mano debajo o al lado de una tabla de consulta (como N1606).
3. En el Excel de SAP, borrar las filas sobrantes (clic derecho → Eliminar), no solo el contenido. Si no, el rango usado sigue creciendo.
4. Al actualizar `Plan de Cuentas`, comprobar duplicados (Datos → Quitar duplicados) y que la columna D no tenga `#N/A`.
5. No tapar errores con `try … otherwise`. Mejor dejar que falle y corregir el dato.
6. Tras cada actualización, revisar las hojas **Setting Check** (deben salir vacías). Con el origen sucio, `Check #N/D` debería haber avisado de las 714 filas.

## D. Estado del fichero

No he modificado el .xlsx. El libro lleva firma digital (`_xmlsignatures`) y el código M va dentro de un paquete binario (DataMashup); reescribirlo sin Excel puede corromper el libro. Para aplicar los cambios:

1. Datos → Obtener datos → Iniciar el Editor de Power Query.
2. Para cada consulta modificada (`Download`, `DB`, `Plan de Cuentas`, `Random`, `Random (2)`), abrir el Editor avanzado y pegar su bloque desde `Section1_corregido.m`.
3. Cerrar y cargar, y comprobar que DB queda en 867 filas (o menos, si se quitan los duplicados del punto 4).
