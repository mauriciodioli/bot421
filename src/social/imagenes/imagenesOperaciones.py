import os
from flask import Flask, request, render_template, Blueprint
from utils.db import db
from models.modelMedia.image import Image

# Configuración del Blueprint para el registro de usuarios
imagenesOperaciones = Blueprint("imagenesOperaciones", __name__)

@imagenesOperaciones.route('/subirImagen/')
def subirImagen():
    return render_template("media/principalMedia/subirImage.html")

@imagenesOperaciones.route('/cargarImagen', methods=['POST'])
def cargarImagen():
    title = request.form['title']
    description = request.form['description']
    image = request.files['image']
    filename = image.filename
    # Guardar la imagen en el servidor
    filepath = os.path.join("carpeta_destino", filename)
    image.save(filepath)
    # Guardar la información de la imagen en la base de datos
    new_image = Image(title=title, description=description, filepath=filepath)
    db.session.add(new_image)
    db.session.commit()
    return 'Image uploaded successfully'

@imagenesOperaciones.route('/MostrarImages')
def MostrarImages():
    # Obtener las imágenes desde la base de datos
    images = Image.query.all()
    return render_template('images.html', images=images)
