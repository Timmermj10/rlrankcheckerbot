PRAGMA foreign_keys = ON;

CREATE TABLE users(
  username VARCHAR(20) NOT NULL,
  id VARCHAR(40) NOT NULL,
  platform VARCHAR(5) NOT NULL,
  PRIMARY KEY(username)
);

CREATE TABLE ones(
  user VARCHAR(20) NOT NULL,
  mmr int NOT NULL,
  period int NOT NULL,
  FOREIGN KEY (user) REFERENCES users(username) ON DELETE CASCADE
);

CREATE TABLE twos(
  user VARCHAR(20) NOT NULL,
  mmr int NOT NULL,
  period int NOT NULL,
  FOREIGN KEY (user) REFERENCES users(username) ON DELETE CASCADE
);

CREATE TABLE threes(
  user VARCHAR(20) NOT NULL,
  mmr int NOT NULL,
  period int NOT NULL,
  FOREIGN KEY (user) REFERENCES users(username) ON DELETE CASCADE
);