# 09 Datos

Datos fuente del análisis de Walmart (WMT.O). Todos los archivos están sueltos en esta carpeta, sin subcarpetas.

Fecha de corte: **30 de octubre de 2026** (precio, opciones y curva del Tesoro). La deuda se valúa con precios del 23 de octubre de 2026.

## Archivos de trabajo
Son los que leen los scripts de `../06_codigo_python`.

| Archivo | Contenido | Quién lo usa |
|---|---|---|
| `wmt_diario.csv` | 1,507 cierres diarios de WMT, del 5-nov-2020 al 5-nov-2026. Columnas `Date` y `WMT`. El cierre del 30-oct-2026 (123.51 USD) es el precio spot del análisis. | `garch_wmt.py` y `generar_dashboard.py` |
| `dec18.csv` | Cadena de opciones con vencimiento 18-dic-2026: 11 strikes (100 a 150), con bid, ask, último, volumen, interés abierto, volatilidad implícita y griegas (delta, gamma, vega, theta, rho) de calls y puts, tal como las reporta LSEG. | `wmt_derivados.py` y `generar_dashboard.py` |
| `vol_term.csv` | Volatilidad implícita ATM por vencimiento (10 vencimientos, del 20-nov-2026 al 19-ene-2029). Columnas `vencimiento` e `iv_atm_pct`. | `generar_dashboard.py` |
| `curva.csv` | Curva del Tesoro de EE. UU. a 13 plazos (1 mes a 30 años), rendimiento en %. Columnas `plazo_anios`, `tenor` y `yield_pct`. Base del bootstrapping y del T-lock (7 años: 4.8230 %). | `wmt_swaps.py` y `generar_dashboard.py` |
| `LSEG_Deuda_WMT.xlsx` | Búsqueda de bonos de Walmart en LSEG (hoja `Search Results`, unas 80 filas): cupón, vencimiento, divisa, monto emitido y vigente, precio, rendimiento y Z-spread. Base de la escalera de vencimientos y de la composición por divisa. | `generar_dashboard.py` |
| `LSEG_Fundamentales_WMT.xlsx` | Estados financieros trimestrales: `Financial Summary`, `Income Statement`, `Balance Sheet`, `Cash Flow`, `Valuation`, `Operating Metrics` y las líneas de negocio por segmento y geografía. | Reporte y dashboard |
| `LSEG_Curva_Tesoro_formulas.xlsx` | Hoja `Government Bond Prices` con los rendimientos del Tesoro; de ahí sale `curva.csv`. | Origen de `curva.csv` |

## Archivos de respaldo (evidencia de acceso a LSEG)
No alimentan los cálculos. Documentan que los datos provienen de LSEG Workspace. Las capturas correspondientes están en `../08_anexo_capturas`.

| Archivo | Contenido |
|---|---|
| `Price_History_20261101_0154.csv` | Exportación del historial de precios de WMT.O hecha el 1-nov-2026. |
| `Price_History_20261106_1157.xlsx` | Exportación del 6-nov-2026. Sus cierres coinciden con `wmt_diario.csv`. |
| `WALMART_INC__01-Nov-2026_020202_Debt_Structure.xlsx` | Estructura de deuda con cuatro hojas: `Summary`, `Bonds`, `Loans` e `Inactive Bonds`. Esta última trae los bonos vencidos, entre ellos los cinco de 2026 que cita el dashboard (euro 2.550 %, USD 4.000 %, USD 3.050 %, USD 5.502 % con put y USD 1.050 %). |
| `IssuerRatings_Walmart_Inc._Sun_Nov_01_2026_T02_03_20.xls` | Calificaciones de S&P, Moody's, Fitch y otras agencias. Tiene extensión `.xls`, pero su formato real es xlsx. |
| `CDSOverview.xlsx` | Credit Default Swap de Walmart (5 y 10 años). Contexto de riesgo de crédito. |
| `EXCHANGEABLES_AND_CNVS.xlsx` | Consulta de convertibles y canjeables de Walmart: LSEG no encuentra ninguno, lo que confirma que el convertible del análisis es una propuesta. |

## Reportes a la SEC
| Archivo | Contenido |
|---|---|
| `Receipt_Date_-_2026-Mar-13_-_WMT.OQ_..._10-K_..._26752440.pdf` | 10-K de Walmart (recibido el 13-mar-2026): deuda, derivados vigentes (nota 7) y calificaciones. |
| `Receipt_Date_-_2026-Aug-28_-_WMT.OQ_..._10-Q_..._261340128.pdf` | 10-Q de Walmart (recibido el 28-ago-2026): cifras del trimestre a julio de 2026. |

## Fuentes
LSEG Workspace, Tradeweb (curva del Tesoro) y reportes a la SEC.

## Nota sobre fechas
Los archivos de respaldo y las capturas son del 1 y 6 de noviembre, posteriores al corte del 30-oct. Por eso algunas cifras en vivo (opciones, CDS, deuda) difieren ligeramente de las del análisis. El anexo de capturas señala cada diferencia.
