from pykalman import KalmanFilter

def apply_kalman_filter(volatility_forecast):
    # Preparar datos para el filtro de Kalman
    observed_volatility = volatility_forecast[:]
    initial_state_mean = [observed_volatility[0]]
    transition_matrix = [[1]]
    observation_matrix = [[1]]
    observation_covariance = [[0.01]]
    transition_covariance = [[0.01]]
    initial_state_covariance = [[0.01]]

    # Crear y ajustar el filtro de Kalman
    kf = KalmanFilter(
        initial_state_mean=initial_state_mean,
        initial_state_covariance=initial_state_covariance,
        transition_matrices=transition_matrix,
        observation_matrices=observation_matrix,
        observation_covariance=observation_covariance,
        transition_covariance=transition_covariance
    )

    # Aplicar el filtro de Kalman a la volatilidad observada
    smoothed_state_means, _ = kf.smooth(observed_volatility)

    # Devolver los resultados suavizados con el filtro de Kalman
    return smoothed_state_means.ravel().tolist()
