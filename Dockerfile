FROM python:3.9.7

WORKDIR /app

COPY src/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Desinstalar la biblioteca requests
RUN pip uninstall -y requests

# Volver a instalar la biblioteca requests
RUN pip install --no-cache-dir requests

COPY src/ .

CMD ["python", "./app.py"]
