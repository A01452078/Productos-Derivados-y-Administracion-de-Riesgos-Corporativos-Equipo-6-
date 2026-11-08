# -*- coding: utf-8 -*-
"""
Analisis conjunto de la cartera al 12-nov-2026.
Pata 1: call 6CZ6 20-nov K=0.715, 10 contratos, comprada en 0.0026.
Pata 2: put  ZNZ6 20-nov K=107.25, 10 contratos, al offer de 0.546875.

El objetivo no es sumar dos P&L sino medir si las patas se compensan.
"""
from math import log, sqrt, exp, erf, pi

RF, T0, T1 = 0.0394, 15.32/365.0, 8.32/365.0
N = lambda x: 0.5*(1.0+erf(x/sqrt(2.0)))

def b76(F,K,T,r,s,tipo):
    if s<=0 or T<=0: return exp(-r*T)*(max(F-K,0.0) if tipo=="c" else max(K-F,0.0))
    d1=(log(F/K)+0.5*s*s*T)/(s*sqrt(T)); d2=d1-s*sqrt(T)
    if tipo=="c": return exp(-r*T)*(F*N(d1)-K*N(d2))
    return exp(-r*T)*(K*N(-d2)-F*N(-d1))

# ---- pata CAD ----
FC, KC, SC, NC, PC, MC = 0.7145, 0.715, 0.0453, 10, 0.0026, 100_000.0
# ---- pata ZN ----
FZ, KZ, SZ, NZ, PZ, MZ = 107.3172, 107.25, 0.0663, 10, 0.546875, 1_000.0

costo_c, costo_z = PC*MC*NC, PZ*MZ*NZ
total = costo_c + costo_z
print("="*78)
print("A. LA CARTERA")
print("="*78)
print(f"   Call 6CZ6  0.715 x{NC:2d} @ {PC:<9}  {costo_c:>9,.0f} USD")
print(f"   Put  ZNZ6 107.25 x{NZ:2d} @ {PZ:<9}  {costo_z:>9,.0f} USD")
print(f"   {'':48}{'-'*12}")
print(f"   Prima total comprometida{'':24}{total:>9,.0f} USD")
print(f"   Sobre capital de 90,162.50{'':22}{total/90162.50*100:>8.2f} %")
print(f"   Perdida maxima posible{'':26}{-total:>9,.0f} USD")

print()
print("="*78)
print("B. MATRIZ CONJUNTA DE P&L AL 12-NOV")
print("="*78)
print("   Filas: movimiento del dolar canadiense.")
print("   Columnas: movimiento del precio del bono (1 punto ~ 13 pb de")
print("   rendimiento; aproximacion con duracion modificada de 7.5 anos,")
print("   la cifra exacta exige identificar el bono entregable mas barato).\n")

movz = [-1.5,-0.75,0.0,0.75,1.5]      # puntos de precio del futuro ZN
movc = [-0.015,-0.0075,0.0,0.0075,0.015]

print(f"   {'':>10}", end="")
for mz in movz:
    print(f"{('bono '+f'{mz:+.2f}'):>13}", end="")
print()
print(f"   {'':>10}", end="")
for mz in movz:
    print(f"{('~'+f'{-mz*13:+.0f}'+' pb'):>13}", end="")
print("\n")

mejor, peor = None, None
for mc in movc:
    F1 = FC*(1+mc)
    vc = b76(F1,KC,T1,RF,SC,"c")*MC*NC
    print(f"   CAD {mc*100:+5.2f}%", end="")
    for mz in movz:
        F2 = FZ + mz
        vz = b76(F2,KZ,T1,RF,SZ,"p")*MZ*NZ
        pnl = vc + vz - total
        if mejor is None or pnl > mejor[0]: mejor = (pnl, mc, mz)
        if peor  is None or pnl < peor[0]:  peor  = (pnl, mc, mz)
        print(f"{pnl:>+12,.0f}$", end="")
    print()

print(f"\n   Mejor celda: {mejor[0]:+,.0f} USD  (CAD {mejor[1]*100:+.2f}%, bono {mejor[2]:+.2f})")
print(f"   Peor  celda: {peor[0]:+,.0f} USD  (CAD {peor[1]*100:+.2f}%, bono {peor[2]:+.2f})")

print()
print("="*78)
print("C. LA PATA DE BONOS COMO DIVERSIFICADOR")
print("="*78)
print("   Las esquinas de la matriz identifican los cuatro regimenes:\n")
reg = [
 ("Fed restrictiva: tasas suben, dolar se fortalece", +1, -1),
 ("Reflacion: tasas suben, dolar se debilita",        +1, +1),
 ("Fed acomodaticia: tasas bajan, dolar se debilita", -1, +1),
 ("Aversion al riesgo: tasas bajan, dolar se fortalece", -1, -1),
]
for nom, sz, sc in reg:
    F1 = FC*(1 + sc*0.015); F2 = FZ - sz*1.5
    vc = b76(F1,KC,T1,RF,SC,"c")*MC*NC
    vz = b76(F2,KZ,T1,RF,SZ,"p")*MZ*NZ
    print(f"   {nom:<52}")
    print(f"      CAD {vc-costo_c:>+9,.0f}$   ZN {vz-costo_z:>+9,.0f}$   "
          f"total {vc+vz-total:>+9,.0f}$")
print("\n   Solo el cuarto regimen castiga a las dos patas a la vez, y es el")
print("   menos probable de los cuatro: exige que el dolar se fortalezca")
print("   mientras los rendimientos caen, combinacion propia de una fuga")
print("   hacia la calidad. En los dos regimenes centrales una pata")
print("   financia a la otra.")
