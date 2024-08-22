from pymongo import MongoClient
from pymongo.collection import Collection
import os
from dotenv import load_dotenv
load_dotenv()
mongodb_url = os.getenv("MONGODB_URL")
client = MongoClient(mongodb_url)

db = client["notes_db_1"]
user_collection= db["users"]
notes_collection= db["notes"]

def get_expense_collection()->Collection:
    return db["expenses"]
def get_transaction_collection()->Collection:
    return db["transactions"]

def get_current_stocks_collection()->Collection:
    return db["current_stocks"]

def get_purchase_collection()->Collection:
    return db["buyed_stocks"]

def get_sold_collection()->Collection:
    return db["sold_stocks"]

def get_stock_data_collection()->Collection:
    return db["stock_data"]