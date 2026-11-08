# -*- coding: utf-8 -*-
"""
Reconstruccion del P&L realizado de Eduardo Ayala (A01192714) en el
simulador Investopedia, del 22-sep al 20-oct de 2026.

Los simbolos siguen la convencion OCC abreviada:
   TICKER + AA + DD + letra_de_mes + strike
La letra codifica mes Y tipo: A-L son calls de enero a diciembre,
M-X son puts de enero a diciembre. Asi J = call de octubre y
V = put de octubre.
"""
import sys, re, pandas as pd
from collections import defaultdict

MES = {}
for i,l in enumerate("ABCDEFGHIJKL"): MES[l] = (i+1, "call")
for i,l in enumerate("MNOPQRSTUVWX"): MES[l] = (i+1, "put")
NOM = ["","ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]

def decod(s):
    m = re.match(r"^([A-Z]+)(\d{2})(\d{2})([A-Z])([\d.]+)$", s)
    if not m: return None
    tk, aa, dd, L, k = m.groups()
    mes, tipo = MES[L]
    return dict(tk=tk, venc=f"{int(dd)}-{NOM[mes]}-20{aa}", tipo=tipo, k=float(k))

df = pd.read_html(sys.argv[1])[0]
df["Price"] = df["Price"].str.replace(r"[$,]", "", regex=True).astype(float)
df["Date"]  = pd.to_datetime(df["Date"])
df = df.sort_values("Date", kind="stable")

print("="*96)
print("A. OPERACIONES DECODIFICADAS")
print("="*96)
print(f"   {'fecha':>11} {'subyacente':>6} {'tipo':>5} {'strike':>8} {'vence':>12} "
      f"{'accion':>8} {'cant':>5} {'precio':>8} {'efectivo':>11}")
pos = defaultdict(list)
for _,r in df.iterrows():
    s, tt, q, p = r["Symbol"], r["Trade Type"], int(r["Quantity"]), r["Price"]
    abre = "Buy" in tt
    d = decod(s)
    mult = 100 if d else 1
    flujo = (-1 if abre else 1) * q * p * mult
    pos[s].append((r["Date"], abre, q, p, mult))
    if d:
        print(f"   {r['Date']:%d-%b-%y} {d['tk']:>6} {d['tipo']:>5} {d['k']:>8.1f} "
              f"{d['venc']:>12} {'COMPRA' if abre else 'VENDE':>8} {q:>5} {p:>8.2f} "
              f"{flujo:>+10,.0f}$")
    else:
        print(f"   {r['Date']:%d-%b-%y} {s:>6} {'accion':>5} {'':>8} {'':>12} "
              f"{'COMPRA' if abre else 'VENDE':>8} {q:>5} {p:>8.2f} {flujo:>+10,.0f}$")

print()
print("="*96)
print("B. RESULTADO POR POSICION CERRADA")
print("="*96)
print(f"   {'instrumento':>16} {'descripcion':>34} {'costo':>10} {'ingreso':>10} "
      f"{'P&L':>10} {'retorno':>9}")
tot_c = tot_i = 0.0
res = []
for s, ops in pos.items():
    c = sum(q*p*m for _,a,q,p,m in ops if a)
    i = sum(q*p*m for _,a,q,p,m in ops if not a)
    if c == 0 or i == 0: continue
    d = decod(s)
    desc = (f"{d['tk']} {d['tipo']} {d['k']:g} vence {d['venc']}" if d
            else f"{s} acciones al contado")
    tot_c += c; tot_i += i
    res.append((s, desc, c, i, i-c))
for s,desc,c,i,pl in sorted(res, key=lambda x:-x[4]):
    print(f"   {s:>16} {desc:>34} {c:>9,.0f}$ {i:>9,.0f}$ {pl:>+9,.0f}$ {pl/c*100:>+8.1f}%")
print(f"   {'':>16} {'':>34} {'-'*10} {'-'*10} {'-'*10}")
print(f"   {'TOTAL':>16} {'':>34} {tot_c:>9,.0f}$ {tot_i:>9,.0f}$ {tot_i-tot_c:>+9,.0f}$ "
      f"{(tot_i-tot_c)/tot_c*100:>+8.1f}%")

print()
print("="*96)
print("C. CONTRASTE CON EL SALDO DE LA CUENTA")
print("="*96)
VAL, CAP = 1003085.00, 1000000.00
print(f"   P&L reconstruido de las operaciones   {tot_i-tot_c:>+12,.2f} USD")
print(f"   Variacion observada de la cuenta      {VAL-CAP:>+12,.2f} USD")
print(f"   Diferencia                            {(VAL-CAP)-(tot_i-tot_c):>+12,.2f} USD")
print()
print(f"   Capital desplegado en total           {tot_c:>12,.2f} USD")
print(f"   Retorno sobre capital arriesgado      {(tot_i-tot_c)/tot_c*100:>+11.2f} %")
print(f"   Retorno sobre capital total           {(VAL-CAP)/CAP*100:>+11.2f} %")
print(f"   Operaciones cerradas                  {len(res):>12d}")
gan = sum(1 for *_,pl in res if pl>0)
print(f"   Aciertos                              {gan:>12d}  ({gan/len(res)*100:.0f}%)")
pos_pl = [pl for *_,pl in res if pl>0]; neg_pl = [pl for *_,pl in res if pl<=0]
print(f"   Ganancia media de los aciertos        {sum(pos_pl)/len(pos_pl):>+12,.0f} USD")
print(f"   Perdida media de los errores          {sum(neg_pl)/len(neg_pl):>+12,.0f} USD")
print(f"   Razon ganancia/perdida                "
      f"{abs(sum(pos_pl)/len(pos_pl))/abs(sum(neg_pl)/len(neg_pl)):>12.2f} a 1")
