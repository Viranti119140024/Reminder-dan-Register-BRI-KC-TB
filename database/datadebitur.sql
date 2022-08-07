-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 08 Agu 2022 pada 00.49
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
  `dt` date NOT NULL,
  `status1` varchar(10) NOT NULL,
  `status2` varchar(10) NOT NULL,
  `status3` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data untuk tabel `datadebitur`
--

INSERT INTO `datadebitur` (`id`, `namadebitur`, `norek`, `jeniskredit`, `bakidebet`, `rm`, `jangkawaktu`, `jadwalpokok`, `sbaw1`, `sbak1`, `sbp1`, `sbaw2`, `sbak2`, `sbp2`, `sbaw3`, `sbak3`, `sbp3`, `jadwaltempo`, `akad`, `bap`, `ksb1`, `ksb2`, `ksb3`, `dt`, `status1`, `status2`, `status3`) VALUES
(1, 'tfghb', 98767, '', 0, '', 36, 0, 1, 12, 1, 13, 24, 2, 25, 36, 3, '2025-08-08', '2022-08-08', '', '2022-07-28', '2023-07-28', '2024-07-28', '2022-08-08', 'B', 'B', 'B');

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
