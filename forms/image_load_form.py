from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import FileField, SubmitField


class ImageLoadForm(FlaskForm):
    file_name = FileField(
        label="Картинка",
        validators=[
            FileRequired(),
            FileAllowed(['jpg', 'png', 'jpeg'], 'Только png и jpg изображения!')
        ]
    )

    submit = SubmitField('Подтвердить')
