from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, FloatField
from wtforms.validators import InputRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=3)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo("password")])
    email = StringField("Email", validators=[InputRequired(), Email()])
    height = FloatField("Height (cm)", validators=[InputRequired()])
    weight = FloatField("Weight (kg)", validators=[InputRequired()])
    dob = DateField("Date of Birth", validators=[InputRequired()])
    submit = SubmitField("Register")
