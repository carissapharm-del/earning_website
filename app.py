import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "super_secret_key_for_session"

# Simulated database (in-memory)
# In a big app, you'd use a real database, but this is perfect for scratch!
user_data = {
    "username": "Guest User",
    "balance": 0,
    "referrals": 0,
    "wallet_address": ""
}

@app.route('/')
def home():
    return render_template('index.html', user=user_data)

@app.route('/complete-task', methods=['POST'])
def complete_task():
    # Reward user 5 Naira for a task click
    user_data["balance"] += 5
    flash("🎉 Task completed! You earned ₦5.", "success")
    return redirect(url_for('home'))

@app.route('/withdraw', methods=['POST'])
def withdraw():
    bank = request.form.get('bank')
    account_number = request.form.get('account_number')
    
    if user_data["balance"] < 2000:
        flash(f"❌ Minimum withdrawal is ₦2,000. Your balance is ₦{user_data['balance']}.", "danger")
    elif not account_number or len(account_number) < 10:
        flash("❌ Please enter a valid 10-digit account number.", "danger")
    else:
        flash(f"✅ Withdrawal request of ₦{user_data['balance']} sent successfully to your {bank} account!", "success")
        user_data["balance"] = 0 # Reset balance after cashout
        
    return redirect(url_for('home'))

if __name__ == '__main__':
    # Run the server locally
    app.run(debug=True, port=5000)
