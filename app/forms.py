from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, TextAreaField 
from wtforms import ValidationError, validators 


class ContactForm(FlaskForm):
    # проверяет, ввел ли пользователь хоть какую-информацию в поле
    name = StringField("Фамилия, Имя, Отчество", [validators.Required('Введите (Фамилию, Имя, Отчество)')])
    # проверяет, является ли введенный электронный адрес действующим. 
    email = StringField("Email", [validators.Required('Ввведите Ваш email'), validators.Email()]) 
    topic = TextField("Тема сообщения")
    message = TextAreaField("Текст сообщения")
    submit = SubmitField("Отправить") 
