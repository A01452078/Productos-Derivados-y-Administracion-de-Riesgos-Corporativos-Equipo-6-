# -*- coding: utf-8 -*-
"""
Comparacion de los dos bull call spreads del equipo.
Eduardo lo armo sobre oro (COMEX), Ulises sobre crudo (NYMEX).
Misma estructura, calibraciones muy distintas.
"""
E = dict(nom="Eduardo - ORO (OG nov-26)", F=4207.9, K1=4200.0, p1=100.50,
         K2=4400.0, p2=31.00, mult=100.0, n=1, uni="onza")
U = dict(nom="Ulises - CRUDO (CL oct-26)", F=88.75, K1=88.75, p1=2.76,
         K2=90.75, p2=1.76, mult=1000.0, n=5, uni="barril")

print("="*84)
print("BULL CALL SPREAD: LA MISMA ESTRUCTURA, DOS CALIBRACIONES")
print("="*84)
fil = []
for d in (E, U):
    deb   = d["p1"] - d["p2"]
    ancho = d["K2"] - d["K1"]
    cost  = deb * d["mult"] * d["n"]
    gmax  = (ancho - deb) * d["mult"] * d["n"]
    be    = d["K1"] + deb
    d.update(deb=deb, ancho=ancho, cost=cost, gmax=gmax, be=be,
             rr=gmax/cost, mov=(be/d["F"]-1)*100,
             cap=deb/ancho*100)
    fil.append(d)

et = ["Subyacente al armar", "Strike comprado", "Prima pagada",
      "Strike vendido", "Prima cobrada", f"Debito neto por unidad",
      "Contratos", "Desembolso", "Ancho del diferencial",
      "Ganancia maxima", "Perdida maxima", "Beneficio / riesgo",
      "Punto de equilibrio", "Movimiento necesario",
      "Debito / ancho"]
val = []
for d in fil:
    val.append([f"{d['F']:,.2f}", f"{d['K1']:,.2f}", f"{d['p1']:,.2f}",
      f"{d['K2']:,.2f}", f"{d['p2']:,.2f}", f"{d['deb']:,.2f}",
      f"{d['n']}", f"{d['cost']:,.0f}$", f"{d['ancho']:,.2f}",
      f"{d['gmax']:,.0f}$", f"{-d['cost']:,.0f}$", f"{d['rr']:.2f} a 1",
      f"{d['be']:,.2f}", f"{d['mov']:+.2f}%", f"{d['cap']:.0f}%"])

print(f"   {'':<24}{fil[0]['nom']:>27}{fil[1]['nom']:>29}")
print(f"   {'-'*78}")
for i, e in enumerate(et):
    print(f"   {e:<24}{val[0][i]:>27}{val[1][i]:>29}")

print()
print("="*84)
print("LECTURA")
print("="*84)
print("   El diferencial de oro paga 1.88 dolares por cada dolar arriesgado;")
print("   el de crudo paga 1.00. La diferencia no viene de la habilidad sino")
print("   de DONDE se colocaron los strikes respecto al subyacente.")
print()
print("   Eduardo pago 35% del ancho del diferencial y necesitaba que el oro")
print("   subiera 1.46%. Ulises pago 50% del ancho y necesitaba 1.13% en el")
print("   crudo. Es el intercambio clasico: cuanto mas estrecho se arma el")
print("   diferencial respecto al precio corriente, mas probable es acertar")
print("   y menos paga cuando se acierta.")
print()
print("   Un bull spread cuyo debito es la mitad del ancho es, en esencia,")
print("   una apuesta a cara o cruz con premio de uno a uno. Uno cuyo debito")
print("   es un tercio del ancho exige mas puntería pero compensa el doble.")
