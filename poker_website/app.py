from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for the buy-in page, triggered when the form on the index page is submitted
@app.route('/buy_in', methods=['POST'])
def buy_in():
    username = request.form.get('username')
    if username:
        # Render the buy_in.html template with the username
        return render_template('buy_in.html', username=username)
    else:
        # Redirect back to the index page if no username is provided
        return redirect(url_for('index'))

# Ensures that the Flask app runs only when this script is executed directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
