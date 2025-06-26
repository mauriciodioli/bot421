<<<<<<< HEAD
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


ambito = Blueprint('ambito', __name__)



@ambito.route('/social-media-ambitos-ambitos/')
def social_media_ambitos_ambitos():
    try:      
          # Obtener el valor de la cookie "language"
        idioma = request.cookies.get('language', 'in')  # Por defecto "in" si no se encuentra la cookie
        datos = db.session.query(Ambitos).filter_by(idioma=idioma).all()
       
        accion = 'crear'
        
        return render_template('media/publicaciones/ambitos/ambitos.html', 
                               datos=datos, 
                               layout='layout_administracion', 
                               accion=accion)
    except Exception as e:
        print(f'Error al obtener los ámbitos: {e}')
        return 'Problemas con la base de datos', 500
    finally:
        db.session.close()




# Crear un nuevo Ambito
@ambito.route('/social-media-publicaciones-ambitos-crear/', methods=['POST'])
def crear_ambito():
    try:
        # Obtener los datos del cuerpo de la solicitud
        data = request.get_json()

        # Extraer datos necesarios para crear un nuevo ámbito
        nombre = data.get('nombre')
        descripcion = data.get('descripcion')
        idioma = data.get('idioma', None)
        valor = data.get('valor', None)
        estado = data.get('estado', None)
        user_id = data.get('user_id')        
        user_id = int(user_id)

        # Validar campos obligatorios
        if not nombre or not descripcion or not user_id:
            return jsonify({"error": "Los campos 'nombre', 'descripcion' y 'user_id' son obligatorios"}), 400

        # Validar que el user_id exista
        user = db.session.query(Usuario).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "El user_id proporcionado no existe"}), 400

        # Comprobar si ya existe el ámbito con el mismo nombre y valor en el idioma especificado
        existing_ambito = db.session.query(Ambitos).filter_by(nombre=nombre, valor=valor, idioma=idioma).first()
        if not existing_ambito:
            # Crear el nuevo ámbito
            nuevo_ambito = Ambitos(
                nombre=nombre,
                descripcion=descripcion,
                idioma=idioma,
                valor=valor,
                estado=estado
            )
            db.session.add(nuevo_ambito)
            db.session.commit()  # Se requiere para obtener el ID asignado automáticamente

            # Crear la relación en Ambito_usuario
            ambito_usuario = Ambito_usuario(
                ambito_id=int(nuevo_ambito.id),  # Usamos el ID generado
                publicacion_id=None,
                user_id=user_id,  # Usamos el ID proporcionado en la solicitud user_id,
                estado=1
            )
            db.session.add(ambito_usuario)
            db.session.commit()

            # Cerrar la sesión explícitamente
            db.session.close()

            # Serializar y devolver el nuevo ámbito
            resultado = serializar_ambito(nuevo_ambito)
            return jsonify(resultado), 201
        else:
            print(f"El ámbito con nombre '{nombre}' y valor '{valor}' ya existe en el idioma '{idioma}'.")

    except Exception as e:
        db.session.rollback()  # Deshacer cualquier cambio en caso de error
        db.session.close()  # Asegurarse de cerrar la sesión en caso de error también
        return jsonify({"error": str(e)}), 500


@ambito.route('/social-media-publicaciones-ambitos-obtener-informe/', methods=['GET'])
def informe_ambito():
    return render_template('ambitos/informe_ambitos.html', layout='layout_administracion')

# Obtener todos los ambitos
@ambito.route('/social-media-publicaciones-obtener-ambitos/', methods=['GET'])
def obtener_ambitos():
    try:
        # Obtener el valor de la cookie "language"
        idioma = request.cookies.get('language', 'in')  # Por defecto "in" si no se encuentra la cookie

        # Consultar los ambitos según el idioma
        ambitos = db.session.query(Ambitos).filter_by(idioma=idioma, estado='ACTIVO').all()

        # Convertir los objetos a dicts serializables
        resultado = [
            {
                "id": ambito.id,
                "user_id": 'none',
                "nombre": ambito.nombre,
                "descripcion": ambito.descripcion,
                "idioma": ambito.idioma,
                "valor": ambito.valor,
                "estado": ambito.estado,
            }
            for ambito in ambitos
        ]
       
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.close()  # Asegura que la sesión se cierre correctamente




# Obtener un ambito por su ID
@ambito.route('/social-media-publicaciones-ambitos/<int:id>', methods=['GET'])
def obtener_ambito(id):
    try:
        # Buscar el ambito por su ID
        ambito = db.session.query(Ambitos).filter_by(id=id).first()
        resultado = serializar_ambito(ambito)
        db.session.close()

        # Verificar si el ambito existe
        if ambito:
            return jsonify(resultado), 200
        else:
            return jsonify({"error": "Ambito no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Actualizar un ambito por su ID
@ambito.route('/social-media-publicaciones-ambitos-actualizar/<int:id>', methods=['PUT'])
def actualizar_ambito(id):
    try:
        # Obtener el ambito existente
        ambito = db.session.query(Ambitos).filter_by(id=id).first() 

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
      
        # Guardar los cambios en la base de datos
        db.session.commit()
       
        # Verificar si el ambito existe
        resultado = serializar_ambito(ambito)
        db.session.close()
            # Devolver el resultado como JSON
        return jsonify(resultado), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Eliminar un ambito por su ID
@ambito.route('/social-media-publicaciones-ambitos-delete/<int:id>', methods=['DELETE'])
def eliminar_ambito(id):
    try:
        # Buscar el ámbito por su ID
        ambito = db.session.query(Ambitos).filter_by(id=id).first()

        # Verificar si el ámbito existe
        if not ambito:
            return jsonify({"error": "Ámbito no encontrado"}), 404

        # Buscar todos los registros en la tabla Ambito_usuario asociados al ámbito
        ambito_usuarios = db.session.query(Ambito_usuario).filter_by(ambito_id=id).all()

        # Eliminar los registros de Ambito_usuario asociados
        for ambito_usuario in ambito_usuarios:
            db.session.delete(ambito_usuario)

        # Eliminar el ámbito
        db.session.delete(ambito)

        # Confirmar los cambios en la base de datos
        db.session.commit()
        db.session.close()

        return jsonify({"message": "Ámbito y usuarios asociados eliminados exitosamente"}), 200
    except Exception as e:
        # Si ocurre un error, revertir los cambios pendientes
        db.session.rollback()
        return jsonify({"error": str(e)}), 500






@ambito.route('/social-media-publicaciones-ambitos-cambiarPosicion/<int:id_1>/<int:id_2>', methods=['PUT'])
def actualizar_cambiarPosicion(id_1, id_2):
    try:
            # Obtener los dos ámbitos existentes
            ambito_1 = db.session.query(Ambitos).filter_by(id=id_1).first()
            ambito_2 = db.session.query(Ambitos).filter_by(id=id_2).first()

            # Verificar si los ámbitos existen
            if not ambito_1 or not ambito_2:
                return jsonify({"error": "Uno o ambos ámbitos no encontrados"}), 404

            # 1. Almacenar los datos del id_1 en una variable
            datos_ambito_1 = {
                'nombre': ambito_1.nombre,
                'descripcion': ambito_1.descripcion,
                'idioma': ambito_1.idioma,
                'valor': ambito_1.valor,
                'estado': ambito_1.estado
            }

            # 2. Almacenar los datos del id_2 en una variable
            datos_ambito_2 = {
                'nombre': ambito_2.nombre,
                'descripcion': ambito_2.descripcion,
                'idioma': ambito_2.idioma,
                'valor': ambito_2.valor,
                'estado': ambito_2.estado
            }

            # 3. Cambiar los datos del registro id_1 por cualquier cosa (por ejemplo, valores vacíos)
            ambito_1.nombre = "Valor temporal"
            ambito_1.descripcion = "Valor temporal"
            ambito_1.idioma = "Valor temporal"
            ambito_1.valor = "Valor temporal"
            ambito_1.estado = "Valor temporal"

            # Guardar los cambios después de modificar el id_1
            db.session.commit()

            # 4. Colocar los datos almacenados del id_1 en el registro del id_2
            ambito_2.nombre = datos_ambito_1['nombre']
            ambito_2.descripcion = datos_ambito_1['descripcion']
            ambito_2.idioma = datos_ambito_1['idioma']
            ambito_2.valor = datos_ambito_1['valor']
            ambito_2.estado = datos_ambito_1['estado']

            # Guardar los cambios después de modificar el id_2
            db.session.commit()

            # 5. Colocar los datos almacenados del id_2 en el registro del id_1
            ambito_1.nombre = datos_ambito_2['nombre']
            ambito_1.descripcion = datos_ambito_2['descripcion']
            ambito_1.idioma = datos_ambito_2['idioma']
            ambito_1.valor = datos_ambito_2['valor']
            ambito_1.estado = datos_ambito_2['estado']

            # Guardar los cambios después de modificar el id_1
            db.session.commit()

            # Serializar los resultados
            resultado_1 = serializar_ambito(ambito_1)
            resultado_2 = serializar_ambito(ambito_2)

            db.session.close()

         
            # Devolver los resultados como JSON
            return jsonify({"ambito_1": resultado_1, "ambito_2": resultado_2}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500












def serializar_ambito(ambito):
    return {
        "id": ambito.id,
        "user_id": 'none',  # Asumiendo que no necesitas información de usuario en este caso
        "nombre": ambito.nombre,
        "descripcion": ambito.descripcion,
        "idioma": ambito.idioma,
        "valor": ambito.valor,
        "estado": ambito.estado,
=======
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


ambito = Blueprint('ambito', __name__)



@ambito.route('/social-media-ambitos-ambitos/')
def social_media_ambitos_ambitos():
    try:      
          # Obtener el valor de la cookie "language"
        idioma = request.cookies.get('language', 'in')  # Por defecto "in" si no se encuentra la cookie
        datos = db.session.query(Ambitos).filter_by(idioma=idioma).all()
       
        accion = 'crear'
        
        return render_template('media/publicaciones/ambitos/ambitos.html', 
                               datos=datos, 
                               layout='layout_administracion', 
                               accion=accion)
    except Exception as e:
        print(f'Error al obtener los ámbitos: {e}')
        return 'Problemas con la base de datos', 500
    finally:
        db.session.close()




# Crear un nuevo Ambito
@ambito.route('/social-media-publicaciones-ambitos-crear/', methods=['POST'])
def crear_ambito():
    try:
        # Obtener los datos del cuerpo de la solicitud
        data = request.get_json()

        # Extraer datos necesarios para crear un nuevo ámbito
        nombre = data.get('nombre')
        descripcion = data.get('descripcion')
        idioma = data.get('idioma', None)
        valor = data.get('valor', None)
        estado = data.get('estado', None)
        user_id = data.get('user_id')        
        user_id = int(user_id)

        # Validar campos obligatorios
        if not nombre or not descripcion or not user_id:
            return jsonify({"error": "Los campos 'nombre', 'descripcion' y 'user_id' son obligatorios"}), 400

        # Validar que el user_id exista
        user = db.session.query(Usuario).filter_by(id=user_id).first()
        if not user:
            return jsonify({"error": "El user_id proporcionado no existe"}), 400

        # Comprobar si ya existe el ámbito con el mismo nombre y valor en el idioma especificado
        existing_ambito = db.session.query(Ambitos).filter_by(nombre=nombre, valor=valor, idioma=idioma).first()
        if not existing_ambito:
            # Crear el nuevo ámbito
            nuevo_ambito = Ambitos(
                nombre=nombre,
                descripcion=descripcion,
                idioma=idioma,
                valor=valor,
                estado=estado
            )
            db.session.add(nuevo_ambito)
            db.session.commit()  # Se requiere para obtener el ID asignado automáticamente

            # Crear la relación en Ambito_usuario
            ambito_usuario = Ambito_usuario(
                ambito_id=int(nuevo_ambito.id),  # Usamos el ID generado
                publicacion_id=None,
                user_id=user_id,  # Usamos el ID proporcionado en la solicitud user_id,
                estado=1
            )
            db.session.add(ambito_usuario)
            db.session.commit()

            # Cerrar la sesión explícitamente
            db.session.close()

            # Serializar y devolver el nuevo ámbito
            resultado = serializar_ambito(nuevo_ambito)
            return jsonify(resultado), 201
        else:
            print(f"El ámbito con nombre '{nombre}' y valor '{valor}' ya existe en el idioma '{idioma}'.")

    except Exception as e:
        db.session.rollback()  # Deshacer cualquier cambio en caso de error
        db.session.close()  # Asegurarse de cerrar la sesión en caso de error también
        return jsonify({"error": str(e)}), 500


@ambito.route('/social-media-publicaciones-ambitos-obtener-informe/', methods=['GET'])
def informe_ambito():
    return render_template('ambitos/informe_ambitos.html', layout='layout_administracion')

# Obtener todos los ambitos
@ambito.route('/social-media-publicaciones-obtener-ambitos/', methods=['GET'])
def obtener_ambitos():
    try:
        # Obtener el valor de la cookie "language"
        idioma = request.cookies.get('language', 'in')  # Por defecto "in" si no se encuentra la cookie

        # Consultar los ambitos según el idioma
        ambitos = db.session.query(Ambitos).filter_by(idioma=idioma, estado='ACTIVO').all()

        # Convertir los objetos a dicts serializables
        resultado = [
            {
                "id": ambito.id,
                "user_id": 'none',
                "nombre": ambito.nombre,
                "descripcion": ambito.descripcion,
                "idioma": ambito.idioma,
                "valor": ambito.valor,
                "estado": ambito.estado,
            }
            for ambito in ambitos
        ]
       
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.close()  # Asegura que la sesión se cierre correctamente




# Obtener un ambito por su ID
@ambito.route('/social-media-publicaciones-ambitos/<int:id>', methods=['GET'])
def obtener_ambito(id):
    try:
        # Buscar el ambito por su ID
        ambito = db.session.query(Ambitos).filter_by(id=id).first()
        resultado = serializar_ambito(ambito)
        db.session.close()

        # Verificar si el ambito existe
        if ambito:
            return jsonify(resultado), 200
        else:
            return jsonify({"error": "Ambito no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Actualizar un ambito por su ID
@ambito.route('/social-media-publicaciones-ambitos-actualizar/<int:id>', methods=['PUT'])
def actualizar_ambito(id):
    try:
        # Obtener el ambito existente
        ambito = db.session.query(Ambitos).filter_by(id=id).first() 

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
      
        # Guardar los cambios en la base de datos
        db.session.commit()
       
        # Verificar si el ambito existe
        resultado = serializar_ambito(ambito)
        db.session.close()
            # Devolver el resultado como JSON
        return jsonify(resultado), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Eliminar un ambito por su ID
@ambito.route('/social-media-publicaciones-ambitos-delete/<int:id>', methods=['DELETE'])
def eliminar_ambito(id):
    try:
        # Buscar el ámbito por su ID
        ambito = db.session.query(Ambitos).filter_by(id=id).first()

        # Verificar si el ámbito existe
        if not ambito:
            return jsonify({"error": "Ámbito no encontrado"}), 404

        # Buscar todos los registros en la tabla Ambito_usuario asociados al ámbito
        ambito_usuarios = db.session.query(Ambito_usuario).filter_by(ambito_id=id).all()

        # Eliminar los registros de Ambito_usuario asociados
        for ambito_usuario in ambito_usuarios:
            db.session.delete(ambito_usuario)

        # Eliminar el ámbito
        db.session.delete(ambito)

        # Confirmar los cambios en la base de datos
        db.session.commit()
        db.session.close()

        return jsonify({"message": "Ámbito y usuarios asociados eliminados exitosamente"}), 200
    except Exception as e:
        # Si ocurre un error, revertir los cambios pendientes
        db.session.rollback()
        return jsonify({"error": str(e)}), 500






@ambito.route('/social-media-publicaciones-ambitos-cambiarPosicion/<int:id_1>/<int:id_2>', methods=['PUT'])
def actualizar_cambiarPosicion(id_1, id_2):
    try:
            # Obtener los dos ámbitos existentes
            ambito_1 = db.session.query(Ambitos).filter_by(id=id_1).first()
            ambito_2 = db.session.query(Ambitos).filter_by(id=id_2).first()

            # Verificar si los ámbitos existen
            if not ambito_1 or not ambito_2:
                return jsonify({"error": "Uno o ambos ámbitos no encontrados"}), 404

            # 1. Almacenar los datos del id_1 en una variable
            datos_ambito_1 = {
                'nombre': ambito_1.nombre,
                'descripcion': ambito_1.descripcion,
                'idioma': ambito_1.idioma,
                'valor': ambito_1.valor,
                'estado': ambito_1.estado
            }

            # 2. Almacenar los datos del id_2 en una variable
            datos_ambito_2 = {
                'nombre': ambito_2.nombre,
                'descripcion': ambito_2.descripcion,
                'idioma': ambito_2.idioma,
                'valor': ambito_2.valor,
                'estado': ambito_2.estado
            }

            # 3. Cambiar los datos del registro id_1 por cualquier cosa (por ejemplo, valores vacíos)
            ambito_1.nombre = "Valor temporal"
            ambito_1.descripcion = "Valor temporal"
            ambito_1.idioma = "Valor temporal"
            ambito_1.valor = "Valor temporal"
            ambito_1.estado = "Valor temporal"

            # Guardar los cambios después de modificar el id_1
            db.session.commit()

            # 4. Colocar los datos almacenados del id_1 en el registro del id_2
            ambito_2.nombre = datos_ambito_1['nombre']
            ambito_2.descripcion = datos_ambito_1['descripcion']
            ambito_2.idioma = datos_ambito_1['idioma']
            ambito_2.valor = datos_ambito_1['valor']
            ambito_2.estado = datos_ambito_1['estado']

            # Guardar los cambios después de modificar el id_2
            db.session.commit()

            # 5. Colocar los datos almacenados del id_2 en el registro del id_1
            ambito_1.nombre = datos_ambito_2['nombre']
            ambito_1.descripcion = datos_ambito_2['descripcion']
            ambito_1.idioma = datos_ambito_2['idioma']
            ambito_1.valor = datos_ambito_2['valor']
            ambito_1.estado = datos_ambito_2['estado']

            # Guardar los cambios después de modificar el id_1
            db.session.commit()

            # Serializar los resultados
            resultado_1 = serializar_ambito(ambito_1)
            resultado_2 = serializar_ambito(ambito_2)

            db.session.close()

         
            # Devolver los resultados como JSON
            return jsonify({"ambito_1": resultado_1, "ambito_2": resultado_2}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500












def serializar_ambito(ambito):
    return {
        "id": ambito.id,
        "user_id": 'none',  # Asumiendo que no necesitas información de usuario en este caso
        "nombre": ambito.nombre,
        "descripcion": ambito.descripcion,
        "idioma": ambito.idioma,
        "valor": ambito.valor,
        "estado": ambito.estado,
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
    }