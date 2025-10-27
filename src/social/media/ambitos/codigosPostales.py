# routes/codigos_postales.py
from flask import Blueprint, render_template, request, jsonify, current_app
from utils.db import db
from utils.db_session import get_db_session
from models.codigoPostal import codigo_postal_schema
from models.codigoPostal import codigos_postales_schema

from models.publicaciones.ambitos import Ambitos
from models.publicaciones.ambito_codigo_postal import AmbitoCodigoPostal
 
from models.codigoPostal import CodigoPostal
from models.publicaciones.ambitoCategoria import AmbitoCategoria
from models.publicaciones.categoriaCodigoPostal import CategoriaCodigoPostal


codigosPostales = Blueprint('codigosPostales', __name__)

@codigosPostales.route('/social-media-ambitos-codigosPostales/', methods=['GET'])
def pagina_codigos_postales():
    with get_db_session() as session:
        datos = session.query(CodigoPostal)\
                       .order_by(CodigoPostal.id.asc()).all()
        cps = [
            {"id": r.id, "codigoPostal": r.codigoPostal, "ciudad": r.ciudad, "pais": r.pais}
            for r in datos
        ]
        # Si usás relaciones, cargalas en caliente aquí (selectinload / joinedload)
        return render_template(
            'media/publicaciones/ambitos/codigosPostales.html',
            datos=cps,
            layout='layout_administracion'
        )


# ---- API CRUD ----
@codigosPostales.route('/api/codigos-postales', methods=['GET'])
def api_listar_cp():
    with get_db_session() as session:
        cps = session.query(CodigoPostal).all()
    return jsonify(codigos_postales_schema.dump(cps))





@codigosPostales.route('/social-media-ambitos-codigosPostales-listar/', methods=['POST'])
def listar_cp_filtrado():
    data = request.get_json(silent=True) or {}
    pais   = (data.get('pais') or '').strip()
    idioma = (data.get('idioma') or '').strip()  # hoy no se usa; se acepta por firma

    try:
       with get_db_session() as session: 
            q = session.query(CodigoPostal)
            if pais:
                q = q.filter(CodigoPostal.pais == pais)  # si querés ilike, cambialo según tu DB

            cps = q.order_by(CodigoPostal.codigoPostal.asc()).all()
            data = [{
                'id': cp.id,
                'codigoPostal': cp.codigoPostal,
                'ciudad': cp.ciudad,
                'pais': cp.pais
            } for cp in cps]

       return jsonify({'ok': True, 'data': data})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@codigosPostales.route('/social-media-ambitos-codigosPostales-crear/', methods=['POST'])
def api_crear_cp():
    data = request.get_json(silent=True) or {}
    codigo = (data.get('codigoPostal') or '').strip()
    ciudad = (data.get('ciudad') or '').strip() or None
    pais   = (data.get('pais') or '').strip() or None
    if not codigo:
        return jsonify({'ok': False, 'error': 'codigoPostal requerido'}), 400

    try:
        with get_db_session() as session:
            existe = session.query(CodigoPostal).filter_by(codigoPostal=codigo).first()
            if existe:
                return jsonify({'ok': False, 'error': 'codigoPostal duplicado'}), 409
            cp = CodigoPostal(codigoPostal=codigo, ciudad=ciudad, pais=pais)
            session.add(cp)
            session.flush()
            return jsonify({'ok': True, 'data': codigo_postal_schema.dump(cp)}), 201
    except Exception as e:
        current_app.logger.exception("crear CP")
        return jsonify({'ok': False, 'error': str(e)}), 500

@codigosPostales.route('/api/codigos-postales/<int:cp_id>', methods=['PUT'])
def api_actualizar_cp(cp_id):
    data = request.get_json(silent=True) or {}
    try:
        with get_db_session() as session:
            cp = session.get(CodigoPostal, cp_id)
            if not cp:
                return jsonify({'ok': False, 'error': 'no existe'}), 404
            # actualiza si vienen
            if 'codigoPostal' in data:
                nuevo = (data['codigoPostal'] or '').strip()
                if not nuevo:
                    return jsonify({'ok': False, 'error': 'codigoPostal vacío'}), 400
                # check duplicado
                dup = session.query(CodigoPostal).filter(
                    CodigoPostal.codigoPostal == nuevo,
                    CodigoPostal.id != cp_id
                ).first()
                if dup:
                    return jsonify({'ok': False, 'error': 'codigoPostal duplicado'}), 409
                cp.codigoPostal = nuevo
            if 'ciudad' in data: cp.ciudad = (data['ciudad'] or '').strip() or None
            if 'pais'   in data: cp.pais   = (data['pais'] or '').strip() or None
            session.flush()
            return jsonify({'ok': True, 'data': codigo_postal_schema.dump(cp)})
    except Exception as e:
        current_app.logger.exception("actualizar CP")
        return jsonify({'ok': False, 'error': str(e)}), 500

@codigosPostales.route('/api/codigos-postales/<int:cp_id>', methods=['DELETE'])
def api_eliminar_cp(cp_id):
    try:
        with get_db_session() as session:
            cp = session.get(CodigoPostal, cp_id)
            if not cp:
                return jsonify({'ok': False, 'error': 'no existe'}), 404
            session.delete(cp)
            return jsonify({'ok': True})
    except Exception as e:
        current_app.logger.exception("eliminar CP")
        return jsonify({'ok': False, 'error': str(e)}), 500

# ---- Asignación Ambitos <-> CP (opcional) ----
@codigosPostales.route('/api/codigos-postales/<int:cp_id>/ambitos', methods=['GET'])
def api_ambitos_de_cp(cp_id):
    
    with get_db_session() as session:
        cp = session.get(CodigoPostal, cp_id)
        if not cp: return jsonify({'ok': False, 'error': 'no existe'}), 404
        items = (session.query(Ambitos)
                .join(AmbitoCodigoPostal, AmbitoCodigoPostal.ambito_id == Ambitos.id)
                .filter(AmbitoCodigoPostal.codigo_postal_id == cp_id)
                .all())
    return jsonify([{'id': a.id, 'nombre': a.nombre, 'valor': a.valor} for a in items])

@codigosPostales.route('/api/codigos-postales/<int:cp_id>/ambitos', methods=['POST'])
def api_asignar_ambito_a_cp(cp_id):
    data = request.get_json(silent=True) or {}
    ambito_id = data.get('ambito_id')
    if not ambito_id:
        return jsonify({'ok': False, 'error': 'ambito_id requerido'}), 400
    try:
        with get_db_session() as session:
            cp = session.get(CodigoPostal, cp_id)
            amb = session.get(Ambitos, ambito_id)
            if not cp or not amb:
                return jsonify({'ok': False, 'error': 'CP o Ambito inexistente'}), 404
            ya = session.query(AmbitoCodigoPostal).filter_by(
                codigo_postal_id=cp_id, ambito_id=ambito_id
            ).first()
            if ya:
                return jsonify({'ok': True, 'msg': 'ya estaba asignado'})
            rel = AmbitoCodigoPostal(codigo_postal_id=cp_id, ambito_id=ambito_id)
            session.add(rel)
            return jsonify({'ok': True})
    except Exception as e:
        current_app.logger.exception("asignar ambito a cp")
        return jsonify({'ok': False, 'error': str(e)}), 500

@codigosPostales.route('/api/codigos-postales/<int:cp_id>/ambitos/<int:ambito_id>', methods=['DELETE'])
def api_desasignar_ambito_de_cp(cp_id, ambito_id):
    try:
        with get_db_session() as session:
            rel = session.query(AmbitoCodigoPostal).filter_by(
                codigo_postal_id=cp_id, ambito_id=ambito_id
            ).first()
            if not rel:
                return jsonify({'ok': False, 'error': 'relación no existe'}), 404
            session.delete(rel)
            return jsonify({'ok': True})
    except Exception as e:
        current_app.logger.exception("desasignar ambito de cp")
        return jsonify({'ok': False, 'error': str(e)}), 500












@codigosPostales.route('/social-media-ambitos-codigosPostales-asignar-CP-categoria/', methods=['POST'])
def api_asignar_categoria_a_cp():
    from flask import request, jsonify, current_app
    data = request.get_json(silent=True) or {}

    categoria_id = data.get('ambito_categoria_id') or data.get('categoria_id')
    cp_ids = data.get('codigo_postal_ids') or data.get('cp_ids') or []

    if not categoria_id:
        return jsonify({'ok': False, 'error': 'ambito_categoria_id requerido'}), 400
    if not isinstance(cp_ids, list) or not cp_ids:
        return jsonify({'ok': False, 'error': 'codigo_postal_ids debe ser lista no vacía'}), 400

    try:
        categoria_id = int(categoria_id)
        cp_ids = [int(x) for x in cp_ids]
    except Exception:
        return jsonify({'ok': False, 'error': 'IDs inválidos'}), 400

    try:
        added = 0
        skipped = 0
        invalid = 0

        with get_db_session() as session:
            cat = session.get(AmbitoCategoria, categoria_id)
            if not cat:
                return jsonify({'ok': False, 'error': 'Categoría inexistente'}), 404

            # CP válidos existentes
            valid_cp_ids = {row[0] for row in session.query(CodigoPostal.id).filter(CodigoPostal.id.in_(cp_ids)).all()}
            existentes = {
                row[0] for row in session.query(CategoriaCodigoPostal.codigo_postal_id)
                .filter(CategoriaCodigoPostal.categoria_id == categoria_id).all()
            }

            for cp_id in cp_ids:
                if cp_id not in valid_cp_ids:
                    invalid += 1
                    continue
                if cp_id in existentes:
                    skipped += 1
                    continue
                session.add(CategoriaCodigoPostal(
                    codigo_postal_id=cp_id,
                    categoria_id=categoria_id  # FK a ambitoCategoria.id
                ))
                added += 1

        return jsonify({'ok': True, 'added': added, 'skipped': skipped, 'invalid': invalid})
    except Exception as e:
        current_app.logger.exception("asignar categoria a cp")
        return jsonify({'ok': False, 'error': str(e)}), 500
    
    
    
    
    
    
    
    
    
    
@codigosPostales.route('/social-media-ambitos-codigosPostales-listar-CP-de-categoria/', methods=['POST'])
def listar_cp_de_categoria():
    data = request.get_json(silent=True) or {}
    categoria_id = data.get('ambito_categoria_id') or data.get('categoria_id')
    if not categoria_id:
        return jsonify({'ok': False, 'error': 'ambito_categoria_id requerido'}), 400

    try:
        categoria_id = int(categoria_id)
    except Exception:
        return jsonify({'ok': False, 'error': 'ID inválido'}), 400

    try:
        with get_db_session() as session:
            # Verificar que la categoría exista (opcional pero sano)
            if not session.get(AmbitoCategoria, categoria_id):
                return jsonify({'ok': False, 'error': 'Categoría inexistente'}), 404

            filas = (session.query(CodigoPostal)
                     .join(CategoriaCodigoPostal, CategoriaCodigoPostal.codigo_postal_id == CodigoPostal.id)
                     .filter(CategoriaCodigoPostal.categoria_id == categoria_id)
                     .order_by(CodigoPostal.codigoPostal.asc())
                     .all())

            data = [{
                'id': cp.id,
                'codigoPostal': cp.codigoPostal,
                'ciudad': cp.ciudad,
                'pais': cp.pais
            } for cp in filas]

            return jsonify({'ok': True, 'data': data})
    except Exception as e:
        current_app.logger.exception('listar_cp_de_categoria')
        return jsonify({'ok': False, 'error': str(e)}), 500
    
    
    
    
@codigosPostales.route('/social-media-ambitos-codigosPostales-quitar-CP-categoria/', methods=['POST'])
def quitar_cp_de_categoria():
    data = request.get_json(silent=True) or {}
    categoria_id = data.get('ambito_categoria_id') or data.get('categoria_id')
    cp_ids = data.get('codigo_postal_ids') or data.get('cp_ids') or []

    if not categoria_id:
        return jsonify({'ok': False, 'error': 'ambito_categoria_id requerido'}), 400
    if not isinstance(cp_ids, list) or not cp_ids:
        return jsonify({'ok': False, 'error': 'codigo_postal_ids debe ser lista no vacía'}), 400

    try:
        categoria_id = int(categoria_id)
        cp_ids = [int(x) for x in cp_ids]
    except Exception:
        return jsonify({'ok': False, 'error': 'IDs inválidos'}), 400

    try:
        removed = 0
        with get_db_session() as session:
            q = (session.query(CategoriaCodigoPostal)
                 .filter(CategoriaCodigoPostal.categoria_id == categoria_id)
                 .filter(CategoriaCodigoPostal.codigo_postal_id.in_(cp_ids)))
            rows = q.all()
            for r in rows:
                session.delete(r)
                removed += 1
        return jsonify({'ok': True, 'removed': removed, 'not_found': len(cp_ids) - removed})
    except Exception as e:
        current_app.logger.exception('quitar_cp_de_categoria')
        return jsonify({'ok': False, 'error': str(e)}), 500