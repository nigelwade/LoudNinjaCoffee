DROP TABLE IF EXISTS articles;
CREATE TABLE articles (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	title STRING NOT NULL,
	text STRING NOT NULL
);