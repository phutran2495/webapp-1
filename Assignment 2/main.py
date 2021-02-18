import datetime as dt
from pydantic import BaseModel
from database import insert_user, get_user, insert_book, read_book, delete_book, getbooks
from EncryptPW import encryptpassword
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, FastAPI, HTTPException, status
import re
import sqlite3
import bcrypt
import uvicorn
import uuid

app = FastAPI()
security = HTTPBasic()

regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
pwregex = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$")


class User(BaseModel):
    email: str
    password: str
    firstname: str
    lastname: str


class UserInfo(BaseModel):
    email: str
    firstname: str
    lastname: str
    account_created: str
    account_updated: str


class UpdateUser(BaseModel):
    firstname: str
    lastname: str
    password: str


class BookInput(BaseModel):
    title: str
    author: str
    isbn: str
    published_date: str


def validateCredential(credentials: HTTPBasicCredentials = Depends(security)):
    try:
        user_info = get_user(credentials.username)
        hashedPassword = user_info[5]
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail= 'invalid credentials'
        )

    if not bcrypt.checkpw(credentials.password.encode(), hashedPassword):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user_info


@app.delete("/books/{id}")
def delete_book(id:str ):
    if not id:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail='N0 Content'
        )
    try:
        conn = sqlite3.connect('Users.db')
        c = conn.cursor()
        c.execute("DELETE from books WHERE id = :id", {'id': id})
        conn.commit()
        return "Successful deletion "
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Not Found'
        )


@app.get("/books/{id}")
def get_book(id:str,user_info=Depends(validateCredential)):
    try:
        book = read_book(id)
        return {"id": book[0],
                "title": book[1],
                "author": book[2],
                "isbn": book[3],
                "published_date": book[4],
                "book_created": book[5],
                "user_id": book[6]}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= "Invalid book id"
        )



@app.post("/books")
def create_book(book_info: BookInput, user_info=Depends(validateCredential)):
    bookid = str(uuid.uuid1())
    book_created = dt.datetime.now()
    user_id = user_info[-1]
    print(user_info)
    try:
        insert_book(bookid, book_info.title, book_info.author, book_info.isbn,
                    book_info.published_date, book_created, user_id)
        return {"id": bookid,
                "title": book_info.title,
                "author": book_info.author,
                "isbn": book_info.isbn,
                "published_date": book_info.published_date,
                "book_created": book_created,
                "user_id": user_id}
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already exists'
        )


@app.get("/user/self")  # protected
def read_user(credentials: HTTPBasicCredentials = Depends(security)):
    try:
        user_info = get_user(credentials.username)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST
        )
    print(user_info)
    hashed_password = user_info[5]
    password = credentials.password.encode()
    if bcrypt.checkpw(password, hashed_password):
        return {'email': user_info[0],
                'firstname': user_info[1],
                'lastname': user_info[2],
                'account_created': user_info[3],
                'account_updated': user_info[4],
                'user_id': user_info[6]
                }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST
        )


@app.put("/user/self")  # protected
def update_user(updatedInput: UpdateUser, credentials: HTTPBasicCredentials = Depends(security)):
    try:
        user_info = get_user(credentials.username)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST
        )

    conn = sqlite3.connect('Users.db')
    c = conn.cursor()
    password = encryptpassword(updatedInput.password)
    c.execute(
        "UPDATE users SET first = ?, last = ?, password = ?, account_updated = ? WHERE email = ? ",
        (updatedInput.firstname, updatedInput.lastname, password, dt.datetime.now(), credentials.username))
    conn.commit()
    updatedUser= get_user(credentials.username)

    return {
        "id" : updatedUser[-1],
        "first_name":updatedUser[1] ,
        "last_name": updatedUser[2] ,
        "username":  updatedUser[0] ,
        "account_created": updatedUser[3],
        "account_updated" :updatedUser[4]
    }


@app.get("/books")
def get_books():
    result = []
    try:
        books = getbooks()
        for book in books:
            book = {
                "id": book[0],
                "title": book[1],
                "author": book[2],
                "isbn": book[3],
                "published_date": book[4],
                "book_created": book[5],
                "user_id": book[6]
            }
            result.append(book)
        return result
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST
        )

@app.post("/createuser")  # public
def create_account(user: User):
    userid = uuid.uuid1()
    now = dt.datetime.now()
    pwd = encryptpassword(user.password)
    if not re.search(regex, user.email):
        return "invalid email"
    if not re.search(pwregex, user.password):
        return "weak password"

    try:
        insert_user(str(userid), user.email, user.firstname, user.lastname, pwd, now)
        return "success"
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
