#!/usr/bin/env python
# coding: utf-8

# # Validación del convertible: Molson Coors (2007) y Walmart (2026)
# 
# **Proyecto Final · Productos Derivados y Administración de Riesgos Corporativos**  
# EGADE Business School · Equipo 6 · Grupo 40  
# Eduardo Ayala Saldaña, Mariann Antonelli Morales Tobias, Ulises Salinas López  
# Dr. Raymundo Díaz Robles · Noviembre de 2026
# 
# Este notebook hace tres cosas:
# 1. Replica el caso Molson Coors con los supuestos de las notas de enseñanza (NE90-06-107) y compara contra sus cifras publicadas.
# 2. Aplica la misma función a Walmart con los parámetros del reporte ejecutivo y compara contra las cifras del reporte.
# 3. Muestra la sensibilidad a la prima de conversión (15 %, 25 %, 40 %, 60 %) y resume ventajas y desventajas del convertible.
# 
# Idea central: convertible = bono recto + opción call sobre la acción. Todo ahorro de cupón se paga con la opción entregada.

# In[1]:


from math import log, sqrt, exp, erf

N = lambda x: 0.5 * (1.0 + erf(x / sqrt(2.0)))

def bs_call(S, K, T, r, sigma, q=0.0):
    """Black-Scholes-Merton, call europea con dividend yield continuo q."""
    d1 = (log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    return S * exp(-q * T) * N(d1) - K * exp(-r * T) * N(d2)

def bono_recto(cupon, T, ytm, face=100.0, f=2):
    """Valor de un bono con cupón semestral descontado a ytm."""
    n, c, y = round(T * f), face * cupon / f, ytm / f
    return sum(c / (1 + y)**t for t in range(1, n + 1)) + face / (1 + y)**n

def convertible(S, T, r, ytm, sigma, q, prima, cupon, face=100.0):
    K = S * (1 + prima)
    ratio = face / K                       # acciones por bono
    opcion = ratio * bs_call(S, K, T, r, sigma, q)
    return dict(K=K, ratio=ratio, bono=bono_recto(cupon, T, ytm, face), opcion=opcion)

def cupon_par(S, T, r, ytm, sigma, q, prima, face=100.0):
    """Cupón que hace bono + opción = nominal (bisección)."""
    f = lambda c: (lambda v: v["bono"] + v["opcion"] - face)(convertible(S, T, r, ytm, sigma, q, prima, c, face))
    if f(0.0) > 0: return 0.0
    lo, hi = 0.0, 2 * ytm
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    return 0.5 * (lo + hi)


# ## 1. Molson Coors (2007), supuestos de las notas de enseñanza
# 
# S = 87.61, prima 25 %, T = 6 años, r = 4.46 %, volatilidad 23 %, tasa de descuento 5.75 %, sin dividendos. Bono de 1,000 dólares.

# In[2]:


S, T, r, ytm, sig, q, prima = 87.61, 6, 0.0446, 0.0575, 0.23, 0.0, 0.25
cp = cupon_par(S, T, r, ytm, sig, q, prima, face=1000)
v = convertible(S, T, r, ytm, sig, q, prima, cp, face=1000)
print(f"Precio de conversión : {v['K']:.2f}   (caso: 109.51)")
print(f"Acciones por bono    : {v['ratio']:.3f}")
print(f"Opción de conversión : {v['opcion']:.1f} por bono   (caso: 191.5)")
print(f"Componente de bono   : {v['bono']:.1f}   (caso: 808.5)")
print(f"Cupón a la par       : {cp*100:.2f} %   (caso: 1.93 %)")


# ### Call spread de Molson Coors (Exhibit 4 del caso)
# 
# Se compran calls con strike a 25 % de prima y se venden warrants a 60 %, sobre 5.25 millones de acciones (575 millones / 109.51).

# In[3]:


acc = 575e6 / 109.51
K1, K2 = S * 1.25, S * 1.60
c_pag = acc * bs_call(S, K1, T, r, sig)
w_cob = acc * bs_call(S, K2, T, r, sig)
print(f"Acciones subyacentes : {acc/1e6:.2f} M")
print(f"Calls compradas (K={K1:.2f}) : {c_pag/1e6:.1f} M   (caso: 106.7)")
print(f"Warrants vendidos (K={K2:.2f}): {w_cob/1e6:.1f} M   (caso: 57.0)")
print(f"Costo neto           : {(c_pag-w_cob)/1e6:.1f} M   (caso: 49.7)  = {(c_pag-w_cob)/575e6*100:.1f} % de la emisión (caso: 8.6 %)")


# Nota: las cifras del call spread de Molson Coors **no coinciden** con el Exhibit 4 (110.1 y 68.9 contra 106.7 y 57.0). Las notas de enseñanza no publican los supuestos de ese cuadro; con una sola volatilidad de 23 % el warrant a 60 % sale más caro que en el caso. Lo más probable es que el caso use otra volatilidad para cada strike (sesgo). No se afirma como causa confirmada. Lo que sí se verifica es la relación: se paga más por las calls que lo que se cobra por los warrants, es decir, no hay free lunch.

# ## 2. Walmart (2026), parámetros del reporte ejecutivo
# 
# S = 123.51, T = 6, r = 4.78 %, deuda recta 5.14 %, volatilidad 29 %, dividend yield 0.81 %, prima 25 %, emisión 1,500 millones.

# In[4]:


S, T, r, ytm, sig, q, prima, EM = 123.51, 6, 0.0478, 0.0514, 0.29, 0.0081, 0.25, 1500e6
cp = cupon_par(S, T, r, ytm, sig, q, prima)
v = convertible(S, T, r, ytm, sig, q, prima, cp)
print(f"Precio de conversión : {v['K']:.2f}   (reporte: 154.39)")
print(f"Acciones por 100     : {v['ratio']:.4f}   (reporte: 0.6477)")
print(f"Cupón a la par       : {cp*100:.3f} %   (reporte: 0.918 %)")
print(f"Componente de bono   : {v['bono']:.3f}   (reporte: 78.438)")
print(f"Componente de opción : {v['opcion']:.3f}   (reporte: 21.562)")
print(f"Total                : {v['bono']+v['opcion']:.3f}")


# ### No hay free lunch
# 
# El valor presente del ahorro de cupón (frente a deuda recta) debe igualar el valor de la opción entregada.

# In[5]:


i = ytm / 2
af = sum(1 / (1 + i)**t for t in range(1, 13))
vp_ahorro = (ytm - cp) * EM / 2 * af
valor_opc = v["opcion"] / 100 * EM
print(f"VP del ahorro de cupón : {vp_ahorro/1e6:.1f} M   (reporte: 323.4)")
print(f"Valor de la opción     : {valor_opc/1e6:.1f} M")
print(f"Diferencia             : {(vp_ahorro-valor_opc)/1e6:.4f} M")


# ### Call spread de Walmart
# 
# Strikes a 25 % y 60 % de prima.

# In[6]:


acc = EM / v["K"]
K1, K2 = S * 1.25, S * 1.60
c_pag = acc * bs_call(S, K1, T, r, sig, q)
w_cob = acc * bs_call(S, K2, T, r, sig, q)
print(f"Strikes              : {K1:.2f} / {K2:.2f}   (reporte: 154.39 / 197.62)")
print(f"Acciones subyacentes : {acc/1e6:.2f} M   (reporte: 9.72)")
print(f"Prima pagada         : {c_pag/1e6:.1f} M   (reporte: 323.4)")
print(f"Prima cobrada        : {w_cob/1e6:.1f} M   (reporte: 227.5)")
print(f"Costo neto           : {(c_pag-w_cob)/1e6:.1f} M = {(c_pag-w_cob)/EM*100:.2f} % de la emisión   (reporte: 95.9 M, 6.39 %)")


# Resultado: las cifras de Walmart coinciden con el reporte (diferencias de una milésima por redondeo de la tasa de 6 años, 4.78 %).
# 
# ## 3. Sensibilidad a la prima de conversión
# 
# A menor prima, la opción vale más y el cupón a la par baja. Es la pregunta 3b de las notas de enseñanza (15 % y 40 %).

# In[7]:


print(f"{'Prima':>6} {'Strike':>8} {'Cupón a la par':>15} {'Opción (por 100)':>17} {'Bono (por 100)':>15}")
for p in (0.15, 0.25, 0.40, 0.50, 0.60):
    c = cupon_par(S, T, r, ytm, sig, q, p)
    x = convertible(S, T, r, ytm, sig, q, p, c)
    print(f"{p*100:5.0f}% {x['K']:8.2f} {c*100:14.3f}% {x['opcion']:17.3f} {x['bono']:15.3f}")


# ## 4. Convertible frente a deuda recta y capital (pregunta 2 del caso)
# 
# | | Convertible | Deuda recta | Emisión de capital |
# |---|---|---|---|
# | Costo en efectivo | Cupón bajo (0.918 % en Walmart) | Cupón de mercado (5.14 %) | Sin cupón, pero dividendos |
# | Costo económico | El mismo: el descuento de cupón paga la opción entregada | Cupón pleno | Costo del capital más alto |
# | Dilución | Sí, solo si la acción supera el strike; el call spread la neutraliza hasta 197.62 | Ninguna | Inmediata |
# | Deducibilidad fiscal | Intereses deducibles | Intereses deducibles | No deducible |
# | Dividendos | No se pagan hasta conversión | No aplica | Sí |
# | Riesgo | Señal de mercado sobre valuación de la acción; conversión anticipada | Riesgo de refinanciamiento | Pérdida de control, precio de emisión |
# | Para el inversionista | Alza ilimitada con piso de bono | Cupón fijo | Participación plena, sin piso |
# 
# **Lectura para Walmart:** el convertible no genera ahorro económico (sección 2). Su valor está en lo que acompaña a la emisión: recompra de deuda a descuento y cobertura de tasa y de divisas.
