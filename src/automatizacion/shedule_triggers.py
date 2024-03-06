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
            fecha_inicio_shedule = data.get('fechaInicioShedule')  # Obtener el valor de fechaInicioShedule
            fecha_fin_shedule = data.get('fechaFinShedule')  # Obtener el valor de fechaFinShedule
            get.detener_proceso_automatico_triggers = False
            # Hacer lo que necesites con los valores obtenidos
            #print('Hora de inicio:', fecha_inicio_shedule)
            #print('Hora de fin:', fecha_fin_shedule)
             # Supongamos que shedule_triggers es tu objeto Blueprint de Flask
            app = current_app._get_current_object() 
            hilo_principal = threading.Thread(target=planificar_schedule, 
                                                args=('1', app, fecha_inicio_shedule, fecha_fin_shedule))

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
def terminar_hilos():
    # Aquí detienes los hilos iniciados desde planificar_schedule
    # Para ello, recorres el diccionario get.hilo_iniciado_panel_control y detienes los hilos que corresponden
    for hilo_id, hilo in get.hilo_iniciado_panel_control.items():
        if hilo.is_alive():
            print('_______________________________________')
            print('_______________________________________')
            print('__________TERMINO CONEXION WS__________')
            print('_______________________________________')
            print('_______________________________________')
            get.pyRofexInicializada.close_websocket_connection()
            hilo.join()  # Espera a que el hilo termine su ejecución si aún está vivo
    get.hilo_iniciado_panel_control.clear()  # Limpia el diccionario de hilos iniciados

def reiniciar_hilos():
    # Reiniciar solo los hilos que han terminado
    for hilo_id, hilo in get.hilo_iniciado_panel_control.items():
        if not hilo.is_alive():
            hilo.start()
        else:
            print(f"El hilo {hilo_id} aún está en ejecución y no será reiniciado.")

def planificar_schedule(user_id, app,tiempoInicioDelDia,tiempoFinDelDia):
    def ejecutar_schedule():
        llama_tarea = functools.partial(llama_tarea_cada_24_horas_estrategias, user_id, app)
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
        schedule.every().day.at(tiempoFinDelDia).do(terminar_hilos)


        while not get.detener_proceso_automatico_triggers:  # Bucle hasta que la bandera detener_proceso sea True
            hora_actual = datetime.now().strftime("%H:%M:%S")

            print("______________________________________________________________________________")
            print("comprobando schedule.run_pending() automatizacion shedule_trigger planificar_shedule  " )
            print('__inicio ',tiempoInicioDelDia,' ___fin ',tiempoFinDelDia,' __hora_actual ',hora_actual)
            #print("Diccionario de hilos iniciados:", get.hilo_iniciado_panel_control)
            print("______________________________________________________________________________")
            schedule.run_pending()
            time.sleep(60)

    hilo_schedule = threading.Thread(target=ejecutar_schedule)
    hilo_schedule.start()

def llama_tarea_cada_24_horas_estrategias(user_id, app):
     
    with app.app_context():
        
        print("______________________________conexion________________________________________________")
        environments = get.pyRofexInicializada.Environment.LIVE
        cuenta = db.session.query(Cuenta).filter_by(user_id=user_id).first()
        get.pyRofexInicializada.initialize(userCuenta=cuenta.user,passwordCuenta=cuenta.password,accountCuenta=cuenta.accountCuenta,environment=environments )
        conexion(app)
        print("______________________________conexion________________________________________________")
   
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
                    hilo = threading.Thread(target=tarea_inicio, args=(user_id, app, triggerEstrategia, usuario))
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
                  
                    
                    
                else:
                    print("El usuario no existe en la lista triggerEstrategias.")  

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
         
    