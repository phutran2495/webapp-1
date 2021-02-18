import bcrypt



def encryptpassword(password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed





