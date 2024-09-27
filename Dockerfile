# Capa 1: Imagen base
FROM python:3.9.7

# Capa 2: Configurar el directorio de trabajo
WORKDIR /app

# Capa 3: Crear un entorno virtual
RUN python -m venv /opt/venv

# Capa 4: Establecer la ruta del entorno virtual en las variables de entorno
ENV PATH="/opt/venv/bin:$PATH"

# Capa 5: Copiar solo el archivo de requisitos para aprovechar la caché
COPY src/requirements.txt .

# Capa 6: Actualizar pip y luego instalar dependencias desde el archivo de requisitos
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Capa 7: Desinstalar y volver a instalar la biblioteca requests
RUN pip uninstall -y requests && pip install --no-cache-dir requests

# Capa 8: Copiar todo el código fuente
COPY src/ .

# Capa 9: Comando por defecto para ejecutar la aplicación
CMD ["python", "./app.py"]
