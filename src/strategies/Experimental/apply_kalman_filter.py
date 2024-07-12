import csv
from scipy.signal import butter, filtfilt
from arch import arch_model
import requests
from io import StringIO

# Definir los parámetros
symbol = 'GOOG'
start_date = '2020-01-01'
end_date = '2024-07-01'

# Construir la URL para obtener datos históricos de Google Finance
url = f"https://finance.google.com/finance/historical?q={symbol}&startdate={start_date}&enddate={end_date}&output=csv"

# Descargar los datos como texto CSV
response = requests.get(url)
csv_data = response.text

# Parsear los datos CSV manualmente
data = []
for line in csv_data.strip().split('\n'):
    row = line.split(',')
    if row[0] != 'Date':  # Ignorar la primera línea de encabezado
        date = row[0]
        close_price = float(row[4])  # Precio de cierre
        data.append((date, close_price))

# Calcular los retornos diarios
returns = []
for i in range(1, len(data)):
    date_prev, close_prev = data[i-1]
    date, close = data[i]
    daily_return = 100 * (close - close_prev) / close_prev
    returns.append(daily_return)

# Ajustar el modelo GARCH(1,1)
model = arch_model(returns, vol='Garch', p=1, q=1)
res = model.fit(disp="off")

# Previsión de volatilidad
forecast = res.forecast(horizon=5)
volatility_forecast_garch = (forecast.variance.values[-1, :])**0.5  # Calculando la raíz cuadrada para obtener la volatilidad

# Funciones para el filtro Butterworth
def butter_lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

# Aplicar filtro Butterworth para suavizar la volatilidad estimada por GARCH
cutoff_frequency = 0.1  # Frecuencia de corte para el filtro Butterworth
fs = 1.0  # Frecuencia de muestreo (puedes ajustar según sea necesario)
smoothed_volatility_garch = butter_lowpass_filter(volatility_forecast_garch, cutoff_frequency, fs=fs, order=5)

# Mostrar resultados suavizados
print("Volatilidad suavizada con filtro Butterworth (GARCH):", smoothed_volatility_garch)
