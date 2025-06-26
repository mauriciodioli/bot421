<<<<<<< HEAD

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
import tokens.token as Token
from datetime import datetime, timedelta
import jwt
from models.usuario import Usuario
from models.brokers import Broker
from models.payment_page.plan import Plan
from models.payment_page.Promotion import Promotion


promociones = Blueprint('promociones',__name__)

@promociones.route('/sistemaDePagos_get_planes_promociones', methods=['GET'])
def sistemaDePagos_get_planes_promociones():
    layout = request.args.get('layout', 'layout')
    return render_template('productosComerciales/promociones/promociones.html', layout = layout)

@promociones.route('/productosComerciales_promociones_get_promociones', methods=['GET'])
def productosComerciales_promociones_get_promociones():
    layout = request.args.get('layout', 'layout')
    return render_template('productosComerciales/promociones/agregaPromocionesSinPlan.html', layout = layout)

@promociones.route('/productosComerciales_promociones_consulta_promociones', methods=['GET'])
def productosComerciales_promociones_consulta_promociones():
    layout = request.args.get('layout', 'layout')
    return render_template('productosComerciales/promociones/consultaPromociones.html', layout = layout)









@promociones.route('/productosComerciales_promociones_muestra_promociones', methods=['POST'])
def productosComerciales_promociones_muestra_promociones():  
    try:
      
        promociones = db.session.query(Promotion).all()
        db.session.close()

        # Serializar los planes
        promociones_serializados = [
            {
                'id': promocione.id,
                'idPlan': promocione.idPlan,
                'description': promocione.description,
                'price': promocione.price,
                'reason': promocione.reason,
                'discount': promocione.discount,
                'image_url': promocione.image_url,
                'state': promocione.state
            } for promocione in promociones
        ]

        return jsonify({'promociones': promociones_serializados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@promociones.route('/sistemaDePagos_get_promociones', methods=['POST'])
def sistemaDePagos_get_promociones():
    try: 
        data = request.json
        access_token = data.get('access_token')
        correo_electronico = data.get('correo_electronico')
      
        if access_token and Token.validar_expiracion_token(access_token=access_token): 
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            numero_de_cuenta = decoded_token.get("numero_de_cuenta")
            user_id = decoded_token.get("sub")        

            promociones = db.session.query(Promotion).all()
            db.session.close()
            if not promociones:
                return jsonify({'promociones': [], 'message': 'No hay promociones disponibles'})

            # Serializar los planes
            promociones_serializados = [
                {
                    'id': promocione.id,
                    'idPlan': promocione.idPlan,
                    'description': promocione.description,
                    'price': promocione.price,
                    'reason': promocione.reason,
                    'discount': promocione.discount,
                    'image_url': promocione.image_url,
                    'state': promocione.state,
                    'cluster': promocione.cluster,
                    'currency_id': promocione.currency_id 
                } for promocione in promociones
            ]

            return jsonify({'promociones': promociones_serializados})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    # Respuesta por defecto si no se cumplen las condiciones anteriores
    return jsonify({'error': 'Datos de entrada inválidos o token no válido'}), 400

    
@promociones.route('/productosComerciales_promociones_agrega_promociones', methods=['POST'])
def productosComerciales_promociones_agrega_promociones():  
    try:
        data = request.json
        promociones = data  # Esto asume que recibes una lista de promociones
        promocion = db.session.query(Promotion).order_by(Promotion.cluster.desc()).first()
        if promocion is None:
            nuevo_cluster = 1
        else:
            nuevo_cluster = promocion.cluster + 1
        
        for promocion_data in promociones:
            idPlan = promocion_data.get('idPlan')
            frecuencia = promocion_data.get('frecuencia')  # Nota: 'descripcion' es la clave que parece estar en tus datos
            monto = promocion_data.get('monto')
            reason = promocion_data.get('descripcion')
            razon = promocion_data.get('razon')
            currency_id = promocion_data.get('moneda')
            meses = promocion_data.get('meses')
           
          
            promocion_nueva = Promotion(
                idPlan=idPlan,
                description=str(nuevo_cluster),
                price=float(monto),
                reason=reason,
                discount= 10.5, #porcentaje de descuento
                image_url='',
                state='activo',
                cluster=nuevo_cluster,
                currency_id = currency_id
            )
           
            db.session.add(promocion_nueva)
            db.session.commit()
        
       
        promociones = db.session.query(Promotion).all()
        db.session.close()

        # Serializar los planes
        promociones_serializados = [
            {
                'id': promocione.id,
                'idPlan': promocione.idPlan,
                'description': promocione.description,
                'price': promocione.price,
                'reason': promocione.reason,
                'discount': promocione.discount,
                'image_url': promocione.image_url,
                'state': promocione.state,
                'cluster': promocione.cluster,
                'currency_id': promocione.currency_id 
                    
            } for promocione in promociones
        ]

        return jsonify({'promociones': promociones_serializados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@promociones.route('/productosComerciales_promociones_agrega_promocionesSinPlan', methods=['POST'])
def productosComerciales_promociones_agrega_promocionesSinPlan():
    try:
        data = request.json
        promociones = data  # Esto asume que recibes una lista de promociones  
        monto = data.get('precio')
        descripcion = data.get('descripcion')  # Nota: 'descripcion' es la clave que parece estar en tus datos
        descuento = data.get('descuento')
        reason = data.get('razon')
        estado = data.get('estado')
        currency_id = data.get('moneda')
        cluster = data.get('cluster')
        
        
        
        promocion_nueva = Promotion(
            idPlan='',
            description=descripcion,
            price=float(monto),
            reason=reason,
            discount= float(descuento), #porcentaje de descuento
            image_url='',
            state=estado,
            cluster=int(cluster),
            currency_id = currency_id
        )
        
        db.session.add(promocion_nueva)
        db.session.commit()
    
       
        promociones = db.session.query(Promotion).all()
        db.session.close()

        # Serializar los planes
        promociones_serializados = [
            {
                'id': promocione.id,
                'idPlan': promocione.idPlan,
                'description': promocione.description,
                'price': promocione.price,
                'reason': promocione.reason,
                'discount': promocione.discount,
                'image_url': promocione.image_url,
                'state': promocione.state,
                'cluster': promocione.cluster,
                'currency_id': promocione.currency_id 
                    
            } for promocione in promociones
        ]

        return jsonify({'promociones': promociones_serializados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@promociones.route('/productosComerciales_promociones_modifica_promocionesSinPlan', methods=['POST'])
def productosComerciales_promociones_modifica_promocionesSinPlan():
    try:
        data = request.json
        
        id = data.get('id')
        monto = data.get('precio')
        descripcion = data.get('descripcion')
        descuento = data.get('descuento')
        reason = data.get('razon')
        estado = data.get('estado')
        currency_id = data.get('moneda')
        cluster = data.get('cluster')
        
        # Buscar la promoción existente por ID
        promocion = db.session.query(Promotion).filter_by(id=int(id)).first()
        
        if not promocion:
            return jsonify({'error': 'Promoción no encontrada'}), 404
        
        # Actualizar los campos de la promoción
        promocion.price = float(monto)
        promocion.description = descripcion
        promocion.discount = float(descuento)
        promocion.reason = reason
        promocion.state = estado
        promocion.currency_id = currency_id
        promocion.cluster = cluster
        
        db.session.commit()
        
        # Recuperar todas las promociones para enviar al cliente
        promociones = db.session.query(Promotion).all()
        db.session.close()

        # Serializar las promociones
        promociones_serializados = [
            {
                'id': promocione.id,
                'idPlan': promocione.idPlan,
                'description': promocione.description,
                'price': promocione.price,
                'reason': promocione.reason,
                'discount': promocione.discount,
                'image_url': promocione.image_url,
                'state': promocione.state,
                'cluster': promocione.cluster,
                'currency_id': promocione.currency_id 
                    
            } for promocione in promociones
        ]

        return jsonify({'promociones': promociones_serializados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@promociones.route('/productosComerciales_promociones_elimina_promociones', methods=['POST'])
def productosComerciales_promociones_elimina_promociones():
    try:
        data = request.json
        
        id = data.get('id')       
        cluster = data.get('cluster')
        
        # Buscar la promoción existente por ID
        promocion = db.session.query(Promotion).filter_by(id=id).first()
        
        if not promocion:
            return jsonify({'error': 'Promoción no encontrada'}), 404
        
        db.session.delete(promocion)
        db.session.commit()  # Confirmar los cambios
        
        # Recuperar todas las promociones para enviar al cliente
        promociones = db.session.query(Promotion).all()
        db.session.close()
        # Serializar las promociones
        promociones_serializados = [
            {
                'id': promocione.id,
                'idPlan': promocione.idPlan,
                'description': promocione.description,
                'price': promocione.price,
                'reason': promocione.reason,
                'discount': promocione.discount,
                'image_url': promocione.image_url,
                'state': promocione.state,
                'cluster': promocione.cluster,
                'currency_id': promocione.currency_id 
            } for promocione in promociones
        ]

        return jsonify({'promociones': promociones_serializados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
   
=======

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
import tokens.token as Token
from datetime import datetime, timedelta
import jwt
from models.usuario import Usuario
from models.brokers import Broker
from models.payment_page.plan import Plan
from models.payment_page.Promotion import Promotion


promociones = Blueprint('promociones',__name__)

@promociones.route('/sistemaDePagos_get_planes_promociones', methods=['GET'])
def sistemaDePagos_get_planes_promociones():
    layout = request.args.get('layout', 'layout')
    return render_template('productosComerciales/promociones/promociones.html', layout = layout)

@promociones.route('/productosComerciales_promociones_get_promociones', methods=['GET'])
def productosComerciales_promociones_get_promociones():
    layout = request.args.get('layout', 'layout')
    return render_template('productosComerciales/promociones/agregaPromocionesSinPlan.html', layout = layout)

@promociones.route('/productosComerciales_promociones_consulta_promociones', methods=['GET'])
def productosComerciales_promociones_consulta_promociones():
    layout = request.args.get('layout', 'layout')
    return render_template('productosComerciales/promociones/consultaPromociones.html', layout = layout)









@promociones.route('/productosComerciales_promociones_muestra_promociones', methods=['POST'])
def productosComerciales_promociones_muestra_promociones():  
    try:
      
        promociones = db.session.query(Promotion).all()
        db.session.close()

        # Serializar los planes
        promociones_serializados = [
            {
                'id': promocione.id,
                'idPlan': promocione.idPlan,
                'description': promocione.description,
                'price': promocione.price,
                'reason': promocione.reason,
                'discount': promocione.discount,
                'image_url': promocione.image_url,
                'state': promocione.state
            } for promocione in promociones
        ]

        return jsonify({'promociones': promociones_serializados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@promociones.route('/sistemaDePagos_get_promociones', methods=['POST'])
def sistemaDePagos_get_promociones():
    try: 
        data = request.json
        access_token = data.get('access_token')
        correo_electronico = data.get('correo_electronico')
      
        if access_token and Token.validar_expiracion_token(access_token=access_token): 
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            numero_de_cuenta = decoded_token.get("numero_de_cuenta")
            user_id = decoded_token.get("sub")        

            promociones = db.session.query(Promotion).all()
            db.session.close()
            if not promociones:
                return jsonify({'promociones': [], 'message': 'No hay promociones disponibles'})

            # Serializar los planes
            promociones_serializados = [
                {
                    'id': promocione.id,
                    'idPlan': promocione.idPlan,
                    'description': promocione.description,
                    'price': promocione.price,
                    'reason': promocione.reason,
                    'discount': promocione.discount,
                    'image_url': promocione.image_url,
                    'state': promocione.state,
                    'cluster': promocione.cluster,
                    'currency_id': promocione.currency_id 
                } for promocione in promociones
            ]

            return jsonify({'promociones': promociones_serializados})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    # Respuesta por defecto si no se cumplen las condiciones anteriores
    return jsonify({'error': 'Datos de entrada inválidos o token no válido'}), 400

    
@promociones.route('/productosComerciales_promociones_agrega_promociones', methods=['POST'])
def productosComerciales_promociones_agrega_promociones():  
    try:
        data = request.json
        promociones = data  # Esto asume que recibes una lista de promociones
        promocion = db.session.query(Promotion).order_by(Promotion.cluster.desc()).first()
        if promocion is None:
            nuevo_cluster = 1
        else:
            nuevo_cluster = promocion.cluster + 1
        
        for promocion_data in promociones:
            idPlan = promocion_data.get('idPlan')
            frecuencia = promocion_data.get('frecuencia')  # Nota: 'descripcion' es la clave que parece estar en tus datos
            monto = promocion_data.get('monto')
            reason = promocion_data.get('descripcion')
            razon = promocion_data.get('razon')
            currency_id = promocion_data.get('moneda')
            meses = promocion_data.get('meses')
           
          
            promocion_nueva = Promotion(
                idPlan=idPlan,
                description=str(nuevo_cluster),
                price=float(monto),
                reason=reason,
                discount= 10.5, #porcentaje de descuento
                image_url='',
                state='activo',
                cluster=nuevo_cluster,
                currency_id = currency_id
            )
           
            db.session.add(promocion_nueva)
            db.session.commit()
        
       
        promociones = db.session.query(Promotion).all()
        db.session.close()

        # Serializar los planes
        promociones_serializados = [
            {
                'id': promocione.id,
                'idPlan': promocione.idPlan,
                'description': promocione.description,
                'price': promocione.price,
                'reason': promocione.reason,
                'discount': promocione.discount,
                'image_url': promocione.image_url,
                'state': promocione.state,
                'cluster': promocione.cluster,
                'currency_id': promocione.currency_id 
                    
            } for promocione in promociones
        ]

        return jsonify({'promociones': promociones_serializados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@promociones.route('/productosComerciales_promociones_agrega_promocionesSinPlan', methods=['POST'])
def productosComerciales_promociones_agrega_promocionesSinPlan():
    try:
        data = request.json
        promociones = data  # Esto asume que recibes una lista de promociones  
        monto = data.get('precio')
        descripcion = data.get('descripcion')  # Nota: 'descripcion' es la clave que parece estar en tus datos
        descuento = data.get('descuento')
        reason = data.get('razon')
        estado = data.get('estado')
        currency_id = data.get('moneda')
        cluster = data.get('cluster')
        
        
        
        promocion_nueva = Promotion(
            idPlan='',
            description=descripcion,
            price=float(monto),
            reason=reason,
            discount= float(descuento), #porcentaje de descuento
            image_url='',
            state=estado,
            cluster=int(cluster),
            currency_id = currency_id
        )
        
        db.session.add(promocion_nueva)
        db.session.commit()
    
       
        promociones = db.session.query(Promotion).all()
        db.session.close()

        # Serializar los planes
        promociones_serializados = [
            {
                'id': promocione.id,
                'idPlan': promocione.idPlan,
                'description': promocione.description,
                'price': promocione.price,
                'reason': promocione.reason,
                'discount': promocione.discount,
                'image_url': promocione.image_url,
                'state': promocione.state,
                'cluster': promocione.cluster,
                'currency_id': promocione.currency_id 
                    
            } for promocione in promociones
        ]

        return jsonify({'promociones': promociones_serializados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@promociones.route('/productosComerciales_promociones_modifica_promocionesSinPlan', methods=['POST'])
def productosComerciales_promociones_modifica_promocionesSinPlan():
    try:
        data = request.json
        
        id = data.get('id')
        monto = data.get('precio')
        descripcion = data.get('descripcion')
        descuento = data.get('descuento')
        reason = data.get('razon')
        estado = data.get('estado')
        currency_id = data.get('moneda')
        cluster = data.get('cluster')
        
        # Buscar la promoción existente por ID
        promocion = db.session.query(Promotion).filter_by(id=int(id)).first()
        
        if not promocion:
            return jsonify({'error': 'Promoción no encontrada'}), 404
        
        # Actualizar los campos de la promoción
        promocion.price = float(monto)
        promocion.description = descripcion
        promocion.discount = float(descuento)
        promocion.reason = reason
        promocion.state = estado
        promocion.currency_id = currency_id
        promocion.cluster = cluster
        
        db.session.commit()
        
        # Recuperar todas las promociones para enviar al cliente
        promociones = db.session.query(Promotion).all()
        db.session.close()

        # Serializar las promociones
        promociones_serializados = [
            {
                'id': promocione.id,
                'idPlan': promocione.idPlan,
                'description': promocione.description,
                'price': promocione.price,
                'reason': promocione.reason,
                'discount': promocione.discount,
                'image_url': promocione.image_url,
                'state': promocione.state,
                'cluster': promocione.cluster,
                'currency_id': promocione.currency_id 
                    
            } for promocione in promociones
        ]

        return jsonify({'promociones': promociones_serializados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@promociones.route('/productosComerciales_promociones_elimina_promociones', methods=['POST'])
def productosComerciales_promociones_elimina_promociones():
    try:
        data = request.json
        
        id = data.get('id')       
        cluster = data.get('cluster')
        
        # Buscar la promoción existente por ID
        promocion = db.session.query(Promotion).filter_by(id=id).first()
        
        if not promocion:
            return jsonify({'error': 'Promoción no encontrada'}), 404
        
        db.session.delete(promocion)
        db.session.commit()  # Confirmar los cambios
        
        # Recuperar todas las promociones para enviar al cliente
        promociones = db.session.query(Promotion).all()
        db.session.close()
        # Serializar las promociones
        promociones_serializados = [
            {
                'id': promocione.id,
                'idPlan': promocione.idPlan,
                'description': promocione.description,
                'price': promocione.price,
                'reason': promocione.reason,
                'discount': promocione.discount,
                'image_url': promocione.image_url,
                'state': promocione.state,
                'cluster': promocione.cluster,
                'currency_id': promocione.currency_id 
            } for promocione in promociones
        ]

        return jsonify({'promociones': promociones_serializados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
   
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
