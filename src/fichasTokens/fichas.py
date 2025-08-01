
# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app
from sqlalchemy import func, cast, String, Integer
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload
import bcrypt
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
from utils.db_session import get_db_session 
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
import routes.api_externa_conexion.cuenta as cuentas
from models.ficha import Ficha
from models.trazaFicha import TrazaFicha
import hashlib
from tokens.token import generar_token
import tokens.token as Token

fichas = Blueprint('fichas',__name__)



def refrescoValorActualCuentaFichas(user_id,pyRofexInicializada,accountCuenta):    
      try:
            repuesta_cuenta = pyRofexInicializada.get_account_report(account=accountCuenta,environment=accountCuenta)
            if repuesta_cuenta and 'accountData' in repuesta_cuenta:
                reporte = repuesta_cuenta['accountData']
                available_to_collateral = reporte['availableToCollateral']
                with get_db_session() as session:
                    fichas_usuario = session.query(Ficha).filter(Ficha.user_id == user_id).all()
                    
                    calculoInteres(fichas_usuario,available_to_collateral)
                
                    
            else:
                # Aquí puedes agregar código adicional si deseas realizar alguna acción específica cuando no hay datos.
                pass

      except Exception as e:
            print(f"Error al refrescar el valor actual de la cuenta: {e}")
            return jsonify({'error': 'Error al refrescar el valor actual de la cuenta'}), 500
            # Manejo de errores, como registrar el error o enviar una notificación.
    # Aquí puedes agregar código adicional si deseas manejar la excepción de alguna manera.
        

@fichas.route('/fichas-asignar', methods = ['POST'])
def fichas_asignar():
    try:  
        access_token = request.form.get('access_token_forma')
        llave_ficha = request.form.get('tokenInput')  
        layouts = request.form.get('layoutOrigen') 
        if access_token and Token.validar_expiracion_token(access_token=access_token): 
                try:
                    user_id = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                except jwt.ExpiredSignatureError:
                    return jsonify({'error': 'Token de acceso expirado'}), 401
                except jwt.InvalidTokenError:
                    return jsonify({'error': 'Token de acceso no válido'}), 401

                if not llave_ficha:
                    return jsonify({'error': 'Falta el valor de la llave de ficha'}), 400

                if not layouts:
                    return jsonify({'error': 'Falta el valor de layout'}), 400
                
        
            
                with get_db_session() as session:
                
                        # Obtener todas las TrazaFichas con sus Fichas relacionadas
                    traza_fichas_con_fichas = session.query(TrazaFicha).join(Ficha).options(joinedload(TrazaFicha.ficha)).all()

                        # Puedes acceder a las fichas relacionadas de cada TrazaFicha en el bucle
                        
                
                
                    try:
                        for traza_ficha in traza_fichas_con_fichas:
                                ficha_relacionada = traza_ficha.ficha
                            
                                llave_bytes = ficha_relacionada.llave
                                llave_hex = llave_bytes.hex()  # Convertimos los bytes a representación hexadecimal

                                # Luego, si necesitas obtener la llave original como bytes nuevamente
                                llave_original_bytes = bytes.fromhex(llave_hex)
                                #obtenemos el valor
                                decoded_token = jwt.decode(ficha_relacionada.token, llave_original_bytes, algorithms=['HS256'])
                                    
                                #obtenemos el numero
                                random_number = decoded_token.get('random_number')
                                if int(llave_ficha) == random_number:  
                                    if traza_ficha.estado == 'ACEPTADA':
                                        if user_id != traza_ficha.user_id_traspaso:         
                                            #print("Llave correcta para la ficha")
                                            ficha_asignada = TrazaFicha(                                
                                                user_id_traspaso=user_id,
                                                fecha_traspaso=datetime.now(),                              
                                                estado_traza="PENDIENTE"
                                            )

                                        
                                            # Guarda la nueva ficha en la base de datos
                                            session.add(ficha_asignada)
                                            session.commit()
                                            
                                        
                                            break 
                                    
                                        
                                else:
                                    # Ninguna ficha tiene una llave que coincida con la proporcionada
                                    print("no es la llave correcta")
                        print("Llave ")
                    except Exception as e:
                      print(f"Error al procesar las fichas: {e}")  
                
                
                    #consultas de las neuvas fichas aceptadas
                    ficha_aceptadas =  session.query(TrazaFicha).filter(TrazaFicha.user_id_traspaso == user_id).all()
                
                   
                    return render_template("fichas/fichasListado.html", datos=ficha_aceptadas, layout = layouts)
        return render_template('notificaciones/tokenVencidos.html',layout = 'layout')       
    except:  
        print("retorno incorrecto")  
        flash('no posee fichas aún')   
        return render_template("fichas/fichasListado.html", datos=[], layout=layouts)
    
  

@fichas.route('/fichas-tomar', methods=['POST'])
def fichas_tomar():
    try:  
        access_token = request.form.get('access_token_forma')
        llave_ficha = request.form.get('tokenInput')  
        layouts = request.form.get('layoutOrigen') 
        if access_token and Token.validar_expiracion_token(access_token=access_token): 
            try:
                user_id = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token de acceso expirado'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Token de acceso no válido'}), 401

            if not llave_ficha:
                return jsonify({'error': 'Falta el valor de la llave de ficha'}), 400

            if not layouts:
                return jsonify({'error': 'Falta el valor de layout'}), 400
            
    
        
        
            with get_db_session() as session:
                fichas = session.query(Ficha).all()

            
            
                try:
                    for ficha in fichas:
                        if ficha.estado == 'PENDIENTE':
                            llave_bytes = ficha.llave
                            llave_hex = llave_bytes.hex()  # Convertimos los bytes a representación hexadecimal

                            # Luego, si necesitas obtener la llave original como bytes nuevamente
                            llave_original_bytes = bytes.fromhex(llave_hex)
                            #obtenemos el valor
                            decoded_token = jwt.decode(ficha.token, llave_original_bytes, algorithms=['HS256'])
                                
                            #obtenemos el numero
                            random_number = decoded_token.get('random_number')
                            if int(llave_ficha) == random_number:                
                                #print("Llave correcta para la ficha")
                                nueva_ficha = TrazaFicha(
                                    idFicha=ficha.id,
                                    user_id_traspaso=user_id,
                                    cuenta_broker_id_traspaso=ficha.cuenta_broker_id,
                                    token=ficha.token,
                                    fecha_traspaso=datetime.now(),
                                    fecha_habilitacion=datetime.now(),
                                    fecha_denuncia=None,
                                    fecha_baja=None,
                                    user_id_denuncia=None,
                                    user_id_alta=ficha.user_id,
                                    user_id_baja=None,
                                    estado_traza="ACEPTADO"
                                )

                            
                                # Guarda la nueva ficha en la base de datos
                                session.add(nueva_ficha)
                                session.commit()
                                #modifico el estado del usuario anterior
                                ficha.estado="ACEPTADO"
                                # Guarda la nueva ficha en la base de datos
                                session.add(ficha)
                                session.commit()
                            
                                break 
                            
                                
                        else:
                            # Ninguna ficha tiene una llave que coincida con la proporcionada
                            print("no es la llave correcta")
                    print("Llave ")
                except Exception as e:
                    print(f"Error al procesar las fichas: {e}")
                    return jsonify({'error': 'Error al procesar las fichas'}), 500
        
        
            #consultas de las neuvas fichas aceptadas
            ficha_aceptadas =  session.query(TrazaFicha).filter(TrazaFicha.user_id_traspaso == user_id).all()
        
                
            return render_template("fichas/fichasListado.html", datos=ficha_aceptadas, layout = layouts)
        return render_template('notificaciones/tokenVencidos.html',layout = 'layout')       
    except:  
        print("retorno incorrecto")  
        flash('no posee fichas aún')   
        return render_template("fichas/fichasListado.html", datos=[], layout=layouts)

    
    
@fichas.route('/crearFicha', methods=['POST'])
def crear_ficha():
    try:
        data = request.json
        valor = data.get('valor')
        access_token = data.get('accessToken')
        cuenta = data.get('cuenta')
        correoElectronico = data.get('correoElectronico')
        total_cuenta = data.get('total_cuenta')
        layouts = data.get('layoutOrigen')
        estado_ficha = data.get('estado_ficha')
       
   
        
        
        # obtener los valores del accesToken
        if access_token and Token.validar_expiracion_token(access_token=access_token): 
            app = current_app._get_current_object()                    
            userid = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            exp_timestamp = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['exp']
            # Llamada a la función para generar el token
            token_con_llave = generar_token(userid, valor, cuenta)

            # Separa el token de la llave secreta
            token_generado = token_con_llave[:-64]
            llave_generada = token_con_llave[-64:]
            llave_bytes = llave_generada.encode('utf-8')
            
            with get_db_session() as session:
                #cuenta_id = Cuenta.query.filter_by(accountCuenta=cuenta).first()
                cuenta_id = session.query(Cuenta).filter_by(accountCuenta=cuenta).first()
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
                    estado=estado_ficha,  
                    fecha_generacion=datetime.now(), 
                    interes=0.0 
                )

                # Almacenar el token en la base de datos
                session.add(nueva_ficha)
                session.commit()
                
                        # Consulta todas las fichas del usuario dado
                #fichas_usuario = Ficha.query.filter_by(user_id=userid).all()
                #total_cuenta = available_to_collateral + portfolio
                total_para_fichas =  total_cuenta * 0.6
                print(total_para_fichas)
            
                fichas_usuario = session.query(Ficha).filter_by(user_id=userid, estado='PENDIENTE').all()
                fichas_json = []
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
                        
                        # Suponiendo que ficha.fecha_generacion ya es un objeto datetime
                        fecha_generacion = ficha.fecha_generacion

                        # Formatear la fecha a 'YYYY-MM-DD HH:MM:SS'
                        fecha_formateada = fecha_generacion.strftime('%Y-%m-%d %H:%M:%S')
                        # Luego, convertimos las fichas a un formato que se pueda enviar como JSON
                        # Añadir la ficha a la lista
                        fichas_json.append({
                            'id': ficha.id,
                            'fecha_generacion': fecha_formateada,
                            'user_id': ficha.user_id,
                            'monto_efectivo': ficha.monto_efectivo,
                            'interes': ficha.interes,
                            'estado': ficha.estado,
                            'random_number': ficha.random_number
                        })
                    session.commit()
                 
                except Exception as e:
                   
                    return jsonify({
                                        "fichas": fichas_json, 
                                        "total_para_fichas": total_para_fichas, 
                                        "total_cuenta": total_cuenta, 
                                        "layout": layouts
                                    })

            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@fichas.route("/fichasToken_fichas_generar/", methods=['POST'])   
def fichasToken_fichas_generar():
  try:  
        total_cuenta = 0.0
        access_token = request.form['access_token_form_GenerarFicha'] 
        layouts = request.form['layoutOrigen']  
        cuenta = request.form['accounCuenta_form_GenerarFicha']
        selector = request.form['selector_form_GenerarFicha']      
              
        
            
        if access_token and Token.validar_expiracion_token(access_token=access_token): 
            user_id = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            #cuentas.indiceCuentas()            
            if cuenta=='':
                accountCuenta = obtenerCuentaDb(user_id=user_id)
            else:
                accountCuenta = cuenta
            reporte = cuentas.obtenerSaldoCuenta(account=accountCuenta)
          
            if reporte!=None:
                available_to_collateral = reporte['availableToCollateral']
                portfolio = reporte['portfolio']
            # layouts = 'layout'
            # print("detalle  ",available_to_collateral)
            # print("detalle ",portfolio)
            
            
            # Consulta todas las fichas del usuario dado
            #fichas_usuario = Ficha.query.filter_by(user_id=user_id).all()
            total_cuenta = available_to_collateral + portfolio
            total_para_fichas =  total_cuenta * 0.6
            with get_db_session() as session:
                fichas_usuario = session.query(Ficha).filter_by(user_id=user_id, estado='PENDIENTE').all()
                datos_fichas = []  # Lista para almacenar los datos de cada ficha

            
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
                        # Agregar los datos de la ficha a la lista
                        datos_fichas.append({
                            "id": ficha.id,
                            "user_id": ficha.user_id,
                            "broker_id": ficha.broker_id,
                            "cuenta_broker_id": ficha.cuenta_broker_id,
                            "activo": ficha.activo,
                            "token": ficha.token,
                            "llave": ficha.llave.hex(),  # Convertir a hexadecimal
                            "monto_efectivo": ficha.monto_efectivo,
                            "porcentaje_creacion": ficha.porcentaje_creacion,
                            "valor_cuenta_creacion": ficha.valor_cuenta_creacion,
                            "valor_cuenta_actual": ficha.valor_cuenta_actual,
                            "estado": ficha.estado,
                            "fecha_generacion": ficha.fecha_generacion,
                            "interes": ficha.interes,
                            "random_number": ficha.random_number
                        })
                        session.commit()
                except Exception as e:
                    session.rollback()   
                
            
                # print(total_para_fichas)    
                session.close()
                print("Datos de las fichas antes de enviar:")
                for ficha in datos_fichas:
                    print(ficha)
                return render_template("fichas/fichasGenerar.html", datos=datos_fichas,total_para_fichas=total_para_fichas,total_cuenta=total_cuenta, layout = layouts)
        else:
             flash('token vencido') 
             return render_template('usuarios/logOutSystem.html')  
  except:  
        print("no llama correctamente")  
        flash('no hay fichas creadas aún')   
        if total_cuenta < 1:
              return render_template("notificaciones/noPoseeDatosFichas.html",layout = layouts)  
        return render_template("fichas/fichasGenerar.html", datos=[],total_para_fichas=total_para_fichas,total_cuenta=total_cuenta, layout = layouts)
        
          

@fichas.route("/fichasToken-fichas-pagar/",  methods=["POST"])
def fichasToken_fichas_pagar():
  if request.method == 'POST':
    access_token = request.form['access_token']
   
    layouts = request.form['layoutOrigen']
    if access_token and Token.validar_expiracion_token(access_token=access_token): 
        app = current_app._get_current_object()
            
        id_ficha = request.form['pagarFichaId']
       
       
        user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
               
        # Buscar y eliminar la ficha
        with get_db_session() as session:
            ficha = session.query(Ficha).filter_by(id=id_ficha).first()
        
            if ficha:
                if ficha.estado == 'ENTREGADO':                          
                    ficha.estado = 'PAGADO'
                    session.add(ficha)
                    session.commit()
                    flash('Ficha pagada correctamente.')
                    mensaje = "La ficha ha sido pagada correctamente."
            else:
                mensaje = "No se encontró la ficha o no tienes permisos para acpetarla."
            fichas_usuario = session.query(Ficha).filter(Ficha.user_id == user_id,
                                                            Ficha.estado != 'STATIC',
                                                            Ficha.estado != 'PAGADO',
                                                            Ficha.estado != 'ACEPTADO').all()

          
        
            fichas_json = []

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
                # Suponiendo que ficha.fecha_generacion ya es un objeto datetime
                fecha_generacion = ficha.fecha_generacion

                # Formatear la fecha a 'YYYY-MM-DD HH:MM:SS'
                fecha_formateada = fecha_generacion.strftime('%Y-%m-%d %H:%M:%S')
                # Luego, convertimos las fichas a un formato que se pueda enviar como JSON
                # Añadir la ficha a la lista
            
            
            
                ficha_dict = {
                    "id": ficha.id,
                    "fecha_generacion": ficha.fecha_generacion.strftime('%Y-%m-%d %H:%M:%S'),
                    "monto_efectivo": ficha.monto_efectivo,
                    "interes": ficha.interes,
                    "estado": ficha.estado,
                    "random_number": ficha.random_number  # Asegúrate de que este valor esté disponible
                }
                fichas_json.append(ficha_dict)
                
            return jsonify({
                                "fichas": fichas_json,                           
                                "layout": layouts
                            })
    flash('token vencido') 
    return render_template('usuarios/logOutSystem.html') 


@fichas.route("/entregar-ficha/",  methods=["POST"])
def entregar_ficha():
  if request.method == 'POST':
    access_token = request.form['access_token']
    account = request.form['eliminarFichaCuenta']
    layouts = request.form['layoutOrigen']
    if access_token and Token.validar_expiracion_token(access_token=access_token): 
        app = current_app._get_current_object()
            
        ficha_id = request.form['eliminarFichaId']
       
        user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
        with get_db_session() as session:     
            # Buscar y eliminar la ficha
            ficha = session.query(Ficha).filter_by(id=ficha_id, user_id=user_id).first()          
            
            if ficha:
                if ficha.estado == 'PENDIENTE' or ficha.estado == 'ENTREGADO':
                            session.delete(ficha)
                            session.commit()
                        

                            flash('Ficha eliminada correctamente.')
                            mensaje = "La ficha ha sido eliminada correctamente."
                else:
                    mensaje = "No se encontró la ficha o no tienes permisos para eliminarla."
                fichas_usuario = []  # o asigna la lista que corresponda

                fichas_usuario = session.query(Ficha).filter_by(user_id=user_id, estado='PENDIENTE').all()
               
                pyRofexInicializada = get.ConexionesBroker.get(account)
                if pyRofexInicializada:
                    repuesta_cuenta = pyRofexInicializada['pyRofex'].get_account_report(account=account,environment=account)
                    reporte = repuesta_cuenta['accountData']
                    available_to_collateral = reporte['availableToCollateral']
                    portfolio = reporte['portfolio']
                    
                    total_cuenta = available_to_collateral + portfolio
                    total_para_fichas =  total_cuenta * 0.6
                    fichas_json = []

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
                        # Suponiendo que ficha.fecha_generacion ya es un objeto datetime
                        fecha_generacion = ficha.fecha_generacion

                        # Formatear la fecha a 'YYYY-MM-DD HH:MM:SS'
                        fecha_formateada = fecha_generacion.strftime('%Y-%m-%d %H:%M:%S')
                        # Luego, convertimos las fichas a un formato que se pueda enviar como JSON
                        # Añadir la ficha a la lista
                        fichas_json.append({
                            'id': ficha.id,
                            'fecha_generacion': fecha_formateada,
                            'user_id': ficha.user_id,
                            'monto_efectivo': ficha.monto_efectivo,
                            'interes': ficha.interes,
                            'estado': ficha.estado,
                            'random_number': ficha.random_number
                        })
                
                    if not fichas_usuario:
                        fichas_usuario = []
                

                    return jsonify({
                                    "fichas": fichas_json, 
                                    "total_para_fichas": total_para_fichas, 
                                    "total_cuenta": total_cuenta, 
                                    "layout": layouts
                                })
            else:
                return render_template('notificaciones/noPoseeDatos.html')
        
        
    flash('token vencido') 
    return render_template('usuarios/logOutSystem.html')      
 
    
@fichas.route("/fichasToken-fichas-entregar/", methods=["POST"])   
def fichasToken_fichas_entregar():    
    try:  
        access_token = request.form['access_token_form_EntregarFicha'] 
        layouts = request.form['layoutOrigen']
        account = request.form['accounCuenta_form_EntregarFicha']
        
        if access_token and Token.validar_expiracion_token(access_token=access_token): 
            user_id = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            with get_db_session() as session:
                # Consulta todas las fichas del usuario dado
                fichas_usuario = session.query(Ficha).filter(Ficha.user_id == user_id, 
                                                                Ficha.estado != 'STATIC',
                                                                Ficha.estado != 'ACEPTADO',
                                                                Ficha.estado != 'PAGADO').all()

                for ficha in fichas_usuario:
                    diferencia = ficha.valor_cuenta_actual - ficha.valor_cuenta_creacion
                    interes = int((diferencia * 100) / ficha.valor_cuenta_actual)
                    ficha.interes = interes
                    
                    llave_bytes = ficha.llave
                    llave_original_bytes = bytes.fromhex(llave_bytes.hex())
                    decoded_token = jwt.decode(ficha.token, llave_original_bytes, algorithms=['HS256'])
                    ficha.random_number = decoded_token.get('random_number')
                
                # Guardamos los cambios
                session.commit()
                
            
                # Renderizar la plantilla con los datos de ambas tablas
                return render_template(
                    "fichas/fichasEntregas.html", 
                    fichas=fichas_usuario,                
                    usuario_id=user_id, 
                    layout=layouts
                )
        
        flash('token vencido') 
        return render_template('usuarios/logOutSystem.html')
        
    except:  
      print("retorno incorrecto")  
      flash('no posee fichas aún')   
      return render_template("notificaciones/errorOperacionSinCuenta.html", layout = layouts) 
    

@fichas.route("/fichasToken-fichas-listar/", methods=["POST"])   
def fichasToken_fichas_listar():
    try:  
        access_token = request.form['access_token_form_ListarFicha'] 
        layouts = request.form['layoutOrigen']
        account = request.form['accounCuenta_form_ListarFicha']
        
        if access_token and Token.validar_expiracion_token(access_token=access_token): 
            user_id = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            with get_db_session() as session:
                # Consulta todas las fichas del usuario dado
                fichas_usuario = session.query(Ficha).filter(Ficha.user_id == user_id, Ficha.estado != 'STATIC').all()

                for ficha in fichas_usuario:
                    diferencia = ficha.valor_cuenta_actual - ficha.valor_cuenta_creacion
                    interes = int((diferencia * 100) / ficha.valor_cuenta_actual)
                    ficha.interes = interes
                    
                    llave_bytes = ficha.llave
                    llave_original_bytes = bytes.fromhex(llave_bytes.hex())
                    decoded_token = jwt.decode(ficha.token, llave_original_bytes, algorithms=['HS256'])
                    ficha.random_number = decoded_token.get('random_number')
                
                # Guardamos los cambios
                session.commit()
                
                # Obtener todas las TrazaFichas con sus Fichas relacionadas
                traza_fichas_con_fichas = session.query(TrazaFicha).join(Ficha).filter(
                    TrazaFicha.user_id_traspaso == user_id
                ).options(joinedload(TrazaFicha.ficha)).all()
        
                # Renderizar la plantilla con los datos de ambas tablas
                return render_template(
                    "fichas/fichasAdminUsuario.html", 
                    fichas=fichas_usuario, 
                    traza_fichas=traza_fichas_con_fichas,
                    usuario_id=user_id, 
                    layout=layouts
                )
            
            flash('token vencido') 
            return render_template('usuarios/logOutSystem.html')
        
    except:  
      print("retorno incorrecto")  
      flash('no posee fichas aún')   
      return render_template("notificaciones/errorOperacionSinCuenta.html", layout = layouts) 
    
    
@fichas.route("/fichasToken-fichas-listar-sin-cuenta/", methods=["POST"])   
def fichasToken_fichas_listar_sin_cuenta():
    try:  
        access_token = request.form['access_token_form_ListarFicha'] 
        layouts = request.form['layoutOrigen']
      
       # print("detalle  ",available_to_collateral)
       # print("detalle ",portfolio)
       
        
        if access_token and Token.validar_expiracion_token(access_token=access_token): 
                user_id = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                # Consulta todas las fichas del usuario dado
                with get_db_session() as session:
                    fichas_usuario = session.query(Ficha).filter(Ficha.user_id == user_id, Ficha.estado != 'STATIC').all()

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
                            valorInicial = decoded_token.get('valor')
                            # Agregamos random_number a la ficha
                            ficha.random_number = random_number
                            session.commit()
                        
                    except Exception as e:
                        session.rollback()   
                    traza_fichas_con_fichas = []  # o asigna la lista que corresponda
                    # Obtener todas las TrazaFichas con sus Fichas relacionadas
                    #traza_fichas_con_fichas = session.query(TrazaFicha).join(Ficha).options(joinedload(TrazaFicha.ficha)).all()
                # Filtramos las TrazaFichas por el user_id_traspaso
                    traza_fichas_con_fichas = session.query(TrazaFicha).join(Ficha).filter(TrazaFicha.user_id_traspaso == user_id).options(joinedload(TrazaFicha.ficha)).all()

                    for traza_ficha in traza_fichas_con_fichas:
                        ficha_relacionada = traza_ficha.ficha
                        llave_bytes = ficha_relacionada.llave
                        llave_hex = llave_bytes.hex()  # Convertimos los bytes a representación hexadecimal

                        # Luego, si necesitas obtener la llave original como bytes nuevamente
                        llave_original_bytes = bytes.fromhex(llave_hex)
                        #obtenemos el valor
                        decoded_token = jwt.decode(ficha_relacionada.token, llave_original_bytes, algorithms=['HS256'])
                            
                        #obtenemos el numero
                        random_number = decoded_token.get('random_number')
                        valorInicial = decoded_token.get('valor')
                        # Agregamos random_number a la ficha
                        ficha_relacionada.random_number = random_number

                        # Imprimir todos los campos de Ficha
                        #print("Campos de Ficha:")
                        #print(f"  ID: {ficha_relacionada.id}")
                        #print(f"  User ID: {ficha_relacionada.user_id}")
                        #print(f"  Cuenta Broker ID: {ficha_relacionada.cuenta_broker_id}")
                        #print(f"  Activo: {ficha_relacionada.activo}")
                        #print(f"  monto_efectivo: {ficha_relacionada.monto_efectivo}")
                        #print(f" interes: {ficha_relacionada.interes}")
                        #print(f"  estado: {ficha_relacionada.estado}")
                        #print(f" user_id_traspaso: {traza_ficha.user_id_traspaso}")
                        # ... Agrega más campos según sea necesario

                        #print("\n")  
                    
                            
                        
                   
                    return render_template("fichas/fichasListado.html", datos=traza_fichas_con_fichas,usuario_id= user_id,layout = layouts)
        flash('token vencido') 
        return render_template('usuarios/logOutSystem.html')
    
    except:  
        print("retorno incorrecto")  
        flash('no posee fichas aún')   
        return render_template("notificaciones/errorOperacionSinCuenta.html", layout = layouts) 
    
@fichas.route("/fichasToken_fichas_all/", methods=["POST"])   
def fichasToken_fichas_all():
    if request.method == 'POST':
        
        access_token = request.json.get('accessToken')

        todasLasCuentas = []

        if access_token and Token.validar_expiracion_token(access_token=access_token): 
            app = current_app._get_current_object()
            
            try:
                user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
                with get_db_session() as session:
                    usuario = session.query(Usuario).get(user_id)         
                    cuentas = session.query(Cuenta).join(Usuario).filter(Cuenta.user_id == user_id).all()
                    session.close()
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
        flash('token vencido') 
       # return render_template('notificaciones/tokenVencidos.html',layout = layouts)      
    
    return jsonify({'message': 'Solicitud no válida.'}), 400

@fichas.route("/fichasToken_fichas_usuarios_get",  methods=["GET"])
def fichasToken_fichas_usuarios_get():
   try:
      if request.method == 'GET': 
          with get_db_session() as session:
            cuentasBroker = session.query(Cuenta).all()
            session.close()
            return render_template("/cuentas/cuntasUsuariosBrokers.html",datos = cuentasBroker)
   except:
       print('no hay usuarios') 
   return 'problemas con la base de datos'

@fichas.route("/eliminar-ficha/",  methods=["POST"])
def eliminar_ficha():
  if request.method == 'POST':
    access_token = request.form['access_token']
    account = request.form['eliminarFichaCuenta']
    layouts = request.form['layoutOrigen']
    if access_token and Token.validar_expiracion_token(access_token=access_token): 
        app = current_app._get_current_object()
            
        ficha_id = request.form['eliminarFichaId']
       
        user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
        with get_db_session() as session:    
            # Buscar y eliminar la ficha
            ficha = session.query(Ficha).filter_by(id=ficha_id, user_id=user_id).first()          
            
            if ficha:
                if ficha.estado == 'PENDIENTE' or ficha.estado == 'ENTREGADO':
                            session.delete(ficha)
                            session.commit()
                        

                            flash('Ficha eliminada correctamente.')
                            mensaje = "La ficha ha sido eliminada correctamente."
                else:
                    mensaje = "No se encontró la ficha o no tienes permisos para eliminarla."
            fichas_usuario = []  # o asigna la lista que corresponda

            fichas_usuario = session.query(Ficha).filter_by(user_id=user_id, estado='PENDIENTE').all()
            session.close()
            pyRofexInicializada = get.ConexionesBroker.get(account)
            if pyRofexInicializada:
                repuesta_cuenta = pyRofexInicializada['pyRofex'].get_account_report(account=account,environment=account)
                reporte = repuesta_cuenta['accountData']
                available_to_collateral = reporte['availableToCollateral']
                portfolio = reporte['portfolio']
                
                total_cuenta = available_to_collateral + portfolio
                total_para_fichas =  total_cuenta * 0.6
                fichas_json = []

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
                    # Suponiendo que ficha.fecha_generacion ya es un objeto datetime
                    fecha_generacion = ficha.fecha_generacion

                    # Formatear la fecha a 'YYYY-MM-DD HH:MM:SS'
                    fecha_formateada = fecha_generacion.strftime('%Y-%m-%d %H:%M:%S')
                    # Luego, convertimos las fichas a un formato que se pueda enviar como JSON
                    # Añadir la ficha a la lista
                    fichas_json.append({
                        'id': ficha.id,
                        'fecha_generacion': fecha_formateada,
                        'user_id': ficha.user_id,
                        'monto_efectivo': ficha.monto_efectivo,
                        'interes': ficha.interes,
                        'estado': ficha.estado,
                        'random_number': ficha.random_number
                    })
            
                if not fichas_usuario:
                    fichas_usuario = []
            

                return jsonify({
                                "fichas": fichas_json, 
                                "total_para_fichas": total_para_fichas, 
                                "total_cuenta": total_cuenta, 
                                "layout": layouts
                            })
            else:
                return render_template('notificaciones/noPoseeDatos.html')
            
        
    flash('token vencido') 
    return render_template('usuarios/logOutSystem.html')      

@fichas.route("/reportar-ficha/",  methods=["POST"])
def reportar_ficha():
  if request.method == 'POST':
    access_token = request.form['access_token']
    layouts = request.form['layoutOrigen']
    if access_token and Token.validar_expiracion_token(access_token=access_token): 
        app = current_app._get_current_object()
            
        ficha_id = request.form['reportarFichaId']
        id_ficha = request.form['reportaridFicha']
       
        user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
        with get_db_session() as session:       
            # Buscar y eliminar la ficha
            ficha = session.query(Ficha).filter_by(id=id_ficha).first()
            trazaficha = session.query(TrazaFicha).filter_by(id=ficha_id).first()
            
            if ficha:
                if ficha.estado != 'ENTREGADO':
                    ficha.estado = 'REPORTADO'
                    trazaficha.estado_traza = 'REPORTADO'
                    session.commit()
                
                    flash('Ficha reportada correctamente.')
                    mensaje = "La ficha ha sido reportada correctamente."
            else:
                mensaje = "No se encontró la ficha o no tienes permisos para reportar."
            fichas_usuario = []  # o asigna la lista que corresponda

            fichas_usuario = session.query(Ficha).filter(Ficha.user_id == user_id).all()
         
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
                    valorInicial = decoded_token.get('valor')
                    # Agregamos random_number a la ficha
                    ficha.random_number = random_number
                    session.commit()
                
            except Exception as e:
                print("Error al calcular el interés:", str(e))
                return render_template('notificaciones/errorOperacionSinCuenta.html', layout = layouts)
           
           # Obtener todas las TrazaFichas con sus Fichas relacionadas
            traza_fichas_con_fichas = session.query(TrazaFicha).join(Ficha).options(joinedload(TrazaFicha.ficha)).all()

            for traza_ficha in traza_fichas_con_fichas:
                ficha_relacionada = traza_ficha.ficha
        

                # Imprimir todos los campos de Ficha
                #print("Campos de Ficha:")
                #print(f"  ID: {ficha_relacionada.id}")
                #print(f"  User ID: {ficha_relacionada.user_id}")
                #print(f"  Cuenta Broker ID: {ficha_relacionada.cuenta_broker_id}")
                #print(f"  Activo: {ficha_relacionada.activo}")
                #print(f"  monto_efectivo: {ficha_relacionada.monto_efectivo}")
                #print(f" interes: {ficha_relacionada.interes}")
                #print(f"  estado: {ficha_relacionada.estado}")
                #print(f" user_id_traspaso: {traza_ficha.user_id_traspaso}")
                # ... Agrega más campos según sea necesario

                #print("\n")  
            
                    
                
           
            return render_template("fichas/fichasListado.html", datos=traza_fichas_con_fichas,usuario_id= user_id,layout = layouts)
    flash('token vencido') 
    return render_template('usuarios/logOutSystem.html') 
   
@fichas.route("/recibir-ficha/",  methods=["POST"])
def recibir_ficha():
  if request.method == 'POST':
    access_token = request.form['recibir_access_token']
    layouts = request.form['layoutOrigen']
    if access_token and Token.validar_expiracion_token(access_token=access_token): 
        app = current_app._get_current_object()
            
        ficha_id = request.form['recibirFichaId']
        id_ficha = request.form['recibiridFicha']
       
        user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
               
        # Buscar y eliminar la ficha
        with get_db_session() as session:
            traza_ficha = session.query(TrazaFicha).filter_by(id=ficha_id, user_id_traspaso=user_id).first() 
            ficha = session.query(Ficha).filter_by(id=traza_ficha.idFicha).first()
        
            if traza_ficha:
                if traza_ficha.estado_traza == 'ACEPTADO':
                    session.delete(traza_ficha)              
                    ficha.estado = 'ENTREGADO'
                    session.add(ficha)
                    session.commit()
                    flash('Ficha recibida correctamente.')
                    mensaje = "La trazaficha ha sido eliminada correctamente."
            else:
                mensaje = "No se encontró la ficha o no tienes permisos para acpetarla."
            traza_fichas_con_fichas = []  # o asigna la lista que corresponda

        
            
        
                # Obtener todas las TrazaFichas con sus Fichas relacionadas
            traza_fichas_con_fichas = session.query(TrazaFicha).join(Ficha).options(joinedload(TrazaFicha.ficha)).all()
            session.close()
            for traza_ficha in traza_fichas_con_fichas:
                ficha_relacionada = traza_ficha.ficha
        

                # Imprimir todos los campos de Ficha
                #print("Campos de Ficha:")
                #print(f"  ID: {ficha_relacionada.id}")
                #print(f"  User ID: {ficha_relacionada.user_id}")
                #print(f"  Cuenta Broker ID: {ficha_relacionada.cuenta_broker_id}")
                #print(f"  Activo: {ficha_relacionada.activo}")
                #print(f"  monto_efectivo: {ficha_relacionada.monto_efectivo}")
                #print(f" interes: {ficha_relacionada.interes}")
                #print(f"  estado: {ficha_relacionada.estado}")
                #print(f" user_id_traspaso: {traza_ficha.user_id_traspaso}")
                # ... Agrega más campos según sea necesario

                #print("\n")  
            
                    
                
                
            return render_template("fichas/fichasListado.html", datos=traza_fichas_con_fichas,usuario_id= user_id,layout = layouts)
    flash('token vencido') 
    return render_template('usuarios/logOutSystem.html')  


def obtenerCuentaDb(user_id=None):
    with get_db_session() as session:
        cuenta = session.query(Cuenta).filter_by(user_id=user_id).first()
        return cuenta.accountCuenta

def calculoInteres(fichas_usuario,available_to_collateral):
    with get_db_session() as session:
        for ficha in fichas_usuario:
            diferencia =  ficha.valor_cuenta_actual - ficha.valor_cuenta_creacion
            porcien= diferencia*100
            interes = porcien/ficha.valor_cuenta_actual
            interes = int(interes)
            ficha.interes = interes
            ficha.valor_cuenta_actual = available_to_collateral
            session.commit()
        return interes