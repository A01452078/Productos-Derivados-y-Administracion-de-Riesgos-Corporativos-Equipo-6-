"""
Proyecto Final - Productos Derivados y Administracion de Riesgos Corporativos
EGADE Business School - Maestria en Finanzas - Equipo 6, Grupo 40

Walmart Inc. (WMT.O) - Swaps de tasa y de divisas.

Cubre los tres instrumentos de cobertura que el reporte recomienda:
  1. Swap de tasa fija-flotante sobre las notas de tasa flotante.
  2. Cross-currency swap sobre la colocacion de C$5,000 M del 23-oct-2026.
  3. T-lock sobre el refinanciamiento del bloque de cupon bajo,
     analogo al que uso Molson Coors durante su recompra de 2007.

Sin dependencias externas: solo biblioteca estandar.
Curva del Tesoro: LSEG / TRADEWEB, 1-nov-2026.
"""

# ============================================================
# 1. CURVA Y BOOTSTRAPPING
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
# 2. SWAP DE TASA DE INTERES (vanilla, fija contra flotante)
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
# 3. T-LOCK  (cobertura de la tasa del Tesoro en un refinanciamiento)
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
# 4. CROSS-CURRENCY SWAP
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

# Basis swap CAD/USD cotizado en LSEG el 6-nov-2026 (RIC CADCBS3Y=, 5Y, 7Y, 10Y), en pb.
# Capturas 20 a 23 del anexo. Signo negativo: prima por obtener dolares.
BASIS_CADUSD = {3: -14.8, 5: -11.6, 7: -8.9, 10: -5.1}

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
# 5. POSICIONES A CUBRIR  (LSEG, corte 23-oct-2026)
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

def main():
    print("="*76)
    print("WALMART INC. (WMT.O) - COBERTURA CON SWAPS")
    print(f"Curva del Tesoro: LSEG/TRADEWEB  |  Analisis al {HOY}")
    print("="*76)

    print("\n[1] CURVA DESCONTADA")
    print(f"  {'Plazo':>6} {'Par':>9} {'Cupon cero':>12} {'Factor dsc':>12}")
    for T in (0.5, 1, 2, 3, 5, 7, 10, 20, 30):
        print(f"  {T:>5}a {par_interp(T)*100:>8.3f}% {cero(T)*100:>11.3f}% {df(T):>12.5f}")

    print("\n[2] SWAP DE TASA SOBRE LAS NOTAS FLOTANTES")
    print("    Walmart paga fijo y recibe flotante: convierte deuda de tasa")
    print("    variable en tasa fija y elimina el riesgo de refijacion.\n")
    print(f"  {'Monto':>9} {'Vence':>12} {'Cupon hoy':>10} {'Plazo':>7} {'Tasa par':>10} {'DV01':>10}")
    tot_n, tot_dv = 0.0, 0.0
    for monto, venc, cpn, T in FRN:
        s = tasa_par_swap(T); d = dv01(monto, T)
        tot_n += monto; tot_dv += d
        print(f"  {monto:>8,.0f} {venc:>12} {cpn:>9.3f}% {T:>6.2f}a {s*100:>9.4f}% {d:>9.4f}")
    print(f"  {'':>8} {'TOTAL':>12} {'':>10} {'':>7} {'':>10} {tot_dv:>9.4f}")
    print(f"\n  Nocional cubierto: ${tot_n:,.0f} M")
    print(f"  Un movimiento paralelo de 100 pb mueve el paquete "
          f"${tot_dv*100:,.2f} M")
    print("\n  Nota: la nota que vence en abril de 2027 tiene menos de seis meses")
    print("  de vida y un DV01 de 0.0367, de modo que swapearla no compensa el")
    print("  costo de ejecucion. La cobertura relevante es la de 2029.")

    print("\n[3] CROSS-CURRENCY SWAP SOBRE LA COLOCACION EN DOLARES CANADIENSES")
    c = CCS; r = costo_todo_incluido()
    print(f"    Nocional: C${c['nocional_cad']:,.0f} M  ->  US${r['nocional_usd']:,.1f} M "
          f"al tipo de cambio {c['usdcad']:.4f}\n")
    print("    Lectura ingenua: el tramo en CAD paga menos cupon que el tramo")
    print("    gemelo en USD, luego emitir en CAD sale mas barato.")
    print(f"      Cupon CAD 2033 ......... {c['cupon_cad']:.3f}%")
    print(f"      Cupon USD 2033 ......... {c['cupon_usd']:.3f}%")
    print(f"      Diferencia ............. {(c['cupon_usd']-c['cupon_cad'])*100:.0f} pb a favor de CAD")
    print(f"\n    Pero el diferencial viene de la curva, no del credito:")
    print(f"      Curva gubernamental canadiense por debajo de la estadounidense: "
          f"{dif_curvas():.1f} pb")
    print(f"      El cross-currency swap intercambia una curva por la otra y")
    print(f"      devuelve ese diferencial completo.")
    print(f"\n    Lo que sobrevive al swap es el spread de credito:")
    print(f"      Emision directa en USD ....... curva USD + {r['directo_usd']:.1f} pb")
    print(f"      Emision en CAD swapeada ...... curva USD + {r['cad_swapeado']:.1f} pb")
    print(f"      DIFERENCIA ................... {r['diferencia_pb']:+.1f} pb "
          f"EN CONTRA de la ruta canadiense")
    costo = r['diferencia_pb']/1e4*r['nocional_usd']
    print(f"\n      Sobre US${r['nocional_usd']:,.1f} M son ${costo:,.2f} M anuales,")
    print(f"      ${costo*c['plazo']:,.1f} M a lo largo de los {c['plazo']:.0f} anos.")
    print(f"\n      El basis cruzado tendria que aportar al menos "
          f"{r['basis_necesario']:.1f} pb para empatar.")
    b7 = abs(BASIS_CADUSD[7])
    print(f"\n      Basis CAD/USD observado en LSEG (6-nov-2026), pb:")
    for t, v in BASIS_CADUSD.items():
        print(f"        {t:>2} anos ... {v:+.1f}")
    print(f"      A 7 anos el valor absoluto es {b7:.1f} pb, {b7/r['basis_necesario']*100:.0f}% de lo necesario.")
    print(f"      Aun a favor de Walmart quedarian {r['basis_necesario']-b7:.1f} pb en contra de la ruta CAD "
          f"(${(r['basis_necesario']-b7)/1e4*r['nocional_usd']:,.2f} M al ano).")
    print("      La conclusion no se revierte.")

    print("\n[4] T-LOCK SOBRE EL REFINANCIAMIENTO DEL BLOQUE DE CUPON BAJO")
    print("    Mismo instrumento que uso Molson Coors en 2007 para fijar la")
    print("    tasa del Tesoro mientras ejecutaba su recompra.\n")
    monto = CUPON_BAJO[0][0]
    T0, T1 = 2.0, 9.0
    f = tasa_forward(T0, T1)
    print(f"  Vencimiento a cubrir: ${monto:,.0f} M al {CUPON_BAJO[0][2]:.3f}% "
          f"({CUPON_BAJO[0][1]})")
    print(f"  Estructura: fijar hoy la tasa a 7 anos que regira dentro de 2 anos")
    print(f"  Tasa forward 7a dentro de 2a: {f*100:.4f}%")
    print(f"  Tasa spot a 7 anos:           {tasa_par_swap(7)*100:.4f}%")
    print(f"  Prima forward:                {(f-tasa_par_swap(7))*1e4:+.1f} pb\n")
    print(f"  {'Escenario':>22} {'Costo extra emision':>22} {'Resultado T-lock':>19} {'Neto':>10}")
    for mov in (-100, -50, 0, 50, 100):
        extra = -anualidad(T0,T1)*monto*1e-4*mov      # mas tasa = mas costo
        gan   = tlock(monto, T0, T1, mov)
        print(f"  {f'{mov:+d} pb':>22} {extra:>21,.2f} {gan:>18,.2f} {extra+gan:>9,.2f}")
    print("\n  La cobertura es exacta en el primer orden: lo que el emisor paga")
    print("  de mas en cupon lo recupera en el T-lock, y viceversa.")

    print("\n[5] LO QUE EL T-LOCK NO CUBRE: RIESGO DE BASE")
    print("    El T-lock fija la tasa del Tesoro, no el costo de fondeo de")
    print("    Walmart. El spread de credito queda descubierto.\n")
    d_fwd = anualidad(T0, T1)*monto*1e-4
    print(f"  {'Tesoro':>10} {'Spread':>10} {'Costo emision':>16} {'T-lock':>12} {'NETO':>12}")
    for mov_t, mov_s, etq in [(0,0,''), (100,0,''), (0,25,''), (0,50,''),
                              (100,25,''), (-50,40,''), (-100,50,'')]:
        extra = -d_fwd*(mov_t + mov_s)
        gan   = d_fwd*mov_t
        print(f"  {f'{mov_t:+d} pb':>10} {f'{mov_s:+d} pb':>10} "
              f"{extra:>15,.2f} {gan:>11,.2f} {extra+gan:>11,.2f}")
    print("\n  Mientras el Tesoro se mueva solo, la cobertura es perfecta.")
    print("  En cuanto el spread de credito se mueve por su cuenta, el T-lock")
    print("  no responde: cada 25 pb de ampliacion cuestan "
          f"${d_fwd*25:,.2f} M sin compensacion.")
    print("\n  Es exactamente el riesgo que corrio Molson Coors, y la razon por")
    print("  la que su T-lock liquido con una ganancia de 1.4 millones y no con")
    print("  una cobertura perfecta del costo total de su recompra.")

if __name__ == "__main__":
    main()
