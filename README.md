# Equipo 6 · Productos Derivados y Administración de Riesgos Corporativos

**EGADE Business School, Tecnológico de Monterrey · Grupo 40**
Profesor: Dr. Raymundo Díaz Robles · Noviembre de 2026

| Integrante | Matrícula |
|---|---|
| Eduardo Ayala Saldaña | A01192714 |
| Mariann Antonelli Morales Tobias | A01452078 |
| Ulises Salinas López | A00814787 |

Este repositorio reúne los dos trabajos del curso en dos secciones independientes. Cada carpeta trae su propio README con el detalle de sus archivos.

| Sección | Carpeta | De qué trata |
|---|---|---|
| 1 | `Proyecto Final/` | Análisis de **Walmart Inc.**: estructura de financiamiento, valuación del bono convertible y coberturas |
| 2 | `Portafolio Derivados/` | **Portafolio de derivados** que el equipo operó en tres simuladores, con la cobertura de la semana del 6 al 9 de noviembre |

---

## Sección 1. Proyecto Final: Walmart Inc.

Perfil de deuda, calificaciones crediticias, valuación del bono convertible (árboles CRR con dividendos discretos, Black-Scholes-Merton y GARCH(1,1) sobre 1,507 observaciones), programa de swaps vigente y recomendaciones de cobertura.

| Carpeta | Contenido |
|---|---|
| `1. Reporte Ejecutivo/` | Reporte de doce páginas (PDF y Word) |
| `2. Dashboard/` | Tablero interactivo de once gráficos, autocontenido (HTML) |
| `3. Reporte Reproducible/` | R Markdown con la memoria de cálculo completa y su HTML |
| `4. Calculadora/` | Calculadora interactiva del bono convertible (HTML) |
| `5. Codigo Python/` | Motor de cálculo (`codigo python/`), notebooks y librería de gráficos |
| `6. Prompt IA/` | Conversaciones con TECgpt y registro del uso de IA |
| `7. Anexo Capturas/` | 23 capturas de LSEG Workspace, con índice y PDF del anexo |
| `8. Datos/` | Series y tablas fuente (LSEG), 10-K y 10-Q |
| `9. Presentacion/` | Presentación de 17 láminas (PPTX y PDF) |

Para reproducir: `Rscript -e 'rmarkdown::render("3. Reporte Reproducible/Reporte_Walmart.Rmd")'` y, desde `5. Codigo Python/codigo python/`, `python generar_dashboard.py`. Detalle en `Proyecto Final/README.md`.

## Sección 2. Portafolio de derivados

Registro de las operaciones del 21 de septiembre al 7 de noviembre de 2026 en Investopedia, CME Group Practice y TradingView Paper Trading. Las Tareas 1 a 3 son movimientos individuales de cada integrante; las Tareas 4 a 7 son trabajo en equipo, ejecutado en las cuentas de Mariann.

| Carpeta | Contenido |
|---|---|
| `Portafolio/` | Reporte consolidado (`.Rmd` y `.html`), carpeta de evidencias en PDF y presentación |
| `Códigos/` y `Notebooks/` | Un script por análisis (14) y sus notebooks ejecutados. El de esta semana es `swap_cobertura.py` |
| `Datos/` | Historiales, posiciones y salidas de la cobertura (CSV y gráfica del Monte Carlo) |
| `Screenshots/` | Capturas por simulador: Investopedia, CME y TradingView |
| `Prompts TecGPT/` | Conversaciones con TECgpt del portafolio y de la cobertura |
| `Histórico/` | Actividades 3 a 6 del curso |

Para reproducir: abrir `Portafolio/Portafolio_Equipo6.Rmd` en RStudio y hacer Knit; la cobertura se recalcula con `python swap_cobertura.py ../Datos` desde `Códigos/`. Detalle en `Portafolio Derivados/README.md`.

---

## Cómo se conectan las dos secciones

La cobertura de la semana (Sección 2) usa el caso de Walmart (Sección 1) como pretexto: el libro de swaps de tasa de Walmart (4,771 millones de dólares de nocional) y su deuda en dólares canadienses se traducen a instrumentos listados en CME. Una opción semanal put sobre el futuro de 10 años (ZN) cubre el riesgo de tasa y una call sobre el futuro del dólar canadiense (6C) cubre el de divisa; ambas vencen el 9 de noviembre. Los cálculos de DV01 y el Monte Carlo de esa cobertura están en `Portafolio Derivados/Códigos/swap_cobertura.py`. Fuera de ese puente, las dos secciones no comparten datos ni código.

## Criterio de trabajo

Ningún resultado se afirma sin que pueda reconstruirse. Los supuestos que no pudieron verificarse (por ejemplo, la vida media de los swaps de 5 años, que Walmart no publica, y la correlación de 0.30 entre ZN y 6C) están declarados como tales en el reporte correspondiente.

## Enlace del repositorio

https://github.com/A01452078/Productos-Derivados-y-Administracion-de-Riesgos-Corporativos-Equipo-6-
