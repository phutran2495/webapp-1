import datetime as dt
from pydantic import BaseModel
from base64 import b64decode
from database import update_user, insert_user, get_user, validate_user
from EncryptPW import encryptpassword
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, FastAPI, HTTPException, status, Header
import re
import sqlite3
import bcrypt

app = FastAPI()
security = HTTPBasic()

regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
pwregex = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$")

def validatePassword(password):
    pwregex = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$")
    if not re.search(pwregex, password):
        return "weak password"
    return "ok"

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


@app.get("/user/self", response_model=UserInfo)  # protected
def read_user(credentials: HTTPBasicCredentials = Depends(security)):
    try:
        user_info = get_user(credentials.username)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST
        )

    hashed_password = user_info[5]
    password = credentials.password.encode()
    if bcrypt.checkpw(password, hashed_password):
        return {'email': user_info[0],
                'firstname': user_info[1],
                'lastname': user_info[2],
                'account_created': user_info[3],
                'account_updated': user_info[4]}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST
        )


@app.put("/user/self")  # protected
def update_user(firstname: str, lastname: str, password: str, credentials: HTTPBasicCredentials = Depends(security)):
    try:
        user_info = get_user(credentials.username)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST
        )

    conn = sqlite3.connect('Users.db')
    c = conn.cursor()
    password = encryptpassword(password)
    c.execute("UPDATE users SET first = ?, last = ?, password = ?, account_updated = 1 WHERE email = ? ",
              (firstname, lastname, password, credentials.username))
    conn.commit()
    return "Success"


@app.post("/createuser")  # public
def create_account(user: User):
    now = dt.datetime.now()
    pwd = encryptpassword(user.password)
    if not re.search(regex, user.email):
        return "invalid email"
    if not re.search(pwregex, user.password):
        return "weak password"

    try:
        insert_user(user.email, user.firstname, user.lastname, pwd, now)
        return "success"
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST
        )
