import mysql.connector  
import bcrypt  # for encrypting passwords

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
    cursor = conn.cursor()  # cursor object lets us execute sql commands

    password_hash = bcrypt.hashpw(
        plain_password.encode("utf-8"),  # string entered password into bytes
        bcrypt.gensalt()
    ).decode("utf-8")

    # this is what we insert into the sql db
    sql = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
    cursor.execute(sql, (username, email, password_hash))  # exectuing the sql command with the values 
    conn.commit()

    user_id = cursor.lastrowid  # so we know the id of the user to then reference later

    print(f"User created with ID: {user_id}")
    cursor.close()
    conn.close()
    return user_id

# finding a user via their username
def get_user(username):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)  # returns the rows as python dictionaries so we can index by key

    sql = "SELECT * FROM users WHERE username = %s"
    cursor.execute(sql, (username,))  # the comma after username is because we need to send it as a tuple
    user = cursor.fetchone()  # retrieves the first row from the results of the query (finding the user by username), the result here is a dictionary with all the row values for the user

    print(f"User found with ID: {user["user_id"]}")
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
        print(f"User logged in with ID: {user["user_id"]}")
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