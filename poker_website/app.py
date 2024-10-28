from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database connection function
def get_db_connection():
    conn = sqlite3.connect("poker_website/database.db")  # Make sure this path is correct
    conn.row_factory = sqlite3.Row
    return conn

# Home route to display the latest session result
@app.route('/home')
def home():
    if 'user_id' not in session:
        flash("Please log in to access this page.")
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    latest_session = conn.execute('SELECT * FROM sessions WHERE user_id = ? ORDER BY id DESC LIMIT 1',
                                  (session['user_id'],)).fetchone()
    conn.close()
    
    return render_template('home.html', username=session['username'], latest_session=latest_session)

# Route to handle new session entry
@app.route('/new_session', methods=['GET', 'POST'])
def new_session():
    if request.method == 'POST':
        buy_in = float(request.form['buy_in'])
        cash_out = float(request.form['cash_out'])
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_id = session['user_id']

        conn = get_db_connection()
        conn.execute('INSERT INTO sessions (user_id, date, buy_in, cash_out) VALUES (?, ?, ?, ?)',
                     (user_id, date, buy_in, cash_out))
        conn.commit()
        conn.close()
        return redirect(url_for('results'))
    
    return render_template('new_session.html')

@app.route('/all_sessions')
def all_sessions():
    if 'user_id' not in session:
        flash("Please log in to access this page.")
        return redirect(url_for('login'))
    conn = get_db_connection()
    sessions = conn.execute('SELECT * FROM sessions WHERE user_id = ? ORDER BY date DESC',
                            (session['user_id'],)).fetchall()
    conn.close()
    return render_template('all_sessions.html', sessions=sessions)

# Route to show results with profit or loss
@app.route('/results')
def results():
    conn = get_db_connection()
    session_data = conn.execute('SELECT * FROM sessions WHERE user_id = ? ORDER BY id DESC LIMIT 1',
                                (session['user_id'],)).fetchone()
    conn.close()

    if session_data:
        profit_or_loss = session_data['cash_out'] - session_data['buy_in']
    else:
        profit_or_loss = None

    return render_template('results.html', session_data=session_data, profit_or_loss=profit_or_loss)

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
            conn.commit()
            flash("Registration successful! Please log in.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists.")
        finally:
            conn.close()
    
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Logged in successfully!")
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password.")
    
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

# Debug mode activated here
if __name__ == "__main__":
    app.run(debug=True)
