import bcrypt
import shortuuid

def generate_id(id_length=10) :
    nano_id = shortuuid.ShortUUID().random(length=id_length)
    return nano_id


def hash_string(password: str) -> str:
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Return the hashed password as a string
    return hashed_password.decode('utf-8')

def compare_strings(plain_password: str, hashed_password: str) -> bool:
    # Check if the plain password matches the hashed password
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))