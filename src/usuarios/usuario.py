# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app

import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify,abort    
from models.instrumento import Instrumento
from utils.db import db
import routes.api_externa_conexion.get_login as get
import jwt
from models.usuario import Usuario
from models.usuarioRegion import UsuarioRegion
from models.usuarioUbicacion import UsuarioUbicacion





usuario = Blueprint('usuario',__name__)

@usuario.route("/usuariosModal/", methods=['GET'])
def obtener_usuarios_modal():
    try:
        usuarios = db.session.query(Usuario).all()
        db.session.close()
        # Crear una lista de diccionarios para cada usuario
        usuarios_json = [{'id': usuario.id, 'nombre': usuario.correo_electronico} for usuario in usuarios]
        return jsonify(usuarios=usuarios_json)
    except Exception as e:
        print('Error al obtener usuarios:', str(e))
        abort(500)  # Devuelve un código de estado de error 500 si hay problemas con la base de datos
        
        
        
        
@usuario.route("/usuarios/", methods=["GET"])
def usuarios():
    try:
        cp = request.cookies.get('codigoPostal')

        if not cp:
            return "Código postal no proporcionado", 400

        # Filtrar UsuarioRegion con ese código postal
        usuario_regiones = db.session.query(UsuarioRegion).filter_by(codigoPostal=cp).all()

        if not usuario_regiones:
            return render_template("notificaciones/noPoseeDatos.html", layout='layout_administracion')

        # Obtener los IDs de usuario asociados a ese código postal
        usuarios_ids = [ur.user_id for ur in usuario_regiones]
        
        # Filtrar los usuarios que coinciden con los IDs obtenidos
        usuarios = db.session.query(Usuario).filter(Usuario.id.in_(usuarios_ids)).all()

        # Crear una estructura de datos que agrupe los usuarios con su información de UsuarioRegion
        usuarios_con_region = [
            {
                "usuario": usuario,
                "regiones": [ur for ur in usuario_regiones if ur.user_id == usuario.id],
                "codigo_postal": usuario_regiones[0].codigoPostal,  # Obtener código postal de UsuarioRegion
                "pais": usuario_regiones[0].pais,  # Obtener país de UsuarioRegion
                "idioma": usuario_regiones[0].idioma  # Obtener idioma de UsuarioRegion
            }
            for usuario in usuarios
        ]

        return render_template(
            "/usuarios/usuarios.html",
            datos=usuarios_con_region,  # Enviamos la lista de usuarios con sus regiones
            layout='layout_administracion'
        )

    except Exception as e:
        print(f'Error en la consulta: {e}')
        return "Problemas con la base de datos", 500

    finally:
        db.session.close()  # Cierra la sesión para evitar conexiones abiertas


@usuario.route("/eliminar-usuario/", methods=["POST"])
def eliminar_usuario():
    try:
        usuario_id = request.form['usuario_id']

        usuario = db.session.query(Usuario).get(usuario_id)
        usuarioRegion = db.session.query(UsuarioRegion).filter_by(user_id=int(usuario_id)).first()
        usuarioUbicacion = db.session.query(UsuarioUbicacion).filter_by(user_id=int(usuario_id)).first()
        
        if usuarioRegion:
            db.session.delete(usuarioRegion)

        if usuario:
            db.session.delete(usuario)
            
        if usuarioUbicacion:
            db.session.delete(usuarioUbicacion)
        
        db.session.commit()
        flash('Usuario eliminado correctamente.')

        cp = request.cookies.get('codigoPostal')
        usuario_regiones = db.session.query(UsuarioRegion).filter_by(codigoPostal=cp).all()

        if not usuario_regiones:
            return render_template("notificaciones/noPoseeDatos.html", layout='layout_administracion')

        usuarios_ids = [ur.user_id for ur in usuario_regiones]
        usuarios = db.session.query(Usuario).filter(Usuario.id.in_(usuarios_ids)).all()

        usuarios_con_region = [
            {
                "usuario": usuario,
                "regiones": [ur for ur in usuario_regiones if ur.user_id == usuario.id],
                "codigo_postal": usuario_regiones[0].codigoPostal,
                "pais": usuario_regiones[0].pais,
                "idioma": usuario_regiones[0].idioma
            }
            for usuario in usuarios
        ]

        return render_template(
            "/usuarios/usuarios.html",
            datos=usuarios_con_region,
            layout='layout_administracion'
        )

    except Exception as e:
        print(f'Error en la consulta: {e}')
        db.session.rollback()  # Revertir cambios en caso de error
        return "Problemas con la base de datos", 500

    finally:
        if db.session.is_active:
            db.session.close()




@usuario.route("/editar-usuario/",  methods=["POST"])
def editar_usuario():
    try:
        usuario_id = request.form['id']    
        usuario = db.session.query(Usuario).get(usuario_id) #Usuario.query.get(usuario_id)
        usuarioRegion = db.session.query(UsuarioRegion).filter_by(user_id=int(usuario_id)).first()
        usuarioUbicacion = db.session.query(UsuarioUbicacion).filter_by(user_id=int(usuario_id)).first()
        usuario.email = request.form['email']
        usuario.roll = request.form['rol']
        usuarioRegion.codigoPostal = request.form['codigoPostal']
        usuarioRegion.pais = request.form['pais']
        usuarioRegion.idioma = request.form['idioma']
        if usuarioUbicacion:
            usuarioUbicacion.latitud = request.form['latitud']
            usuarioUbicacion.longitud = request.form['longitud']
        else:
            usuarioUbicacion = UsuarioUbicacion(user_id=int(usuario_id), id_region=usuarioRegion.id, codigoPostal=request.form['codigoPostal'], latitud=float(request.form['latitud']), longitud=float(request.form['longitud'])) #UsuarioUbicacion(user_id=int(usuario_id), id_region=usuarioRegion.id, codigoPostal=request.form['codigoPostal'], latitud=request.form['latitud'], longitud=request.form['longitud'])
            db.session.add(usuarioUbicacion)
        
        db.session.commit()
        flash('Usuario editado correctamente.')
        cp = request.cookies.get('codigoPostal')
        # Filtrar UsuarioRegion con ese código postal
        usuario_regiones = db.session.query(UsuarioRegion).filter_by(codigoPostal=cp).all()

        if not usuario_regiones:
             return render_template("notificaciones/noPoseeDatos.html", layout='layout_administracion')

        # Obtener los IDs de usuario asociados a ese código postal
        usuarios_ids = [ur.user_id for ur in usuario_regiones]
        
        # Filtrar los usuarios que coinciden con los IDs obtenidos
        usuarios = db.session.query(Usuario).filter(Usuario.id.in_(usuarios_ids)).all()

        # Crear una estructura de datos que agrupe los usuarios con su información de UsuarioRegion
        usuarios_con_region = [
            {
                "usuario": usuario,
                "regiones": [ur for ur in usuario_regiones if ur.user_id == usuario.id],
                "codigo_postal": usuario_regiones[0].codigoPostal,  # Obtener código postal de UsuarioRegion
                "pais": usuario_regiones[0].pais,  # Obtener país de UsuarioRegion
                "idioma": usuario_regiones[0].idioma  # Obtener idioma de UsuarioRegion
            }
            for usuario in usuarios
        ]

        return render_template(
            "/usuarios/usuarios.html",
            datos=usuarios_con_region,  # Enviamos la lista de usuarios con sus regiones
            layout='layout_administracion'
        )

    except Exception as e:
        print(f'Error en la consulta: {e}')
        return "Problemas con la base de datos", 500

    finally:
        db.session.close()  # Cierra la sesión para evitar conexiones abiertas


