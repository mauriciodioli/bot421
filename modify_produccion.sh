#!/bin/bash

# Modificar app.py
sed -i "s/app.run(host='0\.0\.0\.0', port=5001, debug=True)/#app.run(host='0\.0\.0\.0', port=5001, debug=True)/g" src/app.py
sed -i "s/#app.run(host='0\.0\.0\.0', port=5001, debug=False)/app.run(host='0\.0\.0\.0', port=5001, debug=False)/g" src/app.py

# Modificar panelControl.py
sed -i "s/modifico = datoSheet.actualizar_precios(get.SPREADSHEET_ID_PRUEBA,'valores',pais)/#modifico = datoSheet.actualizar_precios(get.SPREADSHEET_ID_PRUEBA,'valores',pais)/g"  src/panelControlBroker/panelControl.py
sed -i "s/#modifico = datoSheet.actualizar_precios(get.SPREADSHEET_ID_PRODUCCION,'valores',pais)/modifico = datoSheet.actualizar_precios(get.SPREADSHEET_ID_PRODUCCION,'valores',pais)/g"  src/panelControlBroker/panelControl.py

sed -i "s/ContenidoSheet=datoSheet.leerSheet(get.SPREADSHEET_ID_PRUEBA,'bot')/#ContenidoSheet=datoSheet.leerSheet(get.SPREADSHEET_ID_PRUEBA,'bot')/g"  src/panelControlBroker/panelControl.py
sed -i "s/#ContenidoSheet=datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'bot')/ContenidoSheet=datoSheet.leerSheet(get.SPREADSHEET_ID_PRODUCCION,'bot')/g"  src/panelControlBroker/panelControl.py


# Modificar accionesSheet.py
sed -i "s/modifico = datoSheet.actualizar_precios(get.SPREADSHEET_ID_PRUEBA,'valores','argentina')/#modifico = datoSheet.actualizar_precios(get.SPREADSHEET_ID_PRUEBA,'valores','argentina')/g"  src/herramientasAdmin/accionesSheet.py
sed -i "s/#modifico = datoSheet.actualizar_precios(get.SPREADSHEET_ID_PRODUCCION,'valores','argentina')/modifico = datoSheet.actualizar_precios(get.SPREADSHEET_ID_PRODUCCION,'valores','argentina')/g"  src/herramientasAdmin/accionesSheet.py



# Modificar get_login
sed -i "s/CUENTA_ACTUALIZAR_SHEET = os.environ.get('CUENTA_ACTUALIZAR_SHEET')/#CUENTA_ACTUALIZAR_SHEET = os.environ.get('CUENTA_ACTUALIZAR_SHEET')/g" src/routes/api_externa_conexion/get_login.py
sed -i "s/CORREO_E_ACTUALIZAR_SHEET = os.environ.get('CORREO_E_ACTUALIZAR_SHEET')/#CORREO_E_ACTUALIZAR_SHEET = os.environ.get('CORREO_E_ACTUALIZAR_SHEET')/g" src/routes/api_externa_conexion/get_login.py
sed -i "s/ID_USER_ACTUALIZAR_SHEET = 1/#ID_USER_ACTUALIZAR_SHEET = 1/g" src/routes/api_externa_conexion/get_login.py

sed -i "s/#CUENTA_ACTUALIZAR_SHEET = os.environ.get('CUENTA_ACTUALIZAR_SHEET_PRODUCCION')/CUENTA_ACTUALIZAR_SHEET = os.environ.get('CUENTA_ACTUALIZAR_SHEET_PRODUCCION')/g" src/routes/api_externa_conexion/get_login.py
sed -i "s/#CORREO_E_ACTUALIZAR_SHEET = os.environ.get('CORREO_E_ACTUALIZAR_SHEET_PRODUCCION')/CORREO_E_ACTUALIZAR_SHEET = os.environ.get('CORREO_E_ACTUALIZAR_SHEET_PRODUCCION')/g" src/routes/api_externa_conexion/get_login.py
sed -i "s/#ID_USER_ACTUALIZAR_SHEET = 2/ID_USER_ACTUALIZAR_SHEET = 2/g" src/routes/api_externa_conexion/get_login.py

# Modificar .env
sed -i "s/MYSQL_DATABASE = flaskmysql/#MYSQL_DATABASE = flaskmysql/g" src/.env
sed -i "s/#MYSQL_DATABASE = base_dbbot421v02/MYSQL_DATABASE = base_dbbot421v02/g" src/.env

# Modificar aws.yml
sed -i "s/EC2_HOST: ec2-18-207-114-83.compute-1.amazonaws.com/#EC2_HOST: ec2-18-207-114-83.compute-1.amazonaws.com/g" .github/workflows/aws.yml
sed -i "s/#EC2_HOST: ec2-44-223-20-210.compute-1.amazonaws.com/EC2_HOST: ec2-44-223-20-210.compute-1.amazonaws.com/g" .github/workflows/aws.yml

# Eliminar el contenido del archivo logs.log
> logs.log

echo "Configuraciones aplicadas con éxito."
