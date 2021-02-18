import sqlite3


def connect_db():
    conn = sqlite3.connect('Users.db')
    c = conn.cursor()

    c.execute("""CREATE TABLE if not exists users (
                    userid text,
                    email text primary key, 
                    first text,
                    last text,
                    password text,
                    account_created text,
                    account_updated integer )                     
    """)

    c.execute("""CREATE TABLE if not exists books (
                    id text primary key,
                    title text,
                    author text,
                    isbn text,
                    published_date text,
                    book_created text,
                    user_id text)
    """)
    conn.commit()


connect_db()


def insert_book(bookid, title, author, isbn, published_date, book_created, userid):
    conn = sqlite3.connect('Users.db')
    c = conn.cursor()
    c.execute("INSERT INTO books VALUES(?,?,?,?,?,?,?)",
              (bookid, title, author, isbn, published_date, book_created, userid))
    conn.commit()


def getbooks():
    conn = sqlite3.connect('Users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM books ")
    return c.fetchall()


def read_book(bookid):
    conn = sqlite3.connect('Users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE id = '{n}'".format(n=bookid))
    return c.fetchone()


def delete_book(id):
    conn = sqlite3.connect('Users.db')
    c = conn.cursor()
    c.execute("DELETE from books WHERE id = :id", {'id': id})
    conn.commit()


def insert_user(userid, email, firstname, lastname, password, account_created):
    conn = sqlite3.connect('Users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?)", (userid, email, firstname, lastname, password, account_created, 0))
    conn.commit()


def update_user(email, firstname, lastname, password, account_updated):
    conn = sqlite3.connect('Users.db')
    c = conn.cursor()

    c.execute("UPDATE users SET first = ?, last = ?, password = ?, account_updated = ? WHERE email = ? ",
              (firstname, lastname, password,account_updated, email))
    conn.commit()
    return True


def get_user(email):
    conn = sqlite3.connect('Users.db')
    c = conn.cursor()
    c.execute(
        "SELECT email, first, last, account_created, account_updated,password, userid FROM users WHERE email = '{n}'".format(
            n=email))
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
