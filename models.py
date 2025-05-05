from extensions import db
from flask_login import UserMixin

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
