from dotenv import load_dotenv
import os

load_dotenv()

user = os.environ["MYSQL_USER"]
password = os.environ["MYSQL_PASSWORD"]
host = os.environ["MYSQL_HOST"]
database = os.environ["MYSQL_DATABASE"]
port = os.environ["MYSQL_PORT"]  # Asegúrate de tener la variable de entorno MYSQL_PORT configurada



#DATABASE_CONNECTION_URI = f'mysql+pymysql://{user}:{password}@{host}/{database}'
#DATABASE_CONNECTION_URI = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
DATABASE_CONNECTION_URI = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_POOL_RECYCLE = 280
SQLALCHEMY_POOL_TIMEOUT = 20
SQLALCHEMY_POOL_SIZE = 5
SQLALCHEMY_MAX_OVERFLOW = 10
#print(DATABASE_CONNECTION_URI)

# Obtener las variables de entorno
sdk_prueba = os.getenv('sdk_prueba')#test
sdk_produccion = os.getenv('sdk_produccion') #test
MERCADOPAGO_KEY_API = os.getenv('MERCADOPAGO_KEY_API')#para produccion
MERCADOPAGO_URL = os.getenv('MERCADOPAGO_URL')
DOMAIN = os.getenv('DOMAIN')




# Configuración de Redis
redis_host = os.environ["REDIS_HOST"]
redis_port = os.environ["REDIS_PORT"]
redis_db = os.environ["REDIS_DB"]




