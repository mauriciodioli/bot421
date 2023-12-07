FROM python:3.9.7

WORKDIR /src

# Copiar el contenido de la carpeta "src" al directorio de trabajo en el contenedor
COPY src .

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "-u", "app.py"]