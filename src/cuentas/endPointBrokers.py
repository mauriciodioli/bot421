
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
from models.brokers import Broker
from models.cuentas import Cuenta
endPointBrokers = Blueprint('endPointBrokers',__name__)

@endPointBrokers.route("/cuentas_endPointBrokers/")
def cuentas_endPointBrokers():
    try:
         # Filtrar los TriggerEstrategia que tengan manualAutomatico igual a "AUTOMATICO"
         with get_db_session() as session:
            todos_brokers = session.query(Broker).all()        
        
            total_brokers = len(todos_brokers)  # Obtener el total de instancias de TriggerEstrategia
          
            
            return render_template("brokers/broker.html", layout='layout_administracion', datos=todos_brokers)
    except:        
        return render_template("notificaciones/noPoseeDatos.html" )


@endPointBrokers.route("/cuentas-endPointBrokers-alta/",  methods=["POST"])
def cuentas_endPointBrokers_alta():
   if request.method == 'POST':
         todasLasCuentas = []
         api_url = request.form['api_url']
         ws_url = request.form['ws_url']
         nombre = request.form['nombre']
         descripcion = request.form['descripcion']
         print("api_url ",api_url)        
         print("ws_url",ws_url)
         print("nombre",nombre)
         # Codificar las cadenas usando UTF-8
        
        # crea_tabla_cuenta()
         try:     
            with get_db_session() as session:
                endpoint = Broker( 
                            id=None,   
                            api_url=api_url,
                            ws_url=ws_url,
                            nombre=nombre,
                            descripcion=descripcion                
                            )
            
                session.add(endpoint)  # Agregar la instancia de Cuenta a la sesión
                session.commit()  # Confirmar los cambios
                session.refresh(endpoint)  # Actualizar la instancia desde la base de datos para obtener el ID generado
                endpoint_id = endpoint.id  # Obtener el ID generado
            
            
                print("endPoint registrado exitosamente id !",endpoint_id)
            #   todasLasCuentas = get_cuentas_de_broker(user_id)
                
                todos_brokers = session.query(Broker).all()
                
             
                print("Cuenta registrada exitosamente!")            

                return render_template("brokers/broker.html",datos = todos_brokers)
             
         except:               
               
                print("No se pudo registrar la cuenta.")
                return 'problemas con la base de datos'



@endPointBrokers.route("/cuentas-endPointBrokers-eliminar/",  methods=["POST"])   
def cuentas_endPointBrokers_eliminar():
    try:
         if request.method == 'POST':
            id = request.form['eliminarEndPointId']  
            with get_db_session() as session:
                dato = session.query(Broker).get(id)  
                
                print(dato)
                session.delete(dato)
                session.commit()
                flash('Operation Removed successfully')
                todos_brokers = session.query(Broker).all()
                session.close()
                return render_template("cuentas/cuentasDeUsuario.html", datos =  todos_brokers)
    except: 
            flash('Operation No Removed')  
            with get_db_session() as session:     
                todos_brokers = session.query(Broker).all()
            
                
                return render_template('cuentas/cuentasDeUsuario.html', datos=todos_brokers) 


@endPointBrokers.route("/cuentas-editar-endpoint", methods=["POST"])
def cuentas_editar_endpoint():
    try:
        if request.method == 'POST':
            id = request.form['id']
            api_url = request.form['api_url']
            ws_url = request.form['ws_url']
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']

            endpoint = Broker.query.get(id)
            endpoint.api_url = api_url
            endpoint.ws_url = ws_url
            endpoint.nombre = nombre
            endpoint.descripcion = descripcion
            with get_db_session() as session:
                session.commit()
                flash('Los cambios se han guardado correctamente')
                todos_brokers = session.query(Broker).all()
               
                return render_template("cuentas/cuentasDeUsuario.html", datos =  todos_brokers)
    except Exception as e:
        flash('Error al guardar los cambios: ' + str(e))
  
    

@endPointBrokers.route("/cuenta-endpoint-all/", methods=["POST"])
def cuenta_endpoint_all():
    access_token = request.json.get('accessToken')

    if access_token and Token.validar_expiracion_token(access_token=access_token): 
        app = current_app._get_current_object()
        
        try:
            user_id = jwt.decode(access_token.encode(), app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            with get_db_session() as session:     
                endPointBrokers = session.query(Broker).all()
              
                if endPointBrokers:
                    data = []  # Lista para almacenar los datos de las cuentas
                    
                    for cuenta in endPointBrokers:
                        data.append({
                            'id': cuenta.id,
                            'nombre': cuenta.nombre,
                            # Agrega otros campos que desees incluir en las opciones del combo
                        })
                    
                    return jsonify({'endpoints': data})  # Devolver los datos en formato JSON
                    
                else:
                    return jsonify({'message': 'No se encontraron cuentas asociadas a este usuario.'}), 404
              
        except Exception as e:
            print("Error:", str(e))
            print("No se pudo registrar la cuenta.")
            session.rollback()  # Hacer rollback de la sesión
            return jsonify({'error': 'Hubo un error en la solicitud.'}), 500

    return render_template('notificaciones/tokenVencidos.html',layout = 'layout')     
   

@endPointBrokers.route("/cuentas-Broker/",  methods=["GET"])
def cuentas_Usuario_Broker():
   try:
      if request.method == 'GET': 
           with get_db_session() as session:
            cuentasBroker = session.query(Cuenta).all()
          
            return render_template("/cuentas/cuentasUsuariosBrokers.html",datos = cuentasBroker)
   except:
       print('no hay usuarios') 
   return 'problemas con la base de datos'

@endPointBrokers.route("/eliminar-broker-administracion/", methods=["POST"])
def eliminar_cuenta_broker_administracion():
    cuenta_id = request.form['eliminarCuentaId']
    with get_db_session() as session:
        cuenta = session.query(Cuenta).get(cuenta_id)
        if cuenta:
            session.delete(cuenta)
            session.commit()
            flash('Cuenta eliminada correctamente.')
        else:
            flash('Cuenta no encontrada.')

        cuentas = session.query(Cuenta).all()
        return render_template("/cuentas/cuntasUsuariosBrokers.html", datos=cuentas)

