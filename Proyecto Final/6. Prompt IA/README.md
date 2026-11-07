# 07 Uso de inteligencia artificial

Registro del uso de IA en el proyecto de Walmart, conforme al requisito del curso. La herramienta principal fue **TECgpt (ChatGPT, GPT 5.2)**, el portal institucional del Tec. Aquí están las tres conversaciones completas, con los prompts de Mariann, las respuestas de la IA, el código recibido y las correcciones hechas después de probarlo.

## Conversaciones

| # | Archivo | Fecha | Páginas | Tema |
|---|---|---|---|---|
| 1 | `TECgpt_1_Dashboard_deuda_Walmart_Rmd_27oct2026.pdf` | 27-oct-2026, 6:49 a 7:03 p. m. | 68 | Reproducir en R Markdown el dashboard de deuda de Walmart a partir de 53 notas vigentes (corte 23-oct-2026). |
| 2 | `TECgpt_2_Dashboard_R_convertible_y_coberturas_1nov2026.pdf` | 1-nov-2026, 4:08 a 4:59 p. m. | 109 | Estructura del dashboard y código en R: deuda, GARCH, convertible (caso Molson Coors), refinanciamiento y T-lock, y las secciones 1 a 17 del dashboard. |
| 3 | `TECgpt_3_Swap_CAD_USD_y_basis_6nov2026.pdf` | 6-nov-2026, 10:07 a 10:19 p. m. | 40 | Actualizar la sección "Cobertura con swaps" y las listas "Resueltos" y "Pendientes" con el basis cruzado CAD/USD de LSEG y los bonos vencidos de 2026. Script en Python. |

## Qué se hizo en cada una

**1. Dashboard de deuda en R Markdown (27-oct).**
Se le dio el rol de analista financiero y programador en R, el dashboard en HTML del equipo y el CSV de 53 notas. Se definieron las variables a calcular (años al vencimiento, valor de mercado, descuento, monto retirado, estadísticos ponderados) y se armó el documento por pasos: secciones 1 a 3 (tesis, escalera de vencimientos y composición por divisa), el análisis de los tramos a 2033 en USD y CAD (diferencial de curva), y el ensamblado final. La conversación cierra con un chunk de control automático que compara las cifras del documento contra los valores de referencia, y con la confirmación de que no quedan formatos de fecha problemáticos.

**2. Dashboard en R, GARCH y convertible (1-nov).**
Se adjuntaron los archivos de LSEG, 10-K, 10-Q y la nota del caso Molson Coors. Se propuso la estructura del dashboard y se pidió código en R para:
- la deuda vigente, el valor de mercado, el cupón y la YTM ponderados, la vida promedio y la escalera de vencimientos;
- el GARCH(1,1) por máxima verosimilitud con `optim`, sin paquetes externos;
- la valuación del convertible con primas de 15, 25, 40 y 60 % (Black-Scholes, árbol CRR y Monte Carlo);
- el costo de refinanciar la deuda de bajo cupón y el DV01 de un T-lock a 10 años.

Después se pidió replicar exactamente el diseño del dashboard final del equipo y se construyeron sus secciones una por una (portada con KPI, perfil financiero, gasto financiero, escalera, composición por divisa, tramos en CAD y las secciones 7 a 14 y 17).

**3. Basis cruzado CAD/USD (6-nov).**
Se dieron las cotizaciones de LSEG (basis de -14.8, -11.6, -8.9 y -5.1 pb a 3, 5, 7 y 10 años) y la lista de bonos vencidos de 2026. Se pidió redactar el texto del dashboard, revisar críticamente la respuesta y escribir un script en Python (numpy, pandas, Plotly) con: escenarios a favor y en contra del basis, tablas de sensibilidad (basis, equilibrio y nocional), pruebas con `assert`, una gráfica y un resumen ejecutivo. La conversación termina con un resumen del uso de la IA, corregido para describir con exactitud lo que se pidió.

## Cómo se verificó lo que entregó la IA
El código no se aceptó tal cual. Las correcciones quedan en las propias conversaciones. Algunos ejemplos:
- **GARCH (conversación 2):** el primer código convergía a un máximo local (alfa 0.055, beta 0.725, persistencia 0.78). Se pidió reestimar con rendimientos logarítmicos por 100, Nelder-Mead, restricciones y tres puntos iniciales, hasta obtener omega 0.03204, alfa 0.01562, beta 0.96933 y persistencia 0.985.
- **Convertible (conversación 2):** se corrigió el descuento del bono recto (cupones semestrales con tasa semestral discreta) y se resolvió el cupón a la par con `uniroot`. El resultado de referencia fue una opción de 201.1 por bono y un cupón de 1.13 % con 25 % de prima.
- **Lectura de datos (conversación 2):** se corrigió la lectura de la hoja "Bonds" del Excel (tres tablas apiladas con encabezados repetidos) y un choque de nombres con `dplyr::pick()`.
- **Gasto financiero (conversación 2):** se evitó contar dos veces los arrendamientos.
- **Controles (conversación 1):** el documento compara sus cifras contra valores de referencia y avisa con `warning()` si difieren.
- **Basis (conversación 3):** se pidió corregir un `NaN` en la tabla por plazo, marcar los costos fuera de 7 años como ilustrativos y etiquetar como ahorro los casos con residual negativo. Las cifras del script se contrastaron con `wmt_swaps.py` (12.28 millones al año con basis 0; 9.1020 y 15.4555 a 7 años).

## Alcance y límites
- Los datos provienen de LSEG Workspace y de los reportes de Walmart (10-K y 10-Q). La IA no aportó datos de mercado: trabajó con los que se le entregaron.
- Todo resultado que aparece en los entregables se contrastó con los archivos de `09_datos` y con las capturas de `08_anexo_capturas`.
- En el PDF de la conversación 3, un prompt muestra caracteres como `é` en lugar de letras con acento. Es un detalle de cómo se pegó el texto, no afecta el contenido.

## Otro archivo
- `Prompt_IA_Walmart.pdf`: resumen de 5 páginas del uso de Claude (Anthropic) durante el trabajo previo (25-oct a 1-nov), con prompts, código recibido y registro de correcciones.
