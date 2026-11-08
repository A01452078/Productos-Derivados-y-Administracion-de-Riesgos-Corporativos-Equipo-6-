# -*- coding: utf-8 -*-
"""
Identificacion de estructuras dentro del historial de Eduardo Ayala.
Dos posiciones abiertas el mismo dia sobre el mismo subyacente no son
operaciones independientes: forman una estrategia con perfil propio.
"""
print("="*80)
print("A. PROTECTIVE PUT SOBRE APPLE  (30-sep al 13-oct)")
print("="*80)
acc_c, acc_v, nq = 330.80, 346.15, 100
put_c, put_v, npq = 4.90, 0.82, 1
pl_acc = (acc_v-acc_c)*nq
pl_put = (put_v-put_c)*npq*100
print(f"   30-sep: compra {nq} acciones AAPL a {acc_c} y {npq} put 320 "
      f"oct-30 a {put_c}")
print(f"   13-oct: vende todo. Accion en {acc_v}, put en {put_v}\n")
print(f"   {'Componente':<26}{'P&L':>12}")
print(f"   {'Acciones':<26}{pl_acc:>+11,.0f}$")
print(f"   {'Put (el seguro)':<26}{pl_put:>+11,.0f}$")
print(f"   {'':<26}{'-'*12}")
print(f"   {'Resultado cubierto':<26}{pl_acc+pl_put:>+11,.0f}$")
print(f"   {'Resultado sin cubrir':<26}{pl_acc:>+11,.0f}$")
print(f"\n   La accion SUBIO {acc_v-acc_c:.2f} por titulo. El put nunca se")
print(f"   necesito y expiro casi sin valor: costo {-pl_put:,.0f} USD, que es")
print(f"   el {-pl_put/pl_acc*100:.1f}% de la ganancia de la accion.")
print(f"   El seguro se paga aunque no haya siniestro. Ese es su precio.")

print()
print("="*80)
print("B. CONTRASTE CON EL PROTECTIVE PUT DE ULISES")
print("="*80)
print(f"   {'':<22}{'Eduardo':>16}{'Ulises':>16}")
print(f"   {'Direccion de la accion':<22}{'subio +15.35':>16}{'bajo -7.48':>16}")
print(f"   {'P&L de la accion':<22}{'+1,535$':>16}{'-1,496$':>16}")
print(f"   {'P&L del put':<22}{'-408$':>16}{'+440$':>16}")
print(f"   {'Resultado combinado':<22}{'+1,127$':>16}{'-1,056$':>16}")
print(f"   {'Papel del put':<22}{'costo inutil':>16}{'amortiguo 29%':>16}")
print()
print("   Los dos casos juntos cuentan la leccion completa del protective put:")
print("   cuando el activo sube el seguro es un costo puro que recorta la")
print("   ganancia; cuando baja amortigua, pero nunca por completo, porque el")
print("   valor temporal se consume aunque la cobertura funcione.")

print()
print("="*80)
print("C. STRADDLE LARGO SOBRE SPY  (13-oct al 20-oct)")
print("="*80)
c_c, c_v = 5.98, 1.15
p_c, p_v = 4.59, 11.31
costo = (c_c+p_c)*100
print(f"   13-oct: compra simultanea de call 778 a {c_c} y put 778 a {p_c},")
print(f"           ambas con vencimiento 23-oct. Mismo strike, misma fecha.")
print(f"           Eso no son dos apuestas: es UNA apuesta a la volatilidad.\n")
print(f"   {'Pata':<22}{'costo':>10}{'ingreso':>10}{'P&L':>10}")
print(f"   {'Call 778':<22}{c_c*100:>9,.0f}${c_v*100:>9,.0f}${(c_v-c_c)*100:>+9,.0f}$")
print(f"   {'Put 778':<22}{p_c*100:>9,.0f}${p_v*100:>9,.0f}${(p_v-p_c)*100:>+9,.0f}$")
print(f"   {'':<22}{'-'*10}{'-'*10}{'-'*10}")
print(f"   {'Straddle':<22}{costo:>9,.0f}${(c_v+p_v)*100:>9,.0f}$"
      f"{((c_v+p_v)-(c_c+p_c))*100:>+9,.0f}$")
print(f"\n   Retorno: {((c_v+p_v)/(c_c+p_c)-1)*100:+.1f}% sobre la prima.")
print(f"   Puntos de equilibrio al vencimiento: {778-(c_c+p_c):.2f} y {778+(c_c+p_c):.2f}")
print(f"   El mercado cayo y el put financio a la call. La estructura no")
print(f"   necesitaba acertar la direccion, solo que hubiera movimiento.")

print()
print("="*80)
print("D. LA POSICION QUE MAS ENSENA: TLT PUT 78")
print("="*80)
print(f"   10 contratos comprados a 0.45 y vendidos a 0.01.")
print(f"   Perdida: {(0.01-0.45)*100*10:+,.0f} USD sobre {0.45*100*10:,.0f} "
      f"invertidos = {(0.01/0.45-1)*100:.1f}%")
print()
print("   Fue la unica posicion con 10 contratos; el resto llevo 1 o 2.")
print("   Era la mas barata por contrato, y esa baratura invito al tamano.")
print("   Una prima de 0.45 sobre un subyacente de 78 es una opcion muy")
print("   fuera del dinero: lo barato lo era porque la probabilidad de")
print("   ejercicio era remota, no porque estuviera mal valuada.")
print("   Es el mismo sesgo que produjo la concentracion de ASML en el")
print("   ciclo III del portafolio de equipo.")
