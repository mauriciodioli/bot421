<<<<<<< HEAD
#!/bin/bash

echo "Iniciando la configuración completa del sistema WebSocket..."

# Dar permisos de ejecución a todos los scripts
echo "Otorgando permisos de ejecución a los scripts..."
chmod +x configure_websocket.sh
chmod +x start_server.sh
chmod +x start_websocket.sh

# Ejecutar el script de configuración
echo "Ejecutando configure_websocket.sh..."
bash configure_websocket.sh

# Ejecutar el script para iniciar el servidor WebSocket
echo "Ejecutando start_server.sh..."
bash start_server.sh

# Ejecutar el script principal para iniciar todo
echo "Ejecutando start_websocket.sh..."
bash start_websocket.sh

echo "Configuración completa. WebSocket en funcionamiento."
=======
#!/bin/bash

echo "Iniciando la configuración completa del sistema WebSocket..."

# Dar permisos de ejecución a todos los scripts
echo "Otorgando permisos de ejecución a los scripts..."
chmod +x configure_websocket.sh
chmod +x start_server.sh
chmod +x start_websocket.sh

# Ejecutar el script de configuración
echo "Ejecutando configure_websocket.sh..."
bash configure_websocket.sh

# Ejecutar el script para iniciar el servidor WebSocket
echo "Ejecutando start_server.sh..."
bash start_server.sh

# Ejecutar el script principal para iniciar todo
echo "Ejecutando start_websocket.sh..."
bash start_websocket.sh

echo "Configuración completa. WebSocket en funcionamiento."
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
