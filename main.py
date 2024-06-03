from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()
enviroment = os.getenv('enviroment')

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World from "+ enviroment}