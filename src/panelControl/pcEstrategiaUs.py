# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app
from utils.db_session import get_db_session 
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from models.triggerEstrategia import TriggerEstrategia
from utils.db import db
import routes.api_externa_conexion.get_login as get
import jwt
from models.usuario import Usuario
from models.cuentas import Cuenta

pcEtrategiaUs = Blueprint('pcEtrategiaUs',__name__)
@pcEtrategiaUs.route("/pcEstrategiaUs-boton-a-m/", methods=['POST'])
def pcEstrategiaUs_boton_a_m():
    data = request.get_json()  # Asegúrate de importar 'request' desde Flask
    user_id = data.get('userId')
    trigger_id = data.get('triggerId')
    user_cuenta = data.get('userCuenta')
    
    resultado = cargaModo(user_id, trigger_id, user_cuenta)
    
    return jsonify({'resultado': 'Operación exitosa', 'trigger_data': resultado})

def cargaModo(user_id, trigger_id, user_cuenta):
    with get_db_session() as session:
        triggerEstrategia = session.query(TriggerEstrategia).filter_by(id=trigger_id).first()
        
        
        #print( triggerEstrategia.ManualAutomatico)
        if triggerEstrategia.ManualAutomatico == "AUTOMATICO":
            triggerEstrategia.ManualAutomatico = "MANUAL"
        else:     
            triggerEstrategia.ManualAutomatico = "AUTOMATICO"   
    
        session.commit()
        triggerEstrategia_list = session.query(TriggerEstrategia).filter_by(user_id=user_id).all()
        
        # Construir una lista de diccionarios con los datos que deseas devolver
        trigger_data = []
        for trigger in triggerEstrategia_list:
            
            trigger_data.append({
                    'id' : trigger.id,
                    'userId': trigger.user_id,
                    'userCuenta':  trigger.userCuenta,
                    'accountCuenta': trigger.accountCuenta,
                    'horaInicio': trigger.horaInicio.strftime('%H:%M:%S'),  # Convertir time a cadena
                    'horaFin': trigger.horaFin.strftime('%H:%M:%S'),  # Convertir time a cadena
                    'ManualAutomatico': trigger.ManualAutomatico,
                    'nombreEstrategia': trigger.nombreEstrategia,
                    
                    # Agregar más campos aquí
                })
        
       
        
        return trigger_data