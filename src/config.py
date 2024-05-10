from dotenv import load_dotenv
import os

load_dotenv()

user = os.environ["MYSQL_USER"]
password = os.environ["MYSQL_PASSWORD"]
host = os.environ["MYSQL_HOST"]
database = os.environ["MYSQL_DATABASE"]
port = os.environ["MYSQL_PORT"]  # Asegúrate de tener la variable de entorno MYSQL_PORT configurada



#DATABASE_CONNECTION_URI = f'mysql+pymysql://{user}:{password}@{host}/{database}'
DATABASE_CONNECTION_URI = f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}'
#print(DATABASE_CONNECTION_URI)