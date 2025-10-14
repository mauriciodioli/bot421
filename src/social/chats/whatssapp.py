# routes/codigos_postales.py
from flask import Blueprint, render_template, request, jsonify, current_app
from utils.db_session import get_db_session
from models.codigoPostal import CodigoPostal
from models.publicaciones.ambitos import Ambitos
from models.publicaciones.ambito_codigo_postal import AmbitoCodigoPostal
from models.publicaciones.ambitoCategoria import AmbitoCategoria
from models.publicaciones.categoriaCodigoPostal import CategoriaCodigoPostal

from models.chats.contacto import Contacto

from sqlalchemy.exc import IntegrityError
import re

whatssapp = Blueprint('whatssapp', __name__)  # si ya existe así en otros lados, mantenelo

# --- Página (vista) -----------------------------------------------------------
@whatssapp.route('/social-chats-whatssapp/', methods=['GET'])
def pagina_chats_whatssapp():
    with get_db_session() as session:
        datos = session.query(CodigoPostal).order_by(CodigoPostal.id.asc()).all()
        return render_template('media/whatssapp.html', datos=datos, layout='layout_administracion')

# --- Helpers -----------------------------------------------------------------
def _validate_e164(valor: str) -> str:
    v = (valor or "").strip().replace(" ", "")
    if not re.fullmatch(r"\+\d{8,}", v):
        raise ValueError("Número en formato internacional (+E.164), ej: +393445977100")
    return v

# --- Listar ------------------------------------------------------------------
@whatssapp.route('/social-chats-whatssapp/whatsapp', methods=['GET'])
def whatsapp_list():
    user_id        = request.args.get('user_id', type=int)
    publicacion_id = request.args.get('publicacion_id', type=int)
    is_active      = request.args.get('is_active', default=1, type=int)

    with get_db_session() as session:
        q = session.query(Contacto).filter(Contacto.tipo == 'whatsapp')
        if user_id is not None:
            q = q.filter(Contacto.user_id == user_id)
        if publicacion_id is not None:
            q = q.filter(Contacto.publicacion_id == publicacion_id)
        if is_active in (0, 1):
            q = q.filter(Contacto.is_active == bool(is_active))
        items = q.order_by(Contacto.is_primary.desc(), Contacto.id.desc()).all()
        return jsonify(contacts_schema.dump(items)), 200




# --- Create -------------------------------------------------------------
@whatssapp.route('/social-chats-whatssapp/whatsapp', methods=['POST'])
def whatsapp_create():
    data = request.get_json(force=True) or {}
    try:
        user_id = int(data['user_id'])
        valor   = _validate_e164(data['valor'])

        # Normalizar opcionales: '' -> None
        def _opt_int(v):
            if v is None: return None
            if isinstance(v, str) and v.strip() == '': return None
            return int(v)

        publicacion_id   = _opt_int(data.get('publicacion_id'))
        ambito_id    = _opt_int(data.get('ambito_rel_id'))
        categoria_id = _opt_int(data.get('categoria_rel_id'))
        codigo_postal_id = _opt_int(data.get('codigo_postal_id'))
        is_primary       = bool(data.get('is_primary', False))

        with get_db_session() as session:
            if is_primary:
                q = session.query(Contacto).filter(
                    Contacto.user_id == user_id,
                    Contacto.tipo == 'whatsapp',
                )
                if publicacion_id is None:
                    q = q.filter(Contacto.publicacion_id.is_(None))
                else:
                    q = q.filter(Contacto.publicacion_id == publicacion_id)

                q.update({'is_primary': False}, synchronize_session=False)

            nuevo = Contacto(
                user_id=user_id,
                publicacion_id=publicacion_id,
                tipo='whatsapp',
                valor=valor,
                is_primary=is_primary,
                is_active=True,
                ambito_id=ambito_id,
                categoria_id=categoria_id,
                codigo_postal_id=codigo_postal_id,
            )
            session.add(nuevo)
            session.flush()  # obtener ID para la respuesta

            # ✅ Sin Marshmallow: respondemos dict “a mano”
            resp = {
                "id": nuevo.id,
                "user_id": nuevo.user_id,
                "publicacion_id": nuevo.publicacion_id,
                "tipo": nuevo.tipo,
                "valor": nuevo.valor,
                "codigo_postal_id": nuevo.codigo_postal_id,
                "ambito_id": nuevo.ambito_id,
                "categoria_id": nuevo.categoria_id,
                "is_primary": nuevo.is_primary,
                "is_active": nuevo.is_active,
                "created_at": nuevo.created_at.isoformat() if nuevo.created_at else None,
                "updated_at": nuevo.updated_at.isoformat() if nuevo.updated_at else None,
            }
            return jsonify(resp), 201

    except (KeyError, ValueError) as e:
        return jsonify({'error': str(e)}), 400
    except IntegrityError:
        return jsonify({'error': 'Duplicado para ese contexto'}), 409
    except Exception:
        current_app.logger.exception('whatsapp_create error')
        return jsonify({'error': 'Error interno'}), 500


# --- Obtener uno -------------------------------------------------------------
@whatssapp.route('/social-chats-whatssapp/whatsapp/<int:contact_id>', methods=['GET'])
def whatsapp_get(contact_id: int):
    with get_db_session() as session:
        c = session.get(Contacto, contact_id)
        if not c or c.tipo != 'whatsapp':
            return jsonify({'error': 'No encontrado'}), 404
        return jsonify(contact_schema.dump(c)), 200

# --- Actualizar --------------------------------------------------------------
@whatssapp.route('/social-chats-whatssapp/whatsapp/<int:contact_id>', methods=['PUT', 'PATCH'])
def whatsapp_update(contact_id: int):
    data = request.get_json(force=True) or {}
    try:
        with get_db_session() as session:
            c = session.get(Contacto, contact_id)
            if not c or c.tipo != 'whatsapp':
                return jsonify({'error': 'No encontrado'}), 404

            if 'valor' in data:
                c.valor = _validate_e164(data['valor'])
            if 'is_active' in data:
                c.is_active = bool(data['is_active'])

            if 'is_primary' in data:
                make_primary = bool(data['is_primary'])
                if make_primary:
                    session.query(Contacto).filter(
                        Contacto.user_id == c.user_id,
                        Contacto.tipo == 'whatsapp',
                        Contacto.publicacion_id.is_(c.publicacion_id)
                    ).update({'is_primary': False})
                c.is_primary = make_primary

            session.commit()   # <- importante
            return jsonify(contact_schema.dump(c)), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except IntegrityError:
        return jsonify({'error': 'Duplicado para ese contexto'}), 409
    except Exception:
        current_app.logger.exception('whatsapp_update error')
        return jsonify({'error': 'Error interno'}), 500

# --- Borrar ------------------------------------------------------------------
@whatssapp.route('/social-chats-whatssapp/whatsapp/<int:contact_id>', methods=['DELETE'])
def whatsapp_delete(contact_id: int):
    try:
        with get_db_session() as session:
            c = session.get(Contacto, contact_id)
            if not c or c.tipo != 'whatsapp':
                return jsonify({'error': 'No encontrado'}), 404
            session.delete(c)
            session.commit()   # <- importante
            return jsonify({'ok': True}), 200
    except Exception:
        current_app.logger.exception('whatsapp_delete error')
        return jsonify({'error': 'Error interno'}), 500
