FROM python:3.9.0

WORKDIR /usr/src/app

# Copiar primero solo el archivo requirements.txt para aprovechar el caché de Docker
COPY src/requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Ahora copiar el resto de los archivos
COPY . .

# Resto del Dockerfile...
