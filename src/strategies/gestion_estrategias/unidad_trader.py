
# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app
from sqlalchemy.exc import IntegrityError
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import jwt
from models.usuario import Usuario
from models.cuentas import Cuenta
from models.triggerEstrategia import TriggerEstrategia
from models.unidadTrader import UnidadTrader
from routes.instrumentos import instrument_por_symbol



unidad_trader = Blueprint('unidad_trader',__name__)

@unidad_trader.route("/unidad-trader-mostrar/", methods=['POST'])
def unidad_trader_mostrar():
    # Obtener los datos de la solicitud POST
    UT_usuario_id = request.form.get('UT_usuario_id')
    UT_cuenta = request.form.get('UT_cuenta')
    UT_IdTrigger = request.form.get('UT_IdTrigger')
   
    
    
    ut_ars = []
    
    # Iterar sobre las listas de datos y filtrar los valores para 'tipo_de_activo' igual a 'ARS'
   # Iterar sobre los elementos de la lista a partir del segundo elemento
    for i in range(1, len(get.diccionario_global_sheet['argentina'])):
        value = get.diccionario_global_sheet['argentina'][i]
        if value[1] == 'ARG':
            print(value[1])
            resultado = instrument_por_symbol(value[0],UT_cuenta)
            for item in resultado:
                # Convierte el string JSON a un diccionario
                json_string = item[3].replace("'", '"')
                data = json.loads(json_string)
                # Accede al precio dentro del diccionario
                precio = data[0]['price']
                ut_ars.append(precio)

    # Encontrar el valor más alto de 'ut' para 'tipo_de_activo' igual a 'ARS'
    max_ut_ars = max(ut_ars)
    return jsonify({'max_ut_ars': max_ut_ars})
    
   


@unidad_trader.route("/unidad-trader-alta/", methods=['POST'])
def unidad_trader_alta():
    # Obtener los datos de la solicitud POST
    UT_cuenta = request.form.get('UT_cuenta')
    UT_usuario_id = int(request.form.get('UT_usuario_id'))
    UT_IdTrigger = int(request.form.get('UT_IdTrigger'))
    UT_unidadTrader = int(request.form.get('UT_unidadTrader'))
   

    # Verificar si ya existe una entrada para la combinación cuenta_id, usuario_id y trigger_id
    existing_ut = UnidadTrader.query.filter_by(accountCuenta=UT_cuenta, usuario_id=UT_usuario_id, trigger_id=UT_IdTrigger).first()

    if existing_ut:
        # Si existe, actualizar la entrada existente
        existing_ut.ut = UT_unidadTrader
    else:
        # Si no existe, agregar una nueva entrada
        ut = UnidadTrader(
            accountCuenta=UT_cuenta,
            usuario_id=UT_usuario_id,
            trigger_id=UT_IdTrigger,
            ut=UT_unidadTrader
        )
        db.session.add(ut)

    try:
        # Intentar realizar los cambios en la base de datos
        db.session.commit()
        
        resultado = cargaUT( UT_IdTrigger,UT_unidadTrader)
    
        return jsonify({'resultado': 'Operación exitosa', 'trigger_data': resultado})
      
    except IntegrityError as e:
        # Manejar errores de integridad (por ejemplo, violaciones de restricciones únicas)
        db.session.rollback()
        return f"Error: {str(e)}. No se pudo completar la operación."
    finally:
        # Cerrar la sesión
        db.session.close()

def cargaUT(trigger_id,UT_unidadTrader):
    try:
        trigger = db.session.query(TriggerEstrategia).filter_by(id=trigger_id).first()
        if not trigger:
            return None  # Retorna None si no se encuentra ningún objeto con el ID dado
        
        trigger_data = {
            'id': trigger.id,
            'userId': trigger.user_id,
            'userCuenta': trigger.userCuenta,
            'accountCuenta': trigger.accountCuenta,
            'horaInicio': trigger.horaInicio.strftime('%H:%M:%S'),
            'horaFin': trigger.horaFin.strftime('%H:%M:%S'),
            'ManualAutomatico': trigger.ManualAutomatico,
            'nombreEstrategia': trigger.nombreEstrategia,
            'ut':UT_unidadTrader
        }
        return trigger_data
    except Exception as e:
        print(f"Error al cargar datos del trigger: {e}")
        return None
    finally:
        db.session.close()
