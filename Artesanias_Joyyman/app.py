from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura_joyyman'

# Función para conectar a la base de datos SQLite
def conectar_db():
    conn = sqlite3.connect('artesanias.db')
    conn.row_factory = sqlite3.Row
    return conn

# Crear la tabla de usuarios si no existe
def inicializar_db():
    conn = conectar_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            telefono TEXT UNIQUE NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Ruta principal (Página web)
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para registrar usuarios en la Base de Datos
@app.route('/registro', methods=['POST'])
def registro():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    telefono = request.form['telefono']
    correo = request.form['correo']
    password = request.form['password']
    
    # Encriptación robusta de la contraseña (Hashing seguro de Werkzeug)
    password_cifrada = generate_password_hash(password)

    try:
        conn = conectar_db()
        conn.execute('''
            INSERT INTO usuarios (nombre, apellido, telefono, correo, password)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, apellido, telefono, correo, password_cifrada))
        conn.commit()
        conn.close()
        flash('¡Cuenta creada exitosamente en la base de datos!', 'success')
    except sqlite3.IntegrityError:
        flash('El correo o el teléfono ya están registrados.', 'error')

    return redirect(url_for('index'))

# Ruta para iniciar sesión consultando la Base de Datos
@app.route('/login', methods=['POST'])
def login():
    identificador = request.form['identificador']
    password = request.form['password']

    conn = conectar_db()
    # Buscar por correo o por teléfono
    usuario = conn.execute('''
        SELECT * FROM usuarios WHERE correo = ? OR telefono = ?
    ''', (identificador, identificador)).fetchone()
    conn.close()

    if usuario and check_password_hash(usuario['password'], password):
        flash(f'¡Bienvenido de nuevo, {usuario["nombre"]}!', 'success')
    else:
        flash('Credenciales incorrectas o usuario no encontrado.', 'error')

    return redirect(url_for('index'))

if __name__ == '__main__':
    inicializar_db()
    app.run(debug=True)