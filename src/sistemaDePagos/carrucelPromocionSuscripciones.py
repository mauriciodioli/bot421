
from flask import current_app,Blueprint, render_template, make_response,request, redirect, url_for, flash,jsonify
from utils.db import db
import tokens.token as Token
import jwt
from models.payment_page.Promotion import Promotion



carrucelPromocionSuscripciones = Blueprint('carrucelPromocionSuscripciones',__name__)


@carrucelPromocionSuscripciones.route('/sistemaDePagos_get_ofertas_suscripciones/',methods=['POST'])
def sistemaDePagos_get_ofertas_suscripciones():
    try:
        data = request.form
        access_token = data.get('access_token_btn_donacion')
        if access_token:
            correo_electronico = data.get('correo_electronico_btn_donacion')
            cluster_btn_donacion = data.get('cluster_btn_donacion')
            layoutOrigen = data.get('layoutOrigen')
            productoComercial = data.get('productoComercial')
            
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
                        'price': promocione.price,
                        'reason': promocione.reason,
                        'discount': promocione.discount,
                        'image_url': promocione.image_url,
                        'state': promocione.state,
                        'currency_id': promocione.currency_id
                    })

                # Filtrar las promociones por el cluster especificado en los datos de la solicitud
                cluster_solicitado = int(cluster_btn_donacion)
                promociones_filtradas = promociones_por_cluster.get(cluster_solicitado, [])

                response = make_response(render_template(
                    'productosComerciales/promociones/carrucelPromocionesSuscripciones.html',
                    promociones=promociones_filtradas,
                    layout=layoutOrigen,
                    productoComercial=productoComercial
                ))
                response.headers['Content-Type'] = 'text/html'
                return response
        else:
            response = make_response(render_template('notificaciones/logeePrimero.html', layout='layout_detalle_productos'))
            response.headers['Content-Type'] = 'text/html'
            return response
        
        return jsonify({'error': 'Error de autenticación o datos incompletos'}), 401
      
    
    except Exception as e:
        # Manejo genérico de excepciones, devolver un mensaje de error
        return jsonify({'error': str(e)}), 500
        
@carrucelPromocionSuscripciones.route('/sistemaDePagos_carrucelPromocionOfertas_get_promociones', methods=['POST'])
def sistemaDePagos_carrucelPromocionOfertas_get_promociones():
    try:
        data = request.json
        access_token = data.get('access_token')
        correo_electronico = data.get('correo_electronico')
        cluster = data.get('cluster')
        if access_token and Token.validar_expiracion_token(access_token=access_token): 
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            numero_de_cuenta = decoded_token.get("numero_de_cuenta")
            user_id = decoded_token.get("sub")        

            promociones = db.session.query(Promotion).all()
            db.session.close()

            # Serializar los planes
            promociones_serializados = [
                {
                    'id': promocione.idPlan,
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
