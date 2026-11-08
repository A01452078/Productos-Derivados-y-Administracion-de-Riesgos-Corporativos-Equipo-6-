# Notebooks

Los 14 scripts de `Códigos/` como notebooks de Jupyter / Colab, ya ejecutados (con sus salidas visibles). El nombre de cada notebook coincide con el del script.

| Notebook | Tema |
|---|---|
| `swap_cobertura.ipynb` | Cobertura del libro de swaps: DV01, valuación, Monte Carlo y regímenes (el de esta semana) |
| `fx_6c`, `zn`, `nov20`, `plazo`, `vencimientos`, `strike_cmp` | Calibración de las cadenas de 6C y ZN |
| `cartera`, `pnl`, `cl_diag` | Análisis conjunto, escenarios de P&L y diagnóstico de crudo |
| `pnl_edu`, `cme_closed`, `estrategias`, `spreads` | Cuentas individuales y comparación de spreads |

## Cómo usarlos

- **Colab:** subir el notebook y ejecutar todo. `swap_cobertura.ipynb` guarda sus tablas en una carpeta de salida (variable `SALIDA` en la primera celda de código); cámbiala si quieres escribir en `Datos/`.
- **Local:** `jupyter notebook` desde esta carpeta. Los datos de referencia están en `../Datos/`.

El código fuente de cada análisis es el de `Códigos/`; si se modifica uno, conviene regenerar el otro para que no diverjan.
