"""GARCH(1,1) por maxima verosimilitud sobre WMT, mismo metodo que la Tarea 6."""
import csv, math, numpy as np
from scipy.optimize import minimize

d = list(csv.DictReader(open('wmt_diario.csv')))
fechas = [r['Date'] for r in d]
px = np.array([float(r['WMT']) for r in d])
u = 100*np.diff(np.log(px))                 # rendimientos log en %
fechas = fechas[1:]
print(f"Observaciones: {len(u)}  |  {fechas[0]} a {fechas[-1]}")
print(f"Media {u.mean():.4f}%  |  Desv. est. diaria {u.std(ddof=1):.4f}%  "
      f"|  Anualizada {u.std(ddof=1)*math.sqrt(252):.2f}%")

def nll(th):
    w, a, b = th
    if w <= 0 or a < 0 or b < 0 or a+b >= 0.9999: return 1e10
    v = np.empty(len(u)); v[0] = u.var()
    for i in range(1, len(u)):
        v[i] = w + a*u[i-1]**2 + b*v[i-1]
    if np.any(v <= 0): return 1e10
    return 0.5*np.sum(np.log(v) + u**2/v)

best, bll = None, 1e18
for a0 in (0.05, 0.10):
    for b0 in (0.85, 0.90):
        r = minimize(nll, [u.var()*(1-a0-b0), a0, b0], method='Nelder-Mead',
                     options=dict(maxiter=20000, xatol=1e-10, fatol=1e-10))
        if r.fun < bll: bll, best = r.fun, r.x
w, a, b = best
vl = w/(1-a-b)                               # varianza de largo plazo
print(f"\nGARCH(1,1):  omega={w:.6f}  alpha={a:.4f}  beta={b:.4f}  alpha+beta={a+b:.4f}")
print(f"Log-verosimilitud: {-bll:.2f}")
print(f"Varianza de largo plazo {vl:.4f}  ->  volatilidad de largo plazo "
      f"{math.sqrt(252*vl)/100:.2%} anual")
print(f"Vida media del shock: {math.log(0.5)/math.log(a+b):.1f} dias")

v = np.empty(len(u)); v[0] = u.var()
for i in range(1, len(u)): v[i] = w + a*u[i-1]**2 + b*v[i-1]
v_hoy = w + a*u[-1]**2 + b*v[-1]
print(f"\nVolatilidad condicional de hoy: {math.sqrt(252*v_hoy)/100:.2%} anual")

# EWMA de RiskMetrics para contraste
lam = 0.94
ve = u.var()
for x in u: ve = lam*ve + (1-lam)*x**2
print(f"EWMA (lambda=0.94):             {math.sqrt(252*ve)/100:.2%} anual")
for n in (30, 60, 90, 252):
    print(f"Historica {n:>3} dias:              {u[-n:].std(ddof=1)*math.sqrt(252)/100*100:.2f}%")

def pron(T):
    """Hull 23.6: volatilidad promedio esperada sobre T dias habiles."""
    tot = sum(vl + (a+b)**k*(v_hoy-vl) for k in range(T))
    return math.sqrt(252*tot/T)/100

print(f"\n{'Horizonte':<34}{'Dias habiles':>13}{'Vol GARCH':>12}")
for lbl, T in [("Al jueves 12-nov (chequeo)", 5), ("Al viernes 13-nov (entrega)", 6),
               ("Al vencimiento 18-dic", 31), ("A 6 meses", 126), ("A 1 ano", 252)]:
    print(f"{lbl:<34}{T:>13}{pron(T):>11.2%}")

IV_DIC, IV_LEAP = 0.3189, 0.29
print(f"\nContraste contra la implicita de LSEG:")
print(f"  Vencimiento 18-dic-2026:  GARCH {pron(31):.2%}  vs  implicita {IV_DIC:.2%}"
      f"   -> la implicita esta {(IV_DIC/pron(31)-1)*100:+.1f}% sobre el modelo")
print(f"  LEAPs (ene-2029):         GARCH {pron(252*2):.2%}  vs  implicita {IV_LEAP:.2%}"
      f"   -> {(IV_LEAP/pron(252*2)-1)*100:+.1f}%")
print(f"\nPrecio de cierre mas reciente: {px[-1]:.2f}  ({fechas[-1]})")
