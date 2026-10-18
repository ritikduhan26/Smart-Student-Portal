-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: student_portal
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `announcements`
--

DROP TABLE IF EXISTS `announcements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `announcements` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(150) NOT NULL,
  `message` text NOT NULL,
  `audience` varchar(100) DEFAULT NULL,
  `announcement_date` date NOT NULL,
  `status` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `announcements`
--

LOCK TABLES `announcements` WRITE;
/*!40000 ALTER TABLE `announcements` DISABLE KEYS */;
INSERT INTO `announcements` VALUES (1,'Welcome to the Student Portal','Welcome to the new academic year. Please check the portal regularly for updates.','All Students','2026-09-01','Active'),(2,'Assignment Reminder','Please check your upcoming assignment deadlines.','All Students','2026-09-10','Active'),(3,'Timetable Update','Please check your timetable for the latest class information.','All Students','2026-09-12','Active'),(7,'Library Opening Hours Update','The university library will be open until 10 pm on weekdays during the assessment period.','All Students','2026-10-09','Active');
/*!40000 ALTER TABLE `announcements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assignments`
--

DROP TABLE IF EXISTS `assignments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assignments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `module_id` int NOT NULL,
  `title` varchar(150) NOT NULL,
  `description` text,
  `deadline` date NOT NULL,
  `status` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `module_id` (`module_id`),
  CONSTRAINT `assignments_ibfk_1` FOREIGN KEY (`module_id`) REFERENCES `modules` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assignments`
--

LOCK TABLES `assignments` WRITE;
/*!40000 ALTER TABLE `assignments` DISABLE KEYS */;
INSERT INTO `assignments` VALUES (1,1,'Student Portal Website','Develop a responsive web application.','2026-10-10','In Progress'),(2,2,'Software Development Project','Develop and test a software application.','2026-10-18','In Progress'),(3,3,'Data Analysis Report','Analyse a dataset and present the findings.','2026-10-25','Not Started'),(4,4,'Artificial Intelligence Report','Research and evaluate an artificial intelligence application.','2026-11-02','Not Started'),(5,5,'Database Design','Design and implement a relational database.','2026-11-10','Not Started'),(6,6,'Penetration Testing Report','Perform security testing and document the results.','2026-11-18','Not Started'),(7,6,'Testing','Security Testing','2026-10-18','Not Started'),(8,1,'Design a Website','Design a web portal using HTML and CSS','2026-10-22','Not Started');
/*!40000 ALTER TABLE `assignments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `module_id` int NOT NULL,
  `attendance_date` date NOT NULL,
  `status` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `student_id` (`student_id`),
  KEY `module_id` (`module_id`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `attendance_ibfk_2` FOREIGN KEY (`module_id`) REFERENCES `modules` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance`
--

LOCK TABLES `attendance` WRITE;
/*!40000 ALTER TABLE `attendance` DISABLE KEYS */;
INSERT INTO `attendance` VALUES (1,1,1,'2026-09-01','Present'),(2,1,2,'2026-09-02','Present'),(3,1,3,'2026-09-03','Present'),(4,1,4,'2026-09-04','Absent'),(5,1,5,'2026-09-05','Present'),(6,1,6,'2026-09-06','Present'),(7,2,1,'2026-09-01','Present'),(8,2,2,'2026-09-02','Absent'),(9,2,3,'2026-09-03','Present'),(10,3,1,'2026-09-01','Present'),(11,3,2,'2026-09-02','Present'),(12,3,3,'2026-09-03','Present'),(13,1,4,'2026-09-30','Present'),(14,1,3,'2026-10-01','Present'),(15,1,5,'2026-09-29','Present');
/*!40000 ALTER TABLE `attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enrolments`
--

DROP TABLE IF EXISTS `enrolments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enrolments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `module_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_id` (`student_id`,`module_id`),
  KEY `module_id` (`module_id`),
  CONSTRAINT `enrolments_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `enrolments_ibfk_2` FOREIGN KEY (`module_id`) REFERENCES `modules` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enrolments`
--

LOCK TABLES `enrolments` WRITE;
/*!40000 ALTER TABLE `enrolments` DISABLE KEYS */;
INSERT INTO `enrolments` VALUES (1,1,1),(2,1,2),(3,1,3),(4,2,2),(5,2,4),(6,2,5),(7,3,1),(8,3,5),(9,3,6),(10,4,3),(11,4,4),(12,4,6);
/*!40000 ALTER TABLE `enrolments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grades`
--

DROP TABLE IF EXISTS `grades`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `grades` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `module_id` int NOT NULL,
  `assessment_name` varchar(150) NOT NULL,
  `grade` decimal(5,2) DEFAULT NULL,
  `result` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `student_id` (`student_id`),
  KEY `module_id` (`module_id`),
  CONSTRAINT `grades_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`),
  CONSTRAINT `grades_ibfk_2` FOREIGN KEY (`module_id`) REFERENCES `modules` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grades`
--

LOCK TABLES `grades` WRITE;
/*!40000 ALTER TABLE `grades` DISABLE KEYS */;
INSERT INTO `grades` VALUES (1,1,1,'Web Development Assessment',82.00,'Pass'),(2,1,2,'Software Development Assessment',78.00,'Pass'),(3,1,3,'Data and Decision Making Assessment',85.00,'Pass'),(4,1,4,'Artificial Intelligence Assessment',80.00,'Pass'),(5,1,5,'Data Management Assessment',88.00,'Pass'),(6,1,6,'Network Security Assessment',76.00,'Pass'),(7,2,1,'Web Development Assessment',72.00,'Pass'),(8,2,2,'Software Development Assessment',68.00,'Pass'),(9,2,3,'Data and Decision Making Assessment',75.00,'Pass'),(10,3,1,'Web Development Assessment',65.00,'Pass'),(11,3,2,'Software Development Assessment',70.00,'Pass'),(12,3,3,'Data and Decision Making Assessment',67.00,'Pass'),(13,1,1,'Web Application',88.00,'Pass');
/*!40000 ALTER TABLE `grades` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `modules`
--

DROP TABLE IF EXISTS `modules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `modules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `module_name` varchar(100) NOT NULL,
  `module_code` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `module_code` (`module_code`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `modules`
--

LOCK TABLES `modules` WRITE;
/*!40000 ALTER TABLE `modules` DISABLE KEYS */;
INSERT INTO `modules` VALUES (1,'Web Development','WD001'),(2,'Software Development','SD002'),(3,'Data and Decision Making','DDM003'),(4,'Application of Artificial Intelligence','AI004'),(5,'Data Management','DM005'),(6,'Network and Penetration Testing','NPT006');
/*!40000 ALTER TABLE `modules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `student_number` varchar(20) NOT NULL,
  `course` varchar(100) NOT NULL,
  `academic_year` varchar(20) DEFAULT NULL,
  `study_mode` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_number` (`student_number`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `students_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES (1,1,'STU001','MSc Computer Science','2025/26','Full-time'),(2,2,'STU002','MSc Computer Science','2025/26','Full-time'),(3,3,'STU003','MSc Computer Science','2025/26','Full-time'),(4,5,'STU004','MSc Computer Science','2025/26','Full-time'),(5,6,'STU005','MSc Computer Science','2025/26','Full-time'),(6,7,'STU006','MSc Computer Science','2025/26','Full-time'),(7,8,'STU007','MSc Computer Science','2025/26','Full-time'),(8,9,'STU008','MSc Computer Science','2025/26','Full-time'),(9,10,'STU009','MSc Computer Science','2025/26','Full-time');
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `timetable`
--

DROP TABLE IF EXISTS `timetable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `timetable` (
  `id` int NOT NULL AUTO_INCREMENT,
  `module_id` int NOT NULL,
  `day_name` varchar(20) NOT NULL,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `room` varchar(50) DEFAULT NULL,
  `lecturer` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `module_id` (`module_id`),
  CONSTRAINT `timetable_ibfk_1` FOREIGN KEY (`module_id`) REFERENCES `modules` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `timetable`
--

LOCK TABLES `timetable` WRITE;
/*!40000 ALTER TABLE `timetable` DISABLE KEYS */;
INSERT INTO `timetable` VALUES (1,1,'Monday','09:00:00','11:00:00','Room 101','Dr Smith'),(2,2,'Monday','13:00:00','15:00:00','Room 102','Dr Jones'),(3,3,'Tuesday','10:00:00','12:00:00','Room 201','Dr Brown'),(4,4,'Wednesday','09:00:00','11:00:00','Lab 1','Dr Taylor'),(5,5,'Thursday','11:00:00','13:00:00','Room 202','Dr Wilson'),(6,6,'Friday','10:00:00','12:00:00','Lab 2','Dr Clark');
/*!40000 ALTER TABLE `timetable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(20) NOT NULL,
  `must_change_password` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Ritik Kumar','ritik@student.com','scrypt:32768:8:1$XzBOOY7s966jcpY4$17f87e181fb54415539dc8c6fc44d7ddfdff8529c957f3e080f773b49f2ca64f35dc646f7f41adb480b4b38903604673c5467edd3799ad29c4a53a26bb3a2381','student',0),(2,'John Smith','john@student.com','scrypt:32768:8:1$l2gbvyuxU3rDWklj$e25838028285e0fb8078fa7602fd7ce40539e7afa67ddabe9fe3282b3dff2993ba35e50bf3d85b6ff8dacdaba78e8edf0513a610e9e81e1b82946d0da2fd138e','student',0),(3,'Tom Brown','tom@student.com','scrypt:32768:8:1$1I630hWsMQnbm5Gn$5615e25b9451e66a308e2022de3a25800a7facb0c215b5e1fdb5336ba650709de01a800b6f58595cacc5ef09660138d900078c2c3b2a5343bb0bc172c6bc11c5','student',0),(4,'Admin User','admin@portal.com','scrypt:32768:8:1$YRC1dKvL9pFTHTzo$dfa78459577f744be240f18cd3883c4577fd4a81ae8be91ba5c5ae84330d0e7024e8ddff06fbaaec8609973735ce20eba0729d1962de1252d970c4a0c41e0723','admin',0),(5,'Sahil','sahil@student.com','scrypt:32768:8:1$Pj9AVut7s357hEgp$e6420c26be65325a1fb68fc00c67310d60214f48187b91198e43786a671b37dde4561408866161bd1616693a90ac7d4fe1ee9bc8d731639b1287744aef51eace','student',0),(6,'Rohan Kumar','rohan@student.com','scrypt:32768:8:1$uGcJeQy2o9oi8zjJ$5e25d88d3b0ed586c1ce8afd31bf497e0e011df8fa31a2c06c54d576ebd4b7cebe0f191a8922c0cb54f399bc2f1b431bcb83fa03911fe62ab89432b40625e5bd','student',0),(7,'Joe Root','joe@student.com','scrypt:32768:8:1$SDVeDfwUsks1y9HB$5048c42678bc0e2551e258560693086c59d2313701a122f12cd38e52cffab90b72ef82cb1d973140ca0ef063f5de759889533dfbf1b2bd2b10518c5a55751e49','student',0),(8,'Steve Smith','steve@student.com','scrypt:32768:8:1$CkmxVX6XqKFrmrn4$88e34e55778e2c68eaf2e9c785a933e314553dfb65f4c49da2fd6748e7c6f9912887159399ec9a7d4ee06973c84c860c8bebf79a8c9c15022d5afa58b0490f38','student',0),(9,'David Warner','David@student.com','scrypt:32768:8:1$kNDZphM2rwWcvPsL$6a5ba7e4b6753b4e48850e68d4657f0df87a66997d4b29dddf7a524ff658fe6c1fa331952c24da355ee264cceca0ff4d7743f75a1a01f496f76c3bf7f675264c','student',0),(10,'Tim Cook','tim@student.com','scrypt:32768:8:1$kI7NbCnc2drTfMmW$fdec3171adb5d1a4e0831616d717a51700017670a2d07206996828e5c21a5e2bc797f6f9e88ea5a3073424a9d5f03f26c626f45e493edc942009b5f0a1c04d57','student',0);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-18 23:50:47
