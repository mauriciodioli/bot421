from flask import Blueprint, request, jsonify
from utils.db import db
from models import Ambitos, ambitos_schema, ambitos_schemas  # Asegúrate de importar el modelo y los esquemas correctamente

ambito = Blueprint('ambito', __name__)

# Crear un nuevo Ambito
@ambito.route('/social-media-publicaciones-ambitos', methods=['POST'])
def crear_ambito():
try:
    # Obtener los datos del cuerpo de la solicitud
    data = request.get_json()
    
    # Extraer datos necesarios para crear un nuevo ambito
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    idioma = data.get('idioma', None)
    valor = data.get('valor', None)
    estado = data.get('estado', None)
    user_id = data.get('user_id')  # ID del usuario

    # Validar que los campos obligatorios estén presentes
    if not nombre or not user_id:
        return jsonify({"error": "El nombre y el user_id son obligatorios"}), 400
    
    # Crear el nuevo ambito
    nuevo_ambito = Ambitos(
        nombre=nombre,
        descripcion=descripcion,
        idioma=idioma,
        valor=valor,
        estado=estado,
        user_id=user_id
    )
    
    # Añadir el nuevo ambito a la base de datos
    db.session.add(nuevo_ambito)
    db.session.commit()

    # Serializar y devolver el nuevo ambito
    return jsonify(ambitos_schema.dump(nuevo_ambito)), 201
except Exception as e:
    db.session.rollback()
    return jsonify({"error": str(e)}), 500

# Obtener todos los ambitos
@ambito.route('/social-media-publicaciones-ambitos', methods=['GET'])
def obtener_ambitos():
    try:
        # Obtener todos los ambitos de la base de datos
        ambitos = Ambitos.query.all()

        # Serializar los ambitos
        return jsonify(ambitos_schemas.dump(ambitos)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Obtener un ambito por su ID
@ambito.route('/social-media-publicaciones-ambitos/<int:id>', methods=['GET'])
def obtener_ambito(id):
try:
    # Buscar el ambito por su ID
    ambito = Ambitos.query.get(id)

    # Verificar si el ambito existe
    if ambito:
        return jsonify(ambitos_schema.dump(ambito)), 200
    else:
        return jsonify({"error": "Ambito no encontrado"}), 404
except Exception as e:
    return jsonify({"error": str(e)}), 500

# Actualizar un ambito por su ID
@ambito.route('/social-media-publicaciones-ambitos/<int:id>', methods=['PUT'])
def actualizar_ambito(id):
try:
    # Obtener el ambito existente
    ambito = Ambitos.query.get(id)

    # Verificar si el ambito existe
    if not ambito:
        return jsonify({"error": "Ambito no encontrado"}), 404

    # Obtener los datos del cuerpo de la solicitud
    data = request.get_json()

    # Actualizar los campos del ambito
    ambito.nombre = data.get('nombre', ambito.nombre)
    ambito.descripcion = data.get('descripcion', ambito.descripcion)
    ambito.idioma = data.get('idioma', ambito.idioma)
    ambito.valor = data.get('valor', ambito.valor)
    ambito.estado = data.get('estado', ambito.estado)
    ambito.user_id = data.get('user_id', ambito.user_id)

    # Guardar los cambios en la base de datos
    db.session.commit()

    # Serializar y devolver el ambito actualizado
    return jsonify(ambitos_schema.dump(ambito)), 200
except Exception as e:
    db.session.rollback()
    return jsonify({"error": str(e)}), 500

# Eliminar un ambito por su ID
@ambito.route('/social-media-publicaciones-ambitos/<int:id>', methods=['DELETE'])
def eliminar_ambito(id):
try:
    # Buscar el ambito por su ID
    ambito = Ambitos.query.get(id)

    # Verificar si el ambito existe
    if not ambito:
        return jsonify({"error": "Ambito no encontrado"}), 404

    # Eliminar el ambito de la base de datos
    db.session.delete(ambito)
    db.session.commit()

    return jsonify({"message": "Ambito eliminado exitosamente"}), 200
except Exception as e:
    db.session.rollback()
    return jsonify({"error": str(e)}), 500
