# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app

import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import tokens.token as Token
import jwt
import asyncio
from models.usuario import Usuario
from models.brokers import Broker
from models.modelMedia.TelegramNotifier import TelegramNotifier
from collections import defaultdict

chat = Blueprint('chat',__name__)

# Simulamos una base de datos en memoria
administrators = defaultdict(list)  # Cada administrador tiene una lista de hilos (máx. 10)
conversations = defaultdict(list)  # Cada usuario tiene una lista de mensajes

# Simulamos administradores disponibles
admin_list = ["admin1", "admin2"]

# Obtener un administrador disponible (menos de 10 hilos activos)
def assign_admin():
    for admin, threads in administrators.items():
        if len(threads) < 10:
            return admin
    return None

# API para manejar el hilo de mensajes
@chat.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    user_id = data['userId']
    message = data['message']
    
    if user_id not in conversations:
        admin = assign_admin()
        if admin:
            administrators[admin].append(user_id)
        else:
            return jsonify({"error": "No hay administradores disponibles."}), 503
    
    conversations[user_id].append({"sender": "user", "text": message})
    
    return jsonify({"status": "Mensaje enviado"})

# Obtener hilos de mensajes para un administrador
@chat.route('/admin/get_threads', methods=['GET'])
def get_threads():
    admin = request.args.get('admin')  # Nombre del administrador
    threads = [{"userId": user_id, "lastMessage": conversations[user_id][-1]["text"]}
               for user_id in administrators[admin]]
    return jsonify(threads)

# Obtener conversación completa de un hilo
@chat.route('/admin/get_conversation/<int:user_id>', methods=['GET'])
def get_conversation(user_id):
    return jsonify(conversations[user_id])

# Enviar respuesta del administrador a un hilo
@chat.route('/admin/send_reply', methods=['POST'])
def send_reply():
    data = request.get_json()
    user_id = data['userId']
    message = data['message']
    
    conversations[user_id].append({"sender": "admin", "text": message})
    
    return jsonify({"status": "Respuesta enviada"})