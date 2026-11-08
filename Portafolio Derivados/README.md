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

## Resumen por tarea y por cuenta

El portafolio se construyó en ciclos. Cada uno agrega una idea al anterior y el último los une con el caso de Walmart.

**Tareas 1 a 3 (individuales), una cuenta por integrante:**

| Cuenta | Qué operó |
|---|---|
| Mariann | Protective put, bull spread y valuación con Black-Scholes |
| Eduardo | Investopedia: acciones y opciones sobre AAPL, NVDA, SPY, JPM, SLV y TLT. CME: un call sobre el E-mini S&P y un bull call spread sobre oro (OG nov-26) |
| Ulises | AAPL: compras de opciones del 24-sep y venta de 200 acciones el 5-nov; bull call spread sobre crudo (apertura del 6-oct) |

**Estructuras que el reporte identifica dentro de esos libros:**

| Estructura | Detalle |
|---|---|
| Protective put sobre AAPL | Armada dos veces, con desenlaces opuestos: Eduardo el 30-sep y Ulises en su Tarea 2 |
| Straddle sobre el SPY | Call y put con strike 778 y el mismo vencimiento, comprados el 13-oct |
| Bull call spreads | Oro (Eduardo) y crudo (Ulises): misma estructura, calibraciones muy distintas |

**Tareas 4 a 7 (equipo), ejecutadas en las cuentas de Mariann:**

| Ciclo | Plataforma | Qué se hizo |
|---|---|---|
| Posiciones del 16-oct | TradingView e Investopedia | Opciones sobre SPY, NVDA, JPM, XOM, TLT, SLV y GLD |
| Ciclo III, 18-dic | Investopedia y TradingView | Posiciones abiertas, entre ellas calls sobre NVDA y ASML |
| Ciclo del 5-nov | CME Practice | Primer diseño de la cobertura sobre las dos exposiciones de Walmart, con las cadenas del 20-nov (calibradas en los scripts de `Códigos/`) |
| Semana del 6 al 9-nov | CME Practice | Versión final con opciones semanales que vencen el 9-nov, como pidió el profesor (sección siguiente) |

Resultados de las cuentas individuales:

| Cuenta | Saldo | Lugar en Investopedia |
|---|---|---|
| Eduardo | $1,003,085 | 2 de 22 |
| Ulises | $1,003,845 | 3 de 22 |
| Mariann | $989,318.90 | 18 de 22 |

Hallazgos del reporte consolidado: las cifras de cada cuenta están cuadradas contra los saldos de las plataformas (en la cuenta de Eduardo el residuo es cero) y el libro de Investopedia tuvo una tasa de acierto de 55% con una razón ganancia/pérdida de 2.38 a 1. El resultado realizado total fue negativo por haber sostenido tres posiciones de CME hasta que su valor temporal se agotó. También se documenta un patrón del equipo: dejar que el precio unitario de la opción, y no el riesgo, determine el tamaño (put de TLT en Investopedia, call de ASML en el ciclo III). La cobertura de la semana corrige ese sesgo con dos posiciones de tamaño comparable y pérdida máxima conocida.

## El cierre: la cobertura de la semana

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
