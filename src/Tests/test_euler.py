# Importar las bibliotecas necesarias
import numpy as np
import matplotlib.pyplot as plt
import io
from flask import Blueprint, make_response
import yfinance as yf
from arch import arch_model
from datetime import datetime, timedelta

# Inicializar el blueprint
test_euler = Blueprint('test_euler', __name__)

# Obtener datos históricos del activo subyacente (por ejemplo, Apple)
data = yf.download('AAPL', start='2020-01-01', end='2021-01-01')

# Calcular los cambios porcentuales de apertura
opens = 100 * data['Open'].pct_change().dropna()

# Función para normalizar los precios
def normalize_prices(prices):
    min_price = np.min(prices)
    max_price = np.max(prices)
    if max_price - min_price == 0:  # Evitar división por cero
        return np.zeros_like(prices)  # Todos los valores son iguales
    normalized = (prices - min_price) / (max_price - min_price)
    return 1 - normalized  # Para que el mínimo sea 1 y el máximo sea 0

# Normalizar precios de apertura
normalized_opens = normalize_prices(opens)

# Función para generar el gráfico
def generar_grafico_euler():
    # Inicializar listas para almacenar los resultados
    volatility_forecast_garch_open = []

    # Ajustar el modelo GARCH y pronosticar para cada día
    # Obtener las fechas desde los datos históricos
    fechas = data.index  # Utilizar el índice del DataFrame como las fechas

    for i in range(len(normalized_opens)):
        # Si hay suficientes datos, ajustar el modelo
        if i >= 20:  # Por ejemplo, usar los últimos 20 días para ajustar el modelo
            model_open = arch_model(normalized_opens[:i], vol='Garch', p=1, q=1)
            res_open = model_open.fit(disp="off")

            # Pronóstico de la volatilidad utilizando el modelo GARCH para un día
            forecast_open = res_open.forecast(horizon=1)  # Pronóstico para un día
            volatility_forecast_garch_open.append(np.sqrt(forecast_open.variance.values[-1, 0]))  # Guardar la volatilidad pronosticada
        else:
            volatility_forecast_garch_open.append(1)  # Asignar un valor por defecto si no hay suficientes datos

    # Crear la figura y ejes
    fig, ax = plt.subplots()
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')  # Fondo de la figura
    ax.set_facecolor('black')         # Fondo de los ejes

    # Cambiar el color de los ejes, las etiquetas y el título a blanco
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')

    # Etiquetas de los ejes
    ax.set_xlabel('Días')
    ax.set_ylabel('Pronóstico de Volatilidad GARCH')

    # Título de la gráfica
    ax.set_title('Gráfico de Identidad de Euler con Aperturas y GARCH')
    # Inicializar listas para almacenar los valores de seno y coseno
    real_part = []
    imaginary_part = []

    # Graficar en tiempo real
    for i in range(len(normalized_opens)):
        x_value_open = normalized_opens[i]

        real_part.append(np.cos(x_value_open))
        imaginary_part.append(np.sin(x_value_open))

         # Limpiar el eje para evitar sobrecargar los puntos anteriores
       # ax.clear()

        # Mantener el fondo negro y los ejes blancos en cada actualización
        ax.set_facecolor('black')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')

        # Volver a colocar las etiquetas y el título
        ax.set_xlabel('Días')
        ax.set_ylabel('Pronóstico de Volatilidad GARCH')
        ax.set_title('Gráfico de Identidad de Euler con Aperturas y GARCH')
        # Crear un objeto de texto para la fecha
        fecha_texto = ax.text(0.5, 1.05, '', fontsize=12, color='green', ha='center', va='bottom', transform=ax.transAxes)
        precio_texto = ax.text(0.7, 1.05, '', fontsize=12, color='yellow', ha='center', va='bottom', transform=ax.transAxes)

        # Graficar la parte real y la parte imaginaria hasta el punto actual
        ax.plot(real_part, imaginary_part, color='cyan')
        # Graficar líneas desde cada punto hasta el origen (0,0)
        for j in range(len(real_part)):
            ax.plot([real_part[j], 0], [imaginary_part[j], 0], color='red')  # Línea roja hacia el origen
        # Graficar líneas horizontales y verticales en cada punto
        ax.axhline(y=imaginary_part[-1], color='grey', linestyle='--', linewidth=0.5)  # Línea horizontal
        ax.axvline(x=real_part[-1], color='grey', linestyle='--', linewidth=0.5)  # Línea vertical
    # Mostrar la fecha correspondiente
        fecha_actual = fechas[i]  # Obtener la fecha actual del índice
        fecha_texto.set_text('____________')
        fecha_texto.set_text(fecha_actual.strftime('%Y-%m-%d'))  # Actualizar el texto de la fecha
       

       # ax.text(0.5, 1.05, fecha_actual.strftime('%Y-%m-%d'), fontsize=12, color='green', ha='center', va='bottom', transform=ax.transAxes)

        if i > 0:
            current_volatility = volatility_forecast_garch_open[i]
            max_convergence = max(volatility_forecast_garch_open[:i + 1])
            if current_volatility == max_convergence:
                # Aquí relacionamos el precio normalizado con el precio original
                precio_relacionado = data['Open'].iloc[i]  # Obtener el precio de apertura original
                precio_texto.set_text('____________') 
                precio_texto.set_text(f"${precio_relacionado:.2f}")  # Actualizar el texto del precio
                
                ax.text(real_part[-1], imaginary_part[-1], f"{precio_relacionado:.2f}", 
                        fontsize=12, color='yellow', ha='center', va='bottom', fontweight='bold')
             

        plt.pause(0.5)

    # Guardar la figura en un objeto BytesIO
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)  # Regresar al inicio del objeto BytesIO
    plt.close(fig)  # Cerrar la figura para liberar recursos
    return img

@test_euler.route('/test_eulerIdentidad')
def test_eulerIdentidad():
    img = generar_grafico_euler()
    response = make_response(img.read())
    response.headers.set('Content-Type', 'image/png')
    response.headers.set('Content-Disposition', 'inline', filename='euler_identidad.png')
    return response
