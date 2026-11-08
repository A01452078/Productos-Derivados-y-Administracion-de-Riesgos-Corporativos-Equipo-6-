# Códigos

Scripts de Python, uno por análisis. Cada archivo explica su propósito en el docstring inicial y tiene su notebook equivalente en `Notebooks/`.

## Cobertura de la semana (swaps de Walmart)

| Script | Qué hace |
|---|---|
| `swap_cobertura.py` | DV01 del libro de swaps (curva plana al par 5Y, sensibilidad de 3 a 7 años de vida media), valuación del put ZN y del call 6C (Black, CRR americano y europeo), Monte Carlo de 200,000 trayectorias con correlación de 0.30, escenarios por régimen y comparación con ZN solo. Escribe los CSV y la gráfica en `Datos/` |

Uso: `python swap_cobertura.py ../Datos`. Parámetros de los tickets del 6-nov: put ZNA6 107.25 (5 contratos, prima 0.25) y call 6C66 0.715 (8 contratos, prima 0.00005), con vencimiento el 9-nov.

## Análisis de las cadenas y del diseño (6C y ZN)

Calibraciones y comparaciones hechas con las cadenas de opciones leídas el 5-nov en CME. Sirvieron de base para el diseño final con opciones semanales del 9-nov.

| Script | Qué hace |
|---|---|
| `fx_6c.py` | Calibración de la cadena de opciones sobre el futuro del dólar canadiense (Black 1976) |
| `zn.py` | Cadena de opciones sobre el futuro del bono a 10 años y convención de cotización (32avos y 64avos) |
| `nov20.py` | Reconstrucción de la cadena de 6C del 20-nov y verificación por paridad put-call |
| `plazo.py` | Calibración inversa del plazo a partir del precio y la volatilidad implícita |
| `vencimientos.py` | Criterio para elegir el vencimiento del call de 6C |
| `strike_cmp.py` | Comparación de ejecución entre strikes del put de ZN (107.25 contra 107.5) |
| `cartera.py` | Análisis conjunto de las dos patas: si se compensan entre sí |
| `pnl.py` | Escenarios de P&L del call de 6C |
| `cl_diag.py` | Diagnóstico de ejecutabilidad de la cadena de crudo (CLF7) |

## Cuentas individuales

| Script | Qué hace |
|---|---|
| `pnl_edu.py` | Reconstrucción del P&L realizado de Eduardo en Investopedia |
| `cme_closed.py` | Reconstrucción del P&L realizado de Eduardo en CME Practice |
| `estrategias.py` | Identificación de estrategias dentro del historial de Eduardo |
| `spreads.py` | Comparación de los dos bull call spreads del equipo (oro de Eduardo y crudo de Ulises) |

Requisitos: Python 3 con `numpy`, `scipy` y `pandas`.
