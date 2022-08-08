from flask import Flask, request, session, redirect, url_for, render_template
from flaskext.mysql import MySQL
from datetime import datetime
import pymysql 
import re 
 
app = Flask(__name__)
 
app.secret_key = 'cairocoders-ednalan'
 
mysql = MySQL()
   
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'bri-minder'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/', methods=['POST', 'GET'])
def function():
    if not 'loggedin' in session:
        return redirect('/login')
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
 # connect
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
  
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        
        username = request.form['username']
        password = request.form['password']
        
        cursor.execute('SELECT * FROM user WHERE username = %s AND password = %s', (username, password))
        
        user = cursor.fetchone()
   
    
        if user:
            
            session['loggedin'] = True
            session['nama'] = user['nama']
            session['username'] = user['username']
            
            return redirect(url_for('home'))
        else:
            
            msg = 'Incorrect username/password!'
    
    return render_template('login.html', msg=msg)
 
@app.route('/registrasi', methods=['GET', 'POST'])
def registrasi():
    
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    msg = ''
    
    if request.method == 'POST' and 'username' in request.form and 'nama' in request.form and 'password' in request.form:
        
        username = request.form['username']
        nama = request.form['nama']
        password = request.form['password']
   
        cursor.execute('SELECT * FROM user WHERE username = %s', (username))
        account = cursor.fetchone()
        
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not nama or not password:
            msg = 'Please fill out the form!'
        else:
            
            cursor.execute('INSERT INTO user VALUES (%s, %s, %s)', (username, nama, password)) 
            conn.commit()
   
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('registrasi.html', msg=msg)
  
@app.route('/beranda')
def home():
    
    if 'loggedin' in session:
        
        return render_template('beranda.html', username=session['username'])
        
    return redirect(url_for('login'))

@app.route('/restrukturisasi')
def restrukturisasi():
    
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
            
            jumlah = cursor.execute("SELECT * FROM datadebitur")
            i=1;
            while i <= jumlah:
                cursor.execute('INSERT IGNORE INTO kenaikansukubunga (namadebitur, norek, jeniskredit, jangkawaktu,sbaw, sbak, sukubunga, jadwaljatuhtempo, akad) SELECT namadebitur, norek, jeniskredit, jangkawaktu, sbaw1, sbak1, sbp1, jadwaltempo, akad FROM datadebitur WHERE id=%s && dt>=ksb1 && dt<=jadwaltempo && sbaw1!=0 && sbak1!=0 && sbp1!=0 && sbp2=0 && sbp3=0 && status1="B"', (i) )
                cursor.execute('INSERT IGNORE INTO kenaikansukubunga (namadebitur, norek, jeniskredit, jangkawaktu,sbaw, sbak, sukubunga, jadwaljatuhtempo, akad) SELECT namadebitur, norek, jeniskredit, jangkawaktu, sbaw1, sbak1, sbp1, jadwaltempo, akad FROM datadebitur WHERE id=%s && dt>=ksb1 && dt<ksb2 && sbaw1!=0 && sbak1!=0 && sbp1!=0 && sbp3=0 && status1="B"', (i) )
                cursor.execute('INSERT IGNORE INTO kenaikansukubunga (namadebitur, norek, jeniskredit, jangkawaktu,sbaw, sbak, sukubunga, jadwaljatuhtempo, akad) SELECT namadebitur, norek, jeniskredit, jangkawaktu, sbaw2, sbak2, sbp2, jadwaltempo, akad FROM datadebitur WHERE id=%s && dt>=ksb2 && dt<=jadwaltempo && sbaw2!=0 && sbak2!=0 && sbp2!=0 && sbp3=0 && status2="B"', (i) )
                cursor.execute('INSERT IGNORE INTO kenaikansukubunga (namadebitur, norek, jeniskredit, jangkawaktu,sbaw, sbak, sukubunga, jadwaljatuhtempo, akad) SELECT namadebitur, norek, jeniskredit, jangkawaktu, sbaw1, sbak1, sbp1, jadwaltempo, akad FROM datadebitur WHERE id=%s && dt>=ksb1 && dt<ksb2 && sbaw1!=0 && sbak1!=0 && sbp1!=0 && sbp2!=0 && sbp3!=0 && status1="B"', (i) )
                cursor.execute('INSERT IGNORE INTO kenaikansukubunga (namadebitur, norek, jeniskredit, jangkawaktu,sbaw, sbak, sukubunga, jadwaljatuhtempo, akad) SELECT namadebitur, norek, jeniskredit, jangkawaktu, sbaw2, sbak2, sbp2, jadwaltempo, akad FROM datadebitur WHERE id=%s && dt>=ksb2 && dt<ksb3 && sbaw1!=0 && sbak1!=0 && sbp1!=0 && sbp2!=0 && sbp3!=0 && status2="B"', (i) )
                cursor.execute('INSERT IGNORE INTO kenaikansukubunga (namadebitur, norek, jeniskredit, jangkawaktu,sbaw, sbak, sukubunga, jadwaljatuhtempo, akad) SELECT namadebitur, norek, jeniskredit, jangkawaktu, sbaw3, sbak3, sbp3, jadwaltempo, akad FROM datadebitur WHERE id=%s && dt>=ksb3 && dt<=jadwaltempo && sbaw1!=0 && sbak1!=0 && sbp1!=0 && sbp2!=0 && sbp3!=0 && status3="B"', (i) )
                cursor.execute("UPDATE IGNORE datadebitur SET ksb1 = DATE_SUB(DATE_ADD(akad, INTERVAL sbaw1 MONTH), INTERVAL 6 WEEK) WHERE id = %s && sbp1!=0", ( i,))
                cursor.execute("UPDATE IGNORE datadebitur SET ksb2 = DATE_SUB(DATE_ADD(akad, INTERVAL sbaw2 MONTH), INTERVAL 6 WEEK) WHERE id = %s && sbp2!=0", ( i,))
                cursor.execute("UPDATE IGNORE datadebitur SET ksb3 = DATE_SUB(DATE_ADD(akad, INTERVAL sbaw3 MONTH), INTERVAL 6 WEEK) WHERE id = %s && sbp3!=0", ( i,))
                cursor.execute('UPDATE IGNORE datadebitur SET ksb1 = 0 WHERE id = %s && sbp1=0', ( i,))
                cursor.execute('UPDATE IGNORE datadebitur SET ksb2 = 0 WHERE id = %s && sbp2=0', ( i,))
                cursor.execute('UPDATE IGNORE datadebitur SET ksb3 = 0 WHERE id = %s && sbp3=0', ( i,))
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
        return render_template('jadwalrestruk.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/notifikasi', methods=['GET', 'POST'])
def notifikasi():
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        notif = cursor.execute("SELECT * FROM kenaikansukubunga")
        conn.commit()
        cursor.close()
        return render_template('notifikasi.html', notif=notif)
    return redirect(url_for('login'))

@app.route('/notifikasi/vewnotif')
def viewnotif():
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM kenaikansukubunga ORDER BY namadebitur ASC')
        kenaikansukubunga = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('viewnotifikasi.html', kenaikansukubunga=kenaikansukubunga)
    return redirect(url_for('login'))

@app.route('/tambahdebitur', methods=['GET', 'POST'])
def tambahdebitur():
    if 'loggedin' in session:
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
            akad = request.form["akad"]
            keterangan = request.form['keterangan']

            if not nama_debitur or not no_rekening or not jenis_kredit or not baki_debet or not rm or not jangkawaktu or not jadwal_pokok or not jadwal_jatuh_tempo or not akad or not keterangan:
                msg = 'Please fill out the form!'
            cursor.execute('''INSERT INTO datadebitur VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0,%s,%s,0,0,0,0,"B","B","B")''',(id, nama_debitur, no_rekening, jenis_kredit, baki_debet, rm, jangkawaktu, jadwal_pokok, sbaw1, sbak1, sbp1, sbaw2, sbak2, sbp2, sbaw3, sbak3, sbp3, akad, keterangan))
            cursor.execute("UPDATE datadebitur SET jadwaltempo = DATE_ADD(akad, INTERVAL %s MONTH) WHERE norek = %s", (jangkawaktu, no_rekening,))
            cursor.execute("UPDATE datadebitur SET ksb1 = DATE_SUB(DATE_ADD(akad, INTERVAL %s MONTH), INTERVAL 6 WEEK) WHERE norek = %s && sbp1!=0", (sbaw1, no_rekening,))
            cursor.execute("UPDATE datadebitur SET ksb2 = DATE_SUB(DATE_ADD(akad, INTERVAL %s MONTH), INTERVAL 6 WEEK) WHERE norek = %s && sbp2!=0", (sbaw2, no_rekening,))
            cursor.execute("UPDATE datadebitur SET ksb3 = DATE_SUB(DATE_ADD(akad, INTERVAL %s MONTH), INTERVAL 6 WEEK) WHERE norek = %s && sbp3!=0", (sbaw3, no_rekening,))
            conn.commit()
            cursor.close()
            return redirect(url_for('restrukturisasi'))

        return render_template('jadwalrestruk.html', msg=msg)
    return redirect(url_for('login'))
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
                cursor.execute("UPDATE datadebitur SET jadwaltempo = DATE_ADD(akad, INTERVAL %s MONTH) WHERE norek = %s", (new_jangkawaktu, norek,))
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

            if not request.form['akad'] == '':
                new_akad = request.form['akad']
                cursor.execute('UPDATE IGNORE datadebitur SET akad = %s WHERE norek = %s', (new_akad, norek))
                conn.commit()

            if not request.form['keterangan'] == '':
                new_bap = request.form['keterangan']
                cursor.execute('UPDATE IGNORE datadebitur SET bap = %s WHERE norek = %s', (new_bap, norek))
                conn.commit()
                
            return redirect(url_for('restrukturisasi'))
    return redirect(url_for('login'))

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
    return redirect(url_for('login'))

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
    return redirect(url_for('login'))

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
    return redirect(url_for('login'))

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
    return redirect(url_for('login'))

@app.route('/notifikasi/viewnotif/notifhapus/<norek>', methods=['GET', 'POST'])
def notifhapus(norek):
    if 'loggedin' in session:
        if request.method == 'GET':
            con = mysql.connect()
            cur = con.cursor(pymysql.cursors.DictCursor)
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('DELETE IGNORE FROM kenaikansukubunga WHERE norek = %s', (norek,))
            cursor.execute('UPDATE IGNORE datadebitur SET status1 = "D" WHERE norek = %s && sbp2=0 && sbp3=0', (norek))
            cursor.execute('DELETE FROM datadebitur WHERE status1 = "D" && sbp2=0 && sbp3=0')
            cursor.execute('UPDATE IGNORE datadebitur SET status1 = "D" WHERE norek = %s && sbp2!=0 && sbp3=0', (norek))
            cursor.execute('UPDATE IGNORE datadebitur SET status2 = "D" WHERE norek = %s && sbp2!=0 && sbp3=0 && dt>=ksb2', (norek))
            cursor.execute('DELETE FROM datadebitur WHERE status1 = "D" && status2 = "D" && sbp2!=0 && sbp3=0')
            cursor.execute('UPDATE IGNORE datadebitur SET status1 = "D" WHERE norek = %s && sbp2!=0 && sbp3!=0', (norek))
            cursor.execute('UPDATE IGNORE datadebitur SET status2 = "D" WHERE norek = %s && sbp2!=0 && sbp3!=0 && dt>=ksb2', (norek))
            cursor.execute('UPDATE IGNORE datadebitur SET status3 = "D" WHERE norek = %s && sbp2!=0 && sbp3!=0 && dt>=ksb3', (norek))
            cursor.execute('DELETE FROM datadebitur WHERE status1 = "D" && status2 = "D" && status3 = "D" && sbp2!=0 && sbp3!=0')
            con.commit()
            conn.commit()
            cursor.close()
        return redirect(url_for('viewnotif'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        select = (request.form.get('tindakan'))
        if select == 'register1':
            return redirect(url_for('ipkrestruk')) 
        elif select == 'register2':
            return redirect(url_for('ppnd'))
        elif select == 'register3':
            return redirect(url_for('ptkrestruk2penyelesaian'))
        elif select == 'register4':
            return redirect(url_for('asskerugian'))
        elif select == 'register5':
            return redirect(url_for('blokirkecil'))
        elif select == 'register6':
            return redirect(url_for('ipk'))
        elif select == 'register7':
            return redirect(url_for('jasakonsultasi'))
        elif select == 'register8':
            return redirect(url_for('bkpbpinjam'))
        return render_template('daftarregister.html')
    return redirect(url_for('login'))

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
    return redirect(url_for('login'))

@app.route('/register/ipkrestruk/tambah', methods=['GET', 'POST'])
def tambahipkrestruk():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
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
            
            cursor.execute('''INSERT INTO ipkrestruk VALUES(%s,%s,%s,%s,%s,%s,%s,%s)''',(no_ipk, nama_debitur, No_PTK, Akad, Jatuh_Tempo, Jangka_Waktu, Rekening, keterangan))
            conn.commit()
            cursor.close()
            return redirect(url_for('ipkrestruk'))

    return redirect(url_for('login'))

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
    return redirect(url_for('login'))

@app.route('/register/ppnd', methods=['GET', 'POST'])
def ppnd():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM ppnd')
        ppnd = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./PPND/detail_PPND.html', ppnd=ppnd)  
    return redirect(url_for('login'))

@app.route('/register/ppnd/tambah', methods=['GET', 'POST'])
def tambahppnd():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./PPND/tambah_PPND.html', username=session['username'])
        else:
            No_PPND_dan_Tanggal_PPND = request.form['No. PPND dan Tanggal PPND']
            Nama_Debitur = request.form['Nama Debitur']
            Alamat_No_Telp_HP = request.form['Alamat No. Telp/HP']
            Jenis_Fasilitas_Kredit = request.form['Jenis Fasilitas Kredit']
            Jenis_Dok_Kredit_yang_Ditunda = request.form['Jenis Dok Kredit yang Ditunda']
            Lamanya_ditunda = int(request.form["Lamanya ditunda"])
            Tanggal_Batas_Akhir = request.form['Tanggal Batas Akhir']
            Pejabat_Pemrakarsa = request.form['Pejabat Pemrakarsa']
            Pejabat_Pemutus = request.form['Pejabat Pemutus']
            keterangan = request.form['keterangan']
            
            cursor.execute('''INSERT INTO ppnd VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(No_PPND_dan_Tanggal_PPND, Nama_Debitur, Alamat_No_Telp_HP, Jenis_Fasilitas_Kredit, Jenis_Dok_Kredit_yang_Ditunda, Lamanya_ditunda, Tanggal_Batas_Akhir, Pejabat_Pemrakarsa, Pejabat_Pemutus, keterangan ))
            conn.commit()
            cursor.close()
            return redirect(url_for('ppnd'))

    return redirect(url_for('login'))

@app.route('/register/ppnd/edit/<NoPPNdanTanggalPPN>', methods=['GET', 'POST'])
def editppnd(NoPPNdanTanggalPPN):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM ppnd WHERE NoPPNdanTanggalPPN = %s', (NoPPNdanTanggalPPN,))
            editppnd = cursor.fetchone()
            return render_template('./PPND/edit_PPND.html', editppnd=editppnd)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['No. PPND dan Tanggal PPND'] == '':
                new_No_PPND_dan_Tanggal_PPND = request.form['No. PPND dan Tanggal PPND']
                cursor.execute('UPDATE IGNORE ppnd SET NoPPNdanTanggalPPN = %s WHERE NoPPNdanTanggalPPN = %s', (new_No_PPND_dan_Tanggal_PPND, NoPPNdanTanggalPPN))
                conn.commit()
                
            if not request.form['Nama Debitur'] == '':
                new_Nama_Debitur = request.form['Nama Debitur']
                cursor.execute('UPDATE IGNORE ppnd SET NamaDebitur = %s WHERE NoPPNdanTanggalPPN = %s', (new_Nama_Debitur, NoPPNdanTanggalPPN))
                conn.commit()
                
            if not request.form['Alamat No. Telp/HP'] == '':
                new_Alamat_No_Telp_HP = request.form['Alamat No. Telp/HP']
                cursor.execute('UPDATE IGNORE ppnd SET AlamatdanNoTeleponHP = %s WHERE NoPPNdanTanggalPPN = %s', (new_Alamat_No_Telp_HP, NoPPNdanTanggalPPN))
                conn.commit()
            
            if not request.form['Jenis Fasilitas Kredit'] == '':
                new_Jenis_Fasilitas_Kredit = request.form['Jenis Fasilitas Kredit']
                cursor.execute('UPDATE IGNORE ppnd SET JenisFasilitasKredit = %s WHERE NoPPNdanTanggalPPN = %s', (new_Jenis_Fasilitas_Kredit, NoPPNdanTanggalPPN))
                conn.commit()

            if not request.form['Jenis Dok Kredit yang Ditunda'] == '':
                new_Jenis_Dok_Kredit_yang_Ditunda = request.form['Jenis Dok Kredit yang Ditunda']
                cursor.execute('UPDATE IGNORE ppnd SET JenisDokKredityangDitunda = %s WHERE NoPPNdanTanggalPPN = %s', (new_Jenis_Dok_Kredit_yang_Ditunda, NoPPNdanTanggalPPN))
                conn.commit()
            
            if not request.form['Lamanya ditunda'] == '':
                new_Lamanya_ditunda = request.form['Lamanya ditunda']
                cursor.execute('UPDATE IGNORE ppnd SET LamanyaDitunda = %s WHERE NoPPNdanTanggalPPN = %s', (new_Lamanya_ditunda, NoPPNdanTanggalPPN))
                conn.commit()

            if not request.form['Tanggal Batas Akhir'] == '':
                new_Tanggal_Batas_Akhir = request.form['Tanggal Batas Akhir']
                cursor.execute('UPDATE IGNORE ppnd SET TanggalBatasAkhir = %s WHERE NoPPNdanTanggalPPN = %s', (new_Tanggal_Batas_Akhir, NoPPNdanTanggalPPN))
                conn.commit()
            
            if not request.form['Pejabat Pemrakarsa'] == '':
                new_Pejabat_Pemrakarsa = request.form['Pejabat Pemrakarsa']
                cursor.execute('UPDATE IGNORE ppnd SET PejabatPemrakarsa = %s WHERE NoPPNdanTanggalPPN = %s', (new_Pejabat_Pemrakarsa, NoPPNdanTanggalPPN))
                conn.commit()

            if not request.form['Pejabat Pemutus'] == '':
                new_Pejabat_Pemutus = request.form['Pejabat Pemutus']
                cursor.execute('UPDATE IGNORE ppnd SET PejabatPemutus = %s WHERE NoPPNdanTanggalPPN = %s', (new_Pejabat_Pemutus, NoPPNdanTanggalPPN))
                conn.commit()

            if not request.form['keterangan'] == '':
                new_keterangan = request.form['keterangan']
                cursor.execute('UPDATE IGNORE ppnd SET Keterangan = %s WHERE NoPPNdanTanggalPPN = %s', (new_keterangan, NoPPNdanTanggalPPN))
                conn.commit()
                
            return redirect(url_for('ppnd'))
    return redirect(url_for('login'))

@app.route('/register/ptkrestruk2penyelesaian', methods=['GET', 'POST'])
def ptkrestruk2penyelesaian():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM ptk_restruk2_penyelesaian')
        ptkrestruk2penyelesaian = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./PTK Restruk 2 Penyelesaian/detail_PTK Restruk 2 Penyelesaian.html', ptkrestruk2penyelesaian=ptkrestruk2penyelesaian)  
    return redirect(url_for('login'))

@app.route('/register/ptkrestruk2penyelesaian/tambah', methods=['GET', 'POST'])
def tambahptkrestruk2penyelesaian():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./PTK Restruk 2 Penyelesaian/tambah_PTK Restruk 2 Penyelesaian.html', username=session['username'])
        else:
            No_PTK = request.form['No. PTK']
            Nama_Debitur = request.form['Nama Debitur']
            Tanggal_Putusan = request.form['Tanggal Putusan']
            Nama_Pemutus = request.form['Nama Pemutus']
            Jabatan = request.form['Jabatan']
            Rp = int(request.form["Rp"])
            keterangan = request.form['keterangan']

            
            cursor.execute('''INSERT INTO ptk_restruk2_penyelesaian VALUES(%s,%s,%s,%s,%s,%s,%s)''',(No_PTK, Nama_Debitur, Tanggal_Putusan, Nama_Pemutus, Jabatan, Rp, keterangan ))
            conn.commit()
            cursor.close()
            return redirect(url_for('ptkrestruk2penyelesaian'))

    return redirect(url_for('login'))

@app.route('/register/ptkrestruk2penyelesaian/edit/<NoPTK>', methods=['GET', 'POST'])
def editptkrestruk2penyelesaian(NoPTK):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM ptk_restruk2_penyelesaian WHERE NoPTK = %s', (NoPTK,))
            editptkrestruk2penyelesaian = cursor.fetchone()
            return render_template('./PTK Restruk 2 Penyelesaian/edit_PTK Restruk 2 Penyelesaian.html', editptkrestruk2penyelesaian=editptkrestruk2penyelesaian)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['No. PTK'] == '':
                new_No_PTK = request.form['No. PTK']
                cursor.execute('UPDATE IGNORE ptk_restruk2_penyelesaian SET NoPTK = %s WHERE NoPTK = %s', (new_No_PTK, NoPTK))
                conn.commit()
                
            if not request.form['Nama Debitur'] == '':
                new_Nama_Debitur = request.form['Nama Debitur']
                cursor.execute('UPDATE IGNORE ptk_restruk2_penyelesaian SET NamaDebitur = %s WHERE NoPTK = %s', (new_Nama_Debitur, NoPTK))
                conn.commit()
                
            if not request.form['Tanggal Putusan'] == '':
                new_Tanggal_Putusan = request.form['Tanggal Putusan']
                cursor.execute('UPDATE IGNORE ptk_restruk2_penyelesaian SET TanggalPutusan = %s WHERE NoPTK = %s', (new_Tanggal_Putusan, NoPTK))
                conn.commit()
            
            if not request.form['Nama Pemutus'] == '':
                new_Nama_Pemutus = request.form['Nama Pemutus']
                cursor.execute('UPDATE IGNORE ptk_restruk2_penyelesaian SET NamaPemutus = %s WHERE NoPTK = %s', (new_Nama_Pemutus, NoPTK))
                conn.commit()

            if not request.form['Jabatan'] == '':
                new_Jabatan = request.form['Jabatan']
                cursor.execute('UPDATE IGNORE ptk_restruk2_penyelesaian SET Jabatan = %s WHERE NoPTK = %s', (new_Jabatan, NoPTK))
                conn.commit()
            
            if not request.form['Rp'] == '':
                new_Rp = request.form['Rp']
                cursor.execute('UPDATE IGNORE ptk_restruk2_penyelesaian SET Rp = %s WHERE NoPTK = %s', (new_Rp, NoPTK))
                conn.commit()
            
            if not request.form['keterangan'] == '':
                new_keterangan = request.form['keterangan']
                cursor.execute('UPDATE IGNORE ptk_restruk2_penyelesaian SET Keterangan = %s WHERE NoPTK = %s', (new_keterangan, NoPTK))
                conn.commit()
                
            return redirect(url_for('ptkrestruk2penyelesaian'))
    return redirect(url_for('login'))

@app.route('/register/asskerugian', methods=['GET', 'POST'])
def asskerugian():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_ass_kerugian')
        asskerugian = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register ASS Kerugian/detail_Register ASS Kerugian.html', asskerugian=asskerugian)  
    return redirect(url_for('login'))

@app.route('/register/asskerugian/tambah', methods=['GET', 'POST'])
def tambahasskerugian():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register ASS Kerugian/tambah_Register ASS Kerugian.html', username=session['username'])
        else:
            Tanggal= request.form['tanggal']
            Nama_Debitur = request.form['Nama Debitur']
            CAD_Premi = request.form['Premi']
            Jumlah_Agunan = request.form['Agunan']
            No_Polis= request.form['Polis']
            Tanggal_OB = request.form["Tanggal"]
            Premi= request.form["Premi"]
            keterangan = request.form['keterangan']

            
            cursor.execute('''INSERT INTO reg_ass_kerugian VALUES(%s,%s,%s,%s,%s,%s,%s,%s)''',(Tanggal, Nama_Debitur, CAD_Premi, Jumlah_Agunan, No_Polis, Tanggal_OB, Premi, keterangan ))
            conn.commit()
            cursor.close()
            return redirect(url_for('asskerugian'))

    return redirect(url_for('login'))

@app.route('/register/asskerugian/edit/<NoPolis>', methods=['GET', 'POST'])
def editasskerugian(NoPolis):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_ass_kerugian WHERE NoPolis = %s', (NoPolis,))
            editasskerugian = cursor.fetchone()
            return render_template('./Register ASS Kerugian/edit_Register ASS Kerugian.html', editasskerugian=editasskerugian)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['tanggal'] == '':
                new_tanggal = request.form['tanggal']
                cursor.execute('UPDATE IGNORE reg_ass_kerugian SET Tanggal = %s WHERE NoPolis = %s', (new_tanggal, NoPolis))
                conn.commit()
                
            if not request.form['Nama Debitur'] == '':
                new_Nama_Debitur = request.form['Nama Debitur']
                cursor.execute('UPDATE IGNORE reg_ass_kerugian SET NamaDebitur = %s WHERE NoPolis = %s', (new_Nama_Debitur, NoPolis))
                conn.commit()
                
            if not request.form['Premi'] == '':
                new_Premi = request.form['Premi']
                cursor.execute('UPDATE IGNORE reg_ass_kerugian SET CADPremi = %s WHERE NoPolis = %s', (new_Premi, NoPolis))
                conn.commit()
            
            if not request.form['Agunan'] == '':
                new_Agunan = request.form['Agunan']
                cursor.execute('UPDATE IGNORE reg_ass_kerugian SET JumlahAgunan = %s WHERE NoPolis = %s', (new_Agunan, NoPolis))
                conn.commit()

            if not request.form['Polis'] == '':
                new_Polis = request.form['Polis']
                cursor.execute('UPDATE IGNORE reg_ass_kerugian SET NoPolis = %s WHERE NoPolis = %s', (new_Polis, NoPolis))
                conn.commit()
            
            if not request.form['Tanggal'] == '':
                new_Tanggal = request.form['Tanggal']
                cursor.execute('UPDATE IGNORE reg_ass_kerugian SET TanggalOB = %s WHERE NoPolis = %s', (new_Tanggal, NoPolis))
                conn.commit()
            
            if not request.form['Premi'] == '':
                new_Premi = request.form['Premi']
                cursor.execute('UPDATE IGNORE reg_ass_kerugian SET Premi = %s WHERE NoPolis = %s', (new_Premi, NoPolis))
                conn.commit()
            
            if not request.form['keterangan'] == '':
                new_keterangan = request.form['keterangan']
                cursor.execute('UPDATE IGNORE reg_ass_kerugian SET Keterangan = %s WHERE NoPolis = %s', (new_keterangan, NoPolis))
                conn.commit()
                
            return redirect(url_for('asskerugian'))
    return redirect(url_for('login'))

@app.route('/register/blokirkecil', methods=['GET', 'POST'])
def blokirkecil():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_blok_kecil_program')
        blokirkecil = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register Blokir Kecil-Program/detail_Register Blokir Kecil-Program.html', blokirkecil=blokirkecil)  
    return redirect(url_for('login'))

@app.route('/register/blokirkecil/tambah', methods=['GET', 'POST'])
def tambahblokirkecil():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register Blokir Kecil-Program/tambah_Register Blokir Kecil-Program.html', username=session['username'])
        else:
            Nama= request.form['Nama']
            Rekening = request.form['Rekening']
            Jumlah = request.form['Jumlah']
            Tanggal = request.form['Tanggal']
            Buka= request.form['Buka']
            Paraf = request.form["Paraf"]
            keterangan = request.form['keterangan']

            
            cursor.execute('''INSERT INTO reg_blok_kecil_program VALUES(%s,%s,%s,%s,%s,%s,%s)''',(Nama, Rekening, Jumlah, Tanggal, Buka, Paraf, keterangan ))
            conn.commit()
            cursor.close()
            return redirect(url_for('blokirkecil'))

    return redirect(url_for('login'))

@app.route('/register/blokirkecil/edit/<NoRekening>', methods=['GET', 'POST'])
def editblokirkecil(NoRekening):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_blok_kecil_program WHERE NoRekening = %s', (NoRekening,))
            editblokirkecil = cursor.fetchone()
            return render_template('./Register Blokir Kecil-Program/edit_Register Blokir Kecil-Program.html', editblokirkecil=editblokirkecil)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['Nama'] == '':
                new_Nama = request.form['Nama']
                cursor.execute('UPDATE IGNORE reg_blok_kecil_program SET NamaDebitur = %s WHERE NoRekening = %s', (new_Nama, NoRekening))
                conn.commit()
                
            if not request.form['Rekening'] == '':
                new_Rekening = request.form['Rekening']
                cursor.execute('UPDATE IGNORE reg_blok_kecil_program SET NoRekening = %s WHERE NoRekening = %s', (new_Rekening, NoRekening))
                conn.commit()
                
            if not request.form['Jumlah'] == '':
                new_Jumlah = request.form['Jumlah']
                cursor.execute('UPDATE IGNORE reg_blok_kecil_program SET Jumlah = %s WHERE NoRekening = %s', (new_Jumlah, NoRekening))
                conn.commit()
            
            if not request.form['Tanggal'] == '':
                new_Tanggal = request.form['Tanggal']
                cursor.execute('UPDATE IGNORE reg_blok_kecil_program SET Tanggal = %s WHERE NoRekening = %s', (new_Tanggal, NoRekening))
                conn.commit()

            if not request.form['Buka'] == '':
                new_Buka = request.form['Buka']
                cursor.execute('UPDATE IGNORE reg_blok_kecil_program SET Buka = %s WHERE NoRekening = %s', (new_Buka, NoRekening))
                conn.commit()
            
            if not request.form['Paraf'] == '':
                new_Paraf = request.form['Paraf']
                cursor.execute('UPDATE IGNORE reg_blok_kecil_program SET Paraf = %s WHERE NoRekening = %s', (new_Paraf, NoRekening))
                conn.commit()
            
            if not request.form['keterangan'] == '':
                new_keterangan = request.form['keterangan']
                cursor.execute('UPDATE IGNORE reg_blok_kecil_program SET Keterangan = %s WHERE NoRekening = %s', (new_keterangan, NoRekening))
                conn.commit()
                
            return redirect(url_for('blokirkecil'))
    return redirect(url_for('login'))

@app.route('/register/ipk', methods=['GET', 'POST'])
def ipk():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM register_ipk')
        ipk = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register IPK/detail_RegisterIPK.html', ipk=ipk)  
    return redirect(url_for('login'))

@app.route('/register/ipk/tambah', methods=['GET', 'POST'])
def tambahipk():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register IPK/tambah_RegisterIPK.html', username=session['username'])
        else:
            IPK= request.form['IPK']
            Debitur = request.form['Debitur']
            Tanggal_Realisasi = request.form['Tanggal Realisasi']
            Tanggal_Jatuh_Tempo = request.form['Tanggal Jatuh Tempo']
            Permohonan= request.form['Permohonan']
            Putusan = request.form["Putusan"]
            Rekening = request.form["Rekening"]
            Fix_Rate = request.form["Fix/Rate"]
            keterangan = request.form['keterangan']

            
            cursor.execute('''INSERT INTO register_ipk VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(IPK, Debitur, Tanggal_Realisasi, Tanggal_Jatuh_Tempo, Permohonan, Putusan, Rekening, Fix_Rate, keterangan ))
            conn.commit()
            cursor.close()
            return redirect(url_for('ipk'))

    return redirect(url_for('login'))

@app.route('/register/ipk/edit/<NoIPK>', methods=['GET', 'POST'])
def editipk(NoIPK):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM register_ipk WHERE NoIPK = %s', (NoIPK,))
            editipk = cursor.fetchone()
            return render_template('./Register IPK/edit_RegisterIPK.html', editipk=editipk)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['IPK'] == '':
                new_IPK = request.form['IPK']
                cursor.execute('UPDATE IGNORE register_ipk SET NoIPK = %s WHERE NoIPK = %s', (new_IPK, NoIPK))
                conn.commit()
                
            if not request.form['Debitur'] == '':
                new_Debitur = request.form['Debitur']
                cursor.execute('UPDATE IGNORE register_ipk SET NamaDebitur = %s WHERE NoIPK = %s', (new_Debitur, NoIPK))
                conn.commit()
                
            if not request.form['Tanggal Realisasi'] == '':
                new_Tanggal_Realisasi = request.form['Tanggal Realisasi']
                cursor.execute('UPDATE IGNORE register_ipk SET TanggalRealisasi = %s WHERE NoIPK = %s', (new_Tanggal_Realisasi, NoIPK))
                conn.commit()
            
            if not request.form['Tanggal Jatuh Tempo'] == '':
                new_Tanggal_Jatuh_Tempo = request.form['Tanggal Jatuh Tempo']
                cursor.execute('UPDATE IGNORE register_ipk SET TanggalJatuhTempo = %s WHERE NoIPK = %s', (new_Tanggal_Jatuh_Tempo, NoIPK))
                conn.commit()

            if not request.form['Permohonan'] == '':
                new_Permohonan = request.form['Permohonan']
                cursor.execute('UPDATE IGNORE register_ipk SET NoPermohonan = %s WHERE NoIPK = %s', (new_Permohonan, NoIPK))
                conn.commit()
            
            if not request.form['Putusan'] == '':
                new_Putusan = request.form['Putusan']
                cursor.execute('UPDATE IGNORE register_ipk SET NoPutusan = %s WHERE NoIPK = %s', (new_Putusan, NoIPK))
                conn.commit()
            
            if not request.form['Rekening'] == '':
                new_Rekening = request.form['Rekening']
                cursor.execute('UPDATE IGNORE register_ipk SET NoRekening = %s WHERE NoIPK = %s', (new_Rekening, NoIPK))
                conn.commit()
            
            if not request.form['Fix/Rate'] == '':
                new_Fix_Rate = request.form['Fix/Rate']
                cursor.execute('UPDATE IGNORE register_ipk SET MasaFixRate = %s WHERE NoIPK = %s', (new_Fix_Rate, NoIPK))
                conn.commit()
            
            if not request.form['keterangan'] == '':
                new_keterangan = request.form['keterangan']
                cursor.execute('UPDATE IGNORE register_ipk SET Keterangan = %s WHERE NoIPK = %s', (new_keterangan, NoIPK))
                conn.commit()
                
            return redirect(url_for('ipk'))
    return redirect(url_for('login'))

@app.route('/register/jasakonsultasi', methods=['GET', 'POST'])
def jasakonsultasi():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_jasa_konsul')
        jasakonsultasi = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register Jasa Konsultasi/detail_Register Jasa Konsultasi.html', jasakonsultasi=jasakonsultasi)  
    return redirect(url_for('login'))

@app.route('/register/jasakonsultasi/tambah', methods=['GET', 'POST'])
def tambahjasakonsultasi():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register Jasa Konsultasi/tambah_Register Jasa Konsultasi.html', username=session['username'])
        else:
            Nama_No_Rekening= request.form['Nama + No. Rekening']
            Jasa_Sesuai_PTK = request.form['Jasa Sesuai PTK']
            Tanggal_Setor = request.form['Tanggal Setor']
            Jumlah_yang_disetor = request.form['Jumlah yang disetor']
            NPWP= request.form['NPWP']
            PPN = request.form["PPN"]
            PPN2 = request.form["PPN"]
            DPP = request.form["DPP"]


            cursor.execute('''INSERT INTO reg_jasa_konsul VALUES(%s,%s,%s,%s,%s,%s,%s,%s)''',(Nama_No_Rekening, Jasa_Sesuai_PTK, Tanggal_Setor, Jumlah_yang_disetor, NPWP, PPN, PPN2, DPP ))
            conn.commit()
            cursor.close()
            return redirect(url_for('jasakonsultasi'))

    return redirect(url_for('login'))

@app.route('/register/jasakonsultasi/edit/<NPWP>', methods=['GET', 'POST'])
def editjasakonsultasi(NPWP):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_jasa_konsul WHERE NPWP = %s', (NPWP,))
            editjasakonsultasi = cursor.fetchone()
            return render_template('./Register Jasa Konsultasi/edit_Register Jasa Konsultasi.html', editjasakonsultasi=editjasakonsultasi)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['Nama + No. Rekening'] == '':
                new_Nama_No_Rekening = request.form['Nama + No. Rekening']
                cursor.execute('UPDATE IGNORE reg_jasa_konsul SET Nama+NoRekening = %s WHERE NPWP = %s', (new_Nama_No_Rekening, NPWP))
                conn.commit()
                
            if not request.form['Jasa Sesuai PTK'] == '':
                new_Jasa_Sesuai_PTK = request.form['Jasa Sesuai PTK']
                cursor.execute('UPDATE IGNORE reg_jasa_konsul SET JasaSesuaiPTK = %s WHERE NPWP = %s', (new_Jasa_Sesuai_PTK, NPWP))
                conn.commit()
                
            if not request.form['Tanggal Setor'] == '':
                new_Tanggal_Setor = request.form['Tanggal Setor']
                cursor.execute('UPDATE IGNORE reg_jasa_konsul SET TanggalSetor = %s WHERE NPWP = %s', (new_Tanggal_Setor, NPWP))
                conn.commit()
            
            if not request.form['Jumlah yang disetor'] == '':
                new_Jumlah_yang_disetor = request.form['Jumlah yang disetor']
                cursor.execute('UPDATE IGNORE reg_jasa_konsul SET JumlahyangDiterima = %s WHERE NPWP = %s', (new_Jumlah_yang_disetor, NPWP))
                conn.commit()

            if not request.form['NPWP'] == '':
                new_NPWP = request.form['NPWP']
                cursor.execute('UPDATE IGNORE reg_jasa_konsul SET NPWP = %s WHERE NPWP = %s', (new_NPWP, NPWP))
                conn.commit()
            
            if not request.form['PPN'] == '':
                new_PPN = request.form['PPN']
                cursor.execute('UPDATE IGNORE reg_jasa_konsul SET PPN = %s WHERE NPWP = %s', (new_PPN, NPWP))
                conn.commit()
            
            if not request.form['PPN'] == '':
                new_Rekening = request.form['PPN']
                cursor.execute('UPDATE IGNORE reg_jasa_konsul SET PPN_ = %s WHERE NPWP = %s', (new_Rekening, NPWP))
                conn.commit()
            
            if not request.form['DPP'] == '':
                new_DPP = request.form['DPP']
                cursor.execute('UPDATE IGNORE reg_jasa_konsul SET DPP = %s WHERE NPWP = %s', (new_DPP, NPWP))
                conn.commit()
            return redirect(url_for('jasakonsultasi'))

    return redirect(url_for('login'))

@app.route('/register/bpkbpinjam', methods=['GET', 'POST'])
def bpkbpinjam():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_bpkb_pinjam')
        bpkbpinjam = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register BKPB yang dipinjam/detail_egister BKPB yang dipinjam.html', bpkbpinjam=bpkbpinjam)  
    return redirect(url_for('login'))

@app.route('/register/bpkbpinjam/tambah', methods=['GET', 'POST'])
def tambahbpkbpinjam():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register BKPB yang dipinjam/tambah_egister BKPB yang dipinjam.html', username=session['username'])
        else:
            Nama= request.form['Nama']
            Rekening = request.form['Rekening']
            Kredit = request.form['Kredit']
            BPKB = request.form['BPKB']
            VIA= request.form['VIA']
            Tanggal_Keluar = request.form["Tanggal_Keluar"]
            Tanggal_Kembali = request.form["Tanggal_Kembali"]

            cursor.execute('''INSERT INTO reg_bpkb_pinjam VALUES(%s,%s,%s,%s,%s,%s,%s)''',(Nama, Rekening, Kredit, BPKB, VIA, Tanggal_Keluar, Tanggal_Kembali ))
            conn.commit()
            cursor.close()
            return redirect(url_for('bpkbpinjam'))

    return redirect(url_for('login'))

@app.route('/register/bpkbpinjam/edit/<NoBPKB>', methods=['GET', 'POST'])
def editbpkbpinjam(NoBPKB):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_bpkb_pinjam WHERE NoBPKB = %s', (NoBPKB,))
            editbpkbpinjam = cursor.fetchone()
            return render_template('./Register BPKB yang dipinjam/edit_Register BPKB yang dipinjam.html', editbpkbpinjam=editbpkbpinjam)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['Nama'] == '':
                new_Nama = request.form['Nama']
                cursor.execute('UPDATE IGNORE reg_bpkb_pinjam SET NamaDebitur = %s WHERE NoBPKB = %s', (new_Nama, NoBPKB))
                conn.commit()
                
            if not request.form['Rekening'] == '':
                new_Rekening = request.form['Rekening']
                cursor.execute('UPDATE IGNORE reg_bpkb_pinjam SET NoRekening = %s WHERE NoBPKB = %s', (new_Rekening, NoBPKB))
                conn.commit()
                
            if not request.form['Kredit'] == '':
                new_Kredit = request.form['Kredit']
                cursor.execute('UPDATE IGNORE reg_bpkb_pinjam SET JenisKredit = %s WHERE NoBPKB = %s', (new_Kredit, NoBPKB))
                conn.commit()
            
            if not request.form['BPKB'] == '':
                new_BPKB = request.form['BPKB']
                cursor.execute('UPDATE IGNORE reg_bpkb_pinjam SET NoBPKB = %s WHERE NoBPKB = %s', (new_BPKB, NoBPKB))
                conn.commit()

            if not request.form['VIA'] == '':
                new_VIA = request.form['VIA']
                cursor.execute('UPDATE IGNORE reg_bpkb_pinjam SET ProsesVIA = %s WHERE NoBPKB = %s', (new_VIA, NoBPKB))
                conn.commit()
            
            if not request.form['Tanggal_Keluar'] == '':
                new_Tanggal_Keluar = request.form['Tanggal_Keluar']
                cursor.execute('UPDATE IGNORE reg_bpkb_pinjam SET PPN = %s WHERE TanggalKeluar = %s', (new_Tanggal_Keluar, NoBPKB))
                conn.commit()
            
            if not request.form['Tanggal_Kembali'] == '':
                new_Tanggal_Kembali = request.form['Tanggal_Kembali']
                cursor.execute('UPDATE IGNORE reg_bpkb_pinjam SET TanggalKembali = %s WHERE NoBPKB = %s', (new_Tanggal_Kembali, NoBPKB))
                conn.commit()
        
            return redirect(url_for('bpkbpinjam'))

    return redirect(url_for('login'))


@app.route('/logout')
def logout():
   session.clear()
   return redirect(url_for('login'))
  
if __name__ == '__main__':
    app.run(debug=True)