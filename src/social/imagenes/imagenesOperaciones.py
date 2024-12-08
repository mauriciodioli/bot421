import os
from flask import Flask,jsonify, request, render_template,redirect, Blueprint,current_app, url_for,flash
from utils.db import db

from models.modelMedia.image import Image
from models.modelMedia.video import Video
import tokens.token as Token

from models.publicaciones.publicaciones import Publicacion
from models.publicaciones.publicacion_imagen_video import Public_imagen_video
from models.usuario import Usuario
from social.buckets.bucketGoog import upload_to_gcs
from social.buckets.bucketGoog import (
    upload_to_gcs, delete_from_gcs, mostrar_from_gcs
)


import logging
import jwt
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
import sys

# Configuración del Blueprint para el registro de usuarios
imagenesOperaciones = Blueprint("imagenesOperaciones", __name__)



@imagenesOperaciones.route('/subirImagen/', methods=['POST'])
def subirImagen():
    # Obtener el valor de 'layout' del parámetro de la URL
    layout = request.args.get('layout')
    publicacion_id = request.form.get('publicacion_id')
    
    # Pasar el valor de 'layout' al template
    return render_template("media/principalMedia/subirImage.html", publicacion_id=publicacion_id, layout=layout)

@imagenesOperaciones.route('/subirVideo/')
def subirVideo():
      # Obtener el valor de 'layout' del parámetro de la URL
    layout = request.files('layout', default='layout', type=str)
    publicacion_id = request.files('publicacion_id', default='publicacion_id', type=str)
    return render_template("media/principalMedia/subirVideo.html", publicacion_id=publicacion_id ,layout=layout)

@imagenesOperaciones.route('/mostrarGaleria/')
def mostrarGaleria():
    return render_template("media/principalMedia/mostrarGaleria.html", layout = 'layout')

@imagenesOperaciones.route('/cargarVideo', methods=['POST'])
def cargarVideo():
    #try:
        # Verificar si el campo 'selectedColor' está en la solicitud
        if 'selectedColor' not in request.form:
            return jsonify({'error': 'No se proporcionó el campo de selectedColor'}), 400

        selectedColor = request.form['selectedColor']

        # Verificar si el campo 'video' está en la solicitud
        if 'video' not in request.files:
            return jsonify({'error': 'No se proporcionó el campo de video'}), 400

        video = request.files['video']

        # Verificar si los campos necesarios están presentes en la solicitud
        required_fields = ['nombreArchivo', 'descriptionVideo', 'randomNumber']
        for field in required_fields:
            if field not in request.form:
                return jsonify({'error': f'No se proporcionó el campo de {field}'}), 400

        nombre_archivo = request.form['nombreArchivo']
        description_video = request.form['descriptionVideo']
        random_number = int(request.form['randomNumber'])
  # Verificar si el token de acceso está presente en el encabezado 'Authorization'
        if 'Authorization' not in request.headers:
            return jsonify({'error': 'Token de acceso no proporcionado'}), 401

        authorization_header = request.headers['Authorization']
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato de token de acceso no válido'}), 401

        access_token = parts[1]
        

        # Guardar el video en la carpeta src/static/uploads
        new_path = os.path.join('static', 'uploads', video.filename)
        video.save(new_path)
        upload_to_gcs(new_path, video.filename)
        if access_token:
            app = current_app._get_current_object()                    
            userid = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
          

        # Crear una nueva instancia de la clase Image y agregarla a la base de datos
        nueva_imagen = Image(
            user_id=userid,
            title=nombre_archivo,
            description=description_video,
            colorDescription=selectedColor,
            filepath=new_path,
            randomNumber=random_number,
            size=0
        )

        db.session.add(nueva_imagen)
        db.session.commit()
        db.session.close()

        # Realizar alguna acción adicional si es necesario, como mostrar las imágenes
     

        return jsonify({'mensaje': 'Video cargado con éxito', 'nombreArchivo': nombre_archivo})

    #except Exception as e:
       # return jsonify({'error': str(e)}), 500
    
    
@imagenesOperaciones.route('/cargarImagen', methods=['POST'])
def cargarImagen():
  try:
      
        if 'selectedColor' not in request.form:
            return jsonify({'error': 'No se proporcionó el campo de selectedColor'}), 400

        selectedColor = request.form['selectedColor']
        # Verificar si el campo 'imagen' está en la solicitud
        if 'imagen' not in request.files:
            return jsonify({'error': 'No se proporcionó el campo de imagen'}), 400

        imagen = request.files['imagen']

        # Verificar si el campo 'nombreArchivo' está en la solicitud
        if 'nombreArchivo' not in request.form:
            return jsonify({'error': 'No se proporcionó el campo de nombreArchivo'}), 400

        nombre_archivo = request.form['nombreArchivo']
        
        if 'descriptionImagen' not in request.form:
            return jsonify({'error': 'No se proporcionó el campo de descriptionImagen'}), 400

        descriptionImagen = request.form['descriptionImagen']
        
        randomNumber_ = request.form['randomNumber']
        numeroAleatoreo = int(randomNumber_)
        # Verificar si el token de acceso está presente en el encabezado 'Authorization'
        if 'Authorization' not in request.headers:
            return jsonify({'error': 'Token de acceso no proporcionado'}), 401

        authorization_header = request.headers['Authorization']
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato de token de acceso no válido'}), 401

        access_token = parts[1]
       
        # Guardar la imagen en la carpeta src/static/uploads
      
        new_path = os.path.join( 'static', 'uploads', imagen.filename)
       # Guardar la imagen en la carpeta src/static/uploads
       # print(f"Ruta completa del archivo: {new_path}")
        imagen.save(new_path)
        upload_to_gcs(new_path, imagen.filename)
        # Resto de tu lógica para manejar la imagen, el nombre del archivo y el access_token
        # Aquí puedes acceder a 'imagen' (objeto FileStorage), 'nombre_archivo' y 'access_token'
        #aqui carga la los datos en la base de datos
        if access_token:
            app = current_app._get_current_object()                    
            userid = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            nueva_imagen = Image(
                user_id=userid,
                title=nombre_archivo,
                description=descriptionImagen,
                colorDescription=selectedColor,
                filepath=new_path,
                randomNumber=numeroAleatoreo,
                size=0
            )
            db.session.add(nueva_imagen)
            db.session.commit()
            db.session.close()
          
       # MostrarImages()
        return jsonify({'mensaje': 'Imagen cargada con éxito', 'nombreArchivo': nombre_archivo})
  except Exception as e:
        return jsonify({'error': str(e)}), 500

@imagenesOperaciones.route('/MostrarImages/', methods=['POST'])
def mostrar_imagenes():
    access_token = request.form.get('access_token')
     
   # Obtener la ruta completa de la carpeta 'static/uploads'
    uploads_folder = os.path.join(current_app.root_path, 'static', 'uploads')

    # Obtener todas las imágenes en la carpeta 'static/uploads'
    image_files = [file for file in os.listdir(uploads_folder) if file.endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    # Crear las rutas completas de las imágenes sin codificación de caracteres
    image_paths = [os.path.join('uploads', filename).replace(os.sep, '/') for filename in image_files]
   
    
    if access_token:
        app = current_app._get_current_object()                    
        try:
            userid = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.DecodeError) as e:
            # Manejar errores específicos de JWT
            flash("Error en el token JWT", "error")
            return render_template("notificaciones/noPoseeDatos.html")
            
        except Exception as e:
            # Manejar otras excepciones
            flash("Error desconocido", "error")
            return redirect(url_for('autenticacion.index')) # Puedes redirigir a la página principal o manejar de otra manera


            
       
        # Obtener todas las imágenes cuyas rutas coincidan con las rutas en db_image_paths
        with db.session.begin(subtransactions=True):            
            try:
                usuarios = db.session.query(Usuario).all()
                imagenes = db.session.query(Image).all()
               
            except Exception as e:
                # Manejar excepciones de la base de datos
                flash("Error en la base de datos", "error")
                return redirect(url_for('index'))  # Puedes redirigir a la página principal o manejar de otra manera
            finally:
                db.session.close()
           
      #  usuarios = Usuario.query.all()
      #  imagenes = Image.query.all()
        
        
       # Filtrar solo las imágenes (puedes ajustar esto según tus necesidades)
        imagenes_filtradas = [img for img in imagenes if es_formato_imagen(img.filepath)]
       # path_separator = '/' if os.name != 'nt' else '\\'
        path_separator = '/'
        # Procesar y asignar los paths solo a las imágenes filtradas
        for img in imagenes_filtradas:
            original_filepath = img.filepath
            # Reemplazar los separadores de ruta para que sean consistentes
            image_paths = original_filepath.replace('\\', path_separator)
            
            # Reemplazar 'static/' o 'static\\' con una cadena vacía
            img.image_paths = image_paths.replace('static/', '')
          
            print(f"Original: {original_filepath}, Modificado: { img.image_paths}")
            sys.stdout.flush()
            
            # Buscar el usuario correspondiente
            usuario_correspondiente = next((usuario for usuario in usuarios if usuario.id == img.user_id), None)
            
            # Agregar el correo electrónico del usuario a la imagen
            if usuario_correspondiente:
                img.correo_electronico = usuario_correspondiente.correo_electronico
            else:
                # Manejar el caso en el que no se encuentra el usuario
                img.correo_electronico = "Usuario no encontrado"
                
      
    return render_template('media/principalMedia/images.html', imagenes=imagenes_filtradas)
    
  

@imagenesOperaciones.route('/imagenesImagenesOperaciones-mostrar-Galeria', methods = ['POST'])
def imagenesImagenesOperaciones_mostrar_Galeria():
    access_token = request.form.get('access_token')
    # Hacer algo con access_token
   
    # Obtener las imágenes desde la base de datos
    #images = Image.query.all()
     # Obtener las rutas completas de las imágenes
    #image_paths = [os.path.join('static', 'uploads', image.filename) for image in images]
    
   # Obtener la ruta completa de la carpeta 'static/uploads'
    uploads_folder = os.path.join(current_app.root_path, 'static', 'uploads')

    # Obtener todas las imágenes en la carpeta 'static/uploads'
    image_files = [file for file in os.listdir(uploads_folder) if file.endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    # Crear las rutas completas de las imágenes sin codificación de caracteres
    image_paths = [os.path.join('uploads', filename).replace(os.sep, '/') for filename in image_files]
   
    # Transformar las rutas al formato almacenado en la base de datos
   # db_image_paths = [os.path.relpath(os.path.join(current_app.root_path, path), current_app.root_path).replace('/', os.sep) for path in image_paths]

   
    if access_token:
        app = current_app._get_current_object()                    
        userid = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']
            
       
        # Obtener todas las imágenes cuyas rutas coincidan con las rutas en db_image_paths
        imagenes = Image.query.filter(Image.user_id == userid).all()
        
       # Filtrar solo las imágenes (puedes ajustar esto según tus necesidades)
        imagenes_filtradas = [img for img in imagenes if es_formato_imagen(img.filepath)]

        # Procesar y asignar los paths solo a las imágenes filtradas
        for img in imagenes_filtradas:
            img.image_paths = img.filepath.replace('static\\', '').replace('\\', '/')

        #          img.image_paths = [img.filepath.replace('static\\', '').replace('\\', '/') for img in imagenes if es_formato_imagen(img.filepath)]
        
          
      
    return render_template('media/principalMedia/mostrarGaleria.html', imagenes=imagenes_filtradas)

@imagenesOperaciones.route('/eliminarImagen', methods=['POST'])
def eliminar_imagen():
    data = request.form  # Puedes ajustar esto según la forma en que envíes los datos desde tu cliente
    randomNumber = data.get('randomNumber')
    imageName = data.get('imageName')
    authorization_header = request.headers.get('Authorization')

    if authorization_header and authorization_header.startswith('Bearer '):
        # Extraer el token de acceso de la cadena del encabezado
        access_token = authorization_header[len('Bearer '):]
        app = current_app._get_current_object()
        userid = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']

        try:
            
            # Reemplazar barras diagonales hacia adelante ("/") por barras diagonales hacia atrás ("\")
            ruta_base_datos = imageName.replace('/', '\\')

            # Agregar "static" al inicio de la ruta
            ruta_base_datos = os.path.normpath('static\\' + ruta_base_datos)
            # Obtener la imagen correspondiente al nombre de la imagen y al ID del usuario
            imagen = Image.query.filter_by(user_id=userid, filepath=ruta_base_datos).first()

            if imagen:
                # Eliminar la imagen de la base de datos
                db.session.delete(imagen)
                db.session.commit()
                db.session.close()
                ruta_imagen = os.path.join(ruta_base_datos)
                os.remove(ruta_imagen)
                return jsonify({'message': 'Imagen eliminada con éxito'}), 200
            else:
                return jsonify({'error': 'Imagen no encontrada'}), 404
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': 'Error al eliminar la imagen'}), 500
    else:
        return jsonify({'error': 'Token de autorización no válido'}), 401
    
def es_formato_imagen(filepath):
    # Extensiones de archivo de imagen comunes
    extensiones_imagen = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

    # Verificar si la extensión del archivo está en la lista de extensiones de imagen
    return any(filepath.lower().endswith(ext) for ext in extensiones_imagen)



@imagenesOperaciones.route('/imagenesOperaciones-cargar-imagen-video-bucket', methods=['POST'])
def imagenesOperaciones_cargar_imagen_video_bucket():
    if request.method == 'POST':
        try:
            # Obtener el id de publicación y el encabezado Authorization
            id_publicacion = request.form.get('id_publicacion')  # Cambiado a request.form
            layout = request.form.get('layout', 'default')
            authorization_header = request.headers.get('Authorization')
            
            if not authorization_header:
                return jsonify({'error': 'Token de acceso no proporcionado'}), 401

            # Verificar formato del encabezado Authorization
            parts = authorization_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return jsonify({'error': 'Formato de token de acceso no válido'}), 401

            # Validar y decodificar el token
            access_token = parts[1]
            if Token.validar_expiracion_token(access_token=access_token):  
                app = current_app._get_current_object()
                decoded_token = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
                user_id = decoded_token.get("sub")

                # Buscar la publicación específica
                publicacion = db.session.query(Publicacion).filter_by(id=id_publicacion).first()
                if not publicacion:
                    return jsonify({'error': 'Publicación no encontrada'}), 404

                # Generar los datos de la publicación
                publicacion_data = armar_publicacion_bucket_para_modal(publicacion, layout)

                db.session.close()
                return jsonify(publicacion_data)

        except Exception as e:
            current_app.logger.error(f"Error: {e}")  # Registro de errores
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'No se pudo procesar la solicitud'}), 500


def armar_publicacion_bucket_para_modal(publicacion, layout):
    publicaciones_data = []

    # Obtener todas las imagenes o videos asociados a la publicación
    imagenVideo = (
        db.session.query(Public_imagen_video)
        .filter_by(publicacion_id=publicacion.id)
        .order_by(Public_imagen_video.id.asc())  # Ordena para obtener el primero
        .all()
    )

    imagenes = []
    videos = []

    for imagen_video in imagenVideo:
        # Si hay una imagen asociada
        if imagen_video.imagen_id:
            try:
                imagen = db.session.query(Image).filter_by(id=imagen_video.imagen_id).first()
                if imagen:
                    filepath = imagen.filepath
                    imagen_url = filepath.replace('static/uploads/', '').replace('static\\uploads\\', '')   
                    imagen_url = mostrar_from_gcs(imagen_url)  # Asegúrate de definir esta función
                    if imagen_url:
                        imagenes.append({
                            'id': imagen.id,
                            'title': imagen.title,
                            'description': imagen.description,
                            'filepath': imagen_url,
                            'randomNumber': imagen.randomNumber,
                            'size': imagen.size
                        })
            except Exception as e:
                logging.error(f"Error al obtener información de la imagen {imagen_video.imagen_id}: {e}")

        # Si hay un video asociado
        if imagen_video.video_id:
            try:
                video = db.session.query(Video).filter_by(id=imagen_video.video_id).first()
                if video:
                    filepath = video.filepath
                    video_url = filepath.replace('static/uploads/', '').replace('static\\uploads\\', '')
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
                logging.error(f"Error al obtener información del video {imagen_video.video_id}: {e}")

    # Agregar los datos de la publicación con imágenes y videos
    publicaciones_data.append({
        'publicacion_id': publicacion.id,
        'user_id': publicacion.user_id,
        'titulo': publicacion.titulo,
        'ambito': publicacion.ambito,
        'correo_electronico': publicacion.correo_electronico,
        'imagenes': imagenes,
        'videos': videos,
        'layout': layout
    })

    return publicaciones_data














@imagenesOperaciones.route('/imagenesOperaciones-cargarImagenVideosAgregados-publicacion', methods=['POST'])
def imagenesOperaciones_cargarImagenVideosAgregados_publicacion():
    try:
        if 'selectedColor' not in request.form:
            return jsonify({'error': 'No se proporcionó el campo de selectedColor'}), 400

        selectedColor = request.form['selectedColor']
        
        # Verificar si se proporcionaron imágenes
        imagenes = request.form.getlist('imagenes')  # Esto debería traer las imágenes en base64
        if imagenes:
            for image_data in imagenes:
                # Decodificar el base64
                header, encoded = image_data.split(",", 1)
                image_bytes = base64.b64decode(encoded)

                # Crear un archivo a partir de los bytes
                imagen = BytesIO(image_bytes)
                filename = secure_filename("image_from_base64.png")
                new_path = os.path.join('static', 'uploads', filename)
                with open(new_path, 'wb') as f:
                    f.write(image_bytes)

                # Subir el archivo a Google Cloud Storage
                upload_to_gcs(new_path, filename)

        # Verificar si los archivos 'imagen' o 'video' están en request.files
        archivo = None
        archivo_type = None
        if 'imagen' in request.files:
            archivo = request.files['imagen']
            archivo_type = 'imagen'
        elif 'video' in request.files:
            archivo = request.files['video']
            archivo_type = 'video'

        if archivo:
            # Lógica para manejar el archivo 'imagen' o 'video'
            if archivo.filename == '':
                return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
            
            # Verificar si el archivo tiene un tipo aceptable
            if archivo_type == 'imagen' and not allowed_image_file(archivo.filename):
                return jsonify({'error': 'Formato de imagen no permitido'}), 400
            if archivo_type == 'video' and not allowed_video_file(archivo.filename):
                return jsonify({'error': 'Formato de video no permitido'}), 400

            # Guardar archivo en la carpeta 'uploads'
            archivo.save(os.path.join('static', 'uploads', archivo.filename))
            # Subir a GCS
            upload_to_gcs(os.path.join('static', 'uploads', archivo.filename), archivo.filename)

        # Verificar y guardar en la base de datos
        if 'nombreArchivo' not in request.form or 'descriptionImagen' not in request.form:
            return jsonify({'error': 'Campos necesarios no proporcionados'}), 400
        
        nombre_archivo = request.form['nombreArchivo']
        descriptionImagen = request.form['descriptionImagen']
        randomNumber_ = request.form['randomNumber']
        numeroAleatoreo = int(randomNumber_)

        # Verificar si el token de acceso está presente
        if 'Authorization' not in request.headers:
            return jsonify({'error': 'Token de acceso no proporcionado'}), 401

        authorization_header = request.headers['Authorization']
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato de token de acceso no válido'}), 401

        access_token = parts[1]
        app = current_app._get_current_object()
        userid = jwt.decode(access_token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])['sub']

        nueva_imagen = Image(
            user_id=userid,
            title=nombre_archivo,
            description=descriptionImagen,
            colorDescription=selectedColor,
            filepath=new_path,
            randomNumber=numeroAleatoreo,
            size=archivo.content_length
        )
        db.session.add(nueva_imagen)
        db.session.commit()

        return jsonify({'mensaje': 'Archivo cargado con éxito', 'nombreArchivo': nombre_archivo})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Función para verificar si el archivo es una imagen
def allowed_image_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Función para verificar si el archivo es un video
def allowed_video_file(filename):
    allowed_extensions = {'mp4', 'mkv', 'avi', 'mov'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
