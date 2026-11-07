# 03 Reporte reproducible (R Markdown)

Memoria de cálculo del análisis, con el código y los resultados en un mismo documento.

## Archivos
| Archivo | Descripción |
|---|---|
| `Reporte_Walmart.Rmd` | Código fuente en R Markdown. |
| `Reporte_Walmart.html` | Documento renderizado. |

## Contenido
Árbol binomial CRR con dividendo discreto (escrow), Black-Scholes-Merton, estimación GARCH(1,1) por máxima verosimilitud, bootstrapping de la curva del Tesoro y valuación de swaps (tasa flotante, cross-currency y T-lock).

## Cómo regenerarlo
Desde RStudio, abrir el `.Rmd` y pulsar Knit, o desde la terminal:

    Rscript -e 'rmarkdown::render("Reporte_Walmart.Rmd")'

Usa R base y `knitr`. Los datos están en `../09_datos`.
