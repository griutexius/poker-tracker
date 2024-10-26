from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'database.db'

# Initialize the database and create tables if not exists
def init_db():
    conn = get_db()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                buy_in INTEGER,
                cash_out INTEGER,
                profit INTEGER,
                session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Route for entering name
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect(url_for('buy_in'))
    return render_template('index.html')

# Route for buy-in and cash-out page
@app.route('/buy_in', methods=['GET', 'POST'])
def buy_in():
    if 'username' not in session:
        return redirect(url_for('index'))
    
    username = session['username']

    if request.method == 'POST':
        buy_in = int(request.form['buy_in'])
        cash_out = int(request.form['cash_out'])
        profit = cash_out - buy_in

        # Insert the session result into the database
        conn = get_db()
        with conn:
            conn.execute('INSERT INTO users (name, buy_in, cash_out, profit) VALUES (?, ?, ?, ?)',
                         (username, buy_in, cash_out, profit))
        
        session['result'] = {
            'buy_in': buy_in,
            'cash_out': cash_out,
            'profit': profit
        }

        return redirect(url_for('result'))

    # Check if there's an existing record for this user
    conn = get_db()
    cur = conn.execute('SELECT buy_in, cash_out, profit FROM users WHERE name = ? ORDER BY session_date DESC LIMIT 1', (username,))
    last_result = cur.fetchone()

    return render_template('buy_in.html', username=username, last_result=last_result)

# Route for displaying results
@app.route('/result')
def result():
    if 'result' not in session:
        return redirect(url_for('index'))
    
    result = session['result']
    username = session['username']

    return render_template('result.html', result=result, username=username)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
