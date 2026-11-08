# -*- coding: utf-8 -*-
"""
Escenarios de P&L al 12-nov-2026 para la call 6CZ6 20-nov strike 0.715,
comprada hoy al offer de 0.0026.

La valuacion del corte NO es intrinseca: el 12-nov la opcion conserva
8.32 dias de vida, de modo que se revalua con Black-76 al plazo remanente
manteniendo la volatilidad implicita observada hoy.
"""
from math import log, sqrt, exp, erf, pi

F0, RF, MULT = 0.7145, 0.0394, 100_000.0
K, IV = 0.715, 0.0453
T_HOY, T_CORTE = 15.32/365.0, 8.32/365.0
ENTRADA, NCONT = 0.0026, 10

N = lambda x: 0.5*(1.0+erf(x/sqrt(2.0)))
n = lambda x: exp(-0.5*x*x)/sqrt(2.0*pi)

def c76(F,K,T,r,s):
    if s<=0 or T<=0: return exp(-r*T)*max(F-K,0.0)
    d1=(log(F/K)+0.5*s*s*T)/(s*sqrt(T)); d2=d1-s*sqrt(T)
    return exp(-r*T)*(F*N(d1)-K*N(d2))

def grg(F,K,T,r,s):
    d1=(log(F/K)+0.5*s*s*T)/(s*sqrt(T))
    return (exp(-r*T)*N(d1), exp(-r*T)*n(d1)/(F*s*sqrt(T)),
            exp(-r*T)*F*n(d1)*sqrt(T)/100.0,
            (-exp(-r*T)*F*n(d1)*s/(2*sqrt(T)))/365.0)

de,ga,ve,th = grg(F0,K,T_HOY,RF,IV)
costo = ENTRADA*MULT*NCONT
print("="*78)
print("A. LA POSICION")
print("="*78)
print(f"   Call 6CZ6 20-nov, strike {K}, {NCONT} contratos al offer de {ENTRADA}")
print(f"   Prima por contrato        {ENTRADA*MULT:>12,.0f} USD")
print(f"   Desembolso total          {costo:>12,.0f} USD   ({costo/90162.50*100:.2f}% de la cuenta)")
print(f"   Nocional                  {NCONT*MULT:>12,.0f} CAD")
print(f"   Delta de la posicion      {de*NCONT*MULT:>12,.0f} CAD equivalentes")
print(f"   Vega  (por punto de vol)  {ve*MULT*NCONT:>12,.0f} USD")
print(f"   Theta (por dia)           {th*MULT*NCONT:>12,.0f} USD")
print(f"   Punto de equilibrio       {K+ENTRADA:>12.4f}   (USD/CAD {1/(K+ENTRADA):.4f})")
print(f"   Perdida maxima            {-costo:>12,.0f} USD   (la prima, y nada mas)")

print()
print("="*78)
print("B. VALOR DE LA POSICION EL 12-NOV (quedan 8.32 dias de vida)")
print("="*78)
print(f"   {'mov. CAD':>10} {'futuro':>9} {'USD/CAD':>9} {'prima':>9} "
      f"{'valor pos.':>12} {'P&L':>11} {'retorno':>9}")
for mv in (-0.020,-0.015,-0.010,-0.005,0.0,0.005,0.010,0.015,0.020):
    F1 = F0*(1+mv)
    p1 = c76(F1,K,T_CORTE,RF,IV)
    val = p1*MULT*NCONT
    print(f"   {mv*100:+9.1f}% {F1:9.4f} {1/F1:9.4f} {p1:9.5f} "
          f"{val:11,.0f}$ {val-costo:+10,.0f}$ {(val-costo)/costo*100:+8.1f}%")

print()
print("="*78)
print("C. SENSIBILIDAD A LA VOLATILIDAD (futuro sin cambio, 12-nov)")
print("="*78)
print("   La vega es el otro motor del P&L. Si la volatilidad implicita se")
print("   mueve, la posicion gana o pierde sin que el tipo de cambio cambie.\n")
print(f"   {'IV':>8} {'prima':>9} {'valor pos.':>12} {'P&L':>11}")
for s in (0.030,0.0353,0.0453,0.0553,0.065):
    p1 = c76(F0,K,T_CORTE,RF,s); val = p1*MULT*NCONT
    mk = "  <- observada hoy" if abs(s-IV)<1e-9 else ""
    print(f"   {s*100:7.2f}% {p1:9.5f} {val:11,.0f}$ {val-costo:+10,.0f}${mk}")

print()
print("="*78)
print("D. PROBABILIDAD DE EJERCICIO (medida neutral al riesgo, al 20-nov)")
print("="*78)
d2 = (log(F0/K)-0.5*IV*IV*T_HOY)/(IV*sqrt(T_HOY))
print(f"   N(d2) = probabilidad de terminar dentro del dinero: {N(d2)*100:.1f}%")
d2b = (log(F0/(K+ENTRADA))-0.5*IV*IV*T_HOY)/(IV*sqrt(T_HOY))
print(f"   Probabilidad de rebasar el punto de equilibrio:     {N(d2b)*100:.1f}%")
print("\n   Advertencia metodologica: son probabilidades bajo la medida neutral")
print("   al riesgo, implicitas en los precios. No son pronosticos del mundo real.")
