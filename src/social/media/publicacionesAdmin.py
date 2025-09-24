# Creating Routes
from pipes import Template
from unittest import result
from flask import current_app

import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

from utils.db import db
import routes.api_externa_conexion.get_login as get
import tokens.token as Token
from datetime import datetime, timedelta
import jwt
import re

from models.usuario import Usuario
from utils.db_session import get_db_session

from models.publicaciones.publicacionCodigoPostal import PublicacionCodigoPostal
from models.publicaciones.publicaciones import Publicacion
from models.codigoPostal import CodigoPostal   

publicacionesAdmin = Blueprint('publicacionesAdmin', __name__)

@publicacionesAdmin.route('/media_consultaPublicaciones_muestra_administracion/', methods=['POST'])
def media_consultaPublicaciones_muestra_administracion():
    try:
        # Datos: prioriza JSON pero acepta form
        data = request.get_json(silent=True) or request.form or {}

        access_token = data.get('access_token_btn_publicaciones')
        if not access_token:
            return jsonify({'error': 'Token no proporcionado.'}), 401

        # Expiración propia
        if not Token.validar_expiracion_token(access_token=access_token):
            return jsonify({'error': 'Token inválido o expirado.'}), 401

        # Decodificar JWT
        try:
            decoded_token = jwt.decode(
                access_token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'El token ha expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401

        user_id = decoded_token.get("sub")
        if not user_id:
            return jsonify({'error': 'Token inválido: falta el user_id.'}), 401

        ambito = (data.get('ambito_btn_publicaciones') or '').strip()
        if not ambito:
            return jsonify({'error': 'Ámbito no proporcionado.'}), 400

        with get_db_session() as session:
            # Usuario válido y activo
            user = session.query(Usuario).filter(Usuario.id == user_id).first()
            if not user:
                return jsonify({'error': 'Usuario no encontrado.'}), 404
            if not user.activo:
                return jsonify({'error': 'El usuario no está activo.'}), 403

            # Publicaciones del ámbito
            publicaciones = (
                session.query(Publicacion)
                .with_entities(
                    Publicacion.id,
                    Publicacion.user_id,
                    Publicacion.titulo,
                    Publicacion.correo_electronico,
                    Publicacion.descripcion,
                    Publicacion.fecha_creacion,
                    Publicacion.texto,
                    Publicacion.imagen
                )
                .filter(Publicacion.ambito == ambito)
                .order_by(Publicacion.id.desc())
                .all()
            )

            data_out = []
            for p in publicaciones:
                precio, _ = obtenerPrecio(p.texto) if p.texto else (None, None)
                data_out.append({
                    'id': p.id,
                    'user_id': p.user_id,
                    'nombre_producto': p.titulo,
                    'texto': p.texto,
                    'precio_venta': precio,
                    'correoElectronico': p.correo_electronico,
                    'descripcion': p.descripcion,
                    'fechaCreacion': p.fecha_creacion,
                    'imagen_url': p.imagen
                })

            # Render siempre con el layout de admin
            return render_template(
                'media/publicaciones/consultaPublicacionesAdmin.html',  # <- corregido el nombre
                data=data_out,  # puede ser [] y tu template lo maneja
                layout='layout_administracion'
            )

    except Exception as e:
        current_app.logger.exception("Error en media_consultaPublicaciones_muestra_administracion")
        return jsonify({'error': 'Hubo un error en la solicitud.', 'detalle': str(e)}), 500



# ================== NUEVO: Helpers de Autenticación ==================
def _get_access_token_from_auth_header():
    """Lee y valida el header Authorization: Bearer <JWT>. Devuelve (token|None, msg_error|None)."""
    auth = request.headers.get('Authorization')
    if not auth:
        return None, 'Token de acceso no proporcionado'
    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None, 'Formato de token de acceso no válido'
    return parts[1], None


def _require_jwt_and_user():
    """
    Valida Authorization + exp + decodifica JWT.
    Devuelve (user_id, err_json_response|None). Si hay error, retorna (None, (jsonify, status)).
    """
    token, err = _get_access_token_from_auth_header()
    if err:
        return None, (jsonify({'error': err}), 401)

    if not Token.validar_expiracion_token(access_token=token):
        return None, (jsonify({'error': 'Token no válido o expirado'}), 401)

    try:
        decoded = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded.get('sub')
        if not user_id:
            return None, (jsonify({'error': 'Token inválido: falta el user_id'}), 401)
        return user_id, None
    except jwt.ExpiredSignatureError:
        return None, (jsonify({'error': 'El token ha expirado'}), 401)
    except jwt.InvalidTokenError:
        return None, (jsonify({'error': 'Token inválido'}), 401)


# === LISTAR todos los CP (para el <select>) ===
@publicacionesAdmin.route('/codigos-postales', methods=['GET'])
def listar_codigos_postales():
    user_id, err = _require_jwt_and_user()
    if err:
        return err

    limit = request.args.get('limit', default=100, type=int)
    try:
        with get_db_session() as session:
            rows = (session.query(CodigoPostal)
                          .order_by(CodigoPostal.id.asc())
                          .limit(limit)
                          .all())
            return jsonify({
                # devolvemos "codigo" para que el JS no cambie
                'codigos': [{'id': r.id, 'codigo': r.codigoPostal, 'ciudad': r.ciudad} for r in rows]
            }), 200
    except Exception as e:
        current_app.logger.exception("listar_codigos_postales")
        return jsonify({'error': 'Error listando códigos postales', 'detalle': str(e)}), 500

# === LISTAR CP de una publicación ===
@publicacionesAdmin.route('/publicaciones/<int:pub_id>/codigos-postales', methods=['GET'])
def listar_codigos_de_publicacion(pub_id):
    try:
        with get_db_session() as session:
            pub = session.query(Publicacion).filter_by(id=pub_id).first()
            if not pub:
                return jsonify({'error': f'Publicación {pub_id} no encontrada'}), 404

            rows = (
                session.query(CodigoPostal)
                .join(PublicacionCodigoPostal, PublicacionCodigoPostal.codigoPostal_id == CodigoPostal.id)
                .filter(PublicacionCodigoPostal.publicacion_id == pub_id)
                .order_by(CodigoPostal.id.asc())
                .all()
            )

            return jsonify({
                'codigos': [{'id': r.id, 'codigo': r.codigoPostal, 'ciudad': r.ciudad} for r in rows]
            }), 200
    except Exception as e:
        current_app.logger.exception("listar_codigos_de_publicacion")
        return jsonify({'error': 'Error listando códigos de la publicación', 'detalle': str(e)}), 500

@publicacionesAdmin.route('/publicaciones/<int:pub_id>/codigos-postales', methods=['POST'])
def agregar_codigo_a_publicacion(pub_id):
    data = request.get_json(silent=True) or {}
    codigo_str = (data.get('codigo_postal') or '').strip()
    if not codigo_str:
        return jsonify({'error': 'codigo_postal requerido'}), 400

    try:
        with get_db_session() as session:
            pub = session.query(Publicacion).filter_by(id=pub_id).first()
            if not pub:
                return jsonify({'error': f'Publicación {pub_id} no encontrada'}), 404

            cp = session.query(CodigoPostal).filter_by(codigoPostal=codigo_str).first()
            if not cp:
                return jsonify({'error': f'Código postal {codigo_str} no encontrado'}), 404

            existe = (session.query(PublicacionCodigoPostal)
                      .filter_by(publicacion_id=pub_id, codigoPostal_id=cp.id)
                      .first())
            payload = {'cp': {'id': cp.id, 'codigo': cp.codigoPostal, 'ciudad': cp.ciudad}}

            if existe:
                resp = jsonify({'ok': True, 'detail': 'ya existía', **payload})
                resp.headers['Cache-Control'] = 'no-store'
                return resp, 200

            rel = PublicacionCodigoPostal(publicacion_id=pub_id, codigoPostal_id=cp.id, estado='ACTIVO')
            session.add(rel)
           
            resp = jsonify({'ok': True, **payload})
            resp.headers['Cache-Control'] = 'no-store'
            return resp, 201

    except Exception as e:
        current_app.logger.exception("agregar_codigo_a_publicacion")
        try: session.rollback()
        except: pass
        return jsonify({'error': 'Error agregando código postal', 'detalle': str(e)}), 500


# === QUITAR relación Pub <-> CP ===
@publicacionesAdmin.route('/publicaciones/<int:pub_id>/codigos-postales/<int:cp_id>', methods=['DELETE'])
def quitar_codigo_de_publicacion(pub_id, cp_id):
    try:
        with get_db_session() as session:
            rel = (session.query(PublicacionCodigoPostal)
                   .filter_by(publicacion_id=pub_id, codigoPostal_id=cp_id)
                   .first())
            if not rel:
                return jsonify({'error': 'Relación no encontrada'}), 404

            session.delete(rel)
       
            return jsonify({'ok': True}), 200
    except Exception as e:
        current_app.logger.exception("quitar_codigo_de_publicacion")
        try: session.rollback()
        except: pass
        return jsonify({'error': 'Error eliminando código postal', 'detalle': str(e)}), 500



# ========================== UTIL EXISTENTE ==========================
def obtenerPrecio(data):
    patron_precio = r'\$\s?\d+(?:\.\d{3})*(?:,\d+)?'
    coincidencia = re.search(patron_precio, data)
    if coincidencia:
        precio = coincidencia.group()
        resto = data.replace(precio, '').strip()
        palabras = resto.split()
        resto_corto = ' '.join(palabras[:7]) + " ..."
        return precio, resto_corto
    else:
        resto_corto = ' '.join(data.split()[:7]) + " ..."
        return 0, resto_corto

# ---- helpers para columnas del pivote ----
def _pcp_cols():
    # Devuelve (col_pub, col_cp) según cómo se llamen realmente en tu modelo
    pcp = PublicacionCodigoPostal
    posibles_pub = ['publicacion_id', 'id_publicacion', 'publicacion', 'publicacionId']
    posibles_cp  = ['codigo_postal_id', 'id_codigo_postal', 'codigo_postal', 'codigoPostalId', 'cp_id']

    col_pub = next((getattr(pcp, n) for n in posibles_pub if hasattr(pcp, n)), None)
    col_cp  = next((getattr(pcp, n) for n in posibles_cp  if hasattr(pcp, n)), None)

    if not col_pub or not col_cp:
        raise RuntimeError(
            "PublicacionCodigoPostal: no se encontraron columnas esperadas. "
            "Ajustá la lista 'posibles_pub/posibles_cp' a tus nombres reales."
        )
    return col_pub, col_cp
