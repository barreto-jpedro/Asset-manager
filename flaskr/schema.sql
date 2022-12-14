DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS transactions;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  transactionDate TIMESTAMP NOT NULL,
  assetTicker TEXT NOT NULL,
  avaragePaidValue INTEGER NOT NULL,
  amount INTEGER NOT NULL,
  operation TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);
