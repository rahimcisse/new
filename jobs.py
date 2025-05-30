


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
def index():
    return render_template('browse_job.html')
@app.route('/account')
def index():
    return render_template('browse_job.html')



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
