-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: db
-- Generation Time: Jan 09, 2024 at 03:22 PM
-- Server version: 11.2.2-MariaDB-1:11.2.2+maria~ubu2204
-- PHP Version: 8.2.13

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `QD`
--

-- --------------------------------------------------------

--
-- Table structure for table `manuscript_view`
--

CREATE TABLE `manuscript_view` (
  `manuscript` text NOT NULL DEFAULT '',
  `column` varchar(100) DEFAULT NULL,
  `line` varchar(100) DEFAULT NULL,
  `reading` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `followed_by` enum('space','break') CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT 'space',
  `sequence_in_line` tinyint(3) UNSIGNED NOT NULL,
  `default_language_id` tinyint(3) UNSIGNED DEFAULT 1,
  `language_id` tinyint(3) UNSIGNED NOT NULL DEFAULT 0,
  `manuscript_id` mediumint(8) UNSIGNED NOT NULL,
  `manuscript_column_id` mediumint(8) UNSIGNED NOT NULL,
  `manuscript_line_id` mediumint(8) UNSIGNED NOT NULL,
  `manuscript_sign_cluster_id` mediumint(8) UNSIGNED NOT NULL,
  `manuscript_sign_cluster_reading_id` int(10) UNSIGNED NOT NULL DEFAULT 0,
  `sequence_of_reading` tinyint(3) UNSIGNED DEFAULT 0,
  `position_in_reference` tinyint(3) UNSIGNED NOT NULL DEFAULT 0,
  `is_public` set('for texts','for articles') CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `system_user_id` smallint(5) UNSIGNED DEFAULT NULL,
  `unique_ordered_id` bigint(20) UNSIGNED DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `manuscript_view`
--

INSERT INTO `manuscript_view` (`manuscript`, `column`, `line`, `reading`, `followed_by`, `sequence_in_line`, `default_language_id`, `language_id`, `manuscript_id`, `manuscript_column_id`, `manuscript_line_id`, `manuscript_sign_cluster_id`, `manuscript_sign_cluster_reading_id`, `sequence_of_reading`, `position_in_reference`, `is_public`, `system_user_id`, `unique_ordered_id`) VALUES
('4Q157', 'frg. 1 i', '1', '[--]', 'break', 1, 1, 1, 92, 656, 4431, 34208, 34208, 0, 0, 'for texts,for articles', NULL, 920001001001),
('4Q157', 'frg. 1 i', '2', '[--', 'space', 1, 1, 1, 92, 656, 4432, 34209, 34209, 0, 0, 'for texts,for articles', NULL, 920001002001),
('4Q157', 'frg. 1 i', '2', 'עלו]הי', 'space', 2, 1, 1, 92, 656, 4432, 34210, 34210, 0, 0, 'for texts,for articles', NULL, 920001002002),
('4Q157', 'frg. 1 i', '2', 'עננא', 'break', 3, 1, 1, 92, 656, 4432, 34211, 34211, 0, 0, 'for texts,for articles', NULL, 920001002003),
('4Q157', 'frg. 1 i', '3', '[--', 'space', 1, 1, 1, 92, 656, 4433, 34212, 34212, 0, 0, 'for texts,for articles', NULL, 920001003001),
('4Q157', 'frg. 1 i', '3', 'ביו]מ֯י', 'space', 2, 1, 1, 92, 656, 4433, 34213, 34213, 0, 0, 'for texts,for articles', NULL, 920001003002),
('4Q157', 'frg. 1 i', '3', 'שנה', 'break', 3, 1, 1, 92, 656, 4433, 34214, 34214, 0, 0, 'for texts,for articles', NULL, 920001003003),
('4Q157', 'frg. 1 i', '4', '[--', 'space', 1, 1, 1, 92, 656, 4434, 34215, 34215, 0, 0, 'for texts,for articles', NULL, 920001004001),
('4Q157', 'frg. 1 i', '4', ']־־־', 'break', 2, 1, 1, 92, 656, 4434, 34216, 34216, 0, 0, 'for texts,for articles', NULL, 920001004002),
('4Q157', 'frg. 1 i', '5', '[--', 'space', 1, 1, 1, 92, 656, 4435, 34217, 34217, 0, 0, 'for texts,for articles', NULL, 920001005001),
('4Q157', 'frg. 1 i', '5', 'מדנ]ח', 'break', 2, 1, 1, 92, 656, 4435, 34218, 34218, 0, 0, 'for texts,for articles', NULL, 920001005002),
('4Q157', 'frg. 1 ii', '1', 'אנ֯[כיר?', 'space', 1, 1, 1, 92, 657, 4436, 34219, 34219, 0, 0, 'for texts,for articles', NULL, 920002001001),
('4Q157', 'frg. 1 ii', '1', '--]', 'break', 2, 1, 1, 92, 657, 4436, 34220, 34220, 0, 0, 'for texts,for articles', NULL, 920002001002),
('4Q157', 'frg. 1 ii', '2', 'האנש', 'space', 1, 1, 1, 92, 657, 4437, 34221, 34221, 0, 0, 'for texts,for articles', NULL, 920002002001),
('4Q157', 'frg. 1 ii', '2', 'מא[לה', 'space', 2, 1, 1, 92, 657, 4437, 34222, 34222, 0, 0, 'for texts,for articles', NULL, 920002002002),
('4Q157', 'frg. 1 ii', '2', '--]', 'break', 3, 1, 1, 92, 657, 4437, 34223, 34223, 0, 0, 'for texts,for articles', NULL, 920002002003),
('4Q157', 'frg. 1 ii', '3', 'ובמלאכו֯[הי', 'space', 1, 1, 1, 92, 657, 4438, 34224, 34224, 0, 0, 'for texts,for articles', NULL, 920002003001),
('4Q157', 'frg. 1 ii', '3', '--]', 'break', 2, 1, 1, 92, 657, 4438, 34225, 34225, 0, 0, 'for texts,for articles', NULL, 920002003002),
('4Q157', 'frg. 1 ii', '4', 'ד֯בעפרא', 'space', 1, 1, 1, 92, 657, 4439, 34226, 34226, 0, 0, 'for texts,for articles', NULL, 920002004001),
('4Q157', 'frg. 1 ii', '4', '[--]', 'break', 2, 1, 1, 92, 657, 4439, 34227, 34227, 0, 0, 'for texts,for articles', NULL, 920002004002),
('4Q157', 'frg. 1 ii', '5', 'ומן', 'space', 1, 1, 1, 92, 657, 4440, 34228, 34228, 0, 0, 'for texts,for articles', NULL, 920002005001),
('4Q157', 'frg. 1 ii', '5', 'בלי', 'space', 2, 1, 1, 92, 657, 4440, 34229, 34229, 0, 0, 'for texts,for articles', NULL, 920002005002),
('4Q157', 'frg. 1 ii', '5', 'מני[ח', 'space', 3, 1, 1, 92, 657, 4440, 34230, 34230, 0, 0, 'for texts,for articles', NULL, 920002005003),
('4Q157', 'frg. 1 ii', '5', '--]', 'break', 4, 1, 1, 92, 657, 4440, 34231, 34231, 0, 0, 'for texts,for articles', NULL, 920002005004),
('4Q157', 'frg. 1 ii', '6', 'ימותון', 'space', 1, 1, 1, 92, 657, 4441, 34232, 34232, 0, 0, 'for texts,for articles', NULL, 920002006001),
('4Q157', 'frg. 1 ii', '6', 'ולא', 'space', 2, 1, 1, 92, 657, 4441, 34233, 34233, 0, 0, 'for texts,for articles', NULL, 920002006002),
('4Q157', 'frg. 1 ii', '6', 'ב֯[חכ]מ֯[ה', 'space', 3, 1, 1, 92, 657, 4441, 34234, 34234, 0, 0, 'for texts,for articles', NULL, 920002006003),
('4Q157', 'frg. 1 ii', '6', '--]', 'break', 4, 1, 1, 92, 657, 4441, 34235, 34235, 0, 0, 'for texts,for articles', NULL, 920002006004),
('4Q157', 'frg. 1 ii', '7', 'ת֯בקה', 'space', 1, 1, 1, 92, 657, 4442, 34236, 34236, 0, 0, 'for texts,for articles', NULL, 920002007001),
('4Q157', 'frg. 1 ii', '7', '_____', 'space', 2, 1, 1, 92, 657, 4442, 34237, 34237, 0, 0, 'for texts,for articles', NULL, 920002007002),
('4Q157', 'frg. 1 ii', '7', 'הלא', 'space', 3, 1, 1, 92, 657, 4442, 34238, 34238, 0, 0, 'for texts,for articles', NULL, 920002007003),
('4Q157', 'frg. 1 ii', '7', 'סכל', 'space', 4, 1, 1, 92, 657, 4442, 34239, 34239, 0, 0, 'for texts,for articles', NULL, 920002007004),
('4Q157', 'frg. 1 ii', '7', 'יק֯[טל', 'space', 5, 1, 1, 92, 657, 4442, 34240, 34240, 0, 0, 'for texts,for articles', NULL, 920002007005),
('4Q157', 'frg. 1 ii', '7', '--]', 'break', 6, 1, 1, 92, 657, 4442, 34241, 34241, 0, 0, 'for texts,for articles', NULL, 920002007006),
('4Q157', 'frg. 1 ii', '8', 'ואנה', 'space', 1, 1, 1, 92, 657, 4443, 34242, 34242, 0, 0, 'for texts,for articles', NULL, 920002008001),
('4Q157', 'frg. 1 ii', '8', 'חזי֯ת', 'space', 2, 1, 1, 92, 657, 4443, 34243, 34243, 0, 0, 'for texts,for articles', NULL, 920002008002),
('4Q157', 'frg. 1 ii', '8', 'ד֯ר֯ש֯ע', 'space', 3, 1, 1, 92, 657, 4443, 34244, 34244, 0, 0, 'for texts,for articles', NULL, 920002008003),
('4Q157', 'frg. 1 ii', '8', 'מ֯[ו]עה', 'space', 4, 1, 1, 92, 657, 4443, 34245, 34245, 0, 0, 'for texts,for articles', NULL, 920002008004),
('4Q157', 'frg. 1 ii', '8', 'ולטת', 'space', 5, 1, 1, 92, 657, 4443, 34246, 34246, 0, 0, 'for texts,for articles', NULL, 920002008005),
('4Q157', 'frg. 1 ii', '8', 'ל־[', 'space', 6, 1, 1, 92, 657, 4443, 34247, 34247, 0, 0, 'for texts,for articles', NULL, 920002008006),
('4Q157', 'frg. 1 ii', '8', '--]', 'break', 7, 1, 1, 92, 657, 4443, 34248, 34248, 0, 0, 'for texts,for articles', NULL, 920002008007),
('4Q157', 'frg. 1 ii', '9', '[מפ]ר֯ק[ן?]', 'space', 1, 1, 1, 92, 657, 4444, 34249, 34249, 0, 0, 'for texts,for articles', NULL, 920002009001),
('4Q157', 'frg. 1 ii', '9', 'והת־־[', 'space', 2, 1, 1, 92, 657, 4444, 34250, 34250, 0, 0, 'for texts,for articles', NULL, 920002009002),
('4Q157', 'frg. 1 ii', '9', ']־־־[', 'space', 3, 1, 1, 92, 657, 4444, 34251, 34251, 0, 0, 'for texts,for articles', NULL, 920002009003),
('4Q157', 'frg. 1 ii', '9', '--]', 'break', 4, 1, 1, 92, 657, 4444, 34252, 34252, 0, 0, 'for texts,for articles', NULL, 920002009004),
('4Q157', 'frg. 1 ii', '10', '[--', 'space', 1, 1, 1, 92, 657, 4445, 34253, 34253, 0, 0, 'for texts,for articles', NULL, 920002010001),
('4Q157', 'frg. 1 ii', '10', ']ל֯[', 'space', 2, 1, 1, 92, 657, 4445, 34254, 34254, 0, 0, 'for texts,for articles', NULL, 920002010002),
('4Q157', 'frg. 1 ii', '10', '--]', 'break', 3, 1, 1, 92, 657, 4445, 34255, 34255, 0, 0, 'for texts,for articles', NULL, 920002010003);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
