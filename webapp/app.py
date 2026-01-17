"""
Task Management Web Application using the custom RDBMS.
"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import sys

# Add parent directory to path to import rdbms
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rdbms import Database, Column, Integer, VarChar, Date, Boolean, SQLParser
from datetime import date

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-in-production'

# Initialize database
DB_FILE = 'taskmanager.db.json'
db = None
parser = None


def init_database():
    """Initialize or load the database."""
    global db, parser
    
    if os.path.exists(DB_FILE):
        db = Database.load(DB_FILE)
    else:
        db = Database('taskmanager')
        
        # Create users table
        db.create_table('users', [
            Column('id', Integer(nullable=False), primary_key=True),
            Column('username', VarChar(50, nullable=False), unique=True),
            Column('email', VarChar(100, nullable=False), unique=True),
            Column('created_at', Date(nullable=False))
        ])
        
        # Create projects table
        db.create_table('projects', [
            Column('id', Integer(nullable=False), primary_key=True),
            Column('name', VarChar(100, nullable=False)),
            Column('description', VarChar(500)),
            Column('owner_id', Integer(nullable=False)),
            Column('created_at', Date(nullable=False))
        ])
        
        # Create tasks table
        db.create_table('tasks', [
            Column('id', Integer(nullable=False), primary_key=True),
            Column('title', VarChar(200, nullable=False)),
            Column('description', VarChar(1000)),
            Column('project_id', Integer(nullable=False)),
            Column('assigned_to', Integer()),
            Column('status', VarChar(20, nullable=False)),
            Column('priority', VarChar(10, nullable=False)),
            Column('completed', Boolean(nullable=False)),
            Column('due_date', Date()),
            Column('created_at', Date(nullable=False))
        ])
        
        # Add sample data
        users_table = db.get_table('users')
        users_table.insert({'id': 1, 'username': 'alice', 'email': 'alice@example.com', 'created_at': date.today()})
        users_table.insert({'id': 2, 'username': 'bob', 'email': 'bob@example.com', 'created_at': date.today()})
        users_table.insert({'id': 3, 'username': 'charlie', 'email': 'charlie@example.com', 'created_at': date.today()})
        
        projects_table = db.get_table('projects')
        projects_table.insert({'id': 1, 'name': 'Website Redesign', 'description': 'Redesign company website', 'owner_id': 1, 'created_at': date.today()})
        projects_table.insert({'id': 2, 'name': 'Mobile App', 'description': 'Develop mobile application', 'owner_id': 2, 'created_at': date.today()})
        
        tasks_table = db.get_table('tasks')
        tasks_table.insert({
            'id': 1, 'title': 'Design mockups', 'description': 'Create UI mockups for homepage',
            'project_id': 1, 'assigned_to': 1, 'status': 'in_progress', 'priority': 'high',
            'completed': False, 'due_date': date(2026, 2, 1), 'created_at': date.today()
        })
        tasks_table.insert({
            'id': 2, 'title': 'Setup database', 'description': 'Configure production database',
            'project_id': 1, 'assigned_to': 2, 'status': 'completed', 'priority': 'medium',
            'completed': True, 'due_date': date(2026, 1, 20), 'created_at': date.today()
        })
        tasks_table.insert({
            'id': 3, 'title': 'API development', 'description': 'Develop REST API endpoints',
            'project_id': 2, 'assigned_to': 3, 'status': 'todo', 'priority': 'high',
            'completed': False, 'due_date': date(2026, 2, 15), 'created_at': date.today()
        })
        
        save_database()
    
    parser = SQLParser(db)


def save_database():
    """Save database to file."""
    db.save(DB_FILE)


# Routes
@app.route('/')
def index():
    """Home page showing overview."""
    users = db.get_table('users').select()
    projects = db.get_table('projects').select()
    tasks = db.get_table('tasks').select()
    
    return render_template('index.html', 
                         users=users, 
                         projects=projects, 
                         tasks=tasks,
                         total_users=len(users),
                         total_projects=len(projects),
                         total_tasks=len(tasks))


@app.route('/users')
def list_users():
    """List all users."""
    users = db.get_table('users').select()
    return render_template('users.html', users=users)


@app.route('/users/new', methods=['GET', 'POST'])
def new_user():
    """Create a new user."""
    if request.method == 'POST':
        try:
            users_table = db.get_table('users')
            # Get next ID
            existing_users = users_table.select()
            next_id = max([u['id'] for u in existing_users], default=0) + 1
            
            users_table.insert({
                'id': next_id,
                'username': request.form['username'],
                'email': request.form['email'],
                'created_at': date.today()
            })
            save_database()
            flash('User created successfully!', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('user_form.html')


@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """Edit a user."""
    users_table = db.get_table('users')
    
    if request.method == 'POST':
        try:
            users_table.update(
                {
                    'username': request.form['username'],
                    'email': request.form['email']
                },
                where=lambda row: row['id'] == user_id
            )
            save_database()
            flash('User updated successfully!', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    users = users_table.select(where=lambda row: row['id'] == user_id)
    if not users:
        flash('User not found', 'error')
        return redirect(url_for('list_users'))
    
    return render_template('user_form.html', user=users[0])


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete a user."""
    try:
        users_table = db.get_table('users')
        count = users_table.delete(where=lambda row: row['id'] == user_id)
        if count > 0:
            save_database()
            flash('User deleted successfully!', 'success')
        else:
            flash('User not found', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('list_users'))


@app.route('/projects')
def list_projects():
    """List all projects."""
    # Join projects with users to get owner names
    projects = db.join('projects', 'users', 'owner_id', 'id', join_type='left')
    return render_template('projects.html', projects=projects)


@app.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    """Create a new project."""
    users = db.get_table('users').select()
    
    if request.method == 'POST':
        try:
            projects_table = db.get_table('projects')
            existing_projects = projects_table.select()
            next_id = max([p['id'] for p in existing_projects], default=0) + 1
            
            projects_table.insert({
                'id': next_id,
                'name': request.form['name'],
                'description': request.form['description'],
                'owner_id': int(request.form['owner_id']),
                'created_at': date.today()
            })
            save_database()
            flash('Project created successfully!', 'success')
            return redirect(url_for('list_projects'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('project_form.html', users=users)


@app.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
def edit_project(project_id):
    """Edit a project."""
    projects_table = db.get_table('projects')
    users = db.get_table('users').select()
    
    if request.method == 'POST':
        try:
            projects_table.update(
                {
                    'name': request.form['name'],
                    'description': request.form['description'],
                    'owner_id': int(request.form['owner_id'])
                },
                where=lambda row: row['id'] == project_id
            )
            save_database()
            flash('Project updated successfully!', 'success')
            return redirect(url_for('list_projects'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    projects = projects_table.select(where=lambda row: row['id'] == project_id)
    if not projects:
        flash('Project not found', 'error')
        return redirect(url_for('list_projects'))
    
    return render_template('project_form.html', project=projects[0], users=users)


@app.route('/projects/<int:project_id>/delete', methods=['POST'])
def delete_project(project_id):
    """Delete a project."""
    try:
        projects_table = db.get_table('projects')
        count = projects_table.delete(where=lambda row: row['id'] == project_id)
        if count > 0:
            save_database()
            flash('Project deleted successfully!', 'success')
        else:
            flash('Project not found', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('list_projects'))


@app.route('/tasks')
def list_tasks():
    """List all tasks."""
    # Get all tasks and related data
    tasks = db.get_table('tasks').select()
    projects = {p['id']: p for p in db.get_table('projects').select()}
    users = {u['id']: u for u in db.get_table('users').select()}
    
    # Enrich tasks with project and user names
    enriched_tasks = []
    for task in tasks:
        enriched = task.copy()
        enriched['project_name'] = projects.get(task['project_id'], {}).get('name', 'Unknown')
        enriched['assigned_to_name'] = users.get(task['assigned_to'], {}).get('username', 'Unassigned')
        enriched_tasks.append(enriched)
    
    return render_template('tasks.html', tasks=enriched_tasks)


@app.route('/tasks/new', methods=['GET', 'POST'])
def new_task():
    """Create a new task."""
    projects = db.get_table('projects').select()
    users = db.get_table('users').select()
    
    if request.method == 'POST':
        try:
            tasks_table = db.get_table('tasks')
            existing_tasks = tasks_table.select()
            next_id = max([t['id'] for t in existing_tasks], default=0) + 1
            
            due_date_str = request.form.get('due_date')
            due_date = None
            if due_date_str:
                parts = due_date_str.split('-')
                due_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
            
            assigned_to = request.form.get('assigned_to')
            assigned_to = int(assigned_to) if assigned_to else None
            
            tasks_table.insert({
                'id': next_id,
                'title': request.form['title'],
                'description': request.form['description'],
                'project_id': int(request.form['project_id']),
                'assigned_to': assigned_to,
                'status': request.form['status'],
                'priority': request.form['priority'],
                'completed': request.form.get('completed') == 'on',
                'due_date': due_date,
                'created_at': date.today()
            })
            save_database()
            flash('Task created successfully!', 'success')
            return redirect(url_for('list_tasks'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('task_form.html', projects=projects, users=users)


@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    """Edit a task."""
    tasks_table = db.get_table('tasks')
    projects = db.get_table('projects').select()
    users = db.get_table('users').select()
    
    if request.method == 'POST':
        try:
            due_date_str = request.form.get('due_date')
            due_date = None
            if due_date_str:
                parts = due_date_str.split('-')
                due_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
            
            assigned_to = request.form.get('assigned_to')
            assigned_to = int(assigned_to) if assigned_to else None
            
            tasks_table.update(
                {
                    'title': request.form['title'],
                    'description': request.form['description'],
                    'project_id': int(request.form['project_id']),
                    'assigned_to': assigned_to,
                    'status': request.form['status'],
                    'priority': request.form['priority'],
                    'completed': request.form.get('completed') == 'on',
                    'due_date': due_date
                },
                where=lambda row: row['id'] == task_id
            )
            save_database()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('list_tasks'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    tasks = tasks_table.select(where=lambda row: row['id'] == task_id)
    if not tasks:
        flash('Task not found', 'error')
        return redirect(url_for('list_tasks'))
    
    task = tasks[0]
    if task['due_date']:
        task['due_date_str'] = task['due_date'].isoformat()
    
    return render_template('task_form.html', task=task, projects=projects, users=users)


@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    """Delete a task."""
    try:
        tasks_table = db.get_table('tasks')
        count = tasks_table.delete(where=lambda row: row['id'] == task_id)
        if count > 0:
            save_database()
            flash('Task deleted successfully!', 'success')
        else:
            flash('Task not found', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('list_tasks'))


@app.route('/sql', methods=['GET', 'POST'])
def sql_console():
    """SQL console for executing raw SQL."""
    result = None
    error = None
    
    if request.method == 'POST':
        sql = request.form.get('sql', '')
        try:
            result = parser.execute(sql)
            save_database()
        except Exception as e:
            error = str(e)
    
    return render_template('sql_console.html', result=result, error=error)


if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
