CREATE DATABASE app
  CHARACTER SET utf8mb4  -- important to allow accented characters
  COLLATE utf8mb4_unicode_ci;  -- important for sorting/ordering/comparing

USE app;  -- making this the active database we want to create tables in

-- users table (each row is a new user)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,  -- auto assigning an identifier to each user made, increments by one each time
    username VARCHAR(100) NOT NULL UNIQUE,  -- cannot be empty, and cannot be repeated with other users
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL  -- storing the encrypted password
);

-- sports events (matches/things to bet on, each row is a new match etc)
CREATE TABLE sports_events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    sport_type VARCHAR(50) NOT NULL,  -- football, baseball, etc
    team1 VARCHAR(100) NOT NULL,
    team2 VARCHAR(100) NOT NULL,
    event_date DATETIME NOT NULL,  -- the type of variable is datetime (for storing a date)
    bet_status ENUM('OPEN', 'CLOSED', 'SETTLED') NOT NULL DEFAULT 'OPEN'  -- "open" for events that can be bet on, "closed" if match has already ended, "settled" for redeeming balances
);

-- wallet transactions (movements in user balance, each row is a transaction which requires it to be linked to an existing user) 
CREATE TABLE wallet_transactions (
    tx_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,  -- to link the transaction to a user
    amount DECIMAL(9,2) NOT NULL,  -- allows numbers to 2 decimal places up to 9,999,999.99
    tx_type ENUM('DEPOSIT', 'WITHDRAW', 'BET', 'WIN') NOT NULL,  -- when a user deposits it'll make a new row with DEPOSIT + amount,  BET subtracts money, WIN adds, WITHDRAW subtracts etc
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)  -- the user_id we use here has to exist already in the users table
);

-- bets table (one row per bet, requires an existing user to place the bet and an existing event to be bet on)
CREATE TABLE bets (
    bet_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,  -- to identify who is placing the bet
    event_id INT NOT NULL,  -- to identify which event they're betting on
    amount DECIMAL(6,2) NOT NULL,  -- can only bet up to 9,999.99
    selected_option ENUM('TEAM1', 'TEAM2', 'DRAW') NOT NULL,  -- the different options for betting
    odds DECIMAL(5,2) NOT NULL,  -- the odds on the bet up to 999.99, this will be saved at the time of bet in case they change
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- registering the time of bet
    result ENUM('PENDING', 'WON', 'LOST') NOT NULL DEFAULT 'PENDING',  -- outcome of the bet, PENDING if the game is still ongoing
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (event_id) REFERENCES sports_events(event_id)  -- can only bet on an event that actually exists
);
