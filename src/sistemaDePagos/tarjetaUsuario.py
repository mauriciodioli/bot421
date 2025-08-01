# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app,session

import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import tokens.token as Token
import jwt
from models.usuario import Usuario
from models.cuentas import Cuenta
from models.payment_page.tarjetaUsuario import TarjetaUsuario
from utils.db_session import get_db_session 



tarjetaUsuario = Blueprint('tarjetaUsuario',__name__)

def altaTarjeta(data):
    try:
        with get_db_session() as session:
            # Verificar si ya existe una tarjeta con el mismo número de tarjeta y usuario
            tarjeta_existente = session.query(TarjetaUsuario).filter_by(
                user_id=int(data['user_id']),
                numeroTarjeta=data['numeroTarjeta']           
            ).first()

            if tarjeta_existente:
                return jsonify({"message": "Ya existe una tarjeta con este número para este usuario"}), 400

            nueva_tarjeta = TarjetaUsuario(
                user_id=data['user_id'],
                numeroTarjeta=data['numeroTarjeta'],
                fecha_vencimiento=data['fecha_vencimiento'],
                cvv=data['cvv'],
                nombreApellidoTarjeta=data['nombreApellidoTarjeta'],
                correo_electronico=data['correo_electronico'],
                accountCuenta=None
            )

            session.add(nueva_tarjeta)
            session.commit()
       
        return jsonify({"message": "Tarjeta creada con éxito", "tarjeta": nueva_tarjeta.id}), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500

def bajaTarjeta(id):
    try:
        with get_db_session() as session:
            tarjeta = session.query(TarjetaUsuario).get_or_404(id)
            session.delete(tarjeta)
            session.commit()
    except Exception as e:
      
        raise e
  

    return jsonify({"message": "Tarjeta eliminada con éxito"}), 200

def modificarTarjeta(id):
    try:
        data = request.json
        with get_db_session() as session:
            tarjeta = session.query(TarjetaUsuario).get_or_404(id)
            
            tarjeta.numeroTarjeta = data['numeroTarjeta']
            tarjeta.fecha_vencimiento = data['fecha_vencimiento']
            tarjeta.cvv = data['cvv']
            tarjeta.nombreApellidoTarjeta = data['nombreApellidoTarjeta']
            tarjeta.correo_electronico = data['correo_electronico']
            tarjeta.accountCuenta = data.get('accountCuenta', tarjeta.accountCuenta)
            
            session.commit()
    except Exception as e:
        
        raise e
   

    return jsonify({"message": "Tarjeta actualizada con éxito"}), 200
