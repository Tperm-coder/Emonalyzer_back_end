from fastapi import FastAPI
from app.routers import users
from app.mws.mws import inject_middlewares
from app.config.settings import settings
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

server = FastAPI()

# Configure CORS
origins = [
    "http://localhost:5173",
     "*",
]

server.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_server():
    inject_middlewares(server);
    server.include_router(users.router) 


init_server()