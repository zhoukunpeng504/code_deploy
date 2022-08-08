-- MySQL dump 10.13  Distrib 5.7.10, for osx10.11 (x86_64)
--
-- Host: 192.168.240.240    Database: cap_1
-- ------------------------------------------------------
-- Server version	5.5.5-10.4.19-MariaDB-log

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
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add 应用',7,'add_app'),(26,'Can change 应用',7,'change_app'),(27,'Can delete 应用',7,'delete_app'),(28,'Can view 应用',7,'view_app'),(29,'Can add 发布记录',8,'add_publog'),(30,'Can change 发布记录',8,'change_publog'),(31,'Can delete 发布记录',8,'delete_publog'),(32,'Can view 发布记录',8,'view_publog'),(33,'Can add 代码仓库服务器',9,'add_reposerver'),(34,'Can change 代码仓库服务器',9,'change_reposerver'),(35,'Can delete 代码仓库服务器',9,'delete_reposerver'),(36,'Can view 代码仓库服务器',9,'view_reposerver'),(37,'Can add 服务器',10,'add_server'),(38,'Can change 服务器',10,'change_server'),(39,'Can delete 服务器',10,'delete_server'),(40,'Can view 服务器',10,'view_server');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$150000$GIfYncvuYund$0VNw3b/333ENtn+mMPqnk4m0smRrkwoRXKQphSC4t+0=','2021-08-16 09:06:49.672369',1,'admin','','','admin@cap.com',1,1,'2021-07-28 18:31:33.034514');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cap_app`
--

DROP TABLE IF EXISTS `cap_app`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cap_app` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `proj_id` int(10) unsigned NOT NULL DEFAULT 0,
  `name` varchar(30) NOT NULL,
  `repo_server_id` int(10) unsigned NOT NULL DEFAULT 0,
  `repo_id` int(10) unsigned NOT NULL DEFAULT 0,
  `repo_git_url` varchar(200) NOT NULL,
  `branch_name` varchar(200) NOT NULL,
  `deploy_to` varchar(200) NOT NULL,
  `old_version_num` smallint(5) unsigned NOT NULL DEFAULT 0,
  `cmd_before_deploy` longtext NOT NULL,
  `cmd_build_app` longtext DEFAULT NULL,
  `cmd_start_app` longtext NOT NULL,
  `success_after_deploy` longtext NOT NULL,
  `cmd_before_deploy_test` longtext NOT NULL,
  `cmd_build_app_test` longtext DEFAULT NULL,
  `cmd_start_app_test` longtext NOT NULL,
  `success_after_deploy_test` longtext NOT NULL,
  `formal_server_ids` varchar(500) NOT NULL,
  `test_server_ids` varchar(500) NOT NULL,
  `addtime` int(10) unsigned NOT NULL,
  `cmd_before_deploy_3`       longtext                    null,
  `cmd_build_app_3`           longtext                    null,
  `cmd_start_app_3`           longtext                    null,
  `success_after_deploy_3`    longtext                    null,
  `cmd_before_deploy_4`       longtext                    null,
  `cmd_build_app_4`           longtext                    null,
  `cmd_start_app_4`           longtext                    null,
  `success_after_deploy_4`    longtext                    null,
  `server_ids_3`              varchar(500)     default '' not null,
  `server_ids_4`              varchar(500)     default '' not null,
  `code_tar_gz_path` varchar(500) default '' not null,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cap_app`
--

LOCK TABLES `cap_app` WRITE;
/*!40000 ALTER TABLE `cap_app` DISABLE KEYS */;
/*!40000 ALTER TABLE `cap_app` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cap_pub_log`
--

DROP TABLE IF EXISTS `cap_pub_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cap_pub_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ope_user_name` varchar(30) NOT NULL,
  `target_version` varchar(100) NOT NULL DEFAULT '',
  `target_version_meta` varchar(100) NOT NULL DEFAULT '',
  `app_id` int(10) unsigned NOT NULL,
  `environ_type` int(10) unsigned NOT NULL,
  `pub_type` int(10) unsigned NOT NULL DEFAULT 0,
  `operatetime` datetime(6) NOT NULL,
  `task_id` varchar(80) NOT NULL DEFAULT '',
  `task_log` longtext NOT NULL,
  `progress` int(11) NOT NULL,
  `status` smallint(5) unsigned NOT NULL,
  `status_uptime` int(11) unsigned NOT NULL DEFAULT 0,
  `reason` varchar(300) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cap_pub_log_ope_user_name_b7355ffb` (`ope_user_name`),
  KEY `cap_pub_log_operatetime_0c17c10c` (`operatetime`),
  KEY `cap_pub_log_progress_04a3506b` (`progress`),
  KEY `cap_pub_log_status_510959ea` (`status`),
  KEY `cap_pub_log_task_id_index` (`task_id`),
  KEY `cap_pub_log_app_id_index` (`app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cap_pub_log`
--

LOCK TABLES `cap_pub_log` WRITE;
/*!40000 ALTER TABLE `cap_pub_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `cap_pub_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cap_repo_server`
--

DROP TABLE IF EXISTS `cap_repo_server`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cap_repo_server` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `repo_name` varchar(50) NOT NULL,
  `server_url` varchar(100) NOT NULL,
  `addtime` int(10) unsigned NOT NULL,
  `repo_type` smallint(5) unsigned NOT NULL,
  `token` varchar(500) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `repo_name` (`repo_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cap_repo_server`
--

LOCK TABLES `cap_repo_server` WRITE;
/*!40000 ALTER TABLE `cap_repo_server` DISABLE KEYS */;
/*!40000 ALTER TABLE `cap_repo_server` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cap_server`
--

DROP TABLE IF EXISTS `cap_server`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cap_server` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `ip` varchar(15) NOT NULL,
  `user` varchar(50) NOT NULL,
  `password` varchar(200) NOT NULL,
  `ssh_port` smallint(6) NOT NULL,
  `addtime` int(10) unsigned NOT NULL,
  `code_mode` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `ip` (`ip`,`ssh_port`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cap_server`
--

LOCK TABLES `cap_server` WRITE;
/*!40000 ALTER TABLE `cap_server` DISABLE KEYS */;
/*!40000 ALTER TABLE `cap_server` ENABLE KEYS */;
UNLOCK TABLES;

DROP TABLE IF EXISTS `cap_project`;
create table `cap_project`
(
	`id` int(11) unsigned auto_increment,
	`name` varchar(100) default '' not null,
	`addtime` int(11) unsigned default 0 not null,
	 PRIMARY KEY (`id`),
	 UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


LOCK TABLES `cap_project` WRITE;
/*!40000 ALTER TABLE `cap_project` DISABLE KEYS */;
/*!40000 ALTER TABLE `cap_project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(7,'cap','app'),(8,'cap','publog'),(9,'cap','reposerver'),(10,'cap','server'),(5,'contenttypes','contenttype'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (2,'contenttypes','0001_initial','2021-07-28 18:27:23.121692'),(3,'auth','0001_initial','2021-07-28 18:27:23.185689'),(4,'admin','0001_initial','2021-07-28 18:27:23.290226'),(5,'admin','0002_logentry_remove_auto_add','2021-07-28 18:27:23.314872'),(6,'admin','0003_logentry_add_action_flag_choices','2021-07-28 18:27:23.323820'),(7,'contenttypes','0002_remove_content_type_name','2021-07-28 18:27:23.359600'),(8,'auth','0002_alter_permission_name_max_length','2021-07-28 18:27:23.372946'),(9,'auth','0003_alter_user_email_max_length','2021-07-28 18:27:23.390919'),(10,'auth','0004_alter_user_username_opts','2021-07-28 18:27:23.401765'),(11,'auth','0005_alter_user_last_login_null','2021-07-28 18:27:23.417455'),(12,'auth','0006_require_contenttypes_0002','2021-07-28 18:27:23.419932'),(13,'auth','0007_alter_validators_add_error_messages','2021-07-28 18:27:23.429661'),(14,'auth','0008_alter_user_username_max_length','2021-07-28 18:27:23.447131'),(15,'auth','0009_alter_user_last_name_max_length','2021-07-28 18:27:23.463844'),(16,'auth','0010_alter_group_name_max_length','2021-07-28 18:27:23.480514'),(17,'auth','0011_update_proxy_permissions','2021-07-28 18:27:23.493895'),(18,'sessions','0001_initial','2021-07-28 18:27:23.504367'),(19,'cap','0001_initial','2021-07-29 17:41:57.210122');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;


create  table `user_app_perm`
(
	uid int(11) unsigned auto_increment
		primary key,
	apps varchar(200) default '' not null,
	addtime int(11) unsigned default 0 not null
);


--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('4ayrarqacdg595afjewzbyixmw6vcvvf','YjI3NzAzOTVkY2RlYmM1MDVlNzUxODI3ZGFmOWM3YTQ5NjhlZjkyYjp7Il9hdXRoX3VzZXJfaWQiOiI2IiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI4YTg3MTU2OWVmZWFiYTRhNjdhZmZiZGRmZjhjOTE1ODExNWZmODNiIn0=','2040-09-22 14:01:01.976214'),('4lkjfhj2y88b7mvik88rxx7xfdpu3ge6','ODI4ODk1MjllOTkwOGUwNGNkYjBkMGQxMTY2ZDBiMzQ1YzE4YjlkNzp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI4ZjY0OWNjZjg5YTA5YjA2ZTkyZmYzMjk0OWE5MjllYTRjMmY4MjFiIn0=','2040-10-08 09:06:49.677059');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-08-16 15:12:21
