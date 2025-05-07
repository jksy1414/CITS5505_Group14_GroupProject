from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash


# Initialize the SQLAlchemy object
db = SQLAlchemy()

# User model
class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Explicitly define the table name

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(150), nullable=False)  # Store hashed passwords
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    # Relationship to the Chart model
    charts = db.relationship('Chart', backref='user', lazy=True)

    # Password methods
    def set_password(self, password):
        """Hashes the given password and stores it in the password_hash field."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks the given password against the stored hash."""
        return check_password_hash(self.password_hash, password)

# Chart model
class Chart(db.Model):
    __tablename__ = 'charts'  # Explicitly define the table name

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to users table

    title = db.Column(db.String(120))
    labels = db.Column(db.PickleType)  # Store labels (e.g., dates, indexes)
    values = db.Column(db.PickleType)  # Store values
    column_name = db.Column(db.String(120))

    visibility = db.Column(db.String(20), default='private')  # public, private, friends
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class HealthData(db.Model):
    __tablename__ = 'health_data'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    date = db.Column(db.Date, default=date.today, nullable=False)
    calories_intake = db.Column(db.Integer)
    sleep_hours = db.Column(db.Float)
    workout_duration = db.Column(db.Integer)  # in minutes
    calories_burned = db.Column(db.Integer)
    steps = db.Column(db.Integer)

    user = db.relationship('User', backref=db.backref('health_records', lazy=True))

    def __repr__(self):
        return f'<HealthData user={self.user_id} date={self.date}>'

    visibility = db.Column(db.String(20), default='private')  # Options: public, private, friends
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
