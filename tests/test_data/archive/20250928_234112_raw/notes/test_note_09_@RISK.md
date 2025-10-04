---
title: '@RISK'
date created: Wednesday, October 3rd 2018, 9:32:31 am
date modified: Wednesday, May 21st 2025, 3:24:24 pm
language: es
---

# @RISK
**INTRO**

* * *

Oil&Gas, Construcción, Seguros y Farmacéuticas

Y Universidades y Academia

|     |     |
| --- | --- |
| ![[attachments/@RISK.resources/unknown_filename.png]] | Proceso para la elaboración rigurosa de un modelo<br>![[attachments/@RISK.resources/unknown_filename.7.png]] |
| ![[attachments/@RISK.resources/unknown_filename.1.png]] |     |
| ![[attachments/@RISK.resources/unknown_filename.2.png]] | A los riesgos que conocemos y podemos controlar / actuar tenemos que añadir los riesgos externos, fuera de nuestro control o conocimiento. |

**PRIMER MODELO**

* * *

Cost Estimation.xlsx

<div class="joplin-table-wrapper"><table style="border-collapse: collapse; min-width: 100%;"><colgroup><col style="width: 226px;"><col style="width: 704px;"></colgroup><tbody><tr><td style="border: 1px solid rgb(219, 219, 219); width: 226px; padding: 8px;"><div><br></div></td><td style="border: 1px solid rgb(219, 219, 219); width: 704px; padding: 8px;"><div>Cuando hablamos de probabilidades al tomador de decisión en el fondo estamos transfiriendo un riesgo, aunque estemos contando algo más realista. Por esto no es fácil.</div><div><span style="background-color: rgb(255, 250, 165);-evernote-highlight:true;">Conviene contar la probabilidad en términos de opcionalidad.</span></div></td></tr><tr><td style="border: 1px solid rgb(219, 219, 219); width: 226px; padding: 8px;"><div><br></div></td><td style="border: 1px solid rgb(219, 219, 219); width: 704px; padding: 8px;"><div>Las funciones permiten extraer análisis del conjunto de datos de la simulación sin necesidad de mirar el gráfico. P.ej. Riskmean.</div></td></tr><tr><td style="border: 1px solid rgb(219, 219, 219); width: 226px; padding: 8px;"><div><img src="./_resources/@RISK.resources/unknown_filename.3.png" alt="unknown_filename.3.png"><br></div></td><td style="border: 1px solid rgb(219, 219, 219); width: 704px; padding: 8px;"><div><span style="font-weight: bold;">RiskResultsGraph</span> permite sacar un gráfico de un output directamente con una función. El número que se pone en la fórmula es el tipo de gráfico.</div></td></tr><tr><td style="border: 1px solid rgb(219, 219, 219); width: 226px; padding: 8px;"><div><br></div></td><td style="border: 1px solid rgb(219, 219, 219); width: 704px; padding: 8px;"><div><span style="font-weight: bold;">RiskMakeInput</span> sirve para convertir un output en input a efectos de cálculo de las sensibilidades. Equivale a unir todas las variables anteriores en una, simplificando el análisis posterior.</div><div>Las variables que une esta función quedan integradas, de forma que el sistema no las considera como independientes y no las muestra en el análisis de sensibilidad.</div></td></tr><tr><td style="border: 1px solid rgb(219, 219, 219); width: 226px; padding: 8px;"><div><img src="./_resources/@RISK.resources/89A86D9C-EB5A-4500-8D1D-6F87A3702DD9.png" alt="89A86D9C-EB5A-4500-8D1D-6F87A3702DD9.png"><br></div></td><td style="border: 1px solid rgb(219, 219, 219); width: 704px; padding: 8px;"><div><span style="font-weight: bold;">Data Viewer</span>: Seleccionamos una tabla de datos y nos hace una representación gráfica de la serie con los estadísticos principales, sin necesidad de entrar en ajuste de distribuciones ni simulaciones.</div></td></tr><tr><td style="border: 1px solid rgb(219, 219, 219); width: 226px; padding: 8px;"><div><img src="./_resources/@RISK.resources/480F24B8-FF61-409E-A20C-C9D90929C066.png" alt="480F24B8-FF61-409E-A20C-C9D90929C066.png"><br></div></td><td style="border: 1px solid rgb(219, 219, 219); width: 704px; padding: 8px;"><div>Resultados de simulación: podemos ver una tabla resumen o todos los datos de la simulación.</div><div><br></div></td></tr><tr><td style="border: 1px solid rgb(219, 219, 219); width: 226px; padding: 8px;"><div><img src="./_resources/@RISK.resources/unknown_filename.4.png" alt="unknown_filename.4.png"><br></div></td><td style="border: 1px solid rgb(219, 219, 219); width: 704px; padding: 8px;"><ul><li>La triangular es una distribución burda pero útil como primera aproximación. Costes sobre todo. Bien para datos simétricos</li><li>La Pert muestrea alrededor de la moda más que la triangular. Aumenta la curtosis. Permite modelar algo parecido a la normal o lognormal sin necesidad de conocer más parámetros.</li><li>Además reduce la asimetría.</li><li>Bernoulli - experimentos en los que el resultado es A o B, con una probabilidad cada uno.</li><li>Binomial - dado un proceso Bernoulli, modela la probabilidad de que si se repite n veces, un resultado determinado se dé x veces&nbsp;</li><li>Normal - procesos naturales, o combinación de un número muy grande de distribuciones similares. Es decir, se aplica a poblaciones.</li><li>Lognormal - valores positivamente sesgados, p.ej. el fallo por fatiga, precios de acciones, tasas de interés, valores inmobiliarios.</li><li>Poisson - nº de eventos que se dan en un período determinado, sabiendo la media de eventos que se han dado en el pasado (lambda). P.ej. accidentes en 1 día, penalizaciones….</li></ul><div><br></div></td></tr></tbody></table></div>

**CORRELACIÓN**

* * *

1 - Model with probability distributions.xlsx

|     |     |
| --- | --- |
| ![[attachments/@RISK.resources/16FE9873-9C32-4E56-87BC-604220D1FA95.png]] | **Riskname:** se usa para especificar el nombre de la distribución cuando el nombre no está justo en la celda a la izquierda.<br>La correlación altera la independencia de muestreo entre distribuciones del modelo, y fuerza a que una muestra aleatoria de una función y otra estén relacionadas.<br>Seleccionamos en excel las dos celdas de distribuciones a correlacionar y damos a correlación.<br>La cópula o correlación multimodal es cuando la correlación varía en el rango de -1 a 1. |
| ![[attachments/@RISK.resources/EB003831-C27C-4D6C-BF1E-416A8624A83A.png]]<br><br>![[attachments/@RISK.resources/4086ED46-A744-4368-A4AD-064227FA6397.png]] | ![[attachments/@RISK.resources/E02DCD25-89C0-4D19-BAA2-F17CE96F7FF4.png]]<br><br>![[attachments/@RISK.resources/F3119EBF-D5E7-4AE2-B759-4EC3D69A26DE.png]] |

**ESCENARIOS**

* * *

14 - Policy comparison RiskSimTable.xlsx

Los escenarios son conjuntos de iteraciones.

P.ej. qué pasa si el CAPEX es el doble? O si la tasa de descuento es distinta? RISKSIMTABLE

|     |     |
| --- | --- |
| ![[attachments/@RISK.resources/E590A8CD-6036-44F1-B09C-BACE03AC1C41.png]] | Para ello, en las celdas de los parámetros que definen las distribuciones incluimos RiskSimTable con referencia a los conjuntos de valores que tomarán esos parámetros en cada simulación.<br><br>CUIDADO con que haya el mismo número de escenarios en la tabla de abajo sea igual que en el desplegable del menú donde dice Simulaciones. Si en la tabla hay 3 escenarios pero arriba dice 2, ignora el tercero. |
| ![[attachments/@RISK.resources/Screen Shot 2018-10-03 at 16.15.28.png]] | Después de hacer las simulaciones podemos sacar estadísticos específicos para cada escenario, porque el escenario se puede especificar. |
| ![[attachments/@RISK.resources/F3C8D416-BECF-48B8-B5F1-89EB032F673A.png]] | Con RiskResultsGraph podríamos entonces tener directamente insertadas las gráficas del VAN para los tres escenarios. |

**REGISTROS DE RIESGOS**

* * *

10 - Event Risk with RiskCompound.xlsx

CashFlow and RiskRegister with strategic risks.xls

<div class="joplin-table-wrapper"><table style="border-collapse: collapse; min-width: 100%;"><colgroup><col style="width: 335px;"><col style="width: 531px;"></colgroup><tbody><tr><td style="border: 1px solid rgb(219, 219, 219); width: 335px; padding: 8px;"><div><img src="./_resources/@RISK.resources/6BD887A4-BABA-4C77-8B0F-026CC406F537.png" alt="6BD887A4-BABA-4C77-8B0F-026CC406F537.png"><br></div></td><td style="border: 1px solid rgb(219, 219, 219); width: 531px; padding: 8px;"><div>En este caso la creación de un registro de riesgos es sencilla:</div><ul><li>Cada evento tiene una probabilidad de ocurrencia (Bernoulli, toma valores 0 o 1) y un posible impacto si ocurre (distribución a definir, p.ej. Lognorm)</li><li>RiskMakeInput para aunar las dos como un producto, y crear la función SEVERIDAD</li><li>La función suma de las severidades es la exposición acumulada. P.ej. la ley de responsabilidad ambiental obliga que la póliza tenga una cobertura el 95% del riesgo acumulado.</li></ul></td></tr><tr><td style="border: 1px solid rgb(219, 219, 219); width: 335px; padding: 8px;"><div><img src="./_resources/@RISK.resources/4571F722-093E-4B5B-9803-5AC95F2AE215.png" alt="4571F722-093E-4B5B-9803-5AC95F2AE215.png"><br></div></td><td style="border: 1px solid rgb(219, 219, 219); width: 531px; padding: 8px;"><div>RiskMakeInput para la severidad: Las variables que une esta función quedan integradas, de forma que el sistema no las considera como independientes y no las muestra en el análisis de sensibilidad.</div><div>Evitamos así que salga en el tornado en primer lugar de sensibilidad la probabilidad de fallo informático y en segundo lugar el impacto de un fallo financiero.</div></td></tr><tr><td style="border: 1px solid rgb(219, 219, 219); width: 335px; padding: 8px;"><div><img src="./_resources/@RISK.resources/469898A2-3694-4D17-9D76-BF447268DCD6.png" alt="469898A2-3694-4D17-9D76-BF447268DCD6.png"><br></div></td><td style="border: 1px solid rgb(219, 219, 219); width: 531px; padding: 8px;"><div>RiskCompound coge dos celdas con distribución, y suma los resultados de la segunda para un número de muestras definidas con la primera. P.ej. una poisson primero define cuántos eventos se dan en el período de tiempo (un año p.ej) y la log norm da el impacto probable cada vez que ocurre el evento.</div></td></tr><tr><td style="border: 1px solid rgb(219, 219, 219); width: 335px; padding: 8px;"><div><br></div></td><td style="border: 1px solid rgb(219, 219, 219); width: 531px; padding: 8px;"><div><br></div></td></tr><tr><td style="border: 1px solid rgb(219, 219, 219); width: 335px; padding: 8px;"><div><img src="./_resources/@RISK.resources/86029CBC-EA7E-448F-82FC-3DD56519D0D5.png" alt="86029CBC-EA7E-448F-82FC-3DD56519D0D5.png"><br></div><div><img src="./_resources/@RISK.resources/6D656AA8-FD6A-4EC7-AC02-9162D3EC8146.png" alt="6D656AA8-FD6A-4EC7-AC02-9162D3EC8146.png"><br></div></td><td style="border: 1px solid rgb(219, 219, 219); width: 531px; padding: 8px;"><div>Ojo a cómo en este caso se introduce la posibilidad de que un evento deje fuera del negocio. Calcula con la tabla de ceros y unos la ocurrencia del evento y toma el año del primero que ocurre, Luego manda el primero de los eventos críticos al cashflow y mete el impacto.</div></td></tr></tbody></table></div>

**STRESS TEST**

* * *

1 - Model with probability distributions - Stress.xlsx

|     |     |
| --- | --- |
| ![[attachments/@RISK.resources/unknown_filename.5.png]] | Advanced Analysis - Stress Analysis<br>Seleccionamos la celda para monitorear (cell to monitor) y añadimos las entradas que queremos estresar, con sus rangos de stress cada una. |
| ![[attachments/@RISK.resources/unknown_filename.6.png]] |     |
|     |     |
