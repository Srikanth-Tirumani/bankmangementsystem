from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong key in production

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                         (username, email, password))
            conn.commit()
            flash("Registered successfully!")
            return redirect('/login')
        except:
            flash("Username already exists!")
        finally:
            conn.close()
    return render_template('bank_app.html', page='register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                            (username, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            flash("Login successful!")
            return redirect('/dashboard')
        else:
            flash("Invalid credentials")
    return render_template('bank_app.html', page='login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template('bank_app.html', page='dashboard', user=user)

@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        trans_type = request.form['type']
        amount = float(request.form['amount'])
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = get_db_connection()
        conn.execute("INSERT INTO transactions (user_id, type, amount, date) VALUES (?, ?, ?, ?)",
                     (session['user_id'], trans_type, amount, date))
        conn.commit()
        conn.close()
        flash('Transaction successful!')
        return redirect('/dashboard')
    return render_template('bank_app.html', page='transaction')

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    history = conn.execute("SELECT * FROM transactions WHERE user_id = ?", 
                           (session['user_id'],)).fetchall()
    conn.close()
    return render_template('bank_app.html', page='history', history=history)

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.")
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
