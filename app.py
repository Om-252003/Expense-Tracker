from flask import Flask, request, render_template, send_file, jsonify
from flask_pymongo import PyMongo
import csv
from io import StringIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/Expense-Tracker"  # Your MongoDB URI
mongo = PyMongo(app)


@app.route('/')
def home():
    return render_template('index.html')

# Route to add a transaction (simplified)
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.form
    mongo.db.transactions.insert_one({
        "Date": data["date"],
        "Description": data["description"],
        "Amount": float(data["amount"]),
        "Category": data["category"]
    })
    return jsonify({"message": "Transaction added successfully!"})


# Route for exporting as CSV
@app.route('/export_csv')
def export_csv():
    category = request.args.get('category', 'All')
    min_amount = float(request.args.get('min_amount', 0))
    max_amount = float(request.args.get('max_amount', 1000000))
    start_date = request.args.get('start_date', '1970-01-01')
    end_date = request.args.get('end_date', '9999-12-31')

    query = {"Amount": {"$gte": min_amount, "$lte": max_amount}}
    if category != 'All':
        query["Category"] = category
    if start_date:
        query["Date"] = {"$gte": start_date}
    if end_date:
        query["Date"] = {"$lte": end_date}

    transactions = mongo.db.transactions.find(query)

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Description', 'Amount', 'Category'])

    for transaction in transactions:
        writer.writerow(
            [transaction['Date'], transaction['Description'], transaction['Amount'], transaction['Category']])

    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name="transactions.csv")


# Route for exporting as PDF
@app.route('/export_pdf')
def export_pdf():
    category = request.args.get('category', 'All')
    min_amount = float(request.args.get('min_amount', 0))
    max_amount = float(request.args.get('max_amount', 1000000))
    start_date = request.args.get('start_date', '1970-01-01')
    end_date = request.args.get('end_date', '9999-12-31')

    query = {"Amount": {"$gte": min_amount, "$lte": max_amount}}
    if category != 'All':
        query["Category"] = category
    if start_date:
        query["Date"] = {"$gte": start_date}
    if end_date:
        query["Date"] = {"$lte": end_date}

    transactions = mongo.db.transactions.find(query)

    output = StringIO()
    pdf = canvas.Canvas(output, pagesize=letter)
    pdf.setFont("Helvetica", 12)

    pdf.drawString(250, 770, "ExpenseTracker Report")
    y_position = 750
    pdf.drawString(30, y_position, "Date")
    pdf.drawString(150, y_position, "Description")
    pdf.drawString(300, y_position, "Amount")
    pdf.drawString(450, y_position, "Category")
    y_position -= 20

    for transaction in transactions:
        pdf.drawString(30, y_position, transaction['Date'])
        pdf.drawString(150, y_position, transaction['Description'])
        pdf.drawString(300, y_position, str(transaction['Amount']))
        pdf.drawString(450, y_position, transaction['Category'])
        y_position -= 20

    pdf.showPage()
    pdf.save()

    output.seek(0)
    return send_file(output, mimetype='application/pdf', as_attachment=True, download_name="transactions.pdf")


@app.route('/transaction_summary')
def transaction_summary():
    category = request.args.get('category', 'All')
    min_amount = float(request.args.get('min_amount', 0))
    max_amount = float(request.args.get('max_amount', 1000000))
    start_date = request.args.get('start_date', '1970-01-01')
    end_date = request.args.get('end_date', '9999-12-31')

    # Construct the query based on filters
    query = {"Amount": {"$gte": min_amount, "$lte": max_amount}}
    if category != 'All':
        query["Category"] = category
    if start_date:
        query["Date"] = {"$gte": start_date}
    if end_date:
        query["Date"] = {"$lte": end_date}

    # Get transactions from the database
    transactions = mongo.db.transactions.find(query)

    # Initialize totals for income, expenses, and balance
    total_income = 0
    total_expense = 0

    # Iterate through transactions and calculate totals
    for transaction in transactions:
        if transaction['Category'] == 'Income':
            total_income += transaction['Amount']
        elif transaction['Category'] == 'Expense':
            total_expense += transaction['Amount']

    # Calculate balance
    balance = total_income - total_expense

    summary = {
        "Total Income": total_income,
        "Total Expense": total_expense,
        "Balance": balance
    }

    return jsonify(summary)


if __name__ == '__main__':
    app.run(debug=True)
