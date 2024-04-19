from pymongo import MongoClient
from app.models.user import UserDbModel
from app.models.record import RecordDbModel
from app.config.settings import settings

# MongoDB configuration
client = MongoClient(settings.MONGODB_URI)
db = client.get_default_database("Emonalyzer")
print("MONGO DB UP AND RUNNING",client,db)

users_collection = db['users']
records_collection = db['records']

async def get_user_by_username(username: str) -> UserDbModel:
    try :
        user_data = users_collection.find_one({"username": username})
        if user_data:
            return UserDbModel(**user_data)
        return None
    except e:
        print(e)

async def save_user_to_db(user: UserDbModel) -> None:
    try :
        user_dict = user.dict()
        users_collection.insert_one(user_dict)
    except e:
        print(e)

async def add_user_record(user_id:str , record_name:str) -> None:
    record_name = f"{user_id}${record_name}" 
    
    records_collection.insert_one({"record_name":record_name , "user_id" : user_id})
    






