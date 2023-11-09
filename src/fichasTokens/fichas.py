
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


def refrescoValorActualCuentaFichas(user_id):    
        repuesta_cuenta = get.pyRofexInicializada.get_account_report()
        reporte = repuesta_cuenta['accountData']
        available_to_collateral = reporte['availableToCollateral']
        fichas_usuario = db.session.query(Ficha).filter(Ficha.user_id == user_id).all()
        
        try:
            for ficha in fichas_usuario:                
                ficha.valor_cuenta_actual = available_to_collateral
                db.session.commit()
        except Exception as e:
               db.session.rollback()              

@fichas.route('/crearFicha', methods=['POST'])
def crear_ficha():
    try:
        data = request.json
        valor = data.get('valor')
        access_token = data.get('accessToken')
        cuenta = data.get('cuenta')
        correoElectronico = data.get('correoElectronico')
        total_cuenta = data.get('total_cuenta')
   
        
        
        # obtener los valores del accesToken
        if access_token:
            app = current_app._get_current_object()                    
            userid = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            exp_timestamp = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['exp']
            # Llamada a la función para generar el token
            token_con_llave = generar_token(userid, valor, cuenta)

            # Separa el token de la llave secreta
            token_generado = token_con_llave[:-64]
            llave_generada = token_con_llave[-64:]
            llave_bytes = llave_generada.encode('utf-8')
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
                token=token_generado, 
                llave = llave_bytes,
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
            
                     # Consulta todas las fichas del usuario dado
            #fichas_usuario = Ficha.query.filter_by(user_id=userid).all()
            #total_cuenta = available_to_collateral + portfolio
            total_para_fichas =  total_cuenta * 0.6
            print(total_para_fichas)
        
           # fichas_usuario = Ficha.query.filter_by(user_id=userid).all()
            fichas_usuario = db.session.query(Ficha).filter(Ficha.user_id == userid).all()
            try:
                for ficha in fichas_usuario:
                    print(ficha.token)
                    llave_bytes = ficha.llave
                    llave_hex = llave_bytes.hex()  # Convertimos los bytes a representación hexadecimal

                    # Luego, si necesitas obtener la llave original como bytes nuevamente
                    llave_original_bytes = bytes.fromhex(llave_hex)
                    #obtenemos el valor
                    decoded_token = jwt.decode(ficha.token, llave_original_bytes, algorithms=['HS256'])
                    
                    #obtenemos el numero
                    random_number = decoded_token.get('random_number')
                    # Agregamos random_number a la ficha
                    ficha.random_number = random_number
                    
                    
                    # Luego, convertimos las fichas a un formato que se pueda enviar como JSON
                    fichas_json = [
                        {
                            'id': ficha.id,
                            'user_id': ficha.user_id,
                            'monto_efectivo': ficha.monto_efectivo,
                            'interes': ficha.interes,
                            'estado': ficha.estado,
                            'random_number': ficha.random_number
                            # Agrega más campos si es necesario
                        }
                        for ficha in fichas_usuario
                    ]
                db.session.commit()
            except Exception as e:
               db.session.rollback()     
            return jsonify({'fichas_usuario': fichas_json})
                
          
        
          
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fichas.route("/fichasToken_fichas_generar/", methods=['POST'])   
def fichasToken_fichas_generar():
   try:  
        
        access_token = request.form['access_token_form_GenerarFicha'] 
        layouts = request.form['layoutOrigen']
        repuesta_cuenta = get.pyRofexInicializada.get_account_report()
        reporte = repuesta_cuenta['accountData']
        if reporte!=None:
            available_to_collateral = reporte['availableToCollateral']
            portfolio = reporte['portfolio']
           # layouts = 'layout'
        # print("detalle  ",available_to_collateral)
        # print("detalle ",portfolio)
        
            
            if access_token:
                    user_id = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            # Consulta todas las fichas del usuario dado
            #fichas_usuario = Ficha.query.filter_by(user_id=user_id).all()
            fichas_usuario = db.session.query(Ficha).filter(Ficha.user_id == user_id).all()
      
            total_cuenta = available_to_collateral + portfolio
            total_para_fichas =  total_cuenta * 0.6
            try:
                for ficha in fichas_usuario:
                    #print(ficha.monto_efectivo)
                    total_para_fichas=total_para_fichas - ficha.monto_efectivo
                    diferencia = available_to_collateral - ficha.valor_cuenta_creacion
                    porcien= diferencia*100
                    interes = porcien/available_to_collateral
                    interes = int(interes)
                    ficha.interes = interes
                    
                # print(interes)  
                    llave_bytes = ficha.llave
                    llave_hex = llave_bytes.hex()  # Convertimos los bytes a representación hexadecimal

                    # Luego, si necesitas obtener la llave original como bytes nuevamente
                    llave_original_bytes = bytes.fromhex(llave_hex)
                    #obtenemos el valor
                    decoded_token = jwt.decode(ficha.token, llave_original_bytes, algorithms=['HS256'])
                    
                    #obtenemos el numero
                    random_number = decoded_token.get('random_number')
                    # Agregamos random_number a la ficha
                    ficha.random_number = random_number
                    ficha.interes = interes
                    db.session.commit()
            except Exception as e:
                db.session.rollback()   
            
        
            print(total_para_fichas)    
           
            return render_template("fichas/fichasGenerar.html", datos=fichas_usuario,total_para_fichas=total_para_fichas,total_cuenta=total_cuenta, layout = layouts)
        else:
             flash('no posee datos') 
             return render_template("notificaciones/noPoseeDatos.html")   
   except:  
        print("no llama correctamente")  
        flash('error en la llamada a generacion de ficha')   
        return render_template("notificaciones/errorOperacionSinCuenta.html",layout = layouts)    
          
  # return render_template("login.html" )
    
 

@fichas.route("/fichasToken-fichas-listar/", methods=["POST"])   
def fichasToken_fichas_listar():
    try:  
        access_token = request.form['access_token_form_ListarFicha'] 
        layouts = request.form['layoutOrigen']
        repuesta_cuenta = get.pyRofexInicializada.get_account_report()
        reporte = repuesta_cuenta['accountData']
        available_to_collateral = reporte['availableToCollateral']
        portfolio = reporte['portfolio']
       # print("detalle  ",available_to_collateral)
       # print("detalle ",portfolio)
        #layouts = 'layout'
        
        if access_token:
                user_id = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
        # Consulta todas las fichas del usuario dado
       # fichas_usuario = Ficha.query.filter_by(user_id=user_id).all()
       # fichas_usuario = db.session.query(Ficha).filter(Ficha.user_id == user_id, Ficha.otra_condicion == valor).all()
        fichas_usuario = db.session.query(Ficha).filter(Ficha.user_id == user_id).all()
        
        try:
            for ficha in fichas_usuario:
                #print(ficha.monto_efectivo)
            
                diferencia = available_to_collateral - ficha.valor_cuenta_creacion
                porcien= diferencia*100
                interes = porcien/available_to_collateral
                interes = int(interes)
                ficha.interes = interes
            # print(interes)  
                llave_bytes = ficha.llave
                llave_hex = llave_bytes.hex()  # Convertimos los bytes a representación hexadecimal

                # Luego, si necesitas obtener la llave original como bytes nuevamente
                llave_original_bytes = bytes.fromhex(llave_hex)
                #obtenemos el valor
                decoded_token = jwt.decode(ficha.token, llave_original_bytes, algorithms=['HS256'])
                
                #obtenemos el numero
                random_number = decoded_token.get('random_number')
                # Agregamos random_number a la ficha
                ficha.random_number = random_number
                db.session.commit()
        except Exception as e:
               db.session.rollback()   
            
        return render_template("fichas/fichasListado.html", datos=fichas_usuario, layout = layouts)
    except:  
        print("no llama correctamente")  
        flash('fichasListado Incorrect')    
    
@fichas.route("/fichasToken-fichas-listar-sin-cuenta/", methods=["POST"])   
def fichasToken_fichas_listar_sin_cuenta():
    try:  
        access_token = request.form['access_token_form_ListarFicha'] 
        layouts = request.form['layoutOrigen']
      
       # print("detalle  ",available_to_collateral)
       # print("detalle ",portfolio)
       
        
        if access_token:
                user_id = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
        # Consulta todas las fichas del usuario dado
        #fichas_usuario = Ficha.query.filter_by(user_id=user_id).all()
        fichas_usuario = db.session.query(Ficha).filter(Ficha.user_id == user_id).all()

        try:
            for ficha in fichas_usuario:
                #print(ficha.monto_efectivo)
            
                diferencia =  ficha.valor_cuenta_actual - ficha.valor_cuenta_creacion
                porcien= diferencia*100
                interes = porcien/ficha.valor_cuenta_actual
                interes = int(interes)
                ficha.interes = interes
            # print(interes)  
                llave_bytes = ficha.llave
                llave_hex = llave_bytes.hex()  # Convertimos los bytes a representación hexadecimal

                # Luego, si necesitas obtener la llave original como bytes nuevamente
                llave_original_bytes = bytes.fromhex(llave_hex)
                #obtenemos el valor
                decoded_token = jwt.decode(ficha.token, llave_original_bytes, algorithms=['HS256'])
                
                #obtenemos el numero
                random_number = decoded_token.get('random_number')
                # Agregamos random_number a la ficha
                ficha.random_number = random_number
                db.session.commit()
        except Exception as e:
               db.session.rollback()   
            
        return render_template("fichas/fichasListado.html", datos=fichas_usuario, layout = layouts)
    except:  
        print("retorno incorrecto")  
        flash('retorno incorrecto')    
    
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

@fichas.route("/eliminar-ficha/",  methods=["POST"])
def eliminar_ficha():
  if request.method == 'POST':
    access_token = request.form['access_token']
    if access_token:
        app = current_app._get_current_object()
            
        ficha_id = request.form['eliminarFichaId']
       
        user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
               
        # Buscar y eliminar la ficha
        ficha = Ficha.query.filter_by(id=ficha_id, user_id=user_id).first()

        if ficha:
            db.session.delete(ficha)
            db.session.commit()
            db.session.close()
            flash('Ficha eliminada correctamente.')
            mensaje = "La ficha ha sido eliminada correctamente."
        else:
            mensaje = "No se encontró la ficha o no tienes permisos para eliminarla."

        fichas_usuario = Ficha.query.filter_by(user_id=user_id).all()
        
        repuesta_cuenta = get.pyRofexInicializada.get_account_report()
        reporte = repuesta_cuenta['accountData']
        available_to_collateral = reporte['availableToCollateral']
        portfolio = reporte['portfolio']
        
        total_cuenta = available_to_collateral + portfolio
        total_para_fichas =  total_cuenta * 0.6
        
        for ficha in fichas_usuario:
           # print(ficha.token)
            llave_bytes = ficha.llave
            llave_hex = llave_bytes.hex()  # Convertimos los bytes a representación hexadecimal

            # Luego, si necesitas obtener la llave original como bytes nuevamente
            llave_original_bytes = bytes.fromhex(llave_hex)
            #obtenemos el valor
            decoded_token = jwt.decode(ficha.token, llave_original_bytes, algorithms=['HS256'])
            
            #obtenemos el numero
            random_number = decoded_token.get('random_number')
            # Agregamos random_number a la ficha
            ficha.random_number = random_number
        return render_template("fichas/fichasGenerar.html", datos=fichas_usuario,total_para_fichas=total_para_fichas,total_cuenta=total_cuenta, )
        
