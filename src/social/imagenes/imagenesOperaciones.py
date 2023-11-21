import os
from flask import Flask,jsonify, request, render_template, Blueprint,current_app, url_for
from utils.db import db
from models.modelMedia.image import Image
import jwt
from flask_jwt_extended import jwt_required, get_jwt_identity

# Configuración del Blueprint para el registro de usuarios
imagenesOperaciones = Blueprint("imagenesOperaciones", __name__)

@imagenesOperaciones.route('/subirImagen/')
def subirImagen():
    return render_template("media/principalMedia/subirImage.html")

@imagenesOperaciones.route('/subirVideo/')
def subirVideo():
    return render_template("media/principalMedia/subirVideo.html")

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
            randomNumber=random_number
        )

        db.session.add(nueva_imagen)
        db.session.commit()

        # Realizar alguna acción adicional si es necesario, como mostrar las imágenes
        MostrarImages()

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
                randomNumber=numeroAleatoreo
            )
            db.session.add(nueva_imagen)
            db.session.commit()
          
       # MostrarImages()
        return jsonify({'mensaje': 'Imagen cargada con éxito', 'nombreArchivo': nombre_archivo})
  except Exception as e:
        return jsonify({'error': str(e)}), 500

@imagenesOperaciones.route('/MostrarImages/', methods=['POST'])
def mostrar_imagenes():
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
        
        # Convertir los paths al formato deseado
       # Obtener los paths en el formato deseado# Cambiar el formato de las rutas
        image_paths = [img.filepath.replace('static\\', '').replace('\\', '/') for img in imagenes]
      
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

@imagenesOperaciones.route('/eliminarImagen', methods = ['POST'])
def eliminar_imagen():
    return''
    
