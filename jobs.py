

# Extend Flask backend to support search functionality
from flask import Flask, request, jsonify, render_template
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    password TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
''')

# Insert dummy user (for testing)
cursor.execute('''
INSERT OR IGNORE INTO users (email, full_name, phone, password)
VALUES ('john.doe@example.com', 'John Doe', '+1 (555) 123-4567', 'password123')
''')

conn.commit()
conn.close()



def get_user(email):
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    conn.close()
    return user

@app.route('/get_user', methods=['POST'])
def get_user_data():
    email = request.json.get('email')
    user = get_user(email)
    if user:
        return jsonify({
            "full_name": user["full_name"],
            "email": user["email"],
            "phone": user["phone"],
            "created_at": user["created_at"]
        })
    return jsonify({"error": "User not found"}), 404

@app.route('/update_password', methods=['POST'])
def update_password():
    email = request.json.get('email')
    current_password = request.json.get('current_password')
    new_password = request.json.get('new_password')

    user = get_user(email)
    if user and user["password"] == current_password:  # You should use hashed passwords!
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    return jsonify({"error": "Incorrect current password"}), 400



@app.route('/')
def index():
    return render_template('account.html')




if __name__ == '__main__':
    
    app.run(debug=True)
