from flask import Flask, redirect, render_template, request, session, url_for
import sqlite3
import bcrypt
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  


def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password BLOB NOT NULL,
            gender TEXT,
            age INTEGER,
            location TEXT
        )
    ''')
    conn.commit()
    conn.close()



@app.route('/')
def home():
    return render_template('getstarted.html')

@app.route('/login')
def homee():
    return render_template('Login.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    gender = request.form.get('gender')
    age = request.form.get('age')
    location = request.form.get('location')

    if not all([username, email, password, gender, age, location]):
        return "Tous les champs sont requis.", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
    if cursor.fetchone():
        conn.close()
        return "Nom d'utilisateur ou email déjà utilisé.", 409

    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    
    cursor.execute("""
        INSERT INTO users (username, email, password, gender, age, location)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, email, hashed_password, gender, age, location))

    conn.commit()
    conn.close()
    return "Inscription réussie !", 201

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return "Tous les champs sont requis.", 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        session['username'] = user["username"]
        session['email'] = user["email"]
        return redirect(url_for('index'))
    else:
        return "Nom d'utilisateur ou mot de passe incorrect.", 401

@app.route('/index')
def index():
    username = session.get('username')
    if not username:
        return redirect(url_for('login_page'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return render_template('index.html',
                               username=user['username'],
                               email=user['email'],
                               age=user['age'],
                               location=user['location'],
                               gender=user['gender'])
    else:
        return "Utilisateur non trouvé", 404


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
