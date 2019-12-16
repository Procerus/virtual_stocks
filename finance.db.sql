BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "stocks" (
	"stockid"	integer NOT NULL PRIMARY KEY AUTOINCREMENT,
	"stocks"	char(5)
);
CREATE TABLE IF NOT EXISTS "history" (
	"id"	integer NOT NULL PRIMARY KEY AUTOINCREMENT,
	"userid"	integer,
	"stockid"	integer,
	"buy"	boolean,
	"cost"	real,
	"amount"	integer,
	"date"	date
);
CREATE TABLE IF NOT EXISTS "owned" (
	"id"	integer NOT NULL PRIMARY KEY AUTOINCREMENT,
	"userid"	integer,
	"stockid"	integer,
	"amount"	integer
);
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"username"	TEXT NOT NULL,
	"hash"	TEXT NOT NULL,
	"cash"	NUMERIC NOT NULL DEFAULT 10000.00
);
INSERT INTO "stocks" VALUES (1,'NFLX');
INSERT INTO "stocks" VALUES (2,'FOR');
INSERT INTO "stocks" VALUES (3,'OIL');
INSERT INTO "stocks" VALUES (7,'GOOG');
INSERT INTO "stocks" VALUES (8,'AAPL');
INSERT INTO "history" VALUES (1,5,1,1,307.35,1,'2019-12-08 14:38:49');
INSERT INTO "history" VALUES (2,5,2,1,19.77,1,'2019-12-08 23:22:00');
INSERT INTO "history" VALUES (3,5,2,1,19.77,1,'2019-12-09 02:08:22');
INSERT INTO "history" VALUES (4,5,3,1,12.11,1,'2019-12-09 02:18:16');
INSERT INTO "history" VALUES (5,5,1,0,307.35,1,'2019-12-09 03:05:03');
INSERT INTO "history" VALUES (6,5,1,0,307.35,1,'2019-12-09 03:05:36');
INSERT INTO "history" VALUES (7,5,2,0,19.67,1,'2019-12-10 04:55:06');
INSERT INTO "history" VALUES (8,5,1,0,302.5,1,'2019-12-10 04:55:15');
INSERT INTO "history" VALUES (9,5,2,0,19.67,-1,'2019-12-10 05:06:40');
INSERT INTO "history" VALUES (10,5,2,1,19.67,2,'2019-12-10 05:13:26');
INSERT INTO "history" VALUES (11,5,1,1,302.5,10,'2019-12-10 05:14:18');
INSERT INTO "history" VALUES (12,5,1,1,302.5,1,'2019-12-10 05:14:55');
INSERT INTO "history" VALUES (13,5,1,0,302.5,-6,'2019-12-10 05:15:28');
INSERT INTO "history" VALUES (14,5,1,0,293.12,-7,'2019-12-11 01:33:05');
INSERT INTO "history" VALUES (15,5,1,1,293.12,1,'2019-12-11 02:39:28');
INSERT INTO "history" VALUES (16,5,1,1,293.12,1,'2019-12-11 02:54:37');
INSERT INTO "history" VALUES (17,5,3,1,12.158,20,'2019-12-11 02:55:21');
INSERT INTO "history" VALUES (18,5,7,1,1344.66,1,'2019-12-11 02:56:35');
INSERT INTO "history" VALUES (19,5,8,1,268.48,1,'2019-12-11 02:58:13');
INSERT INTO "history" VALUES (20,8,2,1,19.61,1,'2019-12-11 03:13:57');
INSERT INTO "history" VALUES (21,9,1,1,293.12,1,'2019-12-11 03:27:04');
INSERT INTO "history" VALUES (22,9,1,0,293.12,-1,'2019-12-11 03:29:04');
INSERT INTO "history" VALUES (23,9,2,1,19.61,1,'2019-12-11 04:10:44');
INSERT INTO "history" VALUES (24,9,2,1,19.61,1,'2019-12-11 04:10:55');
INSERT INTO "history" VALUES (25,9,2,0,19.61,-1,'2019-12-11 04:11:04');
INSERT INTO "history" VALUES (26,9,2,0,19.61,-1,'2019-12-11 04:11:28');
INSERT INTO "owned" VALUES (3,5,3,21);
INSERT INTO "owned" VALUES (4,5,2,2);
INSERT INTO "owned" VALUES (5,5,1,2);
INSERT INTO "owned" VALUES (6,5,7,1);
INSERT INTO "owned" VALUES (7,5,8,1);
INSERT INTO "owned" VALUES (8,8,2,1);
INSERT INTO "users" VALUES (5,'lucas','pbkdf2:sha256:150000$HbscTFnx$a619bbe46f08efb75c2bd066de9dd3cbc3a3764b7b83c5b043469697404f9a31',3539.68);
INSERT INTO "users" VALUES (6,'lucas1','pbkdf2:sha256:150000$ju4S9biO$a16fd2da2b8ff635383acb212cc07eedec4260927f1835adedd69702a9d077ca',10000);
INSERT INTO "users" VALUES (8,'name','pbkdf2:sha256:150000$Zr74Ta9o$b40d26f306ad04fe6580d19bbe2a1d2d6ef527112934c6694e7f1d533f498b90',9980.39);
INSERT INTO "users" VALUES (9,'u','pbkdf2:sha256:150000$sRmi4Dlo$48b6da24705b48a829d6619ba3a92b541f1a4996934425490e690a31909f8b4c',10000);
CREATE UNIQUE INDEX IF NOT EXISTS "username" ON "users" (
	"username"
);
COMMIT;
