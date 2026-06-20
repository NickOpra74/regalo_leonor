from flask import Flask, render_template, jsonify, request, session
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'leonor-regalo-secreto-2025')

PASSWORD = "01/12/2025"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/almanaque')
def almanaque():
    return render_template('almanaque.html')

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    if data and data.get('password') == PASSWORD:
        session['authenticated'] = True
        return jsonify({'success': True})
    return jsonify({'success': False}), 401

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
