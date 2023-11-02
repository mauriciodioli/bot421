from models.usuario import Usuario
from models.cuentas import Cuenta
from models.ficha import Ficha
from models.logs import Logs
from datetime import datetime
from flask import Blueprint

creaTabla = Blueprint('creaTabla',__name__)

def crea_tabla_ficha():
    ficha = Ficha(           
        user_id = "1",
        cuenta_broker_id = "1083",
        activo = "True",
        token = "", 
        llave ='',
        monto_efectivo = 1.1,
        porcentaje_creacion = 10 ,
        valor_cuenta_creacion = 1.1,
        valor_cuenta_actual = 9.9,
        fecha_generacion = datetime(2023, 10, 5),
        interes = 10.5    
    )
    ficha.crear_tabla_ficha()
    print("Tabla creada!")

def crea_tabla_cuenta():
    cuenta = Cuenta(    
        id=1,
        user_id = "1",
        userCuenta="mauriciodioli6603",
        passwordCuenta="zbwitW5#",
        accountCuenta="REM6603",
        selector="simulado"                
    )
    cuenta.crear_tabla_cuentas()
    print("Tabla creada!")

def crea_tabla_logs():
    log = Logs(  
        user_id = "1",
        userCuenta="mauriciodioli6603",       
        accountCuenta="REM6603",
        fecha_log=datetime.now(),  # Aquí se carga la fecha actual
        ip='192.168.0.1',
        funcion='cualquiera',
        archivo='cualquiera',
        linea='1',
        error='cualquiera'               
    )
    log.crear_tabla_logs()
    print("Tabla creada!")
