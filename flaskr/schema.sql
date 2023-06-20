-- Host: 127.0.0.1    Database: rebuild_notion
-- ------------------------------------------------------
-- Server version	8.0.29

CREATE SCHEMA IF NOT EXISTS `rebuild_notion`;
USE `rebuild_notion`;

-- Drops
DROP TABLE IF EXISTS `article`;
DROP TABLE IF EXISTS `book`;
DROP TABLE IF EXISTS `settings`;

-- Article
CREATE TABLE `article` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) DEFAULT NULL,
  `text` longtext DEFAULT NULL,
  `created_at` date,
  
  PRIMARY KEY (`id`)
);


-- Book
CREATE TABLE `book` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) DEFAULT NULL,
  `description` longtext DEFAULT NULL,
  `img` longtext DEFAULT NULL,
  `link` longtext DEFAULT NULL,
  `created_at` date,
  
  PRIMARY KEY (`id`)
);


-- Settings
CREATE TABLE `settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(150) DEFAULT "تَربيَة الأُمةِ مِنْ جَديدٍ",
  `cover_text` varchar(200) DEFAULT "{فَاعْلَمْ أَنَّهُ لَا إِلَٰهَ إِلَّا اللَّهُ}",
  `admin_username` varchar(50) DEFAULT "Admin",
  `admin_password` text DEFAULT "12345",
  PRIMARY KEY (`id`)
);

insert into `settings`(`title`,`cover_text`,`admin_username`,`admin_password`) values ("تَربيَة الأُمةِ مِنْ جَديدٍ","{فَاعْلَمْ أَنَّهُ لَا إِلَٰهَ إِلَّا اللَّهُ}","Admin","12345");
