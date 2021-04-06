import datetime as dt
from pydantic import BaseModel
from database import validate_bookid_userid,insert_object_name,delete_object_name,search_object_name,connect_mysql, insert_user, get_user, update_user, insert_book, read_book, delete_book, getbooks
from EncryptPW import encryptpassword
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, FastAPI, HTTPException, status, File, UploadFile
import re
import bcrypt
import uvicorn
import uuid
from statsd import StatsClient
from S3 import upload_file, delete_file
import logging
import boto3
from sns_utility import SNSWrapper


logging.basicConfig(filename="/home/ubuntu/csye6225.log", level=logging.INFO)
logger = logging.getLogger()
statsd_client = StatsClient('localhost', 8125)
app = FastAPI()
security = HTTPBasic()

sns_client = boto3.client('sns')
sns_wrapper = SNSWrapper(client)


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
            detail='invalid credentials'
        )

    if not bcrypt.checkpw(credentials.password.encode('utf8'), hashedPassword.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user_info


@app.post("/book/{book_id}/image")
def add_book_images_by_bookid(book_id: str, file: UploadFile = File(...), user_info=Depends(validateCredential)):
    logger.info("a user has accessed add_book_images_by_bookid endpoint")
    pipe = statsd_client.pipeline()
    pipe.incr('add_book_image_counts')
    pipe.send()

    with statsd_client.timer('add_book_images_api_timer'):
        if not validate_bookid_userid(book_id,user_info[6]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="book id does not match with your account"
            )

        contents = file.file.read()
        image_id = str(uuid.uuid1())
        objectname = book_id + '/' + image_id + "/" + file.filename
        with statsd_client.timer('s3_bucket_timer'):
            response = upload_file(contents,'webapp.phu.tran',objectname)

        insert_object_name( image_id, book_id, objectname, user_info[6])
        if response:
            return {"filename": file.filename,
                    "s3_object_name": objectname,
                    "image_id": image_id,
                    "created_date": dt.datetime.now(),
                    "user_id": user_info[6]}


@app.delete("/book/{book_id}/image/{image_id}")
def delete_image(book_id: str, image_id: str, user_info=Depends(validateCredential)):
    logger.info("a user has accessed delete_image endpoint")
    pipe = statsd_client.pipeline()
    pipe.incr('delete_image_counts')
    pipe.send()

    if not validate_bookid_userid(book_id, user_info[6]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="book id does not match with your account"
        )

    try:
        objectname = search_object_name(image_id)[-1]
        delete_object_name(imageid=image_id)
        if delete_file('webapp.phu.tran', objectname):
            return "deleted"
    except:
        return "cannt find the book"



@app.delete("/books/{id}")
def delete_book(id: str, user_info=Depends(validateCredential)):
    logger.info("a user has accessed delete_book endpoint")
    pipe = statsd_client.pipeline()
    pipe.incr('delete_book_counts')
    pipe.send()
    bookid = id
    # useremail = user_info[0]

    # sns_message = {
    # 'recipient': useremail,
    # 'message': 'You have deleted a book. Book id: ' + bookid + '\n ' + 'Book link: ' + "prod.phutran.me/book/" + bookid
    # }
    # sns_wrapper.publish_message(topic_arn="arn:aws:sns:us-east-1:709891834787:book_api_topic", message=sns_message)


    try:
        conn = connect_mysql()
        c = conn.cursor()
        c.execute("DELETE from books WHERE id = %s", (id,))
        conn.commit()
        return f"Successfully delete {id} "
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Not Found'
        )


@app.get("/book/{id}")
def get_book(id: str, user_info=Depends(validateCredential)):
    logger.info("a user has accessed get_book endpoint")
    pipe = statsd_client.pipeline()
    pipe.incr('get_book_counts')
    pipe.send()



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
            detail="Invalid book id"
        )


@app.post("/book")
def create_book(book_info: BookInput, user_info=Depends(validateCredential)):
    logger.info("a user has accessed create_book endpoint")
    pipe = statsd_client.pipeline()
    pipe.incr('create_book_counts')
    pipe.send()
    bookid = str(uuid.uuid1())
    book_created = dt.datetime.now()
    user_id = user_info[-1]
    # useremail = user_info[0]

    # sns_message = {
    # 'recipient': useremail,
    # 'message': 'You have created a book. Book id: ' + bookid + '\n ' + 'Book link: ' + "prod.phutran.me/book/" + bookid
    # }
    # sns_wrapper.publish_message(topic_arn="arn:aws:sns:us-east-1:709891834787:book_api_topic", message=sns_message)

    with statsd_client.timer('create_book_api_timer'):

        try:
            insert_book(bookid, book_info.title, book_info.author, book_info.isbn,
                        book_info.published_date, str(book_created), user_id)
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
                detail='something wrong with create the book'
            )


@app.get("/user/self")  # protected
def read_user(credentials: HTTPBasicCredentials = Depends(security)):
    logger.info("a user has accessed read_user account")
    pipe = statsd_client.pipeline()
    pipe.incr('read_user_counts')
    pipe.send()

    with statsd_client.timer('read_user_api_timer'):
        try:
            user_info = get_user(credentials.username)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST
            )
        print(user_info)
        hashed_password = user_info[5]
        password = credentials.password.encode('utf8')
        print(type(password))
        if bcrypt.checkpw(password, hashed_password.encode()):
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
def update_user_account(updatedInput: UpdateUser, credentials: HTTPBasicCredentials = Depends(security)):
    logger.info("a user has accessed update_user_account endpoint")
    pipe = statsd_client.pipeline()
    pipe.incr('update_user_account_count')
    pipe.send()

    try:
        user_info = get_user(credentials.username)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST
        )
    password = encryptpassword(updatedInput.password)
    update_user(updatedInput.firstname, updatedInput.lastname, password, dt.datetime.now(), credentials.username)
    updatedUser = get_user(credentials.username)
    return {
        "id": updatedUser[-1],
        "first_name": updatedUser[1],
        "last_name": updatedUser[2],
        "username": updatedUser[0],
        "account_created": updatedUser[3],
        "account_updated": updatedUser[4]
    }


@app.get("/books")  #public
def get_books():
    logger.info("a user has accessed get_books endpoint")
    result = []
    
    with statsd_client.timer('get_all_books_api_timer'):
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
            pipe = statsd_client.pipeline()
            pipe.incr('get_books_counts')
            pipe.send()
            return result
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST
            )


@app.post("/createuser")  # public
def create_account(user: User):
    logger.info("a user has accessed create_account endpoint")
    pipe = statsd_client.pipeline()
    pipe.incr('create_user_counts')
    pipe.send()

    with statsd_client.timer('create_user_api_timer'):
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
