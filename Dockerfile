# Capa 1: Imagen base
FROM python:3.9.7


# Capa 2: Instalar dependencias del sistema, incluyendo Redis
RUN apt-get update && apt-get install -y tzdata redis-server redis-tools && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Capa 3: Configurar el directorio de trabajo
WORKDIR /app

# Capa 4: Instalar tzdata para manejar zonas horarias
RUN apt-get update && apt-get install -y tzdata

# Establecer la zona horaria
ENV TZ=America/Argentina/Buenos_Aires
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Capa 4: Copiar solo el archivo de requisitos para aprovechar la caché
COPY src/requirements.txt .

# Capa 5: Instalar dependencias desde el archivo de requisitos
RUN pip install --no-cache-dir -r requirements.txt

# Capa 6: Copiar todo el código fuente
COPY src/ .


# Capa 7: Comando por defecto para ejecutar la aplicación
CMD ["python", "./app.py"]


