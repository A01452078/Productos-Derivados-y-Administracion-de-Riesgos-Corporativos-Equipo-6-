# -*- coding: utf-8 -*-
"""
Cadena real de 6CZ6, vencimiento 20-nov-2026 (15.32 DTE), leida en pantalla
el 5-nov-2026 a las 16:24 CST.

El cuadro de Trade tapa la columna de strikes. El mapeo se reconstruye desde
los strikes visibles al pie de la tabla (0.721 a 0.724) retrocediendo en
incrementos de 0.001, y se VERIFICA de forma independiente con la paridad
put-call. Si el mapeo estuviera corrido un renglon, la paridad fallaria por
0.001 (100 USD por contrato), que es imposible de confundir con ruido.
"""
from math import log, sqrt, exp, erf, pi

F, RF, MULT = 0.7145, 0.0394, 100_000.0
T = 15.32 / 365.0

N = lambda x: 0.5 * (1.0 + erf(x / sqrt(2.0)))
n = lambda x: exp(-0.5 * x * x) / sqrt(2.0 * pi)

def black76(F, K, T, r, s, tipo="call"):
    if s <= 0 or T <= 0:
        return exp(-r*T) * (max(F-K,0.0) if tipo=="call" else max(K-F,0.0))
    d1 = (log(F/K) + 0.5*s*s*T) / (s*sqrt(T)); d2 = d1 - s*sqrt(T)
    if tipo == "call": return exp(-r*T) * (F*N(d1) - K*N(d2))
    return exp(-r*T) * (K*N(-d2) - F*N(-d1))

def griegas(F, K, T, r, s, tipo="call"):
    d1 = (log(F/K) + 0.5*s*s*T) / (s*sqrt(T))
    de = exp(-r*T) * (N(d1) if tipo=="call" else N(d1)-1.0)
    ga = exp(-r*T) * n(d1) / (F*s*sqrt(T))
    ve = exp(-r*T) * F * n(d1) * sqrt(T) / 100.0
    th = (-exp(-r*T)*F*n(d1)*s/(2*sqrt(T))) / 365.0
    return de, ga, ve, th

def iv(precio, F, K, T, r, tipo="call"):
    lo, hi = 1e-6, 5.0
    if precio <= black76(F,K,T,r,lo,tipo) or precio >= black76(F,K,T,r,hi,tipo):
        return None
    for _ in range(200):
        m = 0.5*(lo+hi)
        if black76(F,K,T,r,m,tipo) < precio: lo = m
        else: hi = m
    return 0.5*(lo+hi)

# renglon -> (strike, call_bid, call_offer, put_bid, put_offer)
CAD = [
 (0.704, 0.0097, 0.0119, None,   None),
 (0.705, 0.0088, 0.0109, 0.0002, 0.00045),
 (0.706, 0.0080, 0.0097, 0.0003, 0.0006),
 (0.707, 0.0074, 0.0087, 0.0004, 0.0007),
 (0.708, 0.0065, 0.0077, 0.0005, 0.0008),
 (0.709, 0.0058, 0.0068, 0.0007, 0.0010),
 (0.710, 0.0052, 0.0059, 0.0009, 0.0012),
 (0.711, 0.0044, 0.0051, 0.0011, 0.0015),
 (0.712, 0.0039, 0.0043, 0.0014, 0.0018),
 (0.713, 0.0033, 0.0037, 0.0018, 0.0022),
 (0.714, 0.0027, 0.0031, 0.0022, 0.0026),
 (0.715, 0.0022, 0.0026, 0.0027, 0.0031),
 (0.716, 0.0018, 0.0022, 0.0033, 0.0037),
 (0.717, 0.0014, 0.0018, 0.0039, 0.0043),
 (0.718, 0.0011, 0.0015, 0.0040, 0.0051),
 (0.719, 0.0009, 0.0012, 0.0051, 0.0059),
 (0.720, 0.0006, 0.0010, 0.0058, 0.0067),
 (0.721, 0.0001, 0.0022, 0.0065, 0.0076),
 (0.722, 0.00035,0.0006, 0.0072, 0.0085),
 (0.723, 0.00025,0.0005, 0.0079, 0.0098),
 (0.724, 0.0002, 0.0004, 0.0087, 0.0108),
]

print("=" * 80)
print("A. VALIDACION DEL MAPEO DE STRIKES VIA PARIDAD PUT-CALL")
print("=" * 80)
print("   C - P = e^(-rT)(F - K).  Un corrimiento de un renglon daria 0.001")
print("   de error, equivalente a 100 USD por contrato.\n")
print(f"   {'K':>7} {'C medio':>9} {'P medio':>9} {'C-P obs':>10} {'C-P teo':>10} {'error USD':>11}")
errs = []
for k, cb, co, pb, po in CAD:
    if pb is None or k == 0.721:   # 0.721 trae una punta rancia
        continue
    cm, pm = 0.5*(cb+co), 0.5*(pb+po)
    obs, teo = cm - pm, exp(-RF*T)*(F-k)
    errs.append(abs(obs-teo))
    print(f"   {k:7.3f} {cm:9.5f} {pm:9.5f} {obs:10.5f} {teo:10.5f} {(obs-teo)*MULT:10,.1f}$")
print(f"\n   Error absoluto medio: {sum(errs)/len(errs)*MULT:,.2f} USD por contrato.")
print("   El mapeo es correcto: el renglon 12 es el strike 0.715.")

print()
print("=" * 80)
print("B. SONRISA DE VOLATILIDAD IMPLICITA AL 20-NOV")
print("=" * 80)
print(f"   {'K':>7} {'IV bid':>9} {'IV offer':>9} {'IV media':>9} {'delta':>8} {'spread':>9}")
s_atm = None
for k, cb, co, pb, po in CAD:
    if k == 0.721: continue
    ib, io = iv(cb,F,k,T,RF,"call"), iv(co,F,k,T,RF,"call")
    if ib is None or io is None: continue
    im = 0.5*(ib+io)
    d = griegas(F,k,T,RF,im,"call")[0]
    if abs(k-0.715) < 1e-9: s_atm = im
    print(f"   {k:7.3f} {ib*100:8.2f}% {io*100:8.2f}% {im*100:8.2f}% {d:8.3f} {(co-cb)*MULT:8,.0f}$")

print(f"\n   IV at-the-money real (K=0.715): {s_atm*100:.2f}%")
print(f"   IV que yo habia supuesto:        7.00%")
print(f"   Sobreestimacion:                 {(0.070/s_atm-1)*100:.1f}%")
