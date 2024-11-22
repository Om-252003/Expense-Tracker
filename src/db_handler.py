# src/db_handler.py
from pymongo import MongoClient
from .config import MONGO_URI, DB_NAME

# Create MongoDB client and connect to the database
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
transactions = db["transactions"]

# Function to add a transaction
def add_transaction(date, description, amount, category):
    transaction = {
        "Date": date,
        "Description": description,
        "Amount": amount,
        "Category": category,  # 'Income' or 'Expense'
    }
    transactions.insert_one(transaction)

# Function to get all transactions
def get_all_transactions():
    return list(transactions.find())

# Function to get filtered transactions
def get_filtered_transactions(filters):
    query = {}
    if filters.get("category"):
        query["Category"] = filters["category"]
    if filters.get("min_amount"):
        query["Amount"] = {"$gte": filters["min_amount"]}
    if filters.get("max_amount"):
        query["Amount"] = {"$lte": filters["max_amount"]}
    if filters.get("start_date"):
        query["Date"] = {"$gte": filters["start_date"]}
    if filters.get("end_date"):
        query["Date"] = {"$lte": filters["end_date"]}
    return list(transactions.find(query))
