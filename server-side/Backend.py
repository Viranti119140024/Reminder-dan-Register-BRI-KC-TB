from flask import Flask, request, session, redirect, url_for, render_template
from flaskext.mysql import MySQL
from datetime import datetime
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
@app.route('/login', methods=['GET', 'POST'])
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
            date = datetime.today()
            date = date.strftime('%Y-%m-%d')
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('ALTER TABLE datadebitur DROP id')
            cursor.execute('ALTER TABLE datadebitur ADD id INT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST')
            cursor.execute("UPDATE datadebitur SET dt = %s", (date))
            # ksb1 = str(ksb1)
            jumlah = cursor.execute("SELECT * FROM datadebitur")
            i=1;
            while i <= jumlah:
                cursor.execute('INSERT IGNORE INTO kenaikansukubunga (namadebitur, norek, jeniskredit, jangkawaktu,sbaw, sbak, sukubunga, jadwaljatuhtempo, akad) SELECT namadebitur, norek, jeniskredit, jangkawaktu, sbaw1, sbak1, sbp1, jadwaltempo, akad FROM datadebitur WHERE id=%s && dt=ksb1', (i) )
                cursor.execute('INSERT IGNORE INTO kenaikansukubunga (namadebitur, norek, jeniskredit, jangkawaktu,sbaw, sbak, sukubunga, jadwaljatuhtempo, akad) SELECT namadebitur, norek, jeniskredit, jangkawaktu, sbaw2, sbak2, sbp2, jadwaltempo, akad FROM datadebitur WHERE id=%s && dt=ksb2', (i) )
                cursor.execute('INSERT IGNORE INTO kenaikansukubunga (namadebitur, norek, jeniskredit, jangkawaktu,sbaw, sbak, sukubunga, jadwaljatuhtempo, akad) SELECT namadebitur, norek, jeniskredit, jangkawaktu, sbaw3, sbak3, sbp3, jadwaltempo, akad FROM datadebitur WHERE id=%s && dt=ksb3', (i) )
                conn.commit()
                i = i+1;
            con = mysql.connect()
            cur = con.cursor(pymysql.cursors.DictCursor)
            cur.execute('SELECT * FROM datadebitur')
            notif = cursor.execute("SELECT * FROM kenaikansukubunga")
            datadebitur = cur.fetchall()
            conn.commit()
            cursor.close()
            return render_template('jadwalrestruk.html', datadebitur=datadebitur, notif=notif)
        # User is loggedin show them the home page
        return render_template('jadwalrestruk.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/notifikasi', methods=['GET', 'POST'])
def notifikasi():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    notif = cursor.execute("SELECT * FROM kenaikansukubunga")
    conn.commit()
    cursor.close()
    return render_template('notifikasi.html', notif=notif)

@app.route('/notifikasi/vewnotif')
def viewnotif():
    # Check if user is loggedin
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM kenaikansukubunga ORDER BY namadebitur ASC')
        kenaikansukubunga = cursor.fetchall()
        conn.commit()
        cursor.close()
        # User is loggedin show them the home page
        return render_template('viewnotifikasi.html', kenaikansukubunga=kenaikansukubunga)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# @app.route('/jatuhtempo', methods=['GET', 'POST'])
# def jatuhtempo():
#     return render_template('viewnotifikasi.html')
  
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
        jangkawaktu = int(request.form["jangkawaktu"])
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
        akad = request.form["akad"]
        keterangan = request.form['keterangan']
        ksb1 = request.form['ksb1']
        ksb2 = request.form['ksb2']
        ksb3 = request.form['ksb3']
        dt = request.form['dt']

        # jt=akad + datetime.timedelta(month=jangkawaktu)
        if not nama_debitur or not no_rekening or not jenis_kredit or not baki_debet or not rm or not jangkawaktu or not jadwal_pokok or not jadwal_jatuh_tempo or not akad or not keterangan:
            msg = 'Please fill out the form!'
        cursor.execute('''INSERT INTO datadebitur VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(id, nama_debitur, no_rekening, jenis_kredit, baki_debet, rm, jangkawaktu, jadwal_pokok, sbaw1, sbak1, sbp1, sbaw2, sbak2, sbp2, sbaw3, sbak3, sbp3, jadwal_jatuh_tempo, akad, keterangan, ksb1, ksb2, ksb3,dt))
        cursor.execute("UPDATE datadebitur SET jadwaltempo = DATE_ADD(akad, INTERVAL %s MONTH) WHERE norek = %s", (jangkawaktu, no_rekening,))
        cursor.execute("UPDATE datadebitur SET ksb1 = DATE_ADD(akad, INTERVAL %s MONTH) WHERE norek = %s", (sbak1, no_rekening,))
        cursor.execute("UPDATE datadebitur SET ksb2 = DATE_ADD(akad, INTERVAL %s MONTH) WHERE norek = %s", (sbak2, no_rekening,))
        cursor.execute("UPDATE datadebitur SET ksb3 = DATE_ADD(akad, INTERVAL %s MONTH) WHERE norek = %s", (sbak3, no_rekening,))
        # ksb1 = cursor.execute("SELECT ksb1 FROM datadebitur")
        import pandas as pd
        ksb1 = pd.to_datetime(ksb1, format='%Y-%m-%d')
        # cursor.execute("UPDATE datadebitur SET dt = ksb1 WHERE norek = %s", (no_rekening))
        # dt = datetime.today()
        # cursor.execute("UPDATE datadebitur SET ksb2 = ksb1 WHERE norek = %s", (no_rekening))
        #     if ksb1 == dt:
        #         cursor.execute("UPDATE datadebitur SET ksb2 = ksb1 WHERE norek = %s", (no_rekening))
        #         cursor.execute('''INSERT INTO kenaikansukubunga VALUES(%s,%s,%s,%s,%s,%s,%s)''',(nama_debitur, no_rekening, jenis_kredit, jangkawaktu, sbp1, jadwal_jatuh_tempo, akad))
        #         conn.commit()
        #         cursor.close()
        conn.commit()
        cursor.close()
        return redirect(url_for('restrukturisasi'))

    return render_template('jadwalrestruk.html', msg=msg)

@app.route('/notifikasi/vewnotif/detail/<norek>', methods=['GET', 'POST'])
def detaildebitur(norek):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('SELECT * from datadebitur WHERE norek = %s', (norek,))
            detaildebitur = cursor.fetchall()
            conn.commit()
            cursor.close()
            return render_template('detaildebitur.html', detaildebitur=detaildebitur)
    return redirect('/login')

@app.route('/restrukturisasi/debiturhapus/<norek>', methods=['GET', 'POST'])
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

@app.route('/notifikasi/viewnotif/notifhapus/<norek>', methods=['GET', 'POST'])
def notifhapus(norek):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM kenaikansukubunga WHERE norek = %s', (norek,))
            conn.commit()
            cursor.close()
            return redirect(url_for('viewnotif'))
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