# -*- coding: utf-8 -*-
"""
Cadena de opciones sobre el futuro de la nota del Tesoro a 10 anos (ZNZ6),
vencimiento 20-nov-2026 (15.31 DTE), leida el 5-nov-2026 a las 16:33 CST.

Convencion de cotizacion: el futuro se cotiza en puntos y 32avos; las opciones
en 64avos de punto. Un punto equivale a 1,000 USD sobre 100,000 de valor
nominal, de modo que 1/64 de punto son 15.625 USD.

El encabezado muestra LAST PRICE 107.1, que NO es 107.10 decimal sino 107-10,
es decir 107 + 10/32 = 107.3125. Se verifica mas abajo con paridad put-call.
"""
from math import log, sqrt, exp, erf, pi

RF   = 0.0394
T    = 15.31/365.0
PUNTO = 1000.0            # USD por punto de un contrato ZN
T64  = 1.0/64.0

N = lambda x: 0.5*(1.0+erf(x/sqrt(2.0)))
n = lambda x: exp(-0.5*x*x)/sqrt(2.0*pi)

def b76(F,K,T,r,s,tipo):
    if s<=0 or T<=0: return exp(-r*T)*(max(F-K,0.0) if tipo=="c" else max(K-F,0.0))
    d1=(log(F/K)+0.5*s*s*T)/(s*sqrt(T)); d2=d1-s*sqrt(T)
    if tipo=="c": return exp(-r*T)*(F*N(d1)-K*N(d2))
    return exp(-r*T)*(K*N(-d2)-F*N(-d1))

def grg(F,K,T,r,s,tipo):
    d1=(log(F/K)+0.5*s*s*T)/(s*sqrt(T))
    de = exp(-r*T)*(N(d1) if tipo=="c" else N(d1)-1.0)
    ga = exp(-r*T)*n(d1)/(F*s*sqrt(T))
    ve = exp(-r*T)*F*n(d1)*sqrt(T)/100.0
    th = (-exp(-r*T)*F*n(d1)*s/(2*sqrt(T)))/365.0
    return de,ga,ve,th

def iv(p,F,K,T,r,tipo):
    lo,hi=1e-6,5.0
    if p<=b76(F,K,T,r,lo,tipo) or p>=b76(F,K,T,r,hi,tipo): return None
    for _ in range(200):
        m=0.5*(lo+hi)
        if b76(F,K,T,r,m,tipo)<p: lo=m
        else: hi=m
    return 0.5*(lo+hi)

# (strike, call_bid, call_offer, put_bid, put_offer)
ZN = [
 (103.75, 3.5625,   3.59375,  0.015625, 0.015625),
 (104.25, 3.0625,   3.109375, 0.015625, 0.03125),
 (104.75, 2.578125, 2.609375, 0.015625, 0.046875),
 (105.25, 2.09375,  2.140625, 0.046875, 0.0625),
 (105.75, 1.640625, 1.671875, 0.078125, 0.109375),
 (106.25, 1.21875,  1.25,     0.15625,  0.1875),
 (106.75, 0.859375, 0.890625, 0.296875, 0.328125),
 (107.25, 0.578125, 0.609375, 0.515625, 0.546875),
 (108.25, 0.234375, 0.265625, 1.15625,  1.1875),
 (108.75, 0.140625, 0.171875, 1.5625,   1.609375),
 (109.25, 0.09375,  0.109375, 2.015625, 2.046875),
 (109.50, 0.078125, 0.09375,  2.234375, 2.28125),
 (110.25, 0.03125,  0.0625,   2.953125, 3.0),
 (110.50, 0.03125,  0.046875, 3.203125, 3.234375),
]
# Se excluyen 104.5, 105.5, 106.5, 107.5, 107.75, 108.5 y 109.75: una de las
# dos puntas esta rancia (spreads de 20 a 40 veces el ancho normal).

print("="*78)
print("A. RECUPERACION DEL PRECIO DEL FUTURO VIA PARIDAD PUT-CALL")
print("="*78)
print("   F = K + (C - P) e^(rT).  Cada strike da una estimacion independiente.\n")
print(f"   {'K':>8} {'C medio':>9} {'P medio':>9} {'F implicito':>12}")
Fs=[]
for k,cb,co,pb,po in ZN:
    cm,pm=0.5*(cb+co),0.5*(pb+po)
    f=k+(cm-pm)*exp(RF*T); Fs.append(f)
    print(f"   {k:8.2f} {cm:9.5f} {pm:9.5f} {f:12.4f}")
F=sum(Fs)/len(Fs)
disp=max(Fs)-min(Fs)
print(f"\n   Futuro implicito promedio: {F:.4f}")
print(f"   Dispersion entre strikes:  {disp:.4f} puntos ({disp*32:.2f}/32)")
print(f"   Lectura del encabezado:    107-10 = {107+10/32:.4f}  <- coincide")

print()
print("="*78)
print("B. VOLATILIDAD IMPLICITA Y GRIEGAS DEL LADO PUT")
print("="*78)
print(f"   {'K':>8} {'offer':>9} {'USD':>9} {'IV':>8} {'delta':>8} "
      f"{'vega':>8} {'theta':>8} {'spread':>8}")
cand={}
for k,cb,co,pb,po in ZN:
    s=iv(po,F,k,T,RF,"p")
    if s is None: continue
    de,ga,ve,th=grg(F,k,T,RF,s,"p")
    cand[k]=(po,s,de,ve,th)
    print(f"   {k:8.2f} {po:9.6f} {po*PUNTO:8,.0f}$ {s*100:7.2f}% {de:8.3f} "
          f"{ve*PUNTO:7,.0f}$ {th*PUNTO:7,.0f}$ {(po-pb)*PUNTO:7,.0f}$")

atm=min(cand, key=lambda k: abs(k-F))
print(f"\n   Strike mas cercano al futuro: {atm:.2f}  (IV {cand[atm][1]*100:.2f}%)")
