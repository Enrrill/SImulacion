# Descripción Detallada de la Imagen para Inteligencia Artificial: "image_69ea59.png"

Esta es una descripción técnica y exhaustiva de la interfaz de usuario que se muestra en el archivo `image_69ea59.png`. Está estructurada analíticamente para facilitar su comprensión por modelos de lenguaje o sistemas de visión artificial.

---

## 1. Información General del Panel (Dashboard)
* **Propósito del Software:** Simulación de la propagación de una epidemia/enfermedad en tiempo real.
* **Estilo Visual:** Interfaz de usuario de tema oscuro (Dark Mode), con una paleta de colores basada en azul marino profundo, gris oscuro, detalles en blanco y colores de contraste vibrantes (rojo, verde, celeste claro) para indicar estados de salud.
* **Idioma:** Español.

---

## 2. Encabezado y Métricas Principales (Barra Superior Izquierda)
* **Título Principal:** "Simulación de Epidemia" (Acompañado de un icono de matraz o tubo de ensayo a la izquierda).
* **Contadores de Estado Actual (Fila Superior):**
  * **SANOS:** `1,240` (Indicado con un círculo color azul claro/blanco).
  * **INFECTADOS:** `452` (Indicado con un círculo color rojo).
  * **INMUNES:** `185` (Indicado con un círculo color verde).
  * **MUERTOS:** `12` (Indicado con un círculo color rojo oscuro/grisáceo).
* **Indicador de Tiempo (Extremo Derecho de la Barra):** `DÍA: 42` (Dentro de una cápsula con un icono de reloj).

---

## 3. Ventana Principal de Simulación Visual (Área Central)
* **Naturaleza del Gráfico:** Es un plano bidimensional oscuro que muestra la simulación interactiva mediante partículas en movimiento (nodos circulares brillantes) representando individuos en el entorno.
* **Texto de Fondo:** Presenta una marca de agua transparente o texto tenue en el centro que dice: **"LIVE DATA"**.
* **Partículas Visibles y sus Estados:**
  * Se observan varios nodos distribuidos dispersamente:
    * 3 nodos celestes/blancos brillantes (Individuos **Sanos**).
    * 2 nodos rojos brillantes (Individuos **Infectados**).
    * 1 nodo verde brillante (Individuo **Inmune**).

---

## 4. Gráfico de Evolución Temporal (Área Inferior Izquierda)
* **Título:** "EVOLUCIÓN TEMPORAL"
* **Leyenda:** Muestra dos etiquetas de seguimiento: `Sanos` (punto celeste) e `Infectados` (punto rojo).
* **Descripción del Gráfico:** Es un gráfico de líneas suavizadas con área rellena (área bajo la curva).
  * **Línea Celeste (Sanos):** Comienza estable, decae formando un valle pronunciado mientras suben los contagios, luego se recupera formando una meseta alta, vuelve a caer notablemente hacia el final de la gráfica y muestra un repunte final abrupto.
  * **Línea Roja (Infectados):** Se comporta de manera inversa a los sanos, mostrando dos picos o "olas de contagio" definidos donde la curva se eleva significativamente en los momentos en que la población sana disminuye.

---

## 5. Panel de Control y Configuración (Columna Derecha)
Este panel lateral permite modificar las variables matemáticas del modelo epidemiológico.

* **Sección Superior:**
  * **Título:** "PARÁMETROS"
  * **Subtítulo:** "CONFIGURACIÓN DE SIMULACIÓN"
* **Lista de Parámetros y Deslizadores (Sliders):**
  1. **Población Total:** Valor asignado `2,500`. *(Descripción inferior: "Define el número de individuos presentes en el entorno.")*
  2. **Velocidad de Simulación:** Valor asignado `x1.5`. *(Descripción inferior: "Ajusta la rapidez con la que transcurre el tiempo y el movimiento.")*
  3. **Radio de Infección:** Valor asignado `12.5m`. *(Descripción inferior: "Distancia máxima a la que un infectado puede contagiar a otros.")*
  4. **Prob. de Infección (%):** Valor asignado `45%`. *(Descripción inferior: "Probabilidad de que el virus se transmita en cada contacto.")*
  5. **Prob. de Inmunidad (%):** Valor asignado `15%`. *(Descripción inferior: "Probabilidad de que un individuo se recupere y se vuelva inmune.")*
  6. **Tiempo de Vida (Frames):** Valor asignado `600`. *(Descripción inferior: "Duración de la infección antes de que el individuo muera o se recupere.")*

* **Sección de Selección de Enfermedad:**
  * **Etiqueta:** "SELECCIONAR ENFERMEDAD"
  * **Menú Desplegable (Dropdown):** Actualmente seleccionado **"COVID-19 (Omicron)"**.

* **Botones de Acción Inferiores:**
  * **Botón Principal 1:** "▶ REANUDAR" (Botón destacado en color azul claro/lavanda con texto oscuro).
  * **Botón Principal 2:** "⟳ REINICIAR" (Botón de borde gris oscuro/transparente con texto claro).
