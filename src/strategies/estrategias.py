from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify,current_app
import routes.instrumentosGet as instrumentosGet
from sqlalchemy.exc import OperationalError
import requests
from utils.db import db
import routes.api_externa_conexion.get_login as get
import routes.api_externa_conexion.validaInstrumentos as val
from routes.api_externa_conexion.cuenta import obtenerSaldoCuenta
import routes.instrumentos as inst
import strategies.gestion_estrategias.unidad_trader as utABM

from datetime import datetime
import enum
from models.instrumentoEstrategiaUno import InstrumentoEstrategiaUno
from models.triggerEstrategia import TriggerEstrategia
from models.brokers import Broker
from models.usuario import Usuario
from models.cuentas import Cuenta
from models.ficha import Ficha
from models.unidadTrader import UnidadTrader
from fichasTokens.fichas import crear_ficha
import tokens.token as Token
from models.administracion.altaEstrategiaApp import AltaEstrategiaApp

import jwt
import os
import re
import socket

estrategias = Blueprint('estrategias',__name__)

       
class States(enum.Enum):
    WAITING_MARKET_DATA = 0
    WAITING_CANCEL = 1
    WAITING_ORDERS = 2


@estrategias.route("/estrategias-usuario-general/",  methods=["GET"])
def estrategias_usuario_general():
    try:
      if request.method == 'GET': 
      # Obtener todos los TriggerEstrategia
        estrategias = db.session.query(TriggerEstrategia).all()

        # Crear un diccionario para almacenar las unidades filtradas por trigger_id
        ut_por_trigger = {}

       
        db.session.close()
        ut_por_trigger = {}
        
        for trigger in estrategias:
            # Obtener 'ut' para el trigger actual
            ut_objects = db.session.query(UnidadTrader).filter_by(trigger_id=trigger.id).all()
            
            # Inicializar una lista para almacenar los valores de 'ut'
            ut_values = []
            
            # Iterar sobre los objetos UnidadTrader y recopilar los valores de 'ut'
            for ut_object in ut_objects:
                ut_values.append(ut_object.ut)
                print("Valor de 'ut':", ut_object.ut)
            
            # Asignar los valores de 'ut' al atributo 'ut' del objeto 'trigger'
            if not ut_values:
                # Si la lista está vacía, asignar 0 al atributo 'ut'
                trigger.ut = 0
            else:
                # Si la lista no está vacía, asignar los valores recopilados al atributo 'ut'
                trigger.ut =  ut_object.ut
        
      
        return render_template("/estrategias/panelControEstrategiaUser.html", datos=[0,estrategias], layout='layout')

          
    except:
       print('no hay usuarios') 
    return 'problemas con la base de datos'


def estrategias_usuario_nadmin_desde_endingOperacionBot(account, usuario_id):
    try:
        # Consulta de estrategias
        estrategias = db.session.query(TriggerEstrategia).join(Usuario).filter(
            TriggerEstrategia.user_id == usuario_id, 
            TriggerEstrategia.accountCuenta == account
        ).all()

        ut_por_trigger = {}

        for trigger in estrategias:
            # Obtener 'ut' para el trigger actual
            ut_objects = db.session.query(UnidadTrader).filter_by(trigger_id=trigger.id).all()
            
            # Inicializar una lista para almacenar los valores de 'ut'
            ut_values = [ut_object.ut for ut_object in ut_objects]
            
            # Asignar los valores de 'ut' al atributo 'ut' del objeto 'trigger'
            trigger.ut = sum(ut_values) if ut_values else 0

        # Renderizar la plantilla con los datos
        return render_template(
            "/estrategias/panelControEstrategiaUser.html", 
            datos=[usuario_id, estrategias], 
            layout='layoutConexBroker'
        )
    
    except Exception as e:
        print(f'Error en estrategias_usuario_nadmin_desde_endingOperacionBot: {e}')
        return render_template("/notificaciones/errorEstrategiaABM.html")

    finally:
        # Asegurarse de cerrar la sesión
        db.session.remove()








@estrategias.route("/estrategias-usuario-nadmin",  methods=["POST"])
def estrategias_usuario_nadmin():
    try:
      if request.method == 'POST': 
          access_token = request.form.get('estrategias_accessToken') 
          refreshToken = request.form.get("estrategias_refreshToken")
          account = request.form.get("estrategias_accounCuenta")
          if access_token and Token.validar_expiracion_token(access_token=access_token): 
            app = current_app._get_current_object()  
            
            usuario_id = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']                    
            estrategias = db.session.query(TriggerEstrategia).join(Usuario).filter(TriggerEstrategia.user_id == usuario_id, TriggerEstrategia.accountCuenta == account).all()
          
         
            db.session.close()
            ut_por_trigger = {}
            try:
                reporte = obtenerSaldoCuenta(account=account)
                resumenCuenta = reporte.get("availableToCollateral", 0)  # Obtener el valor, o 0 si no existe la clave
            except Exception as e:
                resumenCuenta = 0  # En caso de error, asignar 0

            # Verificar si el valor es None o 0
            if resumenCuenta is None or resumenCuenta == 0:
                resumenCuenta = 0    
            for trigger in estrategias:
                # Obtener 'ut' para el trigger actual
                ut_objects = db.session.query(UnidadTrader).filter_by(trigger_id=trigger.id).all()
                
                # Inicializar una lista para almacenar los valores de 'ut'
                ut_values = []
                
                # Iterar sobre los objetos UnidadTrader y recopilar los valores de 'ut'
                for ut_object in ut_objects:
                    ut_values.append(ut_object.ut)
                    print("Valor de 'ut':", ut_object.ut)
                
                # Asignar los valores de 'ut' al atributo 'ut' del objeto 'trigger'
                if not ut_values:
                    # Si la lista está vacía, asignar 0 al atributo 'ut'
                    trigger.ut = 0
                else:
                    # Si la lista no está vacía, asignar los valores recopilados al atributo 'ut'
                    trigger.ut =  ut_object.ut
        
# Ahora cada objeto en 'trigger_estrategias' tiene un atributo 'ut' que contiene los valores de 'ut' asociados, o 0 si no hay ningún valor

           
                   
            #return render_template("/estrategias/panelControEstrategiaUser.html",datos = [usuario_id,ut_por_trigger])
            return render_template("/estrategias/panelControEstrategiaUser.html",datos = [usuario_id,estrategias],resumenCuenta=resumenCuenta, layout='layoutConexBroker')
          else:
               return render_template('notificaciones/tokenVencidos.html', layout='layout')  
    except:
       print('no hay estrategias en strategies/estrategias.py') 
    return  render_template("/notificaciones/errorEstrategiaABM.html")


@estrategias.route("/estrategias-usuario",  methods=["POST"])
def estrategias_usuario():
    try:
      if request.method == 'POST': 
            usuario_id = request.form['usuario_id']                      
            estrategias = db.session.query(TriggerEstrategia).join(Usuario).filter(TriggerEstrategia.user_id == usuario_id).all()
            db.session.close()
            for estrategia in estrategias:
                print("ID:", estrategia.id)
                print("Name:", estrategia.userCuenta)
                # Print other attributes as needed
                print()
            return render_template("/estrategias/panelControEstrategiaUser.html",datos = [usuario_id,estrategias],resumenCuenta='', layout='layoutConexBroker')
    
    except:
       print('no hay estrategias') 
    return  render_template("/notificaciones/errorEstrategiaVacia.html")

def eliminarArhivoEstrategia(nombreEstrategia):    
       # Construye la ruta al archivo
    ruta_archivo = os.path.join("src", "strategies/estrategiasUsuarios", nombreEstrategia + ".py")
    
    try:
        # Intenta eliminar el archivo
        os.remove(ruta_archivo)
        print(f"Archivo {nombreEstrategia}.py eliminado correctamente.")
    except FileNotFoundError:
        # Si el archivo no existe, muestra un mensaje de error
        print(f"El archivo {nombreEstrategia}.py no existe.")
    except Exception as e:
        # Si ocurre un error inesperado, muestra el mensaje de error
        print(f"Error al intentar eliminar el archivo {nombreEstrategia}.py: {e}")

def modificar_app_elimina_estrategia(nombreEstrategia):
    
    path_app_modelo = os.path.join(os.getcwd(), 'app.py')
    
    try:
        # Leer el contenido del archivo original
        with open(path_app_modelo, "r", encoding="utf-8") as archivo_entrada:
            lineas = archivo_entrada.readlines()

        # Filtrar las líneas que no contienen la cadena
        lineas_filtradas = [linea for linea in lineas if nombreEstrategia not in linea]

        # Escribir el contenido filtrado de vuelta al archivo
        with open(path_app_modelo, "w", encoding="utf-8") as archivo_salida:
            archivo_salida.writelines(lineas_filtradas)
            
        print(f"Líneas que contienen '{nombreEstrategia}' eliminadas correctamente.")
    except FileNotFoundError:
        print(f"El archivo {path_app_modelo} no existe.")
    except Exception as e:
        print(f"Error al intentar eliminar las líneas que contienen '{nombreEstrategia}': {e}")
        
@estrategias.route("/eliminar-trigger/",  methods=["POST"])
def eliminar_trigger():
    IdTrigger = request.form['IdTrigger']   
    usuario_id = request.form['user_id']
    access_token = request.form['eliminarEstrategiaToken']
    account = request.form['eliminarEstrategiaCuenta']
    if access_token and Token.validar_expiracion_token(access_token=access_token): 
        Trigger = db.session.query(TriggerEstrategia).get(IdTrigger)
        utABM.eliminarUT(IdTrigger)
        eliminarArhivoEstrategia(Trigger.nombreEstrategia)
        
        db.session.delete(Trigger)
        db.session.commit()
        
        
        flash('Trigger eliminado correctamente.')
        estrategias = db.session.query(TriggerEstrategia).filter_by(accountCuenta=account).all()
      
        db.session.close()   
        return render_template("/estrategias/panelControEstrategiaUser.html",datos = [usuario_id,estrategias],resumenCuenta='', layout='layoutConexBroker')
    else:
         flash('El token a expirado')
         return render_template('notificaciones/tokenVencidos.html',layout = 'layout') 
@estrategias.route("/editar-trigger-nombre", methods=["POST"])
def editar_trigger_nombre():
    IdTrigger = request.form['IdTrigger']
    usuario_id = request.form['usuario_id']  
    
    Trigger = TriggerEstrategia.query.get(IdTrigger)
    Trigger.nombreEstrategia = request.form['TriggerNombre']
   
    db.session.commit()
   
    flash('Estrategia editado correctamente.')
    
    estrategias = db.session.query(TriggerEstrategia).all()
    db.session.close()
    return render_template("/estrategias/panelControEstrategiaUser.html",datos = [usuario_id,estrategias],resumenCuenta='', layout='layoutConexBroker')
    
@estrategias.route("/editar-Trigger/", methods = ["POST"] )
def editar_Trigger():
    try:
        if request.method == 'POST':
            usuario_id = request.form['user_id']
            IdTrigger = request.form['IdTrigger']
            horaInicio = request.form['horaInicio']  
            horaFin = request.form['horaFin']  
            ManualAutomatico = request.form['ManualAutomatico'] 
            
            horaInicioSalvar, minutosInicioSalvar = horaInicio.split(':')
            horaFinSalvar, minutosFinSalvar = horaFin.split(':')
            hora_inicio = datetime(year=2023, month=7, day=3, hour=int(horaInicioSalvar), minute=int(minutosInicioSalvar))
            hora_fin = datetime(year=2023, month=7, day=3, hour=int(horaFinSalvar), minute=int(minutosFinSalvar))
            
            
            Trigger = TriggerEstrategia.query.get(IdTrigger)            
            Trigger.ManualAutomatico = ManualAutomatico
            Trigger.horaInicio = hora_inicio
            Trigger.horaFin = hora_fin
            
            db.session.commit()
            
            flash('Estrategia editada correctamente.')
            estrategias = db.session.query(TriggerEstrategia).all()
            db.session.close()
            return render_template("/estrategias/panelControEstrategiaUser.html",datos = [usuario_id,estrategias],resumenCuenta='', layout='layoutConexBroker')
                    
    except:
                print('no hay estrategias')
    return render_template("/notificaciones/errorEstrategiaVacia.html")



def altaEstrategiaApp(account, nombreEstrategia):
    try:
        # Verificar si ya existe una estrategia con el mismo nombre
        existing_estrategia = db.session.query(AltaEstrategiaApp).filter_by(nombreEstrategia=nombreEstrategia).first()
        
        # Si existe una estrategia con el mismo nombre, no agregar y retornar False
        if existing_estrategia:
            print(f"Estrategia con nombre '{nombreEstrategia}' ya existe.")
            return False

        # Obtener la fecha actual como una cadena de texto
        fecha_actual_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Crear una instancia de AltaEstrategiaApp
        estrategia = AltaEstrategiaApp(
            id=None,
            accountCuenta=account,
            nombreEstrategia=nombreEstrategia,
            estado='INICIADO',
            descripcion='NO SE AGREGÓ AÚN',
            fecha=fecha_actual_str
        )

        # Agregar la instancia de AltaEstrategiaApp a la sesión
        db.session.add(estrategia)
        # Confirmar los cambios
        db.session.commit()

        return True

    except OperationalError as e:
        # Manejar la excepción de error operacional (tabla ya existe)
        print("Error al intentar agregar la estrategia:", e)
        return False
    except Exception as e:
        # Manejar cualquier otra excepción
        print("Error inesperado:", e)
        return False








def agregar_estrategia_nueva_app(nombreEstrategia):
    try:
        # Ruta del archivo a leer
        path_app_modelo = os.path.join(os.getcwd(), 'app.py')

        # Leer el contenido del archivo original
        with open(path_app_modelo, "r", encoding="utf-8") as archivo_entrada:
            contenido = archivo_entrada.readlines()

        # Definir las nuevas líneas
        nueva_linea = 'from strategies.estrategiasUsuarios.' + nombreEstrategia + ' import ' + nombreEstrategia + '\n'
        nueva_linea2 = 'app.register_blueprint(' + nombreEstrategia + ')\n'

        # Encontrar la línea que contiene '*****************'
        linea_referencia1 = None
        linea_referencia2 = None

        # Encuentra la primera referencia
        for i, linea in enumerate(contenido):
            if '######################zona de estrategias de usuarios####################' in linea:
                linea_referencia1 = i
                # Verificar si la siguiente línea está en blanco
                if i + 1 < len(contenido) and contenido[i + 1].strip() == "":
                    linea_referencia1 = i+1
                    print("La próxima línea está en blanco.")
                break
        # Encuentra la segunda referencia
        for i, linea in enumerate(contenido):
            if '#####################zona blueprin de usuarios##############' in linea:
                linea_referencia2 = i
                 # Verificar si la siguiente línea está en blanco
                if i + 1 < len(contenido) and contenido[i + 1].strip() == "":
                    linea_referencia2 = i+1
                    print("La próxima línea está en blanco.")
                break

        #Verifica si se encontraron las referencias
        if linea_referencia1 is not None and linea_referencia2 is not None:
            # Inserta la primera línea en la posición encontrada
           # if linea_referencia1 + 1 < len(contenido) and contenido[linea_referencia1 + 1].strip():
            #    contenido.insert(linea_referencia1 + 1, '\n')
            contenido.insert(linea_referencia1 + 1, nueva_linea)
            
            # Calcula la nueva posición de inserción para la segunda línea
            if linea_referencia2 > linea_referencia1:
                linea_referencia2 += 1
            
            # Inserta la segunda línea en la posición encontrada
           # if linea_referencia2 + 1 < len(contenido) and contenido[linea_referencia2 + 1].strip():
           #     contenido.insert(linea_referencia2 + 1, '\n')
            contenido.insert(linea_referencia2 + 1, nueva_linea2)

            # Escribir el contenido modificado de vuelta al archivo
            with open(path_app_modelo, "w", encoding="utf-8") as archivo_salida:
                archivo_salida.writelines(contenido)
        else:
            # Manejar caso donde no se encontraron las referencias
            print("No se encontraron las referencias necesarias en el archivo.")

    except Exception as e:
        print("Error al agregar la estrategia nueva al archivo:", e)







def generarArchivoEstrategia(nombreEstrategia,ruta_estrategia,archivoEstrategia):
    try:
        # Ruta del archivo a leer
        path_estrategia_modelo = os.path.join(os.getcwd(), 'strategies/'+archivoEstrategia+'.py')

        # Leer el contenido del archivo original
        with open(path_estrategia_modelo, "r", encoding="utf-8") as archivo_entrada:
            contenido = archivo_entrada.read()
        # Patrón de expresión regular para coincidir con la cadena exacta
        patron = r'(?<![-/])\b' + re.escape(archivoEstrategia) + r'\b(?![-/])'

        # Realizar el reemplazo solo en coincidencias exactas
         # Reemplazar la cadena "estrategiaSheetWS" con el contenido de nombreEstrategia
        contenido_modificado = re.sub(patron, nombreEstrategia, contenido)
     

        
        # Ruta del  # Reemplazar la definición de la función con el nuevo nombre
        nuevo_nombre_funcion = nombreEstrategia.replace("_", "")
        nombre_estrategia = ruta_estrategia.replace("-", "_")
        contenido_modificado = contenido_modificado.replace("def "+nombre_estrategia+"():", f"def {nuevo_nombre_funcion}():")
        
       # Reemplazar la cadena "estrategia-002" con el contenido de nombreEstrategia
        nombreEstrategiaNuevo = nombreEstrategia.replace("_", "-")
        contenido_modificado = contenido_modificado.replace(ruta_estrategia, nombreEstrategiaNuevo)
       
       # Arma la nueva direccion a donde guardar
        nuevo_path_estrategia_modelo = path_estrategia_modelo.replace(archivoEstrategia+'.py', "estrategiasUsuarios")
        directorio_destino = os.path.join(os.getcwd(), nuevo_path_estrategia_modelo)

        # Ruta del nuevo archivo
        nombreNuevo_py = nombreEstrategia+'.py'
        ruta_nuevo_archivo = os.path.join(directorio_destino, nombreNuevo_py)

        # Si el directorio de destino no existe, lo creamos
        if not os.path.exists(directorio_destino):
            os.makedirs(directorio_destino)

        # Verificar si ya existe un archivo con el mismo nombre
        if os.path.exists(ruta_nuevo_archivo):
            raise FileExistsError(f"El archivo '{nombreEstrategia}' ya existe.")

        # Escribir el contenido modificado en el nuevo archivo
        with open(ruta_nuevo_archivo, "w", encoding="utf-8") as archivo_salida:
            archivo_salida.write(contenido_modificado)

        print(f"Archivo '{nombreEstrategia}' creado exitosamente.")
        return None  # No hay error, así que devolvemos None

    except Exception as e:
        print(f"Se produjo un error: {e}")
        return e  # Devolvemos el error encontrado

@estrategias.route("/alta-estrategias-trig", methods=["POST"])
def alta_estrategias_trig():
    try:
        if request.method == 'POST':
            user_id = request.form['usuario_id']          
            correo_electronico = request.form['correo_electronico_form_altaEstrategia']
            account = request.form['cuenta']
            access_token = request.form['access_token_form_altaEstrategia']
            layouts = request.form['layoutOrigen']
            archivoEstrategia = request.form['estrategia']
            #nombreEstrategia = request.form['nombreEstrategia']
            cuentas = db.session.query(Cuenta).filter_by(user_id=user_id, accountCuenta=account).first()
            nombre_broker = db.session.query(Broker.nombre).filter_by(id=cuentas.broker_id).first()
            estrategias = db.session.query(TriggerEstrategia).filter_by(accountCuenta=account).all()
            ruta_estrategia = archivoEstrategia+'-001'
            if estrategias is None or  len(estrategias) == 0:
                if nombre_broker:
                    
                    nombre_broker = nombre_broker[0].replace(" ", "_")
                    nombreEstrategia = nombre_broker+'_'+account+'_001'
                   
            else:    
                # Lista para almacenar los nombres
                # Lista para almacenar los últimos tres números de los nombres
                ultimos_tres_numeros = []

                # Itera sobre los resultados y extrae los tres últimos dígitos de cada nombre
                for trigger_estrategia in estrategias:
                    nombre = trigger_estrategia.nombreEstrategia
                    # Supongamos que los tres últimos números están al final del nombre
                    numero = nombre[-3:]  # Extrae los últimos tres caracteres del nombre
                    ultimos_tres_numeros.append(numero)
                # Encuentra el número más alto en la lista ultimos_tres_numeros
            # Convierte los números de cadena a enteros
                numeros_enteros = [int(numero) for numero in ultimos_tres_numeros]

                # Encuentra el número más alto en la lista numeros_enteros
                numero_mas_alto = max(numeros_enteros) 
                # Convertir a entero, sumar uno y convertir de nuevo a cadena
                numero_nuevo = str(int(numero_mas_alto) + 1)

                # Asegurarse de que el número tenga tres dígitos utilizando zfill
                numero_nuevo = numero_nuevo.zfill(3) 
            
                nombre_broker = nombre_broker[0].replace(" ", "_")

                nombreEstrategia = nombre_broker+'_'+account+'_'+numero_nuevo
              
           
            generarArchivoEstrategia(nombreEstrategia,ruta_estrategia,archivoEstrategia)
           
            #######################################################################
            # Aquí cargo los datos a la tabla para actualizar app.py#
            #######################################################################
            
            altaEstrategiaApp(account,nombreEstrategia)
         
            if cuentas:
                print("Datos de la cuenta:")
                print("ID:", cuentas.id)
                print("User ID:", cuentas.user_id)
                print("User Cuenta:", cuentas.userCuenta)
                print("Password Cuenta:", cuentas.passwordCuenta)
                print("Account Cuenta:", cuentas.accountCuenta)                
                nombreEstrategia = nombreEstrategia
                hora_inicio = datetime(year=2023, month=7, day=3, hour=int(15), minute=int(00))
                hora_fin = datetime(year=2023, month=7, day=3, hour=int(17), minute=int(00))
                triggerEstrategia = TriggerEstrategia( 
                        id=None,   
                        user_id=user_id,
                        userCuenta=cuentas.userCuenta,
                        passwordCuenta=cuentas.passwordCuenta,
                        accountCuenta=cuentas.accountCuenta, 
                        horaInicio=hora_inicio,  # Ejemplo de hora de inicio (15:00)
                        horaFin=hora_fin,  # Ejemplo de hora de fin (17:00)     
                        ManualAutomatico = 'AUTOMATICO',
                        nombreEstrategia = nombreEstrategia    
                        )
                
            
                db.session.add(triggerEstrategia)  # Agregar la instancia de Cuenta a la sesión
                db.session.commit()  # Confirmar los cambios
                db.session.refresh(triggerEstrategia)  # Actualizar la instancia desde la base de datos para obtener el ID generado
                triggerEstrategia_id = triggerEstrategia.id  # Obtener el ID generado
                estrategias = db.session.query(TriggerEstrategia).join(Usuario).filter(TriggerEstrategia.user_id == user_id,TriggerEstrategia.accountCuenta == cuentas.accountCuenta).all()
                
                #######################################################################
                # Aquí debes tener los datos que deseas pasar a la función crear_ficha#
                #######################################################################
                fichaStatic = db.session.query(Ficha).filter_by(user_id=user_id, estado='STATIC').all()
                # Cerrar la sesión
                db.session.close()
                if not fichaStatic:
                    reporte = obtenerSaldoCuenta(account=cuentas.accountCuenta)   
                    valor = reporte['availableToCollateral'] 
                    cash = reporte['currentCash'] 
                    total_cuenta = int(valor) + int(cash)
                    data = {
                        'valor': total_cuenta,
                        'accessToken': access_token,
                        'cuenta': cuentas.accountCuenta,
                        'correoElectronico': correo_electronico,
                        'total_cuenta': total_cuenta,
                        'layoutOrigen': layouts,
                        'estado_ficha' :'STATIC'
                    }

                    # URL a la que enviar la solicitud POST
                    url = url_for('fichas.crear_ficha', _external=True)  # Utiliza _external=True para obtener la URL completa

                
                    # Realizar la solicitud POST con los datos
                    response = requests.post(url, json=data)
                
                return render_template("/estrategias/panelControEstrategiaUser.html", datos=[user_id, estrategias],layout='layoutConexBroker')
           
    except:
        print('no hay estrategias')
    flash('No se puede regitrar la estrategia.')
    return  render_template("/notificaciones/errorEstrategiaABM.html")
  


@estrategias.route('/inicioEstrategias/')
def inicioEstrategias():
 try:
   get.pyRofexInicializada.get_account_position()
   return render_template('/estrategias.html')
 except:  
     print("contraseña o usuario incorrecto")  
     flash('Loggin Incorrect')    
     return render_template("notificaciones/noPoseeDatos.html" )    
 
@estrategias.route('/detenerWS/', methods=["GET", "POST"])
def detenerWS():
    try:
        # Cerrar la conexión del websocket
        get.pyRofexInicializada.close_websocket_connection()
        
        # Obtener el usuario_id si la solicitud es POST
        if request.method == 'POST':
            usuario_id = request.form.get('usuario_id')
            # Llamar a la función estrategias_usuario_nadmin y pasar los datos por POST
            resultado_estrategias = estrategias_usuario_nadmin(usuario_id)
            # Hacer algo con el resultado de la función si es necesario

        # Si la solicitud es GET, no se espera ningún parámetro, ya que no se está enviando ningún formulario
        elif request.method == 'GET':
           #resultado_estrategias = estrategias_usuario_nadmin()
           return jsonify({'success': True, 'message': 'Procesos en Threads detenidos'})

    except Exception as e:
        print('Error al detener WS:', str(e))
        return render_template("errorOperacion.html")  # Puedes renderizar una plantilla de error específica
    
@estrategias.route('/cargaDatosEstrategyUno/', methods = ['POST'])
def cargaDatosEstrategyUno():   
    if request.method == 'POST':         
        Ticker = request.form["Ticker"]   
        cantidad = request.form["cantidad"] 
        spread = request.form["spread"] 
        mensaje = Ticker+','+cantidad+','+spread
        
        inst = InstrumentoEstrategiaUno(Ticker, cantidad, spread)
       #00
        get.pyRofexInicializada.init_websocket_connection (market_data_handler,order_report_handler,error_handler,exception_error)
        tickers=[inst.instrument]
        print("tickers",tickers)
        entries = [get.pyRofexInicializada.MarketDataEntry.BIDS,
                    get.pyRofexInicializada.MarketDataEntry.OFFERS
                    ]   
        print("entries",entries)     
        instrumento_suscriptio = get.pyRofexInicializada.market_data_subscription(tickers,entries)
        print(instrumento_suscriptio)
        print(inst.instrument)
        # Subscribes to receive order report for the default account
        get.pyRofexInicializada.order_report_subscription(snapshot=True)
        return render_template('/estrategiaOperando.html')
    
    
@estrategias.route('/estrategyUno/')
def estrategyUno():     
    
    try:
        print()
        print()
        print("<<<--------EstrategyUno-------->>>>>")
        inst = InstrumentoEstrategiaUno("WTI/MAY23", 12, 0.05) 
        get.pyRofexInicializada.init_websocket_connection (market_data_handler,order_report_handler,error_handler,exception_error)
        tickers=[inst.instrument]
        print("_EstrategyUno_tickers_",tickers)
        entries = [get.pyRofexInicializada.MarketDataEntry.BIDS,
                    get.pyRofexInicializada.MarketDataEntry.OFFERS
                    ]   
        print("_EstrategyUno_entries_",entries)     
        print()
        instrumento_suscription = get.pyRofexInicializada.market_data_subscription(tickers,entries)
        print()
        print("_EstrategyUno_instrumento_suscriptio_",instrumento_suscription)
        print("_EstrategyUno_inst.instrument_",inst.instrument)
        # Subscribes to receive order report for the default account
        get.pyRofexInicializada.order_report_subscription(snapshot=True)
        return render_template('/estrategiaOperando.html')
    except:  
        print("_EstrategyUno_contraseña o usuario incorrecto")  
        flash('Loggin Incorrect')    
        return render_template("errorLogueo.html" ) 
    
       
@estrategias.route('/estrategyDos/')
def estrategyDos():     
    
    
    try:
        inst = InstrumentoEstrategiaUno("WTI/MAY23", 12, 0.05) 
        print("<<<--------estrategyDoooooooooooooooooooosssssss-------->>>>>")
        get.pyRofexInicializada.init_websocket_connection (handler_estrategyDos,o_r_handler_estrategyDos,error_handler,exception_error)
        tickers=[inst.instrument]
        print("tickers",tickers)
        entries = [get.pyRofexInicializada.MarketDataEntry.BIDS,
                    get.pyRofexInicializada.MarketDataEntry.OFFERS
                    ]   
        print("entries",entries)     
        instrumento_suscriptio = get.pyRofexInicializada.market_data_subscription(tickers,entries)
        print(instrumento_suscriptio)
        print(inst.instrument)
        # Subscribes to receive order report for the default account
        get.pyRofexInicializada.order_report_subscription(snapshot=True)
        return render_template('/estrategiaOperando.html')
    except:  
        print("contraseña o usuario incorrecto")  
        flash('Loggin Incorrect')    
        return render_template("errorLogueo.html" ) 
 
 
@estrategias.route('/estrategyPcDaniel/')
def estrategyPcDaniel():
    print("<<<<<<--------estrategyPcDaniel----->>>>>>>")
    variable1=123
    variable2=456
    variable3=789
    variable4=12458.21444
    return render_template('/estrategiaOperando.html')
 
    # Defines the handlers that will process the messages.
#<<<<<<<<<<<<<<<<<<-------------------AQUI SE DEFINE LA COMPRA Y VENTA AUTOMATICA DIRECTA -------------------->>>>>>>>>>>>>


@estrategias.route('/Estrategia_001/')
def Estrategia_001():
    try:
        inst = InstrumentoEstrategiaUno("WTI/MAY23", 12, 0.05) 
        print("_____________________Estrategia_001:...")
        get.pyRofexInicializada.init_websocket_connection (handler_Estrategia_001,o_r_handler_Estrategia_001,error_handler,exception_error)
        tickers=[inst.instrument]
        print("tickers",tickers)
        entries = [get.pyRofexInicializada.MarketDataEntry.BIDS,
                    get.pyRofexInicializada.MarketDataEntry.OFFERS
                    ]   
        print("entries",entries)     
        instrumento_suscriptio = get.pyRofexInicializada.market_data_subscription(tickers,entries)
        print(instrumento_suscriptio)
        print(inst.instrument)
        
        # Subscribes to receive order report for the default account
        get.pyRofexInicializada.order_report_subscription(snapshot=True)
        return render_template('/estrategiaOperando.html')
    except:  
        print("contraseña o usuario incorrecto")  
        flash('Loggin Incorrect')    
        return render_template("errorLogueo.html" ) 

    

def handler_Estrategia_001(message):
    # mensaje = Ticker+','+cantidad+','+spread
        print("_____________________Estrategia_001:...")
        print("Processing ddddddddddddddddddMarket Data Message Received: ",message)
        
                
        last_md = None
        bid = message["marketData"]["BI"]
        offer = message["marketData"]["OF"]
        symbol =  message["instrumentId"]["symbol"]
        price = message["marketData"]["BI"][0]["price"]
        orderQty = "3"
        if bid and offer:
           bid_px = bid[0]["price"]
           offer_px = offer[0]["price"]
           print("bid_px: ",bid_px," offer_px ",offer_px," symbol ",symbol," orderQty ",orderQty," price ",price)
           #datos = saaoperacionGral(bid,offer)
           #datos = saaoperacionGral(bid,offer)
           #datos = saaoperacionGral(bid,offer)
           get.pyRofexInicializada.send_order_via_websocket(ticker=symbol, side=get.pyRofexInicializada.Side.BUY, size=orderQty, order_type=get.pyRofexInicializada.OrderType.LIMIT,price=price)  
        
        else:
          InstrumentoEstrategiaUno._cancel_if_orders()
      


def o_r_handler_Estrategia_001(message):
  print("_____________________Estrategia_001:...")
  #print("Mensaje de OrderRouting: {0}".format(message))
  get.reporte_de_ordenes.append(message)



def handler_estrategyDos(message):
    # mensaje = Ticker+','+cantidad+','+spread
        print("Processing ddddddddddddddddddMarket Data Message Received: ",message)
        
                   
        last_md = None
        bid = message["marketData"]["BI"]
        offer = message["marketData"]["OF"]
        symbol =  message["instrumentId"]["symbol"]
        price = message["marketData"]["BI"][0]["price"]
        orderQty = "3"
        if bid and offer:
           bid_px = bid[0]["price"]
           offer_px = offer[0]["price"]
           print("bid_px: ",bid_px," offer_px ",offer_px," symbol ",symbol," orderQty ",orderQty," price ",price)
           get.pyRofexInicializada.send_order_via_websocket(ticker=symbol, side=get.pyRofexInicializada.Side.BUY, size=orderQty, order_type=get.pyRofexInicializada.OrderType.LIMIT,price=price)  
         
        else:
          InstrumentoEstrategiaUno._cancel_if_orders()




def o_r_handler_estrategyDos(message):
  
  #print("Mensaje de OrderRouting: {0}".format(message))
  get.reporte_de_ordenes.append(message)
      

  
    
def market_data_handler( message):
    
       # mensaje = Ticker+','+cantidad+','+spread
        print("Processing Market Data Message Received: {0}".format(message))
       # clientesocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #clientesocket.connect(('localhost',8089))
        #clientesocket.send(format(message).encode())
       
        if InstrumentoEstrategiaUno.state is States.WAITING_MARKET_DATA:
            print("Processing Market Data Message Received: {0}".format(message))
            last_md = None
            bid = message["marketData"]["BI"]
            offer = message["marketData"]["OF"]
            if bid and offer:
                bid_px = bid[0]["price"]
                offer_px = offer[0]["price"]
                bid_offer_spread = round(offer_px - bid_px, 6) - 0.002
                if bid_offer_spread >= InstrumentoEstrategiaUno.spread:
                    if InstrumentoEstrategiaUno.my_order:
                        for order in InstrumentoEstrategiaUno.my_order.values():
                            if order["orderReport"]["side"] == "BUY" and \
                                    order["orderReport"]["price"] < bid_px:
                                InstrumentoEstrategiaUno._send_order(get.pyRofexInicializada.Side.BUY, bid_px + InstrumentoEstrategiaUno.tick, InstrumentoEstrategiaUno.buy_size)
                            elif order["orderReport"]["side"] == "SELL" and \
                                    order["orderReport"]["price"] > offer_px:
                                InstrumentoEstrategiaUno._send_order(get.pyRofexInicializada.Side.SELL, offer_px - InstrumentoEstrategiaUno.tick, InstrumentoEstrategiaUno.sell_size)
                    else:
                        if InstrumentoEstrategiaUno.buy_size > 0:
                            InstrumentoEstrategiaUno._send_order(get.pyRofexInicializada.Side.BUY, bid_px + InstrumentoEstrategiaUno.tick, InstrumentoEstrategiaUno.buy_size)
                        if InstrumentoEstrategiaUno.sell_size > 0:
                            InstrumentoEstrategiaUno._send_order(get.pyRofexInicializada.Side.SELL, offer_px - InstrumentoEstrategiaUno.tick, InstrumentoEstrategiaUno.sell_size)
                else:  # Lower spread
                    InstrumentoEstrategiaUno._cancel_if_orders()
            else:
                InstrumentoEstrategiaUno._cancel_if_orders()
        else:
            InstrumentoEstrategiaUno.last_md = message








    # Defines the handlers that will process the Order Reports.
def order_report_handler( order_report):
        print("Order Report Message Received: {0}".format(order_report))
        if order_report["orderReport"]["clOrdId"] in InstrumentoEstrategiaUno.my_order.keys():
            InstrumentoEstrategiaUno._update_size(order_report)
            if order_report["orderReport"]["status"] in ("NEW", "PARTIALLY_FILLED"):
                print("processing new order")
                InstrumentoEstrategiaUno.my_order[order_report["orderReport"]["clOrdId"]] = order_report
            elif order_report["orderReport"]["status"] == "FILLED":
                print("processing filled")
                del InstrumentoEstrategiaUno.my_order[order_report["orderReport"]["clOrdId"]]
            elif order_report["orderReport"]["status"] == "CANCELLED":
                print("processing cancelled")
                del InstrumentoEstrategiaUno.my_order[order_report["orderReport"]["clOrdId"]]

            if InstrumentoEstrategiaUno.state is States.WAITING_CANCEL:
                if not InstrumentoEstrategiaUno.my_order:
                    InstrumentoEstrategiaUno.state = States.WAITING_MARKET_DATA
                    if InstrumentoEstrategiaUno.last_md:
                        InstrumentoEstrategiaUno.market_data_handler(InstrumentoEstrategiaUno.last_md)
            elif InstrumentoEstrategiaUno.state is States.WAITING_ORDERS:
                for order in InstrumentoEstrategiaUno.my_order.values():
                    if not order:
                        return
                InstrumentoEstrategiaUno.state = States.WAITING_MARKET_DATA
                if InstrumentoEstrategiaUno.last_md:
                    InstrumentoEstrategiaUno.market_data_handler(InstrumentoEstrategiaUno.last_md)
                    
                    
                    
                    

def _update_size(order):
        if order["orderReport"]["status"] in ("PARTIALLY_FILLED", "FILLED"):
            if order["orderReport"]["side"] == "BUY":
                InstrumentoEstrategiaUno.buy_size -= round(order["orderReport"]["lastQty"])
            if order["orderReport"]["side"] == "SELL":
                InstrumentoEstrategiaUno.sell_size -= round(order["orderReport"]["lastQty"])
            if InstrumentoEstrategiaUno.sell_size == InstrumentoEstrategiaUno.buy_size == 0:
                InstrumentoEstrategiaUno.sell_size = InstrumentoEstrategiaUno.buy_size = InstrumentoEstrategiaUno.initial_size

def _cancel_if_orders():
        if InstrumentoEstrategiaUno.my_order:
            InstrumentoEstrategiaUno.state = States.WAITING_CANCEL
            for order in InstrumentoEstrategiaUno.my_order.values():
                get.pyRofexInicializada.cancel_order(order["orderReport"]["clOrdId"])
                print("canceling order %s" % order["orderReport"]["clOrdId"])

def _send_order( side, px, size):
        InstrumentoEstrategiaUno.state = States.WAITING_ORDERS
        order = get.pyRofexInicializada.send_order(
            ticker=InstrumentoEstrategiaUno.instrument,
            side=side,
            size=size,
            price=round(px, 6),
            order_type=get.pyRofexInicializada.OrderType.LIMIT,
            cancel_previous=True
        )
        InstrumentoEstrategiaUno.my_order[order["order"]["clientId"]] = None
        print("sending %s order %s@%s - id: %s" % (side, size, px, order["order"]["clientId"]))
        
        
        
##########################esto es para ws#############################
#Mensaje de MarketData: {'type': 'Md', 'timestamp': 1632505852267, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'DLR/DIC21'}, 'marketData': {'BI': [{'price': 108.25, 'size': 100}], 'LA': {'price': 108.35, 'size': 3, 'date': 1632505612941}, 'OF': [{'price': 108.45, 'size': 500}]}}
def error_handler(message):
  print("Mensaje de error: {0}".format(message))
  
def exception_error(message):
  print("Mensaje de excepción: {0}".format(message))  
  {"type":"or","orderReport":{"orderId":"1128056","clOrdId":"user14545967430231","proprietary":"api","execId":"160127155448-fix1-1368","accountId":{"id":"30"},"instrumentId":{"marketId":"ROFX","symbol":"DODic21"},"price":18.000,"orderQty":10,"ordType":"LIMIT","side":"BUY","timeInForce":"DAY","transactTime":"20160204-11:41:54","avgPx":0,"lastPx":0,"lastQty":0,"cumQty":0,"leavesQty":10,"status":"CANCELLED","text":"Reemplazada"}}


  
  


   

