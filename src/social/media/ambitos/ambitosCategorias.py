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
from models.usuario import Usuario
from models.publicaciones.ambitos import Ambitos
from models.publicaciones.ambito_usuario import Ambito_usuario
from models.publicaciones.ambitoCategoria import AmbitoCategoria
from models.publicaciones.ambitoCategoriaRelation import AmbitoCategoriaRelation
from models.publicaciones.categoriaPublicacion import CategoriaPublicacion
from models.publicaciones.publicacionCodigoPostal import PublicacionCodigoPostal


ambitosCategorias = Blueprint('ambitosCategorias', __name__)



@ambitosCategorias.route('/social-media-ambitosCategorias-categorias/')
def social_media_social_categorias():
    print('social_media_social_categorias')
    return render_template('ambitos/ambitoCategoria.html', layout='layout_administracion')



@ambitosCategorias.route('/social-media-ambitosCategorias-categoria-mostrar/', methods=['POST'])
def social_media_ambitosCategorias_categoria_mostrar():
    try:
        # Obtener el valor de la cookie "language"
        idioma = request.cookies.get('language', 'in')  # Valor por defecto "in"

        # Obtener los datos del formulario
        ambito_nombre = request.form.get('ambito')
        codigo_postal = request.form.get('cp')
        if not ambito_nombre:
            ambito_nombre = 'Laboral'
        # Buscar el ámbito
        ambitos = db.session.query(Ambitos).filter(
            Ambitos.valor == ambito_nombre,
            Ambitos.idioma == idioma
        ).first()

        if not ambitos:
            db.session.close()
            return jsonify({'error': 'Ámbito no encontrado'}), 404

       # Buscar las relaciones
        relations = db.session.query(AmbitoCategoriaRelation).filter_by(ambito_id=ambitos.id).all()

        # Obtener todos los ids de las categorías que necesitamos
        categoria_ids = [relation.ambitoCategoria_id for relation in relations]

        # Obtener todas las categorías asociadas de una vez
        categorias_map = {categoria.id: categoria for categoria in db.session.query(AmbitoCategoria).filter(AmbitoCategoria.id.in_(categoria_ids)).all()}

        # Lista para almacenar las categorías
        categorias = []

        # Ahora, simplemente accedemos al diccionario de categorías
        for relation in relations:
            categoria = categorias_map.get(relation.ambitoCategoria_id)
            if categoria:  # Verificar que la categoría exista
                categorias.append(categoria)


        # Serializar los datos
        categorias_data = [{
            'id': categoria.id,     
            'ambito': ambito_nombre,     
            'nombre': categoria.nombre,
            'descripcion': categoria.descripcion,
            'idioma': categoria.idioma,
            'valor': categoria.valor,
            'color': categoria.color,
            'estado': categoria.estado
        } for categoria in categorias]
        db.session.close()
        return jsonify({'categorias': categorias_data})

    except Exception as e:
        print(f'Error al obtener los ámbitos: {e}')
        return jsonify({'error': 'Problemas con la base de datos'}), 500

    finally:
        db.session.close()




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

        # Buscar si ya existe un ámbito con ese nombre e idioma
        existing_ambito = db.session.query(AmbitoCategoria).filter_by(nombre=nombre, idioma=idioma).first()
        if existing_ambito:
            db.session.close()
            return jsonify({"error": "La categoría ya existe en este idioma"}), 400
        ambito = db.session.query(Ambitos).filter_by(valor=nombreAmbito,idioma=idioma).first()
        # Crear la nueva categoría
        nuevo_ambito_categoria = AmbitoCategoria(
            nombre=nombre,
            descripcion=descripcion,
            idioma=idioma,
            valor=valor,
            color=color,
            estado=estado
        )
        db.session.add(nuevo_ambito_categoria)
        db.session.commit()  # Confirmar antes de usar el ID generado

        # Crear la relación en Ambito_Categoria_Relation
        ambito_categoria = AmbitoCategoriaRelation(
            ambito_id=ambito.id,  # Usamos el ID generado correctamente
            ambitoCategoria_id=nuevo_ambito_categoria.id,               
            estado=estado
        )
        db.session.add(ambito_categoria)
        db.session.commit()

        # Serializar y devolver el nuevo ámbito
        resultado = serializar_ambito(nuevo_ambito_categoria)
        db.session.close()
        return jsonify(resultado), 201

    except Exception as e:
        db.session.rollback()  # Deshacer cambios en caso de error
        return jsonify({"error": str(e)}), 500



@ambitosCategorias.route('/social-media-ambitos-actualizar-categoria/<int:id>', methods=['PUT'])
def social_media_ambitos_actualizar_categoria(id):
    try:
        # Obtener el ambito existente
        ambitoCategoria = db.session.query(AmbitoCategoria).filter_by(id=id).first() 

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
        db.session.commit()
       
        resultado = serializar_ambito(ambitoCategoria)

        return jsonify(resultado), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.close()  # ✅ Se ejecuta siempre

@ambitosCategorias.route('/social-media-publicaciones-ambitosCategorias-delete/<int:id>', methods=['DELETE'])
def social_media_publicaciones_ambitosCategorias_delete(id):
    try:
        # Buscar el ámbito por su ID
        ambitoCategoria = db.session.query(AmbitoCategoria).filter_by(id=id).first()

        # Verificar si el ámbito existe antes de proceder
        if not ambitoCategoria:
            return jsonify({"error": "Ámbito no encontrado"}), 404

        # Buscar y eliminar relaciones asociadas
        relaciones = db.session.query(AmbitoCategoriaRelation).filter_by(ambitoCategoria_id=id).all()
        for relacion in relaciones:
            db.session.delete(relacion)

        # Eliminar el ámbito
        db.session.delete(ambitoCategoria)

        # Confirmar los cambios en la base de datos
        db.session.commit()

        return jsonify({"message": "Ámbito y usuarios asociados eliminados exitosamente"}), 200

    except Exception as e:
        # Si ocurre un error, revertir los cambios pendientes
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        # Cerrar la sesión al final del proceso
        db.session.close()


@ambitosCategorias.route('/social-media-publicaciones-obtener-ambitosCategorias/', methods=['POST'])
def obtener_ambitosCategorias():
    try:
        # Obtener el ámbito por su valor
        data = request.get_json()
        print("Datos recibidos:", data)  # Para depuración

        if not data or 'ambito' not in data:
            return jsonify({"error": "Falta el campo 'ambito' en la solicitud"}), 400
        
        ambito_valor = data['ambito']

        # Obtener el ámbito por su valor
        ambito = db.session.query(Ambitos).filter_by(valor=ambito_valor).first()
        if not ambito:
            return jsonify({"error": "Ámbito no encontrado"}), 404
        
        # Obtener todas las relaciones del ámbito con sus categorías
        relations = db.session.query(AmbitoCategoriaRelation).filter_by(ambito_id=ambito.id).all()
        
        # Obtener los IDs de las categorías relacionadas
        categoria_ids = [relation.ambitoCategoria_id for relation in relations]
        
        # Consultar las categorías correspondientes
        ambitosCategorias = db.session.query(AmbitoCategoria).filter(AmbitoCategoria.id.in_(categoria_ids)).all()

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

    finally:
        db.session.close()  # Asegura que la sesión se cierre siempre


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