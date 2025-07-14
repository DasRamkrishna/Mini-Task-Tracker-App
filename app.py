# mini_task_tracker_app/backend/app.py

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'super_secret_key'

# Initialize DB
def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_name TEXT NOT NULL,
            details TEXT,
            owner TEXT,
            created_date TEXT,
            due_date TEXT,
            is_approved INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/init-db')
def initialize_db():
    init_db()
    return "Database initialized successfully."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin_login_page():
    return render_template('admin_login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form['username']
    password = request.form['password']
    if username == 'admin' and password == 'admin123':
        session['is_admin'] = True
        return redirect(url_for('index'))
    return render_template('admin_login.html', error="Invalid credentials")

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

@app.route('/session-status')
def session_status():
    return jsonify({'is_admin': session.get('is_admin', False)})

@app.route('/tasks', methods=['GET'])
def get_tasks():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks')
    rows = c.fetchall()
    conn.close()
    tasks = [
        {
            'id': row[0],
            'short_name': row[1],
            'details': row[2],
            'owner': row[3],
            'created_date': row[4],
            'due_date': row[5],
            'is_approved': bool(row[6])
        } for row in rows
    ]
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO tasks (short_name, details, owner, created_date, due_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data['short_name'],
        data['details'],
        data['owner'],
        datetime.today().strftime('%Y-%m-%d'),
        data['due_date']
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Task added'})

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
        UPDATE tasks SET short_name=?, details=?, owner=?, due_date=? WHERE id=? AND is_approved=0
    ''', (
        data['short_name'],
        data['details'],
        data['owner'],
        data['due_date'],
        task_id
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Task updated'})

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id=? AND is_approved=0', (task_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Task deleted'})

@app.route('/tasks/approve/<int:task_id>', methods=['POST'])
def approve_task(task_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403

    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('UPDATE tasks SET is_approved=1 WHERE id=?', (task_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Task approved'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
