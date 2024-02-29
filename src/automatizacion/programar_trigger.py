from pipes import Template
from unittest import result
from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.usuario import Usuario
from models.cuentas import Cuenta
from models.triggerEstrategia import TriggerEstrategia
from datetime import datetime, timedelta, time

import smtplib
import schedule
import functools
import time
import strategies.estrategiaSheetWS as estrategiaSheetWS 
from routes.api_externa_conexion.wsocket import wsocketConexion as conexion
import routes.api_externa_conexion.get_login as get
import strategies.estrategias as estrategias
from utils.common import Marshmallow, db
from datetime import datetime
import jwt
import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
programar_trigger = Blueprint('programar_trigger', __name__)

# Crear la tabla cuenta si no existe
def crea_tabla_triggerEstrategia():
    hora_inicio = datetime(year=2023, month=7, day=3, hour=15, minute=0)
    hora_fin = datetime(year=2023, month=7, day=3, hour=17, minute=0)
    triggerEstrategia = TriggerEstrategia(    
        id=1,
        user_id = "1",
        userCuenta="mauriciodioli6603",
        passwordCuenta="zbwitW5#",
        accountCuenta="REM6603",  
        horaInicio=hora_inicio,  # Ejemplo de hora de inicio (15:00)
        horaFin=hora_fin,  # Ejemplo de hora de fin (17:00) 
        ManualAutomatico = "MANUAL",  
        nombreEstrategia = "sheet"     
    )
    triggerEstrategia.crear_tabla_triggerEstrategia()
    print("Tabla creada!")




@programar_trigger.route('/trigger/')
def trigger():
    
    return render_template("/automatizacion/trigger.html")

@programar_trigger.route('/programador_trigger/', methods=['POST'])
def programador_trigger():
    
    #crea_tabla_triggerEstrategia()
    # Obtener las horas ingresadas por el usuario desde los datos enviados en el cuerpo de la solicitud
    horaInicio = request.json["horaInicio"]
    horaFin = request.json["horaFin"]
    cuenta =  request.json["cuenta"]    
    usuario =  request.json["usuario"]
    correoElectronico =  request.json["correoElectronico"]
    access_token = request.json["tokenAcceso"]
    accesoManualAutomatico =request.json["accesoManualAutomatico"]
    ##passwordCuenta=passwordCuenta_encoded,
    if access_token:
        app = current_app._get_current_object()
        try:
            user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            usuario_objeto = Usuario.query.get(user_id)  # Obtener el objeto Usuario correspondiente al user_id
            
            cuenta = Cuenta.query.filter_by(user_id=user_id).first()
            if cuenta:
                print("Datos de la cuenta:")
                print("ID:", cuenta.id)
                print("User ID:", cuenta.user_id)
                print("User Cuenta:", cuenta.userCuenta)
                print("Password Cuenta:", cuenta.passwordCuenta)
                print("Account Cuenta:", cuenta.accountCuenta)
                horaInicioSalvar, minutosInicioSalvar = horaInicio.split(':')
                horaFinSalvar, minutosFinSalvar = horaFin.split(':')
               
            hora_inicio = datetime(year=2023, month=7, day=3, hour=int(horaInicioSalvar), minute=int(minutosInicioSalvar))
            hora_fin = datetime(year=2023, month=7, day=3, hour=int(horaFinSalvar), minute=int(minutosFinSalvar))
            triggerEstrategia = TriggerEstrategia( 
                     id=None,   
                     user_id=user_id,
                     userCuenta=cuenta.userCuenta,
                     passwordCuenta=cuenta.passwordCuenta,
                     accountCuenta=cuenta.accountCuenta, 
                     horaInicio=hora_inicio,  # Ejemplo de hora de inicio (15:00)
                     horaFin=hora_fin,  # Ejemplo de hora de fin (17:00)     
                     ManualAutomatico = accesoManualAutomatico         
                            
                     )
            
           
            db.session.add(triggerEstrategia)  # Agregar la instancia de Cuenta a la sesión
            db.session.commit()  # Confirmar los cambios
            db.session.refresh(triggerEstrategia)  # Actualizar la instancia desde la base de datos para obtener el ID generado
            triggerEstrategia_id = triggerEstrategia.id  # Obtener el ID generado
           
            print("Auomatico registrada exitosamente!")
            print("automatico registrada usuario id !",triggerEstrategia_id)
         #   todasLasCuentas = get_cuentas_de_broker(user_id)
            triggerEstrategia1 = TriggerEstrategia.query.filter_by(id=triggerEstrategia_id).first() 
            db.session.close()
            render_template("/")
              
          #  for cuenta in todasLasCuentas:
           #       print(cuenta['accountCuenta'])

        except Exception as e:
            # Manejo específico de la excepción
            print("Error:", str(e))
            db.session.rollback()  # Hacer rollback de la sesión
            db.session.close()
            print("No se pudo registrar la hora a automatizar.")
        # Llamar a la función del trigger y pasarle las horas ingresadas
    programar_tareas(horaInicio, horaFin)

    return "Triggers programados"

def programar_tareas(horaInicio, horaFin):
    # Convertir las horas ingresadas en formato de cadena a objetos de fecha y hora
    horaInicio_deseada = datetime.strptime(horaInicio, "%H:%M")
    horaFin_deseada = datetime.strptime(horaFin, "%H:%M")

    # Obtener la hora actual
    hora_actual = datetime.now()

    # Calcular las diferencias de tiempo hasta las horas deseadas
    diferencia_tiempo_inicio = horaInicio_deseada - hora_actual
    diferencia_tiempo_fin = horaFin_deseada - hora_actual

    # Si las horas deseadas ya han pasado hoy, se ajustan para que sean las del próximo día
    if diferencia_tiempo_inicio.total_seconds() < 0:
        diferencia_tiempo_inicio += timedelta(days=1)
    if diferencia_tiempo_fin.total_seconds() < 0:
        diferencia_tiempo_fin += timedelta(days=1)

    # Programar las tareas de inicio y finalización a las horas deseadas
    schedule.every().day.at(horaInicio_deseada.strftime("%H:%M")).do(tarea_inicio)
    schedule.every().day.at(horaFin_deseada.strftime("%H:%M")).do(tarea_fin)


##############################################################################################################
################# INICIA LA AUTOMATIZACION ###############################
#############################################################################################################
def reiniciar_hilos():
    # Reiniciar solo los hilos que han terminado
    for hilo_id, hilo in get.hilo_iniciado_panel_control.items():
        if not hilo.is_alive():
            hilo.start()
        else:
            print(f"El hilo {hilo_id} aún está en ejecución y no será reiniciado.")

def planificar_schedule(user_id, app):
    def ejecutar_schedule():
        llama_tarea = functools.partial(llama_tarea_cada_24_horas_estrategias, user_id, app)
        schedule.every().day.at("13:07").do(llama_tarea)
        schedule.every().day.until("14:20").do(reiniciar_hilos)

        while not get.detener_proceso_automatico_triggers:  # Bucle hasta que la bandera detener_proceso sea True
            print("______________________________________________________________________________")
            print("comprobando tarea pendiente schedule.run_pending() planificar_shedule ")
            print("______________________________________________________________________________")
            schedule.run_pending()
            time.sleep(60)

    hilo_schedule = threading.Thread(target=ejecutar_schedule)
    hilo_schedule.start()

def llama_tarea_cada_24_horas_estrategias(user_id, app):
    get.hilo_iniciado_estrategia_usuario
    with app.app_context():
        triggerEstrategias = db.session.query(TriggerEstrategia).all()    
        hilos = []
        
        for triggerEstrategia in triggerEstrategias:
            if triggerEstrategia.ManualAutomatico == "AUTOMATICO":
                
                usuario = db.session.query(Usuario).filter_by(id=triggerEstrategia.user_id).first()
                if usuario:
                    print("El usuario existe en la lista triggerEstrategias.")
                    
                    # Verifica si ya hay un hilo iniciado para este usuario
                    if user_id in get.hilo_iniciado_estrategia_usuario and get.hilo_iniciado_estrategia_usuario[user_id].is_alive():
                        print(f"Hilo para {user_id} ya está en funcionamiento para la estrategia {triggerEstrategia.nombreEstrategia}")
                        continue
                    
                    print("usuario ",usuario.id," nombre estrategia ",triggerEstrategia.nombreEstrategia," Hora de inicio:", triggerEstrategia.horaInicio)
                    
                # # Si no hay un hilo iniciado para este usuario, lo inicia
                    hilo_id = f"{usuario.correo_electronico}_{triggerEstrategia.nombreEstrategia}"  # Utiliza el correo electrónico del usuario y el nombre de la estrategia como identificador único del hilo
                    hilo = threading.Thread(target=tarea_inicio, args=(user_id, app, triggerEstrategias, usuario))
                    get.hilo_iniciado_panel_control[hilo_id] = hilo
                    # Define las horas de inicio y fin para el hilo
                    hora_inicio = triggerEstrategia.horaInicio
                    hora_fin = triggerEstrategia.horaFin
                    
                    # Establece un atributo personalizado en el hilo para las horas de inicio y fin
                   # hilo.hora_inicio = hora_inicio
                   # hilo.hora_fin = hora_fin
                    hilo.start()
                    hilos.append(hilo)
                    # Imprimir el diccionario de hilos iniciados
                    print("Diccionario de hilos iniciados:", get.hilo_iniciado_panel_control)
                    
                    
                else:
                    print("El usuario no existe en la lista triggerEstrategias.")  

        # Esperar a que todos los hilos terminen antes de finalizar
        for hilo in hilos:
            hilo.join()
        
    



def tarea_inicio(user_id,app,triggerEstrategias,usuario):
    
    # Programar la próxima ejecución después de 24 horas
#    schedule.every(24).hours.do(tarea_inicio)
    #se inicia cada minuto para test
   
    

    # Aquí puedes enviar los datos a otra ruta en otro archivo Python
    # utilizando la librería requests o similar
    #traer los datos del usuario y trigger
    with app.app_context():
    
        # Realizar la consulta
       
        
        # Procesar los usuarios (aquí puedes hacer lo que necesites con los resultados)
        
        for triggerEstrategia in triggerEstrategias:
                # Construir los datos a enviar a la otra ruta
            datos = {
                        "userCuenta": triggerEstrategia.userCuenta,
                        "idTrigger":triggerEstrategia.id,
                        "access_token": 'access_token',
                        "idUser": triggerEstrategia.user_id,
                        "correo_electronico": usuario.correo_electronico,
                        "cuenta": triggerEstrategia.accountCuenta,
                        "tiempoInicio": triggerEstrategia.horaInicio,
                        "tiempoFin": triggerEstrategia.horaFin,
                        "automatico": triggerEstrategia.ManualAutomatico,
                        "nombre": triggerEstrategia.nombreEstrategia
                    }
            # Convertir los objetos datetime a cadenas de texto
            datos["tiempoInicio"] = triggerEstrategia.horaInicio.strftime('%Y-%m-%dT%H:%M:%S')
            datos["tiempoFin"] = triggerEstrategia.horaFin.strftime('%Y-%m-%dT%H:%M:%S')

            #conectar el WS y suscribe
            
            #conexion()
            
            #enviar los datos a la estrategia
            #url =  'estrategiaSeetWS.',triggerEstrategia.nombreEstrategia
            #response = requests.post(url_for(url), data=datos)
            # Construir la URL de destino
            url_destino = 'http://127.0.0.1:5001/' + triggerEstrategia.nombreEstrategia
            
           
            # Enviar los datos a la estrategia
            response = requests.post(url_destino, json=datos)

            if response.status_code == 200:
                print("**************************************************inicia***********************")
                print("Datos de usuario enviados con éxito")
                print("estrategia ",triggerEstrategia.nombreEstrategia," iniciada con exito")
                print("**************************************************")
            else:
                    print("Error al enviar los datos de usuario en  automatizacion/programar_trigger/thread/tarea_inicio")


        






