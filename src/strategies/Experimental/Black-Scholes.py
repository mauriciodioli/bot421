# Importar Librerías Necesarias:
# numpy para cálculos matemáticos.
# scipy.stats.norm para la función de distribución acumulativa de la distribución normal.

import numpy as np
from scipy.stats import norm

# Definir Parámetros:
# S: Precio actual del activo subyacente
# K: Precio de ejercicio de la opción
# T: Tiempo hasta el vencimiento en años
# r: Tasa de interés libre de riesgo
# sigma: Volatilidad del precio del activo subyacente

S = 100  # Precio actual del activo subyacente
K = 100  # Precio de ejercicio de la opción
T = 1    # Tiempo hasta el vencimiento en años
r = 0.05 # Tasa de interés libre de riesgo
sigma = 0.2 # Volatilidad del precio del activo subyacente

# Calcular d1 y d2:
# Utilizando las fórmulas mencionadas anteriormente.
d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
d2 = d1 - sigma * np.sqrt(T)

# Calcular Precios de las Opciones:
# Usar las fórmulas de Black-Scholes para una opción de compra (call) y una opción de venta (put).

# Precio de la opción de compra (Call)
C = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

# Precio de la opción de venta (Put)
P = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

# Resultados
# El código proporcionará los precios de la opción de compra y de venta basados en los parámetros ingresados. 
# Esto ilustra cómo se aplica la ecuación de Black-Scholes/Merton en la práctica para calcular los precios de las opciones.

print(f"Precio de la opción de compra (Call): {C:.2f}")
print(f"Precio de la opción de venta (Put): {P:.2f}")

# Ecuación de Black-Scholes/Merton
# La ecuación en la imagen es la siguiente:
# ∂V/∂t + rS ∂V/∂S + 1/2 σ^2 S^2 ∂^2 V/∂S^2 - rV = 0
#
# donde:
# V es el valor de la opción
# t es el tiempo
# S es el precio del activo subyacente
# r es la tasa de interés libre de riesgo
# σ es la volatilidad del precio del activo subyacente

# Aplicación de la Fórmula
# Para aplicar esta fórmula, necesitas:
# Determinar los parámetros necesarios:
# Precio actual del activo subyacente (S).
# Precio de ejercicio de la opción (K).
# Tiempo hasta el vencimiento (T).
# Volatilidad del activo subyacente (σ).
# Tasa de interés libre de riesgo (r).
# Resolver la ecuación de Black-Scholes para obtener el precio de la opción.

# La solución analítica de la ecuación de Black-Scholes para una opción de compra europea (call) y una opción de venta europea (put) se da por las siguientes fórmulas:

# Precio de una Opción de Compra Europea (Call)
# C = S0 N(d1) - K e^(-rT) N(d2)

# Precio de una Opción de Venta Europea (Put)
# P = K e^(-rT) N(-d2) - S0 N(-d1)

# donde:
# d1 = [ln(S0 / K) + (r + 1/2 σ^2) T] / (σ √T)
# d2 = d1 - σ √T
# N(·) es la función de distribución acumulativa de la distribución normal estándar
