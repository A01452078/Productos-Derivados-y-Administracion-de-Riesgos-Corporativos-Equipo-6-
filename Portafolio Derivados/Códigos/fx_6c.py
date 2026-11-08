# -*- coding: utf-8 -*-
"""
Calibracion de la cadena de opciones sobre el futuro del dolar canadiense (6CZ6)
en CME, tomada el 5-nov-2026 a las 15:00 CST.

Modelo: Black (1976) sobre futuros. El subyacente es el futuro, no el spot,
de modo que el costo de acarreo ya esta dentro del precio F y no aparece
como tasa de dividendo o diferencial de tasas.
"""
from math import log, sqrt, exp, erf, pi

F   = 0.7145          # Ultimo precio del futuro 6CZ6
T   = 1.32 / 365.0    # Plazo al vencimiento del 6-nov (DTE que reporta CME)
RF  = 0.0394          # Tasa libre de riesgo a muy corto plazo
MULT = 100_000.0      # Tamano del contrato: C$100,000

N = lambda x: 0.5 * (1.0 + erf(x / sqrt(2.0)))
n = lambda x: exp(-0.5 * x * x) / sqrt(2.0 * pi)

def black76(F, K, T, r, s, tipo="call"):
    if s <= 0 or T <= 0:
        intr = max(F - K, 0.0) if tipo == "call" else max(K - F, 0.0)
        return exp(-r * T) * intr
    d1 = (log(F / K) + 0.5 * s * s * T) / (s * sqrt(T))
    d2 = d1 - s * sqrt(T)
    if tipo == "call":
        return exp(-r * T) * (F * N(d1) - K * N(d2))
    return exp(-r * T) * (K * N(-d2) - F * N(-d1))

def vega(F, K, T, r, s):
    d1 = (log(F / K) + 0.5 * s * s * T) / (s * sqrt(T))
    return exp(-r * T) * F * n(d1) * sqrt(T)

def delta(F, K, T, r, s, tipo="call"):
    d1 = (log(F / K) + 0.5 * s * s * T) / (s * sqrt(T))
    return exp(-r * T) * (N(d1) if tipo == "call" else N(d1) - 1.0)

def vol_implicita(precio, F, K, T, r, tipo="call"):
    """Bisección sobre sigma. Devuelve None si el precio esta fuera de
       las cotas de no arbitraje."""
    lo, hi = 1e-6, 5.0
    if precio <= black76(F, K, T, r, lo, tipo) or precio >= black76(F, K, T, r, hi, tipo):
        return None
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if black76(F, K, T, r, mid, tipo) < precio:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)

# Cadena del 6-nov tal como aparece en pantalla: (strike, bid_call, offer_call)
CALLS = [
    (0.704, 0.0102, 0.0109), (0.705, 0.0093, 0.0099), (0.706, 0.0082, 0.0089),
    (0.707, 0.0073, 0.0080), (0.708, 0.0063, 0.0069), (0.709, 0.0053, 0.0059),
    (0.710, 0.0043, 0.0050), (0.711, 0.0034, 0.0040), (0.712, 0.0026, 0.0031),
    (0.713, 0.0018, 0.0021), (0.714, 0.0011, 0.0015), (0.715, 0.0007, 0.0009),
    (0.716, 0.00035, 0.0006), (0.717, 0.0002, 0.00035),
]
PUTS = [
    (0.714, 0.0006, 0.0009), (0.715, 0.0012, 0.0014), (0.716, 0.0018, 0.0021),
    (0.718, 0.0032, 0.0040), (0.719, 0.0041, 0.0048), (0.720, 0.0052, 0.0058),
    (0.721, 0.0060, 0.0069), (0.722, 0.0070, 0.0079), (0.723, 0.0080, 0.0090),
    (0.724, 0.0090, 0.0100),
]

print("=" * 74)
print("A. VERIFICACION DE LA CADENA: PARIDAD PUT-CALL SOBRE FUTUROS")
print("=" * 74)
print("   C - P = e^(-rT) (F - K).  Si la cadena esta bien cotizada, se cumple.\n")
print(f"   {'K':>7} {'C medio':>9} {'P medio':>9} {'C-P':>10} {'teorico':>10} {'error':>9}")
pc = dict((k, 0.5 * (b + o)) for k, b, o in PUTS)
err_pc = []
for k, b, o in CALLS:
    if k not in pc:
        continue
    cm, pm = 0.5 * (b + o), pc[k]
    obs = cm - pm
    teo = exp(-RF * T) * (F - k)
    err_pc.append(abs(obs - teo))
    print(f"   {k:7.3f} {cm:9.5f} {pm:9.5f} {obs:10.5f} {teo:10.5f} {obs-teo:9.5f}")
print(f"\n   Error absoluto medio: {sum(err_pc)/len(err_pc):.6f} "
      f"({sum(err_pc)/len(err_pc)*MULT:,.2f} USD por contrato)")

print()
print("=" * 74)
print("B. SONRISA DE VOLATILIDAD IMPLICITA, VENCIMIENTO 6-NOV (1.32 dias)")
print("=" * 74)
print(f"   {'K':>7} {'moneyness':>10} {'IV bid':>9} {'IV offer':>9} {'IV media':>9} {'delta':>8}")
smile = []
for k, b, o in CALLS:
    ivb = vol_implicita(b, F, k, T, RF, "call")
    ivo = vol_implicita(o, F, k, T, RF, "call")
    if ivb is None or ivo is None:
        continue
    ivm = 0.5 * (ivb + ivo)
    d = delta(F, k, T, RF, ivm, "call")
    smile.append((k, ivm, d))
    print(f"   {k:7.3f} {k/F:10.4f} {ivb*100:8.2f}% {ivo*100:8.2f}% {ivm*100:8.2f}% {d:8.3f}")

atm = min(smile, key=lambda x: abs(x[0] - F))
IV_ATM = atm[1]
print(f"\n   Strike mas cercano al dinero: {atm[0]:.3f}")
print(f"   Volatilidad implicita at-the-money: {IV_ATM*100:.2f}%")
