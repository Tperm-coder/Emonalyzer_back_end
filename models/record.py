from pydantic import BaseModel

class RecordDbModel(BaseModel):
    ownerId: str
    recordName: str
