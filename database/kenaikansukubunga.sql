-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 04 Agu 2022 pada 00.51
-- Versi server: 10.4.24-MariaDB
-- Versi PHP: 8.1.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `bri-minder`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `kenaikansukubunga`
--

CREATE TABLE `kenaikansukubunga` (
  `namadebitur` varchar(50) NOT NULL,
  `norek` int(30) NOT NULL,
  `jeniskredit` varchar(50) NOT NULL,
  `jangkawaktu` int(30) NOT NULL,
  `sbaw` int(11) NOT NULL,
  `sbak` int(11) NOT NULL,
  `sukubunga` int(11) NOT NULL,
  `jadwaljatuhtempo` date NOT NULL,
  `akad` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data untuk tabel `kenaikansukubunga`
--

INSERT INTO `kenaikansukubunga` (`namadebitur`, `norek`, `jeniskredit`, `jangkawaktu`, `sbaw`, `sbak`, `sukubunga`, `jadwaljatuhtempo`, `akad`) VALUES
('hj', 0, 'briguna', 24, 0, 0, 13, '2024-08-02', '2022-08-02'),
('gfe', 2342, '', 14, 0, 0, 23, '2023-10-02', '2022-08-02'),
('SEZAF', 6456, '', 14, 0, 0, 14, '2023-10-04', '2022-08-04'),
('tbbn', 21345, '', 6, 0, 0, 22, '2023-02-02', '2022-08-02'),
('werthgfd', 23145, '', 10, 0, 0, 23, '2023-06-02', '2022-08-02'),
('hjwe', 123455, 'briguna', 24, 0, 0, 15, '2024-08-02', '2022-08-02'),
('sfeg', 634656, 'briguna', 12, 0, 0, 1, '2023-08-02', '2022-08-02'),
('ertgfds', 1234567543, '', 14, 0, 1, 22, '2023-09-03', '2022-07-03');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `kenaikansukubunga`
--
ALTER TABLE `kenaikansukubunga`
  ADD PRIMARY KEY (`norek`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
