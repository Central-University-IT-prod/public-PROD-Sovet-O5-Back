"""Client for MongoDB connection"""
from os import getenv
import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

client = MongoClient(getenv("MONGO_CONNECTION"))
db = client[getenv("DB_DATABASE")]

users = db["users"]
positions = db["positions"]
teams = db["teams"]
reactions = db["reactions"]
counters = db["counters"] # internal collection for autoincrementing
adminsIDS = db["adminsIDS"]
specialData = db["specialData"]
reactions = db["reactions"]
constraints = db["constraints"]
skills = db["skills"]


def insert_one_with_id(collection: Collection, document: dict, inc_value: int = 1) -> int:
    """
    Insert one document with autoincremented ID
    """
    while True:
        try:
            document["_id"] = counters.find_one_and_update(
                {"_id": collection.name},
                {"$inc": {"seq": inc_value}},
                upsert=True,
                return_document=True
            )["seq"]
            collection.insert_one(document)
            return document["_id"]
        except DuplicateKeyError:
            continue
