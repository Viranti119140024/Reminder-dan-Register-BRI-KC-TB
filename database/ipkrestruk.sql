-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 08 Agu 2022 pada 00.47
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
-- Struktur dari tabel `ipkrestruk`
--

CREATE TABLE `ipkrestruk` (
  `noipk` varchar(30) NOT NULL,
  `namadebitur` varchar(30) NOT NULL,
  `noptk` varchar(30) NOT NULL,
  `akad` date NOT NULL,
  `jatuhtempo` date NOT NULL,
  `jangkawaktu` int(20) NOT NULL,
  `norek` varchar(30) NOT NULL,
  `keterangan` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data untuk tabel `ipkrestruk`
--

INSERT INTO `ipkrestruk` (`noipk`, `namadebitur`, `noptk`, `akad`, `jatuhtempo`, `jangkawaktu`, `norek`, `keterangan`) VALUES
('5677.679899', 'gfyuff', '56787663', '2022-08-05', '2023-09-05', 13, '567898763', 'tfcgghhj vcytyg vuuf'),
('31231', 'ferfe', '232141', '2022-08-05', '2022-09-05', 1, '23454', 'freger vrbrt fregss');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
