
# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app
from utils.db_session import get_db_session 
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import tokens.token as Token
import jwt
from models.usuario import Usuario
from models.cuentas import Cuenta
from models.unidadTrader import UnidadTrader
from sqlalchemy.exc import SQLAlchemyError

cuentas = Blueprint('cuentas',__name__)

@cuentas.route("/cuentaUsuarioBroker_all_cuentas_post/", methods=["POST"])   
def cuentaUsuarioBroker_all_cuentas_post():
    if request.method == 'POST':
        
        access_token = request.json.get('accessToken')

        todasLasCuentas = []

        if access_token and Token.validar_expiracion_token(access_token=access_token): 
            app = current_app._get_current_object()
            
            try:
                user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                with get_db_session() as session:              
                    cuentas = session.query(Cuenta).join(Usuario).filter(Cuenta.user_id == user_id).all()
                
                    if cuentas:
                        data = []  # Lista para almacenar los datos de las cuentas
                        
                        for cuenta in cuentas:
                            password_cuenta = cuenta.passwordCuenta.decode('utf-8')
                            data.append({
                                'id': cuenta.id,
                                'user_id': cuenta.user_id,
                                'accountCuenta': cuenta.accountCuenta,
                                'userCuenta': cuenta.userCuenta,
                                'passwordCuenta': password_cuenta,
                                'selector': cuenta.selector
                            })
                        
                        return jsonify({'cuentas': data})  # Devolver los datos en formato JSON
                    
                    else:
                        return jsonify({'message': 'No se encontraron cuentas asociadas a este usuario.'}), 404
                  
            except Exception as e:
                print("Error:", str(e))
                print("No se pudo registrar la cuenta.")               
                return jsonify({'error': 'Hubo un error en la solicitud.'}), 500
    
    return jsonify({'message': 'Solicitud no válida.'}), 400

@cuentas.route("/cuentas-Usuario-Broker/",  methods=["GET"])
def cuentas_Usuario_Broker():
   try:
      if request.method == 'GET': 
           with get_db_session() as session:
            cuentasBroker = session.query(Cuenta).all()
         
            return render_template("/cuentas/cuntasUsuariosBrokers.html", layout = 'layout_administracion', datos = cuentasBroker)
   except:
       print('no hay usuarios') 
   return 'problemas con la base de datos'

@cuentas.route("/eliminar-Cuenta-broker-administracion/", methods=["POST"])
def eliminar_cuenta_broker_administracion():
    try:
        cuenta_id = request.form['eliminarCuentaId']
        with get_db_session() as session:
            cuenta = session.get(Cuenta, cuenta_id)  # ✅ método moderno

            if cuenta:
                session.delete(cuenta)
                flash('Cuenta eliminada correctamente.')
            else:
                flash('La cuenta no existe.')
            
            cuentas = session.query(Cuenta).all()
            return render_template("/cuentas/cuentasUsuariosBrokers.html", datos=cuentas)

    except SQLAlchemyError as e:
        flash('Ocurrió un error al intentar eliminar la cuenta. Por favor, inténtelo de nuevo.')
        print(f"Error de base de datos: {str(e)}")
        return redirect(request.url)

    except KeyError:
        flash('El identificador de la cuenta no fue proporcionado.')
        return redirect(request.url)

    except Exception as e:
        flash('Ocurrió un error inesperado. Por favor, inténtelo de nuevo.')
        print(f"Error inesperado: {str(e)}")
        return redirect(request.url)

  

@cuentas.route("/cuentas-cuentaUsuarioBroker-actualizarUt/", methods=["POST"])
def cuentas_cuentaUsuarioBroker_actualizarUt():
    # Obtener los datos enviados por AJAX
    ut_usuario = request.form.get('ut_usuario')
    access_token = request.form.get('access_token')
    refresh_token = request.form.get('refresh_token')
    selector = request.form.get('selector')
    usuario_id = request.form.get('usuario_id')
    accountCuenta = request.form.get('cuenta')

    if access_token and Token.validar_expiracion_token(access_token=access_token):
        app = current_app._get_current_object()

        try:
            # Decodificar el token JWT para obtener el user_id
            user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            
            
            with get_db_session() as session:
                cuentas = session.query(Cuenta).filter_by(user_id=user_id).all()
                
                if cuentas:
                    # El usuario ya tiene una cuenta, no se puede modificar
                    return jsonify({"status": "error", "message": "Tiene cuenta, no puede modificar desde aquí"})
                
                unidad_trader = session.query(UnidadTrader).filter_by(usuario_id=user_id,accountCuenta=0,trigger_id=0).first()
            
                    
                    

                if unidad_trader:
                    # Si la unidad_trader existe, actualizar ut_usuario
                    unidad_trader.ut = int(ut_usuario)
                else:
                    # Si no existe, crear una nueva instancia de UnidadTrader
                    unidad_trader = UnidadTrader(accountCuenta=0, usuario_id=user_id,trigger_id=0, ut=int(ut_usuario))
                    session.add(unidad_trader)
                
                # Guardar los cambios en la base de datos
                session.commit()
                return jsonify({"status": "success", "message": "UT actualizado con éxito"})
        
        except Exception as e:
           
            return jsonify({"status": "error", "message": str(e)})
        
      
    
    return jsonify({"status": "error", "message": "Datos incompletos o token inválido"})

