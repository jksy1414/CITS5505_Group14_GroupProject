from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd  # for reading CSVs
from Routes.auth_routes import auth
from models import db, User
from flask_login import LoginManager
from extensions import db, mail
import os
from dotenv import load_dotenv
from flask import flash

#load env file
load_dotenv()

app = Flask(__name__)



# protect cookie/session
app.config['SECRET_KEY'] = 'your-secret-key'
# save sqlite db location 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

#configurate flask email for resetting passwords
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# bind SQLAlchemy, mail with Flask
db.init_app(app)
mail.init_app(app)

#Login management
login_manager = LoginManager()
#if the status is not login, web will transfer to /login
login_manager.login_view = 'auth.login'
#bind login_manager and flask
login_manager.init_app(app)

#loading user object from user_id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
#register blueprint
app.register_blueprint(auth)

#create db tables
with app.app_context():
    db.create_all()

# Route for home page
@app.route('/')
def home():
    return render_template('home.html')
    
# Route for input page
@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        # 1. Grab file + column selection from form
        file = request.files.get('fitnessFile')
        selected_columns = request.form.getlist('columns')
        visibility = request.form.get('visibility')  # 📦 Share setting

        # 🧾 Show error if no file
        if not file or file.filename == "":
            flash("Please upload a CSV file.", "danger")
            return redirect(url_for('analyze'))

        # 🧾 Show error if no columns selected
        if not selected_columns:
            flash("Please select at least one column to analyze.", "danger")
            return redirect(url_for('analyze'))

        # 🧪 Try to read the CSV file
        try:
            df = pd.read_csv(file)
        except Exception as e:
            flash("Error reading the CSV file. Please upload a valid .csv format.", "danger")
            return redirect(url_for('analyze'))

        # 🧪 Check that selected columns exist
        if not all(col in df.columns for col in selected_columns):
            flash("Selected column(s) not found in the uploaded file. Please check your CSV format.", "danger")
            return redirect(url_for('analyze'))

        # ✅ Process data
        selected_data = df[selected_columns]
        session['labels'] = list(selected_data.index)
        session['values'] = selected_data[selected_columns[0]].tolist()
        session['column_name'] = selected_columns[0]
        session['visibility'] = visibility  # 📦 Save for result sharing

        flash("Analysis successful! Proceed to view your chart.", "success")
        return redirect(url_for('results'))

    return render_template('input_analyze.html')


@app.route('/results')
def results():
    labels = session.get('labels', [])
    values = session.get('values', [])
    column_name = session.get('column_name', 'Your Fitness Data')
    visibility = session.get('visibility', 'private')

    return render_template('output_result.html',
                           labels=labels,
                           values=values,
                           column_name=column_name,
                           visibility=visibility)

@app.route('/set_visibility', methods=['POST'])
def set_visibility():
    visibility = request.form.get('visibility')
    session['visibility'] = visibility  # store in session
    flash("Sharing option updated!", "success")
    return redirect(url_for('results'))

if __name__ == '__main__':
    app.run(debug=True)
