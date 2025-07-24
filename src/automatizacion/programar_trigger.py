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
from utils.db_session import get_db_session 
import strategies.estrategiaSheetWS as estrategiaSheetWS 
from routes.api_externa_conexion.wsocket import wsocketConexion as conexion
import routes.api_externa_conexion.get_login as get
import tokens.token as Token
import strategies.estrategias as estrategias
from utils.common import Marshmallow, db
from datetime import datetime
import jwt
import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
programar_trigger = Blueprint('programar_trigger', __name__)

@programar_trigger.route('/trigger/')
def trigger():
    
    return render_template("/automatizacion/trigger.html")

@programar_trigger.route('/programador_trigger/', methods=['POST'])
def programador_trigger():
    horaInicio = request.json.get("horaInicio")
    horaFin = request.json.get("horaFin")
    cuenta = request.json.get("cuenta")
    usuario = request.json.get("usuario")
    correoElectronico = request.json.get("correoElectronico")
    access_token = request.json.get("tokenAcceso")
    accesoManualAutomatico = request.json.get("accesoManualAutomatico")

    if not access_token or not Token.validar_expiracion_token(access_token=access_token):
        return render_template('notificaciones/tokenVencidos.html', layout='layout')

    app = current_app._get_current_object()

    try:
        with get_db_session() as session:
            user_id = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']

            cuenta_obj = session.query(Cuenta).filter_by(user_id=user_id).first()
            if not cuenta_obj:
                raise Exception("Cuenta no encontrada para el usuario.")

            print(f"Cuenta: {cuenta_obj.userCuenta} / ID usuario: {user_id}")

            horaInicioSalvar, minutosInicioSalvar = horaInicio.split(':')
            horaFinSalvar, minutosFinSalvar = horaFin.split(':')

            hora_inicio = datetime(year=2023, month=7, day=3, hour=int(horaInicioSalvar), minute=int(minutosInicioSalvar))
            hora_fin = datetime(year=2023, month=7, day=3, hour=int(horaFinSalvar), minute=int(minutosFinSalvar))

            nueva_trigger = TriggerEstrategia(
                user_id=user_id,
                userCuenta=cuenta_obj.userCuenta,
                passwordCuenta=cuenta_obj.passwordCuenta,
                accountCuenta=cuenta_obj.accountCuenta,
                horaInicio=hora_inicio,
                horaFin=hora_fin,
                ManualAutomatico=accesoManualAutomatico
            )

            session.add(nueva_trigger)
            session.flush()  # asegura que tenga ID antes del commit

            triggerEstrategia_id = nueva_trigger.id
            print(f"Automático registrado con ID: {triggerEstrategia_id}")

        # Lógica post-guardado fuera del contexto
        programar_tareas(horaInicio, horaFin)
        return render_template("/")

    except Exception as e:
        print("Error en programador_trigger:", str(e))
        return jsonify(success=False, error=str(e)), 500



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











