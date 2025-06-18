from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import random
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'secretkey'

DB_PATH = 'users.db'

# Initialize DB
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip TEXT,
                        earnings REAL DEFAULT 0,
                        referrals INTEGER DEFAULT 0,
                        last_task_time TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS withdrawals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_ip TEXT,
                        method TEXT,
                        data TEXT,
                        created_at TEXT
                    )''')
        conn.commit()

init_db()

# Utility: get user by IP
def get_user():
    ip = request.remote_addr
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE ip = ?", (ip,))
        user = c.fetchone()
        if not user:
            c.execute("INSERT INTO users (ip) VALUES (?)", (ip,))
            conn.commit()
            c.execute("SELECT * FROM users WHERE ip = ?", (ip,))
            user = c.fetchone()
        return user

@app.route('/')
def index():
    user = get_user()
    return render_template('index.html', user=user)

@app.route('/earn_ad', methods=['POST'])
def earn_ad():
    user = get_user()
    reward = round(random.uniform(0.1, 1.0), 2)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET earnings = earnings + ? WHERE ip = ?", (reward, request.remote_addr))
        conn.commit()
    return jsonify({'success': True, 'reward': reward})

@app.route('/complete_task', methods=['POST'])
def complete_task():
    user = get_user()
    last_task_time = user[4]
    now = datetime.utcnow().isoformat()
    if not last_task_time:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET earnings = earnings + 3, last_task_time = ? WHERE ip = ?", (now, request.remote_addr))
            conn.commit()
        return jsonify({'success': True, 'reward': 3})
    return jsonify({'success': False, 'message': 'Task already completed'})

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == 'POST':
        method = request.form['method']
        data = request.form['data']
        created_at = datetime.utcnow().isoformat()
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO withdrawals (user_ip, method, data, created_at) VALUES (?, ?, ?, ?)",
                      (request.remote_addr, method, data, created_at))
            conn.commit()
        return redirect(url_for('withdraw'))
    return render_template('withdraw.html')

@app.route('/policy')
def policy():
    return render_template('policy.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/referral')
def referral():
    return render_template('referral.html')

@app.route('/dashboard')
def dashboard():
    user = get_user()
    return render_template('dashboard.html', user=user)

@app.route('/api/notifications')
def notifications():
    random_names = ["Ali", "Zara", "Ahmed", "Fatima", "Usman", "Hassan", "Ayesha", "Bilal"]
    name = random.choice(random_names)
    earned_amount = random.choice([70, 120, 150, 210, 320, 400, 499])
    withdrawn_amount = random.choice([500, 1000, 2000, 3000, 4000, 5000])
    return jsonify({
        "name": name,
        "earned": f"${earned_amount}",
        "withdrawn": f"${withdrawn_amount}"
    })

if __name__ == '__main__':
    app.run(debug=True)
