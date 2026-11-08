# -*- coding: utf-8 -*-
"""
Eleccion del vencimiento para una call sobre 6CZ6 que debe seguir VIVA
y con valor temporal el jueves 12-nov, fecha en que se fotografia el
portafolio para el reporte.

El criterio no es minimizar la prima sino maximizar la fraccion del valor
que sobrevive a la erosion temporal, para que el P&L del 12-nov refleje el
movimiento del subyacente y no la simple muerte del theta.
"""
from math import log, sqrt, exp, erf, pi

F, RF, MULT = 0.7145, 0.0394, 100_000.0
N = lambda x: 0.5 * (1.0 + erf(x / sqrt(2.0)))
n = lambda x: exp(-0.5 * x * x) / sqrt(2.0 * pi)

def black76(F, K, T, r, s, tipo="call"):
    if s <= 0 or T <= 0:
        return exp(-r*T) * (max(F-K,0.0) if tipo=="call" else max(K-F,0.0))
    d1 = (log(F/K) + 0.5*s*s*T) / (s*sqrt(T)); d2 = d1 - s*sqrt(T)
    if tipo == "call": return exp(-r*T) * (F*N(d1) - K*N(d2))
    return exp(-r*T) * (K*N(-d2) - F*N(-d1))

def griegas(F, K, T, r, s, tipo="call"):
    d1 = (log(F/K) + 0.5*s*s*T) / (s*sqrt(T)); d2 = d1 - s*sqrt(T)
    de = exp(-r*T) * (N(d1) if tipo=="call" else N(d1)-1.0)
    ga = exp(-r*T) * n(d1) / (F*s*sqrt(T))
    ve = exp(-r*T) * F * n(d1) * sqrt(T) / 100.0          # por punto de vol
    th = (-exp(-r*T)*F*n(d1)*s/(2*sqrt(T))) / 365.0        # por dia natural
    return de, ga, ve, th

# La IV de 1.32 dias (6.01%) no se extrapola: la estructura temporal de
# volatilidad en divisas sube con el plazo porque los vencimientos ultracortos
# descuentan sesiones sin eventos. Se usa un rango para acotar.
IV_CORTA = 0.0601
ESCENARIOS = [("piso", IV_CORTA), ("central", 0.070), ("techo", 0.080)]

VENCS = [("13-nov", 8.32), ("17-nov", 12.32), ("20-nov", 15.32),
         ("25-nov", 20.32), ("27-nov", 22.32)]
DIAS_HASTA_CORTE = 7.0   # del 5-nov al 12-nov

print("=" * 78)
print("A. EROSION TEMPORAL: QUE FRACCION DE LA PRIMA SIGUE VIVA EL 12-NOV")
print("=" * 78)
print("   Supuesto: el futuro no se mueve. Solo actua el paso del tiempo.")
print("   Strike at-the-money (0.715). Volatilidad central 7.00%.\n")
print(f"   {'Vencimiento':>12} {'DTE hoy':>8} {'DTE 12-nov':>11} "
      f"{'prima hoy':>11} {'prima 12-nov':>13} {'retiene':>9}")
K = 0.715
for nom, dte in VENCS:
    rem = dte - DIAS_HASTA_CORTE
    p0 = black76(F, K, dte/365.0, RF, 0.070)
    p1 = black76(F, K, max(rem,1e-6)/365.0, RF, 0.070)
    print(f"   {nom:>12} {dte:8.2f} {rem:11.2f} "
          f"{p0*MULT:10,.0f}$ {p1*MULT:12,.0f}$ {p1/p0*100:8.1f}%")

print("\n   Lectura: el 13-nov conserva apenas un tercio de la prima por puro")
print("   theta. A partir del 20-nov se retiene mas del 70%, de modo que el")
print("   P&L del corte mide la direccion del tipo de cambio y no la agonia")
print("   del valor temporal.")

print()
print("=" * 78)
print("B. CANDIDATO ELEGIDO: CALL 6CZ6, VENCIMIENTO 20-NOV (15.32 DTE)")
print("=" * 78)
T = 15.32/365.0
print(f"   {'Strike':>8} {'esc.':>9} {'prima':>9} {'USD/contr':>11} "
      f"{'delta':>8} {'vega':>8} {'theta/dia':>10} {'equilibrio':>11}")
for K in (0.712, 0.714, 0.715, 0.717, 0.720):
    for nom, iv in ESCENARIOS:
        p = black76(F, K, T, RF, iv)
        de, ga, ve, th = griegas(F, K, T, RF, iv)
        be = K + p
        print(f"   {K:8.3f} {nom:>9} {p:9.5f} {p*MULT:10,.0f}$ "
              f"{de:8.3f} {ve*MULT:7,.0f}$ {th*MULT:9,.0f}$ {be:11.4f}")
    print()
