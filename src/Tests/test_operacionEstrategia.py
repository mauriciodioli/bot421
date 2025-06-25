import os

# Construir la ruta al archivo operacionEstrategia.py
file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'operacionEstrategia.py'))

# La línea que deseas verificar
line_to_check = "self.pyRofexInicializada.send_order_via_websocket"

# Función para verificar si la línea está comentada
def is_line_commented(file_path, line_to_check):
    with open(file_path, 'r') as file:
        for line in file:
            stripped_line = line.strip()
            if stripped_line.startswith("#") and line_to_check in stripped_line:
                return True
    return False

# Verificar si la línea está comentada
def test_line_not_commented():
    if is_line_commented(file_path, line_to_check):
        print(f"La línea '{line_to_check}' está comentada.")
    else:
        print(f"La línea '{line_to_check}' no está comentada.")

# Llamar a la función de prueba
test_line_not_commented()
