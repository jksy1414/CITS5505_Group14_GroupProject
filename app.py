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

# Route for input page (Step 1: Upload CSV UTF-8 only)
@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        # ✅ Clear any existing session data
        #session.clear()
        session.pop('column_choices', None)
        session.pop('csv_data', None)
        session.pop('labels', None)
        session.pop('values', None)
        session.pop('columns', None)

        file = request.files.get('fitnessFile')

        # Check for file presence
        if not file or file.filename == "":
            flash("Please upload a CSV file.", "danger")
            return redirect(url_for('analyze'))

        filename = file.filename.lower()

        # Reject non-CSV files
        if not filename.endswith('.csv'):
            flash("Only CSV files are allowed.", "danger")
            return redirect(url_for('analyze'))

        try:
            # Detect delimiter dynamically
            sample = file.read(2048).decode('utf-8-sig')  # Increase sample size
            file.seek(0)  # Reset file pointer after reading sample
            dialect = csv.Sniffer().sniff(sample)
            delimiter = dialect.delimiter
            print(f"DEBUG: Detected delimiter: {delimiter}")  # Debug log
        except csv.Error:
            # Fallback to default delimiter if detection fails
            delimiter = ','
            flash("Could not determine delimiter. Using default delimiter (comma).", "warning")
            print("DEBUG: Could not determine delimiter. Using default delimiter (comma).")  # Debug log

        try:
            # Read the CSV file with the detected or default delimiter
            df = pd.read_csv(file, encoding='utf-8-sig', delimiter=delimiter)
        except UnicodeDecodeError:
            try:
                file.seek(0)  # Reset file pointer
                df = pd.read_csv(file, encoding='latin1', delimiter=delimiter)
                flash("File read successfully with fallback encoding (latin1).", "info")
            except Exception as e:
                flash("Error reading the CSV file. Please ensure it is a valid CSV.", "danger")
                print(f"DEBUG: Error reading file: {e}")  # Debug log
                return redirect(url_for('analyze'))

        # Clean headers
        df.columns = [col.strip() for col in df.columns]
        print(f"DEBUG: Headers: {df.columns.tolist()}")  # Debug log

        # Validate headers
        if df.columns.duplicated().any():
            flash("Duplicate column names detected. Please check your CSV file.", "danger")
            print("DEBUG: Duplicate column names detected.")  # Debug log
            return redirect(url_for('analyze'))

        # Store for next page
        session['column_choices'] = df.columns.tolist()
        session['csv_data'] = df.to_dict(orient='records')
        print(f"DEBUG: First few rows: {df.head()}")  # Debug log

        flash("File uploaded successfully!", "success")
        return redirect(url_for('select_columns'))

    # Initial GET request shows the upload form
    return render_template('input_analyze.html')

# Route for column selection (Step 2: Pick columns to analyze)
@app.route('/select-columns', methods=['GET', 'POST'])
def select_columns():
    if not session.get('column_choices'):  # 🔐 Prevent direct access
        flash("Please upload a CSV file before selecting columns.", "danger")
        return redirect(url_for('analyze'))

    if request.method == 'POST':
        selected_columns = request.form.getlist('columns')

        if not selected_columns:
            flash("Please select at least one column.", "danger")
            return redirect(url_for('select_columns'))

        df = pd.DataFrame(session['csv_data'])
        selected_data = df[selected_columns]

        session['labels'] = list(selected_data.index)
        # Store all selected columns and their values
        values_dict = {}
        for col in selected_columns:
            values_dict[col] = selected_data[col].tolist()

        session['values'] = values_dict
        session['columns'] = selected_columns

        return redirect(url_for('results'))

    columns = session.get('column_choices', [])
    return render_template('input_analyze_columns.html', columns=columns)

# Route for results page
@app.route("/results")
def results():
    labels = session.get("labels")
    values = session.get("values")  # dict: {column_name: [data]}
    columns = session.get("columns")  # list of selected column names
    visibility = session.get("visibility", "private")

    if not labels or not values or not columns:
        flash("Missing data for chart rendering.", "danger")
        return redirect(url_for("select_columns"))

    return render_template(
        "output_result.html",
        columns=columns,
        labels=labels,
        values=values,
        visibility=visibility
    )



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