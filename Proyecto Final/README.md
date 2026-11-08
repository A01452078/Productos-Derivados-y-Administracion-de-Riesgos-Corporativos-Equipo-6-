# Proyecto Final: Walmart Inc.

**Equipo 6 · Grupo 40 · EGADE Business School**
Productos Derivados y Administración de Riesgos Corporativos · Dr. Raymundo Díaz Robles · Noviembre de 2026

| Integrante | Matrícula |
|---|---|
| Eduardo Ayala Saldaña | A01192714 |
| Mariann Antonelli Morales Tobias | A01452078 |
| Ulises Salinas López | A00814787 |

---

## De qué trata

Análisis de **Walmart Inc. (WMT.O)**: estructura de financiamiento, calificaciones crediticias, valuación de un bono convertible propuesto, programa de swaps vigente y recomendaciones de cobertura. Esta sección contiene solo el proyecto de Walmart; el portafolio de derivados que el equipo operó en los simuladores es un trabajo aparte y está en `../Portafolio Derivados/`.

Corte de datos: 30 de octubre de 2026 (precio, opciones y curva del Tesoro); la deuda se valúa con precios del 23 de octubre. Fuentes: LSEG Workspace, Tradeweb y los reportes a la SEC (10-K y 10-Q).

## Contenido

| Carpeta | Qué contiene |
|---|---|
| `1. Reporte Ejecutivo/` | Documento de doce páginas (`.pdf` y `.docx`): perfil de deuda, calificaciones, valuación del convertible, swaps vigentes y recomendaciones |
| `2. Dashboard/` | `Dashboard_Walmart.html`: tablero interactivo de once gráficos (escalera de vencimientos, divisas, curva, sonrisa de volatilidad, ejercicio anticipado, GARCH, calificaciones y swaps). Autocontenido, se abre sin conexión |
| `3. Reporte Reproducible/` | `Reporte_Walmart.Rmd` y su `.html`: memoria de cálculo con árboles CRR y dividendos discretos (escrow), Black-Scholes-Merton, GARCH(1,1) por máxima verosimilitud, bootstrapping de la curva del Tesoro y valuación de swaps. Solo R base y `knitr` |
| `4. Calculadora/` | `Calculadora_Convertible.html`: valúa el convertible con nueve parámetros editables y resuelve el cupón a la par por bisección. Sin dependencias |
| `5. Codigo Python/` | `codigo python/` (motor de cálculo), `notebooks/` (uno por script, ejecutados) y `assets/` (librería Plotly) |
| `6. Prompt IA/` | Tres conversaciones con TECgpt y el registro del uso de IA conforme al requisito del curso |
| `7. Anexo Capturas/` | 23 capturas de LSEG Workspace con `INDICE.md` y el PDF `Anexo_Capturas_LSEG_Walmart.pdf` |
| `8. Datos/` | Series y tablas fuente, exportaciones de LSEG y los reportes 10-K y 10-Q (archivos sueltos, sin subcarpetas) |
| `9. Presentacion/` | Presentación de 17 láminas (`.pptx` y `.pdf`) basada en el reporte ejecutivo |

Cada carpeta con documentación propia trae su `README.md` o `LEEME.md`.

## Código

| Script | Qué hace |
|---|---|
| `wmt_derivados.py` | Opciones, griegas, volatilidad implícita y valuación del convertible |
| `garch_wmt.py` | Estimación GARCH(1,1) sobre 1,507 cierres diarios |
| `wmt_swaps.py` | Swaps de tasa, cross-currency y T-lock |
| `convertible_validacion.py` | Validación del modelo con el caso Molson Coors y con Walmart |
| `generar_dashboard.py` | Lee `8. Datos/`, recalcula todo, verifica 13 cifras contra el reporte ejecutivo y escribe `2. Dashboard/Dashboard_Walmart.html` |

Todos usan solo la biblioteca estándar, salvo `generar_dashboard.py`, que además requiere `numpy`, `pandas` y `openpyxl`.

## Cómo reproducir

```bash
# Reporte reproducible (desde esta carpeta)
Rscript -e 'rmarkdown::render("3. Reporte Reproducible/Reporte_Walmart.Rmd")'

# Dashboard (desde "5. Codigo Python/codigo python")
python generar_dashboard.py
# o indicando las rutas:
python generar_dashboard.py --datos "../../8. Datos" --salida "../../2. Dashboard/Dashboard_Walmart.html"

# Motor de cálculo
python wmt_derivados.py
```

## Verificación de las cifras

Ningún resultado se afirma sin que pueda reconstruirse. El modelo se valida contra la volatilidad implícita de LSEG y contra el ejemplo de la put americana de Hull. `generar_dashboard.py` compara 13 cifras clave contra el reporte ejecutivo y avisa si alguna difiere. Los supuestos que no pudieron verificarse están declarados en la sección de limitaciones del reporte.

## Datos y evidencia

- `8. Datos/` separa los archivos de trabajo (`wmt_diario.csv`, `dec18.csv`, `vol_term.csv`, `curva.csv`, `LSEG_Deuda_WMT.xlsx`, `LSEG_Fundamentales_WMT.xlsx`, `LSEG_Curva_Tesoro_formulas.xlsx`), que leen los scripts, de los archivos de respaldo (exportaciones de LSEG del 1 y 6 de noviembre y reportes a la SEC), que documentan el acceso a las fuentes pero no alimentan los cálculos.
- `Price_History_20261106_1157.xlsx` (05-nov-2020 a 05-nov-2026, 1,507 cierres) coincide exactamente con `wmt_diario.csv`.
- Las capturas de `7. Anexo Capturas/` son del 6 de noviembre, posteriores al corte del 30 de octubre, por lo que las pantallas en vivo (opciones, CDS, precio) muestran cifras ligeramente distintas; el índice señala cada diferencia.
- Las capturas de las plataformas de operación (saldos y órdenes) están en `../Portafolio Derivados/Screenshots/`.

## Presentación y repositorio

La última lámina de la presentación lista los entregables. Repositorio: https://github.com/A01452078/Productos-Derivados-y-Administracion-de-Riesgos-Corporativos-Equipo-6-
