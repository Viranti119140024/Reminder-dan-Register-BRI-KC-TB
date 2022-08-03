-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 04 Agu 2022 pada 00.50
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
-- Struktur dari tabel `datadebitur`
--

CREATE TABLE `datadebitur` (
  `id` int(11) NOT NULL,
  `namadebitur` varchar(50) NOT NULL,
  `norek` int(30) NOT NULL,
  `jeniskredit` varchar(50) NOT NULL,
  `bakidebet` int(50) NOT NULL,
  `rm` varchar(50) NOT NULL,
  `jangkawaktu` int(30) NOT NULL,
  `jadwalpokok` int(50) NOT NULL,
  `sbaw1` int(11) NOT NULL,
  `sbak1` int(11) NOT NULL,
  `sbp1` int(11) NOT NULL,
  `sbaw2` int(11) NOT NULL,
  `sbak2` int(11) NOT NULL,
  `sbp2` int(11) NOT NULL,
  `sbaw3` int(11) NOT NULL,
  `sbak3` int(11) NOT NULL,
  `sbp3` int(11) NOT NULL,
  `jadwaltempo` date NOT NULL,
  `akad` date NOT NULL,
  `bap` text NOT NULL,
  `ksb1` date NOT NULL,
  `ksb2` date NOT NULL,
  `ksb3` date NOT NULL,
  `dt` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data untuk tabel `datadebitur`
--

INSERT INTO `datadebitur` (`id`, `namadebitur`, `norek`, `jeniskredit`, `bakidebet`, `rm`, `jangkawaktu`, `jadwalpokok`, `sbaw1`, `sbak1`, `sbp1`, `sbaw2`, `sbak2`, `sbp2`, `sbaw3`, `sbak3`, `sbp3`, `jadwaltempo`, `akad`, `bap`, `ksb1`, `ksb2`, `ksb3`, `dt`) VALUES
(1, 'ewrr', 12345, 'serdt', 231, 'were', 12, 32432, 12, 1, 12, 4, 8, 13, 9, 12, 6, '2023-07-31', '2022-07-31', 'weree', '2022-11-30', '0000-00-00', '0000-00-00', '2022-08-04'),
(2, 'hjwe', 123455, 'briguna', 1, 'aa', 24, 123, 1, 12, 12, 13, 34, 13, 0, 0, 15, '2024-08-02', '2022-08-02', 'asa', '2023-08-02', '2025-06-02', '2022-08-02', '2022-08-04'),
(3, 'sfeg', 634656, 'briguna', 1, 'aa', 12, 123, 0, 0, 1, 1, 6, 2, 7, 12, 3, '2023-08-02', '2022-08-02', 'gh', '2022-08-02', '2023-02-02', '2023-08-02', '2022-08-04'),
(4, 'tbbn', 21345, '', 0, '', 6, 0, 0, 0, 22, 1, 3, 23, 4, 6, 12, '2023-02-02', '2022-08-02', '', '2022-08-02', '2022-11-02', '2023-02-02', '2022-08-04'),
(5, 'ertgfdsnqqq', 1234567543, '', 0, '', 14, 0, 0, 0, 12, 0, 1, 22, 2, 14, 32, '2023-09-03', '2022-07-03', '', '2022-07-03', '2022-08-03', '2023-09-03', '2022-08-04'),
(6, 'SEZAF', 6456, '', 0, '', 14, 0, 1, 7, 14, 0, 0, 14, 8, 14, 14, '2023-10-04', '2022-08-04', '', '2023-02-18', '2022-07-21', '2023-09-20', '2022-08-04');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `datadebitur`
--
ALTER TABLE `datadebitur`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `datadebitur`
--
ALTER TABLE `datadebitur`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
