# 09 Datos

Datos fuente del análisis. Fecha de corte: 30 de octubre de 2026 (precio, opciones y curva).

## Archivos de trabajo (los que leen los scripts)
| Archivo | Contenido |
|---|---|
| `wmt_diario.csv` | 1,507 cierres diarios de WMT (del 5-nov-2020 al 5-nov-2026), usados en el GARCH. |
| `dec18.csv` | Cadena de opciones con vencimiento 18-dic-2026: 11 strikes (100 a 150) con precios, volatilidad implícita y griegas de LSEG. |
| `vol_term.csv` | Volatilidad implícita ATM por vencimiento (10 vencimientos). |
| `curva.csv` | Curva del Tesoro a 13 plazos. |

## Carpetas
- `lseg/`: exportaciones de LSEG Workspace usadas por el generador del dashboard: `LSEG_Deuda_WMT.xlsx`, `LSEG_Fundamentales_WMT.xlsx` y `LSEG_Curva_Tesoro_formulas.xlsx`.
- `lseg_evidencia/`: exportaciones de respaldo (precio histórico, estructura de deuda con bonos vencidos, calificaciones, CDS y convertibles). No alimentan los cálculos: documentan el acceso a LSEG.
- `sec/`: 10-K (marzo de 2026) y 10-Q (agosto de 2026) de Walmart.

## Fuentes
LSEG Workspace, Tradeweb (curva del Tesoro) y reportes a la SEC.
