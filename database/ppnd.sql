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

CREATE TABLE `ppnd2` (

  id INT AUTO_INCREMENT PRIMARY KEY,
  NoPPNTanggalPPND VARCHAR(255),
  NamaDebitur VARCHAR(255),
  AlamatNoTelpHP VARCHAR(255),
  JenisFasilitasKredit VARCHAR(255),
  JenisDokKreditDitunda VARCHAR(255),
  LamanyaDitunda VARCHAR(255),
  TanggalBatasAkhir DATE,
  PejabatPemrakarsa VARCHAR(255),
  PejabatPemutus VARCHAR(255),
  Keterangan TEXT

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data untuk tabel `ipkrestruk`
--



/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
