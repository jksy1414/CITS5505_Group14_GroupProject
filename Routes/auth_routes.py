from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, HealthData
import random, string, time, re, os
from flask import session
from flask_mail import Message
from extensions import db, mail
from flask import current_app
from flask_login import current_user
from werkzeug.utils import secure_filename
from util import calculate_health_score, aggregate_week_data
from datetime import date, timedelta
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
    #return render_template('account.html', user=current_user)

    user = current_user

    #computing BMI
    if not user.height or not user.weight:
        bmi = "Height and weight not available"
    else:
        try:
            bmi_value = user.weight / ((user.height / 100) ** 2 )
            bmi = f"{bmi_value:.2f}"
        except ZeroDivisionError:
            bmi= "Invalid height"

    #data (calorie_intake， calorie_burned，steps, workout_duration, sleep_hours ) from Monday to Sunday for two pictures
    today = date.today()
    days = [today-timedelta(days=i) for i in range(6, -1, -1)]
    steps = []
    workout_duration = []
    sleep_hours = []

    intake = []
    burned = []

    labels = [d.strftime('%a') for d in days] # ['Mon', ..., 'Sun']

    for d in days:
        record = HealthData.query.filter_by(user_id=user.id, date=d).first()
        
        if record:
            intake.append(record.calories_intake)
            burned.append(record.calories_burned)
            steps.append(record.steps)
            workout_duration.append(record.workout_duration)
            sleep_hours.append(record.sleep_hours)
        else: #no record, no picture
            intake.append(None) 
            burned.append(None)
            steps.append(None)
            workout_duration.append(None)
            sleep_hours.append(None)

    #get last Monday and last Sunday
    monday_last_week = today - timedelta(days=today.weekday()+7)
    sunday_last_week = monday_last_week + timedelta(days=6)

    #query last week data
    last_week_data = HealthData.query.filter(
        HealthData.user_id == user.id,
        HealthData.date >= monday_last_week,
        HealthData.date <= sunday_last_week
    ).all()

    if len(last_week_data) ==7:
        show_weekly_summary = True
        #computing workout_days, active_days, avg_deficit
        workout_days= sum(1 for d in last_week_data if d.workout_duration and d.workout_duration > 0)
        active_days = sum(1 for d in last_week_data if d.steps and d.steps >= 6000)

        deficits = [
            (d.calories_burned or 0) - (d.calories_intake or 0)
            for d in last_week_data
        ]

        avg_deficit = round(sum(deficits) / 7 , 1)

        last_week_summary = {
            'workout_days': workout_days,
            'active_days': active_days,
            'avg_deficit': avg_deficit
        }
    else:
        show_weekly_summary = False
        last_week_summary = None

    monday_of_this_week = today - timedelta(days=today.weekday()) #Monday
    sunday_of_this_week = monday_of_this_week + timedelta(days=6) #Sunday

    #query this week data for radar
    week_data = HealthData.query.filter(
        HealthData.user_id == user.id,
        HealthData.date >= monday_of_this_week,
        HealthData.date <= sunday_of_this_week
    ).all()
    #at least 3 days data, or not display picture
    if len(week_data) < 3: 
        show_radar = False
        radar_score = None
        radar_breakdown = None
        this_week_summary = None
    else:
        show_radar = True
        aggregated = aggregate_week_data(week_data)
        radar_score, radar_breakdown = calculate_health_score(aggregated)

        workout_days = sum(1 for d in week_data if d.workout_duration and d.workout_duration > 0)
        active_days = sum(1 for d in week_data if d.steps and d.steps >= 6000)
        avg_deficit = round(
            sum((d.calories_burned or 0) - (d.calories_intake or 0) for d in week_data) / len(week_data),
            1
        )

        this_week_summary = {
            'workout_days': workout_days,
            'active_days': active_days,
            'avg_deficit': avg_deficit
        }


    print("Last week dates:")
    for d in last_week_data:
        print(d.date)

    print("This week dates:")
    for d in week_data:
        print(d.date)


    return render_template(
        'account.html', 
        user=user, 
        bmi=bmi, 
        health_score = radar_score, 
        health_metrics = radar_breakdown,
        calorie_labels = labels,
        calorie_intake = intake,
        calorie_burned = burned,
        line_labels=labels,
        line_steps=steps,
        line_workout=workout_duration,
        line_sleep=sleep_hours,
        show_radar = show_radar,
        show_weekly_summary = show_weekly_summary,
        last_week_summary = last_week_summary,
        this_week_summary = this_week_summary,
        )

@auth.route('/upload_avatar', methods=['POST'])

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