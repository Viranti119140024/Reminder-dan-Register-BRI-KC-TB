-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 27 Jul 2022 pada 11.16
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
  `bap` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data untuk tabel `datadebitur`
--

INSERT INTO `datadebitur` (`namadebitur`, `norek`, `jeniskredit`, `bakidebet`, `rm`, `jangkawaktu`, `jadwalpokok`, `sbaw1`, `sbak1`, `sbp1`, `sbaw2`, `sbak2`, `sbp2`, `sbaw3`, `sbak3`, `sbp3`, `jadwaltempo`, `akad`, `bap`) VALUES
('', 0, '', 0, '', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '0000-00-00', '0000-00-00', ''),
('nesa', 0, '', 0, '', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '0000-00-00', '0000-00-00', ''),
('', 789, '', 0, '', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '0000-00-00', '0000-00-00', '');

-- --------------------------------------------------------

--
-- Struktur dari tabel `user`
--

CREATE TABLE `user` (
  `username` varchar(50) NOT NULL,
  `nama` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data untuk tabel `user`
--

INSERT INTO `user` (`username`, `nama`, `password`) VALUES
('user', 'user', 'user'),
('admin', 'admin', 'admin'),
('ezio', 'ezio', 'ezio');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
