CREATE TABLE laporan_restrukturisasi (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tanggal DATE NOT NULL,
  jumlah_debitur INT NOT NULL,
  target INT NOT NULL,
  persentase FLOAT NOT NULL
);
