from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange
from flask_wtf.file import FileAllowed

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Post Comment')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address')
    profile_image = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

class AddToCartForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add to Cart')

class CheckoutForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Place Order')
