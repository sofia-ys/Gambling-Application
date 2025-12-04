import mysql.connector  
import bcrypt  # for encrypting passwords
from datetime import datetime
import random 

FROZEN_NOW = datetime(2025, 3, 15, 12, 0, 0)  # this is because we're not implenting an actual API, and just a frozen in time sort of app :/

# user CRUD management
# making the connection to the mysql db
def get_connection():
    conn = mysql.connector.connect(  # opens a connection the the mysql server
        host="localhost",
        user="root",
        password="Passw0rd!",  # this will have to be adjusted to each user's thing?? 
        database="app"
    )
    return conn

# creating a user in the database
def create_user(username, email, plain_password):
    conn = get_connection()  # opens the db connection
    cursor = conn.cursor(dictionary=True)  # cursor object lets us execute sql commands

    password_hash = bcrypt.hashpw(
        plain_password.encode("utf-8"),  # string entered password into bytes
        bcrypt.gensalt()
    ).decode("utf-8")

    # this is what we insert into the sql db
    sql = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
    cursor.execute(sql, (username, email, password_hash))  # exectuing the sql command with the values 
    conn.commit()

    user_id = cursor.lastrowid  # so we know the id of the user to then reference later
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    print(f"User created with ID: {user['user_id']}")
    cursor.close()
    conn.close()
    return user

# finding a user via their username
def get_user(username):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)  # returns the rows as python dictionaries so we can index by key

    sql = "SELECT * FROM users WHERE username = %s"
    cursor.execute(sql, (username,))  # the comma after username is because we need to send it as a tuple
    user = cursor.fetchone()  # retrieves the first row from the results of the query (finding the user by username), the result here is a dictionary with all the row values for the user

    if not user:  # if we don't find the user </3
        return None

    print(f"User found with ID: {user['user_id']}")
    cursor.close()
    conn.close()
    return user

# checking if the password matches for a user
def verify_login(username, plain_password):
    user = get_user(username)
    if user is None:
        print(f"User not found")
        return None  # the user isn't registered

    stored_password_hash = user["password_hash"].encode("utf-8")  # getting their password
    if bcrypt.checkpw(plain_password.encode("utf-8"), stored_password_hash):  # if the password they entered when encrypted matches the encrypted one stored
        print(f"User logged in with ID: {user['user_id']}")
        return user
    else:
        print(f"User password did not match")
        return None

# updating a user's username, email, or password
def update_user(user_id, username=None, email=None, plain_password=None):
    conn = get_connection()
    cursor = conn.cursor()

    # here we send up to 3 different sql queries, might be better to make it just one...
    if username is not None:  # if this exists
        sql = "UPDATE users SET username = %s WHERE user_id = %s"
        cursor.execute(sql, (username, user_id))
        conn.commit()
        print(f"Username updated with ID: {user_id}")

    if email is not None:
        sql = "UPDATE users SET email = %s WHERE user_id = %s"
        cursor.execute(sql, (email, user_id))
        conn.commit()
        print(f"Email updated with ID: {user_id}")

    if plain_password is not None:  
        password_hash = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        sql = "UPDATE users SET password_hash = %s WHERE user_id = %s"
        cursor.execute(sql, (password_hash, user_id))
        conn.commit()
        print(f"Password updated with ID: {user_id}")

    cursor.close()
    conn.close()

# removing a user from the database
def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM users WHERE user_id = %s"  # removing the user from the table
    cursor.execute(sql, (user_id,))
    conn.commit()
    print(f"User deleted with ID: {user_id}")
    cursor.close()
    conn.close()

# transactions management

# sports events management
def get_sports_events():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM sports_events ORDER BY event_date"  # Adjust table/columns as needed
    cursor.execute(sql)
    events = cursor.fetchall()
    cursor.close()
    conn.close()
    return events  # Returns list of dicts like [{'event_id':1, 'team1':'Real Madrid', 'team2':'Barcelona', 'odds':1.8, ...}]

def update_event_status_by_cutoff(): #Update bet_status using frontend cutoff values
    conn = get_connection()
    cursor = conn.cursor()
    
    # Convert Python datetime to MySQL format for comparison
    # cutoff_start_str = cutoff_live_start.strftime('%Y-%m-%d %H:%M:%S')
    # cutoff_end_str = cutoff_live_end.strftime('%Y-%m-%d %H:%M:%S')

    cutoff_str = FROZEN_NOW.strftime('%Y-%m-%d %H:%M:%S')  # this is the cutoff date that we chose
    
    # Update past events to CLOSED
    cursor.execute("UPDATE sports_events SET bet_status = 'CLOSED' WHERE event_date < %s AND bet_status = 'OPEN'", (cutoff_str,))
    
    updated = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    
def place_bet(user_id, event_id, outcome, amount, odds):
    """Place a bet: create wallet transaction, bet record, deduct balance"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verify user balance (balance is INT in your schema)
        cursor.execute("SELECT balance FROM users WHERE user_id = %s FOR UPDATE", (user_id,))
        user = cursor.fetchone()
        if not user or user['balance'] < amount:
            print("Insufficient balance")
            return None
        
        # Verify event is OPEN
        cursor.execute("SELECT bet_status FROM sports_events WHERE event_id = %s", (event_id,))
        event = cursor.fetchone()
        if not event or event['bet_status'] != 'OPEN':
            print("Event not available for betting")
            return None
        
        # Convert frontend outcomes to backend format
        outcome_map = {"HOME_WIN": "TEAM1", "AWAY_WIN": "TEAM2", "DRAW": "DRAW"}
        db_outcome = outcome_map.get(outcome, outcome)
        
        # Begin transaction
        cursor.execute("START TRANSACTION")
        
        # 1. Create BET transaction (negative amount)
        cursor.execute("""
            INSERT INTO wallet_transactions (user_id, amount, tx_type) 
            VALUES (%s, %s, 'BET')
        """, (user_id, -float(amount)))
        
        # 2. Deduct from balance
        cursor.execute("UPDATE users SET balance = balance - %s WHERE user_id = %s", (amount, user_id))
        
        # 3. Insert bet
        sql = """
            INSERT INTO bets (user_id, event_id, amount, selected_option, odds) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (user_id, event_id, amount, db_outcome, odds))
        bet_id = cursor.lastrowid
        
        conn.commit()
        print(f"Bet placed: ID {bet_id}, ${amount} on {db_outcome} (odds: {odds})")
        return {'bet_id': bet_id, 'status': 'PENDING'}
    
    except Exception as e:
        conn.rollback()
        print(f"Bet failed: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_balance(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    sql = "SELECT balance FROM users WHERE user_id = %s"
    cursor.execute(sql, (user_id,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:  # if the user_id doesn't exist 
        return None 
    return float(row[0])  # gives us the balance as a number


def deposit(user_id, amount):

    if amount <= 0:
        print("Deposit amount must be positive.")
        return None

    conn = get_connection()
    cursor = conn.cursor()

    sql_wallet = """
            INSERT INTO wallet_transactions (user_id, amount, tx_type) 
            VALUES (%s, %s, "DEPOSIT")
        """
    sql_users = """
            UPDATE users SET balance = balance + %s WHERE user_id = %s
        """
    
    cursor.execute(sql_wallet, (user_id, amount))  # adding the transaction so we can keep track of it
    cursor.execute(sql_users, (amount, user_id))
    conn.commit()

    new_balance = get_balance(user_id)

    cursor.close()
    conn.close()

    print(f"${amount} deposited to user {user_id}. New balance is ${new_balance}")
    return new_balance

def withdraw(user_id, amount):

    if amount <= 0: 
        print("Withdraw amount must be positive.")
        return None
    
    if get_balance(user_id) < amount:  # not enough money
        print("Insufficient balance.")
        return None

    conn = get_connection()
    cursor = conn.cursor()

    sql_wallet = """
            INSERT INTO wallet_transactions (user_id, amount, tx_type) 
            VALUES (%s, %s, "WITHDRAW")
        """
    sql_users = """
            UPDATE users SET balance = balance - %s WHERE user_id = %s
        """
    
    cursor.execute(sql_wallet, (user_id, amount))  # adding the transaction so we can keep track of it
    cursor.execute(sql_users, (amount, user_id))
    conn.commit()

    new_balance = get_balance(user_id)

    cursor.close()
    conn.close()

    print(f"${amount} withdrawn from user {user_id}. New balance is ${new_balance}")
    return new_balance

def get_wallet_transactions(user_id, limit=10):  # only show past 10 txs bc otherwise too much <3
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT tx_id, amount, tx_type, created_at
        FROM wallet_transactions
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s
    """
    cursor.execute(sql, (user_id, limit))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows

# here we connect the bet with the sport event to get all the bets from a specific user
def get_user_bets(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT 
            b.*,
            s.sport_type,
            s.team1,
            s.team2,
            s.event_date,
            s.bet_status
        FROM bets b
        JOIN sports_events s ON b.event_id = s.event_id
        WHERE b.user_id = %s
        ORDER BY s.event_date DESC, b.created_at DESC
    """
    cursor.execute(sql, (user_id,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows

def _pick_random_outcome():  # this is just to randomly choose an outcome of the event
    return random.choice(["TEAM1", "TEAM2", "DRAW"])

def settle_event_random(event_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM sports_events WHERE event_id = %s FOR UPDATE",
        (event_id,)
    )
    event = cursor.fetchone()
    if not event or event["bet_status"] != "OPEN":
        print("Event cannot be settled (not found or not OPEN).")
        return 0

    winning_option = _pick_random_outcome()
    print(f"Settling event {event_id} with random winner: {winning_option}")

    # get all pending bets for this event
    cursor.execute(
        "SELECT * FROM bets WHERE event_id = %s AND result = 'PENDING'",
        (event_id,)
    )
    bets = cursor.fetchall()

    # start transaction
    cursor.execute("START TRANSACTION")

    # here we go through each bet placed on an event, and for every user that bet, mark the bet as won/lost and update their balance if they won
    for bet in bets:  # so for each bet made by all the users for that one specific event
        bet_id = bet["bet_id"]
        user_id = bet["user_id"]
        amount = float(bet["amount"])
        odds = float(bet["odds"])
        selected = bet["selected_option"]

        if selected == winning_option:
            win_amount = round(amount * odds, 2)

            cursor.execute(
                "UPDATE bets SET result = 'WON' WHERE bet_id = %s",  # mark bet as WON
                (bet_id,)
            )

            cursor.execute( # wallet transaction for WIN
                """
                INSERT INTO wallet_transactions (user_id, amount, tx_type)
                VALUES (%s, %s, 'WIN')
                """,
                (user_id, win_amount)
            )

            cursor.execute(  # update user balance
                "UPDATE users SET balance = balance + %s WHERE user_id = %s",
                (win_amount, user_id)
            )
        else:
            cursor.execute(  # mark bet as LOST, the user doesn't get any money back from the bet
                "UPDATE bets SET result = 'LOST' WHERE bet_id = %s",
                (bet_id,)
            )

    cursor.execute(  # mark event as SETTLED after we finish going through all bets placed on it
        "UPDATE sports_events SET bet_status = 'SETTLED' WHERE event_id = %s",
        (event_id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return len(bets)  # just to know how many bets were placed

# for any event that has PASSED we need to get the result of the game
def settle_past_events_random(cutoff_datetime=None):
    if cutoff_datetime is None:
        cutoff_datetime = FROZEN_NOW  # datetime.now() this is adjust to our frozen in time

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT * FROM sports_events
        WHERE bet_status = 'OPEN' AND event_date <= %s
        """,
        (cutoff_datetime,)
    )
    events = cursor.fetchall()

    count = 0
    for event in events:  # for each event that is happening
        event_id = event["event_id"]
        # reuse the single-event function
        settled_bets = settle_event_random(event_id)
        if settled_bets >= 0:
            count += 1

    cursor.close()
    conn.close()
    return count

