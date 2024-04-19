from fastapi import APIRouter, HTTPException, Depends, status , Request , File , UploadFile

from app.models.user import UserDbModel
from app.models.response import Response
from app.config.settings import settings
from app.prediction_model.prediction_model import pretrainedModel

import app.db.users as userDb
import app.utils.helper_functions as helperFunctions 
import app.dependencies.auth as authDeps

from pydub import AudioSegment
from struct import pack, unpack

import shutil
import subprocess
import wave
import os

router = APIRouter()

    
@router.post("/register",response_model=Response)
async def register(request:Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Data isn't valid")

    # Check if username already exists
    existing_user = await userDb.get_user_by_username(username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    # Hash password before saving
    hashed_password = helperFunctions.hash_string(password)
    password = hashed_password

    uid = helperFunctions.generate_id(30)
    
    # Save user to database 
    new_user = UserDbModel(username=username , password=password , uid=uid)
    print("------------->")
    await userDb.save_user_to_db(new_user)

    return {"msg" : "Success" , "state" : True , "data" : { "user_name" : username , "user_id" : uid}}

@router.post("/login" , response_model=Response)
async def login(request:Request):

    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    existing_user = await userDb.get_user_by_username(username)

    if not existing_user or not helperFunctions.compare_strings(password, existing_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    # Generate JWT token
    token = authDeps.create_access_token(data={"name": existing_user.username , "id" : existing_user.uid })
    return {"msg" : "Success" , "state" : True , "data" :  {"access_token": token, "token_type": "bearer"}}


def fix_corrupted_audio(input_file, output_file):
    try:
        wav_header = "4si4s4sihhiihh4si"
        f = open(input_file, 'rb+')
        data = list(unpack(wav_header,f.read(44)))
        assert data[0]=='RIFF'
        assert data[2]=='WAVE'
        assert data[3]=='fmt '
        assert data[4]==16
        assert data[-2]=='data'
        assert data[1]==data[-1]+36

        f.seek(0,2)
        filesize = f.tell()
        datasize = filesize - 44

        data[-1] = datasize
        data[1]  = datasize+36

        f.seek(0)
        f.write(pack(wav_header, *data))
        f.close()
    except Exception as e:
        print(f"Error fixing audio: {e}")


@router.post("/upload_audio/")
async def upload_audio(file: UploadFile = File(...)):

    # Create a directory to store the uploaded audio files if it does not exist
    upload_folder = settings.UPLOADS_PATH
    if not os.path.exists(upload_folder):
        print("path didn't exits")
        os.makedirs(upload_folder)

    # Create a file path to save the uploaded audio file

    file_path = os.path.join(upload_folder, file.filename)

    # Save the uploaded audio file locally
    with open(file_path, "wb") as buffer:
        print(file.file)
        content = await file.read()  # Read the file content
        buffer.write(content)

        # Usage
    # fix_corrupted_audio(file_path, os.path.join(upload_folder, "fixed.wav"))

    
    await userDb.add_user_record(user_id="13456123456",record_name=file.filename)
    predictions = pretrainedModel.predict(file_path=file_path)

    return {"filename": file.filename, "predictions": "sdf"}
    
    