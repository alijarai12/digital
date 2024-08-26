import django

django.setup()
import json
import os
import time
from typing import Optional, Union

from bson import ObjectId, json_util
from django.contrib.auth import get_user_model
from fastapi import FastAPI
from pydantic import BaseModel, Field
from pymongo import MongoClient

from user.models import UserProfile

User = get_user_model()
MONGO_USERNAME = os.environ.get("MONGO_USERNAME", "root")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", "root")
MONGO_HOST = os.environ.get("MONGO_HOST", "mongo")
MONGO_PORT = os.environ.get("MONGO_PORT", "27017")
# UserProfile=get_userprofile_model()

app = FastAPI()

client = MongoClient(
    f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
)

# MONGO_DETAILS = "mongodb://root:root@172.21.0.2:27017"

# client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client["project_data"]


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Project(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


@app.get("/")
def read_root():
    users = User.objects.values("username", "email", "id")
    return [
        {"username": i.get("username"), "email": i.get("email"), "id": i.get("id")}
        for i in users
    ]


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/profile")
def profile():
    users = UserProfile.objects.values("id")
    data = []
    for i in users:
        data.append({"id": i.id})
    return data


@app.get("/ping")
def ping():
    print("Hello")
    time.sleep(5)
    print("bye")
    return {"ping": "pong!"}


@app.get("/test-mongo")
def test_m():
    # m_d=database.project_col.insert_one({"name":"binod"})
    query_data = database.project_col.find()
    # json.dumps(list(m_d))
    # print(database.list_collection_names())
    data_json = json.loads(json_util.dumps(query_data))
    return data_json
