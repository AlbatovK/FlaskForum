from flask_wtf import FlaskForm
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import SubmitField, widgets, SelectMultipleField
from wtforms.validators import DataRequired


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class AddPostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    tags = MultiCheckboxField(validate_choice=False)
    submit = SubmitField('Применить')
