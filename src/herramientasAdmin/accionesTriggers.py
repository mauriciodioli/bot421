from flask import Blueprint, render_template,current_app ,session,request, make_response,redirect, url_for, flash,jsonify
from utils.common import Marshmallow, db, get
import routes.instrumentosGet as instrumentosGet
import routes.api_externa_conexion.validaInstrumentos as val
from utils.db_session import get_db_session 
import strategies.datoSheet as datoSheet
from models.servidores.servidorAws import ServidorAws
import routes.instrumentos as inst
from panelControlBroker.panelControl import enviar_leer_sheet
from panelControlBroker.panelControl import terminaConexionParaActualizarSheet
from strategies.datoSheet import update_precios
from werkzeug.exceptions import BadRequest
import pyRofex #lo utilizo para test
import time    #lo utilizo para test
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError  # Importar para el manejo de errores

from flask_paginate import Pagination, get_page_parameter

import json
import os
import copy

accionesTriggers = Blueprint('accionesTriggers',__name__)


@accionesTriggers.route("/herramAdmin_accionesTrigger_actualizaHorario/")
def herramAdmin_accionesTrigger_actualizaHorario(): 
    return render_template('automatizacion/actualizaHorarioShedule.html', layout='layout_administracion')

@accionesTriggers.route('/actualizaHorario', methods=['GET', 'POST'])
def actualiza_horario():
    mensaje_confirmacion = None
    if request.method == 'POST':
        hora_seleccionada = request.form.get('hora')
        response = make_response(render_template('automatizacion/actualizaHorarioShedule.html', hora=hora_seleccionada, layout='layout', mensaje='Hora almacenada correctamente'))
        
        # Almacenar la cookie
        response.set_cookie('horaGuardada', 'true', max_age=5*24*60*60)  # 5 días
        response.set_cookie('diferenciaHoraria', hora_seleccionada, max_age=7*24*60*60)  # 7 días
        
        
        # Acceder a la cookie 'horaGuardada' y 'diferenciaHoraria'
        hora_guardada = request.cookies.get('horaGuardada')
        hora_diferencia = request.cookies.get('diferenciaHoraria')
        # Si necesitas hacer algo con las horas almacenadas
        with get_db_session() as session:
            if hora_seleccionada:
                servidor = cargarDatosServidor(request, hora_seleccionada)
                if servidor:
                    session.add(servidor)  # Agrega la instancia a la sesión
                    session.commit()  # Comitea los cambios
                  
                print(f'Hora de diferencia almacenada: {hora_seleccionada}')
            

            
        return response
    
    return render_template('automatizacion/actualizaHorarioShedule.html', layout='layout_administracion')


@accionesTriggers.route('/get_server_time')
def get_server_time():
    from datetime import datetime
    # Obtener la hora actual del servidor
    hora_actual = datetime.now().strftime('%H:%M')
    return {'hora': hora_actual}





@accionesTriggers.route("/terminoEjecutarEstrategia/")
def terminoEjecutarEstrategia(): 
    return render_template('notificaciones/terminoEjecutarEstrategia.html')
@accionesTriggers.route('/herramientasAdmin_accionesTriggers_actualizaLuzTrigger')
def herramientasAdmin_accionesTriggers_actualizaLuzTrigger():
    luz = get.luzShedule_funcionando
    get.luzShedule_funcionando = False
    return jsonify({'luzTrigger_control':luz})
def control_tiempo_lectura_verifiar_estado(tiempo_espera_ms, tiempo_inicial_ms):
    # Obtener el tiempo actual en milisegundos
    tiempo_actual_ms = int(datetime.now().timestamp()) * 1000
    
    # Calcular la diferencia de tiempo desde la última vez que fue llamada la función
    diferencia_tiempo_ms = tiempo_actual_ms - tiempo_inicial_ms
    
    # Lógica para determinar si se puede realizar la lectura del sheet
    if diferencia_tiempo_ms < tiempo_espera_ms:
        # Aún no ha pasado suficiente tiempo, no se realiza la lectura del sheet
        #print(f"No se realiza la lectura del sheet. Tiempo transcurrido: {diferencia_tiempo_ms} ms.")
        # Retornar False u otra indicación según sea necesario
        return False
    else:
        # Ha pasado suficiente tiempo, se realiza la lectura del sheet
        minutos = diferencia_tiempo_ms // 60000
        segundos = (diferencia_tiempo_ms % 60000) // 1000
        #print(f"Se realiza la lectura del sheet. Tiempo transcurrido: {minutos}m {segundos}s.")
       
        
        # Reiniciar el tiempo inicial para la próxima llamada
        get.marca_de_tiempo_para_verificar_estado = tiempo_actual_ms
        
        # Retornar True u otra indicación según sea necesario
        return True
from datetime import datetime

def cargarDatosServidor(request, hora_diferencia):
    try:
        with get_db_session() as session:
            # Comprobación si el servidor ya existe
            servidor = session.query(ServidorAws).filter_by(nombre=request.form.get('nombre_servidor_contenedor')).first()

            if servidor:
                # Actualiza la diferencia horaria si es necesario
                if servidor.diferencia_horaria != hora_diferencia:
                    servidor.diferencia_horaria = hora_diferencia                
                    print(f"Diferencia horaria actualizada a: {hora_diferencia} para el servidor: {servidor.nombre}")
                return servidor  # Retorna la instancia actualizada
            else:
                # Si el servidor no existe, crea uno nuevo
                url = 'http://127.0.0.1:5001/index'
                ws_url = 'ssh -i .\bot421dbversion2.pem ubuntu@144.223.20.210'
                nombre = request.form.get('nombre_servidor_contenedor')
                descripcion = request.form.get('descripcion')
                instance_id = request.form.get('instancia_id')  # Obtén el valor del formulario

                if not instance_id:
                    print("Error: instance_id es requerido y no puede ser None.")
                    return None  # O maneja el error de otra manera

                # Obtén fecha y hora
                fecha_generacion = request.form.get('fecha_generacion')
                hora_generacion = request.form.get('hora_generacion')

                # Convertir fecha y hora a objetos datetime
                if fecha_generacion:
                    fecha_generacion = datetime.strptime(fecha_generacion, '%Y-%m-%d').date()  # Convertir a objeto date
                if hora_generacion:
                    hora_generacion = datetime.strptime(hora_generacion, '%H:%M:%S').time()  # Convertir a objeto time

                # Combina fecha y hora en un objeto datetime
                if fecha_generacion and hora_generacion:
                    hora_generacion = datetime.combine(fecha_generacion, hora_generacion)  # Combina ambos en un datetime

                hora_clientes = datetime.now()  # Considerar zona horaria si es necesario
                hora_servidor_str = request.form.get('hora_servidor')

                # Supongamos que quieres convertir hora_servidor también
                if hora_servidor_str:
                    # Convertir a un objeto datetime. Usamos la fecha actual como base para la hora.
                    hora_actual = datetime.now()
                    hora_servidor = datetime.combine(hora_actual.date(), datetime.strptime(hora_servidor_str, '%H:%M').time())
                else:
                    hora_servidor = None  # o un valor por defecto que tenga sentido para tu lógica

                hora_invierno = datetime.now()  # Considerar zona horaria si es necesario
                hora_verano = datetime.now()  # Considerar zona horaria si es necesario
                estado = request.form.get('estado')

                # Crea una instancia de ServidorAws con todos los atributos
                servidor = ServidorAws(
                            url=url,
                            ws_url=ws_url,
                            nombre=nombre,
                            descripcion=descripcion,                    
                            ip_address=None,
                            region=None, 
                            instance_type=None,
                            operating_system=None, 
                            instance_state=None, 
                            instance_id= request.form.get('instancia_id'),
                            uptime=None, 
                            cpu_usage=None,
                            memory_usage=None, 
                            last_status_check=None, 
                            fecha_generacion=None, 
                            diferencia_horaria=hora_diferencia, 
                            estado=None)

                # Configuración de otros atributos
                servidor.set_hora_clientes(hora_clientes)
                servidor.set_hora_servidor(hora_servidor)
                servidor.set_hora_invierno(hora_invierno)
                servidor.set_hora_verano(hora_verano)
                servidor.set_estado(estado)

                session.add(servidor)
                session.commit()
                return servidor  # Retorna la instancia creada
    except SQLAlchemyError as e:
        print(f"Error al crear o actualizar instancias de ServidorAws: {e}")
     
        return None

  