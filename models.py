from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


# User model
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(150), nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    avatar = db.Column(db.String(255), default='images/buggohome.jpg')


    charts = db.relationship('Chart', backref='user', lazy=True)
    analysis_histories = db.relationship('AnalysisHistory', backref='user', lazy=True)
    activity_logs = db.relationship('ActivityLog', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Chart model
class Chart(db.Model):
    __tablename__ = 'charts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(120))
    labels = db.Column(db.PickleType)
    values = db.Column(db.PickleType)
    column_name = db.Column(db.String(120))
    chart_type = db.Column(db.String(20), default='bar')
    visibility = db.Column(db.String(20), default='private')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    color = db.Column(db.String(20), nullable=True)
    fill_color = db.Column(db.String(10), default="#4bc0c0")
    border_color = db.Column(db.String(10), default="#007b7b")

# HealthData model
class HealthData(db.Model):
    __tablename__ = 'health_data'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    calories_intake = db.Column(db.Integer)
    sleep_hours = db.Column(db.Float)
    workout_duration = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)
    steps = db.Column(db.Integer)
    user = db.relationship('User', backref=db.backref('health_records', lazy=True))
    visibility = db.Column(db.String(20), default='private')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# AnalysisHistory model
class AnalysisHistory(db.Model):
    __tablename__ = 'analysis_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255))
    raw_csv = db.Column(db.Text)  # Store entire CSV content as plain text
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())


# ActivityLog model
class ActivityLog(db.Model):
    __tablename__ = 'activity_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    selected_columns = db.Column(db.Text)
    renamed_headers = db.Column(db.Text)
    shared_images = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Friend model – to support friend requests and accepted friendships
class Friend(db.Model):
    __tablename__ = 'friends'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)      # requester
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)    # receiver
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted'
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())