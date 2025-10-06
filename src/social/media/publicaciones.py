# Librerías estándar
import os
import random
import json
from datetime import datetime
import base64
import logging
from utils.db_session import get_db_session
# Librerías externas
import requests
import jwt
from PIL import Image as PILImage  # Renombrar la clase Image de Pillow
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
)
from werkzeug.utils import secure_filename
from sqlalchemy import func
from sqlalchemy.orm.exc import StaleDataError

# Importaciones del proyecto
from models.instrumento import Instrumento
from models.usuario import Usuario
from models.brokers import Broker
from models.publicaciones.publicaciones import Publicacion
from models.publicaciones.ambitos import Ambitos
from models.publicaciones.ambitoCategoria import AmbitoCategoria
from models.publicaciones.ambitoCategoriaRelation import AmbitoCategoriaRelation
from models.publicaciones.categoriaPublicacion import CategoriaPublicacion
from models.publicaciones.estado_publi_usu import Estado_publi_usu
from models.codigoPostal import CodigoPostal
from models.publicaciones.publicacion_imagen_video import Public_imagen_video
from models.usuarioPublicacionUbicacion import UsuarioPublicacionUbicacion
from models.publicaciones.ambito_codigo_postal import AmbitoCodigoPostal
from models.publicaciones.publicacionCodigoPostal import PublicacionCodigoPostal
from models.modelMedia.image import Image
from models.modelMedia.video import Video

from models.modelMedia.TelegramNotifier import TelegramNotifier
from utils.db import db
import re
import redis
import routes.api_externa_conexion.get_login as get
import tokens.token as Token
from social.buckets.bucketGoog import (
    upload_to_gcs, delete_from_gcs, mostrar_from_gcs,upload_chunk_to_gcs_with_redis
)


#import boto3
#from botocore.exceptions import NoCredentialsError


publicaciones = Blueprint('publicaciones',__name__)



# Configura el cliente de S3
#s3 = boto3.client('s3', aws_access_key_id='TU_ACCESS_KEY', aws_secret_access_key='TU_SECRET_KEY', region_name='tu-region')


# Configuración de Redis usando las variables de entorno
redis_host = os.getenv('REDIS_HOST', 'localhost')  # Valor por defecto 'localhost' si no se encuentra la variable
redis_port = os.getenv('REDIS_PORT', 6379)        # Valor por defecto 6379
redis_db = os.getenv('REDIS_DB', 0)                # Valor por defecto 0
# Conexión a Redis
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
MONEDAS_PERMITIDAS = {"USD","EUR","GBP","JPY","ARS","BRL","MXN","PLN","CHF","CNY"}


# Probar la conexión a Redis (opcional)
try:
    redis_client.ping()  # Verifica si Redis está accesible
    print("Conexión a Redis exitosa")
except redis.ConnectionError:
    print("No se pudo conectar a Redis")


@publicaciones.route('/media-publicaciones-mostrar/', methods=['POST']) 
def media_publicaciones_mostrar():
    try:
        layout = request.form.get('layout')
        ambito = request.form.get('ambito')
        idioma = request.form.get('lenguaje')
        codigoPostal = request.form.get('codigoPostal')
        categoria = request.form.get('categoria')

        if categoria == None or categoria == 'undefined' or categoria == 'null':
            categoria = '1' 
        if codigoPostal == None:
            codigoPostal = request.cookies.get('codigoPostal')
        if codigoPostal == 'null':
            codigoPostal = '1'
        if ambito == 'laboral':
            ambito = 'Laboral'

        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            return jsonify({'error': 'Token de acceso no proporcionado'}), 401

        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato de token de acceso no válido'}), 401

        access_token = parts[1]
        if Token.validar_expiracion_token(access_token=access_token):  
            app = current_app._get_current_object()                    
            decoded_token = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = decoded_token.get("sub")

            with get_db_session() as session:

                if codigoPostal == '1':
                    publicaciones_user = session.query(Publicacion).filter_by(user_id=user_id, ambito=ambito, idioma=idioma).all()
                else:
                    if categoria == '1':
                        ambito_id = session.query(Ambitos).filter_by(valor=ambito,idioma=idioma).first()
                        categoriaRelation = session.query(AmbitoCategoriaRelation).filter_by(ambito_id=ambito_id.id).first()
                        if categoriaRelation == None:                        
                            publicaciones_user = session.query(Publicacion).filter_by(user_id=user_id, ambito=ambito, idioma=idioma, codigoPostal=codigoPostal).all()  
                        else:
                            categoria_id = session.query(AmbitoCategoria).filter_by(id=categoriaRelation.ambitoCategoria_id).first()
                            publicaciones_user = session.query(Publicacion).filter_by(user_id=user_id, ambito=ambito, idioma=idioma, codigoPostal=codigoPostal, categoria_id=categoria_id.id).all()  
                    else:
                        if not categoria.isdigit():
                            ambito_id = session.query(Ambitos).filter_by(valor=ambito, idioma=idioma).first()
                            if ambito_id:
                                categoriaRelation = session.query(AmbitoCategoriaRelation).filter_by(ambito_id=ambito_id.id).all()
                                for categoriaR in categoriaRelation:
                                    categoria_id = session.query(AmbitoCategoria).filter_by(id=categoriaR.ambitoCategoria_id, valor=categoria).first()
                                    if categoria_id:
                                        publicaciones_user = session.query(Publicacion).filter_by(
                                            user_id=user_id, ambito=ambito, idioma=idioma,
                                            codigoPostal=codigoPostal, categoria_id=categoria_id.id
                                        ).all()  
                                        break
                        else:
                            publicaciones_user = session.query(Publicacion).filter_by(
                                user_id=user_id, ambito=ambito, idioma=idioma,
                                codigoPostal=codigoPostal, categoria_id=int(categoria)
                            ).all()  

                        if len(publicaciones_user) == 0:
                            publicaciones_user = session.query(Publicacion).filter_by(
                                user_id=user_id, ambito=ambito, idioma=idioma,
                                codigoPostal='1'
                            ).all()

                publicaciones_data = armar_publicacion_bucket_para_dpi(publicaciones_user, layout)
                return jsonify(publicaciones_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


    # Respuesta por defecto en caso de que algo falle sin lanzar una excepción
    return jsonify({'error': 'No se pudo procesar la solicitud'}), 500

@publicaciones.route('/media-publicaciones-mostrar-home/', methods=['POST'])
def media_publicaciones_mostrar_home():
    try:
        
        layout = request.form.get('layout')
        ambito = request.form.get('ambito')
        idioma = request.form.get('lenguaje')
        categoria = request.form.get('categoria')
        codigoPostal = request.form.get('codigoPostal')
        
        # Obtener el encabezado Authorization
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            return jsonify({'error': 'Token de acceso no proporcionado'}), 401
        
        # Verificar formato del encabezado Authorization
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato de token de acceso no válido'}), 401
        
        # Obtener el token de acceso
        access_token = parts[1]
        if Token.validar_expiracion_token(access_token=access_token):  
            app = current_app._get_current_object() 
                               
            decoded_token = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = decoded_token.get("sub")

            # Inicializar la lista de publicaciones
            publicaciones = []
            with get_db_session() as session:
            # Obtener todas las publicaciones del usuario
                publicacion_estados = session.query(Estado_publi_usu).filter_by(user_id=user_id).all()

                if publicacion_estados:
                        publicacion_estados = session.query(Estado_publi_usu).filter_by(user_id=user_id).all()

                        # IDs a excluir
                        eliminadas_ids = set()

                        for estado in publicacion_estados:
                            if estado.estado == 'eliminado' and estado.fecha_eliminado:
                                dias = (datetime.today().date() - estado.fecha_eliminado).days
                                if dias <= 30:
                                    eliminadas_ids.add(estado.publicacion_id)
                        categoria = safe_int(categoria, 0)           
                        
                       # Subquery: códigos (string) del ámbito
                        ambito_id = session.query(Ambitos).filter_by(valor=ambito,idioma=idioma).first()                        
                        subq_codigos = session.query(AmbitoCodigoPostal).filter_by(ambito_id=ambito_id.id).all()                        
                        cp_ids = [r.codigo_postal_id for r in subq_codigos]

                        # si no hay CPs, no hay publicaciones
                        if not cp_ids:
                            publicaciones = []
                        else:
                            publicaciones = session.query(Publicacion).filter(
                                Publicacion.estado == 'activo',
                                Publicacion.idioma == idioma,
                                Publicacion.categoria_id == int(categoria),
                                ~Publicacion.id.in_(eliminadas_ids)
                              
                            ).all()



                else:
                # Subquery: códigos (IDs) del ámbito
                    ambito_row = session.query(Ambitos).filter_by(valor=ambito, idioma=idioma).first()
                    if not ambito_row:
                        publicaciones = []
                    else:
                        subq_codigos = session.query(AmbitoCodigoPostal)\
                                            .filter_by(ambito_id=ambito_row.id).all()
                        cp_ids = [r.codigo_postal_id for r in subq_codigos]

                        # si no hay CPs, no hay publicaciones para este ámbito
                        if not cp_ids:
                            publicaciones = []
                        else:
                            # ⛔ antes estaba mal: filter_by(id=cp_ids)
                            codigo_postal_rows = session.query(CodigoPostal)\
                                                        .filter(CodigoPostal.id.in_(cp_ids)).all()

                            # ⚠ Tomar el CÓDIGO textual del CP (ajusta el atributo según tu modelo de CodigoPostal)
                            cp_valores = [
                                getattr(r, 'codigo', None) or
                                getattr(r, 'codigo_postal', None) or
                                getattr(r, 'codigoPostal', None)
                                for r in codigo_postal_rows
                            ]
                            cp_valores = [v for v in cp_valores if v]

                            if categoria == '1':
                                # reutilizo ambito_row; no vuelvo a consultar Ambitos
                                categoriaRelation = session.query(AmbitoCategoriaRelation)\
                                                        .filter_by(ambito_id=ambito_row.id).first()
                                if not categoriaRelation:
                                    publicaciones = []
                                else:
                                    # antes filtrabas por codigoPostal=codigoPostal (uno solo);
                                    # ahora IN sobre TODOS los CP del ámbito
                                    publicaciones = session.query(Publicacion).filter(
                                        Publicacion.estado == 'activo',
                                        Publicacion.idioma == idioma,
                                        Publicacion.codigoPostal.in_(cp_valores),
                                        Publicacion.categoria_id == categoriaRelation.ambitoCategoria_id
                                    ).all()
                            else:
                                publicaciones = session.query(Publicacion).filter(
                                    Publicacion.estado == 'activo',
                                    Publicacion.idioma == idioma,
                                    Publicacion.codigoPostal.in_(cp_valores),
                                    Publicacion.categoria_id == int(categoria)
                                ).all()

                    # Armar el diccionario con todas las publicaciones, imágenes y videos
                publicaciones_data = armar_publicacion_bucket_para_dpi(publicaciones, layout)

            
                return jsonify(publicaciones_data)
        else:
            return jsonify({'error': 'Token de acceso expirado'}), 401

    except Exception as e:
        # Manejo genérico de excepciones, devolver un mensaje de error
        return jsonify({'error': str(e)}), 500
    
    # Respuesta por defecto en caso de que algo falle sin lanzar una excepción
    return jsonify({'error': 'No se pudo procesar la solicitud'}), 500



@publicaciones.route('/media-publicaciones-mostrar-dpi/', methods=['POST'])
def media_publicaciones_mostrar_dpi():
    try:
        # Obtener el encabezado Authorization
        authorization_header = request.headers.get('Authorization')
         # Obtener el valor de 'ambitos' enviado en el cuerpo de la solicitud
        ambitos = request.form.get('ambitos')  # Si el contenido es application/x-www-form-urlencoded
        categoria = request.form.get('categoria')
        idioma = request.form.get('lenguaje')
        categoriaValor = request.form.get('categoriaValor') 
        codigoPostal = request.cookies.get('codigoPostal')
        if codigoPostal == None:
            codigoPostal = request.form.get('codigoPostal')
        if codigoPostal == None:
            codigoPostal = '1'
        if ambitos == 'inicialDominio':
            ambitos = 'Laboral'
        if categoria == None:
            categoria = '18'
        
        layout = 'layout_dpi'
        if not authorization_header:
            return jsonify({'error': 'Token de acceso no proporcionado'}), 401
        
        # Verificar formato del encabezado Authorization
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato de token de acceso no válido'}), 401
        
        # Obtener el token de acceso
        access_token = parts[1]
        if Token.validar_expiracion_token(access_token=access_token):  
            app = current_app._get_current_object() 

            # Inicializar la lista de publicaciones
            publicaciones = []
            with get_db_session() as session:
            # Obtener todas las publicaciones del usuario
                publicacion_estados = session.query(Estado_publi_usu).all()

                if publicacion_estados:
                    publicacion_estados = session.query(Estado_publi_usu).all()

                    # IDs a excluir
                    eliminadas_ids = set()

                    for estado in publicacion_estados:
                        if estado.estado == 'eliminado' and estado.fecha_eliminado:
                            dias = (datetime.today().date() - estado.fecha_eliminado).days
                            if dias <= 30:
                                eliminadas_ids.add(estado.publicacion_id)
                    if categoriaValor:
                        ambitosCategorias = session.query(AmbitoCategoria).filter_by(valor=categoriaValor).first()
                        if ambitosCategorias:
                            categoria = ambitosCategorias.id
                        else:
                         
                            raise ValueError(f"No se encontró una categoría con el valor: {categoriaValor}")
                  
                    # Subquery: códigos (string) del ámbito
                    ambito_id = session.query(Ambitos).filter_by(valor=ambitos,idioma=idioma).first()                        
                    subq_codigos = session.query(AmbitoCodigoPostal).filter_by(ambito_id=ambito_id.id).all()                        
                    cp_ids = [r.codigo_postal_id for r in subq_codigos]

                    # si no hay CPs, no hay publicaciones
                    if not cp_ids:
                        publicaciones = []
                    else:
                        publicaciones = session.query(Publicacion).filter(
                            Publicacion.estado == 'activo',
                            Publicacion.idioma == idioma,
                            Publicacion.categoria_id == int(categoria),
                            ~Publicacion.id.in_(eliminadas_ids)
                            
                        ).all()



                else:
                    # (mantengo tu bloque previo tal cual)
                    # Subquery: códigos (IDs) del ámbito
                    ambito_row = session.query(Ambitos).filter_by(valor=ambitos, idioma=idioma).first()
                    subq_codigos = session.query(AmbitoCodigoPostal).filter_by(ambito_id=ambito_row.id).all()
                    cp_ids = [r.codigo_postal_id for r in subq_codigos]

                    # si no hay CPs, no hay publicaciones para este ámbito
                    if not cp_ids:
                        publicaciones = []
                    else:
                        if categoria == '1':
                            ambito_id = session.query(Ambitos).filter_by(valor=ambitos, idioma=idioma).first()
                            categoriaRelation = session.query(AmbitoCategoriaRelation).filter_by(ambito_id=ambito_id.id).first()
                            categoria_id = session.query(AmbitoCategoria).filter_by(id=categoriaRelation.ambitoCategoria_id).first()

                            # antes: filter_by(..., codigoPostal=codigoPostal, ...)
                            # ahora: IN sobre TODOS los CP del ámbito
                            publicaciones = session.query(Publicacion).filter(
                                Publicacion.estado == 'activo',                                
                                Publicacion.idioma == idioma,
                                Publicacion.codigoPostal.in_(cp_ids),
                                Publicacion.categoria_id == categoria_id.id
                            ).all()
                        else:
                            publicaciones = session.query(Publicacion).filter(
                                Publicacion.estado == 'activo',                              
                                Publicacion.idioma == idioma,
                                Publicacion.codigoPostal.in_(cp_ids),
                                Publicacion.categoria_id == int(categoria)
                            ).all()

                    
                # Armar el diccionario con todas las publicaciones, imágenes y videos
                publicaciones_data = armar_publicacion_bucket_para_dpi(publicaciones,layout)
                
                return jsonify(publicaciones_data)

    except Exception as e:
       
        # Manejo genérico de excepciones, devolver un mensaje de error
        return jsonify({'error': str(e)}), 500

    # Respuesta por defecto en caso de que algo falle sin lanzar una excepción
    return jsonify({'error': 'No se pudo procesar la solicitud'}), 500


def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
















# Definir la función para armar las publicaciones con imágenes y videos



def armar_publicacion_bucket_para_dpi(publicaciones, layout):
    publicaciones_data = []

    with get_db_session() as session:
        for publicacion in publicaciones:
            imagen_video = (
                session.query(Public_imagen_video)
                .filter_by(publicacion_id=publicacion.id)
                .order_by(Public_imagen_video.id.asc())
                .first()
            )

            imagenes = []
            videos = []

            if imagen_video:
                if imagen_video.imagen_id:
                    try:
                        imagen = session.query(Image).filter_by(id=imagen_video.imagen_id).first()
                        if imagen:
                            filepath = imagen.filepath
                            imagen_url = filepath.replace('static/uploads/', '').replace('static\\uploads\\', '')  
                            if publicacion.imagen:
                                file_path = publicacion.imagen
                                file_data = None
                            else:
                                file_data, file_path = mostrar_from_gcs(imagen_url)
                            imagen_base64 = base64.b64encode(file_data).decode('utf-8') if file_data else None
                            if imagen_url:
                                imagenes.append({
                                    'id': imagen.id,
                                    'title': imagen.title,
                                    'description': imagen.description,
                                    'filepath': file_path,
                                    'imagen': imagen_base64,
                                    'mimetype': 'image/jpeg',
                                    'randomNumber': imagen.randomNumber,
                                    'size': imagen.size
                                })
                    except Exception as e:
                        logging.error(f"Error imagen {imagen_video.imagen_id}: {e}")

                if imagen_video.video_id:
                    try:
                        video = session.query(Video).filter_by(id=imagen_video.video_id).first()
                        if video:
                            filepath = video.filepath
                            video_url = filepath.replace('static/uploads/', '').replace('static\\uploads\\', '')
                            file_data, file_path = mostrar_from_gcs(video_url)
                            video_base64 = base64.b64encode(file_data).decode('utf-8') if file_data else None
                            if video_url:
                                videos.append({
                                    'id': video.id,
                                    'title': video.title,
                                    'description': video.description,
                                    'video': video_base64,
                                    'filepath': file_path,
                                    'mimetype': video.mimetype,
                                    'size': video.size
                                })
                    except Exception as e:
                        logging.error(f"Error video {imagen_video.video_id}: {e}")

            if not publicacion.imagen:
                if imagenes:
                    publicacion.imagen = imagenes[0]['filepath']
                elif videos:
                    publicacion.imagen = videos[0]['filepath']
                session.commit()  # se hace dentro del contexto seguro

            categoriaPublicacion = session.query(CategoriaPublicacion).filter_by(publicacion_id=publicacion.id).first()
            categoria = None
            if categoriaPublicacion:
                categoria = session.query(AmbitoCategoria).filter_by(id=categoriaPublicacion.categoria_id).first()
            simbolo = retorna_simbolo_desde_codigo_postal(session,publicacion.codigoPostal,publicacion.idioma)
            if publicacion.precio:
                if random.random() < 0.5:
                    descuento_porcentaje = random.choice([10, 15, 20, 25, 30, 35, 40])
                    descuento = f"{descuento_porcentaje}% OFF"
                    precio_original_num = round(publicacion.precio / (1 - descuento_porcentaje / 100), 2)
                    precio_original = f"{simbolo} {precio_original_num}"  # usa el mismo símbolo
                else:
                    descuento = None
                    precio_original = None
            else:
                descuento = None
                precio_original = None

            publicaciones_data.append({
                'publicacion_id': publicacion.id,
                'user_id': publicacion.user_id,
                'titulo': publicacion.titulo,
                'texto': publicacion.texto,
                'ambito': publicacion.ambito,
                'categoriaNombre': categoria.nombre if categoria else None,
                'categoria_id': categoria.id if categoria else None,
                'correo_electronico': publicacion.correo_electronico,
                'descripcion': publicacion.descripcion,
                'color_texto': publicacion.color_texto,
                'color_titulo': publicacion.color_titulo,
                'fecha_creacion': publicacion.fecha_creacion,
                'estado': publicacion.estado,
                'idioma': publicacion.idioma,               
                'imagenes': imagenes,
                'videos': videos,
                'layout': layout,
                'rating': round(random.uniform(3.0, 5.0), 1),
                'reviews': random.randint(1, 150),
                'descuento': descuento,
                'simbolo':simbolo,
                'precio': publicacion.precio,
                'afiliado_link': publicacion.afiliado_link,
                'precio_original': precio_original
            })

    return publicaciones_data






def extraer_precio_y_descripcion(publicacion_id,texto):
    SIMBOLOS = {
        "EUR": "€",
        "€": "€",
        "USD": "$",
        "$": "$",
        "ARS": "$",
        "GBP": "£",
        "£": "£",
        "COP": "$",
        "BRL": "R$",
        "MXN": "$",
        "AUD": "A$",
        "CAD": "C$"
    }
    patron = r"^(EUR|€|USD|\$|ARS|GBP|£|COP|BRL|MXN|AUD|CAD)[\s\u202f]*([\d]+(?:[.,]\d{1,2})?)\b(.*)$"

    #patron = r"^.*?(EUR|€|USD|\$|ARS|GBP|£|COP|BRL|MXN|AUD|CAD)[\s\u202f]*([\d]+(?:[.,]\d{1,2})?)[\s\u202f]*(.*)$"
    match = re.match(patron, texto.strip(), re.IGNORECASE)

    if match:
        raw_symbol = match.group(1) or "$"
        simbolo = SIMBOLOS.get(raw_symbol.upper(), "$")
        numero_str = match.group(2).replace(",", ".")
        descripcion = match.group(3).strip()

        try:
            numero = float(numero_str)
        except ValueError:
            return None, descripcion, None

        precio_actual = f"{simbolo} {numero:.2f}"
       
        return precio_actual, descripcion, numero

    return None, texto.strip(), None


def retorna_simbolo_desde_codigo_postal(session, codigo_postal,idioma):
    
    simbolos_por_moneda = {
        "USD": "$", "EUR": "€", "ARS": "$", "GBP": "£",
        "BRL": "R$", "MXN": "$", "AUD": "A$", "CAD": "C$", "PLN": "zł"
    }

    moneda_por_pais = {
        "Argentina": "ARS",
        "Italia": "EUR",
        "Polonia": "PLN",
        "Estados Unidos": "USD",
        "Reino Unido": "GBP",
        "Brasil": "BRL",
        "México": "MXN",
        "Canadá": "CAD"
        # Agregá más si necesitás
    }

    moneda_por_idioma = {
        "es": "ARS", "it": "EUR", "en": "USD", "pt": "BRL", "pl": "PLN"
    }

    
    entry = session.query(CodigoPostal).filter_by(codigoPostal=codigo_postal).first()

    pais = entry.pais if entry and entry.pais else None
    moneda = moneda_por_pais.get(pais)

    if not moneda and idioma:
        moneda = moneda_por_idioma.get(idioma)

    simbolo = simbolos_por_moneda.get(moneda, "$")
    return simbolo













def armar_publicacion_bucket(publicaciones):
    publicaciones_data = []
    with get_db_session() as session:
        for publicacion in publicaciones:
            # Obtener todas las imágenes y videos asociados a esta publicación
            imagenes_videos = session.query(Public_imagen_video).filter_by(publicacion_id=publicacion.id).all()

            imagenes = []
            videos = []

            for iv in imagenes_videos:
                # Obtener la información de las imágenes
                if iv.imagen_id:
                    try:
                        imagen = session.query(Image).filter_by(id=iv.imagen_id).first()
                        
                        if imagen:
                            # Generar la URL pública desde GCS
                            filepath = imagen.filepath
                            imagen_url = filepath.replace('static/uploads/', '').replace('static\\uploads\\', '')   
                            imagen_url = mostrar_from_gcs(imagen_url)
                            if imagen_url:                         
                                imagenes.append({
                                    'id': imagen.id,
                                    'title': imagen.title,
                                    'description': imagen.description,
                                    'filepath': imagen_url,  # Usar la URL de GCS
                                    'randomNumber': imagen.randomNumber,
                                    'size': imagen.size
                                })
                    except Exception as e:
                        logging.error(f"Error al obtener información de la imagen {iv.imagen_id}: {e}")

                # Obtener la información de los videos
                if iv.video_id:
                    try:
                        video = session.query(Video).filter_by(id=iv.video_id).first()
                        if video:
                            filepath = video.filepath
                            video_url = filepath.replace('static\\uploads\\', '').replace('static\\uploads\\', '')     # Asegúrate de que la barra final se mantenga si es necesario
                            video_url = mostrar_from_gcs(video_url)
                            if video_url:
                                videos.append({
                                    'id': video.id,
                                    'title': video.title,
                                    'description': video.description,
                                    'filepath': video_url,
                                    'size': video.size
                                })
                    except Exception as e:
                        logging.error(f"Error al obtener información del video {iv.video_id}: {e}")

            # Agregar la publicación con sus imágenes y videos al diccionario
            publicaciones_data.append({
                'publicacion_id': publicacion.id,
                'user_id': publicacion.user_id,
                'titulo': publicacion.titulo,
                'texto': publicacion.texto,
                'ambito': publicacion.ambito,
                'correo_electronico': publicacion.correo_electronico,
                'descripcion': publicacion.descripcion,
                'color_texto': publicacion.color_texto,
                'color_titulo': publicacion.color_titulo,
                'fecha_creacion': publicacion.fecha_creacion,
                'estado': publicacion.estado,
                'idioma':publicacion.idioma,
                'imagenes': imagenes,
                'videos': videos
            })

        return publicaciones_data









def armar_publicacion(publicaciones):
    publicaciones_data = []
    
    # Obtener la ruta completa de la carpeta 'static/uploads'
    uploads_folder = os.path.join(current_app.root_path, 'static', 'uploads')

    # Obtener todas las imágenes en la carpeta 'static/uploads'
    image_files = [file for file in os.listdir(uploads_folder) if file.endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    # Crear las rutas completas de las imágenes sin codificación de caracteres
    image_paths = [os.path.join('uploads', filename).replace(os.sep, '/') for filename in image_files]
    with get_db_session() as session:
        for publicacion in publicaciones:
            # Obtener todas las imágenes y videos asociados a esta publicación
            imagenes_videos = session.query(Public_imagen_video).filter_by(publicacion_id=publicacion.id).all()
            
            imagenes = []
            videos = []

            for iv in imagenes_videos:
                # Obtener la información de las imágenes
                if iv.imagen_id:
                    imagen = session.query(Image).filter_by(id=iv.imagen_id).first()
                    if imagen:
                        imagenes.append({
                            'id': imagen.id,
                            'title': imagen.title,
                            'description': imagen.description,
                            'filepath': imagen.filepath,
                            'randomNumber': imagen.randomNumber,  
                            'size': imagen.size                      
                        })

                # Obtener la información de los videos
                if iv.video_id:
                    video = session.query(Video).filter_by(id=iv.video_id).first()
                    if video:
                        videos.append({
                            'id': video.id,
                            'title': video.title,
                            'description': video.description,
                            'filepath': video.filepath,
                            'size': video.size
                        })

            # Ajustar las rutas de archivos según el sistema operativo
            path_separator = '/'
            for imagen in imagenes:
                imagen['filepath'] = imagen['filepath'].replace('\\', path_separator)
            
            for video in videos:
                video['filepath'] = video['filepath'].replace('\\', path_separator)

            # Agregar la publicación con sus imágenes y videos al diccionario
            publicaciones_data.append({
                'publicacion_id': publicacion.id,
                'user_id': publicacion.user_id,
                'titulo': publicacion.titulo,
                'texto': publicacion.texto,
                'ambito': publicacion.ambito,
                'correo_electronico': publicacion.correo_electronico,
                'descripcion': publicacion.descripcion,
                'color_texto': publicacion.color_texto,
                'color_titulo': publicacion.color_titulo,
                'fecha_creacion': publicacion.fecha_creacion, 
                'estado': publicacion.estado,
                'afiliado_link': publicacion.afiliado_link,      
                'idioma':publicacion.idioma,       
                'imagenes': imagenes,
                'videos': videos
            })

        return publicaciones_data

@publicaciones.route('/media-publicaciones-cambiar-estado', methods=['POST'])
def media_publicaciones_cambiar_estado():
    data = request.form
    publicacion_id = data.get('id')
    nuevo_estado = data.get('nuevoEstado')
    
    # Validar los datos
    if not publicacion_id or not nuevo_estado:
        return jsonify({'error': 'Faltan parámetros'}), 400
    with get_db_session() as session:
        # Buscar la publicación en la base de datos
        publicacion = session.query(Publicacion).filter_by(id=publicacion_id).first()    
        if not publicacion:
            return jsonify({'error': 'Publicación no encontrada'}), 404
        
        # Refrescar para asegurar que la instancia esté actualizada
        session.refresh(publicacion)
        
        # Actualizar el estado de la publicación
        publicacion.estado = nuevo_estado
        try:
            session.commit()
        except StaleDataError:
          
            return jsonify({'error': 'No se pudo actualizar el estado, verifique si los datos cambiaron'}), 409
       
    
    return jsonify({'success': True, 'nuevoEstado': nuevo_estado}), 200




        

def cargarImagen_crearPublicacion(app, request, filename, id_publicacion, color_texto, titulo_publicacion=None, mimetype=None, userid=0, index=None, size=0):
    size = size
    # Guardar información en la base de datos   
   
    nombre_archivo = filename
    descriptionImagen = titulo_publicacion
    randomNumber_ = random.randint(1, 1000000)  # Número aleatorio
    
    try:
        with get_db_session() as session:
            imagen_existente = session.query(Image).filter_by(title=filename).first()
            if imagen_existente:
                cargar_id_publicacion_id_imagen_video(id_publicacion, imagen_existente.id, 0, 'imagen', size=size)
                return filename
            else:
                nueva_imagen = Image(
                    user_id=userid,
                    title=nombre_archivo,
                    description=descriptionImagen,
                    colorDescription=color_texto,
                    filepath=filename,
                    randomNumber=randomNumber_,
                    size=float(size),
                    mimetype=mimetype
                )
                session.add(nueva_imagen)
                session.commit()
                
                cargar_id_publicacion_id_imagen_video(id_publicacion, nueva_imagen.id, 0, 'imagen', size=size)
                return filename
    except Exception as db_error:
        app.logger.error(f"Error al interactuar con la base de datos: {db_error}")
     

        raise  # Propagar el error para que pueda ser manejado por capas superiores
      


def cargarVideo_crearPublicacion(app, request, filename, id_publicacion, color_texto, titulo_publicacion=None, mimetype=None, userid=0, index=None, size=0):
    print(f"Entering cargarVideo_crearPublicacion with filename: {filename}, userid: {userid}, index: {index}, size: {size}")
   # Guardar información en la base de datos
   
    nombre_archivo = filename
    descriptionVideo = titulo_publicacion
    randomNumber_ = random.randint(1, 1000000)  # Número aleatorio
    
    try:
        with get_db_session() as session:
            video_existente = session.query(Video).filter_by(title=filename,size=size).first()

            if video_existente:
                print("Video already exists, saving relation to publicacion_media")
                # Si la imagen ya existe, solo guarda la relación en publicacion_media
                
                cargar_id_publicacion_id_imagen_video(id_publicacion,0,video_existente.id,'video',size=size)
                return filename
            else:
                print("Creating new video")
                nuevo_video = Video(
                    user_id=userid,
                    title=nombre_archivo,
                    description=descriptionVideo,
                    colorDescription=color_texto,
                    filepath=filename,
                    randomNumber=randomNumber_,
                    size=float(size),
                    mimetype=mimetype
                )
                session.add(nuevo_video)
                session.commit()
                print("Saving relation to publicacion_media")
                cargar_id_publicacion_id_imagen_video(id_publicacion,0,nuevo_video.id,'video',size=size)
            return filename
    except Exception as db_error:
        app.logger.error(f"Error al interactuar con la base de datos: {db_error}")
      

        raise  # Propagar el error para que pueda ser manejado por capas superiores



def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def es_formato_imagen(filepath):
    # Extensiones de archivo de imagen comunes
    extensiones_imagen = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

    # Verificar si la extensión del archivo está en la lista de extensiones de imagen
    return any(filepath.lower().endswith(ext) for ext in extensiones_imagen)




def _parse_bool(value) -> bool:
    if value is None:
        return False
    return str(value).strip().lower() in {"1","true","on","sí","si","yes"}

def _parse_precio(value: str) -> float:
    if not value:
        return 0.0
    s = value.strip()
    # quita separadores de miles comunes y normaliza decimal
    s = s.replace(" ", "").replace(".", "").replace(",", ".")
    # solo deja número con decimal opcional y signo
    if not re.fullmatch(r"-?\d+(\.\d+)?", s):
        raise ValueError(f"Precio inválido: {value!r}")
    return float(s)

def guardarPublicacion(user_id):
    form = request.form
    try:
        post_title       = form.get('postTitle_creaPublicacion', '').strip()
        post_text        = form.get('postText_creaPublicacion', '')   
        post_descripcion = form.get('postDescription_creaPublicacion', '')
        ambito           = form.get('postAmbito_creaPublicacion', '')
        correo_electronico = form.get('correo_electronico')
        color_texto      = form.get('color_texto')
        color_titulo     = form.get('color_titulo')
        estado           = form.get('postEstado_creaPublicacion') or 'ACTIVO'
        botonCompra      = _parse_bool(form.get('postBotonCompra_creaPublicacion'))
        codigoPostal     = request.cookies.get('codigoPostal')
        moneda           = form.get('moneda_agregaPublicacion') or ''
        precio_raw       = form.get('precio_creaPublicacion')

        if not post_title:
            raise ValueError("El título es obligatorio.")

        if moneda and moneda not in MONEDAS_PERMITIDAS:
            raise ValueError(f"Moneda no permitida: {moneda}")

        precio = _parse_precio(precio_raw)

        with get_db_session() as session:
            # Doble defensa: chequear duplicado por (titulo, user_id)
            existente = session.query(Publicacion)\
                               .filter_by(titulo=post_title, user_id=user_id)\
                               .first()
            if existente:
                # sugerencia: lanzar una excepción específica y que la capa de ruta maneje el 409
                raise ValueError("Ya existe una publicación con ese título para este usuario.")

            nueva = Publicacion(
                user_id=user_id,
                titulo=post_title,
                texto=post_text,
                ambito=ambito,
                correo_electronico=correo_electronico,
                descripcion=post_descripcion,
                color_texto=color_texto,
                color_titulo=color_titulo,
                fecha_creacion=datetime.utcnow(),
                estado=estado,
                codigoPostal=codigoPostal,
                botonCompra=botonCompra,
                precio=precio,
                moneda=moneda or None,
            )
            session.add(nueva)
            session.commit()
            return nueva.id

            
    except Exception as e:
         raise
   

def cargar_id_publicacion_id_imagen_video(id_publicacion,nueva_imagen_id,nuevo_video_id,media_type,size=0):
    with get_db_session() as session:
        nuevo_ids= Public_imagen_video(
            publicacion_id=id_publicacion,
            imagen_id=nueva_imagen_id,
            video_id=nuevo_video_id,
            fecha_creacion=datetime.now(),
            media_type=media_type,
            size=float(size)
        )
        session.add(nuevo_ids)
        session.commit()
    
        return True

def show_publicacion_galeriaimagenes(request, media_files,id_publicacion):
     return render_template('publicaciones/publicacionesGaleriaImagenes.html', media_files=media_files,id_publicacion=id_publicacion)
     

@publicaciones.route('/social_imagenes_eliminar_publicacion/', methods=['POST'])
def social_imagenes_eliminar_publicacion():
    # Obtener el encabezado Authorization
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return jsonify({'error': 'Token de acceso no proporcionado'}), 401

    # Verificar formato del encabezado Authorization
    parts = authorization_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return jsonify({'error': 'Formato de token de acceso no válido'}), 401

    # Obtener el token de acceso
    access_token = parts[1]

    # Validar y decodificar el token
    if Token.validar_expiracion_token(access_token=access_token):
        app = current_app._get_current_object()
        decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded_token.get("sub")
        
        # Obtener el ID de la publicación a eliminar
        publicacion_id = request.form.get('publicacion_id')
        correo_electronico = request.form.get('correo_electronico')

        # Aquí deberías añadir la lógica para eliminar la publicación, imágenes y videos
        try:
            # Ejemplo de eliminación (ajustar según tu implementación)
            with app.app_context():
                with get_db_session() as session:
                    eliminar_relacion_categorias_publicaciones(publicacion_id)
                    eliminar_publicacion_y_medios(publicacion_id, user_id)
                  
            return jsonify({'success': True}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Token de acceso no válido o expirado'}), 401

def eliminar_relacion_categorias_publicaciones(publicacion_id):
    try:
        publicacion_id = int(publicacion_id)
        with get_db_session() as session:
            # Eliminar la relación entre la publicación y las categorías
            session.query(CategoriaPublicacion).filter_by(publicacion_id=publicacion_id).delete()
            session.commit()
            return True
    except Exception as e:
        print(str(e))
     
        return False

def eliminar_publicacion_y_medios(publicacion_id, user_id):
    try:
        with get_db_session() as session:
            publicacion = session.query(Publicacion).filter_by(id=publicacion_id, user_id=user_id).first()
            if publicacion:
                publicacion_id = int(publicacion_id)
                usuario_publicacion_ubicacion = session.query(UsuarioPublicacionUbicacion).filter_by(id_publicacion=publicacion_id).first()
                if usuario_publicacion_ubicacion:
                    session.delete(usuario_publicacion_ubicacion)  
                # Obtener los registros de medios relacionados en la tabla intermedia
                publicacion_imagen_video = session.query(Public_imagen_video).filter_by(publicacion_id=publicacion_id).all()
                
                # Eliminar la publicación
                session.delete(publicacion)          
            
                for p in publicacion_imagen_video:
                    # Verificar si la imagen está asociada a más de una publicación
                    imagen_en_multiples_publicaciones = (
                        session.query(func.count(Public_imagen_video.publicacion_id))
                        .filter_by(imagen_id=p.imagen_id)
                        .scalar() > 1
                    )
                    if not imagen_en_multiples_publicaciones:
                        # Eliminar la imagen asociada, si no está en otras publicaciones
                        imagen = session.query(Image).filter_by(id=p.imagen_id, user_id=user_id).first()
                        if imagen:
                            session.delete(imagen)
                        #  eliminar_desde_archivo(imagen.title, user_id)
                            delete_from_gcs(imagen.title)
                    
                    # Verificar si el video está asociado a más de una publicación
                    video_en_multiples_publicaciones = (
                        session.query(func.count(Public_imagen_video.publicacion_id))
                        .filter_by(video_id=p.video_id)
                        .scalar() > 1
                    )
                    if not video_en_multiples_publicaciones:
                        # Eliminar el video asociado, si no está en otras publicaciones
                        video = session.query(Video).filter_by(id=p.video_id, user_id=user_id).first()
                        if video:
                            session.delete(video)
                            #eliminar_desde_archivo(video.title, user_id)
                            delete_from_gcs(video.title)
                        
                    # Eliminar el registro de la tabla intermedia
                    session.delete(p)
                
                # Commit de todas las eliminaciones en una sola transacción
                session.commit()
                
                return True

    except Exception as e:
    
        print(f"Error al eliminar la publicación y medios: {e}")
        return False


def  eliminar_desde_archivo(title,user_id):
    try:
        # Reemplazar barras diagonales hacia adelante ("/") por barras diagonales hacia atrás ("\")
        
        #ruta_base_datos = title.replace('/', '\\')
        file_path = os.path.join('static', 'uploads', title)
      
        #file_path = file_path.replace('\\', '/')
        # Agregar "static" al inicio de la ruta
        #ruta_base_datos = os.path.normpath('static\\' + file_path)
        ruta_ = os.path.join(file_path)
        ruta_ = ruta_.replace('\\', '/')
        absolute_file_path = os.path.abspath(ruta_)  # Obtener la ruta absoluta 
        os.remove(absolute_file_path)
        return True
    except OSError as e:
        print(f"Error al eliminar el archivo: {e}")
        return False

@publicaciones.route('/social_media_publicaciones_borrado_logico_publicaciones/', methods=['POST'])
def social_media_publicaciones_borrado_logico_publicaciones(): 
    try:
        # Obtener el encabezado Authorization
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            return jsonify({'error': 'Token de acceso no proporcionado'}), 401
        
        # Verificar formato del encabezado Authorization
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato de token de acceso no válido'}), 401
        
        # Obtener el token de acceso
        access_token = parts[1]

        # Validar y decodificar el token
        if Token.validar_expiracion_token(access_token=access_token):  # Asegúrate de que este método acepte el token directamente
            app = current_app._get_current_object()
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = decoded_token.get("sub")

            # Obtener el ID de la publicación del cuerpo de la solicitud
            data = request.form
            publicacion_id = data.get('id')
            estado = data.get('estado')
            
            if not publicacion_id:
                return jsonify({'error': 'ID de publicación no proporcionado'}), 400
            
            # Llamar a la función para el borrado lógico
            borrado_logicopublicacion(int(publicacion_id), user_id,estado)

            return jsonify({'success': True}), 200

        return jsonify({'error': 'Token de acceso expirado o no válido'}), 401
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def borrado_logicopublicacion(publicacion_id, user_id, estado):
    try:
        # Inicializa una lista vacía para almacenar las publicaciones
        publicaciones = []
        with get_db_session() as session:
            # Obtén todos los estados de la publicación con el publicacion_id y user_id dados
            publicacion_estados = session.query(Estado_publi_usu).filter_by(publicacion_id=publicacion_id, user_id=user_id).all()

            nuevo_estado = Estado_publi_usu(
                publicacion_id=publicacion_id,
                user_id=user_id,
                estado=estado,
                visto=False,  # Puedes cambiar esto según tus necesidades
                gusto='',  # Puedes cambiar esto según tus necesidades
                tiempo_visto='',  # Puedes cambiar esto según tus necesidades
                fecha_visto=datetime.now(),  # Puedes cambiar esto según tus necesidades
                fecha_eliminado=datetime.now(),  # Puedes cambiar esto según tus necesidades
                fecha_gustado=datetime.now()  # Puedes cambiar esto según tus necesidades
            )
            
            # Agregar el nuevo estado a la base de datos
            session.add(nuevo_estado)
            session.commit()
            
            publicaciones.append(nuevo_estado)  
                        
            return True
        
    except Exception as e:
       
        print(f"Error: {e}")
        return False
   


@publicaciones.route('/social_media_publicaciones_modificar_publicaciones/', methods=['POST'])
def publicaciones_modificar_publicaciones():
    # --- Auth: Bearer token ---
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return jsonify({'error': 'Token de acceso no proporcionado'}), 401
    parts = authorization_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return jsonify({'error': 'Formato de token no válido'}), 401
    access_token = parts[1]

    try:
        if not Token.validar_expiracion_token(access_token=access_token):
            return jsonify({'error': 'Token de acceso expirado o inválido'}), 401
        decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded_token.get("sub")
        if not user_id:
            return jsonify({'error': 'Token sin sujeto (sub) válido'}), 401
    except Exception:
        return jsonify({'error': 'No se pudo validar el token'}), 401

    # --- Datos del form ---
    form = request.form
    post_id        = form.get('postId_modificaPublicacion')
    titulo         = form.get('postTitle_modificaPublicacion')
    texto          = form.get('postText_modificaPublicacion')
    descripcion    = form.get('postDescription_modificaPublicacion')
    estado         = form.get('postEstado_modificaPublicacion')
    ambito         = form.get('postAmbito_modificaPublicacion')
    categoria      = form.get('postAmbitoCategorias_modificaPublicacion')
    idioma         = form.get('postCambiarIdioma_modificaPublicacion')
    botonCompra    = form.get('postBotonCompra_modificaPublicacion')
    codigoPostal   = form.get('codigoPostal_modificaPublicacion')
    botonPagoOnline= form.get('postPagoOnline_modificaPublicacion')
    afiliado_link  = form.get('afiliado_link_modificaPublicacion')
    precio_raw     = form.get('precio_modificaPublicacion')
    moneda         = form.get('moneda_modificaPublicacion')

    # archivos = request.files.getlist('mediaFile_modificaPublicacion')  # si los usás, procesalos luego

    # Validaciones rápidas
    if not post_id:
        return jsonify({'error': 'Falta postId'}), 400
    try:
        post_id_int = int(post_id)
    except ValueError:
        return jsonify({'error': 'postId inválido'}), 400

    if moneda and moneda not in MONEDAS_PERMITIDAS:
        return jsonify({'error': f"Moneda no permitida: {moneda}"}), 400

    try:
        precio = _parse_precio(precio_raw)
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400

    # Sanitizar texto (quita etiquetas HTML básicas)
    texto_limpio = re.sub(r'<[^>]*>', '', texto) if texto else ''

    # --- DB ---
    try:
        with get_db_session() as session:
            publicacion = session.query(Publicacion).filter_by(id=post_id_int, user_id=user_id).first()
            if not publicacion:
                return jsonify({'error': 'Publicación no encontrada o no autorizada'}), 404

            # Si usás tabla puente CategoriaPublicacion, mantenla; si NO, borra el bloque y usa solo publicacion.categoria_id
            if categoria:
                try:
                    categoria_id_int = int(categoria)
                except ValueError:
                    return jsonify({'error': 'categoria inválida'}), 400

                categoriPublicacion = session.query(CategoriaPublicacion).filter(
                    CategoriaPublicacion.id == categoria_id_int,
                    CategoriaPublicacion.publicacion_id == publicacion.id
                ).first()

                if not categoriPublicacion:
                    new_categoriPublicacion = CategoriaPublicacion(
                        publicacion_id=publicacion.id,
                        categoria_id=categoria_id_int,
                        estado='activo'
                    )
                    session.add(new_categoriPublicacion)
                else:
                    categoriPublicacion.categoria_id = categoria_id_int

                # Si además guardás FK directa en Publicacion, coherencia:
                publicacion.categoria_id = categoria_id_int

            publicacion.titulo             = titulo or publicacion.titulo
            publicacion.texto              = texto_limpio
            publicacion.descripcion        = descripcion
            publicacion.estado             = estado or publicacion.estado
            publicacion.ambito             = ambito
            publicacion.idioma             = idioma or publicacion.idioma
            publicacion.codigoPostal       = codigoPostal
            publicacion.afiliado_link      = afiliado_link
            publicacion.fecha_modificacion = datetime.utcnow()
            publicacion.botonCompra        = _parse_bool(botonCompra)
            publicacion.pagoOnline         = _parse_bool(botonPagoOnline)
            publicacion.precio             = precio
            publicacion.moneda             = moneda or None

            session.commit()

        return jsonify({"mensaje": "Publicación modificada con éxito!"})

    except Exception as e:
        # el rollback dentro del with ya se manejó; acá solo informamos
        print(str(e))
        return jsonify({'error': 'Ocurrió un error al modificar la publicación.'}), 500

            
   
@publicaciones.route('/social_imagenes_eliminar_Imagenes_Publicaciones', methods=['POST'])
def social_imagenes_eliminar_Imagenes_Publicaciones():
    try:
        # Obtener el encabezado Authorization
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            return jsonify({'error': 'Token de acceso no proporcionado'}), 401
        
        # Verificar formato del encabezado Authorization
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato de token de acceso no válido'}), 401
        
        # Obtener el token de acceso
        access_token = parts[1]

        # Validar y decodificar el token
        if Token.validar_expiracion_token(access_token=access_token):  # Asegúrate de que este método acepte el token directamente
            app = current_app._get_current_object()
            decoded_token = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = decoded_token.get("sub")

            # Obtener el ID de la publicación del cuerpo de la solicitud
            data = request.form
            publicacion_id = data.get('publicacion_id')
            
            if not publicacion_id:
                return jsonify({'error': 'ID de publicación no proporcionado'}), 400
            
            eliminar_desde_db_imagen_video(data, user_id)

            return jsonify({'success': True}), 200

        return jsonify({'error': 'Token de acceso expirado o no válido'}), 401
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
def eliminar_desde_db_imagen_video(data, user_id):
    try:
        publicacion_id = data.get('publicacion_id')
        id_imagen = data.get('id_imagen')

        if not publicacion_id or not id_imagen:
            raise ValueError("publicacion_id o id_imagen no proporcionados.")

        publicacion_id = int(publicacion_id)
        multimedia_id = int(id_imagen) if str(id_imagen).isdigit() else id_imagen
        with get_db_session() as session:
            # Buscar imagen o video
            multimedia = (
                session.query(Image).filter_by(id=multimedia_id, user_id=user_id).first()
                or session.query(Video).filter_by(id=multimedia_id, user_id=user_id).first()
            )

            if not multimedia:
                raise ValueError(f"Multimedia con ID {multimedia_id} no encontrado.")

            # Obtener los registros de la tabla intermedia
            publicacion_imagen_video = session.query(Public_imagen_video).filter_by(
                publicacion_id=publicacion_id, imagen_id=multimedia_id
            ).all()

            if len(publicacion_imagen_video) < 2:
                # Eliminar el registro multimedia si no está asociado a otras publicaciones
                session.delete(multimedia)
                delete_from_gcs(multimedia.title)

            # Eliminar los registros de la tabla intermedia
            for item in publicacion_imagen_video:
                session.delete(item)

            session.commit()
            return True

    except Exception as e:
       
        # Log del error para depuración
        print(f"Error eliminando multimedia: {e}")
        raise e
