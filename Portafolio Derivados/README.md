# Portafolio de derivados del Equipo 6

**Equipo 6 · Grupo 40 · EGADE Business School**
Productos Derivados y Administración de Riesgos Corporativos · Dr. Raymundo Díaz Robles · Noviembre de 2026

Integrantes: Eduardo Ayala Saldaña (A01192714), Mariann Antonelli Morales Tobias (A01452078) y Ulises Salinas López (A00814787).

---

## De qué trata

Registro de las operaciones del equipo del 21 de septiembre al 7 de noviembre de 2026 en tres plataformas: Investopedia, CME Group Practice y TradingView Paper Trading. Las Tareas 1 a 3 son movimientos **individuales** de cada integrante; las Tareas 4 a 7 son **trabajo en equipo**, ejecutado en las cuentas de Mariann.

La última semana conecta con el caso de Walmart (ver `../Proyecto Final/`): su libro de swaps de tasa (4,771 millones de dólares de nocional) y su deuda en dólares canadienses se cubren con instrumentos listados en CME, con opciones semanales que vencen el 9 de noviembre.

## Carpetas (cada una trae su propio README)

| Carpeta | Contenido |
|---|---|
| `Portafolio/` | Reporte consolidado (`Portafolio_Equipo6.Rmd` y `.html`), carpeta de evidencias en PDF y presentación |
| `Códigos/` | Un script de Python por análisis, 14 en total. El de esta semana es `swap_cobertura.py` |
| `Notebooks/` | Los mismos scripts como notebooks ejecutados |
| `Datos/` | Historiales, posiciones y salidas de la cobertura (CSV y gráfica del Monte Carlo) |
| `Screenshots/` | Capturas por simulador: `Investopedia/`, `CME/` y `TradingView/` |
| `Prompts TecGPT/` | Conversaciones con TECgpt del portafolio y de la cobertura de swaps |
| `Histórico/` | Actividades 3 a 6 del curso (Rmd, HTML, notebooks, capturas y TECgpt) |

## Individual y de equipo

| Cuenta | Tipo | Dónde se documenta |
|---|---|---|
| Equipo (operada en las cuentas de Mariann) | Tareas 4 a 7 | Sección 6 del reporte y `Screenshots/` |
| Mariann | Individual, Tareas 1 a 3 | Sección 6 del reporte (columna Origen) |
| Eduardo | Individual | Secciones 2 y 3 del reporte |
| Ulises | Individual | Secciones 2 y 3 del reporte |

## La cobertura de la semana

| Pata | Instrumento | Cantidad | Prima |
|---|---|---|---|
| Tasa | Put semanal ZNA6, strike 107.25 | 5 contratos | 0.25 puntos (1,250 USD) |
| Divisa | Call semanal 6C66, strike 0.715 | 8 contratos | 0.00005 (40 USD) |

Órdenes del 6 de noviembre (2:59 pm CST, 2.40 días al vencimiento), ejecutadas por Mariann en CME Practice. Prima total: 1,290 USD (1.27% de la cuenta CME), que es también la pérdida máxima.

- **Escala:** bajo el supuesto de curva plana al par 5Y y vida media de 5 años, el DV01 del libro es de unos 2.08 millones de USD por punto base. Los 5 puts equivalen a unos 2.26 futuros de ZN (DV01 cercano a 140 USD por pb), cerca de 0.0067% de ese riesgo. La posición es una demostración del método y un hedge táctico de muy corto plazo, no una cobertura integral.
- **Monte Carlo** (200,000 trayectorias, correlación 0.30 entre ZN y 6C): desviación del P&L conjunto de unos 1,735 USD y probabilidad de ganar de 48%. El put por sí solo tiene media negativa de unos 260 USD, el costo del seguro. La media positiva del conjunto proviene de haber pagado el call en el mínimo de 0.00005, muy por debajo de su valor teórico (punto de equilibrio: 0.000493), y no debe leerse como ventaja esperada.

## Cómo reproducir

- **Reporte:** abrir `Portafolio/Portafolio_Equipo6.Rmd` en RStudio y hacer Knit. Lee los CSV de `../Datos/`. En RStudio Cloud usar la subcarpeta `Portafolio/Cargar paquete en R Studio/`.
- **Cobertura:** desde `Códigos/`, `python swap_cobertura.py ../Datos`. El subyacente y la volatilidad vienen de `zn.py` y `fx_6c.py`; la prima y las cantidades son las de los tickets de CME (`Screenshots/CME/ticket_*`).

## Alcance y supuestos

- CME Practice no permite descargar el historial de operaciones; los movimientos de CME se documentan con capturas.
- Los libros de Eduardo y Ulises se incorporan con lo auditado al 5 de noviembre.
- Supuestos del modelo de cobertura: vida media de los swaps de 5 años (no publicada en el 10-K), correlación de 0.30 entre ZN y 6C (probada de -0.3 a 0.6), volatilidad implícita constante y DV01 de ZN cercano a 62 USD por contrato.
- Si se renombran las carpetas, conservar el nombre `Datos`: el Rmd y los scripts la buscan por nombre.
