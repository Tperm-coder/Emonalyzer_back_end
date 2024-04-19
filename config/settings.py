import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    def __init__(self):
        # MongoDB connection settings
        self.MONGODB_URI = os.getenv("MONGODB_URI")

        # JWT configuration
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        self.JWT_ALGORITHM = "HS256"
        self.JWT_EXPIRATION_TIME_MINUTES = 60

        # Password hashing configuration
        self.PASSWORD_SALT = os.getenv("PASSWORD_SALT")
        self.TOKEN_EXPIRATION = os.getenv("TOKEN_EXPIRATION_IN_MIN")

        self.UPLOADS_PATH = os.getenv("UPLOADS_PATH")
        self.MODEL_PATH = os.getenv("MODEL_PATH")


settings = Settings()
