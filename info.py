


# Extend Flask backend to support search functionality
from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT NOT NULL,
                    job_type TEXT NOT NULL,
                    salary TEXT,
                    skills TEXT,
                    description TEXT
                )''')
    conn.commit()
    conn.close()

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    query = request.args.get('q', '').strip()
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    if query:
        c.execute('''SELECT * FROM jobs WHERE 
                        title LIKE ? OR 
                        company LIKE ? OR 
                        location LIKE ? OR 
                        job_type LIKE ? OR 
                        salary LIKE ? OR 
                        skills LIKE ? OR 
                        description LIKE ?''',
                  tuple([f"%{query}%"] * 7))
    else:
        c.execute('SELECT * FROM jobs')
    jobs = [dict(id=row[0], title=row[1], company=row[2], location=row[3],
                 job_type=row[4], salary=row[5], skills=row[6], description=row[7])
            for row in c.fetchall()]
    conn.close()
    return jsonify(jobs)

@app.route('/api/jobs', methods=['POST'])
def add_job():
    data = request.get_json()
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute('''INSERT INTO jobs (title, company, location, job_type, salary, skills, description)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (data['title'], data['company'], data['location'],
               data['job_type'], data['salary'], data['skills'], data['description']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'}), 201

@app.route('/')
@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/api/user', methods=['GET'])
def get_user():
    # In a real app, you would get the user ID from the session
    # For this example, we'll use a hardcoded user ID
    user_id = 1
    
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    
    # First check if we need to create the users table
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not c.fetchone():
        # Create users table if it doesn't exist
        c.execute('''CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        fullname TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        phone TEXT,
                        account_created TEXT DEFAULT CURRENT_TIMESTAMP,
                        membership_type TEXT DEFAULT 'Standard'
                    )''')
        
        # Insert sample user data
        c.execute('''INSERT INTO users (username, fullname, email, phone, membership_type)
                     VALUES (?, ?, ?, ?, ?)''',
                 ('johndoe', 'John Doe', 'john.doe@example.com', '+1 (555) 123-4567', 'Premium'))
        conn.commit()
    
    # Get user data
    c.execute('SELECT username, fullname, email, phone, account_created, membership_type FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'username': user[0],
            'fullname': user[1],
            'email': user[2],
            'phone': user[3],
            'created': user[4],
            'membership': user[5]
        })
    else:
        return jsonify({'error': 'User not found'}), 404


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
