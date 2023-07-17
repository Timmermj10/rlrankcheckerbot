PRAGMA foreign_keys = ON;

CREATE TABLE users(
  username VARCHAR(20) NOT NULL,
  id VARCHAR(40) NOT NULL,
  PRIMARY KEY(username)
);