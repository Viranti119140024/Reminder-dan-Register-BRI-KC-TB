from flask import Flask, request, session, redirect, url_for, render_template, make_response, flash,Response
from flask_change_password.flask_change_password import ChangePassword, ChangePasswordForm
from flaskext.mysql import MySQL
from werkzeug.utils import secure_filename
from flask import flash
from werkzeug.security import generate_password_hash
from flask import send_from_directory
from flask import jsonify
import mysql.connector
import math
from datetime import datetime
from datetime import date
from flask import send_file
import datetime
import pymysql 
import os
import re 
import pdfkit
import locale


 
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')  # Mengatur lokasi folder upload
 
app.secret_key = 'cairocoders-ednalan'
 
flask_change_password = ChangePassword(min_password_length=10, rules=dict(long_password_override=2))
flask_change_password.init_app(app)

mysql = MySQL(app)


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

# Fungsi filter untuk mengonversi nilai ke format mata uang
def format_rupiah(value):
    locale.setlocale(locale.LC_ALL, 'id_ID')
    return locale.currency(value, grouping=True)

# Registrasi filter ke aplikasi Flask
app.jinja_env.filters['rupiah'] = format_rupiah


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
            session['level'] = user['level']
            
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
        level = request.form['level']
   
        cursor.execute('SELECT * FROM user WHERE username = %s', (username))
        account = cursor.fetchone()
        
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not nama or not password:
            msg = 'Please fill out the form!'
        else:
            
            cursor.execute('INSERT INTO user VALUES ( %s, %s, %s, %s, %s)', (id, username, nama, password, level)) 
            conn.commit()
   
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('registrasi.html', msg=msg)
  
@app.route('/kelolauser', methods=['GET', 'POST'])
def kelolauser():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM user')
        user = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('kelolauser.html', username=session['level'], user=user)
    
    return redirect(url_for('login'))

@app.route('/gantipassword/<username>', methods=['GET', 'POST'])
def gantipassword(username):
    if 'loggedin' in session or session['level'] == 'admin':
        if request.method == 'POST':
            username = username
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']

            # Validasi input
            if new_password != confirm_password:
                flash('Password baru dan konfirmasi password tidak cocok', 'error')
                return redirect(url_for('kelolauser'))

            # Lakukan perubahan password sesuai kebutuhan
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM user WHERE username = %s', (username,))
            user = cursor.fetchone()
            if user:
                # Update password user di database
                cursor.execute('UPDATE user SET password = %s WHERE username = %s', (new_password, username))
                conn.commit()
                flash('Password petugas berhasil diubah', 'success')
                return redirect(url_for('kelolauser'))
            else:
                flash('Username tidak ditemukan', 'error')
                return redirect(url_for('kelolauser'))
            cursor.close()
            conn.close()
            return redirect(url_for('kelolauser'))

        return render_template('gantipassword.html', username=session['level'],nama=username)
    else:
        return redirect(url_for('login'))

@app.route('/hapusakun/<username>', methods=['GET', 'POST'])
def hapusakun(username):
    if 'loggedin' in session or session['level'] == 'admin':
        username = username
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('DELETE FROM user WHERE username = %s', (username))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('kelolauser'))
    else:
        return redirect(url_for('login'))
   
@app.route('/beranda')
def home():
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # Menghitung jumlah notifikasi kenaikansukubunga
        cursor.execute("SELECT COUNT(*) FROM kenaikansukubunga")
        notif_result = cursor.fetchone()
        notif = notif_result['COUNT(*)'] if notif_result else 0

        # Menghitung jumlah notifikasi laporan yang belum terbaca
        cursor.execute("SELECT COUNT(*) FROM laporan WHERE status = 'unread'")
        unread_counts_result = cursor.fetchone()
        unread_counts = unread_counts_result['COUNT(*)'] if unread_counts_result else 0

        
       
        # Mengambil data user
        cursor.execute('SELECT * FROM user')
        user = cursor.fetchall()

        conn.commit()
        cursor.close()

        # Menyimpan nilai unread_counts dalam sesi
        session['unread_counts'] = unread_counts

        

        return render_template('beranda.html', username=session['level'], unread_count=notif, unread_counts=unread_counts,  user=user)

    return redirect(url_for('login'))


@app.route('/restrukturisasi')
def restrukturisasi():
    
    if 'loggedin' in session:
        if request.method == 'GET':
            date = datetime.datetime.now()
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
        cursor.execute('SELECT * FROM kenaikansukubunga NATURAL JOIN datadebitur ORDER BY kenaikansukubunga.namadebitur ASC')
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

            if not nama_debitur or not no_rekening or not jenis_kredit or not baki_debet or not rm or not jangkawaktu or not jadwal_pokok or not akad or not keterangan:
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


@app.route('/generate_pdf/<norek>', methods=['GET'])
def cetak_pdf(norek):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)                              
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM datadebitur WHERE norek = %s', (norek,))
        detaildebitur = cursor.fetchall()
        conn.commit()
        cursor.close()
        
        path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

        rendered_html = render_template('pdf.html', detaildebitur=detaildebitur)

        pdf = pdfkit.from_string(rendered_html,configuration=config)
        
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        #response.headers['Content-Disposition'] = 'attachment; filename=detail_debitur.pdf'
        return response

                                      
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
            return redirect(url_for('bpkbpinjam'))
        elif select == 'register9':
            return redirect(url_for('angkringan'))
        elif select == 'register10':
            return redirect(url_for('kmkwa'))
        elif select == 'register11':
            return redirect(url_for('kprbangun'))
        elif select == 'register12':
            return redirect(url_for('ndb'))
        elif select == 'register13':
            return redirect(url_for('pb1'))
        elif select == 'register14':
            return redirect(url_for('pdt'))
        elif select == 'register15':
            return redirect(url_for('pkkonsumer'))
        elif select == 'register16':
            return redirect(url_for('ppnd2'))
        elif select == 'register17':
            return redirect(url_for('ptk'))
        elif select == 'register18':
            return redirect(url_for('flpp'))
        elif select == 'register19':
            return redirect(url_for('roya'))
        elif select == 'register20':
            return redirect(url_for('royakkb'))
        elif select == 'register21':
            return redirect(url_for('slik'))
        elif select == 'register22':
            return redirect(url_for('spph'))
        elif select == 'register23':
            return redirect(url_for('tbnk'))
        elif select == 'register24':
            return redirect(url_for('ttsn'))
        elif select == 'register25':
            return redirect(url_for('verbek'))
        elif select == 'register26':
            return redirect(url_for('adk'))
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

@app.route('/register/ipkrestruk/hapus/<norek>', methods=['GET', 'POST'])
def hapusipkrestruk(norek):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM ipkrestruk WHERE norek = %s', (norek,)) 
            conn.commit()
            cursor.close()
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
                
            # Tambahkan logika update untuk kolom lainnya yang sesuai
            
            return redirect(url_for('ppnd'))
    return redirect(url_for('login'))

@app.route('/register/ppnd/hapus/<NoPPNdanTanggalPPN>', methods=['GET', 'POST'])
def hapusppnd(NoPPNdanTanggalPPN):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('DELETE IGNORE FROM ppnd WHERE NoPPNdanTanggalPPN = %s', (NoPPNdanTanggalPPN,))
            conn.commit()
            cursor.close()
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
    
@app.route('/register/ptkrestruk2penyelesaian/hapus/<NoPTK>', methods=['GET', 'POST'])
def hapusptkrestruk2penyelesaian(NoPTK):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM ptk_restruk2_penyelesaian WHERE NoPTK = %s', (NoPTK,))
            conn.commit()
            cursor.close()
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

@app.route('/register/asskerugian/hapus/<NoPolis>', methods=['GET', 'POST'])
def hapusasskerugian(NoPolis):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_ass_kerugian WHERE NoPolis = %s', (NoPolis,))
            conn.commit()
            cursor.close()
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

@app.route('/register/blokirkecil/hapus/<NoRekening>', methods=['GET', 'POST'])
def hapusblokirkecil(NoRekening):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_blok_kecil_program WHERE NoRekening = %s', (NoRekening,))
            conn.commit()
            cursor.close()
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

@app.route('/register/ipk/hapus/<NoIPK>', methods=['GET', 'POST'])
def hapusipk(NoIPK):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM register_ipk WHERE NoIPK = %s', (NoIPK,))
            conn.commit()
            cursor.close()
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
            PPN2 = request.form['PPN2']
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
                cursor.execute('UPDATE IGNORE reg_jasa_konsul SET NamaNoRekening = %s WHERE NPWP = %s', (new_Nama_No_Rekening, NPWP))
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
            
            if not request.form['PPN2'] == '':
                new_PPN2 = request.form['PPN2']
                cursor.execute('UPDATE IGNORE reg_jasa_konsul SET PPN_ = %s WHERE NPWP = %s', (new_PPN2, NPWP))
                conn.commit()
            
            if not request.form['DPP'] == '':
                new_DPP = request.form['DPP']
                cursor.execute('UPDATE IGNORE reg_jasa_konsul SET DPP = %s WHERE NPWP = %s', (new_DPP, NPWP))
                conn.commit()
            return redirect(url_for('jasakonsultasi'))

    return redirect(url_for('login'))

@app.route('/register/jasakonsultasi/hapus/<NPWP>', methods=['GET', 'POST'])
def hapujasakonsultasi(NPWP):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_jasa_konsul WHERE NPWP = %s', (NPWP,))
            conn.commit()
            cursor.close()
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
        return render_template('./Register BPKB yang dipinjam/detail_Register BPKB yang dipinjam.html', bpkbpinjam=bpkbpinjam)  
    return redirect(url_for('login'))

@app.route('/register/bpkbpinjam/tambah', methods=['GET', 'POST'])
def tambahbpkbpinjam():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register BPKB yang dipinjam/tambah_Register BPKB yang dipinjam.html', username=session['username'])
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
                cursor.execute('UPDATE IGNORE reg_bpkb_pinjam SET TanggalKeluar = %s WHERE NoBPKB = %s', (new_Tanggal_Keluar, NoBPKB))
                conn.commit()
            
            if not request.form['Tanggal_Kembali'] == '':
                new_Tanggal_Kembali = request.form['Tanggal_Kembali']
                cursor.execute('UPDATE IGNORE reg_bpkb_pinjam SET TanggalKembali = %s WHERE NoBPKB = %s', (new_Tanggal_Kembali, NoBPKB))
                conn.commit()
        
            return redirect(url_for('bpkbpinjam'))

    return redirect(url_for('login'))

@app.route('/register/bpkbpinjam/hapus/<NoBPKB>', methods=['GET', 'POST'])
def hapusbpkbpinjam(NoBPKB):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_bpkb_pinjam WHERE NoBPKB = %s', (NoBPKB,))
            conn.commit()
            cursor.close()
            return redirect(url_for('bpkbpinjam'))
    return redirect(url_for('login'))

@app.route('/register/angkringan', methods=['GET', 'POST'])
def angkringan():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_kkb_cop_angkr')
        angkringan = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register KKB & COP ANGKRINGAN/detail_Register_KKB_&_COP_ANGKRINGAN.html', angkringan=angkringan)  
    return redirect(url_for('login'))

@app.route('/register/angkringan/tambah', methods=['GET', 'POST'])
def tambahangkringan():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register KKB & COP ANGKRINGAN/tambah_Register_KKB_&_COP_ANGKRINGAN.html', username=session['username'])
        else:
            Debitur= request.form['Debitur']
            tanggal = request.form['tanggal']
            Plafond = request.form['Plafond']
            Waktu = request.form['Waktu']
            Angsuran_Pokok= request.form['Angsuran Pokok']
            Angsuran_Bunga = request.form["Angsuran Bunga"]
            No_Rekening = request.form["No Rekening"]
            keterangan = request.form["keterangan"]

            cursor.execute('''INSERT INTO reg_kkb_cop_angkr VALUES(%s,%s,%s,%s,%s,%s,%s,%s)''',(Debitur, tanggal, Plafond, Waktu, Angsuran_Pokok, Angsuran_Bunga, No_Rekening, keterangan  ))
            conn.commit()
            cursor.close()
            return redirect(url_for('angkringan'))

    return redirect(url_for('login'))

@app.route('/register/angkringan/edit/<NoRekening>', methods=['GET', 'POST'])
def editangkringan(NoRekening):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_kkb_cop_angkr WHERE NoRekening = %s', (NoRekening,))
            editangkringan = cursor.fetchone()
            return render_template('./Register KKB & COP ANGKRINGAN/edit_Register_KKB_&_COP_ANGKRINGAN.html', editangkringan=editangkringan)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['Debitur'] == '':
                new_Debitur = request.form['Debitur']
                cursor.execute('UPDATE IGNORE reg_kkb_cop_angkr SET NamaDebitur = %s WHERE NoRekening = %s', (new_Debitur, NoRekening))
                conn.commit()
                
            if not request.form['tanggal'] == '':
                new_tanggal = request.form['tanggal']
                cursor.execute('UPDATE IGNORE reg_kkb_cop_angkr SET TanggalRealisasi = %s WHERE NoRekening = %s', (new_tanggal, NoRekening))
                conn.commit()
                
            if not request.form['Plafond'] == '':
                new_Plafond = request.form['Plafond']
                cursor.execute('UPDATE IGNORE reg_kkb_cop_angkr SET PlafondRP = %s WHERE NoRekening = %s', (new_Plafond, NoRekening))
                conn.commit()
            
            if not request.form['Waktu'] == '':
                new_Waktu = request.form['Waktu']
                cursor.execute('UPDATE IGNORE reg_kkb_cop_angkr SET JangkaWaktu = %s WHERE NoRekening = %s', (new_Waktu, NoRekening))
                conn.commit()

            if not request.form['Angsuran Pokok'] == '':
                new_Angsuran_Pokok = request.form['Angsuran Pokok']
                cursor.execute('UPDATE IGNORE reg_kkb_cop_angkr SET AngsuranPokok = %s WHERE NoRekening = %s', (new_Angsuran_Pokok, NoRekening))
                conn.commit()
            
            if not request.form['Angsuran Bunga'] == '':
                new_Angsuran_Bunga = request.form['Angsuran Bunga']
                cursor.execute('UPDATE IGNORE reg_kkb_cop_angkr SET AngsuranBunga = %s WHERE NoRekening = %s', (new_Angsuran_Bunga, NoRekening))
                conn.commit()
            
            if not request.form['No Rekening'] == '':
                new_No_Rekening = request.form['No Rekening']
                cursor.execute('UPDATE IGNORE reg_kkb_cop_angkr SET NoRekening = %s WHERE NoRekening = %s', (new_No_Rekening, NoRekening))
                conn.commit()
            
            if not request.form['keterangan'] == '':
                new_keterangan = request.form['keterangan']
                cursor.execute('UPDATE IGNORE reg_kkb_cop_angkr SET Keterangan = %s WHERE NoRekening = %s', (new_keterangan, NoRekening))
                conn.commit()
        
            return redirect(url_for('angkringan'))

    return redirect(url_for('login'))

@app.route('/register/angkringan/hapus/<NoRekening>', methods=['GET', 'POST'])
def hapusangkringan(NoRekening):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_kkb_cop_angkr WHERE NoRekening = %s', (NoRekening,))
            conn.commit()
            cursor.close()
            return redirect(url_for('angkringan'))
    return redirect(url_for('login'))

@app.route('/register/kmkwa', methods=['GET', 'POST'])
def kmkwa():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_kmk_wa')
        kmkwa = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register KMK_WA/detail_RegisterKMK_WA.html', kmkwa=kmkwa)  
    return redirect(url_for('login'))

@app.route('/register/kmkwa/tambah', methods=['GET', 'POST'])
def tambahkmkwa():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register KMK_WA/tambah_RegisterKMK_WA.html', username=session['username'])
        else:
            keterangan= request.form['keterangan']
            rp = request.form['rp']
            Plafond = request.form['Plafond']
            Os_Awal = request.form['Os Awal']
            tanggal= request.form['tanggal']
            keterangan = request.form["keterangan"]
            Pencairan = request.form["Pencairan"]
            keterangan = request.form["keterangan"]
            Nilai_Pembayaran = request.form["Nilai Pembayaran"]
            OS_Setelah_Pembayaran = request.form["OS Setelah Pembayaran"]
            OS_Brinets = request.form["OS Brinets"]
            Sisa_Tagihan = request.form["Sisa Tagihan"]
            Keterangan = request.form["Keterangan"]

            cursor.execute('''INSERT INTO reg_kmk_wa VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(keterangan, rp, Plafond, Os_Awal, tanggal, keterangan, Pencairan, keterangan, Nilai_Pembayaran, OS_Setelah_Pembayaran, OS_Brinets, Sisa_Tagihan, Keterangan  ))
            conn.commit()
            cursor.close()
            return redirect(url_for('kmkwa'))

    return redirect(url_for('login'))

@app.route('/register/kmkwa/edit/<SPK_PO_Kontrak_Kerja>', methods=['GET', 'POST'])
def editkmkwa(SPK_PO_Kontrak_Kerja):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_kmk_wa WHERE SPK_PO_KontrakKerja = %s', (SPK_PO_Kontrak_Kerja))
            editkmkwa = cursor.fetchone()
            return render_template('./Register KMK_WA/edit_RegisterKMK_WA.html', editkmkwa=editkmkwa)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['SPK/PO/Kontrak Kerja'] == '':
                new_keterangan= request.form['SPK/PO/Kontrak Kerja']
                cursor.execute('UPDATE IGNORE reg_kmk_wa SET SPK_PO_KontrakKerja = %s WHERE SPK_PO_KontrakKerja = %s', (new_keterangan, SPK_PO_Kontrak_Kerja))
                conn.commit()
                
            if not request.form['rp'] == '':
                new_rp = request.form['rp']
                cursor.execute('UPDATE IGNORE reg_kmk_wa SET NilaiProyek = %s WHERE SPK_PO_KontrakKerja = %s', (new_rp, SPK_PO_Kontrak_Kerja))
                conn.commit()
                
            if not request.form['PlafondRp'] == '':
                new_Plafond = request.form['PlafondRp']
                cursor.execute('UPDATE IGNORE reg_kmk_wa SET PlafondRP = %s WHERE SPK_PO_KontrakKerja = %s', (new_Plafond, SPK_PO_Kontrak_Kerja))
                conn.commit()
            
            if not request.form['Os Awal'] == '':
                new_Os_Awal = request.form['Os Awal']
                cursor.execute('UPDATE IGNORE reg_kmk_wa SET osAwal = %s WHERE SPK_PO_KontrakKerja = %s', (new_Os_Awal, SPK_PO_Kontrak_Kerja))
                conn.commit()

            if not request.form['tanggal'] == '':
                new_tanggal = request.form['tanggal']
                cursor.execute('UPDATE IGNORE reg_kmk_wa SET TanggalPencairan = %s WHERE SPK_PO_KontrakKerja = %s', (new_tanggal, SPK_PO_Kontrak_Kerja))
                conn.commit()
            
            if not request.form['Pencairan'] == '':
                new_keterangan = request.form['Pencairan']
                cursor.execute('UPDATE IGNORE reg_kmk_wa SET DokSumberPencairan = %s WHERE SPK_PO_KontrakKerja = %s', (new_keterangan, SPK_PO_Kontrak_Kerja))
                conn.commit()
            
            if not request.form['Pencairan'] == '':
                new_Pencairan = request.form['Pencairan']
                cursor.execute('UPDATE IGNORE reg_kmk_wa SET NilaiPencairan = %s WHERE SPK_PO_KontrakKerja = %s', (new_Pencairan, SPK_PO_Kontrak_Kerja))
                conn.commit()
            
            if not request.form['sumber_Pembayaran'] == '':
                new_keterangan = request.form['sumber_Pembayaran']
                cursor.execute('UPDATE IGNORE reg_kmk_wa SET DokSumberPembayaran = %s WHERE SPK_PO_KontrakKerja = %s', (new_keterangan, SPK_PO_Kontrak_Kerja))
                conn.commit()
            
            if not request.form['Nilai Pembayaran'] == '':
                new_Nilai_Pembayaran = request.form['Nilai Pembayaran']
                cursor.execute('UPDATE IGNORE reg_kmk_wa SET NilaiPembayaran = %s WHERE SPK_PO_KontrakKerja = %s', (new_Nilai_Pembayaran, SPK_PO_Kontrak_Kerja))
                conn.commit()
            
            if not request.form['OS Setelah Pembayaran'] == '':
                new_OS_Setelah_Pembayaran = request.form['OS Setelah Pembayaran']
                cursor.execute('UPDATE IGNORE reg_kmk_wa SET OSSetelahPembayaran = %s WHERE SPK_PO_KontrakKerja = %s', (new_OS_Setelah_Pembayaran, SPK_PO_Kontrak_Kerja))
                conn.commit()
            
            if not request.form['OS Brinets'] == '':
                new_OS_Brinets = request.form['OS Brinets']
                cursor.execute('UPDATE IGNORE reg_kmk_wa SET OSBrinets = %s WHERE SPK_PO_KontrakKerja = %s', (new_OS_Brinets, SPK_PO_Kontrak_Kerja))
                conn.commit()
            
            if not request.form['Sisa Tagihan'] == '':
                new_Sisa_Tagihan = request.form['Sisa Tagihan']
                cursor.execute('UPDATE IGNORE reg_kmk_wa SET SisaTagihan = %s WHERE SPK_PO_KontrakKerja = %s', (new_Sisa_Tagihan, SPK_PO_Kontrak_Kerja))
                conn.commit()

            if not request.form['Keterangan'] == '':
                new_Keterangan = request.form['Keterangan']
                cursor.execute('UPDATE IGNORE reg_kmk_wa SET Keterangan = %s WHERE SPK_PO_KontrakKerja = %s', (new_Keterangan, SPK_PO_Kontrak_Kerja))
                conn.commit()
        
            return redirect(url_for('kmkwa'))

    return redirect(url_for('login'))

@app.route('/register/kmkwa/hapus/<SPK_PO_Kontrak_Kerja>', methods=['GET', 'POST'])
def hapuskmkwa(SPK_PO_Kontrak_Kerja):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_kmk_wa WHERE SPK_PO_KontrakKerja = %s', (SPK_PO_Kontrak_Kerja,))
            conn.commit()
            cursor.close()
            return redirect(url_for('kmkwa'))
    return redirect(url_for('login'))

@app.route('/register/kprbangun', methods=['GET', 'POST'])
def kprbangun():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_kpr_bangun')
        kprbangun = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register KPR Bangun/detail_RegisterKPRBangun.html', kprbangun=kprbangun)  
    return redirect(url_for('login'))

@app.route('/register/kprbangun/tambah', methods=['GET', 'POST'])
def tambahkprbangun():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register KPR Bangun/tambah_RegisterKPRBangun.html', username=session['username'])
        else:
            np= request.form['np']
            tanggal = request.form['tanggal']
            Nama_Debitur = request.form['Nama Debitur']
            Jabatan_Pemutus = request.form['Jabatan Pemutus']
            Nama_Pemutus= request.form['Nama Pemutus']
            keterangan = request.form["keterangan"]
            keterangan = request.form["keterangan"]
            tanggal = request.form["tanggal"]

            cursor.execute('''INSERT INTO reg_kpr_bangun VALUES(%s,%s,%s,%s,%s,%s,%s,%s)''',(np, tanggal, Nama_Debitur, Jabatan_Pemutus, Nama_Pemutus, keterangan, keterangan, tanggal ))
            conn.commit()
            cursor.close()
            return redirect(url_for('kprbangun'))

    return redirect(url_for('login'))

@app.route('/register/kprbangun/edit/<NoPutusan>', methods=['GET', 'POST'])
def editkprbangun(NoPutusan):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_kpr_bangun WHERE NoPutusan = %s', (NoPutusan))
            editkprbangun = cursor.fetchone()
            return render_template('./Register KPR Bangun/edit_RegisterKPRBangun.html', editkprbangun=editkprbangun)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['np'] == '':
                new_np= request.form['np']
                cursor.execute('UPDATE IGNORE reg_kpr_bangun SET NoPutusan = %s WHERE NoPutusan = %s', (new_np, NoPutusan))
                conn.commit()
                
            if not request.form['tanggal'] == '':
                new_tanggal = request.form['tanggal']
                cursor.execute('UPDATE IGNORE reg_kpr_bangun SET TanggalPutusan = %s WHERE NoPutusan = %s', (new_tanggal, NoPutusan))
                conn.commit()
                
            if not request.form['Nama Debitur'] == '':
                new_Nama_Debitur = request.form['Nama Debitur']
                cursor.execute('UPDATE IGNORE reg_kpr_bangun SET NamaDebitur = %s WHERE NoPutusan = %s', (new_Nama_Debitur, NoPutusan))
                conn.commit()
            
            if not request.form['Jabatan Pemutus'] == '':
                new_Jabatan_Pemutus = request.form['Jabatan Pemutus']
                cursor.execute('UPDATE IGNORE reg_kpr_bangun SET JabatanPemutus = %s WHERE NoPutusan = %s', (new_Jabatan_Pemutus, NoPutusan))
                conn.commit()

            if not request.form['Nama Pemutus'] == '':
                new_Nama_Pemutus = request.form['Nama Pemutus']
                cursor.execute('UPDATE IGNORE reg_kpr_bangun SET NamaPemutus = %s WHERE NoPutusan = %s', (new_Nama_Pemutus, NoPutusan))
                conn.commit()

            if not request.form['Nama Perumahan'] == '':
                new_Nama_Perumahan = request.form['Nama Perumahan']
                cursor.execute('UPDATE IGNORE reg_kpr_bangun SET NamaPerumahan = %s WHERE NoPutusan = %s', (new_Nama_Perumahan, NoPutusan))
                conn.commit()
            
            if not request.form['keterangan'] == '':
                new_keterangan = request.form['keterangan']
                cursor.execute('UPDATE IGNORE reg_kpr_bangun SET NamaPemutus = %s WHERE NoPutusan = %s', (new_keterangan, NoPutusan))
                conn.commit()
            
            if not request.form['keterangan'] == '':
                new_keterangan = request.form['keterangan']
                cursor.execute('UPDATE IGNORE reg_kpr_bangun SET Keterangan = %s WHERE NoPutusan = %s', (new_keterangan, NoPutusan))
                conn.commit()
            
            if not request.form['tanggal'] == '':
                new_tanggal = request.form['tanggal']
                cursor.execute('UPDATE IGNORE reg_kpr_bangun SET TanggalOB = %s WHERE NoPutusan = %s', (new_tanggal, NoPutusan))
                conn.commit()
            
            return redirect(url_for('kprbangun'))

    return redirect(url_for('login'))

@app.route('/register/kprbangun/hapus/<NoPutusan>', methods=['GET', 'POST'])
def hapuskprbangun(NoPutusan):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_kpr_bangun WHERE NoPutusan = %s', (NoPutusan,))
            conn.commit()
            cursor.close()
            return redirect(url_for('kprbangun'))
    return redirect(url_for('login'))

@app.route('/register/ndb', methods=['GET', 'POST'])
def ndb():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_nas_bridyna')
        ndb = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register NAS dan Bridyna/detail_Register NAS dan Bridyna.html', ndb=ndb)  
    return redirect(url_for('login'))

@app.route('/register/ndb/tambah', methods=['GET', 'POST'])
def tambahndb():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register NAS dan Bridyna/tambah_Register NAS dan Bridyna.html', username=session['username'])
        else:
            Nama_Debitur= request.form['Nama Debitur']
            Rek_Pinjaman = request.form['Rek Pinjaman']
            tanggal = request.form['tanggal']
            Rekening_Giro = request.form['Rekening Giro']
            NAS_Bridyna= request.form['NAS / Bridyna']
            Keterangan = request.form["Keterangan"]

            cursor.execute('''INSERT INTO reg_nas_bridyna VALUES(%s,%s,%s,%s,%s,%s)''',(Nama_Debitur, Rek_Pinjaman, tanggal, Rekening_Giro, NAS_Bridyna, Keterangan ))
            conn.commit()
            cursor.close()
            return redirect(url_for('ndb'))

    return redirect(url_for('login'))

@app.route('/register/ndb/edit/<RekeningGiro>', methods=['GET', 'POST'])
def editndb(RekeningGiro):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_nas_bridyna WHERE RekeningGiro = %s', (RekeningGiro))
            editndb = cursor.fetchone()
            return render_template('./Register NAS dan Bridyna/edit_Register NAS dan Bridyna.html', editndb=editndb)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['Nama Debitur'] == '':
                new_Nama_Debitur= request.form['Nama Debitur']
                cursor.execute('UPDATE IGNORE reg_nas_bridyna SET NamaDebitur = %s WHERE RekeningGiro = %s', (new_Nama_Debitur, RekeningGiro))
                conn.commit()
                
            if not request.form['Rek Pinjaman'] == '':
                new_Rek_Pinjaman = request.form['Rek Pinjaman']
                cursor.execute('UPDATE IGNORE reg_nas_bridyna SET RekPinjaman = %s WHERE RekeningGiro = %s', (new_Rek_Pinjaman, RekeningGiro))
                conn.commit()
                
            if not request.form['tanggal'] == '':
                new_tanggal = request.form['tanggal']
                cursor.execute('UPDATE IGNORE reg_nas_bridyna SET Tanggal = %s WHERE RekeningGiro = %s', (new_tanggal, RekeningGiro))
                conn.commit()
            
            if not request.form['Rekening Giro'] == '':
                new_Rekening_Giro = request.form['Rekening Giro']
                cursor.execute('UPDATE IGNORE reg_nas_bridyna SET RekeningGiro = %s WHERE RekeningGiro = %s', (new_Rekening_Giro, RekeningGiro))
                conn.commit()

            if not request.form['NAS / Bridyna'] == '':
                new_NAS_Bridyna = request.form['NAS / Bridyna']
                cursor.execute('UPDATE IGNORE reg_nas_bridyna SET NasBridyna = %s WHERE RekeningGiro = %s', (new_NAS_Bridyna, RekeningGiro))
                conn.commit()
            
            if not request.form['Keterangan'] == '':
                new_Keterangan = request.form['Keterangan']
                cursor.execute('UPDATE IGNORE reg_nas_bridyna SET Keterangan = %s WHERE RekeningGiro = %s', (new_Keterangan, RekeningGiro))
                conn.commit()
            
            return redirect(url_for('ndb'))

    return redirect(url_for('login'))

@app.route('/register/ndb/hapus/<RekeningGiro>', methods=['GET', 'POST'])
def hapusndb(RekeningGiro):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_nas_bridyna WHERE RekeningGiro = %s', (RekeningGiro,))
            conn.commit()
            cursor.close()
            return redirect(url_for('ndb'))
    return redirect(url_for('login'))

@app.route('/register/pb1', methods=['GET', 'POST'])
def pb1():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_peminjam_berkas1')
        pb1 = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register Peminjaman Berkas 1/detail_Register Peminjaman Berkas 1.html', pb1=pb1)  
    return redirect(url_for('login'))

@app.route('/register/pb1/tambah', methods=['GET', 'POST'])
def tambahpb1():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register Peminjaman Berkas 1/tambah_Register Peminjaman Berkas 1.html', username=session['username'])
        else:
            tanggal= request.form['tanggal']
            Nama_Debitur = request.form['Nama Debitur']
            Dok_yag_dipinjam = request.form['Dok yag dipinjam']
            Nama_Peminjam = request.form['Nama Peminjam']
            Keperluan= request.form['Keperluan']
            tanggal = request.form["tanggal"]
            Kelengkapan_Dok = request.form['Kelengkapan Dok']
            Pinjam = request.form['Pinjam']
            Kembali = request.form['Kembali']

            cursor.execute('''INSERT INTO reg_peminjam_berkas1 VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(tanggal, Nama_Debitur, Dok_yag_dipinjam, Nama_Peminjam, Keperluan, tanggal, Kelengkapan_Dok, Pinjam, Kembali ))
            conn.commit()
            cursor.close()
            return redirect(url_for('pb1'))

    return redirect(url_for('login'))

@app.route('/register/pb1/edit/<NamaDebitur>', methods=['GET', 'POST'])
def editpb1(NamaDebitur):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_peminjam_berkas1 WHERE NamaDebitur = %s', (NamaDebitur))
            editpb1 = cursor.fetchone()
            return render_template('./Register Peminjaman Berkas 1/edit_Register Peminjaman Berkas 1.html', editpb1=editpb1)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['tanggal'] == '':
                new_tanggal = request.form['tanggal']
                cursor.execute('UPDATE IGNORE reg_peminjam_berkas1 SET Tanggal = %s WHERE NamaDebitur = %s', (new_tanggal, NamaDebitur))
                conn.commit()
                
            if not request.form['Nama Debitur'] == '':
                new_Nama_Debitur = request.form['Nama Debitur']
                cursor.execute('UPDATE IGNORE reg_peminjam_berkas1 SET NamaDebitur = %s WHERE NamaDebitur = %s', (new_Nama_Debitur, NamaDebitur))
                conn.commit()
                
            if not request.form['Dok yag dipinjam'] == '':
                new_Dok_yag_dipinjam = request.form['Dok yag dipinjam']
                cursor.execute('UPDATE IGNORE reg_peminjam_berkas1 SET DokyangDipinjam = %s WHERE NamaDebitur = %s', (new_Dok_yag_dipinjam, NamaDebitur))
                conn.commit()
            
            if not request.form['Nama Peminjam'] == '':
                new_Nama_Peminjam = request.form['Nama Peminjam']
                cursor.execute('UPDATE IGNORE reg_peminjam_berkas1 SET NamaPeminjam = %s WHERE NamaDebitur = %s', (new_Nama_Peminjam, NamaDebitur))
                conn.commit()

            if not request.form['Keperluan'] == '':
                new_Keperluan = request.form['Keperluan']
                cursor.execute('UPDATE IGNORE reg_peminjam_berkas1 SET Keperluan = %s WHERE NamaDebitur = %s', (new_Keperluan, NamaDebitur))
                conn.commit()
            
            if not request.form['tanggal'] == '':
                new_tanggal = request.form['tanggal']
                cursor.execute('UPDATE IGNORE reg_peminjam_berkas1 SET TanggalKembali = %s WHERE NamaDebitur = %s', (new_tanggal, NamaDebitur))
                conn.commit()
            
            if not request.form['Kelengkapan Dok'] == '':
                new_Kelengkapan_Dok = request.form['Kelengkapan Dok']
                cursor.execute('UPDATE IGNORE reg_peminjam_berkas1 SET KelengkapanDokumen = %s WHERE NamaDebitur = %s', (new_Kelengkapan_Dok, NamaDebitur))
                conn.commit()
            
            if not request.form['Pinjam'] == '':
                new_Pinjam = request.form['Pinjam']
                cursor.execute('UPDATE IGNORE reg_peminjam_berkas1 SET Pinjamparaf = %s WHERE NamaDebitur = %s', (new_Pinjam, NamaDebitur))
                conn.commit()

            if not request.form['Kembali'] == '':
                new_Kembali = request.form['Kembali']
                cursor.execute('UPDATE IGNORE reg_peminjam_berkas1 SET Kembaliparaf = %s WHERE NamaDebitur = %s', (new_Kembali, NamaDebitur))
                conn.commit()
            
            return redirect(url_for('pb1'))

    return redirect(url_for('login'))

@app.route('/register/pb1/hapus/<NamaDebitur>', methods=['GET', 'POST'])
def hapuspb1(NamaDebitur):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_peminjam_berkas1 WHERE NamaDebitur = %s', (NamaDebitur,))
            conn.commit()
            cursor.close()
            return redirect(url_for('pb1'))
    return redirect(url_for('login'))

@app.route('/register/pdt', methods=['GET', 'POST'])
def pdt():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_pencair_dana_ditahan')
        pdt = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register Pencairan Dana Ditahan/detail_RegisterPencairanDanaDitahan.html', pdt=pdt)  
    return redirect(url_for('login'))

@app.route('/register/pdt/tambah', methods=['GET', 'POST'])
def tambahpdt():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register Pencairan Dana Ditahan/tambah_RegisterPencairanDanaDitahan.html', username=session['username'])
        else:
            Nama_Debitur= request.form['Nama Debitur']
            No_Rekening = request.form['No. Rekening']
            Plafond = request.form['Plafond']
            Tanggal = request.form['tanggal']
            Nama_Developer = request.form['Nama Developer']
            Nominal= request.form['Nominal']
            Tanggal_di_Buku = request.form["Tanggal di Buku"]
            keterangan = request.form['keterangan']

            cursor.execute('''INSERT INTO reg_pencair_dana_ditahan VALUES(%s,%s,%s,%s,%s,%s,%s,%s)''',(Nama_Debitur, No_Rekening, Plafond, Tanggal, Nama_Developer, Nominal, Tanggal_di_Buku, keterangan ))
            conn.commit()
            cursor.close()
            return redirect(url_for('pdt'))

    return redirect(url_for('login'))

@app.route('/register/pdt/edit/<NoRekening>', methods=['GET', 'POST'])
def editpdt(NoRekening):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_pencair_dana_ditahan WHERE NoRekening = %s', (NoRekening))
            editpdt = cursor.fetchone()
            return render_template('./Register Pencairan Dana Ditahan/edit_RegisterPencairanDanaDitahan.html', editpdt=editpdt)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['Nama Debitur'] == '':
                new_Nama_Debitur = request.form['Nama Debitur']
                cursor.execute('UPDATE IGNORE reg_pencair_dana_ditahan SET NamaDebitur = %s WHERE NoRekening = %s', (new_Nama_Debitur, NoRekening))
                conn.commit()
                
            if not request.form['No. Rekening'] == '':
                new_No_Rekening = request.form['No. Rekening']
                cursor.execute('UPDATE IGNORE reg_pencair_dana_ditahan SET NoRekening = %s WHERE NoRekening = %s', (new_No_Rekening, NoRekening))
                conn.commit()
                
            if not request.form['Plafond'] == '':
                new_Plafond = request.form['Plafond']
                cursor.execute('UPDATE IGNORE reg_pencair_dana_ditahan SET Plafond = %s WHERE NoRekening = %s', (new_Plafond, NoRekening))
                conn.commit()
            
            if not request.form['tanggal'] == '':
                new_Tanggal = request.form['tanggal']
                cursor.execute('UPDATE IGNORE reg_pencair_dana_ditahan SET TanggalAkad = %s WHERE NoRekening = %s', (new_Tanggal, NoRekening))
                conn.commit()

            if not request.form['Nama Developer'] == '':
                new_Nama_Developer = request.form['Nama Developer']
                cursor.execute('UPDATE IGNORE reg_pencair_dana_ditahan SET NamaDeveloper_Penjual = %s WHERE NoRekening = %s', (new_Nama_Developer, NoRekening))
                conn.commit()
            
            if not request.form['Nominal'] == '':
                new_Nominal = request.form['Nominal']
                cursor.execute('UPDATE IGNORE reg_pencair_dana_ditahan SET Nominal = %s WHERE NoRekening = %s', (new_Nominal, NoRekening))
                conn.commit()
            
            if not request.form['Tanggal di Buku'] == '':
                new_Tanggal_di_Buku = request.form['Tanggal di Buku']
                cursor.execute('UPDATE IGNORE reg_pencair_dana_ditahan SET TanggaldiBuku = %s WHERE NoRekening = %s', (new_Tanggal_di_Buku, NoRekening))
                conn.commit()
            
            if not request.form['keterangan'] == '':
                new_keterangan = request.form['keterangan']
                cursor.execute('UPDATE IGNORE reg_pencair_dana_ditahan SET Keterangan = %s WHERE NoRekening = %s', (new_keterangan, NoRekening))
                conn.commit()
            
            return redirect(url_for('pdt'))

    return redirect(url_for('login'))

@app.route('/register/pdt/hapus/<NoRekening>', methods=['GET', 'POST'])
def hapuspdt(NoRekening):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_pencair_dana_ditahan WHERE NoRekening = %s', (NoRekening,))
            conn.commit()
            cursor.close()
            return redirect(url_for('pdt'))
    return redirect(url_for('login'))

@app.route('/register/pkkonsumer', methods=['GET', 'POST'])
def pkkonsumer():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_ptk_konsumer')
        pkkonsumer = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register PK Konsumer/detail_RegisterPK_Konsumer.html', pkkonsumer=pkkonsumer)  
    return redirect(url_for('login'))

@app.route('/register/pkkonsumer/tambah', methods=['GET', 'POST'])
def tambahpkkonsumer():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register PK Konsumer/tambah_RegisterPK_Konsumer.html', username=session['username'])
        else:
            Putusan= request.form['Putusan']
            tanggal = request.form['tanggal']
            Nama_Debitur = request.form['Nama Debitur']
            Pemutus = request.form['Pemutus']
            Jabatan_Pemutus = request.form['Jabatan Pemutus']
            keterangan= request.form['keterangan']
        
            cursor.execute('''INSERT INTO reg_ptk_konsumer VALUES(%s,%s,%s,%s,%s,%s)''',(Putusan, tanggal, Nama_Debitur, Pemutus, Jabatan_Pemutus, keterangan ))
            conn.commit()
            cursor.close()
            return redirect(url_for('pkkonsumer'))

    return redirect(url_for('login'))

@app.route('/register/pkkonsumer/edit/<NoPutusan>', methods=['GET', 'POST'])
def editpkkonsumer(NoPutusan):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_ptk_konsumer WHERE NoPutusan = %s', (NoPutusan))
            editpkkonsumer = cursor.fetchone()
            return render_template('./Register PK Konsumer/edit_RegisterPK_Konsumer.html', editpkkonsumer=editpkkonsumer)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['Putusan'] == '':
                new_Putusan = request.form['Putusan']
                cursor.execute('UPDATE IGNORE reg_ptk_konsumer SET NoPutusan = %s WHERE NoPutusan = %s', (new_Putusan, NoPutusan))
                conn.commit()
            
            if not request.form['tanggal'] == '':
                new_tanggal = request.form['tanggal']
                cursor.execute('UPDATE IGNORE reg_ptk_konsumer SET TanggalPutusan = %s WHERE NoPutusan = %s', (new_tanggal, NoPutusan))
                conn.commit()

            if not request.form['Nama Debitur'] == '':
                new_NamaDebitur = request.form['Nama Debitur']
                cursor.execute('UPDATE IGNORE reg_ptk_konsumer SET NamaDebitur = %s WHERE NoPutusan = %s', (new_NamaDebitur, NoPutusan))
                conn.commit()

            if not request.form['Pemutus'] == '':
                new_Pemutus = request.form['Pemutus']
                cursor.execute('UPDATE IGNORE reg_ptk_konsumer SET NamaPemutus = %s WHERE NoPutusan = %s', (new_Pemutus, NoPutusan))
                conn.commit()

            if not request.form['Jabatan Pemutus'] == '':
                new_JabatanPemutus = request.form['Jabatan Pemutus']
                cursor.execute('UPDATE IGNORE reg_ptk_konsumer SET JabatanPemutus = %s WHERE NoPutusan = %s', (new_JabatanPemutus, NoPutusan))
                conn.commit()                

            if not request.form['keterangan'] == '':
                new_keterangan = request.form['keterangan']
                cursor.execute('UPDATE IGNORE reg_ptk_konsumer SET Keterangan = %s WHERE NoPutusan = %s', (new_keterangan, NoPutusan))
                conn.commit()
            
            return redirect(url_for('pkkonsumer'))

    return redirect(url_for('login'))

@app.route('/register/pkkonsumer/hapus/<NoPutusan>', methods=['GET', 'POST'])
def hapuspkkonsumer(NoPutusan):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_ptk_konsumer WHERE NoPutusan = %s', (NoPutusan,))
            conn.commit()
            cursor.close()
            return redirect(url_for('pkkonsumer'))
    return redirect(url_for('login'))

@app.route('/register/ppnd2', methods=['GET', 'POST'])
def ppnd2():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_ppnd')
        ppnd2 = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register PPND/detail_RegisterPPND.html', ppnd2=ppnd2)  
    return redirect(url_for('login'))

@app.route('/register/ppnd2/tambah', methods=['GET', 'POST'])
def tambahppnd2():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register PPND/tambah_RegisterPPND.html', username=session['username'])
        else:
            PPND= request.form['PPND']
            Nama_Debitur = request.form['Nama Debitur']
            tanggal = request.form['tanggal']
            Jenis_Pinjaman = request.form['Jenis Pinjaman']
            Jenis_Dokumen_Yang_Ditunda = request.form['Jenis Dokumen Yang Ditunda']
            Lama_PPND_Hari= request.form['Lama PPND (Hari)']
            Tanggal_Diserahkan_Dokumen= request.form['Tanggal Diserahkan Dokumen']
        
            cursor.execute('''INSERT INTO reg_ppnd VALUES(%s,%s,%s,%s,%s,%s,%s)''',(PPND, Nama_Debitur, tanggal, Jenis_Pinjaman, Jenis_Dokumen_Yang_Ditunda, Lama_PPND_Hari, Tanggal_Diserahkan_Dokumen ))
            conn.commit()
            cursor.close()
            return redirect(url_for('ppnd2'))

    return redirect(url_for('login'))

@app.route('/register/ppnd2/edit/<NoPPND>', methods=['GET', 'POST'])
def editppnd2(NoPPND):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_ppnd WHERE NoPPND = %s', (NoPPND))
            editppnd2 = cursor.fetchone()
            return render_template('./Register PPND/edit_RegisterPPND.html', editppnd2=editppnd2)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['PPND'] == '':
                new_PPND = request.form['PPND']
                cursor.execute('UPDATE IGNORE reg_ppnd SET NoPPND = %s WHERE NoPPND = %s', (new_PPND, NoPPND))
                conn.commit()
                
            if not request.form['Nama Debitur'] == '':
                new_Nama_Debitur = request.form['Nama Debitur']
                cursor.execute('UPDATE IGNORE reg_ppnd SET Nama = %s WHERE NoPPND = %s', (new_Nama_Debitur, NoPPND))
                conn.commit()
                
            if not request.form['tanggal'] == '':
                new_tanggal = request.form['tanggal']
                cursor.execute('UPDATE IGNORE reg_ppnd SET TanggalRealisasi = %s WHERE NoPPND = %s', (new_tanggal, NoPPND))
                conn.commit()
            
            if not request.form['Jenis Pinjaman'] == '':
                new_Jenis_Pinjaman = request.form['Jenis Pinjaman']
                cursor.execute('UPDATE IGNORE reg_ppnd SET JenisPinjaman = %s WHERE NoPPND = %s', (new_Jenis_Pinjaman, NoPPND))
                conn.commit()

            if not request.form['Jenis Dokumen Yang Ditunda'] == '':
                new_Jenis_Dokumen_Yang_Ditunda = request.form['Jenis Dokumen Yang Ditunda']
                cursor.execute('UPDATE IGNORE reg_ppnd SET JenisDokumenYangDitunda = %s WHERE NoPPND = %s', (new_Jenis_Dokumen_Yang_Ditunda, NoPPND))
                conn.commit()
            
            if not request.form['Lama PPND (Hari)'] == '':
                new_Lama_PPND_Hari = request.form['Lama PPND (Hari)']
                cursor.execute('UPDATE IGNORE reg_ppnd SET LamaPPND = %s WHERE NoPPND = %s', (new_Lama_PPND_Hari, NoPPND))
                conn.commit()
            
            if not request.form['Tanggal Diserahkan Dokumen'] == '':
                new_Tanggal_Diserahkan_Dokumen = request.form['Tanggal Diserahkan Dokumen']
                cursor.execute('UPDATE IGNORE reg_ppnd SET TanggalDiserahkanDokumen = %s WHERE NoPPND = %s', (new_Tanggal_Diserahkan_Dokumen, NoPPND))
                conn.commit()
            
            return redirect(url_for('ppnd2'))

    return redirect(url_for('login'))

@app.route('/register/ppnd2/hapus/<NoPPND>', methods=['GET', 'POST'])
def hapusppnd2(NoPPND):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_ppnd WHERE NoPPND = %s', (NoPPND,))
            conn.commit()
            cursor.close()
            return redirect(url_for('ppnd2'))
    return redirect(url_for('login'))

@app.route('/register/ptk', methods=['GET', 'POST'])
def ptk():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_ptk')
        ptk = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register PTK/detail_RegisterPTK.html', ptk=ptk)  
    return redirect(url_for('login'))

@app.route('/register/ptk/tambah', methods=['GET', 'POST'])
def tambahptk():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register PTK/tambah_RegisterPTK.html', username=session['username'])
        else:
            Nomer_Putusan= request.form['Nomer Putusan']
            tanggal = request.form['tanggal']
            Nama_Debitur = request.form['Nama Debitur']
            Nama_Pemutus_AO_Pemrakarsa = request.form['Nama Pemutus & AO Pemrakarsa']
            Jabatan_Pemutus = request.form['Jabatan Pemutus']
            keterangan= request.form['keterangan']
        
            cursor.execute('''INSERT INTO reg_ptk VALUES(%s,%s,%s,%s,%s,%s)''',(Nomer_Putusan, tanggal, Nama_Debitur, Nama_Pemutus_AO_Pemrakarsa, Jabatan_Pemutus, keterangan ))
            conn.commit()
            cursor.close()
            return redirect(url_for('ptk'))

    return redirect(url_for('login'))

@app.route('/register/ptk/edit/<NoPutusan>', methods=['GET', 'POST'])
def editptk(NoPutusan):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_ptk WHERE NoPutusan = %s', (NoPutusan))
            editptk = cursor.fetchone()
            return render_template('./Register PTK/edit_RegisterPTK.html', editptk=editptk)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['Nomer Putusan'] == '':
                new_Nomer_Putusan = request.form['Nomer Putusan']
                cursor.execute('UPDATE IGNORE reg_ptk SET NoPutusan = %s WHERE NoPutusan = %s', (new_Nomer_Putusan, NoPutusan))
                conn.commit()
            
            if not request.form['tanggal'] == '':
                new_tanggal = request.form['tanggal']
                cursor.execute('UPDATE IGNORE reg_ptk SET TanggalPutusan = %s WHERE NoPutusan = %s', (new_tanggal, NoPutusan))
                conn.commit()
                
            if not request.form['Nama Debitur'] == '':
                new_Nama_Debitur = request.form['Nama Debitur']
                cursor.execute('UPDATE IGNORE reg_ptk SET NamaDebitur = %s WHERE NoPutusan = %s', (new_Nama_Debitur, NoPutusan))
                conn.commit()
                
            
            if not request.form['Nama Pemutus & AO Pemrakarsa'] == '':
                new_Nama_Pemutus_AO_Pemrakarsa = request.form['Nama Pemutus & AO Pemrakarsa']
                cursor.execute('UPDATE IGNORE reg_ptk SET NamaPemutus = %s WHERE NoPutusan = %s', (new_Nama_Pemutus_AO_Pemrakarsa, NoPutusan))
                conn.commit()

            if not request.form['JabatanPemutus'] == '':
                new_Jabatan_Pemutus = request.form['JabatanPemutus']
                cursor.execute('UPDATE IGNORE reg_ptk SET JabatanPemutus = %s WHERE NoPutusan = %s', (new_Jabatan_Pemutus, NoPutusan))
                conn.commit()
            
            if not request.form['keterangan'] == '':
                new_keterangan = request.form['keterangan']
                cursor.execute('UPDATE IGNORE reg_ptk SET Keterangan = %s WHERE NoPutusan = %s', (new_keterangan, NoPutusan))
                conn.commit()
            
            return redirect(url_for('ptk'))

    return redirect(url_for('login'))

@app.route('/register/ptk/hapus/<NoPutusan>', methods=['GET', 'POST'])
def hapusptk(NoPutusan):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_ptk WHERE NoPutusan = %s', (NoPutusan,))
            conn.commit()
            cursor.close()
            return redirect(url_for('ptk'))
    return redirect(url_for('login'))

@app.route('/register/flpp', methods=['GET', 'POST'])
def flpp():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_ptk_flpp')
        flpp = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register PTK (Putusan Kredit) FLPP/detail_RegisterPTK (Putusan Kredit)FLPP.html', flpp=flpp)  
    return redirect(url_for('login'))

@app.route('/register/flpp/tambah', methods=['GET', 'POST'])
def tambahflpp():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register PTK (Putusan Kredit) FLPP/tambah_RegisterPTK (Putusan Kredit)FLPP.html', username=session['username'])
        else:
            Nomer_Putusan= request.form['Nomer Putusan']
            tanggal = request.form['tanggal']
            Nama_Debitur = request.form['Nama Debitur']
            Jabatan_Pemutus = request.form['Jabatan Pemutus']
            Nama_Pemutus = request.form['Nama Pemutus']
            Plafond_Rp= request.form['Plafond(Rp)']
            Nama_Perumahan = request.form['Nama Perumahan']
            keterangan = request.form['keterangan']
        
            cursor.execute('''INSERT INTO reg_ptk_flpp VALUES(%s,%s,%s,%s,%s,%s,%s,%s)''',(Nomer_Putusan, tanggal, Nama_Debitur, Jabatan_Pemutus, Nama_Pemutus, Plafond_Rp, Nama_Perumahan, keterangan ))
            conn.commit()
            cursor.close()
            return redirect(url_for('flpp'))

    return redirect(url_for('login'))

@app.route('/register/flpp/edit/<NoPutusan>', methods=['GET', 'POST'])
def editflpp(NoPutusan):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_ptk_flpp WHERE NoPutusan = %s', (NoPutusan))
            editflpp = cursor.fetchone()
            return render_template('./Register PTK (Putusan Kredit) FLPP/edit_RegisterPTK (Putusan Kredit)FLPP.html', editflpp=editflpp)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['Nomer Putusan'] == '':
                new_Nomer_Putusan = request.form['Nomer Putusan']
                cursor.execute('UPDATE IGNORE reg_ptk_flpp SET NoPutusan = %s WHERE NoPutusan = %s', (new_Nomer_Putusan, NoPutusan))
                conn.commit()
            
            if not request.form['tanggal'] == '':
                new_tanggal = request.form['tanggal']
                cursor.execute('UPDATE IGNORE reg_ptk_flpp SET TanggalPutusan = %s WHERE NoPutusan = %s', (new_tanggal, NoPutusan))
                conn.commit()
                
            if not request.form['Nama Debitur'] == '':
                new_Nama_Debitur = request.form['Nama Debitur']
                cursor.execute('UPDATE IGNORE reg_ptk_flpp SET NamaDebitur = %s WHERE NoPutusan = %s', (new_Nama_Debitur, NoPutusan))
                conn.commit()
                
            
            if not request.form['Jabatan Pemutus'] == '':
                new_Jabatan_Pemutus = request.form['Jabatan Pemutus']
                cursor.execute('UPDATE IGNORE reg_ptk_flpp SET JabatanPemutus = %s WHERE NoPutusan = %s', (new_Jabatan_Pemutus, NoPutusan))
                conn.commit()

            if not request.form['Nama Pemutus'] == '':
                new_Nama_Pemutus = request.form['Nama Pemutus']
                cursor.execute('UPDATE IGNORE reg_ptk_flpp SET NamaPemutus = %s WHERE NoPutusan = %s', (new_Nama_Pemutus, NoPutusan))
                conn.commit()
            
            if not request.form['Plafond(Rp)'] == '':
                new_Plafond_Rp = request.form['Plafond(Rp)']
                cursor.execute('UPDATE IGNORE reg_ptk_flpp SET PlafondRp = %s WHERE NoPutusan = %s', (new_Plafond_Rp, NoPutusan))
                conn.commit()
            
            if not request.form['Nama Perumahan'] == '':
                new_Nama_Perumahan = request.form['Nama Perumahan']
                cursor.execute('UPDATE IGNORE reg_ptk_flpp SET NamaPerumahan = %s WHERE NoPutusan = %s', (new_Nama_Perumahan, NoPutusan))
                conn.commit()
            
            if not request.form['keterangan'] == '':
                new_keterangan = request.form['keterangan']
                cursor.execute('UPDATE IGNORE reg_ptk_flpp SET Keterangan = %s WHERE NoPutusan = %s', (new_keterangan, NoPutusan))
                conn.commit()
            
            return redirect(url_for('flpp'))

    return redirect(url_for('login'))

@app.route('/register/flpp/hapus/<NoPutusan>', methods=['GET', 'POST'])
def hapusflpp(NoPutusan):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_ptk_flpp WHERE NoPutusan = %s', (NoPutusan,))
            conn.commit()
            cursor.close()
            return redirect(url_for('flpp'))
    return redirect(url_for('login'))

@app.route('/register/roya', methods=['GET', 'POST'])
def roya():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_roya')
        roya = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register Roya/detail_Register Roya.html', roya=roya)  
    return redirect(url_for('login'))

@app.route('/register/roya/tambah', methods=['GET', 'POST'])
def tambahroya():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register Roya/tambah_Register Roya.html', username=session['username'])
        else:
            Tanggal_Surat_Roya= request.form['Tanggal Surat Roya']
            Nama_Debitur = request.form['Nama Debitur']
            Kantor_BPN = request.form['Kantor BPN']
            keterangan = request.form['keterangan']
            tanggal= request.form['tanggal']
            Diterima_Oleh = request.form['Diterima Oleh']
        
            cursor.execute('''INSERT INTO reg_roya VALUES(%s,%s,%s,%s,%s,%s)''',(Tanggal_Surat_Roya, Nama_Debitur, Kantor_BPN, keterangan, tanggal, Diterima_Oleh ))
            conn.commit()
            cursor.close()
            return redirect(url_for('roya'))

    return redirect(url_for('login'))

@app.route('/register/roya/edit/<NamaDebitur>', methods=['GET', 'POST'])
def editroya(NamaDebitur):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_roya WHERE NamaDebitur = %s', (NamaDebitur))
            editroya = cursor.fetchone()
            return render_template('./Register Roya/edit_Register Roya.html', editroya=editroya)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['Tanggal Surat Roya'] == '':
                new_Tanggal_Surat_Roya = request.form['Tanggal Surat Roya']
                cursor.execute('UPDATE IGNORE reg_roya SET TanggalSuratRoya = %s WHERE NamaDebitur = %s', (new_Tanggal_Surat_Roya, NamaDebitur))
                conn.commit()
            
            if not request.form['Nama Debitur'] == '':
                new_Nama_Debitur = request.form['Nama Debitur']
                cursor.execute('UPDATE IGNORE reg_roya SET NamaDebitur = %s WHERE NamaDebitur = %s', (new_Nama_Debitur, NamaDebitur))
                conn.commit()
                
            if not request.form['Kantor BPN'] == '':
                new_Kantor_BPN = request.form['Kantor BPN']
                cursor.execute('UPDATE IGNORE reg_roya SET KantorBPN = %s WHERE KantorBPN = %s', (new_Kantor_BPN, NamaDebitur))
                conn.commit()
                
            
            if not request.form['keterangan'] == '':
                new_keterangan = request.form['keterangan']
                cursor.execute('UPDATE IGNORE reg_roya SET JenisAgunan_keterangan = %s WHERE NamaDebitur = %s', (new_keterangan, NamaDebitur))
                conn.commit()

            if not request.form['tanggal'] == '':
                new_tanggal = request.form['tanggal']
                cursor.execute('UPDATE IGNORE reg_roya SET DiterimaTanggal = %s WHERE NamaDebitur = %s', (new_tanggal, NamaDebitur))
                conn.commit()
            
            if not request.form['Diterima Oleh'] == '':
                new_Diterima_Oleh = request.form['Diterima Oleh']
                cursor.execute('UPDATE IGNORE reg_roya SET DiterimOleh = %s WHERE NamaDebitur = %s', (new_Diterima_Oleh, NamaDebitur))
                conn.commit()
            
            return redirect(url_for('roya'))

    return redirect(url_for('login'))

@app.route('/register/roya/hapus/<NamaDebitur>', methods=['GET', 'POST'])
def hapusroya(NamaDebitur):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_roya WHERE NamaDebitur = %s', (NamaDebitur,))
            conn.commit()
            cursor.close()
            return redirect(url_for('roya'))
    return redirect(url_for('login'))


@app.route('/register/royakkb', methods=['GET', 'POST'])
def royakkb():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_roya_kkb')
        royakkb = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register Roya&KKB/detail_Roya&KKB.html', royakkb=royakkb)  
    return redirect(url_for('login'))

@app.route('/register/royakkb/tambah', methods=['GET', 'POST'])
def tambahroyakkb():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register Roya&KKB/tambah_Roya&KKB.html', username=session['username'])
        else:
            Tanggal_Surat_Roya= request.form['tgl_surat_roya']
            Nama_Debitur = request.form['Nama_debitur']
            Kantor_BPN = request.form['kantor_bpn']
            Diterima_tgl = request.form['diterima_tgl']
            Diterima_oleh= request.form['diterima_oleh']
            Jenis_Agunan = request.form['jenis_agunan']
        
            cursor.execute('''INSERT INTO reg_roya_kkb VALUES(%s,%s,%s,%s,%s,%s)''',(Tanggal_Surat_Roya, Nama_Debitur, Kantor_BPN, Diterima_tgl, Diterima_oleh, Jenis_Agunan ))
            conn.commit()
            cursor.close()
            return redirect(url_for('royakkb'))

    return redirect(url_for('login'))

@app.route('/register/royakkb/edit/<NamaDebitur>', methods=['GET', 'POST'])
def editroyakkb(NamaDebitur):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_roya_kkb WHERE NamaDebitur = %s', (NamaDebitur))
            editroyakkb = cursor.fetchone()
            return render_template('./Register Roya&KKB/edit_Roya&KKB.html', editroyakkb=editroyakkb)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['tgl_surat_roya'] == '':
                new_tgl_surat_roya= request.form['tgl_surat_roya']
                cursor.execute('UPDATE IGNORE reg_roya_kkb SET TanggalSuratRoya = %s WHERE NamaDebitur = %s', (new_tgl_surat_roya, NamaDebitur))
                conn.commit()
            
            if not request.form['Nama_debitur'] == '':
                new_Nama_debitur = request.form['Nama_debitur']
                cursor.execute('UPDATE IGNORE reg_roya_kkb SET NamaDebitur = %s WHERE NamaDebitur = %s', (new_Nama_debitur, NamaDebitur))
                conn.commit()
                
            if not request.form['kantor_bpn'] == '':
                new_kantor_bpn = request.form['kantor_bpn']
                cursor.execute('UPDATE IGNORE reg_roya_kkb SET KantorBPN = %s WHERE NamaDebitur = %s', (new_kantor_bpn, NamaDebitur))
                conn.commit()
                
            
            if not request.form['diterima_tgl'] == '':
                new_diterima_tgl = request.form['diterima_tgl']
                cursor.execute('UPDATE IGNORE reg_roya_kkb SET DiterimaDebiturTanggal = %s WHERE NamaDebitur = %s', (new_diterima_tgl, NamaDebitur))
                conn.commit()

            if not request.form['diterima_oleh'] == '':
                new_diterima_oleh = request.form['diterima_oleh']
                cursor.execute('UPDATE IGNORE reg_roya_kkb SET DiterimaDebituroleh = %s WHERE NamaDebitur = %s', (new_diterima_oleh, NamaDebitur))
                conn.commit()
            
            if not request.form['jenis_agunan'] == '':
                new_jenis_agunan = request.form['jenis_agunan']
                cursor.execute('UPDATE IGNORE reg_roya_kkb SET JenisAgunanKeterangan = %s WHERE NamaDebitur = %s', (new_jenis_agunan, NamaDebitur))
                conn.commit()
            
            return redirect(url_for('royakkb'))

    return redirect(url_for('login'))

@app.route('/register/royakkb/hapus/<NamaDebitur>', methods=['GET', 'POST'])
def hapusroyakkb(NamaDebitur):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_roya_kkb WHERE NamaDebitur = %s', (NamaDebitur,))
            conn.commit()
            cursor.close()
            return redirect(url_for('royakkb'))
    return redirect(url_for('login'))
    

@app.route('/register/slik', methods=['GET', 'POST'])
def slik():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_slik')
        slik = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register Slik/detail_Register SLIK.html', slik=slik)  
    return redirect(url_for('login'))

@app.route('/register/slik/tambah', methods=['GET', 'POST'])
def tambahs():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register Slik/tambah_Register SLIK.html', username=session['username'])
        else:
            Tanggal= request.form['Tanggal']
            Nama_Pemohon = request.form['Nama Pemohon']
            Nama_Debitur = request.form['Nama Debitur']
            Tanggal1 = request.form['Tanggal1']
            Nama = request.form['Nama']
            Debitur = request.form['Debitur']
        
            cursor.execute('''INSERT INTO reg_slik VALUES(%s,%s,%s,%s,%s,%s)''',(Tanggal, Nama_Pemohon, Nama_Debitur, Tanggal1, Nama, Debitur ))
            conn.commit()
            cursor.close()
            return redirect(url_for('slik'))

    return redirect(url_for('login'))

@app.route('/register/slik/edit/<NamaDebitur>', methods=['GET', 'POST'])
def editslik(NamaDebitur):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_slik WHERE NamaDebitur = %s', (NamaDebitur))
            editslik = cursor.fetchone()
            return render_template('./Register Slik/edit_Register SLIK.html', editslik=editslik)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['Tanggal'] == '':
                new_Tanggal= request.form['Tanggal']
                cursor.execute('UPDATE IGNORE reg_slik SET Tanggal = %s WHERE NamaDebitur = %s', (new_Tanggal, NamaDebitur))
                conn.commit()
            
            if not request.form['Nama Pemohon'] == '':
                new_Nama_Pemohon = request.form['Nama Pemohon']
                cursor.execute('UPDATE IGNORE reg_slik SET NamaPemohon = %s WHERE NamaDebitur = %s', (new_Nama_Pemohon, NamaDebitur))
                conn.commit()
                
            if not request.form['Nama Debitur'] == '':
                new_Nama_Debitur = request.form['Nama Debitur']
                cursor.execute('UPDATE IGNORE reg_slik SET NamaDebitur = %s WHERE NamaDebitur = %s', (new_Nama_Debitur, NamaDebitur))
                conn.commit()
                
            
            return redirect(url_for('slik'))

    return redirect(url_for('login'))

@app.route('/register/slik/hapus/<NamaDebitur>', methods=['GET', 'POST'])
def hapusslik(NamaDebitur):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_slik WHERE NamaDebitur = %s', (NamaDebitur,))
            conn.commit()
            cursor.close()
            return redirect(url_for('slik'))
    return redirect(url_for('login'))

@app.route('/register/spph', methods=['GET', 'POST'])
def spph():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_spph')
        spph = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register SPPH/detail_Register SPPH.html', spph=spph)  
    return redirect(url_for('login'))

@app.route('/register/spph/tambah', methods=['GET', 'POST'])
def tambahspph():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register SPPH/tambah_Register SPPH.html', username=session['username'])
        else:
            Nama_Debitur= request.form['Nama Debitur']
            Nomer_SPPA = request.form['Nomer SPPA']
            Nomor_Premi = request.form['Nomor Premi']
            Jenis_Pertanggungan = request.form['Jenis Pertanggungan']
            Nilai_Pertanggungann = request.form['Nilai Pertanggungann']
            Jangka_Waktu = request.form['Jangka Waktu']
            Setor_Rp = request.form['Setor Rp.']
            Tanggal_Setor = request.form['Tanggal Setor.']
            Paraf = request.form['Paraf']
        
            cursor.execute('''INSERT INTO reg_spph VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(Nama_Debitur, Nomer_SPPA, Nomor_Premi, Jenis_Pertanggungan, Nilai_Pertanggungann, Jangka_Waktu, Setor_Rp, Tanggal_Setor, Paraf ))
            conn.commit()
            cursor.close()
            return redirect(url_for('spph'))

    return redirect(url_for('login'))

@app.route('/register/spph/edit/<premi>', methods=['GET', 'POST'])
def editspph(premi):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_spph WHERE premi = %s', (premi))
            editspph = cursor.fetchone()
            return render_template('./Register SPPH/edit_Register SPPH.html', editspph=editspph)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['Nama Debitur'] == '':
                new_Nama_Debitur= request.form['Nama Debitur']
                cursor.execute('UPDATE IGNORE reg_spph SET NamaDebitur = %s WHERE premi = %s', (new_Nama_Debitur, premi))
                conn.commit()
            
            if not request.form['Nomer SPPA'] == '':
                new_Nomer_SPPA = request.form['Nomer SPPA']
                cursor.execute('UPDATE IGNORE reg_spph SET NomorSPPA = %s WHERE premi = %s', (new_Nomer_SPPA, premi))
                conn.commit()
                
            if not request.form['Nomor Premi'] == '':
                new_Nomor_Premi = request.form['Nomor Premi']
                cursor.execute('UPDATE IGNORE reg_spph SET premi = %s WHERE premi = %s', (new_Nomor_Premi, premi))
                conn.commit()
                
            if not request.form['Jenis Pertanggungan'] == '':
                new_Jenis_Pertanggungan = request.form['Jenis Pertanggungan']
                cursor.execute('UPDATE IGNORE reg_spph SET JenisPertanggungan = %s WHERE premi = %s', (new_Jenis_Pertanggungan, premi))
                conn.commit()

            if not request.form['Nilai Pertanggungann'] == '':
                new_Nilai_Pertanggungann = request.form['Nilai Pertanggungann']
                cursor.execute('UPDATE IGNORE reg_spph SET NilaiPertanggungan = %s WHERE premi = %s', (new_Nilai_Pertanggungann, premi))
                conn.commit()
            
            if not request.form['Jangka Waktu'] == '':
                new_Jangka_Waktu = request.form['Jangka Waktu']
                cursor.execute('UPDATE IGNORE reg_spph SET JangkaWaktu = %s WHERE premi = %s', (new_Jangka_Waktu, premi))
                conn.commit()
            
            if not request.form['Setor Rp.'] == '':
                new_Setor_Rp = request.form['Setor Rp.']
                cursor.execute('UPDATE IGNORE reg_spph SET SetorRp = %s WHERE premi = %s', (new_Setor_Rp, premi))
                conn.commit()
            
            if not request.form['Tanggal Setor.'] == '':
                new_Tanggal_Setor = request.form['Tanggal Setor.']
                cursor.execute('UPDATE IGNORE reg_spph SET SetorTanggal = %s WHERE premi = %s', (new_Tanggal_Setor, premi))
                conn.commit()
            
            if not request.form['Paraf'] == '':
                new_Paraf = request.form['Paraf']
                cursor.execute('UPDATE IGNORE reg_spph SET Paraf = %s WHERE premi = %s', (new_Paraf, premi))
                conn.commit()
            
            return redirect(url_for('spph'))

    return redirect(url_for('login'))

@app.route('/register/spph/hapus/<premi>', methods=['GET', 'POST'])
def hapusspph(premi):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_spph WHERE premi = %s', (premi,))
            conn.commit()
            cursor.close()
            return redirect(url_for('spph'))
    return redirect(url_for('login'))

@app.route('/register/tbnk', methods=['GET', 'POST'])
def tbnk():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_titipan_biaya_notaris')
        tbnk = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register TBNK/detail_titipbiayanotaris.html', tbnk=tbnk)  
    return redirect(url_for('login'))

@app.route('/register/tbnk/tambah', methods=['GET', 'POST'])
def tambahtbnk():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register TBNK/tambahdata_titipbiayanotaris.html', username=session['username'])
        else:
            Nama_Debitur= request.form['nama_debitur']
            rp = request.form['rp']
            Tanggal_Setor = request.form['tanggal_setor']
            nama_notaris = request.form['nama_notaris']
            tanggal_ob = request.form['tanggal_ob']
            OB = request.form['ob']
            keterangan = request.form['keterangan']
        
            cursor.execute('''INSERT INTO reg_titipan_biaya_notaris VALUES(%s,%s,%s,%s,%s,%s,%s)''',(Nama_Debitur, rp, Tanggal_Setor, nama_notaris, tanggal_ob, OB, keterangan ))
            conn.commit()
            cursor.close()
            return redirect(url_for('tbnk'))

    return redirect(url_for('login'))

@app.route('/register/tbnk/edit/<NamaDebitur>', methods=['GET', 'POST'])
def edittbnk(NamaDebitur):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_titipan_biaya_notaris WHERE NamaDebitur = %s', (NamaDebitur))
            edittbnk = cursor.fetchone()
            return render_template('./Register TBNK/edit_titipbiayanotaris.html', edittbnk=edittbnk)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['nama_debitur'] == '':
                new_nama_debitur= request.form['nama_debitur']
                cursor.execute('UPDATE IGNORE reg_titipan_biaya_notaris SET NamaDebitur = %s WHERE NamaDebitur = %s', (new_nama_debitur, NamaDebitur))
                conn.commit()
            
            if not request.form['rp'] == '':
                new_rp = request.form['rp']
                cursor.execute('UPDATE IGNORE reg_titipan_biaya_notaris SET Rp = %s WHERE NamaDebitur = %s', (new_rp, NamaDebitur))
                conn.commit()
            
            if not request.form['tanggal_setor'] == '':
                new_tanggal_setor = request.form['tanggal_setor']
                cursor.execute('UPDATE IGNORE reg_titipan_biaya_notaris SET TanggalSetor = %s WHERE NamaDebitur = %s', (new_tanggal_setor, NamaDebitur))
                conn.commit()
                
            if not request.form['nama_notaris'] == '':
                new_nama_notaris = request.form['nama_notaris']
                cursor.execute('UPDATE IGNORE reg_titipan_biaya_notaris SET NamaNotaris = %s WHERE NamaDebitur = %s', (new_nama_notaris, NamaDebitur))
                conn.commit()
                
            if not request.form['tanggal_ob'] == '':
                new_tanggal_ob = request.form['tanggal_ob']
                cursor.execute('UPDATE IGNORE reg_titipan_biaya_notaris SET TanggaldiOB = %s WHERE NamaDebitur = %s', (new_tanggal_ob, NamaDebitur))
                conn.commit()
            
            if not request.form['ob'] == '':
                new_ob= request.form['ob']
                cursor.execute('UPDATE IGNORE reg_titipan_biaya_notaris SET RpOB = %s WHERE NamaDebitur = %s', (new_ob, NamaDebitur))
                conn.commit()
            
            if not request.form['keterangan'] == '':
                new_keterangan = request.form['keterangan']
                cursor.execute('UPDATE IGNORE reg_titipan_biaya_notaris SET Keterangan = %s WHERE NamaDebitur = %s', (new_keterangan, NamaDebitur))
                conn.commit()
        
            return redirect(url_for('tbnk'))

    return redirect(url_for('login'))

@app.route('/register/tbnk/hapus/<NamaDebitur>', methods=['GET', 'POST'])
def hapustbnk(NamaDebitur):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_titipan_biaya_notaris WHERE NamaDebitur = %s', (NamaDebitur))
            conn.commit()
            cursor.close()
            return redirect(url_for('tbnk'))
    return redirect(url_for('login'))

@app.route('/register/ttsn', methods=['GET', 'POST'])
def ttsn():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_tandaterima_sertif_kenotaris')
        ttsn = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register TTS Notaris/detail_RegisterTTSNotaris.html', ttsn=ttsn)  
    return redirect(url_for('login'))

@app.route('/register/ttsn/tambah', methods=['GET', 'POST'])
def tambahttsn():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register TTS Notaris/tambah_RegisterTTSNotaris.html', username=session['username'])
        else:
            Nama_Debitur= request.form['Nama Debitur']
            No_SHM_SHGB = request.form['No. SHM / SHGB']
            Tanggal_Sertifikat = request.form['Tanggal Sertifikat']
            Nomor_Surat_Ukur = request.form['Nomor Surat Ukur']
            Tanggal_Surat_Ukur = request.form['Tanggal Surat Ukur']
            Luas_m = request.form['Luas(m)']
            Nama_Pemilik_SHM_SHGB = request.form['Nama Pemilik SHM/SHGB']
            Tanggal_Penyerahan = request.form['Tanggal Penyerahan']
            Tanda_Tangan_Nama = request.form['Tanda Tangan / Nama']
        
            cursor.execute('''INSERT INTO reg_tandaterima_sertif_kenotaris VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(Nama_Debitur, No_SHM_SHGB, Tanggal_Sertifikat, Nomor_Surat_Ukur, Tanggal_Surat_Ukur, Luas_m, Nama_Pemilik_SHM_SHGB, Tanggal_Penyerahan, Tanda_Tangan_Nama ))
            conn.commit()
            cursor.close()
            return redirect(url_for('ttsn'))

    return redirect(url_for('login'))

@app.route('/register/ttsn/edit/<NoSHM_SHGB>', methods=['GET', 'POST'])
def editttsn(NoSHM_SHGB):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_tandaterima_sertif_kenotaris WHERE NoSHM_SHGB = %s', (NoSHM_SHGB))
            editttsn = cursor.fetchone()
            return render_template('./Register TTS Notaris/edit_RegisterTTSNotaris.html', editttsn=editttsn)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['Nama Debitur'] == '':
                new_Nama_Debitur= request.form['Nama Debitur']
                cursor.execute('UPDATE IGNORE reg_tandaterima_sertif_kenotaris SET NamaDebitur = %s WHERE NoSHM_SHGB = %s', (new_Nama_Debitur, NoSHM_SHGB))
                conn.commit()
            
            if not request.form['No. SHM / SHGB'] == '':
                new_No_SHM_SHGB = request.form['No. SHM / SHGB']
                cursor.execute('UPDATE IGNORE reg_tandaterima_sertif_kenotaris SET NoSHM_SHGB = %s WHERE NoSHM_SHGB = %s', (new_No_SHM_SHGB, NoSHM_SHGB))
                conn.commit()
            
            if not request.form['Tanggal Sertifikat'] == '':
                new_Tanggal_Sertifikat = request.form['Tanggal Sertifikat']
                cursor.execute('UPDATE IGNORE reg_tandaterima_sertif_kenotaris SET TanggalSertifikat = %s WHERE NoSHM_SHGB = %s', (new_Tanggal_Sertifikat, NoSHM_SHGB))
                conn.commit()
                
            if not request.form['Nomor Surat Ukur'] == '':
                new_Nomor_Surat_Ukur = request.form['Nomor Surat Ukur']
                cursor.execute('UPDATE IGNORE reg_tandaterima_sertif_kenotaris SET NomorSuratUkur = %s WHERE NoSHM_SHGB = %s', (new_Nomor_Surat_Ukur, NoSHM_SHGB))
                conn.commit()
                
            if not request.form['Tanggal Surat Ukur'] == '':
                new_Tanggal_Surat_Ukur = request.form['Tanggal Surat Ukur']
                cursor.execute('UPDATE IGNORE reg_tandaterima_sertif_kenotaris SET TanggalSuratUkur = %s WHERE NoSHM_SHGB = %s', (new_Tanggal_Surat_Ukur, NoSHM_SHGB))
                conn.commit()
            
            if not request.form['Luas(m)'] == '':
                new_Luas_= request.form['Luas(m)']
                cursor.execute('UPDATE IGNORE reg_tandaterima_sertif_kenotaris SET Luas = %s WHERE NoSHM_SHGB = %s', (new_Luas_, NoSHM_SHGB))
                conn.commit()
            
            if not request.form['Nama Pemilik SHM/SHGB'] == '':
                new_Nama_Pemilik_SHM_SHGB = request.form['Nama Pemilik SHM/SHGB']
                cursor.execute('UPDATE IGNORE reg_tandaterima_sertif_kenotaris SET NamaPemilikSHM_SHGB = %s WHERE NoSHM_SHGB = %s', (new_Nama_Pemilik_SHM_SHGB, NoSHM_SHGB))
                conn.commit()
            
            if not request.form['Tanggal Penyerahan'] == '':
                new_Tanggal_Penyerahan = request.form['Tanggal Penyerahan']
                cursor.execute('UPDATE IGNORE reg_tandaterima_sertif_kenotaris SET TanggalPenyerahan = %s WHERE NoSHM_SHGB = %s', (new_Tanggal_Penyerahan, NoSHM_SHGB))
                conn.commit()
            
            if not request.form['Tanda Tangan / Nama'] == '':
                new_Tanda_Tangan_Nama = request.form['Tanda Tangan / Nama']
                cursor.execute('UPDATE IGNORE reg_tandaterima_sertif_kenotaris SET TTD_Nama = %s WHERE NoSHM_SHGB = %s', (new_Tanda_Tangan_Nama, NoSHM_SHGB))
                conn.commit()
        
            return redirect(url_for('ttsn'))

    return redirect(url_for('login'))

@app.route('/register/ttsn/hapus/<NoSHM_SHGB>', methods=['GET', 'POST'])
def hapusttsn(NoSHM_SHGB):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_tandaterima_sertif_kenotaris WHERE NoSHM_SHGB = %s', (NoSHM_SHGB))
            conn.commit()
            cursor.close()
            return redirect(url_for('ttsn'))
    return redirect(url_for('login'))

@app.route('/register/verbek', methods=['GET', 'POST'])
def verbek():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_verbek')
        verbek = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./Register Verifikasi Berkas/detail_RegisterVerifikasiBerkas.html', verbek=verbek)  
    return redirect(url_for('login'))

@app.route('/register/verbek/tambah', methods=['GET', 'POST'])
def tambahverbek():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./Register Verifikasi Berkas/tambah_RegisterVerifikasiBerkas.html', username=session['username'])
        else:
            Nama_Debitur= request.form['Nama Debitur']
            RM_Pengelola = request.form['RM Pengelola']
            Fasilitas = request.form['Fasilitas']
            Tanggal_Berkas_Diserahkan = request.form['Tanggal Berkas Diserahkan']
            Jam_Berkas_Diserahkan = request.form['Jam Berkas Diserahkan']
            Yang_Menyerahkan = request.form['Yang Menyerahkan']
            Paraf = request.form['Paraf']
            Tanggal_Penyerahan = request.form['Tanggal Kembali Setelah Diputus']
        
            cursor.execute('''INSERT INTO reg_verbek VALUES(%s,%s,%s,%s,%s,%s,%s,%s)''',(Nama_Debitur, RM_Pengelola, Fasilitas, Tanggal_Berkas_Diserahkan, Jam_Berkas_Diserahkan, Yang_Menyerahkan, Paraf, Tanggal_Penyerahan ))
            conn.commit()
            cursor.close()
            return redirect(url_for('verbek'))

    return redirect(url_for('login'))

@app.route('/register/verbek/edit/<NamaDebitur>', methods=['GET', 'POST'])
def editverbek(NamaDebitur):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_verbek WHERE NamaDebitur = %s', (NamaDebitur))
            editverbek = cursor.fetchone()
            return render_template('./Register Verifikasi Berkas/edit_RegisterVerifikasiBerkas.html', editverbek=editverbek)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['Nama Debitur'] == '':
                new_Nama_Debitur= request.form['Nama Debitur']
                cursor.execute('UPDATE IGNORE reg_verbek SET NamaDebitur = %s WHERE NamaDebitur = %s', (new_Nama_Debitur, NamaDebitur))
                conn.commit()
            
            if not request.form['RM Pengelola'] == '':
                new_RM_Pengelola = request.form['RM Pengelola']
                cursor.execute('UPDATE IGNORE reg_verbek SET RMPengelola = %s WHERE NamaDebitur = %s', (new_RM_Pengelola, NamaDebitur))
                conn.commit()
            
            if not request.form['Fasilitas'] == '':
                new_Fasilitas = request.form['Fasilitas']
                cursor.execute('UPDATE IGNORE reg_verbek SET Fasilitas = %s WHERE NamaDebitur = %s', (new_Fasilitas, NamaDebitur))
                conn.commit()
                
            if not request.form['Tanggal Berkas Diserahkan'] == '':
                new_Tanggal_Berkas_Diserahkan = request.form['Tanggal Berkas Diserahkan']
                cursor.execute('UPDATE IGNORE reg_verbek SET TanggalBerkasDiserahkan = %s WHERE NamaDebitur = %s', (new_Tanggal_Berkas_Diserahkan, NamaDebitur))
                conn.commit()
                
            if not request.form['Jam Berkas Diserahkan'] == '':
                new_Jam_Berkas_Diserahkan = request.form['Jam Berkas Diserahkan']
                cursor.execute('UPDATE IGNORE reg_verbek SET JamBerkasDiserahkan = %s WHERE NamaDebitur = %s', (new_Jam_Berkas_Diserahkan, NamaDebitur))
                conn.commit()
            
            if not request.form['Yang Menyerahkan'] == '':
                new_Yang_Menyerahkan = request.form['Yang Menyerahkan']
                cursor.execute('UPDATE IGNORE reg_verbek SET YangMenyerahkan = %s WHERE NamaDebitur = %s', (new_Yang_Menyerahkan, NamaDebitur))
                conn.commit()
            
            if not request.form['Paraf'] == '':
                new_Paraf = request.form['Paraf']
                cursor.execute('UPDATE IGNORE reg_verbek SET Paraf = %s WHERE NamaDebitur = %s', (new_Paraf, NamaDebitur))
                conn.commit()
            
            if not request.form['Tanggal Kembali Setelah Diputus'] == '':
                new_Tanggal_Kembali_Setelah_Diputus = request.form['Tanggal Kembali Setelah Diputus']
                cursor.execute('UPDATE IGNORE reg_verbek SET TanggalKembaliSetelahDiputus = %s WHERE NamaDebitur = %s', (new_Tanggal_Kembali_Setelah_Diputus, NamaDebitur))
                conn.commit()
            
            return redirect(url_for('verbek'))

    return redirect(url_for('login'))

@app.route('/register/verbek/hapus/<NamaDebitur>', methods=['GET', 'POST'])
def hapusverbek(NamaDebitur):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_verbek WHERE NamaDebitur = %s', (NamaDebitur))
            conn.commit()
            cursor.close()
            return redirect(url_for('verbek'))
    return redirect(url_for('login'))

@app.route('/register/adk', methods=['GET', 'POST'])
def adk():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM reg_persekot_internadk')
        adk = cursor.fetchall()
        conn.commit()
        cursor.close()
        return render_template('./RegisterPersekotInteren/detail_RegisterPersekotInteren.html', adk=adk)  
    return redirect(url_for('login'))

@app.route('/register/adk/tambah', methods=['GET', 'POST'])
def tambahadk():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template('./RegisterPersekotInteren/tambah_RegisterPersekotInteren.html', username=session['username'])
        else:
            tanggal= request.form['tanggal']
            rp = request.form['rp']
            Pengambilan = request.form['Pengambilan']
            saldo_akhir = request.form['saldo_akhir']
            Tanggal_Pengambilan = request.form['Tanggal Pengambilan']
            keterangan = request.form['keterangan']
           
            cursor.execute('''INSERT INTO reg_persekot_internadk VALUES(%s,%s,%s,%s,%s,%s)''',(tanggal, keterangan, rp, Pengambilan, Tanggal_Pengambilan, saldo_akhir))
            conn.commit()
            cursor.close()
            return redirect(url_for('adk'))

    return redirect(url_for('login'))

@app.route('/register/adk/edit/<Keterangan>', methods=['GET', 'POST'])
def editadk(Keterangan):
    if 'loggedin' in session:
        if request.method == 'GET':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM reg_persekot_internadk WHERE Keterangan = %s', (Keterangan))
            editadk = cursor.fetchone()
            return render_template('./RegisterPersekotInteren/edit_RegisterPersekotInteren.html', editadk=editadk)
        elif request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
                
            if not request.form['tanggal'] == '':
                new_tanggal= request.form['tanggal']
                cursor.execute('UPDATE IGNORE reg_persekot_internadk SET Tanggal = %s WHERE Keterangan = %s', (new_tanggal, Keterangan))
                conn.commit()
            
            if not request.form['rp'] == '':
                new_rp = request.form['rp']
                cursor.execute('UPDATE IGNORE reg_persekot_internadk SET Rp = %s WHERE Keterangan = %s', (new_rp, Keterangan))
                conn.commit()
            
            if not request.form['Pengambilan'] == '':
                new_Pengambilan = request.form['Pengambilan']
                cursor.execute('UPDATE IGNORE reg_persekot_internadk SET Pengambilan = %s WHERE Keterangan = %s', (new_Pengambilan, Keterangan))
                conn.commit()
                
            if not request.form['saldo_akhir'] == '':
                new_saldo_akhir = request.form['saldo_akhir']
                cursor.execute('UPDATE IGNORE reg_persekot_internadk SET SaldoAkhir = %s WHERE Keterangan = %s', (new_saldo_akhir, Keterangan))
                conn.commit()
                
            if not request.form['Tanggal Pengambilan'] == '':
                new_Tanggal_Pengambilan = request.form['Tanggal Pengambilan']
                cursor.execute('UPDATE IGNORE reg_persekot_internadk SET TanggalPengambilan = %s WHERE Keterangan = %s', (new_Tanggal_Pengambilan, Keterangan))
                conn.commit()
            
            if not request.form['keterangan'] == '':
                new_keterangan = request.form['keterangan']
                cursor.execute('UPDATE IGNORE reg_persekot_internadk SET Keterangan = %s WHERE Keterangan = %s', (new_keterangan, Keterangan))
                conn.commit()
            
            return redirect(url_for('adk'))

    return redirect(url_for('login'))

@app.route('/register/adk/hapus/<Keterangan>', methods=['GET', 'POST'])
def hapusadk(Keterangan):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'GET':
            cursor.execute('DELETE IGNORE FROM reg_persekot_internadk WHERE Keterangan = %s', (Keterangan))
            conn.commit()
            cursor.close()
            return redirect(url_for('adk'))
    return redirect(url_for('login'))


def is_admin():
    if 'level' in session and session['level'] == 'admin':
        return True
    else:
        return False


# Halaman daftar pengguna
@app.route('/group-chat', methods=['GET', 'POST'])
def group_chat():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'POST':
            message = request.form['message']
            sender = session['username']  # Mengambil username pengirim dari sesi
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Menyimpan pesan ke tabel GroupChat bersama dengan waktu pengiriman dan pengirim
            query = "INSERT INTO GroupChat (message, created_at, sender) VALUES (%s, %s, %s)"
            cursor.execute(query, (message, current_time, sender))
            conn.commit()
        # Mengambil semua pesan dari tabel GroupChat
        query = "SELECT * FROM GroupChat ORDER BY created_at ASC"
        cursor.execute(query)
        messages = cursor.fetchall()
        

        return render_template('group_chat.html', messages=messages)
    else:
        return redirect(url_for('login'))
    
@app.route('/clear-chat', methods=['POST'])
def clear_chat():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        # Hapus semua data dari tabel GroupChat
        query = "TRUNCATE TABLE GroupChat"
        cursor.execute(query)
        conn.commit()
        return redirect(url_for('group_chat'))
    else:
        return redirect(url_for('login'))



'''@app.route('/notes', methods=['GET', 'POST'])
def notes():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'loggedin' in session:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            # Menyimpan judul dan konten catatan ke tabel Notes
            query = "INSERT INTO Notes (title, content) VALUES (%s, %s)"
            cursor.execute(query, (title, content,))
            conn.commit()
    
    # Mengambil semua catatan dari tabel Notes
    query = "SELECT * FROM Notes"
    cursor.execute(query)
    notes = cursor.fetchall()

    return render_template('notes.html', notes=notes)




@app.route('/obrolan')
def obrolan():
    if 'username' in session:
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM user")
        users = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('obrolan.html', users=users)
    else:
        return redirect('/login')

@app.route('/room-chat/<int:user_id>')
def room_chat(user_id):
    if 'username' in session:
        conn = mysql.connect()
        cur = conn.cursor()

        # Ambil informasi pengguna yang sedang login
        current_user_id = session['user_id']
        cur.execute("SELECT username FROM user WHERE id = %s", (current_user_id,))
        current_username = cur.fetchone()[0]

        # Ambil informasi pengguna yang akan diajak obrolan
        cur.execute("SELECT username FROM user WHERE id = %s", (user_id,))
        target_username = cur.fetchone()[0]

        # Ambil pesan yang dikirim antara kedua pengguna
        cur.execute("SELECT * FROM pesan WHERE (pengirim = %s AND penerima = %s) OR (pengirim = %s AND penerima = %s) ORDER BY tanggal_pengiriman ASC",
                    (current_user_id, user_id, user_id, current_user_id))
        pesan = cur.fetchall()
        session['user_id'] = user_id


        cur.close()
        conn.close()

        return render_template('room_chat.html', current_username=current_username, target_username=target_username, pesan=pesan)
    else:
        return redirect('/login')




@app.route("/delete", methods = ['GET'])
def delete():
    if 'loggedin' in session :
        deleteUserId = request.args.get('user')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM user WHERE username = %s', (deleteUserId,) )
        mysql.connection.commit()
        return redirect(url_for('user'))
    return redirect(url_for('login'))

# Fungsi untuk memeriksa apakah pengguna sudah login
def user_belum_login():
    return 'username' not in session

# Fungsi untuk mendapatkan pengguna yang sedang login
def get_current_user():
    return session['username']

# Register the function as a template context processor
@app.context_processor
def inject_current_user():
    return dict(get_current_user=get_current_user)



        

# Halaman pengiriman pesan
@app.route('/kirim-pesan', methods=['GET', 'POST'])
def kirim_pesan():
    if request.method == 'POST':
        penerima = request.form['penerima']
        isi_pesan = request.form['isi_pesan']
        
        if 'username' in session:
            pengirim = session['username']
            simpan_pesan(pengirim, penerima, isi_pesan)
            return redirect('/pesan')
        else:
            return render_template('error.html', message="Anda harus login untuk mengirim pesan.")
    
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user")
    user = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('kirim_pesan.html', user=user)

# Fungsi untuk menyimpan pesan ke database
def simpan_pesan(pengirim, penerima, isi_pesan):
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("SELECT id FROM user WHERE username = %s", (penerima,))
    result = cur.fetchone()
    if result:
        penerima_id = result[0]
        cur.execute("INSERT INTO pesan (pengirim, penerima, isi_pesan) VALUES (%s, %s, %s)", (pengirim, penerima_id, isi_pesan))
        conn.commit()
    cur.close()
    conn.close()

# Halaman pesan
@app.route('/pesan')
def pesan():
    if 'username' in session:
        pengguna = session['username']
        
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("SELECT u.username AS pengirim, p.isi_pesan, p.tanggal_pengiriman FROM pesan p JOIN user u ON p.pengirim = u.id JOIN user u2 ON p.penerima = u2.id WHERE u2.username = %s ORDER BY p.tanggal_pengiriman DESC", (pengguna,))
        pesan = cur.fetchall()
        cur.close()
        conn.close()
        
        return render_template('pesan.html', pesan=pesan, pengguna=pengguna)
    else:
        return redirect('/login')'''


# Fungsi untuk menghasilkan nama file yang unik
def generate_unique_filename(filename):
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    return unique_filename

@app.route('/laporan', methods=['GET'])
@app.route('/laporan/<int:page>', methods=['GET'])
def laporan(page=1):
    if 'loggedin' in session:
        username = session['username']
        conn = mysql.connect()
        cursor = conn.cursor()

        keterangan = request.args.get('keterangan')  # Ambil parameter pencarian keterangan

        # Retrieve laporan data from the database based on the search query and order by tanggal descending
        if keterangan:
            cursor.execute("SELECT * FROM laporan WHERE keterangan LIKE %s ORDER BY tanggal DESC", ('%' + keterangan + '%',))
        else:
            cursor.execute("SELECT * FROM laporan ORDER BY tanggal ASC")

        laporan = cursor.fetchall()

        # Update status laporan menjadi "read" untuk semua laporan
        cursor.execute("UPDATE laporan SET status = 'read'")
        conn.commit()

        # Commit perubahan ke database
        conn.commit()

        # Mendapatkan jumlah notifikasi yang belum dibaca oleh admin
        if session['level'] == 'admin':
            unread_counts = get_unread_notifications_count()
        else:
            unread_counts = 0

        # Set nilai unread_counts menjadi 0 saat halaman laporan dibuka
        session['unread_counts'] = 0

        # Count the total number of laporan
        cursor.execute("SELECT COUNT(*) FROM laporan")
        total_laporan = cursor.fetchone()[0]
        total_pages = math.ceil(total_laporan / 5)

        # Close cursor and database connection
        cursor.close()
        conn.close()

        return render_template('laporan.html', laporan=laporan, page=page, total_pages=total_pages, unread_counts=session.get('unread_counts', 0))

    return redirect(url_for('login'))

@app.route('/laporan/download/<int:laporan_id>', methods=['GET'])
def download_laporan(laporan_id):
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor()

        # Dapatkan informasi laporan berdasarkan ID dari database
        cursor.execute("SELECT * FROM laporan WHERE id = %s", (laporan_id,))
        laporan = cursor.fetchone()

        # Periksa apakah laporan ditemukan
        if laporan:
            # Periksa status laporan sebelum diubah
            if laporan[7] != 'read':  # Ganti indeks 3 dengan indeks yang benar untuk kolom status di tabel laporan
                # Update status laporan menjadi "read"
                cursor.execute("UPDATE laporan SET status = 'read' WHERE id = %s", (laporan_id,))
                conn.commit()

                # Kurangi nilai unread_counts sebanyak 1
                session['unread_counts'] = session.get('unread_counts', 0) - 1

            # Close cursor and database connection
            cursor.close()
            conn.close()

            # Lakukan proses unduh file
            file_name = laporan[7]  # Ganti dengan indeks yang benar untuk kolom yang menyimpan nama file di tabel laporan
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)  # Ganti dengan path direktori uploads yang sesuai
            if os.path.exists(file_path):
                return send_from_directory(app.config['UPLOAD_FOLDER'], file_name, as_attachment=True)

        # Jika laporan tidak ditemukan atau file tidak ada, kembali ke halaman laporan
        return redirect(url_for('laporan'))

    return redirect(url_for('login'))






@app.route('/laporan/hapus/<int:laporan_id>', methods=['POST'])
def hapus_laporan(laporan_id):
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor()

        # Hapus laporan berdasarkan ID dari database
        cursor.execute("DELETE FROM laporan WHERE id = %s", (laporan_id,))
        conn.commit()

        # Close cursor and database connection
        cursor.close()
        conn.close()

        return redirect(url_for('laporan'))

    return redirect(url_for('login'))


@app.route('/laporan/edit/<int:laporan_id>', methods=['GET', 'POST'])
def edit_laporan(laporan_id):
    if 'loggedin' in session:
        if request.method == 'POST':
            judul = request.form['judul']
            keterangan = request.form['keterangan']

            conn = mysql.connect()
            cursor = conn.cursor()

            # Update data laporan berdasarkan ID
            cursor.execute("UPDATE laporan SET judul = %s, keterangan = %s WHERE id = %s",
                           (judul, keterangan, laporan_id))
            conn.commit()

            # Close cursor and database connection
            cursor.close()
            conn.close()

            return redirect(url_for('laporan'))

        else:
            conn = mysql.connect()
            cursor = conn.cursor()

            # Ambil data laporan berdasarkan ID dari database
            cursor.execute("SELECT * FROM laporan WHERE id = %s", (laporan_id,))
            laporan = cursor.fetchone()

            # Close cursor and database connection
            cursor.close()
            conn.close()

            return render_template('edit_laporan.html', laporan=laporan)

    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'loggedin' in session:
        if request.method == 'POST':
            # Mengambil data dari form
            judul = request.form.get('judul')
            keterangan = request.form.get('keterangan')
            dokumen = request.files.get('dokumen')
            username = session['username']
            tanggal = date.today().strftime("%Y-%m-%d")

            if judul and keterangan:
                dokumen_filename = None
                if dokumen and dokumen.filename != '':
                    # Mengamankan nama file yang diunggah
                    dokumen_filename = secure_filename(dokumen.filename)
                    # Menyimpan file ke direktori UPLOAD_FOLDER yang telah dikonfigurasi
                    dokumen.save(os.path.join(app.config['UPLOAD_FOLDER'], dokumen_filename))

                # Mendapatkan koneksi database
                conn = mysql.connect()
                cursor = conn.cursor()

                # Insert data laporan ke dalam database
                cursor.execute('INSERT INTO laporan (username, tanggal, judul, keterangan, file_laporan) VALUES (%s, %s, %s, %s, %s)',
                               (username, tanggal, judul, keterangan, dokumen_filename))
                conn.commit()

                # Membuat notifikasi baru untuk admin
                if session['level'] == 'admin':
                    cursor.execute('SELECT id FROM user WHERE level = "admin"')
                    admin_id = cursor.fetchone()[0]
                    laporan_id = cursor.lastrowid
                    cursor.execute('INSERT INTO notifications (user_id, laporan_id) VALUES (%s, %s)',
                                   (admin_id, laporan_id))
                    conn.commit()

                cursor.close()
                conn.close()

                return redirect(url_for('upload'))

        return render_template('upload.html')

    return redirect(url_for('login'))

def update_unread_notifications_count(count):
    session['unread_count'] = count

def get_unread_notifications_count():
    if 'loggedin' in session and session['level'] == 'admin':
        conn = mysql.connect()
        cursor = conn.cursor()

        # Mengambil jumlah notifikasi yang belum terbaca dari tabel notifikasi
        cursor.execute("SELECT COUNT(*) FROM notifikasi WHERE status = 'unread'")
        unread_count = cursor.fetchone()[0]

        # Menutup cursor dan koneksi database
        cursor.close()
        conn.close()

        return unread_count
    else:
        return 0

@app.route('/laporan/set_read/<int:laporan_id>', methods=['GET'])
def set_read(laporan_id):
    if 'loggedin' in session and session['level'] == 'admin':
        conn = mysql.connect()
        cursor = conn.cursor()

        # Update status laporan menjadi "read" berdasarkan ID
        cursor.execute("UPDATE laporan SET status = 'read' WHERE id = %s", (laporan_id,))
        conn.commit()

        # Close cursor and database connection
        cursor.close()
        conn.close()

        # Mengurangi unreads_count
        update_unread_notifications_count()

        return jsonify({'status': 'success'})  # Mengirim respons JSON jika berhasil

    return jsonify({'status': 'error'})  # Mengirim respons JSON jika terjadi kesalahan



@app.route('/laporan_restrukturisasi')
def laporan_restrukturisasi():
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # Mengambil data debitur yang melewati jangka waktu dari database
        today = datetime.date.today()
        cursor.execute("SELECT namadebitur, norek, jangkawaktu, akad, jadwaltempo  FROM datadebitur WHERE jadwaltempo < %s", (today,))
        debitur_laporan = cursor.fetchall()


        cursor.close()

        return render_template('laporan_restrukturisasi.html', debitur_laporan=debitur_laporan)

    return redirect(url_for('login'))




  
@app.route('/logout')
def logout():
   session.clear()
   return redirect(url_for('login'))


  
if __name__ == '__main__':
    app.run(debug=True)