import os
import sqlite3
import subprocess
import requests
from flask import Flask, request, session, g, render_template, redirect, url_for, make_response

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')

def get_db():
    if not hasattr(g, 'db'):
        g.db = sqlite3.connect('database.db')
        g.db.row_factory = sqlite3.Row
        create_tables()
    return g.db

def create_tables():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS memos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, content TEXT)''')
    conn.commit()
    conn.close()

@app.teardown_appcontext
def close_db(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = get_db()
        cursor = db.cursor()
        query = "SELECT * FROM users WHERE username = '{}' AND password = '{}'".format(username, password)
        cursor.execute(query)
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            return redirect(url_for('profile'))
        else:
            return render_template('login.html', error="Login failed")
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'user_id' in session:
        user_id = session['user_id']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT username FROM users WHERE id = {}".format(user_id))
        user = cursor.fetchone()
        if user:
            response = make_response(f"<h2>Hello, " + user['username'] + "!</h2>")
            return response
        else:
            return redirect(url_for('login'))
    return redirect(url_for('login'))

@app.route('/fetch')
def fetch():
    url = request.args.get('url')
    if url:
        try:
            response = requests.get(url)
            return render_template('fetch.html', content=response.content.decode())
        except Exception as e:
            return str(e)
    else:
        return "Please provide a URL"

@app.route('/ping')
def ping():
    ip = request.args.get('ip', '8.8.8.8')
    try:
        result = subprocess.check_output(f"ping -c 1 {ip}", shell=True, stderr=subprocess.STDOUT)
        return render_template('ping.html', ip=ip, result=result.decode())
    except subprocess.CalledProcessError as e:
        return f"Error executing ping: {e.output.decode()}"

@app.route('/view')
def view():
    filename = request.args.get('file')
    if filename:
        try:
            with open(filename, 'r') as f:
                content = f.read()
            return render_template('view.html', content=content)
        except Exception as e:
            return str(e)
    else:
        return "Please provide a file name"

@app.route('/memo', methods=['GET', 'POST'])
def memo():
    if 'user_id' in session:
        user_id = session['user_id']
        db = get_db()
        cursor = db.cursor()
        if request.method == 'POST':
            content = request.form.get('content')
            cursor.execute("INSERT INTO memos (user_id, content) VALUES (?, ?)", (user_id, content))
            db.commit()
            return redirect(url_for('memo'))
        else:
            cursor.execute("SELECT content FROM memos WHERE user_id = ?", (user_id,))
            memos = cursor.fetchall()
            return render_template('memo.html', memos=memos)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        db.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
