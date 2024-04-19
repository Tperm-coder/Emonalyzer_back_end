from pydantic import BaseModel
from typing import Optional


class UserDbModel(BaseModel):
    username: str
    password: str
    uid: str
    _id: Optional[str] = None