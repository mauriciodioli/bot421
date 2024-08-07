#!/bin/bash

CONTAINER_NAME="202404"

# Detener el contenedor
echo "Deteniendo el contenedor $CONTAINER_NAME..."
docker stop $CONTAINER_NAME

# Esperar hasta que el contenedor se haya detenido
echo "Esperando a que el contenedor se detenga..."
while [ "$(docker inspect -f '{{.State.Running}}' $CONTAINER_NAME)" == "true" ]; do
    sleep 1
done

echo "Contenedor $CONTAINER_NAME detenido."

# Iniciar el contenedor
echo "Iniciando el contenedor $CONTAINER_NAME..."
docker start $CONTAINER_NAME

echo "Contenedor $CONTAINER_NAME iniciado."
