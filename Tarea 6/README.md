# GARCH, Monte Carlo y árboles binomiales: NVDA, AMD y XOM

Tarea Clase 6 · **Productos Derivados y Administración de Riesgos Corporativos**
Maestría en Finanzas, EGADE Business School (Tecnológico de Monterrey) · Grupo 40 · Equipo 6
Profesor: Dr. Raymundo Díaz Robles

**Autores:** Eduardo Ayala Saldaña, Mariann Antonelli Morales Tobias y Ulises Salinas López

---

## De qué trata

Se usa un modelo **GARCH(1,1)** para pronosticar la volatilidad de **NVDA, AMD y XOM** hasta el vencimiento de sus opciones (**18 de diciembre de 2026**), se mete esa volatilidad en un **árbol binomial americano (CRR)** y se decide qué opciones comprar. El análisis responde cuatro preguntas:

1. ¿Qué volatilidad espera GARCH frente a la volatilidad implícita que cobra el mercado?
2. ¿Qué rango de precios deja el Monte Carlo con GARCH al vencimiento y a 2 semanas?
3. ¿La opción está barata o cara (razón σ GARCH ÷ σ implícita) y qué tan sólida es esa señal?
4. ¿Qué se compra en Investopedia, cuánto cuesta y cuánto se espera ganar o perder?

El método sigue la presentación del profesor y a Hull, *Options, Futures and Other Derivatives* (caps. 13, 22 y 23).

## Resultados principales

Cotizaciones de TradingView al cierre del **30-oct-2026** (capturadas el 1-nov). Tasa libre de riesgo continua de 3.94%, 49 días naturales al vencimiento (T = 49/365) y 34 días hábiles para simular trayectorias.

| Acción | Persistencia GARCH | Razón σ GARCH ÷ σ implícita | Señal | Posición de la tarea | Costo total |
|---|---|---|---|---|---|
| NVDA | 0.974 | 1.10 | Sin ventaja de volatilidad (señal frágil) | Call 200 × 2 contratos | 3,150 USD |
| AMD | 0.872 | 1.04 | Sin ventaja de volatilidad (señal frágil) | Put 500 × 1 contrato | 4,075 USD |
| XOM | 0.991 | 0.83 | No comprar por volatilidad (opción cara, señal sólida) | Call 185 × 3 contratos (tesis direccional) | 2,760 USD |

Nota: las cifras vienen del Rmd. Los notebooks de Python llegan a las mismas decisiones, con diferencias pequeñas por el generador de números aleatorios (por ejemplo, la razón de NVDA sale 1.09 en Python y 1.10 en R, y el P&L a 2 semanas sale −43, −72 y +5 USD).

Lectura honesta del resultado: a 2 semanas el P&L esperado de las posiciones queda **cerca de cero** (aprox. −47, −63 y +13 USD para NVDA, AMD y XOM). La ventaja de GARCH se cobra cuando la volatilidad implícita converge hacia la que GARCH espera, y en el ejercicio se mantiene constante. Las posiciones son compras de opciones, así que la pérdida máxima es la prima pagada.

## Contenido del repositorio

| Archivo | Para qué sirve |
|---|---|
| `GARCH_Opciones_NVDA_AMD_XOM.Rmd` | **Entregable principal.** Análisis completo en R Markdown (GARCH por máxima verosimilitud, EWMA, Monte Carlo, árbol CRR, griegas, nodos del árbol, señal, estrategia, rentabilidad a 2 semanas). |
| `GARCH_Opciones_NVDA_AMD_XOM_Rmd.html` | Resultado ya compilado del Rmd. |
| `Dashboard_GARCH.html` | Dashboard interactivo (Plotly), se abre en cualquier navegador sin instalar nada. |
| `GARCH_Colab_LSEG.ipynb` | Versión en Python para Google Colab. Instala sus paquetes, reproduce el análisis y construye el dashboard. |
| `GARCH_Notebook_Colab.html` | Salida del notebook de Colab ya ejecutada (con el dashboard incrustado). |
| `GARCH_CodeBook.ipynb` | Versión de código del análisis en Python, sin dashboard, compatible con Python 3.8. |
| `precios_usados.csv` | Precios de cierre ajustados diarios (nov-2021 a 30-oct-2026) de NVDA, AMD y XOM. |
| `evidencias/` | Capturas de cotizaciones (TradingView), de los simuladores (Investopedia, TradingView, CME) y la conversación con TECgpt. |

Nota sobre las evidencias: `Tarea_6_Screenshots_Cotizaciones.pdf` contiene las 6 capturas de las opciones (call y put de cada acción), `Tarea_6_Screenshots_Simuladores.pdf` las capturas de Investopedia, TradingView y CME, y `TECgpt_Portal_-_GARCH_y_opciones__NVDA_AMD_XOM_ChatGPT.pdf` la conversación con TECgpt (85 páginas).

## Cómo reproducirlo

### R Markdown

Requisitos: R 4.x, los paquetes `quantmod` y `zoo`, y RStudio (o `rmarkdown`).

1. Descarga el repositorio y deja `precios_usados.csv` en la misma carpeta que el Rmd.
2. Abre `GARCH_Opciones_NVDA_AMD_XOM.Rmd` en RStudio y pulsa **Knit**.

El Rmd intenta descargar los precios de Yahoo Finance con `getSymbols`; si no hay internet, usa `precios_usados.csv`. Con 100,000 trayectorias de Monte Carlo, la compilación tarda unos minutos. En Windows, si los acentos salen como `<U+00ED>`, el Rmd intenta activar la codificación UTF-8 automáticamente.

Para actualizar las cotizaciones basta con editar `F0` (fecha) y la lista `mercado` en el bloque de parámetros.

### Notebook de Python (Colab)

1. Abre `GARCH_Colab_LSEG.ipynb` en [Google Colab](https://colab.research.google.com/).
2. Ejecuta todas las celdas. La primera instala los paquetes necesarios.
3. Los parámetros de mercado se cambian en la sección "0. Parámetros".
4. Si no hay conexión a internet, el notebook usa archivos locales: crea una carpeta `datos/` con `NVDA.csv`, `AMD.csv` y `XOM.csv`, cada uno con columnas `Date` y `Close`.

`GARCH_CodeBook.ipynb` es la versión sin dashboard, para correr el análisis en un entorno local.

## Metodología

- **Rendimientos:** logarítmicos diarios en porcentaje.
- **GARCH(1,1):** máxima verosimilitud con innovaciones normales; reporta α, β, persistencia, volatilidad de largo plazo, volatilidad de hoy y vida media del shock.
- **EWMA:** λ = 0.94 (RiskMetrics).
- **Pronóstico:** reversión a la media de la varianza condicional; la σ promedio hasta el vencimiento es la que entra al árbol.
- **Monte Carlo:** 100,000 trayectorias GARCH día a día; mundo real (rendimiento esperado supuesto de 8% anual) para el rango de precios y mundo neutral al riesgo (r − q) para valuar.
- **Árbol CRR americano:** 500 pasos, dividendo continuo q (NVDA 0.47%, AMD 0%, XOM 2.25%), con griegas calculadas desde el árbol, nodos de 4 pasos con la decisión ejercer o esperar, y comprobación contra Monte Carlo europeo.
- **Señal de volatilidad:** razón σ GARCH ÷ σ implícita con umbral de 10%; se prueba su solidez con GARCH a 5, 3 y 2 años, la histórica de 1 año y EWMA.
- **Rentabilidad a 2 semanas:** trayectorias a 10 días hábiles, revaluación de la opción con lo que le queda de vida y venta al bid, medida contra el ask pagado.

## Limitaciones

- GARCH(1,1) supone normalidad y no captura asimetría (para eso existen GJR-GARCH y EGARCH).
- GARCH no conoce las fechas de reporte de resultados, y la volatilidad implícita sí las incorpora.
- La volatilidad implícita de TradingView sale de su propio modelo, por lo que el árbol con esa σ no reproduce exactamente el precio medio de mercado.
- El rendimiento esperado (8% anual), la tasa libre de riesgo y las cotizaciones del 30-oct son supuestos y datos de una fecha concreta.
- Las señales de NVDA y AMD son frágiles: cambian con la ventana de datos usada.

## Uso de inteligencia artificial

El trabajo se desarrolló con apoyo de herramientas de IA y fue revisado por el equipo:

- **TECgpt:** conversación en la que se construyó y verificó código en R base para cada bloque del análisis. Está en `evidencias/`.
- **Claude (Anthropic):** apoyo para armar y actualizar el Rmd, los notebooks y el dashboard, y para verificar que los resultados coincidieran entre archivos.

## Aviso

Material educativo para un curso de posgrado. No constituye una recomendación de inversión. Las opciones compradas pueden perder todo el valor pagado.
