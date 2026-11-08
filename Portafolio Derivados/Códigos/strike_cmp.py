# -*- coding: utf-8 -*-
"""Comparacion de ejecucion: put ZNZ6 20-nov en 107.25 contra 107.5."""
from math import log, sqrt, exp, erf, pi
F, RF, T, M, NC = 107.3172, 0.0394, 15.31/365.0, 1000.0, 10
N=lambda x:0.5*(1.0+erf(x/sqrt(2.0))); n=lambda x:exp(-0.5*x*x)/sqrt(2.0*pi)
def p76(F,K,T,r,s):
    if s<=0: return exp(-r*T)*max(K-F,0.0)
    d1=(log(F/K)+0.5*s*s*T)/(s*sqrt(T)); d2=d1-s*sqrt(T)
    return exp(-r*T)*(K*N(-d2)-F*N(-d1))
def grg(F,K,T,r,s):
    d1=(log(F/K)+0.5*s*s*T)/(s*sqrt(T))
    return exp(-r*T)*(N(d1)-1.0), exp(-r*T)*F*n(d1)*sqrt(T)/100.0
def iv(p,F,K,T,r):
    lo,hi=1e-6,5.0
    for _ in range(200):
        m=0.5*(lo+hi)
        if p76(F,K,T,r,m)<p: lo=m
        else: hi=m
    return 0.5*(lo+hi)

print("="*76)
print("CALIDAD DE EJECUCION: DOS STRIKES SEPARADOS POR UN CUARTO DE PUNTO")
print("="*76)
print(f"   {'':16}{'K = 107.25':>16}{'K = 107.50':>16}{'diferencia':>16}")
fil=[]
for nom,(K,b,o) in [("a",(107.25,0.515625,0.546875)),("b",(107.5,0.50,0.671875))]:
    s_o, s_b = iv(o,F,K,T,RF), iv(b,F,K,T,RF)
    de,ve = grg(F,K,T,RF,s_o)
    fil.append(dict(K=K,b=b,o=o,so=s_o,sb=s_b,de=de,ve=ve))
a,b_=fil
def lin(et,fa,fb,fmt,dif=None):
    va,vb = fa,fb
    d = "" if dif is None else format(dif,fmt.strip('%>0123456789.,$f') or 's')
    print(f"   {et:16}{format(va,fmt):>16}{format(vb,fmt):>16}{d:>16}")

print(f"   {'offer':16}{a['o']:>16.6f}{b_['o']:>16.6f}{b_['o']-a['o']:>+16.6f}")
print(f"   {'costo x10':16}{a['o']*M*NC:>15,.0f}${b_['o']*M*NC:>15,.0f}$"
      f"{(b_['o']-a['o'])*M*NC:>+15,.0f}$")
print(f"   {'bid':16}{a['b']:>16.6f}{b_['b']:>16.6f}")
print(f"   {'spread x10':16}{(a['o']-a['b'])*M*NC:>15,.0f}${(b_['o']-b_['b'])*M*NC:>15,.0f}$"
      f"{((b_['o']-b_['b'])-(a['o']-a['b']))*M*NC:>+15,.0f}$")
print(f"   {'spread / costo':16}{(a['o']-a['b'])/a['o']*100:>15.1f}%"
      f"{(b_['o']-b_['b'])/b_['o']*100:>15.1f}%")
print(f"   {'IV en el offer':16}{a['so']*100:>15.2f}%{b_['so']*100:>15.2f}%"
      f"{(b_['so']-a['so'])*100:>+15.2f}%")
print(f"   {'IV en el bid':16}{a['sb']*100:>15.2f}%{b_['sb']*100:>15.2f}%")
print(f"   {'delta':16}{a['de']:>16.3f}{b_['de']:>16.3f}")
print(f"   {'delta x10':16}{a['de']*NC:>16.2f}{b_['de']*NC:>16.2f}")

print()
print("="*76)
print("EL COSTO DE LA EQUIVOCACION")
print("="*76)
# cuanto valdria el 107.5 si cotizara a la IV del 107.25
just = p76(F,107.5,T,RF,a['so'])
print(f"   Valor teorico del put 107.5 a la volatilidad del 107.25 ({a['so']*100:.2f}%):")
print(f"      {just:.6f} puntos = {just*M:,.0f} USD por contrato")
print(f"   Offer que estas a punto de pagar:")
print(f"      {b_['o']:.6f} puntos = {b_['o']*M:,.0f} USD por contrato")
print(f"   Sobreprecio por contrato: {(b_['o']-just)*M:,.0f} USD")
print(f"   Sobreprecio en 10 contratos: {(b_['o']-just)*M*NC:,.0f} USD")
print()
print(f"   Delta adicional que compras: {(b_['de']-a['de'])*NC:+.2f} contratos de futuro")
print(f"   Dinero adicional que pagas:  {(b_['o']-a['o'])*M*NC:+,.0f} USD")
print(f"   Costo por unidad de delta:   "
      f"{(b_['o']-a['o'])*M*NC/abs((b_['de']-a['de'])*NC):,.0f} USD")
print()
print("   En 107.25 el delta cuesta "
      f"{a['o']*M*NC/abs(a['de']*NC):,.0f} USD por unidad.")
print("   El cuarto de punto adicional se cobra a "
      f"{(b_['o']-a['o'])*M*NC/abs((b_['de']-a['de'])*NC):,.0f} USD por unidad, "
      f"{(b_['o']-a['o'])*M*NC/abs((b_['de']-a['de'])*NC)/(a['o']*M*NC/abs(a['de']*NC)):.1f} veces mas caro.")
