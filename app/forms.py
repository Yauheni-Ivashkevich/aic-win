from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, TextAreaField 
from wtforms.validators import DataRequired, Email 


class ContactForm(FlaskForm):
    # проверяет, ввел ли пользователь хоть какую-информацию в поле
    name = StringField("Fullname", validators=[DataRequired("Please enter your fullname.")])
    # проверяет, является ли введенный электронный адрес действующим. 
    email = StringField("Email", validators=[Email("Please enter your email address.")])
    topic = TextField("Please enter your topic message.")
    message = TextAreaField("Please enter your message.")
    submit = SubmitField("Send")
