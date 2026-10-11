from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from functools import wraps
import os

from storage import crear_store, limpiar_carta, CollectionStore
from werkzeug.utils import secure_filename
from datetime import datetime
from io import BytesIO

try:
    from pymongo import MongoClient
    import gridfs
except ImportError:
    MongoClient = None
    gridfs = None


# Carga el archivo .env si existe (solo para desarrollo local)
try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'leonor-regalo-secreto-2025')

PASSWORD = os.environ.get('APP_PASSWORD', "01/12/2025")

# Base de datos de las cartitas (MongoDB si hay MONGODB_URI, si no un JSON local)
store, aviso_store = crear_store()
items_uri = os.environ.get('MONGODB_URI', '').strip()
data_dir = os.path.join(os.path.dirname(__file__), 'data')
recuerdos_store = CollectionStore(items_uri, 'recuerdos', os.path.join(data_dir, 'recuerdos.json'))
planes_store = CollectionStore(items_uri, 'planes', os.path.join(data_dir, 'planes.json'))
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)
media_db = None
media_fs = None
if items_uri and MongoClient and gridfs:
    try:
        media_client = MongoClient(items_uri, serverSelectionTimeoutMS=8000, tz_aware=True)
        media_client.admin.command('ping')
        media_db = media_client[os.environ.get('MONGODB_DB', 'regalo_leonor')]
        media_fs = gridfs.GridFS(media_db)
        print('[recuerdos] Fotos conectadas a MongoDB GridFS ✔')
    except Exception as error:
        print(f'[recuerdos] AVISO: no se pudo conectar GridFS: {error}')
if aviso_store:
    print(f"[cartas] AVISO: {aviso_store}")
else:
    print("[cartas] Conectado a MongoDB Atlas ✔")


# ──────────────────────────────────────────────
#  PROTECCIÓN: solo con la contraseña se entra
# ──────────────────────────────────────────────
def login_requerido(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('authenticated'):
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'No autorizado'}), 401
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return wrapper


# ──────────────────────────────────────────────
#  PÁGINAS
# ──────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/menu')
@login_requerido
def menu():
    return render_template('menu.html')


@app.route('/almanaque')
@login_requerido
def almanaque():
    return render_template('almanaque.html')


@app.route('/tiempo')
@login_requerido
def tiempo():
    return render_template('tiempo.html')


@app.route('/planes')
@login_requerido
def planes():
    return render_template('planes.html')


@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json(silent=True)
    if data and data.get('password') == PASSWORD:
        session['authenticated'] = True
        session.permanent = True
        return jsonify({'success': True})
    return jsonify({'success': False}), 401


@app.route('/salir')
def salir():
    session.clear()
    return redirect(url_for('index'))


@app.route('/api/recuerdos', methods=['GET', 'POST'])
@login_requerido
def api_recuerdos():
    if request.method == 'GET':
        return jsonify({'success': True, 'recuerdos': recuerdos_store.listar()})
    foto = request.files.get('foto')
    fecha = (request.form.get('fecha') or '').strip()
    descripcion = (request.form.get('descripcion') or '').strip()
    if not foto or not fecha:
        return jsonify({'success': False, 'error': 'La foto y la fecha son obligatorias.'}), 400
    extension = os.path.splitext(secure_filename(foto.filename))[1].lower() or '.jpg'
    if media_fs is not None:
        file_id = media_fs.put(foto.stream.read(), filename=secure_filename(foto.filename) or f'recuerdo{extension}', content_type=foto.mimetype or 'image/jpeg')
        foto_url = url_for('media_file', file_id=str(file_id))
    else:
        nombre = f"{os.urandom(8).hex()}{extension}"
        foto.save(os.path.join(UPLOAD_DIR, nombre))
        foto_url = url_for('static', filename=f'uploads/{nombre}')
    item = recuerdos_store.crear({'foto': foto_url, 'fecha': fecha, 'descripcion': descripcion})
    return jsonify({'success': True, 'recuerdo': item}), 201


@app.route('/media/<file_id>')
def media_file(file_id):
    if media_fs is None:
        return jsonify({'error': 'Almacenamiento de fotos no disponible'}), 503
    try:
        from bson import ObjectId
        stored = media_fs.get(ObjectId(file_id))
    except Exception:
        return jsonify({'error': 'Foto no encontrada'}), 404
    return app.response_class(stored.read(), mimetype=stored.content_type or 'application/octet-stream')


@app.route('/api/planes', methods=['GET', 'POST'])
@login_requerido
def api_planes():
    if request.method == 'GET': return jsonify({'success': True, 'planes': planes_store.listar()})
    data = request.get_json(silent=True) or {}
    required = ('lugar', 'fecha', 'hora', 'estado')
    if any(not str(data.get(k, '')).strip() for k in required):
        return jsonify({'success': False, 'error': 'Completa lugar, fecha, hora y estado.'}), 400
    item = planes_store.crear({k: str(data[k]).strip() for k in (*required, 'nota')})
    return jsonify({'success': True, 'plan': item}), 201


@app.route('/api/planes/<plan_id>', methods=['PUT', 'DELETE'])
@login_requerido
def api_plan_detalle(plan_id):
    if request.method == 'DELETE': return jsonify({'success': planes_store.borrar(plan_id)})
    item = planes_store.actualizar(plan_id, request.get_json(silent=True) or {})
    return jsonify({'success': bool(item), 'plan': item}), (200 if item else 404)


# ──────────────────────────────────────────────
#  API DE CARTITAS
# ──────────────────────────────────────────────
@app.route('/api/cartas', methods=['GET'])
@login_requerido
def api_listar_cartas():
    return jsonify({'success': True, 'cartas': store.listar(), 'modo': store.modo})


@app.route('/api/cartas', methods=['POST'])
@login_requerido
def api_crear_carta():
    carta, error = limpiar_carta(request.get_json(silent=True))
    if error:
        return jsonify({'success': False, 'error': error}), 400
    try:
        creada = store.crear(carta)
    except Exception as e:  # noqa: BLE001
        return jsonify({'success': False, 'error': f'No se pudo guardar: {e}'}), 500
    return jsonify({'success': True, 'carta': creada}), 201


@app.route('/api/cartas/<carta_id>', methods=['PUT'])
@login_requerido
def api_editar_carta(carta_id):
    cambios, error = limpiar_carta(request.get_json(silent=True), parcial=True)
    if error:
        return jsonify({'success': False, 'error': error}), 400
    try:
        carta = store.actualizar(carta_id, cambios)
    except Exception as e:  # noqa: BLE001
        return jsonify({'success': False, 'error': f'No se pudo editar: {e}'}), 500
    if not carta:
        return jsonify({'success': False, 'error': 'Esa cartita ya no existe.'}), 404
    return jsonify({'success': True, 'carta': carta})


@app.route('/api/cartas/<carta_id>', methods=['DELETE'])
@login_requerido
def api_borrar_carta(carta_id):
    try:
        ok = store.borrar(carta_id)
    except Exception as e:  # noqa: BLE001
        return jsonify({'success': False, 'error': f'No se pudo borrar: {e}'}), 500
    if not ok:
        return jsonify({'success': False, 'error': 'Esa cartita ya no existe.'}), 404
    return jsonify({'success': True})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

