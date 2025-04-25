from flask import Flask, render_template
from Routes.auth_routes import auth
from models import db, User
from flask_login import LoginManager

app = Flask(__name__)
# protect cookie/session
app.config['SECRET_KEY'] = 'your-secret-key'
# save sqlite db location 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
# bind SQLAlchemy and Flask
db.init_app(app)


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


# Route for input page
@app.route('/analyze')
def analyze():
    return render_template('input_analyze.html')

# Route for output page
@app.route('/results')
def results():
    return render_template('output_result.html')

if __name__ == '__main__':
    app.run(debug=True)
