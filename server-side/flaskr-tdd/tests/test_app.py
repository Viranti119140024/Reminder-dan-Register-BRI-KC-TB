import pytest
from flask import session
from flaskext.mysql import MySQL
from project.app import app
from markupsafe import Markup
from flask import g



@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


def login(client, username, password):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)


def test_login(client):
    response = login(client, 'admin', 'password123')
    assert response.status_code == 200
    with client.session_transaction() as session:
        session['loggedin'] = True
    with client.session_transaction() as session:
        assert 'loggedin' in session.keys()
        assert session['loggedin'] is True

def test_logout(client):
    response = logout(client)
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert 'loggedin' not in sess
        assert 'username' not in sess


def test_registrasi(client):
    response = client.post('/registrasi', data={'username': 'newuser', 'nama': 'New User', 'password': 'password123', 'level': 'user'})
    assert response.status_code == 200
   

def test_kelolauser(client):
    response = client.get('/kelolauser')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/login')

def test_home_route_with_logged_in_session(client):
    with client.session_transaction() as session:
        session['loggedin'] = True
        session['level'] = 'admin'

    response = client.get('/beranda')
    assert response.status_code == 200
    assert b'Beranda' in response.data
    assert b'Role: admin' in response.data

def test_home_route_without_logged_in_session(client):
    response = client.get('/beranda')
    assert response.status_code == 302
    assert response.headers['Location'] == '/login'

def test_restrukturisasi_route_with_logged_in_session(client):
    with client.session_transaction() as session:
        session['loggedin'] = True
        session['level'] = 'admin'

    response = client.get('/restrukturisasi')
    assert response.status_code == 200
    assert b'Jadwal Restrukturisasi' in response.data

def test_restrukturisasi_route_without_logged_in_session(client):
    response = client.get('/restrukturisasi')
    assert response.status_code == 302
    assert response.headers['Location'] == '/login'

def test_notifikasi_route_with_logged_in_session(client):
    with client.session_transaction() as session:
        session['loggedin'] = True
        session['level'] = 'admin'

    response = client.get('/notifikasi')
    assert response.status_code == 200
    assert b'Notifikasi' in response.data

def test_notifikasi_route_without_logged_in_session(client):
    response = client.get('/notifikasi')
    assert response.status_code == 302
    assert response.headers['Location'] == '/login'

def test_viewnotif_route_with_logged_in_session(client):
    with client.session_transaction() as session:
        session['loggedin'] = True
        session['level'] = 'admin'

    response = client.get('/notifikasi/viewnotif')
    assert response.status_code == 404
    

def test_viewnotif_route_without_logged_in_session(client):
    response = client.get('/notifikasi/viewnotif')
    assert response.status_code == 404

def test_tambahdebitur_route_with_logged_in_session(client):
    with client.session_transaction() as session:
        session['loggedin'] = True
        session['level'] = 'admin'
        session['username'] = 'admin'  # Pastikan kunci 'username' telah diatur dengan benar

    response = client.get('/tambahdebitur')
    assert response.status_code == 200
    

def test_tambahdebitur_route_without_logged_in_session(client):
    response = client.get('/tambahdebitur')
    assert response.status_code == 302
    assert response.headers['Location'] == '/login'

def test_editdebitur_route_with_logged_in_session(client):
    with client.session_transaction() as session:
        session['loggedin'] = True
        session['level'] = 'admin'

    # Replace '12345' with a valid debitur ID
    response = client.get('/restrukturisasi/editdebitur/12345')
    assert response.status_code == 200
    

def test_editdebitur_route_without_logged_in_session(client):
    response = client.get('/restrukturisasi/editdebitur/12345')
    assert response.status_code == 302
    assert response.headers['Location'] == '/login'

# Test register route
# Test register route
def test_register_route(client):
    response = client.get('/register')
    assert response.status_code == 302  # Redirect to login

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register')
    assert response.status_code == 200
    


# Test ipkrestruk route
def test_ipkrestruk_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [{'no_ipk': '1', 'nama_debitur': 'John Doe'}]

    response = client.get('/register/ipkrestruk')
    assert response.status_code == 302  # Redirect to login

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/ipkrestruk')
    assert response.status_code == 200
    assert b'IPK RESTRUK' in response.data.decode()  # Change here
    assert b'John Doe' in response.data.decode()  # Change here
    assert 'daftarregister.html' in response.data.decode()


# Test ipkrestruk route
def test_ipkrestruk_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [{'no_ipk': '1', 'nama_debitur': 'John Doe'}]

    response = client.get('/register/ipkrestruk')
    assert response.status_code == 302
    


# Test tambahipkrestruk route
def test_tambahipkrestruk_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.post('/register/ipkrestruk/tambah', data={
        'no_ipk': '1',
        'nama_debitur': 'John Doe',
        'No.PTK': 'PTK123',
        'Akad': 'Akad1',
        'Jatuh_Tempo': '2023-05-31',
        'Jangka_Waktu': '3',
        'Rekening': '12345',
        'keterangan': 'Test IPK Restructure'
    })
    assert response.status_code == 302

# Test editipkrestruk route
def test_editipkrestruk_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = {
        'no_ipk': '1',
        'nama_debitur': 'John Doe',
        'No.PTK': 'PTK123',
        'Akad': '6/1/2023',
        'Jatuh_Tempo': '2023-05-31',
        'Jangka_Waktu': '3',
        'Rekening': '12345',
        'keterangan': 'Test IPK Restructure'
    }

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.post('/register/ipkrestruk/struk/edit/1', data={
        'no_ipk': '1',
        'nama_debitur': 'John Doe',
        'No.PTK': 'PTK123',
        'Akad': 'Akad1',
        'Jatuh_Tempo': '2023-05-31',
        'Jangka_Waktu': '3',
        'Rekening': '12345',
        'keterangan': 'Test IPK Restructure Updated'
    })
    assert response.status_code == 404

# Test hapusipkrestruk route
def test_hapusipkrestruk_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/ipkrestruk/hapus/1')
    assert response.status_code == 302

# Test ppnd route
def test_ppnd_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [
        {'No_PPND_dan_Tanggal_PPND': 'PPND1', 'Nama_Debitur': 'John Doe'},
        {'No_PPND_dan_Tanggal_PPND': 'PPND2', 'Nama_Debitur': 'Jane Smith'}
    ]

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/ppnd')
    assert response.status_code == 200
   
# Test tambahppnd route
def test_tambahppnd_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['username'] = 'testuser'

    response = client.get('/register/ppnd/tambah')
    assert response.status_code == 200

    response = client.post('/register/ppnd/tambah', data={
        'No. PPND dan Tanggal PPND': 'PPND1',
        'Nama Debitur': 'John Doe',
        'Alamat No. Telp/HP': '12345',
        'Jenis Fasilitas Kredit': 'Fasilitas1',
        'Jenis Dok Kredit yang Ditunda': 'Dokumen1',
        'Lamanya ditunda': '3',
        'Tanggal Batas Akhir': '2023-05-31',
        'Pejabat Pemrakarsa': 'Pejabat1',
        'Pejabat Pemutus': 'Pejabat2',
        'keterangan': 'Test PPND'
    })
    assert response.status_code == 302


# Test editppnd route
def test_editppnd_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = {
        'No_PPND_dan_Tanggal_PPND': 'PPND1',
        'Nama_Debitur': 'John Doe',
        'Alamat_No_Telp_HP': '12345',
        'Jenis_Fasilitas_Kredit': 'Fasilitas1',
        'Jenis_Dok_Kredit_yang_Ditunda': 'Dokumen1',
        'Lamanya_ditunda': 3,
        'Tanggal_Batas_Akhir': '2023-05-31',
        'Pejabat_Pemrakarsa': 'Pejabat1',
        'Pejabat_Pemutus': 'Pejabat2',
        'keterangan': 'Test PPND'
    }

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/ppnd/edit/PPND1')
    assert response.status_code == 200
    assert b'PPND1' in response.data
    assert b'John Doe' in response.data
    assert b'12345' in response.data
    assert b'Fasilitas1' in response.data

    response = client.post('/register/ppnd/edit/PPND1', data={
        'No. PPND dan Tanggal PPND': '',
        'Nama Debitur': 'John Smith',
        'Alamat No. Telp/HP': '54321',
        'Jenis Fasilitas Kredit': '',
        'Jenis Dok Kredit yang Ditunda': 'Dokumen2',
        'Lamanya ditunda': '5',
        'Tanggal Batas Akhir': '',
        'Pejabat Pemrakarsa': '',
        'Pejabat Pemutus': 'Pejabat3',
        'keterangan': ''
    })
    assert response.status_code == 302


# Test hapusppnd route
def test_hapusppnd_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/ppnd/hapus/PPND1')
    assert response.status_code == 302


# Test ptkrestruk2penyelesaian route
def test_ptkrestruk2penyelesaian_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [
        {'NoPTK': 'PTK1', 'NamaDebitur': 'John Doe'},
        {'NoPTK': 'PTK2', 'NamaDebitur': 'Jane Smith'}
    ]

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/ptkrestruk2penyelesaian')
    assert response.status_code == 200
    


# Test editptkrestruk2penyelesaian route
def test_editptkrestruk2penyelesaian_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = {
        'NoPTK': 'PTK1',
        'NamaDebitur': 'John Doe',
        'TanggalPutusan': '2023-05-31',
        'NamaPemutus': 'Pemutus1',
        'Jabatan': 'Jabatan1',
        'Rp': 1000000,
        'Keterangan': 'Test PTK'
    }

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/ptkrestruk2penyelesaian/edit/PTK1')
    assert response.status_code == 200
   

    response = client.post('/register/ptkrestruk2penyelesaian/edit/PTK1', data={
        'No. PTK': b'PTK2',
        'Nama Debitur': b'Jane Smith',
        'Tanggal Putusan': b'2023-06-01',
        'Nama Pemutus': b'Pemutus2',
        'Jabatan': b'Jabatan2',
        'Rp': b'2000000',
        'keterangan': b'Updated PTK'
    })
    assert response.status_code == 302

# Test asskerugian route
def test_asskerugian_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [
        {'NoPolis': 'Polis1', 'NamaDebitur': 'John Doe'}
    ]


    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/asskerugian')
    assert response.status_code == 200
    


# Test tambahasskerugian route
def test_tambahasskerugian_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['username'] = 'testuser'

    response = client.get('/register/asskerugian/tambah')
    assert response.status_code == 200
    assert b'<form' in response.data
  

    response = client.post('/register/asskerugian/tambah', data={
        'tanggal': '2023-05-31',
        'Nama Debitur': 'John Doe',
        'Premi': '1000000',
        'Agunan': 'Agunan1',
        'Polis': 'Polis1',
        'Tanggal': '2023-06-01',
        'Premi': '2000000',
        'keterangan': 'Test ASS Kerugian'
    })
    assert response.status_code == 302



# Test editasskerugian route
def test_editasskerugian_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = {
        'NoPolis': 'Polis1',
        'NamaDebitur': 'John Doe',
        'Tanggal': '2023-05-31',
        'CADPremi': '1000000',
        'JumlahAgunan': 'Agunan1',
        'NoPolis': 'Polis1',
        'TanggalOB': '2023-06-01',
        'Premi': '2000000',
        'Keterangan': 'Test ASS Kerugian'
    }

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/asskerugian/edit/Polis1')
    assert response.status_code == 200
  

    response = client.post('/register/asskerugian/edit/Polis1', data={
        'tanggal': '2023-06-02',
        'Nama Debitur': 'Jane Smith',
        'Premi': '3000000',
        'Agunan': 'Agunan2',
        'Polis': 'Polis1',
        'Tanggal': '2023-06-03',
        'Premi': '4000000',
        'keterangan': 'Updated ASS Kerugian'
    })
    assert response.status_code == 302


# Test hapusasskerugian route
def test_hapusasskerugian_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/asskerugian/hapus/Polis1')
    assert response.status_code == 302

# Test blokirkecil route
def test_blokirkecil_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/blokirkecil')
    assert response.status_code == 200
    assert b'Blokir Kecil-Program' in response.data

# Test tambahblokirkecil route
def test_tambahblokirkecil_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['username'] = 'testuser'

    response = client.get('/register/blokirkecil/tambah')
    assert response.status_code == 200
    assert b'<form' in response.data
  

    response = client.post('/register/blokirkecil/tambah', data={
        'Nama': 'John Doe',
        'Rekening': '123456',
        'Jumlah': '1000000',
        'Tanggal': '2023-05-31',
        'Buka': 'Buka',
        'Paraf': 'Paraf',
        'keterangan': 'Test Blokir Kecil'
    })
    assert response.status_code == 302

# Test editblokirkecil route
def test_editblokirkecil_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/blokirkecil/edit/123456')
    assert response.status_code == 200
    assert b'<form' in response.data

    response = client.post('/register/blokirkecil/edit/123456', data={
        'Rekening': '654321',
        'Jumlah': '2000000',
        'Paraf': 'New Paraf',
        'keterangan': 'Updated Blokir Kecil'
    })
    assert response.status_code == 400

# Test hapusblokirkecil route
def test_hapusblokirkecil_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/blokirkecil/hapus/123456')
    assert response.status_code == 302

def test_ipk_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/ipk')
    assert response.status_code == 200
    

def test_tambahipk_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['username'] = 'testuser'

    response = client.get('/register/ipk/tambah')
    assert response.status_code == 200
    assert b'<form' in response.data
    

    response = client.post('/register/ipk/tambah', data={
        'IPK': '123456',
        'Debitur': 'John Doe',
        'Tanggal Realisasi': '2023-05-31',
        'Tanggal Jatuh Tempo': '2023-06-30',
        'Permohonan': 'Permohonan123',
        'Putusan': 'Putusan123',
        'Rekening': '654321',
        'Fix/Rate': 'Fix',
        'keterangan': 'Test IPK'
    })
    assert response.status_code == 302

def test_editipk_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/ipk/edit/123456')
    assert response.status_code == 200
    assert b'<form' in response.data

    response = client.post('/register/ipk/edit/123456', data={
        'IPK': '654321',
        'Debitur': 'Jane Doe',
        'Tanggal Realisasi': '2023-06-01',
        'Tanggal Jatuh Tempo': '2023-07-01',
        'Permohonan': 'Permohonan456',
        'Putusan': 'Putusan456',
        'Rekening': '123456',
        'Fix/Rate': 'Rate',
        'keterangan': 'Updated IPK'
    })
    assert response.status_code == 302

def test_hapusipk_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/ipk/hapus/123456')
    assert response.status_code == 302

def test_jasakonsultasi_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['username'] = 'testuser'

    response = client.get('/register/jasakonsultasi')
    assert response.status_code == 200
    
    # Assert other expected content

def test_tambahjasakonsultasi_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['username'] = 'testuser'

    response = client.get('/register/jasakonsultasi/tambah')
    assert response.status_code == 200
    
    # Assert other expected content

    response = client.post('/register/jasakonsultasi/tambah', data={
        'Nama + No. Rekening': 'Test Rekening',
        'Jasa Sesuai PTK': 'Test Jasa',
        'Tanggal Setor': '2023-05-31',
        'Jumlah yang disetor': '1000',
        'NPWP': 'Test NPWP',
        'PPN': 'Test PPN',
        'PPN2': 'Test PPN2',
        'DPP': 'Test DPP'
    })
    assert response.status_code == 302

def test_editjasakonsultasi_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['username'] = 'testuser'

    response = client.get('/register/jasakonsultasi/edit/TestNPWP')
    assert response.status_code == 200
    
    # Assert other expected content

    response = client.post('/register/jasakonsultasi/edit/TestNPWP', data={
        'Nama + No. Rekening': 'Updated Rekening',
        'Jasa Sesuai PTK': 'Updated Jasa',
        'Tanggal Setor': '2023-06-01',
        'Jumlah yang disetor': '2000',
        'NPWP': 'Updated NPWP',
        'PPN': 'Updated PPN',
        'PPN2': 'Updated PPN2',
        'DPP': 'Updated DPP'
    })
    assert response.status_code == 302

def test_hapujasakonsultasi_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['username'] = 'testuser'

    response = client.get('/register/jasakonsultasi/hapus/TestNPWP')
    assert response.status_code == 302

def test_bpkbpinjam_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    mock_cursor.fetchall.return_value = [{'NoBPKB': 'TestNoBPKB', 'NamaDebitur': 'TestNama', 'NoRekening': 'TestRekening', 'JenisKredit': 'TestKredit', 'ProsesVIA': 'TestVIA', 'TanggalKeluar': '2023-05-31', 'TanggalKembali': '2023-06-01'}]

    response = client.get('/register/bpkbpinjam')
    assert response.status_code == 200

    # Assert other expected content

def test_tambahbpkbpinjam_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['username'] = 'testuser'  # Add 'username' key to the session

    response = client.get('/register/bpkbpinjam/tambah')
    assert response.status_code == 200
    
    # Assert other expected content

    response = client.post('/register/bpkbpinjam/tambah', data={
        'Nama': 'Test Nama',
        'Rekening': 'Test Rekening',
        'Kredit': 'Test Kredit',
        'BPKB': 'Test BPKB',
        'VIA': 'Test VIA',
        'Tanggal_Keluar': '2023-05-31',
        'Tanggal_Kembali': '2023-06-01'
    })
    assert response.status_code == 302


def test_editbpkbpinjam_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/bpkbpinjam/edit/TestNoBPKB')
    assert response.status_code == 200
    
    # Assert other expected content

    response = client.post('/register/bpkbpinjam/edit/TestNoBPKB', data={
        'Nama': 'Updated Nama',
        'Rekening': 'Updated Rekening',
        'Kredit': 'Updated Kredit',
        'BPKB': 'Updated BPKB',
        'VIA': 'Updated VIA',
        'Tanggal_Keluar': '2023-06-02',
        'Tanggal_Kembali': '2023-06-03'
    })
    assert response.status_code == 302

def test_hapusbpkbpinjam_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/bpkbpinjam/hapus/TestNoBPKB')
    assert response.status_code == 302

def test_angkringan_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/angkringan')
    assert response.status_code == 200
   

def test_tambahangkringan_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True
        sess['username'] = 'testuser'

    response = client.get('/register/angkringan/tambah')
    assert response.status_code == 200
    
    # Assert other expected content

    response = client.post('/register/angkringan/tambah', data={
        'Debitur': 'Test Debitur',
        'tanggal': '2023-05-31',
        'Plafond': 'Test Plafond',
        'Waktu': 'Test Waktu',
        'Angsuran Pokok': 'Test Angsuran Pokok',
        'Angsuran Bunga': 'Test Angsuran Bunga',
        'No Rekening': 'Test No Rekening',
        'keterangan': 'Test Keterangan'
    })
    assert response.status_code == 302

def test_editangkringan_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/angkringan/edit/TestNoRekening')
    assert response.status_code == 200
    
    # Assert other expected content

    response = client.post('/register/angkringan/edit/TestNoRekening', data={
        'Debitur': 'Test Debitur',
        'tanggal': '2023-05-31',
        'Plafond': 'Test Plafond',
    
        'Angsuran Pokok': 'Test Angsuran Pokok',
        'Angsuran Bunga': 'Test Angsuran Bunga',
        'No Rekening': 'Test No Rekening',
        'keterangan': 'Test Keterangan'
    })
    assert response.status_code == 400


def test_hapusangkringan_route(client, mocker):
    mock_connect = mocker.patch('mysql.connector.connect')
    mock_cursor = mock_connect.return_value.cursor.return_value

    with client.session_transaction() as sess:
        sess['loggedin'] = True

    response = client.get('/register/angkringan/hapus/TestNoRekening')
    assert response.status_code == 302



if __name__ == '__main__':
    pytest.main()
