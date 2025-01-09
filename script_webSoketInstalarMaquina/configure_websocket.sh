#!/bin/bash

echo "Iniciando configuración para autoinicio del servidor WebSocket..."

# Asegurarse de que el script principal sea ejecutable
echo "Haciendo ejecutable el script start_websocket.sh..."
chmod +x start_websocket.sh

# Configurar cron para Linux
echo "Configurando crontab para ejecución al inicio del sistema..."
(crontab -l 2>/dev/null; echo "@reboot $(pwd)/start_websocket.sh") | crontab -

# Configuración específica para Termux
if [ -d "$HOME/.termux" ]; then
  echo "Configurando Termux para iniciar automáticamente..."
  pkg install termux-services -y
  mkdir -p $HOME/.termux/boot
  echo "bash $(pwd)/start_websocket.sh" > $HOME/.termux/boot/start_websocket.sh
  chmod +x $HOME/.termux/boot/start_websocket.sh
fi

echo "Configuración completada."
