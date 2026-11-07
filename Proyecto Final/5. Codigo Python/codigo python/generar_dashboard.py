# -*- coding: utf-8 -*-
"""
Generador del dashboard de Walmart (WMT.O)
Proyecto Final · Productos Derivados y Administración de Riesgos Corporativos
EGADE Business School · Maestría en Finanzas · Equipo 6, Grupo 40
Eduardo Ayala Saldaña (A01192714) | Mariann Antonelli Morales Tobias (A01452078) | Ulises Salinas López (A00814787)

Este script produce Dashboard_Walmart.html de principio a fin, sin pasos manuales:

    datos de LSEG (09_datos)  ->  cálculo en Python  ->  HTML autocontenido con Plotly

Entradas (carpeta 09_datos):
    lseg/LSEG_Deuda_WMT.xlsx   Government and Corporate Bonds Advanced Search (LSEG Workspace), corte 23-oct-2026
    curva.csv                  Curva del Tesoro, 13 plazos (LSEG / TRADEWEB), 1-nov-2026
    dec18.csv                  Cadena de opciones de WMT, vencimiento 18-dic-2026 (LSEG Option Watch)
    vol_term.csv               Volatilidad implícita ATM por vencimiento (LSEG Option Watch)
    wmt_diario.csv             Cierres diarios de WMT, nov-2020 a nov-2026 (LSEG Price History)
Salida:
    Dashboard_Walmart.html     Un solo archivo, se abre en cualquier navegador sin conexión.

Uso:
    python generar_dashboard.py
    python generar_dashboard.py --datos ../09_datos --salida ../02_dashboard/Dashboard_Walmart.html
    (sin argumentos busca 09_datos junto al script o un nivel arriba y escribe en 02_dashboard/)

Dependencias: numpy, scipy, openpyxl (en Colab ya vienen instaladas, salvo quizá openpyxl).
Plotly se lee de assets/plotly-basic.min.js; si no existe se descarga una vez de jsDelivr.
"""
import os, sys, csv, json, math, datetime, statistics, argparse, urllib.request
from dataclasses import dataclass
import numpy as np
from scipy.optimize import minimize
import openpyxl

# ============================================================
# 0. CONFIGURACION
# ============================================================
AQUI = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
_ap = argparse.ArgumentParser(description="Genera Dashboard_Walmart.html")
_ap.add_argument("--datos",  default=None, help="carpeta 09_datos (por defecto ../09_datos)")
_ap.add_argument("--salida", default=None, help="ruta del HTML (por defecto <raíz>/02_dashboard/Dashboard_Walmart.html)")
_ap.add_argument("--etapa",  default="Proyecto Final", help="etiqueta amarilla de la portada")
ARGS, _ = _ap.parse_known_args()          # parse_known_args: también funciona dentro de un notebook

def _primera_existente(*rutas):
    for r in rutas:
        if r and os.path.exists(r): return r
    return rutas[0]

DATOS  = ARGS.datos or _primera_existente(os.path.join(AQUI, "..", "09_datos"), os.path.join(AQUI, "..", "..", "09_datos"),
                                          os.path.join(AQUI, "09_datos"), "09_datos", "/content/09_datos")
RAIZ   = os.path.dirname(os.path.abspath(DATOS))          # raíz del repositorio
SALIDA = ARGS.salida or os.path.join(RAIZ, "02_dashboard", "Dashboard_Walmart.html")
PLOTLY = _primera_existente(os.path.join(AQUI, "assets", "plotly-basic.min.js"), os.path.join(AQUI, "..", "assets", "plotly-basic.min.js"),
                            os.path.join(RAIZ, "06_codigo_python", "assets", "plotly-basic.min.js"))
PLOTLY_CDN = "https://cdn.jsdelivr.net/npm/plotly.js-basic-dist-min@4.1.2/plotly-basic.min.js"
ETAPA  = ARGS.etapa
ASOF   = datetime.date(2026, 10, 23)      # corte de la deuda y de los precios de los bonos
PX_DEUDA = 119.89                          # cierre de WMT.O el 23-oct-2026 (corte de la deuda)

# ============================================================
# 1. VALORACION: Black-Scholes, arbol binomial y convertible
#    (misma lógica que wmt_derivados.py, copiada tal cual)
# ============================================================
# ============================================================
# 2. PARAMETROS DE MERCADO  (LSEG Workspace, corte 30-oct-2026)
# ============================================================
S0       = 123.51      # Precio de cierre WMT.O
DIV      = 0.25        # Dividendo trimestral declarado
T_DIV    = 40/365      # Dias al ex-dividendo (11-dic-2026), desde 01-nov-2026
T_EXP    = 47/365      # Dias al vencimiento  (18-dic-2026), desde 01-nov-2026
                       # NOTA: LSEG mide el plazo desde la fecha calendario corriente,
                       # no desde la fecha del ultimo trade. Verificado por calibracion
                       # inversa contra ImpVol Mid: el sesgo pasa de -72 pb a -6 pb.
RF       = 0.0403      # Tasa libre de riesgo a 47 dias, interpolada de la curva
                       # del Tesoro (LSEG/TRADEWEB 01-nov-2026): 1M 3.97%, 2M 4.08%
SIGMA_LP = 0.29        # Volatilidad de largo plazo (LEAPs 2028-2029)

# ============================================================
# 3. BLACK-SCHOLES-MERTON con dividendo discreto (modelo escrow)
# ============================================================
def _norm_cdf(x):
    return 0.5*(1.0+math.erf(x/math.sqrt(2.0)))

def _norm_pdf(x):
    return math.exp(-0.5*x*x)/math.sqrt(2.0*math.pi)

def pv_dividendos(divs, r):
    """Valor presente de los dividendos discretos anteriores al vencimiento."""
    return sum(d*math.exp(-r*t) for d, t in divs)

def black_scholes(S, K, T, r, sigma, tipo="call", divs=()):
    """Precio europeo. Los dividendos discretos se descuentan del spot (Hull, cap. 15)."""
    S_adj = S - pv_dividendos(divs, r)
    if T <= 0 or sigma <= 0:
        intr = max(S_adj-K, 0.0) if tipo == "call" else max(K-S_adj, 0.0)
        return intr
    d1 = (math.log(S_adj/K) + (r + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
    d2 = d1 - sigma*math.sqrt(T)
    if tipo == "call":
        return S_adj*_norm_cdf(d1) - K*math.exp(-r*T)*_norm_cdf(d2)
    return K*math.exp(-r*T)*_norm_cdf(-d2) - S_adj*_norm_cdf(-d1)

def griegas_bs(S, K, T, r, sigma, tipo="call", divs=()):
    """Griegas analiticas. Theta por dia natural, vega y rho por punto porcentual."""
    S_adj = S - pv_dividendos(divs, r)
    d1 = (math.log(S_adj/K) + (r + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
    d2 = d1 - sigma*math.sqrt(T)
    disc = math.exp(-r*T)
    delta = _norm_cdf(d1) if tipo == "call" else _norm_cdf(d1)-1.0
    gamma = _norm_pdf(d1)/(S_adj*sigma*math.sqrt(T))
    vega  = S_adj*_norm_pdf(d1)*math.sqrt(T)/100.0
    if tipo == "call":
        theta = (-S_adj*_norm_pdf(d1)*sigma/(2*math.sqrt(T)) - r*K*disc*_norm_cdf(d2))/365.0
        rho   =  K*T*disc*_norm_cdf(d2)/100.0
    else:
        theta = (-S_adj*_norm_pdf(d1)*sigma/(2*math.sqrt(T)) + r*K*disc*_norm_cdf(-d2))/365.0
        rho   = -K*T*disc*_norm_cdf(-d2)/100.0
    return dict(delta=delta, gamma=gamma, vega=vega, theta=theta, rho=rho)

def vol_implicita(precio, S, K, T, r, tipo="call", divs=(), lo=1e-4, hi=5.0, tol=1e-10):
    """Volatilidad implicita por biseccion sobre Black-Scholes."""
    f = lambda s: black_scholes(S, K, T, r, s, tipo, divs) - precio
    if f(lo)*f(hi) > 0:
        return None
    for _ in range(200):
        mid = 0.5*(lo+hi)
        if abs(hi-lo) < tol:
            break
        if f(lo)*f(mid) <= 0: hi = mid
        else:                 lo = mid
    return 0.5*(lo+hi)

# ============================================================
# 4. ARBOL BINOMIAL COX-ROSS-RUBINSTEIN
# ============================================================
@dataclass
class ResultadoArbol:
    europea: float
    americana: float
    premio_ejercicio: float
    delta: float
    gamma: float
    theta: float
    nodos_ejercicio: int

def arbol_crr(S, K, T, r, sigma, N, tipo="call", americana=True, divs=()):
    """
    Arbol CRR con dividendos discretos por el metodo de escrow (Hull, cap. 21).
    El arbol se construye sobre S* = S - VP(dividendos); el dividendo se
    reincorpora en los nodos anteriores a la fecha ex-dividendo, de modo que el
    valor intrinseco en cada nodo refleja el precio observable de la accion.
    """
    dt = T/N
    u  = math.exp(sigma*math.sqrt(dt))
    d  = 1.0/u
    p  = (math.exp(r*dt) - d)/(u - d)
    disc = math.exp(-r*dt)
    S_star = S - pv_dividendos(divs, r)

    def escrow(i):
        """VP al paso i de los dividendos que aun no se pagan."""
        t = i*dt
        return sum(dv*math.exp(-r*(td-t)) for dv, td in divs if td > t)

    precios = [[S_star*(u**(j))*(d**(i-j)) + escrow(i) for j in range(i+1)] for i in range(N+1)]
    intr = (lambda s: max(s-K, 0.0)) if tipo == "call" else (lambda s: max(K-s, 0.0))

    V = [intr(s) for s in precios[N]]
    nodos_ej = 0
    guardar = {}
    for i in range(N-1, -1, -1):
        Vn = []
        for j in range(i+1):
            cont = disc*(p*V[j+1] + (1-p)*V[j])
            if americana:
                ex = intr(precios[i][j])
                if ex > cont:
                    nodos_ej += 1
                    Vn.append(ex)
                else:
                    Vn.append(cont)
            else:
                Vn.append(cont)
        V = Vn
        if i <= 2:
            guardar[i] = (list(V), list(precios[i]))
    return V[0], nodos_ej, guardar, dict(u=u, d=d, p=p, dt=dt)

def valuar_arbol(S, K, T, r, sigma, N, tipo="call", divs=()):
    """Europea, americana, premio de ejercicio y griegas tomadas del arbol."""
    eur, _, _, _   = arbol_crr(S, K, T, r, sigma, N, tipo, False, divs)
    ame, nej, g, par = arbol_crr(S, K, T, r, sigma, N, tipo, True, divs)
    (V0,_), (V1,P1), (V2,P2) = g[0], g[1], g[2]
    # Delta y gamma del paso 1 y 2; theta del nodo central del paso 2
    delta = (V1[1]-V1[0])/(P1[1]-P1[0])
    d1 = (V2[2]-V2[1])/(P2[2]-P2[1])
    d2 = (V2[1]-V2[0])/(P2[1]-P2[0])
    gamma = (d1-d2)/(0.5*(P2[2]-P2[0]))
    theta = (V2[1]-V0[0])/(2*par['dt'])/365.0
    return ResultadoArbol(eur, ame, ame-eur, delta, gamma, theta, nej)

def griegas_arbol(S, K, T, r, sigma, N, tipo="call", divs=(), h_s=0.01, h_v=0.01, h_r=0.0001):
    """Vega y rho por revaluacion; delta, gamma y theta del propio arbol."""
    base = valuar_arbol(S, K, T, r, sigma, N, tipo, divs)
    up   = arbol_crr(S, K, T, r, sigma+h_v, N, tipo, True, divs)[0]
    dn   = arbol_crr(S, K, T, r, max(sigma-h_v,1e-6), N, tipo, True, divs)[0]
    rup  = arbol_crr(S, K, T, r+h_r, sigma, N, tipo, True, divs)[0]
    rdn  = arbol_crr(S, K, T, r-h_r, sigma, N, tipo, True, divs)[0]
    return dict(precio=base.americana, europea=base.europea,
                premio=base.premio_ejercicio, nodos_ejercicio=base.nodos_ejercicio,
                delta=base.delta, gamma=base.gamma, theta=base.theta,
                vega=(up-dn)/(2*h_v)/100.0, rho=(rup-rdn)/(2*h_r)/100.0)


# ============================================================
# 5. CURVA DE TASAS Y VALORACION DEL CONVERTIBLE
# ============================================================
CURVA_UST = [(0.0833,3.9715),(0.1667,4.0835),(0.25,4.0820),(0.3333,4.1905),
             (0.5,4.2690),(1,4.3755),(2,4.6030),(3,4.6710),(5,4.7320),
             (7,4.8230),(10,4.9350),(20,5.3420),(30,5.3145)]  # LSEG/TRADEWEB 01-nov-2026

def ust(T):
    """Tasa del Tesoro interpolada linealmente, en decimal."""
    C = CURVA_UST
    if T <= C[0][0]:  return C[0][1]/100
    if T >= C[-1][0]: return C[-1][1]/100
    for (t0,y0),(t1,y1) in zip(C, C[1:]):
        if t0 <= T <= t1:
            return (y0 + (y1-y0)*(T-t0)/(t1-t0))/100

def bono_recto(cupon, anios, ytm, face=100.0, freq=2):
    """Valor presente de un bono bullet con cupones semestrales."""
    n = int(round(anios*freq)); c = face*cupon/freq; y = ytm/freq
    return sum(c/(1+y)**k for k in range(1, n+1)) + face/(1+y)**n

def bs_call_q(S, K, T, r, sigma, q):
    """Call europea con dividend yield continuo (Merton 1973)."""
    d1 = (math.log(S/K) + (r - q + 0.5*sigma**2)*T)/(sigma*math.sqrt(T))
    d2 = d1 - sigma*math.sqrt(T)
    return S*math.exp(-q*T)*_norm_cdf(d1) - K*math.exp(-r*T)*_norm_cdf(d2)

def convertible(S, anios, ytm_recto, sigma, q, prima_conv, cupon, face=100.0):
    """
    Convertible = bono recto + opcion call sobre la accion.
    prima_conv: prima de conversion sobre el spot (0.25 = 25%).
    Devuelve los componentes por cada 100 de valor nominal.
    """
    K   = S*(1+prima_conv)                 # precio de conversion
    ratio = face/K                         # acciones por cada 100 de nominal
    r   = ust(anios)
    bono = bono_recto(cupon, anios, ytm_recto, face)
    opc  = ratio*bs_call_q(S, K, anios, r, sigma, q)
    return dict(precio_conversion=K, ratio=ratio, bono=bono, opcion=opc,
                total=bono+opc, r=r, ytm_recto=ytm_recto)

def cupon_a_la_par(S, anios, ytm_recto, sigma, q, prima_conv, face=100.0):
    """Cupon que hace que el convertible cotice exactamente a la par."""
    lo, hi = 0.0, ytm_recto*1.5
    for _ in range(200):
        mid = (lo+hi)/2
        v = convertible(S, anios, ytm_recto, sigma, q, prima_conv, mid, face)["total"]
        if v > face: hi = mid
        else:        lo = mid
    return (lo+hi)/2

def call_spread(S, anios, sigma, q, prima_compra, prima_venta, acciones):
    """
    Estructura Molson Coors: se compra la call al strike de conversion y se vende
    un warrant a un strike mas alto. El neto eleva la prima de conversion efectiva
    sin pagar el costo de una call sola.
    """
    r  = ust(anios)
    K1 = S*(1+prima_compra); K2 = S*(1+prima_venta)
    c1 = bs_call_q(S, K1, anios, r, sigma, q)
    c2 = bs_call_q(S, K2, anios, r, sigma, q)
    return dict(K_compra=K1, K_venta=K2, prima_pagada=c1*acciones,
                prima_cobrada=c2*acciones, costo_neto=(c1-c2)*acciones,
                costo_unitario=c1-c2)

# ============================================================
# 6. PARAMETROS DEL CONVERTIBLE PROPUESTO
# ============================================================
CV_PLAZO   = 6          # anios, mismo plazo que la emision de Molson Coors 2007
CV_SIGMA   = 0.29       # volatilidad implicita de los LEAPs (ene-2029)
CV_Q       = 0.0081     # dividend yield prospectivo FY ene-2027 (LSEG)
CV_YTM     = 0.0514     # rendimiento de deuda recta WMT a 6 anios
                        # interpolado: nota 4.15% 2031 (5a) 5.019% / 5.35% 2033 (7a) 5.255%
CV_PRIMA   = 0.25       # prima de conversion, igual que Molson Coors
CV_EMISION = 1500.0     # millones de dolares
CS_PRIMA_V = 0.60       # prima del warrant vendido, igual que Molson Coors


# ============================================================
# 7. SWAPS Y CURVA BOOTSTRAPEADA  (de wmt_swaps.py)
# ============================================================
# ============================================================
# 8. CURVA Y BOOTSTRAPPING
# ============================================================
PAR_UST = [(0.0833,3.9715),(0.1667,4.0835),(0.25,4.0820),(0.3333,4.1905),
           (0.5,4.2690),(1,4.3755),(2,4.6030),(3,4.6710),(5,4.7320),
           (7,4.8230),(10,4.9350),(20,5.3420),(30,5.3145)]

FREQ = 2                      # cupon semestral, convencion del mercado de swaps
TAU  = 1.0/FREQ

def par_interp(T, curva=PAR_UST):
    """Rendimiento par interpolado linealmente, en decimal."""
    if T <= curva[0][0]:  return curva[0][1]/100
    if T >= curva[-1][0]: return curva[-1][1]/100
    for (t0,y0),(t1,y1) in zip(curva, curva[1:]):
        if t0 <= T <= t1:
            return (y0 + (y1-y0)*(T-t0)/(t1-t0))/100

def bootstrap(curva=PAR_UST, Tmax=30.0):
    """
    Factores de descuento en malla semestral.
    Hasta 1 ano las cotizaciones son de bills (cupon cero).
    De ahi en adelante son rendimientos par de bonos con cupon semestral:
        100 = c * sum(DF_i) + 100 * DF_n   =>   DF_n = (100 - c*sum) / (100 + c)
    """
    DF = {}
    n = int(round(Tmax*FREQ))
    acum = 0.0
    for k in range(1, n+1):
        t = k*TAU
        y = par_interp(t, curva)
        if t <= 1.0:
            DF[t] = 1.0/(1.0 + y*TAU)**(t*FREQ)      # cupon cero
        else:
            c = 100*y*TAU
            DF[t] = (100 - c*acum)/(100 + c)
        acum += DF[t]
    return DF

DF = bootstrap()

def df(T):
    """Factor de descuento interpolado sobre la malla semestral."""
    if T <= 0: return 1.0
    ks = sorted(DF)
    if T <= ks[0]:  return 1.0 + (DF[ks[0]]-1.0)*T/ks[0]
    if T >= ks[-1]: return DF[ks[-1]]
    for a, b in zip(ks, ks[1:]):
        if a <= T <= b:
            return DF[a] + (DF[b]-DF[a])*(T-a)/(b-a)

def cero(T):
    """Tasa cupon cero con capitalizacion semestral, en decimal."""
    return FREQ*((1.0/df(T))**(1.0/(T*FREQ)) - 1.0)

def fechas(T0, T1):
    """
    Fechas de pago semestrales, contadas hacia atras desde el vencimiento.
    Un swap que vence en 2.48 anos paga en 2.48, 1.98, 1.48, 0.98 y 0.48,
    no en la malla de 0.5 en 0.5 desde el origen.
    """
    out, t = [], T1
    while t > T0 + 1e-9:
        out.append(t); t -= TAU
    return sorted(out)

def anualidad(T0, T1):
    """Valor presente de 1 unidad anual pagada semestralmente entre T0 y T1."""
    return sum(TAU*df(t) for t in fechas(T0, T1))

# ============================================================
# 9. SWAP DE TASA DE INTERES (vanilla, fija contra flotante)
# ============================================================
def tasa_par_swap(T, T0=0.0):
    """
    Tasa fija que hace que el swap valga cero al inicio.
    Con una sola curva de descuento, la pata flotante vale
    DF(T0) - DF(T1), de modo que la tasa par es esa diferencia
    dividida entre la anualidad.
    """
    return (df(T0) - df(T)) / anualidad(T0, T)

def valor_swap(nocional, fija, T, T0=0.0, paga_fija=True):
    """
    Valor de mercado del swap, en unidades del nocional.
    paga_fija=True: el cliente paga fijo y recibe flotante
    (es la direccion que convierte deuda flotante en fija).
    """
    pata_fija = fija*anualidad(T0, T)*nocional
    pata_flot = (df(T0) - df(T))*nocional
    return (pata_flot - pata_fija) if paga_fija else (pata_fija - pata_flot)

def dv01(nocional, T, T0=0.0):
    """Sensibilidad del swap a un punto base, en unidades del nocional."""
    return anualidad(T0, T)*nocional*1e-4

# ============================================================
# 10. T-LOCK  (cobertura de la tasa del Tesoro en un refinanciamiento)
# ============================================================
def tasa_forward(T0, T1):
    """Tasa par forward: empieza en T0, vence en T1."""
    return (df(T0) - df(T1)) / anualidad(T0, T1)

def tlock(nocional, T0, T1, mov_pb):
    """
    Resultado del T-lock ante un movimiento paralelo de la curva.
    Quien va a emitir deuda se perjudica si las tasas suben; el T-lock
    gana en ese escenario y compensa el mayor costo de la emision.
    Se aproxima por duracion: resultado = DV01 forward * movimiento.
    """
    d = anualidad(T0, T1)*nocional*1e-4
    return d*mov_pb

# ============================================================
# 11. CROSS-CURRENCY SWAP
# ============================================================
# La emision del 23-oct-2026 en dolares canadienses y su tramo gemelo en
# dolares permiten aislar el calculo, porque comparten emisor, fecha de
# emision y fecha de vencimiento.
CCS = dict(
    nocional_cad   = 5000.0,     # millones de dolares canadienses
    usdcad         = 1.4008,     # tipo de cambio implicito en la conversion de LSEG
    cupon_cad      = 4.450,      # tramo 2033 en CAD, %
    cupon_usd      = 5.350,      # tramo 2033 en USD, %
    ytm_cad        = 4.313,      # %
    ytm_usd        = 5.255,      # %
    z_cad          = 70.0,       # puntos base sobre la curva
    z_usd          = 35.6,       # puntos base
    plazo          = 7.0,        # anos
)

def dif_curvas():
    """
    Diferencial entre la curva gubernamental canadiense y la estadounidense,
    despejado de los dos tramos a 2033:
        YTM = curva + Z-spread   =>   curva_USD - curva_CAD = dYTM + dZ
    """
    d_ytm = CCS['ytm_usd'] - CCS['ytm_cad']
    d_z   = CCS['z_cad'] - CCS['z_usd']
    return d_ytm*100 + d_z          # en puntos base

def costo_todo_incluido():
    """
    Costo de la emision en CAD una vez swapeada a dolares, contra la
    emision directa en dolares.

    El cross-currency swap intercambia la tasa canadiense por la
    estadounidense. Lo que sobrevive al swap no es el diferencial de
    curva, que el propio swap devuelve, sino el diferencial de
    spread de credito entre las dos monedas.
    """
    base_usd = CCS['z_usd']                          # pb sobre la curva USD
    base_cad = CCS['z_cad']                          # pb sobre la curva CAD
    return dict(
        directo_usd      = base_usd,
        cad_swapeado     = base_cad,
        diferencia_pb    = base_cad - base_usd,
        basis_necesario  = base_cad - base_usd,      # el basis que haria indiferente
        nocional_usd     = CCS['nocional_cad']/CCS['usdcad'],
    )

# ============================================================
# 12. POSICIONES A CUBRIR  (LSEG, corte 23-oct-2026)
# ============================================================
HOY = "2026-11-05"
FRN = [  # notas de tasa flotante: (monto MUSD, vencimiento, cupon vigente %, plazo en anos)
    (750.0, "2027-04-28", 4.18213, 0.48),
    (350.0, "2029-04-30", 4.15576, 2.48),
]
# Bloque de cupon bajo que debe refinanciarse
CUPON_BAJO = [
    (1250.0, "2028-09-22", 1.500, 1.88),
    (2000.0, "2031-09-22", 1.800, 4.88),
    ( 500.0, "2029-09-24", 2.375, 2.89),
]


# ============================================================
# 13. CALCULO DE TODOS LOS DATOS DEL DASHBOARD
# ============================================================
def cargar_deuda(ruta):
    """Notas de Walmart (53) y papel comercial (26) desde el export de LSEG."""
    wb = openpyxl.load_workbook(ruta, data_only=True)
    ws = wb.worksheets[0]; hdr = [c.value for c in ws[1]]; H = {k: i for i, k in enumerate(hdr)}
    num = lambda v: float(v) if isinstance(v, (int, float)) else None
    CUR = {'US Dollar': 'USD', 'British Pound': 'GBP', 'Canadian Dollar': 'CAD', 'Euro': 'EUR', 'Japanese Yen': 'JPY'}
    bonds, cp = [], []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[0] != 'Walmart Inc.': continue
        g = lambda k: r[H[k]]
        rec = dict(isin=g('ISIN'), cur=CUR.get(g('Principal Currency'), g('Principal Currency')),
                   cpn=num(r[2]), mat=g('Maturity').date().isoformat(), iss=g('Issue Date').date().isoformat(),
                   out=num(g('Amount Outstanding (USD)')), issd=num(g('Amount Issued (USD)')),
                   ytm=num(g('Yield to Maturity')), z=num(g('Option Adjusted Zero Volatility Spread (Z-Spread)')),
                   px=num(g('TRPS / Composite Price')), call=g('Callable'), ctype=g('Call Type'))
        (bonds if g('Instrument Type') == 'Note' else cp).append(rec)
    for b in bonds:
        b['yrs'] = round((datetime.date.fromisoformat(b['mat']) - ASOF).days / 365.25, 2)
        b['ret'] = round((1 - b['out'] / b['issd']) * 100, 1) if b['issd'] else 0
    bonds.sort(key=lambda b: b['mat'])
    return bonds, cp

def estadisticas(bonds, cp):
    OUT = sum(b['out'] for b in bonds); ISS = sum(b['issd'] for b in bonds)
    MV = sum(b['out'] * b['px'] / 100 for b in bonds)
    W = lambda f: sum(f(b) * b['out'] for b in bonds) / OUT
    zs = [b for b in bonds if b['z'] is not None]
    new = [b for b in bonds if b['iss'] == '2026-10-23']
    cur = {}
    for b in bonds: cur[b['cur']] = cur.get(b['cur'], 0) + b['out']
    corr = statistics.correlation([b['cpn'] for b in bonds], [b['ret'] for b in bonds])
    low = [b for b in bonds if b['cpn'] < 3]
    return dict(asof=ASOF.isoformat(), n=len(bonds), ncp=len(cp),
        out=OUT, issd=ISS, ret=ISS - OUT, retpct=(ISS - OUT) / ISS * 100, mv=MV, disc=OUT - MV, discpct=(OUT - MV) / OUT * 100,
        wcpn=W(lambda b: b['cpn']), wytm=W(lambda b: b['ytm']), wyrs=W(lambda b: b['yrs']),
        wz=sum(b['z'] * b['out'] for b in zs) / sum(b['out'] for b in zs),
        newtot=sum(b['out'] for b in new), nnew=len(new),
        nonusd=OUT - cur.get('USD', 0), nonusdpct=(OUT - cur.get('USD', 0)) / OUT * 100,
        ncall=sum(1 for b in bonds if b['call'] == 'Yes'),
        callamt=sum(b['out'] for b in bonds if b['call'] == 'Yes'),
        corr=corr, lowtot=sum(b['out'] for b in low),
        lowcpn=sum(b['cpn'] * b['out'] for b in low) / sum(b['out'] for b in low),
        newusd=sum(b['cpn'] * b['out'] for b in new if b['cur'] == 'USD') / sum(b['out'] for b in new if b['cur'] == 'USD'),
        cpmin=min(c['mat'] for c in cp), cpmax=max(c['mat'] for c in cp), cur=cur)

def _cupon_par(S, T, ytm, sig, q, p):
    """Cupón que deja el convertible a la par; cero si ya con cupón cero vale más de 100."""
    if convertible(S, T, ytm, sig, q, p, 0.0)["total"] > 100: return 0.0
    return cupon_a_la_par(S, T, ytm, sig, q, p)

def calcular_opciones(bonds, ruta_cadena, ruta_term):
    cad = {float(r["strike"]): r for r in csv.DictReader(open(ruta_cadena))}
    D_ = ((DIV, T_DIV),)
    f = lambda x: float(x) if x not in ("", None) else None
    smile = [dict(K=K, c=f(cad[K]["c_iv"]), p=f(cad[K]["p_iv"]), coi=f(cad[K]["c_oi"]), poi=f(cad[K]["p_oi"]))
             for K in sorted(cad) if 100 <= K <= 150]
    term = []
    for r in csv.DictReader(open(ruta_term)):
        v = r["vencimiento"]
        a = round((datetime.date.fromisoformat(v) - datetime.date(2026, 11, 1)).days / 365.25, 3)
        term.append(dict(v=v, iv=float(r["iv_atm_pct"]), a=a))
    ej = []                                           # premio de ejercicio anticipado, árbol de 800 pasos
    for K in (115, 120, 125, 130, 135):
        rc = valuar_arbol(S0, K, T_EXP, RF, f(cad[K]["c_iv"])/100, 800, "call", D_)
        rp = valuar_arbol(S0, K, T_EXP, RF, f(cad[K]["p_iv"])/100, 800, "put", D_)
        ej.append(dict(K=float(K), c=round(100*rc.premio_ejercicio/rc.americana, 4), p=round(100*rp.premio_ejercicio/rp.americana, 4),
                       ce=round(rc.europea, 5), ca=round(rc.americana, 5), pe=round(rp.europea, 5), pa=round(rp.americana, 5)))
    iv125 = f(cad[125]["c_iv"])/100
    divexp = []                                       # el dividendo como única fuente de ejercicio anticipado
    for d in (0, 0.25, 0.75, 1.5, 2.5, 4.0):
        dv = ((d, T_DIV),) if d > 0 else ()
        r = valuar_arbol(S0, 125, T_EXP, RF, iv125, 800, "call", dv)
        divexp.append(dict(d=d, e=round(r.europea, 5), a=round(r.americana, 5), pr=round(r.premio_ejercicio, 6)))
    T, sig, q, ytm, prima, E = CV_PLAZO, CV_SIGMA, CV_Q, CV_YTM, CV_PRIMA, CV_EMISION
    cp = cupon_a_la_par(S0, T, ytm, sig, q, prima)
    cv = convertible(S0, T, ytm, sig, q, prima, cp)
    af = sum(1/(1+ytm/2)**k for k in range(1, T*2+1))
    cvd = dict(T=T, sig=sig, q=q, ytm=ytm, prima=prima, emision=E, cupon=cp*100, K=cv["precio_conversion"], ratio=cv["ratio"],
               bono=cv["bono"], opcion=cv["opcion"], pv=(ytm-cp)*E/2*af, opM=cv["opcion"]/100*E)
    tradeoff = []
    for p in range(5, 80, 2):
        c = _cupon_par(S0, T, ytm, sig, q, p/100)
        v = convertible(S0, T, ytm, sig, q, p/100, c)
        tradeoff.append(dict(p=p, op=round(v["opcion"], 4), ah=round((ytm-c)/2*100*af, 4), cpn=round(c*100, 4)))
    volsens = []
    for s in (0.20, 0.24, 0.29, 0.34, 0.40):
        c = _cupon_par(S0, T, ytm, s, q, prima)
        v = convertible(S0, T, ytm, s, q, prima, c)
        volsens.append(dict(s=s*100, cpn=round(c*100, 4), op=round(v["opcion"], 3), bo=round(v["bono"], 3)))
    acc = E/(S0*(1+prima))
    cs = call_spread(S0, T, sig, q, prima, CS_PRIMA_V, acc)
    csd = dict(K1=cs["K_compra"], K2=cs["K_venta"], acc=acc, pag=cs["prima_pagada"], cob=cs["prima_cobrada"], net=cs["costo_neto"])
    b = [x for x in bonds if x["cpn"] == 2.65][0]      # nota 2.65% 2051: objetivo de la recompra
    fondos = dict(px=b["px"], facial=b["out"]/1e6, costo=b["out"]/1e6*b["px"]/100, desc=b["out"]/1e6*(1-b["px"]/100))
    return dict(spot=S0, T=T_EXP, Tdiv=T_DIV, rf=RF, div=DIV, smile=smile, term=term, ej=ej, divexp=divexp,
                cv=cvd, tradeoff=tradeoff, volsens=volsens, cs=csd, fondos=fondos)

def calcular_garch(ruta_csv):
    """GARCH(1,1) por máxima verosimilitud sobre los rendimientos logarítmicos diarios (en %)."""
    d = list(csv.DictReader(open(ruta_csv)))
    fechas_ = [r['Date'] for r in d]; px = np.array([float(r['WMT']) for r in d])
    u = 100*np.diff(np.log(px)); fechas_ = fechas_[1:]
    def nll(th):
        w, a, b = th
        if w <= 0 or a < 0 or b < 0 or a+b >= 0.9999: return 1e10
        v = np.empty(len(u)); v[0] = u.var()
        for i in range(1, len(u)): v[i] = w + a*u[i-1]**2 + b*v[i-1]
        if np.any(v <= 0): return 1e10
        return 0.5*np.sum(np.log(v) + u**2/v)
    best, bll = None, 1e18
    for a0 in (0.05, 0.10):
        for b0 in (0.85, 0.90):
            r = minimize(nll, [u.var()*(1-a0-b0), a0, b0], method='Nelder-Mead',
                         options=dict(maxiter=20000, xatol=1e-10, fatol=1e-10))
            if r.fun < bll: bll, best = r.fun, r.x
    w, a, b = best; vl = w/(1-a-b)
    v = np.empty(len(u)); v[0] = u.var()
    for i in range(1, len(u)): v[i] = w + a*u[i-1]**2 + b*v[i-1]
    v_hoy = w + a*u[-1]**2 + b*v[-1]
    def pron(T):
        """Hull 23.6: volatilidad promedio esperada sobre T días hábiles."""
        tot = sum(vl + (a+b)**k*(v_hoy-vl) for k in range(T))
        return math.sqrt(252*tot/T)/100
    G_ = dict(w=w, a=a, b=b, ab=a+b, VL=math.sqrt(252*vl), hoy=math.sqrt(252*v_hoy), vm=math.log(0.5)/math.log(a+b), ll=-bll,
              serie=[dict(d=fechas_[i], v=round(math.sqrt(252*v[i]), 3)) for i in range(0, len(u), 5)],
              pron=[dict(a=round(T/252, 3), v=round(pron(T)*100, 3)) for T in range(5, 756, 5)],
              p31=pron(31)*100, p504=pron(504)*100, px_hoy=float(px[-1]), fecha=fechas_[-1], n=len(u))
    # el convertible bajo cada supuesto de volatilidad (GARCH contra implícitas de LSEG)
    filas = [(G_["VL"]/100, "GARCH largo plazo"), (G_["p504"]/100, "GARCH 2 anos"), (G_["p31"]/100, "GARCH al 18-dic"),
             (CV_SIGMA, "Implicita LEAPs"), (0.3189, "Implicita 18-dic")]
    esc = []
    for s, src in filas:
        c = cupon_a_la_par(S0, CV_PLAZO, CV_YTM, s, CV_Q, CV_PRIMA)
        vv = convertible(S0, CV_PLAZO, CV_YTM, s, CV_Q, CV_PRIMA, c)
        esc.append(dict(s=round(s*100, 2), src=src, cpn=round(c*100, 3), op=round(vv["opcion"], 2), bo=round(vv["bono"], 2)))
    G_["esc"] = esc
    return G_

def calcular_swaps():
    """Tres coberturas: swap de tasa, cross-currency swap y T-lock, sobre la curva bootstrapeada."""
    frn = [dict(m=m, v=v, T=T, par=tasa_par_swap(T)*100, dv=dv01(m, T)) for m, v, c, T in FRN]
    c = CCS; r = costo_todo_incluido()
    costo = r["diferencia_pb"]/1e4*r["nocional_usd"]
    ccs = dict(cad=c["cupon_cad"], usd=c["cupon_usd"], difcpn=round((c["cupon_usd"]-c["cupon_cad"])*100), difcurva=dif_curvas(),
               zusd=c["z_usd"], zcad=c["z_cad"], dif=r["diferencia_pb"], noc=r["nocional_usd"], anual=costo, total=costo*c["plazo"])
    T0, T1, monto = 2.0, 9.0, CUPON_BAJO[0][0]
    d = anualidad(T0, T1)*monto*1e-4
    esc = []
    for s in (0, 25, 50):
        for t in (-100, 0, 100):
            e = -d*(t+s); l = d*t
            esc.append(dict(t=t, s=s, e=round(e, 2), l=round(l, 2), n=round(e+l, 2)))
    tl = dict(fwd=tasa_forward(T0, T1)*100, spot=par_interp(7)*100, dv=d, esc=esc)
    curva = [dict(t=T, par=par_interp(T)*100, cero=cero(T)*100, df=df(T)) for T in (0.5, 1, 2, 3, 5, 7, 10, 20, 30)]
    return dict(frn=frn, ccs=ccs, tlock=tl, curva=curva)

def verificar(D):
    """Contrasta cifras clave con las del reporte ejecutivo. Si algo no coincide, se detiene."""
    S_, O_, G_, W_ = D['stats'], D['opt'], D['garch'], D['swaps']
    pruebas = [
        ("Emisiones vigentes",                 S_['n'],                      53,       0),
        ("Deuda vigente (miles de millones)",  S_['out']/1e9,                45.90,    0.01),
        ("Z-spread ponderado (pb)",            S_['wz'],                     38.6,     0.05),
        ("Precio de conversión",               O_['cv']['K'],                154.39,   0.005),
        ("Cupón a la par del convertible (%)", O_['cv']['cupon'],            0.918,    0.0005),
        ("Componente de opción (por 100)",     O_['cv']['opcion'],           21.562,   0.0005),
        ("VP del ahorro de cupón (M USD)",     O_['cv']['pv'],               323.4,    0.05),
        ("Costo neto del call spread (M USD)", O_['cs']['net'],              95.9,     0.05),
        ("Strike del warrant vendido",         O_['cs']['K2'],               197.62,   0.005),
        ("GARCH alfa + beta",                  G_['ab'],                     0.9878,   0.00005),
        ("GARCH volatilidad de largo plazo (%)", G_['VL'],                   22.51,    0.005),
        ("Cross-currency: diferencia que sobrevive (pb)", W_['ccs']['dif'],  34.4,     0.05),
        ("T-lock: tasa forward 7a en 2a (%)",  W_['tlock']['fwd'],           5.0019,   0.00005),
    ]
    print(f"{'Verificación contra el reporte ejecutivo':<52}{'calculado':>12}{'reporte':>10}   ")
    ok = True
    for n, x, ref, tol in pruebas:
        bien = abs(x - ref) <= tol
        ok &= bien
        print(f"{n:<52}{x:>12.4f}{ref:>10}   {'OK' if bien else 'DIFIERE'}")
    if not ok: raise SystemExit("Alguna cifra no coincide con el reporte: revisar datos de entrada.")
    print("Todas las cifras coinciden con el reporte.\n")

def plotly_js():
    """Plotly se incluye dentro del HTML para que el archivo funcione sin conexión."""
    if not os.path.exists(PLOTLY):
        print("No está assets/plotly-basic.min.js; intentando descargarlo de jsDelivr...")
        try:
            os.makedirs(os.path.dirname(PLOTLY), exist_ok=True)
            urllib.request.urlretrieve(PLOTLY_CDN, PLOTLY)
        except Exception as e:
            raise SystemExit(f"No se pudo descargar Plotly ({e}). Copia plotly-basic.min.js a {PLOTLY} "
                             "(viene en el repositorio, carpeta 06_codigo_python/assets).")
    return open(PLOTLY, encoding="utf-8").read()

bonds_, cp_ = cargar_deuda(os.path.join(DATOS, "lseg", "LSEG_Deuda_WMT.xlsx"))
_dat = dict(bonds=bonds_, stats=estadisticas(bonds_, cp_),
            opt=calcular_opciones(bonds_, os.path.join(DATOS, "dec18.csv"), os.path.join(DATOS, "vol_term.csv")),
            garch=calcular_garch(os.path.join(DATOS, "wmt_diario.csv")), swaps=calcular_swaps())
D = _dat
UST6 = ust(CV_PLAZO)                 # tasa del Tesoro a 6 años interpolada de la curva
verificar(D)

# ============================================================
# 14. PLANTILLA HTML (diseño del equipo) Y ESCRITURA
# ============================================================
import json
B=D['bonds']; S=D['stats']
b9=lambda v: f"{v/1e9:,.2f}"
b6=lambda v: f"{v/1e6:,.0f}"
CURCOL={'USD':1,'GBP':2,'CAD':3}
for b in B: b['grp']='USD' if b['cur']=='USD' else ('GBP' if b['cur']=='GBP' else ('CAD' if b['cur']=='CAD' else 'Otras'))
new=sorted([b for b in B if b['iss']=='2026-10-23'],key=lambda x:x['mat'])
low=sorted([b for b in B if b['cpn']<3],key=lambda x:x['mat'])
disc=sorted(B,key=lambda b:-(b['out']*(100-b['px'])/100))[:8]
O=D['opt']; CV=O['cv']; CS=O['cs']; FD=O['fondos']
EJC=[e for e in O['ej']]
G=D['garch']; SW=D['swaps']; CC=SW['ccs']; TL=SW['tlock']
GESC="\n".join(f'<tr><td>{e["s"]:.2f}%</td><td>{e["src"]}</td><td class="n">{e["cpn"]:.3f}%</td>'
  f'<td class="n">{e["bo"]:.2f}</td><td class="n">{e["op"]:.2f}</td></tr>' for e in G['esc'])
FRN_R="\n".join(f'<tr><td>${f["m"]:,.0f} M</td><td>{f["v"]}</td><td class="n">{f["T"]:.2f} a</td>'
  f'<td class="n">{f["par"]:.4f}%</td><td class="n">{f["dv"]:.4f}</td></tr>' for f in SW['frn'])
TL_R="\n".join(f'<tr><td class="n">{e["t"]:+d} pb</td><td class="n">{e["s"]:+d} pb</td>'
  f'<td class="n">{e["e"]:,.2f}</td><td class="n">{e["l"]:,.2f}</td>'
  f'<td class="n"><strong>{e["n"]:,.2f}</strong></td></tr>' for e in TL['esc'])
DVX=O['divexp']
VS=O['volsens']
TR=O['tradeoff']
PAY=json.dumps({'bonds':B,'stats':{k:v for k,v in S.items()},'opt':O,'garch':D['garch'],'swaps':D['swaps']},separators=(',',':'))

def rows(items,cols):
    return "\n".join("<tr>"+"".join(f'<td{c[2]}>{c[1](b)}</td>' for c in cols)+"</tr>" for b in items)
fmtd=lambda s: datetime.date.fromisoformat(s).strftime('%d %b %Y')
NC=[('Cupón',lambda b:f"{b['cpn']:.2f}%",' class="n"'),('Vencimiento',lambda b:fmtd(b['mat']),''),
    ('Moneda',lambda b:f'<span class="chip c{b["grp"]}">{b["cur"]}</span>',''),
    ('Monto USD-eq',lambda b:f"${b6(b['out'])} M",' class="n"'),('YTM',lambda b:f"{b['ytm']:.3f}%",' class="n"'),
    ('Z-spread',lambda b:f"{b['z']:.1f} pb" if b['z'] else 's/d',' class="n"'),('ISIN',lambda b:f'<code>{b["isin"]}</code>','')]
LC=[('Cupón',lambda b:f"{b['cpn']:.2f}%",' class="n"'),('Vencimiento',lambda b:fmtd(b['mat']),''),
    ('Emitido',lambda b:fmtd(b['iss']),''),('Vigente',lambda b:f"${b6(b['out'])} M",' class="n"'),
    ('Precio',lambda b:f"{b['px']:.2f}",' class="n"'),('YTM',lambda b:f"{b['ytm']:.3f}%",' class="n"')]
DC=[('Cupón',lambda b:f"{b['cpn']:.2f}%",' class="n"'),('Vencimiento',lambda b:fmtd(b['mat']),''),
    ('Precio',lambda b:f"{b['px']:.2f}",' class="n"'),('Facial',lambda b:f"${b6(b['out'])} M",' class="n"'),
    ('Mercado',lambda b:f"${b6(b['out']*b['px']/100)} M",' class="n"'),
    ('Descuento',lambda b:f"<strong>${b6(b['out']*(100-b['px'])/100)} M</strong>",' class="n"')]
DIVEXP_ROWS="\n".join(f'<tr><td>${d["d"]:.2f}</td><td class="n">{d["e"]:.5f}</td>'
  f'<td class="n">{d["a"]:.5f}</td><td class="n"><strong>{d["pr"]:.6f}</strong></td></tr>' for d in DVX)
VOLSENS_ROWS="\n".join(f'<tr><td>{v["s"]:.0f}%</td><td class="n">{v["cpn"]:.3f}%</td>'
  f'<td class="n">{v["bo"]:.2f}</td><td class="n">{v["op"]:.2f}</td></tr>' for v in VS)
th=lambda C:"".join(f'<th{c[2]}>{c[0]}</th>' for c in C)

HTML=f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Walmart · Deuda y Cobertura</title>
<script>{{PLOTLY}}</script>
<style>
:root{{color-scheme:light;--surface:#fcfcfb;--plane:#f9f9f7;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;
--grid:#e1e0d9;--axis:#c3c2b7;--line:rgba(11,11,11,.10);--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#898781;
--good:#0ca30c;--crit:#d03b3b;--warn:#fab219;--accent:#2a78d6;--chipbg:rgba(42,120,214,.10)}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{color-scheme:dark;--surface:#1a1a19;--plane:#0d0d0d;
--ink:#f0efec;--ink2:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--axis:#383835;--line:rgba(255,255,255,.10);
--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#898781;--accent:#3987e5;--chipbg:rgba(57,135,229,.16)}}}}
:root[data-theme=dark]{{color-scheme:dark;--surface:#1a1a19;--plane:#0d0d0d;--ink:#f0efec;--ink2:#c3c2b7;
--muted:#898781;--grid:#2c2c2a;--axis:#383835;--line:rgba(255,255,255,.10);--s1:#3987e5;--s2:#d95926;
--s3:#199e70;--s4:#898781;--accent:#3987e5;--chipbg:rgba(57,135,229,.16)}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--plane);color:var(--ink);font:15px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}}
.wrap{{max-width:1180px;margin:0 auto;padding:0 16px 72px}}
header{{border-bottom:1px solid var(--line);padding:32px 0 20px;margin-bottom:28px}}
.eyebrow{{color:var(--muted);font-size:12px;letter-spacing:.09em;text-transform:uppercase;font-weight:600}}
h1{{font-size:clamp(26px,4.4vw,40px);line-height:1.15;margin:10px 0 6px;letter-spacing:-.02em}}
.sub{{color:var(--ink2);font-size:16px;margin:0}}
.meta{{display:flex;flex-wrap:wrap;gap:8px 20px;margin-top:16px;color:var(--muted);font-size:13px}}
h2{{font-size:21px;margin:44px 0 6px;letter-spacing:-.01em}}
h2:first-of-type{{margin-top:12px}}
.lead{{color:var(--ink2);margin:0 0 18px;max-width:none}}
.card{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:18px}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(168px,1fr));gap:12px;margin:18px 0}}
.tile .k{{color:var(--muted);font-size:12px;font-weight:600;letter-spacing:.04em;text-transform:uppercase}}
.tile .v{{font-size:27px;font-weight:650;letter-spacing:-.02em;margin:6px 0 2px}}
.tile .d{{color:var(--ink2);font-size:13px}}
.chart{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 10px 6px;margin:14px 0}}
.note{{border-left:3px solid var(--accent);background:var(--chipbg);padding:14px 16px;border-radius:0 8px 8px 0;margin:16px 0}}
.note p{{margin:0 0 8px}} .note p:last-child{{margin:0}}
table{{width:100%;border-collapse:collapse;font-size:13.5px;font-variant-numeric:tabular-nums}}
th{{text-align:left;color:var(--muted);font-size:11px;letter-spacing:.06em;text-transform:uppercase;
padding:0 10px 9px;border-bottom:1px solid var(--axis);white-space:nowrap}}
td{{padding:9px 10px;border-bottom:1px solid var(--grid)}}
td.n,th.n{{text-align:right}} tr:last-child td{{border-bottom:0}}
code{{font:12px ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--ink2)}}
.chip{{display:inline-block;padding:1px 8px;border-radius:99px;font-size:11.5px;font-weight:650;color:#fff}}
.cUSD{{background:var(--s1)}}.cGBP{{background:var(--s2)}}.cCAD{{background:var(--s3)}}.cOtras{{background:var(--s4)}}
.scroll{{overflow-x:auto;-webkit-overflow-scrolling:touch}}
.pend li{{margin-bottom:7px}} .pend{{color:var(--ink2)}}
.tog{{position:fixed;top:14px;right:14px;z-index:9;background:var(--surface);color:var(--ink2);
border:1px solid var(--line);border-radius:99px;padding:7px 14px;font:inherit;font-size:13px;cursor:pointer}}
footer{{border-top:1px solid var(--line);margin-top:52px;padding-top:18px;color:var(--muted);font-size:13px}}
.badge{{display:inline-block;background:var(--chipbg);color:var(--accent);font-size:12px;font-weight:650;
padding:3px 10px;border-radius:99px;margin-bottom:10px}}
@media(max-width:640px){{.tile .v{{font-size:23px}}}}

html{{scroll-behavior:smooth}}
.hero{{background:linear-gradient(135deg,#0d2342 0%,#17407a 60%,#1f5aa6 100%);color:#fff;border:0;border-radius:0 0 18px 18px;padding:34px 28px 18px;margin:0 -16px 0;position:relative;overflow:hidden}}
.hero:after{{content:"";position:absolute;left:0;right:0;bottom:0;height:4px;background:linear-gradient(90deg,#f6b73c,#eb6834 55%,#1baf7a)}}
.hero .eyebrow{{color:#a9c6ea}}
.hero h1{{color:#fff;font-size:clamp(30px,5vw,48px);margin:8px 0 8px}}
.hero .tk{{color:#f6b73c;font-weight:800;margin-right:10px;letter-spacing:-.03em}}
.hero .sub{{color:#cfe0f5;max-width:60ch;font-size:15px}}
.hero-top{{display:flex;flex-wrap:wrap;justify-content:space-between;gap:20px}}
.who{{display:flex;flex-direction:column;gap:2px;text-align:right;font-size:13px;color:#cfe0f5}}
.who strong{{color:#fff;font-size:15px;margin-bottom:0}}.who strong+strong{{margin-bottom:4px}} .who .prof{{margin-top:8px;color:#a9c6ea}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.14);border-radius:12px;overflow:hidden;margin:26px 0 12px}}
.kpis div{{background:rgba(9,26,52,.55);padding:12px 14px;display:flex;flex-direction:column;gap:1px}}
.kpis span{{font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:#9fbde3;font-weight:600}}
.kpis b{{font-size:21px;letter-spacing:-.01em;font-variant-numeric:tabular-nums}} .kpis i{{font-style:normal;font-size:11.5px;color:#9fbde3}}
.hero .src{{font-size:12px;color:#9fbde3;padding-bottom:6px}}
.nav{{position:sticky;top:0;z-index:8;display:flex;gap:4px;overflow-x:auto;padding:10px 70px 10px 4px;margin:0 -16px 8px;background:color-mix(in srgb,var(--plane) 88%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);scrollbar-width:none}}
.nav::-webkit-scrollbar{{display:none}}
.nav a{{white-space:nowrap;color:var(--ink2);text-decoration:none;font-size:13px;padding:5px 11px;border-radius:99px;border:1px solid transparent}}
.nav a:hover{{background:var(--chipbg);color:var(--accent)}}
.nav a.act{{background:var(--accent);color:#fff}}
.tog{{top:9px}}
.wrap{{counter-reset:sec}}
h2[id]:not(.plain){{counter-increment:sec;scroll-margin-top:64px}}
h2[id]:not(.plain):before{{content:counter(sec,decimal-leading-zero);display:inline-block;font:600 12px ui-monospace,Menlo,monospace;color:var(--accent);background:var(--chipbg);border-radius:6px;padding:2px 7px;margin-right:10px;vertical-align:3px;letter-spacing:.04em}}
.sec-head{{display:flex;align-items:center;gap:12px;margin-top:30px}} .sec-head h2{{margin:0}}
.risks{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px;margin:18px 0}}
.risk{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px 18px;border-top:4px solid var(--axis)}}
.risk:nth-child(1){{border-top-color:var(--s2)}} .risk:nth-child(2){{border-top-color:var(--warn)}} .risk:nth-child(3){{border-top-color:var(--s3)}}
.rh{{display:flex;justify-content:space-between;align-items:center;gap:8px}}
.rh span{{font-size:11.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);font-weight:650}}
.lv{{font-style:normal;font-weight:700;font-size:13px}}
.lv.hi{{color:var(--s2)}} .lv.md{{color:#b07d00}} .lv.lo{{color:var(--s3)}}
.meter{{display:flex;gap:4px;margin:10px 0 12px}} .meter i{{flex:1;height:7px;border-radius:4px;background:var(--grid)}}
.meter i.on.hi{{background:var(--s2)}} .meter i.on.md{{background:var(--warn)}} .meter i.on.lo{{background:var(--s3)}}
.risk p{{margin:0 0 10px;color:var(--ink2);font-size:14px;line-height:1.5}}
.ins{{font-size:12.5px;color:var(--accent);font-weight:600;border-top:1px dashed var(--axis);padding-top:9px}}
.tools{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin-bottom:8px}}
.tool{{display:flex;flex-direction:column;gap:3px;background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:10px;padding:12px 14px}}
.tool b{{font-size:14.5px}} .tool span{{font-size:13px;color:var(--ink2)}}
.tool em{{font-style:normal;font-size:11px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--s3);margin-top:3px}} .tool em.pe{{color:var(--s2)}}
.ladder{{display:flex;gap:3px;margin:16px 0 4px;overflow-x:auto}}
.ladder div{{flex:1;min-width:46px;text-align:center;font-size:11px;padding:8px 2px 6px;border-radius:8px;background:var(--grid);color:var(--muted)}}
.ladder div.ig{{background:var(--chipbg);color:var(--ink2)}} .ladder div.me{{background:var(--accent);color:#fff;font-weight:700}}
.ladder small{{display:block;font-size:9.5px;opacity:.85;margin-top:3px;min-height:12px}}
@media(max-width:820px){{.kpis{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:640px){{.who{{text-align:left}}.hero{{padding:26px 18px 14px}}}}
.who em{{font-style:normal;font-variant-numeric:tabular-nums;color:#a9c6ea;margin-left:8px;font-size:12px;letter-spacing:.03em}}.hero-top{{flex-wrap:nowrap}}.hero-top>div:first-child{{flex:1 1 0;min-width:0}}.who{{flex:0 0 auto}}@media(max-width:820px){{.hero-top{{flex-wrap:wrap}}.hero-top>div:first-child{{flex-basis:100%}}}}.hero .ey1{{white-space:nowrap;overflow:hidden;text-overflow:clip;font-size:clamp(9px,1.45vw,12px);letter-spacing:.07em}}.hero .ey2{{margin-top:4px;color:#f6b73c;font-size:12px}}.who small{{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#a9c6ea;font-weight:600}}.hero h1{{margin-top:14px}}@media(max-width:640px){{.hero .ey1{{white-space:normal}}}}.cols2{{display:grid;grid-template-columns:1fr 1fr;gap:22px}}
@media(max-width:760px){{.cols2{{grid-template-columns:1fr}}}}

.bar{{display:flex;height:34px;border-radius:8px;overflow:hidden;font-weight:650;font-size:13px;color:#fff}}.bar div{{display:flex;align-items:center;justify-content:center;white-space:nowrap}}.barlab{{display:flex;justify-content:space-between;margin-top:10px;font-size:13px;color:var(--ink2)}}
</style></head><body>
<button class="tog" onclick="tog()">Tema</button>
<div class="wrap">
<header class="hero">
  <div class="eyebrow ey1">EGADE Business School · Maestría en Finanzas · Productos Derivados y Administración de Riesgos Corporativos</div>
  <div class="eyebrow ey2">{ETAPA}</div>
  <div class="hero-top">
    <div>
      <h1><span class="tk">WMT</span> Walmart Inc.</h1>
      <p class="sub">Estructura de deuda y estrategia de cobertura.</p>
    </div>
    <div class="who">
      <strong>Grupo 40</strong>
      <strong>Equipo 6</strong>
      <span>Eduardo Ayala Saldaña <em>A01192714</em></span>
      <span>Mariann Antonelli Morales Tobias <em>A01452078</em></span>
      <span>Ulises Salinas López <em>A00814787</em></span>
    </div>
  </div>
  <div class="kpis">
    <div><span>Precio WMT</span><b>${PX_DEUDA:.2f}</b><i>23-oct-2026</i></div>
    <div><span>Deuda vigente</span><b>${b9(S['out'])} B</b><i>{S['n']} emisiones</i></div>
    <div><span>Valor de mercado</span><b>${b9(S['mv'])} B</b><i>{S['discpct']:.1f}% bajo par</i></div>
    <div><span>Vida promedio</span><b>{S['wyrs']:.1f} años</b><i>ponderada por monto</i></div>
    <div><span>Cupón ponderado</span><b>{S['wcpn']:.2f}%</b><i>YTM ponderado {S['wytm']:.2f}%</i></div>
    <div><span>Volatilidad LEAPs</span><b>{CV['sig']*100:.0f}%</b><i>opciones sobre WMT</i></div>
    <div><span>Cupón del convertible</span><b>{CV['cupon']:.3f}%</b><i>vs {CV['ytm']*100:.3f}% bono recto</i></div>
    <div><span>Costo neto call spread</span><b>${CS['net']:,.1f} M</b><i>{CS['net']/CV['emision']*100:.2f}% de la emisión</i></div>
  </div>
  <div class="src"><strong>Profesor:</strong> Dr. Raymundo Díaz Robles &nbsp;·&nbsp; Deuda y precios al <strong>23 oct 2026</strong>; opciones y convertible al cierre del <strong>30 oct 2026</strong> &nbsp;·&nbsp; Fuente: LSEG Workspace</div>
</header>
<nav class="nav"><a href="#tesis">Tesis</a><a href="#escalera">Vencimientos</a><a href="#divisas">Divisas</a><a href="#emision">Emisión</a><a href="#calificacion">Calificación</a><a href="#curva">Curva</a><a href="#pared">Pared</a><a href="#manual">Manual Molson</a><a href="#recompra">Recompra</a><a href="#opciones">Opciones</a><a href="#ejercicio">Ejercicio anticipado</a><a href="#convertible">Convertible</a><a href="#estructura">Estructura</a><a href="#garch">GARCH</a><a href="#swaps">Swaps</a><a href="#pendientes">Pendientes</a></nav>

<span class="badge">Tesis</span>
<h2 id="tesis">El caso Molson Coors, pero doce veces más grande</h2>
<p class="lead">Walmart cotiza en Nasdaq como <code>WMT.O</code> con calificación de grado de inversión y deuda neta de
1.01× EBITDA. Por costo de fondeo no necesita un convertible: su spread de crédito promedio es de
{S['wz']:.0f} puntos base. Pero sí enfrenta la misma decisión que Molson Coors en 2007: refinanciar deuda barata
que vence en un entorno de tasas más alto, y cubrir el riesgo que eso genera.</p>

<div class="tiles">
  <div class="card tile"><div class="k">Deuda vigente</div><div class="v">${b9(S['out'])} B</div><div class="d">{S['n']} emisiones, valor facial</div></div>
  <div class="card tile"><div class="k">Valor de mercado</div><div class="v">${b9(S['mv'])} B</div><div class="d">{S['discpct']:.1f}% bajo par</div></div>
  <div class="card tile"><div class="k">Cupón ponderado</div><div class="v">{S['wcpn']:.2f}%</div><div class="d">costo contractual</div></div>
  <div class="card tile"><div class="k">YTM ponderado</div><div class="v">{S['wytm']:.2f}%</div><div class="d">costo marginal hoy</div></div>
  <div class="card tile"><div class="k">Brecha</div><div class="v">+{(S['wytm']-S['wcpn'])*100:.0f} pb</div><div class="d">repreciación pendiente</div></div>
  <div class="card tile"><div class="k">Vida promedio</div><div class="v">{S['wyrs']:.1f} años</div><div class="d">ponderada por monto</div></div>
</div>

<div class="note">
  <p><strong>El 23 de octubre Walmart emitió ${b9(S['newtot'])} mil millones</strong> en {S['nnew']} tramos: cuatro en
  dólares y cuatro en dólares canadienses por un total de C$5,000 millones. La fecha de emisión (23 de octubre de
  2026) es la misma del corte de precios de este análisis.</p>
  <p>El proyecto deja de ser hipotético: analizamos una operación de financiamiento real, en curso, con la
  información de mercado del día en que se colocó.</p>
</div>

<h2 id="escalera">Escalera de vencimientos</h2>
<p class="lead">Perfil de amortización por año y divisa, en millones de dólares equivalentes. No hay concentración
peligrosa: el máximo anual es inferior al 12% del total y la vida promedio es de {S['wyrs']:.1f} años.</p>
<div class="chart"><div id="g1" style="height:380px"></div></div>

<h2 id="divisas">Composición por divisa</h2>
<p class="lead">${b9(S['nonusd'])} mil millones (el {S['nonusdpct']:.1f}% de la deuda vigente) están denominados en
cuatro divisas distintas al dólar. Esa es la exposición cambiaria estructural, independiente de la operativa.</p>
<div class="chart"><div id="g2" style="height:240px"></div></div>

<h2 id="emision">La emisión del 23 de octubre de 2026</h2>
<div class="card scroll"><table><thead><tr>{th(NC)}</tr></thead><tbody>
{rows(new,NC)}
</tbody></table></div>

<div class="note">
  <p><strong>El arbitraje de fondeo, aislado.</strong> Los tramos a 2033 permiten una comparación limpia: mismo
  emisor, misma fecha de emisión, mismo vencimiento, dos divisas.</p>
  <p>El tramo en dólares rinde <strong>5.255%</strong> y el canadiense <strong>4.313%</strong>: una ventaja de
  <strong>94 puntos base</strong> por emitir en CAD. Pero los Z-spreads van al revés (35.6 pb en USD contra 70.0 pb
  en CAD), lo que implica que la curva gubernamental canadiense está unos <strong>129 pb</strong> por debajo de la
  estadounidense. La ventaja es de curva, no de crédito.</p>
  <p>Walmart no tiene operación canadiense que justifique C$5,000 millones de pasivo. Levantó barato en una divisa
  que no necesita, lo cual obliga a un <strong>cross-currency swap</strong> para regresar la exposición a dólares.
  Ese es el primero de los instrumentos de cobertura a modelar.</p>
</div>

<h2 id="calificacion">Calificación crediticia</h2>
<div class="card scroll"><table><thead><tr><th>Agencia</th><th>Tipo</th><th class="n">Calificación</th><th class="n">Outlook</th><th class="n">Vigente desde</th></tr></thead><tbody>
<tr><td>S&amp;P</td><td>Long-term Issuer Rating</td><td class="n"><strong>AA</strong></td><td class="n">Estable</td><td class="n">25-jul-1983</td></tr>
<tr><td>S&amp;P</td><td>Senior Unsecured</td><td class="n">AA</td><td class="n">s/d</td><td class="n">08-oct-1993</td></tr>
<tr><td>S&amp;P</td><td>Papel comercial</td><td class="n">A-1+</td><td class="n">s/d</td><td class="n">30-jun-1999</td></tr>
<tr><td>Moody's</td><td>Long-term Issuer Rating</td><td class="n"><strong>Aa2</strong></td><td class="n">Estable</td><td class="n">06-mar-1996</td></tr>
<tr><td>Moody's</td><td>Senior Unsecured</td><td class="n">Aa2</td><td class="n">s/d</td><td class="n">06-mar-1996</td></tr>
<tr><td>Moody's</td><td>Papel comercial</td><td class="n">P-1</td><td class="n">Estable</td><td class="n">14-oct-2015</td></tr>
<tr><td>Fitch</td><td>Senior Unsecured / IDR</td><td class="n"><strong>AA</strong></td><td class="n">s/d</td><td class="n">afirmada 02-oct-2026</td></tr>
<tr><td>Fitch</td><td>Deuda de corto plazo</td><td class="n">F1+</td><td class="n">s/d</td><td class="n">s/d</td></tr>
</tbody></table></div>
<div class="note">
  <p>Las tres agencias coinciden en el mismo escalón. <strong>Moody's bajó la calificación de Aa1 a Aa2 el 6 de
  marzo de 1996 y no la ha movido desde entonces; S&amp;P mantiene AA desde 1983.</strong> Treinta años en el
  mismo nivel, con afirmaciones de junio y octubre de 2026.</p>
  <p>Una empresa cuya calificación no se mueve en tres décadas no tiene un problema de crédito que resolver con
  ingeniería financiera. El Z-spread promedio de 38.6 pb la coloca exactamente un escalón por debajo del
  soberano estadounidense, calificado AA+ por Fitch y S&amp;P y Aa1 por Moody's.</p>
</div>

<h2 id="curva">Curva de rendimiento de la deuda de Walmart</h2>
<p class="lead">Cada punto es una emisión vigente: rendimiento al vencimiento contra años restantes, al 23 de
octubre de 2026. El tamaño refleja el monto vigente. La separación vertical entre los puntos azules y los verdes
es el diferencial de curva entre Estados Unidos y Canadá.</p>
<div class="chart"><div id="g3" style="height:420px"></div></div>

<h2 id="pared">La pared de refinanciamiento</h2>
<p class="lead">Siete emisiones con cupón inferior al 3% (${b9(S['lowtot'])} mil millones al {S['lowcpn']:.2f}%
promedio) fueron colocadas entre 2017 y 2021. Refinanciarlas al {S['newusd']:.2f}% de la emisión reciente en
dólares implica un costo incremental del orden de {(S['newusd']-S['lowcpn'])*S['lowtot']/100/1e6:,.0f} millones de
dólares anuales.</p>
<div class="card scroll"><table><thead><tr>{th(LC)}</tr></thead><tbody>
{rows(low,LC)}
</tbody></table></div>
<p class="lead" style="margin-top:14px">Molson Coors ejecutó toda su estructura (convertible, call spread y
T-lock) para ahorrar cerca de 15 millones de dólares anuales. La exposición de Walmart es un orden de magnitud
mayor.</p>

<h2 id="manual">Walmart ya ejecuta el manual de Molson Coors</h2>
<p class="lead">De ${b9(S['issd'])} mil millones emitidos históricamente, quedan vigentes ${b9(S['out'])} mil
millones: <strong>${b9(S['ret'])} mil millones, el {S['retpct']:.1f}%, ya fueron retirados</strong>. Y el patrón de
qué se retira no es aleatorio.</p>
<div class="chart"><div id="g4" style="height:400px"></div></div>
<div class="note">
  <p>Entre las emisiones anteriores a 2022, Walmart ha retirado cerca de la <strong>mitad</strong> del papel con
  cupón superior al 3% (50.9% en el rango de 3% a 4.5%, y 48.4% por encima de 4.5%), mientras que el papel con
  cupón inferior al 3% permanece prácticamente intacto: <strong>solo 7.2% retirado</strong>.</p>
  <p>Es exactamente el uso de fondos del caso Molson Coors, que destinó $465 millones a recomprar sus notas al
  6.375%. Walmart lleva años aplicando la misma lógica. Nuestra propuesta no inventa una estrategia: extiende una
  que la empresa ya demostró preferir.</p>
</div>

<h2 id="recompra">Oportunidad de recompra</h2>
<p class="lead">Con tasas al alza, la deuda de cupón bajo cotiza muy por debajo de par. Recomprarla retira valor
facial a descuento: ${b9(S['disc'])} mil millones de diferencia entre el facial vigente y su valor de mercado.</p>
<div class="chart"><div id="g5" style="height:380px"></div></div>
<div class="card scroll" style="margin-top:14px"><table><thead><tr>{th(DC)}</tr></thead><tbody>
{rows(disc,DC)}
</tbody></table></div>

<h2 id="opciones">Opciones sobre WMT</h2>
<p class="lead">Cadena del vencimiento 18 de diciembre de 2026, el mismo que cruza el ex-dividendo del 11 de
diciembre. Todas las volatilidades y griegas son del precio medio, no del último operado.</p>

<div class="note">
  <p><strong>Un hallazgo de convención.</strong> Las primeras volatilidades implícitas calculadas con el plazo
  medido desde el último trade salieron <strong>72 puntos base por debajo</strong> de las de LSEG, de forma
  sistemática en calls y en puts. Un sesgo del mismo signo en ambos tipos descarta el dividendo, que mueve calls
  y puts en direcciones opuestas.</p>
  <p>Calibrando a la inversa: <strong>LSEG mide el plazo desde la fecha calendario corriente</strong>, no desde
  la última operación. Con 47 días el error medio cae a 20 pb y el sesgo desaparece. Es el mismo tipo de
  diferencia que encontramos en TradingView, que usa días hábiles sobre año calendario.</p>
</div>

<h2 style="font-size:17px">Sonrisa de volatilidad</h2>
<div class="note">
  <p><strong>Fechas de corte y tasas.</strong> El análisis de deuda (bonos, curva, recompra) usa precios del 23 de octubre de 2026, con WMT a ${PX_DEUDA:.2f}. La cadena de opciones y el convertible usan el cierre del 30 de octubre, con WMT a <strong>${O['spot']:.2f}</strong>.</p>
  <p>La tasa libre de riesgo depende del plazo: las opciones a {O['T']*365:.0f} días usan <strong>{O['rf']*100:.2f}%</strong> y el convertible a {CV['T']} años usa <strong>{UST6*100:.2f}%</strong>, ambas de la curva del Tesoro (TRADEWEB). No son supuestos contradictorios, son puntos distintos de la misma curva.</p>
</div>
<div class="chart"><div id="g6" style="height:360px"></div></div>
<p class="lead">El mínimo está en el strike 130 y la curva es plana entre 115 y 150, pero se empina con fuerza
por debajo de 110. Es sesgo bajista: la protección contra caídas fuertes cotiza con prima. Por debajo de 100 y
por encima de 150 las cotizaciones dejan de ser informativas (LSEG reporta implícitas de 57% a 124% con bid en
cero) y quedan excluidas del análisis.</p>

<h2 style="font-size:17px">Estructura temporal</h2>
<div class="chart"><div id="g7" style="height:330px"></div></div>
<div class="note">
  <p>El vencimiento del 20 de noviembre cotiza a <strong>41.0%</strong>, unos doce puntos por encima del resto:
  el reporte trimestral de Walmart cae dentro de esa ventana. A partir de enero la curva se aplana en
  <strong>29%</strong> y se mantiene ahí tres años.</p>
  <p>Consecuencia directa: la volatilidad para valuar el convertible es la de los LEAPs, no la del mes cercano.
  Usar 41% sobrevaluaría la opción de conversión y daría vuelta a la conclusión.</p>
</div>

<h2 id="ejercicio">Ejercicio anticipado</h2>
<p class="lead">Premio de la opción americana sobre la europea, como porcentaje del precio, calculado con árbol
Cox-Ross-Rubinstein de 800 pasos y dividendo discreto.</p>
<div class="chart"><div id="g8" style="height:330px"></div></div>

<h2 style="font-size:17px">El dividendo es la única fuente de ejercicio anticipado en una call</h2>
<p class="lead">Experimento controlado sobre la call de strike 125. Todo idéntico, solo cambia el dividendo.</p>
<div class="card scroll"><table><thead><tr><th>Dividendo</th><th class="n">Europea</th><th class="n">Americana</th><th class="n">Premio</th></tr></thead><tbody>
{DIVEXP_ROWS}
</tbody></table></div>
<p class="lead" style="margin-top:14px">Con dividendo cero el premio es <strong>exactamente cero</strong>: la
call americana vale lo mismo que la europea, que es el resultado de Merton de 1973. Con el dividendo real
aparece y crece de forma monótona. En la actividad previa de árboles binomiales los ocho subyacentes tenían
q&nbsp;=&nbsp;0, así que la igualdad era un resultado teórico que se afirmaba sin poder exhibirlo. Aquí se
demuestra con datos de mercado.</p>

<h2 id="convertible">El convertible propuesto</h2>
<p class="lead">Emisión de {CV['emision']:,.0f} millones a {CV['T']} años con prima de conversión de {CV['prima']:.0%}, replicando la estructura
de Molson Coors de junio de 2007. Insumos al 30 de octubre de 2026: WMT ${O['spot']:.2f}, volatilidad {CV['sig']*100:.0f}%, tasa libre de riesgo a {CV['T']} años {UST6*100:.2f}%.</p>
<div class="tiles">
  <div class="card tile"><div class="k">Precio de conversión</div><div class="v">${CV['K']:.2f}</div><div class="d">{CV['ratio']:.4f} acciones por 100 nom.</div></div>
  <div class="card tile"><div class="k">Cupón a la par</div><div class="v">{CV['cupon']:.3f}%</div><div class="d">deuda recta: {CV['ytm']*100:.3f}%</div></div>
  <div class="card tile"><div class="k">Ahorro aparente</div><div class="v">{(CV["ytm"]*100-CV["cupon"])*100:.0f} pb</div><div class="d">${(CV["ytm"]*100-CV["cupon"])/100*CV["emision"]:,.1f} M al año</div></div>
  <div class="card tile"><div class="k">Costo neto call spread</div><div class="v">${CS['net']:,.1f} M</div><div class="d">{CS["net"]/CV["emision"]*100:.2f}% de la emisión</div></div>
</div>

<div class="card" style="margin-top:14px">
  <div class="bar"><div style="background:var(--s1);width:{CV['bono']:.2f}%">{CV['bono']:.2f}</div><div style="background:var(--s3);width:{CV["opcion"]:.2f}%">{CV['opcion']:.2f}</div></div>
  <div class="barlab"><span>Bono recto <b>{CV['bono']:.2f}</b></span><span><b>{CV['opcion']:.2f}</b> Opción de conversión</span></div>
</div>

<h2 style="font-size:17px">No hay free lunch</h2>
<div class="card scroll"><table><thead><tr><th>Concepto</th><th class="n">Millones USD</th></tr></thead><tbody>
<tr><td>Valor presente del ahorro de cupón</td><td class="n">${CV['pv']:,.1f}</td></tr>
<tr><td>Valor de la opción entregada al tenedor</td><td class="n">${CV['opM']:,.1f}</td></tr>
<tr><td><strong>Diferencia</strong></td><td class="n"><strong>${abs(CV["pv"]-CV["opM"]):,.1f}</strong></td></tr>
</tbody></table></div>
<div class="chart"><div id="g9" style="height:340px"></div></div>
<div class="note">
  <p>Las dos curvas se superponen en todo el rango relevante. El convertible cotiza a la par precisamente porque
  el descuento de cupón que recibe el emisor equivale, peso por peso, al valor de la opción que entrega.
  <strong>El emisor no ahorra: vende opcionalidad a precio de mercado y la cobra en forma de cupón reducido.</strong></p>
  <p>Se separan por debajo de <strong>14.5%</strong> de prima, y la separación también tiene sentido económico:
  ahí la opción vale tanto que ni con cupón cero el instrumento bajaría a la par. Existe una prima mínima por
  debajo de la cual una emisión a la par es imposible.</p>
</div>

<h2 style="font-size:17px">Sensibilidad a la volatilidad</h2>
<p class="lead">El 29% viene de LEAPs a 2.2 años. Extrapolarlo a seis es un supuesto, no un dato, y pesa.</p>
<div class="card scroll"><table><thead><tr><th>Volatilidad</th><th class="n">Cupón a la par</th><th class="n">Bono recto</th><th class="n">Opción</th></tr></thead><tbody>
{VOLSENS_ROWS}
</tbody></table></div>

<h2 id="estructura">La estructura completa</h2>
<div class="cols2">
<div>
<h2 style="font-size:17px;margin-top:0">Call spread</h2>
<div class="card scroll"><table><tbody>
<tr><td>Strike comprado (prima 25%)</td><td class="n">${CS['K1']:.2f}</td></tr>
<tr><td>Strike vendido (prima 60%)</td><td class="n">${CS['K2']:.2f}</td></tr>
<tr><td>Acciones subyacentes</td><td class="n">{CS['acc']:.2f} M</td></tr>
<tr><td>Prima pagada</td><td class="n">${CS['pag']:,.1f} M</td></tr>
<tr><td>Prima cobrada</td><td class="n">${CS['cob']:,.1f} M</td></tr>
<tr><td><strong>Costo neto</strong></td><td class="n"><strong>${CS['net']:,.1f} M</strong></td></tr>
</tbody></table></div>
<p class="lead" style="margin-top:12px;font-size:14px">Molson Coors pagó 8.6% de su emisión; Walmart sale en
{CS["net"]/CV["emision"]*100:.2f}%, más barato porque su sesgo de volatilidad es menos pronunciado. La estructura eleva la prima efectiva
de 25% a 60%: no hay dilución mientras la acción no supere ${CS['K2']:.2f}.</p>
</div>
<div>
<h2 style="font-size:17px;margin-top:0">Uso de fondos</h2>
<div class="card scroll"><table><tbody>
<tr><td>Objetivo</td><td class="n">Nota 2.65% de 2051</td></tr>
<tr><td>Precio de mercado</td><td class="n">{FD['px']:.3f}</td></tr>
<tr><td>Valor facial a retirar</td><td class="n">${FD['facial']:,.1f} M</td></tr>
<tr><td>Costo de la recompra</td><td class="n">${FD['costo']:,.1f} M</td></tr>
<tr><td><strong>Descuento capturado</strong></td><td class="n"><strong>${FD['desc']:,.1f} M</strong></td></tr>
<tr><td>Facial retirado por dólar</td><td class="n">{100/FD["px"]:.2f}</td></tr>
</tbody></table></div>
<p class="lead" style="margin-top:12px;font-size:14px">Cada dólar de efectivo retira {100/FD["px"]:.2f} dólares de valor
facial. Es la pieza que da sentido económico a la estructura más allá del arbitraje de cupón, y es el paralelo
exacto del uso de fondos de Molson Coors, que destinó $465 M a recomprar sus notas al 6.375%.</p>
</div>
</div>

<h2 id="garch">Pronóstico de volatilidad con GARCH</h2>
<p class="lead">Toda la valoración anterior usa volatilidad implícita, que es el precio que el mercado cobra hoy
por la incertidumbre futura. El GARCH responde otra pregunta: dado el comportamiento histórico de la acción,
cuánta volatilidad cabe esperar. Estimado por máxima verosimilitud sobre {G["n"]:,} observaciones diarias, de {G["serie"][0]["d"]} a
{G["fecha"]}.</p>

<div class="tiles">
  <div class="card tile"><div class="k" style="text-transform:none">α + β</div><div class="v">{G["ab"]:.4f}</div><div class="d">persistencia del choque</div></div>
  <div class="card tile"><div class="k">Vida media</div><div class="v">{G["vm"]:.0f} d</div><div class="d">para disiparse a la mitad</div></div>
  <div class="card tile"><div class="k">Largo plazo</div><div class="v">{G["VL"]:.2f}%</div><div class="d">volatilidad del modelo</div></div>
  <div class="card tile"><div class="k">Condicional hoy</div><div class="v">{G["hoy"]:.2f}%</div><div class="d">{G["fecha"]}</div></div>
</div>

<div class="chart"><div id="g10" style="height:340px"></div></div>
<p class="lead">La volatilidad condicional sube y baja alrededor de su nivel de largo plazo, pero con
α&nbsp;+&nbsp;β&nbsp;=&nbsp;{G["ab"]:.4f} la reversión es lenta: un choque tarda {G["vm"]:.0f} días en disiparse a la mitad.</p>

<div class="chart"><div id="g11" style="height:340px"></div></div>
<div class="note">
  <p>El pronóstico parte de {G["hoy"]:.2f}% y converge hacia {G["VL"]:.2f}%. En los dos horizontes que importan, la volatilidad
  implícita cotiza <strong>alrededor de 25 % por encima</strong> del modelo: {G["p31"]:.2f}% contra 31.89 % al vencimiento
  de diciembre, y {G["p504"]:.2f}% contra 29.00 % en los LEAPs.</p>
  <p>Esa brecha es la <strong>prima de riesgo de volatilidad</strong>: el mercado cobra más de lo que la serie
  histórica justifica. Es el estado normal en opciones sobre acciones, no una anomalía.</p>
</div>

<h2 style="font-size:17px">Qué cambia en el convertible</h2>
<div class="card scroll"><table><thead><tr><th>Volatilidad</th><th>Origen</th><th class="n">Cupón a la par</th><th class="n">Bono</th><th class="n">Opción</th></tr></thead><tbody>
{GESC}
</tbody></table></div>
<p class="lead" style="margin-top:14px"><strong>El cupón a la par casi se duplica</strong> al sustituir la
implícita por el pronóstico del modelo. No invalida la demostración de que no hay free lunch (esa es una
identidad y se sostiene con cualquier volatilidad), pero sí cambia la magnitud del supuesto ahorro.</p>
<p class="lead">La decisión de usar la implícita es económica, no estadística: para emitir hay que valuar al
precio al que el mercado compra, no al que un modelo considera justo. Si la administración creyera en el
pronóstico del GARCH, la conclusión sería que vender esa opcionalidad es buen negocio, porque se cobraría por
ella más de lo que vale. Es un argumento a favor de emitir, pero por una razón distinta a la del ahorro de cupón.</p>

<h2 id="swaps">Cobertura con swaps</h2>
<p class="lead">El reporte recomienda tres coberturas. Esta sección las valúa sobre la curva del Tesoro
descontada por bootstrapping.</p>

<h2 style="font-size:17px">El programa de cobertura que ya existe</h2>
<p class="lead">Antes de proponer coberturas conviene documentar las contratadas. La nota 7 del 10-K del
ejercicio fiscal 2026, en millones de dólares.</p>
<div class="card scroll"><table><thead><tr><th>Instrumento</th><th class="n">Nocional ene-2026</th><th class="n">Valor razonable</th><th class="n">Nocional ene-2025</th></tr></thead><tbody>
<tr><td>IRS: recibe fija, paga variable <span style="color:var(--muted)">(valor razonable)</span></td><td class="n">4,771</td><td class="n">(411)</td><td class="n">4,771</td></tr>
<tr><td>Cross-currency: recibe fija, paga fija <span style="color:var(--muted)">(flujo de efectivo)</span></td><td class="n">6,020</td><td class="n">(920)</td><td class="n">5,452</td></tr>
<tr><td><strong>Total</strong></td><td class="n"><strong>10,791</strong></td><td class="n"><strong>(1,331)</strong></td><td class="n"><strong>10,223</strong></td></tr>
</tbody></table></div>
<div class="note">
  <p><strong>La dirección es contraintuitiva.</strong> Walmart recibe fija y paga variable: convierte deuda de
  tasa fija en flotante. No busca fijar su costo sino mantener una mezcla deliberada entre ambos tipos de tasa.</p>
  <p><strong>Y los swaps vencen donde está la deuda barata.</strong> La nota precisa que vencen entre septiembre
  de 2028 y septiembre de 2031. Las únicas emisiones que vencen en esos meses exactos son la nota al 1.500 % del
  22 de septiembre de 2028 y la del 1.800 % del 22 de septiembre de 2031, ambas de la colocación de 2021.
  Walmart convirtió su papel más barato en flotante poco antes del alza de tasas, y el valor razonable negativo
  de 411 millones es la factura.</p>
  <p><strong>La colocación canadiense todavía no aparece.</strong> El balance es al 31 de enero de 2026 y la
  emisión fue el 23 de octubre, nueve meses después. Pero un programa permanente de 6,020 millones confirma que
  swapear la deuda no denominada en dólares es práctica habitual: el diferencial de 90 pb se devuelve por
  política propia, de modo que la emisión canadiense no pudo responder a un motivo de costo.</p>
</div>

<h2 style="font-size:17px">Swap de tasa sobre las notas flotantes</h2>
<p class="lead">Un swap en el que Walmart paga fijo y recibe flotante convertiría estas dos notas en deuda de
tasa fija. Va en sentido inverso a su política vigente, así que se valúa por completitud y con esa salvedad.</p>
<div class="card scroll"><table><thead><tr><th>Monto</th><th>Vence</th><th class="n">Plazo</th><th class="n">Tasa par del swap</th><th class="n">DV01</th></tr></thead><tbody>
{FRN_R}
</tbody></table></div>
<p class="lead" style="margin-top:14px">Cien puntos base mueven el paquete <strong>$11.87 millones</strong>.
Pero la nota de abril de 2027 tiene menos de seis meses de vida y un DV01 de 0.0367: swapearla no compensa el
costo de ejecución. La cobertura que vale la pena es la de 2029.</p>

<h2 style="font-size:17px">Cross-currency swap: el arbitraje que no sobrevive</h2>
<div class="card scroll"><table><tbody>
<tr><td>Diferencia de cupón entre los tramos gemelos a 2033</td><td class="n">{CC["difcpn"]:.0f} pb a favor de CAD</td></tr>
<tr><td>Curva gubernamental canadiense por debajo de la estadounidense</td><td class="n">{CC["difcurva"]:.1f} pb</td></tr>
<tr><td>Emisión directa en dólares</td><td class="n">curva USD + {CC["zusd"]:.1f} pb</td></tr>
<tr><td>Emisión en canadienses, una vez swapeada</td><td class="n">curva USD + {CC["zcad"]:.1f} pb</td></tr>
<tr><td><strong>Diferencia que sobrevive al swap</strong></td><td class="n"><strong>{CC["dif"]:.1f} pb en contra de CAD</strong></td></tr>
<tr><td>Costo anual sobre US${CC["noc"]:,.1f} M</td><td class="n">${CC["anual"]:,.2f} M</td></tr>
<tr><td>Costo a siete años</td><td class="n">${CC["total"]:,.1f} M</td></tr>
</tbody></table></div>
<div class="note">
  <p><strong>El diferencial de 90 puntos base viene de la curva, no del crédito.</strong> El cross-currency swap
  intercambia una curva por la otra y devuelve ese diferencial completo. Lo que sobrevive es el spread de
  crédito, que es {CC["dif"]:.1f} puntos base más ancho en canadienses.</p>
  <p>Después de cubrir, <strong>la ruta canadiense resulta más cara que emitir directamente en dólares</strong>.
  Es el resultado de paridad cubierta de tasas: el costo de fondeo no se arbitra entre divisas porque el mercado
  de swaps lo cobra.</p>
  <p>Quedan tres explicaciones para la decisión de Walmart, y ninguna es el ahorro de cupón: diversificación de
  la base de inversionistas, capacidad de mercado (colocar 6,569 millones de golpe solo en dólares habría
  ampliado el spread de la propia emisión) o un basis cruzado favorable. El basis tendría que aportar al menos
  {CC["dif"]:.1f} puntos base para dejar indiferentes las dos rutas. El basis CAD/USD cotizado en LSEG el 6 de noviembre va de -14.8 pb a 3 años a -5.1 pb a 10 años; a 7 años es de -8.9 pb. Aun si jugara a favor de Walmart, quedarían {CC["dif"]-8.9:.1f} pb en contra de la ruta canadiense, así que la conclusión no se revierte.</p>
</div>

<h2 style="font-size:17px">T-lock y riesgo de base</h2>
<p class="lead">Tasa forward a siete años dentro de dos: <strong>{TL["fwd"]:.4f}%</strong>, contra {TL["spot"]:.4f}% spot. Prima
forward de {(TL["fwd"]-TL["spot"])*100:.1f} puntos base. Montos en millones de dólares sobre un nocional de $1,250 M.</p>
<div class="card scroll"><table><thead><tr><th class="n">Tesoro</th><th class="n">Spread</th><th class="n">Costo emisión</th><th class="n">T-lock</th><th class="n">Neto</th></tr></thead><tbody>
{TL_R}
</tbody></table></div>
<div class="note">
  <p>Contra movimientos del Tesoro la cobertura es exacta: con el spread quieto, el neto es cero en los tres
  escenarios. <strong>Pero el T-lock fija la tasa del Tesoro, no el costo de fondeo de Walmart.</strong> Cada
  25 puntos base de ampliación del spread cuestan ${TL["dv"]*25:,.2f} millones sin compensación.</p>
  <p>El peor escenario no es que suban las tasas, sino que <strong>bajen mientras el crédito se amplía</strong>:
  ahí el T-lock pierde y el spread cobra al mismo tiempo. Es exactamente el riesgo que corrió Molson Coors, y la
  razón por la que su T-lock liquidó con una ganancia de 1.4 millones en lugar de cubrir el costo total de su
  recompra.</p>
</div>

<h2 id="pendientes">Pendientes</h2>
<ul class="pend">
  <li><strong>Condiciones reales del swap cruzado de Walmart.</strong> Las cotizaciones de LSEG son de mercado; el basis que Walmart obtuvo en su propia operación no es público.</li>
</ul>

<h2 class="plain">Resueltos desde el avance</h2>
<ul class="pend">
  <li>Cadena de opciones de WMT con volatilidad implícita y las cinco griegas, vencimiento 18-dic-2026.</li>
  <li>Curva del Tesoro completa, trece plazos de 1 mes a 30 años, fuente TRADEWEB.</li>
  <li>Valoración del convertible, call spread y uso de fondos.</li>
  <li>Verificación del gasto financiero: la razón de cobertura LTM de LSEG es 12.73x sobre EBIT, consistente con
  la historia. El 26x de un trimestre aislado era ruido del dato trimestral.</li>
  <li>Calificaciones de las tres agencias, con outlook y fecha de vigencia.</li>
  <li>Nota 7 del 10-K: nocionales y valor razonable del programa de derivados.</li>
  <li>Serie diaria de seis años y estimación GARCH(1,1).</li>
  <li>Valuación de las tres coberturas con swaps.</li>
  <li>Basis cruzado CAD/USD de LSEG (6-nov-2026): -14.8 pb a 3 años, -11.6 a 5, -8.9 a 7 y -5.1 a 10. No revierte la conclusión sobre la emisión canadiense.</li>
  <li>Corrida de emisiones vencidas en 2026 (hoja Inactive Bonds de LSEG): euro 2.550% (8 de abril), USD 4.000% (15 de abril), USD 3.050% (8 de julio), USD 5.502% con put (15 de julio) y USD 1.050% (17 de septiembre), cinco bonos por 4,975 millones según el monto emitido en LSEG.</li>
</ul>

<footer>
  <p>Fuente: LSEG Workspace, Government and Corporate Bonds Advanced Search y Company Fundamentals, corte al 23 de
  octubre de 2026. Precio de la acción al cierre del 23 de octubre de 2026: USD 119.89. Papel comercial: {S['ncp']}
  emisiones vigentes con vencimientos entre el 27 de octubre de 2026 y el 7 de enero de 2027, excluidas del
  análisis de notas. {S['ncall']} de las {S['n']} emisiones son redimibles anticipadamente (${b9(S['callamt'])} B).</p>
  <p>Documento académico elaborado por el Equipo 6 con fines didácticos. No constituye recomendación de inversión
  ni representa a Walmart Inc.</p>
</footer>
</div>
<script>
const DATA={PAY};
const V=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const GC={{USD:'--s1',GBP:'--s2',CAD:'--s3',Otras:'--s4'}};
const money=v=>'$'+(v/1e6).toLocaleString('en-US',{{maximumFractionDigits:0}})+' M';
function base(extra){{return Object.assign({{
  paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',
  font:{{family:'system-ui,-apple-system,sans-serif',size:12,color:V('--ink2')}},
  margin:{{l:58,r:18,t:16,b:46}},hovermode:'closest',
  hoverlabel:{{bgcolor:V('--surface'),bordercolor:V('--line'),font:{{color:V('--ink'),size:12.5}}}},
  xaxis:{{gridcolor:'rgba(0,0,0,0)',linecolor:V('--axis'),zeroline:false,tickfont:{{color:V('--muted')}}}},
  yaxis:{{gridcolor:V('--grid'),linecolor:'rgba(0,0,0,0)',zeroline:false,tickfont:{{color:V('--muted')}}}},
  legend:{{orientation:'h',y:1.14,x:0,traceorder:'normal',font:{{color:V('--ink2')}}}}
}},extra||{{}});}}
const CFG={{displayModeBar:false,responsive:true}};
function draw(){{
 const B=DATA.bonds, ORD=['USD','GBP','CAD','Otras'];
 // 1 maturity ladder
 const yrs=[...new Set(B.map(b=>+b.mat.slice(0,4)))].sort();
 Plotly.react('g1',ORD.map(g=>({{type:'bar',name:g,x:yrs,
   y:yrs.map(y=>B.filter(b=>+b.mat.slice(0,4)===y&&b.grp===g).reduce((s,b)=>s+b.out,0)/1e6),
   marker:{{color:V(GC[g]),line:{{width:2,color:V('--surface')}}}},
   hovertemplate:'<b>%{{x}}</b> · '+g+'<br>%{{y:,.0f}} M USD-eq<extra></extra>'}})),
  base({{barmode:'stack',yaxis:{{gridcolor:V('--grid'),zeroline:false,ticksuffix:' M',
   tickfont:{{color:V('--muted')}},linecolor:'rgba(0,0,0,0)'}},
   xaxis:{{type:'category',linecolor:V('--axis'),tickfont:{{color:V('--muted')}},gridcolor:'rgba(0,0,0,0)'}}}}),CFG);
 // 2 currency
 const cs=ORD.map(g=>[g,B.filter(b=>b.grp===g).reduce((s,b)=>s+b.out,0)]).sort((a,b)=>a[1]-b[1]);
 Plotly.react('g2',[{{type:'bar',orientation:'h',x:cs.map(c=>c[1]/1e6),y:cs.map(c=>c[0]),
   marker:{{color:cs.map(c=>V(GC[c[0]]))}},width:.62,
   text:cs.map(c=>money(c[1])),textposition:'auto',outsidetextfont:{{color:V('--ink2'),size:12}},insidetextfont:{{color:'#fff',size:12}},cliponaxis:false,
   hovertemplate:'%{{y}}: %{{x:,.0f}} M<extra></extra>'}}],
  base({{showlegend:false,margin:{{l:62,r:110,t:8,b:34}},
   xaxis:{{visible:false}},yaxis:{{gridcolor:'rgba(0,0,0,0)',tickfont:{{color:V('--ink2'),size:13}}}}}}),CFG);
 // 3 yield curve
 const sz=v=>8+26*Math.sqrt(v/3e9);
 Plotly.react('g3',ORD.map(g=>{{const s=B.filter(b=>b.grp===g);return {{type:'scatter',mode:'markers',name:g,
   x:s.map(b=>b.yrs),y:s.map(b=>b.ytm),
   marker:{{color:V(GC[g]),size:s.map(b=>sz(b.out)),line:{{width:2,color:V('--surface')}},opacity:.92}},
   customdata:s.map(b=>[b.cpn,b.mat,b.out/1e6,b.z||0]),
   hovertemplate:'<b>'+g+' %{{customdata[0]:.2f}}%</b><br>vence %{{customdata[1]}}<br>YTM %{{y:.3f}}%<br>'+
   'Z-spread %{{customdata[3]:.1f}} pb<br>%{{customdata[2]:,.0f}} M vigente<extra></extra>'}};}}),
  base({{xaxis:{{title:{{text:'Años al vencimiento',font:{{color:V('--muted'),size:12}}}},
    gridcolor:V('--grid'),linecolor:V('--axis'),tickfont:{{color:V('--muted')}},zeroline:false}},
   yaxis:{{title:{{text:'Rendimiento al vencimiento',font:{{color:V('--muted'),size:12}}}},
    ticksuffix:'%',gridcolor:V('--grid'),tickfont:{{color:V('--muted')}},zeroline:false,linecolor:'rgba(0,0,0,0)'}},
   annotations:[{{x:6.99,y:5.255,ax:46,ay:-34,text:'USD 2033<br>5.255%',font:{{color:V('--ink2'),size:11}},
     arrowcolor:V('--axis'),arrowwidth:1.5,arrowhead:0}},
    {{x:6.99,y:4.313,ax:46,ay:34,text:'CAD 2033<br>4.313%',font:{{color:V('--ink2'),size:11}},
     arrowcolor:V('--axis'),arrowwidth:1.5,arrowhead:0}}]}}),CFG);
 // 4 buybacks
 const pre=B.filter(b=>b.iss<'2022-01-01'), pos=B.filter(b=>b.iss>='2022-01-01');
 const mk=(s,c)=>({{type:'scatter',mode:'markers',x:s.map(b=>b.cpn),y:s.map(b=>b.ret),
   marker:{{color:V(c),size:s.map(b=>sz(b.issd)),line:{{width:2,color:V('--surface')}},opacity:.9}},
   customdata:s.map(b=>[b.mat,b.issd/1e6,b.out/1e6]),
   hovertemplate:'<b>%{{x:.2f}}%</b> · vence %{{customdata[0]}}<br>emitido %{{customdata[1]:,.0f}} M → '+
   'vigente %{{customdata[2]:,.0f}} M<br>retirado %{{y:.0f}}%<extra></extra>'}});
 Plotly.react('g4',[Object.assign(mk(pre,'--s1'),{{name:'Emitidos antes de 2022'}}),
                    Object.assign(mk(pos,'--s4'),{{name:'Emitidos 2022 en adelante'}})],
  base({{xaxis:{{title:{{text:'Cupón',font:{{color:V('--muted'),size:12}}}},ticksuffix:'%',
    gridcolor:V('--grid'),linecolor:V('--axis'),tickfont:{{color:V('--muted')}},zeroline:false}},
   yaxis:{{title:{{text:'Porcentaje del monto emitido ya retirado',font:{{color:V('--muted'),size:12}}}},
    ticksuffix:'%',range:[-6,78],gridcolor:V('--grid'),tickfont:{{color:V('--muted')}},zeroline:false,
    linecolor:'rgba(0,0,0,0)'}}}}),CFG);
 // 5 price vs par
 const s5=B.slice().sort((a,b)=>a.yrs-b.yrs);
 Plotly.react('g5',ORD.map(g=>{{const s=s5.filter(b=>b.grp===g);return {{type:'scatter',mode:'markers',name:g,
   x:s.map(b=>b.yrs),y:s.map(b=>b.px),
   marker:{{color:V(GC[g]),size:s.map(b=>sz(b.out)),line:{{width:2,color:V('--surface')}},opacity:.92}},
   customdata:s.map(b=>[b.cpn,b.mat,b.out*(100-b.px)/100/1e6]),
   hovertemplate:'<b>'+g+' %{{customdata[0]:.2f}}%</b><br>vence %{{customdata[1]}}<br>precio %{{y:.2f}}<br>'+
   'descuento %{{customdata[2]:,.0f}} M<extra></extra>'}};}}),
  base({{shapes:[{{type:'line',x0:0,x1:31,y0:100,y1:100,line:{{color:V('--axis'),width:1.5,dash:'dot'}}}}],
   annotations:[{{x:30,y:100,yanchor:'bottom',xanchor:'right',text:'par',showarrow:false,
    font:{{color:V('--muted'),size:11}}}}],
   xaxis:{{title:{{text:'Años al vencimiento',font:{{color:V('--muted'),size:12}}}},
    gridcolor:V('--grid'),linecolor:V('--axis'),tickfont:{{color:V('--muted')}},zeroline:false}},
   yaxis:{{title:{{text:'Precio limpio',font:{{color:V('--muted'),size:12}}}},
    gridcolor:V('--grid'),tickfont:{{color:V('--muted')}},zeroline:false,linecolor:'rgba(0,0,0,0)'}}}}),CFG);

 // 6 sonrisa
 const SM=DATA.opt.smile.filter(x=>x.c!==null);
 Plotly.react('g6',[
  {{type:'scatter',mode:'lines+markers',name:'Call',x:SM.map(x=>x.K),y:SM.map(x=>x.c),
   line:{{color:V('--s1'),width:2}},marker:{{size:9,color:V('--s1'),line:{{width:2,color:V('--surface')}}}},
   customdata:SM.map(x=>x.coi),hovertemplate:'Call K=%{{x}}<br>IV %{{y:.2f}}%<br>OI %{{customdata:,}}<extra></extra>'}},
  {{type:'scatter',mode:'lines+markers',name:'Put',x:SM.map(x=>x.K),y:SM.map(x=>x.p),
   line:{{color:V('--s2'),width:2}},marker:{{size:9,color:V('--s2'),line:{{width:2,color:V('--surface')}}}},
   customdata:SM.map(x=>x.poi),hovertemplate:'Put K=%{{x}}<br>IV %{{y:.2f}}%<br>OI %{{customdata:,}}<extra></extra>'}}],
  base({{shapes:[{{type:'line',x0:DATA.opt.spot,x1:DATA.opt.spot,yref:'paper',y0:0,y1:1,
    line:{{color:V('--axis'),width:1,dash:'dot'}}}}],
   annotations:[{{x:DATA.opt.spot,yref:'paper',y:1,yanchor:'top',xanchor:'left',showarrow:false,
    text:' spot $'+DATA.opt.spot.toFixed(2),font:{{color:V('--muted'),size:11}}}}],
   xaxis:{{title:{{text:'Precio de ejercicio (USD)',font:{{color:V('--muted'),size:12}}}},
    gridcolor:V('--grid'),linecolor:V('--axis'),tickfont:{{color:V('--muted')}},zeroline:false}},
   yaxis:{{title:{{text:'Volatilidad implícita',font:{{color:V('--muted'),size:12}}}},ticksuffix:'%',
    gridcolor:V('--grid'),tickfont:{{color:V('--muted')}},zeroline:false,linecolor:'rgba(0,0,0,0)'}}}}),CFG);

 // 7 estructura temporal
 const TM=DATA.opt.term;
 Plotly.react('g7',[
  {{type:'scatter',mode:'lines+markers',name:'IV en el dinero',x:TM.map(t=>t.a),y:TM.map(t=>t.iv),
   line:{{color:V('--s1'),width:2}},marker:{{size:9,color:V('--s1'),line:{{width:2,color:V('--surface')}}}},
   customdata:TM.map(t=>t.v),hovertemplate:'%{{customdata}}<br>IV %{{y:.2f}}%<extra></extra>'}},
  {{type:'scatter',mode:'markers',name:'Reporte trimestral dentro del plazo',
   x:[TM[0].a],y:[TM[0].iv],marker:{{size:17,color:V('--s2'),line:{{width:2,color:V('--surface')}}}},
   hovertemplate:'20-nov-2026<br>IV %{{y:.2f}}%<br>incluye el reporte<extra></extra>'}}],
  base({{shapes:[{{type:'line',xref:'paper',x0:0,x1:1,y0:29,y1:29,
    line:{{color:V('--s3'),width:2,dash:'dash'}}}}],
   annotations:[{{xref:'paper',x:1,y:29,yanchor:'bottom',xanchor:'right',showarrow:false,
    text:'volatilidad de largo plazo 29% ',font:{{color:V('--s3'),size:11}}}}],
   xaxis:{{title:{{text:'Años al vencimiento',font:{{color:V('--muted'),size:12}}}},
    gridcolor:V('--grid'),linecolor:V('--axis'),tickfont:{{color:V('--muted')}},zeroline:false}},
   yaxis:{{ticksuffix:'%',range:[27,43],gridcolor:V('--grid'),tickfont:{{color:V('--muted')}},
    zeroline:false,linecolor:'rgba(0,0,0,0)'}}}}),CFG);

 // 8 ejercicio anticipado
 const EJ=DATA.opt.ej;
 Plotly.react('g8',[
  {{type:'bar',name:'Call',x:EJ.map(e=>e.K),y:EJ.map(e=>e.c),
   marker:{{color:V('--s1'),line:{{width:2,color:V('--surface')}}}},
   customdata:EJ.map(e=>[e.ce,e.ca]),
   hovertemplate:'Call K=%{{x}}<br>europea %{{customdata[0]:.4f}} · americana %{{customdata[1]:.4f}}<br>premio %{{y:.3f}}%<extra></extra>'}},
  {{type:'bar',name:'Put',x:EJ.map(e=>e.K),y:EJ.map(e=>e.p),
   marker:{{color:V('--s2'),line:{{width:2,color:V('--surface')}}}},
   customdata:EJ.map(e=>[e.pe,e.pa]),
   hovertemplate:'Put K=%{{x}}<br>europea %{{customdata[0]:.4f}} · americana %{{customdata[1]:.4f}}<br>premio %{{y:.3f}}%<extra></extra>'}}],
  base({{barmode:'group',bargap:.3,bargroupgap:.08,
   xaxis:{{type:'category',title:{{text:'Precio de ejercicio',font:{{color:V('--muted'),size:12}}}},
    linecolor:V('--axis'),tickfont:{{color:V('--muted')}},gridcolor:'rgba(0,0,0,0)'}},
   yaxis:{{title:{{text:'Premio sobre la europea',font:{{color:V('--muted'),size:12}}}},ticksuffix:'%',
    gridcolor:V('--grid'),tickfont:{{color:V('--muted')}},zeroline:false,linecolor:'rgba(0,0,0,0)'}}}}),CFG);

 // 9 trade-off
 const TO=DATA.opt.tradeoff;
 Plotly.react('g9',[
  {{type:'scatter',mode:'lines',name:'Valor de la opción entregada',x:TO.map(t=>t.p),y:TO.map(t=>t.op),
   line:{{color:V('--s3'),width:3}},
   hovertemplate:'prima %{{x}}%<br>opción %{{y:.2f}} por 100 nom.<extra></extra>'}},
  {{type:'scatter',mode:'lines',name:'VP del ahorro de cupón',x:TO.map(t=>t.p),y:TO.map(t=>t.ah),
   line:{{color:V('--s1'),width:3,dash:'dash'}},customdata:TO.map(t=>t.cpn),
   hovertemplate:'prima %{{x}}%<br>ahorro %{{y:.2f}}<br>cupón %{{customdata:.3f}}%<extra></extra>'}}],
  base({{shapes:[{{type:'line',x0:25,x1:25,yref:'paper',y0:0,y1:1,
    line:{{color:V('--axis'),width:1,dash:'dot'}}}}],
   annotations:[{{x:25,yref:'paper',y:1,yanchor:'top',xanchor:'left',showarrow:false,
    text:' prima propuesta 25%',font:{{color:V('--muted'),size:11}}}}],
   xaxis:{{title:{{text:'Prima de conversión',font:{{color:V('--muted'),size:12}}}},ticksuffix:'%',
    gridcolor:V('--grid'),linecolor:V('--axis'),tickfont:{{color:V('--muted')}},zeroline:false}},
   yaxis:{{title:{{text:'Valor por cada 100 de nominal',font:{{color:V('--muted'),size:12}}}},
    gridcolor:V('--grid'),tickfont:{{color:V('--muted')}},zeroline:false,linecolor:'rgba(0,0,0,0)'}}}}),CFG);

 // 10 volatilidad condicional en el tiempo
 const GS=DATA.garch.serie, GG=DATA.garch;
 Plotly.react('g10',[
  {{type:'scatter',mode:'lines',name:'Volatilidad condicional GARCH',
   x:GS.map(p=>p.d),y:GS.map(p=>p.v),line:{{color:V('--s1'),width:1.6}},
   hovertemplate:'%{{x}}<br>%{{y:.2f}}%<extra></extra>'}}],
  base({{shapes:[
    {{type:'line',xref:'paper',x0:0,x1:1,y0:GG.VL,y1:GG.VL,line:{{color:V('--s4'),width:2,dash:'dash'}}}},
    {{type:'line',xref:'paper',x0:0,x1:1,y0:31.89,y1:31.89,line:{{color:V('--s2'),width:1.5,dash:'dot'}}}}],
   annotations:[
    {{xref:'paper',x:0,y:GG.VL,yanchor:'bottom',xanchor:'left',showarrow:false,
     text:' largo plazo '+GG.VL.toFixed(2)+'%',font:{{color:V('--s4'),size:11}}}},
    {{xref:'paper',x:1,y:31.89,yanchor:'bottom',xanchor:'right',showarrow:false,
     text:'implícita 18-dic 31.89% ',font:{{color:V('--s2'),size:11}}}}],
   showlegend:false,
   xaxis:{{gridcolor:V('--grid'),linecolor:V('--axis'),tickfont:{{color:V('--muted')}},zeroline:false}},
   yaxis:{{title:{{text:'Volatilidad anualizada',font:{{color:V('--muted'),size:12}}}},ticksuffix:'%',
    gridcolor:V('--grid'),tickfont:{{color:V('--muted')}},zeroline:false,linecolor:'rgba(0,0,0,0)'}}}}),CFG);

 // 11 pronostico por horizonte
 const PR=DATA.garch.pron;
 Plotly.react('g11',[
  {{type:'scatter',mode:'lines',name:'Pronóstico GARCH',x:PR.map(p=>p.a),y:PR.map(p=>p.v),
   line:{{color:V('--s1'),width:3}},hovertemplate:'%{{x:.2f}} años<br>%{{y:.2f}}%<extra></extra>'}},
  {{type:'scatter',mode:'lines',name:'Implícita 18-dic (31.89%)',x:[0,3],y:[31.89,31.89],
   line:{{color:V('--s2'),width:2,dash:'dot'}},hoverinfo:'skip'}},
  {{type:'scatter',mode:'lines',name:'Implícita LEAPs (29.00%)',x:[0,3],y:[29,29],
   line:{{color:V('--s3'),width:2,dash:'dot'}},hoverinfo:'skip'}},
  {{type:'scatter',mode:'lines',name:'Largo plazo del modelo',x:[0,3],y:[GG.VL,GG.VL],
   line:{{color:V('--s4'),width:2,dash:'dash'}},hoverinfo:'skip'}}],
  base({{xaxis:{{title:{{text:'Horizonte (años)',font:{{color:V('--muted'),size:12}}}},
    gridcolor:V('--grid'),linecolor:V('--axis'),tickfont:{{color:V('--muted')}},zeroline:false}},
   yaxis:{{title:{{text:'Volatilidad anual',font:{{color:V('--muted'),size:12}}}},ticksuffix:'%',
    range:[21,34],gridcolor:V('--grid'),tickfont:{{color:V('--muted')}},zeroline:false,
    linecolor:'rgba(0,0,0,0)'}}}}),CFG);
}}
function tog(){{const r=document.documentElement;
 const d=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
 r.setAttribute('data-theme',d==='dark'?'light':'dark');draw();}}
matchMedia('(prefers-color-scheme:dark)').addEventListener('change',()=>{{
 if(!document.documentElement.getAttribute('data-theme'))draw();}});
draw();
(function(){{const L=[...document.querySelectorAll('.nav a')];const S=L.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);
function spy(){{let y=scrollY+120,cur=0;S.forEach((s,i)=>{{if(s.getBoundingClientRect().top+scrollY<=y)cur=i}});L.forEach((a,i)=>a.classList.toggle('act',i===cur));
 const a=L[cur];if(a&&a.scrollIntoView){{const n=document.querySelector('.nav');n.scrollTo({{left:a.offsetLeft-60,behavior:'auto'}})}}}}
addEventListener('scroll',spy,{{passive:true}});spy();}})();
</script></body></html>"""

HTML = HTML.replace('{PLOTLY}', plotly_js())
os.makedirs(os.path.dirname(os.path.abspath(SALIDA)), exist_ok=True)
with open(SALIDA, 'w', encoding='utf-8') as _f: _f.write(HTML)
print(f"Dashboard generado: {os.path.relpath(SALIDA)}  ({os.path.getsize(SALIDA)/1e6:.2f} MB)")
