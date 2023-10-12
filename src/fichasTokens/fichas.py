
# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies
    
)
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import jwt
from datetime import datetime, timedelta
import random
from models.usuario import Usuario
from models.cuentas import Cuenta
from models.ficha import Ficha
from tokens.token import generar_token

fichas = Blueprint('fichas',__name__)

def crea_tabla_ficha():
    ficha = Ficha(           
        user_id = "1",
        cuenta_broker_id = "1083",
        activo = "True",
        token = "", 
        monto_efectivo = 1.1,
        porcentaje_creacion = 10 ,
        valor_cuenta_creacion = 1.1,
        valor_cuenta_actual = 9.9,
        fecha_generacion = datetime(2023, 10, 5),
        interes = 10.5    
    )
    ficha.crear_tabla_ficha()
    print("Tabla creada!")


@fichas.route('/crearFicha', methods=['POST'])
def crear_ficha():
    try:
        data = request.json
        valor = data.get('valor')
        access_token = data.get('accessToken')
        cuenta = data.get('cuenta')
        correoElectronico = data.get('correoElectronico')
        total_cuenta = data.get('total_cuenta')
        crea_tabla_ficha()
        # obtener los valores del accesToken
        if access_token:
            app = current_app._get_current_object()                    
            userid = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            exp_timestamp = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['exp']
            access_token = generar_token(userid, valor, cuenta)
            #cuenta_id = Cuenta.query.filter_by(accountCuenta=cuenta).first()
            cuenta_id = db.session.query(Cuenta).filter_by(accountCuenta=cuenta).first()
            # almacenar el valor en el token
            # Ahora puedes crear una nueva ficha
            valorPorCien = valor * 100
            porcentajeCreacion = valorPorCien / total_cuenta  
            nueva_ficha = Ficha(
                user_id=userid,
                cuenta_broker_id=cuenta_id.id,  
                activo=True,  
                token=access_token, 
                monto_efectivo=valor,
                porcentaje_creacion=porcentajeCreacion, 
                valor_cuenta_creacion=total_cuenta, 
                valor_cuenta_actual=total_cuenta,  
                estado="PENDIENTE",  
                fecha_generacion=datetime.now(), 
                interes=0.0 
            )

            # Almacenar el token en la base de datos
            db.session.add(nueva_ficha)
            db.session.commit()

            return jsonify({'mensaje': 'Ficha creada exitosamente en la base de datos'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fichas.route("/fichasToken_fichas_generar/", methods=['POST'])   
def fichasToken_fichas_generar():
 #  try:  
        
        access_token = request.form['access_token_form_GenerarFicha'] 
        repuesta_cuenta = get.pyRofexInicializada.get_account_report()
        reporte = repuesta_cuenta['accountData']
        available_to_collateral = reporte['availableToCollateral']
        portfolio = reporte['portfolio']
       # print("detalle  ",available_to_collateral)
       # print("detalle ",portfolio)
       
        total_cuenta = available_to_collateral + portfolio
        total_para_fichas =  total_cuenta * 0.6
        print(total_para_fichas)
        if access_token:
                user_id = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
        # Consulta todas las fichas del usuario dado
        fichas_usuario = Ficha.query.filter_by(user_id=user_id).all()
        
        
        return render_template("fichas/fichasGenerar.html", datos=fichas_usuario)
        
   #except:  
   #     print("no lla correctamente")  
   #     flash('Loggin Incorrect')    
          
  # return render_template("login.html" )
    
 

@fichas.route("/fichasToken_fichas_listar/", methods=["POST"])   
def fichasToken_fichas_listar():
    
    
 return jsonify({'cuentas': data})  # Devolver los datos en formato JSON      
    

@fichas.route("/fichasToken_fichas_all/", methods=["POST"])   
def fichasToken_fichas_all():
    if request.method == 'POST':
        
        access_token = request.json.get('accessToken')

        todasLasCuentas = []

        if access_token:
            app = current_app._get_current_object()
            
            try:
                user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                usuario = Usuario.query.get(user_id)         
                cuentas = db.session.query(Cuenta).join(Usuario).filter(Cuenta.user_id == user_id).all()

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
                db.session.rollback()  # Hacer rollback de la sesión
                return jsonify({'error': 'Hubo un error en la solicitud.'}), 500
    
    return jsonify({'message': 'Solicitud no válida.'}), 400

@fichas.route("/fichasToken_fichas_usuarios_get",  methods=["GET"])
def fichasToken_fichas_usuarios_get():
   try:
      if request.method == 'GET': 
           cuentasBroker = db.session.query(Cuenta).all()
           db.session.close()
           return render_template("/cuentas/cuntasUsuariosBrokers.html",datos = cuentasBroker)
   except:
       print('no hay usuarios') 
   return 'problemas con la base de datos'

@fichas.route("/eliminar_fichasToken_fichas_usuarios_post/",  methods=["POST"])
def eliminar_fichasToken_fichas_usuarios_post():

    cuenta_id = request.form['eliminarCuentaId']
    cuenta = Cuenta.query.get(cuenta_id)
    db.session.delete(cuenta)
    db.session.commit()
    flash('Cuenta eliminada correctamente.')
    cuentas = db.session.query(Cuenta).all()
    db.session.close()
    return render_template("/cuentas/cuntasUsuariosBrokers.html",datos = cuentas)
