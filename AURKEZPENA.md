# Dokumentazio teknikoa · Documentación técnica

**Proiektua / Proyecto:** «Zenbat buru?» — Bizkaian jaiotzen diren abereak,
banan-banan / «¿Cuántas cabezas?» — Las cabezas de ganado que nacen en Bizkaia,
una a una

**Lana ikusgai / Trabajo publicado:** https://zenbatburu.berezuma.com

**Kodea eta datuak / Código y datos:** https://github.com/berezuma/zenbatburu

**Kategoria / Categoría:** 1 · Datuen bistaratzea / Visualización de datos

**Egilea / Autor:** Beñat

**Deialdia / Convocatoria:** Datu Kazetaritzaren Erronkaren Sariak 2026 ·
Premios al reto del periodismo de datos 2026. Izapidea / Trámite: 3104.
Aurkezpen-epea / Plazo: 2026-11-20.

---

# EUSKARAZ

## 1 · Erabilitako datu-iturriak

**Open Data Bizkaia ataria, `explotaciones-ganaderas` datu-multzoa.**
https://www.opendatabizkaia.eus/es/catalogo/explotaciones-ganaderas

Datu-multzo horrek hiru taula-mota ditu pakete berean, eta hirurak erabili dira,
CKAN `datastore_search` APIaren bidez eskuratuta:

| Taula | Ilarak | Eremuak | Aldia |
|---|---|---|---|
| Ustiategien erregistroa | 52.488 | 17 | 2021–2025 |
| Abereen jaiotzak | 84.058 | 12 | 2023–2025 |
| Abereen mugimenduak | 63.809 | 20 | 2023–2025 |

Ez da beste daturik erabili, salbuespen bakar batekin: **arrazen egoera
ofiziala**, 81/2015 Dekretuaren eranskinetik hartua (Euskal Arraza Autoktonoen
Katalogo Ofiziala, EHAA 110, 2015-06-15). Xedapen ofizial bat da, eta orrian
esplizituki aitortzen da. Guk ez dugu arrazarik sailkatu.

## 2 · Lan-prozesua

**Eskuratzea.** `build.py` script batek datu-multzoaren hamaika baliabideak
jaisten ditu CKAN APItik, orrikatuta, eta taula-motaren arabera hiru fitxategitan
batzen. Oharra: atariaren suebakiak `Mozilla/5.0` User-Agenta ukatzen du eta HTML
bat itzultzen du JSONaren ordez; Pythonen lehenetsiak funtzionatzen du.

**Hautaketa.** Jaiotzen taula da ardatza, abere bakoitza ilara bat delako:
identifikazioa, espeziea, arraza, sexua, jaiotze-data, udalerria eta ustiategia.
**2023, 2024 eta 2025 urteak bakarrik** hartzen dira: beste 13 ilara dago, 2008tik
2026ra sakabanatuta, eta urte horiek ez daude osorik. Ustiategien taulak testuingurua
ematen du, eta mugimenduenak jaio ondoren zer gertatzen den.

**Tratamendua.** `compact.py` script batek lau arazo konpontzen ditu:

- *Identifikazio errepikatuak.* 11 ilarak abere bera bitan zerrendatzen zuten;
  behin bakarrik zenbatzen dira. Emaitza: **84.034 abere**.
- *Espezie-izenak taulaz taula aldatzen dira:* jaiotzetan «Bovinos», ustiategietan
  «Bovidos»; «Caballo» eta «Asno» batetik, «Équidos» bestetik. Mapa dokumentatu
  batekin bateratzen dira.
- *Arrazak bi mailatan etiketatuta.* Iturriak batzuetan familia idazten du
  («LATXA») eta batzuetan aldaera («LATXA CARA NEGRA»), erregistratzailearen
  arabera. Horrek aldaeren serieak fidagarri gabe uzten ditu: aldaera baten
  beherakada etiketatze-aldaketa izan daiteke. **Dena familia mailan neurtzen da**,
  eta aldaerak informazio gisa gordetzen dira, ez serie gisa. 99 etiketa → 92
  familia.
- *Kodeak Excel moduan bilduta* (`="022"`) eta maiuskula/minuskula nahasiak,
  normalizatuta. Eremuen izenak elebidunak dira («UDALERRIA/MUNICIPIO»), eta
  izen bat bestearen barruan dago: `LUGAR_DESTINO` bilatzeak
  `CODIGO_LUGAR_DESTINO` ere harrapatzen du, eta kodea itzultzen du izenaren
  ordez. Datu-multzo hau berrerabiltzen duenak **zehatz** bilatu behar du,
  azpikateaz fidatu gabe.

**Hitzak.** Erregistroan dagoena ez da «animalia» orokorra: *abereak* dira,
abeltzaintzako ustiategietan jaioak eta banan-banan identifikatuak. Horregatik
erabiltzen da *abere* orri osoan eta ez *animalia* — txakur bat ere animalia da,
eta ez dago hemen. Gaztelaniazko bertsioan *ganado* eta *cabezas* dira termino
baliokideak, eta ez *animal* soila.

**Analisia.** Hiru aurkikuntza atera dira datuetatik, eta hirurak datuen beraien
mugei buruzkoak dira, ez bakarrik edukiari buruzkoak:

1. *Sexuaren ratioa.* Behietan emeak % 51,9 dira — biologiak hori ematen du.
   Ardietan erregistratutako abereen % 90,9 emeak dira, eta ahuntzetan % 87,5.
   Erregistroak ez ditu jaiotza guztiak biltzen: ustiategitik lehenago ateratzen
   direnak ez dira zerrendara iristen. Orrian ez da esaten *zergatik* gertatzen
   den — erregistroak ez du azaltzen —; esaten dena da zifra hori dela erregistroaren
   mugaren frogarik argiena.
2. *Egunen biribiltzea.* Abereen % 16,1 hilabete baten lehen egunean dago
   idatzita (13.521 abere hamabi egunetan): ardietan % 38,6, behietan % 4,5.
   Aurkikuntza hori bistaratzea egiten ari ginela agertu zen — hamabi zutabe
   besteak baino askoz luzeagoak—, eta proiektuaren ardatz bihurtu zen. Ondorioa:
   **ez da egun bati buruzko baieztapenik egiten orri osoan**; hilabetea da neurria.
3. *Katalogo ofiziala eta errealitatea.* 81/2015 Dekretuko hamalau abere-arrazatatik
   hamaikak dute jaiotzarik erregistroan. Eta arrisku-mailak ez du norabidea
   iragartzen: Azpigorri «kritikoa» erdira jaitsi da bi urtean (698 → 337), eta
   Monchina, «kritikoa» ere bai, igo egin da (348 → 440).

**Egiaztapena.** `verify.py` script batek orrian argitaratutako **53 zifra** iturri
gordinetik berriro kalkulatzen ditu, trinkotze-prozesutik erabat independenteki
(beste kode-bide bat, beste egitura bat). Grafikoak eta taulak datu
trinkotuetatik sortzen dira zuzenean; egiaztapenak eskuz idatzitako testuko
zifrak ere kontrolatzen ditu. **Hiru desadostasun** atzeman zituen argitaratu
aurretik, eta hirurak zuzendu ziren:

- urteko guztizkoak bikoiztuak kendu aurretikoak ziren (29.626 → 29.619);
- «arkumeen % 59 neguan» idatzita zegoen, eta % 58,3 da;
- «moxalak hamabi aldiz gutxiago urtarrilean» idatzita zegoen, eta hogeita hiru
  aldiz dira.

## 3 · Tresnak eta teknikak

**Datuak:** Python 3, liburutegi gehigarririk gabe (`urllib`, `json`,
`collections`, `re`, `unicodedata`, `base64`, `struct`).

**Bistaratzea:** HTML, CSS eta JavaScript eskuz idatziak, **kanpo-liburutegirik
gabe**. Eszena nagusia `<canvas>` bat da: 84.034 marratxo erradial fotograma
bakoitzean, bakoitza abere bat, bere jaiotze-eguneko angeluan. Eguna → angelua
mapaketa bakarra da eszena guztietan, eta horregatik marratxoak **erradialki
bakarrik** mugitzen dira: begiak abere berberak jarraitu ahal die eraztun handi
bakarra bost gurpil bihurtzen denean. Grafiko estatikoak SVG dira.

**Formatu trinkoa:** abere bakoitza lau byte da — eguna, urtea, espeziea eta
sexua zenbaki bakarrean bilduta (`Uint16`), eta arraza eta udalerria byte bana —,
base64-an kodetuta. 147 MB gordin → **459 KB**, orriak datu guztiak barruan eraman
ditzan, eskaera gehigarririk gabe.

**Eskala-erabakia:** hilaren lehen eguneko zutabeak gainerakoak baino zortzi aldiz
luzeagoak dira. Gehienekoarekin eskalatuz gero, gainerako urtea ezabatuko litzateke;
horregatik 98. pertzentilarekin eskalatzen da, zutabe horiek **moztuta** marrazten
dira, eta **benetako kopurua puntan idazten da**. Ezer ez da ezkutatzen.

**Errepikagarritasuna:** script bat datuak jaisteko, beste bat garbitzeko, beste bat
egiaztatzeko, beste bat orria muntatzeko. Prozesu osoa hutsetik errepika daiteke.

## 4 · Erabilgarritasuna

Elebiduna (euskara/gaztelania), egoera URLan gordetzen duena esteka
partekagarrietarako, teklatuz nabigagarria, CSV gisa deskargagarria, pantaila
txikietara egokitua (390 px-tik gora probatuta) eta paperean inprimagarria.
Mugimendua murriztea eskatzen duten erabiltzaileentzat (`prefers-reduced-motion`)
animazioak eten egiten dira. JavaScriptik gabe, albistearen laburpena agertzen da,
bi hizkuntzatan.

**Datu pertsonalak:** ez dago izen-abizenik datu-multzoan ez orrian. Ustiategiak
kodez identifikatzen dira (`ES480220006941`), eta orriak ez du ustiategi-koderik
erakusten: udalerri mailan agregatzen da beti.

---

# EN CASTELLANO

## 1 · Fuentes de datos utilizadas

Se indica expresamente el **conjunto de datos del portal Open Data Bizkaia**
utilizado, que es el único empleado en el proyecto:

**`explotaciones-ganaderas`** — Registro de explotaciones ganaderas.
https://www.opendatabizkaia.eus/es/catalogo/explotaciones-ganaderas

Ese conjunto contiene tres tipos de tabla en el mismo paquete, y se han usado los
tres, obtenidos mediante la API CKAN `datastore_search`:

| Tabla | Filas | Campos | Periodo |
|---|---|---|---|
| Registro de explotaciones | 52.488 | 17 | 2021–2025 |
| Nacimientos de ganado | 84.058 | 12 | 2023–2025 |
| Movimientos de ganado | 63.809 | 20 | 2023–2025 |

No se ha empleado ninguna otra fuente, con una única excepción: el **estado oficial
de las razas**, tomado del anexo del Decreto 81/2015 (Catálogo Oficial de Razas
Animales Autóctonas Vascas, BOPV 110, 15-06-2015). Es una disposición oficial, se
acredita expresamente en la página, y la clasificación no es nuestra.

## 2 · Proceso de trabajo

**Obtención.** Un script `build.py` descarga los once recursos del conjunto desde
la API CKAN, paginando, y los unifica en tres ficheros según el tipo de tabla.
Nota: el cortafuegos del portal rechaza el User-Agent `Mozilla/5.0` y devuelve HTML
en lugar de JSON; el agente por defecto de Python sí funciona.

**Selección.** La tabla de nacimientos es el eje, porque cada cabeza es una fila:
identificación, especie, raza, sexo, fecha de nacimiento, municipio y explotación.
Se toman **solo 2023, 2024 y 2025**: hay otras 13 filas dispersas de 2008 a 2026, y
esos años no están completos. La tabla de explotaciones aporta contexto, y la de
movimientos, qué ocurre después de nacer.

**Tratamiento.** Un script `compact.py` resuelve cuatro problemas:

- *Identificaciones repetidas.* 11 filas listaban el mismo animal dos veces; se
  cuentan una sola vez. Resultado: **84.034 cabezas de ganado**.
- *Los nombres de especie cambian entre tablas:* «Bovinos» en nacimientos,
  «Bovidos» en explotaciones; «Caballo» y «Asno» por un lado, «Équidos» por otro.
  Se unifican con un mapa documentado.
- *Razas etiquetadas en dos niveles.* La fuente escribe a veces la familia («LATXA»)
  y a veces la variedad («LATXA CARA NEGRA»), según quien registre. Eso deja las
  series por variedad sin fiabilidad: la caída de una variedad puede ser un cambio
  de etiquetado. **Todo se mide a nivel de familia**, y las variedades se guardan
  como información, no como serie. 99 etiquetas → 92 familias.
- *Códigos envueltos al estilo Excel* (`="022"`) y mayúsculas mezcladas,
  normalizados. Los nombres de campo son bilingües («UDALERRIA/MUNICIPIO») y hay que
  un nombre está contenido en otro: buscar `LUGAR_DESTINO` captura también
  `CODIGO_LUGAR_DESTINO` y devuelve el código en lugar del nombre. Quien reutilice
  este conjunto debe buscar de forma **exacta**, sin fiarse de la subcadena.

**Las palabras.** Lo que hay en el registro no son «animales» en general: son
*cabezas de ganado*, nacidas en explotaciones ganaderas e identificadas una a una.
Por eso se usa *ganado* y *cabezas*, y no *animal* a secas — un perro también es un
animal, y aquí no está. En euskera el término es *abere*, que significa exactamente
eso.

**Análisis.** Del conjunto salen tres hallazgos, y los tres hablan de los límites del
propio registro, no solo de su contenido:

1. *La ratio de sexos.* En bovinos las hembras son el 51,9 % — eso es lo que da la
   biología. En ovinos, el 90,9 % de lo registrado son hembras, y en caprinos el
   87,5 %. El registro no recoge todos los nacimientos: los que salen antes de la
   explotación no llegan a la lista. La página no afirma *por qué* ocurre —el
   registro no lo explica—; afirma que esa cifra es la prueba más clara del límite.
2. *El redondeo de los días.* El 16,1 % de las cabezas está anotado el día 1 de
   algún mes (13.521 cabezas en doce días): en ovinos el 38,6 %, en bovinos el
   4,5 %. El hallazgo apareció mientras se construía la visualización —doce columnas
   mucho más largas que las demás— y acabó siendo el eje del proyecto. Consecuencia:
   **no se hace ninguna afirmación sobre días** en toda la página; la unidad es el mes.
3. *El catálogo oficial frente a la realidad.* De las catorce razas ganaderas del
   Decreto 81/2015, once tienen nacimientos en el registro. Y el nivel de riesgo no
   anticipa la dirección: la Azpigorri, «crítica», ha caído a la mitad en dos años
   (698 → 337), y la Monchina, también «crítica», ha subido (348 → 440).

**Verificación.** Un script `verify.py` recalcula las **53 cifras** publicadas desde
la fuente en bruto, de forma completamente independiente al proceso de compactación
(otro camino de código, otra estructura). Los gráficos y las tablas salen
directamente de los datos compactados; la verificación controla además las cifras
escritas a mano en el texto. Detectó **tres discrepancias** antes de publicar, y
las tres se corrigieron:

- los totales anuales eran previos a eliminar duplicados (29.626 → 29.619);
- se había escrito «el 59 % de los corderos en invierno», y es el 58,3 %;
- se había escrito «doce veces menos potros en enero», y son veintitrés.

## 3 · Herramientas y técnicas

**Datos:** Python 3, sin librerías adicionales (`urllib`, `json`, `collections`,
`re`, `unicodedata`, `base64`, `struct`).

**Visualización:** HTML, CSS y JavaScript escritos a mano, **sin librerías externas**.
La escena principal es un `<canvas>`: 84.034 marcas radiales en cada fotograma, cada
una un animal, en el ángulo de su día de nacimiento. La correspondencia día → ángulo
es única en todas las escenas, y por eso las marcas solo se mueven **en radio**: el
ojo puede seguir a los mismos animales cuando el anillo grande se convierte en cinco
ruedas. Los gráficos estáticos son SVG.

**Formato compacto:** cada cabeza son cuatro bytes —día, año, especie y sexo en un
solo número (`Uint16`), y raza y municipio un byte cada uno—, codificados en base64.
147 MB en bruto → **459 KB**, para que la página lleve todos los datos dentro sin
peticiones adicionales.

**Una decisión de escala:** las columnas del día 1 de cada mes son ocho veces más
largas que el resto. Escalar por el máximo borraría el resto del año; por eso se
escala por el percentil 98, esas columnas se dibujan **recortadas**, y **la cifra real
se escribe en la punta**. No se oculta nada.

**Reproducibilidad:** un script para descargar, otro para limpiar, otro para
verificar, otro para montar la página. Todo el proceso puede repetirse desde cero.

## 4 · Usabilidad

Bilingüe (euskera/castellano), con el estado guardado en la URL para compartir
enlaces, navegable con teclado, descargable en CSV, adaptada a pantallas pequeñas
(probada desde 390 px) e imprimible en papel. Para quienes piden movimiento reducido
(`prefers-reduced-motion`) las animaciones se detienen. Sin JavaScript, se muestra el
resumen de la noticia en los dos idiomas.

**Datos personales:** no hay nombres de personas ni en el conjunto de datos ni en la
página. Las explotaciones se identifican por código (`ES480220006941`), y la página no
muestra ningún código de explotación: siempre agrega a nivel de municipio.
