from flask import Flask, request, session, redirect, url_for, render_template
from flaskext.mysql import MySQL
import pymysql 
import re 
 
app = Flask(__name__)
 
# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'cairocoders-ednalan'
 
mysql = MySQL()
   
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'bri-minder'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
 
# http://localhost:5000/pythonlogin/ - this will be the login page
@app.route('/login/', methods=['GET', 'POST'])
def login():
 # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM user WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        user = cursor.fetchone()
   
    # If account exists in accounts table in out database
        if user:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['nama'] = user['nama']
            session['username'] = user['username']
            # Redirect to home page
            #return 'Logged in successfully!'
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    
    return render_template('login.html', msg=msg)
 
# http://localhost:5000/register - this will be the registration page
@app.route('/registrasi', methods=['GET', 'POST'])
def registrasi():
 # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'nama' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        nama = request.form['nama']
        password = request.form['password']
   
  #Check if account exists using MySQL
        cursor.execute('SELECT * FROM user WHERE username = %s', (username))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not nama or not password:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO user VALUES (%s, %s, %s)', (username, nama, password)) 
            conn.commit()
   
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('registrasi.html', msg=msg)
  
# http://localhost:5000/home - this will be the home page, only accessible for loggedin users
@app.route('/beranda')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
   
        # User is loggedin show them the home page
        return render_template('beranda.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/restrukturisasi')
def restrukturisasi():
    # Check if user is loggedin
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM datadebitur ORDER BY namadebitur ASC')
            datadebitur = cursor.fetchall()
            return render_template('jadwalrestruk.html', datadebitur=datadebitur)
   
        # User is loggedin show them the home page
        return render_template('jadwalrestruk.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/notifikasi', methods=['GET', 'POST'])
def notifikasi():
    return render_template('notifikasi.html')

@app.route('/jatuhtempo', methods=['GET', 'POST'])
def jatuhtempo():
    return render_template('viewnotifikasi.html')

@app.route('/detaildebitur', methods=['GET', 'POST'])
def detaildebitur():
    return render_template('detaildebitur.html')
  
@app.route('/tambahdebitur', methods=['GET', 'POST'])
def tambahdebitur():
 # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    if request.method == 'GET':
        return render_template('tambahdebitur.html', username=session['username'])
    else:
        nama_debitur = request.form['nama_debitur']
        no_rekening = request.form['no_rekening']
        jenis_kredit = request.form['jenis_kredit']
        baki_debet = request.form['baki_debet']
        rm = request.form['rm']
        jangkawaktu = request.form['jangkawaktu']
        sbaw1 = request.form['sbaw1']
        sbak1 = request.form['sbak1']
        sbp1 = request.form['sbp1']
        sbaw2 = request.form['sbaw2']
        sbak2 = request.form['sbak2']
        sbp2 = request.form['sbp2']
        sbaw3 = request.form['sbaw3']
        sbak3 = request.form['sbak3']
        sbp3 = request.form['sbp3']
        jadwal_pokok = request.form['jadwal_pokok']
        jadwal_jatuh_tempo = request.form['jadwal_jatuh_tempo']
        akad = request.form['akad']
        keterangan = request.form['keterangan']

        if not nama_debitur or not no_rekening or not jenis_kredit or not baki_debet or not rm or not jangkawaktu or not sukubunga1 or not jadwal_pokok or not jadwal_jatuh_tempo or not akad or not keterangan:
            msg = 'Please fill out the form!'

        cursor.execute('''INSERT INTO datadebitur VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(nama_debitur, no_rekening, jenis_kredit, baki_debet, rm, jangkawaktu, jadwal_pokok, sbaw1, sbak1, sbp1, sbaw2, sbak2, sbp2, sbaw3, sbak3, sbp3, jadwal_jatuh_tempo, akad, keterangan))
        conn.commit()
        cursor.close()
        return redirect(url_for('restrukturisasi'))

    return render_template('jadwalrestruk.html', msg=msg)
def postskill():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        skills = request.form.getlist('skill[]')
        for value in skills:  
            cur.execute("INSERT INTO skills (skillname) VALUES (%s)",[value])
            mysql.connection.commit()       
        cur.close()
        msg = 'New record created successfully'    
    return jsonify(msg)

@app.route('/restrukturisasi/debiturhapus', methods=['GET', 'POST'])
def debiturhapus(norek):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM datadebitur WHERE norek = %s', (norek,))
            conn.commit()
            cursor.close()
            return redirect(url_for('restrukturisasi'))
    return redirect('/login')

# http://localhost:5000/logout - this will be the logout page
@app.route('/logout')
def logout():
   session.clear()
   return redirect(url_for('login'))
 
# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile(): 
 # Check if account exists using MySQL
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
  
  
  
if __name__ == '__main__':
    app.run(debug=True)