from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)

# Path to the SQLite database
DB_PATH = 'database.db'


# Function to create the database and table if they don't exist
def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT,
                        amount REAL,
                        date TEXT)''')
        conn.commit()
        conn.close()

# Initialize database
init_db()

# Function to get all expenses from the database
def get_expenses():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, category, amount, date FROM expenses ORDER BY date DESC")
    expenses = c.fetchall()
    conn.close()
    return expenses

# Function to add an expense
def add_expense(category, amount, date):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)",
              (category, amount, date))
    conn.commit()
    conn.close()

# Function to delete an expense
def delete_expense(expense_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

# Route for the homepage
@app.route('/')
def index():
    expenses = get_expenses()
    categories = [expense[1] for expense in expenses]
    amounts = [expense[2] for expense in expenses]
    
    # Prepare data for the chart
    category_totals = {}
    for category, amount in zip(categories, amounts):
        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount
    
    chart_data = {
        "labels": list(category_totals.keys()),
        "datasets": [{
            "data": list(category_totals.values()),
            "backgroundColor": ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#ffb3e6"]
        }]
    }
    
    return render_template('index.html', expenses=expenses, chart_data=chart_data)


# Route to add a new expense
@app.route('/add', methods=['POST'])
def add():
    category = request.form['category']
    amount = float(request.form['amount'])
    date = request.form['date']
    add_expense(category, amount, date)
    return redirect(url_for('index'))


# Route to delete an expense
@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete(expense_id):
    delete_expense(expense_id)
    return redirect(url_for('index'))


# API endpoint to fetch expenses in JSON format (for chart update if needed)
@app.route('/api/expenses')
def api_expenses():
    expenses = get_expenses()
    return jsonify(expenses)


if __name__ == '__main__':
    app.run(debug=True)
