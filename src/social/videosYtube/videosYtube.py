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

import jwt
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
import sys

# Configuración del Blueprint para el registro de usuarios
videosYtube = Blueprint("videosYtube", __name__)



@videosYtube.route('/subirVideoYtube/')
def subirVideoYtube():      
    return render_template('media/principalMedia/subirVideoYtube.html', layout='layout_dpi')