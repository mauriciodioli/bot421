
from flask import current_app,Blueprint, render_template, make_response,request, redirect, url_for, flash,jsonify
from utils.db import db
import tokens.token as Token
import jwt
from models.payment_page.Promotion import Promotion


pagoPedidos = Blueprint('pagoPedidos',__name__)


@pagoPedidos.route('/sistemaDePagos_pagoPedidos/',methods=['POST'])
def sistemaDePagos_pagoPedidos():
    try:
       
        data = request.form
        access_token = data.get('access_token_btn_finalizarPago')
        correo_electronico = data.get('correo_electronico_btn_finalizarPago')
        cluster_btn_finalizarPago = data.get('cluster_btn_finalizarPago')
        layoutOrigen = data.get('layoutOrigen')
        productoComercial = data.get('productoComercial')
        total = data.get('total_pago')
        if access_token and Token.validar_expiracion_token(access_token=access_token):
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            numero_de_cuenta = decoded_token.get("numero_de_cuenta")
            user_id = decoded_token.get("sub")
            
            promociones_todas = db.session.query(Promotion).all()
            db.session.close()

           # Crear un diccionario vacío para agrupar las promociones por cluster
            promociones_por_cluster = {}

            for promocione in promociones_todas:
                cluster = promocione.cluster
                # Verificar si el cluster ya existe en el diccionario
                if cluster not in promociones_por_cluster:
                    promociones_por_cluster[cluster] = []
                
                # Agregar la promoción al cluster correspondiente
                promociones_por_cluster[cluster].append({
                    'id': promocione.idPlan,
                    'description': promocione.description,
                    'price': float(total),
                    'reason': promocione.reason,
                    'discount': promocione.discount,
                    'image_url': promocione.image_url,
                    'state': promocione.state,
                    'currency_id': promocione.currency_id
                })

            # Filtrar las promociones por el cluster especificado en los datos de la solicitud
            cluster_solicitado = int(cluster_btn_finalizarPago)
            promociones_filtradas = promociones_por_cluster.get(cluster_solicitado, [])
            
            print(promociones_filtradas)
            promociones_por_cluster =[{'id': '', 'description': 'producto por unica vez', 'price': 5000.0, 'reason': 'Donacion 1', 'discount': 5.0, 'image_url': '', 'state': 'activo', 'currency_id': 'ARS'}, {'id': '', 'description': 'por unica vez', 'price': 9994.0, 'reason': 'Donacion 2', 'discount': 10.5, 'image_url': '', 'state': 'activo', 'currency_id': 'ARS'}]
        
        
            return render_template('productosComerciales/promociones/carrucelPromociones.html', promociones=promociones_por_cluster, layout=layoutOrigen, productoComercial='donacion')
        
        return jsonify({'error': 'Error de autenticación o datos incompletos'}), 401
      
    
    except Exception as e:
        # Manejo genérico de excepciones, devolver un mensaje de error
        return jsonify({'error': str(e)}), 500