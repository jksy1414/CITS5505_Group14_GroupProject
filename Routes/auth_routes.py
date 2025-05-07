from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Query the user by email
        user = User.query.filter_by(email=email).first()

        # Validate email and password
        if not user or not user.check_password(password):
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('auth.login'))

        # Log in the user
        login_user(user)
        flash('Login successful!', 'success')
        return redirect(url_for('auth.account'))  # Redirect to the account page after login

    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        height = request.form.get('height')
        weight = request.form.get('weight')
        age = request.form.get('age')

        # Validate that all required fields are provided
        if not username or not email or not password or not confirm_password or not height or not weight or not age:
            flash('All fields are required!', 'danger')
            return redirect(url_for('auth.register'))

        # Validate password confirmation
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.register'))

        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('There is already an account using this username or email address.', 'danger')
            return redirect(url_for('auth.register'))

        try:
            # Create a new user
            new_user = User(
                username=username,
                email=email,
                height=float(height),
                weight=float(weight),
                age=int(age)
            )
            new_user.set_password(password)  # Hash the password
            db.session.add(new_user)
            db.session.commit()

            # Display success message and redirect to login page
            flash('Account created - please login.', 'success')
            return redirect(url_for('auth.login'))

        except ValueError:
            flash('Invalid value for height, weight, or age.', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('register.html')

@auth.route('/account', methods=['GET'])
@login_required
def account():
    return render_template('account.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))