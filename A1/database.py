import sqlite3

def connect_db():
    conn = sqlite3.connect('Users.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE if not exists users (
                    email text primary key, 
                    first text,
                    last text,
                    password text,
                    account_created text,
                    account_updated integer )                     
    """)

connect_db()


def insert_user(email, firstname, lastname, password, account_created):
    conn = sqlite3.connect('Users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES(?,?,?,?,?,?)", (email, firstname, lastname, password, account_created, 0))
    conn.commit()


def update_user(email, firstname, lastname, password):
    conn = sqlite3.connect('Users.db')
    c = conn.cursor()

    c.execute("UPDATE users SET first = '?', last = '?', password = '?', account_updated = 1 WHERE email = '?' ",
              (firstname, lastname, password, email))
    conn.commit()
    return True



def get_user(email):
    conn = sqlite3.connect('Users.db')
    c = conn.cursor()
    c.execute(
        "SELECT email, first, last, account_created, account_updated,password FROM users WHERE email = '{n}'".format(n=email))
    conn.commit()
    return c.fetchone()


def validate_user(email, pw):
    try:
        conn = sqlite3.connect('Users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = '?' and password = '?'", (email, pw))
        conn.commit()
        return True
    except:
        return False
