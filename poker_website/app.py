from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# Route to show registration form and handle form submission
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        
        conn = get_db_connection()
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        conn.close()

        flash("Registration successful. Please log in.")
        return redirect(url_for('login'))
    return render_template('register.html')

# Route to show login form and handle login submission
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Logged in successfully!")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials. Please try again.")
    return render_template('login.html')

# Home route (only accessible when logged in)
@app.route('/home')
def home():
    if 'user_id' not in session:
        flash("Please log in to access this page.")
        return redirect(url_for('login'))
    return render_template('home.html', username=session['username'])

# Route to log out
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for('login'))

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
