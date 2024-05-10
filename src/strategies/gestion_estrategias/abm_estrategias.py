
# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app

import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import jwt
from models.usuario import Usuario
from models.strategy import Strategy
from models.brokers import Broker
import strategies.gestion_estrategias.unidad_trader as utABM 
import tokens.token as Token

abm_estrategias = Blueprint('abm_estrategias',__name__)

@abm_estrategias.route("/abm-estrategias-mostrar/")
def abm_estrategias_mostrar():
    #try:
         # Filtrar los TriggerEstrategia que tengan manualAutomatico igual a "AUTOMATICO"
        
         todas_estrategias = db.session.query(Strategy).all()        
       
         total = len(todas_estrategias)  # Obtener el total de instancias de TriggerEstrategia
         db.session.close()
         
         return render_template("estrategias/ABMestrategias.html", datos=todas_estrategias)
    #except:        
     #   return render_template("notificaciones/noPoseeDatos.html" )


@abm_estrategias.route("/abm-estrategias-alta/",  methods=["POST"])
def abm_estrategias_alta():
   if request.method == 'POST':
         todasLasCuentas = []
         api_url = request.form['api_url']
         ws_url = request.form['ws_url']
         nombre = request.form['nombre']
         descripcion = request.form['descripcion']
     
         # Codificar las cadenas usando UTF-8
        
        # crea_tabla_cuenta()
         try:     
            
            endpoint = Strategy( 
                        id=None,   
                        api_url=api_url,
                        ws_url=ws_url,
                        nombre=nombre,
                        descripcion=descripcion                
                        )
          
            db.session.add(endpoint)  # Agregar la instancia de Cuenta a la sesión
            db.session.commit()  # Confirmar los cambios
            db.session.refresh(endpoint)  # Actualizar la instancia desde la base de datos para obtener el ID generado
            endpoint_id = endpoint.id  # Obtener el ID generado
           
           
            print("endPoint registrado exitosamente id !",endpoint_id)
         #   todasLasCuentas = get_cuentas_de_broker(user_id)
            
            todos_brokers = db.session.query(Strategy).all()
            
            db.session.close()
            print("Cuenta registrada exitosamente!")            

            return render_template("estrategias/ABMestrategias.html",datos = todos_brokers)
             
         except:               
                db.session.rollback()  # Hacer rollback de la sesión
                db.session.close()
                print("No se pudo registrar la cuenta.")
                return 'problemas con la base de datos'



@abm_estrategias.route("/abm-estrategias-eliminar/",  methods=["POST"])   
def abm_estrategias_eliminar():
    try:
         if request.method == 'POST':
            id = request.form['eliminarEstrategiaId']  
            dato = db.session.query(Strategy).get(id)  
            
            print(dato)
            db.session.delete(dato)
            db.session.commit()
            
            flash('Operation Removed successfully')
            todas = db.session.query(Strategy).all()
            db.session.close()
            return render_template("estrategias/ABMestrategias.html", datos =  todas)
    except: 
            flash('Operation No Removed')       
            todos_brokers = db.session.query(Strategy).all()
            db.session.close()
            
            return render_template('cuentas/cuentasDeUsuario.html', datos=todas) 


@abm_estrategias.route("/abm-estrategias-editar", methods=["POST"])
def abm_estrategias_editar():
    try:
        if request.method == 'POST':
            id = request.form['id']
            api_url = request.form['api_url']
            ws_url = request.form['ws_url']
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']

            endpoint = Strategy.query.get(id)
            endpoint.api_url = api_url
            endpoint.ws_url = ws_url
            endpoint.nombre = nombre
            endpoint.descripcion = descripcion

            db.session.commit()
            flash('Los cambios se han guardado correctamente')
            todas = db.session.query(Strategy).all()
            db.session.close()
            return render_template("estrategias/ABMestrategias.html", datos =  todas)
    except Exception as e:
        flash('Error al guardar los cambios: ' + str(e))
    
    

@abm_estrategias.route("/abm-estrategias-all-Brokers-post/", methods=["POST"])   
def abm_estrategias_all_Brokers_post():
    if request.method == 'POST':
        
        access_token = request.json.get('accessToken')

        todasLosBrokers = []

        if access_token and Token.validar_expiracion_token(access_token=access_token): 
            app = current_app._get_current_object()
            
            try:
                brokers = db.session.query(Broker).all()

                if brokers:
                    data = []  # Lista para almacenar los datos de las cuentas
                    
                    for broker in brokers:
                       
                        data.append({
                            'id': broker.id,
                            'api_url': broker.api_url,
                            'ws_url': broker.ws_url,
                            'nombre': broker.nombre,
                            'descripcion': broker.descripcion                         
                        })
                    
                    return jsonify({'brokers': data})  # Devolver los datos en formato JSON
                
                else:
                    return jsonify({'message': 'No se encontraron brokers.'}), 404
                  
            except Exception as e:
                print("Error:", str(e))
                print("No se pudo registrar los brokers.")
                db.session.rollback()  # Hacer rollback de la sesión
                return jsonify({'error': 'Hubo un error en la solicitud.'}), 500
    
    return jsonify({'message': 'Solicitud no válida.'}), 400

@abm_estrategias.route("/abm-estrategias-all/", methods=["POST"])
def abm_estrategias_all():
    access_token = request.json.get('accessToken')

    if access_token and Token.validar_expiracion_token(access_token=access_token): 
        app = current_app._get_current_object()
        
        try:
                     
            estrategias = db.session.query(Strategy).all()

            if estrategias:
                data = []  # Lista para almacenar los datos de las cuentas
                
                for estrategia in estrategias:
                    data.append({
                            'id': estrategia.id,
                            'api_url': estrategia.api_url,
                            'ws_url': estrategia.ws_url,
                            'nombre': estrategia.nombre,
                            'descripcion': estrategia.descripcion                         
                        })
                
                return jsonify({'estrategias': data})  # Devolver los datos en formato JSON
                
            else:
                return jsonify({'message': 'No se encontraron cuentas asociadas a este usuario.'}), 404
              
        except Exception as e:
            print("Error:", str(e))
            print("No se pudo registrar la cuenta.")
            db.session.rollback()  # Hacer rollback de la sesión
            return jsonify({'error': 'Hubo un error en la solicitud.'}), 500

    return jsonify({'message': 'Solicitud no válida.'}), 400

@abm_estrategias.route("/abm-estrategias-estrategias/",  methods=["GET"])
def abm_estrategias_estrategias():
   try:
      if request.method == 'GET': 
           cuentasBroker = db.session.query(Cuenta).all()
           db.session.close()
           return render_template("/cuentas/cuentasUsuariosBrokers.html",datos = cuentasBroker)
   except:
       print('no hay usuarios') 
   return 'problemas con la base de datos'

@abm_estrategias.route("/abm-estrategias-eliminar-estrategia-administracion/",  methods=["POST"])
def abm_estrategias_eliminar_estrategia_administracion():

    cuenta_id = request.form['eliminarCuentaId']
    cuenta = Cuenta.query.get(cuenta_id)
    db.session.delete(cuenta)
    db.session.commit()
    flash('Cuenta eliminada correctamente.')
    cuentas = db.session.query(Cuenta).all()
    db.session.close()
    return render_template("/cuentas/cuntasUsuariosBrokers.html",datos = cuentas)

