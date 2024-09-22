from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length, Email
from flask_wtf.file import FileField, FileRequired, FileAllowed


class RegisterForm(FlaskForm):
	email = StringField("Email", validators=[DataRequired(), Email()])
	password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
	submit = SubmitField("Submit")

class LoginForm(FlaskForm):
	email = StringField("email", validators=[DataRequired(), Email()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField("Submit")

class UserSettingForm(FlaskForm):
	name_user = StringField("Name", validators=[DataRequired()])
	year_birth = StringField("Year Birth", validators=[DataRequired()])
	sex = StringField("Sex", validators=[DataRequired()])
	avatar_user = FileField("Images", validators=[FileRequired(), FileAllowed(["jpg", "png", "bmp"], "Images only!")])
	introduction = StringField("Introduction", validators=[DataRequired()])
	submit = SubmitField("Submit")

class SettingPasswordForm(FlaskForm):
	current_password = PasswordField("Your Password", validators=[DataRequired()])
	new_password = PasswordField("New Your Password", validators=[DataRequired(), Length(min=8)])
	confirm_password = PasswordField("Confirm Your Password", validators=[DataRequired(), EqualTo("new_password", message="Passwords Must Match!")])
	submit = SubmitField("Submit")

class ForgotPasswordForm(FlaskForm):
	email = StringField("email", validators=[DataRequired(), Email()])
	new_password = PasswordField("New Your Password", validators=[DataRequired(), Length(min=8)])
	confirm_password = PasswordField("Confirm Your Password", validators=[DataRequired(), EqualTo("new_password", message="Passwords Must Match!")])
	submit = SubmitField("Submit")

class CommentsForm(FlaskForm):
	content = StringField("Contents", validators=[DataRequired()])
	submit = SubmitField("Submit")
