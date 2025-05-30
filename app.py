# new animated signup
# Extend Flask backend to support search functionality
from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
app = Flask(__name__)

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route('/browse')
def browse():
    return render_template('Job-Browse-Page.html')

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/how_it_works')
def how_it_works():
    return render_template('how_it_works.html')

@app.route('/addJob')
def addJob():
    return render_template('addJob.html')
@app.route('/account')
def account():
    return render_template('account.html')

def init_db():
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    location TEXT NOT NULL,
                    job_type TEXT NOT NULL,
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
                        location LIKE ? OR 
                        job_type LIKE ? OR 
                        description LIKE ?''',
                  tuple([f"%{query}%"] * 4))
    else:
        c.execute('SELECT * FROM jobs')
    jobs = [dict(id=row[0], title=row[1], location=row[2],
                 job_type=row[3], description=row[4])
            for row in c.fetchall()]
    conn.close()
    return jsonify(jobs)

@app.route('/api/jobs', methods=['POST'])
def add_job():
    data = request.get_json()
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute('''INSERT INTO jobs (title, location, job_type, description)
                 VALUES (?, ?, ?, ? )''',
              (data['title'], data['location'],
               data['job_type'], data['description']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'}), 201



CORS(app)  # Enable CORS for frontend access

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iconnect_users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Routes
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    new_user = User(name=name, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Signup successful'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


