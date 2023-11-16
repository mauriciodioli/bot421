import os
from flask import Flask,jsonify, request, render_template, Blueprint,current_app, url_for
from utils.db import db
from models.modelMedia.image import Image

# Configuración del Blueprint para el registro de usuarios
imagenesOperaciones = Blueprint("imagenesOperaciones", __name__)

@imagenesOperaciones.route('/subirImagen/')
def subirImagen():
    return render_template("media/principalMedia/subirImage.html")

@imagenesOperaciones.route('/cargarImagen', methods=['POST'])
def cargarImagen():
  try:
        # Verificar si el campo 'imagen' está en la solicitud
        if 'imagen' not in request.files:
            return jsonify({'error': 'No se proporcionó el campo de imagen'}), 400

        imagen = request.files['imagen']

        # Verificar si el campo 'nombreArchivo' está en la solicitud
        if 'nombreArchivo' not in request.form:
            return jsonify({'error': 'No se proporcionó el campo de nombreArchivo'}), 400

        nombre_archivo = request.form['nombreArchivo']

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
        # Resto de tu lógica para manejar la imagen, el nombre del archivo y el access_token
        # Aquí puedes acceder a 'imagen' (objeto FileStorage), 'nombre_archivo' y 'access_token'
        MostrarImages()
        return jsonify({'mensaje': 'Imagen cargada con éxito', 'nombreArchivo': nombre_archivo})
  except Exception as e:
        return jsonify({'error': str(e)}), 500

@imagenesOperaciones.route('/MostrarImages/')
def MostrarImages():
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

    return render_template('media/principalMedia/images.html', image_paths=image_paths)
    
  

@imagenesOperaciones.route('/mostrarGaleria', methods = ['POST'])
def MostrarGaleria():
     if request.method == 'POST':
        correo_electronico = request.form['correo_electronico']
        password = request.form['password']
        selector = request.json.get('selectorEnvironment')
        account = request.json.get('account')
        # Buscar el usuario en la base de datos
        #crea_tabla_Image()
        #usuario = Usuario.query.filter_by(correo_electronico=correo_electronico).first()
        imagenes = Image.query.all()
    
    # Envía información adicional (cuenta) a la plantilla
 #      cuenta = [account, user, selector]
    
# return render_template('home.html', imagenes=imagenes, cuenta=cuenta)
