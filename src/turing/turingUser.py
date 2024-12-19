# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify,abort    
from utils.db import db
import routes.api_externa_conexion.get_login as get
import jwt
import random
from datetime import datetime

from models.turing.preguntas import Pregunta, PreguntaSchema
from models.turing.preguntaUsuario import PreguntaUsuario, PreguntaUsuarioSchema
from models.turing.testTuringUser import TestTuringUser


turingUser = Blueprint('turingUser', __name__)


def turingUser_crear_user(ip_cliente):
    
    usuario = db.session.query(TestTuringUser).filter_by(ip_cliente=ip_cliente).first()
    if usuario:
        return usuario
    else:
        # Genera un número entre 1 y 100 como nombre (puedes cambiar esto)
        nombre = random.randint(1, 100)
        nombre = str(nombre) + "_" + ip_cliente
        # Si el usuario no existe, crearlo
        nuevo_usuario = TestTuringUser(nombre=nombre, 
                                ip_cliente=ip_cliente,
                                fecha_registro=datetime.now(),
                                estado="activo",
                                )
        db.session.add(nuevo_usuario)
        db.session.commit()
       
        return nuevo_usuario
    
def turingUser_eliminar_user(id):
    user = db.session.query(TestTuringUser).filter_by(id=id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        db.session.close()
        return True
    else:
        return False
