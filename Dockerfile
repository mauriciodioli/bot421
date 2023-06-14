FROM ubuntu:latest

# Instala los paquetes necesarios para XAMPP
RUN apt-get update && apt-get install -y \
    wget \
    apache2 \
    php \
    libapache2-mod-php \
    php-mysql \
    php-curl \
    php-gd \
    php-json \
    php-mbstring \
    php-xml \
    php-zip \
    && rm -rf /var/lib/apt/lists/*

# Descarga e instala XAMPP
RUN wget https://www.apachefriends.org/xampp-files/8.0.9/xampp-linux-x64-8.0.9-0-installer.run && \
    chmod +x xampp-linux-x64-8.0.9-0-installer.run && \
    ./xampp-linux-x64-8.0.9-0-installer.run --mode unattended && \
    rm xampp-linux-x64-8.0.9-0-installer.run

# Instala MySQL
RUN apt-get update && apt-get install -y mysql-server

# Agrega el archivo requirements.txt
COPY src/requirements.txt /app/requirements.txt

# Crea un entorno virtual y activa el entorno
RUN apt-get install -y python3-venv
RUN python3 -m venv /app/env
ENV PATH="/app/env/bin:$PATH"
RUN . /app/env/bin/activate

# Instala los paquetes necesarios
RUN pip install -r /app/requirements.txt

# Abre los puertos necesarios para XAMPP y MySQL
EXPOSE 80 443 3306

# Arranca XAMPP y MySQL
CMD ["/opt/lampp/xampp", "start"] && service mysql start
