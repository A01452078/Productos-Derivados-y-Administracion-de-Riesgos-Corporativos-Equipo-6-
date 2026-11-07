# 06 Código

Motor de cálculo del proyecto de Walmart. Cada script tiene su notebook en `notebooks/`.

## Scripts
| Script | Qué hace |
|---|---|
| `wmt_derivados.py` | Black-Scholes, árbol CRR de 800 pasos con dividendo discreto, griegas, volatilidad implícita, validación contra Hull y LSEG, valuación del convertible y del call spread. |
| `garch_wmt.py` | Estima el GARCH(1,1) por máxima verosimilitud y pronostica la volatilidad. |
| `wmt_swaps.py` | Bootstrapping de la curva, swap de tasa flotante, swap cross-currency CAD/USD (con el basis de LSEG del 6-nov-2026) y T-lock. |
| `convertible_validacion.py` | Validación de la metodología con Molson Coors (2007) y aplicación a Walmart. |
| `generar_dashboard.py` | Genera `../02_dashboard/Dashboard_Walmart.html` y verifica 13 cifras contra el reporte. |

## Carpetas
- `notebooks/`: un notebook por script, ya ejecutados (ver su `LEEME.md`).
- `assets/`: librería `plotly-basic.min.js`, que el generador incrusta en el dashboard. No moverla.
- `auxiliares/`: scripts de versiones previas, no necesarios para reproducir resultados.
- `colab_avance2/`: los dos notebooks de Colab entregados en el Avance 2.

## Cómo correr
    python wmt_derivados.py
    python garch_wmt.py
    python wmt_swaps.py
    python convertible_validacion.py
    python generar_dashboard.py

Los scripts leen los datos de `../09_datos`.
