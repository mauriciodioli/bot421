# main.py
import numpy as np
from scipy.signal import butter, filtfilt
import yfinance as yf
from arch import arch_model
from kalman_filter import apply_kalman_filter

# Obtener datos históricos del activo subyacente (por ejemplo, Apple)
data = yf.download('AAPL', start='2020-01-01', end='2023-01-01')

# Calcular los retornos diarios
returns = 100 * data['Close'].pct_change().dropna()

# Ajustar el modelo GARCH(1,1)
model = arch_model(returns, vol='Garch', p=1, q=1)
res = model.fit(disp="off")

# Previsión de volatilidad
forecast = res.forecast(horizon=5)
volatility_forecast_garch = np.sqrt(forecast.variance.values[-1, :])

# Aplicar filtro Butterworth para suavizar la volatilidad estimada
def butter_lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

cutoff_frequency = 0.1  # Frecuencia de corte para el filtro Butterworth
smoothed_volatility_garch = butter_lowpass_filter(volatility_forecast_garch, cutoff_frequency, fs=1.0)

# Aplicar el filtro de Kalman a la volatilidad estimada por GARCH
smoothed_volatility_kalman = apply_kalman_filter(volatility_forecast_garch)

# Mostrar resultados suavizados
print("Volatilidad suavizada con filtro Butterworth (GARCH):", smoothed_volatility_garch)
print("Volatilidad suavizada con filtro de Kalman:", smoothed_volatility_kalman)
