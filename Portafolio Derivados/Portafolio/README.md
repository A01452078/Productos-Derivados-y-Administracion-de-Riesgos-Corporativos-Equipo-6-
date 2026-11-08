# Portafolio

Entregables principales del proyecto.

| Archivo | Qué es |
|---|---|
| `Portafolio_Equipo6.Rmd` | Código fuente del reporte consolidado (historia de movimientos, estrategia explicada, cuentas del equipo e individuales y cobertura de swaps) |
| `Portafolio_Equipo6.html` | El reporte ya generado con Knit. Es la evidencia de los movimientos de la semana |
| `Reporte_Portafolio_Equipo6.pdf` | Carpeta de evidencias en un solo PDF: historia, estrategia, capturas, código y prompt de TECgpt |
| `PPT_Portafolio_Equipo6.pdf` | Presentación del equipo |
| `Cargar paquete en R Studio/` | Versión plana para RStudio Cloud (ver su README) |

## Cómo hacer Knit

1. Abrir `Portafolio_Equipo6.Rmd` en RStudio (en esta misma carpeta).
2. Verificar que la carpeta `Datos/` esté al lado de `Portafolio/`: el Rmd lee de `../Datos/`.
3. Knit to HTML. Debe producir el mismo `Portafolio_Equipo6.html`.

Si RStudio marca que no encuentra `historial_investopedia.csv`, usar la subcarpeta `Cargar paquete en R Studio/`, que busca los datos junto al Rmd.
