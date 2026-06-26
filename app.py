import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_key_for_session")

# Secure absolute path for Render's environment
DATABASE = '/tmp/database.db'
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            balance REAL DEFAULT 0.0,
            referrals INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    return render_template('index.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash("❌ All fields are required.", "danger")
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password, method='scrypt')
        
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            conn.close()
            flash("🎉 Account created successfully! Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("❌ Username already used. Please choose another one.", "danger")
            return redirect(url_for('register'))
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            flash("❌ Invalid username or password.", "danger")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("🔒 Logged out successfully.", "success")
    return redirect(url_for('login'))

@app.route('/complete-task', methods=['POST'])
def complete_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    conn.execute('UPDATE users SET balance = balance + 5 WHERE id = ?', (session['user_id'],))
    conn.commit()
    conn.close()
    
    flash("🎉 Task completed! You earned ₦5.", "success")
    return redirect(url_for('home'))

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    bank = request.form.get('bank')
    account_number = request.form.get('account_number')
    
    conn = get_db_connection()
    user = conn.execute('SELECT balance FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if user['balance'] < 2000:
        flash(f"❌ Minimum withdrawal is ₦2,000. Your balance is ₦{user['balance']}.", "danger")
        conn.close()
    elif not account_number or len(account_number) < 10:
        flash("❌ Please enter a valid 10-digit account number.", "danger")
        conn.close()
    else:
        conn.execute('UPDATE users SET balance = 0 WHERE id = ?', (session['user_id'],))
        conn.commit()
        conn.close()
        flash(f"✅ Withdrawal request of ₦{user['balance']} sent successfully to your {bank} account!", "success")
        
    return redirect(url_for('home'))

# Master Control Panel Route
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    # Security checkpoint: Only allow 'emmanuel'
    if session['username'] != 'emmanuel':
        flash("⛔ Access Denied: Admins only.", "danger")
        return redirect(url_for('home'))
        
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, balance, referrals FROM users').fetchall()
    conn.close()
    
    return render_template('admin.html', users=users)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
