# Anexo de capturas de LSEG Workspace

Todas las capturas se tomaron el 6 de noviembre de 2026 (entre 12:11 y 15:04, hora de Ciudad de México) con el ticker WMT.O. El corte de datos del análisis es el 30 de octubre de 2026 (el 1 de noviembre para la curva del Tesoro), por lo que las pantallas en vivo (opciones, CDS, precio) muestran cifras posteriores. Los archivos de `09_datos/lseg_evidencia/` son las exportaciones del 1 de noviembre.

| Archivo | Mnemónico | Qué muestra |
|---|---|---|
| 01_Precio_Historico_WMT_2020-2026_QH | QH | Price History diario, 05-nov-2020 a 05-nov-2026. Fuente de `wmt_diario.csv` |
| 02_Opciones_Option_Watch_18dic2026_OPW | OPW | Cadena de opciones de Walmart, vencimiento 18-dic-2026 (bid, ask, volumen, interés abierto, volatilidad implícita, delta) |
| 03_Fundamentales_Financial_Summary_FINSUM | FINSUM | Resumen financiero trimestral consolidado |
| 04_Fundamentales_Income_Statement_INC | INC | Estado de resultados trimestral |
| 05_Fundamentales_Balance_Sheet_BAL | BAL | Balance general trimestral |
| 06_Deuda_Resumen_Debt_Structure_DS | DS | Estructura de deuda: 76 bonos, 45,917 millones USD vigentes, una línea de crédito por 17,000 millones |
| 07_Deuda_Escalera_Vencimientos_DSCOMP | DSCOMP | Saldo vigente por año de vencimiento |
| 08_Deuda_Tabla_por_Vencimiento_DSCOMP | DSCOMP | Emisiones, saldo vigente y monto emitido por año |
| 09_Deuda_Totales_Parametros_DSCOMP | DSCOMP | Deuda de Walmart 45,916 millones y de subsidiarias 1.06 millones |
| 10_Deuda_Grafica_por_Plazo_DSCOMP | DSCOMP | Composición de la deuda por bloques de diez años |
| 11_Calificaciones_SP_Issuer_Ratings_IR | IR | Calificaciones de S&P: AA, perspectiva estable |
| 12_Calificaciones_Moodys_Issuer_Ratings_IR | IR | Calificaciones de Moody's: Aa2 (afirmada 10-jun-2026) |
| 13_Calificaciones_Fitch_Issuer_Ratings_IR | IR | Calificaciones de Fitch: AA, perspectiva estable (2-oct-2026) |
| 14_Calificaciones_DBRS_Descontinuada_DSCOMP | DSCOMP | DBRS descontinuada (24-oct-2024) |
| 15_Curva_del_Emisor_ISCRV | ISCRV | Curva corporativa de Walmart: rendimiento, spread y probabilidad de incumplimiento por plazo |
| 16_Convertibles_Sin_Resultados_EXCNV | EXCNV | LSEG no encuentra convertibles ni canjeables de Walmart |
| 17_CDS_Overview_CDSOV | CDSOV | CDS a 5 años en 26.5 pb y a 10 años, recuperación de 40% |
| 18_CDS_Calculadora_CDSOV | CDSOV | Calculadora de CDS: nivel 25.6 pb, DV01 de crédito 474 |
| 19_Dividendos_Resumen_DIVO | DIVO | Rendimiento por dividendo histórico (0.79%) y proyectado (0.73%). No muestra el monto ni la fecha ex-dividendo |
| 20_Basis_Cruzado_CAD_USD_3Y_CADCBS | CADCBS3Y= | Basis swap CAD/USD a 3 años: -14.80 pb (6-nov-2026, 09:45) |
| 21_Basis_Cruzado_CAD_USD_5Y_CADCBS | CADCBS5Y= | Basis swap CAD/USD a 5 años: -11.60 pb (6-nov-2026, 09:14) |
| 22_Basis_Cruzado_CAD_USD_7Y_CADCBS | CADCBS7Y= | Basis swap CAD/USD a 7 años: -8.90 pb (6-nov-2026, 09:14) |
| 23_Basis_Cruzado_CAD_USD_10Y_CADCBS | CADCBS10Y= | Basis swap CAD/USD a 10 años: -5.10 pb (6-nov-2026, 09:10) |
