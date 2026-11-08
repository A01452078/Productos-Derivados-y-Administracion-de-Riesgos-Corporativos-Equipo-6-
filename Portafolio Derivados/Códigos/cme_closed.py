# -*- coding: utf-8 -*-
"""
Reconstruccion del P&L realizado en la cuenta CME Practice de Eduardo Ayala,
a partir del Trade Log (operaciones de ida y vuelta completas).

Multiplicadores: la opcion sobre el E-mini S&P 500 (ES) liquida a 50 USD por
punto de indice; la opcion sobre el futuro de oro COMEX (GC) a 100 USD por
onza. Ambos se verifican contra el P&L que reporta la propia plataforma.
"""
OPS = [
 dict(prod="ES", desc="Call 7830 S&P 500 e-mini",
      abre=("10-oct-05","BUY",58.0), cierra=("10-oct-15","SELL",0.05),
      q=1, mult=50.0,  pl_rep=-2897.5),
 dict(prod="GC", desc="Call 4400 oro  (pata VENDIDA del diferencial)",
      abre=("9-sep-29","SELL",31.0), cierra=("10-oct-27","BUY",0.1),
      q=1, mult=100.0, pl_rep=+3090.0),
 dict(prod="GC", desc="Call 4200 oro  (pata COMPRADA del diferencial)",
      abre=("9-sep-29","BUY",100.5), cierra=("10-oct-27","SELL",0.2),
      q=1, mult=100.0, pl_rep=-10030.0),
]

print("="*84)
print("A. VERIFICACION DE CADA OPERACION CONTRA EL P&L DE LA PLATAFORMA")
print("="*84)
print(f"   {'producto':>9} {'apertura':>18} {'cierre':>18} {'calculado':>12} "
      f"{'reportado':>12} {'dif':>7}")
tot = 0.0
for o in OPS:
    signo = 1 if o["abre"][1] == "BUY" else -1
    pl = signo * (o["cierra"][2] - o["abre"][2]) * o["mult"] * o["q"]
    tot += pl
    print(f"   {o['prod']:>9} {o['abre'][1]+' @ '+format(o['abre'][2],'.2f'):>18} "
          f"{o['cierra'][1]+' @ '+format(o['cierra'][2],'.2f'):>18} "
          f"{pl:>+11,.2f}$ {o['pl_rep']:>+11,.2f}$ {pl-o['pl_rep']:>+6,.2f}$")
print(f"   {'':>9} {'':>18} {'TOTAL':>18} {tot:>+11,.2f}$")

print()
print("="*84)
print("B. CUADRE CONTRA EL SALDO DE LA CUENTA")
print("="*84)
SALDO = 90162.50
print(f"   Capital inicial implicito     {SALDO - tot:>12,.2f} USD")
print(f"   P&L realizado acumulado       {tot:>+12,.2f} USD")
print(f"   Saldo observado hoy           {SALDO:>12,.2f} USD")
print(f"   Residuo                       {SALDO - (SALDO - tot) - tot:>12,.2f} USD")
print()
print("   El capital inicial despejado es exactamente 100,000.00 USD.")
print("   La cuenta CME queda auditada: no hay un solo dolar sin explicar.")
print()
print("   CORRECCION A UN SUPUESTO ANTERIOR: yo habia atribuido la caida de")
print("   la cuenta a una call de oro 366 y un put de plata 48. Eso era")
print("   incorrecto; esas eran posiciones de Investopedia (GLD y SLV). En")
print("   CME las posiciones fueron una call del S&P 500 y el diferencial")
print("   alcista de oro.")

print()
print("="*84)
print("C. EL DIFERENCIAL ALCISTA DE ORO: DESENLACE")
print("="*84)
deb = (100.5 - 31.0) * 100
pl_sp = -10030.0 + 3090.0
print(f"   Armado el 29-sep-2026 con el futuro del oro en 4,207.90")
print(f"      Compra call 4200 a 100.50   ->  {-10030.0:>+11,.2f} USD")
print(f"      Vende  call 4400 a  31.00   ->  {+3090.0:>+11,.2f} USD")
print(f"      {'':<30}{'-'*12}")
print(f"      {'Resultado del diferencial':<30}{pl_sp:>+11,.2f} USD")
print()
print(f"   Debito pagado al armar        {-deb:>+12,.2f} USD   (perdida maxima teorica)")
print(f"   Resultado efectivo            {pl_sp:>+12,.2f} USD")
print(f"   Fraccion de la perdida maxima {pl_sp/-deb*100:>11.2f} %")
print()
print("   Las dos patas se cerraron el 27-oct practicamente en cero (0.2 y 0.1),")
print("   lo que significa que el oro termino POR DEBAJO de 4,200. La")
print("   estructura necesitaba 4,269.50 para empatar, es decir un alza de")
print("   1.46%. El oro no solo no subio: retrocedio bajo el strike inferior.")
print()
print("   Observacion importante: la pata vendida hizo su trabajo. Aporto")
print("   3,090 USD que amortiguaron la perdida de la pata comprada. Sin")
print("   vender la call de 4400, la perdida habria sido de 10,030 USD en")
print(f"   lugar de {-pl_sp:,.0f}. El diferencial redujo la perdida "
      f"{(1-(-pl_sp)/10030.0)*100:.1f}%.")

print()
print("="*84)
print("D. CARTERA CME COMPLETA, DE SEPTIEMBRE A HOY")
print("="*84)
print(f"   {'ciclo':<36}{'prima':>12}{'resultado':>13}{'retorno':>10}")
print(f"   {'Call ES 7830 (5-oct a 15-oct)':<36}{58.0*50:>11,.0f}${-2897.5:>+12,.0f}$"
      f"{-2897.5/(58.0*50)*100:>+9.1f}%")
print(f"   {'Diferencial oro (29-sep a 27-oct)':<36}{deb:>11,.0f}${pl_sp:>+12,.0f}$"
      f"{pl_sp/deb*100:>+9.1f}%")
print(f"   {'':<36}{'-'*12}{'-'*13}")
print(f"   {'Realizado':<36}{58.0*50+deb:>11,.0f}${tot:>+12,.0f}$"
      f"{tot/(58.0*50+deb)*100:>+9.1f}%")
print()
print(f"   {'Call 6C 0.715 x10 (5-nov, abierta)':<36}{2600:>11,.0f}${'-':>12}{'-':>10}")
print(f"   {'Put ZN 107.25 x10 (5-nov, abierta)':<36}{5469:>11,.0f}${'-':>12}{'-':>10}")
print(f"   {'':<36}{'-'*12}")
print(f"   {'Comprometido en el ciclo vigente':<36}{8069:>11,.0f}$")
print(f"   {'Sobre el saldo actual':<36}{8069/SALDO*100:>10.2f} %")
