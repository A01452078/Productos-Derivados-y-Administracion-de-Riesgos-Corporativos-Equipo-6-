# 05 Calculadora del convertible

Herramienta interactiva para valuar el bono convertible propuesto para Walmart.

## Archivo
- `Calculadora_Convertible.html`: se abre en el navegador, sin dependencias externas.

## Qué hace
Con los parámetros editables (precio de la acción, plazo, rendimiento del bono recto, volatilidad, rendimiento por dividendo, prima de conversión y otros) calcula el cupón a la par por bisección. Descompone el convertible en bono recto más opción call (Black-Scholes con rendimiento por dividendo), igual que el caso Molson Coors.

## Alcance
Solo cubre la valuación del convertible. El árbol binomial, el GARCH y los swaps están en `../06_codigo_python`.
