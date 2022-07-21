from flask import Flask,render_template,url_for, request,jsonify,session,flash,redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.utils import append_slash_redirect
from cryptography.fernet import Fernet
# from crypto_key import key
from datetime import datetime
# from flask_mail import Mail, Message

#Crypto key
# f = Fernet(key())


#inisialisasi
app = Flask(__name__)
app.secret_key = '069420'

#Koneksi, inisialisasi DB
# app.config['MYSQL_HOST'] = f"mysql + mysqldb://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?unix_socket =/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}"
app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bri-minder'
mysql = MySQL(app)

@app.route('/', methods=['POST', 'GET'])
def function():
    if not 'loggedin' in session:
        return redirect('/login')
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET','POST'])
def login():
    if not 'loggedin' in session:
        msg = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            # Create variables for easy access
            username = request.form['username']
            password = request.form['password']
            # Check if account exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM user WHERE username = %s AND password = %s', (username, password,))
            # Fetch one record and return result
            account = cursor.fetchone()
            # If account exists in accounts table in out database
            if account:
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['nama'] = account['nama']
                session['username'] = account['username']
                # Redirect to home page
                return 'Logged in successfully!'
            else:
                msg = 'Invalid username or password!'
                
        return render_template('login.html', msg=msg)
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('beranda.html')
    return redirect('/login')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)