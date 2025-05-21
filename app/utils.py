from passlib.context import CryptContext


pwd_context = CryptContext(schemes = ["bcrypt"], deprecated ="auto")

##helper to hash passwords
def hash(password: str):
    return pwd_context.hash(password)

