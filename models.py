from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    platforms = db.relationship('Platform', backref='user', lazy=True, cascade="all, delete-orphan")
    rules = db.relationship('ForwardingRule', backref='user', lazy=True, cascade="all, delete-orphan")
    logs = db.relationship('MessageLog', backref='user', lazy=True, cascade="all, delete-orphan")

class Platform(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    type = db.Column(db.String(64), nullable=False)  # telegram, whatsapp, slack, etc.
    credentials = db.Column(db.Text, nullable=False)  # JSON string with credentials (username, password, tokens, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    source_rules = db.relationship('ForwardingRule', foreign_keys='ForwardingRule.source_id', backref='source', lazy=True)
    destination_rules = db.relationship('ForwardingRule', foreign_keys='ForwardingRule.destination_id', backref='destination', lazy=True)

class ForwardingRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('platform.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('platform.id'), nullable=False)
    schedule = db.Column(db.String(64), nullable=True)  # Cron-like schedule (e.g., "*/10 * * * *" for every 10 minutes)
    filters = db.Column(db.Text, nullable=True)  # JSON string with filters (keywords, senders, etc.)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    logs = db.relationship('MessageLog', backref='rule', lazy=True)

class MessageLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source_message = db.Column(db.Text, nullable=True)
    destination_message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(64), nullable=False)  # success, error
    error_message = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    rule_id = db.Column(db.Integer, db.ForeignKey('forwarding_rule.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
