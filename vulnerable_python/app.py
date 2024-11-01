import os
import shlex
import sqlite3
import subprocess
import requests
from flask import Flask, request, session, g, render_template, redirect, url_for, make_response
from markupsafe import Markup, escape
from urllib.parse import urlparse
import ipaddress
import bleach

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
        # query = "SELECT * FROM users WHERE username = '{}' AND password = '{}'".format(username, password)
        # cursor.execute(query)

        # Secured Query
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        cursor.execute(query, (username, password))
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
        # cursor.execute("SELECT username FROM users WHERE id = {}".format(user_id))
        query = "SELECT username FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))

        user = cursor.fetchone()
        if user:
            # XSS vulnerability
            #response = make_response(f"<h2>Hello, " + user['username'] + "!</h2>")
            response = render_template('profile.html', username=user['username'])
            return response
        else:
            return redirect(url_for('login'))
    return redirect(url_for('login'))

#SSRF 방어
def is_safe_url(url):
    if not url:
        return False
        
    URL_WHITELIST = ['example.com']
    try:
        parsed_url = urlparse(url)
        # 스키마 검사 추가
        if parsed_url.scheme not in ['http', 'https']:
            return False
        # 포트 검사 추가    
        if parsed_url.port and parsed_url.port not in [80, 443]:
            return False
        # IP 주소 형태의 호스트네임 차단
        try:
            ipaddress.ip_address(parsed_url.hostname)
            return False
        except ValueError:
            pass
        # 화이트리스트 검사    
        return parsed_url.hostname in URL_WHITELIST
    except Exception:
        return False

@app.route('/fetch')
def fetch():
    url = request.args.get('url')

    if not is_safe_url(url):
        return "Invalid or unsafe URL"
    try:
            # XSS 방어 (escape 처리)
            escaped_url = escape(url)
            response = requests.get(escaped_url)
            content = response.content.decode()
            # HTML 태그를 이스케이프 처리하여 텍스트로 표시
            escaped_content = escape(content)
            # Markup으로 감싸서 안전한 HTML로 렌더링
            safe_content = Markup(escaped_content)
            
            return render_template('fetch.html', content=safe_content)
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

#SSRF 방어
def is_safe_ip(ip):
    try:
        return not ip.is_private and not ip.is_loopback
    except ValueError:
        return False
    
@app.route('/ping')
def ping():
    # XSS 방어 (escape 처리)
    ip = escape(request.args.get('ip', '8.8.8.8'))
    ip_obj = ipaddress.ip_address(ip)
    if is_safe_ip(ip_obj):
        try:
            
            quoted_ip = shlex.quote(str(ip_obj))
            result = subprocess.check_output(f"ping -c 1 {quoted_ip}", shell=True, stderr=subprocess.STDOUT)
            return render_template('ping.html', ip=quoted_ip, result=result.decode())
        except subprocess.CalledProcessError as e:
            return f"Error executing ping: {e.output.decode()}"
    else:
        return "Invalid IP address"

#LFI 방어(Directory Traversal)
def is_safe_file(filename):
    DIRECTORY = os.getcwd()
    safe_path = os.path.join(DIRECTORY, filename)
    return filename.endswith('.txt') and os.path.isfile(safe_path) and os.path.commonpath([DIRECTORY, safe_path]) == DIRECTORY

@app.route('/view')
def view():
    filename = request.args.get('file')
    if filename:
        # LFI 방어
        if is_safe_file(filename):
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
            # XSS 방어 (script 방지.)
            escaped_content = escape(content)
            # escaped_content = escape(content)
            cursor.execute("INSERT INTO memos (user_id, content) VALUES (?, ?)", (user_id,escaped_content))
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
