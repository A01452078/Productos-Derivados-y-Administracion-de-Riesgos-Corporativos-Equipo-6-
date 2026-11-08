# Datos

Insumos del reporte y salidas de la cobertura.

## Insumos

| Archivo | Contenido |
|---|---|
| `historial_investopedia.csv` | Historial de operaciones de Mariann en Investopedia (fecha, símbolo, tipo, cantidad, precio) |
| `tradingview_posiciones.csv` | Posiciones abiertas en TradingView Paper Trading (símbolo, lado, cantidad, precio promedio, P&L, vencimiento) |
| `historial_cme.xls` | Exportación original del historial de Investopedia (26 operaciones, hoja `simulator`) de la que se derivó `historial_investopedia.csv`. Es un HTML con extensión .xls: Excel lo abre y avisa del formato. A pesar del nombre, no es de CME, que no permite descargar su historial |

## Salidas de `Códigos/swap_cobertura.py`

| Archivo | Contenido |
|---|---|
| `swap_dv01.csv` | DV01 del libro de swaps por vida media (3 a 7 años) y contratos de ZN equivalentes |
| `swap_valuacion.csv` | Valor teórico de cada pata (Black, CRR americano y europeo) contra la prima del ticket |
| `swap_resumen_mc.csv` | Resumen del Monte Carlo por pata y conjunto: media, desviación, percentiles, probabilidad de ganar, VaR y CVaR |
| `swap_regimenes.csv` | P&L del put, del call y del total en cuatro regímenes (reflación, Fed restrictiva, Fed acomodaticia, aversión al riesgo) |
| `swap_montecarlo.png` | Distribución del P&L simulado, usada en el reporte y en la presentación |

El Rmd y los scripts buscan esta carpeta por su nombre `Datos`: no renombrarla.
