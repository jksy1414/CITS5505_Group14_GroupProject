from extensions import db
from flask_login import UserMixin
from datetime import date

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash= db.Column(db.String(128), nullable= False)
    height = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    age = db.Column(db.Integer)
    avatar = db.Column(db.String(255), nullable=True)


    def __repr__(self):
        return f'<User {self.username}>'
    
class Chart(db.Model):
    __tablename__ = 'charts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    title = db.Column(db.String(120))
    labels = db.Column(db.PickleType)  # Store labels (e.g., dates, indexes)
    values = db.Column(db.PickleType)  # Store values
    column_name = db.Column(db.String(120))
    visibility = db.Column(db.String(20), default='private')  # public, private, friends
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref='charts')

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
