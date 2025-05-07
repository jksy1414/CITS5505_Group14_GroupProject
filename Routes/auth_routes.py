from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

# Create auth blueprint
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Login route for user authentication."""
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
    """Register route for creating a new user."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        height = request.form.get('height')
        weight = request.form.get('weight')
        age = request.form.get('age')

        # Validate that all required fields are provided
        if not all([username, email, password, confirm_password, height, weight, age]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('auth.register'))

        # Validate password confirmation
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.register'))

        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists!', 'danger')
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

            # Log in the user immediately after registration
            login_user(new_user)

            flash('Registration successful!', 'success')
            return redirect(url_for('auth.account'))

        except ValueError:
            flash('Invalid value for height, weight, or age. Please provide valid numbers.', 'danger')
            return redirect(url_for('auth.register'))

        except Exception as e:
            # Handle unexpected errors
            flash(f'An unexpected error occurred: {str(e)}', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('register.html')


@auth.route('/account', methods=['GET'])
@login_required
def account():
    return render_template('account.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    """Logout route to end the user session."""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Placeholder for forgot password functionality."""
    if request.method == 'POST':
        # Logic for handling password reset can be added here
        flash('Password reset instructions have been sent to your email.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')  # Create a corresponding template if needed

@auth.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile."""
    username = request.form.get('username')
    age = request.form.get('age')
    height = request.form.get('height')
    weight = request.form.get('weight')

    # Validate input
    if not all([username, age, height, weight]):
        flash('All fields are required!', 'danger')
        return redirect(url_for('auth.account'))

    try:
        # Update user details
        current_user.username = username
        current_user.age = int(age)
        current_user.height = float(height)
        current_user.weight = float(weight)
        db.session.commit()

        flash('Profile updated successfully!', 'success')
    except ValueError:
        flash('Invalid input. Please provide valid numbers for age, height, and weight.', 'danger')

    return redirect(url_for('auth.account'))