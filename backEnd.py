import mysql.connector  
import bcrypt  # for encrypting passwords

# making the connection to the mysql db
def get_connection():
    conn = mysql.connector.connect(  # opens a connection the the mysql server
        host="localhost",
        user="root",
        password="Gr4C14sT0t4l3s!",
        database="betting_app"
    )
    return conn

def create_user(name, surname, email, plain_password, dni=None):
    conn = get_connection()  # opens the db connection
    cursor = conn.cursor()  # cursor object lets us execute sql commands

    password_hash = bcrypt.hashpw(
        plain_password.encode("utf-8"),  # string entered password into bytes
        bcrypt.gensalt()
    ).decode("utf-8")

    sql = """
        INSERT INTO users (dni, name, surname, email, password_hash)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (dni, name, surname, email, password_hash))
    conn.commit()

    user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return user_id

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = "SELECT * FROM users WHERE email = %s"
    cursor.execute(sql, (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()
    return user

def update_user(user_id, name=None, surname=None):
    conn = get_connection()
    cursor = conn.cursor()

    sql = "UPDATE users SET name = %s, surname = %s WHERE user_id = %s"
    cursor.execute(sql, (name, surname, user_id))
    conn.commit()

    cursor.close()
    conn.close()

def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    sql = "DELETE FROM users WHERE user_id = %s"
    cursor.execute(sql, (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
