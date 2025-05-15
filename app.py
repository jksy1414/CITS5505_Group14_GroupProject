from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd  # for reading CSVs
from flask_login import current_user
from extensions import login_manager
from extensions import db, mail
from Routes.auth_routes import auth
from models import User, Chart
import os
from dotenv import load_dotenv
import csv
from extensions import migrate
from flask_wtf.csrf import CSRFProtect # CSRF Protect


# Load environment variables
load_dotenv()

# Create Flask app instance
app = Flask(__name__)

# Protect cookie/session #csrf protection
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', '342ws-ij67f-uhn-oiuyt-68')  # Load from .env
# Save SQLite DB location
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Load from .env or use default
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

# Configure Flask email for resetting passwords
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Initialize CSRF Protection
csrf = CSRFProtect(app)

# Bind SQLAlchemy and Mail with Flask
db.init_app(app)
mail.init_app(app)

# Initialize Flask-Migrate here
migrate.init_app(app, db)

# Login management
login_manager.login_view = 'auth.login'  # Redirect to login if not authenticated
login_manager.init_app(app)

# Load user function for Flask-Login
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

@app.route('/set_visibility', methods=['POST'])
def set_visibility():
    visibility = request.form.get('visibility')
    session['visibility'] = visibility  # Store in session

    # Require login only if visibility is "public"
    if visibility == "public" and not current_user.is_authenticated:
        flash("You must be logged in to set visibility to public.", "danger")
        return redirect(url_for('auth.login', next=request.url))

    # Save chart data to the database if visibility is "public"
    if visibility == "public":
        labels = session.get("labels")
        values = session.get("values")
        columns = session.get("columns")

        if not labels or not values or not columns:
            flash("Missing data for saving the chart.", "danger")
            return redirect(url_for('results'))
        
    if visibility == "friends" and not current_user.is_authenticated:
        flash("You must be logged in to set visibility to public.", "danger")
        return redirect(url_for('auth.login', next=request.url))

    # Save chart data to the database if visibility is "public"
    if visibility == "friends":
        labels = session.get("labels")
        values = session.get("values")
        columns = session.get("columns")

        if not labels or not values or not columns:
            flash("Missing data for saving the chart.", "danger")
            return redirect(url_for('results'))

        # Save each column as a separate chart
        for column in columns:
            chart = Chart(
                user_id=current_user.id if current_user.is_authenticated else None,  # Use the logged-in user's ID
                title=f"Chart for {column}",
                labels=labels,
                values=values[column],
                column_name=column,
                visibility=visibility
            )
            db.session.add(chart)

        db.session.commit()

    flash("Sharing option updated!", "success")
    return redirect(url_for('results'))


# New Route for setting visibility of charts
@app.route('/set_visibility_2', methods=['POST'])
def set_visibility_2():
    visibility = request.form.get('visibility')  # Correct name from form
    selected_column = request.form.get('selected_column')  # Get selected column from hidden input
    chart_type = request.form.get('chart_type')

    # Ensure session data is retained
    session['csv_path'] = session.get('csv_path')
    session['selected_columns'] = session.get('selected_columns')
    session['renamed_headers'] = session.get('renamed_headers')

    session['visibility'] = visibility  # Store in session

    # Recalculate data from CSV file
    filepath = session.get('csv_path')
    selected_columns = session.get('selected_columns', [])
    renamed_headers = session.get('renamed_headers', {})

    # Debug checks to confirm session state
    print(f"DEBUG: visibility = {visibility}")
    print(f"DEBUG: session['csv_path'] = {filepath}")
    print(f"DEBUG: session['selected_columns'] = {selected_columns}")
    print(f"DEBUG: session['renamed_headers'] = {renamed_headers}")
    print(f"DEBUG: selected_column = {selected_column}")
    print(f"DEBUG: chart_type = {chart_type}")


    # Require login only if visibility is "public"
    if not current_user.is_authenticated:
        flash("You must be logged in to set visibility share graphs.", "danger")
        return redirect(url_for('auth.login', next=request.url))
    
    if not filepath or not selected_columns:
            flash("Missing data for saving the chart.", "danger")
            return redirect(url_for('auth.analyze_full', step='results'))

    # Save chart data if public
    if visibility == "public":
        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            flash(f"Failed to read uploaded data: {e}", "danger")
            return redirect(url_for('auth.analyze_full', step='results'))

        # Build values dict and labels
        values = {}
        for old_name in selected_columns:
            new_name = renamed_headers.get(old_name, old_name)
            try:
                cleaned = pd.to_numeric(df[old_name], errors='coerce').dropna()
                values[new_name] = cleaned.tolist()
            except Exception as e:
                print(f"DEBUG: Error processing {old_name} - {e}")
                values[new_name] = []

        labels = list(range(len(next(iter(values.values()), []))))

        if selected_column not in values:
            flash("Invalid column selected for saving.", "danger")
            return redirect(url_for('auth.analyze_full', step='results'))

        chart_data = values[selected_column]
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
            chart_type=chart_type 
        )
        db.session.add(chart)
        db.session.commit()

    flash("Sharing option updated!", "success")
    return redirect(url_for('auth.analyze_full', step='results'))


# Route for exploring public charts
@app.route('/explore')
def explore():
    public_charts = Chart.query.filter(Chart.visibility.in_(['public', 'friends'])).order_by(Chart.created_at.desc()).all()
    return render_template('explore.html', charts=public_charts)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)




