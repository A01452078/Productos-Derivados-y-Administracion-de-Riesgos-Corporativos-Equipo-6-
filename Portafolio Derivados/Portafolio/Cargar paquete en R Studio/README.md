# Cargar paquete en R Studio

Versión plana del reporte para usar en **RStudio Cloud / Posit Cloud**, donde no existe la estructura de carpetas del proyecto.

## Contenido

- `Portafolio_Equipo6.Rmd`: el mismo reporte, pero con una búsqueda flexible de los datos (busca junto al Rmd o en una carpeta `Datos`).
- Siete archivos de datos: `historial_investopedia.csv`, `tradingview_posiciones.csv`, `swap_dv01.csv`, `swap_valuacion.csv`, `swap_regimenes.csv`, `swap_resumen_mc.csv` y `swap_montecarlo.png`.

## Cómo usarla

1. Subir **todos** estos archivos juntos a un proyecto de RStudio Cloud, en la misma carpeta (sin subcarpetas).
2. Abrir `Portafolio_Equipo6.Rmd` y hacer Knit to HTML.

Si falta algún archivo de datos, el Rmd se detiene con un mensaje que indica cuál y desde qué carpeta de trabajo está buscando.
