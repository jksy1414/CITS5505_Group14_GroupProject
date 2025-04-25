from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from models import db, User

auth = Blueprint('auth', __name__)

@auth.route('/register', methods = ['GET','POST'] )
def register():
#deal with register function
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role') #'student' or 'teacher'

        #check if username or email exist
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('username or email may exist')
            return redirect(url_for('auth.register'))
        
        new_user = User(username=username, email=email, role=role)
        #encrypt password
        new_user.password_hash = generate_password_hash(password)
        #add new user to db
        db.session.add(new_user)
        db.session.commit()

        flash('successful enrollment, please login.')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth.route('/login', methods = ['GET','POST'] )
def login():
    #deal with login function
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        #query email from db
        user = User.query.filter_by(email=email).first()

        #check right email
        if not user:
            flash('No account found with this email')
            return redirect(url_for('auth.login'))
        #check same password and password_hash
        if not check_password_hash(user.password_hash, password):
            flash('Incorrect password. Please try again.')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        flash('Login successful!')
        return redirect(url_for('upload'))
    
    return render_template('login.html')

@auth.route('/logout')
#only login users have access to the logout route
@login_required
def logout():
    #deal with logout function
    #remove current user session
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))
