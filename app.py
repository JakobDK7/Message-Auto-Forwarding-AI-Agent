import os
import logging
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create database base class
class Base(DeclarativeBase):
    pass

# Initialize Flask extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///message_forwarder.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database and login manager with the app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models after initializing db to avoid circular imports
with app.app_context():
    from models import User, Platform, ForwardingRule, MessageLog
    db.create_all()

# Import necessary components after initializing the app
from forwarder import MessageForwarder
from scheduler import ScheduleManager

# Initialize forwarder and scheduler
forwarder = MessageForwarder()
scheduler = ScheduleManager(forwarder)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    from models import User
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    from models import User
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate form input
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        # Check if username or email exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    from models import Platform, ForwardingRule, MessageLog
    
    platforms = Platform.query.filter_by(user_id=current_user.id).all()
    rules = ForwardingRule.query.filter_by(user_id=current_user.id).all()
    logs = MessageLog.query.filter_by(user_id=current_user.id).order_by(MessageLog.timestamp.desc()).limit(10).all()
    
    platform_count = len(platforms)
    active_rules = sum(1 for rule in rules if rule.is_active)
    
    return render_template('dashboard.html', 
                          platforms=platforms, 
                          rules=rules, 
                          logs=logs,
                          platform_count=platform_count,
                          active_rules=active_rules)

@app.route('/platforms', methods=['GET', 'POST'])
@login_required
def platforms():
    from models import Platform
    
    if request.method == 'POST':
        name = request.form.get('name')
        platform_type = request.form.get('type')
        credentials = request.form.get('credentials')
        
        if not all([name, platform_type, credentials]):
            flash('All fields are required', 'danger')
            return redirect(url_for('platforms'))
        
        # Create new platform
        new_platform = Platform(
            name=name,
            type=platform_type,
            credentials=credentials,
            user_id=current_user.id
        )
        
        db.session.add(new_platform)
        db.session.commit()
        
        flash('Platform added successfully', 'success')
        return redirect(url_for('platforms'))
    
    platforms = Platform.query.filter_by(user_id=current_user.id).all()
    return render_template('platforms.html', platforms=platforms)

@app.route('/platform/delete/<int:platform_id>', methods=['POST'])
@login_required
def delete_platform(platform_id):
    from models import Platform
    
    platform = Platform.query.filter_by(id=platform_id, user_id=current_user.id).first()
    
    if not platform:
        flash('Platform not found', 'danger')
        return redirect(url_for('platforms'))
    
    db.session.delete(platform)
    db.session.commit()
    
    flash('Platform deleted successfully', 'success')
    return redirect(url_for('platforms'))

@app.route('/rules', methods=['GET', 'POST'])
@login_required
def rules():
    from models import Platform, ForwardingRule
    
    if request.method == 'POST':
        name = request.form.get('name')
        source_id = request.form.get('source_id')
        destination_id = request.form.get('destination_id')
        schedule = request.form.get('schedule')
        filters = request.form.get('filters')
        
        if not all([name, source_id, destination_id]):
            flash('Name, source, and destination are required', 'danger')
            return redirect(url_for('rules'))
        
        # Create new rule
        new_rule = ForwardingRule(
            name=name,
            source_id=source_id,
            destination_id=destination_id,
            schedule=schedule,
            filters=filters,
            user_id=current_user.id,
            is_active=True
        )
        
        db.session.add(new_rule)
        db.session.commit()
        
        # Add rule to scheduler
        scheduler.add_rule(new_rule)
        
        flash('Forwarding rule added successfully', 'success')
        return redirect(url_for('rules'))
    
    platforms = Platform.query.filter_by(user_id=current_user.id).all()
    rules = ForwardingRule.query.filter_by(user_id=current_user.id).all()
    
    return render_template('rules.html', platforms=platforms, rules=rules)

@app.route('/rule/toggle/<int:rule_id>', methods=['POST'])
@login_required
def toggle_rule(rule_id):
    from models import ForwardingRule
    
    rule = ForwardingRule.query.filter_by(id=rule_id, user_id=current_user.id).first()
    
    if not rule:
        flash('Rule not found', 'danger')
        return redirect(url_for('rules'))
    
    rule.is_active = not rule.is_active
    db.session.commit()
    
    if rule.is_active:
        scheduler.add_rule(rule)
        flash('Rule activated', 'success')
    else:
        scheduler.remove_rule(rule)
        flash('Rule deactivated', 'success')
    
    return redirect(url_for('rules'))

@app.route('/rule/delete/<int:rule_id>', methods=['POST'])
@login_required
def delete_rule(rule_id):
    from models import ForwardingRule
    
    rule = ForwardingRule.query.filter_by(id=rule_id, user_id=current_user.id).first()
    
    if not rule:
        flash('Rule not found', 'danger')
        return redirect(url_for('rules'))
    
    # Remove from scheduler
    scheduler.remove_rule(rule)
    
    db.session.delete(rule)
    db.session.commit()
    
    flash('Rule deleted successfully', 'success')
    return redirect(url_for('rules'))

@app.route('/logs')
@login_required
def logs():
    from models import MessageLog
    
    logs = MessageLog.query.filter_by(user_id=current_user.id).order_by(MessageLog.timestamp.desc()).all()
    return render_template('logs.html', logs=logs)

@app.route('/execute_rule/<int:rule_id>', methods=['POST'])
@login_required
def execute_rule(rule_id):
    from models import ForwardingRule
    
    rule = ForwardingRule.query.filter_by(id=rule_id, user_id=current_user.id).first()
    
    if not rule:
        flash('Rule not found', 'danger')
        return redirect(url_for('rules'))
    
    try:
        # Execute the rule immediately
        forwarder.forward_message(rule)
        flash('Rule executed successfully', 'success')
    except Exception as e:
        flash(f'Error executing rule: {str(e)}', 'danger')
    
    return redirect(url_for('rules'))

# Start scheduler when app starts
with app.app_context():
    from models import ForwardingRule
    
    # Load active rules from database
    active_rules = ForwardingRule.query.filter_by(is_active=True).all()
    
    # Add active rules to scheduler
    for rule in active_rules:
        scheduler.add_rule(rule)
    
    # Start the scheduler
    scheduler.start()
