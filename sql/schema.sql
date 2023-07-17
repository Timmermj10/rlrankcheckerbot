PRAGMA foreign_keys = ON;

CREATE TABLE users(
  username VARCHAR(20) NOT NULL,
  id VARCHAR(40) NOT NULL,
  platform VARCHAR(5) NOT NULL,
  PRIMARY KEY(username)
);