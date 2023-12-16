-- db1.Comments definition

CREATE TABLE `Comments` (
  `CommentID` char(36) NOT NULL,
  `UserID` char(36) DEFAULT NULL,
  `PostID` char(36) DEFAULT NULL,
  `Content` text,
  `Timestamp` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`CommentID`),
  KEY `UserID` (`UserID`),
  KEY `PostID` (`PostID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- db1.Friends definition

CREATE TABLE `Friendship` (
  `FriendshipID` char(36) NOT NULL,
  `UserID` char(36) NOT NULL,
  `FriendID` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`FriendshipID`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- db1.Posts definition

CREATE TABLE `Posts` (
  `PostID` char(36) NOT NULL,
  `UserID` char(36) DEFAULT NULL,
  `CommentCount` int DEFAULT NULL,
  `Content` text,
  `Timestamp` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`PostID`),
  KEY `UserID` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- db1.Users definition

CREATE TABLE `Users` (
  `UserID` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `Username` varchar(255) DEFAULT NULL,
  `Name` varchar(255) DEFAULT NULL,
  `Email` varchar(255) DEFAULT NULL,
  `Birthday` date DEFAULT NULL,
  `FriendCount` int DEFAULT NULL,
  `IpIdentifier` int DEFAULT NULL,
  PRIMARY KEY (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;