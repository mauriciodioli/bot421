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
from models.publicaciones.categoriaCodigoPostal import CategoriaCodigoPostal
from models.codigoPostal import CodigoPostal
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


            cp_id = session.query(CodigoPostal.id)\
                            .filter(CodigoPostal.codigoPostal == codigo_postal)\
                            .scalar()


           # 1) IDs desde la relación CategoriaCodigoPostal (filtrando por CP string)
            relaciones_categorias = (
                session.query(CategoriaCodigoPostal.categoria_id)
                .filter(
                    CategoriaCodigoPostal.categoria_id.in_(categoria_ids),
                    CategoriaCodigoPostal.codigo_postal_id == cp_id
                )
                .all()
            )

            # 2) Flatten a lista simple
            categoria_ids2 = [cid for (cid,) in relaciones_categorias]

            if not categoria_ids2:
                print("[DEBUG] No hay categorías asociadas a ese CP para este ámbito")
                return jsonify({'categorias': []})

            # 3) Traer las categorías finales
            categorias = session.query(AmbitoCategoria).filter(
                AmbitoCategoria.id.in_(categoria_ids2),
                AmbitoCategoria.estado == 'ACTIVO'
                # opcional: , AmbitoCategoria.idioma == idioma
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

        nombre        = data.get('nombre')
        descripcion   = data.get('descripcion')
        idioma        = data.get('idioma', None)
        valor         = data.get('valor', None)
        color         = data.get('color', None)
        estado        = data.get('estado', None)
        nombreAmbito  = data.get('ambito', None)
        codigo_postal = data.get('cp', None)

        # Validar campos obligatorios
        if not nombre or not descripcion:
            return jsonify({"error": "Los campos 'nombre' y 'descripcion' son obligatorios"}), 400

        with get_db_session() as session:
            # 1) Validar duplicado por nombre+idioma
            existing_ambito = session.query(AmbitoCategoria).filter_by(nombre=nombre, idioma=idioma).first()
            if existing_ambito:
                return jsonify({"error": "La categoría ya existe en este idioma"}), 400

            # 2) Buscar ámbito destino (obligatorio)
            ambito = session.query(Ambitos).filter_by(valor=nombreAmbito, idioma=idioma, estado='ACTIVO').first()
            if not ambito:
                return jsonify({"error": "Ámbito no encontrado o inactivo para ese idioma"}), 404

            # 3) Crear categoría
            nuevo_ambito_categoria = AmbitoCategoria(
                nombre=nombre,
                descripcion=descripcion,
                idioma=idioma,
                valor=valor,
                color=color,
                estado=estado
            )
            session.add(nuevo_ambito_categoria)
            session.flush()  # <-- NECESARIO para tener nuevo_ambito_categoria.id

            # 4) Relación Ámbito ↔ Categoría
            ambito_categoria = AmbitoCategoriaRelation(
                ambito_id=ambito.id,
                ambitoCategoria_id=nuevo_ambito_categoria.id,
                estado=estado
            )
            session.add(ambito_categoria)

            # 5) (Nuevo) Relación Categoría ↔ Código Postal
            if codigo_postal:
                # Buscar/crear CP
                cp_obj = session.query(CodigoPostal).filter_by(codigoPostal=codigo_postal).first()
                if not cp_obj:
                    cp_obj = CodigoPostal(codigoPostal=codigo_postal)
                    session.add(cp_obj)
                    session.flush()  # <-- para cp_obj.id

                # Evitar duplicado de relación
                cat_cp_rel = session.query(CategoriaCodigoPostal).filter_by(
                    categoria_id=nuevo_ambito_categoria.id,
                    codigo_postal_id=cp_obj.id
                ).first()
                if not cat_cp_rel:
                    cat_cp_rel = CategoriaCodigoPostal(
                        categoria_id=nuevo_ambito_categoria.id,
                        codigo_postal_id=cp_obj.id
                    )
                    session.add(cat_cp_rel)

            # 6) Serializar y devolver
            resultado = serializar_ambito(nuevo_ambito_categoria)
            return jsonify(resultado), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ambitosCategorias.route('/social-media-ambitos-actualizar-categoria', methods=['POST'])
def social_media_ambitos_actualizar_categoria():
    try:
        with get_db_session() as session:
            data = request.get_json(silent=True) or {}
            cat_id = data.get('id')
            ambito_id = data.get('ambitoId')

            if not cat_id:
                return jsonify({"error": "Falta el ID de la categoría"}), 400
            if ambito_id is None:
                return jsonify({"error": "Falta 'ambitoId'"}), 400

            cat = session.query(AmbitoCategoria).filter_by(id=cat_id).first()
            if not cat:
                return jsonify({"error": "Categoría no encontrada"}), 404

            # Actualizar campos de la categoría
            cat.nombre      = data.get('nombre', cat.nombre)
            cat.descripcion = data.get('descripcion', cat.descripcion)
            cat.idioma      = data.get('idioma', cat.idioma)
            cat.valor       = data.get('valor', cat.valor)
            cat.color       = data.get('color', cat.color)
            cat.estado      = data.get('estado', cat.estado)

            # --- Actualizar relación Ámbito <-> Categoría ---
            ambito_id = int(ambito_id)

            # 1) Si ya existe EXACTAMENTE esa relación, no dupliques
            existe = session.query(AmbitoCategoriaRelation).filter_by(
                ambitoCategoria_id=cat.id,
                ambito_id=ambito_id
            ).first()

            if not existe:
                # 2) Opcional: borrar otras relaciones previas de la categoría (si la relación es 1:1)
                session.query(AmbitoCategoriaRelation).filter_by(
                    ambitoCategoria_id=cat.id
                ).delete(synchronize_session=False)

                # 3) Crear la nueva relación
                session.add(AmbitoCategoriaRelation(
                    ambitoCategoria_id=cat.id,
                    ambito_id=ambito_id,
                    estado=cat.estado or 'ACTIVO'
                ))
            # --- fin actualización relación ---

            return jsonify(serializar_ambito(cat)), 200

    except Exception as e:
        import traceback; traceback.print_exc()
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
        data = request.get_json(silent=True) or {}
        print("Datos recibidos:", data)
        languaje = request.cookies.get('language', 'in')
        if 'ambito' not in data:
            return jsonify({"error": "Falta el campo 'ambito' en la solicitud"}), 400
        
        ambito_valor = data['ambito']
        cp = data.get('cp')  # puede venir string tipo "06049"

        with get_db_session() as session:
            # Ámbito por valor+idioma
            ambito = session.query(Ambitos).filter_by(valor=ambito_valor, idioma=languaje).first()
            if not ambito:
                return jsonify({"error": "Ámbito no encontrado"}), 404
            
            # Relaciones del ámbito -> categoria_ids
            relations = session.query(AmbitoCategoriaRelation).filter_by(ambito_id=ambito.id).all()
            categoria_ids = [r.ambitoCategoria_id for r in relations]

            # ---------- Fallback por Código Postal ----------
            if not categoria_ids and cp:
                # resolver cp_id (FK) desde el string de CP
                cp_id = session.query(CodigoPostal.id)\
                               .filter(CodigoPostal.codigoPostal == cp)\
                               .scalar()
                if cp_id:
                    # tomar las categorías asociadas a ese CP
                    cat_ids_cp = session.query(CategoriaCodigoPostal.categoria_id)\
                                        .filter(CategoriaCodigoPostal.codigo_postal_id == cp_id)\
                                        .all()
                    categoria_ids = [cid for (cid,) in cat_ids_cp]
                else:
                    # no existe ese CP en la tabla -> no hay categorías
                    categoria_ids = []
            # ------------------------------------------------

            if not categoria_ids:
                return jsonify([]), 200

            # Categorías finales
            ambitosCategorias = session.query(AmbitoCategoria).filter(
                AmbitoCategoria.id.in_(categoria_ids),
                AmbitoCategoria.idioma == languaje,
                AmbitoCategoria.estado == 'ACTIVO'
            ).all()

            resultado = [{
                "id": c.id,
                "nombre": c.nombre,
                "descripcion": c.descripcion,
                "idioma": c.idioma,
                "valor": c.valor,
                "color": c.color,
                "estado": c.estado,
            } for c in ambitosCategorias]

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