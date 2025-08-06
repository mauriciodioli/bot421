# Creating  Routes
from pipes import Template
from unittest import result
from flask import current_app
import requests
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash,jsonify,abort    
from utils.db import db
from sqlalchemy import and_
import routes.api_externa_conexion.get_login as get
import jwt
from sqlalchemy import func
from models.usuario import Usuario
from models.publicaciones.ambitos import Ambitos
from models.publicaciones.ambito_usuario import Ambito_usuario
from models.publicaciones.ambitoCategoria import AmbitoCategoria
from models.publicaciones.ambitoCategoriaRelation import AmbitoCategoriaRelation
from models.publicaciones.categoriaPublicacion import CategoriaPublicacion
from models.publicaciones.publicacionCodigoPostal import PublicacionCodigoPostal
from utils.db_session import get_db_session 


from sqlalchemy.orm import aliased
from models.publicaciones.categoria_general import CategoriaGeneral, CategoriaTraduccion
from models.publicaciones.ambito_general import AmbitoGeneral,AmbitoTraduccion
from models.publicaciones.publicaciones import Publicacion


ambitosCategorias = Blueprint('ambitosCategorias', __name__)



@ambitosCategorias.route('/social-media-ambitosCategorias-categorias/')
def social_media_social_categorias():
    print('social_media_social_categorias')
    return render_template('ambitos/ambitoCategoria.html', layout='layout_administracion')

@ambitosCategorias.route('/social-media-ambitosCategorias-categoria-mostrar/', methods=['POST'])
def social_media_ambitosCategorias_categoria_mostrar():
    try:
        idioma = request.cookies.get('language', 'in')  # Idioma destino
        ambito_nombre = request.form.get('ambito') or 'Laboral'
        codigo_postal = request.form.get('cp')

        print(f"[DEBUG] idioma recibido: {idioma}")
        print(f"[DEBUG] código postal recibido: {codigo_postal}")
        print(f"[DEBUG] ambito_nombre recibido: {ambito_nombre}")
        with get_db_session() as session:
            # Paso 1: Buscar el ámbito directamente
            ambito = session.query(Ambitos).filter(
                func.lower(Ambitos.valor) == ambito_nombre.lower(),
                Ambitos.idioma == idioma,
                Ambitos.estado == 'ACTIVO'
            ).first()

            if not ambito:
                print("[DEBUG] Ámbito no encontrado directamente, devolviendo error.")
                return jsonify({'error': 'Ámbito no encontrado en este idioma'}), 404

            print(f"[DEBUG] Ámbito encontrado: {ambito.id} | {ambito.valor}")

            # Paso 2: Buscar relaciones con categorías
            relaciones = session.query(AmbitoCategoriaRelation).filter_by(
                ambito_id=ambito.id,
                estado='ACTIVO'
            ).all()

            print(f"[DEBUG] Relaciones encontradas: {len(relaciones)}")

            if not relaciones:
                print("[DEBUG] No hay relaciones de categoría para este ámbito")
                return jsonify({'categorias': []})

            categoria_ids = [rel.ambitoCategoria_id for rel in relaciones]

            # Paso 3: Buscar categorías asociadas
            categorias = session.query(AmbitoCategoria).filter(
                AmbitoCategoria.id.in_(categoria_ids),
                AmbitoCategoria.estado == 'ACTIVO',
                AmbitoCategoria.idioma == idioma
            ).all()

            print(f"[DEBUG] Categorías encontradas: {len(categorias)}")

            # Paso 4: Serializar
            categorias_data = [{
                'id': c.id,
                'ambito': ambito.valor,
                'nombre': c.nombre,
                'descripcion': c.descripcion,
                'idioma': c.idioma,
                'valor': c.valor,
                'color': c.color,
                'estado': c.estado
            } for c in categorias]

            return jsonify({'categorias': categorias_data})

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({'error': 'Problemas con la base de datos'}), 500

 






# Crear un nuevo Ambito
@ambitosCategorias.route('/social-media-ambitos-crear-categoria/', methods=['POST'])
def social_media_ambitos_crear_categoria():
    try:
        data = request.get_json()

        nombre = data.get('nombre')
        descripcion = data.get('descripcion')
        idioma = data.get('idioma', None)
        valor = data.get('valor', None)
        color = data.get('color', None)
        estado = data.get('estado', None)
        nombreAmbito = data.get('ambito', None)
        codigo_postal = data.get('cp', None)
        # Validar campos obligatorios
        if not nombre or not descripcion:
            return jsonify({"error": "Los campos 'nombre' y 'descripcion' son obligatorios"}), 400
        with get_db_session() as session:
            # Buscar si ya existe un ámbito con ese nombre e idioma
            existing_ambito = session.query(AmbitoCategoria).filter_by(nombre=nombre, idioma=idioma).first()
            if existing_ambito:
                session.close()
                return jsonify({"error": "La categoría ya existe en este idioma"}), 400
            ambito = session.query(Ambitos).filter_by(valor=nombreAmbito,idioma=idioma).first()
            # Crear la nueva categoría
            nuevo_ambito_categoria = AmbitoCategoria(
                nombre=nombre,
                descripcion=descripcion,
                idioma=idioma,
                valor=valor,
                color=color,
                estado=estado
            )
            session.add(nuevo_ambito_categoria)
            session.commit()  # Confirmar antes de usar el ID generado

            # Crear la relación en Ambito_Categoria_Relation
            ambito_categoria = AmbitoCategoriaRelation(
                ambito_id=ambito.id,  # Usamos el ID generado correctamente
                ambitoCategoria_id=nuevo_ambito_categoria.id,               
                estado=estado
            )
            session.add(ambito_categoria)
            session.commit()

            # Serializar y devolver el nuevo ámbito
            resultado = serializar_ambito(nuevo_ambito_categoria)
          
            return jsonify(resultado), 201

    except Exception as e:
       
        return jsonify({"error": str(e)}), 500



@ambitosCategorias.route('/social-media-ambitos-actualizar-categoria/<int:id>', methods=['PUT'])
def social_media_ambitos_actualizar_categoria(id):
    try:
        with get_db_session() as session:
            # Obtener el ambito existente
            ambitoCategoria = session.query(AmbitoCategoria).filter_by(id=id).first() 

            # Verificar si el ambito existe
            if not ambitoCategoria:
                return jsonify({"error": "Ambito no encontrado"}), 404

            # Obtener los datos del cuerpo de la solicitud
            data = request.get_json()

            # Actualizar los campos del ambito
            ambitoCategoria.nombre = data.get('nombre', ambitoCategoria.nombre)
            ambitoCategoria.descripcion = data.get('descripcion', ambitoCategoria.descripcion)
            ambitoCategoria.idioma = data.get('idioma', ambitoCategoria.idioma)
            ambitoCategoria.valor = data.get('valor', ambitoCategoria.valor)
            ambitoCategoria.color = data.get('color', ambitoCategoria.color)
            ambitoCategoria.estado = data.get('estado', ambitoCategoria.estado)
        
            # Guardar los cambios en la base de datos
            session.commit()
        
            resultado = serializar_ambito(ambitoCategoria)

            return jsonify(resultado), 200
    except Exception as e:       
        return jsonify({"error": str(e)}), 500
    

@ambitosCategorias.route('/social-media-publicaciones-ambitosCategorias-delete/<int:id>', methods=['DELETE'])
def social_media_publicaciones_ambitosCategorias_delete(id):
    try:
        with get_db_session() as session:
            # Buscar el ámbito por su ID
            ambitoCategoria = session.query(AmbitoCategoria).filter_by(id=id).first()

            # Verificar si el ámbito existe antes de proceder
            if not ambitoCategoria:
                return jsonify({"error": "Ámbito no encontrado"}), 404

            # Buscar y eliminar relaciones asociadas
            relaciones = session.query(AmbitoCategoriaRelation).filter_by(ambitoCategoria_id=id).all()
            for relacion in relaciones:
                session.delete(relacion)

            # Eliminar el ámbito
            session.delete(ambitoCategoria)

            # Confirmar los cambios en la base de datos
            session.commit()

            return jsonify({"message": "Ámbito y usuarios asociados eliminados exitosamente"}), 200

    except Exception as e:
        # Si ocurre un error, revertir los cambios pendientes
         return jsonify({"error": str(e)}), 500

   


@ambitosCategorias.route('/social-media-publicaciones-obtener-ambitosCategorias/', methods=['POST'])
def obtener_ambitosCategorias():
    try:
        # Obtener el ámbito por su valor
        data = request.get_json()
        print("Datos recibidos:", data)  # Para depuración

        if not data or 'ambito' not in data:
            return jsonify({"error": "Falta el campo 'ambito' en la solicitud"}), 400
        
        ambito_valor = data['ambito']
        cp = data['cp']
        with get_db_session() as session:
            # Obtener el ámbito por su valor
            ambito = session.query(Ambitos).filter_by(valor=ambito_valor).first()
            if not ambito:
                session.close()
                return jsonify({"error": "Ámbito no encontrado"}), 404
            
            # Obtener todas las relaciones del ámbito con sus categorías
            relations = session.query(AmbitoCategoriaRelation).filter_by(ambito_id=ambito.id).all()
            
            # Obtener los IDs de las categorías relacionadas
            categoria_ids = [relation.ambitoCategoria_id for relation in relations]
            
            # Consultar las categorías correspondientes
            ambitosCategorias = session.query(AmbitoCategoria).filter(AmbitoCategoria.id.in_(categoria_ids),).all()

            # Convertir los objetos a diccionarios serializables
            resultado = [
                {
                    "id": categoria.id,              
                    "nombre": categoria.nombre,
                    "descripcion": categoria.descripcion,
                    "idioma": categoria.idioma,
                    "valor": categoria.valor,
                    "color": categoria.color,
                    "estado": categoria.estado,
                }
                for categoria in ambitosCategorias
            ]
            return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

   


def serializar_ambito(ambito):
    return {
        "id": ambito.id,
        "user_id": 'none',  # Asumiendo que no necesitas información de usuario en este caso
        "nombre": ambito.nombre,
        "descripcion": ambito.descripcion,
        "idioma": ambito.idioma,
        "valor": ambito.valor,
        "color": ambito.color,
        "estado": ambito.estado,
    }