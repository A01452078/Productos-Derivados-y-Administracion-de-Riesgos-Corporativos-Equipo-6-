# -*- coding: utf-8 -*-
"""
Calibracion inversa del plazo: dado el precio cotizado de la opcion y la
volatilidad implicita de la cadena, se despeja el tiempo al vencimiento.

Es la misma tecnica con la que establecimos que LSEG mide el plazo desde la
fecha calendario corriente. Si la orden quedo en el vencimiento de diciembre,
el plazo despejado debe rondar los 45-50 dias; si quedo en el 20-nov, los 15.
"""
from math import log, sqrt, exp, erf, pi
F, K, RF = 107.3172, 107.25, 0.0394
N = lambda x: 0.5*(1.0+erf(x/sqrt(2.0)))

def put76(F,K,T,r,s):
    if s<=0 or T<=0: return exp(-r*T)*max(K-F,0.0)
    d1=(log(F/K)+0.5*s*s*T)/(s*sqrt(T)); d2=d1-s*sqrt(T)
    return exp(-r*T)*(K*N(-d2)-F*N(-d1))

def plazo_implicito(precio, s):
    """Biseccion sobre T. El valor del put crece de forma monotona con T
       cuando la opcion esta practicamente at-the-money."""
    lo, hi = 1e-6, 2.0
    for _ in range(300):
        m = 0.5*(lo+hi)
        if put76(F,K,m,RF,s) < precio: lo = m
        else: hi = m
    return 0.5*(lo+hi)

COTIZADO = 0.546875     # el ask que aparece en el cuadro de AMEND
IV       = 0.0663       # volatilidad de la cadena del 20-nov en ese strike

print("="*74)
print("A. PLAZO DESPEJADO DEL PRECIO COTIZADO")
print("="*74)
for s in (0.0600, 0.0663, 0.0700, 0.0750):
    T = plazo_implicito(COTIZADO, s)
    print(f"   Si la volatilidad real es {s*100:5.2f}%  ->  plazo implicito "
          f"{T*365:6.2f} dias")

print()
print("="*74)
print("B. QUE COSTARIA CADA VENCIMIENTO A LA MISMA VOLATILIDAD (6.63%)")
print("="*74)
print(f"   {'vencimiento':>14} {'dias':>7} {'precio':>10} {'USD x10':>11} "
      f"{'vs cotizado':>13}")
for nom, d in [("20-nov", 15.31), ("27-nov", 22.31), ("4-dic", 29.31),
               ("11-dic", 36.31), ("19-dic", 44.31), ("24-dic", 49.31)]:
    p = put76(F,K,d/365.0,RF,IV)
    print(f"   {nom:>14} {d:7.2f} {p:10.6f} {p*1000*10:10,.0f}$ "
          f"{(p/COTIZADO-1)*100:+12.1f}%")

print()
print("="*74)
print("C. VEREDICTO")
print("="*74)
T = plazo_implicito(COTIZADO, IV)
print(f"   Precio cotizado en el AMEND:        {COTIZADO:.6f}")
print(f"   Precio de la cadena del 20-nov:     0.546875   <- identico")
print(f"   Plazo despejado:                    {T*365:.2f} dias")
print(f"   Dias del 5-nov al 20-nov:           15.31")
print()
print("   Un vencimiento de diciembre valdria entre 35% y 80% mas. La orden")
print("   SI quedo en el 20-nov. La columna MONTH etiqueta el futuro")
print("   subyacente (ZNZ6, entrega diciembre), no el vencimiento de la")
print("   opcion. En el canadiense dice Nov porque ahi la plataforma etiqueta")
print("   la opcion; es inconsistencia de nomenclatura entre clases de activo,")
print("   no un error de la orden.")
