#!/bin/bash

# Ruta para el servidor WebSocket
WEBSOCKET_DIR="$HOME/websocket_server"

echo "Iniciando configuración del servidor WebSocket..."

# Crear directorio para el servidor si no existe
if [ ! -d "$WEBSOCKET_DIR" ]; then
  echo "Creando directorio del servidor WebSocket..."
  mkdir -p "$WEBSOCKET_DIR"
fi

# Descargar el código del servidor WebSocket (si no existe)
if [ ! -f "$WEBSOCKET_DIR/server.py" ]; then
  echo "Descargando el servidor WebSocket..."
  cat > "$WEBSOCKET_DIR/server.py" << 'EOF'
import asyncio
import websockets
from subprocess import call

async def control_volumen(websocket, path):
    async for message in websocket:
        if message == "subir_volumen":
            print("Subiendo volumen...")
            # Comando para subir volumen en Linux/Android
            call(["amixer", "set", "Master", "5%+"])
        elif message == "bajar_volumen":
            print("Bajando volumen...")
            call(["amixer", "set", "Master", "5%-"])

start_server = websockets.serve(control_volumen, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
EOF
fi

# Actualizar paquetes del sistema
echo "Actualizando paquetes del sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar Python y pip si no están instalados
echo "Verificando Python y pip..."
if ! command -v python3 &> /dev/null; then
  echo "Instalando Python3..."
  sudo apt install python3 -y
fi

if ! command -v pip3 &> /dev/null; then
  echo "Instalando pip..."
  sudo apt install python3-pip -y
fi

# Instalar librerías necesarias para WebSocket
echo "Instalando dependencias del servidor WebSocket..."
pip3 install websockets

# Iniciar el servidor WebSocket
echo "Iniciando el servidor WebSocket..."
python3 "$WEBSOCKET_DIR/server.py" &
echo "Servidor WebSocket iniciado en el puerto 8765."

# Fin del script
