from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect

csrf = CSRFProtect()        # CSRF Protection
db = SQLAlchemy()           # Database ORM
mail = Mail()               # Email handling
migrate = Migrate()         # DB migrations
login_manager = LoginManager()  # User session manager
