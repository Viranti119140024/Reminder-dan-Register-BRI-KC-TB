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
            conn.commit()
            cursor.execute('ALTER TABLE datadebitur ADD id INT NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST')
            conn.commit()
            cursor.execute("UPDATE datadebitur SET dt = %s", (date))
            conn.commit()
            cursor.execute("TRUNCATE TABLE kenaikansukubunga")
            conn.commit()
            # ksb1 = str(ksb1)
            jumlah = cursor.execute("SELECT * FROM datadebitur")
            i=1;
            while i <= jumlah:
                cursor.execute('INSERT IGNORE INTO kenaikansukubunga (namadebitur, norek, jeniskredit, jangkawaktu,sbaw, sbak, sukubunga, jadwaljatuhtempo, akad) SELECT namadebitur, norek, jeniskredit, jangkawaktu, sbaw1, sbak1, sbp1, jadwaltempo, akad FROM datadebitur WHERE id=%s && dt>=ksb1 && dt<ksb2 && dt<ksb3', (i) )
                cursor.execute('INSERT IGNORE INTO kenaikansukubunga (namadebitur, norek, jeniskredit, jangkawaktu,sbaw, sbak, sukubunga, jadwaljatuhtempo, akad) SELECT namadebitur, norek, jeniskredit, jangkawaktu, sbaw2, sbak2, sbp2, jadwaltempo, akad FROM datadebitur WHERE id=%s && dt>=ksb2 && dt<ksb3', (i) )
                cursor.execute('INSERT IGNORE INTO kenaikansukubunga (namadebitur, norek, jeniskredit, jangkawaktu,sbaw, sbak, sukubunga, jadwaljatuhtempo, akad) SELECT namadebitur, norek, jeniskredit, jangkawaktu, sbaw3, sbak3, sbp3, jadwaltempo, akad FROM datadebitur WHERE id=%s && dt>=ksb3', (i) )
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

        if not nama_debitur or not no_rekening or not jenis_kredit or not baki_debet or not rm or not jangkawaktu or not jadwal_pokok or not jadwal_jatuh_tempo or not akad or not keterangan:
            msg = 'Please fill out the form!'
        cursor.execute('''INSERT INTO datadebitur VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(id, nama_debitur, no_rekening, jenis_kredit, baki_debet, rm, jangkawaktu, jadwal_pokok, sbaw1, sbak1, sbp1, sbaw2, sbak2, sbp2, sbaw3, sbak3, sbp3, jadwal_jatuh_tempo, akad, keterangan, ksb1, ksb2, ksb3,dt))
        cursor.execute("UPDATE datadebitur SET jadwaltempo = DATE_ADD(akad, INTERVAL %s MONTH) WHERE norek = %s", (jangkawaktu, no_rekening,))
        cursor.execute("UPDATE datadebitur SET ksb1 = DATE_SUB(DATE_ADD(akad, INTERVAL %s MONTH), INTERVAL 2 WEEK) WHERE norek = %s", (sbak1, no_rekening,))
        cursor.execute("UPDATE datadebitur SET ksb2 = DATE_SUB(DATE_ADD(akad, INTERVAL %s MONTH), INTERVAL 2 WEEK) WHERE norek = %s", (sbak2, no_rekening,))
        cursor.execute("UPDATE datadebitur SET ksb3 = DATE_SUB(DATE_ADD(akad, INTERVAL %s MONTH), INTERVAL 2 WEEK) WHERE norek = %s", (sbak3, no_rekening,))
        conn.commit()
        cursor.close()
        return redirect(url_for('restrukturisasi'))

    return render_template('jadwalrestruk.html', msg=msg)

@app.route('/restrukturisasi/editdebitur/<norek>', methods=['GET', 'POST'])
def editdebitur(norek):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM datadebitur WHERE norek = %s', (norek,))
            editdebitur = cursor.fetchone()
            return render_template('editdebitur.html', editdebitur=editdebitur)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['nama_debitur'] == '':
                new_nama_debitur = request.form['nama_debitur']
                cursor.execute('UPDATE IGNORE datadebitur SET namadebitur = %s WHERE norek = %s', (new_nama_debitur, norek))
                conn.commit()
                
            if not request.form['no_rekening'] == '':
                new_no_rekening = request.form['no_rekening']
                cursor.execute('UPDATE IGNORE datadebitur SET norek = %s WHERE norek = %s', (new_no_rekening, norek))
                conn.commit()
                
            if not request.form['jenis_kredit'] == '':
                new_jenis_kredit = request.form['jenis_kredit']
                cursor.execute('UPDATE IGNORE datadebitur SET jeniskredit = %s WHERE norek = %s', (new_jenis_kredit, norek))
                conn.commit()
                
            if not request.form['baki_debet'] == '':
                new_baki_debet = request.form['baki_debet']
                cursor.execute('UPDATE IGNORE datadebitur SET bakidebet = %s WHERE norek = %s', (new_baki_debet, norek))
                conn.commit()
                
            if not request.form['rm'] == '':
                new_rm = request.form['rm']
                cursor.execute('UPDATE IGNORE datadebitur SET rm = %s WHERE norek = %s', (new_rm, norek))
                conn.commit()
                
            if not request.form['jangkawaktu'] == '':
                new_jangkawaktu = request.form['jangkawaktu']
                cursor.execute('UPDATE IGNORE datadebitur SET jangkawaktu = %s WHERE norek = %s', (new_jangkawaktu, norek))
                conn.commit()
                
            if not request.form['jadwal_pokok'] == '':
                new_jadwal_pokok = request.form['jadwal_pokok']
                cursor.execute('UPDATE IGNORE datadebitur SET jadwalpokok = %s WHERE norek = %s', (new_jadwal_pokok, norek))
                conn.commit()
                
            if not request.form['sbaw1'] == '':
                new_sbaw1 = request.form['sbaw1']
                cursor.execute('UPDATE IGNORE datadebitur SET sbaw1 = %s WHERE norek = %s', (new_sbaw1, norek))
                conn.commit()

            if not request.form['sbak1'] == '':
                new_sbak1 = request.form['sbak1']
                cursor.execute('UPDATE IGNORE datadebitur SET sbak1 = %s WHERE norek = %s', (new_sbak1, norek))
                cursor.execute("UPDATE datadebitur SET ksb1 = DATE_SUB(DATE_ADD(akad, INTERVAL %s MONTH), INTERVAL 2 WEEK) WHERE norek = %s", (new_sbak1, norek,))
                conn.commit()

            if not request.form['sbp1'] == '':
                new_sbp1 = request.form['sbp1']
                cursor.execute('UPDATE IGNORE datadebitur SET sbp1 = %s WHERE norek = %s', (new_sbp1, norek))
                conn.commit()

            if not request.form['sbaw2'] == '':
                new_sbaw2 = request.form['sbaw2']
                cursor.execute('UPDATE IGNORE datadebitur SET sbaw2 = %s WHERE norek = %s', (new_sbaw2, norek))
                conn.commit()

            if not request.form['sbak2'] == '':
                new_sbak2 = request.form['sbak2']
                cursor.execute('UPDATE IGNORE datadebitur SET sbak2 = %s WHERE norek = %s', (new_sbak2, norek))
                cursor.execute("UPDATE datadebitur SET ksb2 = DATE_SUB(DATE_ADD(akad, INTERVAL %s MONTH), INTERVAL 2 WEEK) WHERE norek = %s", (new_sbak2, norek,))
                conn.commit()

            if not request.form['sbp2'] == '':
                new_sbp2 = request.form['sbp2']
                cursor.execute('UPDATE IGNORE datadebitur SET sbp2 = %s WHERE norek = %s', (new_sbp2, norek))
                conn.commit()

            if not request.form['sbaw3'] == '':
                new_sbaw3 = request.form['sbaw3']
                cursor.execute('UPDATE IGNORE datadebitur SET sbaw3 = %s WHERE norek = %s', (new_sbaw3, norek))
                conn.commit()

            if not request.form['sbak3'] == '':
                new_sbak3 = request.form['sbak3']
                cursor.execute('UPDATE IGNORE datadebitur SET sbak3 = %s WHERE norek = %s', (new_sbak3, norek))
                cursor.execute("UPDATE datadebitur SET ksb3 = DATE_SUB(DATE_ADD(akad, INTERVAL %s MONTH), INTERVAL 2 WEEK) WHERE norek = %s", (new_sbak3, norek,))
                conn.commit()

            if not request.form['sbp3'] == '':
                new_sbp3 = request.form['sbp3']
                cursor.execute('UPDATE IGNORE datadebitur SET sbp3 = %s WHERE norek = %s', (new_sbp3, norek))
                conn.commit()

            if not request.form['keterangan'] == '':
                new_bap = request.form['keterangan']
                cursor.execute('UPDATE IGNORE datadebitur SET bap = %s WHERE norek = %s', (new_bap, norek))
                conn.commit()
                
            return redirect(url_for('restrukturisasi'))

@app.route('/restrukturisasi/notifikasi/viewnotif/editdebitur/<norek>', methods=['GET', 'POST'])
def editdebitur2(norek):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM datadebitur WHERE norek = %s', (norek,))
            editdebitur = cursor.fetchone()
            return render_template('editdebitur2.html', editdebitur=editdebitur)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['nama_debitur'] == '':
                new_nama_debitur = request.form['nama_debitur']
                cursor.execute('UPDATE IGNORE datadebitur SET namadebitur = %s WHERE norek = %s', (new_nama_debitur, norek))
                conn.commit()
                
            if not request.form['no_rekening'] == '':
                new_no_rekening = request.form['no_rekening']
                cursor.execute('UPDATE IGNORE datadebitur SET norek = %s WHERE norek = %s', (new_no_rekening, norek))
                conn.commit()
                
            if not request.form['jenis_kredit'] == '':
                new_jenis_kredit = request.form['jenis_kredit']
                cursor.execute('UPDATE IGNORE datadebitur SET jeniskredit = %s WHERE norek = %s', (new_jenis_kredit, norek))
                conn.commit()
                
            if not request.form['baki_debet'] == '':
                new_baki_debet = request.form['baki_debet']
                cursor.execute('UPDATE IGNORE datadebitur SET bakidebet = %s WHERE norek = %s', (new_baki_debet, norek))
                conn.commit()
                
            if not request.form['rm'] == '':
                new_rm = request.form['rm']
                cursor.execute('UPDATE IGNORE datadebitur SET rm = %s WHERE norek = %s', (new_rm, norek))
                conn.commit()
                
            if not request.form['jangkawaktu'] == '':
                new_jangkawaktu = request.form['jangkawaktu']
                cursor.execute('UPDATE IGNORE datadebitur SET jangkawaktu = %s WHERE norek = %s', (new_jangkawaktu, norek))
                conn.commit()
                
            if not request.form['jadwal_pokok'] == '':
                new_jadwal_pokok = request.form['jadwal_pokok']
                cursor.execute('UPDATE IGNORE datadebitur SET jadwalpokok = %s WHERE norek = %s', (new_jadwal_pokok, norek))
                conn.commit()
                
            if not request.form['sbaw1'] == '':
                new_sbaw1 = request.form['sbaw1']
                cursor.execute('UPDATE IGNORE datadebitur SET sbaw1 = %s WHERE norek = %s', (new_sbaw1, norek))
                conn.commit()

            if not request.form['sbak1'] == '':
                new_sbak1 = request.form['sbak1']
                cursor.execute('UPDATE IGNORE datadebitur SET sbak1 = %s WHERE norek = %s', (new_sbak1, norek))
                conn.commit()

            if not request.form['sbp1'] == '':
                new_sbp1 = request.form['sbp1']
                cursor.execute('UPDATE IGNORE datadebitur SET sbp1 = %s WHERE norek = %s', (new_sbp1, norek))
                conn.commit()

            if not request.form['sbaw2'] == '':
                new_sbaw2 = request.form['sbaw2']
                cursor.execute('UPDATE IGNORE datadebitur SET sbaw2 = %s WHERE norek = %s', (new_sbaw2, norek))
                conn.commit()

            if not request.form['sbak2'] == '':
                new_sbak2 = request.form['sbak2']
                cursor.execute('UPDATE IGNORE datadebitur SET sbak2 = %s WHERE norek = %s', (new_sbak2, norek))
                conn.commit()

            if not request.form['sbp2'] == '':
                new_sbp2 = request.form['sbp2']
                cursor.execute('UPDATE IGNORE datadebitur SET sbp2 = %s WHERE norek = %s', (new_sbp2, norek))
                conn.commit()

            if not request.form['sbaw3'] == '':
                new_sbaw3 = request.form['sbaw3']
                cursor.execute('UPDATE IGNORE datadebitur SET sbaw3 = %s WHERE norek = %s', (new_sbaw3, norek))
                conn.commit()

            if not request.form['sbak3'] == '':
                new_sbak3 = request.form['sbak3']
                cursor.execute('UPDATE IGNORE datadebitur SET sbak3 = %s WHERE norek = %s', (new_sbak3, norek))
                conn.commit()

            if not request.form['sbp3'] == '':
                new_sbp3 = request.form['sbp3']
                cursor.execute('UPDATE IGNORE datadebitur SET sbp3 = %s WHERE norek = %s', (new_sbp3, norek))
                conn.commit()

            if not request.form['keterangan'] == '':
                new_bap = request.form['keterangan']
                cursor.execute('UPDATE IGNORE datadebitur SET bap = %s WHERE norek = %s', (new_bap, norek))
                conn.commit()
                
            return redirect(url_for('viewnotif'))


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

@app.route('/restrukturisasi/detail/<norek>', methods=['GET', 'POST'])
def detaildebitur2(norek):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('SELECT * from datadebitur WHERE norek = %s', (norek,))
            detaildebitur = cursor.fetchall()
            conn.commit()
            cursor.close()
            return render_template('detaildebitur2.html', detaildebitur=detaildebitur)
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
            cursor.execute('DELETE t1 FROM datadebitur t1 JOIN kenaikansukubunga t2 ON t1.sbaw3 = t2.sbaw && t1.sbak3 = t2.sbak && t1.sbp3 = t2.sukubunga && t1.norek = %s && t2.norek = %s', (norek,norek))
            conn.commit()
            cursor.close()


            
            return redirect(url_for('viewnotif'))
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        select = (request.form.get('tindakan'))
        if select == 'register1':
            return render_template('detail_IPK RESTRUK.html')  
        elif select == 'register2':
            return redirect(url_for('ipkrestruk'))
        return render_template('daftarregister.html')
    return redirect('/login')

@app.route('/register/ipkrestruk', methods=['GET', 'POST'])
def ipkrestruk():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM ipkrestruk')
        ipkrestruk = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./IPK RESTRUK/detail_IPK RESTRUK.html', ipkrestruk=ipkrestruk)  
    return redirect('/login')

@app.route('/register/ipkrestruk/tambah', methods=['GET', 'POST'])
def tambahipkrestruk():
 # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    if request.method == 'GET':
        return render_template('./IPK RESTRUK/tambah_IPK RESTRUK.html', username=session['username'])
    else:
        no_ipk = request.form['no_ipk']
        nama_debitur = request.form['nama_debitur']
        No_PTK = request.form['No.PTK']
        Akad = request.form['Akad']
        Jatuh_Tempo = request.form['Jatuh_Tempo']
        Jangka_Waktu = int(request.form["Jangka_Waktu"])
        Rekening = request.form['Rekening']
        keterangan = request.form['keterangan']

        # if not nama_debitur or not no_rekening or not jenis_kredit or not baki_debet or not rm or not jangkawaktu or not jadwal_pokok or not jadwal_jatuh_tempo or not akad or not keterangan:
        #     msg = 'Please fill out the form!'
        cursor.execute('''INSERT INTO ipkrestruk VALUES(%s,%s,%s,%s,%s,%s,%s,%s)''',(no_ipk, nama_debitur, No_PTK, Akad, Jatuh_Tempo, Jangka_Waktu, Rekening, keterangan))
        conn.commit()
        cursor.close()
        return redirect(url_for('ipkrestruk'))

    return render_template('./IPK RESTRUK/detail_IPK RESTRUK.html', msg=msg)

@app.route('/register/ipkrestruk/edit/<norek>', methods=['GET', 'POST'])
def editipkrestruk(norek):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM ipkrestruk WHERE norek = %s', (norek,))
            editipkrestruk = cursor.fetchone()
            return render_template('./IPK RESTRUK/edit_IPK RESTRUK.html', editipkrestruk=editipkrestruk)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['no_ipk'] == '':
                new_no_ipk = request.form['no_ipk']
                cursor.execute('UPDATE IGNORE ipkrestruk SET noipk = %s WHERE norek = %s', (new_no_ipk, norek))
                conn.commit()
                
            if not request.form['nama_debitur'] == '':
                new_nama_debitur = request.form['nama_debitur']
                cursor.execute('UPDATE IGNORE ipkrestruk SET namadebitur = %s WHERE norek = %s', (new_nama_debitur, norek))
                conn.commit()
                
            if not request.form['No.PTK'] == '':
                new_No_PTK = request.form['No.PTK']
                cursor.execute('UPDATE IGNORE ipkrestruk SET noptk = %s WHERE norek = %s', (new_No_PTK, norek))
                conn.commit()
            
            if not request.form['Akad'] == '':
                new_Akad = request.form['Akad']
                cursor.execute('UPDATE IGNORE ipkrestruk SET akad = %s WHERE norek = %s', (new_Akad, norek))
                conn.commit()

            if not request.form['Jatuh_Tempo'] == '':
                new_Jatuh_Tempo = request.form['Jatuh_Tempo']
                cursor.execute('UPDATE IGNORE ipkrestruk SET jatuhtempo = %s WHERE norek = %s', (new_Jatuh_Tempo, norek))
                conn.commit()
            
            if not request.form['Jangka_Waktu'] == '':
                new_Jangka_Waktu = request.form['Jangka_Waktu']
                cursor.execute('UPDATE IGNORE ipkrestruk SET jangkawaktu = %s WHERE norek = %s', (new_Jangka_Waktu, norek))
                conn.commit()

            if not request.form['Rekening'] == '':
                new_Rekening = request.form['Rekening']
                cursor.execute('UPDATE IGNORE ipkrestruk SET norek = %s WHERE norek = %s', (new_Rekening, norek))
                conn.commit()
            
            if not request.form['keterangan'] == '':
                new_keterangan = request.form['keterangan']
                cursor.execute('UPDATE IGNORE ipkrestruk SET keterangan = %s WHERE norek = %s', (new_keterangan, norek))
                conn.commit()
                
            return redirect(url_for('ipkrestruk'))

# http://localhost:5000/logout - this will be the logout page
@app.route('/logout')
def logout():
   session.clear()
   return redirect(url_for('login'))
  
if __name__ == '__main__':
    app.run(debug=True)