/*
 Navicat Premium Data Transfer

 Source Server         : localhost_3306
 Source Server Type    : MySQL
 Source Server Version : 80025
 Source Host           : localhost:3306
 Source Schema         : web_disk

 Target Server Type    : MySQL
 Target Server Version : 80025
 File Encoding         : 65001

 Date: 29/04/2025 17:48:20
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for files
-- ----------------------------
DROP TABLE IF EXISTS `files`;
CREATE TABLE `files`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `parent_id` int(0) NULL DEFAULT NULL,
  `is_folder` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  INDEX `parent_id`(`parent_id`) USING BTREE,
  CONSTRAINT `files_ibfk_2` FOREIGN KEY (`parent_id`) REFERENCES `files` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of files
-- ----------------------------

-- ----------------------------
-- Table structure for security_questions
-- ----------------------------
DROP TABLE IF EXISTS `security_questions`;
CREATE TABLE `security_questions`  (
  `QuestionID` int(0) NOT NULL AUTO_INCREMENT,
  `Question` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`QuestionID`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of security_questions
-- ----------------------------
INSERT INTO `security_questions` VALUES (1, '你出生的城市是哪座？');
INSERT INTO `security_questions` VALUES (2, '你父亲的名字是什么？');
INSERT INTO `security_questions` VALUES (3, '你最喜欢的假期是什么时候？');
INSERT INTO `security_questions` VALUES (4, '你第一次乘坐飞机的目的地是哪里？');
INSERT INTO `security_questions` VALUES (5, '你第一次去的音乐会是哪一场？');
INSERT INTO `security_questions` VALUES (6, '你最喜欢的书籍是什么？');
INSERT INTO `security_questions` VALUES (7, '你最喜欢的电视节目是什么？');
INSERT INTO `security_questions` VALUES (8, '你第一次去的国外城市是哪座？');
INSERT INTO `security_questions` VALUES (9, '你上高中的学校名字是什么？');
INSERT INTO `security_questions` VALUES (10, '你最喜欢的运动队是哪支？');

-- ----------------------------
-- Table structure for sysuser
-- ----------------------------
DROP TABLE IF EXISTS `sysuser`;
CREATE TABLE `sysuser`  (
  `UserID` int(0) NOT NULL AUTO_INCREMENT COMMENT '用户id',
  `UserName` varchar(25) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '用户名',
  `passwd` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '用户密码',
  `Note` varchar(25) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '备注',
  `admin` int(0) NULL DEFAULT NULL COMMENT '管理员标识',
  PRIMARY KEY (`UserID`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of sysuser
-- ----------------------------

-- ----------------------------
-- Table structure for user_security
-- ----------------------------
DROP TABLE IF EXISTS `user_security`;
CREATE TABLE `user_security`  (
  `UserID` int(0) NOT NULL,
  `QuestionID` int(0) NOT NULL,
  `Answer` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`UserID`, `QuestionID`) USING BTREE,
  INDEX `QuestionID`(`QuestionID`) USING BTREE,
  CONSTRAINT `user_security_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `sysuser` (`UserID`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `user_security_ibfk_2` FOREIGN KEY (`QuestionID`) REFERENCES `security_questions` (`QuestionID`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user_security
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
