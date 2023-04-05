import mysql.connector

db = mysql.connector.connect(
  host='nombre_de_host',
  user='nombre_de_usuario',
  password='contraseña',
  database='nombre_de_base_de_datos'
)

cursor = db.cursor()

cursor.execute('''
  CREATE TABLE usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    correo_electronico VARCHAR(255) NOT NULL UNIQUE,
    token VARCHAR(255) NOT NULL,
    refresh_token VARCHAR(255) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT FALSE
  )
''')

db.close()
