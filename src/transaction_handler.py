# src/transaction_handler.py
from .db_handler import add_transaction, get_all_transactions, get_filtered_transactions

# Logic for adding a transaction (from user input)
def handle_add_transaction(date, description, amount, category):
    add_transaction(date, description, amount, category)

# Logic to get all transactions
def handle_get_all_transactions():
    return get_all_transactions()

# Logic to get filtered transactions
def handle_get_filtered_transactions(filters):
    return get_filtered_transactions(filters)
