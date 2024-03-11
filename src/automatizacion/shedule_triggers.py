from pipes import Template
from unittest import result
from flask import current_app
import smtplib
import os
import pyRofex
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
from routes.api_externa_conexion.wsocket import websocketConexionShedule as conexion
import routes.api_externa_conexion.get_login as get
import strategies.estrategias as estrategias
from utils.common import Marshmallow, db
from datetime import datetime
import jwt
import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging


shedule_triggers = Blueprint('shedule_triggers', __name__)


@shedule_triggers.route("/muestraTriggers/")
def muestraTriggers():
    try:
         # Filtrar los TriggerEstrategia que tengan manualAutomatico igual a "AUTOMATICO"
         triggers_automaticos = TriggerEstrategia.query.filter_by(ManualAutomatico="AUTOMATICO").all()        
 
         total_triggers = len(triggers_automaticos)  # Obtener el total de instancias de TriggerEstrategia
         db.session.close()
         
         return render_template("automatizacion/trigger.html", num_triggers=total_triggers)
    except:        
        return render_template("errorLogueo.html" )
   
@shedule_triggers.route("/ArrancaShedule/", methods=['POST'])
def ArrancaShedule():
    try:
        if request.method == 'POST':
            
            data = request.json  # Obtener los datos JSON de la solicitud POST
            fecha_inicio_shedule = data['fechaInicioShedule']  # Obtener el valor de fechaInicioShedule
            fecha_fin_shedule = data['fechaFinShedule'] # Obtener el valor de fechaFinShedule
            get.accountLocalStorage = data['userCuenta']
            access_token = data['access_token']
            idUser = data['idUser']
            correo_electronico = data['correo_electronico']
            cuenta = data['cuenta']     
            selector = data['selector']  
            
       
            get.detener_proceso_automatico_triggers = False
            # Hacer lo que necesites con los valores obtenidos
            #print('Hora de inicio:', fecha_inicio_shedule)
            #print('Hora de fin:', fecha_fin_shedule)
             # Supongamos que shedule_triggers es tu objeto Blueprint de Flask
            app = current_app._get_current_object() 
            hilo_principal = threading.Thread(target=planificar_schedule, 
                                                args=(app,idUser,fecha_inicio_shedule, fecha_fin_shedule,cuenta,correo_electronico,selector ))

            hilo_principal.start()

            # Retornar una respuesta si es necesario
              # Retornar una respuesta indicando éxito
            return jsonify({'success': True, 'message': 'Hilo iniciado exitosamente'})
    except Exception as e:
           # Manejar cualquier error aquí
        print(str(e))
        return jsonify({'success': False, 'message': 'Hubo un problema al iniciar el hilo'})

@shedule_triggers.route("/DetenerShedule/")
def DetenerShedule():
    try:
       get.detener_proceso_automatico_triggers = True
       terminar_hilos_shedule()
       print('DetenerShedule get.detener_proceso_automatico_triggers ',get.detener_proceso_automatico_triggers)
            # Retornar una respuesta si es necesario
              # Retornar una respuesta indicando éxito
       return jsonify({'success': True, 'message': 'Proceso Shedule detenido'})
    except Exception as e:
           # Manejar cualquier error aquí
        print(str(e))
        return jsonify({'success': False, 'message': 'Hubo un problema al iniciar el hilo'})



##############################################################################################################
################# INICIA LA AUTOMATIZACION ###############################
#############################################################################################################
def terminar_hilos(app,hilo):
    src_directory = os.path.dirname(os.path.abspath(__file__))
    logs_file_path = os.path.join(src_directory, 'logs.log')
    # Aquí detienes los hilos iniciados desde planificar_schedule, excepto el hilo ejecutar_schedule
    # Para ello, recorres el diccionario get.hilo_iniciado_panel_control y detienes los hilos que corresponden, excepto el hilo ejecutar_schedule
    get.pyRofexInicializada.close_websocket_connection()
    
    app.logger.info("_______________TERMINA CONEXION WS__________________________")
    print('_______________________________________')
    print('_______________________________________')
    print('__________TERMINA CONEXION WS__________')
    print('_______________________________________')
    print('_______________________________________')
    
    
    for indice, (hilo_id, h) in enumerate(get.hilo_iniciado_panel_control.items()):
        app.logger.info("______HILO EXAMINADO___________")
        with open(logs_file_path, 'a') as f:
                f.write(f'Índice {indice} ID del hilo: {hilo_id} , Hilo: {h}\n') 
        app.logger.log(get.CUSTOM_LEVEL, 'Índice %s ID del hilo %s Hilo %s', indice, hilo_id, h)
        
        if h is not hilo and h.is_alive():
            print(f'El hilo con ID {hilo_id} está vivo.')
            print(f'Índice: {indice}, ID del hilo: {hilo_id}, Hilo: {h}')
             # Escribir la nueva información en el archivo de logs
           
            print('_________temina hilo________ ', h)
            app.logger.info("______TERMINA CONEXION WS___________")
            app.logger.info("______TERMINA HILO__________________")
            h.join()  # Espera a que el hilo termine su ejecución si aún está vivo
        else:
            app.logger.info("________NO HAY HILOS ACTIVOS PARA EL SCHEDULE_____________")
           

    get.hilo_iniciado_panel_control.clear()  # Limpia el diccionario de hilos iniciados

def terminar_hilos_shedule():
    # Terminar solo los hilos del schedule
    # Iterar sobre la lista de hilos iniciados
    for indice, hilo in enumerate(get.hilos_iniciados_shedule):
        hilo.join()  # Esperar a que el hilo termine su ejecución
        print(f"Hilo ID: {indice}, Hilo: {hilo}")
        print('FUNC__terminar_hilos_shedule___ TERMINA HILO EN SHEDULE____')
    # Limpiar la lista de hilos iniciados
    get.hilos_iniciados_shedule.clear()

    
      

def reiniciar_hilos(app):
    # Reiniciar solo los hilos que han terminado
    for hilo_id, hilo in get.hilo_iniciado_panel_control.items():
        if not hilo.is_alive():
            hilo.start()
            app.logger.info("_______________REINICIA HILO_______________________")
        else:
            print(f"El hilo {hilo_id} aún está en ejecución y no será reiniciado.")


def planificar_schedule(app,user_id,tiempoInicioDelDia, tiempoFinDelDia,cuenta,correo_electronico,selector ):
    def ejecutar_schedule():
        #busca el directorio src/logs.log
        src_directory = os.path.dirname(os.path.abspath(__file__))
       # if os.path.exists(src_directory):
            # Eliminar el archivo
        #    os.remove(src_directory)
        # Ruta al archivo de logs dentro del directorio 'src'
        logs_file_path = os.path.join(src_directory, 'logs.log')
        # Abrir el archivo en modo de escritura para borrar su contenido
        with open(logs_file_path, 'w') as f:
            pass  # No es necesario escribir nada, solo abrir y cerrar el archivo borrará su contenido
        print("El contenido del archivo logs.log ha sido borrado.")
          # Variable local para mantener un registro de los hilos iniciados aquí
        app.logger.info("Se accedió a la página de inicio")
        llama_tarea = functools.partial(llama_tarea_cada_24_horas_estrategias, app,user_id, cuenta,correo_electronico,selector)
        #tiempoInicioDelDia = '12:00'
        #tiempoFinDelDia = '14:20'
        #schedule.every().day.at(get.hora_inicio_manana.strftime('%H:%M')).do(llama_tarea)
        #INICIA LOS HILOS AL PRINCIPIO DEL DIA
       
        schedule.every().day.at(tiempoInicioDelDia).do(llama_tarea)
        
        #REINICIA LOS HILOS HASTA EL FIN DEL DIA
        # Calcula la hora 10 minutos antes de tiempoFinDelDia
        
        hora_fin =datetime.strptime(tiempoFinDelDia, '%H:%M')
        hora_fin_10_minutos_antes = (hora_fin  - timedelta(minutes=10)).strftime('%H:%M')
        
        #schedule.every().day.at(hora_fin_10_minutos_antes).do(reiniciar_hilos)

        #DETIENE LOS HILOS LAS FINAL DEL DIA
        
        schedule.every().day.at(tiempoFinDelDia).do(terminar_hilos,app, hilo_schedule)
        
      

        while not get.detener_proceso_automatico_triggers:  # Bucle hasta que la bandera detener_proceso sea True
            hora_actual = datetime.now().strftime("%H:%M:%S")
            # Obtener la ruta al directorio 'src' de tu proyecto
           
            # Escribir la nueva información en el archivo de logs
            with open(logs_file_path, 'a') as f:
                f.write(f'__inicio {tiempoInicioDelDia} ___fin {tiempoFinDelDia}\n') 
            app.logger.log(get.CUSTOM_LEVEL, '__inicio %s ___fin %s __hora_actual %s', tiempoInicioDelDia, tiempoFinDelDia, hora_actual)


            print("______________________________________________________________________________")
            print("comprobando schedule.run_pending() automatizacion shedule_trigger planificar_shedule  " )
            print('__inicio ',tiempoInicioDelDia,' ___fin ',tiempoFinDelDia,' __hora_actual ',hora_actual)
            #print("Diccionario de hilos iniciados:", get.hilo_iniciado_panel_control)
            print("______________________________________________________________________________")
            schedule.run_pending()
            time.sleep(60)

    hilo_schedule = threading.Thread(target=ejecutar_schedule)
    hilo_schedule.start()
    get.hilos_iniciados_shedule.append(hilo_schedule)
    
    
    
    
    
def llama_tarea_cada_24_horas_estrategias(app, user_id, cuenta, correo_electronico, selector):
    with app.app_context():
        try:
            app.logger.info("_______________Intentando__conexion__con WS__________________________")
            print("____________________________Intentando__conexion__desde Shedule_______________________")
            conexion(app, Cuenta, cuenta, user_id, correo_electronico, selector)           
            app.logger.info("___________________Se conecto con exito al WS______________________")
            print("_____________________________Se conecto con exito al WS________________________________")
   
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
                        print("usuario ", usuario.id, " nombre estrategia ", triggerEstrategia.nombreEstrategia, " Hora de inicio:", triggerEstrategia.horaInicio)
                        # Si no hay un hilo iniciado para este usuario, lo inicia
                        hilo_id = f"{usuario.correo_electronico}_{triggerEstrategia.nombreEstrategia}"  # Utiliza el correo electrónico del usuario y el nombre de la estrategia como identificador único del hilo
                        hilo = threading.Thread(target=tarea_inicio, args=(user_id, app, triggerEstrategia, usuario))
                        get.hilo_iniciado_panel_control[hilo_id] = hilo
                        app.logger.info("___________________Se se inicia hilo de estrategia______________________")
                        hilo.start()
                        hilos.append(hilo)
                    else:
                        print("El usuario no existe en la lista triggerEstrategias.")
        except Exception as e:
            # Agregar el mensaje de error al registro de logs con nivel de error
            logging.error(str(e), exc_info=True)

        # Esperar a que todos los hilos terminen antes de finalizar
        for hilo in hilos:
            hilo.join()

def tarea_inicio(user_id,app,triggerEstrategia,usuario):
    
    # Aquí puedes enviar los datos a otra ruta en otro archivo Python
    # utilizando la librería requests o similar
    #traer los datos del usuario y trigger
    with app.app_context():
    
        # Realizar la consulta
       
        
        # Procesar los usuarios (aquí puedes hacer lo que necesites con los resultados)
        
     
 
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
                    print("estrategia ",url_destino," iniciada con exito")
                    print("**************************************************")
                else:
                        print("Error al enviar los datos de usuario en  automatizacion/programar_trigger/thread/tarea_inicio")

def tarea_fin():
    print("Tarea de finalización ejecutada")
    
    # Programar la próxima ejecución después de 24 horas
    schedule.every(24).hours.do(tarea_fin)


    response = requests.get(url_for('estrategias.detenerWS'))

    if response.status_code == 200:
        print("Detener WS exitoso")
    else:
        print("Error al detener WS")
         
    