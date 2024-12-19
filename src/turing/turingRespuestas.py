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
from models.turing.respuesta import Respuesta, RespuestaSchema
from models.turing.respuestaUsuario import RespuestaUsuario, RespuestaUsuarioSchema
from models.turing.preguntaUsuario import PreguntaUsuario, PreguntaUsuarioSchema


turingRespuestas = Blueprint('turingRespuestas', __name__)

@turingRespuestas.route('/turing-turingRespuestas-crear', methods=['GET', 'POST'])
def social_media_turing_turingRespuestas_crear():    
    try:
        data = request.get_json()
        
        # Genera un número entre 1 y 100 como nombre (puedes cambiar esto)
        
        ip_cliente = data.get('ip_cliente', 'default_value')  # Proporciona un valor por defecto
      
        # Verificar si el usuario ya existe
        usuario = turingUser_crear_user(ip_cliente)
      
        nueva_respuesta = Respuesta(           
            descripcion=data.get('descripcion'),
            idioma=data.get('idioma'),
            valor=data['valor'],
            estado=data.get('estado'),
            dificultad=data.get('dificultad'),
            categoria=data.get('categoria')
        )
        
        # Agrega la nueva pregunta a la sesión
        db.session.add(nueva_pregunta)
        db.session.commit()  # Guarda la pregunta en la base de datos
        
        # Accede al id de la pregunta después de hacer commit
        pregunta_id = nueva_pregunta.id
        # Guardar como objeto datetime
        tiempo = datetime.now()
        nueva_respuesta_usuario = RespuestaUsuario(
            user_id=id_usuario,
            pregunta_id=pregunta_id,
            dificultad=data.get('dificultad'),
            estado=data.get('estado'),
            tiempo = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            fecha=tiempo.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Agrega la nueva relación de usuario-pregunta
        db.session.add(nueva_respuesta_usuario)
        db.session.commit()
        nueva_respuesta = serialize(nueva_respuesta)
        db.session.close()
        
        return jsonify(nueva_respuesta), 201

    except Exception as e:
      return jsonify({'error': str(e)}), 400
      db.session.rollback()
      db.session.close()
        