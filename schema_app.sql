CREATE DATABASE app
  CHARACTER SET utf8mb4  -- important to allow accented characters
  COLLATE utf8mb4_unicode_ci;  -- important for sorting/ordering/comparing

USE app;  -- making this the active database we want to create tables in

-- users table (each row is a new user)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,  -- auto assigning an identifier to each user made, increments by one each time
    username VARCHAR(100) NOT NULL UNIQUE,  -- cannot be empty, and cannot be repeated with other users
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,  -- storing the encrypted password
    balance DECIMAL(9,2) NOT NULL DEFAULT 0.00  -- assigning a balance for each user
);

-- sports events (matches/things to bet on, each row is a new match etc)
CREATE TABLE sports_events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    sport_type VARCHAR(50) NOT NULL,  -- football, baseball, etc
    team1 VARCHAR(100) NOT NULL,
    team2 VARCHAR(100) NOT NULL,
    event_date DATETIME NOT NULL,  -- the type of variable is datetime (for storing a date)
    bet_status ENUM("OPEN", "CLOSED", "SETTLED") NOT NULL DEFAULT "OPEN"  -- "open" for events that can be bet on, "closed" if match has already started, "settled" for redeeming balances
);

-- wallet transactions (movements in user balance, each row is a transaction which requires it to be linked to an existing user) 
CREATE TABLE wallet_transactions (
    tx_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,  -- to link the transaction to a user
    amount DECIMAL(9,2) NOT NULL,  -- allows numbers to 2 decimal places up to 9,999,999.99
    tx_type ENUM("DEPOSIT", "WITHDRAW", "BET", "WIN") NOT NULL,  -- when a user deposits it"ll make a new row with DEPOSIT + amount,  BET subtracts money, WIN adds, WITHDRAW subtracts etc
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)  -- the user_id we use here has to exist already in the users table
);

-- bets table (one row per bet, requires an existing user to place the bet and an existing event to be bet on)
CREATE TABLE bets (
    bet_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,  -- to identify who is placing the bet
    event_id INT NOT NULL,  -- to identify which event they"re betting on
    amount DECIMAL(6,2) NOT NULL,  -- can only bet up to 9,999.99
    selected_option ENUM("TEAM1", "TEAM2", "DRAW") NOT NULL,  -- the different options for betting
    odds DECIMAL(5,2) NOT NULL,  -- the odds on the bet up to 999.99, this will be saved at the time of bet in case they change
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- registering the time of bet
    result ENUM("PENDING", "WON", "LOST") NOT NULL DEFAULT "PENDING",  -- outcome of the bet, PENDING if the game is still ongoing
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (event_id) REFERENCES sports_events(event_id)  -- can only bet on an event that actually exists
);

-- sample entries generated to use (because i don"t have the money for an api...)
INSERT INTO sports_events (sport_type, team1, team2, event_date, bet_status) VALUES
("Football", "Real Madrid", "Barcelona", "2025-01-14 20:45:00", "OPEN"),
("Football", "Arsenal", "Chelsea", "2025-01-16 18:30:00", "OPEN"),
("Football", "Boca Juniors", "River Plate", "2025-01-22 21:00:00", "OPEN"),
("Football", "Manchester City", "Liverpool", "2025-01-25 17:00:00", "OPEN"),
("Football", "Inter Milan", "Juventus", "2025-02-01 20:00:00", "OPEN"),

("Basketball", "LA Lakers", "Boston Celtics", "2025-01-19 02:30:00", "OPEN"),
("Basketball", "Chicago Bulls", "Miami Heat", "2025-01-21 01:00:00", "OPEN"),
("Basketball", "Golden State Warriors", "Phoenix Suns", "2025-01-20 03:00:00", "OPEN"),
("Basketball", "New York Knicks", "Brooklyn Nets", "2025-01-28 02:00:00", "OPEN"),
("Basketball", "San Antonio Spurs", "Houston Rockets", "2025-02-03 01:30:00", "OPEN"),

("Tennis", "Novak Djokovic", "Carlos Alcaraz", "2025-01-15 14:00:00", "OPEN"),
("Tennis", "Jannik Sinner", "Daniil Medvedev", "2025-01-17 12:00:00", "CLOSED"),
("Tennis", "Rafael Nadal", "Holger Rune", "2025-01-18 16:30:00", "SETTLED"),

("Baseball", "New York Yankees", "LA Dodgers", "2025-04-02 19:00:00", "OPEN"),
("Baseball", "Chicago Cubs", "St. Louis Cardinals", "2025-04-04 20:00:00", "OPEN"),
("Baseball", "Boston Red Sox", "Houston Astros", "2025-04-05 18:30:00", "OPEN"),

("MMA", "Jon Jones", "Stipe Miocic", "2025-03-11 23:00:00", "OPEN"),
("MMA", "Sean O'Malley", "Merab Dvalishvili", "2025-03-12 23:00:00", "OPEN"),
("MMA", "Alex Pereira", "Jiri Prochazka", "2025-03-15 22:30:00", "OPEN"),

("Boxing", "Tyson Fury", "Oleksandr Usyk", "2025-05-09 22:00:00", "OPEN"),
("Boxing", "Gervonta Davis", "Ryan Garcia", "2025-05-15 23:00:00", "OPEN"),
("Boxing", "Canelo Alvarez", "David Benavidez", "2025-05-20 21:30:00", "OPEN");
