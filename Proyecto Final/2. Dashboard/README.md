# 02 Dashboard

Tablero interactivo de Walmart en un solo archivo HTML, con gráficas de Plotly incrustadas. Se abre con doble clic en cualquier navegador, sin conexión a internet.

## Archivo
- `Dashboard_Walmart.html`

## Secciones
Tesis (caso Molson Coors), escalera de vencimientos, composición por divisa, emisión del 23 de octubre de 2026, calificación crediticia, curva de rendimiento, pared de refinanciamiento, recompras, opciones sobre WMT, ejercicio anticipado, convertible propuesto, estructura completa, pronóstico GARCH, cobertura con swaps y pendientes.

## Cómo se regenera
No se edita a mano. Lo produce `../06_codigo_python/generar_dashboard.py`, que lee los datos de `../09_datos` y verifica 13 cifras contra el reporte:

    cd ../06_codigo_python
    python generar_dashboard.py
