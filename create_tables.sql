USE oksanen;
SET NAMES utf8;

#DROP TABLE IF EXISTS user;
CREATE TABLE user (
    id INT unsigned NOT NULL AUTO_INCREMENT,
    user VARCHAR(20) NOT NULL,
    said INT DEFAULT 0,
    words INT DEFAULT 0,
    kicks INT DEFAULT 0,
    bans INT DEFAULT 0,
    kickeds INT DEFAULT 0,
    banneds INT DEFAULT 0,
    joins INT DEFAULT 0,
    parts INT DEFAULT 0,
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    part_date TIMESTAMP DEFAULT 0,
    averagetime INT DEFAULT 0,
    password VARCHAR(42),
    primary key (id)
) ENGINE=MyISAM DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

#DROP TABLE IF EXISTS gamescores;
CREATE TABLE gamescores (
	user VARCHAR(20) NOT NULL,
	wordgame INT DEFAULT 0,
	musavisa INT DEFAULT 0,
	ruletti INT DEFAULT 0,
	ruletti_bang INT DEFAULT 0,
	primary key (user)
) ENGINE=MyISAM DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

#DROP TABLE IF EXISTS hourstats;
CREATE TABLE hourstats (
	hour INT unsigned NOT NULL,
    said INT DEFAULT 0,
	words INT DEFAULT 0,
	primary key (hour)
) ENGINE=MyISAM DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

#INSERT INTO hourstats values(0,0,0);
#INSERT INTO hourstats values(1,0,0);
#INSERT INTO hourstats values(2,0,0);
#INSERT INTO hourstats values(3,0,0);
#INSERT INTO hourstats values(4,0,0);
#INSERT INTO hourstats values(5,0,0);
#INSERT INTO hourstats values(6,0,0);
#INSERT INTO hourstats values(7,0,0);
#INSERT INTO hourstats values(8,0,0);
#INSERT INTO hourstats values(9,0,0);
#INSERT INTO hourstats values(10,0,0);
#INSERT INTO hourstats values(11,0,0);
#INSERT INTO hourstats values(12,0,0);
#INSERT INTO hourstats values(13,0,0);
#INSERT INTO hourstats values(14,0,0);
#INSERT INTO hourstats values(15,0,0);
#INSERT INTO hourstats values(16,0,0);
#INSERT INTO hourstats values(17,0,0);
#INSERT INTO hourstats values(18,0,0);
#INSERT INTO hourstats values(19,0,0);
#INSERT INTO hourstats values(20,0,0);
#INSERT INTO hourstats values(21,0,0);
#INSERT INTO hourstats values(22,0,0);
#INSERT INTO hourstats values(23,0,0);

#DROP TABLE IF EXISTS log;
CREATE TABLE log (
	ID INT unsigned NOT NULL AUTO_INCREMENT,
	USER VARCHAR(20) NOT NULL,
	ENTRY VARCHAR(400) NOT NULL,
	SCORE INT DEFAULT 0,
	DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	LASTVOTEIP VARCHAR(15),
	FULLTEXT (USER,ENTRY),
	primary key (ID)
) ENGINE=MyISAM DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

#DROP TABLE IF EXISTS url;
CREATE TABLE url (
	ID INT unsigned NOT NULL AUTO_INCREMENT,
	USER VARCHAR(20) NOT NULL,
	URI TEXT NOT NULL,
	TITLE TEXT NOT NULL,
	DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FULLTEXT (TITLE,USER,URI),
	primary key (ID)
) ENGINE=MyISAM DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

#DROP TABLE IF EXISTS uustytto;
CREATE TABLE uustytto (
	ID INT unsigned NOT NULL AUTO_INCREMENT,
	NAME varchar(32),
	primary key (ID)
) ENGINE=MyISAM DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
