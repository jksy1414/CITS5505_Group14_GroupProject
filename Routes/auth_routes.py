from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Chart, AnalysisHistory, ActivityLog, HealthData, Friend
import random, string, time, re, os
from flask_mail import Message
from extensions import mail
from werkzeug.utils import secure_filename
from util import calculate_health_score, aggregate_week_data
from datetime import date, timedelta, datetime
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse, urljoin
import pandas as pd


# Create auth blueprint
auth = Blueprint('auth', __name__)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

# Logging in with existing user credentials
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

        # Redirect to the original page or account page
        next_page = request.args.get('next')
        if next_page and not is_safe_url(next_page):
            return abort(400)  # Bad Request
        return redirect(next_page) if next_page else redirect(url_for('results'))

    # Capture the `next` parameter and pass it to the login template
    next_page = request.args.get('next')
    return render_template('login.html', next=next_page)

# Registering a new user
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

# Account page with user details and health data
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

    # NEW: activity tab data (✅ required by user)
    activity_data = HealthData.query.filter_by(user_id=user.id).order_by(HealthData.date.desc()).limit(15).all()
    history_records = AnalysisHistory.query.filter_by(user_id=user.id).order_by(AnalysisHistory.timestamp.desc()).all()
    activity_logs = ActivityLog.query.filter_by(user_id=user.id).order_by(ActivityLog.timestamp.desc()).all()

    return render_template(
        'account.html', 
        user=user, 
        Friend=Friend,
        User=User,
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
        activity_data = activity_data,
        history_records=history_records,
        activity_logs=activity_logs # ✅ include this to support Activity Log tab
    )

# Upoad new avatar image for user
@auth.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    pass # placeholder

# Logging out user
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

# Updating user profile details
@auth.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile."""
    age = request.form.get('age')
    height = request.form.get('height')
    weight = request.form.get('weight')

    # Validate input
    if not all([age, height, weight]):
        flash('All fields are required!', 'danger')
        return redirect(url_for('auth.account'))

    try:
        # Update user details
        current_user.age = int(age)
        current_user.height = float(height)
        current_user.weight = float(weight)
        db.session.commit()

        flash('Profile updated successfully!', 'success')
    except ValueError:
        flash('Invalid input. Please provide valid numbers for age, height, and weight.', 'danger')

    return redirect(url_for('auth.account'))

# ✅ New route for changing password
@auth.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not all([current_password, new_password, confirm_password]):
        flash('Please fill in all password fields.', 'danger')
        return redirect(url_for('auth.account'))

    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('auth.account'))

    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('auth.account'))

    current_user.set_password(new_password)
    db.session.commit()
    flash('Password changed successfully!', 'success')
    return redirect(url_for('auth.account'))

# New analysis page
@auth.route('/analyze_full', methods=['GET', 'POST'])
@login_required
def analyze_full():
    if request.method == 'POST':
        step = request.form.get('step')

        if step == 'upload':
            file = request.files.get('fitnessFile')
            if not file:
                flash("No file uploaded!", "danger")
                return redirect(url_for('auth.analyze_full'))

            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                filepath = os.path.join('temp_uploads', filename)
                file.save(filepath)

                # Read once to get headers
                df = pd.read_csv(filepath)

                # Save metadata to session
                session['csv_path'] = filepath
                session['columns'] = df.columns.tolist()
                session['filename'] = filename

                return redirect(url_for('auth.analyze_full', step='columns'))

            except Exception as e:
                flash(f"Error reading CSV: {e}", "danger")
                return redirect(url_for('auth.analyze_full'))

        elif step == 'columns':
            selected = request.form.getlist('columns')
            if not selected:
                flash("Please select at least one column.", "danger")
                return redirect(url_for('auth.analyze_full', step='columns'))

            session['selected_columns'] = selected
            return redirect(url_for('auth.analyze_full', step='rename'))

        elif step == 'rename':
            selected = session.get('selected_columns', [])
            new_headers = {}

            for i, col in enumerate(selected):
                mapped = request.form.get(f'header_map_{i}')
                if mapped == 'custom':
                    mapped = request.form.get(f'custom_{i}', col)
                new_headers[col] = mapped or col

            session['renamed_headers'] = new_headers

            # Re-read file for logging
            filepath = session.get('csv_path')
            try:
                df = pd.read_csv(filepath)
                csv_raw = df.to_csv(index=False)
            except Exception:
                csv_raw = ""

            history = AnalysisHistory(
                user_id=current_user.id,
                filename=session.get('filename', 'UploadedData.csv'),
                raw_csv=csv_raw
            )
            db.session.add(history)

            log = ActivityLog(
                user_id=current_user.id,
                selected_columns=", ".join(selected),
                renamed_headers=str(new_headers),
                shared_images=''
            )
            db.session.add(log)
            db.session.commit()

            return redirect(url_for('auth.analyze_full', step='results'))

    # ----- GET Request Handling -----

    step_param = request.args.get('step', 'upload')
    filepath = session.get('csv_path')
    columns = session.get('columns', [])
    selected_columns = session.get('selected_columns', [])
    renamed_headers = session.get('renamed_headers', {})

    values = {}
    labels = []

    if step_param == 'results' and filepath and selected_columns:
        try:
            df = pd.read_csv(filepath)
            for old_name in selected_columns:
                new_name = renamed_headers.get(old_name, old_name)
                try:
                    cleaned = pd.to_numeric(df[old_name], errors='coerce').dropna()
                    values[new_name] = cleaned.tolist()
                except Exception as e:
                    print(f"Error processing column '{old_name}': {e}")
                    values[new_name] = []

            if values:
                labels = list(range(len(next(iter(values.values()), []))))

        except Exception as e:
            flash(f"Error reading CSV for analysis: {e}", "danger")

    print("=== DEBUG: analyze_full ===")
    print("Selected Columns:", selected_columns)
    print("Renamed Headers:", renamed_headers)
    print("Values (sample):", {k: v[:5] for k, v in values.items()})
    print("Labels:", labels[:5])

    predefined_headers = ['Steps', 'Calories', 'Workout', 'Sleep']
    csv_uploaded = bool(filepath)

    return render_template(
        'analyze_full.html',
        step=step_param,
        columns=columns,
        selected_columns=selected_columns,
        predefined_headers=predefined_headers,
        renamed_headers=renamed_headers,
        values=values,
        labels=labels,
        csv_uploaded=csv_uploaded
    )
