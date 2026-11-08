# -*- coding: utf-8 -*-
"""
Diagnostico de ejecutabilidad de la cadena CLF7 (crudo, ene-2027), 20-nov.

No se calibra volatilidad ni se proponen strikes: primero hay que establecer
si las cotizaciones son operables. Un spread bid-offer que supera al propio
punto medio significa que no existe mercado de dos puntas y que comprar al
offer destruiria capital en el instante de la ejecucion.
"""
F, BARRILES = 89.75, 1000.0

CL = [  # strike, call_bid, call_offer, put_bid, put_offer
 (86.50, 5.73,  6.07,  2.51, 23.42), (86.75, 5.57,  5.92,  2.60, 23.76),
 (87.25, 0.89, 32.16,  0.02, 24.45), (87.50, 0.76, 31.85,  1.19, 10.63),
 (87.75, 0.64, 31.54,  0.18, 25.18), (88.25, 2.24, 13.77,  0.98, 11.22),
 (88.50, 2.10, 13.58,  0.45,  4.50), (88.75, 1.98, 13.41,  2.27, 11.57),
 (89.25, 1.72, 13.08,  1.36, 12.07), (89.50, 1.64, 12.92,  1.47, 12.29),
 (89.75, 1.52, 12.76,  1.57, 12.45), (90.25, 1.31, 12.51,  1.80, 12.92),
 (90.50, 1.21, 12.29,  1.92, 13.16), (90.75, 1.13, 12.08,  2.06, 13.33),
 (91.25, 0.98, 11.68,  2.35, 13.70), (91.50, 0.91, 11.49,  2.49, 13.89),
 (91.75, 0.83, 11.31,  2.64, 14.08), (92.25, 0.70, 10.95,  2.96, 14.48),
 (92.50, 1.73, 10.78,  3.10, 14.69), (92.75, 2.77, 25.03,  1.46, 32.32),
 (93.25, 2.61, 24.38,  1.78, 32.96),
]

print("="*78)
print("A. ANCHO DEL MERCADO EN CLF7 (crudo)  vs  ZNZ6 (nota 10 anos)")
print("="*78)
print(f"   {'K':>7} {'C bid':>8} {'C offer':>9} {'spread':>8} {'% del medio':>12} "
      f"{'offer/bid':>10}")
rel=[]
for k,cb,co,pb,po in CL:
    mid=0.5*(cb+co); sp=co-cb; r=sp/mid*100
    rel.append(r)
    marca = "  <- at-the-money" if abs(k-F)<1e-9 else ""
    print(f"   {k:7.2f} {cb:8.2f} {co:9.2f} {sp:8.2f} {r:11.0f}% {co/cb:9.1f}x{marca}")

print(f"\n   Spread medio como porcentaje del punto medio: {sum(rel)/len(rel):.0f}%")
print(f"   Referencia ZNZ6 at-the-money (put 107.25): 31 USD sobre 547 USD = 6%")
print(f"   Referencia 6CZ6 at-the-money (call 0.715):  40 USD sobre 260 USD = 15%")

print()
print("="*78)
print("B. COHERENCIA INTERNA: QUE PUNTA ES LA CREIBLE")
print("="*78)
print("   Paridad put-call usando SOLO bids, y luego SOLO offers.")
print("   Si una de las dos series reproduce F - K y la otra no, la que")
print("   falla esta rancia.\n")
print(f"   {'K':>7} {'(Cb-Pb)':>9} {'(Co-Po)':>10} {'F-K':>8} "
      f"{'err bid':>9} {'err offer':>11}")
eb,eo=[],[]
for k,cb,co,pb,po in CL:
    t=F-k; a,b=cb-pb, co-po
    eb.append(abs(a-t)); eo.append(abs(b-t))
    print(f"   {k:7.2f} {a:9.2f} {b:10.2f} {t:8.2f} {a-t:9.2f} {b-t:10.2f}")
print(f"\n   Error absoluto medio con bids:   {sum(eb)/len(eb):6.2f} USD/barril "
      f"({sum(eb)/len(eb)*BARRILES:,.0f} USD por contrato)")
print(f"   Error absoluto medio con offers: {sum(eo)/len(eo):6.2f} USD/barril "
      f"({sum(eo)/len(eo)*BARRILES:,.0f} USD por contrato)")
print("\n   Veredicto: el lado comprador es coherente; el lado vendedor no")
print("   existe como mercado. Comprar al offer implicaria pagar multiplos")
print("   del valor teorico. La posicion de crudo queda descartada por")
print("   ejecutabilidad, no por tesis.")
