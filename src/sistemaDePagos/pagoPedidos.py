<<<<<<< HEAD

from flask import current_app,Blueprint, render_template, make_response,request, redirect, url_for, flash,jsonify
from utils.db import db
import tokens.token as Token
import jwt
import random
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
        ambito = data.get('ambito_btn_finalizarPago')
        botonPagoOnline = data.get('boton_pagoOnline')
        calendly_url = data.get('calendly_url')
        nombrePublicacionUsuario = data.get('nombrePublicacionUsuario')
        # Captura y procesa el JSON de pedidos
        pedido_data_json = data.get('pedido_data')  # JSON string enviado desde el formulario
       

        if access_token and Token.validar_expiracion_token(access_token=access_token):
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            numero_de_cuenta = decoded_token.get("numero_de_cuenta")
            user_id = decoded_token.get("sub")
            
           #promociones_todas = db.session.query(Promotion).all()
            db.session.close()

           # Crear un diccionario vacío para agrupar las promociones por cluster
            #promociones_por_cluster = {}

            #generar numero aletorio para el id de la promocion
            random_number = random.randint(1, 1000000)
            reason = 'Pedido'+str(random_number)
                # Agregar la promoción al cluster correspondiente
            productos_comerciales =[{
                'id': '',
                'description': 'producto por unica vez',
                'price': float(total),
                'reason': reason,
                'discount': 0.0,
                'image_url':'',
                'state': 'activo',
                'currency_id':'ARS',
                'correo_electronico': correo_electronico,                    
                'ambito':ambito,
                'cluster':random_number,
                'pedido_data_json':pedido_data_json, 
                'calendly_url':calendly_url,
                'nombrePublicacionUsuario':nombrePublicacionUsuario,
                'botonPagoOnline':botonPagoOnline
                                  
            }]

               
            print(productos_comerciales)
            productoComercial = 'donacion'
            return render_template('productosComerciales/pedidos/pagoPedidos.html', pedidos=productos_comerciales, layout=layoutOrigen, productoComercial=productoComercial)
    
        return jsonify({'error': 'Error de autenticación o datos incompletos'}), 401
      
    
    except Exception as e:
        # Manejo genérico de excepciones, devolver un mensaje de error
=======

from flask import current_app,Blueprint, render_template, make_response,request, redirect, url_for, flash,jsonify
from utils.db import db
import tokens.token as Token
import jwt
import random
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
        ambito = data.get('ambito_btn_finalizarPago')
        botonPagoOnline = data.get('boton_pagoOnline')
        calendly_url = data.get('calendly_url')
        nombrePublicacionUsuario = data.get('nombrePublicacionUsuario')
        # Captura y procesa el JSON de pedidos
        pedido_data_json = data.get('pedido_data')  # JSON string enviado desde el formulario
       

        if access_token and Token.validar_expiracion_token(access_token=access_token):
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            numero_de_cuenta = decoded_token.get("numero_de_cuenta")
            user_id = decoded_token.get("sub")
            
           #promociones_todas = db.session.query(Promotion).all()
            db.session.close()

           # Crear un diccionario vacío para agrupar las promociones por cluster
            #promociones_por_cluster = {}

            #generar numero aletorio para el id de la promocion
            random_number = random.randint(1, 1000000)
            reason = 'Pedido'+str(random_number)
                # Agregar la promoción al cluster correspondiente
            productos_comerciales =[{
                'id': '',
                'description': 'producto por unica vez',
                'price': float(total),
                'reason': reason,
                'discount': 0.0,
                'image_url':'',
                'state': 'activo',
                'currency_id':'ARS',
                'correo_electronico': correo_electronico,                    
                'ambito':ambito,
                'cluster':random_number,
                'pedido_data_json':pedido_data_json, 
                'calendly_url':calendly_url,
                'nombrePublicacionUsuario':nombrePublicacionUsuario,
                'botonPagoOnline':botonPagoOnline
                                  
            }]

               
            print(productos_comerciales)
            productoComercial = 'donacion'
            return render_template('productosComerciales/pedidos/pagoPedidos.html', pedidos=productos_comerciales, layout=layoutOrigen, productoComercial=productoComercial)
    
        return jsonify({'error': 'Error de autenticación o datos incompletos'}), 401
      
    
    except Exception as e:
        # Manejo genérico de excepciones, devolver un mensaje de error
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
        return jsonify({'error': str(e)}), 500