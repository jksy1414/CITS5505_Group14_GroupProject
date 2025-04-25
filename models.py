from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash= db.Column(db.String(128), nullable= False)
    role = db.Column(db.String(10), nullable= False) #'student' or 'teacher'

    def __repr__(self):
        return f'<User {self.username}>'
    
