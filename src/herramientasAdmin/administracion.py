from flask import Blueprint, render_template, current_app, session, request, redirect, url_for, flash, jsonify
from utils.common import Marshmallow, db, get
import tokens.token as Token
import jwt
administracion = Blueprint('administracion', __name__)

@administracion.route('/herramientaAdmin-administracion', methods=['POST'])
def herramientaAdmin_administracion():
    try:
        # Obtener el token del encabezado Authorization
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            return jsonify({'error': 'Token de acceso no proporcionado'}), 401
        
        # Verificar formato del encabezado Authorization
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato de token de acceso no válido'}), 401
        
        # Obtener el token de acceso
        access_token = parts[1]

        # Validar expiración del token (asegúrate de que Token esté definido e importado)
        if Token.validar_expiracion_token(access_token=access_token):
            app = current_app._get_current_object()
            try:
                decoded_token = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
                user_id = decoded_token.get("sub")
                
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'El token ha expirado'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Token inválido'}), 401
            data = request.get_json()  # Convierte el cuerpo JSON en un diccionario de Python
            if not data:
                return jsonify({'error': 'Datos no enviados en el cuerpo de la solicitud'}), 400

            layout = data.get('layout')  # Obtener el valor de "layout"
            tipoUso = data.get('tipoUso')  # Obtener el valor de "tipoUso"

            # Validar que los valores requeridos estén presentes
            if not layout or not tipoUso:
                return jsonify({'error': 'Parámetros requeridos faltantes'}), 400

            # Renderizar la plantilla usando el layout
            return render_template('administracion/administracion.html', layout=layout)

              
        else:
                return jsonify({'error': 'Token no válido o expirado'}), 403

    except Exception as e:
        # Manejo de excepciones generales
        return jsonify({'error': 'Error en el servidor', 'detalle': str(e)}), 500
