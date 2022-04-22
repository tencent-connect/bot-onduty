-- MySQL dump 10.14  Distrib 5.5.64-MariaDB, for Linux (x86_64)
--
-- Host: 9.135.138.187    Database: bot_onduty
-- ------------------------------------------------------
-- Server version	5.7.18-txsql-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `t_feedback`
--

DROP TABLE IF EXISTS `t_feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_feedback` (
  `id` int(9) NOT NULL AUTO_INCREMENT,
  `feedback_user_name` varchar(50) DEFAULT NULL COMMENT '反馈用户名称',
  `feedback_message_id` mediumtext NOT NULL COMMENT '反馈消息id',
  `feedback_text` text COMMENT '反馈内容',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `feedback_user_id` varchar(50) DEFAULT NULL COMMENT '反馈用户id',
  `feedback_owner_name` varchar(50) DEFAULT NULL COMMENT '反馈跟进人员名称',
  `feedback_owner_id` varchar(50) DEFAULT NULL COMMENT '反馈跟进人员id',
  `feedback_status` int(9) DEFAULT '0' COMMENT '反馈处理状态 0:打开、1:处理好',
  `feedback_type` varchar(9) NOT NULL DEFAULT '缺陷',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=153 DEFAULT CHARSET=utf8 COMMENT='反馈数据表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `t_owner`
--

DROP TABLE IF EXISTS `t_owner`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_owner` (
  `owner_id` varchar(50) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `owner_name` varchar(50) DEFAULT NULL,
  `on_duty_time` varchar(20) DEFAULT NULL,
  `owner_type` varchar(9) DEFAULT '技术',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=85 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `t_sign`
--

DROP TABLE IF EXISTS `t_sign`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t_sign` (
  `id` int(16) NOT NULL AUTO_INCREMENT,
  `owner_id` varchar(50) NOT NULL,
  `owner_name` varchar(20) DEFAULT NULL,
  `sign_in_time` datetime DEFAULT NULL,
  `sign_out_time` datetime DEFAULT NULL,
  `date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;


/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-04-21 21:01:36
