FROM python:3.9.7

WORKDIR /app

COPY src/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Desinstalar la biblioteca requests
RUN pip uninstall -y requests

COPY src/ .

CMD ["python", "./app.py"]
