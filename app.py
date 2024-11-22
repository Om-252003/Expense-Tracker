import json

from flask import send_file, jsonify
from flask_pymongo import PyMongo
import csv
from io import StringIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/Expense-Tracker"  # Your MongoDB URI
mongo = PyMongo(app)


# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client["Expense-Tracker"]
collection = db["transactions"]

@app.route('/')
def home():
    return render_template('landing.html')

@app.route("/add_transaction", methods=["GET", "POST"])
def add_transaction():
    if request.method == "POST":
        date = request.form["date"]
        description = request.form["description"]
        amount = float(request.form["amount"])  # Ensure the amount is a float
        category = request.form["category"]

        # Insert the data into MongoDB
        collection.insert_one({
            "Date": date,
            "Description": description,
            "Amount": amount,
            "Category": category
        })

        return redirect(url_for("add_transaction"))  # Redirect after successful insert
    return render_template("add_transaction.html")  # Display the form for GET request


@app.route('/view_report', methods=['GET', 'POST'])
def view_report():
    # Get filter parameters from either GET or POST request
    start_date = request.args.get('start_date') or request.form.get('start_date')
    end_date = request.args.get('end_date') or request.form.get('end_date')
    category = request.args.get('category') or request.form.get('category', 'All')
    min_amount = request.args.get('min_amount') or request.form.get('min_amount', '0')
    max_amount = request.args.get('max_amount') or request.form.get('max_amount')

    # Build the query
    query = {}
    if start_date:
        query['Date'] = {'$gte': start_date}
    if end_date:
        if 'Date' in query:
            query['Date']['$lte'] = end_date
        else:
            query['Date'] = {'$lte': end_date}
    if category and category != 'All':
        query['Category'] = category
    if min_amount:
        query['Amount'] = {'$gte': float(min_amount)}
    if max_amount:
        if 'Amount' in query:
            query['Amount']['$lte'] = float(max_amount)
        else:
            query['Amount'] = {'$lte': float(max_amount)}

    # Fetch transactions
    transactions = list(collection.find(query))

    # Calculate totals
    total_income = sum(t['Amount'] for t in transactions if t['Category'] == 'Income')
    total_expense = sum(t['Amount'] for t in transactions if t['Category'] == 'Expense')
    balance = total_income - total_expense

    # Prepare chart data
    bar_chart_data = {}
    for t in transactions:
        date = t['Date']
        if date in bar_chart_data:
            if t['Category'] == 'Income':
                bar_chart_data[date] += t['Amount']
            else:
                bar_chart_data[date] -= t['Amount']
        else:
            if t['Category'] == 'Income':
                bar_chart_data[date] = t['Amount']
            else:
                bar_chart_data[date] = -t['Amount']

    # Sort dates for consistent display
    sorted_dates = sorted(bar_chart_data.keys())
    bar_chart_labels = sorted_dates
    bar_chart_values = [bar_chart_data[date] for date in sorted_dates]

    return render_template(
        'view_report.html',
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        bar_chart_labels=json.dumps(bar_chart_labels),
        bar_chart_values=json.dumps(bar_chart_values),
        pie_chart_data=json.dumps([total_income, total_expense])
    )



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
