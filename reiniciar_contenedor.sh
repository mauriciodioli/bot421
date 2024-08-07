#!/bin/bash

CONTAINER_NAME="202404"

# Función para verificar si el comando anterior fue exitoso
check_success() {
    if [ $? -ne 0 ]; then
        echo "Error: $1"
        exit 1
    fi
}

# Detener el contenedor (esto es opcional si el contenedor ya está detenido)
echo "Deteniendo el contenedor $CONTAINER_NAME..."
docker stop $CONTAINER_NAME
check_success "No se pudo detener el contenedor $CONTAINER_NAME."

# Esperar hasta que el contenedor se haya detenido completamente
echo "Esperando a que el contenedor se detenga..."
while [ "$(docker inspect -f '{{.State.Status}}' $CONTAINER_NAME)" != "exited" ]; do
    sleep 1
done

echo "Contenedor $CONTAINER_NAME detenido."

# Iniciar el contenedor
echo "Iniciando el contenedor $CONTAINER_NAME..."
docker start $CONTAINER_NAME
check_success "No se pudo iniciar el contenedor $CONTAINER_NAME."

echo "Contenedor $CONTAINER_NAME iniciado."
