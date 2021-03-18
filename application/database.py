import mysql.connector
import os

dbendpoint = os.environ.get('dbendpoint')
dbusername = os.environ.get('dbusername')
dbpassword = os.environ.get('dbpassword')


def connect_mysql():
    conn = mysql.connector.connect(
        host=dbendpoint, user=dbusername, password=dbpassword,
    )

    c = conn.cursor()
    c.execute("CREATE DATABASE if not exists CSYE6225")
    conn1 = mysql.connector.connect(
        host=dbendpoint,
        user=dbusername,
        password=dbpassword,
        database="CSYE6225"
    )
    c = conn1.cursor()
    return conn1


def setup_table():
    conn = connect_mysql()
    c = conn.cursor()
    c.execute("""CREATE TABLE if not exists users (
                       userid VARCHAR(255),
                       email VARCHAR(255) PRIMARY KEY, 
                       first VARCHAR(255),
                       last VARCHAR(255),
                       password VARCHAR(255),
                       account_created VARCHAR(255),
                       account_updated VARCHAR(255) )                     
       """)
    conn.commit()
    c.execute("""CREATE TABLE if not exists books (
                        id VARCHAR(255) ,
                        title VARCHAR(255),
                        author VARCHAR(255),
                        isbn VARCHAR(255),
                        published_date VARCHAR(255),
                        book_created VARCHAR(255),
                        user_id VARCHAR(255)
                        )
        """)
    conn.commit()
    c.execute("""CREATE TABLE if not exists images (
                        imageid VARCHAR(255) primary key,
                        bookid VARCHAR(255),
                        s3_object_name VARCHAR(255),
                        user_id VARCHAR(255)
                        )
        """)
    conn.commit()


setup_table()


def validate_bookid_userid(bookid, userid):
    conn = connect_mysql()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM books WHERE id = %s and user_id = %s", (bookid, userid))
        return c.fetchone()
    except:
        return False


def search_object_name(imageid):
    conn = connect_mysql()
    c = conn.cursor()
    c.execute("SELECT s3_object_name FROM images WHERE imageid = %s", (imageid,))
    return c.fetchone()


def delete_object_name(imageid):
    conn = connect_mysql()
    c = conn.cursor()
    c.execute("DELETE FROM images WHERE imageid = %s ", (imageid,))
    conn.commit()

def insert_object_name(imageid, bookid, s3objectname, userid):
    conn = connect_mysql()
    c = conn.cursor()
    c.execute("INSERT INTO images VALUES(%s,%s,%s,%s)", (imageid, bookid, s3objectname, userid))
    conn.commit()


def insert_book(bookid, title, author, isbn, published_date, book_created, userid):
    conn = connect_mysql()
    c = conn.cursor()
    c.execute("INSERT INTO books VALUES(%s,%s,%s,%s,%s,%s,%s)",
              (bookid, title, author, isbn, published_date, book_created, userid)
              )
    conn.commit()


def getbooks():
    conn = connect_mysql()
    c = conn.cursor()
    c.execute("SELECT * FROM books ")
    return c.fetchall()


def read_book(bookid):
    conn = connect_mysql()
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE id = %s ", (bookid,))
    return c.fetchone()


def delete_book(bookid):
    conn = connect_mysql()
    c = conn.cursor()
    c.execute("DELETE from books WHERE id = %s", (bookid,))


delete_book("b93c5492-7d22-11eb-9fde-0433c25d0535")


def insert_user(userid, email, firstname, lastname, password, account_created):
    conn = connect_mysql()
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES(%s,%s,%s,%s,%s,%s,%s)",
              (userid, email, firstname, lastname, password, account_created, 0))
    conn.commit()


def update_user(email, firstname, lastname, password, account_updated):
    conn = connect_mysql()
    c = conn.cursor()

    c.execute("UPDATE users SET first = %s, last = %s, password = %s, account_updated = %s WHERE email = %s ",
              (firstname, lastname, password, account_updated, email))
    conn.commit()
    return True


def get_user(email):
    conn = connect_mysql()
    c = conn.cursor()
    c.execute(
        "SELECT email, first, last, account_created, account_updated,password, userid FROM users WHERE email = %s ",
        (email,))
    return c.fetchone()


def validate_user(email, pw):
    try:
        conn = connect_mysql()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = %s and password = %s ", (email, pw))

        if c.fetchone():
            return True
        else:
            return False
    except:
        return False
