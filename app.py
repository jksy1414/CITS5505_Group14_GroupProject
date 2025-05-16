from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import current_user
from extensions import login_manager, db, mail, migrate, csrf  # ✅ include csrf from extensions
from Routes.auth_routes import auth
from models import User, Chart
from dotenv import load_dotenv
from pathlib import Path
import os
import csv
import pandas as pd  # for reading CSVs
from flask_wtf.csrf import CSRFProtect

# Load environment variables
env_path = Path('.') / 'named.env'
load_dotenv(dotenv_path=env_path)

# Create Flask app instance
app = Flask(__name__)

# Configure app from environment
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', '342ws-ij67f-uhn-oiuyt-68')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))

# Initialize extensions
db.init_app(app)
mail.init_app(app)
migrate.init_app(app, db)
csrf.init_app(app)  # ✅ CSRF initialized from shared extensions.py

# Setup Flask-Login
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register the auth Blueprint
app.register_blueprint(auth)

# Create database tables
with app.app_context():
    db.create_all()

# Route for home page
@app.route('/')
def home():
    return render_template('home.html')


# New Route for setting visibility of charts
@app.route('/set_visibility_2', methods=['POST'])
def set_visibility_2():
    # form values
    visibility = request.form.get('visibility')  # public or private
    selected_column = request.form.get('selected_column')  
    chart_type = request.form.get('chart_type')
    share_now = request.form.get('share_now')  # Check if "Share Now" was clicked

    # get colour selection values
    color = request.form.get('color') or '#ffffff' # default white
    fill_color = request.form.get("fill_color", "#4bc0c0")
    border_color = request.form.get("border_color", "#007b7b")

    # Ensure session data is retained
    session['csv_path'] = session.get('csv_path')
    session['selected_columns'] = session.get('selected_columns')
    session['renamed_headers'] = session.get('renamed_headers')

    # Recalculate data from CSV file
    filepath = session.get('csv_path')
    renamed_headers = session.get('renamed_headers', {})
    
    # Require login
    if not current_user.is_authenticated:
        flash("You must be logged in to set visibility share graphs.", "danger")
        return redirect(url_for('auth.login', next=request.url))
    
    # check for column selection
    if not selected_column: 
        flash("Missing column selection for chart sharing.", "danger")
        return redirect(url_for('auth.analyze_full', step='results'))

    # check for filepath
    if not filepath: 
        flash("Missing data for sharing the chart.", "danger")
        return redirect(url_for('auth.analyze_full', step='results'))    
    # read data file
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        flash(f"Failed to read uploaded data: {e}", "danger")
        return redirect(url_for('auth.analyze_full', step='results'))

    # clean empty values out of data
    old_name = next((old for old, new in renamed_headers.items() if new == selected_column), selected_column)
    try:
        cleaned = pd.to_numeric(df[old_name], errors='coerce').dropna()
        chart_data = cleaned.tolist()
    except Exception as e:
        flash(f"Error processing {old_name} - {e}", "danger")
        return redirect(url_for('auth.analyze_full', step='results'))

    labels = list(range(len(chart_data)))

    if not chart_data:
        flash("Selected column has no data to save as a public chart.", "danger")
        return redirect(url_for('auth.analyze_full', step='results'))

    # Save chart
    chart = Chart(
        user_id=current_user.id if current_user.is_authenticated else None,
        title=f"Chart: {selected_column}",
        labels=labels,
        values=chart_data,
        column_name=selected_column,
        visibility=visibility,
        chart_type=chart_type,
        color=color,
        fill_color=fill_color,
        border_color=border_color 
    )
    db.session.add(chart)
    db.session.commit()

    flash("Sharing option updated!", "success")

    # Redirect to explore.html if "Share Now" was clicked
    if share_now:
        return redirect(url_for('auth.explore'))
    return redirect(url_for('auth.analyze_full', step='results'))


# Route for exploring public charts
@app.route('/explore')
def explore():
    public_charts = Chart.query.filter(Chart.visibility.in_(['public', 'friends'])).order_by(Chart.created_at.desc()).all()
    return render_template('explore.html', charts=public_charts)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)



app.config['SECRET_KEY'] = 'your_secret_key'
csrf = CSRFProtect(app)



# App factory function for testing 
def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__)

    # Default configuration
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

    # Apply test config override
    if test_config:
        app.config.update(test_config)

    # Extensions
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(auth)

    # Import routes here and attach
    from Routes.main_routes import main as main_bp
    app.register_blueprint(main_bp)

    return app