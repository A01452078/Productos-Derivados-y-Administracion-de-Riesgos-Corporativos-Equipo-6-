# -*- coding: utf-8 -*-
"""
Cobertura del libro de swaps de Walmart con futuros de tasa y de divisa (CME).
Opciones semanales con vencimiento el lunes 9 de noviembre de 2026.

Contexto. Walmart recibe fijo y paga variable sobre 4,771 MM USD nocionales
(Nota 7 del 10-K) y debe C$5,000 MM. Ni Investopedia ni CME Practice operan
swaps OTC, asi que se usa un proxy listado:

    - Put comprado sobre ZN (nota del Tesoro a 10 anos): gana si suben las tasas,
      que es el escenario que le cuesta al swap receptor de fijo.
    - Call comprado sobre 6C (dolar canadiense): gana si el CAD se aprecia,
      que es el escenario que encarece la deuda en CAD.

Este script hace cuatro cosas y las deja en CSV y PNG:
    1. DV01 del libro de swaps y razon de cobertura (con el supuesto declarado).
    2. Valuacion Black (1976) contra arbol binomial CRR (opciones americanas).
    3. Monte Carlo del P&L conjunto con correlacion entre las dos patas.
    4. Dimensionamiento por presupuesto de riesgo, no por precio unitario.

Los parametros de entrada son los de zn.py y fx_6c.py (lectura del 5-nov-2026).
Los tickets de CME Practice son del 6-nov-2026 a las 2:59 pm CST (2.40 DTE).

Uso:  python3 swap_cobertura.py [carpeta_de_salida]
"""
# %% Parametros
import sys, os
from math import log, sqrt, exp, erf, pi
import numpy as np
from scipy.stats import norm

SALIDA = sys.argv[1] if len(sys.argv) > 1 else "salida_swap"
os.makedirs(SALIDA, exist_ok=True)
SEMILLA = 20261107

RF = 0.0394                       # tasa libre de riesgo (mismo valor que zn.py y fx_6c.py)
CUENTA = 101_200.63               # Practice Funds de CME al 6-nov-2026
PRESUPUESTO = 0.05                # tope de prima: 5% de la cuenta
T_ENTRADA = 2.4 / 365.0           # 2.40 DTE en el ticket del 6-nov, vence el lunes 9-nov
T_HORIZ = 1.0 / 365.0             # revision a 1 dia, antes del vencimiento

PATAS = {
    "ZN": dict(nombre="Put ZNA6 107.25", tipo="put", F=107.3172, K=107.25,
               iv=0.0663, mult=1000.0, prima=0.25, n=5),
    "6C": dict(nombre="Call 6C66 0.715", tipo="call", F=0.7145, K=0.715,
               iv=0.0453, mult=100000.0, prima=0.00005, n=8),
}
RHO = 0.30     # correlacion entre el retorno del ZN y el del 6C (supuesto, ver nota)
# Nota sobre RHO: si suben las tasas, ZN cae y el CAD tiende a caer, de modo que los
# retornos de los dos futuros se mueven juntos (rho > 0). Eso hace que el put de ZN y la
# call de 6C tengan P&L de signo opuesto, que es lo que se quiere en una cobertura.

# Supuesto sobre el libro de swaps de Walmart. El 10-K da el nocional (4,771 MM)
# y el valor razonable (-411 MM), no el plazo medio. Se declara 5 anos y se
# muestra la sensibilidad a ese supuesto mas abajo.
NOCIONAL_SWAPS = 4771e6
VIDA_MEDIA = 5.0
PAR_5A = 0.04732                  # tasa par a 5 anos, curva LSEG del 5-nov
DV01_ZN_CONTRATO = 62.0           # USD por pb de un contrato ZN (aprox., nota CTD ~6.4 anos)

# %% Modelos
N = lambda x: 0.5 * (1.0 + erf(x / sqrt(2.0)))
n = lambda x: exp(-0.5 * x * x) / sqrt(2.0 * pi)

def b76(F, K, T, r, s, tipo):
    if T <= 0 or s <= 0:
        v = max(F - K, 0.0) if tipo == "call" else max(K - F, 0.0)
        return v
    d1 = (log(F / K) + 0.5 * s * s * T) / (s * sqrt(T)); d2 = d1 - s * sqrt(T)
    if tipo == "call":
        return exp(-r * T) * (F * N(d1) - K * N(d2))
    return exp(-r * T) * (K * N(-d2) - F * N(-d1))

def delta76(F, K, T, r, s, tipo):
    d1 = (log(F / K) + 0.5 * s * s * T) / (s * sqrt(T))
    return exp(-r * T) * (N(d1) if tipo == "call" else N(d1) - 1.0)

def crr_futuro(F, K, T, r, s, tipo, pasos=800, americana=True):
    """Arbol CRR para opcion sobre futuro: el futuro tiene deriva cero bajo Q."""
    dt = T / pasos; u = exp(s * sqrt(dt)); d = 1.0 / u
    p = (1.0 - d) / (u - d); desc = exp(-r * dt)
    j = np.arange(pasos + 1)
    S = F * u ** (pasos - j) * d ** j
    v = np.maximum(S - K, 0.0) if tipo == "call" else np.maximum(K - S, 0.0)
    for i in range(pasos - 1, -1, -1):
        v = desc * (p * v[:-1] + (1.0 - p) * v[1:])
        if americana:
            S = F * u ** (i - np.arange(i + 1)) * d ** np.arange(i + 1)
            ej = np.maximum(S - K, 0.0) if tipo == "call" else np.maximum(K - S, 0.0)
            v = np.maximum(v, ej)
    return float(v[0])

# %% 1. DV01 del libro de swaps y razon de cobertura
def anualidad(par, anios):
    """Factor de anualidad con una curva plana al nivel de la tasa par."""
    return (1.0 - (1.0 + par) ** (-anios)) / par

ann = anualidad(PAR_5A, VIDA_MEDIA)
dv01_swaps = NOCIONAL_SWAPS * ann * 1e-4
print("=" * 72)
print("1. DV01 DEL LIBRO DE SWAPS Y RAZON DE COBERTURA")
print("=" * 72)
print(f"  Nocional receptor de fijo      : ${NOCIONAL_SWAPS/1e6:,.0f} MM")
print(f"  Vida media supuesta            : {VIDA_MEDIA:.1f} anos (supuesto, no viene del 10-K)")
print(f"  Anualidad a {PAR_5A*100:.3f}%          : {ann:.3f}")
print(f"  DV01 del libro                 : ${dv01_swaps:,.0f} por punto base")
print(f"  (valor razonable reportado -411 MM; el DV01 ordena de magnitud la perdida por tasas)")

print("\n  Sensibilidad al supuesto de vida media:")
print(f"  {'Vida media':>11} {'DV01 (USD/pb)':>15} {'Contratos ZN':>14}")
for vm in (3.0, 4.0, 5.0, 6.0, 7.0):
    d = NOCIONAL_SWAPS * anualidad(PAR_5A, vm) * 1e-4
    print(f"  {vm:>10.1f}a {d:>15,.0f} {d/DV01_ZN_CONTRATO:>14,.0f}")

p_zn = PATAS["ZN"]
delta_zn = delta76(p_zn["F"], p_zn["K"], T_ENTRADA, RF, p_zn["iv"], "put")
dv01_pata = abs(delta_zn) * DV01_ZN_CONTRATO * p_zn["n"]
print(f"\n  Delta del put ZN               : {delta_zn:.3f}")
print(f"  DV01 efectivo de {p_zn['n']} puts ZN    : ${dv01_pata:,.1f} por pb")
razon = dv01_pata / dv01_swaps
print(f"  Razon de cobertura             : {razon*100:.4f}% del DV01 del libro")
print("  Lectura: con una cuenta de practica de ~$100 mil la posicion es una")
print("  demostracion a escala, no una cobertura efectiva. Lo que se evalua es la")
print("  logica de la cobertura y el dimensionamiento, no su tamano.")

# %% 2. Black vs arbol CRR
print("\n" + "=" * 72)
print("2. VALUACION: BLACK (1976) VS ARBOL BINOMIAL CRR (800 PASOS, AMERICANA)")
print("=" * 72)
print(f"  {'Pata':<18} {'Black':>10} {'CRR amer.':>11} {'CRR eur.':>10} {'Prima ticket':>11} {'Dif. B-real':>12}")
filas_val = []
for k, p in PATAS.items():
    b = b76(p["F"], p["K"], T_ENTRADA, RF, p["iv"], p["tipo"])
    ca = crr_futuro(p["F"], p["K"], T_ENTRADA, RF, p["iv"], p["tipo"], 800, True)
    ce = crr_futuro(p["F"], p["K"], T_ENTRADA, RF, p["iv"], p["tipo"], 800, False)
    p["b76"], p["crr"] = b, ca
    filas_val.append((p["nombre"], b, ca, ce, p["prima"]))
    f = "{:>10.6f}" if k == "6C" else "{:>10.4f}"
    print(f"  {p['nombre']:<18} {f.format(b)} {f.format(ca).rjust(11)} {f.format(ce)} {f.format(p['prima']).rjust(11)} {f.format(b-p['prima']).rjust(12)}")
print("  La prima es el limite del ticket del 6-nov. En el put de ZN queda por encima del modelo")
print("  (la volatilidad implicita de la semanal es mayor que la usada). El limite del call de 6C")
print("  es el tick minimo (0.00005), muy por debajo de la valuacion: por eso el modelo le asigna ganancia esperada positiva.")

# %% 3. Monte Carlo del P&L conjunto
print("\n" + "=" * 72)
print("3. MONTE CARLO DEL P&L CONJUNTO (200,000 TRAYECTORIAS, RHO = %.2f)" % RHO)
print("=" * 72)
rng = np.random.default_rng(SEMILLA)
NSIM = 200_000
Z1 = rng.standard_normal(NSIM // 2); Z2 = rng.standard_normal(NSIM // 2)
Z1 = np.concatenate([Z1, -Z1]); Z2 = np.concatenate([Z2, -Z2])        # antitetico
Zc = RHO * Z1 + sqrt(1 - RHO ** 2) * Z2

def terminal(F, s, T, z):
    return F * np.exp(-0.5 * s * s * T + s * sqrt(T) * z)

def payoff_vec(S, K, tipo):
    return np.maximum(S - K, 0.0) if tipo == "call" else np.maximum(K - S, 0.0)

costo = {}; pnl = {}
for (k, p), z in zip(PATAS.items(), (Z1, Zc)):
    costo[k] = p["prima"] * p["mult"] * p["n"]
    S = terminal(p["F"], p["iv"], T_ENTRADA, z)
    pnl[k] = payoff_vec(S, p["K"], p["tipo"]) * p["mult"] * p["n"] - costo[k]
pnl_tot = pnl["ZN"] + pnl["6C"]
COSTO_TOT = sum(costo.values())

def resumen(nombre, x, c):
    q = np.percentile(x, [5, 25, 50, 75, 95])
    var95 = -np.percentile(x, 5); cvar = -x[x <= np.percentile(x, 5)].mean()
    return (nombre, x.mean(), x.std(), q, (x > 0).mean(), var95, cvar, c)

filas = [resumen("Put ZN", pnl["ZN"], costo["ZN"]),
         resumen("Call 6C", pnl["6C"], costo["6C"]),
         resumen("Conjunto", pnl_tot, COSTO_TOT)]
print(f"  Prima total comprometida: ${COSTO_TOT:,.0f}  ({COSTO_TOT/CUENTA*100:.2f}% de la cuenta)")
print(f"  Perdida maxima posible   : ${-COSTO_TOT:,.0f}  (no hay patas vendidas)\n")
print(f"  {'':<10} {'Media':>9} {'Desv.':>9} {'P5':>9} {'P50':>9} {'P95':>9} {'P(ganar)':>9} {'CVaR95':>9}")
for nom, m, sd, q, pg, v, cv, c in filas:
    print(f"  {nom:<10} {m:>9,.0f} {sd:>9,.0f} {q[0]:>9,.0f} {q[2]:>9,.0f} {q[4]:>9,.0f} {pg*100:>8.1f}% {cv:>9,.0f}")
corr_pnl = np.corrcoef(pnl["ZN"], pnl["6C"])[0, 1]
print(f"\n  Correlacion entre los P&L de las dos patas: {corr_pnl:+.3f}")
print("  (Negativa: una pata financia a la otra. Es lo que distingue una cobertura de acumulacion.)")
print(f"  Media del conjunto ${pnl_tot.mean():,.0f}: la pata de ZN pierde en promedio (costo del seguro) y la de 6C gana en promedio")
print("  solo porque su limite (0.00005) esta muy por debajo de la valuacion. La media del put de ZN solo es el costo limpio del seguro.")

# Referencia: el ZN solo (misma cantidad, sin la pata de divisa)
pnl_conc = pnl["ZN"]; n_conc = PATAS["ZN"]["n"]; c_conc = costo["ZN"]
print(f"\n  ZN solo ({n_conc} puts, ${c_conc:,.0f}): media ${pnl_conc.mean():,.0f} | desv. ${pnl_conc.std():,.0f} | P(ganar) {(pnl_conc>0).mean()*100:.1f}%")
print(f"  Conjunto          : media ${pnl_tot.mean():,.0f} | desv. ${pnl_tot.std():,.0f} | P(ganar) {(pnl_tot>0).mean()*100:.1f}%")

# P&L a 1 dia con revaluacion Black (antes del vencimiento)
pnl_h = np.zeros(NSIM)
for (k, p), z in zip(PATAS.items(), (Z1, Zc)):
    S = terminal(p["F"], p["iv"], T_ENTRADA - T_HORIZ, z)
    # revaluacion con Black al tiempo remanente, vectorizada
    d1 = (np.log(S / p["K"]) + 0.5 * p["iv"] ** 2 * (T_ENTRADA - T_HORIZ)) / (p["iv"] * sqrt(T_ENTRADA - T_HORIZ))
    d2 = d1 - p["iv"] * sqrt(T_ENTRADA - T_HORIZ)
    if p["tipo"] == "call":
        v = exp(-RF * (T_ENTRADA - T_HORIZ)) * (S * norm.cdf(d1) - p["K"] * norm.cdf(d2))
    else:
        v = exp(-RF * (T_ENTRADA - T_HORIZ)) * (p["K"] * norm.cdf(-d2) - S * norm.cdf(-d1))
    pnl_h += v * p["mult"] * p["n"] - costo[k]
print(f"\n  P&L a 1 dia (revaluado): media ${pnl_h.mean():,.0f} | P5 ${np.percentile(pnl_h,5):,.0f} | P95 ${np.percentile(pnl_h,95):,.0f}")
print("  Con 2.4 dias de vida el valor temporal se consume rapido: por eso el horizonte")
print("  de revision se fija antes de abrir, una de las tres correcciones del ciclo.")

# %% 4. Regimenes y dimensionamiento
print("\n" + "=" * 72)
print("4. REGIMENES Y DIMENSIONAMIENTO POR PRESUPUESTO DE RIESGO")
print("=" * 72)
mov_zn = {"tasas suben": -1.0, "tasas bajan": +1.0}      # puntos de ZN
mov_cad = {"CAD sube": +0.0050, "CAD cae": -0.0050}       # retorno relativo
reg = [("Reflacion (tasas suben, dolar se debilita: CAD sube)", "tasas suben", "CAD sube"),
       ("Fed restrictiva (tasas suben, dolar se fortalece: CAD cae)", "tasas suben", "CAD cae"),
       ("Fed acomodaticia (tasas bajan, dolar se debilita: CAD sube)", "tasas bajan", "CAD sube"),
       ("Aversion al riesgo (tasas bajan, dolar se fortalece: CAD cae)", "tasas bajan", "CAD cae")]
T_R = 0.0                         # los regimenes se valoran al vencimiento (valor intrinseco)
filas_reg = []
print(f"  {'Regimen':<60} {'Put ZN':>9} {'Call 6C':>9} {'Total':>9}")
for nom, a, b in reg:
    pz = PATAS["ZN"]; pc = PATAS["6C"]
    vz = b76(pz["F"] + mov_zn[a], pz["K"], T_R, RF, pz["iv"], "put") * pz["mult"] * pz["n"] - costo["ZN"]
    vc = b76(pc["F"] * (1 + mov_cad[b]), pc["K"], T_R, RF, pc["iv"], "call") * pc["mult"] * pc["n"] - costo["6C"]
    filas_reg.append((nom, vz, vc, vz + vc))
    print(f"  {nom:<60} {vz:>9,.0f} {vc:>9,.0f} {vz+vc:>9,.0f}")
print("  Solo el cuarto regimen castiga las dos patas: dolar fuerte con rendimientos a la baja,\n  el patron de una fuga hacia la calidad. En los otros tres una pata financia a la otra.")

print("\n  Dimensionamiento: las cantidades (5 y 8) son las de los tickets del 6-nov.")
prima_t = {k: p["prima"] * p["mult"] for k, p in PATAS.items()}
print(f"    Put ZN : 5 x ${prima_t['ZN']:,.0f} = ${costo['ZN']:,.0f}")
print(f"    Call 6C: 8 x ${prima_t['6C']:,.0f} = ${costo['6C']:,.0f}")
print(f"    Total  : ${COSTO_TOT:,.0f} = {COSTO_TOT/CUENTA*100:.2f}% de la cuenta (tope del 5% sin usar)")
presup_pata = {"ZN": 2750.0, "6C": 2100.0}
print("  Referencia: con la regla de presupuesto por pata (contratos = presupuesto / (prima x mult))")
for k, p in PATAS.items():
    b = b76(p["F"], p["K"], T_ENTRADA, RF, p["iv"], p["tipo"]) * p["mult"]
    print(f"    {p['nombre']:<18} a precio Black (${b:,.0f} por contrato): {int(presup_pata[k] // b)} contratos")

# %% Salidas
import csv
with open(os.path.join(SALIDA, "swap_resumen_mc.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["pata", "media", "desv", "p5", "p25", "p50", "p75", "p95", "p_ganar", "var95", "cvar95", "prima"])
    for nom, m, sd, q, pg, v, cv, c in filas:
        w.writerow([nom, round(m, 2), round(sd, 2)] + [round(x, 2) for x in q] + [round(pg, 4), round(v, 2), round(cv, 2), round(c, 2)])
with open(os.path.join(SALIDA, "swap_regimenes.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["regimen", "put_zn", "call_6c", "total"])
    for r in filas_reg: w.writerow([r[0]] + [round(x, 2) for x in r[1:]])
with open(os.path.join(SALIDA, "swap_valuacion.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["pata", "black", "crr_americana", "crr_europea", "prima_ticket"])
    for r in filas_val: w.writerow([r[0]] + [round(x, 6) for x in r[1:]])

with open(os.path.join(SALIDA, "swap_dv01.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["vida_media_anios", "dv01_usd_por_pb", "contratos_zn_equivalentes"])
    for vm in (3.0, 4.0, 5.0, 6.0, 7.0):
        d = NOCIONAL_SWAPS * anualidad(PAR_5A, vm) * 1e-4
        w.writerow([vm, round(d, 0), round(d / DV01_ZN_CONTRATO, 0)])
    w.writerow(["pata_efectiva_5_puts_zn", round(dv01_pata, 1), round(razon * 100, 4)])

try:
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    AZUL, NARANJA, VERDE, GRIS = "#2a78d6", "#eb6834", "#1baf7a", "#898781"
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    lim = np.percentile(pnl_tot, [0.5, 99.5])
    ax[0].hist(np.clip(pnl_tot, *lim), bins=70, color=AZUL, alpha=.85)
    ax[0].axvline(-COSTO_TOT, color=NARANJA, lw=1.5, label=f"Perdida maxima -${COSTO_TOT:,.0f}")
    ax[0].axvline(pnl_tot.mean(), color=VERDE, lw=1.5, label=f"Media ${pnl_tot.mean():,.0f}")
    ax[0].set_title("P&L conjunto al vencimiento (Monte Carlo)"); ax[0].set_xlabel("USD"); ax[0].legend(frameon=False, fontsize=8)
    ax[1].scatter(pnl["ZN"][::40], pnl["6C"][::40], s=3, color=AZUL, alpha=.35)
    ax[1].axhline(0, color=GRIS, lw=.6); ax[1].axvline(0, color=GRIS, lw=.6)
    ax[1].set_title(f"P&L por pata (corr. {corr_pnl:+.2f})"); ax[1].set_xlabel("Put ZN, USD"); ax[1].set_ylabel("Call 6C, USD")
    for a in ax:
        for s in ("top", "right"): a.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(os.path.join(SALIDA, "swap_montecarlo.png"), dpi=150)
    print("\nGuardado:", os.path.join(SALIDA, "swap_montecarlo.png"))
except Exception as e:
    print("Sin grafica:", e)
print("Guardados los CSV en", SALIDA)
