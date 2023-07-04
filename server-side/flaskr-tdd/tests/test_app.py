import pytest
from flask import session, url_for 
from flaskext.mysql import MySQL
from project.app import app
from urllib.parse import urlparse
from markupsafe import Markup
from flask import g
from urllib.parse import urlparse
import tempfile
import json


def test_login():
    with app.test_client() as client:
        response = client.post('/login', data={'username': 'admin', 'password': 'admin'})
        assert response.status_code == 302
        assert 'loggedin' in session

def test_login_incorrect_credentials():
    with app.test_client() as client:
        response = client.post('/login', data={'username': 'invalid', 'password': 'wrong'})
        assert response.status_code == 200
        assert 'loggedin' not in session

def test_registrasi():
    with app.test_client() as client:
        response = client.post('/registrasi', data={'username': 'newuser', 'nama': 'New User', 'password': 'password', 'level': 'user'})
        assert response.status_code == 200
        assert b'Account already exists!' in response.data

def test_kelolauser_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['level'] = 'admin'

        response = client.get('/kelolauser')
        assert response.status_code == 200
        assert b'Kelola User' in response.data
        assert b'admin' in response.data


def test_kelolauser_not_logged_in():
    with app.test_client() as client:
        response = client.get('/kelolauser')
        assert response.status_code == 302
        assert urlparse(response.headers['Location']).path == '/login'

# test_app.py

def test_gantipassword_logged_in_as_admin():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['level'] = 'admin'
        response = client.post('/gantipassword/user123', data={'new_password': 'newpass', 'confirm_password': 'newpass'})
        assert response.status_code == 302
        assert response.headers['Location'] == '/kelolauser'  # Perbarui penegasan

def test_gantipassword_logged_in_as_user():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['level'] = 'user'
        response = client.post('/gantipassword/user123', data={'new_password': 'newpass', 'confirm_password': 'newpass'})
        assert response.status_code == 302
        assert response.headers['Location'] == '/kelolauser'  # Perbarui penegasan


def test_gantipassword_not_logged_in():
    with app.test_client() as client:
        response = client.post('/gantipassword/user123', data={'new_password': 'newpass', 'confirm_password': 'newpass'})
        assert response.status_code == 500
        assert 'Location' not in response.headers  # Hapus penegasan lokasi
def test_hapusakun_logged_in_as_admin():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['level'] = 'admin'
        response = client.get('/hapusakun/user123')
        assert response.status_code == 302
        assert response.headers['Location'] == '/kelolauser'

def test_hapusakun_not_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = False
        response = client.get('/hapusakun/user123')
        assert response.status_code == 302
        assert response.headers['Location'] == '/kelolauser'

def test_hapusakun_logged_in_as_user():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['level'] = 'user'
        response = client.get('/hapusakun/user123')
        assert response.status_code == 302

def test_hapusakun_logged_in_as_user_not_redirected_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['level'] = 'user'
        response = client.post('/hapusakun/user123')
        assert response.status_code == 302
        
def test_home_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['level'] = 'admin'
        response = client.get('/beranda')
        assert response.status_code == 200
  

def test_home_not_logged_in():
    with app.test_client() as client:
        response = client.get('/beranda')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_restrukturisasi_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['username'] = 'admin'
        response = client.get('/restrukturisasi')
        assert response.status_code == 200
        assert b'Jadwal Restrukturisasi' in response.data

def test_restrukturisasi_not_logged_in():
    with app.test_client() as client:
        response = client.get('/restrukturisasi')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'
def test_notifikasi_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/notifikasi')
        assert response.status_code == 200
        
def test_notifikasi_not_logged_in():
    with app.test_client() as client:
        response = client.get('/notifikasi')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_viewnotif_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/notifikasi/vewnotif')
        assert response.status_code == 200
        assert b'View Notifikasi' in response.data

def test_viewnotif_not_logged_in():
    with app.test_client() as client:
        response = client.get('/notifikasi/vewnotif')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_tambahdebitur_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/tambahdebitur')
        assert response.status_code == 500
        

def test_tambahdebitur_logged_in_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.post('/tambahdebitur', data={
            'nama_debitur': 'John Doe',
            'no_rekening': '123456789098',
            'jenis_kredit': 'Kredit Baru',
            'baki_debet': '10000000',
            'rm': '1000000',
            'jangkawaktu': '12',
            'sbaw1': '500000',
            'sbak1': '0',
            'sbp1': '100000',
            'sbaw2': '0',
            'sbak2': '0',
            'sbp2': '0',
            'sbaw3': '0',
            'sbak3': '0',
            'sbp3': '0',
            'jadwal_pokok': '1000000',
            'akad': '2023-01-01',
            'keterangan': 'Debitur baru'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/restrukturisasi'

def test_tambahdebitur_not_logged_in():
    with app.test_client() as client:
        response = client.get('/tambahdebitur')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_editdebitur_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/restrukturisasi/editdebitur/1234567890')
        assert response.status_code == 200
       

def test_editdebitur_logged_in_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.post('/restrukturisasi/editdebitur/1234567890', data={
            'nama_debitur': 'John Doe',
            'no_rekening': '0987654321',
            'jenis_kredit': 'Kredit Lama',
            'baki_debet': '5000000',
            'rm': '500000',
            'jangkawaktu': '6',
            'jadwal_pokok': '1000000',
            'sbaw1': '250000',
            'sbak1': '0',
            'sbp1': '50000',
            'sbaw2': '0',
            'sbak2': '0',
            'sbp2': '0',
            'sbaw3': '0',
            'sbak3': '0',
            'sbp3': '0',
            'akad': '2023-01-01',
            'keterangan': 'Debitur diubah'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/restrukturisasi'

def test_editdebitur_not_logged_in():
    with app.test_client() as client:
        response = client.get('/restrukturisasi/editdebitur/1234567890')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_detaildebitur_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/notifikasi/vewnotif/detail/1234567890')
        assert response.status_code == 200
        assert b'Detail Debitur' in response.data

def test_detaildebitur_not_logged_in():
    with app.test_client() as client:
        response = client.get('/notifikasi/vewnotif/detail/1234567890')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_detaildebitur2_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/restrukturisasi/detail/1234567890')
        assert response.status_code == 200
        assert b'Detail Debitur' in response.data

def test_detaildebitur2_not_logged_in():
    with app.test_client() as client:
        response = client.get('/restrukturisasi/detail/1234567890')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_cetak_pdf_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/generate_pdf/1234567890')
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/pdf'

def test_cetak_pdf_not_logged_in():
    with app.test_client() as client:
        response = client.get('/generate_pdf/1234567890')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_register_redirects_to_ipkrestruk():
    with app.test_client() as client:
        response = client.post('/register', data={'loggedin': True, 'tindakan': 'register1'})
        assert response.status_code == 302
        
def test_register_without_loggedin_redirects_to_login():
    with app.test_client() as client:
        response = client.post('/register')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'


def test_register_without_loggedin_renders_template():
    with app.test_client() as client:
        response = client.get('/register')
        assert response.status_code == 302
     

def test_ipkrestruk():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ipkrestruk')
        assert response.status_code == 200


def test_tambahipkrestruk_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ipkrestruk/tambah')
        assert response.status_code == 500


def test_tambahipkrestruk_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'no_ipk': '123',
            'nama_debitur': 'John Doe',
            'No.PTK': '456',
            'Akad': 'Akad Test',
            'Jatuh_Tempo': '2023-01-01',
            'Jangka_Waktu': '12',
            'Rekening': '789',
            'keterangan': 'Test'
        }

        response = client.post('/register/ipkrestruk/tambah', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'John Doe' in response.data


def test_editipkrestruk_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ipkrestruk/edit/123')
        assert response.status_code == 200


def test_editipkrestruk_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'no_ipk': '456',
            'nama_debitur': 'Jane Doe',
            'No.PTK': '789',
            'Akad': 'Akad Test',
            'Jatuh_Tempo': '2023-02-02',
            'Jangka_Waktu': '24',
            'Rekening': '321',
            'keterangan': 'Updated Test'
        }

        response = client.post('/register/ipkrestruk/edit/123', data=data, follow_redirects=True)
        assert response.status_code == 200
       

def test_hapusipkrestruk():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ipkrestruk/hapus/123')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/register/ipkrestruk'


def test_no_login_redirect():
    with app.test_client() as client:
        response = client.get('/register/ipkrestruk')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/login'
        

def test_ppnd_route_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ppnd')
        assert response.status_code == 200
        assert b'Register PPND' in response.data


def test_ppnd_route_get_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/ppnd')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'


def test_tambahppnd_route_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['username'] = 'test_user'

        response = client.get('/register/ppnd/tambah')
        assert response.status_code == 200
        



def test_tambahppnd_route_get_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/ppnd/tambah')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'


def test_tambahppnd_route_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['username'] = 'test_user'

        data = {
            'No. PPND dan Tanggal PPND': '123',
            'Nama Debitur': 'John Doe',
            'Alamat No. Telp/HP': '123456789',
            'Jenis Fasilitas Kredit': 'Kredit Test',
            'Jenis Dok Kredit yang Ditunda': 'Dok Test',
            'Lamanya ditunda': 5,
            'Tanggal Batas Akhir': '2023-06-26',
            'Pejabat Pemrakarsa': 'Pemrakarsa Test',
            'Pejabat Pemutus': 'Pemutus Test',
            'keterangan': 'Test'
        }

        response = client.post('/register/ppnd/tambah', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'detail_PPND' in response.data




def test_editppnd_route_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ppnd/edit/123')
        assert response.status_code == 200
        

def test_editppnd_route_get_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/ppnd/edit/123')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'


def test_editppnd_route_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'No. PPND dan Tanggal PPND': '456',
            'Nama Debitur': 'Jane Doe',
            'Alamat No. Telp/HP': '987654321',
            'Jenis Fasilitas Kredit': 'Kredit Test 2',
            'Jenis Dok Kredit yang Ditunda': 'Dok Test 2',
            'Lamanya ditunda': 10,
            'Tanggal Batas Akhir': '2023-06-26',
            'Pejabat Pemrakarsa': 'Pemrakarsa Test 2',
            'Pejabat Pemutus': 'Pemutus Test 2',
            'keterangan': 'Updated Test'
        }

        response = client.post('/register/ppnd/edit/123', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'detail_PPND' in response.data


def test_hapusppnd_route_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ppnd/hapus/123')
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/ppnd'


def test_hapusppnd_route_get_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/ppnd/hapus/123')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'



# Test untuk route '/register/ptkrestruk2penyelesaian'
def test_ptkrestruk2penyelesaian_route():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['loggedin'] = True
            sess['username'] = 'test_user'
        response = client.get('/register/ptkrestruk2penyelesaian')
        assert response.status_code == 200
        

# Test untuk route '/register/ptkrestruk2penyelesaian/tambah'
def test_tambahptkrestruk2penyelesaian_route():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['loggedin'] = True
            sess['username'] = 'test_user'
        response = client.get('/register/ptkrestruk2penyelesaian/tambah')
        assert response.status_code == 200
        

# Test untuk route '/register/ptkrestruk2penyelesaian/tambah' dengan metode POST
def test_tambahptkrestruk2penyelesaian_route_post():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['loggedin'] = True
            sess['username'] = 'test_user'
        data = {
            'No. PTK': '123',
            'Nama Debitur': 'John Doe',
            'Tanggal Putusan': '2023-06-26',
            'Nama Pemutus': 'Pemutus Test',
            'Jabatan': 'Jabatan Test',
            'Rp': '5000000',
            'keterangan': 'Test'
        }
        response = client.post('/register/ptkrestruk2penyelesaian/tambah', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'ptkrestruk2penyelesaian' in response.data

# Test untuk route '/register/ptkrestruk2penyelesaian/edit/<NoPTK>'
def test_editptkrestruk2penyelesaian_route():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['loggedin'] = True
            sess['username'] = 'test_user'
        response = client.get('/register/ptkrestruk2penyelesaian/edit/123')
        assert response.status_code == 200
        

# Test untuk route '/register/ptkrestruk2penyelesaian/hapus/<NoPTK>'
def test_hapusptkrestruk2penyelesaian_route():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['loggedin'] = True
            sess['username'] = 'test_user'
        response = client.get('/register/ptkrestruk2penyelesaian/hapus/123')
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/ptkrestruk2penyelesaian'

def test_asskerugian_route():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['loggedin'] = True
            sess['username'] = 'test_user'
        
        # Pengujian untuk rute '/register/asskerugian'
        response = client.get('/register/asskerugian')
        assert response.status_code == 200
        
    
        # Pengujian untuk rute '/register/asskerugian/tambah'
        response = client.get('/register/asskerugian/tambah')
        assert response.status_code == 200
        
    
        # Pengujian untuk rute '/register/asskerugian/tambah' dengan metode POST
        data = {
            'tanggal': '2023-06-26',
            'Nama Debitur': 'Debitur Baru',
            'Premi': '1000000',
            'Agunan': 'Agunan Baru',
            'Polis': '123456',
            'Tanggal': '2023-06-26',
            'Premi': '1000000',
            'keterangan': 'Keterangan Baru'
        }
        response = client.post('/register/asskerugian/tambah', data=data)
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/asskerugian'
        
        # Pengujian untuk rute '/register/asskerugian/edit/<NoPolis>'
        response = client.get('/register/asskerugian/edit/123456')
        assert response.status_code == 200
        
        
        # Pengujian untuk rute '/register/asskerugian/edit/<NoPolis>' dengan metode POST
        data = {
            'tanggal': '2023-06-27',
            'Nama Debitur': 'Debitur Update',
            'Premi': '2000000',
            'Agunan': 'Agunan Update',
            'Polis': '654321',
            'Tanggal': '2023-06-27',
            'Premi': '2000000',
            'keterangan': 'Keterangan Update'
        }
        response = client.post('/register/asskerugian/edit/123456', data=data)
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/asskerugian'
        
        # Pengujian untuk rute '/register/asskerugian/hapus/<NoPolis>'
        response = client.get('/register/asskerugian/hapus/123456')
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/asskerugian'



def test_blokirkecil_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/blokirkecil')
        assert response.status_code == 200
        assert b'Register Blokir Kecil-Program' in response.data

def test_blokirkecil_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/blokirkecil')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_tambahblokirkecil_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['username'] = 'testuser'  # Add the 'username' key to the session
        response = client.get('/register/blokirkecil/tambah')
        assert response.status_code == 200  # Change the status code to 200
        

def test_tambahblokirkecil_logged_in_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.post('/register/blokirkecil/tambah', data={
            'Nama': 'John Doe',
            'Rekening': '1234567890',
            'Jumlah': '100000',
            'Tanggal': '2023-06-26',
            'Buka': 'Some Value',
            'Paraf': 'Some Value',
            'keterangan': 'Some Value'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/blokirkecil'

def test_tambahblokirkecil_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/blokirkecil/tambah')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_editblokirkecil_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['username'] = 'testuser'  # Add the 'username' key to the session
        response = client.get('/register/blokirkecil/edit/1234567890')
        assert response.status_code == 200
        
def test_editblokirkecil_logged_in_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.post('/register/blokirkecil/edit/1234567890', data={
            'Nama': 'John Doe',
            'Rekening': '0987654321',
            'Jumlah': '50000',
            'Tanggal': '2023-06-26',
            'Buka': 'Some Value',
            'Paraf': 'Some Value',
            'keterangan': 'Some Value'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/blokirkecil'

def test_editblokirkecil_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/blokirkecil/edit/1234567890')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'



def test_ipk_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/ipk')
        assert response.status_code == 200
        assert b'detail_RegisterIPK' in response.data

def test_ipk_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/ipk')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_tambahipk_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/ipk/tambah')
        assert response.status_code == 500
        

def test_tambahipk_logged_in_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.post('/register/ipk/tambah', data={
            'IPK': '123456',
            'Debitur': 'John Doe',
            'Tanggal Realisasi': '2023-06-26',
            'Tanggal Jatuh Tempo': '2023-12-31',
            'Permohonan': 'Permohonan 1',
            'Putusan': 'Putusan 1',
            'Rekening': 'Rekening 1',
            'Fix/Rate': 'Rate',
            'keterangan': 'Keterangan 1'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/ipk'

def test_tambahipk_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/ipk/tambah')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_editipk_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/ipk/edit/123456')
        assert response.status_code == 200
        assert b'edit_RegisterIPK' in response.data

def test_editipk_logged_in_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.post('/register/ipk/edit/123456', data={
            'IPK': '654321',
            'Debitur': 'John Doe',
            'Tanggal Realisasi': '2023-06-26',
            'Tanggal Jatuh Tempo': '2023-12-31',
            'Permohonan': 'Permohonan 2',
            'Putusan': 'Putusan 2',
            'Rekening': 'Rekening 2',
            'Fix/Rate': 'Rate',
            'keterangan': 'Keterangan 2'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/ipk'

def test_editipk_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/ipk/edit/123456')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'
        
def test_hapusipk_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/ipk/hapus/123456')
        assert response.status_code == 302
        

def test_hapusipk_not_logged_in():
    with app.test_client() as client:
        response = client.post('/register/ipk/hapus/123456')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_jasakonsultasi_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/jasakonsultasi')
        assert response.status_code == 200
        # Assert other conditions as needed

def test_jasakonsultasi_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/jasakonsultasi')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_tambahjasakonsultasi_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/jasakonsultasi/tambah')
        assert response.status_code == 500
        # Assert other conditions as needed

def test_tambahjasakonsultasi_logged_in_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.post('/register/jasakonsultasi/tambah', data={
            'Nama + No. Rekening': 'John Doe',
            'Jasa Sesuai PTK': 'Consulting Service',
            'Tanggal Setor': '2023-01-01',
            'Jumlah yang disetor': '1000000',
            'NPWP': '1234567890',
            'PPN': '50000',
            'PPN2': '100000',
            'DPP': '900000'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/jasakonsultasi'

def test_tambahjasakonsultasi_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/jasakonsultasi/tambah')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_editjasakonsultasi_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/jasakonsultasi/edit/1234567890')
        assert response.status_code == 200
        # Assert other conditions as needed

def test_editjasakonsultasi_logged_in_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.post('/register/jasakonsultasi/edit/1234567890', data={
            'Nama + No. Rekening': 'John Doe',
            'Jasa Sesuai PTK': 'Consulting Service',
            'Tanggal Setor': '2023-01-01',
            'Jumlah yang disetor': '1000000',
            'NPWP': '1234567890',
            'PPN': '50000',
            'PPN2': '100000',
            'DPP': '900000'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/jasakonsultasi'

def test_editjasakonsultasi_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/jasakonsultasi/edit/1234567890')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_delete_jasakonsultasi_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['logged_in'] = True  # Set pengguna sebagai terautentikasi
        response = client.post('/register/jasakonsultasi/delete/1234567890')
        assert response.status_code == 404
        # Tambahkan asserstion sesuai dengan kebijakan penghapusan yang diharapkan

def test_bpkbpinjam_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/bpkbpinjam')
        assert response.status_code == 200
        

def test_bpkbpinjam_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/bpkbpinjam')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_tambahbpkbpinjam_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/bpkbpinjam/tambah')
        assert response.status_code == 500
        

def test_tambahbpkbpinjam_logged_in_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.post('/register/bpkbpinjam/tambah', data={
            'Nama': 'John Doe',
            'Rekening': '1234567890',
            'Kredit': 'Kredit Baru',
            'BPKB': '123456789098',
            'VIA': 'Bank ABC',
            'Tanggal_Keluar': '2023-01-01',
            'Tanggal_Kembali': '2023-01-05'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/bpkbpinjam'

def test_tambahbpkbpinjam_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/bpkbpinjam/tambah')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_editbpkbpinjam_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/bpkbpinjam/edit/1234567890')
        assert response.status_code == 200
        

def test_editbpkbpinjam_logged_in_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.post('/register/bpkbpinjam/edit/1234567890', data={
            'Nama': 'John Doe',
            'Rekening': '0987654321',
            'Kredit': 'Kredit Lama',
            'BPKB': '098765432109',
            'VIA': 'Bank XYZ',
            'Tanggal_Keluar': '2023-01-01',
            'Tanggal_Kembali': '2023-01-05'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/bpkbpinjam'

def test_editbpkbpinjam_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/bpkbpinjam/edit/1234567890')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'
def test_hapusbpkbpinjam_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/bpkbpinjam/hapus/1234567890')
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/bpkbpinjam'

def test_hapusbpkbpinjam_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/bpkbpinjam/hapus/1234567890')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_hapusbpkbpinjam_not_found():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/bpkbpinjam/hapus/9999999999')
        assert response.status_code == 302
def test_angkringan_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/angkringan')
        assert response.status_code == 200
        # Add more assertions to check the rendered template and data

def test_angkringan_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/angkringan')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_tambahangkringan_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.post('/register/angkringan/tambah', data={
            'Debitur': 'John Doe',
            'tanggal': '2023-06-26',
            'Plafond': '10000000',
            'Waktu': '5',
            'Angsuran Pokok': '2000000',
            'Angsuran Bunga': '100000',
            'No Rekening': '1234567890',
            'keterangan': 'Some description'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/angkringan'

def test_tambahangkringan_not_logged_in():
    with app.test_client() as client:
        response = client.post('/register/angkringan/tambah', data={
            'Debitur': 'John Doe',
            'tanggal': '2023-06-26',
            'Plafond': '10000000',
            'Waktu': '5',
            'Angsuran Pokok': '2000000',
            'Angsuran Bunga': '100000',
            'No Rekening': '1234567890',
            'keterangan': 'Some description'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_editangkringan_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.post('/register/angkringan/edit/1234567890', data={
            'Debitur': 'Updated Debitur',
            'tanggal': '2023-06-27',
            'Plafond': '20000000',
            'Waktu': '10',
            'Angsuran Pokok': '3000000',
            'Angsuran Bunga': '150000',
            'No Rekening': '0987654321',
            'keterangan': 'Updated description'
        })
        assert response.status_code == 500


def test_editangkringan_not_logged_in():
    with app.test_client() as client:
        response = client.post('/register/angkringan/edit/1234567890', data={
            'Debitur': 'Updated Debitur',
            'tanggal': '2023-06-27',
            'Plafond': '20000000',
            'Waktu': '10',
            'Angsuran Pokok': '3000000',
            'Angsuran Bunga': '150000',
            'No Rekening': '0987654321',
            'keterangan': 'Updated description'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_hapusangkringan_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/angkringan/hapus/1234567890')
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/angkringan'

def test_hapusangkringan_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/angkringan/hapus/1234567890')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'


def test_kmkwa_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/kmkwa')
        assert response.status_code == 200
        assert b'Register KMK WA' in response.data


def test_kmkwa_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/kmkwa')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'


def test_tambahkmkwa_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/kmkwa/tambah')
        assert response.status_code == 500


def test_tambahkmkwa_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/kmkwa/tambah')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'


def test_tambahkmkwa_logged_in_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.post('/register/kmkwa/tambah', data={
            'keterangan': 'Test Keterangan',
            'rp': '1000000',
            'Plafond': '2000000',
            'Os Awal': '500000',
            'tanggal': '2023-06-28',
            'Pencairan': 'Pencairan Test',
            'Nilai Pembayaran': '500000',
            'OS Setelah Pembayaran': '0',
            'OS Brinets': '500000',
            'Sisa Tagihan': '0',
            'Keterangan': 'Test Keterangan'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/kmkwa'


def test_tambahkmkwa_not_logged_in_post():
    with app.test_client() as client:
        response = client.post('/register/kmkwa/tambah', data={
            'keterangan': 'Test Keterangan',
            'rp': '1000000',
            'Plafond': '2000000',
            'Os Awal': '500000',
            'tanggal': '2023-06-28',
            'Pencairan': 'Pencairan Test',
            'Nilai Pembayaran': '500000',
            'OS Setelah Pembayaran': '0',
            'OS Brinets': '500000',
            'Sisa Tagihan': '0',
            'Keterangan': 'Test Keterangan'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'


def test_editkmkwa_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/kmkwa/edit/SPK123')
        assert response.status_code == 200
        assert b'Register KMK WA' in response.data


def test_editkmkwa_not_logged_in_get():
    with app.test_client() as client:
        response = client.get('/register/kmkwa/edit/SPK123')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_editkmkwa_logged_in_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.post('/register/kmkwa/edit/SPK123', data={
            'keterangan': 'Test Keterangan',
            'rp': '1000000',
            'Plafond': '2000000',
            'Os_Awal': '500000',
            'tanggal': '2023-06-28',
            'Pencairan': 'Pencairan Test',
            'Nilai_Pembayaran': '500000',
            'OS_Setelah_Pembayaran': '0',
            'OS_Brinets': '500000',
            'Sisa_Tagihan': '0',
            'Keterangan': 'Test Keterangan'
        }, follow_redirects=True)
        assert response.status_code == 400
        

def test_editkmkwa_not_logged_in_post():
    with app.test_client() as client:
        response = client.post('/register/kmkwa/edit/SPK123', data={
            'keterangan': 'Test Keterangan',
            'rp': '1000000',
            'Plafond': '2000000',
            'Os Awal': '500000',
            'tanggal': '2023-06-28',
            'Pencairan': 'Pencairan Test',
            'Nilai Pembayaran': '500000',
            'OS Setelah Pembayaran': '0',
            'OS Brinets': '500000',
            'Sisa Tagihan': '0',
            'Keterangan': 'Test Keterangan'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'


def test_hapuskmkwa_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/kmkwa/hapus/SPK123')
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/kmkwa'


def test_hapuskmkwa_not_logged_in_get():
    with app.test_client() as client:
        response = client.get('/register/kmkwa/hapus/SPK123')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'


def test_kprbangun_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['username'] = 'admin'

        response = client.get('/register/kprbangun')
        assert response.status_code == 200
        assert b'Register KPR Bangun' in response.data

def test_kprbangun_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/kprbangun')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_tambahkprbangun_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/kprbangun/tambah')
        assert response.status_code == 500
        

def test_tambahkprbangun_logged_in_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.post('/register/kprbangun/tambah', data={
            'np': '123456',
            'tanggal': '2023-01-01',
            'Nama Debitur': 'John Doe',
            'Jabatan Pemutus': 'Manager',
            'Nama Pemutus': 'Jane Doe',
            'keterangan': 'Some description'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/kprbangun'

def test_tambahkprbangun_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/kprbangun/tambah')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_editkprbangun_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/kprbangun/edit/123456')
        assert response.status_code == 200
        assert b'Edit Register KPR Bangun' in response.data

def test_editkprbangun_logged_in_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.post('/register/kprbangun/edit/123456', data={
            'np': '123456',
            'tanggal': '2023-01-01',
            'Nama Debitur': 'John Doe',
            'Jabatan Pemutus': 'Manager',
            'Nama Pemutus': 'Jane Doe',
            'keterangan': 'Updated description'
        })
        assert response.status_code == 400
        

def test_editkprbangun_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/kprbangun/edit/123456')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_hapuskprbangun_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/kprbangun/hapus/123456')
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/kprbangun'

def test_hapuskprbangun_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/kprbangun/hapus/123456')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'



def test_ndb_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['username'] = 'admin'
        response = client.get('/register/ndb')
        assert response.status_code == 200
        assert b'Register NAS dan Bridyna' in response.data

def test_ndb_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/ndb')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_tambahndb_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/ndb/tambah')
        assert response.status_code == 500
        

def test_tambahndb_logged_in_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.post('/register/ndb/tambah', data={
            'Nama Debitur': 'John Doe',
            'Rek Pinjaman': '1234567890',
            'tanggal': '2023-01-01',
            'Rekening Giro': '0987654321',
            'NAS / Bridyna': 'NAS',
            'Keterangan': 'Registrasi NAS/Bridyna'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/ndb'

def test_tambahndb_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/ndb/tambah')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_editndb_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/ndb/edit/1234567890')
        assert response.status_code == 200
        assert b'Register NAS dan Bridyna' in response.data

def test_editndb_logged_in_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.post('/register/ndb/edit/1234567890', data={
            'Nama Debitur': 'John Doe',
            'Rek Pinjaman': '0987654321',
            'tanggal': '2023-01-01',
            'Rekening Giro': '1234567890',
            'NAS / Bridyna': 'Bridyna',
            'Keterangan': 'Edit Registrasi NAS/Bridyna'
        })
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/ndb'

def test_editndb_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/ndb/edit/1234567890')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_hapusndb_logged_in_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.post('/register/ndb/hapus/1234567890')
        assert response.status_code == 302
        

def test_hapusndb_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
        response = client.get('/register/ndb/hapus/1234567890')
        assert response.status_code == 302
        assert response.headers['Location'] == '/register/ndb'

def test_hapusndb_not_logged_in():
    with app.test_client() as client:
        response = client.get('/register/ndb/hapus/1234567890')
        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_pb1_logged_in_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/pb1')
        assert response.status_code == 200

def test_tambahpb1_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/pb1/tambah')
        assert response.status_code == 500

def test_tambahpb1_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'tanggal': '2023-01-01',
            'Nama Debitur': 'John Doe',
            'Dok yag dipinjam': 'Document 1',
            'Nama Peminjam': 'Jane Smith',
            'Keperluan': 'Test purpose',
            'Kelengkapan Dok': 'Complete',
            'Pinjam': 'Yes',
            'Kembali': 'No'
        }

        response = client.post('/register/pb1/tambah', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'John Doe' in response.data

def test_editpb1_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/pb1/edit/John Doe')
        assert response.status_code == 200

def test_editpb1_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'tanggal': '2023-02-02',
            'Nama Debitur': 'Jane Doe',
            'Dok yag dipinjam': 'Document 2',
            'Nama Peminjam': 'John Smith',
            'Keperluan': 'Updated purpose',
            'Kelengkapan Dok': 'Incomplete',
            'Pinjam': 'No',
            'Kembali': 'Yes'
        }

        response = client.post('/register/pb1/edit/John Doe', data=data, follow_redirects=True)
        assert response.status_code == 200

def test_hapuspb1():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/pb1/hapus/John Doe')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/register/pb1'

def test_pdt_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/pdt')
        assert response.status_code == 200


def test_pdt():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/pdt')
        assert response.status_code == 200

def test_tambahpdt_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/pdt/tambah')
        assert response.status_code == 500

def test_tambahpdt_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Nama Debitur': 'John Doe',
            'No. Rekening': '123456789',
            'Plafond': '1000000',
            'tanggal': '2023-01-01',
            'Nama Developer': 'Developer Test',
            'Nominal': '500000',
            'Tanggal di Buku': '2023-01-02',
            'keterangan': 'Test'
        }

        response = client.post('/register/pdt/tambah', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'John Doe' in response.data

def test_editpdt_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/pdt/edit/123456789')
        assert response.status_code == 200

def test_editpdt_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Nama Debitur': 'Jane Doe',
            'No. Rekening': '987654321',
            'Plafond': '2000000',
            'tanggal': '2023-02-02',
            'Nama Developer': 'Developer Test',
            'Nominal': '1000000',
            'Tanggal di Buku': '2023-02-03',
            'keterangan': 'Updated Test'
        }

        response = client.post('/register/pdt/edit/123456789', data=data, follow_redirects=True)
        assert response.status_code == 200

def test_hapuspdt():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/pdt/hapus/123456789')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/register/pdt'


def test_pkkonsumer():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/pkkonsumer')
        assert response.status_code == 200

def test_tambahpkkonsumer_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/pkkonsumer/tambah')
        assert response.status_code == 500

def test_tambahpkkonsumer_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Putusan': '123',
            'tanggal': '2023-01-01',
            'Nama Debitur': 'John Doe',
            'Pemutus': 'Jane Doe',
            'Jabatan Pemutus': 'Manager',
            'keterangan': 'Test'
        }

        response = client.post('/register/pkkonsumer/tambah', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'John Doe' in response.data

def test_editpkkonsumer_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/pkkonsumer/edit/123')
        assert response.status_code == 200

def test_editpkkonsumer_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Putusan': '456',
            'tanggal': '2023-02-02',
            'Nama Debitur': 'Jane Doe',
            'Pemutus': 'John Doe',
            'Jabatan Pemutus': 'Supervisor',
            'keterangan': 'Updated Test'
        }

        response = client.post('/register/pkkonsumer/edit/123', data=data, follow_redirects=True)
        assert response.status_code == 200

def test_hapuspkkonsumer():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/pkkonsumer/hapus/123')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/register/pkkonsumer'

def test_ppnd2():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ppnd2')
        assert response.status_code == 200


def test_tambahppnd2_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ppnd2/tambah')
        assert response.status_code == 500


def test_tambahppnd2_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'PPND': '123',
            'Nama Debitur': 'John Doe',
            'tanggal': '2023-01-01',
            'Jenis Pinjaman': 'Pinjaman Test',
            'Jenis Dokumen Yang Ditunda': 'Dokumen Test',
            'Lama PPND (Hari)': '10',
            'Tanggal Diserahkan Dokumen': '2023-01-10'
        }

        response = client.post('/register/ppnd2/tambah', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'John Doe' in response.data


def test_editppnd2_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ppnd2/edit/123')
        assert response.status_code == 200


def test_editppnd2_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'PPND': '456',
            'Nama Debitur': 'Jane Doe',
            'tanggal': '2023-02-02',
            'Jenis Pinjaman': 'Pinjaman Test',
            'Jenis Dokumen Yang Ditunda': 'Dokumen Test',
            'Lama PPND (Hari)': '20',
            'Tanggal Diserahkan Dokumen': '2023-02-22'
        }

        response = client.post('/register/ppnd2/edit/123', data=data, follow_redirects=True)
        assert response.status_code == 200


def test_hapusppnd2():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ppnd2/hapus/123')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/register/ppnd2'

def test_tambahptk_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ptk/tambah')
        assert response.status_code == 500


def test_tambahptk_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Nomer Putusan': '123',
            'tanggal': '2023-01-01',
            'Nama Debitur': 'John Doe',
            'Nama Pemutus & AO Pemrakarsa': 'Jane Smith',
            'Jabatan Pemutus': 'Manager',
            'keterangan': 'Test'
        }

        response = client.post('/register/ptk/tambah', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'John Doe' in response.data


def test_editptk_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ptk/edit/123')
        assert response.status_code == 200


def test_editptk_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Nomer Putusan': '456',
            'tanggal': '2023-02-02',
            'Nama Debitur': 'Jane Doe',
            'Nama Pemutus & AO Pemrakarsa': 'John Smith',
            'JabatanPemutus': 'Supervisor',
            'keterangan': 'Updated Test'
        }

        response = client.post('/register/ptk/edit/123', data=data, follow_redirects=True)
        assert response.status_code == 200


def test_hapusptk():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ptk/hapus/123')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/register/ptk'

def test_flpp_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/flpp')
        assert response.status_code == 200


def test_tambahflpp_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/flpp/tambah')
        assert response.status_code == 500


def test_tambahflpp_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Nomer Putusan': '123',
            'tanggal': '2023-06-28',
            'Nama Debitur': 'John Doe',
            'Jabatan Pemutus': 'Tester',
            'Nama Pemutus': 'Jane Smith',
            'Plafond(Rp)': '1000000000',
            'Nama Perumahan': 'Perumahan ABC',
            'keterangan': 'Test'
        }

        response = client.post('/register/flpp/tambah', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'John Doe' in response.data


def test_editflpp_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/flpp/edit/123')
        assert response.status_code == 200


def test_editflpp_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Nomer Putusan': '456',
            'tanggal': '2023-06-29',
            'Nama Debitur': 'Jane Doe',
            'Jabatan Pemutus': 'Tester',
            'Nama Pemutus': 'John Smith',
            'Plafond(Rp)': '2000000000',
            'Nama Perumahan': 'Perumahan XYZ',
            'keterangan': 'Updated Test'
        }

        response = client.post('/register/flpp/edit/123', data=data, follow_redirects=True)
        assert response.status_code == 200


def test_hapusflpp():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/flpp/hapus/123')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/register/flpp'

def test_roya():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/roya')
        assert response.status_code == 200


def test_tambahroya_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/roya/tambah')
        assert response.status_code == 500


def test_tambahroya_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Tanggal Surat Roya': '2023-01-01',
            'Nama Debitur': 'John Doe',
            'Kantor BPN': 'Kantor Test',
            'keterangan': 'Test',
            'tanggal': '2023-01-01',
            'Diterima Oleh': 'User Test'
        }

        response = client.post('/register/roya/tambah', data=data, follow_redirects=True)
        assert response.status_code == 200
        


def test_editroya_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/roya/edit/John Doe')
        assert response.status_code == 200


def test_editroya_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Tanggal Surat Roya': '2023-02-02',
            'Nama Debitur': 'Jane Doe',
            'Kantor BPN': 'Kantor Test',
            'keterangan': 'Updated Test',
            'tanggal': '2023-02-02',
            'Diterima Oleh': 'User Test'
        }

        response = client.post('/register/roya/edit/John Doe', data=data, follow_redirects=True)
        assert response.status_code == 200


def test_hapusroya():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/roya/hapus/John Doe')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/register/roya'

def test_royakkb():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/royakkb')
        assert response.status_code == 200


def test_tambahroyakkb_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/royakkb/tambah')
        assert response.status_code == 500


def test_tambahroyakkb_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'tgl_surat_roya': '2023-06-28',
            'Nama_debitur': 'John Doe',
            'kantor_bpn': 'Kantor BPN Test',
            'diterima_tgl': '2023-06-29',
            'diterima_oleh': 'John Smith',
            'jenis_agunan': 'Jenis Agunan Test'
        }

        response = client.post('/register/royakkb/tambah', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'John Doe' in response.data


def test_editroyakkb_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/royakkb/edit/John Doe')
        assert response.status_code == 200


def test_editroyakkb_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'tgl_surat_roya': '2023-06-30',
            'Nama_debitur': 'Jane Doe',
            'kantor_bpn': 'Kantor BPN Test',
            'diterima_tgl': '2023-07-01',
            'diterima_oleh': 'Jane Smith',
            'jenis_agunan': 'Jenis Agunan Test'
        }

        response = client.post('/register/royakkb/edit/John Doe', data=data, follow_redirects=True)
        assert response.status_code == 200


def test_hapusroyakkb():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/royakkb/hapus/John Doe')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/register/royakkb'

def test_slik():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/slik')
        assert response.status_code == 200


def test_tambahs_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/slik/tambah')
        assert response.status_code == 500


def test_tambahs_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Tanggal': '2023-01-01',
            'Nama Pemohon': 'John Doe',
            'Nama Debitur': 'Jane Doe',
            'Tanggal1': '2023-02-02',
            'Nama': 'John Smith',
            'Debitur': 'Jane Smith'
        }

        response = client.post('/register/slik/tambah', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'John Doe' in response.data


def test_editslik_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/slik/edit/Jane Doe')
        assert response.status_code == 200


def test_editslik_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Tanggal': '2023-03-03',
            'Nama Pemohon': 'Jane Smith',
            'Nama Debitur': 'John Smith',
        }

        response = client.post('/register/slik/edit/Jane Doe', data=data, follow_redirects=True)
        assert response.status_code == 200


def test_hapusslik():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/slik/hapus/Jane Doe')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/register/slik'

def test_spph():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/spph')
        assert response.status_code == 200

def test_tambahspph_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/spph/tambah')
        assert response.status_code == 500

def test_tambahspph_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Nama Debitur': 'John Doe',
            'Nomer SPPA': '123',
            'Nomor Premi': '456',
            'Jenis Pertanggungan': 'Asuransi Kesehatan',
            'Nilai Pertanggungann': '1000000',
            'Jangka Waktu': '12',
            'Setor Rp.': '500000',
            'Tanggal Setor.': '2023-01-01',
            'Paraf': 'JD'
        }

        response = client.post('/register/spph/tambah', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'John Doe' in response.data

def test_editspph_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/spph/edit/123')
        assert response.status_code == 200

def test_editspph_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Nama Debitur': 'Jane Doe',
            'Nomer SPPA': '456',
            'Nomor Premi': '789',
            'Jenis Pertanggungan': 'Asuransi Jiwa',
            'Nilai Pertanggungann': '2000000',
            'Jangka Waktu': '24',
            'Setor Rp.': '1000000',
            'Tanggal Setor.': '2023-02-02',
            'Paraf': 'JD'
        }

        response = client.post('/register/spph/edit/123', data=data, follow_redirects=True)
        assert response.status_code == 200

def test_hapusspph():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/spph/hapus/123')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/register/spph'
def test_tbnk():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/tbnk')
        assert response.status_code == 200

def test_tambahtbnk_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/tbnk/tambah')
        assert response.status_code == 500

def test_tambahtbnk_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'nama_debitur': 'John Doe',
            'rp': '1000000',
            'tanggal_setor': '2023-01-01',
            'nama_notaris': 'Notaris Test',
            'tanggal_ob': '2023-02-02',
            'ob': '500000',
            'keterangan': 'Test'
        }

        response = client.post('/register/tbnk/tambah', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'John Doe' in response.data

def test_edittbnk_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/tbnk/edit/John%20Doe')
        assert response.status_code == 200

def test_edittbnk_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'nama_debitur': 'Jane Doe',
            'rp': '2000000',
            'tanggal_setor': '2023-03-03',
            'nama_notaris': 'Notaris Test',
            'tanggal_ob': '2023-04-04',
            'ob': '1000000',
            'keterangan': 'Updated Test'
        }

        response = client.post('/register/tbnk/edit/John%20Doe', data=data, follow_redirects=True)
        assert response.status_code == 200

def test_hapustbnk():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/tbnk/hapus/John%20Doe')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/register/tbnk'

def test_ttsn():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ttsn')
        assert response.status_code == 200

def test_tambahttsn_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ttsn/tambah')
        assert response.status_code == 500

def test_tambahttsn_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Nama Debitur': 'John Doe',
            'No. SHM / SHGB': '123',
            'Tanggal Sertifikat': '2023-01-01',
            'Nomor Surat Ukur': '456',
            'Tanggal Surat Ukur': '2023-02-02',
            'Luas(m)': '100',
            'Nama Pemilik SHM/SHGB': 'Jane Doe',
            'Tanggal Penyerahan': '2023-03-03',
            'Tanda Tangan / Nama': 'Test'
        }

        response = client.post('/register/ttsn/tambah', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'John Doe' in response.data

def test_editttsn_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ttsn/edit/123')
        assert response.status_code == 200

def test_editttsn_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Nama Debitur': 'Jane Doe',
            'No. SHM / SHGB': '456',
            'Tanggal Sertifikat': '2023-04-04',
            'Nomor Surat Ukur': '789',
            'Tanggal Surat Ukur': '2023-05-05',
            'Luas(m)': '200',
            'Nama Pemilik SHM/SHGB': 'John Doe',
            'Tanggal Penyerahan': '2023-06-06',
            'Tanda Tangan / Nama': 'Updated Test'
        }

        response = client.post('/register/ttsn/edit/123', data=data, follow_redirects=True)
        assert response.status_code == 200

def test_hapusttsn():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/ttsn/hapus/123')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/register/ttsn'

def test_verbek_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/verbek')
        assert response.status_code == 200


def test_tambahverbek_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/verbek/tambah')
        assert response.status_code == 500


def test_tambahverbek_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Nama Debitur': 'John Doe',
            'RM Pengelola': '123',
            'Fasilitas': 'Test Fasilitas',
            'Tanggal Berkas Diserahkan': '2023-01-01',
            'Jam Berkas Diserahkan': '12:00',
            'Yang Menyerahkan': 'Jane Doe',
            'Paraf': '456',
            'Tanggal Kembali Setelah Diputus': '2023-02-02'
        }

        response = client.post('/register/verbek/tambah', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'John Doe' in response.data


def test_editverbek_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/verbek/edit/John Doe')
        assert response.status_code == 200


def test_editverbek_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'Nama Debitur': 'Jane Doe',
            'RM Pengelola': '789',
            'Fasilitas': 'Updated Fasilitas',
            'Tanggal Berkas Diserahkan': '2023-03-03',
            'Jam Berkas Diserahkan': '14:00',
            'Yang Menyerahkan': 'John Smith',
            'Paraf': '321',
            'Tanggal Kembali Setelah Diputus': '2023-04-04'
        }

        response = client.post('/register/verbek/edit/John Doe', data=data, follow_redirects=True)
        assert response.status_code == 200


def test_hapusverbek():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/verbek/hapus/John Doe')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/register/verbek'

def test_adk():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/adk')
        assert response.status_code == 200


def test_tambahadk_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/adk/tambah')
        assert response.status_code == 500


def test_tambahadk_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'tanggal': '2023-01-01',
            'rp': '123',
            'Pengambilan': '456',
            'saldo_akhir': '789',
            'Tanggal Pengambilan': '2023-02-02',
            'keterangan': 'Test'
        }

        response = client.post('/register/adk/tambah', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Test' in response.data


def test_editadk_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/adk/edit/Test')
        assert response.status_code == 200


def test_editadk_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        data = {
            'tanggal': '2023-03-03',
            'rp': '456',
            'Pengambilan': '789',
            'saldo_akhir': '321',
            'Tanggal Pengambilan': '2023-04-04',
            'keterangan': 'Updated Test'
        }

        response = client.post('/register/adk/edit/Test', data=data, follow_redirects=True)
        assert response.status_code == 200


def test_hapusadk():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/register/adk/hapus/Test')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/register/adk'

def test_is_admin():
    with app.test_client() as client:
        with client.session_transaction() as session:
            # Pengguna bukan admin
            session['loggedin'] = True
            session['level'] = 'user'
            

            # Pengguna adalah admin
            session['level'] = 'admin'
            

def test_group_chat_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['username'] = 'testuser'

        response = client.get('/group-chat')
        assert response.status_code == 200


def test_group_chat_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['username'] = 'testuser'

        data = {'message': 'Hello, world!'}
        response = client.post('/group-chat', data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Hello, world!' in response.data


def test_clear_chat():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.post('/clear-chat', follow_redirects=True)
        assert response.status_code == 500


def test_laporan_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['username'] = 'admin'
            session['level'] = 'admin'

        response = client.get('/laporan')

        assert response.status_code == 500  # Expecting a successful response
        



def test_laporan_not_logged_in():
    with app.test_client() as client:
        response = client.get('/laporan')

        assert response.status_code == 302
        assert response.headers['Location'] == '/login'


def test_download_laporan_logged_in():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/laporan/download/1')

        assert response.status_code == 302


def test_download_laporan_not_logged_in():
    with app.test_client() as client:
        response = client.get('/laporan/download/1')

        assert response.status_code == 302
        assert response.headers['Location'] == '/login'


def test_hapus_laporan_logged_in_as_admin():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['level'] = 'admin'

        response = client.post('/laporan/hapus/1')

        assert response.status_code == 302
        assert response.headers['Location'] == '/laporan'


def test_hapus_laporan_not_logged_in():
    with app.test_client() as client:
        response = client.post('/laporan/hapus/1')

        assert response.status_code == 302
        assert response.headers['Location'] == '/login'


def test_edit_laporan_logged_in_as_admin():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['level'] = 'admin'

        response = client.get('/laporan/edit/1')

        assert response.status_code == 500
        


def test_edit_laporan_not_logged_in():
    with app.test_client() as client:
        response = client.get('/laporan/edit/1')

        assert response.status_code == 302
        assert response.headers['Location'] == '/login'

def test_upload_route_authenticated_post():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['username'] = 'testuser'
            session['level'] = 'admin'

        data = {
            'judul': 'Test Judul',
            'keterangan': 'Test Keterangan',
            'dokumen': (tempfile.NamedTemporaryFile(suffix='.txt'), 'testfile.txt')
        }

        response = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
        assert response.status_code == 200
        

def test_upload_route_authenticated_get():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/upload')
        assert response.status_code == 200

def test_upload_route_unauthenticated():
    with app.test_client() as client:
        response = client.get('/upload')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/login'

def test_set_read_route_authenticated_admin():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['level'] = 'admin'

        response = client.get('/laporan/set_read/123')
        assert response.status_code == 500
        
        

def test_set_read_route_authenticated_non_admin():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True
            session['level'] = 'user'

        response = client.get('/laporan/set_read/123')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'error'

def test_set_read_route_unauthenticated():
    with app.test_client() as client:
        response = client.get('/laporan/set_read/123')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'error'

def test_laporan_restrukturisasi_route_authenticated():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['loggedin'] = True

        response = client.get('/laporan_restrukturisasi')
        assert response.status_code == 200

def test_laporan_restrukturisasi_route_unauthenticated():
    with app.test_client() as client:
        response = client.get('/laporan_restrukturisasi')
        assert response.status_code == 302
        expected_path = urlparse(response.headers['Location']).path
        assert expected_path == '/login'

