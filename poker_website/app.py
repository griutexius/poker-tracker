from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Route for the enter name page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect(url_for('buy_in'))
    return render_template('index.html')

# Route for the buy-in page
@app.route('/buy_in', methods=['GET', 'POST'])
def buy_in():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        buy_in_amount = request.form['buy_in']
        session['buy_in'] = buy_in_amount
        return redirect(url_for('result'))
    
    username = session['username']
    return render_template('buy_in.html', username=username)

# Route for the result (cash-out) page
@app.route('/result', methods=['GET', 'POST'])
def result():
    if 'username' not in session or 'buy_in' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        cash_out_amount = request.form['cash_out']
        session['cash_out'] = cash_out_amount
        
        buy_in = float(session['buy_in'])
        cash_out = float(cash_out_amount)
        profit = cash_out - buy_in
        
        return render_template('result.html', username=session['username'], buy_in=buy_in, cash_out=cash_out, profit=profit)
    
    return render_template('result.html', username=session['username'], buy_in=session['buy_in'])

if __name__ == '__main__':
    app.run(debug=True)
