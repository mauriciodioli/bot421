# Instrucciones de Instalación y Configuración para el Proyecto "bot 421"

## Descripción

Sistema para la creación de red social de negocios.

## Instalación

### Modificaciones Necesarias

Antes de ejecutar el proyecto, realiza las siguientes modificaciones en los archivos:

#### En `app.py`

- **Configuración del Servidor Flask:**

  Comenta la línea para el modo de depuración y descomenta la línea para el modo de producción.

  ```python
  # Comentar esta línea
  app.run(host='0.0.0.0', port=5001, debug=True)

  # Descomentar esta línea
  app.run(host='0.0.0.0', port=5001, debug=False)
#### En aws.yml
Configuración de Host de AWS:
# ssh -i "bot421dbversion2.pem" ubuntu@ec2-44-223-20-210.compute-1.amazonaws.com
Comenta la primera línea de host de prueba y descomenta la línea de host de producción.
# Comentar la línea de host de prueba
EC2_HOST: ec2-18-207-114-83.compute-1.amazonaws.com # IMAGEN TEST

# Descomentar la línea de host de producción
EC2_HOST: ec2-44-223-20-210.compute-1.amazonaws.com # IMAGEN PRODUCCION
### En panelControl.py
Actualización de Datos en Panel de Control:

Comenta la línea de actualización de precios de prueba y descomenta la línea de actualización de precios de producción.

# Comentar la línea de actualización de precios de prueba
modifico = datoSheet.actualizar_precios(get.SPREADSHEET_ID_PRUEBA,'valores',pais)

# Descomentar la línea de actualización de precios de producción
modifico = datoSheet.actualizar_precios(get.SPREADSHEET_ID_PRODUCCION,'valores',pais)
### En get_login.py
Actualización de Datos de Acceso:

Comenta las líneas de datos de acceso de prueba y descomenta las líneas de datos de acceso de producción.
# Comentar las líneas de datos de acceso de prueba
CUENTA_ACTUALIZAR_SHEET = '44593'
CORREO_E_ACTUALIZAR_SHEET = 'madioli26@hotmail.com'
ID_USER_ACTUALIZAR_SHEET = 1

# Descomentar las líneas de datos de acceso de producción
CUENTA_ACTUALIZAR_SHEET = '10861'
CORREO_E_ACTUALIZAR_SHEET = 'dpuntillo@gmail.com'
ID_USER_ACTUALIZAR_SHEET = 2

### En .env
Configuración de Base de Datos:

Comenta la línea de base de datos de prueba y descomenta la línea de base de datos de producción.
# Comentar la línea de base de datos de prueba
MYSQL_DATABASE = base_dbbot421v02

# Descomentar la línea de base de datos de producción
MYSQL_DATABASE = flaskmysql

# Clona el repositorio
git clone https://github.com/mauriciodioli/bot421.git

# Entra en el directorio del proyecto
cd bot421

# Instala las dependencias
pip install -r requirements.txt
