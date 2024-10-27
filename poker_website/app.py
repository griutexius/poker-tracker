from flask import Flask, render_template, request
from openpyxl import load_workbook
import os

app = Flask(__name__)

# Route to the home page where user inputs their name
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        return render_template("buy_in.html", username=username)
    return render_template("index.html")

# Route to handle buy-in and cash-out input
@app.route("/buy_in", methods=["POST"])
def buy_in():
    username = request.form["username"]
    buy_in_amount = float(request.form["buy_in"])
    cash_out_amount = float(request.form["cash_out"])
    result = cash_out_amount - buy_in_amount
    log_to_excel(username, buy_in_amount, cash_out_amount, result)
    return render_template("result.html", username=username, buy_in=buy_in_amount, cash_out=cash_out_amount, result=result)

# Function to log data into Excel
def log_to_excel(username, buy_in, cash_out, result):
    # Load or create an Excel file
    file_path = "poker_sessions.xlsx"
    if os.path.exists(file_path):
        workbook = load_workbook(file_path)
        sheet = workbook.active
    else:
        from openpyxl import Workbook
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(["Username", "Buy In (€)", "Cash Out (€)", "Result (€)"])  # Add headers if creating new file

    # Append session data
    sheet.append([username, buy_in, cash_out, result])

    # Save the workbook
    workbook.save(file_path)

# Ensures that the Flask app runs only when this script is executed directly
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)