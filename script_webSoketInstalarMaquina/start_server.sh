<<<<<<< HEAD
#!/bin/bash

# Ruta al directorio del servidor WebSocket
WEBSOCKET_DIR="$HOME/websocket_server"

echo "Iniciando el servidor WebSocket..."

# Ejecutar el servidor y redirigir logs
python3 "$WEBSOCKET_DIR/server.py" > "$WEBSOCKET_DIR/server.log" 2>&1 &

echo "Servidor WebSocket iniciado. Logs disponibles en $WEBSOCKET_DIR/server.log."
=======
#!/bin/bash

# Ruta al directorio del servidor WebSocket
WEBSOCKET_DIR="$HOME/websocket_server"

echo "Iniciando el servidor WebSocket..."

# Ejecutar el servidor y redirigir logs
python3 "$WEBSOCKET_DIR/server.py" > "$WEBSOCKET_DIR/server.log" 2>&1 &

echo "Servidor WebSocket iniciado. Logs disponibles en $WEBSOCKET_DIR/server.log."
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
