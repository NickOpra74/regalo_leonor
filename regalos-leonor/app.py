from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from functools import wraps
import os

from storage import crear_store, limpiar_carta

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

