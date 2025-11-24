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
from utils.db_session import get_db_session 




usuario = Blueprint('usuario',__name__)

@usuario.route("/usuariosModal/", methods=['GET'])
def obtener_usuarios_modal():
    try:
        with get_db_session() as session:
            usuarios = session.query(Usuario).all()
            
            # Crear una lista de diccionarios para cada usuario
            usuarios_json = [{'id': usuario.id, 'nombre': usuario.correo_electronico} for usuario in usuarios]
            return jsonify(usuarios=usuarios_json)
    except Exception as e:
        print('Error al obtener usuarios:', str(e))
        abort(500)  # Devuelve un código de estado de error 500 si hay problemas con la base de datos
        
        
     
        
@usuario.route("/usuarios-generales/", methods=["GET"])
def usuarios_generales():
    try:
     
        with get_db_session() as session:
            # Filtrar UsuarioRegion con ese código postal
            usuario_regiones = session.query(UsuarioRegion).all()

            if not usuario_regiones:
                return render_template("notificaciones/noPoseeDatos.html", layout='layout_administracion')

            # Obtener los IDs de usuario asociados a ese código postal
            usuarios_ids = [ur.user_id for ur in usuario_regiones]
            
            # Filtrar los usuarios que coinciden con los IDs obtenidos
            usuarios = session.query(Usuario).filter(Usuario.id.in_(usuarios_ids)).all()

            # Crear una estructura de datos que agrupe los usuarios con su información de UsuarioRegion
            usuarios_con_region = [
                    {
                        "usuario": serializar_usuario(usuario),
                        "regiones": [serializar_region(ur) for ur in usuario_regiones if ur.user_id == usuario.id],
                        "codigo_postal": usuario_regiones[0].codigoPostal,
                        "pais": usuario_regiones[0].pais,
                        "idioma": usuario_regiones[0].idioma
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

  
       
        
@usuario.route("/usuarios/", methods=["GET"])
def usuarios():
    try:
        cp = request.cookies.get('codigoPostal')

        if not cp:
            return "Código postal no proporcionado", 400
        with get_db_session() as session:
            # Filtrar UsuarioRegion con ese código postal
            usuario_regiones = session.query(UsuarioRegion).filter_by(codigoPostal=cp).all()

            if not usuario_regiones:
                return render_template("notificaciones/noPoseeDatos.html", layout='layout_administracion')

            # Obtener los IDs de usuario asociados a ese código postal
            usuarios_ids = [ur.user_id for ur in usuario_regiones]
            
            # Filtrar los usuarios que coinciden con los IDs obtenidos
            usuarios = session.query(Usuario).filter(Usuario.id.in_(usuarios_ids)).all()

            # Crear una estructura de datos que agrupe los usuarios con su información de UsuarioRegion
            usuarios_con_region = [
                {
                    "usuario": serializar_usuario(usuario),
                    "regiones": [serializar_region(ur) for ur in usuario_regiones if ur.user_id == usuario.id],
                    "codigo_postal": usuario_regiones[0].codigoPostal,
                    "pais": usuario_regiones[0].pais,
                    "idioma": usuario_regiones[0].idioma
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

    


@usuario.route("/eliminar-usuario/", methods=["POST"])
def eliminar_usuario():
    try:
        usuario_id = request.form['usuario_id']
        with get_db_session() as session:
            usuario = session.query(Usuario).get(int(usuario_id))
            usuarioRegion = session.query(UsuarioRegion).filter_by(user_id=int(usuario_id)).first()
            usuarioUbicacion = session.query(UsuarioUbicacion).filter_by(user_id=int(usuario_id)).first()
            
            if usuarioRegion:
                session.delete(usuarioRegion)

            if usuario:
                session.delete(usuario)
                
            if usuarioUbicacion:
                session.delete(usuarioUbicacion)
            
          
            flash('Usuario eliminado correctamente.')

            cp = request.cookies.get('codigoPostal')
            usuario_regiones = session.query(UsuarioRegion).filter_by(codigoPostal=cp).all()

            if not usuario_regiones:
                return render_template("notificaciones/noPoseeDatos.html", layout='layout_administracion')

            usuarios_ids = [ur.user_id for ur in usuario_regiones]
            usuarios = session.query(Usuario).filter(Usuario.id.in_(usuarios_ids)).all()

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
      
        return "Problemas con la base de datos", 500

   




@usuario.route("/editar-usuario/",  methods=["POST"])
def editar_usuario():
    try:
        with get_db_session() as session:
            usuario_id = request.form['id']    
            usuario = session.query(Usuario).get(usuario_id) #Usuario.query.get(usuario_id)
            usuarioRegion = session.query(UsuarioRegion).filter_by(user_id=int(usuario_id)).first()
            usuarioUbicacion = session.query(UsuarioUbicacion).filter_by(user_id=int(usuario_id)).first()
            usuario.correo_electronico = request.form['email']
            usuario.roll = request.form['rol']
            usuarioRegion.codigoPostal = request.form['codigoPostal']
            usuarioRegion.pais = request.form['pais']
            usuarioRegion.idioma = request.form['idioma']
            if usuarioUbicacion:
                usuarioUbicacion.id_region = usuarioRegion.id             
                usuarioUbicacion.codigoPostal = request.form['codigoPostal']
                usuarioUbicacion.latitud = float(request.form['latitud'])
                usuarioUbicacion.longitud = float(request.form['longitud'])
            else:
                usuarioUbicacion = UsuarioUbicacion(
                    user_id=int(usuario_id),
                    id_region=usuarioRegion.id,
                    codigoPostal=request.form['codigoPostal'],
                    latitud=float(request.form['latitud']),
                    longitud=float(request.form['longitud'])
                )
                session.add(usuarioUbicacion)
                session.flush()

            
            
            flash('Usuario editado correctamente.')
            cp = request.form['codigoPostal']
            # Filtrar UsuarioRegion con ese código postal
            usuario_regiones = session.query(UsuarioRegion).filter_by(codigoPostal=cp).all()

            if not usuario_regiones:
                return render_template("notificaciones/noPoseeDatos.html", layout='layout_administracion')

            # Obtener los IDs de usuario asociados a ese código postal
            usuarios_ids = [ur.user_id for ur in usuario_regiones]
            
            # Filtrar los usuarios que coinciden con los IDs obtenidos
            usuarios = session.query(Usuario).filter(Usuario.id.in_(usuarios_ids)).all()

            # Crear una estructura de datos que agrupe los usuarios con su información de UsuarioRegion
             # Crear una estructura de datos que agrupe los usuarios con su información de UsuarioRegion
            usuarios_con_region = []
            for u in usuarios:
                regiones_u = [ur for ur in usuario_regiones if ur.user_id == u.id]

                usuarios_con_region.append({
                    "usuario": {
                        "id": u.id,
                        # usa los campos que realmente tengas en el modelo
                        "correo_electronico": getattr(u, "correo_electronico", None),
                        "roll": getattr(u, "roll", None),
                    },
                    "regiones": [
                        {
                            "id": r.id,
                            "user_id": r.user_id,
                            "codigoPostal": r.codigoPostal,
                            "pais": r.pais,
                            "idioma": r.idioma,
                        }
                        for r in regiones_u
                    ],
                    "codigo_postal": regiones_u[0].codigoPostal if regiones_u else None,
                    "pais": regiones_u[0].pais if regiones_u else None,
                    "idioma": regiones_u[0].idioma if regiones_u else None,
                })

            return render_template(
                "/usuarios/usuarios.html",
                datos=usuarios_con_region,  # Enviamos la lista de usuarios con sus regiones
                layout='layout_administracion'
            )

    except Exception as e:
        print(f'Error en la consulta: {e}')
        return "Problemas con la base de datos", 500

  

def serializar_region(region):
    return {
        "id": region.id,
        "user_id": region.user_id,
        "idioma": region.idioma,
        "codigo_postal": region.codigoPostal,
        "pais": region.pais,
        "region": region.region,
        "provincia": region.provincia,
        "ciudad": region.ciudad,
    }

def serializar_usuario(usuario):
    return {
        "id": usuario.id,
        "correo_electronico": usuario.correo_electronico,
        "roll": usuario.roll,
    }
