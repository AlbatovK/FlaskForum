from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class MessageForm(FlaskForm):
    content = TextAreaField('Ответ', validators=[DataRequired()])
    submit = SubmitField('Отправить')
