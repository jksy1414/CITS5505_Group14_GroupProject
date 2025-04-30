from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from models import User
import random, string, time, re, os
from flask import session
from flask_mail import Message
from extensions import db, mail
from flask import current_app
from flask_login import current_user
from werkzeug.utils import secure_filename


auth = Blueprint('auth', __name__)

@auth.route('/register', methods = ['GET','POST'] )
def register():
#deal with register function
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        height = request.form.get('height')
        weight = request.form.get('weight')
        age = request.form.get('age')



        #check if username or email exist
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('username or email may exist')
            return redirect(url_for('auth.register'))
        
        new_user = User(username=username, email=email, height=height, weight=weight, age=age)
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
        return redirect(url_for('auth.account'))
    
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

@auth.route('/forgot-password', methods=['GET'])
def forgot_password():
    return render_template('forgot_password.html')

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        #get verified email
        email = session.get('reset_email')

        if not email:
            flash('Session expired. Please restart the process.')
            return redirect(url_for('auth.forgot_password'))
        
        #check if either input password is null
        if not new_password or not confirm_password:
            flash('Please fill out both password fields.')
            return render_template('reset_password.html')
        
        if new_password != confirm_password:
            flash('Passwords do not match. Please try again.')
            return render_template('reset_password.html')

        #check password protect strength
        if len(new_password) < 8 or not re.search(r'[A-Z]', new_password) \
            or not re.search(r'[a-z]', new_password) \
            or not re.search(r'\d', new_password):
                flash('Password must be at least 8 characters and contain uppercase, lowercase letters and a number.')
                return render_template('reset_password.html')

        #update db
        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = generate_password_hash(new_password)
            #save new password into db
            db.session.commit()
            flash('Password reset successful! Please login.')
            return redirect(url_for('auth.login'))
        else:
            flash('User not found.')
            return redirect(url_for('auth.forgot_password.'))
        
    return render_template('reset_password.html')

@auth.route('/send_code', methods=['POST'])
def send_code():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return(jsonify({'success': False, 'error': 'Email is required'}))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'error': 'No account associated with this email.'}), 400
    code = ''.join(random.choices(string.digits, k=6))

    session['reset_code'] = code
    session['reset_email'] = email
    session['code_time'] = int(time.time())
    session['fail_attempts'] = 0

    msg = Message('Password Reset Code',
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[email])
    msg.body=f"Your password reset code is: {code}"
    try:
        mail.send(msg)
        return jsonify({'success': True }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    

    
@auth.route('/verify_code', methods=['GET', 'POST'])
def verify_code():
    entered_code = request.form.get('code')
    stored_code = session.get('reset_code')
    stored_time = session.get('code_time')
    fail_attempts = session.get('fail_attempts', 0)

    if not stored_code or not stored_time:
        flash('Please request a code first.')
        return redirect(url_for('auth.forgot_password'))
    
    if time.time() - stored_time >300:
        flash('Verification code expired. Please request a new one.')
        session.pop('reset_code', None)
        session.pop('code_time', None)
        session.pop('fail_attempts', None)
        return redirect(url_for('auth.forgot_password'))
    
    if entered_code == stored_code:
        flash('Code verified! Please reset your password')
        return redirect(url_for('auth.reset_password'))
    else:
        fail_attempts += 1
        session['fail_attempts'] = fail_attempts
        if fail_attempts >= 5:
            flash('Too many failed attempts. Please request a new code.')
            session.pop('reset_code', None)
            session.pop('code_time', None)
            session.pop('fail_attempts', None)
        else:
            flash(f"Incorrect code. You have {5 - fail_attempts} attempts left")
        return redirect(url_for('auth.forgot_password')) 

@auth.route('/account')
@login_required
def account():
    user = current_user

    if not user.height or not user.weight:
        bmi = "Height and weight not available"
    else:
        try:
            bmi_value = user.weight / ((user.height / 100) ** 2 )
            bmi = f"{bmi_value:.2f}"
        except ZeroDivisionError:
            bmi= "Invalid height"

    return render_template('account.html', user=user, bmi=bmi)

@auth.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    #check avatar name in request
    if 'avatar' not in request.files:
        flash('No file part')
        return redirect(url_for('auth.account'))
    
    #get avatar file object
    file=request.files['avatar']

    #check meaningless file
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('auth.account'))
    
    #check extension name 
    if not allowed_file(file.filename):
        flash('Only jpg, jpeg, png files are allowed!')
        return redirect(url_for('auth.account'))
    
    # check file is None 
    if file:
        #remove illegal characters
        filename = secure_filename(file.filename)

        #define save path
        upload_folder = os.path.join(current_app.root_path, 'static/uploads')

        #ensure uploads folder exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        #create an unique filename(avoid duplication)
        filename=f"{current_user.id}_{filename}"
        file_path = os.path.join(upload_folder, filename)

        #save file
        file.save(file_path)

        #update db current_app avatar path
        current_user.avatar = filename
        db.session.commit()

        flash('Avatar uploaded successfully!')

    return redirect(url_for('auth.account'))

#def allowed extension names
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@auth.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    age = request.form.get('age','').strip()
    height = request.form.get('height','').strip()
    weight = request.form.get('weight','').strip()

    #check null 
    if not age or not height or not weight:
        flash("All fields (age, height, weight) are required.", 'danger')
        return redirect(url_for('auth.account'))
     
    #check type
    if not age.isdigit() or not height.isdigit() or not weight.isdigit():
        flash('Age, height and weight must be valid numbers', 'danger')
        return redirect(url_for('auth.account'))
    
    #transform into int type
    age = int(age)
    height = int(height)
    weight = int(weight)

    #update db
    current_user.age = age
    current_user.height = height
    current_user.weight = weight
    db.session.commit()

    flash('Profile updated successfully', 'success')
    return redirect (url_for('auth.account'))



    


