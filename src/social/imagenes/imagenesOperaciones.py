import os
    
from flask import Flask, request, render_template,Blueprint
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
    #filepath = os.path.join(UPLOAD_FOLDER , filename)
    #image.save(filepath)
    # Save the filepath and other image information to the MySQL database
    return 'Image uploaded successfully'

@imagenesOperaciones.route('/MostrarImages')
def MostrarImages():
    
    cursor = db.conn.cursor()
    cursor.execute('SELECT * FROM images')
    images = cursor.fetchall()
    return render_template('images.html', images=images)