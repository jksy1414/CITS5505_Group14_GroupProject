from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify,session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Chart, AnalysisHistory, ActivityLog, HealthData, Friend
import random, string, time, re, os
from flask_mail import Message
from extensions import db, mail
from flask import current_app
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
        return redirect(next_page) if next_page else redirect(url_for('home'))

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

    # Fetch all accepted friend relationships
    friendships_sent = Friend.query.filter_by(user_id=current_user.id, status='accepted').all()
    friendships_received = Friend.query.filter_by(friend_id=current_user.id, status='accepted').all()

    friend_ids = [f.friend_id for f in friendships_sent] + [f.user_id for f in friendships_received]
    friends = User.query.filter(User.id.in_(friend_ids)).all()

    # Fetch pending requests
    pending_received = Friend.query.filter_by(friend_id=user.id, status='pending').all()
    pending_sent = Friend.query.filter_by(user_id=user.id, status='pending').all()

    pending_received_users = [(fr, User.query.get(fr.user_id)) for fr in pending_received]
    pending_sent_users = [(fr, User.query.get(fr.friend_id)) for fr in pending_sent]

    # NEW: activity tab data (✅ required by user)
    activity_data = HealthData.query.filter_by(user_id=user.id).order_by(HealthData.date.desc()).limit(15).all()
    history_records = AnalysisHistory.query.filter_by(user_id=user.id).order_by(AnalysisHistory.timestamp.desc()).all()
    activity_logs = ActivityLog.query.filter_by(user_id=user.id).order_by(ActivityLog.timestamp.desc()).all()

    return render_template(
        'account.html', 
        user=user, 
        friends=friends,
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
        activity_logs=activity_logs, # ✅ include this to support Activity Log tab
        pending_received_users=pending_received_users,
        pending_sent_users=pending_sent_users,

    )


UPLOAD_FOLDER = 'static/uploads/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload new avatar image for user
@auth.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    file = request.files.get('avatar')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        rel_path = f"uploads/avatars/user_{current_user.id}_{filename}"
        abs_path = os.path.join('static', rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        file.save(abs_path)
        user = User.query.get(current_user.id)
        user.avatar = rel_path
        db.session.commit()

        return jsonify(success=True, avatar_url=url_for('static', filename=f"uploads/avatars/user_{current_user.id}_{filename}"))
    return jsonify(success=False, message="Invalid file.")

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
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Please enter your email.', 'danger')
            return redirect(url_for('auth.forgot_password'))

        user = User.query.filter_by(email=email).first()
        if not user:
            flash('No account found with that email.', 'danger')
            return redirect(url_for('auth.forgot_password'))

        code = ''.join(random.choices(string.digits, k=6))
        session['reset_code'] = code
        session['reset_email'] = email
        session['code_time'] = int(time.time())
        session['fail_attempts'] = 0

        msg = Message('Password Reset Code',
                      sender=current_app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.body = f"Your password reset code is: {code}"

        try:
            mail.send(msg)
            flash('Verification code sent to your email.', 'info')
            return redirect(url_for('auth.forgot_password'))
        except Exception as e:
            flash('Error sending email: ' + str(e), 'danger')
            return redirect(url_for('auth.forgot_password'))

    return render_template('forgot_password.html')

@auth.route('/send_code', methods=['POST'])
def send_code():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'success': False, 'error': 'Email is required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'error': 'No account found'}), 404

    code = ''.join(random.choices(string.digits, k=6))
    session['reset_code'] = code
    session['reset_email'] = email
    session['code_time'] = int(time.time())
    session['fail_attempts'] = 0

    try:
        msg = Message("Password Reset Code",
                      sender=current_app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.body = f"Your password reset code is: {code}"
        mail.send(msg)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@auth.route('/verify_code', methods=['POST'])
def verify_code():
    entered_code = request.form.get('code')
    stored_code = session.get('reset_code')
    stored_time = session.get('code_time')
    fail_attempts = session.get('fail_attempts', 0)

    if not stored_code or not stored_time:
        flash('Please request a code first.')
        return redirect(url_for('auth.forgot_password'))

    if time.time() - stored_time > 300:
        flash('Verification code expired. Please request a new one.')
        session.clear()
        return redirect(url_for('auth.forgot_password'))

    if entered_code == stored_code:
        flash('Code verified! Please reset your password.')
        return redirect(url_for('auth.reset_password'))
    else:
        fail_attempts += 1
        session['fail_attempts'] = fail_attempts
        if fail_attempts >= 5:
            flash('Too many failed attempts. Please request a new code.')
            session.clear()
        else:
            flash(f"Incorrect code. You have {5 - fail_attempts} attempts left.")
        return redirect(url_for('auth.forgot_password'))

@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        email = session.get('reset_email')

        if not email:
            flash('Session expired. Please restart the reset process.')
            return redirect(url_for('auth.forgot_password'))

        if not new_password or not confirm_password:
            flash('Please fill out both password fields.')
            return redirect(url_for('auth.reset_password'))

        if new_password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('auth.reset_password'))

        if len(new_password) < 8 or not re.search(r'[A-Z]', new_password) \
            or not re.search(r'[a-z]', new_password) or not re.search(r'\d', new_password):
            flash('Password must be at least 8 characters and include uppercase, lowercase, and a number.')
            return redirect(url_for('auth.reset_password'))

        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            session.clear()
            flash('Password reset successful! Please log in.')
            return redirect(url_for('auth.login'))
        else:
            flash('User not found.')
            return redirect(url_for('auth.forgot_password'))

    return render_template('reset_password.html')

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
                    # predefined_headers.append()
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
    
    session['values'] = values
    session['labels'] = labels

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

@auth.route('/download_history/<int:history_id>')
@login_required
def download_history(history_id):
    record = AnalysisHistory.query.get_or_404(history_id)
    if record.user_id != current_user.id:
        abort(403)
    response = current_app.response_class(record.raw_csv, mimetype='text/csv')
    response.headers.set("Content-Disposition", "attachment", filename=record.filename)
    return response

@auth.route('/add_friend', methods=['POST'])
@login_required
def add_friend():
    username = request.form.get('username')
    if not username:
        flash("Enter a username.", "warning")
        return redirect(url_for('auth.account'))

    if username == current_user.username:
        flash("You cannot add yourself.", "danger")
        return redirect(url_for('auth.account'))

    user_to_add = User.query.filter_by(username=username).first()
    if not user_to_add:
        flash("User not found.", "danger")
        return redirect(url_for('auth.account'))

    # Check if request already exists (forward or reverse)
    existing = Friend.query.filter_by(user_id=current_user.id, friend_id=user_to_add.id).first()
    reverse = Friend.query.filter_by(user_id=user_to_add.id, friend_id=current_user.id).first()
    if existing or reverse:
        flash("Friend request already exists or you are already friends.", "info")
        return redirect(url_for('auth.account'))

    new_request = Friend(user_id=current_user.id, friend_id=user_to_add.id, status='pending')
    db.session.add(new_request)
    db.session.commit()

    flash("Friend request sent!", "success")
    return redirect(url_for('auth.account'))

@auth.route('/cancel_friend/<int:request_id>', methods=['POST'])
@login_required
def cancel_friend(request_id):
    """Cancel a pending friend request sent by the current user."""
    friend_request = Friend.query.get_or_404(request_id)

    # Only allow the user who sent the request to cancel it
    if friend_request.user_id != current_user.id:
        abort(403)  # Forbidden action

    db.session.delete(friend_request)
    db.session.commit()
    flash("Friend request cancelled.", "info")
    return redirect(url_for('auth.account'))

@auth.route('/accept_friend/<int:request_id>', methods=['GET'])
@login_required
def accept_friend(request_id):
    friend_request = Friend.query.get_or_404(request_id)

    # Only the receiver (current user) can accept
    if friend_request.friend_id != current_user.id:
        abort(403)

    friend_request.status = 'accepted'
    db.session.commit()
    flash("Friend request accepted!", "success")
    return redirect(url_for('auth.account'))

@auth.route('/remove_friend/<int:friend_id>', methods=['GET'])
@login_required
def remove_friend(friend_id):
    """Remove an accepted friend connection."""
    friend_link = Friend.query.filter(
        ((Friend.user_id == current_user.id) & (Friend.friend_id == friend_id)) |
        ((Friend.user_id == friend_id) & (Friend.friend_id == current_user.id))
    ).first()

    if not friend_link:
        flash("Friend not found or already removed.", "warning")
        return redirect(url_for('auth.account'))

    db.session.delete(friend_link)
    db.session.commit()
    flash("Friend removed successfully.", "info")
    return redirect(url_for('auth.account'))

@auth.route('/explore', methods=['GET'])
@login_required
def explore():
    user = current_user

    # Query public charts
    public_charts = Chart.query.filter_by(visibility='public').all()

    # Query friends-only charts shared by friends
    friendships_sent = Friend.query.filter_by(user_id=user.id, status='accepted').all()
    friendships_received = Friend.query.filter_by(friend_id=user.id, status='accepted').all()

    friend_ids = [f.friend_id for f in friendships_sent] + [f.user_id for f in friendships_received]
    friends_charts = Chart.query.filter(Chart.visibility == 'friends', Chart.user_id.in_(friend_ids)).all()

    # Include user's own charts (both public and friends-only)
    user_charts = Chart.query.filter(
        (Chart.user_id == user.id) & (Chart.visibility.in_(['public', 'friends']))
    ).all()

    # Combine public, friends-only, and user's own charts
    charts = public_charts + friends_charts + user_charts

    # Remove duplicates (if any) by converting the list to a set
    charts = list(set(charts))

    return render_template('explore.html', charts=charts)

@auth.route('/set_visibility_2', methods=['POST'])
@login_required
def set_visibility():
    selected_column = request.form.get('selected_column')
    visibility = request.form.get('visibility')  # 'public' or 'friends'
    share_now = request.form.get('share_now')  # Check if "Share Now" was clicked
    color = request.form.get('color') or '#ffffff' #get chosen color or default white color
    fill_color = request.form.get("fill_color", "#4bc0c0")
    border_color = request.form.get("border_color", "#007b7b")
    # Validate the selected column
    if not selected_column:
        flash("No column selected for sharing.", "danger")
        return redirect(url_for('auth.analyze_full', step='results'))

    # Prepare chart data for saving
    labels = session.get("labels")
    values = session.get("values")
    renamed_headers = session.get("renamed_headers")

    if not labels or not values or not renamed_headers:
        flash("Missing data for sharing the chart.", "danger")
        return redirect(url_for('auth.analyze_full', step='results'))

    # Retrieve chart data for the selected column
    chart_data = values.get(selected_column)
    if not chart_data:
        flash("Selected column has no data to share.", "danger")
        return redirect(url_for('auth.analyze_full', step='results'))

    # Save the chart to the database
    chart = Chart(
        user_id=current_user.id,
        title=f"Chart for {selected_column}",
        labels=labels,
        values=chart_data,
        column_name=selected_column,
        visibility=visibility,
        color=color,
        fill_color=fill_color,
        border_color=border_color
    )
    db.session.add(chart)
    db.session.commit()

    flash("Chart shared successfully!", "success")

    # Redirect to explore.html if "Share Now" was clicked
    if share_now:
        return redirect(url_for('auth.explore'))

    # Default redirect back to results page
    return redirect(url_for('auth.analyze_full', step='results'))